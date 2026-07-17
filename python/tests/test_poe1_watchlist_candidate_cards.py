# -*- coding: utf-8 -*-
"""Regression tests for player-facing watchlist candidate cards."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from build_poe1_watchlist_candidate_cards import build_watchlist_candidate_cards  # noqa: E402


def _cards_by_id(data: dict) -> dict:
    return {card["candidate_id"]: card for card in data["cards"]}


def test_watchlist_cards_include_user_considered_build_lanes():
    data = build_watchlist_candidate_cards()
    cards = _cards_by_id(data)

    assert "3.28_exsanguinate_reap_mines_trickster" in cards
    assert "3.28_poison_carrion_golem_witch" in cards
    assert "3.28_ignite_slamentalist_elementalist" in cards
    assert "3.28_righteous_cold_dot_autobomber_elementalist" in cards
    assert "3.29_cws_chieftain_emiracle_watch" in cards
    assert "3.29_luminary_destructive_link_crit_merc" in cards

    assert cards["3.28_exsanguinate_reap_mines_trickster"]["player_label"] == "연습해도 됨"
    assert cards["3.28_poison_carrion_golem_witch"]["player_label"] == "연습해도 됨"
    assert cards["3.29_cws_chieftain_emiracle_watch"]["player_label"] == "연습해도 됨"


def test_cws_watchlist_card_uses_emiracle_mobalytics_and_spreadsheet_sources():
    data = build_watchlist_candidate_cards()
    cws = _cards_by_id(data)["3.29_cws_chieftain_emiracle_watch"]
    source_ids = {source["source_id"] for source in cws["sources"]}

    assert "mobalytics_328_emiracles_cws_chieftain" in source_ids
    assert "emiracle_328_progression_sheet" in source_ids
    assert "pohx_rf_wiki" in source_ids
    assert "pohx_rf_chieftain_mobalytics" in source_ids
    assert "pohx_rf_act_walkthrough_video" in source_ids
    assert "https://mobalytics.gg/poe/builds/cws-chieftain-3-28" in {
        source.get("url") for source in cws["sources"]
    }
    assert "https://pobb.in/9212xFSq-G5F" in cws["additional_pob_urls"]
    assert "https://pobb.in/ehTCpUVi7R-r" in cws["additional_pob_urls"]
    assert "https://pobb.in/AALRvyYQX1m3" in cws["pob_urls"]
    assert "https://pobb.in/GUKwCsAq5x-g" in cws["pob_urls"]
    assert cws["default_recommendation"] is False


def test_cws_watchlist_card_exposes_leveling_and_transition_route():
    data = build_watchlist_candidate_cards()
    cws = _cards_by_id(data)["3.29_cws_chieftain_emiracle_watch"]
    stages = {stage["stage"]: stage for stage in cws["practice_route"]}

    expected_order = [
        "레벨링 / Campaign",
        "No Bloodnotch Swap",
        "Bloodnotch Initial Swap",
        "Midgame 1 - Nebulis",
        "Midgame 2 - Initial Large Cluster",
        "Midgame 3 - Triple Large Cluster",
        "Midgame 4 - Prism Guardian Malevolence Aura",
        "Midgame 5 - Unearth/DD",
        "Aspirational",
        "Ultra Aspirational - Hybrid Mageblood/Imbue",
    ]
    assert [stage["stage"] for stage in cws["practice_route"]] == expected_order
    assert stages["No Bloodnotch Swap"]["pob_url"] == "https://pobb.in/JK3kksNTM0Fq"
    assert stages["Bloodnotch Initial Swap"]["pob_url"] == "https://pobb.in/PmBU7tMlln4I"
    assert stages["Midgame 1 - Nebulis"]["pob_url"] == "https://pobb.in/TEx-3of-uWyu"
    assert stages["Midgame 4 - Prism Guardian Malevolence Aura"]["pob_url"] == "https://pobb.in/1aIufgwcXUTx"
    assert stages["Midgame 5 - Unearth/DD"]["pob_url"] == "https://pobb.in/AJfx7FUUUGzv"
    assert stages["Ultra Aspirational - Hybrid Mageblood/Imbue"]["pob_url"] == "https://pobb.in/GUKwCsAq5x-g"
    leveling = stages["레벨링 / Campaign"]
    leveling_source_ids = {source["source_id"] for source in leveling["source_links"]}
    assert leveling["pob_url"] is None
    assert {"pohx_rf_wiki", "pohx_rf_chieftain_mobalytics", "pohx_rf_act_walkthrough_video"}.issubset(leveling_source_ids)
    assert "78" in " ".join(leveling["checks"] + [leveling["source_note"]])
    assert "87+" in " ".join(leveling["checks"] + [leveling["source_note"]])
    assert "Righteous Fire" in stages["레벨링 / Campaign"]["skill_setups"]
    assert any("Pohx RF" in skill for skill in stages["레벨링 / Campaign"]["skill_setups"])
    assert any(
        "Punishment" in skill and "Cast when Stunned" in skill
        for skill in stages["No Bloodnotch Swap"]["skill_setups"]
    )
    assert any("Brine King" in item for item in cws["red_flags"])
    assert any("Life Recoup" in item for item in cws["red_flags"])
    assert any("3.29" in item for item in cws["promotion_checks"])


def test_cws_watchlist_card_captures_emiracle_xlsx_operational_rules():
    data = build_watchlist_candidate_cards()
    cws = _cards_by_id(data)["3.29_cws_chieftain_emiracle_watch"]

    assert any("Simulacrum" in item for item in cws["playstyle_summary"])
    assert any("87+" in item for item in cws["mirage_notes"])
    assert any("Bloodnotch nerf" in item for item in cws["mirage_notes"])
    assert any("Lori's Lantern" in item for item in cws["mirage_notes"])
    assert any("400k" in item and "Simulacrum" in item for item in cws["mirage_notes"])
    assert any("Defiance of Destiny" in item for item in cws["upgrade_notes"])
    assert any("DD imbue" in item for item in cws["upgrade_notes"])

    avoid_groups = {group["severity"]: group for group in cws["map_mods_to_avoid"]}
    assert "extremely_bad" in avoid_groups
    assert "less recovery rate of Life and ES" in avoid_groups["extremely_bad"]["mods"]
    assert "gain as random extra element" in avoid_groups["t17_worst"]["mods"]

    bloodnotch_stage = next(
        stage for stage in cws["practice_route"]
        if stage["stage"] == "Bloodnotch Initial Swap"
    )
    assert any("Life Recoup over 3 seconds mastery" in check for check in bloodnotch_stage["checks"])
    assert any("Firestorm of Pelting" in skill for skill in bloodnotch_stage["skill_setups"])
    assert any("Vaal Breach" in item and "Defiance" in item for item in cws["red_flags"])

    unearth_stage = next(
        stage for stage in cws["practice_route"]
        if stage["stage"] == "Midgame 5 - Unearth/DD"
    )
    assert any("Detonate Dead, not Detonate Dead of Scavenging" in skill for skill in unearth_stage["skill_setups"])


def test_watchlist_cards_do_not_expose_internal_backend_guard_keys():
    data = build_watchlist_candidate_cards()

    forbidden = {
        "backend_guard",
        "backend_guard_summary",
        "player_facing_default",
        "recommendation_visibility",
        "forward_guard_note",
    }
    for card in data["cards"]:
        assert forbidden.isdisjoint(card)
