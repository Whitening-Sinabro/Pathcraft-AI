# -*- coding: utf-8 -*-
"""Sanity checks for POE1 build corpus collection targets."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TARGET_PATH = ROOT / "data" / "build_corpus_collection_targets_v1.json"
REAL_CASES_PATH = ROOT / "data" / "build_variant_real_cases_v1.json"


def _load_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def test_collection_target_totals_are_consistent():
    data = _load_json(TARGET_PATH)

    assert data["dataset_kind"] == "poe1_build_corpus_collection_targets"
    assert data["patch_range"]["confirmed_collection_patches"] == [
        "3.22",
        "3.23",
        "3.24",
        "3.25",
        "3.26",
        "3.27",
        "3.28",
    ]
    assert data["patch_range"]["watchlist_patches"] == ["3.29"]

    per_patch = data["per_patch_target"]
    composition = per_patch["composition"]
    assert sum(composition.values()) == per_patch["canonical_build_cases"]
    assert per_patch["canonical_build_cases"] == 20
    assert per_patch["minimum_state_snapshots_per_case"] == 2
    assert per_patch["minimum_state_snapshots_per_patch"] == 40

    stable_lane_total = sum(
        lane["stable_shells_per_patch"] for lane in data["archetype_lanes"]
    )
    assert stable_lane_total == composition["stable_shells"]

    confirmed = data["totals"]["confirmed_3_22_to_3_28"]
    operational = data["totals"]["operational_including_3_29_watchlist"]
    assert confirmed["patch_count"] == 7
    assert operational["patch_count"] == 8
    assert confirmed["build_cases"] == per_patch["canonical_build_cases"] * 7
    assert operational["build_cases"] == per_patch["canonical_build_cases"] * 8
    assert confirmed["state_snapshots"] == per_patch["minimum_state_snapshots_per_patch"] * 7
    assert operational["state_snapshots"] == per_patch["minimum_state_snapshots_per_patch"] * 8


def test_current_baseline_matches_real_case_file():
    targets = _load_json(TARGET_PATH)
    real_cases = _load_json(REAL_CASES_PATH)

    counts: dict[str, dict[str, int]] = defaultdict(lambda: {"cases": 0, "states": 0})
    for case in real_cases["cases"]:
        patch_counts = counts[case["patch"]]
        patch_counts["cases"] += 1
        patch_counts["states"] += len(case.get("states", []))

    baseline_rows = targets["current_local_baseline"]["patches"]
    for row in baseline_rows:
        patch_counts = counts[row["patch"]]
        assert row["current_build_cases"] == patch_counts["cases"]
        assert row["current_state_snapshots"] == patch_counts["states"]
        assert row["case_deficit"] == row["target_build_cases"] - row["current_build_cases"]
        assert row["snapshot_deficit"] == row["target_state_snapshots"] - row["current_state_snapshots"]

    confirmed_total = targets["current_local_baseline"]["confirmed_total"]
    assert confirmed_total["current_build_cases"] == sum(
        row["current_build_cases"] for row in baseline_rows
    )
    assert confirmed_total["current_state_snapshots"] == sum(
        row["current_state_snapshots"] for row in baseline_rows
    )
    assert confirmed_total["case_deficit"] == sum(row["case_deficit"] for row in baseline_rows)
    assert confirmed_total["snapshot_deficit"] == sum(
        row["snapshot_deficit"] for row in baseline_rows
    )

