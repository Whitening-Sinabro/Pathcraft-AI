# -*- coding: utf-8 -*-
"""POE2 분기 (D6 L1+L2) 단위 테스트.

대상:
- coach_normalizer._load_valid_gems(game="poe2") POE2 JSON 스키마 flatten
- normalize_gem(name, game="poe2") POE2 젬 exact/unmatched
- coach_validator._get_valid_gems(game="poe2") 별도 cache
- validate_coach_output(result, build, game="poe2") POE1 테스트 skip + POE2 젬 hallucination 탐지
- _BY_GAME cache 격리 (POE1/POE2 간 오염 없음)
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest  # noqa: E402

from coach_normalizer import (  # noqa: E402
    _ensure_loaded,
    _reset_caches,
    normalize_gem,
    normalize_gem_list,
)
from coach_validator import (  # noqa: E402
    _get_valid_gems,
    validate_coach_output,
)


@pytest.fixture(autouse=True)
def _clean_caches():
    """각 테스트 간 _BY_GAME 캐시 초기화 — POE1/POE2 간 오염 방지."""
    _reset_caches()
    # validator cache 도 초기화 (module-level dict 비우기)
    from coach_validator import _VALID_GEMS_BY_GAME
    _VALID_GEMS_BY_GAME.clear()
    yield
    _reset_caches()
    _VALID_GEMS_BY_GAME.clear()


class TestNormalizerPoe2Branch:
    """coach_normalizer POE2 분기"""

    def test_poe2_twister_exact_match(self):
        """POE2 'Twister' 는 valid_gems_poe2.json 의 active 카테고리에 존재."""
        canon, match_type = normalize_gem("Twister", game="poe2")
        assert canon == "Twister"
        assert match_type == "exact"

    def test_poe2_rake_exact_match(self):
        """POE2 Spear 스킬 Rake 존재 확인."""
        canon, match_type = normalize_gem("Rake", game="poe2")
        assert canon == "Rake"
        assert match_type == "exact"

    def test_poe2_case_insensitive(self):
        """대소문자 무시 exact 매칭."""
        canon, match_type = normalize_gem("whirling slash", game="poe2")
        assert canon == "Whirling Slash"
        assert match_type == "exact"

    def test_poe1_gem_unmatched_in_poe2(self):
        """POE1 전용 젬 (Cast when Damage Taken Support) 은 POE2 에 없음."""
        canon, match_type = normalize_gem(
            "Cast when Damage Taken Support", game="poe2"
        )
        assert canon is None
        assert match_type == "unmatched"

    def test_poe2_gem_unmatched_in_poe1(self):
        """POE2 전용 젬 (Twister) 은 POE1 valid_gems.json 에 없음."""
        canon, match_type = normalize_gem("Twister", game="poe1")
        assert canon is None
        assert match_type == "unmatched"

    def test_cache_isolation_poe1_poe2(self):
        """POE1 / POE2 cache 독립. 한 쪽 로드가 다른 쪽에 영향 안 줌."""
        # POE2 먼저 로드
        poe2_gems, poe2_lower, poe2_alias = _ensure_loaded("poe2")
        assert "twister" in poe2_lower

        # POE1 로드 후 POE2 가 여전히 존재하는지
        poe1_gems, poe1_lower, _ = _ensure_loaded("poe1")
        assert "twister" not in poe1_lower  # POE1 에는 없음
        assert "twister" in poe2_lower  # POE2 cache 여전히 유지


class TestNormalizerPoe2DropCase:
    """L2 strict allowlist — unmatched 젬 drop 동작 (POE2)"""

    def test_list_drops_invalid_poe2_gem(self):
        """존재하지 않는 POE2 젬은 배열에서 drop, trace 기록."""
        trace: list[dict] = []
        gems_in = ["Twister", "NonExistentGem_XYZ", "Rake"]
        result, warnings = normalize_gem_list(
            gems_in, trace=trace, path="test", game="poe2"
        )
        assert "Twister" in result
        assert "Rake" in result
        assert "NonExistentGem_XYZ" not in result  # drop 됨
        # trace 기록
        dropped = [t for t in trace if t["match_type"] == "dropped"]
        assert len(dropped) == 1
        assert dropped[0]["from"] == "NonExistentGem_XYZ"
        assert dropped[0]["to"] is None


class TestValidatorPoe2Branch:
    """coach_validator POE2 분기"""

    def test_poe2_cache_independent(self):
        """validator _VALID_GEMS_BY_GAME POE1/POE2 독립 cache."""
        g1 = _get_valid_gems("poe1")
        g2 = _get_valid_gems("poe2")
        # POE2 에 Twister 있어야, POE1 에 없어야
        assert "twister" in g2
        assert "twister" not in g1
        # POE1 에 Cyclone 있어야 (기본 POE1 스킬)
        assert "cyclone" in g1
        # Cyclone 은 POE2 에도 없어야 (Warrior skill 아직 미도입 등)
        assert "cyclone" not in g2

    def test_poe2_hallucination_detected(self):
        """POE2 모드에서 존재하지 않는 젬 이름 감지 경고."""
        fake_result = {
            "build_summary": "test",
            "tier": "A",
            "strengths": [], "weaknesses": [],
            "leveling_guide": {}, "leveling_skills": {},
            "build_rating": {}, "gear_progression": [],
            # leveling_skills.recommended.links_progression[*].gems 에서 젬 추출
            "leveling_skills": {
                "recommended": {
                    "links_progression": [
                        {"gems": ["Twister", "InventedGem_ABC"]}
                    ]
                }
            },
        }
        warnings = validate_coach_output(fake_result, None, game="poe2")
        # 'Twister' 는 valid — 경고 없음
        # 'InventedGem_ABC' 는 invalid — 경고 1건
        gem_warnings = [w for w in warnings if "InventedGem_ABC" in w]
        assert len(gem_warnings) == 1
        assert "POE2" in gem_warnings[0]  # 라벨 분기 확인

    def test_poe2_skips_quest_rewards_crosscheck(self):
        """POE2 는 quest_rewards 구조 미확정 → POE1 전용 체크 skip."""
        # skill_transitions 있으면 POE1 에서는 quest cross-check 가동
        # POE2 에서는 skip 되어 관련 경고 없어야 함
        fake_result = {
            "build_summary": "test",
            "tier": "A",
            "strengths": [], "weaknesses": [],
            "leveling_guide": {},
            "leveling_skills": {
                "skill_transitions": [
                    {"level": 12, "change": "Twister으로 전환"}
                ]
            },
            "build_rating": {}, "gear_progression": [],
        }
        build_data = {"meta": {"class": "Huntress"}}
        warnings = validate_coach_output(fake_result, build_data, game="poe2")
        # quest 관련 경고가 없어야 (POE1 만 cross-check)
        quest_warnings = [w for w in warnings if "[퀘스트]" in w]
        assert quest_warnings == []


class TestPoe1RegressionUnchanged:
    """POE1 기본 동작 regression — 기존 테스트가 깨지지 않았는지 spot-check"""

    def test_poe1_default_support_gem_exact(self):
        """POE1 'Chance to Bleed Support' exact 매칭 유지."""
        canon, match_type = normalize_gem(
            "Chance to Bleed Support", game="poe1"
        )
        assert canon == "Chance to Bleed Support"
        assert match_type == "exact"

    def test_poe1_validate_uses_poe1_gems(self):
        """validate_coach_output game 생략 시 POE1 기본값."""
        g = _get_valid_gems()  # game 생략 = poe1
        assert "chance to bleed support" in g
