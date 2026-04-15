# -*- coding: utf-8 -*-
"""syndicate_vision 단위 테스트 — Claude API mock으로 정규화/파싱 검증."""

import base64
import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from syndicate_vision import (
    _detect_media_type,
    _load_member_catalog,
    _normalize_response,
    analyze_image,
)


PNG_HEADER = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
JPEG_HEADER = b"\xff\xd8\xff\xe0" + b"\x00" * 100
WEBP_HEADER = b"RIFF" + b"\x00" * 4 + b"WEBP" + b"\x00" * 100


class TestDetectMediaType:
    def test_png(self):
        assert _detect_media_type(PNG_HEADER) == "image/png"

    def test_jpeg(self):
        assert _detect_media_type(JPEG_HEADER) == "image/jpeg"

    def test_webp(self):
        assert _detect_media_type(WEBP_HEADER) == "image/webp"

    def test_unsupported_raises(self):
        with pytest.raises(ValueError, match="Unsupported"):
            _detect_media_type(b"BMxxxxxx")


class TestLoadMemberCatalog:
    def test_excludes_catarina(self):
        catalog = _load_member_catalog()
        ids = {m["id"] for m in catalog}
        assert "catarina" not in ids
        assert "aisling" in ids
        assert len(catalog) == 17  # 18 total - 1 Mastermind

    def test_required_fields(self):
        catalog = _load_member_catalog()
        for m in catalog:
            assert m["id"] and m["name_en"] and m["default_division"]


class TestNormalizeResponse:
    @pytest.fixture
    def catalog(self):
        return _load_member_catalog()

    def test_valid_response(self, catalog):
        parsed = {
            "divisions": {
                "Research": [
                    {"member_id": "aisling", "rank": "Leader"},
                    {"member_id": "vorici", "rank": "Member"},
                ],
                "Intervention": [{"member_id": "cameria", "rank": "Leader"}],
            },
            "confidence": "high",
            "notes": "",
        }
        result = _normalize_response(parsed, catalog)
        assert result["divisions"]["Research"][0] == {"member_id": "aisling", "rank": "Leader"}
        assert result["divisions"]["Research"][1] == {"member_id": "vorici", "rank": "Member"}
        assert result["divisions"]["Intervention"][0]["member_id"] == "cameria"
        assert result["divisions"]["Transportation"] == []
        assert result["confidence"] == "high"
        assert result["diagnostics"]["unknown_members"] == []

    def test_unknown_member_dropped_and_logged(self, catalog):
        parsed = {
            "divisions": {
                "Research": [
                    {"member_id": "aisling", "rank": "Leader"},
                    {"member_id": "ghost_member_xyz", "rank": "Member"},
                ]
            }
        }
        result = _normalize_response(parsed, catalog)
        assert len(result["divisions"]["Research"]) == 1
        assert result["divisions"]["Research"][0]["member_id"] == "aisling"
        assert result["diagnostics"]["unknown_members"] == [
            {"div": "Research", "raw": "ghost_member_xyz"}
        ]

    def test_english_name_fallback(self, catalog):
        """Claude이 id 대신 영문 이름 반환 시 자동 매핑."""
        parsed = {
            "divisions": {
                "Research": [{"member_id": "Aisling Laffrey", "rank": "Leader"}]
            }
        }
        result = _normalize_response(parsed, catalog)
        assert result["divisions"]["Research"][0]["member_id"] == "aisling"

    def test_invalid_rank_defaults_to_member(self, catalog):
        parsed = {
            "divisions": {
                "Fortification": [{"member_id": "elreon", "rank": "Mastermind"}]
            }
        }
        result = _normalize_response(parsed, catalog)
        assert result["divisions"]["Fortification"][0]["rank"] == "Member"
        assert result["diagnostics"]["invalid_ranks"][0]["raw"] == "Mastermind"

    def test_invalid_division_ignored(self, catalog):
        parsed = {"divisions": {"Mastermind": [{"member_id": "aisling", "rank": "Leader"}]}}
        result = _normalize_response(parsed, catalog)
        # Mastermind은 4 분과 화이트리스트 밖 → 모두 빈 배열
        for div in ("Transportation", "Fortification", "Research", "Intervention"):
            assert result["divisions"][div] == []

    def test_empty_response(self, catalog):
        result = _normalize_response({}, catalog)
        for div in ("Transportation", "Fortification", "Research", "Intervention"):
            assert result["divisions"][div] == []
        assert result["confidence"] == "medium"  # default

    def test_malformed_slot_skipped(self, catalog):
        parsed = {
            "divisions": {
                "Research": [
                    "not a dict",  # invalid
                    {"member_id": "aisling", "rank": "Leader"},
                    None,  # invalid
                ]
            }
        }
        result = _normalize_response(parsed, catalog)
        assert len(result["divisions"]["Research"]) == 1
        assert result["divisions"]["Research"][0]["member_id"] == "aisling"


class TestAnalyzeImage:
    """Claude API mock으로 통합 흐름 검증."""

    def _mock_response(self, text: str):
        msg = MagicMock()
        msg.content = [MagicMock(type="text", text=text)]
        msg.usage = MagicMock(
            input_tokens=100,
            output_tokens=50,
            cache_creation_input_tokens=0,
            cache_read_input_tokens=0,
        )
        msg.stop_reason = "end_turn"
        return msg

    @patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"})
    @patch("anthropic.Anthropic")
    def test_clean_json_response(self, mock_client_class):
        client = MagicMock()
        client.messages.create.return_value = self._mock_response(
            '{"divisions": {"Research": [{"member_id": "aisling", "rank": "Leader"}]}, '
            '"confidence": "high", "notes": ""}'
        )
        mock_client_class.return_value = client

        result = analyze_image(PNG_HEADER)
        assert result["divisions"]["Research"][0]["member_id"] == "aisling"
        assert result["confidence"] == "high"

    @patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"})
    @patch("anthropic.Anthropic")
    def test_markdown_fence_stripped(self, mock_client_class):
        """Claude이 ```json fence로 감싸도 정상 파싱."""
        client = MagicMock()
        client.messages.create.return_value = self._mock_response(
            '```json\n{"divisions": {"Research": [{"member_id": "vorici", "rank": "Member"}]}}\n```'
        )
        mock_client_class.return_value = client

        result = analyze_image(PNG_HEADER)
        assert result["divisions"]["Research"][0]["member_id"] == "vorici"

    @patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"})
    @patch("anthropic.Anthropic")
    def test_invalid_json_raises(self, mock_client_class):
        client = MagicMock()
        client.messages.create.return_value = self._mock_response("not json at all")
        mock_client_class.return_value = client

        with pytest.raises(RuntimeError, match="JSON 파싱 실패"):
            analyze_image(PNG_HEADER)

    @patch.dict("os.environ", {}, clear=True)
    @patch("dotenv.load_dotenv", return_value=False)
    def test_missing_api_key_raises(self, _mock_dotenv):
        with pytest.raises(RuntimeError, match="ANTHROPIC_API_KEY"):
            analyze_image(PNG_HEADER)

    @patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"})
    def test_unsupported_format_raises(self):
        with pytest.raises(ValueError, match="Unsupported"):
            analyze_image(b"BMxxxxxx")

    @patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"})
    @patch("anthropic.Anthropic")
    def test_uses_opus_4_6_with_caching(self, mock_client_class):
        client = MagicMock()
        client.messages.create.return_value = self._mock_response('{"divisions": {}}')
        mock_client_class.return_value = client

        analyze_image(PNG_HEADER)

        call = client.messages.create.call_args
        assert call.kwargs["model"] == "claude-opus-4-6"
        # System prompt에 cache_control 적용
        assert call.kwargs["system"][0]["cache_control"] == {"type": "ephemeral"}
