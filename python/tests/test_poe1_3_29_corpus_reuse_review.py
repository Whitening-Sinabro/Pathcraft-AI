# -*- coding: utf-8 -*-
"""Integrity checks for the 3.29 corpus reuse review matrix."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REVIEW_PATH = ROOT / "data" / "poe1_3_29_corpus_reuse_review_v1.json"


def _load_review() -> dict:
    return json.loads(REVIEW_PATH.read_text(encoding="utf-8"))


def _tracks(data: dict) -> dict:
    return {
        track["track_id"]: track
        for category in data["category_matrix"]
        for track in category["tracks"]
    }


def _reviews(data: dict) -> dict:
    return {row["family_id"]: row for row in data["reviews"]}


def test_reuse_review_has_player_facing_labels_and_depth():
    data = _load_review()

    assert data["dataset_kind"] == "poe1_3_29_corpus_reuse_review"
    assert data["patch"] == "3.29"
    assert data["review_policy"]["launch_state"] == "pre_launch_patch_notes_only"
    assert data["review_policy"]["poe2_scope"] == "excluded"
    assert "later official patch notes" in data["review_policy"]["historical_patch_gate"]
    assert "data/patch_notes/poe1_3_27_3_29_patch_history_context.json" in data["source_context"]
    assert "data/poe1_3_29_luminary_merc_link_intake_v1.json" in data["source_context"]

    labels = {row["label"] for row in data["label_legend"]}
    assert {"가능성 높음", "연습해도 됨", "손봐야 가능", "구경만", "위험 신호"} <= labels

    category_tracks = _tracks(data)
    assert len(data["category_matrix"]) >= 4
    assert len(category_tracks) >= 30


def test_reuse_review_splits_leveling_delivery_and_defense_axes():
    data = _load_review()
    categories = {row["category_id"]: row for row in data["category_matrix"]}

    assert {"leveling_routes", "damage_delivery", "defense_and_gear_pressure", "creator_source_priorities"} <= set(categories)

    tracks = _tracks(data)
    assert tracks["mine_pyroclast_to_exsanguinate"]["judgement"] == "연습해도 됨"
    assert tracks["totem_holy_flame_to_spell_totem"]["judgement"] == "손봐야 가능"
    assert tracks["scion_reliquarian_luminary_start"]["judgement"] == "구경만"
    assert "Hallowed Monarch" in json.dumps(tracks["mercenary_luminary_state"], ensure_ascii=False)
    assert tracks["mana_cost_efficiency"]["judgement"] == "손봐야 가능"
    assert tracks["socket_color_quality"]["judgement"] == "연습해도 됨"
    assert "품질 효과" in tracks["socket_color_quality"]["why"]
    assert "optimization choice" in " ".join(tracks["socket_color_quality"]["patch_hooks"])


def test_reuse_review_does_not_merge_spectres_with_positive_minion_lanes():
    data = _load_review()
    tracks = _tracks(data)
    reviews = _reviews(data)

    assert tracks["non_spectre_minion_delivery"]["judgement"] == "가능성 높음"
    assert tracks["spectre_delivery"]["judgement"] == "위험 신호"
    assert reviews["minion_srs_zombie_dominating_blow"]["label"] == "가능성 높음"
    assert reviews["raise_spectre_wretched_defiler"]["label"] == "위험 신호"

    spectre_text = json.dumps(reviews["raise_spectre_wretched_defiler"], ensure_ascii=False)
    assert "Spectres" in spectre_text
    assert "life" in spectre_text.casefold()


def test_reuse_review_keeps_exsang_mines_separate_from_hexblast_and_cowb():
    data = _load_review()
    reviews = _reviews(data)
    tracks = _tracks(data)

    assert reviews["exsanguinate_reap_miner_and_mines"]["label"] == "연습해도 됨"
    assert reviews["hexblast_mines"]["label"] == "위험 신호"
    assert reviews["cast_on_ward_break_cowb"]["label"] == "위험 신호"

    mine_goal = json.dumps(tracks["mine_sources"], ensure_ascii=False)
    assert "Exsanguinate/Reap" in mine_goal
    assert "Hexblast" in json.dumps(reviews["hexblast_mines"], ensure_ascii=False)
    assert "watchlist-only" in json.dumps(reviews["hexblast_mines"], ensure_ascii=False)


def test_reuse_review_covers_creator_specific_current_sources():
    data = _load_review()
    tracks = _tracks(data)

    minion_sources = json.dumps(tracks["minion_sources"], ensure_ascii=False)
    mine_sources = json.dumps(tracks["mine_sources"], ensure_ascii=False)
    caster_sources = json.dumps(tracks["caster_brand_sources"], ensure_ascii=False)
    ranger_sources = json.dumps(tracks["ranger_melee_sources"], ensure_ascii=False)

    assert "Tori-sensei" in minion_sources
    assert "Dconnic" in minion_sources
    assert "Cptn Garbage" in mine_sources
    assert "Jorgen" in mine_sources
    assert "ZeeBoub" in caster_sources
    assert "anime princess" in caster_sources
    assert "Fubgun" in ranger_sources
    assert "Kankar" in ranger_sources
