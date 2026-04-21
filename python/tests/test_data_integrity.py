# -*- coding: utf-8 -*-
"""Phase H5-1 — data_integrity.check_base_item_drift 테스트."""

import hashlib
import json
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from data_integrity import (  # noqa: E402
    check_base_item_drift,
    _reset_drift_warnings,
    _repo_root,
)


def _real_sha() -> str:
    p = _repo_root() / "data" / "game_data" / "BaseItemTypes.json"
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def test_drift_match():
    _reset_drift_warnings()
    meta = {"source_sha256": _real_sha()}
    assert check_base_item_drift(meta, "test") is True


def test_drift_mismatch_warns():
    _reset_drift_warnings()
    meta = {"source_sha256": "0" * 64}
    with patch("data_integrity.logger") as mock_log:
        assert check_base_item_drift(meta, "test_mismatch") is False
        assert mock_log.warning.called


def test_drift_no_pin_passes():
    _reset_drift_warnings()
    assert check_base_item_drift({}, "test") is True
    assert check_base_item_drift(None, "test") is True  # type: ignore[arg-type]
    assert check_base_item_drift({"source_sha256": ""}, "test") is True


def test_drift_warning_dedupe():
    _reset_drift_warnings()
    meta = {"source_sha256": "1" * 64}
    with patch("data_integrity.logger") as mock_log:
        check_base_item_drift(meta, "dup_label")
        check_base_item_drift(meta, "dup_label")
        # 같은 (label, sha) 조합은 1회만 경고
        assert mock_log.warning.call_count == 1


def test_coach_normalizer_loads_without_drift():
    # 실 데이터 상태에서 drift 경고 없이 로드되는지 (SHA pin 이 현재 데이터와 일치)
    from coach_normalizer import _reset_caches, normalize_gem
    _reset_caches()
    _reset_drift_warnings()
    with patch("data_integrity.logger") as mock_log:
        # 임의의 젬 정규화 호출 → _load_valid_gems 발동
        normalize_gem("Cleave")
        # drift 경고 없어야 함 (refresh_valid_gems.py 방금 실행됨)
        assert not mock_log.warning.called, (
            f"drift 경고 발생: {mock_log.warning.call_args_list}"
        )
