# -*- coding: utf-8 -*-
"""Build simple coverage summaries for the POE1 variant corpus work."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
QUEUE_PATH = ROOT / "data" / "build_variant_collection_queue_v1.json"
REAL_CASES_PATH = ROOT / "data" / "build_variant_real_cases_v1.json"


def _load_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def build_coverage_summary() -> dict:
    queue = _load_json(QUEUE_PATH)
    real_cases = _load_json(REAL_CASES_PATH)

    seeded_case_ids = {case["case_id"] for case in real_cases["cases"]}
    provisional_case_ids = {
        case["case_id"]
        for case in real_cases["cases"]
        if case.get("source_status") == "provisional_seeded"
    }
    by_patch: dict[str, dict] = {}

    for patch_entry in queue["patches"]:
        patch = patch_entry["patch"]
        target = patch_entry["target_flagship_count"]
        items = patch_entry["queue"]
        flagship_items = [item for item in items if item.get("candidate_role", "flagship") == "flagship"]
        personal_target_items = [item for item in items if item.get("candidate_role") == "personal_target"]

        seeded = [item for item in flagship_items if item["status"] == "seeded_into_real_cases_v1"]
        blocked = [item for item in flagship_items if "blocked" in item["status"]]
        needs_verification = [item for item in flagship_items if "verification" in item["status"]]
        personal_target_seeded = [item for item in personal_target_items if item["status"] == "seeded_into_real_cases_v1"]
        provisional_seeded = [
            item for item in flagship_items
            if item["status"] == "seeded_into_real_cases_v1"
            and any(case_id.startswith(item["candidate_id"] + "_") for case_id in provisional_case_ids)
        ]
        confirmed_seeded = [item for item in seeded if item not in provisional_seeded]

        by_patch[patch] = {
            "patch": patch,
            "league_name": patch_entry["league_name"],
            "target_flagship_count": target,
            "queue_count": len(items),
            "flagship_queue_count": len(flagship_items),
            "personal_target_count": len(personal_target_items),
            "seeded_count": len(seeded),
            "confirmed_seeded_count": len(confirmed_seeded),
            "provisional_seeded_count": len(provisional_seeded),
            "blocked_count": len(blocked),
            "needs_verification_count": len(needs_verification),
            "personal_target_seeded_count": len(personal_target_seeded),
            "coverage_ratio": round(len(seeded) / target, 3) if target else 0.0,
            "confirmed_coverage_ratio": round(len(confirmed_seeded) / target, 3) if target else 0.0,
        }

    return {
        "queue_dataset_kind": queue["dataset_kind"],
        "real_case_dataset_kind": real_cases["dataset_kind"],
        "real_case_count": len(real_cases["cases"]),
        "real_case_ids": sorted(seeded_case_ids),
        "by_patch": [by_patch[key] for key in sorted(by_patch.keys())],
    }


if __name__ == "__main__":
    print(json.dumps(build_coverage_summary(), ensure_ascii=False, indent=2))
