# -*- coding: utf-8 -*-
"""PoB 빌드 → 택소노미 v2 축 자동 레이블러.

축 정의는 `data/build_corpus_taxonomy.json` (v2), 스킬 성질 id 는
`data/active_skill_types.json` (GGPK 역산본) 를 쓴다.

**메인 스킬 판정이 모든 하위 레이블을 좌우한다.** 실제 빌드 63개로 측정한 근거 순서:

    1. pob_raw.build.attributes.mainSocketGroup  — PoB 가 직접 표시한 주 소켓 그룹 (61/63)
    2. includeInFullDPS == true 인 그룹          — 40건에만 있으나 있을 때 38/40
    3. 최대 링크 그룹 (오라/저주/링크 제외)       — 위 둘이 없을 때 53/63

어느 단계가 발동했는지 `main_skill_source` 로 남긴다. 근거 없이 채운 값과
구분되지 않으면 코퍼스가 조용히 오염된다.

자동으로 못 얻는 축(`range` 의 aoe 구분, `scaling`, 맥락 축)은 채우지 않고
`unresolved` 에 남긴다.
"""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Any

logger = logging.getLogger("build_labeller")

ROOT = Path(__file__).resolve().parent.parent
ACTIVE_SKILL_TYPES_PATH = ROOT / "data" / "active_skill_types.json"
GEM_TAXONOMY_PATH = ROOT / "data" / "poe1_gem_taxonomy.latest.json"
ACTIVE_SKILLS_PATH = ROOT / "data" / "game_data" / "ActiveSkills.json"

_ACTIVE_GEM_KINDS = {"active_gem", "active_skill_only", "active_transfigured_or_valid_active"}
_PREFIX_RE = re.compile(r"^(Vaal|Awakened)\s+")

# delivery 는 우선순위가 있다. 토템 트랩 지뢰 소환은 attack/spell 을 이긴다.
# herald 는 attack/spell 보다 앞이다 — 전령은 spell 타입도 함께 갖는데,
# 누르지 않아도 스스로 발동한다는 쪽이 이 빌드의 정체성이라 그게 primary 가 돼야 한다.
# minion 이 herald 보다 앞인 건 의도다 (Herald of Agony 는 소환수 빌드로 잡혀야 한다).
_DELIVERY_PRIORITY = ("totem", "trap", "mine", "minion", "link", "curse", "aura", "herald",
                      "attack", "spell")
_DELIVERY_TO_AXIS = {
    "totem": "totem",
    "trap": "trap",
    "mine": "mine",
    "minion": "minion",
    "link": "aura_link",
    "curse": "curse",
    "aura": "aura_self",
    "herald": "trigger",
    "attack": "attack",
    "spell": "self_cast",
}
# 이 delivery 는 플레이어가 직접 교전하지 않는다.
_PROXY_DELIVERY = {"totem", "trap", "mine", "minion", "aura_link"}

_cache: dict[str, Any] = {}


def reset_cache() -> None:
    _cache.clear()


def _load(path: Path) -> Any:
    key = str(path)
    if key not in _cache:
        _cache[key] = json.loads(path.read_text(encoding="utf-8"))
    return _cache[key]


def _type_ids() -> dict[str, int]:
    data = _load(ACTIVE_SKILL_TYPES_PATH)
    return {name: info["id"] for name, info in data["types"].items()}


def _skill_types_by_name() -> dict[str, set[int]]:
    if "skill_types" in _cache:
        return _cache["skill_types"]
    raw = _load(ACTIVE_SKILLS_PATH)
    rows = raw["rows"] if isinstance(raw, dict) and "rows" in raw else raw
    table: dict[str, set[int]] = {}
    for row in rows:
        name = (row.get("DisplayedName") or "").strip()
        if name and name not in table:
            table[name] = set(row.get("ActiveSkillTypes") or [])
    _cache["skill_types"] = table
    return table


def _is_active_gem(name: str) -> bool:
    entry = (_load(GEM_TAXONOMY_PATH).get("entries") or {}).get(name)
    return bool(entry and entry.get("gem_kind") in _ACTIVE_GEM_KINDS)


def skill_types(skill_name: str) -> set[int]:
    """스킬 이름 → ActiveSkillTypes. Vaal/Awakened 접두어를 벗겨 재시도한다."""
    table = _skill_types_by_name()
    if skill_name in table:
        return table[skill_name]
    stripped = _PREFIX_RE.sub("", skill_name)
    return table.get(stripped, set())


# --------------------------------------------------------------------------
# 메인 스킬 판정 (근거 캐스케이드)
# --------------------------------------------------------------------------

def _active_skill_groups(build_data: dict) -> list[dict]:
    skills = ((build_data.get("pob_raw") or {}).get("skills")) or {}
    active_set = str(skills.get("active_skill_set_id") or "")
    for skill_set in skills.get("skill_sets") or []:
        if active_set and str(skill_set.get("id")) != active_set:
            continue
        return skill_set.get("skills") or []
    return []


def _group_gem_names(group: dict) -> list[str]:
    names = []
    for gem in group.get("gems") or []:
        name = (gem.get("attributes") or {}).get("nameSpec") or gem.get("name_spec") or ""
        if name:
            names.append(name.strip())
    return names


def _first_active(names: list[str]) -> str | None:
    for name in names:
        if _is_active_gem(name):
            return name
    return None


def _is_support_role(name: str) -> bool:
    ids = _type_ids()
    markers = {ids.get("aura"), ids.get("curse"), ids.get("link")} - {None}
    return bool(skill_types(name) & markers)


def _damaging(name: str) -> bool:
    entry = (_load(GEM_TAXONOMY_PATH).get("entries") or {}).get(name)
    if not entry or entry.get("gem_kind") not in _ACTIVE_GEM_KINDS:
        return False
    flags = entry.get("damage_flags") or {}
    return bool(flags.get("attack") or flags.get("caster") or flags.get("dot") or flags.get("minion"))


def detect_main_skill(build_data: dict) -> tuple[str | None, str]:
    """메인 액티브 스킬과 그 근거. (skill_name, source)."""
    groups = _active_skill_groups(build_data)
    if not groups:
        return None, "no_skill_groups"

    # 1) PoB 가 표시한 주 소켓 그룹 (1-based)
    index = ((build_data.get("pob_raw") or {}).get("build") or {}).get("attributes", {}).get("mainSocketGroup")
    if index and str(index).isdigit():
        position = int(index) - 1
        if 0 <= position < len(groups):
            candidate = _first_active(_group_gem_names(groups[position]))
            if candidate and _damaging(candidate) and not _is_support_role(candidate):
                return candidate, "main_socket_group"

    # 2) Full DPS 에 포함된 그룹 중 가장 큰 것
    full_dps = []
    for group in groups:
        if str((group.get("attributes") or {}).get("includeInFullDPS", "")).lower() != "true":
            continue
        names = _group_gem_names(group)
        candidate = _first_active(names)
        if candidate and _damaging(candidate) and not _is_support_role(candidate):
            full_dps.append((len(names), candidate))
    if full_dps:
        full_dps.sort(key=lambda item: -item[0])
        return full_dps[0][1], "include_in_full_dps"

    # 3) 오라/저주/링크를 제외한 최대 링크 그룹
    fallback = []
    for group in groups:
        names = _group_gem_names(group)
        candidate = _first_active(names)
        if candidate and _damaging(candidate) and not _is_support_role(candidate):
            fallback.append((len(names), candidate))
    if fallback:
        fallback.sort(key=lambda item: -item[0])
        return fallback[0][1], "largest_link_group"

    return None, "no_damaging_active"


# --------------------------------------------------------------------------
# 축 판정
# --------------------------------------------------------------------------

def classify_delivery(skill_name: str) -> tuple[str | None, list[str]]:
    """메인 스킬의 ActiveSkillTypes → (primary, secondary)."""
    ids = _type_ids()
    present = skill_types(skill_name)
    matched = [name for name in _DELIVERY_PRIORITY if ids.get(name) in present]
    if not matched:
        return None, []
    primary = _DELIVERY_TO_AXIS[matched[0]]
    secondary = [_DELIVERY_TO_AXIS[name] for name in matched[1:] if _DELIVERY_TO_AXIS[name] != primary]
    return primary, secondary


def classify_range(skill_name: str, delivery_primary: str | None) -> tuple[str | None, list[str]]:
    """(확정값, 후보목록).

    proxy / melee / projectile 은 확정된다. `area` 는 GGPK 에 있지만
    자기중심(Ice Nova/Righteous Fire)과 원격(Firestorm/Storm Call)을 가르는 id 는
    없다 — 양방향 시드 모두 분리 id 가 나오지 않았다. 그래서 5지선다를 2지선다로
    좁혀 후보만 돌려주고 확정은 하지 않는다.
    """
    if delivery_primary in _PROXY_DELIVERY:
        return "proxy", []
    ids = _type_ids()
    present = skill_types(skill_name)
    if ids.get("melee") in present:
        return "melee", []
    if ids.get("projectile") in present:
        return "projectile", []
    if ids.get("area") in present:
        return None, ["aoe_self", "aoe_remote"]
    return None, []


_ELEMENTS = ("fire", "cold", "lightning", "chaos")


def classify_damage(skill_name: str) -> dict[str, Any]:
    """스킬 타입으로 원소/형태 판정.

    물리는 GGPK 에 통합 타입이 없다(근접물리 23 / 물리주문 27 만 따로 존재).
    공격 스킬의 물리 피해는 스킬이 아니라 무기에서 오기 때문이며, 그래서
    원소가 하나도 안 잡힌 공격 스킬은 미판정으로 남긴다.
    """
    ids = _type_ids()
    present = skill_types(skill_name)
    matched = [name for name in _ELEMENTS if ids.get(name) in present]

    entry = (_load(GEM_TAXONOMY_PATH).get("entries") or {}).get(skill_name) or {}
    flags = entry.get("damage_flags") or {}
    form = ["dot"] if flags.get("dot") else ["hit"]

    if not matched:
        return {"element": {"primary": None, "secondary": []}, "form": form, "resolved": False}
    return {
        "element": {"primary": matched[0], "secondary": matched[1:]},
        "form": form,
        "resolved": True,
    }


def _stat(build_data: dict, key: str) -> float:
    value = (build_data.get("stats") or {}).get(key)
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


# 실측 63빌드: es 비율 30% 이상이 하이브리드 구간. defense_type_extractor 와 같은 값.
HYBRID_ES_RATIO = 0.3


def classify_defense(build_data: dict) -> dict[str, Any]:
    """stats 로 방어 축 판정.

    pool: CI 는 최대 생명력을 1 로 만든다 → `life == 1` 이 확정 신호다.
    layer: armour/evasion 은 장비만으로도 거의 항상 0 이 아니라서 원시값으로는
           판정할 수 없다. 이미 검증된 `defense_type_extractor` 의 판단을 재사용한다.
    """
    life = _stat(build_data, "life")
    energy_shield = _stat(build_data, "energy_shield")

    pool: str | None = None
    if life == 1 and energy_shield > 0:
        pool = "ci"
    elif life > 0 or energy_shield > 0:
        total = life + energy_shield
        ratio = energy_shield / total if total else 0.0
        pool = "hybrid" if ratio >= HYBRID_ES_RATIO else "life"

    layer: list[str] = []
    try:
        from defense_type_extractor import extract_build_defence_types

        axes = extract_build_defence_types(build_data)
    except ImportError:
        logger.warning("defense_type_extractor 를 불러오지 못함 — layer 판정 생략")
        axes = frozenset()

    if "ar" in axes:
        layer.append("armour")
    if "ev" in axes:
        layer.append("evasion")
    if _stat(build_data, "block") > 0:
        layer.append("block")

    return {"pool": pool, "layer": layer}


def label_player(build_data: dict) -> dict[str, Any]:
    """플레이어 주체 하나를 레이블링. 확정 못 한 축은 unresolved 로 남긴다."""
    skill, source = detect_main_skill(build_data)
    unresolved: list[str] = []

    if not skill:
        return {
            "main_skill": None,
            "main_skill_source": source,
            "delivery": {"primary": None, "secondary": []},
            "range": None,
            "range_candidates": [],
            "damage": {"element": {"primary": None, "secondary": []}, "form": []},
            "defense": {"pool": None, "layer": []},
            "unresolved": ["delivery", "range", "damage", "defense", "weapon", "scaling"],
        }

    primary, secondary = classify_delivery(skill)
    if primary is None:
        unresolved.append("delivery")

    engagement, range_candidates = classify_range(skill, primary)
    if engagement is None:
        unresolved.append("range")

    damage = classify_damage(skill)
    if not damage["resolved"]:
        unresolved.append("damage")

    defense = classify_defense(build_data)
    if defense["pool"] is None:
        unresolved.append("defense")

    unresolved.append("scaling")  # 이 소스로는 성장 축을 알 수 없다
    unresolved.append("weapon")

    return {
        "main_skill": skill,
        "main_skill_source": source,
        "delivery": {"primary": primary, "secondary": secondary},
        "range": engagement,
        "range_candidates": range_candidates,
        "damage": {"element": damage["element"], "form": damage["form"]},
        "defense": defense,
        "unresolved": unresolved,
    }


def label_build(build_data: dict) -> dict[str, Any]:
    """빌드 하나 → 주체별 태그. 현재는 player 만 (용병/AG 는 PoB 에 없다)."""
    return {"entities": {"player": label_player(build_data)}}
