"""GGPK truth reference 검증 (계층 1+3+5).

- 계층 1 (auto): data/game_data/*.json 실 추출값과 ref 파일 rows+content_hash 일치
- 계층 3 (semi-auto): schema.min.json의 현재 sha256 및 git commit이 ref.schema_pin과 일치
- 계층 5 (manual anchor drift): verified_at이 180일 경과 시 warning

실패 시 대응:
- content_hash 불일치 + anchored_to.expected_changes 설명 있음 → 예상된 리그 전환. ref 재빌드 후 커밋
- 불일치 + 설명 없음 → 조사 필요 (회귀 가능성)
- schema_pin 불일치 → schema 변경됨. 재해석 필요
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
REF_PATH = ROOT / "_analysis" / "ggpk_truth_reference.json"
GAME_DATA = ROOT / "data" / "game_data"
SCHEMA_FILE = ROOT / "data" / "schema" / "schema.min.json"

# Layer 5 stale 임계 — 리그 주기 3~4개월 → 180일이면 "최소 1리그 놓침" 신호
STALE_DAYS_THRESHOLD = 180

sys.path.insert(0, str(ROOT / "python" / "scripts"))
from ggpk_truth_builder import KEY_FIELDS, table_hash  # noqa: E402


@pytest.fixture(scope="module")
def ref() -> dict:
    if not REF_PATH.exists():
        pytest.skip(f"ref missing: {REF_PATH} -- python python/scripts/ggpk_truth_builder.py 먼저 실행")
    return json.loads(REF_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def has_game_data() -> bool:
    return GAME_DATA.exists() and any(GAME_DATA.glob("*.json"))


class TestLayer1Rows:
    """추출 산출물의 row 수가 ref 박제값과 일치하는가."""

    def test_all_tables_row_count_matches(self, ref, has_game_data):
        if not has_game_data:
            pytest.skip("data/game_data 비어있음. cargo run --bin extract_data -- --json 필요")
        mismatches = []
        for table, meta in ref["tables"].items():
            path = GAME_DATA / f"{table}.json"
            if not path.exists():
                mismatches.append(f"{table}: 파일 없음")
                continue
            rows = json.loads(path.read_text(encoding="utf-8"))
            if len(rows) != meta["rows"]:
                mismatches.append(
                    f"{table}: ref={meta['rows']} vs extract={len(rows)}"
                )
        assert not mismatches, (
            "row count drift 감지:\n  " + "\n  ".join(mismatches)
            + "\n→ anchored_to.expected_changes에 원인 있으면 ref 재빌드, 없으면 조사"
        )


class TestLayer1ContentHash:
    """content hash 일치 — rows 수가 같아도 내용 바뀌면 감지."""

    def test_all_content_hashes_match(self, ref, has_game_data):
        if not has_game_data:
            pytest.skip("data/game_data 비어있음")
        mismatches = []
        for table, meta in ref["tables"].items():
            path = GAME_DATA / f"{table}.json"
            if not path.exists():
                continue
            rows = json.loads(path.read_text(encoding="utf-8"))
            fields = tuple(meta["key_fields"])
            actual = table_hash(rows, fields)
            if actual != meta["content_hash"]:
                mismatches.append(
                    f"{table}: ref={meta['content_hash'][:12]}.. vs extract={actual[:12]}.."
                )
        assert not mismatches, (
            "content drift 감지 (rows 동일하나 내용 변경):\n  " + "\n  ".join(mismatches)
            + "\n→ 리그 전환이면 expected_changes 반영 후 builder 재실행, 아니면 회귀 조사"
        )


class TestLayer3SchemaPin:
    """schema.min.json 고정 상태 검증."""

    def test_schema_sha256_matches_pin(self, ref):
        pin = ref["schema_pin"]
        current_sha = hashlib.sha256(SCHEMA_FILE.read_bytes()).hexdigest()
        assert current_sha == pin["sha256"], (
            f"schema sha 불일치: ref={pin['sha256'][:12]}.. vs current={current_sha[:12]}..\n"
            f"→ 스키마 변경됨. content_hash 전부 재해석 필요."
        )

    def test_schema_size_matches(self, ref):
        pin = ref["schema_pin"]
        assert SCHEMA_FILE.stat().st_size == pin["size_bytes"]


class TestLayer5AnchorFreshness:
    """verified_at이 STALE_DAYS_THRESHOLD 이상 경과했는지 soft warning."""

    def test_anchor_not_stale(self, ref):
        verified_at = ref["anchored_to"]["verified_at"]
        verified = dt.date.fromisoformat(verified_at)
        today = dt.date.today()
        days_elapsed = (today - verified).days
        assert days_elapsed <= STALE_DAYS_THRESHOLD, (
            f"anchor stale: verified_at={verified_at}, {days_elapsed}일 경과 (임계 {STALE_DAYS_THRESHOLD}일)\n"
            f"→ 최신 리그 패치노트 확인 후 ref 재빌드 + verified_at 갱신"
        )


class TestReferenceStructure:
    """ref 파일 필수 필드 검증."""

    def test_required_top_level_fields(self, ref):
        for k in ("patch_note_sources", "anchored_to", "schema_pin", "extractor_pin", "tables"):
            assert k in ref, f"ref 누락 필드: {k}"

    def test_all_19_tables_present(self, ref):
        assert len(ref["tables"]) == 19, f"테이블 19개 기대, got {len(ref['tables'])}"
        for table in KEY_FIELDS.keys():
            assert table in ref["tables"], f"ref에 {table} 없음"

    def test_patch_note_sources_urls(self, ref):
        src = ref["patch_note_sources"]
        assert src["canonical_forum"].startswith("https://www.pathofexile.com/")
        assert src["wiki_version_history"].startswith("https://www.poewiki.net/")
