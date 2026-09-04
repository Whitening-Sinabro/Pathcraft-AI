"""GGPK 탐색기 — 경로로 열람 · 덤프 · 무결성 확인.

142GB 파일이라 트리 전체 재귀는 안 끝난다. 경로를 따라 한 단계씩만 내려간다.

    python scripts/ggpk_explore.py ls     Bundles2
    python scripts/ggpk_explore.py cat    Bundles2/_.index.high.bin --hex 200
    python scripts/ggpk_explore.py cat    Bundles2/_.index.bin --out D:/tmp/index.bin
    python scripts/ggpk_explore.py verify Bundles2
    python scripts/ggpk_explore.py verify Bundles2/_.index.bin --deep

`verify` 가 이 도구의 핵심이다. GGPK FILE 레코드는 내용의 SHA256 을 32바이트로
들고 있는데, **패치가 덜 받아진 파일은 그 자리가 전부 0** 이다. 추출이 실패할 때
"우리 파서가 틀렸나 / 포맷이 바뀌었나" 를 헤매기 전에 이걸 먼저 본다 —
2026-09-04 에 그렇게 두 번 잘못 진단했다. `_.index.bin` 의 해시가 0 이면
게임 클라이언트를 켜서 패치를 끝내는 것이 답이고, 리버싱할 것이 없다.
"""
from __future__ import annotations

import argparse
import hashlib
import struct
import sys

GGPK = (r"C:\Program Files (x86)\Grinding Gear Games"
        r"\Path of Exile 2 - poe2_production\Content.ggpk")
NUL = chr(0)
ZERO32 = bytes(32)


def u32(f) -> int:
    return struct.unpack("<I", f.read(4))[0]


def u64(f) -> int:
    return struct.unpack("<Q", f.read(8))[0]


def record(f, off) -> tuple[int, str]:
    """레코드 헤더 -> (length, tag)."""
    f.seek(off)
    return u32(f), f.read(4).decode("ascii", "replace")


def peek(f, off) -> tuple[str, str, int, int]:
    """(tag, name, record_length, 데이터/엔트리 시작 위치)."""
    length, tag = record(f, off)
    if tag == "PDIR":
        name_len = u32(f)
        u32(f)  # entry count
        f.seek(32, 1)  # hash
        return tag, f.read(name_len * 2).decode("utf-16-le").rstrip(NUL), length, f.tell()
    if tag == "FILE":
        name_len = u32(f)
        f.seek(32, 1)  # sha256
        return tag, f.read(name_len * 2).decode("utf-16-le").rstrip(NUL), length, f.tell()
    return tag, "", length, f.tell()


def children(f, off) -> list[int]:
    """PDIR 의 자식 오프셋 목록. FILE 이면 빈 목록."""
    length, tag = record(f, off)
    if tag != "PDIR":
        return []
    name_len = u32(f)
    count = u32(f)
    f.seek(32, 1)
    f.read(name_len * 2)
    out = []
    for _ in range(count):
        u32(f)  # name hash
        out.append(u64(f))
    return out


def root_dir(f) -> int:
    """GGPK v3 루트에는 child_count 필드가 없다 — 레코드 길이에서 역산한다."""
    root_len, tag = record(f, 0)
    if tag != "GGPK":
        raise SystemExit(f"루트 태그가 GGPK 가 아니다: {tag}")
    u32(f)  # version
    for off in [u64(f) for _ in range((root_len - 12) // 8)]:
        if record(f, off)[1] == "PDIR":
            return off
    raise SystemExit("root PDIR 없음")


def resolve(f, path: str) -> tuple[str, str, int, int, int]:
    """'Bundles2/Folders/2D' -> (tag, name, length, data_off, node_off)."""
    node = root_dir(f)
    info: tuple[str, str, int, int] = ("PDIR", "", 0, 0)
    for seg in [s for s in path.split("/") if s]:
        for child in children(f, node):
            tag, name, length, data = peek(f, child)
            if name.lower() == seg.lower():
                node, info = child, (tag, name, length, data)
                break
        else:
            raise SystemExit(f"경로 없음: {seg} (in {path})")
    return (*info, node)


def file_record(f, node) -> tuple[bytes | None, int, int]:
    """FILE 레코드 -> (저장된 32B 해시, data_off, size)."""
    f.seek(node)
    rec_len = u32(f)
    if f.read(4) != b"FILE":
        return None, 0, 0
    name_len = u32(f)
    stored = f.read(32)
    f.read(name_len * 2)
    data_off = f.tell()
    return stored, data_off, rec_len - (data_off - node)


def sha256_of(f, off: int, size: int) -> bytes:
    h = hashlib.sha256()
    f.seek(off)
    left = size
    while left:
        chunk = f.read(min(1 << 22, left))
        if not chunk:
            break
        h.update(chunk)
        left -= len(chunk)
    return h.digest()


def cmd_ls(f, args) -> int:
    node = root_dir(f) if not args.path else resolve(f, args.path)[-1]
    kids = children(f, node)
    print(f"{args.path or '/'} — {len(kids)}개")
    rows = []
    for child in kids:
        tag, name, length, data = peek(f, child)
        rows.append((tag, name, length - (data - child) if tag == "FILE" else 0))
    rows.sort(key=lambda r: (r[0] != "PDIR", r[1].lower()))
    for tag, name, size in rows[: args.limit]:
        print(f"  [{tag}] {name}" + (f"   {size:,}B" if tag == "FILE" else ""))
    if len(rows) > args.limit:
        print(f"  … 외 {len(rows) - args.limit}개")
    return 0


def cmd_cat(f, args) -> int:
    tag, name, length, data, node = resolve(f, args.path)
    if tag != "FILE":
        raise SystemExit(f"파일이 아니다: {tag}")
    size = length - (data - node)
    print(f"{args.path}  record@{node:,}  data@{data:,}  {size:,}B")
    if args.out:
        f.seek(data)
        with open(args.out, "wb") as w:
            left = size
            while left:
                chunk = f.read(min(1 << 20, left))
                if not chunk:
                    break
                w.write(chunk)
                left -= len(chunk)
        print(f"  -> {args.out}")
        return 0
    f.seek(data)
    raw = f.read(min(args.hex, size))
    for i in range(0, len(raw), 16):
        row = raw[i : i + 16]
        text = "".join(chr(b) if 32 <= b < 127 else "." for b in row)
        print(f"  {i:04x}  {row.hex(' '):<47}  {text}")
    return 0


def cmd_verify(f, args) -> int:
    """저장 해시가 0 인 레코드(=패치 미완료)를 골라낸다. --deep 이면 실제 해시까지 대조."""
    if args.path:
        tag, _name, _length, _data, node = resolve(f, args.path)
    else:
        tag, node = "PDIR", root_dir(f)
    targets = [node] if tag == "FILE" else children(f, node)

    live = placeholder = mismatch = 0
    for child in targets:
        stored, off, size = file_record(f, child)
        if stored is None:
            continue
        name = peek(f, child)[1]
        if stored == ZERO32:
            placeholder += 1
            print(f"  [미완료] {name:<34} {size:>14,}B  저장 해시가 0")
            continue
        live += 1
        if not args.deep:
            continue
        if sha256_of(f, off, size) != stored:
            mismatch += 1
            print(f"  [불일치] {name:<34} {size:>14,}B")
        elif args.verbose:
            print(f"  [정상]   {name:<34} {size:>14,}B")

    tail = f" · 해시 불일치 {mismatch}" if args.deep else " · (--deep 으로 실제 해시 대조)"
    print(f"\n  정상 {live} · 미완료(해시 0) {placeholder}{tail}")
    if placeholder:
        print("  -> 미완료가 있으면 게임 클라이언트를 켜서 패치를 끝내라. 파서 문제가 아니다.")
    return 1 if (placeholder or mismatch) else 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("cmd", choices=["ls", "cat", "verify"])
    ap.add_argument("path", nargs="?", default="")
    ap.add_argument("--hex", type=int, default=128)
    ap.add_argument("--out")
    ap.add_argument("--limit", type=int, default=60)
    ap.add_argument("--deep", action="store_true", help="verify: 실제 SHA256 까지 대조")
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--ggpk", default=GGPK)
    args = ap.parse_args(argv)
    with open(args.ggpk, "rb") as f:
        return {"ls": cmd_ls, "cat": cmd_cat, "verify": cmd_verify}[args.cmd](f, args)


if __name__ == "__main__":
    raise SystemExit(main())
