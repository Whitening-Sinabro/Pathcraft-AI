"""Layer 2 독립 추출기 cross-check 검증.

`_analysis/crosscheck/tables/English/*.json`가 있을 때만 실행 (soft 테스트).
없으면 skip — CI에서 crosscheck는 선택적.

재현:
    npm install -g pathofexile-dat
    cd _analysis/crosscheck
    node "$(npm root -g)/pathofexile-dat/dist/cli/run.js"
    cd ../..
    python -m pytest python/tests/test_ggpk_crosscheck.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "python" / "scripts"))

from ggpk_crosscheck import COMPARE_FIELDS, THEIRS_DIR, compare_table  # noqa: E402


@pytest.fixture(scope="module")
def has_crosscheck_output() -> bool:
    return THEIRS_DIR.exists() and any(THEIRS_DIR.glob("*.json"))


@pytest.mark.parametrize("table,fields", list(COMPARE_FIELDS.items()))
def test_table_matches_independent_extractor(table, fields, has_crosscheck_output):
    if not has_crosscheck_output:
        pytest.skip(
            f"{THEIRS_DIR.relative_to(ROOT)} 없음. "
            "pathofexile-dat CLI 실행 필요 (README 참조)"
        )
    result = compare_table(table, fields)
    assert result["status"] in ("ok", "ok_rows_only"), (
        f"{table} 교차검증 실패: {result.get('reason', '')}\n"
        f"전체 결과: {result}"
    )
