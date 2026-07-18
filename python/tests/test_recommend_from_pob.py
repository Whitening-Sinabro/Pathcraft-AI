# -*- coding: utf-8 -*-
"""CLI-level regression checks for PoB link recommendation runner."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from recommend_from_pob import build_recommendation_result, load_build_data_from_pob_url  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent.parent


def test_load_build_data_from_local_xml_uri():
    sample_xml = ROOT / "data" / "samples" / "recommendation_runner_sample.xml"

    build_data = load_build_data_from_pob_url(sample_xml.as_uri())

    assert build_data["meta"]["class"] == "Ranger"
    assert build_data["meta"]["ascendancy"] == "Deadeye"
    assert build_data["stats"]["dps"] == 4000000
    assert build_data["build_instance"]["identity"]["class"] == "Ranger"
    assert build_data["build_instance"]["gem_state"]["main_skill_group"]["active_gem"] == "Lightning Arrow"
    assert "Main Clear" in build_data["progression_stages"][0]["gem_setups"]
    assert build_data["progression_stages"][0]["passive_tree_options"][0]["active"] is True
    assert build_data["progression_stages"][0]["passive_tree_options"][0]["url"].endswith("/sample")


def test_build_recommendation_result_from_pob_uri():
    sample_xml = ROOT / "data" / "samples" / "recommendation_runner_sample.xml"
    user_state = ROOT / "data" / "user_state.example.json"

    result = build_recommendation_result(
        build_json_paths=[],
        pob_urls=[sample_xml.as_uri()],
        user_state_path=str(user_state),
        coach_json_paths=[],
    )

    recommendation = result["recommendation"]
    profile = result["profiles"][0]

    assert recommendation["selected_plan"] == "A"
    assert recommendation["selected_build_id"] == "3_25_lightning_arrow_deadeye"
    assert profile["identity"]["leveling_skill"] == "Rain of Arrows"
    assert profile["progression"]["passive_plan"][0]["tree_url"].endswith("/sample")
