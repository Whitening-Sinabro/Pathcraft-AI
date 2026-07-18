# -*- coding: utf-8 -*-
"""Regression checks for build_build_profile CLI helper."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from build_build_profile import build_profile_result  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent.parent


def test_build_profile_result_from_local_xml_uri():
    sample_xml = ROOT / "data" / "samples" / "recommendation_runner_sample.xml"

    profile = build_profile_result(
        build_json_path=None,
        pob_url=sample_xml.as_uri(),
        patch="3.25",
        representative_status="confirmed",
    )

    assert profile["dataset_kind"] == "poe1_build_profile"
    assert profile["schema_version"] == "1.1.0"
    assert profile["identity"]["main_skill"] == "Lightning Arrow"
    assert profile["identity"]["leveling_skill"] == "Rain of Arrows"
    assert profile["progression"]["passive_plan"][0]["tree_url"].endswith("/sample")
    assert profile["confidence"]["representative_build_status"] == "confirmed"
