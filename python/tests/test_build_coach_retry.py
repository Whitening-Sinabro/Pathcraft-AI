"""Phase H6 L3 — Gate + Auto-retry 단위 테스트.

검증 포인트:
1. 1차 응답에 drop 없음 → 재시도 없음, _retry_info 없음
2. 1차 응답에 drop 있고 재시도 응답 clean → _retry_info.attempts=2, final_dropped=[]
3. 1차/재시도 모두 drop → _retry_info 기록, final_dropped 남음 (L4 차단 조건)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def _mk_build() -> dict:
    return {
        "meta": {"build_name": "Test", "class_level": 90, "class": "Marauder"},
        "stats": {"dps": 1, "life": 1, "energy_shield": 0},
        "gem_setups": {"Cleave": {"links": "Cleave - Multistrike"}},
        "passives": {},
        "equipment": {},
    }


def _mk_result_gem(gem: str) -> str:
    """Mock Claude 응답 — leveling_skills.recommended.links_progression[0].gems[0] 에 특정 젬."""
    result = {
        "build_summary": "test",
        "tier": "A",
        "strengths": [], "weaknesses": [],
        "leveling_guide": {"act1_4": "", "act5_10": "", "early_maps": "", "endgame": ""},
        "leveling_skills": {
            "damage_type": "physical",
            "recommended": {
                "name": "Cleave",
                "links_progression": [{"level_range": "1-10", "gems": [gem]}],
                "reason": "test",
                "transition_level": "",
            },
            "options": [],
            "skill_transitions": [],
        },
        "key_items": [],
        "aura_utility_progression": [],
        "build_rating": {
            "newbie_friendly": 0, "gearing_difficulty": 0, "play_difficulty": 0,
            "league_start_viable": 0, "hcssf_viability": 0,
        },
        "gear_progression": [],
        "map_mod_warnings": {"deadly": [], "dangerous": [], "caution": [], "regex_filter": ""},
        "variant_snapshots": [],
        "passive_priority": [],
        "danger_zones": [],
        "farming_strategy": "",
    }
    return json.dumps(result)


def _make_mock_anthropic(responses: list[str]):
    """순차적으로 responses[0], responses[1], ... 리턴하는 mock.

    streaming + non-streaming 양쪽 경로 커버. call_count 공유로 순서 보장.
    """
    call_idx = {"i": 0}

    def capture_create(**_kwargs):
        idx = call_idx["i"]
        call_idx["i"] += 1
        r = MagicMock()
        r.content = [MagicMock(text=responses[min(idx, len(responses) - 1)])]
        r.stop_reason = "end_turn"
        usage = MagicMock()
        usage.input_tokens = 1
        usage.output_tokens = 1
        usage.cache_read_input_tokens = 0
        usage.cache_creation_input_tokens = 0
        r.usage = usage
        return r

    def capture_stream(**_kwargs):
        idx = call_idx["i"]
        call_idx["i"] += 1
        cm = MagicMock()
        cm.__enter__ = MagicMock(return_value=cm)
        cm.__exit__ = MagicMock(return_value=False)
        text = responses[min(idx, len(responses) - 1)]
        cm.text_stream = iter([text])
        final = MagicMock()
        final.content = [MagicMock(text=text)]
        final.stop_reason = "end_turn"
        usage = MagicMock()
        usage.input_tokens = 1
        usage.output_tokens = 1
        usage.cache_read_input_tokens = 0
        usage.cache_creation_input_tokens = 0
        final.usage = usage
        cm.get_final_message = MagicMock(return_value=final)
        return cm

    mock_anthropic = MagicMock()
    mock_client = MagicMock()
    mock_client.messages.create.side_effect = capture_create
    mock_client.messages.stream.side_effect = capture_stream
    mock_anthropic.Anthropic.return_value = mock_client
    return mock_anthropic, call_idx


class TestL3Retry:
    def test_clean_first_call_no_retry(self):
        """유효 젬만 반환 → 재시도 없음, _retry_info 없음."""
        import build_coach
        responses = [_mk_result_gem("Multistrike Support")]
        mock, idx = _make_mock_anthropic(responses)
        with patch.object(build_coach, "anthropic", mock):
            result = build_coach.coach_build(_mk_build())
        # 재시도 없음 — API call 1회만
        assert idx["i"] == 1
        assert "_retry_info" not in result

    def test_retry_recovers(self):
        """1차: Onslaught Support drop → 2차: 유효 젬 → _retry_info.final_dropped=[]."""
        import build_coach
        responses = [
            _mk_result_gem("Onslaught Support"),     # 1차 drop
            _mk_result_gem("Multistrike Support"),   # 2차 clean
        ]
        mock, idx = _make_mock_anthropic(responses)
        with patch.object(build_coach, "anthropic", mock):
            result = build_coach.coach_build(_mk_build())
        assert idx["i"] == 2, "재시도 1회 발생해야 함"
        assert "_retry_info" in result
        info = result["_retry_info"]
        assert info["attempts"] == 2
        assert "Onslaught Support" in info["recovered_from"]
        assert info["final_dropped"] == []

    def test_retry_still_drops(self):
        """양쪽 응답 모두 drop → _retry_info 기록, final_dropped 남음 (L4 차단 조건)."""
        import build_coach
        responses = [
            _mk_result_gem("Onslaught Support"),    # 1차 drop
            _mk_result_gem("FakeGem Support"),      # 2차도 drop
        ]
        mock, idx = _make_mock_anthropic(responses)
        with patch.object(build_coach, "anthropic", mock):
            result = build_coach.coach_build(_mk_build())
        assert idx["i"] == 2
        info = result["_retry_info"]
        assert info["attempts"] == 2
        assert "Onslaught Support" in info["recovered_from"]
        assert info["final_dropped"]  # 비어있지 않음
        # trace 에 dropped 엔트리 있어서 L4 차단될 조건
        trace = result.get("_normalization_trace", [])
        assert any(t.get("match_type") == "dropped" for t in trace)

    def test_retry_metric_log_emitted_success(self, caplog):
        """L3_RETRY_METRIC 로그 — 복구 성공 시 success=true."""
        import build_coach
        import logging
        responses = [
            _mk_result_gem("Onslaught Support"),
            _mk_result_gem("Multistrike Support"),
        ]
        mock, _ = _make_mock_anthropic(responses)
        with caplog.at_level(logging.INFO, logger="build_coach"):
            with patch.object(build_coach, "anthropic", mock):
                build_coach.coach_build(_mk_build())
        metric_lines = [r.message for r in caplog.records if "L3_RETRY_METRIC" in r.message]
        assert len(metric_lines) == 1
        assert "success=true" in metric_lines[0]
        assert "attempts=2" in metric_lines[0]
        assert "final_dropped=0" in metric_lines[0]

    def test_retry_metric_log_emitted_failure(self, caplog):
        """L3_RETRY_METRIC 로그 — 복구 실패 시 success=false."""
        import build_coach
        import logging
        responses = [
            _mk_result_gem("Onslaught Support"),
            _mk_result_gem("FakeGem Support"),
        ]
        mock, _ = _make_mock_anthropic(responses)
        with caplog.at_level(logging.INFO, logger="build_coach"):
            with patch.object(build_coach, "anthropic", mock):
                build_coach.coach_build(_mk_build())
        metric_lines = [r.message for r in caplog.records if "L3_RETRY_METRIC" in r.message]
        assert len(metric_lines) == 1
        assert "success=false" in metric_lines[0]
