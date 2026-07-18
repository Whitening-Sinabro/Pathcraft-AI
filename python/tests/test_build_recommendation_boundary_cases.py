# -*- coding: utf-8 -*-
"""Regression checks for recommendation boundary case simulations."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from build_recommendation_boundary_cases import build_boundary_case_report  # noqa: E402


def _index_cases(report: dict) -> dict[str, dict]:
    return {case["case_id"]: case for case in report["cases"]}


def test_boundary_case_report_has_expected_shape():
    report = build_boundary_case_report()

    assert report["dataset_kind"] == "poe1_recommendation_boundary_case_report"
    assert report["corpus_path"] == "data/poe1_representative_build_profiles.latest.json"
    assert len(report["cases"]) >= 5


def test_boundary_case_report_keeps_hold_exact_fallback_as_plan_b():
    cases = _index_cases(build_boundary_case_report())
    case = cases["corpus_hold_exact_fallback_plan_b"]

    assert case["actual"]["active_scope"] == "fallback_with_hold"
    assert case["actual"]["selected_plan"] == "B"
    assert case["actual"]["selected_candidate_id"] == "3.28_kinetic_fusillade_of_detonation"
    assert case["actual"]["template_id"] == "plan_b_hold_exact"
    assert case["actual"]["ai_mode"] == "verification_only"


def test_boundary_case_report_keeps_same_class_skill_mismatch_as_plan_c():
    cases = _index_cases(build_boundary_case_report())
    case = cases["profile_hold_skill_mismatch_plan_c"]

    assert case["source_candidate"]["candidate_id"] == "3.26_ball_lightning_caster"
    assert case["actual"]["selected_plan"] == "C"
    assert case["actual"]["template_id"] == "plan_c_skill_proxy"
    assert case["actual"]["ai_mode"] == "proxy_only"
    assert "skill_mismatch" in case["actual"]["hard_blocks"]


def test_boundary_case_report_marks_patch_and_budget_as_plan_d():
    cases = _index_cases(build_boundary_case_report())
    patch_case = cases["profile_hold_patch_block_plan_d"]
    budget_case = cases["profile_hold_budget_block_plan_d"]

    assert patch_case["actual"]["selected_plan"] == "D"
    assert patch_case["actual"]["template_id"] == "plan_d_patch_block"
    assert "patch_mismatch" in patch_case["actual"]["hard_blocks"]
    assert "hold_status" in patch_case["actual"]["soft_flags"]

    assert budget_case["actual"]["selected_plan"] == "D"
    assert budget_case["actual"]["template_id"] == "plan_d_budget_block"
    assert "underfunded" in budget_case["actual"]["hard_blocks"]
    assert "hold_status" in budget_case["actual"]["soft_flags"]


def test_boundary_case_report_keeps_cross_class_proxy_scope_blocked():
    cases = _index_cases(build_boundary_case_report())
    case = cases["corpus_cross_class_proxy_scope_plan_d"]

    assert case["actual"]["selected_plan"] == "D"
    assert case["actual"]["template_id"] == "plan_d_proxy_scope_block"
    assert case["actual"]["ai_mode"] == "disabled"
