# -*- coding: utf-8 -*-
"""Run the five-lens adversarial audit for POE1 gem taxonomy consumers."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from build_coach import build_season_research_context
from build_extractor import detect_build_type, extract_build_gems
from gem_taxonomy import (
    damage_flags_for,
    get_gem_entry,
    is_active_gem,
    is_support_gem,
    resolve_gem_name,
    weapon_requirements_for,
)
from recommendation_engine import extract_main_skill, infer_build_profile


ROOT = Path(__file__).resolve().parent.parent
DATA_ROOT = ROOT / "data"
TAXONOMY_PATH = DATA_ROOT / "poe1_gem_taxonomy.latest.json"
SEASON_RESEARCH_PATH = DATA_ROOT / "poe1_season_research_3_29_reliquarian.json"
DEFAULT_OUTPUT_PATH = DATA_ROOT / "gem_taxonomy_adversarial_audit.latest.json"

ACTIVE_SOCKETABLE_KINDS = {"active_gem", "active_transfigured_or_valid_active"}
NON_SOCKETABLE_ACTIVE_KINDS = {"active_skill_only", "active_skill_only_and_support_alias"}
SUPPORT_KINDS = {"support_gem", "support_alias"}
CANDIDATE_FIELDS = (
    "primary_offense_gems",
    "secondary_offense_gems",
    "enabler_offense_gems",
    "carrier_gems",
    "fallback_offense_gems",
    "rejected_or_lower_priority_active_gems",
)


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8-sig") as f:
        value = json.load(f)
    return value if isinstance(value, dict) else {}


def _finding(
    severity: str,
    issue: str,
    *,
    lens: str,
    subject: str,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "severity": severity,
        "issue": issue,
        "lens": lens,
        "subject": subject,
        "details": details or {},
    }


def _build(gem_setups: dict[str, str], *, class_name: str = "Scion", ascendancy: str = "Reliquarian") -> dict:
    return {
        "meta": {
            "build_name": f"{class_name} {ascendancy} adversarial audit",
            "class": class_name,
            "ascendancy": ascendancy,
            "version": "3.29",
        },
        "progression_stages": [{
            "gem_setups": {
                label: {"links": links, "reasoning": None}
                for label, links in gem_setups.items()
            }
        }],
    }


def _audit_source_integrity(entries: dict[str, dict[str, Any]]) -> dict[str, Any]:
    lens = "source_integrity"
    findings: list[dict[str, Any]] = []
    checked = 0
    alias_count = 0

    for name, entry in sorted(entries.items()):
        if not isinstance(entry, dict):
            continue
        checked += 1
        kind = entry.get("gem_kind")
        socketable = bool(entry.get("socketable"))
        alias_target = entry.get("support_alias_of")
        flags = entry.get("damage_flags") if isinstance(entry.get("damage_flags"), dict) else {}
        offense_class = entry.get("offense_class")

        if kind in {"support_alias", "active_skill_only_and_support_alias"}:
            alias_count += 1
            target = entries.get(alias_target) if isinstance(alias_target, str) else None
            if not target:
                findings.append(_finding("failure", "missing_support_alias_target", lens=lens, subject=name, details={
                    "support_alias_of": alias_target,
                }))
            elif target.get("gem_kind") != "support_gem" or not target.get("socketable"):
                findings.append(_finding("failure", "support_alias_target_not_socketable_support", lens=lens, subject=name, details={
                    "support_alias_of": alias_target,
                    "target_kind": target.get("gem_kind"),
                    "target_socketable": target.get("socketable"),
                }))
            if socketable:
                findings.append(_finding("failure", "support_alias_marked_socketable", lens=lens, subject=name))

        if kind == "support_gem":
            if not socketable:
                findings.append(_finding("failure", "support_gem_not_socketable", lens=lens, subject=name))
            if alias_target is not None:
                findings.append(_finding("failure", "support_gem_has_alias_target", lens=lens, subject=name, details={
                    "support_alias_of": alias_target,
                }))

        if kind in ACTIVE_SOCKETABLE_KINDS and (not socketable or alias_target is not None):
            findings.append(_finding("failure", "socketable_active_has_bad_shape", lens=lens, subject=name, details={
                "socketable": socketable,
                "support_alias_of": alias_target,
            }))

        if kind in NON_SOCKETABLE_ACTIVE_KINDS and socketable:
            findings.append(_finding("failure", "triggered_or_alias_active_marked_socketable", lens=lens, subject=name))

        if kind in SUPPORT_KINDS and offense_class == "offensive_active":
            findings.append(_finding("failure", "support_classed_as_offensive_active", lens=lens, subject=name))

        if offense_class == "offensive_active" and not any(bool(flags.get(axis)) for axis in ("attack", "caster", "dot", "minion")):
            findings.append(_finding("failure", "offensive_active_without_damage_axis", lens=lens, subject=name))

    return {
        "lens": lens,
        "checked_entries": checked,
        "support_alias_entries": alias_count,
        "findings": findings,
    }


def _audit_name_collisions(entries: dict[str, dict[str, Any]]) -> dict[str, Any]:
    lens = "name_collision"
    findings: list[dict[str, Any]] = []
    collision_names: list[str] = []

    for name, entry in sorted(entries.items()):
        if not isinstance(entry, dict):
            continue
        support_name = f"{name} Support"
        if support_name not in entries:
            continue
        if entry.get("gem_kind") in ACTIVE_SOCKETABLE_KINDS:
            collision_names.append(name)
            resolved = resolve_gem_name(name)
            if resolved != name:
                findings.append(_finding("failure", "active_name_resolved_to_support_sibling", lens=lens, subject=name, details={
                    "resolved": resolved,
                    "support_sibling": support_name,
                }))
            if is_support_gem(name):
                findings.append(_finding("failure", "active_name_detected_as_support", lens=lens, subject=name))

    known_expectations = {
        "Barrage": "Barrage",
        "Barrage Support": "Barrage Support",
        "Added Lightning Damage": "Added Lightning Damage Support",
        "Summon Phantasm": "Summon Phantasm Support",
    }
    for raw, expected in known_expectations.items():
        resolved = resolve_gem_name(raw)
        if resolved != expected:
            findings.append(_finding("failure", "known_collision_resolution_changed", lens=lens, subject=raw, details={
                "expected": expected,
                "actual": resolved,
            }))

    if resolve_gem_name("Added Lightning Damage", allow_support_alias=False) is not None:
        findings.append(_finding("failure", "support_alias_allowed_when_aliases_disabled", lens=lens, subject="Added Lightning Damage"))
    if resolve_gem_name("Summon Phantasm", allow_support_alias=False) is not None:
        findings.append(_finding("failure", "active_support_alias_allowed_when_aliases_disabled", lens=lens, subject="Summon Phantasm"))
    if not is_active_gem("Barrage", socketable_only=True):
        findings.append(_finding("failure", "known_socketable_active_not_active", lens=lens, subject="Barrage"))
    if is_active_gem("Summon Phantasm", socketable_only=True):
        findings.append(_finding("failure", "known_alias_active_marked_socketable_active", lens=lens, subject="Summon Phantasm"))

    return {
        "lens": lens,
        "active_support_sibling_collisions": collision_names,
        "findings": findings,
    }


def _audit_socketability_pipeline() -> dict[str, Any]:
    lens = "socketability_pipeline"
    findings: list[dict[str, Any]] = []
    build = _build({
        "Main": "Static Strike - Shockwave Support - Faster Attacks Support",
        "Trigger Package": "Molten Burst - Greater Multiple Projectiles Support",
        "Minion Trigger": "Raise Spiders - Minion Damage Support",
        "Phantasm Support Alias": "Summon Phantasm - Minion Damage Support",
    })

    skills, supports = extract_build_gems(build)
    main_skill = extract_main_skill(build)
    build_type = detect_build_type(build)

    expected_absent = {"Molten Burst", "Raise Spiders", "Summon Phantasm"}
    leaked = sorted(expected_absent.intersection(skills))
    if leaked:
        findings.append(_finding("failure", "non_socketable_skills_leaked_into_skill_list", lens=lens, subject="synthetic_trigger_build", details={
            "leaked": leaked,
            "skills": skills,
        }))
    if "Summon Phantasm Support" not in supports:
        findings.append(_finding("failure", "support_alias_not_routed_to_supports", lens=lens, subject="Summon Phantasm"))
    if main_skill != "Static Strike":
        findings.append(_finding("failure", "trigger_noise_changed_main_skill", lens=lens, subject="synthetic_trigger_build", details={
            "main_skill": main_skill,
        }))
    if build_type != "attack":
        findings.append(_finding("failure", "trigger_noise_changed_build_type", lens=lens, subject="synthetic_trigger_build", details={
            "build_type": build_type,
        }))

    for name in sorted(expected_absent):
        entry = get_gem_entry(name)
        if not entry:
            findings.append(_finding("failure", "known_trigger_or_alias_missing_from_taxonomy", lens=lens, subject=name))
        elif entry.get("socketable"):
            findings.append(_finding("failure", "known_trigger_or_alias_marked_socketable", lens=lens, subject=name, details={
                "gem_kind": entry.get("gem_kind"),
            }))

    return {
        "lens": lens,
        "synthetic_result": {
            "main_skill": main_skill,
            "build_type": build_type,
            "skills": skills,
            "supports": supports,
        },
        "findings": findings,
    }


def _audit_context_scoring() -> dict[str, Any]:
    lens = "context_scoring"
    findings: list[dict[str, Any]] = []
    build = _build(
        {
            "Auras": "Wrath - Grace - Herald of Thunder - Added Lightning Damage",
            "Movement": "Flame Dash - Arcane Surge",
            "Guard": "Steelskin - Increased Duration Support",
            "Main Clear": "Barrage - Added Lightning Damage - Barrage Support",
        },
        class_name="Ranger",
        ascendancy="Deadeye",
    )
    main_skill = extract_main_skill(build)
    build_type = detect_build_type(build)
    profile = infer_build_profile(build)
    weapon_requirements = weapon_requirements_for("Barrage")
    damage_flags = damage_flags_for("Barrage")

    if main_skill != "Barrage":
        findings.append(_finding("failure", "utility_or_support_noise_changed_main_skill", lens=lens, subject="synthetic_barrage_build", details={
            "main_skill": main_skill,
        }))
    if build_type != "attack":
        findings.append(_finding("failure", "utility_or_support_noise_changed_build_type", lens=lens, subject="synthetic_barrage_build", details={
            "build_type": build_type,
        }))
    if profile.get("identity", {}).get("main_skill") != "Barrage":
        findings.append(_finding("failure", "profile_main_skill_mismatch", lens=lens, subject="synthetic_barrage_build", details={
            "profile_main_skill": profile.get("identity", {}).get("main_skill"),
        }))
    if profile.get("identity", {}).get("damage_tags") != ["attack"]:
        findings.append(_finding("failure", "profile_damage_tag_mismatch", lens=lens, subject="synthetic_barrage_build", details={
            "damage_tags": profile.get("identity", {}).get("damage_tags"),
        }))
    if "Bows" not in weapon_requirements or not damage_flags.get("attack"):
        findings.append(_finding("failure", "taxonomy_attack_weapon_context_missing", lens=lens, subject="Barrage", details={
            "weapon_requirements": weapon_requirements,
            "damage_flags": damage_flags,
        }))

    return {
        "lens": lens,
        "synthetic_result": {
            "main_skill": main_skill,
            "build_type": build_type,
            "profile_identity": profile.get("identity", {}),
            "weapon_requirements": weapon_requirements,
            "damage_flags": damage_flags,
        },
        "findings": findings,
    }


def _candidate_entries(season_research: dict[str, Any]) -> list[dict[str, Any]]:
    rows = season_research.get("lenses", {}).get("offensive_gem_lens", [])
    candidates: list[dict[str, Any]] = []
    for row in rows if isinstance(rows, list) else []:
        if not isinstance(row, dict):
            continue
        branch_id = row.get("branch_id", "unknown")
        for field in CANDIDATE_FIELDS:
            values = row.get(field, [])
            if not isinstance(values, list):
                continue
            for candidate in values:
                if not isinstance(candidate, dict) or not candidate.get("skill"):
                    continue
                candidates.append({
                    "branch_id": branch_id,
                    "field": field,
                    **candidate,
                })
    return candidates


def _audit_season_crosscheck(season_research: dict[str, Any]) -> dict[str, Any]:
    lens = "season_crosscheck"
    findings: list[dict[str, Any]] = []
    candidates = _candidate_entries(season_research)

    for candidate in candidates:
        name = candidate["skill"]
        entry = get_gem_entry(name)
        if not entry:
            findings.append(_finding("failure", "season_candidate_missing_from_taxonomy", lens=lens, subject=name, details={
                "branch_id": candidate["branch_id"],
                "field": candidate["field"],
            }))
            continue

        expected_socketable = candidate.get("socketable_gem")
        if expected_socketable is True and not entry.get("socketable"):
            findings.append(_finding("failure", "season_candidate_claims_socketable_but_taxonomy_rejects", lens=lens, subject=name, details={
                "branch_id": candidate["branch_id"],
                "field": candidate["field"],
                "taxonomy_kind": entry.get("gem_kind"),
                "support_alias_of": entry.get("support_alias_of"),
            }))
        if expected_socketable is False and entry.get("socketable") and candidate["field"] != "rejected_or_lower_priority_active_gems":
            findings.append(_finding("warning", "season_candidate_marks_socketable_skill_as_non_socketable", lens=lens, subject=name, details={
                "branch_id": candidate["branch_id"],
                "field": candidate["field"],
                "taxonomy_kind": entry.get("gem_kind"),
            }))

        if candidate["field"] in {"primary_offense_gems", "fallback_offense_gems", "carrier_gems"}:
            if not entry.get("socketable"):
                findings.append(_finding("failure", "primary_or_carrier_candidate_is_not_socketable", lens=lens, subject=name, details={
                    "branch_id": candidate["branch_id"],
                    "field": candidate["field"],
                    "taxonomy_kind": entry.get("gem_kind"),
                }))
            if entry.get("offense_class") != "offensive_active":
                findings.append(_finding("failure", "primary_or_carrier_candidate_not_offensive_active", lens=lens, subject=name, details={
                    "branch_id": candidate["branch_id"],
                    "field": candidate["field"],
                    "taxonomy_offense_class": entry.get("offense_class"),
                }))

    synthetic_build = _build({
        "Herald of Thunder": "Herald of Thunder - Lightning Penetration Support - Added Lightning Damage Support",
        "Static Strike Carrier": "Static Strike - Shockwave Support - Faster Attacks Support",
        "Blight Fallback": "Blight of Contagion - Void Manipulation Support - Efficacy Support",
    })
    context = build_season_research_context(synthetic_build)
    selected_ids = set(context.get("match", {}).get("selected_branch_ids", []))
    expected_ids = {"hot_autobomber", "static_strike_ngamahu", "blight_of_contagion_fallback"}
    if not expected_ids <= selected_ids:
        findings.append(_finding("failure", "season_context_missed_expected_branch", lens=lens, subject="synthetic_reliquarian_build", details={
            "expected": sorted(expected_ids),
            "actual": sorted(selected_ids),
        }))

    taxonomy_names = {
        row.get("name")
        for row in context.get("gem_taxonomy_lens", [])
        if isinstance(row, dict)
    }
    for name in ("Herald of Thunder", "Static Strike", "Blight of Contagion", "Molten Burst"):
        if name not in taxonomy_names:
            findings.append(_finding("failure", "season_context_missing_taxonomy_lens_entry", lens=lens, subject=name))

    rules = " ".join(context.get("coach_rules", []))
    if "gem_taxonomy_lens" not in rules or "socketable" not in rules:
        findings.append(_finding("failure", "coach_rules_do_not_require_taxonomy_crosscheck", lens=lens, subject="coach_rules"))

    return {
        "lens": lens,
        "checked_candidates": len(candidates),
        "selected_branch_ids": sorted(selected_ids),
        "context_taxonomy_entry_count": len(taxonomy_names),
        "findings": findings,
    }


def build_adversarial_audit() -> dict[str, Any]:
    taxonomy = _load_json(TAXONOMY_PATH)
    season_research = _load_json(SEASON_RESEARCH_PATH)
    entries = taxonomy.get("entries", {}) if isinstance(taxonomy.get("entries"), dict) else {}

    lenses = [
        _audit_source_integrity(entries),
        _audit_name_collisions(entries),
        _audit_socketability_pipeline(),
        _audit_context_scoring(),
        _audit_season_crosscheck(season_research),
    ]

    all_findings = [
        finding
        for lens in lenses
        for finding in lens.get("findings", [])
    ]
    failures = [item for item in all_findings if item.get("severity") == "failure"]
    warnings = [item for item in all_findings if item.get("severity") == "warning"]

    return {
        "dataset_kind": "poe1_gem_taxonomy_adversarial_audit",
        "schema_version": "1.0.0",
        "generated_by": "python/gem_taxonomy_adversarial_audit.py",
        "status": "passed" if not failures else "failed",
        "summary": {
            "lens_count": len(lenses),
            "taxonomy_entry_count": len(entries),
            "finding_count": len(all_findings),
            "failure_count": len(failures),
            "warning_count": len(warnings),
        },
        "lenses": [
            {
                key: value
                for key, value in lens.items()
                if key != "findings"
            } | {
                "finding_count": len(lens.get("findings", [])),
                "failure_count": sum(1 for item in lens.get("findings", []) if item.get("severity") == "failure"),
                "warning_count": sum(1 for item in lens.get("findings", []) if item.get("severity") == "warning"),
            }
            for lens in lenses
        ],
        "findings": all_findings,
    }


def write_adversarial_audit(path: Path = DEFAULT_OUTPUT_PATH) -> dict[str, Any]:
    audit = build_adversarial_audit()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(audit, f, ensure_ascii=False, indent=2)
        f.write("\n")
    return audit


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run POE1 gem taxonomy five-lens adversarial audit.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--fail-on-finding", action="store_true")
    args = parser.parse_args(argv)

    audit = write_adversarial_audit(args.output)
    print(json.dumps(audit["summary"], ensure_ascii=False, indent=2))
    if audit["summary"]["failure_count"]:
        return 1
    if args.fail_on_finding and audit["summary"]["finding_count"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
