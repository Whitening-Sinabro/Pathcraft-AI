# -*- coding: utf-8 -*-
"""Backend guard for player-facing PoE1 build recommendations.

This guard is deliberately separate from UI filtering and corpus generation.
It is applied at recommendation/load time so stale generated JSON cannot promote
old build families directly to users.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any


PATCH_BASELINE = "3.29.0"

GUARDS: tuple[dict[str, Any], ...] = (
    {
        "guard_id": "post_3_26_hexblast_trigger_cooldown_guard",
        "visibility": "hold",
        "tokens": ("hexblast",),
        "note": (
            "Hexblast Mine cannot be carried forward as a default recommendation "
            "without current-patch specialist PoB/live proof."
        ),
    },
    {
        "guard_id": "patch_3_29_ballista_totem_guard",
        "visibility": "practice_only",
        "tokens": ("ballista",),
        "note": (
            "3.29 increases Ballista Totem less-damage pressure; old Ballista PoBs "
            "are practice-only until refreshed."
        ),
    },
    {
        "guard_id": "patch_3_29_spell_totem_and_totem_scaling_guard",
        "visibility": "practice_only",
        "tokens": ("totem",),
        "note": (
            "3.29 directly changes Spell Totem penalty and multiple totem scaling "
            "passives; old Totem PoBs are practice-only until refreshed."
        ),
    },
    {
        "guard_id": "patch_3_29_mine_support_guard",
        "visibility": "practice_only",
        "tokens": (" mine", "_mine", "mines"),
        "note": (
            "3.29 changes Blastchain Mine, High-Impact Mine, and Charged Mines "
            "cost/damage/throw-speed values; old Mine PoBs are practice-only until refreshed."
        ),
    },
)


def _norm(value: Any) -> str:
    return str(value or "").casefold()


def _row_text(row: dict[str, Any]) -> str:
    profile = row.get("build_profile") or {}
    identity = profile.get("identity") or {}
    return " ".join(
        _norm(value)
        for value in (
            row.get("candidate_id"),
            profile.get("build_id"),
            identity.get("build_name"),
            identity.get("main_skill"),
            identity.get("leveling_skill"),
            identity.get("ascendancy"),
        )
    )


def _match_guard(row: dict[str, Any]) -> dict[str, Any] | None:
    text = f" {_row_text(row)} "
    for guard in GUARDS:
        if any(token in text for token in guard["tokens"]):
            return guard
    return None


def verify_profile_row(row: dict[str, Any]) -> dict[str, Any]:
    verified = copy.deepcopy(row)
    profile = verified.setdefault("build_profile", {})
    confidence = profile.setdefault("confidence", {})
    constraints = profile.setdefault("constraints", {})
    pain_points = constraints.setdefault("pain_points", [])
    guard = _match_guard(verified)

    if guard:
        visibility = guard["visibility"]
        verified["player_facing_default"] = False
        verified["recommendation_visibility"] = visibility
        verified["forward_guard_note"] = guard["note"]
        verified["backend_guard"] = {
            "status": "blocked_from_default",
            "guard_id": guard["guard_id"],
            "visibility": visibility,
            "verified_against_patch": PATCH_BASELINE,
        }
        if guard["guard_id"] not in pain_points:
            pain_points.append(guard["guard_id"])
        if visibility == "hold":
            verified["board_status"] = "hold"
            verified["use_policy"] = "do_not_default"
            confidence["representative_build_status"] = "hold"
        return verified

    player_default = verified.get("player_facing_default")
    if player_default is None:
        player_default = verified.get("board_status") != "hold" and verified.get("use_policy") != "do_not_default"
    verified["player_facing_default"] = bool(player_default)
    verified["recommendation_visibility"] = verified.get("recommendation_visibility") or (
        "default" if verified["player_facing_default"] else "hold"
    )
    verified["backend_guard"] = {
        "status": "passed",
        "guard_id": None,
        "visibility": verified["recommendation_visibility"],
        "verified_against_patch": PATCH_BASELINE,
    }
    return verified


def apply_recommendation_guard_to_corpus(corpus: dict[str, Any]) -> dict[str, Any]:
    guarded = copy.deepcopy(corpus)
    rows = [verify_profile_row(row) for row in guarded.get("profiles", [])]
    guarded["profiles"] = rows
    blocked = [row for row in rows if row.get("player_facing_default") is False]
    guarded["backend_guard_summary"] = {
        "dataset_kind": "poe1_backend_recommendation_guard_summary",
        "verified_against_patch": PATCH_BASELINE,
        "profile_count": len(rows),
        "default_candidate_count": sum(1 for row in rows if row.get("player_facing_default") is not False and row.get("board_status") != "hold"),
        "blocked_from_default_count": len(blocked),
        "blocked_candidate_ids": [row.get("candidate_id") for row in blocked],
        "guard_ids": sorted({
            row.get("backend_guard", {}).get("guard_id")
            for row in blocked
            if row.get("backend_guard", {}).get("guard_id")
        }),
    }
    return guarded


def is_player_facing_default_row(row: dict[str, Any]) -> bool:
    return (
        row.get("board_status") != "hold"
        and row.get("use_policy") != "do_not_default"
        and row.get("player_facing_default") is not False
    )


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("corpus", type=Path)
    args = parser.parse_args()
    guarded = apply_recommendation_guard_to_corpus(json.loads(args.corpus.read_text(encoding="utf-8")))
    print(json.dumps(guarded["backend_guard_summary"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
