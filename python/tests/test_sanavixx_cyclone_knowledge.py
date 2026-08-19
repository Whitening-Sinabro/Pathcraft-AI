from __future__ import annotations

import json

import pytest

from knowledge_router import build_context_pack
from sanavixx_cyclone_knowledge import (
    SanavixxKnowledgeBase,
    SanavixxKnowledgeError,
    hashing_embedder,
    load_pack,
    validate_pack,
)


def test_pack_integrity_and_progression():
    pack = load_pack()
    assert pack["snapshot_at"] == "2026-08-08"
    assert pack["revision_chain"][-1]["revision_id"] == "pob_329_current"
    assert len(pack["pob_variants"]) == 12
    assert any(row["recipe_id"] == "early_endgame_ezomyte_staff" for row in pack["crafting_recipes"])
    claims = {row["claim_id"]: row for row in pack["claims"]}
    assert "회복 속도.*감폭" in claims["korean_regular_map_regex"]["text_ko"]
    assert "폭발성 중심부" in claims["korean_nightmare_map_regex"]["text_ko"]
    assert "폐기된 라벨" in claims["map_regex_exact"]["text_ko"]
    assert "소켓:" in claims["korean_vendor_and_gem_regex"]["text_ko"]


def test_pack_rejects_dangling_claim():
    pack = load_pack()
    broken = json.loads(json.dumps(pack))
    broken["diagnostic_rules"][0]["claim_refs"].append("missing")
    with pytest.raises(SanavixxKnowledgeError):
        validate_pack(broken)


def test_korean_crafting_search():
    kb = SanavixxKnowledgeBase()
    hits = kb.search("사나빅스 HCSSF 지팡이 크래프팅 재조합", limit=12)
    ids = {row["doc_id"] for row in hits}
    assert "craft:early_endgame_ezomyte_staff" in ids or "claim:staff_craft_current" in ids


def test_index_hybrid_search(tmp_path):
    kb = SanavixxKnowledgeBase()
    db = tmp_path / "sanavixx.db"
    result = kb.build_index(db, hashing_embedder)
    assert result["documents"] == len(kb.docs)
    assert result["vectors"] == len(kb.docs)
    hits = kb.search("Starter Body Armor Essence of Fear 잘못된 절차", db_path=db, embedder=hashing_embedder)
    assert any(row["doc_id"] == "claim:crafting_page_body_inconsistent" for row in hits)


def test_hcssf_diagnostics():
    kb = SanavixxKnowledgeBase()
    result = kb.diagnose({
        "mode": "hcssf",
        "elemental_res_capped": False,
        "level": 70,
        "main_skill": "Cyclone",
        "has_yielding_mortality": False,
        "uses_ehp_as_only_safety_metric": True,
    })
    ids = {row["rule_id"] for row in result["diagnoses"]}
    assert {"hcssf_uncapped_resistance", "missing_yielding_mortality_ssf", "ehp_overconfidence"} <= ids


def test_router_selects_sanavixx_context():
    context = build_context_pack("SANAVIXX Cyclone Shockwave HCSSF 지팡이 제작")
    source_ids = {row["id"] for row in context["selected_sources"]}
    assert "sanavixx_cyclone_329" in source_ids
    assert context["sanavixx_cyclone_context"]["build_id"] == "poe1_3_29_sanavixx_cyclone_shockwave_slayer"
