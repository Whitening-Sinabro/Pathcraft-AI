# -*- coding: utf-8 -*-
"""Tests for the external-guide-source validator and CWS card projector."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cws_guide_loader import (  # noqa: E402
    GuideSourceError,
    validate_external_guide_source,
    load_cws_card,
)


def _load(name: str) -> dict:
    path = ROOT / "data" / "guide_sources" / name
    return json.loads(path.read_text(encoding="utf-8-sig"))


def test_validator_accepts_cws_guide():
    guide = _load("poe1_cws_chieftain_emiracles_v1.json")
    validate_external_guide_source(guide)  # must not raise


def test_validator_accepts_zeeboub_guide():
    # Proves the validator is schema-shaped, not CWS-shaped.
    guide = _load("poe1_brand_guide_zeeboub_v2.json")
    validate_external_guide_source(guide)  # must not raise


def test_validator_rejects_orphan_pob_link():
    guide = _load("poe1_cws_chieftain_emiracles_v1.json")
    guide["pob_links"].append({"url": "https://pobb.in/ORPHAN", "label": "no role"})
    with pytest.raises(GuideSourceError, match="orphan"):
        validate_external_guide_source(guide)


def test_validator_rejects_dangling_prereq():
    guide = _load("poe1_cws_chieftain_emiracles_v1.json")
    guide["upgrade_nodes"][0]["prereq"] = ["does_not_exist"]
    with pytest.raises(GuideSourceError, match="prereq"):
        validate_external_guide_source(guide)


def test_validator_rejects_dangling_node_phase():
    guide = _load("poe1_cws_chieftain_emiracles_v1.json")
    guide["upgrade_nodes"][0]["phase"] = "no_such_phase"
    with pytest.raises(GuideSourceError, match="phase"):
        validate_external_guide_source(guide)


def test_validator_rejects_patch_locked_key():
    guide = _load("poe1_cws_chieftain_emiracles_v1.json")
    guide["mirage_3_28_notes"] = ["patch baked into a key name"]
    with pytest.raises(GuideSourceError, match="patch-locked"):
        validate_external_guide_source(guide)


def test_projected_card_identity_and_no_default_recommendation():
    card = load_cws_card()
    assert card["candidate_id"] == "3.29_cws_chieftain_emiracle_watch"
    assert card["display_name"] == "Cast When Stunned Chieftain"
    assert card["default_recommendation"] is False
    assert card["player_label"] == "연습해도 됨"


def test_projected_sources_include_pohx_and_emiracle():
    card = load_cws_card()
    source_ids = {s["source_id"] for s in card["sources"]}
    assert {"mobalytics_328_emiracles_cws_chieftain", "emiracle_328_progression_sheet",
            "pohx_rf_wiki", "pohx_rf_chieftain_mobalytics", "pohx_rf_act_walkthrough_video"}.issubset(source_ids)


def test_projected_source_count_matches_sources_length():
    # The old lying counter (source_count 8 vs 5 shipped) must be impossible.
    card = load_cws_card()
    assert card["source_count"] == len(card["sources"])


def test_projected_practice_route_order_and_stage_pobs():
    card = load_cws_card()
    stages = {s["stage"]: s for s in card["practice_route"]}
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
    assert [s["stage"] for s in card["practice_route"]] == expected_order
    assert stages["No Bloodnotch Swap"]["pob_url"] == "https://pobb.in/JK3kksNTM0Fq"
    assert stages["Bloodnotch Initial Swap"]["pob_url"] == "https://pobb.in/PmBU7tMlln4I"
    assert stages["Midgame 1 - Nebulis"]["pob_url"] == "https://pobb.in/TEx-3of-uWyu"
    assert stages["Midgame 4 - Prism Guardian Malevolence Aura"]["pob_url"] == "https://pobb.in/1aIufgwcXUTx"
    assert stages["Midgame 5 - Unearth/DD"]["pob_url"] == "https://pobb.in/AJfx7FUUUGzv"
    assert stages["Ultra Aspirational - Hybrid Mageblood/Imbue"]["pob_url"] == "https://pobb.in/GUKwCsAq5x-g"


def test_projected_leveling_stage_has_pohx_source_links():
    card = load_cws_card()
    stages = {s["stage"]: s for s in card["practice_route"]}
    leveling = stages["레벨링 / Campaign"]
    assert leveling["pob_url"] is None
    ids = {s["source_id"] for s in leveling["source_links"]}
    assert {"pohx_rf_wiki", "pohx_rf_chieftain_mobalytics", "pohx_rf_act_walkthrough_video"}.issubset(ids)
    assert "78" in " ".join(leveling["checks"] + [leveling["source_note"]])
    assert "87+" in " ".join(leveling["checks"] + [leveling["source_note"]])
    assert "Righteous Fire" in leveling["skill_setups"]
    assert any("Pohx RF" in s for s in leveling["skill_setups"])


def test_projected_anytime_upgrades_are_order_free():
    card = load_cws_card()
    anytime_ids = {u["node_id"] for u in card["anytime_upgrades"]}
    assert {"defiance_of_destiny", "watchers_eye", "good_jewels", "ignite_tattoos"}.issubset(anytime_ids)
    # anytime upgrades must not appear in the ordered practice_route
    stage_names = {s["stage"] for s in card["practice_route"]}
    assert not any("Defiance of Destiny" == s for s in stage_names)


def test_projected_no_orphan_pob_urls():
    card = load_cws_card()
    stage_pobs = {s["pob_url"] for s in card["practice_route"] if s.get("pob_url")}
    # Every pob_url advertised at card level maps to a stage or an alt role; none float unused.
    for url in card["pob_urls"]:
        assert url in stage_pobs or url in card.get("alt_pob_urls", []), f"orphan pob_url: {url}"


def test_projected_guardrails_split_into_red_flags_and_promotion_checks():
    card = load_cws_card()
    assert any("Brine King" in x for x in card["red_flags"])
    assert any("Life Recoup" in x for x in card["red_flags"])
    assert any("3.29" in x for x in card["promotion_checks"])


def test_projected_map_mods_and_knowledge_cards():
    card = load_cws_card()
    avoid = {g["severity"]: g for g in card["map_mods_to_avoid"]}
    assert "less recovery rate of Life and ES" in avoid["extremely_bad"]["mods"]
    assert "gain as random extra element" in avoid["t17_worst"]["mods"]
    assert any("Simulacrum" in x for x in card["playstyle_summary"])
    assert any("87+" in x for x in card["mirage_notes"])
    assert any("Defiance of Destiny" in x for x in card["upgrade_notes"])
    assert any("DD imbue" in x for x in card["upgrade_notes"])
