# -*- coding: utf-8 -*-
"""Route build/user questions to the smallest useful Pathcraft knowledge pack.

The router is intentionally not a vector search layer. It first classifies
structured entities and evidence needs, then marks only unstructured sources as
future vector candidates.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from ggpk_index import GGPKIndex
from item_mod_semantics import parse_item_mod_lines, parse_item_raw_text, summarize_item_mods
from cws_knowledge import CWSKnowledgeBase
from allie_luminary_knowledge import LuminaryKnowledgeBase
from sanavixx_cyclone_knowledge import SanavixxKnowledgeBase

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
DATA_ROOT = ROOT / "data"


SOURCE_REGISTRY = {
    "db_catalog": {
        "path": "db_catalog.json",
        "kind": "catalog",
        "evidence_layer": "inventory",
        "retrieval_mode": "summary",
        "vectorization": "never_exact_metadata",
    },
    "ggpk_gems": {
        "path": "game_data/SkillGems.json + game_data/ActiveSkills.json",
        "kind": "raw_ggpk",
        "evidence_layer": "implementation_truth",
        "retrieval_mode": "exact_lookup",
        "vectorization": "never_exact_numeric",
    },
    "ggpk_items_mods": {
        "path": "game_data/BaseItemTypes.json + game_data/Mods.json",
        "kind": "raw_ggpk",
        "evidence_layer": "implementation_truth",
        "retrieval_mode": "exact_lookup",
        "vectorization": "never_exact_numeric",
    },
    "ggpk_passives": {
        "path": "game_data/PassiveSkills.json",
        "kind": "raw_ggpk",
        "evidence_layer": "implementation_truth",
        "retrieval_mode": "exact_lookup",
        "vectorization": "never_exact_numeric",
    },
    "patch_delta": {
        "path": "patch_notes/poe1_3_29_0_patch_delta_index.json",
        "kind": "patch_notes",
        "evidence_layer": "official_text_delta",
        "retrieval_mode": "filtered_entries",
        "vectorization": "hybrid_exact_for_numbers",
    },
    "patch_overlay_policy": {
        "path": "patch_notes/poe1_3_29_0_early_patch_adjustment_policy.json",
        "kind": "patch_notes",
        "evidence_layer": "overlay_policy",
        "retrieval_mode": "summary",
        "vectorization": "never_policy",
    },
    "gem_taxonomy": {
        "path": "poe1_gem_taxonomy.latest.json",
        "kind": "gems",
        "evidence_layer": "derived_taxonomy",
        "retrieval_mode": "exact_lookup",
        "vectorization": "never_exact_taxonomy",
    },
    "item_mod_index": {
        "path": "ggpk_derived/poe1_item_mod_derivation_manifest.json",
        "kind": "items_and_mods",
        "evidence_layer": "derived_ggpk",
        "retrieval_mode": "exact_lookup",
        "vectorization": "never_exact_numeric",
    },
    "season_research": {
        "path": "poe1_season_research_3_29_allflame_live.json",
        "kind": "season_research",
        "evidence_layer": "official_research",
        "retrieval_mode": "summary",
        "vectorization": "maybe_for_long_notes",
    },
    "global_review": {
        "path": "poe1_3_29_global_review.json",
        "kind": "season_research",
        "evidence_layer": "crosscheck_summary",
        "retrieval_mode": "summary",
        "vectorization": "maybe_for_long_notes",
    },
    "live_validation_queue": {
        "path": "poe1_3_29_live_validation_queue.json",
        "kind": "season_research",
        "evidence_layer": "launch_validation",
        "retrieval_mode": "summary",
        "vectorization": "never_queue",
    },
    "information_intake": {
        "path": "poe1_3_29_information_intake_plan.json",
        "kind": "operations",
        "evidence_layer": "operations",
        "retrieval_mode": "summary",
        "vectorization": "never_policy",
    },
    "atlas_farming": {
        "path": "atlas_farming_knowledge.json",
        "kind": "atlas_farming",
        "evidence_layer": "strategy_baseline",
        "retrieval_mode": "summary",
        "vectorization": "maybe_for_long_notes",
    },
    "farming_meta": {
        "path": "farming_meta/farming_meta_all.json",
        "kind": "atlas_farming",
        "evidence_layer": "farming_meta",
        "retrieval_mode": "summary",
        "vectorization": "maybe_for_long_notes",
    },
    "poe_ninja_economy": {
        "path": "python/game_data/*.json",
        "kind": "economy",
        "evidence_layer": "economy_observation",
        "retrieval_mode": "exact_price_snapshot",
        "vectorization": "never_numeric_snapshot",
    },
    "build_corpus": {
        "path": "build_corpus_* + builds/",
        "kind": "builds",
        "evidence_layer": "build_samples",
        "retrieval_mode": "filtered_candidates",
        "vectorization": "hybrid_for_guide_text",
    },
    "brand_guide_zeeboub": {
        "path": "guide_sources/poe1_brand_guide_zeeboub_v2.json",
        "kind": "community_build_guide",
        "evidence_layer": "external_creator_guide",
        "retrieval_mode": "structured_section_lookup",
        "vectorization": "hybrid_for_long_guide_notes",
    },
    "cws_emiracles_329": {
        "path": "guide_sources/poe1_cws_chieftain_emiracles_3_29_v2.json",
        "kind": "community_build_knowledge",
        "evidence_layer": "versioned_creator_guide_and_diagnostics",
        "retrieval_mode": "structured_filters_plus_fts_vector",
        "vectorization": "hybrid_for_atomic_claims",
    },
    "allie_luminary_329": {
        "path": "guide_sources/poe1_luminary_allie_bob_friends_3_29_v1.json",
        "kind": "community_build_knowledge",
        "evidence_layer": "versioned_creator_guide_multi_entity_diagnostics",
        "retrieval_mode": "structured_filters_plus_fts_vector",
        "vectorization": "hybrid_for_atomic_claims",
    },
    "sanavixx_cyclone_329": {
        "path": "guide_sources/poe1_cyclone_shockwave_slayer_sanavixx_3_29_v1.json",
        "kind": "community_build_knowledge",
        "evidence_layer": "versioned_creator_guide_hcssf_and_crafting_diagnostics",
        "retrieval_mode": "structured_filters_plus_fts_vector",
        "vectorization": "hybrid_for_atomic_claims_and_crafts",
    },
    "community_probe": {
        "path": "build_variant_live_source_probe.latest.json",
        "kind": "community_search",
        "evidence_layer": "community_signal",
        "retrieval_mode": "filtered_candidates",
        "vectorization": "yes_unstructured_text",
    },
    "new_player_friction": {
        "path": "new_player_friction_knowledge.json",
        "kind": "support",
        "evidence_layer": "explanation_taxonomy",
        "retrieval_mode": "summary",
        "vectorization": "maybe_for_long_notes",
    },
}

INTENT_RULES = {
    "patch_update": ("patch", "hotfix", "3.29", "패치", "핫픽스", "수치", "변경"),
    "ggpk_truth": ("ggpk", "client", "구현", "데이터", "db", "mod", "모드"),
    "build_analysis": ("build", "pob", "pobb", "빌드", "젬", "dps", "ehp"),
    "farming_strategy": ("farm", "farming", "atlas", "map", "fossil", "guardian", "blight", "파밍", "아틀라스", "맵"),
    "economy_check": ("price", "trade", "poe.ninja", "economy", "비싸", "가격", "경제"),
    "community_signal": ("reddit", "youtube", "guide", "streamer", "커뮤니티", "유튜브", "가이드"),
    "new_player_help": ("beginner", "new player", "초보", "유입", "어려"),
    "scion_329": ("scion", "reliquarian", "luminary", "ascendant", "사이온", "레퀼", "루미너리"),
    "cws_diagnosis": ("cws", "cast when stunned", "bloodnotch", "emiracle", "emiracles", "기절 시 시전"),
    "allie_luminary": ("allie", "allie's", "bob & friends", "bob and friends", "앨리", "알리"),
    "sanavixx_cyclone": ("sanavixx", "sanavix", "사나빅스", "cyclone shockwave", "cyclone of tumult"),
}

CWS_TERMS = {
    "cws", "cast when stunned", "bloodnotch", "immutable force", "emiracle", "emiracles",
    "기절 시 시전", "시전 시 기절",
}

ALLIE_LUMINARY_TERMS = {
    "allie", "allie's", "bob & friends", "bob and friends", "allliee_",
    "앨리", "알리", "hallowed monarch", "soulthirst", "ceinture of benevolence",
}

SANAVIXX_CYCLONE_TERMS = {
    "sanavixx", "sanavix", "사나빅스", "cyclone shockwave", "cyclone of tumult",
    "void shockwave", "the yielding mortality", "ezomyte staff",
}

FARMING_TERMS = {
    "fossil",
    "guardian",
    "blight",
    "atlas",
    "map",
    "scrying",
    "allflame",
    "파밍",
    "가디언",
    "화석",
    "아틀라스",
}

BRAND_GUIDE_TERMS = {
    "brand",
    "brands",
    "penance",
    "penance brand",
    "penance brand of dissipation",
    "storm brand",
    "armageddon brand",
    "arma brand",
    "brand recall",
    "inquisitor brand",
}

ITEM_NAME_KEYS = ("name", "base_type", "base", "item")
ITEM_MOD_LINE_KEYS = (
    "mods",
    "explicit_mods",
    "implicit_mods",
    "enchant_mods",
    "crafted_mods",
    "fractured_mods",
)

SEASON_TERMS = {
    "3.29",
    "allflame",
    "curse of the allflame",
    "scion",
    "reliquarian",
    "luminary",
    "mercenary",
    "사이온",
    "레퀼",
    "루미너리",
    "용병",
}


def _load_json(rel_path: str, default: Any) -> Any:
    path = DATA_ROOT / rel_path
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _norm(value: object) -> str:
    return str(value or "").strip().casefold()


def _text_blob(query: str = "", build_data: dict[str, Any] | None = None) -> str:
    parts = [query]
    if isinstance(build_data, dict):
        meta = build_data.get("meta", {}) or {}
        for key in ("class", "ascendancy", "main_skill", "skill", "build_name"):
            parts.append(str(meta.get(key, "")))
        try:
            parts.extend(GGPKIndex.extract_gem_names(build_data))
            parts.extend(GGPKIndex.extract_item_names(build_data))
        except Exception:
            pass
    return " ".join(part for part in parts if part).casefold()


def classify_intents(query: str = "", build_data: dict[str, Any] | None = None) -> list[str]:
    text = _text_blob(query, build_data)
    intents = []
    for intent, needles in INTENT_RULES.items():
        if any(needle.casefold() in text for needle in needles):
            intents.append(intent)
    if build_data and "build_analysis" not in intents:
        intents.append("build_analysis")
    return sorted(intents)


def extract_entities(query: str = "", build_data: dict[str, Any] | None = None, game: str = "poe1") -> dict[str, Any]:
    index = GGPKIndex(game=game)
    text = _text_blob(query, build_data)
    query_lower = _norm(query)

    gem_names: set[str] = set()
    item_names: set[str] = set()
    missing_terms: set[str] = set()

    if isinstance(build_data, dict):
        gem_names.update(GGPKIndex.extract_gem_names(build_data))
        item_names.update(GGPKIndex.extract_item_names(build_data))

    # Query-side exact lookup: try quoted terms, punctuation-safe phrases, and small n-grams.
    candidates = set(re.findall(r"[A-Za-z][A-Za-z' -]{2,60}", query))
    candidates.update(re.findall(r"'([^']{3,60})'", query))
    candidates.update(re.findall(r'"([^"]{3,60})"', query))
    words = re.findall(r"[A-Za-z][A-Za-z']+", query)
    for size in range(1, min(5, len(words) + 1)):
        for start in range(0, len(words) - size + 1):
            candidates.add(" ".join(words[start:start + size]))
    for candidate in candidates:
        name = candidate.strip(" -:,.")
        if not name:
            continue
        if index.get_gem(name):
            gem_names.add(name)
        elif index.get_item(name):
            item_names.add(name)

    matched_gems = [index.get_gem(name) for name in sorted(gem_names) if index.get_gem(name)]
    matched_items = [index.get_item(name) for name in sorted(item_names) if index.get_item(name)]
    missing_terms.update(name for name in gem_names if not index.get_gem(name))
    missing_terms.update(name for name in item_names if not index.get_item(name))

    season_terms = sorted(term for term in SEASON_TERMS if term in text)
    farming_terms = sorted(term for term in FARMING_TERMS if term in text or term in query_lower)
    brand_guide_terms = sorted(term for term in BRAND_GUIDE_TERMS if term in text or term in query_lower)
    cws_terms = sorted(term for term in CWS_TERMS if term in text or term in query_lower)
    allie_luminary_terms = sorted(term for term in ALLIE_LUMINARY_TERMS if term in text or term in query_lower)
    sanavixx_cyclone_terms = sorted(term for term in SANAVIXX_CYCLONE_TERMS if term in text or term in query_lower)

    meta = build_data.get("meta", {}) if isinstance(build_data, dict) else {}
    return {
        "game": game,
        "class": meta.get("class"),
        "ascendancy": meta.get("ascendancy"),
        "matched_gems": matched_gems,
        "matched_items": matched_items,
        "missing_terms": sorted(missing_terms),
        "season_terms": season_terms,
        "farming_terms": farming_terms,
        "brand_guide_terms": brand_guide_terms,
        "cws_terms": cws_terms,
        "allie_luminary_terms": allie_luminary_terms,
        "sanavixx_cyclone_terms": sanavixx_cyclone_terms,
    }


def _add_source(selected: dict[str, dict[str, Any]], source_id: str, reason: str) -> None:
    source = dict(SOURCE_REGISTRY[source_id])
    source["id"] = source_id
    source.setdefault("reasons", [])
    source["reasons"].append(reason)
    if source_id in selected:
        selected[source_id]["reasons"].append(reason)
    else:
        selected[source_id] = source


def select_sources(intents: list[str], entities: dict[str, Any]) -> list[dict[str, Any]]:
    selected: dict[str, dict[str, Any]] = {}
    _add_source(selected, "db_catalog", "Always include catalog inventory for traceability.")

    has_gems = bool(entities.get("matched_gems") or entities.get("missing_terms"))
    has_items = bool(entities.get("matched_items"))
    has_season = bool(entities.get("season_terms")) or "scion_329" in intents
    has_farming = bool(entities.get("farming_terms")) or "farming_strategy" in intents
    has_brand_guide = bool(entities.get("brand_guide_terms")) or any(
        "brand" in _norm(row.get("name"))
        for row in entities.get("matched_gems", [])
    )
    has_cws = bool(entities.get("cws_terms")) or "cws_diagnosis" in intents
    has_allie_luminary = bool(entities.get("allie_luminary_terms")) or "allie_luminary" in intents
    has_sanavixx_cyclone = bool(entities.get("sanavixx_cyclone_terms")) or "sanavixx_cyclone" in intents

    if has_gems:
        _add_source(selected, "ggpk_gems", "Gem names require exact SkillGems/ActiveSkills lookup.")
        _add_source(selected, "gem_taxonomy", "Gem role/supportability should come from taxonomy before AI explanation.")
        _add_source(selected, "patch_delta", "Gem numbers may have 3.29 patch-note deltas.")

    if has_items or "economy_check" in intents:
        _add_source(selected, "ggpk_items_mods", "Items and affix claims require exact BaseItemTypes/Mods lookup.")
        _add_source(selected, "item_mod_index", "Item mod availability should use derived GGPK mod index.")
        _add_source(selected, "poe_ninja_economy", "Item access and price need economy snapshots.")

    if has_season:
        _add_source(selected, "season_research", "3.29 season terms require official season research.")
        _add_source(selected, "global_review", "3.29 whole-patch implications require cross-domain review.")
        _add_source(selected, "patch_delta", "3.29 claims should be anchored to patch deltas.")
        _add_source(selected, "patch_overlay_policy", "Early-season numbers need overlay/GGPK refresh policy.")
        _add_source(selected, "live_validation_queue", "Launch-week recommendations must stay gated until validation.")
        _add_source(selected, "information_intake", "Stale source state affects confidence.")

    if has_farming:
        _add_source(selected, "atlas_farming", "Farming advice needs phase gates and atlas baseline.")
        _add_source(selected, "farming_meta", "Farming meta/reward data should be separated from build advice.")
        _add_source(selected, "poe_ninja_economy", "Farming rewards need economy snapshots.")
        _add_source(selected, "live_validation_queue", "Farming promotion needs live map measurements.")

    if "build_analysis" in intents:
        _add_source(selected, "build_corpus", "Build claims need corpus or PoB-backed samples.")
        _add_source(selected, "patch_delta", "Build-relevant numbers may have patch deltas.")

    if has_brand_guide:
        _add_source(selected, "brand_guide_zeeboub", "Brand/Penance/Storm Brand coaching can use the structured ZeeBoub guide DB.")
        _add_source(selected, "build_corpus", "Brand guide claims should still be cross-checked against corpus/PoB samples.")

    if has_cws:
        _add_source(selected, "cws_emiracles_329", "CWS/Emiracle questions require the versioned 3.29 claim and diagnosis pack.")
        _add_source(selected, "build_corpus", "User-vs-creator comparisons require PoB-backed build facts.")

    if has_allie_luminary:
        _add_source(selected, "allie_luminary_329", "Allie/Bob & Friends questions require the current versioned player/mercenary/Bob/spectre pack.")
        _add_source(selected, "build_corpus", "Player and mercenary snapshots must be compared separately from creator guidance.")

    if has_sanavixx_cyclone:
        _add_source(selected, "sanavixx_cyclone_329", "SANAVIXX Cyclone questions require staged 3.29 HCSSF safety and crafting evidence.")
        _add_source(selected, "build_corpus", "User-vs-creator Cyclone comparisons require the user's exact PoB stage and weapon.")

    if "community_signal" in intents:
        _add_source(selected, "community_probe", "Community guide discovery should remain lower confidence.")
        _add_source(selected, "build_corpus", "Community candidates need parsed build corpus confirmation.")

    if "new_player_help" in intents:
        _add_source(selected, "new_player_friction", "Beginner explanations should use friction taxonomy.")

    if "ggpk_truth" in intents or "patch_update" in intents:
        _add_source(selected, "patch_overlay_policy", "Patch/GGPK conflicts need overlay rules.")
        _add_source(selected, "information_intake", "Freshness matters for current patch/GGPK questions.")

    if "ggpk_truth" in intents:
        _add_source(selected, "ggpk_passives", "GGPK truth questions may involve passive tree or ascendancy data.")

    order = {
        "db_catalog": 0,
        "information_intake": 1,
        "patch_overlay_policy": 2,
        "patch_delta": 3,
        "ggpk_gems": 4,
        "ggpk_items_mods": 5,
        "ggpk_passives": 6,
    }
    return sorted(selected.values(), key=lambda row: (order.get(row["id"], 50), row["id"]))


def _filter_patch_entries(delta: dict[str, Any], entities: dict[str, Any], intents: list[str], limit: int) -> list[dict[str, Any]]:
    entries = delta.get("entries", []) if isinstance(delta, dict) else []
    if not entries:
        return []

    names = {_norm(row.get("name")) for row in entities.get("matched_gems", []) + entities.get("matched_items", [])}
    tags = set()
    if entities.get("season_terms"):
        tags.update({"allflame", "scion", "mercenary"})
    if entities.get("farming_terms") or "farming_strategy" in intents:
        tags.update({"atlas", "economy_reward"})
    if "economy_check" in intents:
        tags.add("economy_reward")

    entity_matched = []
    tag_matched = []
    for entry in entries:
        entity = _norm(entry.get("entity"))
        entry_tags = set(entry.get("watch_tags", []) or [])
        if entity and entity in names:
            entity_matched.append(entry)
        elif tags and entry_tags & tags:
            tag_matched.append(entry)
    return (entity_matched + tag_matched)[:limit]


def _clean_text(value: object) -> str:
    return str(value or "").strip()


def _is_unique_item(rarity: str = "", item_info: dict[str, Any] | None = None) -> bool:
    return rarity.casefold() == "unique" or bool((item_info or {}).get("unique_base"))


def _compact_item_info(item_info: dict[str, Any] | None) -> dict[str, Any] | None:
    if not item_info:
        return None
    return {
        "name": item_info.get("name"),
        "base_type": item_info.get("base_type"),
        "metadata_id": item_info.get("metadata_id"),
        "drop_level": item_info.get("drop_level"),
        "item_class": item_info.get("item_class"),
        "mod_domain": item_info.get("mod_domain"),
        "unique_base": item_info.get("unique_base"),
        "unique_tier": item_info.get("unique_tier"),
        "tag_keys": item_info.get("tag_keys") or [],
    }


def _compact_candidate_mod(mod: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": mod.get("id"),
        "name": mod.get("name"),
        "level": mod.get("level"),
        "generation_type": mod.get("generation_type"),
        "spawn_weight": mod.get("spawn_weight"),
        "mod_type_key": mod.get("mod_type_key"),
        "families": (mod.get("families") or [])[:4],
        "is_essence_only": bool(mod.get("is_essence_only")),
        "stats": (mod.get("stats") or [])[:4],
    }


def _compact_current_mod(mod: dict[str, Any]) -> dict[str, Any]:
    return {
        "text": mod.get("text"),
        "source": mod.get("source"),
        "categories": mod.get("categories") or [],
        "numeric_totals": mod.get("numeric_totals") or {},
        "likely_affix_generation": mod.get("likely_affix_generation"),
    }


def _iter_build_item_payloads(build_data: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not isinstance(build_data, dict):
        return []

    payloads: list[dict[str, Any]] = []
    for item in build_data.get("items", []) or []:
        if isinstance(item, dict):
            payload = dict(item)
            payload.setdefault("_pathcraft_source", "build_data.items")
            payloads.append(payload)

    for stage_index, stage in enumerate(build_data.get("progression_stages", []) or []):
        if not isinstance(stage, dict):
            continue
        gear = stage.get("gear_recommendation") or {}
        if not isinstance(gear, dict):
            continue
        for slot_name, item in gear.items():
            if not isinstance(item, dict):
                continue
            payload = dict(item)
            payload.setdefault("slot", slot_name)
            payload.setdefault("_pathcraft_source", f"progression_stages[{stage_index}].gear_recommendation")
            payloads.append(payload)

    return payloads


def _collect_item_mod_lines(item: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    for key in ITEM_MOD_LINE_KEYS:
        value = item.get(key)
        if isinstance(value, str):
            lines.extend(line.strip() for line in value.splitlines() if line.strip())
        elif isinstance(value, (list, tuple, set)):
            lines.extend(_clean_text(line) for line in value if _clean_text(line))
    return lines


def _lookup_name_for_item(item: dict[str, Any]) -> str:
    rarity = _clean_text(item.get("rarity"))
    if rarity.casefold() == "unique":
        for key in ("name", "item", "base_type", "base"):
            value = _clean_text(item.get(key))
            if value:
                return value
    for key in ("base_type", "base", "item", "name"):
        value = _clean_text(item.get(key))
        if value:
            return value
    return ""


def _build_ggpk_item_mod_context(
    index: GGPKIndex,
    lookup_name: str,
    *,
    rarity: str = "",
    item_level: int = 100,
    candidate_limit: int = 8,
) -> dict[str, Any]:
    if not lookup_name:
        return {
            "lookup_name": "",
            "candidate_scope": "unknown_base",
            "join_status": "missing_item_or_base_name",
            "base": None,
            "affix_candidate_counts": None,
        }

    item_info = index.get_item(lookup_name)
    if _is_unique_item(rarity, item_info):
        base_lookup = _clean_text((item_info or {}).get("base_type")) or lookup_name
        return {
            "lookup_name": lookup_name,
            "candidate_scope": "unique_item_base_reference_only",
            "join_status": "unique_item_no_rare_affix_slots",
            "unique": _compact_item_info(item_info),
            "base": _compact_item_info(index.get_item(base_lookup)),
            "affix_candidate_counts": None,
            "candidate_samples": {},
        }

    candidates = index.get_item_mod_candidates(
        lookup_name,
        item_level=item_level,
        limit_per_group=candidate_limit,
    )
    if not candidates:
        return {
            "lookup_name": lookup_name,
            "candidate_scope": "rare_magic_base_or_base_query",
            "join_status": "base_not_found_or_no_affix_candidates",
            "base": _compact_item_info(item_info),
            "affix_candidate_counts": None,
            "candidate_samples": {},
        }

    return {
        "lookup_name": lookup_name,
        "candidate_scope": "rare_magic_base_or_base_query",
        "join_status": "resolved",
        "base": candidates.get("item"),
        "item_level": candidates.get("item_level"),
        "effective_tags": (candidates.get("item") or {}).get("effective_tags") or [],
        "affix_candidate_counts": candidates.get("counts") or {},
        "candidate_samples": {
            group: [_compact_candidate_mod(mod) for mod in mods]
            for group, mods in (candidates.get("mods") or {}).items()
        },
        "truncated": candidates.get("truncated") or {},
    }


def _build_current_item_mod_summary(item: dict[str, Any], rarity: str) -> dict[str, Any]:
    raw_text = _clean_text(item.get("raw_text") or item.get("pob_raw_text"))
    if raw_text:
        raw_parsed = parse_item_raw_text(raw_text, rarity_hint=rarity)
        mods = raw_parsed.get("mods") or []
        return {
            "mod_source": "pob_raw_item_text",
            "raw_name": raw_parsed.get("name"),
            "raw_base_type": raw_parsed.get("base_type"),
            "mod_line_count": len(mods),
            "current_mod_summary": summarize_item_mods(mods),
            "current_mods_sample": [_compact_current_mod(mod) for mod in mods[:8]],
        }

    lines = _collect_item_mod_lines(item)
    mods = parse_item_mod_lines(lines, rarity=rarity) if lines else []
    return {
        "mod_source": "pob_item_mod_lines" if lines else "none",
        "mod_line_count": len(mods),
        "current_mod_summary": summarize_item_mods(mods),
        "current_mods_sample": [_compact_current_mod(mod) for mod in mods[:8]],
    }


def build_item_mod_context(
    entities: dict[str, Any],
    build_data: dict[str, Any] | None = None,
    *,
    game: str = "poe1",
    candidate_limit: int = 8,
) -> dict[str, Any]:
    """Attach PoB-style item text semantics and GGPK affix pools to item entities."""
    index = GGPKIndex(game=game)
    items: list[dict[str, Any]] = []
    seen_lookup_names: set[str] = set()

    for payload in _iter_build_item_payloads(build_data):
        rarity = _clean_text(payload.get("rarity"))
        lookup_name = _lookup_name_for_item(payload)
        if not lookup_name:
            continue
        seen_lookup_names.add(_norm(lookup_name))
        current = _build_current_item_mod_summary(payload, rarity)
        items.append({
            "source": payload.get("_pathcraft_source") or "build_data",
            "slot": payload.get("slot"),
            "name": _clean_text(payload.get("name")),
            "rarity": rarity,
            "base_type": _clean_text(payload.get("base_type") or payload.get("base")),
            "lookup_name": lookup_name,
            **current,
            "ggpk_mod_context": _build_ggpk_item_mod_context(
                index,
                lookup_name,
                rarity=rarity,
                candidate_limit=candidate_limit,
            ),
        })

    for matched_item in entities.get("matched_items", []) or []:
        name = _clean_text(matched_item.get("name"))
        if not name or _norm(name) in seen_lookup_names:
            continue
        base_type = _clean_text(matched_item.get("base_type"))
        if base_type and _norm(base_type) in seen_lookup_names:
            continue
        rarity = "Unique" if matched_item.get("unique_base") else ""
        items.append({
            "source": "query_exact_item_match",
            "slot": None,
            "name": name,
            "rarity": rarity,
            "base_type": base_type,
            "lookup_name": name,
            "mod_source": "none",
            "mod_line_count": 0,
            "current_mod_summary": summarize_item_mods([]),
            "current_mods_sample": [],
            "ggpk_mod_context": _build_ggpk_item_mod_context(
                index,
                name,
                rarity=rarity,
                candidate_limit=candidate_limit,
            ),
        })

    return {
        "schema_version": 1,
        "rule": (
            "PoB-style item handling: parse current item modifier text separately from "
            "GGPK affix availability; unique items lock rare prefix/suffix candidate slots."
        ),
        "items": items,
        "counts": {
            "items": len(items),
            "with_current_mod_lines": sum(1 for item in items if item.get("mod_line_count")),
            "with_resolved_affix_pool": sum(
                1
                for item in items
                if (item.get("ggpk_mod_context") or {}).get("join_status") == "resolved"
            ),
            "unique_locked": sum(
                1
                for item in items
                if (item.get("ggpk_mod_context") or {}).get("join_status") == "unique_item_no_rare_affix_slots"
            ),
        },
    }


def _brand_guide_match_terms(entities: dict[str, Any]) -> set[str]:
    terms = {_norm(term) for term in entities.get("brand_guide_terms", []) if _norm(term)}
    for row in entities.get("matched_gems", []) or []:
        name = _norm(row.get("name"))
        if name:
            terms.add(name)
    return terms


def _matches_terms(payload: dict[str, Any], terms: set[str]) -> bool:
    if not terms:
        return False
    blob = json.dumps(payload, ensure_ascii=False).casefold()
    return any(term in blob for term in terms)


def build_brand_guide_context(
    entities: dict[str, Any],
    *,
    card_limit: int = 8,
    pob_limit: int = 12,
) -> dict[str, Any]:
    guide = _load_json("guide_sources/poe1_brand_guide_zeeboub_v2.json", {})
    if not isinstance(guide, dict) or not guide:
        return {}

    terms = _brand_guide_match_terms(entities)
    cards = guide.get("knowledge_cards", []) or []
    matching_cards = [card for card in cards if _matches_terms(card, terms)]
    if not matching_cards:
        preferred = {
            "penance_brand_mechanics",
            "conversion_sources",
            "swap_requirements",
            "atlas_upgrade_order",
            "pob_configuration",
        }
        matching_cards = [card for card in cards if card.get("card_id") in preferred]

    pobs = guide.get("pob_links", []) or []
    matching_pobs = [pob for pob in pobs if _matches_terms(pob, terms)]
    if not matching_pobs:
        matching_pobs = pobs

    return {
        "schema_version": 1,
        "source_id": guide.get("source_id"),
        "dataset_kind": guide.get("dataset_kind"),
        "source": guide.get("source", {}),
        "scope": guide.get("scope", {}),
        "link_summary": guide.get("link_summary", {}),
        "matched_terms": sorted(terms),
        "knowledge_cards": matching_cards[:card_limit],
        "pob_links": matching_pobs[:pob_limit],
        "phase_model": guide.get("phase_model", []),
        "guardrails": guide.get("guardrails", []),
    }


def build_context_pack(
    query: str = "",
    build_data: dict[str, Any] | None = None,
    game: str = "poe1",
    patch_entry_limit: int = 12,
) -> dict[str, Any]:
    intents = classify_intents(query, build_data)
    entities = extract_entities(query, build_data, game=game)
    sources = select_sources(intents, entities)
    item_mod_context = build_item_mod_context(entities, build_data, game=game)
    brand_guide_context = (
        build_brand_guide_context(entities)
        if any(source["id"] == "brand_guide_zeeboub" for source in sources)
        else {}
    )
    cws_context = {}
    if any(source["id"] == "cws_emiracles_329" for source in sources):
        kb = CWSKnowledgeBase()
        cws_context = {
            "build_id": kb.pack["build_id"],
            "patch": kb.pack["patch"],
            "snapshot_at": kb.pack["snapshot_at"],
            "hits": kb.search(query, limit=8),
            "known_gaps": kb.pack.get("known_gaps", []),
        }
    allie_luminary_context = {}
    if any(source["id"] == "allie_luminary_329" for source in sources):
        kb = LuminaryKnowledgeBase()
        allie_luminary_context = {
            "build_id": kb.pack["build_id"],
            "patch": kb.pack["patch"],
            "snapshot_at": kb.pack["snapshot_at"],
            "hits": kb.search(query, limit=8),
            "known_gaps": kb.pack.get("known_gaps", []),
        }
    sanavixx_cyclone_context = {}
    if any(source["id"] == "sanavixx_cyclone_329" for source in sources):
        kb = SanavixxKnowledgeBase()
        sanavixx_cyclone_context = {
            "build_id": kb.pack["build_id"],
            "patch": kb.pack["patch"],
            "snapshot_at": kb.pack["snapshot_at"],
            "hits": kb.search(query, limit=8),
            "known_gaps": kb.pack.get("known_gaps", []),
        }

    patch_delta = _load_json("patch_notes/poe1_3_29_0_patch_delta_index.json", {})
    patch_entries = (
        _filter_patch_entries(patch_delta, entities, intents, patch_entry_limit)
        if any(source["id"] == "patch_delta" for source in sources)
        else []
    )

    vector_candidates = [
        source["id"]
        for source in sources
        if str(source.get("vectorization", "")).startswith("yes")
        or str(source.get("vectorization", "")).startswith("maybe")
        or str(source.get("vectorization", "")).startswith("hybrid")
    ]

    exact_sources = [
        source["id"]
        for source in sources
        if "exact" in str(source.get("retrieval_mode", "")) or "exact" in str(source.get("vectorization", ""))
    ]

    compact_entities = {
        "game": entities["game"],
        "class": entities.get("class"),
        "ascendancy": entities.get("ascendancy"),
        "gems": [row.get("name") for row in entities.get("matched_gems", [])],
        "items": [row.get("name") for row in entities.get("matched_items", [])],
        "season_terms": entities.get("season_terms", []),
        "farming_terms": entities.get("farming_terms", []),
        "brand_guide_terms": entities.get("brand_guide_terms", []),
        "cws_terms": entities.get("cws_terms", []),
        "allie_luminary_terms": entities.get("allie_luminary_terms", []),
        "sanavixx_cyclone_terms": entities.get("sanavixx_cyclone_terms", []),
        "missing_terms": entities.get("missing_terms", []),
    }

    return {
        "dataset_kind": "pathcraft_knowledge_context_pack",
        "schema_version": 1,
        "game": game,
        "intents": intents,
        "entities": compact_entities,
        "selected_sources": sources,
        "exact_sources": exact_sources,
        "vector_candidates": vector_candidates,
        "item_mod_context": item_mod_context,
        "brand_guide_context": brand_guide_context,
        "cws_context": cws_context,
        "allie_luminary_context": allie_luminary_context,
        "sanavixx_cyclone_context": sanavixx_cyclone_context,
        "patch_entry_sample": [
            {
                "id": entry.get("id"),
                "domain": entry.get("domain"),
                "entity": entry.get("entity"),
                "change_type": entry.get("change_type"),
                "line": entry.get("line"),
                "numeric_delta": entry.get("numeric_delta"),
                "watch_tags": entry.get("watch_tags"),
            }
            for entry in patch_entries
        ],
        "evidence_rule": (
            "Use exact/GGPK sources for ids, stats, supportability, item mods, and passive data. "
            "Use item_mod_context for current item lines, unique slot locks, and GGPK affix pools. "
            "Use brand_guide_context only as creator guide evidence; verify exact current-patch numbers through GGPK/PoB. "
            "Use cws_context for patch-locked Emiracle claims and expose its source_refs; do not infer an exact death cause without user PoB/scene evidence. "
            "Use allie_luminary_context for Allie's current staged guide and keep player, mercenary, Bob, and spectre states separate. "
            "Use sanavixx_cyclone_context for SANAVIXX's staged 3.29 Cyclone guide, HCSSF safety gates, and crafting recipes; do not treat aspirational trade crafts as SSF prerequisites. "
            "Use vector candidates only for unstructured guide/community prose or broad explanation recall."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Route a query/build to Pathcraft knowledge DBs.")
    parser.add_argument("--query", default="", help="User question or short topic.")
    parser.add_argument("--build-json", type=Path, help="Optional build JSON file.")
    parser.add_argument("--game", choices=("poe1", "poe2"), default="poe1")
    args = parser.parse_args(argv)

    build_data = None
    if args.build_json:
        build_data = json.loads(args.build_json.read_text(encoding="utf-8"))
    print(json.dumps(build_context_pack(args.query, build_data, game=args.game), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
