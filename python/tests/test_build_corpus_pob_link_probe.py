# -*- coding: utf-8 -*-
"""Regression checks for corpus PoB link probing and promotion work orders."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from build_corpus_pob_link_probe import (  # noqa: E402
    _candidate_direct_links,
    beginner_failure_lens,
    build_pob_link_probe,
    candidate_search_queries,
    candidate_terms,
    extract_pob_links,
    normalize_url,
    relevance_score,
    text_mentions_patch,
)


SAMPLE_CANDIDATE = {
    "candidate_id": "3.25_lightning_arrow_deadeye",
    "patch": "3.25",
    "display_name": "Lightning Arrow Deadeye",
    "lane_id": "bow_projectile_attack_mapper",
    "collection_role": "stable_shell",
    "source_status": "source_hunted",
    "main_skill": "Lightning Arrow",
    "class_name": "Ranger",
    "ascendancy": "Deadeye",
}


def test_extract_pob_links_from_plain_text_and_html_anchors():
    text = """
    Recommended PoB: https://pobb.in/abcDEF_123.
    <a href="https://pastebin.com/raw/Qwerty12">Path of Building</a>
    <a href="/pob/zyx987">Not absolute poe ninja</a>
    """

    links = extract_pob_links(text, "https://poe.ninja/builds/example")
    urls = {row["url"] for row in links}

    assert "https://pobb.in/abcDEF_123" in urls
    assert "https://pastebin.com/raw/Qwerty12" in urls
    assert "https://poe.ninja/pob/zyx987" in urls


def test_normalize_url_converts_pastebin_to_raw_and_strips_punctuation():
    assert normalize_url("https://pastebin.com/AbCd12).") == "https://pastebin.com/raw/AbCd12"


def test_candidate_terms_and_relevance_ignore_generic_role_words():
    terms = candidate_terms(SAMPLE_CANDIDATE)

    assert "lightning" in terms
    assert "arrow" in terms
    assert "deadeye" not in terms
    assert relevance_score(SAMPLE_CANDIDATE, "3.25 Lightning Arrow pobb.in guide") >= 4


def test_candidate_search_queries_target_pob_sources():
    queries = candidate_search_queries(SAMPLE_CANDIDATE)

    assert len(queries) >= 5
    assert any("site:pobb.in" in query for query in queries)
    assert any("site:pobarchives.com" in query for query in queries)
    assert any("site:youtube.com" in query for query in queries)


def test_pob_link_probe_builds_promotion_work_orders_without_live_network():
    probe = build_pob_link_probe(live=False)

    assert probe["dataset_kind"] == "poe1_build_corpus_pob_link_probe"
    assert probe["summary"]["candidate_count"] >= 161
    assert probe["summary"]["manual_source_record_count"] >= 6
    assert probe["summary"]["direct_pob_candidate_count"] >= 6
    assert probe["summary"]["promotion_status_counts"]["ready_for_pob_parse"] >= 5
    assert probe["summary"]["promotion_status_counts"]["watchlist_needs_patch_notes_and_pob"] == 20

    for order in probe["work_orders"]:
        assert len(order["state_snapshot_plan"]) >= 2
        assert order["search_queries"]
        assert order["beginner_failure_lens"]["must_record"]

    manual = next(order for order in probe["work_orders"] if order["candidate_id"] == "3.23_boneshatter_slayer")
    assert manual["direct_pob_candidates"][0]["discovery_method"] == "manual_verified_source"

    # 골렘은 3.28 가이드에서 parser 검증된 direct PoB 를 확보해 needs_direct_pob_link 에서
    # 승격됐다. 승격 경로가 수동 검증 source 를 타는지까지 확인한다.
    golem = next(order for order in probe["work_orders"] if order["candidate_id"] == "3.28_poison_carrion_golem_witch")
    assert golem["promotion_status"] == "ready_for_pob_parse"
    assert golem["direct_pob_candidates"]
    assert all(
        pob["discovery_method"] == "manual_verified_source"
        for pob in golem["direct_pob_candidates"]
    )

    # 승격 후보를 특정 candidate_id 에 고정하면 수집이 진행될 때마다 깨지므로,
    # needs_direct_pob_link 분기는 아직 direct PoB 가 없는 후보 전체로 커버한다.
    assert probe["summary"]["promotion_status_counts"]["needs_direct_pob_link"] >= 1


def test_pob_link_probe_promotes_exsanguinate_miner_manual_sources():
    probe = build_pob_link_probe(live=False)
    orders = {order["candidate_id"]: order for order in probe["work_orders"]}

    exsang_324 = orders["3.24_exsanguinate_mines_trickster"]
    exsang_328 = orders["3.28_exsanguinate_reap_mines_trickster"]

    assert exsang_324["promotion_status"] == "ready_for_pob_parse"
    assert {row["url"] for row in exsang_324["direct_pob_candidates"]} >= {
        "https://pobb.in/BWiaBJnF0XdF",
        "https://pobb.in/VUc0XkHnNAmo",
    }
    assert exsang_328["promotion_status"] == "ready_for_pob_parse"
    assert {row["url"] for row in exsang_328["direct_pob_candidates"]} >= {
        "https://pobb.in/3J6Dm6pkA6-5",
        "https://pobb.in/ZFC1itVixJSB",
    }


def test_pob_link_probe_promotes_tori_sensei_spectre_manual_source():
    probe = build_pob_link_probe(live=False)
    spectre_328 = next(
        order for order in probe["work_orders"] if order["candidate_id"] == "3.28_raise_spectre_necromancer"
    )

    assert spectre_328["promotion_status"] == "ready_for_pob_parse"
    assert any(row["url"] == "https://pobb.in/oimmJKVwZB2e" for row in spectre_328["direct_pob_candidates"])


def test_failure_edge_cases_require_extra_snapshot_and_negative_lens():
    probe = build_pob_link_probe(live=False)
    failure = next(order for order in probe["work_orders"] if order["collection_role"] == "failure_edge_case")

    assert len(failure["state_snapshot_plan"]) == 3
    assert "explicit_negative_or_bricked_case_required" in failure["beginner_failure_lens"]["risk_tags"]


def test_beginner_failure_lens_is_lane_specific():
    lens = beginner_failure_lens(SAMPLE_CANDIDATE)

    assert lens["lens_id"] == "bow_projectile_attack_mapper_stable_shell"
    assert "weapon_dps_or_added_damage_too_low" in lens["risk_tags"]


GOLEM_CANDIDATE = {
    "candidate_id": "3.28_poison_carrion_golem_witch",
    "patch": "3.28",
    "display_name": "Poison Carrion Golem Necromancer",
    "lane_id": "minion_trigger_autobomber_special",
    "collection_role": "transition_case",
    "source_status": "source_hunted",
    "main_skill": "Summon Carrion Golem",
    "class_name": "Witch",
    "ascendancy": "Necromancer",
    "source_refs": ["youtube_326_tori_poison_carrion_golem"],
}


def test_manual_source_with_mismatched_patch_is_not_admitted():
    # A same-candidate manual record whose own patch field disagrees with the
    # candidate's patch must be skipped; a matching one must still be admitted.
    matching = {
        "patch": "3.28",
        "source_url": "https://example/match",
        "source_label": "matching 3.28 record",
        "pob_urls": [{"url": "https://pobb.in/MATCH328xx", "role": "primary"}],
        "confidence": "high",
    }
    mismatched = {
        "patch": "3.26",
        "source_url": "https://example/mismatch",
        "source_label": "stale 3.26 record",
        "pob_urls": [{"url": "https://pobb.in/STALE326xx", "role": "primary"}],
        "confidence": "high",
    }

    links = _candidate_direct_links(GOLEM_CANDIDATE, {}, [], [matching, mismatched])
    urls = {row["url"] for row in links}

    assert "https://pobb.in/MATCH328xx" in urls
    assert "https://pobb.in/STALE326xx" not in urls


def test_live_source_page_pob_requires_candidate_patch_in_text():
    # The proven leak: a 3.26 PoB scores on skill terms alone. Without the
    # candidate's own patch token it must not become a direct link.
    stale_326_link = {
        "url": "https://pobb.in/Gji0uiu1Aoog",
        "source_url": "https://youtu.be/stale",
        "anchor_text": "3.26 Poison Carrion Golem Necromancer PoB",
        "context": "PoE 3.26 Summon Carrion Golem poison league start Path of Building",
    }
    # Same PoB body but carrying the candidate's real patch token clears the bar.
    fresh_328_link = dict(stale_326_link)
    fresh_328_link["url"] = "https://pobb.in/Fresh328xxxx"
    fresh_328_link["anchor_text"] = "3.28 Poison Carrion Golem Necromancer PoB"
    fresh_328_link["context"] = "PoE 3.28 Summon Carrion Golem poison league start Path of Building"

    source_id = GOLEM_CANDIDATE["source_refs"][0]

    # Guard against a tautology: the 3.26 text really does score at/above the
    # admission threshold on skill terms, so patch is what excludes it.
    stale_text = " ".join(
        (stale_326_link["anchor_text"], stale_326_link["context"], stale_326_link["url"])
    )
    assert relevance_score(GOLEM_CANDIDATE, stale_text) >= 2
    assert not text_mentions_patch(GOLEM_CANDIDATE, stale_text)

    stale_only = _candidate_direct_links(
        GOLEM_CANDIDATE, {source_id: [stale_326_link]}, []
    )
    assert stale_only == []

    fresh_only = _candidate_direct_links(
        GOLEM_CANDIDATE, {source_id: [fresh_328_link]}, []
    )
    assert {row["url"] for row in fresh_only} == {"https://pobb.in/Fresh328xxxx"}


def test_penance_brand_326_anchor_stays_admitted_despite_325_anchor_text():
    # The manual record's own patch (3.26) is the authority; a 3.25 mention in the
    # anchor text must not reject it. Regression guard for the legit cross-patch ref.
    probe = build_pob_link_probe(live=False)
    penance = next(
        order
        for order in probe["work_orders"]
        if order["candidate_id"] == "3.26_penance_brand_inquisitor"
    )

    assert penance["promotion_status"] == "ready_for_pob_parse"
    assert penance["direct_pob_candidates"]
    assert all(
        row["discovery_method"] == "manual_verified_source"
        for row in penance["direct_pob_candidates"]
    )
