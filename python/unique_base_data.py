"""유니크 → chanceable base 매핑 단일 진실원 로더.

기존 `build_extractor.UNIQUE_TO_BASE` 하드코딩 dict를 `data/unique_base_mapping.json`
으로 이관. POB에 `base_type` 필드가 없을 때 fallback + L10 re_show chanceable block
생성에서 소비.

데이터 구조:
    {"Mageblood": "Heavy Belt", "Tabula Rasa": "Simple Robe", ...}
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

_DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "unique_base_mapping.json"
_CACHE: dict[str, str] | None = None


def load_unique_base_mapping() -> dict[str, str]:
    """{unique_name: base_type_name}.

    파일 누락/JSON 파싱 실패 시 빈 dict 반환 + error 로깅.
    호출 측은 `mapping.get(name)` 패턴으로 안전하게 None 폴백.
    """
    global _CACHE
    if _CACHE is not None:
        return _CACHE

    try:
        raw = json.loads(_DATA_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError:
        logger.error(
            "unique_base_mapping.json missing at %s — run scripts/refresh_unique_base_mapping.py",
            _DATA_PATH,
        )
        _CACHE = {}
        return _CACHE
    except json.JSONDecodeError as e:
        logger.error("unique_base_mapping.json invalid JSON: %s", e)
        _CACHE = {}
        return _CACHE

    _CACHE = raw.get("unique_to_base", {})
    return _CACHE


def reset_cache() -> None:
    """테스트용 — 캐시 초기화."""
    global _CACHE
    _CACHE = None
