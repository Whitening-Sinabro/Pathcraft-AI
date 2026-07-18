# -*- coding: utf-8 -*-
"""Build the collection backlog for the POE1 build corpus target."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
TARGET_PATH = ROOT / "data" / "build_corpus_collection_targets_v1.json"
REAL_CASES_PATH = ROOT / "data" / "build_variant_real_cases_v1.json"
LATEST_OUTPUT_PATH = ROOT / "data" / "build_corpus_collection_backlog.latest.json"


LANE_RULES: list[tuple[str, tuple[str, ...]]] = [
    (
        "minion_trigger_autobomber_special",
        (
            "autobomber",
            "herald_of_thunder",
            "cast_on_critical",
            "cast_on_crit",
            "coc",
            "wardloop",
            "trigger",
            "minion",
            "summon",
            "spectre",
            "skeleton",
            "srs",
            "dominating_blow",
            "holy_relic",
            "raise_spectre",
        ),
    ),
    (
        "trap_mine_totem",
        (
            "trap",
            "mine",
            "miner",
            "totem",
            "ballista",
            "shockwave_totem",
            "hexblast_mine",
            "pyroclast_mine",
            "siege_ballista",
            "explosive_arrow_ballista",
        ),
    ),
    (
        "melee_strike_slam",
        (
            "melee",
            "strike",
            "slam",
            "boneshatter",
            "lacerate",
            "earthquake",
            "ground_slam",
            "lightning_strike",
            "heavy_strike",
            "static_strike",
        ),
    ),
    (
        "dot_ailment_dot",
        (
            " dot",
            "_dot",
            "damage over time",
            "ignite",
            "poison",
            "bleed",
            "toxic_rain",
            "righteous_fire",
            "corrupting_fever",
            "blight",
            "contagion",
            "caustic",
        ),
    ),
    (
        "bow_projectile_attack_mapper",
        (
            "bow",
            "projectile attack",
            "wand projectile",
            "wander",
            "kinetic",
            "lightning_arrow",
            "ice_shot",
            "deadeye",
        ),
    ),
    (
        "spell_hit_brand_selfcast",
        (
            "spell",
            "brand",
            "caster",
            "archmage",
            "penance_brand",
            "ice_nova",
            "ball_lightning",
            "spark",
            "shock_nova",
            "cold_snap",
            "detonate_dead",
        ),
    ),
]


def _load_json(path: Path) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def _normalize_text(value: object) -> str:
    return str(value or "").strip().lower().replace("-", "_")


def _case_search_text(case: dict[str, Any]) -> str:
    parts: list[str] = [
        _normalize_text(case.get("case_id")),
        _normalize_text(case.get("archetype_id")),
        _normalize_text(case.get("source_status")),
        _normalize_text(case.get("confidence")),
    ]
    for state in case.get("states", []) or []:
        for key in (
            "state_id",
            "damage_engine",
            "defense_engine",
            "core_unique_gate",
            "tree_shape_class",
            "play_pattern",
            "gear_package_id",
            "aura_package_id",
            "cluster_package_id",
            "content_specialization",
        ):
            parts.append(_normalize_text(state.get(key)))
    return " ".join(parts)


def infer_lane(case: dict[str, Any]) -> str:
    """Infer the broad collection lane from normalized case text."""
    text = _case_search_text(case)
    for lane_id, needles in LANE_RULES:
        if any(needle in text for needle in needles):
            return lane_id
    return "unclassified"


def _has_transition_signal(case: dict[str, Any]) -> bool:
    for decision in case.get("expected_pairwise_decisions", []) or []:
        if decision.get("decision") in {"sub_archetype_split", "variant_split"}:
            return True
    return False


def _has_failure_edge_signal(case: dict[str, Any]) -> bool:
    tags = {
        _normalize_text(value)
        for key in ("case_role", "role", "tags", "mechanic_tags")
        for value in ([case.get(key)] if not isinstance(case.get(key), list) else case.get(key))
        if value
    }
    return bool(tags.intersection({"failure", "edge", "bricked", "blocked", "negative_case"}))


def _empty_patch_summary(patch: str, lane_ids: list[str], target: dict[str, Any]) -> dict[str, Any]:
    return {
        "patch": patch,
        "current_build_cases": 0,
        "current_state_snapshots": 0,
        "complete_case_count": 0,
        "transition_signal_count": 0,
        "failure_edge_signal_count": 0,
        "source_status_counts": {},
        "lane_counts": {lane_id: 0 for lane_id in lane_ids},
        "target_build_cases": target["canonical_build_cases"],
        "target_state_snapshots": target["minimum_state_snapshots_per_patch"],
        "case_deficit": target["canonical_build_cases"],
        "snapshot_deficit": target["minimum_state_snapshots_per_patch"],
    }


def _make_slot_id(patch: str, slot_type: str, lane_id: str | None, index: int) -> str:
    lane_part = lane_id or "general"
    return f"{patch}_{slot_type}_{lane_part}_{index:02d}"


def _build_patch_slots(
    patch: str,
    summary: dict[str, Any],
    lane_targets: dict[str, int],
    composition: dict[str, int],
) -> list[dict[str, Any]]:
    remaining = max(0, summary["case_deficit"])
    slots: list[dict[str, Any]] = []

    lane_rows = summary["lane_coverage"]
    lane_slot_index = 1
    for lane in lane_rows:
        if remaining <= 0:
            break
        lane_id = lane["lane_id"]
        for _ in range(min(lane["stable_shell_deficit"], remaining)):
            slots.append(
                {
                    "slot_id": _make_slot_id(patch, "stable_shell_backfill", lane_id, lane_slot_index),
                    "slot_type": "stable_shell_backfill",
                    "lane_id": lane_id,
                    "reason": "lane_has_fewer_than_two_stable_shell_candidates",
                    "status": "needs_source_hunt",
                }
            )
            lane_slot_index += 1
            remaining -= 1
            if remaining <= 0:
                break

    failure_deficit = max(0, composition["failure_edge_cases"] - summary["failure_edge_signal_count"])
    transition_deficit = max(0, composition["transition_cases"] - summary["transition_signal_count"])

    for slot_type, deficit, reason in (
        ("failure_edge_case_backfill", failure_deficit, "patch_needs_negative_or_bricked_build_examples"),
        ("transition_case_backfill", transition_deficit, "patch_needs_progression_or_respec_examples"),
    ):
        for index in range(1, min(deficit, remaining) + 1):
            slots.append(
                {
                    "slot_id": _make_slot_id(patch, slot_type, None, index),
                    "slot_type": slot_type,
                    "lane_id": None,
                    "reason": reason,
                    "status": "needs_source_hunt",
                }
            )
        remaining -= min(deficit, remaining)

    for index in range(1, remaining + 1):
        slots.append(
            {
                "slot_id": _make_slot_id(patch, "general_case_backfill", None, index),
                "slot_type": "general_case_backfill",
                "lane_id": None,
                "reason": "patch_total_case_target_not_met",
                "status": "needs_source_hunt",
            }
        )

    return slots


def build_collection_backlog() -> dict[str, Any]:
    targets = _load_json(TARGET_PATH)
    real_cases = _load_json(REAL_CASES_PATH)

    per_patch_target = targets["per_patch_target"]
    composition = per_patch_target["composition"]
    lane_ids = [lane["lane_id"] for lane in targets["archetype_lanes"]]
    lane_targets = {lane["lane_id"]: lane["stable_shells_per_patch"] for lane in targets["archetype_lanes"]}
    patches = (
        targets["patch_range"]["confirmed_collection_patches"]
        + targets["patch_range"]["watchlist_patches"]
    )
    watchlist = set(targets["patch_range"]["watchlist_patches"])

    by_patch = {
        patch: _empty_patch_summary(patch, lane_ids, per_patch_target)
        for patch in patches
    }

    case_lanes: list[dict[str, str]] = []
    for case in real_cases.get("cases", []) or []:
        patch = case.get("patch")
        if patch not in by_patch:
            continue
        summary = by_patch[patch]
        lane_id = infer_lane(case)
        state_count = len(case.get("states", []) or [])

        summary["current_build_cases"] += 1
        summary["current_state_snapshots"] += state_count
        summary["complete_case_count"] += int(state_count >= 2)
        summary["transition_signal_count"] += int(_has_transition_signal(case))
        summary["failure_edge_signal_count"] += int(_has_failure_edge_signal(case))
        if lane_id in summary["lane_counts"]:
            summary["lane_counts"][lane_id] += 1
        else:
            summary["lane_counts"][lane_id] = summary["lane_counts"].get(lane_id, 0) + 1

        status = case.get("source_status", "unknown")
        summary["source_status_counts"][status] = summary["source_status_counts"].get(status, 0) + 1
        case_lanes.append(
            {
                "patch": patch,
                "case_id": case["case_id"],
                "archetype_id": case["archetype_id"],
                "lane_id": lane_id,
            }
        )

    for patch, summary in by_patch.items():
        summary["case_deficit"] = max(
            0,
            summary["target_build_cases"] - summary["current_build_cases"],
        )
        summary["snapshot_deficit"] = max(
            0,
            summary["target_state_snapshots"] - summary["current_state_snapshots"],
        )
        summary["patch_target_status"] = "watchlist" if patch in watchlist else "confirmed_collection"
        summary["lane_coverage"] = [
            {
                "lane_id": lane_id,
                "current_cases": summary["lane_counts"].get(lane_id, 0),
                "stable_shell_target": lane_targets[lane_id],
                "stable_shell_deficit": max(
                    0,
                    lane_targets[lane_id] - summary["lane_counts"].get(lane_id, 0),
                ),
            }
            for lane_id in lane_ids
        ]
        summary["planned_slots"] = _build_patch_slots(
            patch,
            summary,
            lane_targets,
            composition,
        )

    patch_rows = [by_patch[patch] for patch in patches]
    confirmed_rows = [
        row for row in patch_rows if row["patch_target_status"] == "confirmed_collection"
    ]
    totals = {
        "confirmed_3_22_to_3_28": {
            "current_build_cases": sum(row["current_build_cases"] for row in confirmed_rows),
            "current_state_snapshots": sum(row["current_state_snapshots"] for row in confirmed_rows),
            "target_build_cases": sum(row["target_build_cases"] for row in confirmed_rows),
            "target_state_snapshots": sum(row["target_state_snapshots"] for row in confirmed_rows),
            "case_deficit": sum(row["case_deficit"] for row in confirmed_rows),
            "snapshot_deficit": sum(row["snapshot_deficit"] for row in confirmed_rows),
        },
        "operational_including_watchlist": {
            "current_build_cases": sum(row["current_build_cases"] for row in patch_rows),
            "current_state_snapshots": sum(row["current_state_snapshots"] for row in patch_rows),
            "target_build_cases": sum(row["target_build_cases"] for row in patch_rows),
            "target_state_snapshots": sum(row["target_state_snapshots"] for row in patch_rows),
            "case_deficit": sum(row["case_deficit"] for row in patch_rows),
            "snapshot_deficit": sum(row["snapshot_deficit"] for row in patch_rows),
        },
    }

    priority_patches = sorted(
        (
            {
                "patch": row["patch"],
                "patch_target_status": row["patch_target_status"],
                "case_deficit": row["case_deficit"],
                "snapshot_deficit": row["snapshot_deficit"],
                "lane_deficit_total": sum(
                    lane["stable_shell_deficit"] for lane in row["lane_coverage"]
                ),
                "planned_slot_count": len(row["planned_slots"]),
            }
            for row in patch_rows
        ),
        key=lambda item: (
            item["patch_target_status"] != "confirmed_collection",
            -item["case_deficit"],
            -item["lane_deficit_total"],
            item["patch"],
        ),
    )

    return {
        "schema_version": "1.0",
        "dataset_kind": "poe1_build_corpus_collection_backlog",
        "target_dataset": TARGET_PATH.relative_to(ROOT).as_posix(),
        "real_case_dataset": REAL_CASES_PATH.relative_to(ROOT).as_posix(),
        "per_patch_target": per_patch_target,
        "totals": totals,
        "priority_patches": priority_patches,
        "by_patch": patch_rows,
        "case_lanes": sorted(case_lanes, key=lambda item: (item["patch"], item["case_id"])),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write-latest",
        action="store_true",
        help="Write data/build_corpus_collection_backlog.latest.json.",
    )
    args = parser.parse_args()

    result = build_collection_backlog()
    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.write_latest:
        LATEST_OUTPUT_PATH.write_text(text + "\n", encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
