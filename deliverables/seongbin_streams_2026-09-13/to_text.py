"""임성빈 다시보기 자막(json3)을 시각 붙은 텍스트로 편다.

왜 자막인가: 유튜브 다시보기는 한국어 자동 자막(ko-orig)이 붙는다. Whisper 로
다시 전사할 이유가 없다 — 오디오 수백 MB 와 GPU 시간을 아낀다.
`ko-orig` 은 원어 자동 인식, `ko` 는 그것을 다듬은 것이라 둘 다 남긴다.

주의: 자동 자막도 고유명사를 틀린다. 수치·아이템 이름은 GGPK/PoB 로 교정하고
인용에는 원문을 남긴다.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def stamp(seconds: int) -> str:
    return f"{seconds // 3600:02}:{seconds % 3600 // 60:02}:{seconds % 60:02}"


def lines(path: Path):
    data = json.loads(path.read_text(encoding="utf-8"))
    out = []
    for ev in data.get("events") or []:
        text = "".join(s.get("utf8", "") for s in (ev.get("segs") or [])).strip()
        if text:
            out.append((ev.get("tStartMs", 0) // 1000, text))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", default="ko-orig")
    args = ap.parse_args()

    for src in sorted(HERE.glob(f"*.{args.lang}.json3")):
        rows = lines(src)
        dest = src.with_suffix("").with_suffix(".txt")
        dest.write_text(
            "".join(f"[{stamp(s)}] {t}\n" for s, t in rows), encoding="utf-8")
        span = stamp(rows[-1][0]) if rows else "00:00:00"
        print(f"{src.name} -> {dest.name} | {len(rows)}줄 | 마지막 {span}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
