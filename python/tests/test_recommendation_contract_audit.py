# -*- coding: utf-8 -*-
"""Regression checks for recommendation contract audit."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from recommendation_contract_audit import (  # noqa: E402
    audit_build_profile,
    audit_user_state,
    build_recommendation_audit,
    evaluate_compatibility,
)


def test_example_contract_builds_plan_a():
    audit = build_recommendation_audit()

    assert audit["dataset_kind"] == "poe1_recommendation_contract_audit"
    assert audit["profile_audit"]["issues"] == []
    assert audit["user_state_audit"]["issues"] == []
    assert audit["compatibility"]["selected_plan"] == "A"
    assert audit["compatibility"]["ai_policy"]["mode"] == "explain_only"
    assert audit["compatibility"]["verification_loop"]["loop_state"] == "satisfied"
    assert audit["compatibility"]["response_layers"]["user_message"]["template_id"] == "plan_a_exact"
    assert audit["compatibility"]["guardrails"]["ai_policy"]["mode"] == "explain_only"
    assert any(entry["guard"] == "patch_guard" for entry in audit["compatibility"]["deterministic_guards"])


def test_confirmed_profile_requires_multiple_source_types():
    profile = {
        "playstyle": {"input_style": "1_click", "manual_buttons": 1},
        "availability": {"league_start_viable": True, "ssf_viable": "medium", "mandatory_uniques": []},
        "budget_curve": {"entry_cost_divines": 0.5},
        "progression": {"leveling_confidence": "near_confirmed", "transition_points": [{"stage": "x"}]},
        "confidence": {"representative_build_status": "confirmed", "source_count": 1},
        "evidence": [{"type": "maxroll", "label": "Only source"}],
    }

    result = audit_build_profile(profile)

    assert any("distinct evidence source types" in item for item in result["issues"])


def test_user_state_detects_skill_contradiction():
    user_state = {
        "character_state": {"level": 90, "character_locked": True},
        "currency_state": {"liquid_divines": 1, "liquid_chaos": 10},
        "preferences": {"max_input_style": "1_click"},
        "constraints": {
            "must_use_skill": "Lightning Arrow",
            "forbidden_skills": ["Lightning Arrow"],
        },
    }

    result = audit_user_state(user_state)

    assert any("must_use_skill conflicts" in item for item in result["issues"])


def test_character_lock_conflict_forces_plan_d():
    profile = {
        "identity": {
            "main_skill": "Lightning Arrow",
            "patch": "3.25",
            "class_name": "Ranger",
            "ascendancy": "Deadeye",
        },
        "playstyle": {"input_style": "1_click"},
        "budget_curve": {"entry_cost_divines": 1},
        "availability": {"ssf_viable": "medium"},
        "progression": {"leveling_confidence": "confirmed"},
        "confidence": {"representative_build_status": "confirmed", "source_count": 2},
        "evidence": [{"type": "maxroll"}, {"type": "poe_vault"}],
        "suitability": {"mapping": 90},
    }
    user_state = {
        "character_state": {
            "patch": "3.25",
            "class_name": "Templar",
            "ascendancy": "Hierophant",
            "character_locked": True,
        },
        "currency_state": {"liquid_divines": 10},
        "preferences": {
            "desired_main_skill": "Lightning Arrow",
            "max_input_style": "1_click",
            "target_contents": ["mapping"],
            "trade_mode": "trade_league_start",
        },
        "constraints": {},
    }

    result = evaluate_compatibility(profile, user_state)

    assert result["selected_plan"] == "D"
    assert "character_lock_conflict" in result["hard_blocks"]
    assert result["ai_policy"]["mode"] == "disabled"
    assert result["verification_loop"]["loop_state"] == "abstain"
    assert result["response_layers"]["user_message"]["template_id"] == "plan_d_character_lock"
    assert any(
        entry["guard"] == "character_guard" and entry["status"] == "block"
        for entry in result["deterministic_guards"]
    )


def test_skill_mismatch_without_character_lock_degrades_to_plan_c():
    profile = {
        "identity": {
            "main_skill": "Boneshatter",
            "patch": "3.25",
            "class_name": "Marauder",
            "ascendancy": "Juggernaut",
        },
        "playstyle": {"input_style": "1_click"},
        "budget_curve": {"entry_cost_divines": 0.5},
        "availability": {"ssf_viable": "high"},
        "progression": {"leveling_confidence": "confirmed"},
        "confidence": {"representative_build_status": "confirmed", "source_count": 2},
        "evidence": [{"type": "maxroll"}, {"type": "poe_vault"}],
        "suitability": {"mapping": 88},
    }
    user_state = {
        "character_state": {
            "patch": "3.25",
            "class_name": "Marauder",
            "ascendancy": "Juggernaut",
            "character_locked": False,
        },
        "currency_state": {"liquid_divines": 2},
        "preferences": {
            "desired_main_skill": "Lightning Arrow",
            "max_input_style": "1_click",
            "target_contents": ["mapping"],
            "trade_mode": "ssf",
        },
        "constraints": {},
    }

    result = evaluate_compatibility(profile, user_state)

    assert result["selected_plan"] == "C"
    assert "skill_mismatch" in result["hard_blocks"]
    assert result["ai_policy"]["mode"] == "proxy_only"
    assert result["verification_loop"]["loop_state"] == "escalate_to_proxy"
    assert result["response_layers"]["user_message"]["template_id"] == "plan_c_skill_proxy"
    assert any(
        entry["guard"] == "skill_guard" and entry["status"] == "proxy"
        for entry in result["deterministic_guards"]
    )


def test_hold_status_keeps_plan_b_but_forces_verification_only_ai_mode():
    profile = {
        "identity": {
            "main_skill": "Hexblast",
            "patch": "3.25",
            "class_name": "Shadow",
            "ascendancy": "Trickster",
        },
        "playstyle": {"input_style": "1_click"},
        "budget_curve": {"entry_cost_divines": 1.0},
        "availability": {"ssf_viable": "medium"},
        "progression": {"leveling_confidence": "inferred"},
        "confidence": {"representative_build_status": "hold", "source_count": 1},
        "evidence": [{"type": "manual_curated"}],
        "suitability": {"mapping": 80},
    }
    user_state = {
        "character_state": {
            "patch": "3.25",
            "class_name": "Shadow",
            "ascendancy": "Trickster",
            "character_locked": False,
        },
        "currency_state": {"liquid_divines": 5},
        "preferences": {
            "desired_main_skill": "Hexblast",
            "max_input_style": "1_click",
            "target_contents": ["mapping"],
            "trade_mode": "trade_league_start",
        },
        "constraints": {},
    }

    result = evaluate_compatibility(profile, user_state)

    assert result["selected_plan"] == "B"
    assert "hold_status" in result["soft_flags"]
    assert result["ai_policy"]["mode"] == "verification_only"
    assert result["verification_loop"]["loop_state"] == "needs_verification"
    assert result["response_layers"]["user_message"]["template_id"] == "plan_b_hold_exact"
    assert any(
        entry["guard"] == "confidence_guard" and entry["status"] == "soft"
        for entry in result["deterministic_guards"]
    )


def test_skill_mismatch_cross_class_without_lock_forces_plan_d():
    profile = {
        "identity": {
            "main_skill": "Lightning Arrow",
            "patch": "3.25",
            "class_name": "Ranger",
            "ascendancy": "Deadeye",
        },
        "playstyle": {"input_style": "1_click_plus_movement"},
        "budget_curve": {"entry_cost_divines": 0.5},
        "availability": {"ssf_viable": "high"},
        "progression": {"leveling_confidence": "confirmed"},
        "confidence": {"representative_build_status": "confirmed", "source_count": 2},
        "evidence": [{"type": "maxroll"}, {"type": "poe_vault"}],
        "suitability": {"mapping": 90},
    }
    user_state = {
        "character_state": {
            "patch": "3.25",
            "class_name": "Templar",
            "ascendancy": "Hierophant",
            "character_locked": False,
        },
        "currency_state": {"liquid_divines": 10},
        "preferences": {
            "desired_main_skill": "Ball Lightning",
            "max_input_style": "1_click_plus_movement",
            "target_contents": ["mapping"],
            "trade_mode": "trade_league_start",
        },
        "constraints": {"forbid_reroll": True},
    }

    result = evaluate_compatibility(profile, user_state)

    assert result["selected_plan"] == "D"
    assert "in_place_proxy_conflict" in result["hard_blocks"]
    assert result["response_layers"]["user_message"]["template_id"] == "plan_d_proxy_scope_block"


def test_skill_mismatch_cross_ascendancy_without_lock_forces_plan_d():
    profile = {
        "identity": {
            "main_skill": "Hexblast Mine",
            "patch": "3.25",
            "class_name": "Shadow",
            "ascendancy": "Saboteur",
        },
        "playstyle": {"input_style": "1_click"},
        "budget_curve": {"entry_cost_divines": 0.5},
        "availability": {"ssf_viable": "high"},
        "progression": {"leveling_confidence": "confirmed"},
        "confidence": {"representative_build_status": "confirmed", "source_count": 2},
        "evidence": [{"type": "maxroll"}, {"type": "poe_vault"}],
        "suitability": {"mapping": 88},
    }
    user_state = {
        "character_state": {
            "patch": "3.25",
            "class_name": "Shadow",
            "ascendancy": "Trickster",
            "character_locked": False,
        },
        "currency_state": {"liquid_divines": 5},
        "preferences": {
            "desired_main_skill": "Hexblast",
            "max_input_style": "1_click",
            "target_contents": ["mapping"],
            "trade_mode": "trade_league_start",
        },
        "constraints": {"forbid_reroll": True},
    }

    result = evaluate_compatibility(profile, user_state)

    assert result["selected_plan"] == "D"
    assert "in_place_proxy_conflict" in result["hard_blocks"]
    assert result["response_layers"]["user_message"]["template_id"] == "plan_d_proxy_scope_block"
