# -*- coding: utf-8 -*-
"""Regression checks for ranked research queue generation."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from build_variant_research_queue import build_research_queue  # noqa: E402


def test_research_queue_has_expected_shape():
    queue = build_research_queue()

    assert queue["dataset_kind"] == "poe1_build_variant_research_queue"
    assert queue["item_count"] >= 15
    assert len(queue["by_patch"]) >= 6
    assert len(queue["by_next_step"]) >= 2


def test_research_queue_prioritizes_remaining_blocked_3_28_candidate():
    queue = build_research_queue()
    items = queue["items"]

    top_candidates = [item["candidate_id"] for item in items[:5]]
    assert "3.28_kinetic_fusillade_of_detonation" in top_candidates


def test_research_queue_tracks_promoted_penance_as_second_source_work():
    queue = build_research_queue()
    items = {item["candidate_id"]: item for item in queue["items"]}
    penance = items["3.28_penance_brand_inquisitor"]

    assert penance["strict_verdict"] == "standard_only"
    assert penance["next_step"] == "find_second_external_build_guide_source"
    assert penance["guide_source_families"] == ["creator_guide"]


def test_research_queue_groups_first_external_source_work():
    queue = build_research_queue()
    by_next_step = {item["next_step"]: item for item in queue["by_next_step"]}

    assert by_next_step["find_first_external_build_guide_source"]["item_count"] >= 4
    assert "3.26_ball_lightning_caster" in by_next_step["find_first_external_build_guide_source"]["top_candidates"]


def test_research_queue_marks_weak_patches_as_dense_backlogs():
    queue = build_research_queue()
    by_patch = {item["patch"]: item for item in queue["by_patch"]}

    assert by_patch["3.26"]["item_count"] == 5
    assert by_patch["3.27"]["item_count"] == 5
    assert by_patch["3.28"]["item_count"] == 5


def test_research_queue_includes_blockers_and_patch_context():
    queue = build_research_queue()
    items = {item["candidate_id"]: item for item in queue["items"]}

    kinetic = items["3.28_kinetic_fusillade_of_detonation"]
    assert kinetic["patch_strict_confirmable_count"] == 0
    assert "missing_external_build_guide" in kinetic["blockers"]

    shockwave = items["3.22_shockwave_totems_hierophant"]
    assert shockwave["next_step"] == "find_second_external_build_guide_source"
