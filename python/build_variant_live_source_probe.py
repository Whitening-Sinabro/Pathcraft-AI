# -*- coding: utf-8 -*-
"""Probe live search results for candidate build source families."""

from __future__ import annotations

import json
import urllib.parse
import xml.etree.ElementTree as ET
from pathlib import Path

import requests

from build_variant_source_hunt_plan import build_source_hunt_plan

ROOT = Path(__file__).resolve().parent.parent
OUT_PATH = ROOT / 'data' / 'build_variant_live_source_probe.latest.json'
BING_RSS = 'https://www.bing.com/search?format=rss&q='
HEADERS = {'User-Agent': 'Mozilla/5.0'}
DOMAIN_FAMILY_MAP = {
    'maxroll.gg': 'maxroll',
    'poe-vault.com': 'poe_vault',
    'pathofexile.com': 'forum_build_guide',
    'reddit.com': 'reddit_build_index',
    'icy-veins.com': 'icy_veins',
    'youtube.com': 'youtube',
    'youtu.be': 'youtube',
    'pobarchives.com': 'pob_archives',
}
IGNORED_TERMS = {
    'of', 'the', 'and', 'or', 'path', 'exile', 'build', 'guide', 'league', 'starter',
    'hierophant', 'inquisitor', 'guardian', 'saboteur', 'juggernaut', 'trickster',
    'pathfinder', 'deadeye', 'duelist', 'ranger', 'caster', 'champion', 'templar',
}


def infer_family(url: str) -> str | None:
    lowered = url.lower()
    for domain, family in DOMAIN_FAMILY_MAP.items():
        if domain in lowered:
            return family
    return None


def parse_bing_rss(xml_text: str) -> list[dict]:
    root = ET.fromstring(xml_text)
    items = []
    for item in root.findall('./channel/item'):
        title = item.findtext('title') or ''
        link = item.findtext('link') or ''
        description = item.findtext('description') or ''
        items.append({
            'title': title.strip(),
            'url': link.strip(),
            'description': ' '.join(description.split()),
        })
    return items


def build_candidate_terms(candidate_id: str) -> list[str]:
    _, _, remainder = candidate_id.partition('_')
    tokens = []
    for token in remainder.split('_'):
        lowered = token.lower()
        if lowered.isdigit() or lowered in IGNORED_TERMS:
            continue
        if len(lowered) < 4:
            continue
        tokens.append(lowered)
    return tokens


def is_relevant_result(candidate_id: str, title: str, url: str, description: str) -> bool:
    haystack = f'{title} {url} {description}'.lower()
    terms = build_candidate_terms(candidate_id)
    if not terms:
        return False
    phrase = ' '.join(terms)
    if phrase and phrase in haystack:
        return True
    hits = sum(1 for term in terms if term in haystack)
    return hits >= min(2, len(terms))


def fetch_query_results(session: requests.Session, query: str) -> list[dict]:
    url = BING_RSS + urllib.parse.quote(query)
    response = session.get(url, timeout=20, headers=HEADERS)
    response.raise_for_status()
    return parse_bing_rss(response.text)


def build_live_source_probe(limit: int | None = None) -> dict:
    plan = build_source_hunt_plan()
    session = requests.Session()
    session.trust_env = False

    selected_items = plan['items'] if limit is None else plan['items'][:limit]
    items = []

    for entry in selected_items:
        existing = set(entry.get('existing_guide_source_families', []))
        seen_urls: set[str] = set()
        harvested = []
        discovered_new_families = []

        for query in entry['query_templates'][:7]:
            try:
                results = fetch_query_results(session, query)
            except Exception as exc:
                harvested.append({
                    'query': query,
                    'error': f'{type(exc).__name__}: {exc}',
                    'results': [],
                })
                continue

            normalized_results = []
            for result in results[:8]:
                url = result['url']
                if not url or url in seen_urls:
                    continue
                seen_urls.add(url)
                family = infer_family(url)
                relevant = is_relevant_result(entry['candidate_id'], result['title'], url, result['description'])
                row = {
                    'title': result['title'],
                    'url': url,
                    'family': family,
                    'description': result['description'],
                    'relevant': relevant,
                }
                normalized_results.append(row)
                if relevant and family and family not in existing and family not in discovered_new_families:
                    discovered_new_families.append(family)

            harvested.append({
                'query': query,
                'results': normalized_results,
            })

        if entry['next_step'] == 'find_first_external_build_guide_source':
            probe_status = 'new_external_family_found' if discovered_new_families else 'no_external_family_found'
        else:
            probe_status = 'strict_upgrade_path_found' if discovered_new_families else 'no_new_family_found'

        items.append({
            'patch': entry['patch'],
            'candidate_id': entry['candidate_id'],
            'next_step': entry['next_step'],
            'existing_guide_source_families': sorted(existing),
            'discovered_new_families': discovered_new_families,
            'probe_status': probe_status,
            'queries': harvested,
        })

    summary = {
        'candidate_count': len(items),
        'new_external_family_found_count': sum(1 for item in items if item['probe_status'] in {'new_external_family_found', 'strict_upgrade_path_found'}),
        'no_external_family_found_count': sum(1 for item in items if item['probe_status'] in {'no_external_family_found', 'no_new_family_found'}),
    }

    by_candidate = [
        {
            'candidate_id': item['candidate_id'],
            'probe_status': item['probe_status'],
            'discovered_new_families': item['discovered_new_families'],
        }
        for item in items
    ]

    return {
        'dataset_kind': 'poe1_build_variant_live_source_probe',
        'summary': summary,
        'items': items,
        'by_candidate': by_candidate,
    }


if __name__ == '__main__':
    data = build_live_source_probe()
    OUT_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(data['summary'], ensure_ascii=False, indent=2))
