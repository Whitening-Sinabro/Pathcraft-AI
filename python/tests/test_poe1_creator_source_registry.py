# -*- coding: utf-8 -*-
"""Integrity checks for POE1 creator source registry."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = ROOT / "data" / "poe1_creator_source_registry_v1.json"


def _load_registry() -> dict:
    return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))


def test_creator_registry_has_expected_shape_and_policy():
    data = _load_registry()

    assert data["dataset_kind"] == "poe1_creator_source_registry"
    assert data["coverage_summary"]["creator_count"] == len(data["creators"])
    assert data["promotion_policy"]["creator_registry_role"] == "source_hunt_priority_only"
    assert "creator_name_only" in data["promotion_policy"]["do_not_promote_from"]


def test_creator_registry_captures_user_seeded_creators():
    data = _load_registry()
    creators = {row["creator_id"]: row for row in data["creators"]}

    assert {
        "cptn_garbage",
        "tori_sensei",
        "dconnic",
        "emiracle",
        "jorgen",
        "conner_converse",
        "captainlance9",
        "ghazzytv",
        "zizaran",
        "goblin_inc_probable",
        "poeguy",
        "zeeboub",
        "sanavixx",
        "fearlessdumb0",
        "exiled_cat",
    } <= set(creators)

    assert "cws_chieftain" in creators["emiracle"]["priority_lanes"]
    assert "mine_exsanguinate_trickster" in creators["cptn_garbage"]["priority_lanes"]
    assert "minion_spectre_necro" in creators["dconnic"]["priority_lanes"]
    assert "minion_general" in creators["ghazzytv"]["priority_lanes"]
    assert "hardcore" in creators["zizaran"]["priority_lanes"]
    assert "minion_poison_carrion_golem_current" in creators["tori_sensei"]["priority_lanes"]
    assert "Poison Carrion Golem" in creators["tori_sensei"]["known_specialties"]
    assert "zero_to_hero_progression" in creators["exiled_cat"]["priority_lanes"]
    assert "From Zero to Hero progressions" in creators["exiled_cat"]["known_specialties"]


def test_creator_registry_marks_one_build_specialists_and_ambiguous_goblin():
    data = _load_registry()
    creators = {row["creator_id"]: row for row in data["creators"]}

    assert creators["poeguy"]["known_specialties"] == ["Siege Ballista Hierophant"]
    assert "Penance Brand" in creators["zeeboub"]["known_specialties"]
    assert "Cyclone Shockwave Slayer" in creators["sanavixx"]["known_specialties"]
    assert {
        "https://sanavixx.com/crafting/",
        "https://pobb.in/RH9MMGmuuro2",
    } <= {source["url"] for source in creators["sanavixx"]["source_urls"]}
    assert "Probable match for user alias Goblin" in creators["goblin_inc_probable"]["collection_notes"]


def test_creator_registry_has_expanded_discovery_creators():
    data = _load_registry()
    creators = {row["creator_id"]: row for row in data["creators"]}

    assert {
        "kankar",
        "anime_princess",
        "llyd",
        "palsteron",
        "fubgun",
        "ruetoo",
        "pohx",
        "mathil",
    } <= set(creators)
    assert "Kankar" in data["coverage_summary"]["expanded_discovery_creators"]
    assert "anime princess" in data["coverage_summary"]["expanded_discovery_creators"]
    assert "LLYD" in data["coverage_summary"]["expanded_discovery_creators"]
    assert "ranger_projectile_venom_gyre" in creators["kankar"]["priority_lanes"]
    assert "caster_archmage_spark" in creators["anime_princess"]["priority_lanes"]
    assert "scion_cyclone_ascendant" in creators["llyd"]["priority_lanes"]


def test_creator_registry_is_catalogued():
    catalog = json.loads((ROOT / "data" / "db_catalog.json").read_text(encoding="utf-8"))
    entry = catalog["derived"]["poe1_creator_source_registry_v1.json"]

    assert entry["kind"] == "operations"
    assert entry["rows"] == 36
    assert entry["path"] == "poe1_creator_source_registry_v1.json"
