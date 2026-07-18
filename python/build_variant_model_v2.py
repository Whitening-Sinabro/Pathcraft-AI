# -*- coding: utf-8 -*-
"""Executable split logic for POE1 build variant model v2."""

from __future__ import annotations

import json
from dataclasses import dataclass, fields
from pathlib import Path


VALID_BUDGET_TIERS = ("starter", "budget", "mid", "high_end", "mirror")
_BUDGET_ORDER = {name: idx for idx, name in enumerate(VALID_BUDGET_TIERS)}
DEFAULT_RULES_PATH = Path(__file__).resolve().parent.parent / "data" / "build_variant_rules_v2.json"


class VariantModelError(ValueError):
    """Raised when a record cannot be classified safely."""


@dataclass(frozen=True)
class SplitRules:
    """Tunable rule profile for split classification.

    Strict mode is the default. Individual checks can be relaxed or disabled
    once real labeled data shows a rule is too noisy.
    """

    split_on_damage_engine_change: bool = True
    split_on_defense_engine_change: bool = True
    split_on_core_unique_gate_change: bool = True
    split_on_tree_shape_change: bool = True
    split_on_play_pattern_change: bool = True
    split_on_content_specialization_change: bool = True
    variant_budget_distance_threshold: int = 2
    variant_package_delta_threshold: int = 2

    @classmethod
    def from_dict(cls, data: dict) -> "SplitRules":
        valid_names = {f.name for f in fields(cls)}
        unknown = sorted(set(data) - valid_names)
        if unknown:
            raise VariantModelError(f"unknown split rule fields: {', '.join(unknown)}")

        kwargs = {}
        for f in fields(cls):
            value = data.get(f.name, getattr(cls, f.name))
            kwargs[f.name] = value

        for name in (
            "variant_budget_distance_threshold",
            "variant_package_delta_threshold",
        ):
            value = kwargs[name]
            if not isinstance(value, int) or value < 1:
                raise VariantModelError(f"{name} must be an integer >= 1")

        return cls(**kwargs)


STRICT_RULES = SplitRules()


@dataclass(frozen=True)
class VariantFingerprint:
    damage_engine: str
    defense_engine: str
    core_unique_gate: str
    tree_shape_class: str
    play_pattern: str
    budget_tier: str
    gear_package_id: str
    aura_package_id: str
    cluster_package_id: str
    content_specialization: str


def load_split_rules(path: Path | None = None) -> SplitRules:
    cfg_path = path or DEFAULT_RULES_PATH
    with open(cfg_path, "r", encoding="utf-8-sig") as f:
        payload = json.load(f)
    if not isinstance(payload, dict):
        raise VariantModelError("split rules file must be a JSON object")
    rules = payload.get("rules", payload)
    if not isinstance(rules, dict):
        raise VariantModelError("split rules payload must contain an object in 'rules'")
    return SplitRules.from_dict(rules)


def _norm(value: str | None) -> str:
    return (value or "").strip().lower()


def normalize_fingerprint(data: dict) -> VariantFingerprint:
    try:
        budget_tier = _norm(data["budget_tier"])
    except KeyError as exc:
        raise VariantModelError("missing required field: budget_tier") from exc

    if budget_tier not in _BUDGET_ORDER:
        raise VariantModelError(f"invalid budget_tier: {budget_tier}")

    required = (
        "damage_engine",
        "defense_engine",
        "core_unique_gate",
        "tree_shape_class",
        "play_pattern",
        "gear_package_id",
        "aura_package_id",
        "cluster_package_id",
        "content_specialization",
    )
    missing = [field for field in required if not _norm(data.get(field))]
    if missing:
        raise VariantModelError(f"missing normalized fields: {', '.join(missing)}")

    return VariantFingerprint(
        damage_engine=_norm(data["damage_engine"]),
        defense_engine=_norm(data["defense_engine"]),
        core_unique_gate=_norm(data["core_unique_gate"]),
        tree_shape_class=_norm(data["tree_shape_class"]),
        play_pattern=_norm(data["play_pattern"]),
        budget_tier=budget_tier,
        gear_package_id=_norm(data["gear_package_id"]),
        aura_package_id=_norm(data["aura_package_id"]),
        cluster_package_id=_norm(data["cluster_package_id"]),
        content_specialization=_norm(data["content_specialization"]),
    )


def _budget_distance(left: str, right: str) -> int:
    return abs(_BUDGET_ORDER[left] - _BUDGET_ORDER[right])


def classify_split(left: dict, right: dict, rules: SplitRules = STRICT_RULES) -> dict:
    """Return split decision between two build states.

    Decisions:
    - sub_archetype_split
    - variant_split
    - phase_state_only
    """

    a = normalize_fingerprint(left)
    b = normalize_fingerprint(right)

    sub_reasons: list[str] = []
    if rules.split_on_damage_engine_change and a.damage_engine != b.damage_engine:
        sub_reasons.append("damage_engine")
    if rules.split_on_defense_engine_change and a.defense_engine != b.defense_engine:
        sub_reasons.append("defense_engine")
    if rules.split_on_core_unique_gate_change and a.core_unique_gate != b.core_unique_gate:
        sub_reasons.append("core_unique_gate")
    if rules.split_on_tree_shape_change and a.tree_shape_class != b.tree_shape_class:
        sub_reasons.append("tree_shape_class")
    if rules.split_on_play_pattern_change and a.play_pattern != b.play_pattern:
        sub_reasons.append("play_pattern")

    budget_distance = _budget_distance(a.budget_tier, b.budget_tier)

    if sub_reasons:
        return {
            "decision": "sub_archetype_split",
            "reasons": sub_reasons,
            "budget_distance": budget_distance,
        }

    variant_reasons: list[str] = []
    if budget_distance >= rules.variant_budget_distance_threshold:
        variant_reasons.append("budget_tier_distance")

    gear_delta = sum(
        1
        for left_value, right_value in (
            (a.gear_package_id, b.gear_package_id),
            (a.aura_package_id, b.aura_package_id),
            (a.cluster_package_id, b.cluster_package_id),
        )
        if left_value != right_value
    )
    if gear_delta >= rules.variant_package_delta_threshold:
        variant_reasons.append("package_delta")

    if rules.split_on_content_specialization_change and a.content_specialization != b.content_specialization:
        if "generic" in {a.content_specialization, b.content_specialization}:
            variant_reasons.append("content_specialization")

    if variant_reasons:
        return {
            "decision": "variant_split",
            "reasons": variant_reasons,
            "budget_distance": budget_distance,
        }

    return {
        "decision": "phase_state_only",
        "reasons": [],
        "budget_distance": budget_distance,
    }
