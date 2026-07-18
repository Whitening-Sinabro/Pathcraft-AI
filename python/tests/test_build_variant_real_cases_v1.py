# -*- coding: utf-8 -*-
"""Regression checks for real-case build variant labels."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from build_variant_case_validator import validate_cases  # noqa: E402
from build_variant_model_v2 import classify_split  # noqa: E402


ROOT = Path(__file__).resolve().parents[2]
CASES_PATH = ROOT / "data" / "build_variant_real_cases_v1.json"


def _load_cases() -> dict:
    with open(CASES_PATH, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def test_real_cases_file_parses():
    data = _load_cases()
    assert data["dataset_kind"] == "poe1_build_variant_real_cases"
    assert len(data["cases"]) >= 16


def test_real_cases_expected_pairwise_decisions_match_classifier():
    data = _load_cases()

    for case in data["cases"]:
        states = {state["state_id"]: state for state in case["states"]}
        for pair in case["expected_pairwise_decisions"]:
            result = classify_split(
                states[pair["left_state_id"]],
                states[pair["right_state_id"]],
            )
            assert result["decision"] == pair["decision"], (
                f"{case['case_id']} expected {pair['decision']} "
                f"for {pair['left_state_id']} -> {pair['right_state_id']}, "
                f"got {result['decision']}"
            )


def test_real_case_validator_returns_no_mismatches():
    assert validate_cases(CASES_PATH) == []



