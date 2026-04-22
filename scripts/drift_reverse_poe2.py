"""
POE2 datc64 drift 역추적.

SkillGems: schema 207B + drift 32B = actual 239B
Mods: schema 653B + drift 24B = actual 677B

분석 방법:
1. Header (4B row_count) 읽기
2. Marker 0xBB×8 위치 찾기 → fixed data 크기 계산
3. row_size 추정 (fixed_size / row_count)
4. row 의 schema 뒤 끝 N바이트 추출
5. Row 간 패턴 비교: 모두 0 / 모두 같은 값 / range 등으로 타입 추정

타입 추정 heuristic:
- 8B 반복 0xFEFEFEFEFEFEFEFE → null foreignrow (Key 절반)
- 16B 0x00*16 → null List or null Key
- 8B 작은 수 (0~10000) → index or rowid
- 8B 0 → bool/enum padding 또는 null
- 16B (count_i64 + offset_i64) where 0 <= count < 10000 and 0 <= offset < variable_data_size → List
"""
from __future__ import annotations

import struct
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "game_data_poe2"

MARKER = b"\xbb" * 8


def read_header_and_fixed(path: Path, schema_row_size: int, drift: int) -> tuple[int, int, bytes, bytes]:
    """
    Returns: (row_count, actual_row_size, drift_region_first_row, drift_region_sampled_rows)
    """
    data = path.read_bytes()
    row_count = struct.unpack_from("<I", data, 0)[0]

    # Find marker position
    marker_pos = data.find(MARKER, 4)
    if marker_pos < 0:
        raise ValueError(f"Marker 0xBB*8 not found in {path.name}")

    fixed_size = marker_pos - 4
    actual_row_size = fixed_size // row_count
    assert actual_row_size * row_count == fixed_size, f"row_size 불일치: {fixed_size} / {row_count}"

    print(f"  file={path.name} row_count={row_count} actual_row_size={actual_row_size}")
    print(f"  schema_row_size={schema_row_size}  drift=+{actual_row_size - schema_row_size}B  expected=+{drift}B")

    # 첫 row 의 drift 영역 (schema 뒤 N바이트)
    row0_start = 4
    drift_start = row0_start + schema_row_size
    drift_end = row0_start + actual_row_size
    row0_drift = data[drift_start:drift_end]

    # 여러 row 의 drift 영역 샘플 (0, 1, 2, 100, 500)
    sample_indices = [0, 1, 2, 100, 500, row_count - 1]
    samples = []
    for idx in sample_indices:
        if idx >= row_count:
            continue
        start = 4 + idx * actual_row_size + schema_row_size
        end = start + (actual_row_size - schema_row_size)
        samples.append((idx, data[start:end]))

    return row_count, actual_row_size, row0_drift, samples


def hex_grouped(b: bytes) -> str:
    """Hex 출력 — 8바이트 단위로 구분."""
    result = []
    for i in range(0, len(b), 8):
        chunk = b[i:i + 8]
        result.append(chunk.hex())
    return " ".join(result)


def analyze_8byte_chunks(chunks: list[bytes]) -> list[str]:
    """여러 row 의 동일 8B chunk 들 타입 추정."""
    if not chunks:
        return []
    # Transpose: 각 row 의 8B chunk 리스트 → column-wise
    n_chunks = len(chunks[0]) // 8
    verdicts = []
    for col in range(n_chunks):
        col_values = []
        for row in chunks:
            if len(row) >= (col + 1) * 8:
                col_values.append(struct.unpack_from("<Q", row, col * 8)[0])
        if not col_values:
            continue

        # null marker
        all_fe = all(v == 0xFEFEFEFEFEFEFEFE for v in col_values)
        all_zero = all(v == 0 for v in col_values)

        # uninitialized
        all_same = len(set(col_values)) == 1
        max_v = max(col_values)
        min_v = min(col_values)

        verdict_parts = []
        if all_fe:
            verdict_parts.append("NULL_FOREIGNROW (0xFE...)")
        elif all_zero:
            verdict_parts.append("all zero (bool/enum/null)")
        elif all_same:
            verdict_parts.append(f"const {hex(col_values[0])}")
        else:
            if max_v < 1_000_000 and min_v >= 0:
                verdict_parts.append(f"small uint ({min_v}..{max_v}) → rowid/count")
            elif max_v == 0xFEFEFEFEFEFEFEFE:
                verdict_parts.append("mixed NULL/value → nullable foreignrow")
            else:
                verdict_parts.append(f"varied ({min_v}..{max_v})")

        sample_hex = ",".join(hex(v) for v in col_values[:3])
        verdicts.append(f"    col[{col}] ({col*8}..{col*8+8}): {'; '.join(verdict_parts)} | sample={sample_hex}")

    return verdicts


def main() -> None:
    print("=== SkillGems drift 분석 ===")
    rc, ars, row0_drift, samples = read_header_and_fixed(
        DATA_DIR / "SkillGems.datc64",
        schema_row_size=207,
        drift=32,
    )
    print(f"  row[0] drift {len(row0_drift)}B hex: {hex_grouped(row0_drift)}")
    print(f"  sample rows drift region:")
    for idx, chunk in samples:
        print(f"    row[{idx}]: {hex_grouped(chunk)}")
    print(f"  컬럼별 타입 추정:")
    for line in analyze_8byte_chunks([s[1] for s in samples]):
        print(line)

    print()
    print("=== Mods drift 분석 ===")
    # Mods 는 JSON 이 없어서 row_count 를 스키마 기반 계산
    rc, ars, row0_drift, samples = read_header_and_fixed(
        DATA_DIR / "Mods.datc64",
        schema_row_size=653,
        drift=24,
    )
    print(f"  row[0] drift {len(row0_drift)}B hex: {hex_grouped(row0_drift)}")
    print(f"  sample rows drift region:")
    for idx, chunk in samples:
        print(f"    row[{idx}]: {hex_grouped(chunk)}")
    print(f"  컬럼별 타입 추정:")
    for line in analyze_8byte_chunks([s[1] for s in samples]):
        print(line)


if __name__ == "__main__":
    main()
