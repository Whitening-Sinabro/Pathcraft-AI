"""
POE2 base_items_poe2.json 생성 — GGPK BaseItemTypes.json 분류/정제.

입력:
  - data/game_data_poe2/BaseItemTypes.json     : 4269 rows 전체 아이템 베이스
  - data/game_data_poe2/AttributeRequirements.json : (선택) BaseItemType → ReqStr/Dex/Int
                                                     존재 시 무기/방어구 entry 에 req_* 필드 부착

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


def load_optional(name: str) -> list[dict] | None:
    """테이블이 아직 GGPK 추출되지 않았으면 None 반환 (graceful degradation)."""
    path = POE2_ROOT / name
    if not path.exists():
        return None
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def build_attribute_requirements(
    rows: list[dict] | None,
) -> dict[int, dict[str, int]]:
    """AttributeRequirements 행을 BaseItemType (int 인덱스) → {req_str, req_dex, req_int} 매핑.

    AttributeRequirements 스키마 (POE2 validFor=2):
      - BaseItemType: foreignrow → BaseItemTypes 인덱스 (int)
      - ReqStr / ReqDex / ReqInt: i32

    None / 빈 리스트 → 빈 dict (graceful). BaseItemType 이 int 가 아닌 행은 건너뜀.
    """
    if not rows:
        return {}
    mapping: dict[int, dict[str, int]] = {}
    for row in rows:
        key = row.get("BaseItemType")
        if not isinstance(key, int) or key < 0:
            continue
        req_str = row.get("ReqStr")
        req_dex = row.get("ReqDex")
        req_int = row.get("ReqInt")
        if not all(isinstance(v, int) for v in (req_str, req_dex, req_int)):
            continue
        if req_str == 0 and req_dex == 0 and req_int == 0:
            # 요구치 0 0 0 은 base 없음과 동치 — 매핑 미부착으로 단순화.
            continue
        mapping[key] = {
            "req_str": req_str,
            "req_dex": req_dex,
            "req_int": req_int,
        }
    return mapping


def is_dnt(item: dict) -> bool:
    """DNT 마커 + 빈 이름 필터."""
    name = (item.get("Name") or "").strip()
    if not name:
        return True
    return any(m in name for m in DNT_NAME_MARKERS)


def simplify(
    item: dict,
    base_index: int | None = None,
    attr_req: dict[int, dict[str, int]] | None = None,
) -> dict:
    """core 필드만 유지 — 코치/UI 에 필요한 minimal projection.

    attr_req 매핑이 주어지면 base_index 로 조회해 req_str/req_dex/req_int 부착.
    매핑에 없거나 attr_req 가 None 이면 req_* 필드 자체 생략 (graceful).
    """
    out = {
        "id": item.get("Id", ""),
        "name": item.get("Name", ""),
        "drop_level": item.get("DropLevel", 0),
        "width": item.get("Width", 0),
        "height": item.get("Height", 0),
        "tags": item.get("Tags", []),
    }
    if attr_req and base_index is not None:
        req = attr_req.get(base_index)
        if req:
            out["req_str"] = req["req_str"]
            out["req_dex"] = req["req_dex"]
            out["req_int"] = req["req_int"]
    return out


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

    attr_req_rows = load_optional("AttributeRequirements.json")
    attr_req = build_attribute_requirements(attr_req_rows)
    if attr_req_rows is not None:
        logger.info(
            "AttributeRequirements: %d rows (매핑 %d)",
            len(attr_req_rows), len(attr_req),
        )
    else:
        logger.info(
            "AttributeRequirements.json 없음 — req_str/req_dex/req_int 생략 "
            "(다음 GGPK 추출 후 자동 반영)",
        )

    weapons: dict[str, list[dict]] = defaultdict(list)
    armours: dict[str, list[dict]] = defaultdict(list)
    other: dict[str, list[dict]] = defaultdict(list)
    filtered = 0

    for idx, item in enumerate(base_items):
        if is_dnt(item):
            filtered += 1
            continue
        inherits = item.get("InheritsFrom", "")
        item_id = item.get("Id", "")

        w = weapon_class(inherits)
        if w:
            weapons[w].append(simplify(item, base_index=idx, attr_req=attr_req))
            continue
        a = armour_class(inherits)
        if a:
            armours[a].append(simplify(item, base_index=idx, attr_req=attr_req))
            continue
        o = other_class(inherits, item_id)
        if o:
            other[o].append(simplify(item, base_index=idx, attr_req=attr_req))
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

    meta: dict = {
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
    }
    if attr_req:
        meta["source"] = "GGPK BaseItemTypes + AttributeRequirements JOIN"
        meta["attribute_requirements_count"] = len(attr_req)
    out = {
        "_meta": meta,
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
