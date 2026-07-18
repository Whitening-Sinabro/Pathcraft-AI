# -*- coding: utf-8 -*-
"""Profile inference and recommendation pipeline for POE1 build matching."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from build_extractor import (
    detect_build_type,
    extract_build_gems,
    extract_build_unique_bases,
    extract_build_uniques,
)
from build_profile_normalizer import build_normalized_progression
from gem_taxonomy import (
    damage_flags_for,
    get_gem_entry,
    is_offensive_active,
    is_support_gem,
    resolve_gem_name,
    weapon_requirements_for,
)
from recommendation_contract_audit import evaluate_compatibility

ROOT = Path(__file__).resolve().parent.parent

STYLE_ORDER = {
    "0_button": 0,
    "1_click": 1,
    "1_click_plus_movement": 2,
    "2_button": 3,
    "multi_button": 4,
}

AUTO_MAIN_SKILLS = {
    "Righteous Fire",
    "Death Aura",
}
ACTIVE_2BUTTON_KEYWORDS = (
    "mine",
    "trap",
    "totem",
    "brand",
    "warcry",
)
PROJECTILE_ATTACK_SKILLS = (
    "lightning arrow",
    "ice shot",
    "tornado shot",
    "elemental hit",
    "kinetic blast",
    "kinetic bolt",
)
MELEE_ATTACK_SKILLS = (
    "boneshatter",
    "lacerate",
    "cyclone",
    "heavy strike",
    "smite",
    "frost blades",
    "lightning strike",
)


def _load_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def _iter_skill_entries(build_data: dict, include_alternate: bool = True) -> list[dict[str, Any]]:
    stages = build_data.get("progression_stages", [])
    if not stages:
        return []

    stage = stages[0]
    entries: list[dict[str, Any]] = []

    def _append(source: str, setups: dict) -> None:
        if not isinstance(setups, dict):
            return
        for label, payload in setups.items():
            if isinstance(payload, dict) and "links" not in payload:
                _append(source, payload)
                continue
            links = ""
            if isinstance(payload, dict):
                links = payload.get("links", "") or ""
            elif isinstance(payload, str):
                links = payload
            gems = [part.strip() for part in links.split(" - ") if isinstance(part, str) and part.strip()]
            entries.append({
                "source": source,
                "label": str(label or "").strip(),
                "links": links,
                "gems": gems,
            })

    _append("primary", stage.get("gem_setups", {}))
    if include_alternate:
        _append("alternate", stage.get("alternate_gem_sets", {}))
    return entries


def _is_utility_setup(label: str, gems: list[str]) -> bool:
    label_lower = label.lower()
    if any(keyword in label_lower for keyword in (
        "aura",
        "curse",
        "guard",
        "movement",
        "mobility",
        "utility",
        "trigger",
        "mark",
        "banner",
    )):
        return True

    first = gems[0] if gems else ""
    first_resolved = resolve_gem_name(first, allow_support_alias=False, require_socketable=False) or first
    if first_resolved and is_offensive_active(first_resolved, socketable_only=False):
        return False

    text = f"{label} {' '.join(gems)}".lower()
    utility_keywords = (
        "aura",
        "curse",
        "guard",
        "movement",
        "flame dash",
        "dash",
        "frostblink",
        "blink arrow",
        "molten shell",
        "steelskin",
        "arctic armour",
        "clarity",
        "determination",
        "grace",
        "wrath",
        "hatred",
        "malevolence",
        "precision",
        "defiance banner",
        "mark",
        "sigil",
        "golem",
    )
    return any(keyword in text for keyword in utility_keywords)


def _score_skill_entry(entry: dict[str, Any]) -> int:
    label = entry["label"].lower()
    gems = entry["gems"]
    first_raw = gems[0] if gems else ""
    first_resolved = resolve_gem_name(first_raw, allow_support_alias=True, require_socketable=False) or first_raw
    first = first_resolved.lower() if first_resolved else ""
    score = 0

    if entry["source"] == "primary":
        score += 20
    if "main" in label:
        score += 50
    if "boss" in label:
        score += 20
    if "clear" in label:
        score += 10
    if entry["label"] and entry["label"].lower() == first:
        score += 20
    score += len(gems) * 3
    first_entry = get_gem_entry(first_resolved) if first_resolved else None
    if first_entry:
        if first_entry.get("gem_kind") in {"support_gem", "support_alias"} or is_support_gem(first_resolved):
            score -= 80
        elif is_offensive_active(first_resolved, socketable_only=False):
            score += 35
            if first_entry.get("socketable"):
                score += 10
        elif first_entry.get("socketable"):
            score += 5
        else:
            score -= 20
    if _is_utility_setup(entry["label"], gems):
        score -= 40
    return score


def extract_main_skill(build_data: dict) -> str:
    entries = _iter_skill_entries(build_data, include_alternate=False)
    if not entries:
        return "Unknown"
    best = max(entries, key=_score_skill_entry)
    if best["gems"]:
        resolved = resolve_gem_name(best["gems"][0], allow_support_alias=False, require_socketable=False)
        if resolved and not is_support_gem(resolved):
            return resolved
        return best["gems"][0]
    if best["label"]:
        return best["label"]
    return "Unknown"


def _load_skill_system():
    try:
        from skill_tag_system import SkillTagSystem
    except ImportError:
        return None
    try:
        return SkillTagSystem()
    except Exception:
        return None


def infer_leveling_skill(build_data: dict, coach_data: dict | None = None) -> tuple[str, list[dict[str, Any]], str]:
    coach_data = coach_data or {}
    leveling = coach_data.get("leveling_skills", {})
    recommended = leveling.get("recommended", {})
    recommended_name = recommended.get("name")
    if isinstance(recommended_name, str) and recommended_name.strip():
        transitions = coach_data.get("leveling_skills", {}).get("skill_transitions", []) or []
        return recommended_name.strip(), transitions, "coach_data"

    main_skill = extract_main_skill(build_data)
    alt_entries = [
        entry for entry in _iter_skill_entries(build_data, include_alternate=True)
        if entry["source"] == "alternate" and entry["gems"]
    ]
    if alt_entries:
        best_alt = max(alt_entries, key=_score_skill_entry)
        alt_skill = best_alt["gems"][0]
        if alt_skill and alt_skill != main_skill:
            transitions = [{
                "stage": "alternate_skillset_detected",
                "main_skill": main_skill,
                "trigger": "POB alternate skill set differs from final active setup",
            }]
            return alt_skill, transitions, "alternate_skillset"

    skill_system = _load_skill_system()
    if skill_system and main_skill != "Unknown":
        meta = build_data.get("meta", {})
        recs = skill_system.get_leveling_skill_for_build(
            main_skill,
            include_korean=False,
            class_name=meta.get("class", ""),
            ascendancy=meta.get("ascendancy", ""),
        )
        if recs:
            rec = recs[0]
            leveling_skill = rec.get("skill") or main_skill
            transition_info = skill_system.get_transition_info(
                leveling_skill,
                main_skill,
                meta.get("ascendancy", ""),
            )
            transitions = [{
                "stage": transition_info.get("transition_point", "campaign"),
                "main_skill": main_skill,
                "trigger": f"recommended_level={transition_info.get('recommended_level', 68)}",
                "required_links": None,
                "required_item": None,
            }]
            return leveling_skill, transitions, "skill_tag_system"

    return main_skill, [], "same_as_final"


def infer_input_style(main_skill: str, skills: list[str], supports: list[str], coach_data: dict | None = None) -> tuple[str, int]:
    coach_data = coach_data or {}
    rating = coach_data.get("build_rating", {})
    play_difficulty = rating.get("play_difficulty")

    if main_skill in AUTO_MAIN_SKILLS:
        return "0_button", 0

    flags = damage_flags_for(main_skill)
    text = " ".join([main_skill] + skills + supports).lower()
    if any(keyword in text for keyword in ACTIVE_2BUTTON_KEYWORDS):
        return "2_button", 2

    if flags.get("attack"):
        if any(skill in main_skill.lower() for skill in PROJECTILE_ATTACK_SKILLS):
            return "1_click_plus_movement", 2
        return "1_click", 1
    if flags.get("dot") and not flags.get("attack"):
        return "2_button", 2

    if any(skill in main_skill.lower() for skill in PROJECTILE_ATTACK_SKILLS):
        return "1_click_plus_movement", 2
    if any(skill in main_skill.lower() for skill in MELEE_ATTACK_SKILLS):
        return "1_click", 1

    if isinstance(play_difficulty, int):
        if play_difficulty >= 4:
            return "1_click", 1
        if play_difficulty <= 2:
            return "2_button", 2

    return "1_click", 1


def infer_budget_curve(build_data: dict, coach_data: dict | None = None) -> tuple[dict, list[str], list[str]]:
    coach_data = coach_data or {}
    unique_names = extract_build_uniques(build_data, coach_data)
    mandatory_uniques = [
        item.get("name", "")
        for item in coach_data.get("key_items", [])
        if item.get("importance") == "필수" and item.get("name")
    ]
    if not mandatory_uniques:
        mandatory_uniques = unique_names[:2]

    gearing_rating = coach_data.get("build_rating", {}).get("gearing_difficulty")
    entry_cost = 0.5 + max(len(mandatory_uniques) - 1, 0) * 0.75
    if isinstance(gearing_rating, int):
        entry_cost += max(0, 5 - gearing_rating) * 0.5

    stats = build_data.get("stats", {})
    if stats.get("dps", 0) >= 10_000_000:
        entry_cost += 1.0

    comfortable_cost = max(round(entry_cost * 4, 1), round(entry_cost + 3, 1))
    aspirational_cost = max(round(comfortable_cost * 8, 1), round(comfortable_cost + 20, 1))
    respec_cost = 18
    if isinstance(coach_data.get("passive_priority"), list) and len(coach_data["passive_priority"]) >= 4:
        respec_cost = 28

    unique_bases = extract_build_unique_bases(build_data, coach_data)
    mandatory_transfigured = []
    main_skill = extract_main_skill(build_data)
    main_entry = get_gem_entry(main_skill)
    if main_entry and main_entry.get("gem_kind") == "active_transfigured_or_valid_active":
        mandatory_transfigured.append(main_skill)
    elif not main_entry and " of " in main_skill:
        mandatory_transfigured.append(main_skill)

    return (
        {
            "entry_cost_divines": round(entry_cost, 1),
            "comfortable_cost_divines": comfortable_cost,
            "aspirational_cost_divines": aspirational_cost,
            "respec_cost_points": respec_cost,
            "notes": "Inferred from unique dependency, coach hints, and visible final-state gear.",
        },
        mandatory_uniques if mandatory_uniques else unique_bases[:2],
        mandatory_transfigured,
    )


def infer_availability(
    build_data: dict,
    coach_data: dict | None,
    mandatory_uniques: list[str],
    mandatory_transfigured: list[str],
    entry_cost_divines: float,
) -> dict:
    coach_data = coach_data or {}
    rating = coach_data.get("build_rating", {})
    league_start_score = rating.get("league_start_viable")
    ssf_score = rating.get("ssf_viability")
    hc_score = rating.get("hcssf_viability")

    if isinstance(league_start_score, int):
        league_start_viable = league_start_score >= 4
    else:
        league_start_viable = entry_cost_divines <= 2.0 and len(mandatory_uniques) <= 1

    if isinstance(ssf_score, int):
        ssf_viable = "high" if ssf_score >= 4 else "medium" if ssf_score == 3 else "low"
    elif len(mandatory_uniques) >= 2 or mandatory_transfigured:
        ssf_viable = "low"
    elif isinstance(league_start_score, int) and league_start_score <= 2 and mandatory_uniques:
        ssf_viable = "low"
    elif entry_cost_divines <= 1.0:
        ssf_viable = "high"
    else:
        ssf_viable = "medium"

    if isinstance(hc_score, int):
        hc_viable = "high" if hc_score >= 4 else "medium" if hc_score == 3 else "low"
    else:
        life = build_data.get("stats", {}).get("life", 0)
        hc_viable = "high" if life >= 5000 else "medium" if life >= 4000 else "low"

    return {
        "league_start_viable": league_start_viable,
        "ssf_viable": ssf_viable,
        "hc_viable": hc_viable,
        "twink_required": not league_start_viable and entry_cost_divines > 2.0,
        "mandatory_uniques": mandatory_uniques,
        "mandatory_transfigured_gems": mandatory_transfigured,
    }


def infer_leveling_confidence(build_data: dict, coach_data: dict | None, leveling_source: str) -> str:
    coach_data = coach_data or {}
    variant_snapshots = coach_data.get("variant_snapshots", [])
    aura_utility = coach_data.get("aura_utility_progression", [])
    leveling = coach_data.get("leveling_skills", {})
    recommended = leveling.get("recommended", {})

    has_links_progression = bool(recommended.get("links_progression"))
    if len(variant_snapshots) >= 5 and len(aura_utility) >= 5 and has_links_progression:
        return "confirmed"
    if leveling_source in {"coach_data", "alternate_skillset", "skill_tag_system"}:
        return "near_confirmed"
    if build_data.get("progression_stages", [{}])[0].get("alternate_gem_sets"):
        return "near_confirmed"
    return "inferred"


def infer_suitability(build_data: dict, build_type: str, main_skill: str, input_style: str) -> dict:
    stats = build_data.get("stats", {})
    dps = int(stats.get("dps", 0))
    life = int(stats.get("life", 0))
    es = int(stats.get("energy_shield", 0))
    ehp = life + es
    main_lower = main_skill.lower()

    mapping = 60
    bossing = 55
    sanctum = 50
    heist = 55
    expedition = 55
    simulacrum = 45

    if build_type == "attack":
        mapping += 15
        expedition += 10
    elif build_type == "dot":
        mapping += 8
        expedition += 12
        bossing += 8
    elif build_type == "minion":
        bossing += 10
        simulacrum += 10
    else:
        sanctum += 10

    if any(keyword in main_lower for keyword in ("mine", "trap", "totem", "brand")):
        bossing += 18
        sanctum += 12
        mapping -= 4
    if any(keyword in main_lower for keyword in PROJECTILE_ATTACK_SKILLS):
        mapping += 18
        heist += 8
    if "boneshatter" in main_lower or "lacerate" in main_lower:
        bossing += 8
        sanctum -= 10

    if dps >= 10_000_000:
        bossing += 20
        simulacrum += 10
    elif dps >= 2_000_000:
        bossing += 10

    if ehp >= 7000:
        simulacrum += 15
        heist += 5
    elif ehp < 4500:
        simulacrum -= 12

    if input_style == "0_button":
        mapping += 10
    elif input_style == "2_button":
        mapping -= 4
        sanctum += 4

    def _clamp(value: int) -> int:
        return max(0, min(100, value))

    return {
        "mapping": _clamp(mapping),
        "bossing": _clamp(bossing),
        "sanctum": _clamp(sanctum),
        "heist": _clamp(heist),
        "expedition": _clamp(expedition),
        "simulacrum": _clamp(simulacrum),
    }


def infer_build_profile(
    build_data: dict,
    coach_data: dict | None = None,
    *,
    representative_status: str = "near_confirmed",
    patch: str | None = None,
) -> dict:
    coach_data = coach_data or {}
    meta = build_data.get("meta", {})
    skills, supports = extract_build_gems(build_data)
    main_skill = extract_main_skill(build_data)
    leveling_skill, transition_points, leveling_source = infer_leveling_skill(build_data, coach_data)
    build_type = detect_build_type(build_data)
    input_style, manual_buttons = infer_input_style(main_skill, skills, supports, coach_data)
    budget_curve, mandatory_uniques, mandatory_transfigured = infer_budget_curve(build_data, coach_data)
    availability = infer_availability(
        build_data,
        coach_data,
        mandatory_uniques,
        mandatory_transfigured,
        budget_curve["entry_cost_divines"],
    )
    leveling_confidence = infer_leveling_confidence(build_data, coach_data, leveling_source)
    suitability = infer_suitability(build_data, build_type, main_skill, input_style)

    evidence = []
    if meta.get("pob_link"):
        evidence.append({
            "type": "pobb",
            "label": "Parsed PoB input",
            "url": meta.get("pob_link"),
            "notes": "Local profile inferred from provided build data.",
        })
    if coach_data:
        evidence.append({
            "type": "manual_curated",
            "label": "Coach output attached",
            "url": None,
            "notes": "Additional structured leveling and gearing hints were provided.",
        })

    progression = build_normalized_progression(
        build_data,
        coach_data,
        leveling_confidence=leveling_confidence,
        leveling_skill=leveling_skill,
        main_skill=main_skill,
        transition_points_seed=transition_points,
    )

    build_name = meta.get("build_name") or f"{meta.get('class', 'Unknown')} {meta.get('ascendancy', 'Unknown')} {main_skill}".strip()
    build_id_parts = [
        (patch or meta.get("version") or "unknown").replace(".", "_"),
        main_skill.lower().replace(" ", "_").replace("'", ""),
        meta.get("ascendancy", "unknown").lower().replace(" ", "_"),
    ]

    return {
        "schema_version": "1.1.0",
        "dataset_kind": "poe1_build_profile",
        "build_id": "_".join(part for part in build_id_parts if part),
        "identity": {
            "build_name": build_name,
            "patch": patch or meta.get("version") or "unknown",
            "class_name": meta.get("class", "Unknown"),
            "ascendancy": meta.get("ascendancy", "Unknown"),
            "main_skill": main_skill,
            "leveling_skill": leveling_skill,
            "damage_tags": [build_type],
            "weapon_preferences": weapon_requirements_for(main_skill),
        },
        "playstyle": {
            "input_style": input_style,
            "manual_buttons": manual_buttons,
            "movement_dependence": "high" if input_style == "1_click_plus_movement" else "medium",
            "aim_requirement": "medium" if build_type == "attack" else "low",
            "notes": f"Inferred from gem setups and build type ({build_type}).",
        },
        "budget_curve": budget_curve,
        "availability": availability,
        "progression": progression,
        "suitability": suitability,
        "constraints": {
            "banned_map_mods": [],
            "pain_points": [
                "Profile inferred from final-state build data",
            ],
            "reroll_recommended_over_respec": True,
        },
        "confidence": {
            "representative_build_status": representative_status,
            "source_count": len(evidence),
            "notes": f"leveling_source={leveling_source}",
        },
        "evidence": evidence or [{
            "type": "manual_curated",
            "label": "No external evidence attached",
            "url": None,
            "notes": "Synthetic local profile",
        }],
    }


def _style_fit_score(profile_style: str, max_style: str) -> int:
    profile_order = STYLE_ORDER.get(profile_style, 4)
    max_order = STYLE_ORDER.get(max_style, 4)
    if profile_order > max_order:
        return 0
    return max(20, 100 - (max_order - profile_order) * 20)


def _budget_fit_score(entry_cost: float, liquid_divines: float) -> int:
    if entry_cost <= 0:
        return 100
    if liquid_divines <= 0:
        return 0
    ratio = entry_cost / liquid_divines
    if ratio <= 1.0:
        return 100
    if ratio <= 1.35:
        return 75
    if ratio <= 1.8:
        return 55
    return 0


def _character_fit_score(profile: dict, user_state: dict) -> int:
    character = user_state.get("character_state", {})
    identity = profile.get("identity", {})
    score = 50
    if character.get("class_name") == identity.get("class_name"):
        score += 25
    if character.get("ascendancy") == identity.get("ascendancy"):
        score += 25
    if not character.get("character_locked"):
        score = max(score, 70)
    return min(100, score)


def _content_fit_score(profile: dict, user_state: dict) -> int:
    targets = user_state.get("preferences", {}).get("target_contents", [])
    if not targets:
        return 70
    values = []
    for target in targets:
        score = profile.get("suitability", {}).get(target)
        if isinstance(score, int):
            values.append(score)
    if not values:
        return 50
    return int(sum(values) / len(values))


def _availability_fit_score(profile: dict, user_state: dict) -> int:
    availability = profile.get("availability", {})
    trade_mode = user_state.get("preferences", {}).get("trade_mode")
    if trade_mode == "ssf":
        return {"low": 20, "medium": 65, "high": 100}.get(availability.get("ssf_viable"), 50)
    if trade_mode == "trade_league_start":
        return 100 if availability.get("league_start_viable") else 50
    if trade_mode == "twink":
        return 100
    return 80


def _confidence_score(profile: dict, user_state: dict) -> int:
    profile_conf = profile.get("confidence", {}).get("representative_build_status")
    leveling_conf = profile.get("progression", {}).get("leveling_confidence")
    status_score = {"confirmed": 100, "near_confirmed": 80, "hold": 50}.get(profile_conf, 40)
    leveling_score = {"confirmed": 100, "near_confirmed": 75, "inferred": 45}.get(leveling_conf, 40)
    if user_state.get("constraints", {}).get("require_confirmed_leveling"):
        return int((status_score + leveling_score * 2) / 3)
    return int((status_score + leveling_score) / 2)


def score_profile(profile: dict, user_state: dict, compatibility: dict) -> int:
    desired_skill = (
        user_state.get("constraints", {}).get("must_use_skill")
        or user_state.get("preferences", {}).get("desired_main_skill")
    )
    exact_skill = desired_skill and desired_skill == profile.get("identity", {}).get("main_skill")
    skill_score = 100 if exact_skill else 45
    if not desired_skill:
        skill_score = 70

    style_score = _style_fit_score(
        profile.get("playstyle", {}).get("input_style", "multi_button"),
        user_state.get("preferences", {}).get("max_input_style", "multi_button"),
    )
    budget_score = _budget_fit_score(
        float(profile.get("budget_curve", {}).get("entry_cost_divines", 0)),
        float(user_state.get("currency_state", {}).get("liquid_divines", 0)),
    )
    character_score = _character_fit_score(profile, user_state)
    content_score = _content_fit_score(profile, user_state)
    availability_score = _availability_fit_score(profile, user_state)
    confidence_score = _confidence_score(profile, user_state)

    total = (
        skill_score * 25
        + style_score * 20
        + budget_score * 20
        + character_score * 15
        + content_score * 10
        + availability_score * 5
        + confidence_score * 5
    ) / 100

    if compatibility.get("selected_plan") == "B":
        total -= 8
    elif compatibility.get("selected_plan") == "C":
        total -= 18

    return int(round(total))


def recommend_profiles(profiles: list[dict], user_state: dict) -> dict:
    exact_candidates: list[dict] = []
    proxy_candidates: list[dict] = []
    rejected: list[dict] = []

    def _result_guardrails(candidate: dict | None, *, plan: str) -> dict:
        if candidate:
            compatibility = candidate["compatibility"]
            guardrails = compatibility.get("guardrails") or {
                "deterministic_guards": compatibility.get("deterministic_guards", []),
                "ai_policy": compatibility.get("ai_policy", {}),
                "verification_loop": compatibility.get("verification_loop", {}),
            }
            return {
                "deterministic_guards": guardrails.get("deterministic_guards", []),
                "ai_policy": guardrails.get("ai_policy", {}),
                "verification_loop": guardrails.get("verification_loop", {}),
                "guardrails": guardrails,
                "response_layers": compatibility.get("response_layers", {}),
            }

        guardrails = {
            "deterministic_guards": [],
            "ai_policy": {
                "mode": "disabled",
                "reason": "현재 조건을 통과한 후보가 없음",
                "allowed_slots": ["rejection_reason_summary", "next_required_inputs"],
                "forbidden_overrides": [],
            },
            "verification_loop": {
                "confidence_lane": "unknown",
                "loop_state": "abstain",
                "recommended_plan": plan,
                "steps": [],
                "promotion_requirements": [],
                "next_actions": ["막힌 조건을 줄이거나, 레벨링 PoB/최근 사례/예산 조건을 추가로 확인"],
            },
        }
        return {
            "deterministic_guards": guardrails["deterministic_guards"],
            "ai_policy": guardrails["ai_policy"],
            "verification_loop": guardrails["verification_loop"],
            "guardrails": guardrails,
            "response_layers": {
                "decision": {
                    "plan": plan,
                    "decision_state": "abstain",
                    "candidate_path": "none",
                    "confidence_lane": "unknown",
                    "blocking_guards": [],
                    "warning_guards": [],
                },
                "user_message": {
                    "template_id": "plan_d_abstain_generic",
                    "title": "아직 확정 추천 없음",
                    "summary": "현재 조건을 통과한 후보가 없습니다. 조건을 완화하거나 원본 PoB, 레벨링 PoB, 최근 사례를 더 넣어야 합니다.",
                    "bullets": [
                        "차단 조건을 통과하기 전에는 추천으로 승격하지 않습니다.",
                        "막힌 조건과 필요한 추가 입력을 먼저 보여줍니다.",
                        "AI는 판정을 바꾸지 않고 설명만 보조합니다.",
                    ],
                },
                "ui_panels": {
                    "show_deterministic_guards": True,
                    "show_ai_policy": True,
                    "show_verification_loop": True,
                },
                "ai_explanation": {
                    "mode": "disabled",
                    "instruction": "AI는 결정론적 결과를 설명만 할 수 있으며, 선택/가드/신뢰도 라벨을 바꾸면 안 된다.",
                    "allowed_slots": ["rejection_reason_summary", "next_required_inputs"],
                    "forbidden_overrides": [],
                },
                "badges": [
                    {"kind": "plan", "label": "추천 보류", "tone": "danger"},
                    {"kind": "ai_mode", "label": "AI 설명 전용", "tone": "muted"},
                ],
            },
        }

    def _serialize_candidate(item: dict, *, include_compatibility: bool = False) -> dict:
        payload = {
            "build_id": item["build_id"],
            "build_name": item["build_name"],
            "score": item["score"],
            "main_skill": item["main_skill"],
            "class_name": item["class_name"],
            "ascendancy": item["ascendancy"],
        }
        if include_compatibility:
            payload["compatibility"] = item["compatibility"]
        return payload

    def _serialize_rejection(item: dict, *, include_compatibility: bool = False) -> dict:
        payload = {
            "build_id": item["build_id"],
            "score": item["score"],
            "hard_blocks": item["compatibility"]["hard_blocks"],
        }
        if include_compatibility:
            payload["compatibility"] = item["compatibility"]
        return payload

    for profile in profiles:
        compatibility = evaluate_compatibility(profile, user_state)
        candidate = {
            "build_id": profile.get("build_id"),
            "build_name": profile.get("identity", {}).get("build_name"),
            "main_skill": profile.get("identity", {}).get("main_skill"),
            "class_name": profile.get("identity", {}).get("class_name"),
            "ascendancy": profile.get("identity", {}).get("ascendancy"),
            "compatibility": compatibility,
            "profile": profile,
        }
        candidate["score"] = score_profile(profile, user_state, compatibility)

        hard_blocks = set(compatibility.get("hard_blocks", []))
        if not hard_blocks:
            exact_candidates.append(candidate)
        elif hard_blocks == {"skill_mismatch"}:
            proxy_candidates.append(candidate)
        else:
            rejected.append(candidate)

    exact_candidates.sort(key=lambda item: item["score"], reverse=True)
    proxy_candidates.sort(key=lambda item: item["score"], reverse=True)
    rejected.sort(
        key=lambda item: (
            len(item["compatibility"].get("hard_blocks", [])),
            -item["score"],
            item["build_name"] or "",
        )
    )

    if exact_candidates:
        selected = exact_candidates[0]
        plan = selected["compatibility"]["selected_plan"]
        result = {
            "selected_plan": plan,
            "selected_build_id": selected["build_id"],
            "selected_build_name": selected["build_name"],
            "selected_score": selected["score"],
            "recommendations": [
                _serialize_candidate(item, include_compatibility=True)
                for item in exact_candidates[:5]
            ],
            "proxy_candidates": [
                _serialize_candidate(item, include_compatibility=False)
                for item in proxy_candidates[:3]
            ],
            "rejections": [
                _serialize_rejection(item, include_compatibility=False)
                for item in rejected[:10]
            ],
        }
        result.update(_result_guardrails(selected, plan=plan))
        return result

    if proxy_candidates:
        selected = proxy_candidates[0]
        result = {
            "selected_plan": "C",
            "selected_build_id": selected["build_id"],
            "selected_build_name": selected["build_name"],
            "selected_score": selected["score"],
            "recommendations": [],
            "proxy_candidates": [
                _serialize_candidate(item, include_compatibility=True)
                for item in proxy_candidates[:5]
            ],
            "rejections": [
                _serialize_rejection(item, include_compatibility=False)
                for item in rejected[:10]
            ],
        }
        result.update(_result_guardrails(selected, plan="C"))
        return result

    blocking_candidate = rejected[0] if rejected else None
    result = {
        "selected_plan": "D",
        "selected_build_id": None,
        "selected_build_name": None,
        "selected_score": 0,
        "blocking_candidate": (
            _serialize_rejection(blocking_candidate, include_compatibility=True)
            if blocking_candidate else None
        ),
        "recommendations": [],
        "proxy_candidates": [],
        "rejections": [
            _serialize_rejection(item, include_compatibility=False)
            for item in rejected[:10]
        ],
    }
    result.update(_result_guardrails(blocking_candidate, plan="D"))
    return result


def recommend_from_build_data(
    build_payloads: list[dict],
    user_state: dict,
    coach_payloads: list[dict] | None = None,
) -> dict:
    coach_payloads = coach_payloads or [None] * len(build_payloads)
    profiles = [
        infer_build_profile(build_data, coach_data)
        for build_data, coach_data in zip(build_payloads, coach_payloads)
    ]
    return {
        "dataset_kind": "poe1_recommendation_pipeline_result",
        "profiles": profiles,
        "recommendation": recommend_profiles(profiles, user_state),
    }


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Infer build profiles and run recommendation matching.")
    parser.add_argument("--build-json", action="append", required=True, help="Parsed build_data JSON path. Repeatable.")
    parser.add_argument("--coach-json", action="append", help="Coach JSON path aligned by index with --build-json.")
    parser.add_argument("--user-state", required=True, help="User state JSON path.")
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    build_payloads = [_load_json(Path(path)) for path in args.build_json]
    coach_payloads = [_load_json(Path(path)) for path in (args.coach_json or [])]
    while len(coach_payloads) < len(build_payloads):
        coach_payloads.append(None)
    user_state = _load_json(Path(args.user_state))
    result = recommend_from_build_data(build_payloads, user_state, coach_payloads)
    print(json.dumps(result, ensure_ascii=False, indent=2))




