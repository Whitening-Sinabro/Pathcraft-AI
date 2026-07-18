# -*- coding: utf-8 -*-
"""3.29 launch-week validation queue integrity tests."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
QUEUE_PATH = ROOT / "data" / "poe1_3_29_live_validation_queue.json"


def _load_queue() -> dict:
    return json.loads(QUEUE_PATH.read_text(encoding="utf-8"))


def test_329_live_validation_queue_has_required_tracks():
    data = _load_queue()

    assert data["dataset_kind"] == "poe1_3_29_live_validation_queue"
    assert data["patch"] == "3.29"
    assert data["status"] == "pre_launch_queue"
    assert "data/poe1_3_29_global_review.json" in data["source_context"]
    assert "data/patch_notes/poe1_3_27_3_29_patch_history_context.json" in data["source_context"]
    assert "data/poe1_3_29_luminary_merc_link_intake_v1.json" in data["source_context"]

    tracks = {row["id"]: row for row in data["validation_tracks"]}
    assert {
        "post_329_ggpk_extract",
        "pob_support_probe",
        "allflame_loop_measurement",
        "mercenary_modeling",
        "scion_branch_validation",
        "socket_crafting_and_filter_update",
        "atlas_legion_scrying_refresh",
        "build_archetype_watchlist",
        "new_player_explanation_pack",
    } <= set(tracks)

    for track in tracks.values():
        assert track["required_inputs"], track["id"]
        assert track["outputs"], track["id"]
        assert track["promotion_gate"], track["id"]

    mercenary = tracks["mercenary_modeling"]
    assert "Luminary link-skill node names and point pathing" in mercenary["required_inputs"]
    assert "Hallowed Monarch current item text and linked-target behavior" in mercenary["required_inputs"]
    assert "Luminary link-shell scorecards" in mercenary["outputs"]


def test_329_live_validation_queue_blocks_premature_recommendations():
    data = _load_queue()
    rules = "\n".join(data["promotion_rules"])

    assert "No build branch can be promoted" in rules
    assert "No farming branch can be promoted" in rules
    assert "Scion branches must stay separated" in rules
    assert "Mercenary setup must be modeled as separate state" in rules
    assert "Older 3.27/3.28 PoBs are practice sources" in rules

    tracks = {row["id"]: row for row in data["validation_tracks"]}
    assert tracks["post_329_ggpk_extract"]["status"] == "blocked_until_launch_client"
    assert tracks["pob_support_probe"]["status"] == "blocked_until_pob_update"
    assert "GGPK" in tracks["post_329_ggpk_extract"]["promotion_gate"]
    assert "PoB" in tracks["pob_support_probe"]["promotion_gate"]


def test_329_live_validation_queue_covers_measurement_schema():
    data = _load_queue()
    schema = data["measurement_schema"]

    run = schema["run_sample"]
    assert run["branch"] == "ascendant|reliquarian|luminary|non_scion"
    assert "duration_seconds" in run
    assert "deaths" in run
    assert "notable_rewards" in run

    economy = schema["economy_sample"]
    assert economy["league"] == "Curse of the Allflame"
    assert economy["confidence"] == "manual|trade_api|community_report"


def test_329_live_validation_queue_is_catalogued():
    catalog = json.loads((ROOT / "data" / "db_catalog.json").read_text(encoding="utf-8"))

    entry = catalog["derived"]["poe1_3_29_live_validation_queue.json"]
    assert entry["kind"] == "season_research"
    assert entry["rows"] >= 9
    assert entry["path"] == "poe1_3_29_live_validation_queue.json"
