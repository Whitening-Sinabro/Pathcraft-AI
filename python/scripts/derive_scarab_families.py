# -*- coding: utf-8 -*-
"""갑충석 계열 정본을 GGPK 에서 도출한다 — 28계열 / 현행 130종 / 비현행 68종.

왜 필요한가:
    `Metadata/Items/Scarabs/` 네임스페이스에는 198개가 있고 `Scarabs` 테이블이 계열로
    묶는 것은 130개뿐이다. 남은 68개를 "미분류 — 리서치 필요"로 두면, 필터나 전략이
    이미 게임에서 빠진 갑충석을 계속 취급하게 된다.

68개의 정체(GGPK 구조만으로 판명):
    - 64개 = 구 티어 체계. `{Rusted|Polished|Gilded|Winged} × 16계열` 로 정확히 4×16 이며,
      현행 `Scarabs` 계열 어디에도 안 들어간다. 현행 130개에는 티어 접두사가 하나도 없다.
    - 4개 = 구 Bestiary Lure. 갑충석 네임스페이스와 상속 루트에는 있으나 현행
      `Scarabs.Items` 에 없고 `scarab` 태그도 비어 있다.
    (언제 빠졌는지는 이 레포로 말할 수 없다 — `data/patch_notes/` 는 3.25 부터다.)

아틀라스 메커니즘 조인:
    `ScarabTypes.Id` 를 `data/atlas_mechanics.json` 의 키에 기계적으로 붙인다. 못 붙는
    계열은 지어내지 않고 `unmapped_to_atlas_mechanic` 에 사유와 함께 남긴다.

실행:
    python python/scripts/derive_scarab_families.py            # 검증만
    python python/scripts/derive_scarab_families.py --write    # data/scarab_families.json 갱신
"""

from __future__ import annotations

import argparse
import collections
import json
import logging
import re
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from derived_data_inventory import ggpk_fingerprint  # noqa: E402

logger = logging.getLogger("derive_scarab_families")

ROOT = Path(__file__).resolve().parents[2]
GAME_DATA = ROOT / "data" / "game_data"
ATLAS_MECHANICS = ROOT / "data" / "atlas_mechanics.json"
OUT_PATH = ROOT / "data" / "scarab_families.json"

# 구 티어 체계의 접두사. 현행 갑충석에는 하나도 안 쓰인다(테스트가 고정).
LEGACY_TIERS = ("Rusted", "Polished", "Gilded", "Winged")
LEGACY_PREFIX = re.compile(rf"^({'|'.join(LEGACY_TIERS)}) ")

# 갑충석의 상속 루트. 이게 아니면 이름에 'Scarab' 이 있어도 갑충석이 아니다.
SCARAB_INHERITS = "Metadata/Items/MapFragments/AbstractMapFragment"

# 아틀라스 앵커 노드 id 에서 메커니즘 토큰을 뽑는 두 패턴.
ANCHOR_TOKEN = (
    re.compile(r"^atlas_mastery_(.+?)_\d+$"),
    re.compile(r"^atlas_(.+?)_mastery_\d+$"),
)

# 기계적으로 못 붙는 계열 — 지어내지 않고 사유를 남긴다.
UNMAPPABLE_REASONS = {
    "Influence": "영향(Shaper/Elder/Conqueror) 갑충석. 아틀라스 그룹은 이 축으로 안 쪼개져 있다",
    "Misc": "단일 메커니즘이 아니다 — Monstrous Lineage / Adversaries 등 잡다한 효과 묶음",
    "Uber": "Horned 계열(정점 보스). 아틀라스에 대응하는 단일 그룹이 없다",
    "Uniques": (
        "Titanic/Reliquary 갑충석은 유니크 몬스터·아이템용이다. "
        "아틀라스의 Unique Maps 그룹과 의미가 달라 조인하지 않는다"
    ),
}

EXPECTED = {"families": 28, "active_variants": 130, "retired": 68}

SCARAB_NAMESPACE = "Metadata/Items/Scarabs/"
SCARAB_TAG_ID = "scarab"


def load_table(name: str) -> list[dict[str, Any]]:
    path = GAME_DATA / f"{name}.json"
    if not path.exists():
        raise FileNotFoundError(f"{path.relative_to(ROOT)} 없음. GGPK 추출을 먼저 할 것.")
    return json.loads(path.read_text(encoding="utf-8"))


def slugify(name: str) -> str:
    """CamelCase 도 쪼갠다 — `DivinationCards` → `divination_cards`."""
    spaced = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", name)
    return re.sub(r"[^a-z0-9]+", "_", spaced.lower()).strip("_")


def atlas_mechanic_index() -> dict[str, str]:
    """아틀라스 메커니즘 키를 조인 가능한 토큰들로 펼친다.

    앵커 노드 id 에 내부 이름이 박혀 있다(`atlas_mastery_anarchy_1` = Rogue Exiles).
    표시 이름만 보면 Anarchy↔Rogue Exiles, Domination↔Shrines 를 절대 못 붙인다.
    """
    if not ATLAS_MECHANICS.exists():
        raise FileNotFoundError(
            f"{ATLAS_MECHANICS.relative_to(ROOT)} 없음. "
            "python/scripts/derive_atlas_mechanics.py --write 를 먼저 실행할 것."
        )
    mechanics = json.loads(ATLAS_MECHANICS.read_text(encoding="utf-8"))["mechanics"]
    index: dict[str, str] = {}
    for key, info in mechanics.items():
        index.setdefault(key, key)
        for node_id in info["anchor_node_ids"]:
            for pattern in ANCHOR_TOKEN:
                match = pattern.match(node_id)
                if match:
                    index.setdefault(match.group(1), key)
    return index


def join_to_mechanic(scarab_type_id: str, index: dict[str, str]) -> str | None:
    """단수/복수 흔들림만 흡수한다. 그 이상은 추측이라 하지 않는다."""
    if scarab_type_id in UNMAPPABLE_REASONS:
        return None
    slug = slugify(scarab_type_id)
    singular = slug[:-1] if slug.endswith("s") else slug
    for candidate in (slug, singular, f"{slug}s", slug.replace("_", "")):
        if candidate in index:
            return index[candidate]
    return None


def derive_families(scarabs, scarab_types, base_items, tags, index) -> dict[str, Any]:
    families: dict[str, Any] = {}
    for row in sorted(scarabs, key=lambda r: r["Type"]):
        type_index = row["Type"]
        meta = scarab_types[type_index]
        tag = tags[meta["Tag"]].get("Id") if 0 <= meta["Tag"] < len(tags) else None
        variants = [base_items[i]["Name"] for i in row["Items"] if 0 <= i < len(base_items)]
        families[slugify(meta["Id"])] = {
            "type_index": type_index,
            "scarab_type_id": meta["Id"],
            "tag": tag,
            "atlas_mechanic": join_to_mechanic(meta["Id"], index),
            "variant_count": len(variants),
            "variants": sorted(variants),
        }
    return families


def scarab_universe_indices(base_items, tags) -> set[int]:
    """이름이 아니라 GGPK 구조로 갑충석 후보 우주를 정의한다.

    현행 데이터에서 `scarab` 태그는 194개를 잡지만 Bestiary Lure 4개에는 비어 있다.
    네임스페이스와 태그의 합집합을 써야 두 신호 중 하나가 흔들려도 누락이 드러난다.
    """
    scarab_tag_indices = {
        i for i, tag in enumerate(tags) if tag.get("Id") == SCARAB_TAG_ID
    }
    if not scarab_tag_indices:
        raise ValueError("Tags.json 에 scarab 태그가 없다")
    return {
        i for i, item in enumerate(base_items)
        if item.get("Id", "").startswith(SCARAB_NAMESPACE)
        or bool(scarab_tag_indices.intersection(item.get("TagsKeys", [])))
    }


def derive_retired(scarabs, base_items, tags) -> dict[str, Any]:
    """현행 계열에 안 들어간 것들을 버리지 않고 정체를 밝혀 남긴다."""
    classified = {i for row in scarabs for i in row["Items"]}
    universe = scarab_universe_indices(base_items, tags)
    leftover = [
        (i, base_items[i]["Name"]) for i, item in enumerate(base_items)
        if i in universe and i not in classified
    ]

    legacy = collections.defaultdict(list)
    other_retired = []
    for index, name in leftover:
        match = LEGACY_PREFIX.match(name)
        if match and base_items[index].get("InheritsFrom") == SCARAB_INHERITS:
            legacy[LEGACY_PREFIX.sub("", name)].append(match.group(1))
        else:
            other_retired.append({
                "name": name,
                "id": base_items[index].get("Id"),
                "inherits_from": base_items[index].get("InheritsFrom"),
                "reason": (
                    "갑충석 네임스페이스에 있으나 현행 Scarabs.Items 계열에 없고 "
                    "구 티어 접두사도 없다"
                ),
            })

    return {
        "legacy_tier_scarabs": {
            "count": sum(len(v) for v in legacy.values()),
            "tiers": list(LEGACY_TIERS),
            "family_count": len(legacy),
            "families": {name: sorted(tiers) for name, tiers in sorted(legacy.items())},
            "note": (
                "구 티어 체계. 현행 Scarabs 계열 어디에도 없고 현행 130종에는 티어 접두사가 "
                "하나도 없다. 언제 빠졌는지는 이 레포로 말할 수 없다(patch_notes 는 3.25 부터)."
            ),
        },
        "other_retired_scarabs": sorted(other_retired, key=lambda x: x["name"]),
    }


def build_payload() -> dict[str, Any]:
    scarabs = load_table("Scarabs")
    scarab_types = load_table("ScarabTypes")
    base_items = load_table("BaseItemTypes")
    tags = load_table("Tags")
    index = atlas_mechanic_index()

    families = derive_families(scarabs, scarab_types, base_items, tags, index)
    retired = derive_retired(scarabs, base_items, tags)
    unmapped = {
        key: UNMAPPABLE_REASONS.get(info["scarab_type_id"], "사유 미기재 — 조사 필요")
        for key, info in families.items() if info["atlas_mechanic"] is None
    }

    return {
        "schema_version": 2,
        "dataset_kind": "poe1_scarab_families",
        "generated_by": "python/scripts/derive_scarab_families.py",
        "source_tables": [
            "data/game_data/Scarabs.json",
            "data/game_data/ScarabTypes.json",
            "data/game_data/BaseItemTypes.json",
            "data/game_data/Tags.json",
        ],
        "ggpk_fingerprint": ggpk_fingerprint(),
        "description": (
            "Scarabs.Type → ScarabTypes 계열, Scarabs.Items → BaseItemTypes 변형으로 도출. "
            "갑충석 우주는 Metadata/Items/Scarabs/ 네임스페이스와 scarab 태그의 합집합이다. "
            "아틀라스 메커니즘 조인은 앵커 노드 id 의 내부 토큰을 쓴다(Anarchy=Rogue Exiles)."
        ),
        "family_count": len(families),
        "active_variant_count": sum(f["variant_count"] for f in families.values()),
        "retired_count": (
            retired["legacy_tier_scarabs"]["count"]
            + len(retired["other_retired_scarabs"])
        ),
        "families": families,
        "unmapped_to_atlas_mechanic": unmapped,
        "retired": retired,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="갑충석 계열 도출")
    parser.add_argument("--write", action="store_true", help="data/scarab_families.json 갱신")
    args = parser.parse_args(argv)

    payload = build_payload()
    measured = {
        "families": payload["family_count"],
        "active_variants": payload["active_variant_count"],
        "retired": payload["retired_count"],
    }
    for key, expected in EXPECTED.items():
        if measured[key] != expected:
            logger.warning("%s %d — 기대값 %d 과 다르다. 리그 변경이면 EXPECTED 를 갱신할 것.",
                           key, measured[key], expected)

    if args.write:
        OUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        logger.info("wrote %s", OUT_PATH.relative_to(ROOT))

    mapped = sum(1 for f in payload["families"].values() if f["atlas_mechanic"])
    logger.info("계열 %d / 현행 변형 %d / 폐기 %d / 지문 %s",
                measured["families"], measured["active_variants"], measured["retired"],
                payload["ggpk_fingerprint"])
    logger.info("아틀라스 메커니즘 매핑 %d/%d — 미매핑: %s",
                mapped, measured["families"], ", ".join(payload["unmapped_to_atlas_mechanic"]) or "없음")
    return 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s", stream=sys.stderr)
    raise SystemExit(main())
