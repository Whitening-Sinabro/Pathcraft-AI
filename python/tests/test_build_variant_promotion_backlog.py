# -*- coding: utf-8 -*-
"""Regression checks for promotion backlog generation."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from build_variant_promotion_backlog import build_promotion_backlog  # noqa: E402


def test_promotion_backlog_has_expected_shape():
    backlog = build_promotion_backlog()

    assert backlog["dataset_kind"] == "poe1_build_variant_promotion_backlog"
    assert backlog["item_count"] >= 10
    assert len(backlog["by_patch"]) >= 5


def test_promotion_backlog_prioritizes_external_confirmation_work():
    backlog = build_promotion_backlog()
    items = backlog["items"]

    assert any(item["candidate_id"] == "3.26_boneshatter_juggernaut" and item["next_step"] == "find_second_external_source" for item in items)
    assert any(item["candidate_id"] == "3.28_kinetic_fusillade_of_detonation" and item["next_step"] == "find_external_confirmation" for item in items)


def test_promotion_backlog_patch_summaries_highlight_weak_patches():
    backlog = build_promotion_backlog()
    by_patch = {item["patch"]: item for item in backlog["by_patch"]}

    assert by_patch["3.26"]["urgent_count"] >= 2
    assert by_patch["3.28"]["urgent_count"] >= 2
