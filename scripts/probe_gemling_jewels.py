"""화염파 젬링 주얼을 등급별(중/상/최상) 거래소 검색으로 낸다.

**등급 기준을 지어내지 않는다.** 임성빈 Lv97 실캐릭이 실제로 끼고 있는 사파이어 주얼 8개의
분포가 앵커다(`.tmp/sb_track/snapshots/lv97_*.json`):

    최대 ES        10 · 11 · 14 · 16 · 18 · 18 · 20   (8개 중 7개)
    카오스 피해    10 · 11 · 12 · 12 · 13             (5개)
    인화성 강도    15 · 16 · 18                       (3개)
    주문 피해      11 · 12                            (2개 — 검은 화염 전환 전 잔재)

  중옵  = 그가 낀 하한       상옵 = 그의 중앙값 이상      최상옵 = 그의 최고 + 세 줄 다
  ("셋 다 붙은 건 1개뿐" — 본인 발언, `.claude/status/poe2_hc_gemling.md`)

축이 둘이다. 검은 화염 서약을 찍으면 **화염 피해 증가가 그 스킬에 안 먹어서**(9/9 방송)
피해 줄이 주문 피해 -> 카오스 피해로 갈린다. 전환 권장은 86~87레벨.

스탯 id 는 공식 trade2 stats 인덱스와 대조한 것만 쓴다(캐시 `data/_cache/trade2/int_stats.json`).
`?q=` 무상태 링크가 정본이다 — 검색 id 단축 링크는 만료되고 서버(글로벌/카카오)마다 다르다.

사용:
    python -X utf8 scripts/probe_gemling_jewels.py            # 링크만(호출 0)
    python -X utf8 scripts/probe_gemling_jewels.py --live     # 매물 수·최저 호가까지(2초 간격)
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

REPO = Path(__file__).resolve().parents[1]
CACHE = REPO / "data" / "_cache" / "trade2" / "int_stats.json"
UA = ("PathcraftAI/0.1 (+https://github.com/Whitening-Sinabro/Pathcraft-AI; "
      "contact: vnddns999@gmail.com)")
HOSTS = {"int": "www.pathofexile.com", "kr": "poe.kakaogames.com"}
LEAGUE = "HC Forbidden Rites"
BASE = "Sapphire"

STATS = {
    "es": "explicit.stat_2482852589",        # #% increased maximum Energy Shield
    "chaos": "explicit.stat_736967255",      # #% increased Chaos Damage
    "flam": "explicit.stat_2968503605",      # #% increased Flammability Magnitude
    "spell": "explicit.stat_2974417149",     # #% increased Spell Damage
}

# (라벨, 피해 축 키, [(스탯키, 최소값)…])
TIERS = [
    ("중옵 — 그가 낀 하한", [("es", 10), ("AXIS", 10)]),
    ("상옵 — 그의 중앙값 이상", [("es", 16), ("AXIS", 12)]),
    ("최상옵 — 그의 최고 + 세 줄 다", [("es", 18), ("AXIS", 12), ("flam", 15)]),
    # 최상옵이 0건일 때의 완화 사다리. 실측으로 카오스 축 최상옵은 매물이 없다
    # (본인도 "셋 다 붙은 건 1개뿐 — 시장에 없어서다"라고 말한다).
    ("최상 대체 A — 인화성 빼고 두 줄", [("es", 18), ("AXIS", 12)]),
    ("최상 대체 B — ES 16 + 인화성 10", [("es", 16), ("AXIS", 12), ("flam", 10)]),
]
AXES = [("전환 전 (주문 피해)", "spell"), ("전환 후 (카오스 피해)", "chaos")]

# 최상옵이 0건일 때 "그럼 지금 살 수 있는 천장은 어디냐"를 찾는 훑기. 등급표와 달리
# 이건 시장 지도이지 기준이 아니다 — 매물 수는 시각을 붙여서만 인용한다.
TOP_SWEEP = [
    ("천장 A — 카오스 13 (그의 최고치)", [("AXIS", 13)]),
    ("천장 B — ES 20 (그의 최고치)", [("es", 20)]),
    ("천장 C — ES 20 + 카오스 12", [("es", 20), ("AXIS", 12)]),
    ("천장 D — ES 18 + 카오스 13", [("es", 18), ("AXIS", 13)]),
    ("천장 E — ES 18 + 카오스 12 + 인화성 10", [("es", 18), ("AXIS", 12), ("flam", 10)]),
    ("천장 F — 카오스 12 + 인화성 15", [("AXIS", 12), ("flam", 15)]),
]

log = logging.getLogger("jewels")


def verify_stat_ids() -> None:
    """문서에 적힌 id 를 공식 인덱스와 대조한다. 안 맞으면 링크가 조용히 빈 검색이 된다."""
    if not CACHE.exists():
        sys.exit(f"{CACHE} 가 없다 — trade2 stats 캐시 없이 링크를 만들지 않는다")
    doc = json.loads(CACHE.read_text(encoding="utf-8"))
    known = {e["id"] for g in doc.get("result", []) for e in g.get("entries", []) if e.get("id")}
    missing = [f"{k}={v}" for k, v in STATS.items() if v not in known]
    if missing:
        sys.exit(f"공식 stats 인덱스에 없는 id: {missing}")


def query_for(axis_key: str, mins: list[tuple[str, int]]) -> dict:
    filters = []
    for key, low in mins:
        stat = STATS[axis_key] if key == "AXIS" else STATS[key]
        filters.append({"id": stat, "value": {"min": low}, "disabled": False})
    return {
        "query": {
            "status": {"option": "securable"},     # 즉시거래. online 은 대면이라 매물이 얇다
            "type": BASE,
            "stats": [{"type": "and", "filters": filters}],
        },
        "sort": {"price": "asc"},
    }


def stateless_link(realm: str, payload: dict) -> str:
    body = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
    return (f"https://{HOSTS[realm]}/trade2/search/poe2/{urllib.parse.quote(LEAGUE)}"
            f"?q={urllib.parse.quote(body)}")


def post(url: str, body: dict) -> dict:
    req = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"), headers={
        "User-Agent": UA, "Accept": "application/json", "Content-Type": "application/json"})
    for _ in range(3):
        try:
            with urllib.request.urlopen(req, timeout=40) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            if exc.code == 429:
                wait = int(exc.headers.get("Retry-After") or 60)
                log.warning("429 — Retry-After %d초", wait)
                time.sleep(wait)
                continue
            raise SystemExit(f"HTTP {exc.code}: {exc.read().decode('utf-8', 'replace')[:200]}")
    raise SystemExit("429 가 계속된다 — 나중에 다시")


def get(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.loads(r.read().decode("utf-8"))


def cheapest(result_ids: list[str]) -> str | None:
    if not result_ids:
        return None
    url = (f"https://{HOSTS['int']}/api/trade2/fetch/{','.join(result_ids[:2])}")
    data = get(url).get("result") or []
    for row in data:
        price = ((row.get("listing") or {}).get("price") or {})
        if price.get("amount") is not None:
            return f"{price['amount']:g} {price.get('currency')}"
    return None


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(message)s", stream=sys.stdout)
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", action="store_true", help="매물 수·최저 호가까지 조회(2초 간격)")
    ap.add_argument("--gap", type=float, default=2.0)
    ap.add_argument("--top-sweep", action="store_true",
                    help="카오스 축에서 지금 실제로 살 수 있는 천장을 훑는다")
    ap.add_argument("--out", default="deliverables/trade_probe")
    args = ap.parse_args()
    verify_stat_ids()

    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    rows = []
    plan = ([("전환 후 (카오스 피해)", "chaos", TOP_SWEEP)] if args.top_sweep
            else [(label, key, TIERS) for label, key in AXES])
    for axis_label, axis_key, tier_list in plan:
        for tier_label, mins in tier_list:
            payload = query_for(axis_key, mins)
            row = {
                "axis": axis_label, "tier": tier_label,
                "mins": {("피해" if k == "AXIS" else k): v for k, v in mins},
                "link_int": stateless_link("int", payload),
                "link_kr": stateless_link("kr", payload),
                "checked_utc": stamp,
            }
            if args.live:
                res = post(f"https://{HOSTS['int']}/api/trade2/search/poe2/"
                           f"{urllib.parse.quote(LEAGUE)}", payload)
                row["total"] = res.get("total")
                row["search_id"] = res.get("id")
                row["short_int"] = (f"https://{HOSTS['int']}/trade2/search/poe2/"
                                    f"{urllib.parse.quote(LEAGUE)}/{res.get('id')}")
                time.sleep(args.gap)
                row["cheapest"] = cheapest(res.get("result") or [])
                time.sleep(args.gap)
                log.info("%-22s %-28s 매물 %-5s 최저 %s", axis_label, tier_label,
                         row["total"], row["cheapest"])
            rows.append(row)

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    dest = out / f"gemling_jewels_{stamp.replace(':', '').replace('-', '')[:15]}.json"
    dest.write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    log.info("저장: %s", dest)
    return 0


if __name__ == "__main__":
    sys.exit(main())
