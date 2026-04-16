"""
Derive POE filter weapon Class names from a parsed POB build.

Used by `sections_continue.L7 weapon_phys_proxy` to emit a `Class ==` line
that matches the build's actual weapon usage. Two independent inputs:
  - `base_to_class`  (data/weapon_base_to_class.json)  — authoritative, GGPK
  - `gem_to_weapon_req` (data/gem_weapon_requirements.json) — authoritative, POB

Resolution order is gear-first, gem-fallback: if the build parser captured a
weapon in `progression_stages[*].gear_recommendation[*].base_type`, that's the
strongest signal (the player picked it). Only if no equipped weapon is seen
do we fall back to the skill gem's allowed weapons — that covers builds where
the POB export has no weapon set yet.

Multi-stage builds (leveling → endgame) are unioned: emitting one Class filter
that covers every stage's weapons.

Returns an empty set when the build has nothing usable; callers skip the L7
block entirely in that case (no false positives).
"""

from __future__ import annotations

import logging
import re
from typing import Iterable

from build_extractor import extract_build_gems

logger = logging.getLogger(__name__)

# Accept "Weapon 1", "Weapon 2", "Weapon1", "weapon 1", "MainHand", "OffHand".
# pob_parser currently emits "Weapon 1"/"Weapon 2" but we stay permissive so
# future parser changes don't silently break detection.
_WEAPON_SLOT_RE = re.compile(r"^(?:weapon\s*\d+|main\s*hand|off\s*hand)$", re.IGNORECASE)


def _iter_gear_slots(build_data: dict) -> Iterable[tuple[str, dict]]:
    """Yield (slot_name, slot_dict) from every stage's gear_recommendation."""
    stages = build_data.get("progression_stages") or []
    if not isinstance(stages, list):
        return
    for stage in stages:
        if not isinstance(stage, dict):
            continue
        gear = stage.get("gear_recommendation")
        if not isinstance(gear, dict):
            gear = stage.get("gear")
        if not isinstance(gear, dict):
            continue
        for slot_name, slot_data in gear.items():
            if isinstance(slot_data, dict):
                yield slot_name, slot_data


def _resolve_from_gear(
    build_data: dict,
    base_to_class: dict[str, str],
) -> set[str]:
    """Extract weapon classes from equipped items. Empty set if none found."""
    found: set[str] = set()
    seen_bases_no_class: list[str] = []

    for slot_name, slot_data in _iter_gear_slots(build_data):
        # Slot-name filter is defensive; the real signal is whether base_type
        # resolves to a weapon class. Non-weapon slots (armour, rings, ...)
        # never appear in base_to_class so they'd be skipped anyway.
        base_type = slot_data.get("base_type") or slot_data.get("base") or ""
        if not isinstance(base_type, str) or not base_type:
            continue
        cls = base_to_class.get(base_type)
        if cls is None:
            # Only surface unknown bases that look like they belong in a weapon slot,
            # to keep logs useful instead of noisy (armour slots also have base_type).
            if _WEAPON_SLOT_RE.match(slot_name):
                seen_bases_no_class.append(base_type)
            continue
        found.add(cls)

    if not found and seen_bases_no_class:
        logger.warning(
            "weapon base(s) present but not in base_to_class map: %s",
            sorted(set(seen_bases_no_class)),
        )
    return found


def _resolve_from_gems(
    build_data: dict,
    gem_to_weapon_req: dict[str, list[str]],
) -> set[str]:
    """Fallback: union of weapon classes allowed by every main skill gem.

    Only active skill gems are consulted — support gems rarely have weapon
    restrictions, and when they do (e.g. Barrage Support) they're already
    narrower than the main skill's requirement.
    """
    skills, _supports = extract_build_gems(build_data)
    found: set[str] = set()
    unknown: list[str] = []
    for gem in skills:
        classes = gem_to_weapon_req.get(gem)
        if classes is None:
            unknown.append(gem)
            continue
        found.update(classes)
    if unknown:
        # Debug-level because many spell gems legitimately have no weapon req
        # (Arc, Fireball, auras, etc.) and would drown out real problems.
        logger.debug(
            "skill gems not in gem_to_weapon_req: %s", sorted(set(unknown)),
        )
    return found


def extract_build_weapon_classes(
    build_data: dict,
    base_to_class: dict[str, str],
    gem_to_weapon_req: dict[str, list[str]],
) -> set[str]:
    """Return POE filter Class names for this build's weapons.

    Args:
      build_data: parsed POB output (same shape `build_extractor` consumes)
      base_to_class: `data/weapon_base_to_class.json#base_to_class`
      gem_to_weapon_req: `data/gem_weapon_requirements.json#gem_weapon_classes`

    Returns:
      Set of POE filter `Class ==` names (e.g. {"One Hand Axes", "Two Hand Axes"}).
      Empty set when no weapon can be inferred — caller should skip L7 emission.
    """
    # Gear is strongest signal: it's what the player actually plans to hold.
    from_gear = _resolve_from_gear(build_data, base_to_class)
    if from_gear:
        return from_gear

    # POB exports without a weapon set happen during early-planning builds.
    # Gem fallback is broader (all weapons the skill *could* use) so we only
    # reach for it when gear is silent.
    from_gems = _resolve_from_gems(build_data, gem_to_weapon_req)
    if from_gems:
        logger.info(
            "weapon classes inferred from gems (no weapon in gear): %s",
            sorted(from_gems),
        )
        return from_gems

    logger.warning(
        "build has no weapon signal in gear or gems — L7 weapon_phys_proxy will be skipped"
    )
    return set()
