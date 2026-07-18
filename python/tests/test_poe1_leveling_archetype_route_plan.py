# -*- coding: utf-8 -*-
"""Integrity checks for POE1 leveling archetype route plan."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PLAN_PATH = ROOT / "data" / "poe1_leveling_archetype_route_plan_v1.json"


def _load_plan() -> dict:
    return json.loads(PLAN_PATH.read_text(encoding="utf-8"))


def test_leveling_route_plan_has_expected_shape():
    data = _load_plan()

    assert data["dataset_kind"] == "poe1_leveling_archetype_route_plan"
    assert data["coverage_summary"]["route_count"] == len(data["routes"])
    assert data["coverage_summary"]["confirmed_route_count"] >= 8
    assert data["coverage_summary"]["near_confirmed_route_count"] >= 5
    assert "poe_ninja_endgame_snapshot_only" in data["selection_policy"]["do_not_confirm_from"]


def test_leveling_route_plan_covers_major_families():
    data = _load_plan()
    families = {row["route_family"] for row in data["routes"]}
    routes = {row["route_id"]: row for row in data["routes"]}

    assert {"caster", "ranger", "melee", "minion", "totem", "mine"} <= families
    assert routes["caster_archmage_templar"]["leveling_confidence"] == "confirmed"
    assert routes["ranger_attack_bow_projectile"]["leveling_confidence"] == "near_confirmed"
    assert routes["melee_strike_duelist"]["leveling_confidence"] == "confirmed"
    assert routes["minion_holy_relic_necro"]["preferred_patch_band"] == "3.28"
    assert routes["minion_poison_carrion_golem"]["preferred_patch_band"] == "3.28-current"
    assert routes["totem_wander_hierophant"]["preferred_patch_band"] == "3.28"
    assert routes["mine_exsanguinate_trickster"]["leveling_confidence"] == "near_confirmed"
    assert routes["mine_exsanguinate_trickster"]["preferred_patch_band"] == "3.24-3.27"


def test_confirmed_leveling_routes_have_stage_markers():
    data = _load_plan()

    for route in data["routes"]:
        if route["leveling_confidence"] != "confirmed":
            continue

        assert route["primary_sources"], route["route_id"]
        assert any(source.get("stage_markers") for source in route["primary_sources"]), route["route_id"]
        assert all(source.get("pob_url") for source in route["primary_sources"]), route["route_id"]


def test_recent_routes_are_used_where_available_and_gaps_are_explicit():
    data = _load_plan()
    routes = {row["route_id"]: row for row in data["routes"]}

    recent_confirmed = [
        "caster_archmage_templar",
        "minion_srs_templar_witch",
        "minion_holy_relic_necro",
        "totem_wander_hierophant",
    ]
    for route_id in recent_confirmed:
        route = routes[route_id]
        assert route["leveling_confidence"] == "confirmed"
        assert any("3.27" in source["candidate_id"] or "3.28" in source["candidate_id"] for source in route["primary_sources"])

    assert routes["ranger_attack_bow_projectile"]["promotion_status"] == "needs_recent_bow_attack_stage_pob"
    assert routes["totem_fire_hierophant"]["promotion_status"] == "needs_fire_totem_stage_pob"
    assert routes["mine_exsanguinate_trickster"]["promotion_status"] == "needs_cptn_garbage_maxroll_pob_ingest"


def test_mine_route_is_exsanguinate_trickster_not_hexblast():
    data = _load_plan()
    routes = {row["route_id"]: row for row in data["routes"]}
    mine = routes["mine_exsanguinate_trickster"]

    assert "Exsanguinate Mine Trickster" in mine["applies_to"]
    assert "Exsanguinate Reap Mines Trickster" in mine["applies_to"]
    assert all("Hexblast" not in applies_to for applies_to in mine["applies_to"])
    assert any(source.get("source_id") == "maxroll_cptn_garbage_exsanguinate_miner" for source in mine["primary_sources"])
    assert any(source.get("source_id") == "youtube_tori_sensei" for source in mine["primary_sources"])
    assert any(source.get("source_id") == "odealo_cold_exsanguinate_miner_3_27" for source in mine["primary_sources"])


def test_minion_routes_track_tori_sensei_sources_without_overpromoting():
    data = _load_plan()
    routes = {row["route_id"]: row for row in data["routes"]}
    srs = routes["minion_srs_templar_witch"]
    golem = routes["minion_poison_carrion_golem"]
    spectre = routes["minion_spectre_necro"]
    relic = routes["minion_holy_relic_necro"]

    assert srs["leveling_confidence"] == "confirmed"
    assert any("Tori-sensei" in note for note in srs["route_notes"])
    assert golem["leveling_confidence"] == "near_confirmed"
    assert golem["promotion_status"] == "needs_current_tori_sensei_poison_carrion_golem_pob"
    assert any(source.get("source_id") == "youtube_tori_sensei_poison_carrion_golem" for source in golem["primary_sources"])
    assert any(source.get("pob_url") == "https://pobb.in/Gji0uiu1Aoog" for source in golem["primary_sources"])
    assert spectre["promotion_status"] == "needs_spectre_creator_pob_ingest"
    assert any(source.get("source_id") == "youtube_tori_sensei_spectre" for source in spectre["primary_sources"])
    assert any(source.get("source_id") == "youtube_dconnic_wretched_defiler" for source in spectre["primary_sources"])
    assert any(source.get("source_id") == "youtube_ghazzytv_minion" for source in spectre["primary_sources"])
    assert any("Tori-sensei" in note for note in relic["route_notes"])


def test_leveling_route_plan_is_catalogued():
    catalog = json.loads((ROOT / "data" / "db_catalog.json").read_text(encoding="utf-8"))
    entry = catalog["derived"]["poe1_leveling_archetype_route_plan_v1.json"]

    assert entry["kind"] == "operations"
    assert entry["rows"] == 13
    assert entry["path"] == "poe1_leveling_archetype_route_plan_v1.json"
