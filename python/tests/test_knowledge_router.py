# -*- coding: utf-8 -*-
"""Knowledge router entity classification and source selection."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "python"))

from knowledge_router import build_context_pack, classify_intents, extract_entities  # noqa: E402


def test_router_classifies_query_and_routes_exact_sources():
    pack = build_context_pack(
        "Scion Reliquarian Arc Storm Secret price fossil farming",
        game="poe1",
    )

    assert pack["dataset_kind"] == "pathcraft_knowledge_context_pack"
    assert "economy_check" in pack["intents"]
    assert "farming_strategy" in pack["intents"]
    assert "scion_329" in pack["intents"]
    assert "Arc" in pack["entities"]["gems"]
    assert "Storm Secret" in pack["entities"]["items"]
    assert "reliquarian" in pack["entities"]["season_terms"]
    assert "fossil" in pack["entities"]["farming_terms"]

    source_ids = {source["id"] for source in pack["selected_sources"]}
    assert {
        "ggpk_gems",
        "ggpk_items_mods",
        "patch_delta",
        "patch_overlay_policy",
        "season_research",
        "atlas_farming",
        "poe_ninja_economy",
        "live_validation_queue",
    }.issubset(source_ids)
    assert "ggpk_gems" in pack["exact_sources"]
    assert "ggpk_items_mods" in pack["exact_sources"]
    assert "patch_delta" in pack["vector_candidates"]


def test_router_uses_build_data_when_query_is_empty():
    build = {
        "meta": {
            "class": "Scion",
            "ascendancy": "Reliquarian",
            "build_name": "Arc Autobomber",
        },
        "items": [
            {"name": "Storm Secret", "rarity": "Unique"},
        ],
        "progression_stages": [
            {
                "gem_setups": {
                    "Arc": {"links": "Arc - Inspiration Support - Coursing Currents Support"}
                }
            }
        ],
    }

    intents = classify_intents(build_data=build)
    entities = extract_entities(build_data=build)
    pack = build_context_pack(build_data=build)

    assert "build_analysis" in intents
    assert "scion_329" in intents
    assert any(row["name"] == "Arc" for row in entities["matched_gems"])
    assert any(row["name"] == "Storm Secret" for row in entities["matched_items"])
    assert pack["patch_entry_sample"]
    assert any(entry["entity"] == "Arc" for entry in pack["patch_entry_sample"])
    item_context = pack["item_mod_context"]
    assert item_context["counts"]["unique_locked"] == 1
    storm_secret = item_context["items"][0]
    assert storm_secret["name"] == "Storm Secret"
    assert storm_secret["ggpk_mod_context"]["candidate_scope"] == "unique_item_base_reference_only"
    assert storm_secret["ggpk_mod_context"]["join_status"] == "unique_item_no_rare_affix_slots"
    assert storm_secret["ggpk_mod_context"]["affix_candidate_counts"] is None


def test_router_separates_vector_candidates_from_exact_numeric_sources():
    pack = build_context_pack("Reddit YouTube guide for new player Blight farming", game="poe1")

    source_ids = {source["id"] for source in pack["selected_sources"]}
    assert "community_probe" in source_ids
    assert "new_player_friction" in source_ids
    assert "atlas_farming" in source_ids
    assert "community_probe" in pack["vector_candidates"]
    assert "ggpk_items_mods" not in pack["vector_candidates"]
    assert "Use exact/GGPK sources" in pack["evidence_rule"]


def test_router_builds_current_item_mod_context_for_rare_base():
    build = {
        "items": [
            {
                "name": "Hypnotic Veil",
                "rarity": "Rare",
                "base_type": "Vaal Regalia",
                "mods": [
                    "+120 to maximum Life",
                    "+45% to Fire Resistance",
                    "+12% chance to Suppress Spell Damage",
                ],
            }
        ]
    }

    pack = build_context_pack(build_data=build)
    context = pack["item_mod_context"]
    item = context["items"][0]
    totals = item["current_mod_summary"]["numeric_totals"]

    assert context["counts"]["with_current_mod_lines"] == 1
    assert item["lookup_name"] == "Vaal Regalia"
    assert item["mod_source"] == "pob_item_mod_lines"
    assert totals["maximum_life"] == 120
    assert totals["fire_resistance"] == 45
    assert totals["spell_suppression"] == 12
    assert item["ggpk_mod_context"]["join_status"] == "resolved"
    assert item["ggpk_mod_context"]["affix_candidate_counts"]["prefix"] > 0
    assert item["ggpk_mod_context"]["affix_candidate_counts"]["suffix"] > 0
    assert item["ggpk_mod_context"]["candidate_samples"]["prefix"]
    assert item["ggpk_mod_context"]["candidate_samples"]["suffix"]


def test_router_builds_affix_context_for_base_query():
    pack = build_context_pack("Pneumatic Dagger item mods", game="poe1")
    context = pack["item_mod_context"]
    item = next(row for row in context["items"] if row["name"] == "Pneumatic Dagger")

    assert item["source"] == "query_exact_item_match"
    assert item["mod_line_count"] == 0
    assert item["ggpk_mod_context"]["candidate_scope"] == "rare_magic_base_or_base_query"
    assert item["ggpk_mod_context"]["join_status"] == "resolved"
    assert item["ggpk_mod_context"]["affix_candidate_counts"]["suffix"] > 0


def test_router_attaches_structured_brand_guide_context():
    pack = build_context_pack(
        "Penance Brand of Dissipation Inquisitor swap requirements pob",
        game="poe1",
    )

    source_ids = {source["id"] for source in pack["selected_sources"]}
    guide = pack["brand_guide_context"]
    card_ids = {card["card_id"] for card in guide["knowledge_cards"]}
    pob_roles = {pob["role"] for pob in guide["pob_links"]}

    assert "brand_guide_zeeboub" in source_ids
    assert "brand_guide_zeeboub" in pack["vector_candidates"]
    assert "penance brand" in pack["entities"]["brand_guide_terms"]
    assert guide["source_id"] == "zeeboub_brand_guide_v2"
    assert guide["link_summary"]["pob_count"] >= 20
    assert "swap_requirements" in card_ids
    assert "transition_armageddon_to_penance" in pob_roles
