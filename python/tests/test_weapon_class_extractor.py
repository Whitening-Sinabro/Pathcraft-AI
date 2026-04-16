"""Unit tests for weapon_class_extractor.

Fixtures mirror the shape produced by pob_parser so the extractor is tested
against the real build_data schema:
  - `progression_stages[*].gear_recommendation[slot_name] = {"base_type": ..., ...}`
  - `progression_stages[*].gem_setups[setup_name] = {"links": "A - B - C"}`

The map dicts passed in are minimal slices of the real JSON files — we don't
load the whole thing to keep tests fast and independent of regeneration.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Make the project's `python/` directory importable without a package shim.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from weapon_class_extractor import extract_build_weapon_classes  # noqa: E402


# Minimal slice of data/weapon_base_to_class.json covering fixture bases
_BASE_MAP = {
    "Reaver Axe": "One Hand Axes",
    "Siege Axe": "One Hand Axes",
    "Abyssal Axe": "Two Hand Axes",
    "Brass Maul": "Two Hand Maces",
    "Driftwood Maul": "Two Hand Maces",
    "Jewelled Foil": "Thrusting One Hand Swords",
    "Opal Wand": "Wands",
    "Eternal Sword": "Two Hand Swords",
    "Corsair Sword": "One Hand Swords",
}

# Minimal slice of data/gem_weapon_requirements.json#gem_weapon_classes
_GEM_MAP = {
    "Sunder": ["One Hand Axes", "One Hand Maces", "Two Hand Axes", "Two Hand Maces"],
    "Boneshatter": ["One Hand Axes", "One Hand Maces", "Two Hand Axes", "Two Hand Maces"],
    "Cleave": ["One Hand Axes", "One Hand Swords", "Thrusting One Hand Swords",
               "Two Hand Axes", "Two Hand Swords"],
    "Kinetic Blast": ["Wands"],
    "Split Arrow": ["Bows"],
    # Spell gems intentionally absent — caller treats them as no-weapon-req
}


def _mk(gear: dict, gem_setups: dict | None = None) -> dict:
    """Build minimum valid build_data with a single stage."""
    stage: dict = {"gear_recommendation": gear}
    if gem_setups is not None:
        stage["gem_setups"] = gem_setups
    return {"progression_stages": [stage]}


# --- Gear-first resolution -------------------------------------------------


def test_single_2h_mace_build_resolves_to_two_hand_maces():
    # Sunder on a 2H mace — the archetypal slam-build case.
    build = _mk({"Weapon 1": {"base_type": "Brass Maul"}})
    assert extract_build_weapon_classes(build, _BASE_MAP, _GEM_MAP) == {"Two Hand Maces"}


def test_dual_wield_collapses_to_single_class():
    # Dual 1H Axe Boneshatter — both slots same class.
    build = _mk({
        "Weapon 1": {"base_type": "Reaver Axe"},
        "Weapon 2": {"base_type": "Siege Axe"},
    })
    assert extract_build_weapon_classes(build, _BASE_MAP, _GEM_MAP) == {"One Hand Axes"}


def test_wand_plus_shield_ignores_non_weapon_slot():
    # Shield base "Pinnacle Tower Shield" not in _BASE_MAP — must be ignored,
    # not treated as an unknown weapon.
    build = _mk({
        "Weapon 1": {"base_type": "Opal Wand"},
        "Weapon 2": {"base_type": "Pinnacle Tower Shield"},
        "Body Armour": {"base_type": "Astral Plate"},
    })
    assert extract_build_weapon_classes(build, _BASE_MAP, _GEM_MAP) == {"Wands"}


def test_multi_stage_unions_weapon_classes():
    # Leveling on 2H sword, endgame swaps to 1H sword.
    build = {
        "progression_stages": [
            {"gear_recommendation": {"Weapon 1": {"base_type": "Eternal Sword"}}},
            {"gear_recommendation": {"Weapon 1": {"base_type": "Corsair Sword"}}},
        ],
    }
    result = extract_build_weapon_classes(build, _BASE_MAP, _GEM_MAP)
    assert result == {"One Hand Swords", "Two Hand Swords"}


# --- Gem fallback ----------------------------------------------------------


def test_no_gear_falls_back_to_gem_weapon_requirements():
    # POB export without weapon in gear slot — fall back to gem's allowed set.
    build = _mk(
        gear={},
        gem_setups={"Main": {"links": "Sunder - Melee Physical Damage Support"}},
    )
    result = extract_build_weapon_classes(build, _BASE_MAP, _GEM_MAP)
    # Sunder fallback = all four Axe+Mace 1H/2H classes.
    assert result == {"One Hand Axes", "One Hand Maces", "Two Hand Axes", "Two Hand Maces"}


def test_gear_beats_gems_when_both_present():
    # Even if Sunder gem allows 4 classes, the player-chosen weapon narrows it.
    build = _mk(
        gear={"Weapon 1": {"base_type": "Brass Maul"}},
        gem_setups={"Main": {"links": "Sunder"}},
    )
    assert extract_build_weapon_classes(build, _BASE_MAP, _GEM_MAP) == {"Two Hand Maces"}


# --- Empty / malformed -----------------------------------------------------


def test_empty_build_returns_empty_set():
    # Totally empty POB — no gear, no gems. Caller must skip L7 emission.
    assert extract_build_weapon_classes({}, _BASE_MAP, _GEM_MAP) == set()


def test_gem_without_weapon_restriction_returns_empty():
    # Spell gem (Arc) not in _GEM_MAP — fallback yields nothing.
    build = _mk(gear={}, gem_setups={"Main": {"links": "Arc"}})
    assert extract_build_weapon_classes(build, _BASE_MAP, _GEM_MAP) == set()


def test_unknown_base_type_is_skipped_not_raised():
    # A future base we haven't mapped yet must not crash the extractor.
    build = _mk({"Weapon 1": {"base_type": "Totally New Base"}})
    assert extract_build_weapon_classes(build, _BASE_MAP, _GEM_MAP) == set()
