# -*- coding: utf-8 -*-
"""Build a two-lane research strategy for strict verification progress."""

from __future__ import annotations

import json
from pathlib import Path

from build_variant_research_queue import build_research_queue

ROOT = Path(__file__).resolve().parent.parent
PATCH_ORDER = ["3.22", "3.23", "3.24", "3.25", "3.26", "3.27", "3.28"]
PATCH_RANK = {patch: index for index, patch in enumerate(PATCH_ORDER, start=1)}


def build_research_strategy() -> dict:
    queue = build_research_queue()

    foundation_lane = []
    conversion_lane = []

    for item in queue['items']:
        guide_family_count = len(item.get('guide_source_families', []))
        min_hits_to_strict = max(0, 2 - guide_family_count)
        strategy_item = {
            'patch': item['patch'],
            'candidate_id': item['candidate_id'],
            'case_id': item['case_id'],
            'archetype_id': item['archetype_id'],
            'strict_verdict': item['strict_verdict'],
            'next_step': item['next_step'],
            'priority_score': item['priority_score'],
            'guide_family_count': guide_family_count,
            'min_hits_to_strict': min_hits_to_strict,
            'patch_strict_confirmable_count': item['patch_strict_confirmable_count'],
            'patch_strict_gap_count': item['patch_strict_gap_count'],
            'blockers': item['blockers'],
        }
        if min_hits_to_strict <= 1:
            strategy_item['lane'] = 'conversion_lane'
            conversion_lane.append(strategy_item)
        else:
            strategy_item['lane'] = 'foundation_lane'
            foundation_lane.append(strategy_item)

    foundation_lane.sort(key=lambda item: (-item['priority_score'], -PATCH_RANK[item['patch']], item['candidate_id']))
    conversion_lane.sort(
        key=lambda item: (
            item['patch_strict_confirmable_count'],
            -item['priority_score'],
            -PATCH_RANK[item['patch']],
            item['candidate_id'],
        )
    )

    by_patch: dict[str, dict] = {}
    for item in foundation_lane + conversion_lane:
        by_patch.setdefault(item['patch'], {
            'patch': item['patch'],
            'foundation_count': 0,
            'conversion_count': 0,
            'top_foundation_candidates': [],
            'top_conversion_candidates': [],
        })
        if item['lane'] == 'foundation_lane':
            by_patch[item['patch']]['foundation_count'] += 1
            if len(by_patch[item['patch']]['top_foundation_candidates']) < 3:
                by_patch[item['patch']]['top_foundation_candidates'].append(item['candidate_id'])
        else:
            by_patch[item['patch']]['conversion_count'] += 1
            if len(by_patch[item['patch']]['top_conversion_candidates']) < 3:
                by_patch[item['patch']]['top_conversion_candidates'].append(item['candidate_id'])

    return {
        'dataset_kind': 'poe1_build_variant_research_strategy',
        'foundation_lane_count': len(foundation_lane),
        'conversion_lane_count': len(conversion_lane),
        'foundation_lane': foundation_lane,
        'conversion_lane': conversion_lane,
        'by_patch': [by_patch[key] for key in sorted(by_patch.keys())],
    }


if __name__ == '__main__':
    print(json.dumps(build_research_strategy(), ensure_ascii=False, indent=2))
