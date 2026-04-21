# -*- coding: utf-8 -*-
"""Phase H2 — coach_normalizer 단위 테스트.

커버리지:
- normalize_gem: exact(case) / alias / fuzzy / unmatched / 경계(empty/non-str)
- normalize_gem_list: 혼합 입력, 경고 누적
- normalize_change_field: 구분자 보존(' - ' / ', '), 설명 문구 허용
- normalize_coach_output: recommended / options / skill_transitions 인플레이스
"""

import sys
from pathlib import Path

# python/ 경로를 sys.path에 추가 (프로젝트 루트 기준)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from coach_normalizer import (  # noqa: E402
    normalize_gem,
    normalize_gem_list,
    normalize_change_field,
    normalize_coach_output,
)


# ---------- normalize_gem ----------


def test_exact_case_insensitive():
    canon, mt = normalize_gem("cleave")
    assert canon == "Cleave"
    assert mt == "exact"


def test_exact_already_canonical():
    canon, mt = normalize_gem("Multistrike Support")
    assert canon == "Multistrike Support"
    assert mt == "exact"


def test_exact_whitespace_strip():
    canon, mt = normalize_gem("  Ruthless Support  ")
    assert canon == "Ruthless Support"
    assert mt == "exact"


def test_alias_bleed_chance():
    canon, mt = normalize_gem("bleed chance")
    assert canon == "Chance to Bleed Support"
    assert mt == "alias"


def test_alias_cwdt():
    canon, mt = normalize_gem("CWDT")
    assert canon == "Cast when Damage Taken Support"
    assert mt == "alias"


def test_alias_ele_focus():
    canon, mt = normalize_gem("ele focus")
    assert canon == "Elemental Focus Support"
    assert mt == "alias"


def test_alias_melee_phys():
    canon, mt = normalize_gem("Melee Phys")
    assert canon == "Melee Physical Damage Support"
    assert mt == "alias"


def test_alias_added_fire():
    canon, mt = normalize_gem("added fire")
    assert canon == "Added Fire Damage Support"
    assert mt == "alias"


def test_alias_gmp():
    canon, mt = normalize_gem("gmp")
    assert canon == "Greater Multiple Projectiles Support"
    assert mt == "alias"


def test_alias_inc_aoe():
    canon, mt = normalize_gem("inc aoe")
    assert canon == "Increased Area of Effect Support"
    assert mt == "alias"


def test_fuzzy_typo():
    # 'Multistrik' (s 누락) → 'Multistrike Support' 기대
    canon, mt = normalize_gem("Multistrik Support")
    assert canon == "Multistrike Support"
    assert mt == "fuzzy"


def test_unmatched_gibberish():
    canon, mt = normalize_gem("Zorgblax Supreme")
    assert canon is None
    assert mt == "unmatched"


def test_unmatched_empty():
    canon, mt = normalize_gem("")
    assert canon is None
    assert mt == "unmatched"


def test_unmatched_non_string():
    canon, mt = normalize_gem(None)  # type: ignore[arg-type]
    assert canon is None
    assert mt == "unmatched"


# ---------- normalize_gem_list ----------


def test_gem_list_mixed():
    gems = ["Cleave", "bleed chance", "Ruthless Support", "NotAGem"]
    out, warnings = normalize_gem_list(gems)
    assert out[0] == "Cleave"
    assert out[1] == "Chance to Bleed Support"
    assert out[2] == "Ruthless Support"
    assert out[3] == "NotAGem"  # 원본 유지
    assert len(warnings) == 1
    assert "NotAGem" in warnings[0]


def test_gem_list_preserves_non_string():
    gems = ["Cleave", 42, None, "Multistrike Support"]
    out, warnings = normalize_gem_list(gems)  # type: ignore[arg-type]
    assert out[1] == 42
    assert out[2] is None
    assert out[3] == "Multistrike Support"


def test_gem_list_empty():
    out, warnings = normalize_gem_list([])
    assert out == []
    assert warnings == []


# ---------- normalize_change_field ----------


def test_change_field_dash_separator():
    new, warnings = normalize_change_field("Cleave - Bleed Chance - Ruthless")
    assert new == "Cleave - Chance to Bleed Support - Ruthless Support"
    assert warnings == []


def test_change_field_comma_separator():
    new, warnings = normalize_change_field("Cleave, bleed chance, ruthless")
    assert new == "Cleave, Chance to Bleed Support, Ruthless Support"
    assert warnings == []


def test_change_field_single_token():
    # "Multistrike" 는 alias 우선 정책으로 "Multistrike Support" 로 정규화됨
    # (LLM 출력 문맥에서 단축명은 Support 의미)
    new, warnings = normalize_change_field("Multistrike")
    assert new == "Multistrike Support"
    assert warnings == []


def test_change_field_canonical_active_gem():
    # 명시적 active gem 이름 ("Cleave") 은 그대로 유지
    new, warnings = normalize_change_field("Cleave")
    assert new == "Cleave"
    assert warnings == []


def test_change_field_empty():
    new, warnings = normalize_change_field("")
    assert new == ""
    assert warnings == []


def test_change_field_with_unmatched():
    new, warnings = normalize_change_field("Cleave - Zorgblax")
    # Cleave 정규화, Zorgblax 원본 유지 + 경고
    assert "Cleave" in new
    assert "Zorgblax" in new
    assert len(warnings) == 1


def test_change_field_korean_description_no_warning():
    # A3-1 회귀: 한국어 혼합 change 는 설명 텍스트 — 경고 생략
    new, warnings = normalize_change_field("Cleave로 전환")
    assert new == "Cleave로 전환"  # 매칭 실패 시 원본 유지
    assert warnings == []


def test_change_field_mixed_korean_and_gem():
    # 한국어 description이 dash로 분리돼도 ASCII 부분만 경고
    new, warnings = normalize_change_field("Cleave - 업그레이드 - Zorgblax")
    assert "Cleave" in new
    assert "업그레이드" in new
    assert "Zorgblax" in new
    # Zorgblax(ASCII)만 경고, 업그레이드는 생략
    assert len(warnings) == 1
    assert "Zorgblax" in warnings[0]


# ---------- normalize_coach_output ----------


def test_coach_output_recommended():
    result = {
        "leveling_skills": {
            "recommended": {
                "name": "cleave",
                "links_progression": [
                    {"level_range": "Lv 1-12", "gems": ["cleave", "bleed chance", "ruthless"]},
                ],
            },
            "options": [],
            "skill_transitions": [],
        },
    }
    warnings, _ = normalize_coach_output(result)
    assert result["leveling_skills"]["recommended"]["name"] == "Cleave"
    assert result["leveling_skills"]["recommended"]["links_progression"][0]["gems"] == [
        "Cleave",
        "Chance to Bleed Support",
        "Ruthless Support",
    ]
    assert warnings == []


def test_coach_output_options():
    result = {
        "leveling_skills": {
            "recommended": {"name": "Cleave", "links_progression": []},
            "options": [
                {
                    "name": "ground slam",
                    "links_progression": [
                        {"level_range": "Lv 1-12", "gems": ["melee phys", "ruthless"]},
                    ],
                },
            ],
            "skill_transitions": [],
        },
    }
    normalize_coach_output(result)  # trace 내용은 별도 테스트에서 검증
    assert result["leveling_skills"]["options"][0]["name"] == "Ground Slam"
    assert result["leveling_skills"]["options"][0]["links_progression"][0]["gems"] == [
        "Melee Physical Damage Support",
        "Ruthless Support",
    ]


def test_coach_output_skill_transitions():
    result = {
        "leveling_skills": {
            "recommended": {"name": "Cleave", "links_progression": []},
            "options": [],
            "skill_transitions": [
                {"level": 28, "change": "cleave - bleed chance - ruthless", "reason": "x"},
            ],
        },
    }
    normalize_coach_output(result)
    assert result["leveling_skills"]["skill_transitions"][0]["change"] == (
        "Cleave - Chance to Bleed Support - Ruthless Support"
    )


def test_coach_output_missing_leveling_skills():
    result = {"build_summary": "x"}
    warnings, _ = normalize_coach_output(result)
    assert warnings == []
    # 구조 보존
    assert result == {"build_summary": "x"}


def test_coach_output_non_dict():
    warnings, trace = normalize_coach_output([])  # type: ignore[arg-type]
    assert warnings == []
    assert trace == []


def test_coach_output_unmatched_reports_path():
    result = {
        "leveling_skills": {
            "recommended": {
                "name": "Zorgblax",
                "links_progression": [
                    {"level_range": "Lv 1", "gems": ["Zorgblax Minor"]},
                ],
            },
            "options": [],
            "skill_transitions": [],
        },
    }
    warnings, _ = normalize_coach_output(result)
    assert len(warnings) == 2
    # 경로 라벨링 — 어디서 실패했는지 보여야 함
    assert any("recommended.name" in w for w in warnings)
    assert any("links_progression" in w for w in warnings)


# ---------- trace 검증 (A2-1) ----------


def test_trace_captures_alias_correction():
    result = {
        "leveling_skills": {
            "recommended": {
                "name": "Cleave",
                "links_progression": [
                    {"level_range": "Lv 1-12", "gems": ["cleave", "bleed chance"]},
                ],
            },
            "options": [],
            "skill_transitions": [],
        },
    }
    warnings, trace = normalize_coach_output(result)
    assert warnings == []
    # "cleave" → "Cleave" (exact, case 변경), "bleed chance" → "Chance to Bleed Support" (alias)
    assert len(trace) == 2
    by_from = {t["from"]: t for t in trace}
    assert by_from["cleave"]["to"] == "Cleave"
    assert by_from["cleave"]["match_type"] == "exact"
    assert by_from["bleed chance"]["to"] == "Chance to Bleed Support"
    assert by_from["bleed chance"]["match_type"] == "alias"
    # field 경로 검증
    assert "links_progression[0].gems[0]" in by_from["cleave"]["field"]


def test_trace_skips_unchanged():
    result = {
        "leveling_skills": {
            "recommended": {
                "name": "Cleave",
                "links_progression": [
                    {"level_range": "Lv 1", "gems": ["Cleave", "Ruthless Support"]},
                ],
            },
            "options": [],
            "skill_transitions": [],
        },
    }
    _, trace = normalize_coach_output(result)
    # 모두 이미 canonical — trace 비어야 함
    assert trace == []


def test_trace_captures_change_field():
    result = {
        "leveling_skills": {
            "recommended": {"name": "Cleave", "links_progression": []},
            "options": [],
            "skill_transitions": [
                {"level": 28, "change": "cleave - bleed chance", "reason": "x"},
            ],
        },
    }
    _, trace = normalize_coach_output(result)
    assert len(trace) == 2
    assert all("skill_transitions[0].change" in t["field"] for t in trace)
