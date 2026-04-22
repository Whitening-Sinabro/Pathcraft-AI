"""
POE2 base_items_poe2.json 생성 — GGPK BaseItemTypes.json 분류/정제.

입력:
  - data/game_data_poe2/BaseItemTypes.json : 4269 rows 전체 아이템 베이스

출력:
  - data/base_items_poe2.json : 무기/방어구/기타 카테고리로 분류, DNT/UNUSED/Hidden 제외

카테고리:
  - weapons (14 classes): OneHandWeapons/<class>, TwoHandWeapons/<class>
  - armours (6 classes): BodyArmours, Helmets, Gloves, Shields, Boots, Focus
  - other: Quivers, Rings, Belts, Amulets, Flasks, Jewels, Charms (Metadata/Items/Flasks/FourCharm*)

필터:
  - Name 이 "[DNT]", "[UNUSED]", "Hidden Item", "Convention Treasure" 류 DNT 마커 포함 시 제외
  - InheritsFrom 경로가 존재하지 않는 row 제외
"""
from __future__ import annotations

import json
import logging
from collections import defaultdict
from pathlib import Path

logger = logging.getLogger(__name__)

POE2_ROOT = Path(__file__).resolve().parents[1] / "data" / "game_data_poe2"
OUTPUT = Path(__file__).resolve().parents[1] / "data" / "base_items_poe2.json"

# DNT / 숨김 / 잔존 POE1 패턴 (Name 기준)
DNT_NAME_MARKERS = (
    "[DNT]",
    "[UNUSED]",
    "Hidden Item",
    "Convention Treasure",
    "Singing Rod",  # POE1 Heist, POE2 미사용
)


def load(name: str) -> list[dict]:
    with (POE2_ROOT / name).open(encoding="utf-8") as f:
        return json.load(f)


def is_dnt(item: dict) -> bool:
    """DNT 마커 + 빈 이름 필터."""
    name = (item.get("Name") or "").strip()
    if not name:
        return True
    return any(m in name for m in DNT_NAME_MARKERS)


def simplify(item: dict) -> dict:
    """core 필드만 유지 — 코치/UI 에 필요한 minimal projection."""
    return {
        "id": item.get("Id", ""),
        "name": item.get("Name", ""),
        "drop_level": item.get("DropLevel", 0),
        "width": item.get("Width", 0),
        "height": item.get("Height", 0),
        "tags": item.get("Tags", []),
    }


def weapon_class(inherits: str) -> str | None:
    """Metadata/Items/Weapons/OneHandWeapons/Spears → Spears"""
    parts = inherits.split("/")
    if len(parts) >= 5 and parts[2] == "Weapons":
        return parts[4]
    return None


def armour_class(inherits: str) -> str | None:
    """Metadata/Items/Armours/BodyArmours → BodyArmours"""
    parts = inherits.split("/")
    if len(parts) >= 4 and parts[2] == "Armours":
        return parts[3]
    return None


def other_class(inherits: str, item_id: str) -> str | None:
    """기타 카테고리 — Quivers/Rings/Belts/Amulets/Flasks/Jewels/Charms."""
    # Charms (FourCharm 1~4) — POE2 특수
    if "Flasks/FourCharm" in item_id:
        return "Charms"
    parts = inherits.split("/")
    if len(parts) < 3:
        return None
    top = parts[2]
    mapping = {
        "Quivers": "Quivers",
        "Rings": "Rings",
        "Belts": "Belts",
        "Amulets": "Amulets",
        "Flasks": "Flasks",
        "Jewels": "Jewels",
    }
    return mapping.get(top)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    base_items = load("BaseItemTypes.json")
    logger.info("BaseItemTypes: %d rows", len(base_items))

    weapons: dict[str, list[dict]] = defaultdict(list)
    armours: dict[str, list[dict]] = defaultdict(list)
    other: dict[str, list[dict]] = defaultdict(list)
    filtered = 0

    for item in base_items:
        if is_dnt(item):
            filtered += 1
            continue
        inherits = item.get("InheritsFrom", "")
        item_id = item.get("Id", "")

        w = weapon_class(inherits)
        if w:
            weapons[w].append(simplify(item))
            continue
        a = armour_class(inherits)
        if a:
            armours[a].append(simplify(item))
            continue
        o = other_class(inherits, item_id)
        if o:
            other[o].append(simplify(item))
            continue
        # 기타 (Currency, Gems, Maps, Quest 등) — base_items scope 외
        filtered += 1

    # 각 카테고리 내 drop_level 순 정렬
    for cat in (weapons, armours, other):
        for k in cat:
            cat[k].sort(key=lambda x: (x["drop_level"], x["name"]))

    weapon_total = sum(len(v) for v in weapons.values())
    armour_total = sum(len(v) for v in armours.values())
    other_total = sum(len(v) for v in other.values())

    out = {
        "_meta": {
            "source": "GGPK BaseItemTypes.datc64 → JSON",
            "game": "poe2",
            "generator": "scripts/build_base_items_poe2.py",
            "total_weapons": weapon_total,
            "total_armours": armour_total,
            "total_other": other_total,
            "weapon_classes": sorted(weapons.keys()),
            "armour_classes": sorted(armours.keys()),
            "other_classes": sorted(other.keys()),
            "filtered_dnt_or_nonbase": filtered,
        },
        "weapons": {k: weapons[k] for k in sorted(weapons.keys())},
        "armours": {k: armours[k] for k in sorted(armours.keys())},
        "other": {k: other[k] for k in sorted(other.keys())},
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(out, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    logger.info(
        "base_items_poe2.json 생성 — 무기 %d (%d classes) / 방어구 %d (%d classes) / 기타 %d (%d classes) / 제외 %d",
        weapon_total, len(weapons), armour_total, len(armours), other_total, len(other), filtered,
    )
    logger.info("weapon classes: %s", sorted(weapons.keys()))
    logger.info("armour classes: %s", sorted(armours.keys()))
    logger.info("other classes: %s", sorted(other.keys()))


if __name__ == "__main__":
    main()
