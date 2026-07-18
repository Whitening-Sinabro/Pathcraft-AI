# -*- coding: utf-8 -*-
"""pob_parser.get_pob_code_from_url 타임아웃 재시도 로직 회귀 테스트.

검증:
- Timeout 1회 + 성공 1회 → 성공 (재시도 성공)
- Timeout 2회 → None (재시도 후 포기)
- 비-Timeout 예외(ConnectionError) → 재시도 없이 즉시 None
- 정상 1회 → 성공 (재시도 안 함)
- poe.ninja raw 엔드포인트 → 텍스트 직접 반환
- Maxroll 프로필 API → JSON 내부 pobCode 추출
- ProxyError → 프록시 비활성 세션으로 재시도
"""

import sys
import os
from unittest.mock import patch, MagicMock

import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pob_parser import get_pob_code_from_url


def _mk_response(text: str = "", *, pastebin: bool = False, json_payload=None) -> MagicMock:
    """raw 경로면 text, HTML 경로면 textarea, JSON 경로면 json() 목업을 제공한다."""
    r = MagicMock()
    r.raise_for_status = MagicMock()
    r.text = text
    r.content = f'<html><body><textarea>{text}</textarea></body></html>'.encode()
    if json_payload is not None:
        r.json = MagicMock(return_value=json_payload)
    else:
        r.json = MagicMock(return_value={})
    if pastebin:
        r.text = text
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

    def test_proxy_error_falls_back_to_direct_session(self):
        """시스템 프록시가 깨져 있으면 trust_env=False 세션으로 재시도한다."""
        success = _mk_response("code_after_proxy_fallback", pastebin=True)
        session = MagicMock()
        session.get.return_value = success

        with patch("pob_parser.requests.get", side_effect=requests.exceptions.ProxyError("proxy")) as mock_get:
            with patch("pob_parser.requests.Session", return_value=session) as mock_session:
                result = get_pob_code_from_url("https://pastebin.com/raw/abc")

        assert result == "code_after_proxy_fallback"
        assert mock_get.call_count == 1
        assert mock_session.call_count == 1
        session.get.assert_called_once()
        assert session.trust_env is False

    def test_poe_ninja_raw_endpoint_returns_text_directly(self):
        """poe.ninja raw 엔드포인트는 텍스트를 직접 반환한다."""
        success = _mk_response("code_from_poe_ninja", pastebin=True)
        with patch("pob_parser.requests.get", return_value=success) as mock_get:
            result = get_pob_code_from_url("https://poe.ninja/poe1/pob/raw/8c8b9")
        assert result == "code_from_poe_ninja"
        assert mock_get.call_count == 1

    def test_maxroll_profile_api_returns_embedded_pob_code(self):
        """Maxroll 프로필 API는 JSON 내부의 pobCode를 추출한다."""
        success = _mk_response(
            json_payload={
                "id": "lz4pi0lj",
                "data": '{"pobCode":"code_from_maxroll"}'
            }
        )
        with patch("pob_parser.requests.get", return_value=success) as mock_get:
            result = get_pob_code_from_url("https://planners.maxroll.gg/profiles/load/poe/lz4pi0lj")
        assert result == "code_from_maxroll"
        assert mock_get.call_count == 1
