"""POE2 campaign 구조를 GGPK WorldAreas + Quest 에서 파생.

목적: SYSTEM_PROMPT_POE2 / Frontend LevelingGuide 에서 쓰는 phase key·label·level_range
를 패치 버전에 하드코딩 하지 않도록, 매 GGPK 재추출 시 자동 재생성되는 단일 source.

생성물: `data/campaign_structure_poe2.json`

실행:
    python scripts/build_poe2_campaign_structure.py

의존: `data/game_data_poe2/WorldAreas.json`, `data/game_data_poe2/Quest.json`
      (둘 다 `cargo run --bin extract_data -- --game poe2 --json` 로 확보)
"""

from __future__ import annotations

import json
import logging
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

logger = logging.getLogger("build_poe2_campaign_structure")
logging.basicConfig(level=logging.INFO, format="%(message)s")

ROOT = Path(__file__).resolve().parent.parent
WORLD_AREAS_PATH = ROOT / "data" / "game_data_poe2" / "WorldAreas.json"
QUEST_PATH = ROOT / "data" / "game_data_poe2" / "Quest.json"
OUT_PATH = ROOT / "data" / "campaign_structure_poe2.json"


def _load_json(p: Path) -> list[dict[str, Any]]:
    if not p.exists():
        raise FileNotFoundError(
            f"{p} 없음. 먼저 `cargo run --bin extract_data -- --game poe2 --json` 실행."
        )
    with p.open(encoding="utf-8") as f:
        return json.load(f)


def _prefix(id_: str) -> str:
    return id_.split("_", 1)[0] if "_" in id_ else id_


# 캠페인 phase 판정에서 배제할 Id prefix — dev/showcase/pinnacle/brag-room.
# 패치마다 Id 추가될 수 있지만 prefix 패턴은 안정적 (Design_*/BossRush_*/Abyss_Pinnacle 등).
_DEV_PREFIXES = (
    "Design", "Programming", "Login", "KaruiShowcase", "Tutorial", "Demo", "Cutscene",
    "Abyss_Pinnacle", "BossRush", "G_login",
    # 리그 메카닉 endgame 버전 — campaign Act 에 배정돼 있지만 실제로는 endgame 콘텐츠.
    # 구분 기준: 'Present' / 'Past' / 'Endgame' 접미사 또는 endgame-level (65+) 리그 area.
    "IncursionTemplePresent",  # Lv 65 Lost Temple — Act 1 배정되나 endgame Incursion
    "IncursionHub",  # Lv 2 Vaal Ruins — Act 3 placeholder, 실제 플레이 레벨 아님
)


def _effective_areas(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """플레이어가 실제 들어가는 캠페인 area 만. dev/hideout/login/WorldMap/pinnacle 제외."""
    out = []
    for r in rows:
        id_ = r.get("Id") or ""
        name = r.get("Name") or ""
        lvl = r.get("AreaLevel", 0) or 0
        if id_ in {"NULL", "CharacterSelect", "CurrentTown"}:
            continue
        if "Hideout" in id_ or r.get("IsHideout"):
            continue
        if id_.endswith("_WorldMap"):
            continue
        if name.startswith("[DNT"):  # Do Not Translate — 미사용/placeholder
            continue
        if any(id_.startswith(p) for p in _DEV_PREFIXES):
            continue
        # Showcase/Demo 가 id 중간에 들어간 경우 (KaruiBossShowcase 등) 제외
        if "Showcase" in id_ or "Demo" in id_:
            continue
        # Lv 0 = login/menu/cutscene 영역 (town 여부 무관하게 campaign area 아님)
        if lvl == 0:
            continue
        out.append(r)
    return out


def _act_phase(act: int, areas: list[dict[str, Any]]) -> dict[str, Any] | None:
    """단일 Act 묶음 → phase entry. 반환 None = skip (미출시)."""
    if not areas:
        return None
    levels = [r.get("AreaLevel", 0) for r in areas if (r.get("AreaLevel") or 0) > 0]
    if not levels:
        return None
    towns = sorted({r.get("Name") for r in areas if r.get("IsTown") and r.get("Name")})
    prefixes = defaultdict(int)
    for r in areas:
        prefixes[_prefix(r.get("Id") or "")] += 1
    # WorldMap prefix 제외 (area count 집계에서 빼고, 판단 기준에는 사용)
    gameplay_prefixes = {p: c for p, c in prefixes.items() if not p.startswith("G") or c > 1}
    map_areas = sum(1 for r in areas if r.get("IsMapArea"))
    return {
        "act": act,
        "area_count": len(areas),
        "level_min": min(levels),
        "level_max": max(levels),
        "towns": towns,
        "map_area_count": map_areas,
        "prefix_groups": sorted(gameplay_prefixes.keys()),
    }


def _group_phases(per_act: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """실측된 Act 들을 의미 단위 phase 로. 각 Act 는 개별 phase.

    규칙 (GGPK-derived, 버전 무관):
    - 단일 town + 단일 G-prefix 계열 Act → `act_N` 개별 phase (정식 캠페인 Act)
    - 복수 town + 복수 non-G prefix 계열 Act → "interlude_acts" (transient, Cruel 대체)
    - IsMapArea 비율 > 50% → "endgame_maps" (Atlas)

    Act 1-3 병합 안 함: 각 Act 의 레벨 범위(~15 per act)가 서로 달라서
    coach guidance 가 구간별로 달라져야 함.
    """
    phases = []

    for p in per_act:
        a = p["act"]

        # Endgame: IsMapArea 비율 우세
        if p["area_count"] > 0 and p["map_area_count"] / p["area_count"] > 0.5:
            phases.append({
                "key": "endgame_maps",
                "label": "엔드게임 (Atlas)",
                "acts": [a],
                "level_range": [p["level_min"], p["level_max"]],
                "towns": p["towns"],
                "area_count": p["area_count"],
                "map_area_count": p["map_area_count"],
                "note": "Waystone / Atlas",
            })
            continue

        # Interlude: 복수 non-G prefix 계열 (P1/P2/P3 …) + 복수 town
        non_g_prefixes = [x for x in p["prefix_groups"] if not x.startswith("G")]
        if len(p["towns"]) >= 2 and len(non_g_prefixes) >= 2:
            phases.append({
                "key": "interlude_acts",
                "label": f"Interlude ({'/'.join(non_g_prefixes)})",
                "acts": [a],
                "level_range": [p["level_min"], p["level_max"]],
                "towns": p["towns"],
                "area_count": p["area_count"],
                "note": "Cruel 대체 임시 콘텐츠 (향후 패치에서 재편 가능)",
                "transient": True,
            })
            continue

        # 단일 Act — Act 1/2/3/4 모두 이 경로
        town_hint = f" ({p['towns'][0]})" if p["towns"] else ""
        phases.append({
            "key": f"act_{a}",
            "label": f"Act {a}{town_hint}",
            "acts": [a],
            "level_range": [p["level_min"], p["level_max"]],
            "towns": p["towns"],
            "area_count": p["area_count"],
            "note": "",
        })

    # level_min 순 정렬 (endgame/interlude 자연 정렬됨)
    phases.sort(key=lambda x: x["level_range"][0])
    return phases


def build_structure() -> dict[str, Any]:
    world = _load_json(WORLD_AREAS_PATH)
    quests = _load_json(QUEST_PATH)

    effective = _effective_areas(world)
    by_act: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for r in effective:
        a = r.get("Act")
        if a is None:
            continue
        by_act[a].append(r)

    per_act = []
    for a in sorted(by_act.keys()):
        entry = _act_phase(a, by_act[a])
        if entry:
            per_act.append(entry)

    phases = _group_phases(per_act)

    # Quest Act 분포 기록 (미출시 Act 탐지용 — area 없지만 quest flag 존재)
    quest_acts: dict[int, int] = defaultdict(int)
    for q in quests:
        qa = q.get("Act")
        if qa is not None:
            quest_acts[qa] += 1

    structure = {
        "game": "poe2",
        "generated_at": None,  # 재현성 위해 고정 — 필요 시 git log 로 확인
        "source": {
            "world_areas": str(WORLD_AREAS_PATH.relative_to(ROOT).as_posix()),
            "quest": str(QUEST_PATH.relative_to(ROOT).as_posix()),
        },
        "phases": phases,
        "raw_act_distribution": {
            "world_areas": {str(a): len(by_act[a]) for a in sorted(by_act)},
            "quests": {str(a): quest_acts[a] for a in sorted(quest_acts)},
        },
        "notes": {
            "unreleased_acts": [a for a in quest_acts if a not in by_act and a != 0],
            "explanation": (
                "area_count=0 + quest_count>0 인 Act 는 미출시/파편 으로 스킵. "
                "transient=true phase 는 다음 패치에서 제거/재편 가능 (예: Interlude → Act 5/6 정식화)."
            ),
        },
    }
    return structure


def main() -> int:
    try:
        structure = build_structure()
    except FileNotFoundError as e:
        logger.error(str(e))
        return 1

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        json.dumps(structure, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    phases = structure["phases"]
    logger.info(f"[+] {OUT_PATH.relative_to(ROOT).as_posix()} — {len(phases)} phases:")
    for p in phases:
        lvl = p["level_range"]
        towns = ", ".join(p["towns"]) if p["towns"] else "-"
        transient = " [transient]" if p.get("transient") else ""
        logger.info(
            f"    {p['key']:20s} Lv {lvl[0]:3d}-{lvl[1]:3d}  areas={p['area_count']:3d}  "
            f"towns=[{towns}]{transient}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
