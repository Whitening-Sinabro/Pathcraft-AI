# -*- coding: utf-8 -*-
"""GGPK `ActiveSkills.ActiveSkillTypes` 의 숫자 id 를 의미로 역산한다.

GGPK 는 스킬 성질을 int 배열로만 준다. 이름표가 없으므로 **알려진 스킬 집합**으로 역산한다:

    분리 id = (양성 시드 전부가 가진 id) - (음성 시드 중 하나라도 가진 id)

후보가 여럿이면 그 id 를 가진 전체 스킬 집합의 크기로 좁힌다(`disambiguate`).
추측으로 적어두면 리그마다 조용히 틀어지므로 **매번 재도출**하고 결과를 pin 한다.

사용법:
    python python/scripts/derive_active_skill_types.py            # 검증만
    python python/scripts/derive_active_skill_types.py --write    # data/active_skill_types.json 갱신
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any

logger = logging.getLogger("derive_active_skill_types")

ROOT = Path(__file__).resolve().parents[2]
ACTIVE_SKILLS = ROOT / "data" / "game_data" / "ActiveSkills.json"
OUT_PATH = ROOT / "data" / "active_skill_types.json"

# (양성 시드, 음성 시드, 모호할 때 고를 id) — 셋째 값이 None 이면 분리 결과가 유일해야 한다.
SEED_CASES: dict[str, tuple[list[str], list[str], int | None]] = {
    "attack": (
        ["Cyclone", "Ground Slam", "Heavy Strike", "Split Arrow", "Spectral Throw", "Frost Blades"],
        ["Fireball", "Freezing Pulse", "Grace", "Flammability", "Summon Raging Spirit"],
        None,
    ),
    # 후보 [1, 6, 21, 69] 중 1 만 attack(0) 과 교집합이 0 이다. PoE 는 Attack 과 Spell 을
    # 상호배타로 보장하므로 이 배타성이 결정 근거다 (id 6 은 attack 과 78개 겹침).
    "spell": (
        ["Fireball", "Freezing Pulse", "Ice Spear", "Firestorm", "Arc"],
        ["Cyclone", "Ground Slam", "Heavy Strike", "Split Arrow", "Spectral Throw"],
        1,
    ),
    "melee": (
        ["Cyclone", "Ground Slam", "Heavy Strike", "Double Strike", "Sunder", "Earthquake"],
        ["Split Arrow", "Spectral Throw", "Lightning Arrow", "Fireball", "Grace"],
        None,
    ),
    "projectile": (
        ["Split Arrow", "Fireball", "Freezing Pulse", "Ice Spear", "Lightning Arrow", "Spectral Throw"],
        ["Cyclone", "Ground Slam", "Heavy Strike", "Grace", "Righteous Fire"],
        2,
    ),
    "totem": (
        ["Ancestral Protector", "Searing Bond", "Shockwave Totem", "Holy Flame Totem", "Decoy Totem"],
        ["Fireball", "Cyclone", "Grace", "Summon Raging Spirit", "Fire Trap", "Stormblast Mine"],
        None,
    ),
    "trap": (
        ["Fire Trap", "Ice Trap", "Bear Trap", "Seismic Trap", "Explosive Trap", "Blade Trap"],
        ["Stormblast Mine", "Icicle Mine", "Fireball", "Cyclone", "Searing Bond", "Grace"],
        None,
    ),
    "mine": (
        ["Stormblast Mine", "Icicle Mine", "Pyroclast Mine"],
        ["Fire Trap", "Ice Trap", "Fireball", "Cyclone", "Grace", "Searing Bond", "Flammability"],
        35,
    ),
    "minion": (
        ["Summon Raging Spirit", "Raise Zombie", "Summon Skeletons", "Raise Spectre",
         "Summon Carrion Golem", "Summon Stone Golem"],
        ["Fireball", "Cyclone", "Grace", "Flammability", "Fire Trap", "Searing Bond", "Flame Link"],
        5,
    ),
    "curse": (
        ["Flammability", "Frostbite", "Conductivity", "Vulnerability", "Despair", "Enfeeble",
         "Temporal Chains", "Elemental Weakness"],
        ["Grace", "Determination", "Hatred", "Fireball", "Cyclone", "Summon Raging Spirit", "Flame Link"],
        68,
    ),
    "aura": (
        ["Grace", "Determination", "Discipline", "Hatred", "Wrath", "Anger", "Malevolence",
         "Zealotry", "Pride", "Haste"],
        ["Flammability", "Frostbite", "Fireball", "Cyclone", "Summon Raging Spirit", "Flame Link", "Fire Trap"],
        80,
    ),
    "link": (
        ["Flame Link", "Soul Link", "Protective Link", "Vampiric Link", "Destructive Link", "Intuitive Link"],
        ["Grace", "Hatred", "Flammability", "Fireball", "Cyclone", "Summon Raging Spirit"],
        None,
    ),
    # 원소 — fire/cold/lightning 이 28/29/30 으로 연속인 것이 구조적 방증이다.
    "fire": (
        ["Fireball", "Firestorm", "Incinerate", "Flame Surge"],
        ["Ice Nova", "Freezing Pulse", "Arc", "Split Arrow", "Bane"],
        None,
    ),
    "cold": (
        ["Ice Nova", "Freezing Pulse", "Ice Spear", "Glacial Cascade"],
        ["Fireball", "Arc", "Split Arrow", "Bane", "Firestorm"],
        None,
    ),
    "lightning": (
        ["Arc", "Ball Lightning", "Spark", "Lightning Tendrils"],
        ["Fireball", "Ice Nova", "Split Arrow", "Bane"],
        None,
    ),
    # 후보 [8, 34, 41] 중 41 만 fire 와 거의 안 겹친다(2건). 34 는 지속피해(Fire Trap /
    # Conflagration 포함), 8 은 424개짜리 범용 플래그다.
    "chaos": (
        ["Bane", "Contagion", "Essence Drain", "Soulrend"],
        ["Fireball", "Ice Nova", "Arc", "Split Arrow"],
        41,
    ),
    # 전령은 누르지 않아도 스스로 발동한다 — delivery 축에서 self_cast 와 갈라야 하는 근거다.
    # 분리 결과가 유일하고(51), 그 id 보유 스킬이 정확히 전령 6종이라 모호성이 없다.
    "herald": (
        ["Herald of Thunder", "Herald of Ash", "Herald of Ice", "Herald of Agony", "Herald of Purity"],
        ["Grace", "Hatred", "Righteous Fire", "Fireball", "Cyclone", "Flame Link", "Flammability",
         "Summon Skitterbots"],
        None,
    ),
    # range 의 aoe 판정 근거.
    "area": (
        ["Firestorm", "Ground Slam", "Ice Nova", "Righteous Fire"],
        ["Split Arrow", "Spectral Throw", "Heavy Strike", "Frenzy"],
        None,
    ),
}

# 이 GGPK 필드로는 갈리지 않는 성질. 다른 근거가 필요하다 (스킬 스탯 / PoB / 수동).
UNRESOLVED = {
    "physical": (
        "통합 Physical 타입이 없다. 근접물리(23: Boneshatter/Bladestorm)와 "
        "물리주문(27: Ethereal Knives/Exsanguinate)만 따로 존재하고 둘의 교집합은 없다. "
        "공격 스킬의 물리 피해는 스킬이 아니라 무기에서 오므로 게임 논리상 맞다 — "
        "공격 빌드의 원소는 무기/전환 보조를 봐야 정해진다."
    ),
    "channelled": "양성(Cyclone/Lightning Tendrils/Incinerate/Blade Flurry/Divine Ire) 공통 id 가 존재하지 않음",
    "trigger": "시드 정의 자체가 애매 — CoC/CWS 는 보조 젬이라 ActiveSkills 행이 아님",
}


def load_skill_types() -> dict[str, set[int]]:
    """DisplayedName → ActiveSkillTypes 집합. 같은 이름 중복 시 첫 행."""
    raw = json.loads(ACTIVE_SKILLS.read_text(encoding="utf-8"))
    rows = raw["rows"] if isinstance(raw, dict) and "rows" in raw else raw
    table: dict[str, set[int]] = {}
    for row in rows:
        name = (row.get("DisplayedName") or "").strip()
        if not name or name in table:
            continue
        table[name] = set(row.get("ActiveSkillTypes") or [])
    return table


def _members(table: dict[str, set[int]], type_id: int) -> list[str]:
    return sorted(name for name, types in table.items() if type_id in types)


def derive(table: dict[str, set[int]]) -> tuple[dict[str, int], list[str]]:
    """분리 id 도출. (category → id, 문제 목록)."""
    resolved: dict[str, int] = {}
    problems: list[str] = []

    for category, (positive, negative, preferred) in SEED_CASES.items():
        pos = [table[n] for n in positive if n in table]
        neg = [table[n] for n in negative if n in table]
        absent = [n for n in positive + negative if n not in table]
        if absent:
            problems.append(f"{category}: 시드가 GGPK 에 없음 {absent}")
            continue

        candidates = sorted(set.intersection(*pos) - set().union(*neg))
        if not candidates:
            problems.append(f"{category}: 분리 id 없음")
            continue
        if len(candidates) == 1:
            resolved[category] = candidates[0]
            continue
        if preferred is None:
            problems.append(f"{category}: 후보가 여럿인데 preferred 미지정 {candidates}")
            continue
        if preferred not in candidates:
            problems.append(f"{category}: preferred={preferred} 가 후보 {candidates} 에 없음")
            continue
        resolved[category] = preferred

    return resolved, problems


def build_payload(table: dict[str, set[int]], resolved: dict[str, int]) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "dataset_kind": "poe1_active_skill_type_ids",
        "description": (
            "GGPK ActiveSkills.ActiveSkillTypes 의 int id 를 의미로 역산한 결과. "
            "손으로 적은 값이 아니라 derive_active_skill_types.py 가 알려진 스킬 집합으로 매번 재도출한다."
        ),
        "derivation": "positive seeds intersection minus negative seeds union",
        "source_table": "data/game_data/ActiveSkills.json",
        "skills_with_display_name": len(table),
        "types": {
            category: {
                "id": type_id,
                "member_count": len(_members(table, type_id)),
                "sample": _members(table, type_id)[:5],
            }
            for category, type_id in sorted(resolved.items())
        },
        "unresolved": UNRESOLVED,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="data/active_skill_types.json 갱신")
    args = parser.parse_args(argv)

    table = load_skill_types()
    resolved, problems = derive(table)

    for problem in problems:
        logger.warning("%s", problem)

    payload = build_payload(table, resolved)
    if args.write:
        OUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        logger.info("wrote %s", OUT_PATH)

    for category, info in payload["types"].items():
        logger.info("%-11s id=%-4d members=%d", category, info["id"], info["member_count"])

    return 1 if problems else 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s", stream=sys.stderr)
    raise SystemExit(main())
