# -*- coding: utf-8 -*-
"""데이터 무결성 체크 공용 유틸 — Phase H5-1.

valid_gems.json 및 BaseItemTypes.json 파생 파일이 상위 원천과 싱크 되어 있는지
런타임 진입 시 확인한다. drift 감지 시 경고만 (차단 없음) — 리프레시 실행 안내.

사용:
  check_base_item_drift(valid_gems_json_data, label="coach_normalizer")
"""

from __future__ import annotations

import hashlib
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger("data_integrity")

_DRIFT_WARNED: set[str] = set()  # 같은 (label, expected) 로 반복 경고 방지


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _sha256(path: Path) -> str | None:
    try:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()
    except OSError as e:
        logger.warning("sha256 계산 실패 (%s): %s", path, e)
        return None


def check_base_item_drift(meta: Any, label: str) -> bool:
    """valid_gems.json._meta 의 source_sha256 이 현재 BaseItemTypes.json 과 일치하는지 확인.

    일치/파일 없음 → True. 불일치 → 경고 + False.
    경고는 프로세스 당 (label, expected_sha) 조합 1회만.
    """
    if not isinstance(meta, dict):
        return True
    expected = meta.get("source_sha256")
    if not isinstance(expected, str) or not expected:
        return True  # drift pin 없는 구버전 파일 — 체크 스킵

    base_path = _repo_root() / "data" / "game_data" / "BaseItemTypes.json"
    if not base_path.exists():
        return True  # 원천 없음 — 검증 불가, 조용히 패스

    actual = _sha256(base_path)
    if actual is None:
        return True
    if actual == expected:
        return True

    key = f"{label}:{expected}"
    if key in _DRIFT_WARNED:
        return False
    _DRIFT_WARNED.add(key)
    logger.warning(
        "[%s] BaseItemTypes.json drift 감지 — expected=%s actual=%s. "
        "scripts/refresh_valid_gems.py 재실행 권장.",
        label, expected[:12] + "...", actual[:12] + "...",
    )
    return False


def _reset_drift_warnings() -> None:
    """테스트 전용."""
    _DRIFT_WARNED.clear()
