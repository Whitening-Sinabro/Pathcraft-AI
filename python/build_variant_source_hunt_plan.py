# -*- coding: utf-8 -*-
"""Build a source hunt plan for unresolved build verification targets."""

from __future__ import annotations

import json
from pathlib import Path

from build_variant_research_queue import build_research_queue

ROOT = Path(__file__).resolve().parent.parent
QUEUE_PATH = ROOT / "data" / "build_variant_collection_queue_v1.json"

SOURCE_DOMAIN_MAP = {
    "maxroll": "maxroll.gg",
    "poe_vault": "poe-vault.com",
    "forum_build_guide": "pathofexile.com/forum/view-thread",
    "reddit_build_index": "reddit.com/r/pathofexile",
    "icy_veins": "icy-veins.com",
    "youtube": "youtube.com",
    "pob_archives": "pobarchives.com",
    "creator_guide": "local guide source",
    "commercial_build_article": "commercial build article",
}
DEFAULT_FAMILY_PRIORITY = [
    "maxroll",
    "poe_vault",
    "forum_build_guide",
    "reddit_build_index",
    "icy_veins",
    "youtube",
    "pob_archives",
]
PATCH_KEYWORDS = {
    "3.22": ["league starter", "build index"],
    "3.23": ["league starter", "starter build"],
    "3.24": ["league starter", "build guide"],
    "3.25": ["league starter", "starter build"],
    "3.26": ["league starter", "starter build"],
    "3.27": ["league starter", "build guide"],
    "3.28": ["league starter", "build guide"],
}


def _load_json(path: Path) -> dict:
    with open(path, 'r', encoding='utf-8-sig') as f:
        return json.load(f)


def _candidate_label(candidate_id: str) -> str:
    _, _, remainder = candidate_id.partition('_')
    return remainder.replace('_', ' ')


def _title_label(candidate_id: str) -> str:
    tokens = _candidate_label(candidate_id).split()
    keep_lower = {"of", "and", "or"}
    titled = [token if token in keep_lower else token.capitalize() for token in tokens]
    return ' '.join(titled)


def _preferred_target_families(item: dict) -> list[str]:
    existing = set(item.get('guide_source_families', []))
    preferred = [family for family in DEFAULT_FAMILY_PRIORITY if family not in existing]
    if item['next_step'] == 'find_first_external_build_guide_source':
        return preferred
    return preferred


def _query_templates(candidate_id: str, patch: str, league_name: str, next_step: str) -> list[str]:
    label = _candidate_label(candidate_id)
    title_label = _title_label(candidate_id)
    keywords = PATCH_KEYWORDS.get(patch, ["build guide", "league starter"])
    queries = [
        f'"Path of Exile" "{title_label}" "{patch}" {keywords[0]}',
        f'"Path of Exile" "{title_label}" "{league_name}" {keywords[1]}',
        f'site:pathofexile.com/forum/view-thread "{title_label}" "Path of Exile"',
        f'site:reddit.com/r/pathofexile "{title_label}" "{patch}"',
        f'site:maxroll.gg "{title_label}" "Path of Exile"',
        f'site:poe-vault.com "{title_label}" "Path of Exile"',
        f'site:youtube.com "{title_label}" "{patch}" "PoB"',
        f'site:pobarchives.com "{title_label}" "{patch}"',
    ]
    if next_step == 'find_first_external_build_guide_source':
        queries.append(f'site:icy-veins.com "{title_label}" "Path of Exile"')
    else:
        queries.append(f'"{label}" "Path of Exile" guide')
    return queries


def _stop_condition(item: dict) -> str:
    existing = item.get('guide_source_families', [])
    if item['next_step'] == 'find_first_external_build_guide_source':
        return 'Add 1 external build guide family from maxroll, poe_vault, forum_build_guide, reddit_build_index, icy_veins, youtube, or pob_archives.'
    if existing:
        return f'Add 1 new external build guide family that is different from existing {", ".join(existing)}.'
    return 'Add 1 new external build guide family.'


def _acceptance_rules(item: dict) -> list[str]:
    rules = []
    if item['next_step'] == 'find_first_external_build_guide_source':
        rules.append('Patch-specific or league-era guide/post must explicitly name the skill/archetype or unmistakable variant.')
        rules.append('Do not accept official patch notes alone as meta confirmation.')
    else:
        rules.append('New source must come from a guide family not already counted for this candidate.')
        rules.append('Do not count local traces as the second external guide family.')
    rules.append('Source should be attributable to one of: maxroll, poe-vault, forum guide thread, reddit build index/discussion, icy-veins, YouTube guide, PoB Archives, or a local creator guide DB.')
    return rules


def build_source_hunt_plan() -> dict:
    queue = _load_json(QUEUE_PATH)
    research_queue = build_research_queue()
    league_name_by_patch = {item['patch']: item['league_name'] for item in queue['patches']}

    items = []
    for record in research_queue['items']:
        preferred_target_families = _preferred_target_families(record)
        preferred_domains = [SOURCE_DOMAIN_MAP[family] for family in preferred_target_families if family in SOURCE_DOMAIN_MAP]
        item = {
            'patch': record['patch'],
            'league_name': league_name_by_patch[record['patch']],
            'candidate_id': record['candidate_id'],
            'candidate_label': _title_label(record['candidate_id']),
            'archetype_id': record['archetype_id'],
            'priority_score': record['priority_score'],
            'strict_verdict': record['strict_verdict'],
            'next_step': record['next_step'],
            'existing_guide_source_families': record.get('guide_source_families', []),
            'missing_target_families': preferred_target_families,
            'preferred_domains': preferred_domains,
            'query_templates': _query_templates(record['candidate_id'], record['patch'], league_name_by_patch[record['patch']], record['next_step']),
            'acceptance_rules': _acceptance_rules(record),
            'stop_condition': _stop_condition(record),
            'blockers': record.get('blockers', []),
        }
        items.append(item)

    by_patch: dict[str, dict] = {}
    for item in items:
        by_patch.setdefault(item['patch'], {
            'patch': item['patch'],
            'league_name': item['league_name'],
            'item_count': 0,
            'top_candidates': [],
        })
        by_patch[item['patch']]['item_count'] += 1
        if len(by_patch[item['patch']]['top_candidates']) < 3:
            by_patch[item['patch']]['top_candidates'].append(item['candidate_id'])

    return {
        'dataset_kind': 'poe1_build_variant_source_hunt_plan',
        'item_count': len(items),
        'items': items,
        'by_patch': [by_patch[key] for key in sorted(by_patch.keys())],
    }


if __name__ == '__main__':
    print(json.dumps(build_source_hunt_plan(), ensure_ascii=False, indent=2))
