# -*- coding: utf-8 -*-
"""Audit provisional build cases and rank confirmation priorities."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QUEUE_PATH = ROOT / "data" / "build_variant_collection_queue_v1.json"
REAL_CASES_PATH = ROOT / "data" / "build_variant_real_cases_v1.json"


PROVISIONAL_REASONS = {
    "poe_vault_only": 3,
    "maxroll_only": 3,
    "patch_note_only": 3,
    "local_trace_only": 3,
    "mixed_single_source": 2,
    "curated_plus_local_only": 2,
}



def _load_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)



def _find_case_for_candidate(cases: list[dict], patch: str, candidate_id: str, archetype: str) -> dict | None:
    prefix = candidate_id + "_"
    for case in cases:
        if case["case_id"].startswith(prefix):
            return case
    for case in cases:
        if case.get("patch") == patch and case.get("archetype_id") == archetype:
            return case
    return None



def _reason_for_case(case: dict) -> str:
    evidence_types = {item["type"] for item in case.get("evidence", [])}
    if len(evidence_types) == 1 and any(t.startswith("poe_vault_") for t in evidence_types):
        return "poe_vault_only"
    if len(evidence_types) == 1 and any(t.startswith("maxroll_") for t in evidence_types):
        return "maxroll_only"
    if evidence_types == {"official_patch_notes_3_28", "local_discussion_trace"}:
        return "patch_note_only"
    if evidence_types == {"raw_transition_patterns", "curated_transition_patterns"}:
        return "curated_plus_local_only"
    if "official_patch_notes_3_28" in evidence_types and len(evidence_types) <= 2:
        return "patch_note_only"
    if any(t.startswith("poe_vault_") for t in evidence_types) and len(evidence_types) == 2 and "curated_transition_patterns" in evidence_types:
        return "mixed_single_source"
    return "mixed_single_source"



def build_confidence_audit() -> dict:
    queue = _load_json(QUEUE_PATH)
    real_cases = _load_json(REAL_CASES_PATH)
    cases = real_cases["cases"]

    priorities: list[dict] = []
    by_patch: dict[str, dict] = {}

    for patch_entry in queue["patches"]:
        patch = patch_entry["patch"]
        provisional_items = []
        confirmed_items = []

        for item in patch_entry["queue"]:
            if item.get("candidate_role") != "flagship":
                continue
            case = _find_case_for_candidate(cases, patch, item["candidate_id"], item["archetype"])
            if not case or item["status"] != "seeded_into_real_cases_v1":
                continue
            if case.get("source_status") == "provisional_seeded":
                reason = _reason_for_case(case)
                evidence_types = [ev["type"] for ev in case.get("evidence", [])]
                priority_score = PROVISIONAL_REASONS.get(reason, 1)
                record = {
                    "patch": patch,
                    "candidate_id": item["candidate_id"],
                    "case_id": case["case_id"],
                    "reason": reason,
                    "priority_score": priority_score,
                    "confidence": case.get("confidence"),
                    "evidence_types": evidence_types,
                }
                priorities.append(record)
                provisional_items.append(record)
            else:
                confirmed_items.append(item["candidate_id"])

        by_patch[patch] = {
            "patch": patch,
            "confirmed_count": len(confirmed_items),
            "provisional_count": len(provisional_items),
            "top_provisional_candidates": [
                item["candidate_id"] for item in sorted(provisional_items, key=lambda x: (-x["priority_score"], x["candidate_id"]))[:3]
            ],
        }

    priorities.sort(key=lambda x: (-x["priority_score"], x["patch"], x["candidate_id"]))
    return {
        "dataset_kind": "poe1_build_variant_confidence_audit",
        "priority_count": len(priorities),
        "priorities": priorities,
        "by_patch": [by_patch[key] for key in sorted(by_patch.keys())],
    }


if __name__ == "__main__":
    print(json.dumps(build_confidence_audit(), ensure_ascii=False, indent=2))
