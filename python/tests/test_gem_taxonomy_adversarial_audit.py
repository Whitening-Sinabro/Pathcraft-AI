# -*- coding: utf-8 -*-
"""Regression tests for the five-lens gem taxonomy adversarial audit."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from gem_taxonomy_adversarial_audit import build_adversarial_audit  # noqa: E402


ROOT = Path(__file__).resolve().parents[2]
AUDIT_PATH = ROOT / "data" / "gem_taxonomy_adversarial_audit.latest.json"


def test_gem_taxonomy_adversarial_audit_passes_all_five_lenses():
    audit = build_adversarial_audit()

    assert audit["dataset_kind"] == "poe1_gem_taxonomy_adversarial_audit"
    assert audit["status"] == "passed"
    assert audit["summary"]["lens_count"] == 5
    assert audit["summary"]["failure_count"] == 0
    assert audit["summary"]["warning_count"] == 0

    lens_names = {lens["lens"] for lens in audit["lenses"]}
    assert lens_names == {
        "source_integrity",
        "name_collision",
        "socketability_pipeline",
        "context_scoring",
        "season_crosscheck",
    }


def test_generated_gem_taxonomy_adversarial_audit_file_is_current_shape():
    audit = json.loads(AUDIT_PATH.read_text(encoding="utf-8"))

    assert audit["status"] == "passed"
    assert audit["summary"]["taxonomy_entry_count"] > 1000
    assert audit["summary"]["finding_count"] == 0
    assert any(
        lens["lens"] == "name_collision" and lens["active_support_sibling_collisions"] == ["Barrage"]
        for lens in audit["lenses"]
    )
