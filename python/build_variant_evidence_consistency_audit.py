# -*- coding: utf-8 -*-
"""Audit evidence consistency between queue candidates and real-case seeds."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QUEUE_PATH = ROOT / "data" / "build_variant_collection_queue_v1.json"
REAL_CASES_PATH = ROOT / "data" / "build_variant_real_cases_v1.json"


def _load_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)



def _find_case(cases: list[dict], patch: str, candidate_id: str, archetype: str) -> dict | None:
    prefix = candidate_id + "_"
    for case in cases:
        if case["case_id"].startswith(prefix):
            return case
    for case in cases:
        if case.get("patch") == patch and case.get("archetype_id") == archetype:
            return case
    return None



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
    if value.startswith("video_transcript"):
        return "video_transcript"
    if value.startswith("manual_curated"):
        return "manual_curated"
    return value



def build_evidence_consistency_audit() -> dict:
    queue = _load_json(QUEUE_PATH)
    real_cases = _load_json(REAL_CASES_PATH)
    cases = real_cases["cases"]

    findings: list[dict] = []
    by_patch: dict[str, dict] = {}

    for patch_entry in queue["patches"]:
        patch = patch_entry["patch"]
        patch_findings = []
        for item in patch_entry["queue"]:
            if item.get("candidate_role") != "flagship":
                continue
            case = _find_case(cases, patch, item["candidate_id"], item["archetype"])
            if not case:
                patch_findings.append({
                    "patch": patch,
                    "candidate_id": item["candidate_id"],
                    "issue": "missing_real_case",
                    "severity": 3,
                })
                continue

            queue_sources = {_normalize_source(src) for src in item.get("evidence_sources", [])}
            case_sources = {_normalize_source(ev["type"]) for ev in case.get("evidence", [])}

            missing_from_case = sorted(queue_sources - case_sources)
            extra_in_case = sorted(case_sources - queue_sources)
            if missing_from_case:
                patch_findings.append({
                    "patch": patch,
                    "candidate_id": item["candidate_id"],
                    "case_id": case["case_id"],
                    "issue": "queue_case_source_mismatch",
                    "severity": 2,
                    "missing_from_case": missing_from_case,
                    "extra_in_case": extra_in_case,
                })

            if case.get("source_status") == "provisional_seeded" and len(queue_sources) >= 2 and item.get("source_confidence") == "medium":
                patch_findings.append({
                    "patch": patch,
                    "candidate_id": item["candidate_id"],
                    "case_id": case["case_id"],
                    "issue": "promotion_candidate",
                    "severity": 1,
                    "queue_sources": sorted(queue_sources),
                    "case_sources": sorted(case_sources),
                })

        by_patch[patch] = {
            "patch": patch,
            "finding_count": len(patch_findings),
            "high_severity_count": sum(1 for item in patch_findings if item["severity"] >= 3),
            "promotion_candidate_count": sum(1 for item in patch_findings if item["issue"] == "promotion_candidate"),
        }
        findings.extend(patch_findings)

    findings.sort(key=lambda item: (-item["severity"], item["patch"], item["candidate_id"], item["issue"]))
    return {
        "dataset_kind": "poe1_build_variant_evidence_consistency_audit",
        "finding_count": len(findings),
        "findings": findings,
        "by_patch": [by_patch[key] for key in sorted(by_patch.keys())],
    }


if __name__ == "__main__":
    print(json.dumps(build_evidence_consistency_audit(), ensure_ascii=False, indent=2))
