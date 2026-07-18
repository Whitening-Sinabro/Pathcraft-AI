# -*- coding: utf-8 -*-
"""Build an internal source-slot queue for representative PoE1 builds.

This file is intentionally not a user-facing dashboard feed. It records which
source slots still need original links so the recommendation corpus can be
upgraded without exposing collection work to players.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
PROFILES_PATH = ROOT / "data" / "poe1_representative_build_profiles.latest.json"
MANUAL_POB_SOURCES_PATH = ROOT / "data" / "build_corpus_manual_pob_sources_v1.json"
OUT_PATH = ROOT / "data" / "poe1_representative_source_slot_queue.latest.json"


SOURCE_SLOTS = (
    {
        "slot_id": "guide",
        "slot_label": "original guide/video",
        "tokens": ("youtube", "twitch", "guide", "maxroll", "poe_vault", "creator", "video"),
    },
    {
        "slot_id": "endgame_pob",
        "slot_label": "endgame PoB",
        "tokens": ("pobb", "pob", "pastebin", "path of building", "endgame"),
    },
    {
        "slot_id": "leveling_pob",
        "slot_label": "leveling PoB",
        "tokens": ("leveling pob", "campaign pob", "act pob", "starter pob", "league-start pob"),
    },
    {
        "slot_id": "poe_ninja",
        "slot_label": "poe.ninja character snapshot",
        "tokens": ("poe.ninja", "ninja", "character", "profile"),
    },
)


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _text(*values: Any) -> str:
    return " ".join(str(value) for value in values if value).casefold()


def _matches_slot(evidence: dict[str, Any], slot: dict[str, Any]) -> bool:
    haystack = _text(evidence.get("type"), evidence.get("label"), evidence.get("url"), evidence.get("notes"))
    return any(token in haystack for token in slot["tokens"])


def _manual_source_index() -> dict[str, list[dict[str, Any]]]:
    if not MANUAL_POB_SOURCES_PATH.exists():
        return {}
    records = _load_json(MANUAL_POB_SOURCES_PATH).get("records", [])
    index: dict[str, list[dict[str, Any]]] = {}
    for record in records:
        candidate_id = record.get("candidate_id")
        if not candidate_id:
            continue
        items: list[dict[str, Any]] = []
        source_url = record.get("source_url")
        if source_url:
            items.append(
                {
                    "type": record.get("source_family") or "guide",
                    "label": record.get("source_label") or record.get("display_name") or source_url,
                    "url": source_url,
                    "notes": "manual_pob_source_record",
                }
            )
        for pob in record.get("pob_urls", []):
            url = pob.get("url")
            if not url:
                continue
            role = pob.get("role") or "pob"
            context = pob.get("context") or "Manual PoB source record."
            items.append(
                {
                    "type": "pobb" if "pobb.in" in url else "pob",
                    "label": f"{record.get('display_name') or candidate_id} {role} PoB",
                    "url": url,
                    "notes": context,
                }
            )
        if items:
            index.setdefault(candidate_id, []).extend(items)
    return index


def _compact_evidence(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    compacted = []
    seen: set[tuple[str, str, str]] = set()
    for item in items:
        key = (str(item.get("type") or ""), str(item.get("label") or ""), str(item.get("url") or ""))
        if key in seen:
            continue
        seen.add(key)
        compacted.append(
            {
                "type": item.get("type"),
                "label": item.get("label"),
                "url": item.get("url"),
                "notes": item.get("notes"),
            }
        )
    return compacted


def _suggested_queries(identity: dict[str, Any], slot_id: str) -> list[str]:
    build_name = identity.get("build_name") or identity.get("main_skill") or "PoE build"
    main_skill = identity.get("main_skill") or build_name
    ascendancy = identity.get("ascendancy") or ""
    patch = identity.get("patch") or "3.29"
    base = " ".join(part for part in (str(patch), str(main_skill), str(ascendancy)) if part)
    if slot_id == "guide":
        return [
            f'"{build_name}" "{patch}" guide',
            f'site:youtube.com "{main_skill}" "{ascendancy}" PoE {patch}',
            f'"{base}" league starter',
        ]
    if slot_id == "endgame_pob":
        return [
            f'"{build_name}" pobb.in',
            f'"{main_skill}" "{ascendancy}" "Path of Building"',
            f'"{base}" endgame PoB',
        ]
    if slot_id == "leveling_pob":
        return [
            f'"{build_name}" leveling PoB',
            f'"{main_skill}" "{ascendancy}" campaign PoB',
            f'"{base}" starter PoB',
        ]
    return [
        f'poe.ninja builds "{main_skill}" "{ascendancy}"',
        f'"{main_skill}" "{ascendancy}" poe.ninja',
        f'"{base}" character snapshot',
    ]


def _priority(slot_id: str, row: dict[str, Any], profile: dict[str, Any], status: str) -> str:
    if status == "ready":
        return "low"
    board_status = row.get("board_status")
    leveling_confidence = profile.get("progression", {}).get("leveling_confidence")
    patch = profile.get("identity", {}).get("patch")
    if slot_id == "leveling_pob" and leveling_confidence != "confirmed":
        return "high"
    if slot_id == "endgame_pob" and board_status in {"confirmed", "near_confirmed"}:
        return "high"
    if slot_id == "guide" and board_status == "confirmed":
        return "medium"
    if slot_id == "poe_ninja" and patch in {"3.28", "3.29"}:
        return "medium"
    return "low"


def _reason(slot_id: str, status: str, profile: dict[str, Any]) -> str:
    identity = profile.get("identity", {})
    build_name = identity.get("build_name") or identity.get("main_skill") or "build"
    if status == "ready":
        return f"{build_name} already has a concrete link for this slot."
    if status == "evidence_without_url":
        return f"{build_name} has source-family evidence, but the original URL is not attached yet."
    if slot_id == "leveling_pob":
        return f"{build_name} needs staged campaign or league-start PoB evidence before campaign certainty is shown."
    if slot_id == "poe_ninja":
        return f"{build_name} needs a character snapshot only as cross-check evidence, not as a primary guide."
    return f"{build_name} needs an original link before this slot can be surfaced."


def build_representative_source_slot_queue() -> dict[str, Any]:
    profiles_payload = _load_json(PROFILES_PATH)
    manual_index = _manual_source_index()
    profiles = profiles_payload.get("profiles", [])

    slots: list[dict[str, Any]] = []
    by_candidate: list[dict[str, Any]] = []
    ready_by_slot = {slot["slot_id"]: 0 for slot in SOURCE_SLOTS}
    missing_by_slot = {slot["slot_id"]: 0 for slot in SOURCE_SLOTS}
    evidence_without_url_by_slot = {slot["slot_id"]: 0 for slot in SOURCE_SLOTS}

    for row in profiles:
        candidate_id = row["candidate_id"]
        profile = row["build_profile"]
        identity = profile.get("identity", {})
        evidence = _compact_evidence((profile.get("evidence") or []) + manual_index.get(candidate_id, []))
        candidate_ready: list[str] = []
        candidate_missing: list[str] = []

        for slot in SOURCE_SLOTS:
            matched = [item for item in evidence if _matches_slot(item, slot)]
            linked = [item for item in matched if item.get("url")]
            if linked:
                status = "ready"
                ready_by_slot[slot["slot_id"]] += 1
                candidate_ready.append(slot["slot_id"])
            elif matched:
                status = "evidence_without_url"
                evidence_without_url_by_slot[slot["slot_id"]] += 1
                candidate_missing.append(slot["slot_id"])
            else:
                status = "missing"
                missing_by_slot[slot["slot_id"]] += 1
                candidate_missing.append(slot["slot_id"])

            priority = _priority(slot["slot_id"], row, profile, status)
            slots.append(
                {
                    "queue_id": f"{candidate_id}:{slot['slot_id']}",
                    "candidate_id": candidate_id,
                    "build_id": profile.get("build_id"),
                    "build_name": identity.get("build_name"),
                    "patch": identity.get("patch"),
                    "class_name": identity.get("class_name"),
                    "ascendancy": identity.get("ascendancy"),
                    "main_skill": identity.get("main_skill"),
                    "leveling_skill": identity.get("leveling_skill"),
                    "board_status": row.get("board_status"),
                    "slot_id": slot["slot_id"],
                    "slot_label": slot["slot_label"],
                    "status": status,
                    "priority": priority,
                    "reason": _reason(slot["slot_id"], status, profile),
                    "matched_evidence": matched[:5],
                    "suggested_queries": [] if status == "ready" else _suggested_queries(identity, slot["slot_id"]),
                }
            )

        high_priority_missing = [
            item["slot_id"]
            for item in slots[-len(SOURCE_SLOTS):]
            if item["status"] != "ready" and item["priority"] == "high"
        ]
        by_candidate.append(
            {
                "candidate_id": candidate_id,
                "build_name": identity.get("build_name"),
                "ready_slot_ids": candidate_ready,
                "missing_slot_ids": candidate_missing,
                "high_priority_missing_slot_ids": high_priority_missing,
            }
        )

    summary = {
        "profile_count": len(profiles),
        "slot_count": len(slots),
        "ready_link_slot_count": sum(1 for item in slots if item["status"] == "ready"),
        "evidence_without_url_slot_count": sum(1 for item in slots if item["status"] == "evidence_without_url"),
        "missing_slot_count": sum(1 for item in slots if item["status"] == "missing"),
        "ready_by_slot": ready_by_slot,
        "evidence_without_url_by_slot": evidence_without_url_by_slot,
        "missing_by_slot": missing_by_slot,
    }

    return {
        "dataset_kind": "poe1_representative_source_slot_queue",
        "schema_version": "1.0",
        "user_visibility": {
            "surface": "internal_only",
            "do_not_render_missing_slots": True,
            "user_facing_rule": "Show only concrete source URLs in player-facing UI.",
        },
        "source_inputs": {
            "representative_profiles": str(PROFILES_PATH.relative_to(ROOT)).replace("\\", "/"),
            "manual_pob_sources": str(MANUAL_POB_SOURCES_PATH.relative_to(ROOT)).replace("\\", "/"),
        },
        "summary": summary,
        "by_candidate": by_candidate,
        "slots": slots,
    }


if __name__ == "__main__":
    data = build_representative_source_slot_queue()
    OUT_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(data["summary"], ensure_ascii=False, indent=2))
