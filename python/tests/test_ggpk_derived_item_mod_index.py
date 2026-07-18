# -*- coding: utf-8 -*-
"""Derived GGPK item/mod export tests."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.build_ggpk_derived_item_mod_index import build_exports  # noqa: E402


def _read_jsonl(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def test_derived_item_mod_export_links_base_tags_affixes_and_mod_stats(tmp_path):
    manifest = build_exports(
        output_dir=tmp_path,
        item_names=["Pneumatic Dagger", "Vaal Regalia"],
        full_mod_index=False,
    )

    assert manifest["counts"]["item_tag_rows"] == 2
    assert manifest["counts"]["item_base_affix_rows"] == 2
    assert manifest["source_tables"]["Stats"] == "missing_in_current_extract"
    assert manifest["mod_index_scope"] == "linked_affix_mods_only"

    affix_rows = _read_jsonl(tmp_path / "poe1_item_base_affix_index.jsonl")
    by_name = {row["base"]["name"]: row for row in affix_rows}

    dagger = by_name["Pneumatic Dagger"]
    assert "weapon" in dagger["base"]["effective_tags"]
    assert "dagger" in dagger["base"]["effective_tags"]
    dagger_suffixes = {mod["name"] for mod in dagger["affixes"]["suffix"]}
    assert "of Celebration" in dagger_suffixes

    body = by_name["Vaal Regalia"]
    assert "body_armour" in body["base"]["effective_tags"]
    body_prefixes = {mod["name"] for mod in body["affixes"]["prefix"]}
    assert "Fecund" in body_prefixes

    with (tmp_path / "poe1_mod_stat_index.json").open("r", encoding="utf-8") as f:
        mod_index = json.load(f)
    assert mod_index["stat_resolution_status"].startswith("raw_stats_table_missing")
    assert any(
        mod["name"] == "of Celebration"
        for mod in mod_index["mods"].values()
    )
    assert any(
        mod["name"] == "Fecund"
        for mod in mod_index["mods"].values()
    )

    with (tmp_path / "poe1_item_base_affix_summary.csv").open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    assert {row["name"] for row in rows} == {"Pneumatic Dagger", "Vaal Regalia"}
    assert all(int(row["prefix_count"]) > 0 for row in rows)
    assert all(int(row["suffix_count"]) > 0 for row in rows)
