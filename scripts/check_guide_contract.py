"""Structural contract check for the POE2 guide HTML files.

These files are not free-form documents: `scratchpad/build_gdoc_v4.mjs` parses them
to build the Google Doc payload, splitting on the purple chapter bands and on
3-column evidence rows, and `@@IMG:name@@` markers say where screenshots go. An
edit that reads fine but drops a band or collapses a table silently produces a
Doc with missing chapters -- which is exactly how a chapter vanished from the
outline once already.

Usage:
    python scripts/check_guide_contract.py                 # check every guide
    python scripts/check_guide_contract.py <file> [...]    # check specific files
    python scripts/check_guide_contract.py --baseline HEAD # compare against git

Exit code is non-zero when any file fails.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DOCS = REPO / "Docs"
GUIDE_GLOB = "*_GUIDE_DOC.html"

BAND = re.compile(r'<table><tr><td style="background:#7c3aed;[^"]*"><b>([^<]+)</b></td></tr></table>')
IMG = re.compile(r"@@IMG:(\w+)@@")
ROW = re.compile(r"<tr>(.*?)</tr>", re.S)
CELL = re.compile(r"<td[^>]*>", re.S)
ANCHOR = re.compile(r"<a href=")
# A timestamp that is not inside an <a> is a claim the reader cannot check without
# scrubbing a 30-minute video by hand. The template calls this a defect.
BARE_TS = re.compile(r"(?<!\d)\d{1,2}:\d{2}(?!\d)")
DEEPLINK = re.compile(r'<a href="[^"]*(?:youtu\.be|youtube\.com)[^"]*[?&]t=\d+')
REQUIRED_BANDS = ["제0장", "제1장", "제2장", "제3장", "제4장",
                  "제5장", "제6장", "제7장", "제8장", "출처"]
# A chapter is identified by its key, not its full title: renaming
# "부록 — 구매 우선순위" to "부록 1·2 — …" is a retitle, not a lost chapter, and
# reporting it as loss trains the reader to ignore the loss warning.
BAND_KEY = re.compile(r"^(제\d장|출처|부록\s*[\d·]*)")
TAG = re.compile(r"<[^>]+>")


def stats(text: str) -> dict:
    rows = ROW.findall(text)
    three_col = sum(1 for r in rows if len(CELL.findall(r)) == 3)
    return {
        "bands": [m.group(1) for m in BAND.finditer(text)],
        "images": IMG.findall(text),
        "rows": len(rows),
        "three_col_rows": three_col,
        "links": len(ANCHOR.findall(text)),
        "body_chars": len(re.sub(r"\s+", " ", TAG.sub(" ", text))),
        "unverified": len(re.findall("미확인", text)),
        "deeplinks": len(DEEPLINK.findall(text)),
        # count timestamps that are not already inside a deep-linked anchor
        "bare_ts": len(BARE_TS.findall(re.sub(r'<a href="[^"]*"[^>]*>.*?</a>', " ", text, flags=re.S))),
    }


def git_show(rev: str, path: Path) -> str | None:
    try:
        rel = path.resolve().relative_to(REPO).as_posix()
    except ValueError:
        return None  # outside the repo -> nothing to compare against
    try:
        out = subprocess.run(
            ["git", "show", f"{rev}:{rel}"], cwd=REPO,
            capture_output=True, check=True,
        )
        return out.stdout.decode("utf-8", errors="replace")
    except subprocess.CalledProcessError:
        return None


def check(path: Path, baseline: str | None) -> list[str]:
    text = path.read_text(encoding="utf-8")
    cur = stats(text)
    problems: list[str] = []

    # POE1 3.29 guides predate the band convention. Only a *regression* matters:
    # a file that had bands and lost them. Flagging a format that never used them
    # is noise, and noise is how a real failure gets scrolled past.
    old_bands = None
    if baseline:
        prior = git_show(baseline, path)
        old_bands = stats(prior)["bands"] if prior is not None else None
    if not cur["bands"]:
        if old_bands:
            problems.append("장 구분 띠가 전부 사라졌다 — 생성기가 문서를 한 덩어리로 본다")
        else:
            print("    (장 구분 띠를 쓰지 않는 이전 포맷 — 띠 검사 생략)")
    if cur["three_col_rows"] == 0 and cur["rows"] > 0:
        problems.append("3열 근거 행이 0 — 표가 다른 형태로 바뀌었다")
    if len(set(cur["images"])) != len(cur["images"]):
        dupes = [i for i in cur["images"] if cur["images"].count(i) > 1]
        problems.append(f"이미지 마커 중복: {sorted(set(dupes))}")

    # template conformance -- only for files that use the band format at all
    if cur["bands"]:
        joined = " | ".join(cur["bands"])
        missing = [b for b in REQUIRED_BANDS if b not in joined]
        if missing:
            problems.append(f"템플릿 필수 장 누락: {missing}")
        appendix = re.findall(r"부록\s*(\d*)", joined)
        if appendix and any(a == "" for a in appendix) and len(appendix) > 1:
            problems.append("부록에 번호 없는 항목이 섞여 있다 — 번호 체계 고정")

    if baseline:
        old_text = git_show(baseline, path)
        if old_text is None:
            problems.append(f"{baseline} 에 이 파일이 없어 비교 불가")
        else:
            old = stats(old_text)
            def key(title: str) -> str:
                m = BAND_KEY.match(title.strip())
                if not m:
                    return title.strip()
                k = m.group(1).replace(" ", "")
                # Appendices get renumbered legitimately (부록 -> 부록 1·2), so they
                # are one class here; the numbering itself is checked separately.
                return "부록" if k.startswith("부록") else k

            cur_keys = [key(b) for b in cur["bands"]]
            lost_bands = [b for b in old["bands"] if key(b) not in cur_keys]
            old_appendix = sum(1 for b in old["bands"] if key(b) == "부록")
            new_appendix = cur_keys.count("부록")
            if new_appendix < old_appendix:
                problems.append(f"부록 띠 감소: {old_appendix} -> {new_appendix}")
            lost_imgs = [i for i in old["images"] if i not in cur["images"]]
            if lost_bands:
                problems.append(f"사라진 장: {lost_bands}")
            if lost_imgs:
                problems.append(f"사라진 이미지 마커: {lost_imgs}")
            if cur["three_col_rows"] < old["three_col_rows"] * 0.9:
                problems.append(
                    f"3열 근거 행 급감: {old['three_col_rows']} -> {cur['three_col_rows']}"
                )
            delta = (
                f"본문 {old['body_chars']}->{cur['body_chars']} "
                f"({cur['body_chars'] - old['body_chars']:+d}) · "
                f"링크 {old['links']}->{cur['links']} ({cur['links'] - old['links']:+d}) · "
                f"미확인 {old['unverified']}->{cur['unverified']}"
            )
            print(f"    {delta}")

    print(
        f"    장 {len(cur['bands'])} · 3열행 {cur['three_col_rows']}/{cur['rows']} · "
        f"이미지 {len(cur['images'])} · 링크 {cur['links']} · 미확인 {cur['unverified']}"
    )
    if cur["bare_ts"]:
        print(
            f"    ⚠ 평문 타임스탬프 {cur['bare_ts']}개 (딥링크 {cur['deeplinks']}개) "
            "— 템플릿상 근거는 전부 딥링크여야 한다"
        )
    return problems


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    baseline = None
    if "--baseline" in sys.argv:
        i = sys.argv.index("--baseline")
        baseline = sys.argv[i + 1] if i + 1 < len(sys.argv) else "HEAD"
        if baseline in args:
            args.remove(baseline)

    files = [Path(a).resolve() for a in args] if args else sorted(DOCS.glob(GUIDE_GLOB))
    failed = 0
    for f in files:
        print(f"\n{f.name}")
        problems = check(f, baseline)
        for p in problems:
            print(f"    ✗ {p}")
        if problems:
            failed += 1
        else:
            print("    ✓ 구조 계약 통과")
    print(f"\n{len(files)}개 중 {failed}개 실패")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
