# -*- coding: utf-8 -*-
"""Whole-patch 3.29 review DB integrity tests."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "python"))

from build_coach import load_poe1_3_29_global_review_knowledge  # noqa: E402

GLOBAL_REVIEW_PATH = ROOT / "data" / "poe1_3_29_global_review.json"


def _load_global_review() -> dict:
    return json.loads(GLOBAL_REVIEW_PATH.read_text(encoding="utf-8"))


def test_global_review_has_whole_poe_coverage_axes():
    data = _load_global_review()

    assert data["dataset_kind"] == "poe1_3_29_global_review"
    assert data["patch"] == "3.29"
    assert data["league"] == "Curse of the Allflame"
    assert data["status"] == "patch_notes_and_wiki_crosschecked_pre_launch"

    axes = set(data["lenses"]["coverage_lens"]["required_axes"])
    assert {
        "league_loop",
        "ascendancy_and_bloodline",
        "mercenary_system",
        "skill_and_support_gems",
        "socket_and_crafting",
        "atlas_and_endgame",
        "economy_and_rewards",
        "build_archetype_impact",
        "new_player_friction",
    } <= axes

    source_ids = {source["id"] for source in data["sources"]}
    assert {
        "official_329_patch_notes",
        "official_allflame_page",
        "official_reliquarian_329",
        "poewiki_scion",
        "poewiki_luminary",
        "poewiki_reliquarian",
        "poewiki_mercenary",
        "poewiki_chart",
        "poewiki_ducat",
    } <= source_ids


def test_build_coach_loads_global_review_context():
    data = load_poe1_3_29_global_review_knowledge()

    assert data["dataset_kind"] == "poe1_3_29_global_review"
    assert data["lenses"]["coverage_lens"]["coverage_state"] == "all_axes_have_patch_notes_or_wiki_evidence"
    assert "unresolved_lens" in data["lenses"]


def test_global_review_keeps_scion_and_mercenary_models_separate():
    data = _load_global_review()
    ascendancy = data["lenses"]["ascendancy_and_bloodline_lens"]
    mercenary = data["lenses"]["mercenary_system_lens"]

    assert any("Ascendant, Reliquarian, and Luminary" in fact for fact in ascendancy["facts"])
    assert any("Reliquarian is item-effect research" in line for line in ascendancy["poe_wide_implications"])
    assert any("Luminary can permanently hire up to 3 Mercenaries" in fact for fact in mercenary["facts"])
    assert any("separate Mercenary state" in line for line in mercenary["poe_wide_implications"])


def test_global_review_tracks_socket_and_economy_changes():
    data = _load_global_review()
    socket = data["lenses"]["socket_and_crafting_lens"]
    economy = data["lenses"]["economy_and_rewards_lens"]

    socket_facts = " ".join(socket["facts"])
    assert "any equipment socket" in socket_facts
    assert "+10% quality" in socket_facts
    assert "white by default" in socket_facts
    assert "Chromatic Orbs are rarer" in socket_facts

    economy_facts = " ".join(economy["facts"])
    assert "Ducats" in economy_facts
    assert "Trarthan Scarabs" in economy_facts
    assert "Legion Timeless Splinter" in economy_facts


def test_global_review_maps_build_archetype_risks_without_promoting_meta():
    data = _load_global_review()
    archetypes = {row["archetype"]: row for row in data["lenses"]["build_archetype_impact_lens"]}

    assert "chaos_dot_or_channeling" in archetypes
    assert "Pact of Ghorr" in archetypes["chaos_dot_or_channeling"]["new_hooks"]
    assert "Pact of Lycia" in archetypes["chaos_dot_or_channeling"]["new_hooks"]
    assert "scion_mercenary" in archetypes
    assert "Luminary" in archetypes["scion_mercenary"]["new_hooks"]
    assert "scion_reliquarian" in archetypes
    assert "separate from Luminary" in archetypes["scion_reliquarian"]["risk"]

    non_goal = data["lenses"]["coverage_lens"]["non_goal"]
    assert "not a meta tier list" in non_goal
    assert "does not mark any build solved" in non_goal


def test_global_review_unresolved_lens_requires_launch_and_pob_data():
    data = _load_global_review()
    unresolved = {row["id"]: row for row in data["lenses"]["unresolved_lens"]}

    assert unresolved["pre_launch_data_gap"]["severity"] == "high"
    assert unresolved["post_329_ggpk_required"]["severity"] == "high"
    assert unresolved["pob_required"]["severity"] == "high"
    assert "PoB" in unresolved["pob_required"]["rule"]

    coach_rules = "\n".join(data["coach_rules"])
    assert "whole-patch context map" in coach_rules
    assert "not as a build tier list" in coach_rules
