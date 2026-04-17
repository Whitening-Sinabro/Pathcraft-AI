# -*- coding: utf-8 -*-
"""POB 빌드 데이터 파싱 헬퍼.

sections_continue.py(β Continue 체인)의 L7/L10 빌드 타겟 주입에 사용.
"""

import json
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# 레벨링/엔드게임 분기 기본 AL (Kitava = AL 68 진입)
DEFAULT_LEVELING_AL_MAX = 67
DEFAULT_ENDGAME_AL_MIN = 68
# Δ>=이면 multi-stage, 아니면 단일 union
STAGE_SPLIT_DELTA = 15


_VALID_GEMS_CACHE: Optional[set[str]] = None


def _load_valid_gems() -> set[str]:
    """data/valid_gems.json 로드 (BaseItemTypes + poedb.tw 합집합).

    POB gem_setups 라벨 중 Ascendancy 효과/Bestiary aspect 등
    실제 필터 가능하지 않은 이름 제거용.
    """
    global _VALID_GEMS_CACHE
    if _VALID_GEMS_CACHE is not None:
        return _VALID_GEMS_CACHE
    path = Path(__file__).resolve().parent.parent / "data" / "valid_gems.json"
    if not path.exists():
        _VALID_GEMS_CACHE = set()
        return _VALID_GEMS_CACHE
    data = json.loads(path.read_text(encoding="utf-8"))
    _VALID_GEMS_CACHE = set(data.get("gems", []))
    return _VALID_GEMS_CACHE


_WEAPON_CLASS_MAPS_CACHE: Optional[tuple[dict[str, str], dict[str, list[str]]]] = None


def _load_weapon_class_maps() -> tuple[dict[str, str], dict[str, list[str]]]:
    """Return (base_to_class, gem_to_weapon_req) from data/*.json.

    Missing files degrade gracefully to empty dicts — caller passes them to
    weapon_class_extractor which returns an empty set, which makes the L7
    weapon_phys_proxy block skip itself. Regenerate with:
      python python/extract_weapon_bases.py
      python python/extract_gem_weapon_reqs.py
    """
    global _WEAPON_CLASS_MAPS_CACHE
    if _WEAPON_CLASS_MAPS_CACHE is not None:
        return _WEAPON_CLASS_MAPS_CACHE
    root = Path(__file__).resolve().parent.parent / "data"
    base_map: dict[str, str] = {}
    gem_map: dict[str, list[str]] = {}
    base_path = root / "weapon_base_to_class.json"
    gem_path = root / "gem_weapon_requirements.json"
    if base_path.exists():
        base_map = json.loads(base_path.read_text(encoding="utf-8")).get(
            "base_to_class", {},
        )
    else:
        logger.warning("weapon_base_to_class.json missing — run extract_weapon_bases.py")
    if gem_path.exists():
        gem_map = json.loads(gem_path.read_text(encoding="utf-8")).get(
            "gem_weapon_classes", {},
        )
    else:
        logger.warning("gem_weapon_requirements.json missing — run extract_gem_weapon_reqs.py")
    _WEAPON_CLASS_MAPS_CACHE = (base_map, gem_map)
    return _WEAPON_CLASS_MAPS_CACHE


# 유니크 → 디비니 카드 매핑은 data/divcard_mapping.json (단일 진실원) 에서 로드.
# 기존 UNIQUE_TO_DIVCARD 하드코딩 dict는 2026-04-17 Phase F1-fix-1 에서 제거.
from divcard_data import load_divcard_mapping

# 유니크 → chanceable base 매핑은 data/unique_base_mapping.json (단일 진실원) 에서 로드.
# 기존 UNIQUE_TO_BASE 하드코딩 dict는 2026-04-17 Phase F6-fix-1 에서 제거.
from unique_base_data import load_unique_base_mapping


def extract_build_uniques(
    build_data: dict,
    coaching_data: Optional[dict] = None,
) -> list[str]:
    """빌드에서 사용하는 유니크 아이템 이름 추출 (backward compat).

    신규 코드는 `extract_build_unique_bases`를 사용해 base_type으로 매칭할 것.
    """
    uniques: set[str] = set()

    if coaching_data:
        for item in coaching_data.get("key_items", []):
            name = item.get("name", "")
            if name:
                uniques.add(name)

    stages = build_data.get("progression_stages", [])
    for stage in stages:
        gear = stage.get("gear_recommendation", stage.get("gear", {}))
        if isinstance(gear, dict):
            for slot_data in gear.values():
                if isinstance(slot_data, dict):
                    name = slot_data.get("name", slot_data.get("item", ""))
                    rarity = slot_data.get("rarity", "")
                    if name and rarity.lower() == "unique":
                        uniques.add(name)

    for item in build_data.get("items", []):
        if isinstance(item, dict):
            if item.get("rarity", "").lower() == "unique":
                name = item.get("name", "")
                if name:
                    uniques.add(name)

    return sorted(uniques)


def extract_build_unique_bases(
    build_data: dict,
    coaching_data: Optional[dict] = None,
) -> list[str]:
    """빌드 유니크 아이템의 **base_type** 리스트 추출.

    POE 필터는 `BaseType == "Mageblood"` (유니크명) 매칭 시 경고 발생.
    `BaseType == "Heavy Belt"` (실제 base)로 매칭해야 깨끗함.

    우선순위:
    1. POB `gear_recommendation[slot].base_type` (pob_parser가 채움)
    2. `data/unique_base_mapping.json` (coaching 전용 또는 POB에 base 없을 때)
    """
    bases: set[str] = set()

    unique_to_base = load_unique_base_mapping()

    stages = build_data.get("progression_stages", [])
    for stage in stages:
        gear = stage.get("gear_recommendation", stage.get("gear", {}))
        if isinstance(gear, dict):
            for slot_data in gear.values():
                if not isinstance(slot_data, dict):
                    continue
                if slot_data.get("rarity", "").lower() != "unique":
                    continue
                base = slot_data.get("base_type", "").strip()
                if base:
                    bases.add(base)
                    continue
                # fallback: 유니크명으로 매핑 조회
                name = slot_data.get("name", "").strip()
                mapped = unique_to_base.get(name)
                if mapped:
                    bases.add(mapped)

    # coaching key_items (POB 없이 이름만 제공될 때)
    if coaching_data:
        for item in coaching_data.get("key_items", []):
            name = item.get("name", "")
            mapped = unique_to_base.get(name)
            if mapped:
                bases.add(mapped)

    for item in build_data.get("items", []):
        if isinstance(item, dict) and item.get("rarity", "").lower() == "unique":
            base = item.get("base_type", "").strip()
            if base:
                bases.add(base)
                continue
            name = item.get("name", "").strip()
            mapped = unique_to_base.get(name)
            if mapped:
                bases.add(mapped)

    return sorted(bases)


def get_target_divcards(unique_names: list[str]) -> list[dict]:
    """유니크 아이템 목록에서 타겟 디비니 카드 추출."""
    mapping = load_divcard_mapping()
    cards: list[dict] = []
    seen: set[str] = set()
    for uname in unique_names:
        for entry in mapping.get(uname, []):
            card_name = entry["card"]
            if card_name not in seen:
                seen.add(card_name)
                cards.append({
                    "card": card_name,
                    "stack": entry["stack"],
                    "target_unique": uname,
                })
    return cards


def get_chanceable_bases(unique_names: list[str]) -> list[dict]:
    """유니크 아이템 목록에서 chanceable 베이스 추출."""
    unique_to_base = load_unique_base_mapping()
    bases: list[dict] = []
    seen: set[str] = set()
    for uname in unique_names:
        base = unique_to_base.get(uname)
        if base and base not in seen:
            seen.add(base)
            bases.append({"base": base, "unique": uname})
    return bases


import re as _re

_POB_LABEL_NOISE = _re.compile(
    r"(\^[0-9]|\*|^\d+[SLs]\s|\s{2,}|"
    r"^(Swap|Optional|Library|Auras?|Trigger|Config|Additional)\b)",
    _re.IGNORECASE,
)


def _is_plausible_gem_name(name: str) -> bool:
    """POB 그룹 라벨/커스텀 주석을 **구조적**으로 걸러냄.

    실제 존재 확인은 `_resolve_gem_name`이 담당. 이 함수는 "POB 마크업/주석인가"만 판단.
    배제: POB 컬러 마커(^2 등), 링크 프리픽스(1S, 2L), 별표, 주석 키워드, 너무 긴 문자열.
    """
    if not name or len(name) > 50:
        return False
    if _POB_LABEL_NOISE.search(name):
        return False
    return True


def _resolve_gem_name(name: str) -> Optional[str]:
    """POB 이름 → 현재 GGPK에 존재하는 젬 이름으로 정규화.

    1. 원래 이름이 valid_gems에 있으면 그대로
    2. Support 접미사 누락 케이스: 'Spell Echo' → 'Spell Echo Support'
    3. 트랜스피그 fallback: 'Boneshatter of Complex Trauma' → 'Boneshatter'
       (유저 POE가 트랜스피그 미지원 시 베이스 젬으로 대체)
    4. 위 모두 실패 → None (POB 라벨/Ascendancy 효과)
    """
    name = name.strip()
    if not name:
        return None
    valid = _load_valid_gems()
    if not valid:
        return name
    # Support 변형 우선 (POB는 접미사 생략 빈번: 'Melee Physical Damage' → 'Melee Physical Damage Support')
    # POE 실제 BaseType은 "X Support"이므로 Support 변형이 존재하면 그것을 반환.
    support_variant = name + " Support"
    if support_variant in valid and not name.endswith(" Support"):
        return support_variant
    if name in valid:
        return name
    # 트랜스피그 fallback: "X of Y" → "X" (POE 버전에 따라 트랜스피그 없으면 베이스)
    if " of " in name:
        base = name.split(" of ")[0].strip()
        base_support = base + " Support"
        if base_support in valid and not base.endswith(" Support"):
            return base_support
        if base in valid:
            return base
    return None


def extract_build_gems(build_data: dict) -> tuple[list[str], list[str]]:
    """빌드에서 사용하는 스킬젬/서포트젬 이름 추출. (skills, supports)

    POB JSON 구조 처리:
    - gem_setups[setup_name] = {"links": "Skill - Support1 - Support2", ...}
    - links 문자열을 ' - '로 split하여 개별 젬 추출
    - POB 그룹 라벨(`1S ^2Arctic Armour`)은 `_is_plausible_gem_name`으로 걸러냄
    - 트랜스피그 젬은 `_resolve_gem_name`이 베이스로 fallback
    """
    skills: set[str] = set()
    supports: set[str] = set()

    def _handle(name: str) -> None:
        if not _is_plausible_gem_name(name):
            return
        resolved = _resolve_gem_name(name)
        if resolved is None:
            return
        if "Support" in resolved:
            supports.add(resolved)
        else:
            skills.add(resolved)

    stages = build_data.get("progression_stages", [])
    for stage in stages:
        gem_setups = stage.get("gem_setups", {})
        for setup_name, links in gem_setups.items():
            _handle(setup_name)
            # links dict: {"links": "A - B - C", "reasoning": None}
            if isinstance(links, dict):
                link_str = links.get("links", "")
                if isinstance(link_str, str):
                    for g in link_str.split(" - "):
                        _handle(g)
            elif isinstance(links, list):
                for link in links:
                    if isinstance(link, str):
                        _handle(link)
                    elif isinstance(link, dict):
                        nm = link.get("name", link.get("gem", ""))
                        if nm:
                            _handle(nm)
            elif isinstance(links, str):
                for g in links.split(" - "):
                    _handle(g)

    return sorted(skills), sorted(supports)


def extract_build_bases(build_data: dict) -> list[str]:
    """빌드 장비에서 베이스 타입 추출."""
    bases: set[str] = set()
    stages = build_data.get("progression_stages", [])
    for stage in stages:
        gear = stage.get("gear_recommendation", stage.get("gear", {}))
        if isinstance(gear, dict):
            for slot_data in gear.values():
                if isinstance(slot_data, dict):
                    base = slot_data.get("base_type", slot_data.get("base", ""))
                    if base:
                        bases.add(base)
    return sorted(bases)


def detect_build_type(build_data: dict) -> str:
    """빌드 타입 감지 (spell/attack/minion/dot)."""
    gems = " ".join(extract_build_gems(build_data)[0]).lower()
    if any(k in gems for k in ["raise zombie", "raise spectre", "summon", "animate"]):
        return "minion"
    if any(k in gems for k in ["blight", "contagion", "essence drain", "toxic rain", "caustic"]):
        return "dot"
    if any(k in gems for k in ["cyclone", "lacerate", "lightning arrow", "tornado shot"]):
        return "attack"
    return "spell"


_LVL_PATTERN = re.compile(r"\bLv(?:l|el)?\s*\.?\s*(\d+)\b", re.IGNORECASE)


def _parse_stage_level(build_data: dict) -> Optional[int]:
    """POB 빌드에서 캐릭터 레벨 추출.

    우선순위:
    1. `meta.class_level` 필드 (명시적)
    2. `meta.build_name` 내 `Lvl N` / `Lv N` / `Level N` 패턴
    3. 실패 시 None (호출자가 fallback 결정)
    """
    meta = build_data.get("meta", {})
    if isinstance(meta.get("class_level"), (int, str)):
        try:
            return int(meta["class_level"])
        except (ValueError, TypeError):
            pass
    name = str(meta.get("build_name", ""))
    m = _LVL_PATTERN.search(name)
    if m:
        return int(m.group(1))
    return None


@dataclass
class StageData:
    """다중 POB 스테이지 통합 결과. layer_build_target이 소비."""

    label: str  # "leveling" | "endgame" | "all" (단일 stage)
    al_min: Optional[int] = None  # None이면 제한 없음
    al_max: Optional[int] = None
    unique_bases: list[str] = field(default_factory=list)
    unique_names: list[str] = field(default_factory=list)  # 디버그/주석용
    target_cards: list[dict] = field(default_factory=list)
    chanceable: list[dict] = field(default_factory=list)
    skills: list[str] = field(default_factory=list)
    supports: list[str] = field(default_factory=list)
    bases: list[str] = field(default_factory=list)
    # POE filter `Class ==` names the build's main skill/weapon can use.
    # Empty list → L7 weapon_phys_proxy block is skipped for this stage.
    weapon_classes: list[str] = field(default_factory=list)
    # 빌드 방어 axis 집합 {"ar", "ev", "es"}의 서브셋. 비면 L7 defense_proxy 블록 생략.
    defence_types: frozenset[str] = field(default_factory=frozenset)
    # 빌드 damage axis 집합 {"attack", "caster", "dot", "minion"}의 서브셋.
    # 비면 L7 accessory_proxy는 common axis(exalter/belt_general)만 emit.
    damage_types: frozenset[str] = field(default_factory=frozenset)

    def al_conditions(self) -> list[str]:
        """AreaLevel 조건 리스트 (없으면 빈 리스트)."""
        out: list[str] = []
        if self.al_min is not None:
            out.append(f"AreaLevel >= {self.al_min}")
        if self.al_max is not None:
            out.append(f"AreaLevel <= {self.al_max}")
        return out


def _extract_stage_bundle(
    build_data: dict,
    coaching_data: Optional[dict] = None,
) -> dict:
    """단일 POB에서 모든 필요 집합 추출 (내부용)."""
    unique_names = extract_build_uniques(build_data, coaching_data)
    unique_bases = extract_build_unique_bases(build_data, coaching_data)
    target_cards = get_target_divcards(unique_names)
    chanceable = get_chanceable_bases(unique_names)
    skills, supports = extract_build_gems(build_data)
    bases = extract_build_bases(build_data)
    # Lazy import: weapon_class_extractor re-imports extract_build_gems from
    # this module, so a top-level import would be circular.
    from weapon_class_extractor import extract_build_weapon_classes
    from defense_type_extractor import extract_build_defence_types
    from damage_type_extractor import extract_build_damage_types
    base_map, gem_map = _load_weapon_class_maps()
    weapon_classes = extract_build_weapon_classes(build_data, base_map, gem_map)
    defence_types = extract_build_defence_types(build_data)
    damage_types = extract_build_damage_types(build_data)
    return {
        "unique_names": set(unique_names),
        "unique_bases": set(unique_bases),
        "target_cards": {c["card"]: c for c in target_cards},  # dedup by card name
        "chanceable": {c["base"]: c for c in chanceable},
        "skills": set(skills),
        "supports": set(supports),
        "bases": set(bases),
        "weapon_classes": weapon_classes,
        "defence_types": defence_types,
        "damage_types": damage_types,
    }


def merge_build_stages(
    build_datas: list[dict],
    coaching_data: Optional[dict] = None,
    no_staging: bool = False,
    al_split: int = DEFAULT_LEVELING_AL_MAX,
) -> list[StageData]:
    """여러 POB를 스테이지로 병합.

    규칙:
    - `len(build_datas) == 1` 또는 `no_staging=True` 또는 Δ<STAGE_SPLIT_DELTA → 단일 stage(label="all", AL 조건 없음)
    - 그 외 → 2 stage ("leveling"은 마지막 POB 제외, AL<=al_split / "endgame"은 마지막 POB, AL>=al_split+1)
    - 두 스테이지 공통 아이템 → 어느 블록에도 넣지 않고 별도 "common" 스테이지(AL 조건 없음)로 분리
    - Lv 파싱 실패 POB → 마지막 스테이지(가장 안전) 취급 + 경고 로그

    Args:
        build_datas: 순서 무관 (내부에서 Lv 기준 정렬)
        coaching_data: 단일 coaching (각 빌드에 동일 적용)
        no_staging: True면 강제 union
        al_split: 레벨링 종료 AL (기본 67, 권장 67-75)
    """
    if not build_datas:
        return []

    bundles = [_extract_stage_bundle(bd, coaching_data) for bd in build_datas]

    # 단일 / 강제 union / Lv spread 작음 → 1 stage
    levels = [_parse_stage_level(bd) for bd in build_datas]
    known_levels = [lv for lv in levels if lv is not None]

    def _union_all(label: str) -> StageData:
        u_bases: set[str] = set()
        u_names: set[str] = set()
        cards: dict[str, dict] = {}
        chance: dict[str, dict] = {}
        sk: set[str] = set()
        sp: set[str] = set()
        bs: set[str] = set()
        wc: set[str] = set()
        dt: set[str] = set()
        dmg: set[str] = set()
        for b in bundles:
            u_bases |= b["unique_bases"]
            u_names |= b["unique_names"]
            cards.update(b["target_cards"])
            chance.update(b["chanceable"])
            sk |= b["skills"]
            sp |= b["supports"]
            bs |= b["bases"]
            wc |= b["weapon_classes"]
            dt |= b["defence_types"]
            dmg |= b["damage_types"]
        return StageData(
            label=label,
            unique_bases=sorted(u_bases),
            unique_names=sorted(u_names),
            target_cards=list(cards.values()),
            chanceable=list(chance.values()),
            skills=sorted(sk),
            supports=sorted(sp),
            bases=sorted(bs),
            weapon_classes=sorted(wc),
            defence_types=frozenset(dt),
            damage_types=frozenset(dmg),
        )

    if len(build_datas) == 1 or no_staging:
        return [_union_all("all")]
    if len(known_levels) < 2 or (max(known_levels) - min(known_levels) < STAGE_SPLIT_DELTA):
        if len(known_levels) < 2:
            logger.warning(
                "Lv 파싱 실패 (%d/%d). 전체 union으로 처리",
                len(build_datas) - len(known_levels), len(build_datas),
            )
        return [_union_all("all")]

    # Multi-stage: Lv 기준 정렬
    indexed = list(zip(build_datas, bundles, levels))
    # Lv 없는 POB는 "엔드게임" 취급 (뒤로)
    indexed.sort(key=lambda x: (x[2] is None, x[2] if x[2] is not None else 0))

    # N >= 3 POB: N개 stage 개별 분할 (각 POB별 AL 구간 소유)
    # 분할점 = 인접 Lv 중간값. Lv 없는 POB는 최대 Lv로 간주.
    if len(indexed) >= 3:
        return _build_n_stages(indexed, al_split)

    # N == 2: 기존 레벨링/엔드게임 2-stage 로직 (common 분리 포함)
    leveling_bundles = [b for _, b, _ in indexed[:-1]]
    endgame_bundles = [indexed[-1][1]]

    def _union(bundles_list: list[dict]) -> dict:
        merged = {
            "unique_bases": set(), "unique_names": set(),
            "target_cards": {}, "chanceable": {},
            "skills": set(), "supports": set(), "bases": set(),
            "weapon_classes": set(),
            "defence_types": set(),
            "damage_types": set(),
        }
        for b in bundles_list:
            merged["unique_bases"] |= b["unique_bases"]
            merged["unique_names"] |= b["unique_names"]
            merged["target_cards"].update(b["target_cards"])
            merged["chanceable"].update(b["chanceable"])
            merged["skills"] |= b["skills"]
            merged["supports"] |= b["supports"]
            merged["bases"] |= b["bases"]
            merged["weapon_classes"] |= b["weapon_classes"]
            merged["defence_types"] |= b["defence_types"]
            merged["damage_types"] |= b["damage_types"]
        return merged

    lv = _union(leveling_bundles)
    eg = _union(endgame_bundles)

    # 공통 = 교집합, 각자 = 차집합
    def _split(key: str, cast=list):
        common = lv[key] & eg[key] if isinstance(lv[key], set) else {
            k: v for k, v in lv[key].items() if k in eg[key]
        }
        lv_only = lv[key] - eg[key] if isinstance(lv[key], set) else {
            k: v for k, v in lv[key].items() if k not in eg[key]
        }
        eg_only = eg[key] - lv[key] if isinstance(eg[key], set) else {
            k: v for k, v in eg[key].items() if k not in lv[key]
        }
        if isinstance(lv[key], dict):
            return (list(lv_only.values()), list(common.values()), list(eg_only.values()))
        return (sorted(lv_only), sorted(common), sorted(eg_only))

    ub_lv, ub_cm, ub_eg = _split("unique_bases")
    un_lv, un_cm, un_eg = _split("unique_names")
    tc_lv, tc_cm, tc_eg = _split("target_cards")
    ch_lv, ch_cm, ch_eg = _split("chanceable")
    sk_lv, sk_cm, sk_eg = _split("skills")
    sp_lv, sp_cm, sp_eg = _split("supports")
    bs_lv, bs_cm, bs_eg = _split("bases")
    wc_lv, wc_cm, wc_eg = _split("weapon_classes")
    dt_lv, dt_cm, dt_eg = _split("defence_types")
    dmg_lv, dmg_cm, dmg_eg = _split("damage_types")

    stages: list[StageData] = []

    if any((ub_cm, un_cm, tc_cm, ch_cm, sk_cm, sp_cm, bs_cm, wc_cm, dt_cm, dmg_cm)):
        stages.append(StageData(
            label="common",
            unique_bases=ub_cm, unique_names=un_cm, target_cards=tc_cm,
            chanceable=ch_cm, skills=sk_cm, supports=sp_cm, bases=bs_cm,
            weapon_classes=wc_cm,
            defence_types=frozenset(dt_cm),
            damage_types=frozenset(dmg_cm),
        ))

    if any((ub_lv, un_lv, tc_lv, ch_lv, sk_lv, sp_lv, bs_lv, wc_lv, dt_lv, dmg_lv)):
        stages.append(StageData(
            label="leveling", al_max=al_split,
            unique_bases=ub_lv, unique_names=un_lv, target_cards=tc_lv,
            chanceable=ch_lv, skills=sk_lv, supports=sp_lv, bases=bs_lv,
            weapon_classes=wc_lv,
            defence_types=frozenset(dt_lv),
            damage_types=frozenset(dmg_lv),
        ))

    if any((ub_eg, un_eg, tc_eg, ch_eg, sk_eg, sp_eg, bs_eg, wc_eg, dt_eg, dmg_eg)):
        stages.append(StageData(
            label="endgame", al_min=al_split + 1,
            unique_bases=ub_eg, unique_names=un_eg, target_cards=tc_eg,
            chanceable=ch_eg, skills=sk_eg, supports=sp_eg, bases=bs_eg,
            weapon_classes=wc_eg,
            defence_types=frozenset(dt_eg),
            damage_types=frozenset(dmg_eg),
        ))

    return stages


def _build_n_stages(
    indexed: list[tuple[dict, dict, Optional[int]]],
    al_split: int,
) -> list[StageData]:
    """N>=3 POB를 Lv 순 정렬 + 각 POB별 AL 구간 소유 stage로 변환.

    분할점 = 인접 Lv 중간값. Lv 없는 POB는 (있는 POB 중) 최대 Lv+1 취급.
    AL 범위 clamp: 최저 1, 최고 85 (엔드게임 최종 stage는 상한 없음).
    """
    max_known = max((lv for _, _, lv in indexed if lv is not None), default=100)
    # 실제 사용할 Lv 리스트 (None → max+1로 마지막에 배치)
    effective_levels = [lv if lv is not None else max_known + 1 for _, _, lv in indexed]
    n = len(indexed)

    # 인접 Lv 중간값 N-1개 계산 — 각 split 경계점
    # midpoint[i] = Lv_i와 Lv_{i+1} 중간값 (integer flooring)
    midpoints = [
        max(1, (effective_levels[i] + effective_levels[i + 1]) // 2)
        for i in range(n - 1)
    ]

    stages: list[StageData] = []
    for i, (_, bundle, _) in enumerate(indexed):
        # al_min: 첫 stage = None (제한 없음), 그 외 = midpoint[i-1] + 1
        al_min = None if i == 0 else midpoints[i - 1] + 1
        # al_max: 마지막 stage = None (제한 없음), 그 외 = midpoint[i]
        al_max = None if i == n - 1 else midpoints[i]

        # 라벨: 구간 설명
        if i == 0:
            label = "leveling_early"
        elif i == n - 1:
            label = "endgame"
        else:
            label = f"stage{i}"

        stages.append(StageData(
            label=label,
            al_min=al_min,
            al_max=al_max,
            unique_bases=sorted(bundle["unique_bases"]),
            unique_names=sorted(bundle["unique_names"]),
            target_cards=list(bundle["target_cards"].values()),
            chanceable=list(bundle["chanceable"].values()),
            skills=sorted(bundle["skills"]),
            supports=sorted(bundle["supports"]),
            bases=sorted(bundle["bases"]),
            weapon_classes=sorted(bundle["weapon_classes"]),
            defence_types=frozenset(bundle["defence_types"]),
            damage_types=frozenset(bundle["damage_types"]),
        ))

    logger.info(
        "Multi-stage N=%d: %s",
        n,
        ", ".join(
            f"{s.label}(AL {s.al_min or 1}~{s.al_max or '∞'})" for s in stages
        ),
    )
    return stages


def get_crafting_bases(build_type: str) -> list[str]:
    """빌드 타입별 크래프팅 베이스 목록."""
    common = [
        "Vaal Regalia", "Astral Plate", "Zodiac Leather", "Titanium Spirit Shield",
        "Fingerless Silk Gloves", "Sorcerer Boots", "Two-Toned Boots", "Bone Helmet",
        "Crystal Belt", "Stygian Vise", "Marble Amulet", "Opal Ring", "Vermillion Ring",
    ]
    type_specific = {
        "spell": ["Profane Wand", "Opal Sceptre", "Void Sceptre", "Samite Helmet"],
        "attack": ["Siege Axe", "Jewelled Foil", "Ambusher", "Imperial Claw",
                   "Thicket Bow", "Spine Bow"],
        "dot": ["Profane Wand", "Opal Sceptre", "Short Bow"],
        "minion": ["Convoking Wand", "Bone Helmet", "Fossilised Spirit Shield"],
    }
    return common + type_specific.get(build_type, [])
