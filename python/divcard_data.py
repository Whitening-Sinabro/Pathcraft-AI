"""디비카 ↔ 유니크 매핑 단일 진실원 로더.

기존 `build_extractor.UNIQUE_TO_DIVCARD` + `wiki_data_provider.KNOWN_DIV_CARDS`를
`data/divcard_mapping.json` 하나로 통합. 두 소비처가 모두 이 모듈을 경유.

데이터 구조:
    {
      "Mageblood": [{"card": "The Apothecary", "stack": 13}],
      "Headhunter": [{"card": "The Doctor", "stack": 8}, ...],
      ...
    }
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

_DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "divcard_mapping.json"
_CACHE: dict[str, list[dict]] | None = None


def load_divcard_mapping() -> dict[str, list[dict]]:
    """{unique_name: [{"card": str, "stack": int}, ...]}.

    파일 누락/JSON 파싱 실패 시 빈 dict 반환 + error 로깅.
    빈 dict 반환은 의도적 — 호출 측에서 `mapping.get(name, [])` 패턴으로 안전하게 폴백.
    """
    global _CACHE
    if _CACHE is not None:
        return _CACHE

    try:
        raw = json.loads(_DATA_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError:
        logger.error(
            "divcard_mapping.json missing at %s — run scripts/refresh_divcard_mapping.py",
            _DATA_PATH,
        )
        _CACHE = {}
        return _CACHE
    except json.JSONDecodeError as e:
        logger.error("divcard_mapping.json invalid JSON: %s", e)
        _CACHE = {}
        return _CACHE

    _CACHE = raw.get("unique_to_cards", {})
    return _CACHE


def reset_cache() -> None:
    """테스트용 — 캐시 초기화."""
    global _CACHE
    _CACHE = None
