"""HC 리그 divination card T1/T2 override 자동 재생성 (poe.ninja API).

사용:
    python scripts/refresh_hc_divcard_tiers.py [--league "Hardcore Mirage"] [--dry-run]

출력: data/hc_divcard_tiers.json

새 스키마 (기존 Sanavi 8-key 폐기):
    {
      "_meta": {
        "source": "poe.ninja itemoverview",
        "league": "Hardcore Mirage",
        "collected_at": "2026-04-17T...",
        "script": "scripts/refresh_hc_divcard_tiers.py",
        "tier_rule": "percentile: top 5% = t1_override, next 10% = t2_override",
        "total_cards": 151
      },
      "t1_override": [...],  // HCSSF T1 승격 (keystone 블록)
      "t2_override": [...]   // HCSSF T2 승격 (core 블록)
    }

설계 근거:
- HC 경제에서 최상위 가격 카드는 SC와 다름 (생존/크래프팅 승격)
- 기존 SC 디비카 티어(neversink_filter_rules.json)는 베이스로 유지
- HCSSF 모드에서는 이 override만 SC 흐름 앞에 삽입 (gen_test_filter_v4 패턴)
- 백분위 컷이 고정 chaos 임계값보다 리그 간 안정적
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

logger = logging.getLogger("refresh_hc_divcard")
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s", stream=sys.stderr)

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "data" / "hc_divcard_tiers.json"

sys.path.insert(0, str(ROOT / "python"))
from poe_ninja_api import POENinjaAPI  # noqa: E402

DEFAULT_LEAGUE = "Hardcore Mirage"
T1_PERCENTILE = 0.05  # top 5%
T2_PERCENTILE = 0.15  # next 10% (누적 15%)


def compute_tier_overrides(
    cards: list[dict],
    t1_pct: float = T1_PERCENTILE,
    t2_pct: float = T2_PERCENTILE,
) -> tuple[list[str], list[str]]:
    """chaos_value 내림차순 정렬된 카드 리스트에서 백분위 컷으로 T1/T2 추출.

    가격 0인 카드는 제외 (poe.ninja가 집계 못 한 카드 = 거래량 없음 = 평균).
    """
    priced = [c for c in cards if c.get("chaos_value", 0) > 0]
    total = len(priced)
    if total == 0:
        return [], []

    t1_cut = max(1, int(total * t1_pct))
    t2_cut = max(1, int(total * t2_pct))
    t1 = [c["name"] for c in priced[:t1_cut]]
    t2 = [c["name"] for c in priced[t1_cut:t2_cut]]
    return t1, t2


def build_payload(league: str, cards: list[dict]) -> dict:
    t1, t2 = compute_tier_overrides(cards)
    return {
        "_meta": {
            "source": "poe.ninja itemoverview",
            "league": league,
            "collected_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "script": "scripts/refresh_hc_divcard_tiers.py",
            "tier_rule": (
                f"percentile: top {int(T1_PERCENTILE*100)}% = t1_override, "
                f"next {int((T2_PERCENTILE-T1_PERCENTILE)*100)}% = t2_override "
                "(chaos_value>0 카드 기준)"
            ),
            "total_cards": len(cards),
            "priced_cards": sum(1 for c in cards if c.get("chaos_value", 0) > 0),
        },
        "t1_override": t1,
        "t2_override": t2,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--league", default=DEFAULT_LEAGUE, help="poe.ninja 리그명")
    ap.add_argument("--dry-run", action="store_true", help="파일 쓰지 않고 결과만 출력")
    ap.add_argument("--no-cache", action="store_true", help="poe.ninja 캐시 무시")
    args = ap.parse_args()

    api = POENinjaAPI(league=args.league, use_cache=not args.no_cache)
    logger.info("Fetching divcards from poe.ninja (league=%s)...", args.league)
    cards = api.get_divcards()
    if not cards:
        logger.error("No divcards returned. Check league name or poe.ninja availability.")
        return 1

    payload = build_payload(args.league, cards)
    t1_count = len(payload["t1_override"])
    t2_count = len(payload["t2_override"])
    logger.info("Computed override: t1=%d, t2=%d (from %d priced / %d total)",
                t1_count, t2_count,
                payload["_meta"]["priced_cards"], payload["_meta"]["total_cards"])

    if args.dry_run:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("Wrote %s", OUTPUT.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
