# -*- coding: utf-8 -*-
"""Deterministic readiness screening for a normalized BuildInstance.

This module must stay conservative: it records what the current PoB/gear proves,
what looks risky, and what still requires runtime measurement. It is not a final
"can clear T16" oracle.
"""

from __future__ import annotations

from typing import Any


STATUS_RANK = {
    "ready": 0,
    "candidate": 1,
    "caution": 2,
    "unknown_runtime_inputs": 3,
    "incomplete": 4,
    "blocked_until_verified": 5,
}


def _status(*statuses: str) -> str:
    values = [status for status in statuses if status]
    if not values:
        return "candidate"
    return max(values, key=lambda status: STATUS_RANK.get(status, 0))


def _int(value: Any, default: int = 0) -> int:
    try:
        if value is None or value == "":
            return default
        return int(float(value))
    except (TypeError, ValueError):
        return default


def _casefold(value: Any) -> str:
    return str(value or "").casefold()


def _slot_items(instance: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        item
        for item in ((instance.get("item_state") or {}).get("slots") or [])
        if isinstance(item, dict)
    ]


def _unique_item_names(instance: dict[str, Any]) -> list[str]:
    return [
        str(item.get("name") or "")
        for item in _slot_items(instance)
        if _casefold(item.get("rarity")) == "unique"
    ]


def _count_unique(instance: dict[str, Any], name: str) -> int:
    needle = name.casefold()
    return sum(1 for unique_name in _unique_item_names(instance) if needle in unique_name.casefold())


def _skill_names(instance: dict[str, Any]) -> set[str]:
    names: set[str] = set()
    for group in ((instance.get("gem_state") or {}).get("skill_groups") or []):
        if not isinstance(group, dict):
            continue
        active = group.get("active_gem")
        if active:
            names.add(str(active))
        for gem in group.get("gems") or []:
            if gem:
                names.add(str(gem))
    return names


def _main_skill(instance: dict[str, Any]) -> str:
    return str((((instance.get("gem_state") or {}).get("main_skill_group") or {}).get("active_gem")) or "")


def _gear_totals(instance: dict[str, Any]) -> dict[str, int]:
    totals = ((instance.get("item_state") or {}).get("gear_pressure") or {}).get("gear_numeric_totals") or {}
    return {str(key): _int(value) for key, value in totals.items()}


def _category_counts(instance: dict[str, Any]) -> dict[str, int]:
    counts = ((instance.get("item_state") or {}).get("mod_summary") or {}).get("category_counts") or {}
    return {str(key): _int(value) for key, value in counts.items()}


def _defense_readiness(instance: dict[str, Any]) -> dict[str, Any]:
    calc = instance.get("calc_state") or {}
    flags = calc.get("flags") or {}
    resists = calc.get("resistances") or {}
    totals = _gear_totals(instance)
    categories = _category_counts(instance)
    life = _int(calc.get("life"))
    es = _int(calc.get("energy_shield"))
    ehp = _int(calc.get("ehp")) or life + es
    chaos_res = _int(resists.get("chaos"))
    suppression = totals.get("spell_suppression", 0)

    reasons: list[str] = []
    next_actions: list[str] = []
    statuses = ["candidate"]

    if not flags.get("elemental_res_capped"):
        statuses.append("incomplete")
        reasons.append("elemental_resistances_not_capped")
        next_actions.append("Cap fire/cold/lightning resistances before judging red-map readiness.")

    if ehp <= 0:
        statuses.append("unknown_runtime_inputs")
        reasons.append("ehp_not_available")
    elif ehp < 4500:
        statuses.append("incomplete")
        reasons.append(f"red_map_screen_ehp_low:{ehp}")
        next_actions.append("Raise combined life/ES before pushing red maps.")
    elif ehp < 6000:
        statuses.append("caution")
        reasons.append(f"red_map_screen_ehp_medium:{ehp}")
        next_actions.append("Treat T16/Guardian attempts as test runs until deaths-per-map is measured.")

    if chaos_res < 0:
        statuses.append("caution")
        reasons.append(f"chaos_resistance_negative:{chaos_res}")
        next_actions.append("Use belt/boots/gloves/helmet suffixes to improve chaos resistance.")

    if 0 < suppression < 50:
        statuses.append("caution")
        reasons.append(f"partial_spell_suppression_from_gear:{suppression}")
        next_actions.append("Do not count suppression as a full defensive layer until the total is confirmed near cap.")
    elif suppression == 0 and categories.get("suppression"):
        statuses.append("unknown_runtime_inputs")
        reasons.append("suppression_category_seen_but_numeric_total_missing")

    storm_secret_count = _count_unique(instance, "Storm Secret")
    if storm_secret_count and not any(categories.get(key) for key in ("recovery", "regeneration", "leech")):
        statuses.append("blocked_until_verified")
        reasons.append(f"storm_secret_self_damage_without_recovery_signal:{storm_secret_count}")
        next_actions.append("Verify recovery against Storm Secret self-damage before Guardian maps or Delve/Fossil pushing.")

    return {
        "status": _status(*statuses),
        "judgement_type": "deterministic_screen_not_final_verdict",
        "signals": {
            "life": life,
            "energy_shield": es,
            "ehp": ehp,
            "resistances": resists,
            "chaos_resistance": chaos_res,
            "spell_suppression_from_gear": suppression,
            "storm_secret_count": storm_secret_count,
        },
        "reasons": reasons,
        "next_actions": next_actions,
    }


def _gear_readiness(instance: dict[str, Any]) -> dict[str, Any]:
    item_state = instance.get("item_state") or {}
    gear_pressure = item_state.get("gear_pressure") or {}
    totals = _gear_totals(instance)
    unique_jewellery = gear_pressure.get("unique_jewellery_slots") or []
    rare_suffixes = _int(gear_pressure.get("rare_likely_suffix_mods"))
    resolved_affix_slots = gear_pressure.get("resolved_affix_slots") or []
    empty_slots = gear_pressure.get("empty_expected_slots") or []

    statuses = ["candidate"]
    reasons: list[str] = []
    next_actions: list[str] = []

    if len(unique_jewellery) >= 3:
        statuses.append("incomplete")
        reasons.append(f"very_high_unique_jewellery_suffix_pressure:{','.join(unique_jewellery)}")
        next_actions.append("Avoid adding more unique jewellery; move resists/attributes/suppression to rare armour, belt, and weapon slots.")
    elif len(unique_jewellery) >= 2:
        statuses.append("caution")
        reasons.append(f"high_unique_jewellery_suffix_pressure:{','.join(unique_jewellery)}")
        next_actions.append("Reserve rare suffixes on belt/boots/gloves/helmet for resists, attributes, chaos res, or suppression.")

    if rare_suffixes >= 8:
        statuses.append("caution")
        reasons.append(f"rare_suffix_pressure_high:{rare_suffixes}")

    if empty_slots:
        statuses.append("caution")
        reasons.append(f"empty_expected_slots:{','.join(empty_slots)}")

    if not resolved_affix_slots:
        statuses.append("unknown_runtime_inputs")
        reasons.append("no_rare_affix_slots_resolved_against_ggpk")

    return {
        "status": _status(*statuses),
        "signals": {
            "gear_numeric_totals": totals,
            "unique_jewellery_slots": unique_jewellery,
            "rare_likely_suffix_mods": rare_suffixes,
            "resolved_affix_slots": resolved_affix_slots,
            "empty_expected_slots": empty_slots,
        },
        "reasons": reasons,
        "next_actions": next_actions,
    }


def _mapping_readiness(instance: dict[str, Any], defense: dict[str, Any]) -> dict[str, Any]:
    calc = instance.get("calc_state") or {}
    flags = calc.get("flags") or {}
    dps = _int(calc.get("dps"))
    ehp = _int(calc.get("ehp")) or _int(calc.get("life")) + _int(calc.get("energy_shield"))
    missing_runtime_inputs = [
        "atlas_passives_allocated",
        "voidstones",
        "highest_completed_map_tier",
        "average_t16_clear_time_seconds",
        "deaths_per_map",
        "map_mod_failure_cases",
        "flask_uptime",
    ]

    reasons = ["runtime_mapping_inputs_missing"]
    next_actions = [
        "Record atlas passive count, voidstones, T16 clear time, and deaths per map before selecting aggressive farming."
    ]
    phase = "unknown"
    if flags.get("elemental_res_capped") and ehp >= 4500 and dps >= 1_000_000:
        phase = "red_map_candidate_screen"
        reasons.append("static_pob_screen_passed_for_red_map_trial")
    elif flags.get("elemental_res_capped") and ehp >= 3500:
        phase = "yellow_to_red_transition_screen"
    else:
        phase = "pre_red_mapping_screen"

    return {
        "status": "unknown_runtime_inputs",
        "phase_screen": phase,
        "signals": {
            "dps": dps,
            "ehp": ehp,
            "elemental_res_capped": bool(flags.get("elemental_res_capped")),
            "defense_status": defense.get("status"),
        },
        "missing_runtime_inputs": missing_runtime_inputs,
        "reasons": reasons,
        "next_actions": next_actions,
    }


def _boss_readiness(instance: dict[str, Any], defense: dict[str, Any]) -> dict[str, Any]:
    main_skill = _main_skill(instance)
    skill_names = _skill_names(instance)
    storm_secret_count = _count_unique(instance, "Storm Secret")
    has_boss_shock_starter = bool({"Storm Brand", "Orb of Storms"} & skill_names)

    statuses = ["candidate"]
    reasons: list[str] = []
    next_actions: list[str] = []

    if main_skill == "Herald of Thunder" and storm_secret_count:
        reasons.append("herald_of_thunder_storm_secret_boss_loop_requires_verification")
        if not has_boss_shock_starter:
            statuses.append("blocked_until_verified")
            reasons.append("missing_explicit_boss_shock_starter")
            next_actions.append("Add or verify Storm Brand/Orb of Storms boss shock starter before Guardian maps.")
        else:
            statuses.append("caution")
            reasons.append("boss_shock_starter_present_but_uptime_unmeasured")
            next_actions.append("Measure boss shock uptime on map bosses before Guardian maps.")

    if storm_secret_count and defense.get("status") in {"blocked_until_verified", "incomplete"}:
        statuses.append("blocked_until_verified")
        reasons.append("storm_secret_recovery_or_defense_not_proven")

    return {
        "status": _status(*statuses),
        "signals": {
            "main_skill": main_skill,
            "storm_secret_count": storm_secret_count,
            "has_boss_shock_starter": has_boss_shock_starter,
            "skill_names_sample": sorted(skill_names)[:12],
        },
        "reasons": reasons,
        "next_actions": next_actions,
    }


def _shell_readiness(instance: dict[str, Any]) -> dict[str, Any]:
    identity = instance.get("identity") or {}
    main_skill = _main_skill(instance)
    storm_secret_count = _count_unique(instance, "Storm Secret")
    tags: list[str] = []
    reasons: list[str] = []

    if identity.get("class") == "Scion" and identity.get("ascendancy") == "Reliquarian":
        tags.append("scion_reliquarian")
    if main_skill == "Herald of Thunder":
        tags.append("herald_of_thunder")
    if main_skill == "Herald of Thunder" and storm_secret_count:
        tags.append("hot_autobomber_candidate")
        reasons.append("hot_autobomber_shell_detected")
    if storm_secret_count >= 2:
        tags.append("double_storm_secret")
        reasons.append("double_storm_secret_suffix_and_recovery_gate")

    return {
        "status": "candidate" if tags else "unknown_runtime_inputs",
        "signals": {
            "class": identity.get("class"),
            "ascendancy": identity.get("ascendancy"),
            "target_version": identity.get("target_version"),
            "main_skill": main_skill,
            "storm_secret_count": storm_secret_count,
        },
        "tags": tags,
        "reasons": reasons,
        "next_actions": [
            "Keep fallback branch until shell-specific recovery, boss uptime, and mapping metrics are verified."
        ] if "hot_autobomber_candidate" in tags else [],
    }


def derive_build_readiness(instance: dict[str, Any]) -> dict[str, Any]:
    defense = _defense_readiness(instance)
    gear = _gear_readiness(instance)
    mapping = _mapping_readiness(instance, defense)
    bossing = _boss_readiness(instance, defense)
    shell = _shell_readiness(instance)
    sections = {
        "defense": defense,
        "gear": gear,
        "mapping": mapping,
        "bossing": bossing,
        "shell": shell,
    }
    blockers = [
        f"{name}:{reason}"
        for name, section in sections.items()
        if section.get("status") in {"blocked_until_verified", "incomplete"}
        for reason in (section.get("reasons") or [])[:3]
    ]
    return {
        "schema_version": 1,
        "overall": {
            "status": _status(*(section.get("status", "candidate") for section in sections.values())),
            "blockers": blockers,
            "unknown_runtime_inputs": mapping.get("missing_runtime_inputs", []),
            "rule": "deterministic screening; runtime metrics still override static PoB guesses",
        },
        **sections,
    }


__all__ = ["derive_build_readiness"]
