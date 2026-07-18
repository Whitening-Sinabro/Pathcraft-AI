# -*- coding: utf-8 -*-
"""Regression checks for evidence consistency audit."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from build_variant_evidence_consistency_audit import build_evidence_consistency_audit  # noqa: E402


def test_evidence_consistency_audit_has_expected_shape():
    audit = build_evidence_consistency_audit()

    assert audit["dataset_kind"] == "poe1_build_variant_evidence_consistency_audit"
    assert len(audit["by_patch"]) >= 7
    assert audit["finding_count"] == 0


def test_evidence_consistency_audit_is_clean_after_evidence_sync():
    audit = build_evidence_consistency_audit()

    assert audit["findings"] == []


def test_evidence_consistency_audit_keeps_clean_patch_low_noise():
    audit = build_evidence_consistency_audit()
    by_patch = {item["patch"]: item for item in audit["by_patch"]}

    assert by_patch["3.25"]["high_severity_count"] == 0
