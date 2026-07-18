# -*- coding: utf-8 -*-
"""Cumulative 3.27 -> 3.29 patch history context integrity tests."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "python"))

from build_coach import load_patch_history_context  # noqa: E402

HISTORY_PATH = ROOT / "data" / "patch_notes" / "poe1_3_27_3_29_patch_history_context.json"


def _load_history() -> dict:
    return json.loads(HISTORY_PATH.read_text(encoding="utf-8"))


def test_patch_history_context_covers_327_328_and_329():
    data = _load_history()

    assert data["dataset_kind"] == "poe1_3_27_3_29_patch_history_context"
    assert data["scope"]["patch_bands"] == ["3.27", "3.28", "3.29"]
    assert data["scope"]["latest_observed_version"] == "3.29.0"
    assert data["cumulative_summary"]["patch_count"] >= 50
    assert data["cumulative_summary"]["missing_files"] == []

    by_band = {row["patch_band"]: row for row in data["patch_band_summary"]}
    assert by_band["3.27"]["patch_count"] >= 10
    assert by_band["3.28"]["patch_count"] >= 30
    assert by_band["3.29"]["patch_count"] >= 1
    assert by_band["3.28"]["hotfix_count"] >= 20


def test_patch_history_exposes_reuse_decision_gates():
    data = _load_history()
    gates = {row["id"]: row for row in data["decision_gates"]}

    assert "historical_patch_survival" in gates
    assert gates["historical_patch_survival"]["player_label"] == "연습해도 됨"
    assert "hotfix_override" in gates
    assert "pob_compatibility" in gates
    assert "socket_quality_optimization" in gates

    rules = {row["source_patch_band"]: row for row in data["candidate_patch_band_rules"]}
    assert rules["3.27"]["default_max_label"] == "연습해도 됨"
    assert rules["3.28"]["default_max_label"] == "가능성 높음"
    assert rules["3.29"]["default_max_label"] == "가능성 높음"


def test_patch_history_tracks_rgb_as_quality_optimization_not_socket_gate():
    data = _load_history()
    policy = data["socket_match_optimization_policy"]

    assert "can be socketed" in policy["access_rule"]
    assert "+10% quality" in policy["optimization_rule"]
    assert "main_damage_skill" in policy["high_priority_matches"]
    assert "temporary_leveling_link" in policy["low_priority_matches"]
    assert "cannot use a gem because the colour is wrong" in policy["coach_rule"]


def test_build_coach_loads_patch_history_context():
    context = load_patch_history_context()

    assert context["dataset_kind"] == "poe1_3_27_3_29_patch_history_context"
    assert context["cumulative_summary"]["patch_count"] >= 50
    assert context["decision_gates"]
    assert context["socket_match_optimization_policy"]["high_priority_matches"]
