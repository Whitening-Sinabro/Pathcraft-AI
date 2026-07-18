# -*- coding: utf-8 -*-
"""Integrity checks for user-supplied Luminary Mercenary/link transcript intake."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
INTAKE_PATH = ROOT / "data" / "poe1_3_29_luminary_merc_link_intake_v1.json"


def _load_intake() -> dict:
    return json.loads(INTAKE_PATH.read_text(encoding="utf-8"))


def test_luminary_intake_is_watchlist_only_and_user_supplied():
    data = _load_intake()

    assert data["dataset_kind"] == "poe1_3_29_luminary_merc_link_intake"
    assert data["patch"] == "3.29"
    assert data["scope_policy"]["poe_scope"] == "poe1_only"
    assert data["scope_policy"]["promotion_status"] == "watchlist_only_prelaunch"
    assert data["source"]["kind"] == "user_supplied_transcript"
    assert data["source"]["local_path"].endswith("luminary.txt")
    assert "Do not reproduce the transcript" in data["source"]["copyright_policy"]


def test_luminary_intake_separates_claims_from_verified_names():
    data = _load_intake()
    claims = {row["claim_id"]: row for row in data["extracted_core_claims"]}
    node_names = {row["transcript_spelling"]: row for row in data["node_name_verification_queue"]}

    assert "permanent_mercenary_model" in claims
    assert "hallowed_monarch_link_target_enabler" in claims
    assert claims["hallowed_monarch_link_target_enabler"]["status"] == "needs_current_item_text_confirmation"
    assert node_names["oath of fieldy"]["verification_status"] == "likely_transcription_error"
    assert node_names["hands of friesia"]["verification_status"] == "likely_transcription_error"


def test_luminary_link_hypotheses_cover_main_shells_without_promoting():
    data = _load_intake()
    hypotheses = {row["hypothesis_id"]: row for row in data["link_skill_hypotheses"]}

    assert {
        "destructive_link_crit_merc",
        "flame_link_life_stack_merc",
        "frigid_bond_fast_merc",
        "soul_link_es_sponge",
        "protective_link_max_block_merc",
        "intuitive_link_trigger_merc",
    } <= set(hypotheses)
    assert all(row["reuse_label"] == "구경만" for row in hypotheses.values())
    assert "Mercenary skill list" in hypotheses["destructive_link_crit_merc"]["risk"]
    assert "uptime" in hypotheses["frigid_bond_fast_merc"]["risk"]


def test_luminary_intake_has_item_and_live_validation_tasks():
    data = _load_intake()
    items = {row["item_name"]: row for row in data["item_watchlist"]}
    tasks = {row["task_id"]: row for row in data["live_validation_tasks"]}

    assert "Hallowed Monarch" in items
    assert "current 3.29 item text" in items["Hallowed Monarch"]["required_checks"]
    assert "Apostate" in items
    assert {
        "luminary_node_truth",
        "mercenary_skill_and_ai_sample",
        "link_skill_runtime_sample",
        "hallowed_monarch_market_and_mechanics",
    } <= set(tasks)
    assert data["practice_judgement"]["player_facing_label"] == "구경만"
    assert any("free player DPS" in row for row in data["practice_judgement"]["do_not_assume"])


def test_luminary_intake_is_catalogued():
    catalog = json.loads((ROOT / "data" / "db_catalog.json").read_text(encoding="utf-8"))
    entry = catalog["derived"]["poe1_3_29_luminary_merc_link_intake_v1.json"]

    assert entry["kind"] == "season_research"
    assert entry["rows"] == 6
    assert entry["path"] == "poe1_3_29_luminary_merc_link_intake_v1.json"
