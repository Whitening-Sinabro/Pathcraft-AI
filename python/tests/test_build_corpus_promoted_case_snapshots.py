# -*- coding: utf-8 -*-
"""Regression checks for promoted case snapshot extraction."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from build_corpus_promoted_case_snapshots import (  # noqa: E402
    _skill_snapshot,
    _tree_snapshot,
    clean_notes,
    extract_beginner_failure_findings,
)


def test_clean_notes_removes_pob_colour_codes():
    assert clean_notes("^xE05030--Why?--^7\nText") == "--Why?--\nText"


def test_extract_beginner_failure_findings_from_faq_sections():
    notes = """--Why does my damage feel low?--
    Make sure you have a spectre and enough corpse level.

    --I dont have enough attributes to level my gems--
    Take +30 attribute nodes temporarily.

    --This build uses too many buttons, how can I automate some?--
    Use a trigger weapon later.
    """

    findings = extract_beginner_failure_findings(notes)
    tags = {row["risk_tag"] for row in findings}

    assert len(findings) == 3
    assert "low_damage_due_to_corpse_or_spectre_setup" in tags
    assert "attribute_requirements_not_met" in tags
    assert "button_pressure_trigger_weapon_gate" in tags


def test_skill_snapshot_selects_enabled_main_skill():
    snapshot = _skill_snapshot(
        {
            "id": "2",
            "title": "DD lategame",
            "skills": [
                {
                    "label": "6L DD",
                    "enabled": "true",
                    "main_active_skill": "1",
                    "gems": [
                        {"name_spec": "Detonate Dead of Chain Reaction"},
                        {"name_spec": "Fire Penetration"},
                    ],
                }
            ],
        },
        "2",
    )

    assert snapshot["state_id"] == "dd_lategame"
    assert snapshot["is_active_final"] is True
    assert snapshot["main_skill"] == "Detonate Dead of Chain Reaction"
    assert snapshot["skill_groups"][0]["link_count"] == 2


def test_tree_snapshot_tracks_url_and_jewel_socket_count():
    snapshot = _tree_snapshot(
        {
            "id": "1",
            "title": "lvl 70 dd respec",
            "tree_version": "3_24",
            "url": "https://www.pathofexile.com/passive-skill-tree/AAAA",
            "sockets": [{"node_id": "1"}, {"node_id": "2"}],
        },
        "1",
    )

    assert snapshot["is_active_tree"] is True
    assert snapshot["url_present"] is True
    assert snapshot["jewel_socket_count"] == 2
