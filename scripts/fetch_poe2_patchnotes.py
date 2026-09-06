"""POE2 공식 패치노트 포럼(view-forum/2212)을 훑어 스레드 본문을 텍스트로 캐시한다.

    python scripts/fetch_poe2_patchnotes.py --since 3883495          # 0.4.0 콘텐츠 업데이트부터
    python scripts/fetch_poe2_patchnotes.py --since 3883495 --pages 6

출력: data/_cache/patchnotes/poe2/<thread_id>_<slug>.txt  +  _index.json
첫 게시물(<td colspan="2"><div class="content">)만 본문으로 취급한다 — 댓글은 버린다.

포럼은 curl UA 로 200 을 준다(2026-09-05 실측). 차단되면 exit 2.
"""
from __future__ import annotations

import argparse
import json
import logging
import re
import sys
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup

FORUM = "https://www.pathofexile.com/forum/view-forum/2212"
THREAD = "https://www.pathofexile.com/forum/view-thread/{id}"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36"
OUT_DIR = Path(__file__).resolve().parent.parent / "data" / "_cache" / "patchnotes" / "poe2"
DATE_RE = re.compile(r"[A-Z][a-z]{2} \d{1,2}, \d{4}")

log = logging.getLogger("poe2_patchnotes")


def fetch(session: requests.Session, url: str) -> str:
    resp = session.get(url, headers={"User-Agent": UA}, timeout=60)
    if resp.status_code != 200:
        raise RuntimeError(f"{url} -> HTTP {resp.status_code}")
    return resp.text


def parse_index(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    seen: dict[int, dict] = {}
    for a in soup.select('a[href*="/forum/view-thread/"]'):
        m = re.search(r"/forum/view-thread/(\d+)", a.get("href", ""))
        title = a.get_text(" ", strip=True)
        if not m or not title:
            continue
        tid = int(m.group(1))
        if tid in seen:
            continue
        row = a.find_parent("tr")
        row_text = row.get_text(" ", strip=True) if row else ""
        dm = DATE_RE.search(row_text)
        seen[tid] = {"id": tid, "title": title, "date": dm.group(0) if dm else ""}
    return list(seen.values())


def first_post_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    # 일반 스레드: forumPostListTable 첫 행의 td.content-container > div.content
    # 대형 콘텐츠 업데이트(뉴스 레이아웃): td[colspan=2] > div.content 에 본문이 있고,
    # forumPostListTable 첫 행은 **댓글**이다 — 0.5.0 스레드가 "massive patch" 로 잡혔던 원인.
    # 둘 다 있으면 긴 쪽이 본문이다.
    candidates = [
        soup.select_one('td[colspan="2"] div.content'),
        soup.select_one("table.forumPostListTable tr td.content-container div.content"),
    ]
    candidates = [c for c in candidates if c is not None]
    if not candidates:
        raise RuntimeError("first post container not found")
    cell = max(candidates, key=lambda c: len(c.get_text(" ", strip=True)))
    for br in cell.find_all("br"):
        br.replace_with("\n")
    text = cell.get_text("\n")
    lines = [ln.rstrip() for ln in text.splitlines()]
    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip() + "\n"


def slugify(title: str) -> str:
    return re.sub(r"[^A-Za-z0-9.]+", "_", title).strip("_")[:60]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", type=int, required=True, help="이 스레드 id 이상만 (예: 3883495 = 0.4.0)")
    ap.add_argument("--pages", type=int, default=8, help="훑을 인덱스 페이지 수 상한")
    ap.add_argument("--delay", type=float, default=0.6)
    args = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    session = requests.Session()

    threads: list[dict] = []
    for page in range(1, args.pages + 1):
        url = FORUM if page == 1 else f"{FORUM}/page/{page}"
        try:
            rows = parse_index(fetch(session, url))
        except RuntimeError as exc:
            log.error("index page %s failed: %s", page, exc)
            return 2
        keep = [r for r in rows if r["id"] >= args.since]
        threads.extend(keep)
        log.info("index page %d: %d rows, %d kept", page, len(rows), len(keep))
        # 고정(sticky) 공지가 낮은 id 로 매 페이지에 끼므로 "낮은 id 존재"로 끊으면 1페이지에서 멈춘다.
        # 이 페이지에서 살린 행이 없을 때만 끝낸다.
        if not keep:
            break
        time.sleep(args.delay)

    threads.sort(key=lambda r: r["id"])
    failures: list[dict] = []
    for row in threads:
        path = OUT_DIR / f"{row['id']}_{slugify(row['title'])}.txt"
        row["file"] = path.name
        if path.exists() and path.stat().st_size > 0:
            continue
        try:
            body = first_post_text(fetch(session, THREAD.format(id=row["id"])))
        except RuntimeError as exc:
            log.warning("thread %s failed: %s", row["id"], exc)
            failures.append({**row, "error": str(exc)})
            continue
        path.write_text(f"{row['title']}\n{row['date']}\n{THREAD.format(id=row['id'])}\n\n{body}", encoding="utf-8")
        log.info("saved %s (%d chars)", path.name, len(body))
        time.sleep(args.delay)

    (OUT_DIR / "_index.json").write_text(json.dumps({"since": args.since, "threads": threads, "failures": failures}, ensure_ascii=False, indent=1), encoding="utf-8")
    log.info("done: %d threads, %d failures", len(threads), len(failures))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
