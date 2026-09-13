"""Skadoosh 생방송 동안 공개 캐릭터와 방송 상태를 주기적으로 확인한다.

왜 폴링인가: poe.ninja 와 트위치는 변경을 알려 주지 않는다. 외부 상태라
직접 물어보는 수밖에 없다. 대신 간격을 넉넉히 두고, 바뀐 것만 기록한다.

기록: `<out>/events.jsonl` 에 변경 시점만 한 줄씩. 스냅샷 원본은
`<out>/snap_<레벨>_<시각>.json` 으로 남겨 나중에 대조할 수 있게 한다.
방송이 끝나면 마지막으로 한 번 더 확인하고 종료한다.
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

log = logging.getLogger("watch")

NINJA = ("https://poe.ninja/poe2/api/builds/latest/character?account=ITheCon-2183"
         "&name=SkadooshShoutedHard&overview=hc-forbidden-rites")
GQL = "https://gql.twitch.tv/gql"
CLIENT_ID = "kimne78kx3ncx6brgo4mv6wki5h1ko"
QUERY = ('{ user(login:"skadoosh_c"){ stream { id title createdAt viewersCount } '
         'videos(first:1, sort:TIME, type:ARCHIVE){ edges { node { id lengthSeconds createdAt } } } } }')


def get_json(url, data=None, headers=None):
    req = urllib.request.Request(url, data=data, headers=headers or {"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=45) as r:
        return json.loads(r.read().decode("utf-8"))


def twitch():
    body = json.dumps({"query": QUERY}).encode()
    d = get_json(GQL, body, {"Client-ID": CLIENT_ID, "Content-Type": "application/json"})
    return d["data"]["user"]


def links(snap):
    out = {}
    for g in snap.get("skills") or []:
        names = [x.get("name") for x in (g.get("allGems") or [])]
        if names:
            out.setdefault(names[0], []).append(names[1:])
    return out


def gear(snap):
    out = {}
    for it in snap.get("items") or []:
        data = it.get("itemData") or {}
        out[str(it.get("itemSlot"))] = ((data.get("name") or "") + " " +
                                        (data.get("typeLine") or data.get("baseType") or "")).strip()
    return out


def describe(before, after):
    """두 스냅샷 사이에서 사람이 읽을 변경만 뽑는다."""
    events = []
    if before.get("level") != after.get("level"):
        events.append(f"레벨 {before.get('level')} → {after.get('level')}")
    a, b = links(before), links(after)
    for k in sorted(set(a) | set(b)):
        if a.get(k) != b.get(k):
            events.append(f"젬 [{k}] {a.get(k)} → {b.get(k)}")
    ga, gb = gear(before), gear(after)
    for k in sorted(set(ga) | set(gb), key=str):
        if ga.get(k) != gb.get(k):
            events.append(f"장비 slot {k}: {ga.get(k, '없음')} → {gb.get(k, '없음')}")
    pa, pb = before.get("passiveCounts") or {}, after.get("passiveCounts") or {}
    if pa != pb:
        events.append(f"패시브 {pa} → {pb}")
    return events


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s", stream=sys.stdout)
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="deliverables/skadoosh_live_watch_2026-09-12")
    ap.add_argument("--interval", type=int, default=300)
    ap.add_argument("--max-minutes", type=int, default=180)
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    events = out / "events.jsonl"

    baseline_path = Path("deliverables/skadoosh_vod_2871483565_2026-09-12/creator_latest.json")
    prev = json.loads(baseline_path.read_text(encoding="utf-8"))
    deadline = time.time() + args.max_minutes * 60
    offline_seen = 0

    def record(kind, payload):
        line = {"utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "kind": kind, **payload}
        with events.open("a", encoding="utf-8") as f:
            f.write(json.dumps(line, ensure_ascii=False) + "\n")
        return line

    log.info("감시 시작 — 기준 레벨 %s (%s)", prev.get("level"), prev.get("updatedUtc"))
    while time.time() < deadline:
        try:
            user = twitch()
            live = bool(user.get("stream"))
        except Exception as exc:
            log.warning("트위치 조회 실패: %s", type(exc).__name__)
            live = None
        try:
            snap = get_json(NINJA, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"})
        except Exception as exc:
            log.warning("ninja 조회 실패: %s", type(exc).__name__)
            snap = None

        if snap and snap.get("updatedUtc") != prev.get("updatedUtc"):
            diffs = describe(prev, snap)
            stamp = (snap.get("updatedUtc") or "").replace(":", "").replace("-", "")[:15]
            (out / f"snap_{snap.get('level')}_{stamp}.json").write_text(
                json.dumps(snap, ensure_ascii=False, indent=2), encoding="utf-8")
            record("character", {"level": snap.get("level"),
                                 "updatedUtc": snap.get("updatedUtc"), "changes": diffs})
            log.info("변경 %d건 (레벨 %s)", len(diffs), snap.get("level"))
            for d in diffs:
                log.info("   %s", d)
            prev = snap

        if live is False:
            offline_seen += 1
            log.info("방송 종료 확인 %d/2", offline_seen)
            if offline_seen >= 2:
                record("stream", {"status": "offline"})
                log.info("방송이 끝났다 — 감시 종료")
                return 0
        elif live:
            offline_seen = 0
        time.sleep(args.interval)

    log.info("시간 상한 도달 — 감시 종료")
    return 0


if __name__ == "__main__":
    sys.exit(main())
