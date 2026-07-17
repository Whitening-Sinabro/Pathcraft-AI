# -*- coding: utf-8 -*-
"""Tests for the external-guide-source validator and CWS card projector."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cws_guide_loader import (  # noqa: E402
    GuideSourceError,
    validate_external_guide_source,
    load_cws_card,
)


def _load(name: str) -> dict:
    path = ROOT / "data" / "guide_sources" / name
    return json.loads(path.read_text(encoding="utf-8-sig"))


def test_validator_accepts_cws_guide():
    guide = _load("poe1_cws_chieftain_emiracles_v1.json")
    validate_external_guide_source(guide)  # must not raise


def test_validator_accepts_zeeboub_guide():
    # Proves the validator is schema-shaped, not CWS-shaped.
    guide = _load("poe1_brand_guide_zeeboub_v2.json")
    validate_external_guide_source(guide)  # must not raise


def test_validator_rejects_orphan_pob_link():
    guide = _load("poe1_cws_chieftain_emiracles_v1.json")
    guide["pob_links"].append({"url": "https://pobb.in/ORPHAN", "label": "no role"})
    with pytest.raises(GuideSourceError, match="orphan"):
        validate_external_guide_source(guide)


def test_validator_rejects_dangling_prereq():
    guide = _load("poe1_cws_chieftain_emiracles_v1.json")
    guide["upgrade_nodes"][0]["prereq"] = ["does_not_exist"]
    with pytest.raises(GuideSourceError, match="prereq"):
        validate_external_guide_source(guide)


def test_validator_rejects_dangling_node_phase():
    guide = _load("poe1_cws_chieftain_emiracles_v1.json")
    guide["upgrade_nodes"][0]["phase"] = "no_such_phase"
    with pytest.raises(GuideSourceError, match="phase"):
        validate_external_guide_source(guide)


def test_validator_rejects_patch_locked_key():
    guide = _load("poe1_cws_chieftain_emiracles_v1.json")
    guide["mirage_3_28_notes"] = ["patch baked into a key name"]
    with pytest.raises(GuideSourceError, match="patch-locked"):
        validate_external_guide_source(guide)
