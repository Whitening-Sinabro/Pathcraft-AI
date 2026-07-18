# -*- coding: utf-8 -*-
"""Normalize parsed PoB/coaching data into a stricter progression profile."""

from __future__ import annotations

import re
from collections import defaultdict
from typing import Any

AURA_GEMS = {
    "Anger",
    "Arctic Armour",
    "Aspect of the Avian",
    "Aspect of the Cat",
    "Aspect of the Crab",
    "Aspect of the Spider",
    "Clarity",
    "Defiance Banner",
    "Determination",
    "Discipline",
    "Dread Banner",
    "Flesh and Stone",
    "Grace",
    "Haste",
    "Hatred",
    "Malevolence",
    "Petrified Blood",
    "Precision",
    "Purity of Elements",
    "Purity of Fire",
    "Purity of Ice",
    "Purity of Lightning",
    "Skitterbots",
    "Tempest Shield",
    "Vitality",
    "War Banner",
    "Wrath",
    "Zealotry",
}
HERALD_GEMS = {
    "Herald of Agony",
    "Herald of Ash",
    "Herald of Ice",
    "Herald of Purity",
    "Herald of Thunder",
}
GUARD_GEMS = {
    "Arcane Cloak",
    "Bone Armour",
    "Frost Shield",
    "Immortal Call",
    "Molten Shell",
    "Steelskin",
}
UTILITY_GEMS = {
    "Automation",
    "Bone Offering",
    "Conductivity",
    "Convocation",
    "Dash",
    "Desecrate",
    "Despair",
    "Elemental Weakness",
    "Enfeeble",
    "Faster Attacks",
    "Flame Dash",
    "Flesh Offering",
    "Frostblink",
    "Leap Slam",
    "Minefield",
    "Shield Charge",
    "Sigil of Power",
    "Sniper's Mark",
    "Temporal Chains",
    "Wave of Conviction",
    "Whirling Blades",
}
COLOR_CODE_RE = re.compile(r"\^x[0-9A-Fa-f]{6}|\^[0-9A-Fa-f]|\{\d+\}")
LEVEL_RANGE_RE = re.compile(r"(\d+)(?:\s*[-+]\s*(\d+))?")

_STAGE_RULES = [
    (re.compile(r"\bact\s*1\s*-\s*3\b", re.IGNORECASE), ("act_1_3", "1-33", 15)),
    (re.compile(r"\bact\s*1\b", re.IGNORECASE), ("act_1", "1-11", 10)),
    (re.compile(r"\bact\s*2\b", re.IGNORECASE), ("act_2", "12-22", 20)),
    (re.compile(r"\bact\s*3\b", re.IGNORECASE), ("act_3", "23-33", 30)),
    (re.compile(r"\bact\s*4\s*-\s*10\b", re.IGNORECASE), ("act_4_10", "34-67", 40)),
    (re.compile(r"\bact\s*4\s*-\s*6\b", re.IGNORECASE), ("act_4_6", "34-51", 40)),
    (re.compile(r"\bact\s*5\s*-\s*10\b", re.IGNORECASE), ("act_5_10", "41-67", 50)),
    (re.compile(r"\bact\s*7\s*-\s*10\b", re.IGNORECASE), ("act_7_10", "52-67", 70)),
    (re.compile(r"\bact\s*4\b", re.IGNORECASE), ("act_4", "34-40", 40)),
    (re.compile(r"\bact\s*5\b", re.IGNORECASE), ("act_5", "41-45", 50)),
    (re.compile(r"\bact\s*6\b", re.IGNORECASE), ("act_6", "46-51", 60)),
    (re.compile(r"\bact\s*7\b", re.IGNORECASE), ("act_7", "52-57", 70)),
    (re.compile(r"\bact\s*8\b", re.IGNORECASE), ("act_8", "58-62", 80)),
    (re.compile(r"\bact\s*9\b", re.IGNORECASE), ("act_9", "63-66", 90)),
    (re.compile(r"\bact\s*10\b", re.IGNORECASE), ("act_10", "67-67", 100)),
    (re.compile(r"\blv(?:l|ling)?\s*70\b|\b3rd\s*lab\b", re.IGNORECASE), ("early_maps", "68-74", 110)),
    (re.compile(r"\bearly\b", re.IGNORECASE), ("early_maps", "68-79", 120)),
    (re.compile(r"\bmid\b", re.IGNORECASE), ("midgame", "80-92", 130)),
    (re.compile(r"\blate\b", re.IGNORECASE), ("late_endgame", "93-100", 140)),
    (re.compile(r"\bleveling\b|\bcampaign\b", re.IGNORECASE), ("campaign", "1-67", 25)),
    (re.compile(r"\bfinal\b", re.IGNORECASE), ("final_build", None, 200)),
]


def clean_pob_text(value: str | None) -> str:
    text = str(value or "")
    text = COLOR_CODE_RE.sub("", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip(" -_\t\r\n")


def split_links(links: str | None) -> list[str]:
    return [clean_pob_text(part) for part in str(links or "").split(" - ") if clean_pob_text(part)]


def _unique(items: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        clean = clean_pob_text(item)
        if not clean or clean in seen:
            continue
        seen.add(clean)
        ordered.append(clean)
    return ordered


def _classify_level(level: int | None) -> tuple[str, str | None, int]:
    if level is None:
        return "unknown", None, 999
    if level <= 11:
        return "act_1", "1-11", 10
    if level <= 22:
        return "act_2", "12-22", 20
    if level <= 33:
        return "act_3", "23-33", 30
    if level <= 40:
        return "act_4", "34-40", 40
    if level <= 45:
        return "act_5", "41-45", 50
    if level <= 51:
        return "act_6", "46-51", 60
    if level <= 57:
        return "act_7", "52-57", 70
    if level <= 62:
        return "act_8", "58-62", 80
    if level <= 66:
        return "act_9", "63-66", 90
    if level <= 67:
        return "act_10", "67-67", 100
    if level <= 79:
        return "early_maps", "68-79", 120
    if level <= 92:
        return "midgame", "80-92", 130
    return "late_endgame", "93-100", 140


def _classify_level_range(level_range: str | None) -> tuple[str, str | None, int]:
    text = clean_pob_text(level_range)
    match = LEVEL_RANGE_RE.search(text)
    if not match:
        return "unknown", text or None, 999
    start = int(match.group(1))
    stage, inferred_range, order = _classify_level(start)
    return stage, text or inferred_range, order


def classify_stage(label: str | None) -> dict[str, Any]:
    clean = clean_pob_text(label)
    for pattern, (stage, level_range, order) in _STAGE_RULES:
        if pattern.search(clean):
            return {
                "stage": stage,
                "stage_label": clean or stage,
                "level_range": level_range,
                "order": order,
            }

    lower = clean.lower()
    level_match = re.search(r"\blv(?:l|ling)?\s*(\d+)\b", lower)
    if level_match:
        stage, level_range, order = _classify_level(int(level_match.group(1)))
        return {
            "stage": stage,
            "stage_label": clean,
            "level_range": level_range,
            "order": order,
        }

    stage, level_range, order = _classify_level_range(clean)
    return {
        "stage": stage,
        "stage_label": clean or "Unknown",
        "level_range": level_range,
        "order": order,
    }


def _is_aura_gem(gem: str) -> bool:
    return gem in AURA_GEMS or gem in HERALD_GEMS


def _is_guard_gem(gem: str) -> bool:
    return gem in GUARD_GEMS


def _is_utility_gem(gem: str) -> bool:
    return gem in UTILITY_GEMS


def _is_utility_setup(label: str, gems: list[str]) -> bool:
    text = f"{clean_pob_text(label)} {' '.join(gems)}".lower()
    utility_keywords = (
        "aura",
        "herald",
        "curse",
        "guard",
        "movement",
        "utility",
        "trigger",
        "mobility",
    )
    return any(keyword in text for keyword in utility_keywords) or all(
        _is_aura_gem(gem) or _is_guard_gem(gem) or _is_utility_gem(gem)
        for gem in gems
    )


def _score_setup(label: str, gems: list[str], source: str) -> int:
    lower = clean_pob_text(label).lower()
    first = gems[0].lower() if gems else ""
    score = 0
    if source == "primary":
        score += 20
    if "main" in lower:
        score += 50
    if "clear" in lower:
        score += 20
    if "boss" in lower:
        score += 10
    if clean_pob_text(label).lower() == first:
        score += 20
    score += len(gems) * 3
    if _is_utility_setup(label, gems):
        score -= 50
    return score


def _iter_nested_setups(setups: dict[str, Any]) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for label, payload in (setups or {}).items():
        if isinstance(payload, dict) and "links" not in payload:
            entries.extend(_iter_nested_setups(payload))
            continue
        links = payload.get("links", "") if isinstance(payload, dict) else payload
        gems = split_links(links)
        if not gems:
            continue
        entries.append({
            "label": clean_pob_text(label),
            "links": clean_pob_text(links),
            "gems": gems,
        })
    return entries


def _extract_plan_from_setups(
    stage_label: str,
    setups: dict[str, Any],
    *,
    source: str,
) -> dict[str, Any] | None:
    entries = _iter_nested_setups(setups)
    if not entries:
        return None

    offensive = [entry for entry in entries if not _is_utility_setup(entry["label"], entry["gems"])]
    best = max(offensive or entries, key=lambda entry: _score_setup(entry["label"], entry["gems"], source))

    auras: list[str] = []
    utility: list[str] = []
    guard: list[str] = []
    for entry in entries:
        for gem in entry["gems"]:
            if _is_guard_gem(gem):
                guard.append(gem)
            elif _is_aura_gem(gem):
                auras.append(gem)
            elif _is_utility_gem(gem):
                utility.append(gem)

    stage_info = classify_stage(stage_label)
    return {
        "stage": stage_info["stage"],
        "stage_label": stage_info["stage_label"],
        "level_range": stage_info["level_range"],
        "main_skill": best["gems"][0],
        "support_links": best["gems"][1:],
        "auras": _unique(auras),
        "utility": _unique(utility),
        "guard": _unique(guard),
        "source": source,
        "notes": f"Derived from {source.replace('_', ' ')} stage '{stage_info['stage_label']}'.",
        "order": stage_info["order"],
    }


def _campaign_plan_from_coach(coach_data: dict[str, Any]) -> list[dict[str, Any]]:
    recommended = ((coach_data or {}).get("leveling_skills") or {}).get("recommended") or {}
    progressions = recommended.get("links_progression") or []
    result: list[dict[str, Any]] = []
    for index, step in enumerate(progressions):
        gems = _unique(step.get("gems") or [])
        if not gems:
            continue
        stage, level_range, order = _classify_level_range(step.get("level_range"))
        result.append({
            "stage": stage,
            "stage_label": clean_pob_text(step.get("level_range") or f"Step {index + 1}"),
            "level_range": clean_pob_text(step.get("level_range")) or level_range,
            "main_skill": gems[0],
            "support_links": gems[1:],
            "auras": [],
            "utility": [],
            "guard": [],
            "source": "coach_data",
            "notes": clean_pob_text(step.get("reason") or "Coach-provided leveling gem progression."),
            "order": order + index,
        })
    return result


def _campaign_plan_from_build(build_data: dict[str, Any]) -> list[dict[str, Any]]:
    stage = (build_data.get("progression_stages") or [{}])[0]
    alt_sets = stage.get("alternate_gem_sets") or {}
    result: list[dict[str, Any]] = []
    for title, payload in alt_sets.items():
        plan = _extract_plan_from_setups(title, payload, source="alternate_skillset")
        if plan:
            result.append(plan)
    return result


def _build_campaign_plan(build_data: dict[str, Any], coach_data: dict[str, Any]) -> list[dict[str, Any]]:
    campaign = _campaign_plan_from_coach(coach_data)
    if not campaign:
        campaign = _campaign_plan_from_build(build_data)
    campaign.sort(key=lambda item: (item.get("order", 999), item.get("stage_label", "")))
    for item in campaign:
        item.pop("order", None)
    return campaign


def _build_final_stage_plan(build_data: dict[str, Any]) -> dict[str, Any] | None:
    stage = (build_data.get("progression_stages") or [{}])[0]
    return _extract_plan_from_setups(stage.get("stage_name") or "Final Build", stage.get("gem_setups") or {}, source="primary")


def _build_aura_plan(
    build_data: dict[str, Any],
    coach_data: dict[str, Any],
    campaign_plan: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    coach_phases = (coach_data or {}).get("aura_utility_progression") or []
    if coach_phases:
        result = []
        for index, phase in enumerate(coach_phases):
            stage_info = classify_stage(phase.get("phase"))
            auras = _unique((phase.get("auras") or []) + (phase.get("heralds") or []))
            guard = _unique([phase.get("guard")] if isinstance(phase.get("guard"), str) else phase.get("guard") or [])
            utility = _unique(phase.get("utility") or [])
            result.append({
                "stage": stage_info["stage"],
                "stage_label": stage_info["stage_label"],
                "level_range": stage_info["level_range"],
                "auras": auras,
                "utility": utility,
                "guard": guard,
                "source": "coach_data",
                "notes": clean_pob_text(phase.get("reason") or phase.get("reservation_total") or "Coach-provided aura plan."),
                "order": stage_info["order"] + index,
            })
        result.sort(key=lambda item: (item.get("order", 999), item.get("stage_label", "")))
        for item in result:
            item.pop("order", None)
        return result

    fallback: list[dict[str, Any]] = []
    for step in campaign_plan:
        if step.get("auras") or step.get("utility") or step.get("guard"):
            fallback.append({
                "stage": step["stage"],
                "stage_label": step["stage_label"],
                "level_range": step.get("level_range"),
                "auras": step.get("auras", []),
                "utility": step.get("utility", []),
                "guard": step.get("guard", []),
                "source": step.get("source", "alternate_skillset"),
                "notes": step.get("notes"),
                "order": classify_stage(step.get("stage_label"))["order"],
            })

    final_stage = _build_final_stage_plan(build_data)
    if final_stage and (final_stage.get("auras") or final_stage.get("utility") or final_stage.get("guard")):
        fallback.append({
            "stage": "final_build",
            "stage_label": final_stage.get("stage_label") or "Final Build",
            "level_range": None,
            "auras": final_stage.get("auras", []),
            "utility": final_stage.get("utility", []),
            "guard": final_stage.get("guard", []),
            "source": "primary",
            "notes": "Derived from active final gem setups.",
            "order": 200,
        })

    fallback.sort(key=lambda item: (item.get("order", 999), item.get("stage_label", "")))
    for item in fallback:
        item.pop("order", None)
    return fallback


def _build_passive_plan(build_data: dict[str, Any], coach_data: dict[str, Any]) -> list[dict[str, Any]]:
    stage = (build_data.get("progression_stages") or [{}])[0]
    options = stage.get("passive_tree_options") or []
    result: list[dict[str, Any]] = []
    seen_urls: set[str] = set()
    for option in options:
        url = clean_pob_text(option.get("url"))
        if not url or url in seen_urls:
            continue
        seen_urls.add(url)
        title = clean_pob_text(option.get("title") or ("Active Tree" if option.get("active") else "Passive Tree"))
        stage_info = classify_stage(title)
        result.append({
            "stage": stage_info["stage"],
            "stage_label": stage_info["stage_label"],
            "level_range": stage_info["level_range"],
            "tree_url": url,
            "active": bool(option.get("active")),
            "source": "pob_tree_spec",
            "priorities": [],
            "notes": f"PoB tree spec '{title}'.",
            "order": stage_info["order"],
        })

    if not result and clean_pob_text(stage.get("passive_tree_url")):
        result.append({
            "stage": "final_build",
            "stage_label": "Final Passive Tree",
            "level_range": None,
            "tree_url": clean_pob_text(stage.get("passive_tree_url")),
            "active": True,
            "source": "primary_stage",
            "priorities": [],
            "notes": "Only active passive tree URL was available in parsed PoB data.",
            "order": 200,
        })

    passive_priority = _unique((coach_data or {}).get("passive_priority") or [])
    if passive_priority:
        if result:
            result[-1]["priorities"] = passive_priority
        else:
            result.append({
                "stage": "final_build",
                "stage_label": "Passive Priorities",
                "level_range": None,
                "tree_url": "",
                "active": False,
                "source": "coach_data",
                "priorities": passive_priority,
                "notes": "Coach-provided passive priorities without a tree URL.",
                "order": 200,
            })

    result.sort(key=lambda item: (item.get("order", 999), item.get("stage_label", ""), not item.get("active", False)))
    for item in result:
        item.pop("order", None)
    return result


def _group_stage_from_text(text: str) -> tuple[str, str | None, int]:
    info = classify_stage(text)
    return info["stage"], info["level_range"], info["order"]


def _build_gear_stages(build_data: dict[str, Any], coach_data: dict[str, Any]) -> list[dict[str, Any]]:
    coach_progression = (coach_data or {}).get("gear_progression") or []
    if coach_progression:
        grouped: dict[str, dict[str, Any]] = {}
        for slot_group in coach_progression:
            slot = clean_pob_text(slot_group.get("slot"))
            for phase in slot_group.get("phases") or []:
                phase_label = clean_pob_text(phase.get("phase") or "Gear Step")
                stage, level_range, order = _group_stage_from_text(phase_label)
                entry = grouped.setdefault(stage, {
                    "stage": stage,
                    "stage_label": phase_label,
                    "level_range": level_range,
                    "priorities": [],
                    "requirements": [],
                    "source": "coach_data",
                    "notes": "Coach-provided gear timeline.",
                    "order": order,
                })
                item = clean_pob_text(phase.get("item"))
                key_stats = _unique(phase.get("key_stats") or [])
                priority = clean_pob_text(phase.get("priority"))
                acquisition = clean_pob_text(phase.get("acquisition"))
                line = f"{slot}: {item}" if slot else item
                if key_stats:
                    line += f" ({', '.join(key_stats)})"
                if line:
                    entry["priorities"].append(line)
                if priority:
                    entry["requirements"].append(f"{slot} priority: {priority}" if slot else priority)
                if acquisition:
                    entry["requirements"].append(f"{slot} acquisition: {acquisition}" if slot else acquisition)

        result = []
        for entry in grouped.values():
            entry["priorities"] = _unique(entry["priorities"])
            entry["requirements"] = _unique(entry["requirements"])
            result.append(entry)
        result.sort(key=lambda item: (item.get("order", 999), item.get("stage_label", "")))
        for item in result:
            item.pop("order", None)
        return result

    gear = ((build_data.get("progression_stages") or [{}])[0]).get("gear_recommendation") or {}
    grouped: dict[str, dict[str, Any]] = {}
    for slot, payload in gear.items():
        if not isinstance(payload, dict):
            continue
        item_name = clean_pob_text(payload.get("name") or payload.get("base_type") or slot)
        stage, level_range, order = _group_stage_from_text(item_name)
        entry = grouped.setdefault(stage, {
            "stage": stage,
            "stage_label": clean_pob_text(item_name if stage != "unknown" else "Final Gear"),
            "level_range": level_range,
            "priorities": [],
            "requirements": [],
            "source": "final_gear_snapshot",
            "notes": "Derived from visible gear names in the parsed PoB snapshot.",
            "order": order,
        })
        display = f"{clean_pob_text(slot)}: {item_name}"
        important_mods = _unique(payload.get("mods") or [])[:2]
        if important_mods:
            display += f" ({'; '.join(important_mods)})"
        entry["priorities"].append(display)

    result = []
    for entry in grouped.values():
        entry["priorities"] = _unique(entry["priorities"])
        result.append(entry)
    result.sort(key=lambda item: (item.get("order", 999), item.get("stage_label", "")))
    for item in result:
        item.pop("order", None)
    return result


def _normalize_transition_seed(
    transitions: list[dict[str, Any]],
    *,
    leveling_skill: str,
    main_skill: str,
) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for transition in transitions or []:
        level = transition.get("level")
        if not isinstance(level, int):
            level = None
        stage = clean_pob_text(transition.get("stage")) or _classify_level(level)[0]
        trigger = clean_pob_text(
            transition.get("trigger")
            or transition.get("reason")
            or transition.get("change")
            or f"Transition into {main_skill}"
        )
        from_skill = clean_pob_text(transition.get("from_skill") or leveling_skill)
        to_skill = clean_pob_text(transition.get("to_skill") or transition.get("main_skill") or main_skill)
        required_links = transition.get("required_links")
        required_item = clean_pob_text(transition.get("required_item")) or None
        normalized.append({
            "stage": stage,
            "main_skill": to_skill or main_skill,
            "trigger": trigger,
            "required_links": required_links if isinstance(required_links, int) else None,
            "required_item": required_item,
            "from_skill": from_skill or None,
            "to_skill": to_skill or None,
            "level": level,
            "source": "coach_data" if level is not None else "inferred",
        })
    return normalized


def _build_transition_points(
    campaign_plan: list[dict[str, Any]],
    seed_transitions: list[dict[str, Any]],
    *,
    leveling_skill: str,
    main_skill: str,
) -> list[dict[str, Any]]:
    transitions = _normalize_transition_seed(seed_transitions, leveling_skill=leveling_skill, main_skill=main_skill)

    previous_skill: str | None = None
    for step in campaign_plan:
        skill = clean_pob_text(step.get("main_skill"))
        if not skill:
            continue
        if previous_skill and previous_skill != skill:
            level = None
            level_range = clean_pob_text(step.get("level_range"))
            match = LEVEL_RANGE_RE.search(level_range)
            if match:
                level = int(match.group(1))
            transitions.append({
                "stage": step.get("stage") or "campaign",
                "main_skill": skill,
                "trigger": f"Campaign step changes from {previous_skill} to {skill}.",
                "required_links": None,
                "required_item": None,
                "from_skill": previous_skill,
                "to_skill": skill,
                "level": level,
                "source": step.get("source", "campaign_plan"),
            })
        previous_skill = skill

    if previous_skill and main_skill and previous_skill != main_skill:
        transitions.append({
            "stage": "early_maps",
            "main_skill": main_skill,
            "trigger": f"Final build swaps from {previous_skill} to {main_skill} once endgame links are online.",
            "required_links": 4,
            "required_item": None,
            "from_skill": previous_skill,
            "to_skill": main_skill,
            "level": 68,
            "source": "inferred_final_swap",
        })

    if not transitions and leveling_skill and main_skill and leveling_skill != main_skill:
        transitions.append({
            "stage": "early_maps",
            "main_skill": main_skill,
            "trigger": f"No explicit swap detected; infer transition from {leveling_skill} into final skill {main_skill} by maps.",
            "required_links": 4,
            "required_item": None,
            "from_skill": leveling_skill,
            "to_skill": main_skill,
            "level": 68,
            "source": "inferred",
        })

    deduped: list[dict[str, Any]] = []
    seen: set[tuple[Any, ...]] = set()
    for transition in transitions:
        key = (
            transition.get("stage"),
            transition.get("from_skill"),
            transition.get("to_skill"),
            transition.get("level"),
        )
        if key in seen:
            continue
        seen.add(key)
        deduped.append(transition)

    deduped.sort(key=lambda item: (
        item.get("level") if isinstance(item.get("level"), int) else 999,
        clean_pob_text(item.get("stage")),
        clean_pob_text(item.get("to_skill")),
    ))
    return deduped


def build_normalized_progression(
    build_data: dict[str, Any],
    coach_data: dict[str, Any] | None,
    *,
    leveling_confidence: str,
    leveling_skill: str,
    main_skill: str,
    transition_points_seed: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    coach_data = coach_data or {}
    campaign_plan = _build_campaign_plan(build_data, coach_data)
    aura_plan = _build_aura_plan(build_data, coach_data, campaign_plan)
    passive_plan = _build_passive_plan(build_data, coach_data)
    gear_stages = _build_gear_stages(build_data, coach_data)
    transition_points = _build_transition_points(
        campaign_plan,
        transition_points_seed or [],
        leveling_skill=leveling_skill,
        main_skill=main_skill,
    )

    stats = build_data.get("stats", {})
    early_mapping_ready = int(stats.get("life", 0)) >= 3000
    if coach_data.get("variant_snapshots"):
        early_mapping_ready = True

    return {
        "leveling_confidence": leveling_confidence,
        "early_mapping_ready": early_mapping_ready,
        "transition_points": transition_points,
        "campaign_plan": campaign_plan,
        "aura_plan": aura_plan,
        "passive_plan": passive_plan,
        "gear_stages": gear_stages,
    }
