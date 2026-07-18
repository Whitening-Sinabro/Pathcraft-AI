# -*- coding: utf-8 -*-
"""Regression checks for the POE1 build corpus collection backlog."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from build_corpus_collection_backlog import build_collection_backlog  # noqa: E402


def test_collection_backlog_has_expected_shape():
    backlog = build_collection_backlog()

    assert backlog["dataset_kind"] == "poe1_build_corpus_collection_backlog"
    assert backlog["per_patch_target"]["canonical_build_cases"] == 20
    assert backlog["per_patch_target"]["minimum_state_snapshots_per_patch"] == 40
    assert len(backlog["by_patch"]) == 8
    assert len(backlog["priority_patches"]) == 8


def test_collection_backlog_totals_match_current_real_cases():
    backlog = build_collection_backlog()
    confirmed = backlog["totals"]["confirmed_3_22_to_3_28"]
    operational = backlog["totals"]["operational_including_watchlist"]

    assert confirmed["current_build_cases"] == 49
    assert confirmed["current_state_snapshots"] == 133
    assert confirmed["target_build_cases"] == 140
    assert confirmed["target_state_snapshots"] == 280
    assert confirmed["case_deficit"] == 91
    assert confirmed["snapshot_deficit"] == 147

    assert operational["target_build_cases"] == 160
    assert operational["target_state_snapshots"] == 320
    assert operational["case_deficit"] == 111
    assert operational["snapshot_deficit"] == 187


def test_collection_backlog_detects_lane_deficits():
    backlog = build_collection_backlog()
    by_patch = {row["patch"]: row for row in backlog["by_patch"]}
    patch_322_lanes = {row["lane_id"]: row for row in by_patch["3.22"]["lane_coverage"]}

    assert patch_322_lanes["spell_hit_brand_selfcast"]["current_cases"] == 0
    assert patch_322_lanes["spell_hit_brand_selfcast"]["stable_shell_deficit"] == 2
    assert patch_322_lanes["minion_trigger_autobomber_special"]["stable_shell_deficit"] == 2
    assert sum(row["stable_shell_deficit"] for row in by_patch["3.22"]["lane_coverage"]) >= 6


def test_collection_backlog_plans_slots_without_exceeding_deficit():
    backlog = build_collection_backlog()

    for row in backlog["by_patch"]:
        assert len(row["planned_slots"]) == row["case_deficit"]
        assert all(slot["status"] == "needs_source_hunt" for slot in row["planned_slots"])

    by_patch = {row["patch"]: row for row in backlog["by_patch"]}
    assert by_patch["3.29"]["patch_target_status"] == "watchlist"
    assert by_patch["3.29"]["current_build_cases"] == 0
    # ACCUMULATING (shrinking deficit): case_deficit = target - current, and it
    # falls toward 0 as real 3.29 cases are gathered. Bound it instead of pinning
    # 20, and pin the derivation invariant so the target/formula is still guarded.
    row_329 = by_patch["3.29"]
    assert 0 <= row_329["case_deficit"] <= 20
    assert row_329["current_build_cases"] + row_329["case_deficit"] == row_329["target_build_cases"] == 20
    # planned_slots track the deficit (line 59 pins len == case_deficit for all
    # patches); as the deficit shrinks the slot count shrinks with it.
    assert len(row_329["planned_slots"]) <= 20
    assert len(row_329["planned_slots"]) == row_329["case_deficit"]

