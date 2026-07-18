# -*- coding: utf-8 -*-
"""Find direct PoB links and build promotion work orders for corpus candidates."""

from __future__ import annotations

import argparse
import html
import json
import logging
import re
import urllib.parse
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
from typing import Any

import requests
from bs4 import BeautifulSoup

from build_corpus_expanded_collection_queue import build_expanded_collection_queue


logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parent.parent
OUT_PATH = ROOT / "data" / "build_corpus_pob_link_probe.latest.json"
MANUAL_POB_SOURCES_PATH = ROOT / "data" / "build_corpus_manual_pob_sources_v1.json"
BING_RSS = "https://www.bing.com/search?format=rss&q="
HEADERS = {"User-Agent": "Mozilla/5.0"}

POB_LINK_RE = re.compile(
    r"https?://(?:"
    r"pobb\.in/[A-Za-z0-9_-]+"
    r"|pastebin\.com/(?:raw/)?[A-Za-z0-9]+"
    r"|poe\.ninja/pob/[A-Za-z0-9]+"
    r"|poeplanner\.com/[^\s<>\")\]]+"
    r"|planners\.maxroll\.gg/[^\s<>\")\]]+"
    r")",
    re.IGNORECASE,
)

GENERIC_TERMS = {
    "path",
    "exile",
    "poe",
    "build",
    "guide",
    "league",
    "starter",
    "specialist",
    "reliquarian",
    "ascendant",
    "witch",
    "ranger",
    "duelist",
    "marauder",
    "shadow",
    "templar",
    "scion",
    "slayer",
    "juggernaut",
    "elementalist",
    "trickster",
    "champion",
    "deadeye",
    "pathfinder",
    "saboteur",
    "inquisitor",
    "hierophant",
    "necromancer",
    "guardian",
    "occultist",
    "berserker",
    "gladiator",
    "assassin",
    "chieftain",
    "mapper",
    "bossing",
    "shell",
    "defense",
}

LANE_FAILURE_LENSES = {
    "bow_projectile_attack_mapper": [
        "weapon_dps_or_added_damage_too_low",
        "accuracy_or_hit_chance_missing",
        "dead_before_damage_due_to_evasion_only_layer",
        "single_target_ballista_or_mark_setup_missing",
    ],
    "melee_strike_slam": [
        "weapon_upgrade_cadence_missing",
        "attack_speed_or_animation_lock_feels_bad",
        "fortify_armour_recovery_layer_missing",
        "map_mods_or_boss_uptime_expose_low_damage",
    ],
    "spell_hit_brand_selfcast": [
        "caster_weapon_plus_gem_level_missing",
        "mana_cost_or_archmage_reservation_mismatch",
        "cast_speed_or_brand_recall_quality_missing",
        "suppression_or_block_layer_not_online",
    ],
    "dot_ailment_dot": [
        "dot_multi_or_gem_level_scaling_missing",
        "wither_exposure_curse_uptime_missing",
        "clear_feels_good_but_single_target_stalls",
        "swap_timing_from_leveling_skill_unclear",
    ],
    "trap_mine_totem": [
        "throw_or_placement_speed_missing",
        "boss_preload_pattern_not_learned",
        "mana_reservation_or_detritus_links_wrong",
        "mapping_feels_clunky_without_movement_setup",
    ],
    "minion_trigger_autobomber_special": [
        "trigger_condition_or_minion_spawn_loop_not_understood",
        "required_unique_or_jewel_gate_hidden",
        "resistance_suffix_pressure_from_unique_slots",
        "single_target_or_boss_ramp_is_overestimated",
    ],
}


def _load_queue() -> dict[str, Any]:
    return build_expanded_collection_queue()


def _load_manual_pob_sources() -> dict[str, list[dict[str, Any]]]:
    if not MANUAL_POB_SOURCES_PATH.exists():
        return {}
    with open(MANUAL_POB_SOURCES_PATH, "r", encoding="utf-8-sig") as handle:
        data = json.load(handle)
    by_candidate: dict[str, list[dict[str, Any]]] = {}
    for record in data.get("records", []):
        by_candidate.setdefault(record["candidate_id"], []).append(record)
    return by_candidate


def normalize_url(url: str) -> str:
    cleaned = html.unescape(url.strip())
    cleaned = cleaned.rstrip(".,;:!?)\"]}'")
    if "pastebin.com/" in cleaned and "/raw/" not in cleaned:
        cleaned = cleaned.replace("pastebin.com/", "pastebin.com/raw/", 1)
    return cleaned


def candidate_terms(candidate: dict[str, Any]) -> list[str]:
    text = " ".join(
        str(candidate.get(key) or "")
        for key in ("display_name", "main_skill", "class_name", "ascendancy")
    )
    terms = []
    for token in re.findall(r"[A-Za-z][A-Za-z0-9]+", text.lower()):
        if len(token) < 4 or token in GENERIC_TERMS:
            continue
        if token not in terms:
            terms.append(token)
    return terms


def candidate_search_queries(candidate: dict[str, Any]) -> list[str]:
    display = candidate["display_name"]
    skill = candidate["main_skill"]
    ascendancy = candidate["ascendancy"]
    patch = candidate["patch"]
    return [
        f'site:pobb.in "{display}" "{patch}"',
        f'site:pobb.in "{skill}" "{ascendancy}" "{patch}"',
        f'"{display}" "pobb.in" "PoE {patch}"',
        f'site:pobarchives.com "{skill}" "{patch}"',
        f'site:youtube.com "{display}" "{patch}" "PoB"',
    ]


def relevance_score(candidate: dict[str, Any], text: str) -> int:
    haystack = text.lower()
    terms = candidate_terms(candidate)
    score = sum(1 for term in terms if term in haystack)
    if str(candidate.get("patch") or "").lower() in haystack:
        score += 2
    if str(candidate.get("main_skill") or "").lower() in haystack:
        score += 2
    if str(candidate.get("ascendancy") or "").lower() in haystack:
        score += 1
    return score


def text_mentions_patch(candidate: dict[str, Any], text: str) -> bool:
    """True only when the candidate's own patch token is present in the text.

    Live-discovered PoBs (source pages, search results) must prove they belong to
    the candidate's patch; a same-skill match on a different patch is not enough.
    """
    patch = str(candidate.get("patch") or "").strip().lower()
    if not patch:
        return False
    return patch in text.lower()


def extract_pob_links(text: str, source_url: str = "") -> list[dict[str, Any]]:
    decoded = html.unescape(text)
    found: dict[str, dict[str, Any]] = {}

    for match in POB_LINK_RE.finditer(decoded):
        url = normalize_url(match.group(0))
        start = max(0, match.start() - 160)
        end = min(len(decoded), match.end() + 160)
        found[url] = {
            "url": url,
            "source_url": source_url,
            "anchor_text": "",
            "context": " ".join(decoded[start:end].split()),
        }

    try:
        soup = BeautifulSoup(decoded, "html.parser")
    except Exception:
        soup = None
    if soup is not None:
        for anchor in soup.find_all("a"):
            href = anchor.get("href") or ""
            href = urllib.parse.urljoin(source_url, href)
            if not POB_LINK_RE.search(href):
                continue
            url = normalize_url(POB_LINK_RE.search(href).group(0))
            parent_text = anchor.parent.get_text(" ", strip=True) if anchor.parent else ""
            found[url] = {
                "url": url,
                "source_url": source_url,
                "anchor_text": anchor.get_text(" ", strip=True),
                "context": " ".join(parent_text.split()),
            }

    return list(found.values())


def parse_bing_rss(xml_text: str) -> list[dict[str, str]]:
    root = ET.fromstring(xml_text)
    rows = []
    for item in root.findall("./channel/item"):
        rows.append(
            {
                "title": (item.findtext("title") or "").strip(),
                "url": normalize_url((item.findtext("link") or "").strip()),
                "description": " ".join((item.findtext("description") or "").split()),
            }
        )
    return rows


def fetch_text(session: requests.Session, url: str, timeout: int = 18) -> tuple[str | None, str | None]:
    try:
        response = session.get(url, timeout=timeout, headers=HEADERS)
        response.raise_for_status()
        return response.text, None
    except Exception as exc:
        return None, f"{type(exc).__name__}: {exc}"


def fetch_search_results(session: requests.Session, query: str) -> tuple[list[dict[str, str]], str | None]:
    url = BING_RSS + urllib.parse.quote(query)
    text, error = fetch_text(session, url, timeout=18)
    if error:
        return [], error
    try:
        return parse_bing_rss(text or ""), None
    except Exception as exc:
        return [], f"{type(exc).__name__}: {exc}"


def _candidate_sources(candidate: dict[str, Any], source_registry: dict[str, dict[str, str]]) -> list[dict[str, str]]:
    rows = []
    for source_id in candidate.get("source_refs", []):
        source = source_registry[source_id]
        rows.append(
            {
                "source_id": source_id,
                "family": source["family"],
                "url": source["url"],
                "label": source["label"],
            }
        )
    return rows


def _snapshot_plan(candidate: dict[str, Any]) -> list[dict[str, str]]:
    skill = candidate["main_skill"]
    lane = candidate["lane_id"]
    role = candidate["collection_role"]
    base = [
        {
            "snapshot_id": "entry_or_leveling_state",
            "required_pob_kind": "campaign_or_maps_entry_pob",
            "purpose": "Capture the skill or fallback used before the final engine is online.",
        },
        {
            "snapshot_id": "budget_mapping_state",
            "required_pob_kind": "budget_mapping_pob",
            "purpose": f"Capture the first real {skill} mapping state for {lane}.",
        },
    ]
    if role in {"transition_case", "failure_edge_case"}:
        base.append(
            {
                "snapshot_id": "gate_or_failure_state",
                "required_pob_kind": "transition_gate_or_failed_setup_pob",
                "purpose": "Capture the item/tree/config gate that causes the build to split or fail.",
            }
        )
    return base


def beginner_failure_lens(candidate: dict[str, Any]) -> dict[str, Any]:
    role = candidate["collection_role"]
    lane = candidate["lane_id"]
    risks = list(LANE_FAILURE_LENSES.get(lane, []))
    if role == "failure_edge_case":
        risks.append("explicit_negative_or_bricked_case_required")
    if candidate["source_status"] == "watchlist_pre_patch_notes":
        risks.append("pre_patch_notes_numbers_may_change")
    return {
        "lens_id": f"{lane}_{role}",
        "risk_tags": risks,
        "must_record": [
            "why_new_player_gets_stuck",
            "minimum_fix_before_next_map_tier",
            "item_or_tree_gate_if_any",
            "map_mods_to_avoid",
        ],
    }


def _candidate_direct_links(
    candidate: dict[str, Any],
    source_pob_links: dict[str, list[dict[str, Any]]],
    search_hits: list[dict[str, Any]],
    manual_sources: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    selected: dict[str, dict[str, Any]] = {}

    candidate_patch = candidate.get("patch")
    for source in manual_sources or []:
        if source.get("patch") != candidate_patch:
            logger.warning(
                "Skipping manual PoB source for %s: record patch %r != candidate patch %r",
                candidate.get("candidate_id"),
                source.get("patch"),
                candidate_patch,
            )
            continue
        for pob in source.get("pob_urls") or []:
            url = normalize_url(pob["url"])
            selected[url] = {
                "url": url,
                "source_url": source.get("source_url", ""),
                "anchor_text": source.get("source_label", ""),
                "context": pob.get("context", ""),
                "match_score": 99,
                "discovery_method": "manual_verified_source",
                "pob_role": pob.get("role", "primary"),
                "confidence": source.get("confidence", "medium"),
            }

    for source_id in candidate.get("source_refs", []):
        for link in source_pob_links.get(source_id, []):
            text = f"{link.get('anchor_text', '')} {link.get('context', '')} {link.get('url', '')}"
            score = relevance_score(candidate, text)
            if score >= 2 and text_mentions_patch(candidate, text):
                row = dict(link)
                row["match_score"] = score
                row["discovery_method"] = "source_page"
                selected[row["url"]] = row

    for hit in search_hits:
        url = hit.get("url", "")
        if not POB_LINK_RE.search(url):
            continue
        text = f"{hit.get('title', '')} {hit.get('url', '')} {hit.get('description', '')}"
        score = relevance_score(candidate, text)
        if score >= 2 and text_mentions_patch(candidate, text):
            selected[url] = {
                "url": url,
                "source_url": hit.get("search_query", ""),
                "anchor_text": hit.get("title", ""),
                "context": hit.get("description", ""),
                "match_score": score,
                "discovery_method": "search_result",
            }

    return sorted(selected.values(), key=lambda row: (-row["match_score"], row["url"]))[:8]


def build_pob_link_probe(
    *,
    live: bool = False,
    candidate_limit: int | None = None,
    source_limit: int | None = None,
    search_queries_per_candidate: int = 2,
) -> dict[str, Any]:
    queue = _load_queue()
    manual_by_candidate = _load_manual_pob_sources()
    source_registry = queue["source_registry"]
    candidates = [
        candidate
        for patch in queue["patches"]
        for candidate in patch["candidates"]
    ]
    if candidate_limit is not None:
        candidates = candidates[:candidate_limit]

    needed_source_ids = []
    for candidate in candidates:
        for source_id in candidate.get("source_refs", []):
            if source_id not in needed_source_ids:
                needed_source_ids.append(source_id)
    if source_limit is not None:
        needed_source_ids = needed_source_ids[:source_limit]

    session = requests.Session()
    session.trust_env = False

    source_fetches: dict[str, dict[str, Any]] = {}
    source_pob_links: dict[str, list[dict[str, Any]]] = {}
    if live:
        for source_id in needed_source_ids:
            source = source_registry[source_id]
            text, error = fetch_text(session, source["url"])
            links = extract_pob_links(text or "", source["url"]) if text else []
            source_fetches[source_id] = {
                "source_id": source_id,
                "family": source["family"],
                "url": source["url"],
                "fetch_status": "ok" if error is None else "error",
                "error": error,
                "direct_pob_link_count": len(links),
            }
            source_pob_links[source_id] = links

    work_orders = []
    search_error_count = 0
    for candidate in candidates:
        search_hits: list[dict[str, Any]] = []
        queries = candidate_search_queries(candidate)
        if live:
            for query in queries[:search_queries_per_candidate]:
                results, error = fetch_search_results(session, query)
                if error:
                    search_error_count += 1
                    continue
                for result in results[:6]:
                    result = dict(result)
                    result["search_query"] = query
                    search_hits.append(result)

        direct_links = _candidate_direct_links(
            candidate,
            source_pob_links,
            search_hits,
            manual_by_candidate.get(candidate["candidate_id"], []),
        )
        promotion_status = (
            "ready_for_pob_parse"
            if direct_links
            else "needs_direct_pob_link"
        )
        if candidate["source_status"] == "watchlist_pre_patch_notes" and not direct_links:
            promotion_status = "watchlist_needs_patch_notes_and_pob"

        work_orders.append(
            {
                "candidate_id": candidate["candidate_id"],
                "patch": candidate["patch"],
                "display_name": candidate["display_name"],
                "lane_id": candidate["lane_id"],
                "collection_role": candidate["collection_role"],
                "source_status": candidate["source_status"],
                "promotion_status": promotion_status,
                "main_skill": candidate["main_skill"],
                "class_name": candidate["class_name"],
                "ascendancy": candidate["ascendancy"],
                "source_refs": _candidate_sources(candidate, source_registry),
                "search_queries": queries,
                "direct_pob_candidates": direct_links,
                "state_snapshot_plan": _snapshot_plan(candidate),
                "beginner_failure_lens": beginner_failure_lens(candidate),
                "required_next_steps": [
                    "confirm_direct_pob_owner_or_guide_context",
                    "parse_pob_with_python_pob_parser",
                    "persist_build_instance_json",
                    "normalize_two_or_more_state_snapshots",
                    "record_beginner_failure_reason",
                ],
            }
        )

    status_counts = Counter(order["promotion_status"] for order in work_orders)
    source_fetch_status_counts = Counter(row["fetch_status"] for row in source_fetches.values())
    direct_count = sum(len(order["direct_pob_candidates"]) for order in work_orders)

    return {
        "schema_version": "1.0",
        "dataset_kind": "poe1_build_corpus_pob_link_probe",
        "updated_at": "2026-07-17",
        "live_probe_enabled": live,
        "summary": {
            "candidate_count": len(work_orders),
            "source_count": len(needed_source_ids),
            "manual_source_record_count": sum(len(rows) for rows in manual_by_candidate.values()),
            "direct_pob_candidate_count": direct_count,
            "promotion_status_counts": dict(sorted(status_counts.items())),
            "source_fetch_status_counts": dict(sorted(source_fetch_status_counts.items())),
            "search_error_count": search_error_count,
        },
        "source_fetches": [source_fetches[source_id] for source_id in needed_source_ids if source_id in source_fetches],
        "work_orders": work_orders,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true", help="Fetch source pages and Bing RSS results.")
    parser.add_argument("--write", action="store_true", help=f"Write {OUT_PATH.relative_to(ROOT)}")
    parser.add_argument("--candidate-limit", type=int, default=None)
    parser.add_argument("--source-limit", type=int, default=None)
    parser.add_argument("--search-queries-per-candidate", type=int, default=2)
    args = parser.parse_args()

    result = build_pob_link_probe(
        live=args.live,
        candidate_limit=args.candidate_limit,
        source_limit=args.source_limit,
        search_queries_per_candidate=args.search_queries_per_candidate,
    )
    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.write:
        OUT_PATH.write_text(text + "\n", encoding="utf-8")
    print(json.dumps(result["summary"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
