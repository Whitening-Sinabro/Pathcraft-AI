"""특정 아이템이 SC·HC 양쪽 리그에 실제로 매물이 있는지 확인하는 탐침.

제품은 거래 API 를 호출하지 않는다(무상태 `?q=` 링크가 표면). 이 스크립트는
"그 아이템이 진짜 시장에 있나"를 사람이 확인할 때만 쓰는 검증 도구다.

예의:
  * 호출 사이 간격을 둔다(기본 2초). 429 면 Retry-After 를 그대로 따른다.
  * 결과는 조회 시각을 붙인 스냅샷이다. 매물 수는 시시각각 바뀐다.
  * 공식 User-Agent 에 연락처를 남긴다.

사용:
    python -X utf8 scripts/probe_trade_listings.py
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

log = logging.getLogger("trade-probe")

UA = ("PathcraftAI/0.1 (+https://github.com/Whitening-Sinabro/Pathcraft-AI; "
      "contact: vnddns999@gmail.com)")
HOST = "https://www.pathofexile.com"
LEAGUES = ["Forbidden Rites", "HC Forbidden Rites"]

# 이름 = 사람이 읽을 라벨, query = 공식 trade2 검색 본문
PROBES: dict[str, dict] = {
    "비행의 법령 (고유 장화)": {
        "query": {"status": {"option": "securable"},
                  "name": "Decree of Flight",
                  "stats": [{"type": "and", "filters": []}]},
        "sort": {"price": "asc"},
    },
    "변이하는 별 (고유 몸통)": {
        "query": {"status": {"option": "securable"},
                  "name": "The Mutable Star",
                  "stats": [{"type": "and", "filters": []}]},
        "sort": {"price": "asc"},
    },
}


def post(url: str, body: dict) -> dict:
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={
        "User-Agent": UA, "Accept": "application/json", "Content-Type": "application/json"})
    for attempt in range(1, 4):
        try:
            with urllib.request.urlopen(req, timeout=40) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            if exc.code == 429:
                wait = int(exc.headers.get("Retry-After") or 60)
                log.warning("429 — Retry-After %d초 대기", wait)
                time.sleep(wait)
                continue
            body_txt = exc.read().decode("utf-8", "replace")[:200]
            raise SystemExit(f"HTTP {exc.code}: {body_txt}")
    raise SystemExit("429 가 계속된다 — 나중에 다시")


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s", stream=sys.stdout)
    ap = argparse.ArgumentParser()
    ap.add_argument("--gap", type=float, default=2.0, help="호출 사이 간격(초)")
    ap.add_argument("--out", default="deliverables/trade_probe")
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    rows = []

    for label, payload in PROBES.items():
        for league in LEAGUES:
            url = f"{HOST}/api/trade2/search/poe2/{urllib.parse.quote(league)}"
            res = post(url, payload)
            total = res.get("total")
            sid = res.get("id")
            link = f"{HOST}/trade2/search/poe2/{urllib.parse.quote(league)}/{sid}" if sid else None
            log.info("%-22s %-20s 매물 %s", label, league, total)
            rows.append({"label": label, "league": league, "total": total,
                         "search_id": sid, "link": link, "checked_utc": stamp})
            time.sleep(args.gap)

    dest = out / f"listings_{stamp.replace(':', '').replace('-', '')[:15]}.json"
    dest.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    log.info("저장: %s", dest)
    return 0


if __name__ == "__main__":
    sys.exit(main())
