# -*- coding: utf-8 -*-
"""Regression checks for direct PoB promotion validation."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from build_corpus_promote_ready_pobs import (  # noqa: E402
    build_skill_text,
    pob_url_slug,
    safe_slug,
    skill_terms,
    summarize_parsed_build,
    validate_candidate_against_build,
)


def _candidate(**overrides):
    base = {
        "candidate_id": "3.24_detonate_dead_necromancer",
        "display_name": "Detonate Dead Necromancer",
        "main_skill": "Detonate Dead",
        "class_name": "Witch",
        "ascendancy": "Necromancer",
    }
    base.update(overrides)
    return base


def _build_data(**meta_overrides):
    meta = {
        "build_name": "Witch Necromancer Lvl 99",
        "class": "Witch",
        "ascendancy": "Necromancer",
        "version": "3_24",
        "pob_link": "https://pobb.in/example",
    }
    meta.update(meta_overrides)
    return {
        "meta": meta,
        "build_notes": "FAQ: Detonate Dead damage scales with corpse level.",
        "stats": {
            "dps": 1000,
            "life": 5000,
            "energy_shield": 1000,
            "ehp": 6000,
            "resistances": {"fire": 75, "cold": 75, "lightning": 75, "chaos": 0},
        },
        "pob_raw": {"summary": {"skill_set_count": 2, "tree_spec_count": 3}},
        "progression_stages": [
            {
                "gem_setups": {
                    "6L DD": {
                        "links": "Detonate Dead of Chain Reaction - Fire Penetration",
                    }
                },
                "alternate_gem_sets": {
                    "Leveling": {
                        "Rolling Magma": {
                            "links": "Rolling Magma - Combustion",
                        }
                    }
                },
            }
        ],
        "build_instance": {"readiness": {"status": "inputs_only"}},
    }


def test_safe_slug_and_pob_url_slug_are_filesystem_safe():
    assert safe_slug("3.24 DD / Necro!") == "3_24_DD_Necro"
    assert pob_url_slug("https://pobb.in/qxb7JEG1jSS-") == "qxb7JEG1jSS-"


def test_skill_terms_remove_generic_support_words():
    assert skill_terms("Detonate Dead of Chain Reaction") == ["detonate", "dead", "chain", "reaction"]
    assert skill_terms("Self-Cast Spell Specialist") == ["self", "cast", "spell"]


def test_build_skill_text_includes_active_alternate_and_notes():
    text = build_skill_text(_build_data())

    assert "detonate dead" in text
    assert "rolling magma" in text
    assert "corpse level" in text


def test_validate_candidate_accepts_matching_class_ascendancy_and_skill():
    validation = validate_candidate_against_build(_candidate(), _build_data())

    assert validation["accepted"] is True
    assert validation["blockers"] == []
    assert "detonate" in validation["matched_skill_terms"]


def test_validate_candidate_rejects_ascendancy_mismatch_even_if_skill_matches():
    validation = validate_candidate_against_build(
        _candidate(ascendancy="Elementalist"),
        _build_data(),
    )

    assert validation["accepted"] is False
    assert "ascendancy_mismatch" in validation["blockers"]
    assert validation["skill_match"] is True


def test_summarize_parsed_build_keeps_compact_buildinstance_inputs():
    summary = summarize_parsed_build(_build_data())

    assert summary["identity"]["ascendancy"] == "Necromancer"
    assert summary["stats"]["life"] == 5000
    assert summary["pob_raw_summary"]["tree_spec_count"] == 3
    assert summary["active_gem_groups"] == ["6L DD"]
    assert summary["alternate_gem_sets"] == ["Leveling"]
