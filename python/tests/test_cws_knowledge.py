# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "python"))

from cws_knowledge import CWSKnowledgeBase, CWSKnowledgeError, load_pack, validate_pack  # noqa: E402
from cws_twitch_collector import merge_catalog  # noqa: E402
from knowledge_router import build_context_pack  # noqa: E402


def _embed(texts: list[str]) -> list[list[float]]:
    needles = ("death", "ultimatum", "stun", "simulacrum")
    return [[float(text.casefold().count(needle)) for needle in needles] for text in texts]


def test_cws_v2_pack_is_referentially_valid():
    pack = load_pack()
    assert pack["patch"] == "3.29"
    assert pack["knowledge_version"] == "2.0.0"
    assert pack["snapshot_at"] == "2026-08-07"
    assert len(pack["sources"]) >= 10
    assert len(pack["diagnostic_rules"]) >= 8
    assert any(row["revision_id"] == "current_written_guide" for row in pack["revision_chain"])


def test_validator_rejects_dangling_diagnostic_claim():
    pack = load_pack()
    pack["diagnostic_rules"][0]["claim_refs"] = ["not_a_claim"]
    with pytest.raises(CWSKnowledgeError, match="dangling claims"):
        validate_pack(pack)


def test_korean_death_question_recalls_diagnosis_and_sources():
    kb = CWSKnowledgeBase()
    hits = kb.search("Emiracle 방송은 안 죽는데 나는 왜 끔살당하지?", limit=12)
    ids = {row["doc_id"] for row in hits}
    assert "claim:comparison_requirements" in ids
    assert any(row["record_type"] == "diagnostic_rule" for row in hits)
    assert all(row["source_refs"] for row in hits if row["record_type"] in {"claim", "diagnostic_rule"})


def test_sqlite_fts_and_optional_vectors_are_disposable(tmp_path: Path):
    kb = CWSKnowledgeBase()
    db = tmp_path / "cws.sqlite3"
    built = kb.build_index(db, embedder=_embed)
    assert built["documents"] == len(kb.docs)
    assert built["vectors"] == len(kb.docs)

    hits = kb.search("울티에서 죽음", db_path=db, embedder=_embed, filters={"record_type": "claim"})
    assert hits
    assert all(row["record_type"] == "claim" for row in hits)
    assert any("ultimatum" in row["text"].casefold() for row in hits)


def test_diagnose_finds_trigger_and_content_gate_failures():
    kb = CWSKnowledgeBase()
    result = kb.diagnose({
        "pob_url": "https://pobb.in/example",
        "pantheon": "Soul of the Brine King",
        "stun_avoidance_percent": 25,
        "content": "ultimatum",
        "variant": "first_bloodnotch",
        "has_bloodnotch": True,
        "map_mods": [],
        "death_pattern": "multi_hit",
        "damage_pattern": "hit",
        "has_defiance_of_destiny": False,
    })
    ids = [row["rule_id"] for row in result["diagnoses"]]
    assert ids[:3] == ["brine_king_breaks_loop", "stun_avoidance_breaks_loop", "wrong_ultimatum_stage"]
    assert result["diagnoses"][0]["source_refs"]


def test_diagnose_requests_pob_when_evidence_is_missing():
    result = CWSKnowledgeBase().diagnose({"content": "mapping"})
    ids = {row["rule_id"] for row in result["diagnoses"]}
    assert "unknown_needs_evidence" in ids
    assert "pob_url" in result["missing_observations"]


def test_knowledge_router_attaches_cws_pack():
    pack = build_context_pack("CWS Emiracle처럼 왜 안 죽고 나는 끔살 나지?")
    source_ids = {source["id"] for source in pack["selected_sources"]}
    assert "cws_diagnosis" in pack["intents"]
    assert "cws_emiracles_329" in source_ids
    assert "cws_emiracles_329" in pack["vector_candidates"]
    assert pack["cws_context"]["patch"] == "3.29"
    assert pack["cws_context"]["hits"]


def test_offline_twitch_catalog_can_be_exported_without_credentials():
    payload = merge_catalog(ROOT / "data" / "guide_sources" / "poe1_cws_chieftain_emiracles_3_29_v2.json", [])
    assert payload["channel"] == "emiracles"
    assert len(payload["videos"]) >= 9
    assert all("url" in row for row in payload["videos"])
    json.dumps(payload, ensure_ascii=False)
