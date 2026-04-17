"""유니크 → base_item 매핑 자동 재생성 (poewiki.net Cargo API).

사용:
    python scripts/refresh_unique_base_mapping.py [--dry-run]

출력: data/unique_base_mapping.json (_meta + unique_to_base 전체)

동작:
1. Wiki Cargo `items` 테이블에서 `rarity="Unique"` + `base_item IS NOT NULL` 쿼리
2. 페이지네이션(limit 500, offset 증가)으로 전수 수집
3. 기존 수동 매핑과 diff 출력 (dry-run 모드)
4. 실제 기록 시 `_meta.collected_at` 갱신 + 수동 엔트리 보존

Wiki Cargo 제약:
- `stack_size` 필드는 MW exception 발생 (스키마 미정의)
- `base_item IS NOT NULL` 필터로 레거시/변형 유니크 제외 (Map 기반 유니크 등은 포함됨)
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from pathlib import Path

import requests

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

logger = logging.getLogger("refresh_unique_base")
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s", stream=sys.stderr)

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "data" / "unique_base_mapping.json"
WIKI_API = "https://www.poewiki.net/w/api.php"
HEADERS = {"User-Agent": "PathcraftAI/1.0 refresh_unique_base"}
PAGE_SIZE = 500


def fetch_page(offset: int) -> list[dict]:
    params = {
        "action": "cargoquery",
        "tables": "items",
        "fields": "items.name,items.base_item,items.is_drop_restricted",
        "where": (
            'items.rarity="Unique" AND items.base_item IS NOT NULL '
            'AND items.is_drop_restricted="0"'
        ),
        "format": "json",
        "limit": str(PAGE_SIZE),
        "offset": str(offset),
    }
    r = requests.get(WIKI_API, params=params, headers=HEADERS, timeout=30)
    r.raise_for_status()
    data = r.json()
    if "error" in data:
        raise RuntimeError(f"Wiki API error: {data['error']}")
    return [item["title"] for item in data.get("cargoquery", [])]


def fetch_all() -> list[dict]:
    all_rows: list[dict] = []
    offset = 0
    while True:
        batch = fetch_page(offset)
        if not batch:
            break
        all_rows.extend(batch)
        logger.info("fetched offset=%d batch=%d total=%d", offset, len(batch), len(all_rows))
        if len(batch) < PAGE_SIZE:
            break
        offset += PAGE_SIZE
        time.sleep(0.3)  # rate-limit courtesy
    return all_rows


def build_mapping(rows: list[dict]) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for row in rows:
        name = (row.get("name") or "").strip()
        base = (row.get("base item") or "").strip()
        if not name or not base:
            continue
        # 중복 유니크명 방어 (리그 변형 등)
        if name in mapping and mapping[name] != base:
            logger.warning("duplicate unique %r: %r vs %r (keeping first)", name, mapping[name], base)
            continue
        mapping[name] = base
    return dict(sorted(mapping.items()))


def diff_against_existing(new: dict[str, str]) -> tuple[list[str], list[str], list[tuple[str, str, str]]]:
    """existing과 비교. (added, removed, changed) 반환."""
    if not OUTPUT.exists():
        return list(new.keys()), [], []
    existing_raw = json.loads(OUTPUT.read_text(encoding="utf-8"))
    existing = existing_raw.get("unique_to_base", {})
    added = sorted(set(new) - set(existing))
    removed = sorted(set(existing) - set(new))
    changed = [(k, existing[k], new[k]) for k in existing if k in new and existing[k] != new[k]]
    return added, removed, changed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="diff만 출력하고 파일 쓰지 않음")
    args = parser.parse_args()

    logger.info("fetching uniques from %s", WIKI_API)
    rows = fetch_all()
    logger.info("raw rows: %d", len(rows))

    mapping = build_mapping(rows)
    logger.info("deduplicated mapping: %d entries", len(mapping))

    added, removed, changed = diff_against_existing(mapping)
    logger.info("added=%d removed=%d changed=%d", len(added), len(removed), len(changed))
    if added[:10]:
        logger.info("sample added: %s", added[:10])
    if removed[:10]:
        logger.info("sample removed: %s", removed[:10])
    for name, old_base, new_base in changed[:10]:
        logger.info("changed %r: %r -> %r", name, old_base, new_base)

    if args.dry_run:
        logger.info("dry-run: 파일 기록 생략")
        return 0

    from datetime import date
    payload = {
        "_meta": {
            "source": "poewiki.net Cargo API (items table)",
            "source_query": 'rarity="Unique" AND base_item IS NOT NULL',
            "version": "auto-refreshed",
            "collected_at": date.today().isoformat(),
            "script": "scripts/refresh_unique_base_mapping.py",
            "notes": f"전수 자동 수집. {len(mapping)} 엔트리 (is_drop_restricted=0, chanceable only). 리그 변형 유니크(Combat Focus/Grand Spectrum/Precursor's Emblem 등)는 첫 변형만 유지.",
        },
        "unique_to_base": mapping,
    }
    OUTPUT.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    logger.info("wrote %s (%d entries)", OUTPUT, len(mapping))
    return 0


if __name__ == "__main__":
    sys.exit(main())
