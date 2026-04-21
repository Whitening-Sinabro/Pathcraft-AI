# -*- coding: utf-8 -*-
"""coach_validator 젬 hallucination 탐지 회귀 테스트.

검증 범위:
- POE2 젬 차단 (Fire Wall 등 학습 데이터 오염 대표)
- 가짜 젬 이름 탐지
- False-positive 억제 (stopword / 한글 / 괄호 변형)
- valid_gems.json 부재 시 섹션 skip (무해 동작)
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import coach_validator
from coach_validator import validate_coach_output, _extract_gem_strings


def _base_result() -> dict:
    """필수 필드 채운 최소 coach 결과 — 이번 테스트에서 필요한 part만 의미 있음."""
    return {
        "build_summary": "Test",
        "tier": "A",
        "strengths": ["fast"],
        "weaknesses": ["squishy"],
        "leveling_guide": {},
        "leveling_skills": {},
        "build_rating": {"newbie_friendly": 3},
        "gear_progression": [],
    }


class TestGemValidation:
    def test_valid_gems_pass(self):
        """valid_gems.json 에 있는 젬은 경고 없음."""
        r = _base_result()
        r["leveling_skills"] = {
            "recommended": {
                "links_progression": [
                    {"level_range": "1-8", "gems": ["Firestorm", "Controlled Destruction Support"]},
                ]
            }
        }
        warnings = validate_coach_output(r)
        gem_warnings = [w for w in warnings if w.startswith("[젬]")]
        assert gem_warnings == [], f"예상: 0 젬 경고, 실제: {gem_warnings}"

    def test_poe2_gem_detected(self):
        """POE2 젬 'Fire Wall'은 POE1 valid_gems.json 에 없으므로 탐지돼야 함."""
        r = _base_result()
        r["leveling_skills"] = {
            "recommended": {"links_progression": [{"gems": ["Fire Wall"]}]}
        }
        warnings = validate_coach_output(r)
        assert any("Fire Wall" in w and "젬" in w for w in warnings)

    def test_fake_gem_detected(self):
        """없는 support 젬도 탐지."""
        r = _base_result()
        r["leveling_skills"] = {
            "recommended": {"links_progression": [{"gems": ["Nonexistent Zap Support"]}]}
        }
        warnings = validate_coach_output(r)
        assert any("Nonexistent Zap Support" in w for w in warnings)

    def test_main_skill_string_parsed(self):
        """variant_snapshots.main_skill 의 ' - ' 구분 문자열에서도 젬 추출."""
        r = _base_result()
        r["variant_snapshots"] = [
            {"main_skill": "Firestorm - Spell Echo Support - Fake Damage Support"}
        ]
        warnings = validate_coach_output(r)
        # Fake Damage Support 는 탐지, Firestorm/Spell Echo Support 는 통과
        assert any("Fake Damage Support" in w for w in warnings)
        assert not any("Firestorm" in w and "valid_gems" in w for w in warnings)

    def test_stopwords_ignored(self):
        """메인스킬/서포트1 등 플레이스홀더는 false-positive 억제."""
        r = _base_result()
        r["leveling_skills"] = {
            "recommended": {"links_progression": [{"gems": ["메인스킬", "서포트1", "4-link"]}]}
        }
        warnings = validate_coach_output(r)
        gem_warnings = [w for w in warnings if w.startswith("[젬]")]
        assert gem_warnings == [], f"플레이스홀더가 오탐: {gem_warnings}"

    def test_paren_variants_allowed(self):
        """'Firestorm (4L)' 같은 주석 붙은 이름은 괄호 앞만 재검사 → 통과."""
        r = _base_result()
        r["leveling_skills"] = {
            "recommended": {"links_progression": [{"gems": ["Firestorm (4L)"]}]}
        }
        warnings = validate_coach_output(r)
        gem_warnings = [w for w in warnings if w.startswith("[젬]") and "Firestorm" in w]
        assert gem_warnings == [], f"괄호 변형이 오탐: {gem_warnings}"


class TestExtractGemStrings:
    def test_extracts_from_gems_array(self):
        obj = {"gems": ["A", "B"], "other": "ignore"}
        out: list[str] = []
        _extract_gem_strings(obj, out)
        assert "A" in out and "B" in out
        assert "ignore" not in out

    def test_splits_main_skill(self):
        obj = {"main_skill": "Firestorm - Spell Echo Support"}
        out: list[str] = []
        _extract_gem_strings(obj, out)
        assert "Firestorm" in out
        assert "Spell Echo Support" in out

    def test_recursive_dict_list(self):
        obj = {"a": {"b": [{"gems": ["Nested"]}]}}
        out: list[str] = []
        _extract_gem_strings(obj, out)
        assert "Nested" in out
