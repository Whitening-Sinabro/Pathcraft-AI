# -*- coding: utf-8 -*-
"""3.29 launch-week information intake plan and freshness status."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "python"))

from build_coach import load_poe1_3_29_information_intake_plan  # noqa: E402
from poe1_live_intake import build_intake_status, load_plan, write_status  # noqa: E402

PLAN_PATH = ROOT / "data" / "poe1_3_29_information_intake_plan.json"


def test_information_intake_plan_has_fast_sources_and_gates():
    plan = json.loads(PLAN_PATH.read_text(encoding="utf-8"))

    assert plan["dataset_kind"] == "poe1_3_29_information_intake_plan"
    assert plan["patch"] == "3.29.0"
    assert plan["latency_targets"]["official_patch_or_hotfix_detection_minutes"] <= 5
    assert plan["latency_targets"]["ggpk_client_update_detection_minutes"] <= 2

    track_ids = {row["id"] for row in plan["intake_tracks"]}
    assert {
        "official_patch_forum",
        "ggpk_client_snapshot",
        "pob_support_probe",
        "poe_ninja_economy",
        "build_source_search",
        "live_map_measurements",
    }.issubset(track_ids)

    gate_names = {row["name"] for row in plan["promotion_gates"]}
    assert {"mechanic_truth", "build_viability", "farming_recommendation"}.issubset(gate_names)
    assert any(row["name"] == "patch_fast_refresh" for row in plan["fastlane_commands"])


def test_build_coach_loads_information_intake_plan():
    plan = load_poe1_3_29_information_intake_plan()

    assert plan["dataset_kind"] == "poe1_3_29_information_intake_plan"
    assert plan["coach_rules"]
    assert any("promotion" in rule.lower() for rule in plan["coach_rules"])


def test_live_intake_status_reports_tracks_and_fastlane_commands(tmp_path):
    plan = load_plan()
    status = build_intake_status(plan, now=datetime.now(timezone.utc))

    assert status["dataset_kind"] == "poe1_3_29_information_intake_status"
    assert status["patch"] == "3.29.0"
    assert status["summary"]["track_count"] == len(plan["intake_tracks"])
    assert status["fastlane_commands"]
    assert status["promotion_gates"]
    assert any(row["id"] == "official_patch_forum" for row in status["tracks"])

    output_path = tmp_path / "status.json"
    written = write_status(output_path)
    assert output_path.exists()
    assert written["dataset_kind"] == "poe1_3_29_information_intake_status"
