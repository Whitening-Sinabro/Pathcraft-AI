# -*- coding: utf-8 -*-
"""Probe direct build index pages on Maxroll and PoE Vault for candidate mentions."""

from __future__ import annotations

import json
from pathlib import Path

import requests

from build_variant_research_strategy import build_research_strategy

ROOT = Path(__file__).resolve().parent.parent
OUT_PATH = ROOT / 'data' / 'build_variant_site_index_probe.latest.json'
HEADERS = {'User-Agent': 'Mozilla/5.0'}
SITE_PAGES = [
    {
        'family': 'maxroll',
        'label': 'maxroll_league_starter_index',
        'url': 'https://maxroll.gg/poe/category/build-guides/league-starter',
    },
    {
        'family': 'maxroll',
        'label': 'maxroll_build_guides_index',
        'url': 'https://maxroll.gg/poe/category/build-guides',
    },
    {
        'family': 'poe_vault',
        'label': 'poe_vault_builds_index',
        'url': 'https://www.poe-vault.com/guides/builds-for-path-of-exile',
    },
]
LEAGUE_NAME_BY_PATCH = {
    '3.22': 'trial of the ancestors',
    '3.23': 'affliction',
    '3.24': 'necropolis',
    '3.25': 'settlers of kalguur',
    '3.26': 'secrets of the atlas',
    '3.27': 'keepers of the flame',
    '3.28': 'mirage',
}
ASCENDANCY_TERMS = {
    'hierophant', 'inquisitor', 'guardian', 'saboteur', 'juggernaut', 'trickster',
    'pathfinder', 'deadeye', 'elementalist', 'occultist', 'gladiator', 'slayer',
    'champion', 'warden'
}
ALIAS_OVERRIDES = {
    '3.28_kinetic_fusillade_of_detonation': ['kinetic fusillade', 'fusillade of detonation'],
    '3.28_penance_brand_inquisitor': ['penance brand'],
    '3.27_ice_nova_caster': ['ice nova'],
    '3.26_ball_lightning_caster': ['ball lightning'],
    '3.26_ice_nova_caster': ['ice nova'],
    '3.28_cold_snap_of_power_hierophant': ['cold snap of power', 'cold snap'],
    '3.27_pyroclast_mine_saboteur': ['pyroclast mine', 'pyroclast'],
    '3.26_boneshatter_juggernaut': ['boneshatter'],
    '3.26_siege_ballista_hierophant': ['siege ballista'],
    '3.22_shockwave_totems_hierophant': ['shockwave totems', 'shockwave totem'],
    '3.23_shockwave_totems_hierophant': ['shockwave totems', 'shockwave totem'],
    '3.24_exsanguinate_mine_trickster': ['exsanguinate mine', 'exsanguinate'],
    '3.27_dominating_blow_guardian': ['dominating blow'],
    '3.27_lacerate_duelist': ['lacerate'],
    '3.27_toxic_rain_pathfinder': ['toxic rain'],
    '3.28_dominating_blow_guardian': ['dominating blow'],
    '3.28_shock_nova_of_procession_hierophant': ['shock nova of procession', 'shock nova'],
    '3.26_lightning_arrow_ranger': ['lightning arrow'],
    '3.22_toxic_rain_ranger': ['toxic rain'],
}


def fetch_pages() -> list[dict]:
    session = requests.Session()
    session.trust_env = False
    pages = []
    for page in SITE_PAGES:
        response = session.get(page['url'], timeout=20, headers=HEADERS)
        response.raise_for_status()
        pages.append({
            **page,
            'text': response.text,
            'text_lower': response.text.lower(),
        })
    return pages


def candidate_aliases(candidate_id: str) -> list[str]:
    aliases = list(ALIAS_OVERRIDES.get(candidate_id, []))
    if aliases:
        return aliases
    _, _, remainder = candidate_id.partition('_')
    parts = [part for part in remainder.split('_') if part not in {'hierophant', 'inquisitor', 'guardian', 'saboteur', 'juggernaut', 'trickster', 'pathfinder', 'deadeye', 'duelist', 'ranger', 'caster'}]
    if parts:
        aliases.append(' '.join(parts[:2]))
        aliases.append(' '.join(parts))
    return [alias for alias in aliases if alias]


def classify_temporal_match(patch: str, page_text_lower: str, snippet_lower: str) -> str:
    patch_marker = patch.lower()
    league_marker = LEAGUE_NAME_BY_PATCH.get(patch, '').lower()
    if patch == '3.28' and ((patch_marker in page_text_lower) or (league_marker and league_marker in page_text_lower)):
        return 'current_patch_compatible'
    if patch_marker in snippet_lower or (league_marker and league_marker in snippet_lower):
        return 'historical_patch_compatible'
    return 'family_presence_only'


def classify_archetype_match(candidate_id: str, archetype_id: str, snippet_lower: str) -> str:
    required_asc = [term for term in ASCENDANCY_TERMS if term in candidate_id or term in archetype_id]
    found_asc = [term for term in ASCENDANCY_TERMS if term in snippet_lower]
    if required_asc and not any(term in snippet_lower for term in required_asc):
        return 'class_mismatch'
    if required_asc and found_asc and not any(term in required_asc for term in found_asc):
        return 'class_mismatch'
    if 'wander' in archetype_id and 'ballista' in snippet_lower:
        return 'delivery_mismatch'
    if 'ballista' in archetype_id and 'ballista' not in snippet_lower:
        return 'delivery_mismatch'
    if 'mine' in archetype_id and not any(term in snippet_lower for term in ['mine', 'miner']):
        return 'delivery_mismatch'
    return 'compatible'


def build_site_index_probe() -> dict:
    strategy = build_research_strategy()
    pages = fetch_pages()
    items = []

    for lane_name in ['foundation_lane', 'conversion_lane']:
        for entry in strategy[lane_name]:
            matches = []
            aliases = candidate_aliases(entry['candidate_id'])
            for page in pages:
                for alias in aliases:
                    idx = page['text_lower'].find(alias.lower())
                    if idx == -1:
                        continue
                    snippet = page['text'][max(0, idx - 80): idx + 160]
                    snippet = ' '.join(snippet.split())
                    temporal_classification = classify_temporal_match(entry['patch'], page['text_lower'], snippet.lower())
                    archetype_classification = classify_archetype_match(entry['candidate_id'], entry['archetype_id'], snippet.lower())
                    matches.append({
                        'family': page['family'],
                        'page_label': page['label'],
                        'url': page['url'],
                        'alias': alias,
                        'snippet': snippet,
                        'temporal_classification': temporal_classification,
                        'archetype_classification': archetype_classification,
                    })
                    break
            discovered_families = sorted({match['family'] for match in matches})
            upgradeable_families = sorted({
                match['family'] for match in matches
                if match['temporal_classification'] != 'family_presence_only' and match['archetype_classification'] == 'compatible'
            })
            items.append({
                'patch': entry['patch'],
                'candidate_id': entry['candidate_id'],
                'lane': lane_name,
                'aliases': aliases,
                'discovered_families': discovered_families,
                'upgradeable_families': upgradeable_families,
                'match_count': len(matches),
                'matches': matches,
            })

    summary = {
        'candidate_count': len(items),
        'candidate_with_any_match_count': sum(1 for item in items if item['match_count'] > 0),
        'candidate_with_maxroll_match_count': sum(1 for item in items if 'maxroll' in item['discovered_families']),
        'candidate_with_poe_vault_match_count': sum(1 for item in items if 'poe_vault' in item['discovered_families']),
        'candidate_with_upgradeable_match_count': sum(1 for item in items if item['upgradeable_families']),
    }

    return {
        'dataset_kind': 'poe1_build_variant_site_index_probe',
        'summary': summary,
        'items': items,
    }


if __name__ == '__main__':
    data = build_site_index_probe()
    OUT_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(data['summary'], ensure_ascii=False, indent=2))
