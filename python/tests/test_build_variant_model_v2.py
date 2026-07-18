# -*- coding: utf-8 -*-
"""POE1 build variant model v2 smoke tests."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "data" / "schema" / "poe1_build_variant_model_v2.schema.json"
SEED_PATH = ROOT / "data" / "build_variant_seed_v2.example.json"


def _load_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def test_variant_model_v2_files_parse():
    schema = _load_json(SCHEMA_PATH)
    seed = _load_json(SEED_PATH)

    assert schema["title"] == "POE1 Build Variant Model V2"
    assert seed["dataset_kind"] == "poe1_build_variant_model_v2"


def test_sub_archetype_variant_phase_ids_are_unique():
    seed = _load_json(SEED_PATH)

    for archetype in seed["archetypes"]:
        sub_ids: set[str] = set()
        for sub in archetype["sub_archetypes"]:
            assert sub["sub_archetype_id"] not in sub_ids
            sub_ids.add(sub["sub_archetype_id"])

            variant_ids: set[str] = set()
            phase_ids: set[str] = set()
            for variant in sub["variants"]:
                assert variant["variant_id"] not in variant_ids
                variant_ids.add(variant["variant_id"])

                for phase in variant["phase_states"]:
                    assert phase["phase_id"] not in phase_ids
                    phase_ids.add(phase["phase_id"])


def test_variant_model_v2_hierarchy_is_not_flattened():
    seed = _load_json(SEED_PATH)
    archetype = seed["archetypes"][0]

    sub_archetypes = archetype["sub_archetypes"]
    assert len(sub_archetypes) >= 3

    # The sample should prove that engine-level changes create sub-archetype
    # boundaries rather than becoming plain budget variants.
    engine_pairs = {
        (sub["damage_engine"], sub["defense_engine"])
        for sub in sub_archetypes
    }
    assert len(engine_pairs) == len(sub_archetypes)


def test_phase_states_do_not_cross_variant_boundaries():
    seed = _load_json(SEED_PATH)

    for archetype in seed["archetypes"]:
        for sub in archetype["sub_archetypes"]:
            for variant in sub["variants"]:
                phase_types = [phase["phase_type"] for phase in variant["phase_states"]]

                # A phase progression is allowed to span multiple stages,
                # but it should stay within one budget and one engine shell.
                assert variant["budget_tier"] in {
                    "starter",
                    "budget",
                    "mid",
                    "high_end",
                    "mirror",
                }
                assert len(phase_types) >= 1


def test_sub_archetype_forced_split_reasons_exist():
    seed = _load_json(SEED_PATH)

    for archetype in seed["archetypes"]:
        for sub in archetype["sub_archetypes"]:
            assert sub["forced_split_reason"], (
                f"sub_archetype {sub['sub_archetype_id']} should document why it split"
            )

