# -*- coding: utf-8 -*-
"""Sanavi/NeverSink 필터에서 실제 tier 데이터 추출.

neversink_filter_rules.json 에 없는 카테고리(uniques, gems, jewels, fragments 등)도
Sanavi 필터 파일 자체에 `$type->X $tier->Y` 주석 + BaseType 리스트로 인코딩돼 있다.
이 파서는 그 데이터를 카테고리×티어별로 뽑아 dict 로 반환한다.

출력 형식:
    {
        "uniques": {
            "t1": ["Headhunter", "Mageblood", ...],
            "t2": ["Shavronne's Wrappings", ...],
            ...
        },
        "gems": {"t1": [...], ...},
        "jewels": {...},
        "fragments": {...},
    }
"""
import re
import json
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

POE_FILTER_DIR = Path.home() / "Documents" / "My Games" / "Path of Exile"
DEFAULT_SANAVI = POE_FILTER_DIR / "Sanavi_3_Strict.filter"


def parse_tier_data(filter_path: Optional[Path] = None) -> dict[str, dict[str, list[str]]]:
    """Sanavi 필터에서 카테고리×티어별 BaseType 리스트 추출."""
    if filter_path is None:
        filter_path = DEFAULT_SANAVI
    if not filter_path.exists():
        raise FileNotFoundError(f"Sanavi filter not found: {filter_path}")

    with open(filter_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Show/Hide 블록 추출
    block_pattern = re.compile(
        r'((?:Show|Hide)[^\n]*\n(?:\t[^\n]*\n?)+)'
    )
    blocks = block_pattern.findall(content)

    # 카테고리 → 티어 → BaseType 리스트
    tier_data: dict[str, dict[str, list[str]]] = {}

    for block in blocks:
        # $type->X $tier->Y 추출
        type_match = re.search(r'\$type->([a-zA-Z0-9_\->]+)', block)
        tier_match = re.search(r'\$tier->([a-zA-Z0-9_]+)', block)
        if not type_match:
            continue
        full_type = type_match.group(1)
        top_type = full_type.split('->')[0]  # "uniques->high" → "uniques"
        tier_id = tier_match.group(1) if tier_match else "any"

        # BaseType == "X" "Y" "Z" 추출
        basetype_match = re.search(r'BaseType\s*(?:==\s*)?(.+)', block)
        if not basetype_match:
            continue
        basetype_line = basetype_match.group(1).strip()

        # 큰따옴표로 둘러싸인 값 추출
        names = re.findall(r'"([^"]+)"', basetype_line)
        if not names:
            continue

        tier_data.setdefault(top_type, {}).setdefault(tier_id, []).extend(names)

    # 중복 제거 & 정렬
    for cat in tier_data:
        for tier in tier_data[cat]:
            tier_data[cat][tier] = sorted(set(tier_data[cat][tier]))

    return tier_data


def save_cache(data: dict, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    logger.info("Saved tier data: %s (%d categories)", out_path, len(data))


def load_cache(cache_path: Path) -> Optional[dict]:
    if not cache_path.exists():
        return None
    with open(cache_path, "r", encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    logging.basicConfig(level=logging.INFO)

    data = parse_tier_data()
    print(f"추출된 카테고리: {len(data)}")
    for cat in sorted(data.keys()):
        tier_count = len(data[cat])
        total_items = sum(len(v) for v in data[cat].values())
        print(f"  {cat:30} : {tier_count:3} tiers, {total_items:5} items")

    # 관심 카테고리 상세
    print("\n=== 주요 카테고리 티어별 아이템 수 ===")
    for cat in ("uniques", "gems", "jewels", "fragments", "divination", "currency"):
        if cat not in data:
            continue
        print(f"\n{cat}:")
        for tier in sorted(data[cat].keys()):
            items = data[cat][tier]
            print(f"  {tier:25} : {len(items):4} items  예: {items[:3]}")

    # 캐시 저장
    cache_path = Path(__file__).parent.parent / "data" / "sanavi_tier_data.json"
    save_cache(data, cache_path)
