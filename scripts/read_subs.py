"""`data/_cache/subs/*.json3` 자막을 타임스탬프 붙은 평문으로 읽는다.

가이드 문서는 크리에이터 발언을 `영상 12:34` 형태로 인용한다. 그 스탬프가
근거의 전부이므로 원문 `tStartMs` 를 잃지 않는 게 이 스크립트의 유일한 책임이다.

주의 — 자막 대부분은 YouTube 자동 생성이라 **고유명사가 망가진다**
("Smite of the Cathar" = Smith of Kitava). 이름은 자막이 아니라 영상 제목 ·
PoB · GGPK 에서 뽑고, 자막은 주장과 수치의 근거로만 쓸 것.

    python scripts/read_subs.py <file.json3>                 # 전문
    python scripts/read_subs.py <file.json3> armor "9,000"   # 검색어 주변만

Windows 콘솔에서는 `PYTHONIOENCODING=utf-8` 이 필요하다(한국어 자막이 깨진다).
"""
from __future__ import annotations

import argparse
import errno
import io
import json
import os
import sys
from pathlib import Path
from typing import Iterator

CONTEXT_LINES = 2

# 이 도구는 사실상 항상 `| head` 로 잘라 쓴다. Windows 는 소비자가 파이프를 닫을 때
# BrokenPipeError 가 아니라 OSError(EINVAL) 을 던져서, 정상적인 조기 종료가
# 트레이스백으로 보인다(인코딩 문제로 오진하기 딱 좋다). 두 형태를 같이 처리한다.
_PIPE_CLOSED_ERRNOS = {errno.EPIPE, errno.EINVAL}


def format_stamp(start_ms: int) -> str:
    """자막 이벤트 시작 시각 -> 인용에 쓰는 `m:ss` / `h:mm:ss`."""
    seconds = max(0, start_ms) // 1000
    minutes, secs = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


def iter_cues(payload: dict) -> Iterator[tuple[str, str]]:
    """json3 events -> (스탬프, 텍스트). 빈 이벤트와 위치 지정용 이벤트는 버린다."""
    for event in payload.get("events", []):
        segments = event.get("segs")
        if not segments:
            continue
        text = "".join(seg.get("utf8", "") for seg in segments).strip()
        if not text:
            continue
        yield format_stamp(event.get("tStartMs", 0)), text


def load_cues(path: Path) -> list[tuple[str, str]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return list(iter_cues(payload))


def find_matches(cues: list[tuple[str, str]], terms: list[str]) -> list[list[tuple[str, str]]]:
    """검색어를 포함한 자막마다 앞뒤 문맥을 붙여 돌려준다.

    한 줄만 보면 문장이 잘려 인용할 수 없어서 문맥을 함께 낸다.
    """
    needles = [term.lower() for term in terms if term]
    if not needles:
        return []
    windows = []
    for index, (_, text) in enumerate(cues):
        if not any(needle in text.lower() for needle in needles):
            continue
        start = max(0, index - CONTEXT_LINES)
        end = min(len(cues), index + CONTEXT_LINES + 1)
        windows.append(cues[start:end])
    return windows


def is_pipe_closed(error: OSError) -> bool:
    return isinstance(error, BrokenPipeError) or error.errno in _PIPE_CLOSED_ERRNOS


def silence_stdout() -> None:
    """남은 출력을 버린다 — 실패해도 무시한다.

    이걸 안 하면 인터프리터가 종료 시 stdout 을 한 번 더 flush 하다가 같은 오류를
    stderr 에 다시 뱉는다. 다만 이건 뒷정리일 뿐이라, stdout 이 fileno 를 안 주는
    환경(테스트 캡처 등)에서 여기서 터지면 정상 종료가 크래시로 바뀐다.
    """
    try:
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
    except (OSError, ValueError, AttributeError, io.UnsupportedOperation):
        pass


def emit(lines: Iterator[str]) -> int:
    """소비자가 파이프를 닫으면 조용히 멈춘다."""
    try:
        for line in lines:
            print(line)
        sys.stdout.flush()
    except OSError as error:
        if not is_pipe_closed(error):
            raise
        silence_stdout()
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, help="data/_cache/subs/ 아래 .json3 자막")
    parser.add_argument("terms", nargs="*", help="주변만 보고 싶을 때의 검색어(대소문자 무시)")
    args = parser.parse_args(argv)

    if not args.path.is_file():
        print(f"자막 파일이 없다: {args.path}", file=sys.stderr)
        return 2

    cues = load_cues(args.path)
    if not cues:
        print(f"자막이 비어 있다: {args.path}", file=sys.stderr)
        return 1

    if not args.terms:
        return emit(f"[{stamp}] {text}" for stamp, text in cues)

    windows = find_matches(cues, args.terms)
    if not windows:
        print(f"일치 없음: {' '.join(args.terms)}", file=sys.stderr)
        return 1
    return emit(
        "--- " + " ".join(f"[{stamp}] {text}" for stamp, text in window) for window in windows
    )


if __name__ == "__main__":
    raise SystemExit(main())
