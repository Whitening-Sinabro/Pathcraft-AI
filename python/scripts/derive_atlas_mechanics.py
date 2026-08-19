# -*- coding: utf-8 -*-
"""아틀라스 메커니즘 정본을 GGPK 에서 도출한다 — `PassiveSkills.AtlasGroup` 기준 42개.

왜 필요한가:
    `data/atlas_farming_knowledge.json` 은 10개만 알고 있고, 그중 `boss_rush` 는 GGPK 에
    없는 이름이다(The Maven / Shaper and Elder / Conquerors / Searing Exarch / Eater of
    Worlds 다섯을 한 덩어리로 뭉갠 것). 손으로 적은 목록이라 리그가 바뀌어도 아무도 모른다.

    이 스크립트가 만드는 파일은 **레포에서 `ggpk_fingerprint` 를 갖는 첫 파생 파일**이다.
    그 순간부터 `test_derived_data_inventory.py` 의 staleness 게이트가 공허를 벗어난다.

도출:
    `PassiveSkills.json` 에서 `AtlasGroup` 이 sentinel 이 아닌 행이 앵커다. 각 그룹의
    이름은 그 행들의 `Name` 에서 얻는다. 손으로 적지 않는다 — 매 실행 재도출한다.

`generated_at` 을 넣지 않는 이유:
    타임스탬프를 넣으면 데이터가 같아도 매 실행 파일 해시가 바뀌어, 인벤토리 핀이 계속
    흔들린다. 최신성 신호는 `ggpk_fingerprint` 가 이미 하고 있고, "언제" 는 git 이 안다.

실행:
    python python/scripts/derive_atlas_mechanics.py            # 검증만
    python python/scripts/derive_atlas_mechanics.py --write    # data/atlas_mechanics.json 갱신
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

logger = logging.getLogger("derive_atlas_mechanics")

ROOT = Path(__file__).resolve().parents[2]
PASSIVE_SKILLS = ROOT / "data" / "game_data" / "PassiveSkills.json"
OUT_PATH = ROOT / "data" / "atlas_mechanics.json"

# GGPK 가 "값 없음" 을 나타내는 값. 0 은 유효한 그룹(Abyss)이므로 falsy 검사로는 못 거른다.
SENTINEL = -72340172838076674

# 3.29 실측 그룹 수. 리그가 바뀌어 이 수가 달라지면 알아야 한다(테스트가 잡는다).
EXPECTED_GROUP_COUNT = 42


def load_anchor_rows() -> list[dict[str, Any]]:
    if not PASSIVE_SKILLS.exists():
        raise FileNotFoundError(
            f"{PASSIVE_SKILLS.relative_to(ROOT)} 없음. GGPK 추출을 먼저 할 것."
        )
    rows = json.loads(PASSIVE_SKILLS.read_text(encoding="utf-8"))
    return [r for r in rows if isinstance(r, dict) and r.get("AtlasGroup") not in (None, SENTINEL)]


def slugify(name: str) -> str:
    """이름 → 안정적인 키. 표시 이름이 바뀌어도 키가 흔들리지 않게 소문자 스네이크로."""
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def canonical_name(names: collections.Counter) -> str:
    """한 그룹에 이름이 여러 개면(`Map Boss` / `Map Bosses`) 최빈값, 동률이면 사전순.

    임의로 하나를 고르면 실행마다 달라져 핀이 흔들린다. 결정적이어야 한다.
    """
    top = max(names.values())
    return sorted(n for n, c in names.items() if c == top)[0]


def derive_mechanics(rows: list[dict[str, Any]]) -> dict[str, Any]:
    grouped: dict[int, list[dict[str, Any]]] = collections.defaultdict(list)
    for row in rows:
        grouped[row["AtlasGroup"]].append(row)

    mechanics: dict[str, Any] = {}
    for group_id in sorted(grouped):
        members = grouped[group_id]
        names = collections.Counter(r["Name"] for r in members if r.get("Name"))
        if not names:
            logger.warning("AtlasGroup %d: 이름 없는 그룹 — 건너뜀", group_id)
            continue
        name = canonical_name(names)
        mechanics[slugify(name)] = {
            "atlas_group": group_id,
            "name": name,
            "name_variants": sorted(names) if len(names) > 1 else [],
            "anchor_node_count": len(members),
            "anchor_node_ids": sorted(r["Id"] for r in members if r.get("Id")),
            "has_keystone": any(r.get("IsKeystone") for r in members),
            "has_notable": any(r.get("IsNotable") for r in members),
        }
    return mechanics


def build_payload() -> dict[str, Any]:
    rows = load_anchor_rows()
    mechanics = derive_mechanics(rows)
    return {
        "schema_version": 1,
        "dataset_kind": "poe1_atlas_mechanics",
        "generated_by": "python/scripts/derive_atlas_mechanics.py",
        "source_table": "data/game_data/PassiveSkills.json",
        "ggpk_fingerprint": ggpk_fingerprint(),
        "description": (
            "PassiveSkills.AtlasGroup 이 sentinel 이 아닌 행에서 도출한 아틀라스 메커니즘 정본. "
            "손으로 적은 값이 아니라 매 실행 재도출한다."
        ),
        "derivation": "PassiveSkills rows where AtlasGroup != sentinel, grouped by AtlasGroup",
        "sentinel": SENTINEL,
        "anchor_row_count": len(rows),
        "mechanic_count": len(mechanics),
        "mechanics": mechanics,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="아틀라스 메커니즘 도출")
    parser.add_argument("--write", action="store_true", help="data/atlas_mechanics.json 갱신")
    args = parser.parse_args(argv)

    payload = build_payload()
    if payload["mechanic_count"] != EXPECTED_GROUP_COUNT:
        logger.warning(
            "메커니즘 수 %d — 기대값 %d 과 다르다. 리그 변경이면 EXPECTED_GROUP_COUNT 를 갱신할 것.",
            payload["mechanic_count"], EXPECTED_GROUP_COUNT,
        )

    if args.write:
        OUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        logger.info("wrote %s", OUT_PATH.relative_to(ROOT))

    logger.info("메커니즘 %d개 / 앵커 행 %d개 / 지문 %s",
                payload["mechanic_count"], payload["anchor_row_count"], payload["ggpk_fingerprint"])
    for key, info in payload["mechanics"].items():
        logger.debug("  %-24s grp=%-3d nodes=%d", key, info["atlas_group"], info["anchor_node_count"])
    return 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s", stream=sys.stderr)
    raise SystemExit(main())
