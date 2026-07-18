# -*- coding: utf-8 -*-
"""Integrity checks for global creator collection priority matrix."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MATRIX_PATH = ROOT / "data" / "poe1_global_creator_priority_matrix_v1.json"
SOURCE_TARGETS_PATH = ROOT / "data" / "poe1_global_creator_source_targets_v1.json"


def _load_matrix() -> dict:
    return json.loads(MATRIX_PATH.read_text(encoding="utf-8"))


def _load_source_targets() -> dict:
    return json.loads(SOURCE_TARGETS_PATH.read_text(encoding="utf-8"))


def _lanes(data: dict) -> dict:
    return {row["lane_id"]: row for row in data["collection_lanes"]}


def test_priority_matrix_shape_and_policy():
    data = _load_matrix()

    assert data["dataset_kind"] == "poe1_global_creator_priority_matrix"
    assert data["source_dataset"] == "data/poe1_global_creator_source_targets_v1.json"
    # ACCUMULATING: creator registry is append-only (creators added, never removed),
    # so the source target count only grows. Floor-check the baseline and pin
    # internal consistency against the source dataset so silent shrinkage is caught.
    assert data["source_target_count"] >= 121
    assert data["source_target_count"] == _load_source_targets()["coverage_summary"]["target_count"]
    assert data["policy"]["poe_scope"] == "poe1_only"
    assert "not build-quality proof" in data["policy"]["popularity_rule"]
    assert data["coverage_summary"]["lane_count"] == 12
    assert data["coverage_summary"]["immediate_queue_count"] >= 35


def test_priority_matrix_has_core_collection_lanes():
    lanes = _lanes(_load_matrix())

    assert {
        "leveling",
        "endgame_build",
        "high_end",
        "farming_strategy",
        "hardcore_safety",
        "minion",
        "mine",
        "caster",
        "ranger_projectile",
        "melee",
        "totem",
        "scion_reliquarian",
    } <= set(lanes)
    assert lanes["leveling"]["creator_count"] >= 30
    assert lanes["farming_strategy"]["creator_count"] >= 5
    assert lanes["mine"]["creator_count"] >= 3
    assert lanes["scion_reliquarian"]["creator_count"] <= 10


def test_priority_matrix_routes_named_sources_to_expected_lanes():
    lanes = _lanes(_load_matrix())

    lane_ids = {
        lane_id: {row["creator_id"] for row in lane["top_creator_targets"]}
        for lane_id, lane in lanes.items()
    }

    assert {"tytykiller", "exiled_cat", "zizaran"} & lane_ids["leveling"]
    assert {"fubgun", "goblin_inc_probable", "exiled_cat"} <= lane_ids["farming_strategy"]
    assert {"tori_sensei", "dconnic", "ghazzytv"} <= lane_ids["minion"]
    assert {"cptn_garbage", "jorgen"} <= lane_ids["mine"]
    assert {"kankar", "fubgun"} <= lane_ids["ranger_projectile"]
    assert "exiled_cat" in lane_ids["melee"]


def test_priority_matrix_immediate_queue_keeps_promotion_gate():
    data = _load_matrix()
    queue = data["immediate_collection_queue"]

    assert queue
    assert all(row["promotion_gate"] == "direct_pob_or_stage_guide_required_before_build_promotion" for row in queue)
    assert all(row["source_urls"] for row in queue)
    assert any(row["queue_id"] == "farming_strategy:exiled_cat" for row in queue)
    assert any(row["queue_id"] == "mine:cptn_garbage" for row in queue)


def test_priority_matrix_tracks_weak_regions_for_followup():
    data = _load_matrix()
    weak = {
        row["region_id"]: row
        for row in data["regional_followup"]
        if row["needs_more_youtube_channel_confirmation"]
    }

    assert {"japan", "russia_cis", "portuguese_br_pt", "poland", "spanish_latam_spain"} <= set(weak)
    assert weak["portuguese_br_pt"]["youtube_sampled_creator_count"] == 0


def test_priority_matrix_is_catalogued():
    catalog = json.loads((ROOT / "data" / "db_catalog.json").read_text(encoding="utf-8"))
    entry = catalog["derived"]["poe1_global_creator_priority_matrix_v1.json"]

    assert entry["kind"] == "operations"
    assert entry["rows"] == 12
    assert entry["path"] == "poe1_global_creator_priority_matrix_v1.json"
