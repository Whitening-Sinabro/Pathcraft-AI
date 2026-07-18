# -*- coding: utf-8 -*-
"""Adversarial tests for the POE1 build variant split classifier."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from build_variant_model_v2 import (  # noqa: E402
    SplitRules,
    VariantModelError,
    classify_split,
    load_split_rules,
)


ROOT = Path(__file__).resolve().parents[2]
RULES_PATH = ROOT / "data" / "build_variant_rules_v2.json"


def _base() -> dict:
    return {
        "damage_engine": "attack hit",
        "defense_engine": "life armour",
        "core_unique_gate": "none",
        "tree_shape_class": "axe melee life",
        "play_pattern": "generic mapper",
        "budget_tier": "budget",
        "gear_package_id": "rare_weapon_package_a",
        "aura_package_id": "determination_herald",
        "cluster_package_id": "none",
        "content_specialization": "generic",
    }


def test_load_default_rules_file():
    rules = load_split_rules(RULES_PATH)
    assert rules == SplitRules()


def test_damage_engine_change_forces_sub_archetype_split():
    result = classify_split(_base(), _base() | {"damage_engine": "totem dot"})
    assert result["decision"] == "sub_archetype_split"
    assert "damage_engine" in result["reasons"]


def test_core_unique_gate_change_forces_sub_archetype_split():
    result = classify_split(_base(), _base() | {"core_unique_gate": "replica alberons warpath"})
    assert result["decision"] == "sub_archetype_split"
    assert "core_unique_gate" in result["reasons"]


def test_two_budget_steps_force_variant_split():
    result = classify_split(_base() | {"budget_tier": "budget"}, _base() | {"budget_tier": "high_end"})
    assert result["decision"] == "variant_split"
    assert "budget_tier_distance" in result["reasons"]


def test_package_delta_inside_same_engine_forces_variant_split():
    result = classify_split(
        _base(),
        _base() | {
            "gear_package_id": "rare_weapon_package_b",
            "aura_package_id": "double_purity",
        },
    )
    assert result["decision"] == "variant_split"
    assert "package_delta" in result["reasons"]


def test_small_power_gain_stays_phase_state_only():
    result = classify_split(_base(), _base() | {"budget_tier": "mid"})
    assert result["decision"] == "phase_state_only"


def test_generic_to_delve_specialization_forces_variant_split():
    result = classify_split(_base(), _base() | {"content_specialization": "delve"})
    assert result["decision"] == "variant_split"
    assert "content_specialization" in result["reasons"]


def test_relaxed_rules_can_downgrade_content_split_to_phase_only():
    rules = SplitRules(split_on_content_specialization_change=False)
    result = classify_split(_base(), _base() | {"content_specialization": "delve"}, rules=rules)
    assert result["decision"] == "phase_state_only"


def test_relaxed_rules_can_raise_package_threshold():
    rules = SplitRules(variant_package_delta_threshold=3)
    result = classify_split(
        _base(),
        _base() | {
            "gear_package_id": "rare_weapon_package_b",
            "aura_package_id": "double_purity",
        },
        rules=rules,
    )
    assert result["decision"] == "phase_state_only"


def test_invalid_rules_file_shape_raises():
    path = Path(r"D:\Pathcraft-AI\_debug\bad_rules_variant_v2.json")
    path.write_text(json.dumps({"rules": []}), encoding="utf-8")
    with pytest.raises(VariantModelError, match="must contain an object"):
        load_split_rules(path)


def test_missing_required_field_raises():
    with pytest.raises(VariantModelError, match="budget_tier"):
        classify_split({"damage_engine": "attack"}, _base())


def test_empty_engine_string_raises():
    broken = _base() | {"damage_engine": "   "}
    with pytest.raises(VariantModelError, match="missing normalized fields"):
        classify_split(_base(), broken)

