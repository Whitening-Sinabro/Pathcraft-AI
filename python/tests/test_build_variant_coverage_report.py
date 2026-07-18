# -*- coding: utf-8 -*-
"""Coverage summary sanity checks for build variant corpus progress."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from build_variant_coverage_report import build_coverage_summary  # noqa: E402


QUEUE_PATH = ROOT / "data" / "build_variant_collection_queue_v1.json"
REAL_CASES_PATH = ROOT / "data" / "build_variant_real_cases_v1.json"


def _load_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def test_coverage_summary_has_expected_shape():
    summary = build_coverage_summary()

    assert summary["queue_dataset_kind"] == "poe1_build_real_case_collection_queue"
    assert summary["real_case_dataset_kind"] == "poe1_build_variant_real_cases"
    assert summary["real_case_count"] >= 24
    assert len(summary["by_patch"]) >= 7


def test_coverage_summary_includes_seeded_progress():
    summary = build_coverage_summary()
    by_patch = {item["patch"]: item for item in summary["by_patch"]}

    assert by_patch["3.23"]["seeded_count"] >= 1
    assert by_patch["3.24"]["seeded_count"] >= 5
    assert by_patch["3.25"]["seeded_count"] >= 5
    assert by_patch["3.26"]["seeded_count"] >= 5
    assert by_patch["3.27"]["seeded_count"] >= 5
    assert by_patch["3.28"]["seeded_count"] >= 5


def test_coverage_summary_tracks_provisional_vs_confirmed_seeded():
    summary = build_coverage_summary()
    by_patch = {item["patch"]: item for item in summary["by_patch"]}

    assert by_patch["3.22"]["provisional_seeded_count"] == 1
    assert by_patch["3.23"]["provisional_seeded_count"] == 1
    assert by_patch["3.26"]["provisional_seeded_count"] == 4
    assert by_patch["3.27"]["confirmed_seeded_count"] == 2
    assert by_patch["3.28"]["provisional_seeded_count"] == 2
    assert by_patch["3.28"]["confirmed_seeded_count"] == 3
    assert by_patch["3.28"]["confirmed_coverage_ratio"] == 0.6


def test_personal_target_does_not_count_as_flagship_coverage():
    summary = build_coverage_summary()
    by_patch = {item["patch"]: item for item in summary["by_patch"]}
    queue = _load_json(QUEUE_PATH)
    real_cases = _load_json(REAL_CASES_PATH)

    patch_queue = next(item for item in queue["patches"] if item["patch"] == "3.28")
    patch_cases = [case for case in real_cases["cases"] if case["patch"] == "3.28"]

    personal_targets = [item for item in patch_queue["queue"] if item.get("candidate_role") == "personal_target"]
    assert len(personal_targets) == 1
    assert personal_targets[0]["candidate_id"] == "3.28_strength_stacker_juggernaut"

    assert len(patch_cases) >= 7
    assert sum(1 for case in patch_cases if case["archetype_id"] == "strength_stacker_juggernaut") == 2
    assert len([case for case in patch_cases if case["archetype_id"] != "strength_stacker_juggernaut"]) >= 5

    assert by_patch["3.28"]["seeded_count"] >= 5
    assert by_patch["3.28"]["personal_target_seeded_count"] == 1
