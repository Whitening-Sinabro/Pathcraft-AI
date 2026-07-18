# -*- coding: utf-8 -*-
"""Regression tests for the recommendation-time backend guard."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from recommendation_backend_guard import (  # noqa: E402
    apply_recommendation_guard_to_corpus,
    is_player_facing_default_row,
)


def _row(candidate_id: str, main_skill: str) -> dict:
    return {
        "candidate_id": candidate_id,
        "board_status": "confirmed",
        "use_policy": "default",
        "build_profile": {
            "build_id": candidate_id,
            "identity": {
                "build_name": main_skill,
                "main_skill": main_skill,
                "class_name": "Shadow",
                "ascendancy": "Trickster",
            },
            "confidence": {
                "representative_build_status": "confirmed",
            },
            "constraints": {
                "pain_points": [],
            },
        },
    }


def test_backend_guard_blocks_stale_patch_sensitive_families_from_default():
    corpus = {
        "profiles": [
            _row("hexblast_case", "Hexblast Mine"),
            _row("exsanguinate_case", "Exsanguinate Mine"),
            _row("shockwave_case", "Shockwave Totem"),
            _row("ballista_case", "Siege Ballista"),
            _row("safe_case", "Lightning Arrow"),
        ],
    }

    guarded = apply_recommendation_guard_to_corpus(corpus)
    rows = {row["candidate_id"]: row for row in guarded["profiles"]}

    assert rows["hexblast_case"]["player_facing_default"] is False
    assert rows["hexblast_case"]["recommendation_visibility"] == "hold"
    assert rows["hexblast_case"]["board_status"] == "hold"
    assert rows["hexblast_case"]["use_policy"] == "do_not_default"
    assert rows["hexblast_case"]["backend_guard"]["guard_id"] == "post_3_26_hexblast_trigger_cooldown_guard"
    assert rows["hexblast_case"]["build_profile"]["confidence"]["representative_build_status"] == "hold"

    for candidate_id in ("exsanguinate_case", "shockwave_case", "ballista_case"):
        assert rows[candidate_id]["player_facing_default"] is False
        assert rows[candidate_id]["recommendation_visibility"] == "practice_only"
        assert rows[candidate_id]["backend_guard"]["status"] == "blocked_from_default"
        assert not is_player_facing_default_row(rows[candidate_id])

    assert rows["safe_case"]["player_facing_default"] is True
    assert rows["safe_case"]["backend_guard"]["status"] == "passed"
    assert is_player_facing_default_row(rows["safe_case"])

    summary = guarded["backend_guard_summary"]
    assert summary["profile_count"] == 5
    assert summary["default_candidate_count"] == 1
    assert summary["blocked_from_default_count"] == 4
    assert set(summary["blocked_candidate_ids"]) == {
        "hexblast_case",
        "exsanguinate_case",
        "shockwave_case",
        "ballista_case",
    }
