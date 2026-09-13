"""Twitch VOD 채팅 리플레이 수집.

cursor 체인만 따라가면 45분 부근에서 끊기므로 300초 간격으로 offset 을 재시드하고
댓글 id 로 중복을 제거한다. (reference_twitch_vod_reading 참조)
"""
import json
import logging
import sys
import time
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent
VIDEO_ID = "2871483565"
DURATION = 13057
STEP = 300
CLIENT_ID = "kimne78kx3ncx6brgo4mv6wki5h1ko"
SHA = "b70a3591ff0f4e0313d126c6a1502d79a1c02baebb288227c582044aa76adf6a"
GQL = "https://gql.twitch.tv/gql"

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s", stream=sys.stdout)
log = logging.getLogger("chat")


def stamp(seconds):
    total = int(seconds)
    return f"{total // 3600:02}:{total % 3600 // 60:02}:{total % 60:02}"


def request(session, variables):
    body = [{
        "operationName": "VideoCommentsByOffsetOrCursor",
        "variables": variables,
        "extensions": {"persistedQuery": {"version": 1, "sha256Hash": SHA}},
    }]
    for attempt in range(1, 6):
        try:
            response = session.post(GQL, headers={"Client-ID": CLIENT_ID}, json=body, timeout=30)
            response.raise_for_status()
            return response.json()[0]["data"]["video"]["comments"]
        except (requests.RequestException, KeyError, TypeError, ValueError) as exc:
            if attempt == 5:
                raise
            log.warning("retry %d after %s", attempt, exc)
            time.sleep(attempt)


def main():
    session = requests.Session()
    seen, rows, calls = {}, [], 0
    for seed in range(0, DURATION + 1, STEP):
        variables = {"videoID": VIDEO_ID, "contentOffsetSeconds": seed}
        while True:
            comments = request(session, variables)
            calls += 1
            edges = comments.get("edges", [])
            if not edges:
                break
            for edge in edges:
                node = edge["node"]
                if node["id"] in seen:
                    continue
                seen[node["id"]] = True
                rows.append({
                    "id": node["id"],
                    "offset": node["contentOffsetSeconds"],
                    "user": (node.get("commenter") or {}).get("displayName") or "?",
                    "text": "".join(f.get("text", "") for f in node["message"]["fragments"]),
                })
            last = edges[-1]
            if not comments.get("pageInfo", {}).get("hasNextPage") or last["node"]["contentOffsetSeconds"] >= seed + STEP:
                break
            variables = {"videoID": VIDEO_ID, "cursor": last["cursor"]}
        log.info("seed %s rows=%d calls=%d", stamp(seed), len(rows), calls)

    rows.sort(key=lambda r: r["offset"])
    (HERE / "chat.json").write_text(json.dumps({"video_id": VIDEO_ID, "requests": calls, "messages": rows}, ensure_ascii=False, indent=2), encoding="utf-8")
    (HERE / "chat.txt").write_text("".join(f"[{stamp(r['offset'])}] {r['user']}: {r['text']}\n" for r in rows), encoding="utf-8")
    log.info("COMPLETE messages=%d requests=%d", len(rows), calls)


if __name__ == "__main__":
    main()
