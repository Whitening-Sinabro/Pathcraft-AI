# -*- coding: utf-8 -*-
"""Build a ranked research queue from promotion and strict verification audits."""

from __future__ import annotations

import json
from pathlib import Path

from build_variant_promotion_backlog import build_promotion_backlog
from build_variant_verification_audit import build_verification_audit

ROOT = Path(__file__).resolve().parent.parent

PATCH_ORDER = ["3.22", "3.23", "3.24", "3.25", "3.26", "3.27", "3.28"]
PATCH_RANK = {patch: index for index, patch in enumerate(PATCH_ORDER, start=1)}
VERDICT_BASE_SCORE = {
    "blocked_no_external_build_guide": 100,
    "provisional_external_gap": 80,
    "standard_only": 60,
    "blocked_no_verifiable_support": 50,
    "strict_confirmed": 0,
}
NEXT_STEP_SCORE = {
    "find_first_external_build_guide_source": 30,
    "find_second_external_build_guide_source": 20,
    "manual_review": 10,
    "none": 0,
}
CONFIDENCE_SCORE = {
    "low": 10,
    "medium": 5,
    "high": 0,
}


def build_research_queue() -> dict:
    verification = build_verification_audit()
    promotion = build_promotion_backlog()

    promotion_index = {item["candidate_id"]: item for item in promotion["items"] if item.get("candidate_id")}
    patch_index = {item["patch"]: item for item in verification["by_patch"]}

    items: list[dict] = []
    for record in verification["items"]:
        if record["strict_confirmable"]:
            continue

        patch_summary = patch_index[record["patch"]]
        promotion_item = promotion_index.get(record["candidate_id"])
        patch_penalty = max(0, 5 - patch_summary["strict_confirmable_count"]) * 4
        recency_bonus = PATCH_RANK.get(record["patch"], 0)
        score = (
            VERDICT_BASE_SCORE.get(record["strict_verdict"], 0)
            + NEXT_STEP_SCORE.get(record["next_step"], 0)
            + CONFIDENCE_SCORE.get(record.get("confidence"), 0)
            + patch_penalty
            + recency_bonus
        )

        items.append({
            "patch": record["patch"],
            "candidate_id": record["candidate_id"],
            "case_id": record["case_id"],
            "archetype_id": record["archetype_id"],
            "strict_verdict": record["strict_verdict"],
            "next_step": record["next_step"],
            "confidence": record.get("confidence"),
            "priority_score": score,
            "patch_strict_confirmable_count": patch_summary["strict_confirmable_count"],
            "patch_strict_gap_count": patch_summary["strict_gap_count"],
            "guide_source_families": record["guide_source_families"],
            "context_source_families": record["context_source_families"],
            "local_source_families": record["local_source_families"],
            "blockers": record["blockers"],
            "promotion_urgency": promotion_item["urgency"] if promotion_item else None,
            "promotion_evidence_types": promotion_item["evidence_types"] if promotion_item else None,
        })

    items.sort(key=lambda item: (-item["priority_score"], -PATCH_RANK.get(item["patch"], 0), item["candidate_id"]))

    by_patch: dict[str, dict] = {}
    by_next_step: dict[str, dict] = {}
    for item in items:
        by_patch.setdefault(item["patch"], {
            "patch": item["patch"],
            "item_count": 0,
            "top_candidates": [],
            "max_priority_score": item["priority_score"],
        })
        by_patch[item["patch"]]["item_count"] += 1
        if len(by_patch[item["patch"]]["top_candidates"]) < 3:
            by_patch[item["patch"]]["top_candidates"].append(item["candidate_id"])
        by_patch[item["patch"]]["max_priority_score"] = max(by_patch[item["patch"]]["max_priority_score"], item["priority_score"])

        by_next_step.setdefault(item["next_step"], {
            "next_step": item["next_step"],
            "item_count": 0,
            "top_candidates": [],
        })
        by_next_step[item["next_step"]]["item_count"] += 1
        if len(by_next_step[item["next_step"]]["top_candidates"]) < 5:
            by_next_step[item["next_step"]]["top_candidates"].append(item["candidate_id"])

    return {
        "dataset_kind": "poe1_build_variant_research_queue",
        "item_count": len(items),
        "items": items,
        "by_patch": [by_patch[key] for key in sorted(by_patch.keys())],
        "by_next_step": [by_next_step[key] for key in sorted(by_next_step.keys())],
    }


if __name__ == "__main__":
    print(json.dumps(build_research_queue(), ensure_ascii=False, indent=2))
