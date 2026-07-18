# -*- coding: utf-8 -*-
"""Create collection priorities from the global POE1 creator target map."""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "data" / "poe1_global_creator_source_targets_v1.json"
OUTPUT_PATH = ROOT / "data" / "poe1_global_creator_priority_matrix_v1.json"

GENERATED_AT = "2026-07-17T00:00:00+07:00"


LANE_RULES: dict[str, dict[str, Any]] = {
    "leveling": {
        "label": "레벨링",
        "purpose": "Campaign, act-to-map, league-start, and From Zero to Hero route extraction.",
        "keywords": [
            "leveling",
            "campaign",
            "league_start",
            "starter",
            "racing",
            "race_meta",
            "zero_to_hero",
            "new_player",
            "ssf",
        ],
    },
    "endgame_build": {
        "label": "엔드게임",
        "purpose": "Early maps through voidstones and normal endgame build state extraction.",
        "keywords": [
            "endgame",
            "mapping",
            "bossing",
            "guide",
            "build_roundups",
            "league_start",
            "zero_to_hero",
            "starter",
        ],
    },
    "high_end": {
        "label": "하이엔드",
        "purpose": "Expensive scaling, min-max, mirror-tier, high-APM, and late reroll research.",
        "keywords": [
            "high_end",
            "min_max",
            "mirror",
            "high_apm",
            "trade_meta",
            "bossing",
            "high_end_mapping",
            "experimental",
        ],
    },
    "farming_strategy": {
        "label": "파밍전략",
        "purpose": "Atlas, economy, heist, mapping, and strategy-per-hour source collection.",
        "keywords": [
            "farming_strategy",
            "atlas_strategy",
            "trade_farming",
            "heist_farming",
            "mapping",
            "farm",
            "economy",
            "gamble",
        ],
    },
    "hardcore_safety": {
        "label": "하드코어/생존",
        "purpose": "HC/SSF/gauntlet survivability and defensive baseline cross-checks.",
        "keywords": [
            "hardcore",
            "ssf",
            "gauntlet",
            "defense",
            "defensive",
            "survivability",
            "racer",
        ],
    },
    "minion": {
        "label": "소환수",
        "purpose": "Minion, Spectre, SRS, Golem, and Animate Guardian source collection.",
        "keywords": [
            "minion",
            "spectre",
            "srs",
            "golem",
            "necromancer",
            "summon",
            "poison_carrion_golem",
        ],
    },
    "mine": {
        "label": "마인",
        "purpose": "Exsanguinate/Reap/Pyroclast/Hexblast mine source separation.",
        "keywords": [
            "mine",
            "miner",
            "exsanguinate",
            "pyroclast",
            "hexblast",
            "reap",
        ],
    },
    "caster": {
        "label": "캐스터",
        "purpose": "Self-cast, Archmage, Spark, Cold DoT, Brand, and spell transition extraction.",
        "keywords": [
            "caster",
            "archmage",
            "spark",
            "cold_dot",
            "brand",
            "spell",
            "autobomber",
            "ignite",
        ],
    },
    "ranger_projectile": {
        "label": "레인저/투사체",
        "purpose": "Bow, projectile, Deadeye, Pathfinder, Venom Gyre and mapping route extraction.",
        "keywords": [
            "ranger",
            "projectile",
            "bow",
            "deadeye",
            "pathfinder",
            "venom_gyre",
            "toxic_rain",
        ],
    },
    "melee": {
        "label": "근접",
        "purpose": "Melee starter, Slayer, Gladiator, Shield Crush, Cyclone, Slam and weapon cadence research.",
        "keywords": [
            "melee",
            "slayer",
            "gladiator",
            "shield_crush",
            "cyclone",
            "slam",
            "boneshatter",
            "life_stacker",
        ],
    },
    "totem": {
        "label": "토템",
        "purpose": "Spell/Ballista/Flamewood/Totem leveling and post-3.29 nerf check targets.",
        "keywords": [
            "totem",
            "hierophant",
            "ballista",
            "flamewood",
        ],
    },
    "scion_reliquarian": {
        "label": "사이온/리리쿼리언",
        "purpose": "Ascendant/Reliquarian/Luminary split and 3.29 shell tracking.",
        "keywords": [
            "scion",
            "reliquarian",
            "luminary",
            "ascendant",
        ],
    },
}


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _parse_view_count(value: str | None) -> int | None:
    if not value:
        return None
    normalized = value.casefold().replace(",", "")
    if "watching" in normalized:
        match = re.search(r"(\d+(?:\.\d+)?)", normalized)
        return int(float(match.group(1))) if match else None
    match = re.search(r"(\d+(?:\.\d+)?)\s*([kmb])?", normalized)
    if not match:
        return None
    amount = float(match.group(1))
    suffix = match.group(2)
    multiplier = {"k": 1_000, "m": 1_000_000, "b": 1_000_000_000}.get(suffix, 1)
    return int(amount * multiplier)


def _keyword_blob(creator: dict[str, Any]) -> str:
    fields: list[str] = []
    for key in ("creator_id", "display_name", "evidence_level"):
        fields.append(str(creator.get(key, "")))
    for key in ("known_focus", "source_roles", "aliases", "primary_platforms"):
        fields.extend(str(item) for item in creator.get(key, []))
    evidence = creator.get("youtube_view_evidence", {})
    if isinstance(evidence, dict):
        if evidence.get("status") == "sampled":
            fields.extend(str(evidence.get(key, "")) for key in ("title", "owner"))
    return " ".join(fields).casefold()


def _score_creator(creator: dict[str, Any]) -> int:
    score = 0
    evidence_level = creator.get("evidence_level", "")
    if "user_seeded" in evidence_level:
        score += 45
    if "known_global" in evidence_level or "known_builder" in evidence_level:
        score += 30
    if "twitchmetrics_language_rank" in evidence_level:
        score += 12
    if "guide_site" in evidence_level or "forum" in evidence_level:
        score += 10

    youtube = creator.get("youtube_view_evidence", {})
    if youtube.get("status") == "sampled":
        score += 20
        views = _parse_view_count(youtube.get("view_count_text"))
        if views:
            score += min(35, int(math.log10(max(views, 10)) * 7))
    elif youtube.get("status") == "queried_no_owner_match":
        score += 3

    twitch = creator.get("twitchmetrics_evidence", {})
    if twitch.get("status") == "sampled":
        score += 18
        rank = int(twitch.get("rank", 999))
        score += max(0, 16 - rank)

    roles = set(creator.get("source_roles", []))
    if {"guide_author", "builder"} & roles:
        score += 10
    if "farming_strategy" in roles:
        score += 8
    return score


def _creator_row(region: dict[str, Any], creator: dict[str, Any], lane_id: str) -> dict[str, Any]:
    youtube = creator.get("youtube_view_evidence", {})
    twitch = creator.get("twitchmetrics_evidence", {})
    return {
        "creator_id": creator["creator_id"],
        "display_name": creator["display_name"],
        "region_id": region["region_id"],
        "country_or_language_region": region["country_or_language_region"],
        "priority_score": _score_creator(creator),
        "source_roles": creator.get("source_roles", []),
        "known_focus": creator.get("known_focus", []),
        "evidence_level": creator.get("evidence_level"),
        "youtube_signal": {
            "status": youtube.get("status"),
            "view_count_text": youtube.get("view_count_text") or youtube.get("nearest_result", {}).get("view_count_text"),
            "video_url": youtube.get("video_url") or youtube.get("nearest_result", {}).get("video_url"),
            "title": youtube.get("title") or youtube.get("nearest_result", {}).get("title"),
            "owner": youtube.get("owner") or youtube.get("nearest_result", {}).get("owner"),
        },
        "twitchmetrics_signal": {
            "status": twitch.get("status"),
            "rank": twitch.get("rank"),
            "viewer_hours_text": twitch.get("viewer_hours_text"),
            "source_url": twitch.get("source_url"),
        },
        "source_urls": creator.get("source_urls", []),
        "promotion_status": creator.get("promotion_status"),
        "collection_goal": _collection_goal(lane_id, creator),
    }


def _collection_goal(lane_id: str, creator: dict[str, Any]) -> str:
    name = creator["display_name"]
    if lane_id == "leveling":
        return f"Collect {name} act/campaign route, stage PoB, or From Zero to Hero transition notes."
    if lane_id == "farming_strategy":
        return f"Collect {name} atlas/economy setup, cost, failure rate, and map-time assumptions."
    if lane_id == "high_end":
        return f"Collect {name} min-max PoB, budget breakpoint, and survivability caveats."
    if lane_id == "hardcore_safety":
        return f"Collect {name} defensive baseline, HC/SSF constraints, and death/failure notes."
    return f"Collect {name} direct PoB, guide context, and patch-current validation for this lane."


def _matching_lanes(creator: dict[str, Any]) -> list[str]:
    blob = _keyword_blob(creator)
    lanes = [
        lane_id
        for lane_id, rule in LANE_RULES.items()
        if any(keyword.casefold() in blob for keyword in rule["keywords"])
    ]
    if not lanes and "builder" in creator.get("source_roles", []):
        lanes.append("endgame_build")
    return lanes


def build_priority_matrix() -> dict[str, Any]:
    source = _load_json(SOURCE_PATH)
    lanes: dict[str, list[dict[str, Any]]] = {lane_id: [] for lane_id in LANE_RULES}

    for region in source["regions"]:
        for creator in region["creator_targets"]:
            for lane_id in _matching_lanes(creator):
                lanes[lane_id].append(_creator_row(region, creator, lane_id))

    lane_rows = []
    for lane_id, rows in lanes.items():
        rows.sort(key=lambda row: (-row["priority_score"], row["region_id"], row["creator_id"]))
        lane_rows.append(
            {
                "lane_id": lane_id,
                "lane_label": LANE_RULES[lane_id]["label"],
                "purpose": LANE_RULES[lane_id]["purpose"],
                "creator_count": len(rows),
                "top_creator_targets": rows[:15],
                "remaining_creator_ids": [row["creator_id"] for row in rows[15:]],
            }
        )

    all_creators = [
        creator
        for region in source["regions"]
        for creator in region["creator_targets"]
    ]
    weak_regions = []
    for region in source["regions"]:
        sampled = sum(1 for creator in region["creator_targets"] if creator["youtube_view_evidence"]["status"] == "sampled")
        weak_regions.append(
            {
                "region_id": region["region_id"],
                "country_or_language_region": region["country_or_language_region"],
                "target_count": region["target_count"],
                "youtube_sampled_creator_count": sampled,
                "needs_more_youtube_channel_confirmation": sampled < max(5, region["target_count"] // 2),
            }
        )

    immediate_queue = []
    for lane_id in ("leveling", "farming_strategy", "minion", "mine", "caster", "ranger_projectile", "melee", "high_end"):
        lane = next(row for row in lane_rows if row["lane_id"] == lane_id)
        for creator in lane["top_creator_targets"][:5]:
            immediate_queue.append(
                {
                    "queue_id": f"{lane_id}:{creator['creator_id']}",
                    "lane_id": lane_id,
                    "creator_id": creator["creator_id"],
                    "display_name": creator["display_name"],
                    "priority_score": creator["priority_score"],
                    "collection_goal": creator["collection_goal"],
                    "source_urls": creator["source_urls"],
                    "youtube_signal": creator["youtube_signal"],
                    "promotion_gate": "direct_pob_or_stage_guide_required_before_build_promotion",
                }
            )

    return {
        "schema_version": "1.0",
        "dataset_kind": "poe1_global_creator_priority_matrix",
        "generated_at": GENERATED_AT,
        "source_dataset": "data/poe1_global_creator_source_targets_v1.json",
        "source_target_count": source["coverage_summary"]["target_count"],
        "purpose": "Translate global POE1 creator targets into practical collection lanes for leveling, endgame, high-end, farming, and archetype-specific source hunting.",
        "policy": {
            "poe_scope": "poe1_only",
            "popularity_rule": "YouTube/Twitch signals only affect source collection priority. They are not build-quality proof.",
            "promotion_gate": "Every build still needs accessible direct PoB or stage guide, parser validation, and current patch context before recommendation.",
        },
        "coverage_summary": {
            "lane_count": len(lane_rows),
            "source_target_count": source["coverage_summary"]["target_count"],
            "creator_lane_assignment_count": sum(row["creator_count"] for row in lane_rows),
            "immediate_queue_count": len(immediate_queue),
            "weak_region_count": sum(1 for row in weak_regions if row["needs_more_youtube_channel_confirmation"]),
        },
        "collection_lanes": lane_rows,
        "immediate_collection_queue": immediate_queue,
        "regional_followup": weak_regions,
        "unassigned_creator_ids": [
            creator["creator_id"]
            for creator in all_creators
            if not _matching_lanes(creator)
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)

    data = build_priority_matrix()
    if args.write:
        OUTPUT_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"wrote {OUTPUT_PATH} ({data['coverage_summary']['immediate_queue_count']} queue rows)")
    else:
        print(json.dumps(data["coverage_summary"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
