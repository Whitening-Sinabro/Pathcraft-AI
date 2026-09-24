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


# ---- 약한 점화 원인 교체용 반지 (2026-09-18) --------------------------------
# 기름 유탄은 공격이라 "공격 시 화염 피해 추가"가 붙으면 유탄이 직접 약한 점화를
# 만든다(아르세리나 9/6 테스트, `.claude/status/poe2_hc_gemling.md`). 그래서 그 줄을
# `type: "not"` 으로 배제하는 게 이 검색의 핵심이고, 나머지는 잃는 저항·생명력을
# 메우는 조건이다. 기준값은 지어낸 게 아니라 교체 대상(Chimeric Gyre)의 실제 수치다.
_NO_FIRE_TO_ATTACKS = {"type": "not", "filters": [
    {"id": "explicit.stat_1573130764"},   # Adds # to # Fire damage to Attacks
    {"id": "implicit.stat_1573130764"},
]}
_LIFE = "explicit.stat_3299347043"
_FIRE_RES = "explicit.stat_3372524247"
_LIGHT_RES = "explicit.stat_1671376347"


def _ring(base: str | None, mins: list[tuple[str, int]]) -> dict:
    query = {"status": {"option": "securable"},
             "stats": [{"type": "and", "filters": [
                 {"id": sid, "value": {"min": low}, "disabled": False} for sid, low in mins]},
                 _NO_FIRE_TO_ATTACKS]}
    if base:
        query["type"] = base
    return {"query": query, "sort": {"price": "asc"}}


PROBES.update({
    "반지 교체 하한 (루비, 생명 60·화저 20)":
        _ring("Ruby Ring", [(_LIFE, 60), (_FIRE_RES, 20)]),
    "반지 교체 동급 (루비, +번저 10)":
        _ring("Ruby Ring", [(_LIFE, 65), (_FIRE_RES, 20), (_LIGHT_RES, 10)]),
    "반지 교체 상위 (루비, 생명 80·화저 25·번저 20)":
        _ring("Ruby Ring", [(_LIFE, 80), (_FIRE_RES, 25), (_LIGHT_RES, 20)]),
    "반지 교체 동급 (베이스 무관)":
        _ring(None, [(_LIFE, 65), (_FIRE_RES, 20), (_LIGHT_RES, 10)]),
    # 루비 베이스를 고집하면 매물이 마르지만, 베이스를 풀면 암묵 화염 저항을 잃는다.
    # 그래서 합산(pseudo)으로 건다 — 지금 끼고 있는 반지의 실제 합(화 43·번 12)이 기준.
    "반지 교체 합산 (화저합 40·번저합 10·생명 65)":
        _ring(None, [("pseudo.pseudo_total_fire_resistance", 40),
                     ("pseudo.pseudo_total_lightning_resistance", 10), (_LIFE, 65)]),
    "반지 교체 합산 (화저합 35·생명 60)":
        _ring(None, [("pseudo.pseudo_total_fire_resistance", 35), (_LIFE, 60)]),
    # not 그룹이 조용히 무시되면 추천 전체가 무너진다 — 대조군으로 같이 돌린다.
    "대조군 — 배제 없이 (루비 생명 60·화저 20)":
        {"query": {"status": {"option": "securable"}, "type": "Ruby Ring",
                   "stats": [{"type": "and", "filters": [
                       {"id": _LIFE, "value": {"min": 60}, "disabled": False},
                       {"id": _FIRE_RES, "value": {"min": 20}, "disabled": False}]}]},
         "sort": {"price": "asc"}},
})


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


def stateless_link(league: str, payload: dict) -> str:
    """검색 id 링크는 만료된다. 기록에 남기는 정본은 무상태 `?q=` 쪽이다."""
    body = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
    return (f"{HOST}/trade2/search/poe2/{urllib.parse.quote(league)}"
            f"?q={urllib.parse.quote(body)}")


def cheapest(result_ids: list[str]) -> str | None:
    if not result_ids:
        return None
    req = urllib.request.Request(f"{HOST}/api/trade2/fetch/{','.join(result_ids[:2])}",
                                 headers={"User-Agent": UA, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=40) as r:
            rows = json.loads(r.read().decode("utf-8")).get("result") or []
    except urllib.error.HTTPError as exc:
        log.warning("fetch 실패 HTTP %s", exc.code)
        return None
    for row in rows:
        price = ((row.get("listing") or {}).get("price") or {})
        if price.get("amount") is not None:
            return f"{price['amount']:g} {price.get('currency')}"
    return None


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s", stream=sys.stdout)
    ap = argparse.ArgumentParser()
    ap.add_argument("--gap", type=float, default=2.0, help="호출 사이 간격(초)")
    ap.add_argument("--out", default="deliverables/trade_probe")
    ap.add_argument("--league", action="append", help="특정 리그만(기본: SC·HC 둘 다)")
    ap.add_argument("--only", help="라벨에 이 문자열이 든 탐침만")
    args = ap.parse_args()
    leagues = args.league or LEAGUES
    probes = {k: v for k, v in PROBES.items() if not args.only or args.only in k}

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    rows = []

    for label, payload in probes.items():
        for league in leagues:
            url = f"{HOST}/api/trade2/search/poe2/{urllib.parse.quote(league)}"
            res = post(url, payload)
            total = res.get("total")
            sid = res.get("id")
            link = f"{HOST}/trade2/search/poe2/{urllib.parse.quote(league)}/{sid}" if sid else None
            time.sleep(args.gap)
            low = cheapest(res.get("result") or [])
            log.info("%-34s %-20s 매물 %-5s 최저 %s", label, league, total, low)
            rows.append({"label": label, "league": league, "total": total,
                         "cheapest": low, "search_id": sid, "link": link,
                         "link_q": stateless_link(league, payload),
                         "checked_utc": stamp})
            time.sleep(args.gap)

    dest = out / f"listings_{stamp.replace(':', '').replace('-', '')[:15]}.json"
    dest.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    log.info("저장: %s", dest)
    return 0


if __name__ == "__main__":
    sys.exit(main())
