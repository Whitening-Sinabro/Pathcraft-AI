# -*- coding: utf-8 -*-
"""Build a concrete promotion backlog for provisional build cases."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REAL_CASES_PATH = ROOT / "data" / "build_variant_real_cases_v1.json"
QUEUE_PATH = ROOT / "data" / "build_variant_collection_queue_v1.json"


def _load_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)



def _normalize_source(value: str) -> str:
    value = value.strip().lower()
    if value.startswith("poe_vault_"):
        return "poe_vault"
    if value.startswith("maxroll_"):
        return "maxroll"
    if value.startswith("icy_veins_"):
        return "icy_veins"
    if value.startswith("forum_build_guide_"):
        return "forum_build_guide"
    if value.startswith("reddit_build_index_"):
        return "reddit_build_index"
    if value.startswith("youtube_"):
        return "youtube"
    if value.startswith("pob_archive_") or value.startswith("pob_archives_"):
        return "pob_archives"
    if value.startswith("creator_guide_") or value.startswith("manual_markdown_guide_"):
        return "creator_guide"
    if value.startswith("commercial_build_article_"):
        return "commercial_build_article"
    if value.startswith("official_patch_notes_"):
        return "official_patch_notes"
    if value.startswith("raw_transition_patterns"):
        return "raw_transition_patterns"
    if value.startswith("curated_transition_patterns"):
        return "curated_transition_patterns"
    if value.startswith("local_discussion_trace"):
        return "local_discussion_trace"
    return value



def _classify_next_step(evidence_types: set[str]) -> tuple[str, int]:
    has_poe_vault = "poe_vault" in evidence_types
    has_maxroll = "maxroll" in evidence_types
    has_external = bool(evidence_types & {
        "poe_vault",
        "maxroll",
        "icy_veins",
        "forum_build_guide",
        "reddit_build_index",
        "youtube",
        "pob_archives",
        "creator_guide",
        "commercial_build_article",
    })
    has_patch = "official_patch_notes" in evidence_types
    has_curated = "curated_transition_patterns" in evidence_types
    has_raw = "raw_transition_patterns" in evidence_types
    has_local = "local_discussion_trace" in evidence_types

    if has_poe_vault and not has_maxroll and not has_patch:
        return "find_second_external_source", 3
    if has_maxroll and not has_poe_vault and not has_patch:
        return "find_second_external_source", 3
    if has_patch and has_local and not has_external:
        return "find_external_confirmation", 3
    if has_curated and has_raw and not has_external:
        return "find_first_external_source", 2
    if has_poe_vault and has_curated and not has_maxroll:
        return "find_second_external_source", 2
    if has_raw and not has_curated and not has_external:
        return "find_external_or_curated_confirmation", 2
    if has_external:
        return "find_second_external_source", 2
    return "manual_review", 1



def build_promotion_backlog() -> dict:
    real_cases = _load_json(REAL_CASES_PATH)
    queue = _load_json(QUEUE_PATH)

    queue_index = {}
    queue_items = []
    for patch_entry in queue["patches"]:
        for item in patch_entry["queue"]:
            queue_index[(patch_entry["patch"], item.get("archetype"))] = item
            queue_items.append((patch_entry["patch"], item))

    backlog: list[dict] = []
    by_patch: dict[str, dict] = {}

    for case in real_cases["cases"]:
        if case.get("source_status") != "provisional_seeded":
            continue
        evidence_types = {_normalize_source(item["type"]) for item in case.get("evidence", [])}
        next_step, urgency = _classify_next_step(evidence_types)
        queue_item = queue_index.get((case["patch"], case["archetype_id"]))
        if queue_item is None:
            queue_item = next(
                (item for patch, item in queue_items if patch == case["patch"] and case["case_id"].startswith(item["candidate_id"] + "_")),
                None,
            )
        backlog.append({
            "patch": case["patch"],
            "case_id": case["case_id"],
            "archetype_id": case["archetype_id"],
            "candidate_id": queue_item["candidate_id"] if queue_item else None,
            "confidence": case.get("confidence"),
            "evidence_types": sorted(evidence_types),
            "next_step": next_step,
            "urgency": urgency,
        })

    backlog.sort(key=lambda item: (-item["urgency"], item["patch"], item["case_id"]))

    for item in backlog:
        patch = item["patch"]
        by_patch.setdefault(patch, {
            "patch": patch,
            "provisional_count": 0,
            "urgent_count": 0,
            "top_candidates": [],
        })
        by_patch[patch]["provisional_count"] += 1
        if item["urgency"] >= 3:
            by_patch[patch]["urgent_count"] += 1
        if len(by_patch[patch]["top_candidates"]) < 3:
            by_patch[patch]["top_candidates"].append(item["candidate_id"])

    return {
        "dataset_kind": "poe1_build_variant_promotion_backlog",
        "item_count": len(backlog),
        "items": backlog,
        "by_patch": [by_patch[key] for key in sorted(by_patch.keys())],
    }


if __name__ == "__main__":
    print(json.dumps(build_promotion_backlog(), ensure_ascii=False, indent=2))
