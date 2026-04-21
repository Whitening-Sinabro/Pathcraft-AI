# -*- coding: utf-8 -*-
"""build_coach `__extra_builds__` 컨텍스트 삽입 회귀 테스트.

Claude API 호출은 mock — 실제 호출 없이 context_parts 구성 검증.
"""

import sys
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def _content_to_text(content) -> str:
    """messages[0]['content']가 이제 list of text blocks (cache_control 포함).
    전체 블록 텍스트 병합 — 테스트가 'in' 검사로 쓸 수 있게."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(
            b.get("text", "") for b in content
            if isinstance(b, dict) and b.get("type") == "text"
        )
    return str(content)


def _mk_build_with_gems(name: str, level: int, gems: dict, uniques: list = None) -> dict:
    return {
        "meta": {"build_name": name, "class_level": level, "class": "Templar"},
        "items": [],
        "progression_stages": [{
            "gem_setups": gems,
            "gear_recommendation": (
                {f"slot_{i}": {"rarity": "Unique", "name": u}
                 for i, u in enumerate(uniques)} if uniques else {}
            ),
        }],
    }


class TestBuildCoachExtras:
    """__extra_builds__ 필드 → context_parts 삽입."""

    def test_no_extras_no_mutation(self):
        """__extra_builds__ 없는 빌드 → 원본 dict 건드리지 않음."""
        import build_coach
        original = _mk_build_with_gems("Primary", 95, {"Cyclone": {"links": "Cyclone"}})
        original_keys = set(original.keys())

        # coach_build는 Claude API 호출 시도 — mock
        with patch.object(build_coach, "anthropic") as mock_anthropic:
            mock_client = MagicMock()
            mock_resp = MagicMock()
            mock_resp.content = [MagicMock(text='{"build_summary": "test"}')]
            mock_client.messages.create.return_value = mock_resp
            mock_anthropic.Anthropic.return_value = mock_client
            try:
                build_coach.coach_build(original)
            except Exception:
                pass  # 다른 에러 무시 — 우리가 볼 건 mutation 여부

        assert set(original.keys()) == original_keys, \
            "coach_build가 원본 build_data를 mutate함 (pop 등)"

    def test_extras_in_prompt(self):
        """__extra_builds__ 있으면 프롬프트에 보조 POB 요약 포함."""
        import build_coach
        primary = _mk_build_with_gems("Endgame", 95, {"Cyclone": {"links": "Cyclone - Melee"}})
        leveling = _mk_build_with_gems("Sunder Leveling", 40,
                                       {"Sunder": {"links": "Sunder - Melee Splash"}})
        primary["__extra_builds__"] = [leveling]

        captured_messages = []

        with patch.object(build_coach, "anthropic") as mock_anthropic:
            mock_client = MagicMock()
            def capture(**kwargs):
                captured_messages.append(kwargs.get("messages", []))
                r = MagicMock()
                r.content = [MagicMock(text='{"build_summary": "test"}')]
                r.stop_reason = "end_turn"
                return r
            mock_client.messages.create.side_effect = capture
            def stream_capture(**kwargs):
                captured_messages.append(kwargs.get("messages", []))
                cm = MagicMock()
                cm.__enter__ = MagicMock(return_value=cm)
                cm.__exit__ = MagicMock(return_value=False)
                cm.text_stream = iter(['{"build_summary": "test"}'])
                final = MagicMock()
                final.content = [MagicMock(text='{"build_summary": "test"}')]
                final.stop_reason = "end_turn"
                cm.get_final_message = MagicMock(return_value=final)
                return cm
            mock_client.messages.stream.side_effect = stream_capture
            mock_anthropic.Anthropic.return_value = mock_client

            try:
                build_coach.coach_build(primary)
            except Exception:
                pass

        assert captured_messages, "Claude API 호출 메시지 없음"
        user_msg = _content_to_text(captured_messages[0][0]["content"])
        # 보조 POB 정보가 프롬프트에 포함돼야 함
        assert "Sunder" in user_msg, "보조 POB Sunder 스킬이 프롬프트에 없음"
        assert "2단계 POB" in user_msg or "progression" in user_msg.lower(), \
            "progression 컨텍스트 지시가 없음"

    def test_alternate_gem_sets_in_prompt(self):
        """progression_stages[0].alternate_gem_sets도 프롬프트에 포함."""
        import build_coach
        primary = _mk_build_with_gems("Endgame", 95, {"Cyclone": {"links": "Cyclone"}})
        primary["progression_stages"][0]["alternate_gem_sets"] = {
            "Leveling Set": {
                "Sunder": {"links": "Sunder - Melee Splash - Added Fire"}
            }
        }

        captured_messages = []
        with patch.object(build_coach, "anthropic") as mock_anthropic:
            mock_client = MagicMock()
            def capture(**kwargs):
                captured_messages.append(kwargs.get("messages", []))
                r = MagicMock()
                r.content = [MagicMock(text='{"build_summary": "test"}')]
                r.stop_reason = "end_turn"
                return r
            # 동기 create 모킹
            mock_client.messages.create.side_effect = capture
            # 스트리밍 stream() 모킹 — context manager + text_stream + get_final_message
            def stream_capture(**kwargs):
                captured_messages.append(kwargs.get("messages", []))
                cm = MagicMock()
                cm.__enter__ = MagicMock(return_value=cm)
                cm.__exit__ = MagicMock(return_value=False)
                cm.text_stream = iter(['{"build_summary": "test"}'])
                final = MagicMock()
                final.content = [MagicMock(text='{"build_summary": "test"}')]
                final.stop_reason = "end_turn"
                cm.get_final_message = MagicMock(return_value=final)
                return cm
            mock_client.messages.stream.side_effect = stream_capture
            mock_anthropic.Anthropic.return_value = mock_client
            try:
                build_coach.coach_build(primary)
            except Exception:
                pass

        assert captured_messages
        user_msg = _content_to_text(captured_messages[0][0]["content"])
        assert "Leveling Set" in user_msg or "Sunder" in user_msg, \
            "alternate_gem_sets이 프롬프트에 전달되지 않음"
