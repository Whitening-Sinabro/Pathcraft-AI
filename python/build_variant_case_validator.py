# -*- coding: utf-8 -*-
"""Validate labeled real-case build variant decisions."""

from __future__ import annotations

import json
from pathlib import Path

from build_variant_model_v2 import classify_split


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CASES_PATH = ROOT / "data" / "build_variant_real_cases_v1.json"


def load_cases(path: Path = DEFAULT_CASES_PATH) -> dict:
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def validate_cases(path: Path = DEFAULT_CASES_PATH) -> list[dict]:
    data = load_cases(path)
    mismatches: list[dict] = []

    for case in data["cases"]:
        states = {state["state_id"]: state for state in case["states"]}
        for pair in case["expected_pairwise_decisions"]:
            actual = classify_split(
                states[pair["left_state_id"]],
                states[pair["right_state_id"]],
            )
            if actual["decision"] != pair["decision"]:
                mismatches.append(
                    {
                        "case_id": case["case_id"],
                        "left_state_id": pair["left_state_id"],
                        "right_state_id": pair["right_state_id"],
                        "expected": pair["decision"],
                        "actual": actual["decision"],
                        "reasons": actual["reasons"],
                    }
                )

    return mismatches


if __name__ == "__main__":
    mismatches = validate_cases()
    if mismatches:
        print(json.dumps({"ok": False, "mismatches": mismatches}, ensure_ascii=False, indent=2))
        raise SystemExit(1)
    print(json.dumps({"ok": True, "mismatch_count": 0}, ensure_ascii=False, indent=2))
