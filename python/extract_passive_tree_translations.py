"""
Passive Tree Korean Translation Extractor

Extracts Korean translations for stats used in the POE character passive tree.

Input:
  - data/skilltree-export/data.json  (GGG official tree export, English)
  - data/poe_translations.json       (38MB, full EN→KR mapping with {N} templates)

Output:
  - data/skilltree-export/passive_tree_translations.json
    Shape: { "en_template": "ko_template", ... }
    Only contains templates that actually appear in the tree (small footprint).

Matching strategy:
  Passive tree stat strings have concrete numbers ("2% increased Effect of your Curses").
  poe_translations.json `mods` keys use {N} placeholders ("{0}% increased Effect of your Curses").
  We replace each numeric literal in the passive stat with {0}, {1}, ... in order,
  then lookup the mods dict.

Baseline measured coverage (character tree, 3338 nodes, 2559 unique stats):
  - {N} placeholder match: 2352/2559 = 91.9%

The remaining misses are multi-line stats with line-break variations and
Trigger-Level-N variants. Runtime falls back to the English source for misses.
"""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path

logger = logging.getLogger(__name__)

# Match optional sign, integer, optional decimals — consumed one numeric literal at a time.
_NUMERIC_RE = re.compile(r"[+-]?\d+(?:\.\d+)?")


def normalize_numbers(stat: str) -> str:
    """Replace each numeric literal with {0}, {1}, ... in order.

    "+2% chance for X" -> "+{0}% chance for X"
    "8% on 5 Hits"     -> "{0}% on {1} Hits"
    """
    counter = 0

    def _sub(_match: re.Match[str]) -> str:
        nonlocal counter
        token = f"{{{counter}}}"
        counter += 1
        return token

    return _NUMERIC_RE.sub(_sub, stat)


def collect_tree_stats(tree_data: dict) -> set[str]:
    """Collect every unique stat string referenced by any node in the tree."""
    nodes = tree_data.get("nodes", {})
    if not isinstance(nodes, dict):
        raise ValueError("skilltree data.json has no 'nodes' dict")

    stats: set[str] = set()
    for node in nodes.values():
        if not isinstance(node, dict):
            continue
        node_stats = node.get("stats")
        if not node_stats:
            continue
        for s in node_stats:
            if isinstance(s, str) and s:
                stats.add(s)
    return stats


def build_translation_map(
    tree_stats: set[str],
    mods: dict[str, str],
) -> tuple[dict[str, str], int, int]:
    """Build a minimal EN->KR template map covering only stats used in the tree.

    Returns (map, hit_count, miss_count).
    The map key is the normalized ({N}) English template;
    the value is the Korean template string from mods.
    """
    out: dict[str, str] = {}
    hit = 0
    miss = 0

    for stat in tree_stats:
        # 1) Try direct match first (no numbers in stat, e.g. "Minions created Recently cannot be Damaged")
        if stat in mods:
            out[stat] = mods[stat]
            hit += 1
            continue

        # 2) {N} placeholder match
        normalized = normalize_numbers(stat)
        kr = mods.get(normalized)
        if kr is not None:
            out[normalized] = kr
            hit += 1
            continue

        miss += 1

    return out, hit, miss


def main() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    project_root = Path(__file__).resolve().parent.parent
    tree_path = project_root / "data" / "skilltree-export" / "data.json"
    trans_path = project_root / "data" / "poe_translations.json"
    out_path = project_root / "data" / "skilltree-export" / "passive_tree_translations.json"

    if not tree_path.exists():
        logger.error("Tree data not found: %s", tree_path)
        return 1
    if not trans_path.exists():
        logger.error("Translation data not found: %s", trans_path)
        return 1

    logger.info("Loading tree: %s", tree_path)
    try:
        with tree_path.open("r", encoding="utf-8") as f:
            tree_data = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        logger.error("Failed to load tree data: %s", e)
        return 1

    logger.info("Loading translations: %s", trans_path)
    try:
        with trans_path.open("r", encoding="utf-8") as f:
            trans_data = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        logger.error("Failed to load translation data: %s", e)
        return 1

    mods = trans_data.get("mods")
    if not isinstance(mods, dict):
        logger.error("poe_translations.json has no 'mods' dict")
        return 1

    tree_stats = collect_tree_stats(tree_data)
    logger.info("Collected %d unique stat strings from tree", len(tree_stats))

    translation_map, hits, misses = build_translation_map(tree_stats, mods)
    total = hits + misses
    coverage = (hits / total * 100.0) if total else 0.0
    logger.info(
        "Translation coverage: %d/%d = %.1f%% (%d misses)",
        hits, total, coverage, misses,
    )

    # Sort keys for deterministic diffs
    sorted_map = dict(sorted(translation_map.items()))
    payload = {
        "source": "poe_translations.json#mods",
        "coverage": {
            "total_stats": total,
            "hits": hits,
            "misses": misses,
        },
        "translations": sorted_map,
    }

    logger.info("Writing: %s", out_path)
    try:
        with out_path.open("w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
    except OSError as e:
        logger.error("Failed to write output: %s", e)
        return 1

    size_kb = out_path.stat().st_size / 1024.0
    logger.info("Wrote %d entries (%.1f KB)", len(sorted_map), size_kb)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
