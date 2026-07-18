# -*- coding: utf-8 -*-
"""Integrity checks for manually attached PoB source links."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCES_PATH = ROOT / "data" / "build_corpus_manual_pob_sources_v1.json"


def _records() -> list[dict]:
    return json.loads(SOURCES_PATH.read_text(encoding="utf-8"))["records"]


def test_manual_pob_sources_include_user_supplied_sanavixx_cyclone_links():
    records = {row["candidate_id"]: row for row in _records()}
    sanavixx = records["3.28_sanavixx_cyclone_of_tumult_slayer"]

    assert sanavixx["source_url"] == "https://sanavixx.com/crafting/"
    assert sanavixx["patch"] == "3.28"
    assert any(
        pob["url"] == "https://pobb.in/RH9MMGmuuro2"
        and pob["role"] == "endgame_cyclone_of_tumult_slayer"
        for pob in sanavixx["pob_urls"]
    )
