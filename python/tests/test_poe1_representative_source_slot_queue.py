# -*- coding: utf-8 -*-
"""Regression checks for the internal representative source-slot queue."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from build_poe1_representative_source_slot_queue import (  # noqa: E402
    OUT_PATH,
    build_representative_source_slot_queue,
)


ROOT = Path(__file__).resolve().parents[2]


def test_source_slot_queue_is_internal_only_and_covers_all_profiles():
    data = build_representative_source_slot_queue()

    assert data["dataset_kind"] == "poe1_representative_source_slot_queue"
    assert data["user_visibility"]["surface"] == "internal_only"
    assert data["user_visibility"]["do_not_render_missing_slots"] is True
    assert data["summary"]["profile_count"] == len(data["by_candidate"])
    assert data["summary"]["slot_count"] == data["summary"]["profile_count"] * 4
    assert len(data["slots"]) == data["summary"]["slot_count"]


def test_source_slot_queue_has_expected_slot_contract_and_queries():
    data = build_representative_source_slot_queue()
    slots_by_candidate: dict[str, set[str]] = {}

    for slot in data["slots"]:
        slots_by_candidate.setdefault(slot["candidate_id"], set()).add(slot["slot_id"])
        assert slot["status"] in {"ready", "evidence_without_url", "missing"}
        assert slot["priority"] in {"high", "medium", "low"}
        if slot["status"] == "ready":
            assert any(item.get("url") for item in slot["matched_evidence"])
            assert slot["suggested_queries"] == []
        else:
            assert slot["suggested_queries"]

    assert all(
        slot_ids == {"guide", "endgame_pob", "leveling_pob", "poe_ninja"}
        for slot_ids in slots_by_candidate.values()
    )


def test_source_slot_queue_merges_manual_pob_records_without_user_exposure():
    data = build_representative_source_slot_queue()
    exsanguinate_slots = {
        slot["slot_id"]: slot
        for slot in data["slots"]
        if slot["candidate_id"] == "3.28_exsanguinate_reap_mines_trickster"
    }

    assert exsanguinate_slots["guide"]["status"] == "ready"
    assert exsanguinate_slots["endgame_pob"]["status"] == "ready"
    assert any(
        item.get("url") == "https://pobb.in/3J6Dm6pkA6-5"
        for item in exsanguinate_slots["endgame_pob"]["matched_evidence"]
    )
    assert data["user_visibility"]["user_facing_rule"].startswith("Show only concrete source URLs")


def test_source_slot_queue_file_is_catalogued_when_written():
    data = build_representative_source_slot_queue()
    OUT_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    catalog_path = ROOT / "data" / "db_catalog.json"
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    entry = catalog["derived"].get("poe1_representative_source_slot_queue.latest.json")

    assert OUT_PATH.exists()
    assert entry["kind"] == "operations"
    assert entry["rows"] == data["summary"]["slot_count"]
    assert entry["path"] == "poe1_representative_source_slot_queue.latest.json"
