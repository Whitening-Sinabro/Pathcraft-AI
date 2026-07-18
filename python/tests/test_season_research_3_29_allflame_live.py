# -*- coding: utf-8 -*-
"""3.29 live-reveal season research integrity tests."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "python"))

from build_coach import build_season_research_context  # noqa: E402

LIVE_RESEARCH_PATH = ROOT / "data" / "poe1_season_research_3_29_allflame_live.json"


def _load_live_research() -> dict:
    return json.loads(LIVE_RESEARCH_PATH.read_text(encoding="utf-8"))


def test_329_allflame_live_research_is_patch_notes_confirmed_watchlist():
    data = _load_live_research()

    assert data["dataset_kind"] == "poe1_season_research"
    assert data["league"]["patch"] == "3.29"
    assert data["league"]["name"] == "Curse of the Allflame"
    assert data["league"]["status"] == "watchlist"
    assert data["league"]["research_status"] == "patch_notes_confirmed"
    assert data["scope"]["class_name"] == "Scion"
    assert data["scope"]["ascendancy"] == "Scion multi-ascendancy"

    source_ids = {source["id"] for source in data["sources"]}
    assert {
        "official_patch_notes_3_29",
        "official_allflame_page",
        "official_launch_announcement_3_29",
        "official_reliquarian_3_29",
        "local_reliquarian_research_pack",
        "poewiki_scion_2026_07_16",
        "poewiki_luminary_2026_07_16",
        "poewiki_reliquarian_2026_07_15",
        "poewiki_mercenary_2026_07_16",
        "poewiki_ascendancy_class_2026_07_16",
    } <= source_ids


def test_329_scion_three_ascendancies_keep_reliquarian_and_luminary_separate():
    data = _load_live_research()

    official_by_id = {row["id"]: row for row in data["lenses"]["official_node_lens"]}
    assert "scion_329_ascendancy_matrix" in official_by_id
    assert "poewiki_scion_ascendancy_crosscheck" in official_by_id
    poewiki = official_by_id["poewiki_scion_ascendancy_crosscheck"]
    assert poewiki["available_scion_ascendancies"] == [
        "Ascendant",
        "Reliquarian",
        "Luminary",
    ]
    assert poewiki["wiki_revision_ids"]["Scion"] == 1673602
    assert poewiki["wiki_revision_ids"]["Luminary"] == 1673612
    assert "noble_blood" in poewiki["mapped_effect_tags"]
    scion_matrix = official_by_id["scion_329_ascendancy_matrix"]
    assert scion_matrix["available_scion_ascendancies"] == [
        "Ascendant",
        "Reliquarian",
        "Luminary",
    ]
    assert "reliquarian" in scion_matrix["mapped_effect_tags"]
    assert "luminary" in scion_matrix["mapped_effect_tags"]
    assert "mercenary" in scion_matrix["mapped_effect_tags"]
    assert any("permanently hire" in fact.lower() for fact in scion_matrix["patch_notes_facts"])

    uncertainty_ids = {row["id"] for row in data["lenses"]["uncertainty_lens"]}
    assert "scion_three_ascendancies_need_branching" in uncertainty_ids
    assert "poewiki_category_index_lag" in uncertainty_ids

    branches = {row["branch_id"]: row for row in data["lenses"]["candidate_branch_lens"]}
    assert branches["hot_autobomber_reliquarian_watchlist"]["rank"] == 3
    assert branches["static_strike_reliquarian_watchlist"]["rank"] == 4
    assert "separate Scion Reliquarian watchlist" in branches["hot_autobomber_reliquarian_watchlist"]["verdict"]


def test_329_socket_lens_uses_official_equipment_socket_scope():
    data = _load_live_research()

    official_by_id = {row["id"]: row for row in data["lenses"]["official_node_lens"]}
    socket_lens = official_by_id["gem_socket_changes"]
    facts = " ".join(socket_lens["patch_notes_facts"]).lower()
    rule_by_id = {row["id"]: row for row in data["lenses"]["uncertainty_lens"]}

    assert "equipment socket" in facts
    assert "white" in facts
    assert "chromatic" in facts
    assert "recursive support" not in facts
    assert rule_by_id["socket_change_scope"]["rule"].endswith(
        "not a recursive support-gem socket system."
    )


def test_329_blight_of_contagion_is_live_retest_not_confirmed_solution():
    data = _load_live_research()

    branches = {row["branch_id"]: row for row in data["lenses"]["candidate_branch_lens"]}
    assert branches["blight_of_contagion_luminary_retest"]["rank"] == 1
    assert "Pact of Ghorr" in " ".join(branches["blight_of_contagion_luminary_retest"]["next_verification"])
    assert "Pact of Lycia" in " ".join(branches["blight_of_contagion_luminary_retest"]["next_verification"])
    assert "Not solved" in branches["blight_of_contagion_luminary_retest"]["verdict"]

    coach_rules = "\n".join(data["coach_rules"])
    assert "not as a confirmed direct skill buff" in coach_rules


def test_329_live_known_skills_point_at_local_active_skills_when_available():
    data = _load_live_research()
    active_skills = json.loads((ROOT / "data" / "game_data" / "ActiveSkills.json").read_text(encoding="utf-8"))
    active_ids = {row["Id"] for row in active_skills}

    for row in data["lenses"]["skill_fact_lens"]:
        active_id = row["local_active_skill_id"]
        if active_id == "post_patch_extract_required":
            assert row["supportability_override"]["state"] == "official_patch_notes_confirmed_local_ggpk_missing"
        else:
            assert active_id in active_ids, row["canonical_skill"]

    blight = next(row for row in data["lenses"]["skill_fact_lens"] if row["canonical_skill"] == "Blight of Contagion")
    assert blight["damage_flags"]["dot"] is True
    assert "pact_of_ghorr_candidate" in blight["semantic_tags"]
    assert "pact_of_lycia_candidate" in blight["semantic_tags"]


def test_build_coach_uses_allflame_live_context_for_scion_luminary():
    build = {
        "meta": {
            "build_name": "Scion Luminary Blight test",
            "class": "Scion",
            "ascendancy": "Luminary",
        },
        "progression_stages": [{
            "gem_setups": {
                "Blight of Contagion": {
                    "links": "Blight of Contagion - Void Manipulation Support"
                }
            }
        }],
    }

    context = build_season_research_context(build)

    assert context["league"]["research_status"] == "patch_notes_confirmed"
    assert context["scope"]["ascendancy"] == "Scion multi-ascendancy"
    assert context["match"]["scoped_character"] is True
    assert "blight_of_contagion_luminary_retest" in context["match"]["selected_branch_ids"]
    assert "community_build_shell_lens" not in context
    assert "Scion multi-ascendancy" in context["rule"]
    assert "patch_notes_confirmed" in context["rule"]

    official_ids = {row["id"] for row in context["official_node_lens"]}
    assert "scion_329_ascendancy_matrix" in official_ids
