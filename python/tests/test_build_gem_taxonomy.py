# -*- coding: utf-8 -*-
"""Generated POE1 gem taxonomy tests."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from build_gem_taxonomy import build_taxonomy  # noqa: E402


ROOT = Path(__file__).resolve().parents[2]
TAXONOMY_PATH = ROOT / "data" / "poe1_gem_taxonomy.latest.json"


def _load_taxonomy() -> dict:
    return json.loads(TAXONOMY_PATH.read_text(encoding="utf-8"))


def test_build_gem_taxonomy_core_counts():
    taxonomy = build_taxonomy()

    assert taxonomy["dataset_kind"] == "poe1_gem_taxonomy"
    assert taxonomy["summary"]["entry_count"] > 1000
    assert taxonomy["summary"]["gem_kind_counts"]["active_gem"] > 300
    assert taxonomy["summary"]["gem_kind_counts"]["support_gem"] > 200
    assert taxonomy["summary"]["gem_kind_counts"]["active_skill_only"] > 100


def test_generated_taxonomy_splits_active_support_alias_and_triggered_skills():
    entries = _load_taxonomy()["entries"]

    assert entries["Herald of Thunder"]["gem_kind"] == "active_gem"
    assert entries["Herald of Thunder"]["socketable"] is True
    assert entries["Herald of Thunder"]["offense_class"] == "offensive_active"

    assert entries["Added Lightning Damage Support"]["gem_kind"] == "support_gem"
    assert entries["Added Lightning Damage Support"]["socketability"] == "socketable_support_gem_item"
    assert entries["Added Lightning Damage"]["gem_kind"] == "support_alias"
    assert entries["Added Lightning Damage"]["socketable"] is False

    assert entries["Blight of Contagion"]["gem_kind"] == "active_transfigured_or_valid_active"
    assert entries["Blight of Contagion"]["socketable"] is True
    assert entries["Blight of Contagion"]["damage_flags"]["dot"] is True

    assert entries["Molten Burst"]["gem_kind"] == "active_skill_only"
    assert entries["Molten Burst"]["socketable"] is False
    assert entries["Molten Burst"]["damage_flags"]["attack"] is True

    assert entries["Raise Spiders"]["gem_kind"] == "active_skill_only"
    assert entries["Raise Spiders"]["socketable"] is False
    assert entries["Raise Spiders"]["damage_flags"]["minion"] is True

    assert entries["Summon Phantasm"]["gem_kind"] == "active_skill_only_and_support_alias"
    assert entries["Summon Phantasm"]["support_alias_of"] == "Summon Phantasm Support"
    assert entries["Summon Phantasm"]["socketable"] is False
    assert entries["Summon Phantasm"]["damage_flags"]["minion"] is True

    assert entries["Barrage"]["gem_kind"] == "active_gem"
    assert entries["Barrage"]["support_alias_of"] is None
    assert entries["Barrage Support"]["gem_kind"] == "support_gem"
