# -*- coding: utf-8 -*-
"""Integrity checks for poe.ninja build variant evidence queue."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
QUEUE_PATH = ROOT / "data" / "poe_ninja_build_variant_evidence_queue_v1.json"


def _load_queue() -> dict:
    return json.loads(QUEUE_PATH.read_text(encoding="utf-8"))


def test_evidence_queue_has_policy_shape():
    data = _load_queue()

    assert data["dataset_kind"] == "poe1_poe_ninja_build_variant_evidence_queue"
    assert data["source_policy"]["source_family"] == "poe_ninja_profile"
    assert "high_volume_internal_build_api_scraping" in data["source_policy"]["disallowed_collection_mode"]
    assert data["queue_status"]["promotion_target"] == "variant_evidence_candidate"
    assert data["queue_status"]["sample_rows_collected"] == 0
    assert data["queue_status"]["creator_source_track_count"] == len(data["creator_source_tracks"])


def test_evidence_queue_covers_collection_tracks():
    data = _load_queue()
    tracks = {row["track_id"]: row for row in data["collection_tracks"]}

    assert {
        "mirage_current_trade_baseline",
        "mirage_ssf_access_pressure",
        "mirage_hc_survivability",
        "ruthless_constraint_separate",
        "historical_patch_delta",
        "gauntlet_stress",
    } <= set(tracks)
    assert tracks["mirage_current_trade_baseline"]["source_leagues"] == ["Mirage"]
    assert "SSF Mirage" in tracks["mirage_ssf_access_pressure"]["source_leagues"]
    assert "Ziz Rapture HCSSF Class Gauntlet" in tracks["gauntlet_stress"]["source_leagues"]


def test_evidence_queue_covers_major_archetype_families():
    data = _load_queue()
    targets = {row["target_id"]: row for row in data["archetype_sampling_targets"]}
    families = {row["route_family"] for row in data["archetype_sampling_targets"]}

    assert data["queue_status"]["archetype_target_count"] == len(targets)
    assert {"caster", "ranger", "melee", "minion", "totem", "mine"} <= families
    assert targets["caster_archmage_hierophant"]["leveling_lane"] == "caster_archmage_templar"
    assert targets["ranger_bow_projectile"]["leveling_lane"] == "ranger_attack_bow_projectile"
    assert targets["minion_holy_relic_necro"]["leveling_lane"] == "minion_holy_relic_necro"
    assert targets["minion_poison_carrion_golem"]["leveling_lane"] == "minion_poison_carrion_golem"
    assert targets["totem_wander_hierophant"]["leveling_lane"] == "totem_wander_hierophant"
    assert targets["mine_exsanguinate_trickster"]["leveling_lane"] == "mine_exsanguinate_trickster"
    assert "Exsanguinate Reap Mines" in targets["mine_exsanguinate_trickster"]["main_skill_families"]
    assert targets["mine_exsanguinate_trickster"]["ascendancy_filter"] == ["Trickster"]


def test_evidence_queue_prioritizes_cptn_garbage_for_exsanguinate_mines():
    data = _load_queue()
    targets = {row["target_id"]: row for row in data["archetype_sampling_targets"]}
    mine = targets["mine_exsanguinate_trickster"]

    creators = {row["source_id"]: row for row in mine["preferred_creator_sources"]}
    assert "maxroll_cptn_garbage_exsanguinate_miner" in creators
    assert creators["maxroll_cptn_garbage_exsanguinate_miner"]["collection_priority"] == 1
    assert creators["youtube_fearlessdumb0_exsanguinate_reap_miner"]["collection_priority"] == 1
    assert "youtube_tori_sensei" in creators
    assert creators["youtube_tori_sensei"]["collection_priority"] == 2
    assert "youtube_jorgen_mines" in creators
    assert "youtube_conner_converse_mine_theory" in creators
    assert "odealo_cold_exsanguinate_miner_trickster" in mine["secondary_reference_families"]


def test_evidence_queue_captures_user_creator_source_tracks():
    data = _load_queue()
    tracks = {row["track_id"]: row for row in data["creator_source_tracks"]}

    assert {
        "cws_chieftain",
        "mine_general",
        "experimental_unique_interactions",
        "minion_broad",
        "current_tori_poison_carrion_golem",
        "hardcore_league_start",
        "variety_creator_watch",
        "one_build_siege_ballista",
        "one_build_brand",
        "one_build_cyclone_slayer",
    } <= set(tracks)

    cws_sources = {row["source_id"] for row in tracks["cws_chieftain"]["creator_sources"]}
    mine_sources = {row["source_id"] for row in tracks["mine_general"]["creator_sources"]}
    minion_sources = {row["source_id"] for row in tracks["minion_broad"]["creator_sources"]}

    assert {"youtube_emiracle_cws", "youtube_jorgen_cws_crosscheck"} <= cws_sources
    assert {"youtube_jorgen_mines", "youtube_conner_converse_mine_theory"} <= mine_sources
    assert {"youtube_ghazzytv_minion", "youtube_tori_sensei_minion", "youtube_dconnic_wretched_defiler"} <= minion_sources
    assert tracks["hardcore_league_start"]["creator_sources"][0]["source_id"] == "youtube_zizaran_hcssf"
    assert tracks["experimental_unique_interactions"]["creator_sources"][0]["source_id"] == "youtube_captainlance9_experimental"
    assert tracks["current_tori_poison_carrion_golem"]["promotion_status"] == "needs_current_season_pob"
    assert tracks["one_build_brand"]["promotion_status"] == "local_guide_available"


def test_evidence_queue_prioritizes_tori_sensei_current_poison_carrion_golem_for_minions():
    data = _load_queue()
    targets = {row["target_id"]: row for row in data["archetype_sampling_targets"]}

    srs_creators = {row["source_id"]: row for row in targets["minion_srs_guardian_necro"]["preferred_creator_sources"]}
    golem_creators = {row["source_id"]: row for row in targets["minion_poison_carrion_golem"]["preferred_creator_sources"]}
    spectre_creators = {row["source_id"]: row for row in targets["minion_spectre_necro"]["preferred_creator_sources"]}
    relic_creators = {row["source_id"]: row for row in targets["minion_holy_relic_necro"]["preferred_creator_sources"]}

    assert golem_creators["youtube_tori_sensei_poison_carrion_golem"]["collection_priority"] == 1
    assert golem_creators["youtube_ghazzytv_minion"]["collection_priority"] == 2
    assert srs_creators["youtube_ghazzytv_minion"]["collection_priority"] == 1
    assert srs_creators["youtube_tori_sensei_minion"]["collection_priority"] == 2
    assert relic_creators["youtube_tori_sensei_minion"]["collection_priority"] == 2

    spectre = spectre_creators["youtube_tori_sensei_spectre"]
    assert spectre["collection_priority"] == 1
    seen_pobs = {
        pob_url
        for hit in spectre["known_public_hits"]
        for pob_url in hit["pob_urls_seen_in_search"]
    }
    assert {
        "https://pobb.in/7p4y5j5TYO0n",
        "https://pobb.in/dTHjbYUrUGVT",
        "https://pobb.in/oimmJKVwZB2e",
    } <= seen_pobs
    assert spectre_creators["youtube_dconnic_wretched_defiler"]["collection_priority"] == 1
    assert any(
        hit["video_url"] == "https://www.youtube.com/watch?v=UK5i9eW3l7U"
        for hit in spectre_creators["youtube_dconnic_wretched_defiler"]["known_public_hits"]
    )
    assert spectre_creators["youtube_ghazzytv_spectre"]["collection_priority"] == 2


def test_evidence_queue_requires_variant_fingerprint_fields():
    data = _load_queue()

    assert {
        "damage_engine",
        "defense_engine",
        "core_unique_gate",
        "tree_shape_class",
        "play_pattern",
        "budget_tier",
        "gear_package_id",
        "aura_package_id",
        "cluster_package_id",
        "content_specialization",
    } == set(data["variant_fingerprint_required_fields"])


def test_evidence_queue_is_catalogued():
    catalog = json.loads((ROOT / "data" / "db_catalog.json").read_text(encoding="utf-8"))
    entry = catalog["derived"]["poe_ninja_build_variant_evidence_queue_v1.json"]

    assert entry["kind"] == "operations"
    assert entry["rows"] == 13
    assert entry["path"] == "poe_ninja_build_variant_evidence_queue_v1.json"
