"""POE2 전용 coach normalizer 경로 — skill_setup.{main_skill, support_gems} 검증.

배경: POE1 normalizer 는 leveling_skills 계열만 봄. POE2 SYSTEM_PROMPT 응답은
skill_setup 중심이라 POE1 경로로는 L2 방어층이 실효 0. 별도 _normalize_coach_output_poe2
가 POE2 스키마를 커버.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "python"))

import coach_normalizer  # noqa: E402


def _reset():
    coach_normalizer._reset_caches()


def test_main_skill_exact_match():
    _reset()
    r = {"skill_setup": {"main_skill": "Twister", "support_gems": []}}
    warnings, trace = coach_normalizer.normalize_coach_output(r, game="poe2")
    # Twister 는 POE2 Spear 스킬 — exact 매치여야 trace 안 남음 or 'exact' 라벨
    assert r["skill_setup"]["main_skill"] == "Twister"
    dropped = [t for t in trace if t.get("match_type") == "dropped"]
    assert not dropped, f"Twister 가 drop 되면 valid_gems_poe2 문제: {trace}"


def test_main_skill_hallucination_dropped():
    """POE1 젬 이름을 main_skill 에 넣으면 drop trace 기록."""
    _reset()
    r = {"skill_setup": {"main_skill": "Cyclone", "support_gems": []}}
    warnings, trace = coach_normalizer.normalize_coach_output(r, game="poe2")
    dropped = [t for t in trace if t.get("match_type") == "dropped"]
    # Cyclone 은 POE1 스킬, POE2 valid_gems 에 없음 → drop
    assert any(t["from"] == "Cyclone" and t["field"] == "skill_setup.main_skill" for t in dropped), (
        f"POE1 hallucination drop 실패: {trace}"
    )


def test_support_gems_progression_string_split():
    """'Bleed I → II → III → IV (progression)' 같은 결합 문자열을 토큰 단위 split + 각각 검증."""
    _reset()
    r = {"skill_setup": {
        "main_skill": "Twister",
        "support_gems": [
            "Bleed I → II → III → IV (progression)",
            "Cold Penetration (cold 확장)",
            "Rapid Attacks I → II → III",
        ],
    }}
    warnings, trace = coach_normalizer.normalize_coach_output(r, game="poe2")
    dropped = [t for t in trace if t.get("match_type") == "dropped"]
    # 전부 POE1 이름 → 최소 3건 drop 기록 (각 첫 토큰만이라도)
    assert len(dropped) >= 3, f"split 후 dropped 가 기대 미만: {trace}"
    # 원본 list 는 최종적으로 비거나 유효 젬만 남음 (Cold Penetration/Rapid Attacks 는 POE2 에 없다고 가정)
    kept = r["skill_setup"]["support_gems"]
    # 각 kept 항목은 POE2 valid_gems 안의 canonical 이름
    valid = set(coach_normalizer._ensure_loaded("poe2")[0])
    for k in kept:
        assert k in valid, f"kept gem '{k}' 가 valid_gems_poe2 에 없음"


def test_support_gems_deduplication():
    """같은 젬이 여러 항목에서 등장해도 최종 리스트는 unique."""
    _reset()
    # POE2 에 실제 존재하는 support 2개 — Chance to Bleed Support / Martial Tempo Support
    # 쉼표 split + 중복 제거 확인
    r = {"skill_setup": {
        "main_skill": "Twister",
        "support_gems": [
            "Chance to Bleed Support",
            "Chance to Bleed Support, Martial Tempo Support",
        ],
    }}
    warnings, trace = coach_normalizer.normalize_coach_output(r, game="poe2")
    kept = r["skill_setup"]["support_gems"]
    assert len(kept) == len(set(kept)), f"중복 미제거: {kept}"


def test_missing_skill_setup_no_crash():
    _reset()
    r = {"build_summary": "no skill_setup"}
    warnings, trace = coach_normalizer.normalize_coach_output(r, game="poe2")
    assert warnings == []
    assert trace == []


def test_poe1_path_untouched_for_poe2_skillsetup_fields():
    """POE1 경로는 skill_setup 을 무시해야 (기존 동작 유지)."""
    _reset()
    r = {"skill_setup": {"main_skill": "Cyclone", "support_gems": ["Multistrike"]}}
    warnings, trace = coach_normalizer.normalize_coach_output(r, game="poe1")
    # POE1 는 leveling_skills 만 보므로 skill_setup 대상 trace 없음
    assert all("skill_setup" not in t.get("field", "") for t in trace)
