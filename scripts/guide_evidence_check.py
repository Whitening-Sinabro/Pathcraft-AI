"""Mechanical evidence checks for a guide HTML — the part an LLM should not be doing.

A verification pass on one guide has been taking ~26 minutes and ~100 tool calls,
and most of that was not judgement: it was re-fetching subtitles another agent had
already downloaded (in one case hunting through five different session scratchpads
for them), re-decoding the same PoB snapshots, and doing timestamp arithmetic by
hand. Only the judgement needs to be independent; the arithmetic does not.

This script does the mechanical half in seconds so the reviewer's turns go to the
question only a reader can answer: *is this claim actually supported by what the
source says*.

Checks (offline unless --online):
  * deep-link arithmetic  — every youtu.be/<id>?t=N anchor's label M:SS must equal N
  * deep-link range       — N must be inside that video's duration (from the cache)
  * silent removals       — text present in the baseline and gone now, via difflib
  * nested anchors        — <a> inside <a> renders as broken markup
  * table shape           — every <tr> column count, so a 3-col contract stays 3-col
  * bare timestamps       — citations still not linked
  * --online: URL liveness, with the hosts that answer 403 to bots allow-listed

Usage:
    python scripts/guide_evidence_check.py <guide.html> [--baseline HEAD] [--online]

Cache: `data/_cache/` (gitignored). `--adopt` pulls subtitle/PoB artifacts that
earlier agents left in session scratchpads into that one place, so the next agent
finds them instead of re-downloading.
"""

from __future__ import annotations

import argparse
import difflib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CACHE = REPO / "data" / "_cache"
SCRATCH_ROOT = Path.home() / "AppData/Local/Temp/claude/D--Pathcraft-AI"

ANCHOR = re.compile(r'<a href="(https://youtu\.be/([\w-]+)\?t=(\d+))"[^>]*>(.*?)</a>', re.S)
ANY_A = re.compile(r'<a href="([^"]+)"[^>]*>(.*?)</a>', re.S)
NESTED = re.compile(r"<a [^>]*>(?:(?!</a>).)*<a ", re.S)
ROW = re.compile(r"<tr>(.*?)</tr>", re.S)
CELL = re.compile(r"<t[dh][^>]*>")
LABEL_TS = re.compile(r"(\d{1,3}):(\d{2})")
TAG = re.compile(r"<[^>]+>")
BARE = re.compile(r"(?<!\d)(\d{1,3}):(\d{2})(?!\d)")

# These answer 403/401 to a scripted request but are live in a browser. Treating
# them as dead once cost a real link; treating them as live is the lesser error.
BOT_BLOCKED = ("mobalytics.gg", "pathofexile.com", "cafe.naver.com")


def text_of(html: str) -> str:
    return re.sub(r"\s+", " ", TAG.sub(" ", html))


def git_show(rev: str, path: Path) -> str | None:
    try:
        rel = path.resolve().relative_to(REPO).as_posix()
    except ValueError:
        return None
    out = subprocess.run(["git", "show", f"{rev}:{rel}"], cwd=REPO, capture_output=True)
    return out.stdout.decode("utf-8", errors="replace") if out.returncode == 0 else None


def durations() -> dict[str, int]:
    """video id -> length in seconds, from whatever the cache knows."""
    f = CACHE / "video_durations.json"
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}


def adopt_scratch_artifacts() -> list[str]:
    """Copy subtitle/PoB artifacts out of per-session scratchpads into the cache.

    Agents write these into their own session directory, so the next agent cannot
    see them and downloads again. One shared location ends that.
    """
    moved = []
    for kind, patterns in (("subs", ("*.json3",)), ("pob", ("*.xml",))):
        dest = CACHE / kind
        dest.mkdir(parents=True, exist_ok=True)
        for pat in patterns:
            for src in SCRATCH_ROOT.glob(f"*/scratchpad/**/{pat}"):
                # keep one copy per logical artifact; ".ko-orig" duplicates ".ko"
                name = src.name.replace(".ko-orig.", ".ko.")
                target = dest / name
                if target.exists():
                    continue
                shutil.copy2(src, target)
                moved.append(f"{kind}/{name}")
    return moved


def check(path: Path, baseline: str | None, online: bool) -> int:
    html = path.read_text(encoding="utf-8")
    problems: list[str] = []
    notes: list[str] = []
    dur = durations()

    # --- deep links -----------------------------------------------------------
    anchors = ANCHOR.findall(html)
    bad_math, out_of_range, no_label = [], [], 0
    for _url, vid, secs, label in anchors:
        m = LABEL_TS.search(text_of(label))
        if not m:
            no_label += 1
            continue
        want = int(m.group(1)) * 60 + int(m.group(2))
        if want != int(secs):
            bad_math.append(f"{label.strip()[:24]} -> t={secs} (라벨 계산 {want})")
        if vid in dur and int(secs) >= dur[vid]:
            out_of_range.append(f"{vid} t={secs} >= 길이 {dur[vid]}")
    if bad_math:
        problems.append(f"딥링크 초 불일치 {len(bad_math)}건: {bad_math[:4]}")
    if out_of_range:
        problems.append(f"영상 길이 초과 {len(out_of_range)}건: {out_of_range[:4]}")
    if no_label:
        notes.append(f"라벨에 M:SS 없는 딥링크 {no_label}건 (수동 확인 필요)")

    # --- markup ---------------------------------------------------------------
    if NESTED.search(html):
        problems.append("중첩 <a> 존재 — 렌더가 깨진다")
    shapes: dict[int, int] = {}
    for r in ROW.findall(html):
        shapes[len(CELL.findall(r))] = shapes.get(len(CELL.findall(r)), 0) + 1
    odd = {k: v for k, v in shapes.items() if k not in (2, 3)}
    if odd:
        notes.append(f"3열이 아닌 행 분포: {odd}")

    # --- bare citations -------------------------------------------------------
    stripped = ANY_A.sub(" ", html)
    bare = BARE.findall(stripped)
    if bare:
        notes.append(f"링크 안 걸린 M:SS {len(bare)}건 (영상 길이·시각 표기는 정상)")

    # --- silent removals ------------------------------------------------------
    if baseline:
        old = git_show(baseline, path)
        if old is None:
            notes.append(f"{baseline} 에 없는 파일 — 삭제 검사 생략")
        else:
            # Compare on sentence-ish units, but count *shrinking replaces* too.
            # A deletion inside a sentence shows up as 'replace', not 'delete', so
            # a delete-only check reports green on text that really did vanish --
            # which is worse than no check at all.
            def units(t: str) -> list[str]:
                return [u.strip() for u in re.split(r"(?<=다\.)\s|(?<=\.)\s", t) if u.strip()]

            a, b = units(text_of(old)), units(text_of(html))
            lost: list[str] = []
            for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b).get_opcodes():
                if tag == "delete":
                    lost += [x for x in a[i1:i2] if len(x) > 40]
                elif tag == "replace":
                    before_len = sum(len(x) for x in a[i1:i2])
                    after_len = sum(len(x) for x in b[j1:j2])
                    # a rewrite that drops more than a quarter of its text is a
                    # removal wearing a rewrite's clothes
                    if before_len - after_len > 40 and after_len < before_len * 0.75:
                        lost.append(
                            f"[축약 {before_len}->{after_len}자] " + " ".join(a[i1:i2])[:120]
                        )
            if lost:
                problems.append(f"사라진/축약된 본문 {len(lost)}건 — 첫 건: {lost[0][:110]}")

    # --- liveness -------------------------------------------------------------
    if online:
        import urllib.request

        seen, dead = set(), []
        for url, _ in ANY_A.findall(html):
            if url in seen or any(h in url for h in BOT_BLOCKED):
                continue
            seen.add(url)
            try:
                req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "Mozilla/5.0"})
                urllib.request.urlopen(req, timeout=15)
            except Exception as e:  # noqa: BLE001 - any failure is worth reporting
                code = getattr(e, "code", None)
                if code in (403, 405, 429):
                    continue  # blocked or method-not-allowed, not dead
                dead.append(f"{url} -> {code or type(e).__name__}")
        if dead:
            problems.append(f"응답 없는 링크 {len(dead)}건: {dead[:4]}")
        notes.append(f"링크 생존 확인 {len(seen)}건 (봇 차단 호스트 제외)")

    print(f"\n{path.name}")
    print(f"    딥링크 {len(anchors)} · 표 행 {sum(shapes.values())} · 캐시된 영상 길이 {len(dur)}건")
    for n in notes:
        print(f"    · {n}")
    for p in problems:
        print(f"    ✗ {p}")
    if not problems:
        print("    ✓ 기계 검사 통과 — 남은 것은 '주장이 근거에 실제로 부합하는가' 뿐이다")
    return len(problems)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="*")
    ap.add_argument("--baseline", default=None)
    ap.add_argument("--online", action="store_true")
    ap.add_argument("--adopt", action="store_true", help="세션 스크래치패드의 자산을 공용 캐시로 모은다")
    args = ap.parse_args()

    if args.adopt:
        moved = adopt_scratch_artifacts()
        print(f"공용 캐시로 옮긴 자산 {len(moved)}건 -> {CACHE}")
        for m in moved[:20]:
            print(f"  {m}")
        if not args.files:
            return 0

    files = [Path(f).resolve() for f in args.files] or sorted((REPO / "Docs").glob("*_GUIDE_DOC.html"))
    failed = sum(1 for f in files if check(f, args.baseline, args.online))
    print(f"\n{len(files)}개 중 {failed}개에 기계 검사 지적 있음")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
