# -*- coding: utf-8 -*-
"""pob_parser.get_pob_code_from_url 타임아웃 재시도 로직 회귀 테스트.

검증:
- Timeout 1회 + 성공 1회 → 성공 (재시도 성공)
- Timeout 2회 → None (재시도 후 포기)
- 비-Timeout 예외(ConnectionError) → 재시도 없이 즉시 None
- 정상 1회 → 성공 (재시도 안 함)
"""

import sys
import os
from unittest.mock import patch, MagicMock

import pytest
import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pob_parser import get_pob_code_from_url


def _mk_response(text: str, *, pastebin: bool = False) -> MagicMock:
    """pastebin/raw 경로면 response.text 반환 경로, 아니면 HTML (textarea) 경로."""
    r = MagicMock()
    r.raise_for_status = MagicMock()
    if pastebin:
        r.text = text
    else:
        r.content = f'<html><body><textarea>{text}</textarea></body></html>'.encode()
    return r


class TestTimeoutRetry:
    def test_timeout_then_success(self):
        """Timeout 1회 후 재시도 성공 → 정상 결과 반환."""
        success = _mk_response("pob_code_abc", pastebin=True)
        with patch("pob_parser.requests.get",
                   side_effect=[requests.exceptions.Timeout("t"), success]) as mock_get:
            result = get_pob_code_from_url("https://pastebin.com/raw/xyz")
        assert result == "pob_code_abc"
        assert mock_get.call_count == 2

    def test_two_timeouts_returns_none(self):
        """Timeout 2회 → 포기, None."""
        with patch("pob_parser.requests.get",
                   side_effect=[requests.exceptions.Timeout("t1"),
                                requests.exceptions.Timeout("t2")]) as mock_get:
            result = get_pob_code_from_url("https://pobb.in/xyz")
        assert result is None
        assert mock_get.call_count == 2

    def test_connection_error_no_retry(self):
        """네트워크 에러(ConnectionError)는 재시도 없이 즉시 None."""
        with patch("pob_parser.requests.get",
                   side_effect=requests.exceptions.ConnectionError("dns")) as mock_get:
            result = get_pob_code_from_url("https://pobb.in/xyz")
        assert result is None
        # 재시도 없음 — 1회만 호출
        assert mock_get.call_count == 1

    def test_first_call_success_no_retry(self):
        """1회 성공 → 재시도 없음."""
        success = _mk_response("code_direct", pastebin=True)
        with patch("pob_parser.requests.get",
                   return_value=success) as mock_get:
            result = get_pob_code_from_url("https://pastebin.com/raw/abc")
        assert result == "code_direct"
        assert mock_get.call_count == 1
