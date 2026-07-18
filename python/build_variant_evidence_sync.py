# -*- coding: utf-8 -*-
"""Sync queue evidence sources into real-case evidence for seeded flagship cases."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QUEUE_PATH = ROOT / "data" / "build_variant_collection_queue_v1.json"
REAL_CASES_PATH = ROOT / "data" / "build_variant_real_cases_v1.json"

LABELS = {
    "maxroll": "Maxroll external cross-check",
    "poe_vault": "PoE Vault external cross-check",
    "official_patch_notes": "Official patch notes support",
    "raw_transition_patterns": "Local raw transition trace",
    "curated_transition_patterns": "Curated transition support",
    "local_discussion_trace": "Local discussion trace",
}


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



def _find_case(cases: list[dict], patch: str, candidate_id: str, archetype: str) -> dict | None:
    prefix = candidate_id + "_"
    for case in cases:
        if case["case_id"].startswith(prefix):
            return case
    for case in cases:
        if case.get("patch") == patch and case.get("archetype_id") == archetype:
            return case
    return None



def sync_evidence() -> dict:
    queue = _load_json(QUEUE_PATH)
    real = _load_json(REAL_CASES_PATH)
    cases = real["cases"]
    updates = []

    for patch_entry in queue["patches"]:
        patch = patch_entry["patch"]
        for item in patch_entry["queue"]:
            if item.get("candidate_role") != "flagship":
                continue
            if item.get("status") != "seeded_into_real_cases_v1":
                continue
            case = _find_case(cases, patch, item["candidate_id"], item["archetype"])
            if not case:
                continue
            existing_norm = {_normalize_source(ev["type"]) for ev in case.get("evidence", [])}
            appended = []
            for src in item.get("evidence_sources", []):
                norm = _normalize_source(src)
                if norm in existing_norm:
                    continue
                case.setdefault("evidence", []).append({
                    "type": src,
                    "label": LABELS.get(norm, "Synced queue evidence"),
                })
                existing_norm.add(norm)
                appended.append(src)
            if appended:
                updates.append({
                    "patch": patch,
                    "candidate_id": item["candidate_id"],
                    "case_id": case["case_id"],
                    "added_sources": appended,
                })

    with open(REAL_CASES_PATH, "w", encoding="utf-8") as f:
        json.dump(real, f, ensure_ascii=False, indent=2)
        f.write("\n")

    return {
        "updated_case_count": len(updates),
        "updates": updates,
    }


if __name__ == "__main__":
    print(json.dumps(sync_evidence(), ensure_ascii=False, indent=2))
