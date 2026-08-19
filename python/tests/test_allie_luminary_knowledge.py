from __future__ import annotations

import json

import pytest

from allie_luminary_knowledge import (
    LuminaryKnowledgeBase,
    LuminaryKnowledgeError,
    hashing_embedder,
    load_pack,
    validate_pack,
)
from cws_twitch_collector import merge_catalog
from knowledge_router import build_context_pack


def test_pack_integrity_and_current_revision():
    pack = load_pack()
    assert pack["snapshot_at"] == "2026-08-07"
    assert pack["revision_chain"][-1]["revision_id"] == "written_v2_4"
    assert len([row for row in pack["pob_variants"] if row.get("order") is not None]) == 9
    assert len(pack["media_catalog"]) == 21


def test_pack_rejects_dangling_rule_claim():
    pack = load_pack()
    broken = json.loads(json.dumps(pack))
    broken["diagnostic_rules"][0]["claim_refs"].append("does_not_exist")
    with pytest.raises(LuminaryKnowledgeError):
        validate_pack(broken)


def test_korean_alias_search_finds_mercenary_gate():
    kb = LuminaryKnowledgeBase()
    hits = kb.search("앨리 루미너리 용병이 T4 레어를 못 잡고 너무 약해", limit=10)
    ids = {hit["doc_id"] for hit in hits}
    assert "claim:mercenary_quality_gate" in ids or "rule:weak_campaign_merc" in ids


def test_index_and_hybrid_search(tmp_path):
    kb = LuminaryKnowledgeBase()
    db = tmp_path / "allie.db"
    result = kb.build_index(db, hashing_embedder)
    assert result["documents"] == len(kb.docs)
    assert result["vectors"] == len(kb.docs)
    hits = kb.search("Stormblast Mine Hand of Phrecia 정정", db_path=db, embedder=hashing_embedder)
    assert any(hit["doc_id"] == "claim:stormblast_removed" for hit in hits)


def test_diagnosis_separates_mercenary_from_player():
    kb = LuminaryKnowledgeBase()
    result = kb.diagnose({
        "variant": "level_90_t16_maps",
        "player_pob_url": "https://pobb.in/example",
        "merc_source": "campaign",
        "merc_effective_supports": 2,
        "merc_class": "kineticist",
        "flame_link_active": False,
        "content": "mapping",
        "map_mods": [],
    })
    ids = [row["rule_id"] for row in result["diagnoses"]]
    assert "weak_campaign_merc" in ids
    assert "flame_link_missing" in ids
    assert "merc_snapshot" in result["missing_observations"]


def test_stale_and_map_mod_rules():
    kb = LuminaryKnowledgeBase()
    result = kb.diagnose({
        "uses_stormblast_mine": True,
        "uses_flesh_and_stone": True,
        "map_mods": ["Players cannot Regenerate Life, Mana or Energy Shield"],
    })
    ids = {row["rule_id"] for row in result["diagnoses"]}
    assert {"stale_stormblast_setup", "stale_flesh_and_stone", "forbidden_map_mod"} <= ids


def test_router_selects_allie_pack_and_context():
    context = build_context_pack("Allie Bob & Friends 루미너리 용병이 약해")
    source_ids = {row["id"] for row in context["selected_sources"]}
    assert "allie_luminary_329" in source_ids
    assert context["allie_luminary_context"]["build_id"] == "poe1_3_29_allie_bob_friends_luminary"


def test_twitch_collector_exports_bundled_allie_catalog():
    payload = merge_catalog(
        LuminaryKnowledgeBase().pack_path,
        [],
        channel="Allliee_",
    )
    assert payload["dataset_kind"] == "pathcraft_creator_twitch_vod_metadata"
    assert payload["channel"] == "Allliee_"
    assert len(payload["videos"]) == 11
