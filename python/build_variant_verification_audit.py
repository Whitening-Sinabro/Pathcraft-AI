# -*- coding: utf-8 -*-
"""Apply stricter verification gates to flagship build cases."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QUEUE_PATH = ROOT / "data" / "build_variant_collection_queue_v1.json"
REAL_CASES_PATH = ROOT / "data" / "build_variant_real_cases_v1.json"


def _load_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def _normalize_source(value: str) -> tuple[str, str]:
    value = value.strip().lower()
    if value.startswith("poe_vault_"):
        return "poe_vault", "external_build_guide"
    if value.startswith("maxroll_"):
        return "maxroll", "external_build_guide"
    if value.startswith("icy_veins_"):
        return "icy_veins", "external_build_guide"
    if value.startswith("forum_build_guide_"):
        return "forum_build_guide", "external_build_guide"
    if value.startswith("reddit_build_index_"):
        return "reddit_build_index", "external_build_guide"
    if value.startswith("youtube_"):
        return "youtube", "external_build_guide"
    if value.startswith("pob_archive_") or value.startswith("pob_archives_"):
        return "pob_archives", "external_build_guide"
    if value.startswith("creator_guide_") or value.startswith("manual_markdown_guide_"):
        return "creator_guide", "external_build_guide"
    if value.startswith("commercial_build_article_"):
        return "commercial_build_article", "external_build_guide"
    if value.startswith("official_patch_notes_"):
        return "official_patch_notes", "official_context"
    if value.startswith("raw_transition_patterns"):
        return "raw_transition_patterns", "local_trace"
    if value.startswith("curated_transition_patterns"):
        return "curated_transition_patterns", "local_trace"
    if value.startswith("local_discussion_trace"):
        return "local_discussion_trace", "local_trace"
    return value, "other"


def _find_case_for_candidate(cases: list[dict], patch: str, candidate_id: str, archetype: str) -> dict | None:
    prefix = candidate_id + "_"
    for case in cases:
        if case["case_id"].startswith(prefix):
            return case
    for case in cases:
        if case.get("patch") == patch and case.get("archetype_id") == archetype:
            return case
    return None


def _classify_case(case: dict) -> dict:
    normalized_sources = []
    guide_families: set[str] = set()
    context_families: set[str] = set()
    local_families: set[str] = set()

    for evidence in case.get("evidence", []):
        family, bucket = _normalize_source(evidence["type"])
        normalized_sources.append({
            "source_type": evidence["type"],
            "family": family,
            "bucket": bucket,
        })
        if bucket == "external_build_guide":
            guide_families.add(family)
        elif bucket == "official_context":
            context_families.add(family)
        elif bucket == "local_trace":
            local_families.add(family)
        else:
            context_families.add(family)

    evidence_family_count = len({item["family"] for item in normalized_sources})
    standard_confirmable = len(guide_families) >= 1 and evidence_family_count >= 2
    strict_confirmable = len(guide_families) >= 2

    blockers: list[str] = []
    if not guide_families:
        blockers.append("missing_external_build_guide")
    elif len(guide_families) == 1:
        blockers.append("missing_second_external_build_guide")

    if guide_families and not strict_confirmable and context_families:
        blockers.append("single_external_plus_context_only")
    if guide_families and not strict_confirmable and local_families and not context_families:
        blockers.append("single_external_plus_local_trace_only")
    if not guide_families and context_families and local_families:
        blockers.append("mechanic_context_without_meta_confirmation")
    if not guide_families and local_families and not context_families:
        blockers.append("local_trace_without_external_confirmation")
    if len(guide_families) == 1 and evidence_family_count == 1:
        blockers.append("single_source_only")

    if strict_confirmable:
        strict_verdict = "strict_confirmed"
        next_step = "none"
    elif standard_confirmable:
        strict_verdict = "standard_only"
        next_step = "find_second_external_build_guide_source"
    elif guide_families:
        strict_verdict = "provisional_external_gap"
        next_step = "find_second_external_build_guide_source"
    elif context_families or local_families:
        strict_verdict = "blocked_no_external_build_guide"
        next_step = "find_first_external_build_guide_source"
    else:
        strict_verdict = "blocked_no_verifiable_support"
        next_step = "manual_review"

    return {
        "normalized_sources": normalized_sources,
        "guide_source_families": sorted(guide_families),
        "context_source_families": sorted(context_families),
        "local_source_families": sorted(local_families),
        "evidence_family_count": evidence_family_count,
        "standard_confirmable": standard_confirmable,
        "strict_confirmable": strict_confirmable,
        "strict_verdict": strict_verdict,
        "blockers": blockers,
        "next_step": next_step,
    }


def build_verification_audit() -> dict:
    queue = _load_json(QUEUE_PATH)
    real_cases = _load_json(REAL_CASES_PATH)
    cases = real_cases["cases"]

    items: list[dict] = []
    by_patch: dict[str, dict] = {}

    for patch_entry in queue["patches"]:
        patch = patch_entry["patch"]
        patch_items: list[dict] = []

        for item in patch_entry["queue"]:
            if item.get("candidate_role") != "flagship":
                continue
            case = _find_case_for_candidate(cases, patch, item["candidate_id"], item["archetype"])
            if not case or item["status"] != "seeded_into_real_cases_v1":
                continue

            classification = _classify_case(case)
            record = {
                "patch": patch,
                "candidate_id": item["candidate_id"],
                "case_id": case["case_id"],
                "archetype_id": case["archetype_id"],
                "source_status": case.get("source_status"),
                "confidence": case.get("confidence"),
                **classification,
            }
            items.append(record)
            patch_items.append(record)

        by_patch[patch] = {
            "patch": patch,
            "flagship_seeded_count": len(patch_items),
            "current_confirmed_count": sum(1 for x in patch_items if x["source_status"] != "provisional_seeded"),
            "standard_confirmable_count": sum(1 for x in patch_items if x["standard_confirmable"]),
            "strict_confirmable_count": sum(1 for x in patch_items if x["strict_confirmable"]),
            "strict_gap_count": sum(1 for x in patch_items if not x["strict_confirmable"]),
            "blocked_no_external_count": sum(1 for x in patch_items if x["strict_verdict"] == "blocked_no_external_build_guide"),
            "top_strict_gaps": [
                x["candidate_id"]
                for x in sorted(
                    (entry for entry in patch_items if not entry["strict_confirmable"]),
                    key=lambda entry: (entry["strict_verdict"], entry["candidate_id"]),
                )[:3]
            ],
        }

    items.sort(key=lambda entry: (entry["patch"], entry["candidate_id"]))

    overall = {
        "flagship_seeded_count": len(items),
        "current_confirmed_count": sum(1 for x in items if x["source_status"] != "provisional_seeded"),
        "standard_confirmable_count": sum(1 for x in items if x["standard_confirmable"]),
        "strict_confirmable_count": sum(1 for x in items if x["strict_confirmable"]),
        "strict_gap_count": sum(1 for x in items if not x["strict_confirmable"]),
        "blocked_no_external_count": sum(1 for x in items if x["strict_verdict"] == "blocked_no_external_build_guide"),
    }

    return {
        "dataset_kind": "poe1_build_variant_verification_audit",
        "overall": overall,
        "items": items,
        "by_patch": [by_patch[key] for key in sorted(by_patch.keys())],
    }


if __name__ == "__main__":
    print(json.dumps(build_verification_audit(), ensure_ascii=False, indent=2))
