# -*- coding: utf-8 -*-
"""Normalize parsed PoB data into a BuildInstance state object.

BuildInstance is the bridge between raw/theoretical game data and coaching:

- GGPK answers what can exist.
- PoB answers what this character currently has.
- Lenses compare the two and decide what is missing.
"""

from __future__ import annotations

from typing import Any, Optional

from build_readiness import derive_build_readiness
from build_profile_normalizer import (
    AURA_GEMS,
    GUARD_GEMS,
    HERALD_GEMS,
    UTILITY_GEMS,
    clean_pob_text,
    split_links,
)
from ggpk_index import GGPKIndex
from item_mod_semantics import parse_item_mod_lines, parse_item_raw_text, summarize_item_mods
from passive_tree_graph import load_default_tree_graph
from passive_tree_url import decode_tree_url


EXPECTED_GEAR_SLOTS = {
    "Weapon 1",
    "Weapon 2",
    "Helmet",
    "Body Armour",
    "Gloves",
    "Boots",
    "Amulet",
    "Ring 1",
    "Ring 2",
    "Belt",
}

JEWELLERY_SLOT_NAMES = {"Amulet", "Ring 1", "Ring 2", "Belt"}


def _to_int(value: Any, default: int | None = None) -> int | None:
    try:
        if value is None or value == "N/A":
            return default
        return int(float(value))
    except (TypeError, ValueError):
        return default


def _first_stage(build_data: dict[str, Any]) -> dict[str, Any]:
    stages = build_data.get("progression_stages") or []
    if stages and isinstance(stages[0], dict):
        return stages[0]
    return {}


RESERVATION_DAMAGE_GEMS = {
    "Herald of Agony",
    "Herald of Ash",
    "Herald of Ice",
    "Herald of Thunder",
}


def _gem_role(gems: list[str], label: str) -> str:
    first = gems[0] if gems else ""
    lower = f"{label} {' '.join(gems)}".lower()
    if first in RESERVATION_DAMAGE_GEMS and any(word in lower for word in ("main", "damage", "autobomber", "auto bomber", "clear", "boss")):
        return "reservation_damage"
    if first in AURA_GEMS or first in HERALD_GEMS or "aura" in lower or "herald" in lower:
        return "aura"
    if first in GUARD_GEMS or "guard" in lower:
        return "guard"
    if first in UTILITY_GEMS or any(word in lower for word in ("movement", "travel", "curse", "utility", "trigger")):
        return "utility"
    return "damage"


def _gem_score(group: dict[str, Any]) -> int:
    label = str(group.get("label") or "").lower()
    role = group.get("role")
    score = 0
    if group.get("source") == "primary":
        score += 20
    if role in ("damage", "reservation_damage"):
        score += 30
    if "main" in label:
        score += 40
    if "clear" in label:
        score += 15
    if "boss" in label or "single" in label:
        score += 10
    score += int(group.get("link_count") or 0) * 4
    return score


def _iter_setup_groups(setups: dict[str, Any], *, source: str, skill_set_title: str = "") -> list[dict[str, Any]]:
    groups: list[dict[str, Any]] = []
    for label, payload in (setups or {}).items():
        if isinstance(payload, dict) and "links" not in payload:
            nested_title = clean_pob_text(label)
            for nested in _iter_setup_groups(payload, source=source, skill_set_title=nested_title):
                groups.append(nested)
            continue

        links = payload.get("links", "") if isinstance(payload, dict) else payload
        gems = split_links(links)
        if not gems:
            continue
        clean_label = clean_pob_text(label) or gems[0]
        groups.append({
            "source": source,
            "skill_set_title": clean_pob_text(skill_set_title),
            "label": clean_label,
            "links": clean_pob_text(links),
            "active_gem": gems[0],
            "support_gems": gems[1:],
            "gems": gems,
            "link_count": len(gems),
            "role": _gem_role(gems, clean_label),
        })
    return groups


def _build_gem_state(stage: dict[str, Any], pob_raw: dict[str, Any] | None = None) -> dict[str, Any]:
    groups = _iter_setup_groups(stage.get("gem_setups") or {}, source="primary", skill_set_title=stage.get("stage_name") or "")
    groups.extend(_iter_setup_groups(stage.get("alternate_gem_sets") or {}, source="alternate"))

    main_group = None
    damage_groups = [group for group in groups if group.get("role") in ("damage", "reservation_damage")]
    if damage_groups:
        main_group = max(damage_groups, key=_gem_score)
    elif groups:
        main_group = max(groups, key=_gem_score)

    return {
        "main_skill_group": main_group,
        "skill_groups": groups,
        "counts": {
            "groups": len(groups),
            "damage_groups": sum(1 for group in groups if group.get("role") == "damage"),
            "reservation_damage_groups": sum(1 for group in groups if group.get("role") == "reservation_damage"),
            "aura_groups": sum(1 for group in groups if group.get("role") == "aura"),
            "utility_groups": sum(1 for group in groups if group.get("role") == "utility"),
            "guard_groups": sum(1 for group in groups if group.get("role") == "guard"),
        },
        "raw_summary": {
            "skill_set_count": len(((pob_raw or {}).get("skills") or {}).get("skill_sets", [])),
            "legacy_skill_count": len(((pob_raw or {}).get("skills") or {}).get("legacy_skills", [])),
            "active_skill_set_id": ((pob_raw or {}).get("skills") or {}).get("active_skill_set_id", ""),
        },
    }


def _lookup_item_mod_context(index: GGPKIndex, item: dict[str, Any]) -> dict[str, Any]:
    rarity = clean_pob_text(item.get("rarity"))
    name = clean_pob_text(item.get("name"))
    base_type = clean_pob_text(item.get("base_type"))
    lookup_name = base_type or name

    if rarity.casefold() == "unique" and name:
        base_info = index.get_item(name)
        if not base_info and base_type:
            base_info = index.get_item(base_type)
        return {
            "candidate_scope": "base_reference_only_unique_item_no_rare_affix_slots",
            "base": base_info,
            "affix_candidate_counts": None,
            "join_status": "unique_slot_locked",
        }

    if not lookup_name:
        return {
            "candidate_scope": "unknown_base",
            "base": None,
            "affix_candidate_counts": None,
            "join_status": "missing_base_name",
        }

    candidates = index.get_item_mod_candidates(lookup_name, item_level=100, limit_per_group=0)
    if not candidates:
        return {
            "candidate_scope": "rare_magic_base",
            "base": index.get_item(lookup_name),
            "affix_candidate_counts": None,
            "join_status": "base_not_found_or_no_affix_candidates",
        }

    return {
        "candidate_scope": "rare_magic_base",
        "base": candidates["item"],
        "affix_candidate_counts": candidates["counts"],
        "effective_tags": candidates["item"].get("effective_tags", []),
        "join_status": "resolved",
    }


def _raw_items_by_active_slot(pob_raw: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    raw_items = ((pob_raw or {}).get("items") or {})
    item_map = raw_items.get("items") or {}
    item_sets = raw_items.get("item_sets") or []
    active_id = raw_items.get("active_item_set_id", "")
    active_set = next((row for row in item_sets if row.get("id") == active_id), None)
    if active_set is None and item_sets:
        active_set = item_sets[0]
    if not active_set:
        return {}

    by_slot: dict[str, dict[str, Any]] = {}
    for slot in active_set.get("slots") or []:
        slot_name = clean_pob_text(slot.get("name"))
        item_id = clean_pob_text(slot.get("item_id"))
        if slot_name and item_id and item_id in item_map:
            by_slot[slot_name] = item_map[item_id]
    return by_slot


def _build_item_affix_pressure(item: dict[str, Any]) -> dict[str, Any]:
    summary = item.get("mod_summary") or {}
    generation_counts = summary.get("likely_generation_counts") or {}
    category_counts = summary.get("category_counts") or {}
    context = item.get("ggpk_mod_context") or {}
    candidate_counts = context.get("affix_candidate_counts") or {}
    suffix_pressure_categories = [
        category
        for category in (
            "resistance",
            "fire_resistance",
            "cold_resistance",
            "lightning_resistance",
            "chaos_resistance",
            "attribute",
            "suppression",
        )
        if category_counts.get(category)
    ]
    return {
        "likely_prefix_mods": int(generation_counts.get("prefix") or 0),
        "likely_suffix_mods": int(generation_counts.get("suffix") or 0),
        "likely_unique_mods": int(generation_counts.get("unique_modifier") or 0),
        "unknown_or_mixed_mods": sum(
            int(generation_counts.get(key) or 0)
            for key in ("unknown", "mixed_or_veiled", "crafted_unknown", "fractured_unknown")
        ),
        "suffix_pressure_categories": suffix_pressure_categories,
        "candidate_pool_status": (
            "suffix_pool_available"
            if context.get("join_status") == "resolved" and candidate_counts.get("suffix")
            else "unique_or_no_rare_affix_pool"
            if context.get("join_status") == "unique_slot_locked"
            else "candidate_pool_unresolved"
        ),
    }


def _build_item_state(
    stage: dict[str, Any],
    *,
    include_ggpk_context: bool,
    index: Optional[GGPKIndex],
    pob_raw: dict[str, Any] | None = None,
) -> dict[str, Any]:
    gear = stage.get("gear_recommendation") or {}
    raw_by_slot = _raw_items_by_active_slot(pob_raw)
    slots: list[dict[str, Any]] = []

    for slot_name, payload in gear.items():
        if not isinstance(payload, dict):
            continue
        clean_slot = clean_pob_text(slot_name)
        raw_item = raw_by_slot.get(clean_slot)
        raw_parsed = parse_item_raw_text(raw_item.get("raw_text", ""), rarity_hint=payload.get("rarity", "")) if raw_item else None
        item = {
            "slot": clean_slot,
            "name": clean_pob_text(payload.get("name") or (raw_parsed or {}).get("name")),
            "rarity": clean_pob_text(payload.get("rarity") or (raw_parsed or {}).get("rarity")),
            "base_type": clean_pob_text(payload.get("base_type") or (raw_parsed or {}).get("base_type")),
            "sockets": clean_pob_text(payload.get("sockets")),
            "explicit_mods": [clean_pob_text(mod) for mod in payload.get("mods", []) if clean_pob_text(mod)],
        }
        if include_ggpk_context and index is not None:
            item["ggpk_mod_context"] = _lookup_item_mod_context(index, item)
        if raw_parsed:
            mod_state = raw_parsed.get("mods") or []
            item["mod_source"] = "pob_raw_item_text"
            item["raw_item_id"] = raw_item.get("id")
        else:
            mod_state = parse_item_mod_lines(item["explicit_mods"], rarity=item.get("rarity", ""))
            item["mod_source"] = "stage_gear_recommendation_mods"
        item["mod_state"] = mod_state
        item["mod_summary"] = summarize_item_mods(mod_state)
        item["affix_pressure"] = _build_item_affix_pressure(item)
        slots.append(item)

    rarity_counts: dict[str, int] = {}
    for item in slots:
        rarity = item.get("rarity") or "Unknown"
        rarity_counts[rarity] = rarity_counts.get(rarity, 0) + 1

    locked_unique_slots = [item["slot"] for item in slots if str(item.get("rarity")).casefold() == "unique"]
    rare_slots = [item["slot"] for item in slots if str(item.get("rarity")).casefold() == "rare"]
    empty_expected_slots = sorted(EXPECTED_GEAR_SLOTS - {item["slot"] for item in slots})
    resolved_affix_slots = [
        item["slot"]
        for item in slots
        if (item.get("ggpk_mod_context") or {}).get("join_status") == "resolved"
    ]
    all_mods = [
        mod
        for item in slots
        for mod in item.get("mod_state", [])
    ]
    mod_summary = summarize_item_mods(all_mods)

    return {
        "slots": slots,
        "mod_summary": mod_summary,
        "raw_summary": {
            "item_count": len(((pob_raw or {}).get("items") or {}).get("items", {})),
            "item_set_count": len(((pob_raw or {}).get("items") or {}).get("item_sets", [])),
            "active_item_set_id": ((pob_raw or {}).get("items") or {}).get("active_item_set_id", ""),
        },
        "gear_pressure": {
            "slot_count": len(slots),
            "rarity_counts": rarity_counts,
            "locked_unique_slots": locked_unique_slots,
            "unique_jewellery_slots": [
                item["slot"]
                for item in slots
                if item["slot"] in JEWELLERY_SLOT_NAMES and str(item.get("rarity")).casefold() == "unique"
            ],
            "rare_slots": rare_slots,
            "empty_expected_slots": empty_expected_slots,
            "resolved_affix_slots": resolved_affix_slots,
            "rare_likely_prefix_mods": sum(
                int((item.get("affix_pressure") or {}).get("likely_prefix_mods") or 0)
                for item in slots
                if str(item.get("rarity")).casefold() in {"rare", "magic"}
            ),
            "rare_likely_suffix_mods": sum(
                int((item.get("affix_pressure") or {}).get("likely_suffix_mods") or 0)
                for item in slots
                if str(item.get("rarity")).casefold() in {"rare", "magic"}
            ),
            "gear_numeric_totals": mod_summary.get("numeric_totals", {}),
        },
    }


def _build_tree_state(
    stage: dict[str, Any],
    pob_raw: dict[str, Any] | None = None,
    index: Optional[GGPKIndex] = None,
) -> dict[str, Any]:
    options = stage.get("passive_tree_options") or []
    active = next((option for option in options if isinstance(option, dict) and option.get("active")), None)
    raw_tree = (pob_raw or {}).get("tree") or {}
    active_tree_url = clean_pob_text(stage.get("passive_tree_url") or (active or {}).get("url"))
    decoded = decode_tree_url(active_tree_url)
    mastery_effects = (decoded or {}).get("mastery_effects") or {}
    graph_summary = None
    try:
        if decoded:
            graph_summary = load_default_tree_graph().connectivity_summary(
                (decoded or {}).get("nodes", []),
                class_index=(decoded or {}).get("class_index"),
            )
    except Exception:
        graph_summary = None
    semantic_lookup = (
        index.get_passives_by_graph_ids((decoded or {}).get("nodes", []))
        if decoded and index is not None
        else {"resolved": [], "missing": (decoded or {}).get("nodes", []), "counts": {}}
    )
    semantic_nodes = semantic_lookup.get("resolved", [])
    semantic_by_node_id = {node.get("node_id"): node for node in semantic_nodes}
    stat_category_counts: dict[str, int] = {}
    for node in semantic_nodes:
        for category in node.get("stat_categories") or []:
            stat_category_counts[category] = stat_category_counts.get(category, 0) + 1
    semantic_masteries = []
    for node_id, effect_id in sorted(mastery_effects.items()):
        node_info = semantic_by_node_id.get(node_id)
        semantic_masteries.append({
            "node_id": node_id,
            "effect_id": effect_id,
            "node_name": node_info.get("name") if node_info else None,
            "node_found": node_info is not None,
        })
    return {
        "active_tree_url": active_tree_url,
        "passive_tree_options": options,
        "raw_spec_count": len(raw_tree.get("specs", [])),
        "raw_active_spec_id": raw_tree.get("active_spec_id", ""),
        "decoded_active_tree": decoded,
        "graph_summary": graph_summary,
        "allocated_passives": (decoded or {}).get("nodes", []),
        "semantic_nodes": semantic_nodes,
        "missing_semantic_node_ids": semantic_lookup.get("missing", []),
        "semantic_counts": semantic_lookup.get("counts", {}),
        "stat_category_counts": dict(sorted(stat_category_counts.items())),
        "notables": [
            {
                "node_id": node.get("node_id"),
                "name": node.get("name"),
                "id": node.get("id"),
                "stat_categories": node.get("stat_categories") or [],
            }
            for node in semantic_nodes
            if node.get("is_notable")
        ],
        "masteries": semantic_masteries,
        "keystones": [
            {
                "node_id": node.get("node_id"),
                "name": node.get("name"),
                "id": node.get("id"),
                "stat_categories": node.get("stat_categories") or [],
            }
            for node in semantic_nodes
            if node.get("is_keystone")
        ],
        "jewel_sockets": [
            {"node_id": node.get("node_id"), "name": node.get("name"), "id": node.get("id")}
            for node in semantic_nodes
            if node.get("is_jewel_socket")
        ],
        "parse_status": (
            "decoded_and_mapped_official_tree_url"
            if decoded and semantic_nodes
            else "decoded_official_tree_url"
            if decoded and index is None
            else "decoded_official_tree_url_no_semantic_matches"
            if decoded
            else "tree_url_present_but_not_decodable" if active_tree_url else "missing_tree_url"
        ),
    }


def _build_calc_state(build_data: dict[str, Any]) -> dict[str, Any]:
    stats = build_data.get("stats") or {}
    res = stats.get("resistances") or {}
    elemental_resists = {
        key: _to_int(res.get(key), 0) or 0
        for key in ("fire", "cold", "lightning")
    }
    return {
        "dps": _to_int(stats.get("dps"), 0) or 0,
        "life": _to_int(stats.get("life"), 0) or 0,
        "energy_shield": _to_int(stats.get("energy_shield"), 0) or 0,
        "ehp": _to_int(stats.get("ehp"), 0) or 0,
        "resistances": {
            **elemental_resists,
            "chaos": _to_int(res.get("chaos"), 0) or 0,
        },
        "defences": {
            "armour": _to_int(stats.get("armour"), 0) or 0,
            "evasion": _to_int(stats.get("evasion"), 0) or 0,
            "block": _to_int(stats.get("block"), 0) or 0,
            "spell_block": _to_int(stats.get("spell_block"), 0) or 0,
            "suppression": None,
            "ailment_avoidance": None,
            "recovery": None,
        },
        "flags": {
            "elemental_res_capped": all(value >= 75 for value in elemental_resists.values()),
            "chaos_res_negative": (_to_int(res.get("chaos"), 0) or 0) < 0,
            "has_xml_stats": bool((build_data.get("meta") or {}).get("has_xml_stats")),
        },
    }


def _build_config_state(stage: dict[str, Any], pob_raw: dict[str, Any] | None = None) -> dict[str, Any]:
    raw_config = (pob_raw or {}).get("config") or {}
    raw_inputs = raw_config.get("inputs") if isinstance(raw_config.get("inputs"), dict) else {}
    return {
        "bandit": clean_pob_text(stage.get("bandit")),
        "pantheon": stage.get("pantheon") or {},
        "charges": {"power": None, "frenzy": None, "endurance": None},
        "enemy": {"pinnacle": None, "guardian": None, "mapping": None},
        "flasks": {"uptime": None, "guarded_by_pob_config": False},
        "raw_config_present": bool(raw_config.get("present")),
        "raw_inputs": raw_inputs,
        "assumption_status": (
            "PoB Config raw inputs are preserved but not semantically normalized yet."
            if raw_config.get("present")
            else "PoB Config tab is not available; missing values must not be invented."
        ),
    }


def _build_lenses(item_state: dict[str, Any], calc_state: dict[str, Any]) -> dict[str, Any]:
    gear_pressure = item_state["gear_pressure"]
    return {
        "gear_pressure": {
            **gear_pressure,
            "suffix_pressure_signals": {
                "unique_jewellery_slots": len(gear_pressure["unique_jewellery_slots"]),
                "rare_likely_suffix_mods": gear_pressure.get("rare_likely_suffix_mods", 0),
                "gear_numeric_totals": gear_pressure.get("gear_numeric_totals", {}),
                "note": "Unique jewellery reduces rare suffix room for resistances/attributes.",
            },
        },
        "t16_readiness_inputs": {
            "life": calc_state["life"],
            "energy_shield": calc_state["energy_shield"],
            "ehp": calc_state["ehp"],
            "dps": calc_state["dps"],
            "elemental_res_capped": calc_state["flags"]["elemental_res_capped"],
            "chaos_resistance": calc_state["resistances"]["chaos"],
            "missing_runtime_inputs": [
                "atlas_passives_allocated",
                "average_t16_clear_time_seconds",
                "deaths_per_map",
                "map_mod_policy",
                "flask_uptime",
                "suppression_or_max_hit",
            ],
            "judgement_status": "inputs_only_not_final_verdict",
        },
    }


def build_instance_from_pob_data(
    build_data: dict[str, Any],
    *,
    include_ggpk_context: bool = True,
    index: Optional[GGPKIndex] = None,
) -> dict[str, Any]:
    """Return a normalized BuildInstance from the existing parsed PoB schema."""
    meta = build_data.get("meta") or {}
    stage = _first_stage(build_data)
    pob_raw = build_data.get("pob_raw") if isinstance(build_data.get("pob_raw"), dict) else None
    level = _to_int(str(meta.get("build_name", "")).split("Lvl")[-1].strip(), None)
    if level is None:
        level = _to_int(meta.get("level"), None)

    ggpk = index if index is not None else (GGPKIndex(game="poe1") if include_ggpk_context else None)
    item_state = _build_item_state(stage, include_ggpk_context=include_ggpk_context, index=ggpk, pob_raw=pob_raw)
    calc_state = _build_calc_state(build_data)

    instance = {
        "schema_version": 1,
        "source": {
            "type": "pob_parser_output",
            "pob_link": clean_pob_text(meta.get("pob_link") or stage.get("pob_link")),
            "parser": "python/pob_parser.py",
            "raw_available": pob_raw is not None,
        },
        "identity": {
            "build_name": clean_pob_text(meta.get("build_name")),
            "class": clean_pob_text(meta.get("class")),
            "ascendancy": clean_pob_text(meta.get("ascendancy")),
            "level": level,
            "target_version": clean_pob_text(meta.get("version")),
        },
        "tree_state": _build_tree_state(stage, pob_raw=pob_raw, index=ggpk),
        "item_state": item_state,
        "gem_state": _build_gem_state(stage, pob_raw=pob_raw),
        "config_state": _build_config_state(stage, pob_raw=pob_raw),
        "calc_state": calc_state,
        "lenses": _build_lenses(item_state, calc_state),
        "evidence_quality": {
            "has_xml_stats": bool(meta.get("has_xml_stats")),
            "has_pob_raw": pob_raw is not None,
            "item_mod_context": "ggpk_joined" if include_ggpk_context else "disabled",
            "known_missing_layers": [
                "passive_mastery_effect_text_lookup",
                "pob_config_tab_normalizer",
                "ggpk_stats_table_extraction_for_non_passive_mods",
                "crafted_influence_fossil_acquisition_lens",
            ],
        },
    }
    instance["readiness"] = derive_build_readiness(instance)
    return instance


normalize_build_instance = build_instance_from_pob_data
