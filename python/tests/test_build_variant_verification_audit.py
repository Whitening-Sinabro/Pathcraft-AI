# -*- coding: utf-8 -*-
"""Regression checks for strict verification gates."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from build_variant_verification_audit import build_verification_audit  # noqa: E402


def test_verification_audit_has_expected_shape():
    audit = build_verification_audit()

    assert audit["dataset_kind"] == "poe1_build_variant_verification_audit"
    assert audit["overall"]["flagship_seeded_count"] >= 35
    assert len(audit["by_patch"]) >= 7


def test_verification_audit_separates_standard_from_strict():
    audit = build_verification_audit()
    by_patch = {item["patch"]: item for item in audit["by_patch"]}

    assert by_patch["3.25"]["standard_confirmable_count"] == 5
    assert by_patch["3.25"]["strict_confirmable_count"] == 5
    assert by_patch["3.27"]["standard_confirmable_count"] == 3
    assert by_patch["3.27"]["strict_confirmable_count"] == 0
    assert by_patch["3.28"]["strict_gap_count"] == 5


def test_verification_audit_marks_context_only_cases_as_blocked():
    audit = build_verification_audit()
    items = {item["candidate_id"]: item for item in audit["items"]}

    kinetic = items["3.28_kinetic_fusillade_of_detonation"]
    assert kinetic["strict_verdict"] == "blocked_no_external_build_guide"
    assert kinetic["next_step"] == "find_first_external_build_guide_source"
    assert "missing_external_build_guide" in kinetic["blockers"]


def test_verification_audit_marks_single_external_only_cases_as_gap():
    audit = build_verification_audit()
    items = {item["candidate_id"]: item for item in audit["items"]}

    shockwave = items["3.22_shockwave_totems_hierophant"]
    assert shockwave["strict_verdict"] == "provisional_external_gap"
    assert shockwave["next_step"] == "find_second_external_build_guide_source"
    assert "single_source_only" in shockwave["blockers"]


def test_verification_audit_recognizes_standard_only_cases():
    audit = build_verification_audit()
    items = {item["candidate_id"]: item for item in audit["items"]}

    toxic_rain = items["3.27_toxic_rain_pathfinder"]
    shock_nova = items["3.28_shock_nova_of_procession_hierophant"]

    assert toxic_rain["standard_confirmable"] is True
    assert toxic_rain["strict_confirmable"] is False
    assert toxic_rain["strict_verdict"] == "standard_only"

    assert shock_nova["standard_confirmable"] is True
    assert shock_nova["strict_confirmable"] is False
