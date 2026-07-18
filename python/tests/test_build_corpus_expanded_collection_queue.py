# -*- coding: utf-8 -*-
"""Regression checks for the expanded build corpus collection queue."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from build_corpus_expanded_collection_queue import build_expanded_collection_queue  # noqa: E402


REQUIRED_LANES = {
    "bow_projectile_attack_mapper",
    "melee_strike_slam",
    "spell_hit_brand_selfcast",
    "dot_ailment_dot",
    "trap_mine_totem",
    "minion_trigger_autobomber_special",
}

# 이미 확보해서 하위 산출물(watchlist 카드 등)이 의존하는 후보들. 누적은 허용하되
# 이 후보들이 조용히 사라지는 것은 막는다. 총계를 숫자로 고정하는 방식은 후보를
# 추가할 때마다 깨지는 데다, 삭제와 추가가 상쇄되면 아예 탐지하지 못한다.
REQUIRED_CANDIDATE_IDS = {
    "3.28_exsanguinate_reap_mines_trickster",
    "3.28_poison_carrion_golem_witch",
    "3.28_ignite_slamentalist_elementalist",
    "3.28_righteous_cold_dot_autobomber_elementalist",
    "3.28_volatile_dead_spellslinger_necromancer",
}


def test_expanded_collection_queue_keeps_20_candidate_baseline_and_allows_additions():
    queue = build_expanded_collection_queue()

    assert queue["dataset_kind"] == "poe1_build_corpus_expanded_collection_queue"
    assert queue["totals"]["patch_count"] == 8

    patches = queue["patches"]
    for patch in patches:
        assert patch["target_candidate_count"] == 20
        assert patch["candidate_count"] >= 20

    # 패치당 20 개는 상한이 아니라 최소 baseline 이고 새 후보는 기존 후보를 빼지 않고
    # 누적한다. 따라서 총계는 숫자로 고정하지 않고, 확보한 후보가 사라지지 않는지로
    # 검증한다.
    all_ids = {
        candidate["candidate_id"] for patch in patches for candidate in patch["candidates"]
    }
    missing = REQUIRED_CANDIDATE_IDS - all_ids
    assert not missing, f"기존 후보가 사라졌다: {sorted(missing)}"

    patch_328 = next(patch for patch in patches if patch["patch"] == "3.28")
    assert patch_328["candidate_count"] >= 21


def test_expanded_collection_queue_covers_required_lanes():
    queue = build_expanded_collection_queue()

    for patch in queue["patches"]:
        lane_counts = patch["lane_counts"]
        assert set(lane_counts).issuperset(REQUIRED_LANES)
        for lane_id in REQUIRED_LANES:
            assert lane_counts[lane_id] >= 2, f"{patch['patch']} missing {lane_id}"


def test_expanded_collection_queue_has_stable_transition_and_edge_roles():
    queue = build_expanded_collection_queue()

    for patch in queue["patches"]:
        role_counts = patch["collection_role_counts"]
        assert role_counts["stable_shell"] == 12
        assert role_counts["transition_case"] >= 4
        assert role_counts["failure_edge_case"] == 4

    # 신규 후보는 stable_shell / failure_edge_case 를 건드리지 않고 transition_case 로
    # 누적되므로 하한만 고정한다.
    patch_328 = next(patch for patch in queue["patches"] if patch["patch"] == "3.28")
    assert patch_328["collection_role_counts"]["transition_case"] >= 5


def test_expanded_collection_queue_tracks_exsanguinate_mine_over_generic_pyroclast_328():
    queue = build_expanded_collection_queue()
    patch_328 = next(patch for patch in queue["patches"] if patch["patch"] == "3.28")
    candidates = {row["candidate_id"]: row for row in patch_328["candidates"]}

    assert "3.28_exsanguinate_reap_mines_trickster" in candidates
    assert "3.28_pyroclast_mines_reliquarian" not in candidates

    mine = candidates["3.28_exsanguinate_reap_mines_trickster"]
    assert mine["lane_id"] == "trap_mine_totem"
    assert mine["class_name"] == "Shadow"
    assert mine["ascendancy"] == "Trickster"
    assert "youtube_328_fearlessdumb0_exsanguinate_reap_miner" in mine["source_refs"]


def test_expanded_collection_queue_tracks_tori_current_poison_carrion_golem():
    queue = build_expanded_collection_queue()
    patch_328 = next(patch for patch in queue["patches"] if patch["patch"] == "3.28")
    candidates = {row["candidate_id"]: row for row in patch_328["candidates"]}

    assert "3.28_poison_carrion_golem_witch" in candidates
    assert "3.28_volatile_dead_spellslinger_necromancer" in candidates

    golem = candidates["3.28_poison_carrion_golem_witch"]
    assert golem["lane_id"] == "minion_trigger_autobomber_special"
    assert golem["main_skill"] == "Summon Carrion Golem"
    assert golem["class_name"] == "Witch"
    assert "youtube_tori_sensei_poison_carrion_golem" in golem["source_refs"]
    assert "youtube_326_tori_poison_carrion_golem" in golem["source_refs"]


def test_expanded_collection_queue_source_mix_is_not_single_site_only():
    queue = build_expanded_collection_queue()
    source_families = {source["family"] for source in queue["source_registry"].values()}

    assert {"reddit", "youtube", "build_site", "official", "community_archive"}.issubset(
        source_families
    )

    for patch in queue["patches"]:
        assert "reddit" in patch["source_family_counts"]
        assert "build_site" in patch["source_family_counts"]
        assert "youtube" in patch["source_family_counts"]
        assert "community_archive" in patch["source_family_counts"]
        if patch["patch"] == "3.29":
            assert "official" in patch["source_family_counts"]


def test_expanded_collection_queue_ids_are_unique_and_watchlist_marked():
    queue = build_expanded_collection_queue()
    ids = [
        candidate["candidate_id"]
        for patch in queue["patches"]
        for candidate in patch["candidates"]
    ]

    assert len(ids) == len(set(ids))

    by_patch = {patch["patch"]: patch for patch in queue["patches"]}
    assert by_patch["3.29"]["patch_target_status"] == "watchlist"
    assert all(
        candidate["source_status"] == "watchlist_pre_patch_notes"
        for candidate in by_patch["3.29"]["candidates"]
    )
