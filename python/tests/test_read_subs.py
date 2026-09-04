"""`scripts/read_subs.py` — 자막 인용 스탬프 보존 + 검색 문맥.

가이드 문서의 근거는 `영상 12:34` 스탬프다. 스탬프가 어긋나면 검증기
(`scripts/guide_evidence_check.py`)가 잡아내기 전에 잘못된 근거가 나간다.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "read_subs.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("read_subs", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


read_subs = _load_module()


def _cue(start_ms: int, text: str) -> dict:
    return {"tStartMs": start_ms, "segs": [{"utf8": text}]}


def test_format_stamp_matches_youtube_display():
    assert read_subs.format_stamp(0) == "0:00"
    assert read_subs.format_stamp(9_000) == "0:09"
    assert read_subs.format_stamp(69_000) == "1:09"
    # 54:24 짜리 LexD 최종본 같은 장편이 mm:ss 로 남아야 인용이 영상과 맞는다.
    assert read_subs.format_stamp(3_264_000) == "54:24"
    # 팟캐스트는 한 시간을 넘는다.
    assert read_subs.format_stamp(6_199_000) == "1:43:19"


def test_iter_cues_drops_empty_and_positional_events():
    payload = {
        "events": [
            {"tStartMs": 0},  # segs 없음 — 자막이 아니라 위치 지정 이벤트
            _cue(1_000, "   "),  # 공백만
            _cue(2_000, "armor is not useless"),
        ]
    }
    assert list(read_subs.iter_cues(payload)) == [("0:02", "armor is not useless")]


def test_iter_cues_joins_split_segments():
    """자동 자막은 한 문장을 seg 여러 개로 쪼갠다. 붙이지 않으면 검색이 샌다."""
    payload = {"events": [{"tStartMs": 5_000, "segs": [{"utf8": "9,"}, {"utf8": "000 phys"}]}]}
    assert list(read_subs.iter_cues(payload)) == [("0:05", "9,000 phys")]


def test_find_matches_includes_surrounding_context():
    cues = [(f"0:{i:02d}", f"line {i}") for i in range(10)]
    cues[5] = ("0:05", "we need 100K armor")
    windows = read_subs.find_matches(cues, ["100K armor"])
    assert len(windows) == 1
    # 한 줄만 보면 문장이 잘려 인용할 수 없다 — 앞뒤 2줄이 함께 나와야 한다.
    assert windows[0] == cues[3:8]


def test_find_matches_is_case_insensitive_and_ignores_blank_terms():
    cues = [("0:01", "Smith of Kitava")]
    assert read_subs.find_matches(cues, ["", "smith of kitava"]) == [cues]
    assert read_subs.find_matches(cues, ["", ""]) == []


def test_load_cues_reads_utf8_korean(tmp_path: Path):
    """한국어 자막이 cp949 로 읽히면 조용히 깨진다 — 인코딩을 고정한다."""
    path = tmp_path / "sample.ko.json3"
    payload = {"events": [_cue(174_000, "경로석 정규식으로 원인불명 사망을 막는다")]}
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    assert read_subs.load_cues(path) == [("2:54", "경로석 정규식으로 원인불명 사망을 막는다")]


def test_main_reports_missing_file_without_traceback(tmp_path: Path, capsys):
    assert read_subs.main([str(tmp_path / "nope.json3")]) == 2
    assert "자막 파일이 없다" in capsys.readouterr().err


def test_main_reports_no_match(tmp_path: Path, capsys):
    path = tmp_path / "s.json3"
    path.write_text(json.dumps({"events": [_cue(0, "hello")]}), encoding="utf-8")
    assert read_subs.main([str(path), "kitava"]) == 1
    assert "일치 없음" in capsys.readouterr().err


def test_is_pipe_closed_covers_windows_einval():
    """Windows 는 파이프가 닫히면 BrokenPipeError 가 아니라 OSError(EINVAL) 을 준다."""
    import errno as _errno

    assert read_subs.is_pipe_closed(BrokenPipeError())
    assert read_subs.is_pipe_closed(OSError(_errno.EPIPE, "broken pipe"))
    assert read_subs.is_pipe_closed(OSError(_errno.EINVAL, "Invalid argument"))
    assert not read_subs.is_pipe_closed(OSError(_errno.ENOENT, "no such file"))


def test_emit_swallows_closed_pipe_without_traceback(monkeypatch, capsys):
    """`| head` 로 자를 때 트레이스백이 뜨면 인코딩 문제로 오진하게 된다."""
    import errno as _errno

    printed = []

    def fake_print(line):
        printed.append(line)
        if len(printed) == 2:
            raise OSError(_errno.EINVAL, "Invalid argument")

    monkeypatch.setattr(read_subs, "print", fake_print, raising=False)

    assert read_subs.emit(iter(["a", "b", "c"])) == 0
    assert printed == ["a", "b"]


def test_emit_reraises_real_oserror(monkeypatch):
    """디스크 오류까지 삼키면 안 된다."""
    import errno as _errno

    def fake_print(_line):
        raise OSError(_errno.ENOSPC, "no space left on device")

    monkeypatch.setattr(read_subs, "print", fake_print, raising=False)
    try:
        read_subs.emit(iter(["a"]))
    except OSError as error:
        assert error.errno == _errno.ENOSPC
    else:
        raise AssertionError("실제 OSError 는 그대로 올라와야 한다")
