"""`scripts/ggpk_explore.py` — GGPK 레코드 파싱과 무결성 판정.

이 도구의 존재 이유는 `verify` 다. 2026-09-04 에 POE2 추출 실패 원인을 두 번
잘못 짚었다(리더 결함 -> 포맷 변경). 실제로는 **패치가 덜 받아진 레코드의 저장
해시가 전부 0** 이었고, 그걸 보는 순간 끝났다. 그 판정이 안 깨지게 고정한다.

실제 GGPK(142GB)는 테스트에 못 쓰므로 같은 포맷의 최소 파일을 합성한다.
"""
from __future__ import annotations

import hashlib
import importlib.util
import struct
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "ggpk_explore.py"


def _load():
    spec = importlib.util.spec_from_file_location("ggpk_explore", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ggpk = _load()


def _name(text: str) -> bytes:
    """GGPK 이름은 UTF-16LE + null 종결. 길이 필드는 '문자 수'다."""
    return (text + "\0").encode("utf-16-le")


def _file(name: str, data: bytes, digest: bytes | None = None) -> bytes:
    """FILE 레코드: [len][FILE][name_len][sha256 32B][name][data]"""
    sha = hashlib.sha256(data).digest() if digest is None else digest
    body = struct.pack("<I", len(name) + 1) + sha + _name(name) + data
    return struct.pack("<I", 8 + len(body)) + b"FILE" + body


def _dir(name: str, child_offsets: list[int]) -> bytes:
    """PDIR 레코드: [len][PDIR][name_len][entry_count][hash 32B][name][(hash,off)…]"""
    entries = b"".join(struct.pack("<IQ", 0, off) for off in child_offsets)
    body = (struct.pack("<II", len(name) + 1, len(child_offsets))
            + bytes(32) + _name(name) + entries)
    return struct.pack("<I", 8 + len(body)) + b"PDIR" + body


def build_ggpk(tmp: Path) -> Path:
    """루트 PDIR 하나에 정상 파일 하나 + 해시 0 파일 하나를 담은 최소 GGPK."""
    good = _file("good.txt", b"hello ggpk")
    stale = _file("stale.bin", b"\x01\x02\x03\x04", digest=bytes(32))

    head_len = 4 + 4 + 4 + 8 * 1  # len + tag + version + child offset 1개
    good_off = head_len
    stale_off = good_off + len(good)
    root_off = stale_off + len(stale)
    root = _dir("", [good_off, stale_off])

    head = struct.pack("<I", head_len) + b"GGPK" + struct.pack("<I", 3) + struct.pack("<Q", root_off)
    path = tmp / "Content.ggpk"
    path.write_bytes(head + good + stale + root)
    return path


def test_root_and_listing(tmp_path: Path, capsys):
    path = build_ggpk(tmp_path)
    with path.open("rb") as f:
        node = ggpk.root_dir(f)
        names = sorted(ggpk.peek(f, c)[1] for c in ggpk.children(f, node))
    assert names == ["good.txt", "stale.bin"]


def test_resolve_reads_file_payload(tmp_path: Path):
    path = build_ggpk(tmp_path)
    with path.open("rb") as f:
        tag, name, length, data, node = ggpk.resolve(f, "good.txt")
        assert tag == "FILE" and name == "good.txt"
        size = length - (data - node)
        f.seek(data)
        assert f.read(size) == b"hello ggpk"


def test_stored_hash_matches_for_intact_file(tmp_path: Path):
    path = build_ggpk(tmp_path)
    with path.open("rb") as f:
        node = ggpk.resolve(f, "good.txt")[-1]
        stored, off, size = ggpk.file_record(f, node)
        assert stored == ggpk.sha256_of(f, off, size)


def test_verify_flags_zero_hash_as_incomplete(tmp_path: Path, capsys):
    """해시가 0 인 레코드는 '미완료'로 잡히고 종료 코드가 0 이 아니어야 한다.

    이걸 놓쳐서 멀쩡한 리더를 두 번 의심했다.
    """
    path = build_ggpk(tmp_path)
    rc = ggpk.main(["verify", "", "--ggpk", str(path)])
    out = capsys.readouterr().out
    assert rc == 1
    assert "stale.bin" in out and "미완료" in out
    assert "정상 1" in out and "미완료(해시 0) 1" in out
    assert "패치를 끝내라" in out


def test_verify_deep_catches_corrupted_content(tmp_path: Path, capsys):
    """저장 해시는 0 이 아닌데 내용이 다르면 --deep 이 잡아야 한다."""
    path = build_ggpk(tmp_path)
    raw = bytearray(path.read_bytes())
    i = raw.index(b"hello ggpk")
    raw[i : i + 5] = b"HELLO"
    path.write_bytes(bytes(raw))

    rc = ggpk.main(["verify", "", "--deep", "--ggpk", str(path)])
    out = capsys.readouterr().out
    assert rc == 1
    assert "불일치" in out and "good.txt" in out


def test_verify_single_file_path(tmp_path: Path, capsys):
    path = build_ggpk(tmp_path)
    assert ggpk.main(["verify", "good.txt", "--deep", "--ggpk", str(path)]) == 0
    assert "미완료(해시 0) 0" in capsys.readouterr().out


def test_cat_hexdump(tmp_path: Path, capsys):
    path = build_ggpk(tmp_path)
    assert ggpk.main(["cat", "good.txt", "--ggpk", str(path)]) == 0
    out = capsys.readouterr().out
    assert "hello ggpk" in out  # ASCII 열
    assert "68 65 6c 6c 6f" in out  # hex 열


def test_cat_writes_file(tmp_path: Path):
    path = build_ggpk(tmp_path)
    out = tmp_path / "dump.bin"
    assert ggpk.main(["cat", "good.txt", "--out", str(out), "--ggpk", str(path)]) == 0
    assert out.read_bytes() == b"hello ggpk"


def test_missing_path_exits(tmp_path: Path):
    path = build_ggpk(tmp_path)
    try:
        ggpk.main(["ls", "nope", "--ggpk", str(path)])
    except SystemExit as e:
        assert "경로 없음" in str(e)
    else:
        raise AssertionError("없는 경로는 SystemExit 이어야 한다")
