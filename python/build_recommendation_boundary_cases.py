# -*- coding: utf-8 -*-
"""Build reproducible QA snapshots for recommendation boundary cases."""

from __future__ import annotations

import json
from pathlib import Path

from recommend_from_corpus import recommend_from_profile_corpus
from recommendation_contract_audit import evaluate_compatibility

ROOT = Path(__file__).resolve().parent.parent
CORPUS_PATH = ROOT / "data" / "poe1_representative_build_profiles.latest.json"


def _load_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def _load_rows() -> list[dict]:
    return _load_json(CORPUS_PATH).get("profiles", [])


def _find_row(rows: list[dict], candidate_id: str) -> dict:
    for row in rows:
        if row.get("candidate_id") == candidate_id:
            return row
    raise KeyError(f"Unknown candidate_id: {candidate_id}")


def _make_user_state(
    *,
    patch: str,
    class_name: str,
    ascendancy: str,
    desired_skill: str,
    liquid_divines: float,
    trade_mode: str = "twink",
    max_input_style: str = "1_click_plus_movement",
    character_locked: bool = False,
) -> dict:
    return {
        "character_state": {
            "patch": patch,
            "class_name": class_name,
            "ascendancy": ascendancy,
            "level": 71,
            "character_locked": character_locked,
        },
        "currency_state": {
            "liquid_divines": liquid_divines,
            "liquid_chaos": 180.0,
            "owned_uniques": [],
        },
        "preferences": {
            "desired_main_skill": desired_skill,
            "max_input_style": max_input_style,
            "target_contents": ["mapping", "expedition"],
            "trade_mode": trade_mode,
            "death_tolerance": "medium",
            "respec_tolerance_points": 30,
        },
        "constraints": {
            "must_use_skill": desired_skill,
            "forbidden_skills": [],
            "require_confirmed_leveling": False,
            "forbid_reroll": True,
        },
    }


def _summarize_compatibility(result: dict) -> dict:
    message = result.get("response_layers", {}).get("user_message", {})
    loop = result.get("verification_loop", {})
    return {
        "selected_plan": result.get("selected_plan"),
        "hard_blocks": result.get("hard_blocks", []),
        "soft_flags": result.get("soft_flags", []),
        "template_id": message.get("template_id"),
        "ai_mode": result.get("ai_policy", {}).get("mode"),
        "loop_state": loop.get("loop_state"),
        "confidence_lane": loop.get("confidence_lane"),
        "promotion_requirements": loop.get("promotion_requirements", []),
        "next_actions": loop.get("next_actions", []),
    }


def _summarize_recommendation(result: dict) -> dict:
    recommendation = result.get("recommendation", {})
    message = recommendation.get("response_layers", {}).get("user_message", {})
    loop = recommendation.get("verification_loop", {})
    selected_candidate = recommendation.get("selected_candidate") or {}
    blocking_candidate = recommendation.get("blocking_candidate") or {}
    return {
        "active_scope": result.get("active_scope"),
        "selected_plan": recommendation.get("selected_plan"),
        "selected_candidate_id": selected_candidate.get("candidate_id"),
        "blocking_candidate_id": blocking_candidate.get("candidate_id"),
        "template_id": message.get("template_id"),
        "ai_mode": recommendation.get("ai_policy", {}).get("mode"),
        "loop_state": loop.get("loop_state"),
        "confidence_lane": loop.get("confidence_lane"),
        "promotion_requirements": loop.get("promotion_requirements", []),
        "next_actions": loop.get("next_actions", []),
    }


def _row_meta(row: dict) -> dict:
    profile = row.get("build_profile", {})
    identity = profile.get("identity", {})
    confidence = profile.get("confidence", {})
    return {
        "candidate_id": row.get("candidate_id"),
        "build_id": profile.get("build_id"),
        "main_skill": identity.get("main_skill"),
        "class_name": identity.get("class_name"),
        "ascendancy": identity.get("ascendancy"),
        "patch": identity.get("patch"),
        "board_status": row.get("board_status"),
        "use_policy": row.get("use_policy"),
        "representative_build_status": confidence.get("representative_build_status"),
        "source_count": confidence.get("source_count"),
    }


def build_boundary_case_report() -> dict:
    rows = _load_rows()

    hold_row = _find_row(rows, "3.26_ball_lightning_caster")

    hold_exact_state = _make_user_state(
        patch="3.28",
        class_name="Shadow",
        ascendancy="Trickster",
        desired_skill="Kinetic Fusillade of Detonation",
        liquid_divines=40.0,
    )
    hold_exact_result = recommend_from_profile_corpus(hold_exact_state, allow_hold_fallback=True)

    same_class_proxy_state = _make_user_state(
        patch="3.26",
        class_name="Templar",
        ascendancy="Hierophant",
        desired_skill="Ice Nova",
        liquid_divines=20.0,
        max_input_style="1_click",
    )
    same_class_proxy_result = evaluate_compatibility(hold_row["build_profile"], same_class_proxy_state)

    patch_block_state = _make_user_state(
        patch="3.25",
        class_name="Templar",
        ascendancy="Hierophant",
        desired_skill="Ball Lightning",
        liquid_divines=20.0,
        max_input_style="1_click",
    )
    patch_block_result = evaluate_compatibility(hold_row["build_profile"], patch_block_state)

    budget_block_state = _make_user_state(
        patch="3.26",
        class_name="Templar",
        ascendancy="Hierophant",
        desired_skill="Ball Lightning",
        liquid_divines=0.2,
        max_input_style="1_click",
    )
    budget_block_result = evaluate_compatibility(hold_row["build_profile"], budget_block_state)

    cross_class_scope_state = _make_user_state(
        patch="3.28",
        class_name="Shadow",
        ascendancy="Trickster",
        desired_skill="Ball Lightning",
        liquid_divines=40.0,
    )
    cross_class_scope_result = recommend_from_profile_corpus(cross_class_scope_state, allow_hold_fallback=False)

    cases = [
        {
            "case_id": "corpus_hold_exact_fallback_plan_b",
            "surface": "recommend_from_corpus",
            "scenario": "Hold-only exact skill can re-enter through hold fallback and stays Plan B with verification-only AI.",
            "expected": {
                "selected_plan": "B",
                "template_id": "plan_b_hold_exact",
            },
            "actual": _summarize_recommendation(hold_exact_result),
        },
        {
            "case_id": "profile_hold_skill_mismatch_plan_c",
            "surface": "evaluate_compatibility",
            "scenario": "The same hold-profile can still degrade to Plan C when the user wants another skill but keeps the same class and ascendancy.",
            "source_candidate": _row_meta(hold_row),
            "expected": {
                "selected_plan": "C",
                "template_id": "plan_c_skill_proxy",
            },
            "actual": _summarize_compatibility(same_class_proxy_result),
        },
        {
            "case_id": "profile_hold_patch_block_plan_d",
            "surface": "evaluate_compatibility",
            "scenario": "The same actual hold profile must abstain with Plan D when the patch guard fails.",
            "source_candidate": _row_meta(hold_row),
            "expected": {
                "selected_plan": "D",
                "template_id": "plan_d_patch_block",
            },
            "actual": _summarize_compatibility(patch_block_result),
        },
        {
            "case_id": "profile_hold_budget_block_plan_d",
            "surface": "evaluate_compatibility",
            "scenario": "The same actual hold profile must abstain with Plan D when the deterministic budget floor is missed.",
            "source_candidate": _row_meta(hold_row),
            "expected": {
                "selected_plan": "D",
                "template_id": "plan_d_budget_block",
            },
            "actual": _summarize_compatibility(budget_block_result),
        },
        {
            "case_id": "corpus_cross_class_proxy_scope_plan_d",
            "surface": "recommend_from_corpus",
            "scenario": "Cross-class Ball Lightning demand must not leak through as an in-place proxy and stays Plan D.",
            "expected": {
                "selected_plan": "D",
                "template_id": "plan_d_proxy_scope_block",
            },
            "actual": _summarize_recommendation(cross_class_scope_result),
        },
    ]

    return {
        "dataset_kind": "poe1_recommendation_boundary_case_report",
        "corpus_path": CORPUS_PATH.relative_to(ROOT).as_posix(),
        "cases": cases,
    }


if __name__ == "__main__":
    print(json.dumps(build_boundary_case_report(), ensure_ascii=False, indent=2))
