# -*- coding: utf-8 -*-
"""Build normalized state snapshots from promoted parsed PoB artifacts."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from build_corpus_promote_ready_pobs import pob_url_slug, safe_slug


ROOT = Path(__file__).resolve().parent.parent
PROMOTED_PATH = ROOT / "data" / "build_corpus_promoted_instances.latest.json"
OUT_PATH = ROOT / "data" / "build_corpus_promoted_case_snapshots.latest.json"


def _load_json(path: Path) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def clean_notes(text: str) -> str:
    cleaned = re.sub(r"\^x[0-9A-Fa-f]{6}", "", text)
    cleaned = cleaned.replace("^7", "")
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


FAQ_PATTERN = re.compile(
    r"^\s*--(?P<title>[^-\n][^-]*?)--(?P<body>.*?)(?=^\s*--[^-\n][^-]*?--|\Z)",
    re.DOTALL | re.MULTILINE,
)


def extract_beginner_failure_findings(notes: str) -> list[dict[str, str]]:
    cleaned = clean_notes(notes)
    findings = []
    for match in FAQ_PATTERN.finditer(cleaned):
        title = " ".join(match.group("title").split())
        body = " ".join(match.group("body").split())
        lowered = f"{title} {body}".lower()
        if "damage feel low" in lowered:
            tag = "low_damage_due_to_corpse_or_spectre_setup"
        elif "attributes" in lowered:
            tag = "attribute_requirements_not_met"
        elif "energy shield" in lowered or "mana" in lowered:
            tag = "resource_cost_or_energy_shield_gate"
        elif "too many buttons" in lowered or "automate" in lowered:
            tag = "button_pressure_trigger_weapon_gate"
        elif "degen" in lowered or "blood rage" in lowered:
            tag = "self_degen_requires_regen_mastery"
        else:
            tag = "guide_faq_warning"
        findings.append(
            {
                "finding_id": safe_slug(title).lower(),
                "risk_tag": tag,
                "question": title,
                "summary": body[:500],
            }
        )
    return findings


def _gem_name(gem: dict[str, Any]) -> str:
    return gem.get("name_spec") or gem.get("skill_id") or ""


def _skill_snapshot(skill_set: dict[str, Any], active_skill_set_id: str) -> dict[str, Any]:
    skills = []
    for skill in skill_set.get("skills") or []:
        gems = [_gem_name(gem) for gem in skill.get("gems") or [] if _gem_name(gem)]
        if not gems:
            continue
        skills.append(
            {
                "label": skill.get("label") or gems[0],
                "enabled": str(skill.get("enabled") or "").lower() == "true",
                "main_active_skill": str(skill.get("main_active_skill") or "").lower() == "1",
                "active_gem": gems[0],
                "support_gems": gems[1:],
                "link_count": len(gems),
            }
        )
    main = next((skill for skill in skills if skill["enabled"] and skill["main_active_skill"]), None)
    if main is None:
        main = next((skill for skill in skills if skill["enabled"]), None)
    if main is None and skills:
        main = skills[0]
    title = skill_set.get("title") or f"SkillSet {skill_set.get('id', '')}"
    return {
        "state_id": safe_slug(title).lower(),
        "source": "pob_skill_set",
        "title": title,
        "skill_set_id": skill_set.get("id", ""),
        "is_active_final": skill_set.get("id", "") == active_skill_set_id,
        "main_skill": (main or {}).get("active_gem", ""),
        "skill_group_count": len(skills),
        "skill_groups": skills,
    }


def _tree_snapshot(spec: dict[str, Any], active_spec_id: str) -> dict[str, Any]:
    title = spec.get("title") or f"Tree {spec.get('id', '')}"
    return {
        "state_id": safe_slug(title).lower(),
        "source": "pob_tree_spec",
        "title": title,
        "tree_spec_id": spec.get("id", ""),
        "is_active_tree": spec.get("id", "") == active_spec_id,
        "tree_version": spec.get("tree_version", ""),
        "url_present": bool(spec.get("url")),
        "jewel_socket_count": len(spec.get("sockets") or []),
    }


def build_case_snapshot(promoted_row: dict[str, Any]) -> dict[str, Any]:
    build_path = ROOT / promoted_row["artifact_paths"]["build_data"]
    build_data = _load_json(build_path)
    raw = build_data.get("pob_raw") or {}
    skills = raw.get("skills") or {}
    tree = raw.get("tree") or {}
    skill_snapshots = [
        _skill_snapshot(skill_set, skills.get("active_skill_set_id", ""))
        for skill_set in skills.get("skill_sets") or []
    ]
    tree_snapshots = [
        _tree_snapshot(spec, tree.get("active_spec_id", ""))
        for spec in tree.get("specs") or []
    ]
    all_titles = [row["title"].lower() for row in skill_snapshots + tree_snapshots]
    return {
        "case_id": f"{promoted_row['candidate_id']}.{pob_url_slug(promoted_row['url'])}",
        "candidate_id": promoted_row["candidate_id"],
        "display_name": promoted_row["display_name"],
        "source_pob": promoted_row["url"],
        "artifact_paths": promoted_row["artifact_paths"],
        "parsed_summary": promoted_row["parsed_summary"],
        "state_snapshot_count": len(skill_snapshots) + len(tree_snapshots),
        "skill_state_snapshots": skill_snapshots,
        "tree_state_snapshots": tree_snapshots,
        "beginner_failure_findings": extract_beginner_failure_findings(build_data.get("build_notes") or ""),
        "minimum_snapshot_contract": {
            "has_two_or_more_snapshots": len(skill_snapshots) + len(tree_snapshots) >= 2,
            "has_leveling_state": any("lvl" in title or "level" in title for title in all_titles),
            "has_mapping_or_final_state": any(
                "map" in title or "late" in title or "endgame" in title or "final" in title
                for title in all_titles
            ),
        },
    }


def build_promoted_case_snapshots() -> dict[str, Any]:
    promoted_data = _load_json(PROMOTED_PATH)
    cases = [build_case_snapshot(row) for row in promoted_data.get("promoted", [])]
    return {
        "schema_version": "1.0",
        "dataset_kind": "poe1_build_corpus_promoted_case_snapshots",
        "updated_at": "2026-07-17",
        "summary": {
            "case_count": len(cases),
            "state_snapshot_count": sum(case["state_snapshot_count"] for case in cases),
            "beginner_failure_finding_count": sum(
                len(case["beginner_failure_findings"])
                for case in cases
            ),
        },
        "cases": cases,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help=f"Write {OUT_PATH.relative_to(ROOT)}")
    args = parser.parse_args()

    result = build_promoted_case_snapshots()
    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.write:
        OUT_PATH.write_text(text + "\n", encoding="utf-8")
    print(json.dumps(result["summary"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
