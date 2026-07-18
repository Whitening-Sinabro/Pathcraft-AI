# -*- coding: utf-8 -*-
"""Integrity checks for the global POE1 creator/source target map."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TARGETS_PATH = ROOT / "data" / "poe1_global_creator_source_targets_v1.json"


def _load_targets() -> dict:
    return json.loads(TARGETS_PATH.read_text(encoding="utf-8"))


def test_global_creator_targets_shape_and_scope():
    data = _load_targets()

    assert data["dataset_kind"] == "poe1_global_creator_source_targets"
    assert data["source_policy"]["poe_scope"] == "poe1_only"
    assert data["source_policy"]["poe2_policy"] == "POE2-only videos and channels are out of scope for this file."
    assert "popularity signals" in data["source_policy"]["youtube_view_rule"]
    assert data["coverage_summary"]["region_count"] == 12
    # ACCUMULATING: creators are a curated collection that is expanded (added,
    # never removed), so target_count only grows past the 121 baseline. Floor-check
    # it and pin the sum-consistency invariant (== sum of per-region creator_targets)
    # so a silent deletion still trips the count mismatch. The named-creator id-set
    # in test_user_seeded_and_expanded_creators guards specific seeded creators.
    assert data["coverage_summary"]["target_count"] >= 121
    assert data["coverage_summary"]["target_count"] == sum(
        len(region["creator_targets"]) for region in data["regions"]
    )
    assert data["coverage_summary"]["minimum_target_count_per_region"] == 10


def test_each_region_has_ten_targets_and_youtube_view_fields():
    data = _load_targets()
    allowed_statuses = {
        "sampled",
        "queried_no_owner_match",
        "no_results",
        "parse_failed",
        "request_failed",
        "not_sampled_offline_generation",
    }

    for region in data["regions"]:
        assert region["region_kind"] == "language_market_not_nationality"
        assert region["target_count"] >= 10
        assert len(region["creator_targets"]) >= 10
        assert region["youtube_market_queries"]

        for creator in region["creator_targets"]:
            assert creator["source_urls"]
            assert creator["promotion_status"].startswith("source_target_only")
            evidence = creator["youtube_view_evidence"]
            assert evidence["status"] in allowed_statuses
            assert evidence.get("source_url") or evidence.get("query")
            if evidence["status"] == "sampled":
                assert evidence["video_url"].startswith("https://www.youtube.com/watch?v=")
                assert evidence["title"]
                assert evidence["owner"]
                assert "view_count_text" in evidence


def test_user_seeded_and_expanded_creators_are_covered():
    data = _load_targets()
    creators = {
        creator["creator_id"]: creator
        for region in data["regions"]
        for creator in region["creator_targets"]
    }

    assert {
        "tori_sensei",
        "cptn_garbage",
        "dconnic",
        "emiracles",
        "jorgen",
        "conner_converse",
        "captainlance9",
        "ghazzytv",
        "zizaran",
        "goblin_inc_probable",
        "poeguy",
        "zeeboub",
        "sanavixx",
        "kankar",
        "anime_princess",
        "llyd",
        "master_t",
        "exiled_cat",
    } <= set(creators)

    assert "poison_carrion_golem" in creators["tori_sensei"]["known_focus"]
    assert "Exsanguinate Miner Trickster" in creators["cptn_garbage"]["known_focus"]
    assert "zero_to_hero" in creators["exiled_cat"]["known_focus"]
    assert "minion" in creators["ghazzytv"]["known_focus"]
    assert "hardcore" in creators["zizaran"]["known_focus"]
    assert creators["goblin_inc_probable"]["evidence_level"] == "user_seeded_ambiguous_alias"
    assert "cyclone_of_tumult" in creators["sanavixx"]["known_focus"]
    assert {
        "https://sanavixx.com/crafting/",
        "https://pobb.in/RH9MMGmuuro2",
    } <= {source["url"] for source in creators["sanavixx"]["source_urls"]}


def test_youtube_and_twitch_snapshots_are_recorded_as_signals():
    data = _load_targets()
    creators = [
        creator
        for region in data["regions"]
        for creator in region["creator_targets"]
    ]
    sampled_youtube = [
        creator
        for creator in creators
        if creator["youtube_view_evidence"]["status"] == "sampled"
    ]
    twitch_sampled = [
        creator
        for creator in creators
        if creator.get("twitchmetrics_evidence", {}).get("status") == "sampled"
    ]

    assert data["coverage_summary"]["youtube_view_sampled_creator_count"] == len(sampled_youtube)
    assert data["coverage_summary"]["twitchmetrics_sampled_creator_count"] == len(twitch_sampled)
    assert len(sampled_youtube) >= 50
    assert len(twitch_sampled) >= 50
    assert all(
        creator["youtube_view_evidence"]["status"] == "sampled"
        for region in data["regions"]
        if region["region_id"] == "english_global_core"
        for creator in region["creator_targets"]
    )


def test_korean_core_targets_have_direct_youtube_samples_where_available():
    data = _load_targets()
    korean = next(region for region in data["regions"] if region["region_id"] == "korea")
    creators = {creator["creator_id"]: creator for creator in korean["creator_targets"]}

    assert creators["tori_sensei"]["youtube_view_evidence"]["status"] == "sampled"
    assert creators["arserina"]["youtube_view_evidence"]["status"] == "sampled"
    assert creators["nyangnyonghyeon"]["youtube_view_evidence"]["status"] == "sampled"
    assert creators["rona_kr"]["youtube_view_evidence"]["status"] == "sampled"
    assert creators["catseye7"]["youtube_view_evidence"]["status"] == "queried_no_owner_match"
