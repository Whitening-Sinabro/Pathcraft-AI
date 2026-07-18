# -*- coding: utf-8 -*-
"""Build cumulative POE1 patch context for 3.27 -> 3.29 reuse decisions."""

from __future__ import annotations

import json
import re
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any

from patch_note_scraper import classify_change, infer_patch_tags

ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = ROOT / "data"
PATCH_DIR = DATA_ROOT / "patch_notes"
INDEX_PATH = PATCH_DIR / "patch_index.json"
OUTPUT_PATH = PATCH_DIR / "poe1_3_27_3_29_patch_history_context.json"

PATCH_BANDS = ("3.27", "3.28", "3.29")
OFFICIAL_FORUM_URL = "https://www.pathofexile.com/forum/view-forum/patch-notes"

DOMAIN_KEYWORDS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("skill_gem", (" gem", " skill", " support", " vaal ", "trigger", "cast ", "spell", "attack")),
    ("minion", ("minion", "spectre", "golem", "zombie", "skeleton", "srs", "guardian")),
    ("mine_trap_totem", ("mine", "trap", "totem", "ballista")),
    ("passive_tree", ("passive", "mastery", "notable", "keystone", "ascendancy")),
    ("item_unique", ("unique", "item", "jewel", "ring", "amulet", "weapon", "shield", "helmet")),
    ("socket_crafting", ("socket", "chromatic", "jeweller", "vorici", "quality", "colour", "color")),
    ("atlas_farming", ("atlas", "map", "scarab", "scrying", "legion", "abyss", "breach", "ritual")),
    ("economy_reward", ("reward", "drop", "currency", "divination", "card", "vendor", "heist")),
    ("league_system", ("league", "mercenary", "trarthan", "allflame", "reliquarian", "luminary")),
)

SAMPLE_KEYWORDS = (
    "gem",
    "support",
    "minion",
    "spectre",
    "golem",
    "mine",
    "totem",
    "passive",
    "ascendancy",
    "unique",
    "socket",
    "chromatic",
    "atlas",
    "scarab",
    "mercenary",
    "reliquarian",
    "luminary",
    "allflame",
)

NOISE_LINES = (
    "view staff posts",
    "post reply",
    "last bumped on",
    "last edited by",
    "report forum post",
)


def _load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        f.write("\n")


def _patch_band(version: str) -> str:
    match = re.match(r"^(\d+\.\d+)\.", version)
    return match.group(1) if match else ""


def _patch_file_for(version: str) -> Path:
    filename = f"patch_{version.replace('.', '_').replace('-', '_')}.json"
    return PATCH_DIR / filename


def _version_sort_key(version: str) -> tuple[int, int, int, int, int]:
    match = re.match(r"^(\d+)\.(\d+)\.(\d+)([a-z]?)(?:-hotfix(\d+))?$", version, re.IGNORECASE)
    if not match:
        return (0, 0, 0, 0, 0)
    major, minor, patch, suffix, hotfix = match.groups()
    suffix_rank = 0 if not suffix else ord(suffix.lower()) - ord("a") + 1
    return (int(major), int(minor), int(patch), suffix_rank, int(hotfix or 0))


def _iter_patch_lines(data: dict[str, Any]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []

    def append_lines(section: str, values: Any) -> None:
        if not isinstance(values, list):
            return
        title = str(data.get("title", "")).strip().casefold()
        for line in values:
            if not isinstance(line, str):
                continue
            stripped = line.strip()
            lowered = stripped.casefold()
            if not stripped or lowered == title:
                continue
            if any(lowered.startswith(prefix) for prefix in NOISE_LINES):
                continue
            rows.append({"section": section, "line": stripped})

    sections = data.get("sections")
    if isinstance(sections, dict):
        for section, lines in sections.items():
            append_lines(str(section), lines)
        return rows

    append_lines("all_changes", data.get("all_changes"))
    append_lines("changes", data.get("changes"))
    return rows


def _domain_for(line: str, section: str) -> str:
    lowered = f"{section} {line}".casefold()
    for domain, keywords in DOMAIN_KEYWORDS:
        if any(keyword in lowered for keyword in keywords):
            return domain
    return "other"


def _is_sample_line(line: str) -> bool:
    lowered = line.casefold()
    return any(keyword in lowered for keyword in SAMPLE_KEYWORDS)


def _source_entry(version: str, info: dict[str, Any], path: Path, data: dict[str, Any]) -> dict[str, Any]:
    lines = _iter_patch_lines(data)
    domain_counts: Counter[str] = Counter()
    watch_counts: Counter[str] = Counter()
    change_counts: Counter[str] = Counter()
    samples: list[dict[str, Any]] = []

    for row in lines:
        line = row["line"]
        section = row["section"]
        domain = _domain_for(line, section)
        tags = infer_patch_tags(line, section)
        domain_counts[domain] += 1
        change_counts[classify_change(line)] += 1
        for tag in tags:
            watch_counts[tag] += 1
        if len(samples) < 8 and _is_sample_line(line):
            samples.append({
                "section": section,
                "domain": domain,
                "change_type": classify_change(line),
                "watch_tags": tags,
                "line": line,
            })

    return {
        "version": version,
        "patch_band": _patch_band(version),
        "title": data.get("title") or info.get("title", ""),
        "patch_type": data.get("patch_type") or info.get("patch_type", ""),
        "url": data.get("url") or info.get("url", ""),
        "source_file": str(path.relative_to(DATA_ROOT)).replace("\\", "/"),
        "collected_at": data.get("collected_at", ""),
        "line_count": len(lines),
        "domain_counts": dict(sorted(domain_counts.items())),
        "watch_tag_counts": dict(sorted(watch_counts.items())),
        "change_type_counts": dict(sorted(change_counts.items())),
        "sample_lines": samples,
    }


def _summarize_band(band: str, sources: list[dict[str, Any]]) -> dict[str, Any]:
    type_counts = Counter(source["patch_type"] for source in sources)
    domains: Counter[str] = Counter()
    watch_tags: Counter[str] = Counter()
    total_lines = 0
    for source in sources:
        total_lines += int(source.get("line_count", 0))
        domains.update(source.get("domain_counts", {}))
        watch_tags.update(source.get("watch_tag_counts", {}))

    latest = sources[-1] if sources else {}
    return {
        "patch_band": band,
        "patch_count": len(sources),
        "major_count": type_counts.get("major", 0),
        "minor_count": type_counts.get("minor", 0),
        "hotfix_count": type_counts.get("hotfix", 0),
        "line_count": total_lines,
        "latest_version": latest.get("version", ""),
        "latest_title": latest.get("title", ""),
        "latest_url": latest.get("url", ""),
        "domain_counts": dict(sorted(domains.items())),
        "watch_tag_counts": dict(sorted(watch_tags.items())),
        "source_versions": [
            {
                "version": source["version"],
                "title": source["title"],
                "patch_type": source["patch_type"],
                "url": source["url"],
                "line_count": source["line_count"],
            }
            for source in sources
        ],
    }


def build_patch_history_context() -> dict[str, Any]:
    index = _load_json(INDEX_PATH)
    if not isinstance(index, dict):
        raise ValueError(f"Invalid patch index: {INDEX_PATH}")

    sources_by_band: dict[str, list[dict[str, Any]]] = {band: [] for band in PATCH_BANDS}
    missing_files: list[str] = []

    for version, info in sorted(index.items(), key=lambda item: _version_sort_key(item[0])):
        band = _patch_band(version)
        if band not in sources_by_band:
            continue
        path = _patch_file_for(version)
        if not path.exists():
            missing_files.append(str(path.relative_to(DATA_ROOT)).replace("\\", "/"))
            continue
        data = _load_json(path)
        if not isinstance(data, dict):
            continue
        sources_by_band[band].append(_source_entry(version, info, path, data))

    band_summaries = [_summarize_band(band, sources_by_band[band]) for band in PATCH_BANDS]
    all_sources = [source for band in PATCH_BANDS for source in sources_by_band[band]]
    latest = all_sources[-1] if all_sources else {}

    cumulative_domains: Counter[str] = Counter()
    cumulative_watch_tags: Counter[str] = Counter()
    patch_type_counts: Counter[str] = Counter()
    for source in all_sources:
        cumulative_domains.update(source.get("domain_counts", {}))
        cumulative_watch_tags.update(source.get("watch_tag_counts", {}))
        patch_type_counts[source.get("patch_type", "")] += 1

    sample_evidence_lines = []
    for source in all_sources:
        for sample in source.get("sample_lines", [])[:2]:
            sample_evidence_lines.append({
                "version": source["version"],
                "patch_band": source["patch_band"],
                "title": source["title"],
                "url": source["url"],
                **sample,
            })
            if len(sample_evidence_lines) >= 24:
                break
        if len(sample_evidence_lines) >= 24:
            break

    return {
        "dataset_kind": "poe1_3_27_3_29_patch_history_context",
        "schema_version": "1.0.0",
        "generated_at": date.today().isoformat(),
        "scope": {
            "game": "poe1",
            "patch_bands": list(PATCH_BANDS),
            "official_forum_url": OFFICIAL_FORUM_URL,
            "latest_observed_version": latest.get("version", ""),
            "latest_observed_title": latest.get("title", ""),
            "latest_observed_url": latest.get("url", ""),
            "current_329_state": "3.29.0 base patch notes only; no 3.29 hotfix is present in the local index as of 2026-07-17.",
        },
        "source_policy": {
            "required_use": "When reusing 3.27 or 3.28 build sources for 3.29, check every later official patch note, minor patch, and hotfix in this context before assigning a player-facing label.",
            "source_order": [
                "official patch note and hotfix text",
                "post-patch local GGPK/client extract",
                "Path of Building support and parseability",
                "poe.ninja or creator live evidence",
                "measured player results",
            ],
            "poe2_scope": "excluded",
        },
        "patch_band_summary": band_summaries,
        "cumulative_summary": {
            "patch_count": len(all_sources),
            "major_count": patch_type_counts.get("major", 0),
            "minor_count": patch_type_counts.get("minor", 0),
            "hotfix_count": patch_type_counts.get("hotfix", 0),
            "domain_counts": dict(sorted(cumulative_domains.items())),
            "watch_tag_counts": dict(sorted(cumulative_watch_tags.items())),
            "missing_files": missing_files,
        },
        "decision_gates": [
            {
                "id": "historical_patch_survival",
                "player_label": "연습해도 됨",
                "rule": "A 3.27 or 3.28 PoB can be used for mechanics practice only until later patch notes, GGPK, and PoB confirm the same engine still works in 3.29.",
            },
            {
                "id": "hotfix_override",
                "player_label": "보류",
                "rule": "Any later hotfix or minor patch touching a required gem, support, item, passive, reward source, or league mechanic overrides the older build source for that affected part.",
            },
            {
                "id": "pob_compatibility",
                "player_label": "가능성 높음",
                "rule": "A candidate can move above practice status only when the current PoB can parse the relevant 3.29 gems, passives, items, or a documented limitation is shown.",
            },
            {
                "id": "socket_quality_optimization",
                "player_label": "최종 최적화",
                "rule": "3.29 colour matching is not a socketability gate. It is a +10% quality optimization and should be prioritized for main links or gems with strong quality scaling after access and link count are solved.",
            },
        ],
        "candidate_patch_band_rules": [
            {
                "source_patch_band": "3.27",
                "default_max_label": "연습해도 됨",
                "upgrade_condition": "Only upgrade after 3.28 and 3.29 patch deltas show no direct engine conflict and a current PoB/live sample exists.",
            },
            {
                "source_patch_band": "3.28",
                "default_max_label": "가능성 높음",
                "upgrade_condition": "Can be prioritized when 3.29 is neutral or favorable, but still needs current PoB/live validation before final recommendation.",
            },
            {
                "source_patch_band": "3.29",
                "default_max_label": "가능성 높음",
                "upgrade_condition": "Can move higher only after launch client/GGPK, PoB support, and live performance evidence exist.",
            },
        ],
        "socket_match_optimization_policy": {
            "access_rule": "In 3.29, gems can be socketed even when gem colour and equipment socket colour do not match.",
            "optimization_rule": "A red, green, or blue socket matching the gem colour grants that socketed gem +10% quality.",
            "why_it_matters": [
                "Quality can be direct damage, projectile speed, duration, radius, shock effect, mana cost, cooldown, minion stats, or utility depending on the gem.",
                "The best value is usually on the main damage link, a build-defining support, or a gem whose quality stat changes clear/boss uptime.",
                "The value is low while leveling if link count, item level, life/resists, or basic DPS are still unsolved.",
            ],
            "high_priority_matches": [
                "main_damage_skill",
                "build_defining_support",
                "quality_scaling_gem",
                "final_six_link",
                "reservation_or_mana_pressure_gem",
                "duration_radius_projectile_or_cooldown_quality_gem",
            ],
            "low_priority_matches": [
                "temporary_leveling_link",
                "utility_gem_with_minor_quality",
                "gear_slot_about_to_be_replaced",
                "when_chromatic_or_non_white_socket_cost_blocks_life_resist_upgrade",
            ],
            "coach_rule": "Explain RGB as access friction down plus quality optimization up. Never tell a user they cannot use a gem because the colour is wrong in 3.29.",
        },
        "sample_evidence_lines": sample_evidence_lines,
    }


def main() -> int:
    payload = build_patch_history_context()
    _write_json(OUTPUT_PATH, payload)
    print(json.dumps({
        "output": str(OUTPUT_PATH.relative_to(ROOT)).replace("\\", "/"),
        "patch_count": payload["cumulative_summary"]["patch_count"],
        "bands": {
            row["patch_band"]: row["patch_count"]
            for row in payload["patch_band_summary"]
        },
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
