"""
Build data/weapon_base_to_class.json from GGPK-extracted BaseItemTypes.

Input : data/game_data/BaseItemTypes.json (GGPK extract)
Output: data/weapon_base_to_class.json

Mapping rule:
  BaseItemTypes[n].InheritsFrom ends with a segment like 'AbstractOneHandAxe' →
  POE filter `Class ==` name "One Hand Axes". We keep only classes listed by
  NeverSink's weapon_phys rule (Sceptres/Staves/RuneDaggers/FishingRods excluded
  because physical skills cannot use them).

Usage:
  python python/extract_weapon_bases.py

Rerun whenever BaseItemTypes.json is refreshed from a new GGPK extract.
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

# InheritsFrom suffix → POE filter Class == name.
# Source: data/weapon_mod_tiers.json#weapon_classes (NeverSink ground truth).
# Classes omitted on purpose: Sceptres, Staves, Rune Daggers, Fishing Rods.
_INHERITS_TO_CLASS: dict[str, str] = {
    "AbstractClaw": "Claws",
    "AbstractDagger": "Daggers",
    "AbstractOneHandAxe": "One Hand Axes",
    "AbstractOneHandMace": "One Hand Maces",
    "AbstractOneHandSword": "One Hand Swords",
    "AbstractOneHandSwordThrusting": "Thrusting One Hand Swords",
    "AbstractWand": "Wands",
    "AbstractBow": "Bows",
    "AbstractWarstaff": "Warstaves",
    "AbstractTwoHandAxe": "Two Hand Axes",
    "AbstractTwoHandMace": "Two Hand Maces",
    "AbstractTwoHandSword": "Two Hand Swords",
}


def classify(inherits_from: str) -> str | None:
    """Return POE filter Class name for a BaseItemTypes inheritance path.

    Returns None for non-physical weapon classes (sceptre, staff, rune dagger, fishing rod).
    """
    if not inherits_from:
        return None
    suffix = inherits_from.rsplit("/", 1)[-1]
    return _INHERITS_TO_CLASS.get(suffix)


def build_mapping(base_items: list[dict]) -> dict[str, str]:
    """Produce {base_name: filter_class_name}.

    Skips entries that have no Name (shouldn't happen for real bases but guard anyway),
    entries with empty-string Name (placeholder/template rows), and entries whose
    InheritsFrom does not map to a physical weapon class.
    """
    mapping: dict[str, str] = {}
    skipped_non_phys = 0
    skipped_empty_name = 0
    collisions: list[tuple[str, str, str]] = []

    for item in base_items:
        if not isinstance(item, dict):
            continue
        name = item.get("Name")
        inherits = item.get("InheritsFrom")
        if not isinstance(name, str) or not name.strip():
            skipped_empty_name += 1
            continue
        cls = classify(inherits or "")
        if cls is None:
            skipped_non_phys += 1
            continue
        prev = mapping.get(name)
        if prev is not None and prev != cls:
            # Two bases with same Name but different Class — record so we can review
            collisions.append((name, prev, cls))
        mapping[name] = cls

    if collisions:
        for name, a, b in collisions:
            logger.warning("base name collision: %s -> %s vs %s", name, a, b)
    logger.info(
        "processed: kept=%d, skipped_non_phys=%d, skipped_empty_name=%d",
        len(mapping), skipped_non_phys, skipped_empty_name,
    )
    return mapping


def main() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    project_root = Path(__file__).resolve().parent.parent
    src = project_root / "data" / "game_data" / "BaseItemTypes.json"
    dst = project_root / "data" / "weapon_base_to_class.json"

    if not src.exists():
        logger.error("BaseItemTypes.json not found: %s", src)
        return 1

    try:
        with src.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        logger.error("failed to load %s: %s", src, e)
        return 1

    if not isinstance(data, list):
        logger.error("expected list at root of %s, got %s", src, type(data).__name__)
        return 1

    mapping = build_mapping(data)

    # Verify every target class is populated — prevents silent regressions after GGPK refresh.
    covered = set(mapping.values())
    expected = set(_INHERITS_TO_CLASS.values())
    missing = expected - covered
    if missing:
        logger.error("no bases mapped for classes: %s — check GGPK source", sorted(missing))
        return 1

    # Sort keys for stable diffs
    payload = {
        "source": "data/game_data/BaseItemTypes.json (GGPK extract)",
        "generator": "python/extract_weapon_bases.py",
        "physical_weapon_classes": sorted(expected),
        "base_to_class": dict(sorted(mapping.items())),
    }

    try:
        with dst.open("w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
    except OSError as e:
        logger.error("failed to write %s: %s", dst, e)
        return 1

    per_class = {c: 0 for c in expected}
    for c in mapping.values():
        per_class[c] += 1
    logger.info("wrote %s: %d bases across %d classes", dst, len(mapping), len(expected))
    for cls in sorted(per_class):
        logger.info("  %s: %d", cls, per_class[cls])
    return 0


if __name__ == "__main__":
    sys.exit(main())
