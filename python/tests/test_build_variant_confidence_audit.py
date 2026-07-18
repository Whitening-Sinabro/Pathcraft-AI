# -*- coding: utf-8 -*-
"""Audit summary regression checks for build confidence priorities."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from build_variant_confidence_audit import build_confidence_audit  # noqa: E402


def test_confidence_audit_has_expected_shape():
    audit = build_confidence_audit()

    assert audit["dataset_kind"] == "poe1_build_variant_confidence_audit"
    assert audit["priority_count"] >= 10
    assert len(audit["by_patch"]) >= 7


def test_confidence_audit_highlights_weak_patches():
    audit = build_confidence_audit()
    by_patch = {item["patch"]: item for item in audit["by_patch"]}

    assert by_patch["3.25"]["provisional_count"] == 0
    assert by_patch["3.26"]["provisional_count"] >= 4
    assert by_patch["3.27"]["provisional_count"] >= 3
    assert by_patch["3.28"]["provisional_count"] >= 2


def test_confidence_audit_aligns_with_confirmed_counts_for_key_patches():
    audit = build_confidence_audit()
    by_patch = {item["patch"]: item for item in audit["by_patch"]}

    assert by_patch["3.22"]["confirmed_count"] == 4
    assert by_patch["3.23"]["confirmed_count"] == 4
    assert by_patch["3.28"]["confirmed_count"] == 3


def test_confidence_audit_marks_3_22_shockwave_as_poe_vault_only():
    audit = build_confidence_audit()
    record = next(item for item in audit["priorities"] if item["candidate_id"] == "3.22_shockwave_totems_hierophant")

    assert record["reason"] == "poe_vault_only"


def test_confidence_audit_priority_reasons_include_single_source_buckets():
    audit = build_confidence_audit()
    reasons = {item["reason"] for item in audit["priorities"]}

    assert "poe_vault_only" in reasons or "patch_note_only" in reasons or "maxroll_only" in reasons
    assert any(item["candidate_id"] == "3.28_kinetic_fusillade_of_detonation" for item in audit["priorities"])
    assert not any(item["candidate_id"] == "3.28_penance_brand_inquisitor" for item in audit["priorities"])
