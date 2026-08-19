from __future__ import annotations

import json

import pytest

from dark_bargain_luminary_knowledge import (
    DarkBargainLuminaryError,
    DarkBargainLuminaryKnowledgeBase,
    hashing_embedder,
    load_pack,
    validate_pack,
)


def test_pack_integrity_and_ordered_ssf_progression():
    pack = load_pack()
    assert pack["snapshot_at"] == "2026-08-08"
    assert pack["status"] == "experimental_ssf_progression"
    assert [row["order"] for row in pack["pob_variants"]] == [0, 1, 2]
    assert [row["order"] for row in pack["atlas_curriculum"]] == list(range(6))
    assert pack["atlas_curriculum"][0]["phase_id"] == "atlas_1_foundation"
    assert pack["atlas_curriculum"][-1]["phase_id"] == "atlas_6_t17_ubers"


def test_pack_rejects_dangling_claim_and_non_contiguous_atlas_order():
    pack = load_pack()
    dangling = json.loads(json.dumps(pack))
    dangling["diagnostic_rules"][0]["claim_refs"].append("missing")
    with pytest.raises(DarkBargainLuminaryError):
        validate_pack(dangling)

    bad_order = json.loads(json.dumps(pack))
    bad_order["atlas_curriculum"][-1]["order"] = 8
    with pytest.raises(DarkBargainLuminaryError):
        validate_pack(bad_order)


def test_korean_search_finds_link_engine_and_atlas_curriculum():
    kb = DarkBargainLuminaryKnowledgeBase()
    link_hits = kb.search("루미너리 원버튼 인튜이티브 링크 해골", limit=10)
    assert any(row["doc_id"] == "claim:one_button_interaction" for row in link_hits)
    atlas_hits = kb.search("아틀라스 Ritual Harvest 용병", limit=12)
    assert any(row["doc_id"] == "atlas:atlas_2_link_engine" for row in atlas_hits)


def test_hybrid_index_and_ci_diagnosis(tmp_path):
    kb = DarkBargainLuminaryKnowledgeBase()
    db = tmp_path / "dark_bargain_luminary.db"
    result = kb.build_index(db, hashing_embedder)
    assert result["documents"] == len(kb.docs)
    assert result["vectors"] == len(kb.docs)

    diagnosis = kb.diagnose({
        "player_pob_url": "https://pobb.in/example",
        "atlas_phase": "red_maps",
        "is_ci": True,
        "energy_shield": 5200,
        "link_trigger_reliable": False,
        "linked_allies_survive": False,
        "uses_full_theorycraft_conditions": True,
        "content": "T16 boss",
    })
    ids = {row["rule_id"] for row in diagnosis["diagnoses"]}
    assert {"link_engine_not_ready", "linked_target_dies", "ci_too_early", "pob_condition_inflation"} <= ids
