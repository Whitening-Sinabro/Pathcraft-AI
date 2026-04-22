# -*- coding: utf-8 -*-
"""Phase H4 — SYSTEM_PROMPT 제약 존재 여부 스모크 테스트.

실 LLM 호출은 하지 않음. 프롬프트 문자열에 H4 제약이 포함됐는지 회귀 방지 목적.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# POE1 prompt 대상 (POE2 는 별도 SYSTEM_PROMPT_POE2 로 분기됨)
from build_coach import SYSTEM_PROMPT_POE1 as SYSTEM_PROMPT  # noqa: E402


def test_prompt_has_canonical_name_constraint():
    # 정식명 전용 제약 문구
    assert "정식명 전용" in SYSTEM_PROMPT
    # 구체적 예시 (약칭 ✗ → 정식 ✓)
    assert "Chance to Bleed Support" in SYSTEM_PROMPT
    assert "Headhunter" in SYSTEM_PROMPT
    assert "Tabula Rasa" in SYSTEM_PROMPT


def test_prompt_has_speculative_unique_ban():
    assert "추측성 유니크 금지" in SYSTEM_PROMPT


def test_prompt_has_normalizer_awareness():
    # 출력이 normalizer에 의해 검증된다는 사실을 프롬프트가 알림
    assert "coach_normalizer" in SYSTEM_PROMPT or "정규화" in SYSTEM_PROMPT
    assert "자동 교정" in SYSTEM_PROMPT


def test_prompt_has_canonical_slot_list():
    # gear_progression slot 정식명 명시
    for slot in ["Body Armour", "Helmet", "Gloves", "Boots", "Weapon", "Belt", "Ring", "Amulet"]:
        assert slot in SYSTEM_PROMPT, f"슬롯 정식명 '{slot}' 누락"


def test_prompt_still_has_poe1_guard():
    # 기존 POE1 전용 제약 유지 (회귀 방지)
    assert "POE1" in SYSTEM_PROMPT
    assert "POE2" in SYSTEM_PROMPT


def test_prompt_still_has_support_whitelist():
    # 기존 support 젬 화이트리스트 제약 유지
    assert "Support 젬 화이트리스트" in SYSTEM_PROMPT
