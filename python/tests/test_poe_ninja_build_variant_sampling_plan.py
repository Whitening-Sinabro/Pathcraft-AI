# -*- coding: utf-8 -*-
"""Integrity checks for poe.ninja build variant sampling contract."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PLAN_PATH = ROOT / "data" / "poe_ninja_build_variant_sampling_plan_v1.json"


def _load_plan() -> dict:
    return json.loads(PLAN_PATH.read_text(encoding="utf-8"))


def test_sampling_plan_has_expected_contract_shape():
    data = _load_plan()

    assert data["dataset_kind"] == "poe1_poe_ninja_build_variant_sampling_plan"
    assert data["source_policy"]["source_family"] == "poe_ninja_profile"
    assert data["source_policy"]["supported_public_api_scope"] == "economy_overview_only"
    assert data["source_policy"]["build_profile_api_status"] == "internal_undocumented_unsupported"
    assert data["source_policy"]["disallowed_collection_mode"] == "high_volume_internal_build_api_scraping"
    assert data["identity_model"]["promotion_target"] == "variant_evidence_candidate"


def test_sampling_plan_tracks_core_variant_dimensions():
    data = _load_plan()
    dimensions = {row["id"]: row for row in data["variant_dimensions"]}

    assert {
        "budget_tier",
        "gear_package_id",
        "defense_engine",
        "aura_package_id",
        "cluster_package_id",
        "tree_shape_class",
        "content_specialization",
        "league_mode_pressure",
        "leveling_route",
    } <= set(dimensions)
    assert dimensions["defense_engine"]["split_behavior"] == "sub_archetype_split_when_core_shell_changes"
    assert "magic_find" in dimensions["content_specialization"]["values"]


def test_sampling_plan_keeps_leveling_confidence_separate_from_endgame_snapshots():
    data = _load_plan()
    contract = data["leveling_confidence_contract"]

    assert {"inferred", "near_confirmed", "confirmed"} == set(contract)
    assert "final endgame snapshot or PoB" in contract["inferred"]["required_evidence"]
    assert "at least three stage PoBs or stage snapshots" in contract["confirmed"]["required_evidence"]
    assert data["sample_record_template"]["leveling_confidence"] == "inferred"


def test_sampling_plan_covers_user_provided_leagues_and_roles():
    data = _load_plan()
    leagues = {row["league"]: row for row in data["league_sampling_plan"]}
    roles = {row["id"] for row in data["sample_roles"]}

    assert {
        "current_meta",
        "ssf_constraint",
        "hc_survivability",
        "ruthless_constraint",
        "historical_patch_delta",
        "gauntlet_stress",
    } <= roles
    assert leagues["Mirage"]["sample_role"] == "current_meta"
    assert leagues["SSF Mirage"]["sample_role"] == "ssf_constraint"
    assert leagues["Hardcore Mirage"]["sample_role"] == "hc_survivability"
    assert leagues["Ruthless Mirage"]["sample_role"] == "ruthless_constraint"
    assert leagues["Keepers"]["sample_role"] == "historical_patch_delta"
    assert leagues["Ziz Rapture HCSSF Class Gauntlet"]["sample_role"] == "gauntlet_stress"
    assert len(leagues) == 29


def test_sampling_plan_requires_mode_tags_for_constraint_samples():
    data = _load_plan()

    for row in data["league_sampling_plan"]:
        assert row["league"]
        assert row["status"] in {"active", "ended"}
        assert row["mode"]
        assert row["sample_role"]
        assert row["priority"] >= 1

        if row["sample_role"] in {"ruthless_constraint", "gauntlet_stress", "hc_survivability"}:
            assert row["mode"] != "trade"


def test_sampling_plan_is_catalogued():
    catalog = json.loads((ROOT / "data" / "db_catalog.json").read_text(encoding="utf-8"))
    entry = catalog["derived"]["poe_ninja_build_variant_sampling_plan_v1.json"]

    assert entry["kind"] == "operations"
    assert entry["rows"] == 29
    assert entry["path"] == "poe_ninja_build_variant_sampling_plan_v1.json"
