# -*- coding: utf-8 -*-
"""Freeze a representative build board for patches 3.22~3.28."""

from __future__ import annotations

import json
from pathlib import Path

from build_variant_verification_audit import build_verification_audit
from build_variant_site_index_probe import build_site_index_probe

ROOT = Path(__file__).resolve().parent.parent
QUEUE_PATH = ROOT / 'data' / 'build_variant_collection_queue_v1.json'
OUT_PATH = ROOT / 'data' / 'poe1_representative_build_board.latest.json'

STATUS_LABELS = {
    'confirmed': '확정',
    'near_confirmed': '준확정',
    'hold': '보류',
}
USE_POLICY = {
    'confirmed': 'safe_default',
    'near_confirmed': 'label_as_provisional_meta',
    'hold': 'do_not_default',
}
PATCH_FORWARD_GUARDS = {
    'hexblast_miner_saboteur': {
        'visibility': 'hold',
        'reason': 'post_3_26_hexblast_trigger_cooldown_guard',
        'note': (
            'Hexblast Mines from 3.23/3.25 cannot be carried forward as a '
            'default recommendation after the 3.26 Hexblast cooldown change; '
            '3.29 reduces the cooldown but still requires current PoB/live proof.'
        ),
    },
    'shockwave_totems_hierophant': {
        'visibility': 'practice_only',
        'reason': 'patch_3_29_spell_totem_and_totem_scaling_guard',
        'note': '3.29 directly changes Spell Totem penalty, Ritual of Awakening, Totem mastery, and Shaman\'s Dominion; old totem PoBs are practice-only until refreshed.',
    },
    'storm_burst_totems_hierophant': {
        'visibility': 'practice_only',
        'reason': 'patch_3_29_spell_totem_and_totem_scaling_guard',
        'note': '3.29 directly changes Spell Totem penalty, Ritual of Awakening, Totem mastery, and Shaman\'s Dominion; old totem PoBs are practice-only until refreshed.',
    },
    'siege_ballista_hierophant': {
        'visibility': 'practice_only',
        'reason': 'patch_3_29_ballista_totem_guard',
        'note': '3.29 increases Ballista Totem less-damage penalty; old ballista PoBs are practice-only until refreshed.',
    },
    'explosive_arrow_ballista_champion': {
        'visibility': 'practice_only',
        'reason': 'patch_3_29_ballista_totem_guard',
        'note': '3.29 increases Ballista Totem less-damage penalty; old Explosive Arrow Ballista PoBs are practice-only until refreshed.',
    },
    'pyroclast_mine_saboteur': {
        'visibility': 'practice_only',
        'reason': 'patch_3_29_mine_support_guard',
        'note': '3.29 changes Blastchain Mine, High-Impact Mine, and Charged Mines cost/damage/throw-speed values; old mine PoBs are practice-only until refreshed.',
    },
    'exsanguinate_mine_trickster': {
        'visibility': 'practice_only',
        'reason': 'patch_3_29_mine_support_guard',
        'note': '3.29 changes Blastchain Mine, High-Impact Mine, and Charged Mines cost/damage/throw-speed values; old mine PoBs are practice-only until refreshed.',
    },
}


def _load_json(path: Path) -> dict:
    with open(path, 'r', encoding='utf-8-sig') as f:
        return json.load(f)


def _title(candidate_id: str) -> str:
    _, _, remainder = candidate_id.partition('_')
    keep_lower = {'of', 'and', 'or'}
    parts = []
    for token in remainder.split('_'):
        parts.append(token if token in keep_lower else token.capitalize())
    return ' '.join(parts)


def build_representative_build_board() -> dict:
    queue = _load_json(QUEUE_PATH)
    verification = build_verification_audit()
    site_probe = build_site_index_probe()

    verification_index = {item['candidate_id']: item for item in verification['items']}
    site_probe_index = {item['candidate_id']: item for item in site_probe['items']}

    patches = []
    overall_counts = {'confirmed': 0, 'near_confirmed': 0, 'hold': 0}

    for patch_entry in queue['patches']:
        patch = patch_entry['patch']
        patch_rows = []
        for item in patch_entry['queue']:
            if item.get('candidate_role') != 'flagship':
                continue
            candidate_id = item['candidate_id']
            verification_row = verification_index[candidate_id]
            site_row = site_probe_index.get(candidate_id, {})
            upgradeable_families = site_row.get('upgradeable_families', [])
            guide_families = verification_row.get('guide_source_families', [])

            if verification_row['strict_confirmable'] or len(upgradeable_families) >= 2:
                status = 'confirmed'
            elif verification_row['standard_confirmable'] or len(guide_families) >= 1:
                status = 'near_confirmed'
            else:
                status = 'hold'

            rationale = []
            if verification_row['strict_confirmable']:
                rationale.append('strict_two_source_pass')
            elif len(upgradeable_families) >= 2:
                rationale.append('direct_index_two_family_match')
            elif verification_row['standard_confirmable']:
                rationale.append('one_external_plus_support')
            elif len(guide_families) >= 1:
                rationale.append('single_external_family_only')
            else:
                rationale.append('no_external_guide_confirmed')

            if verification_row['blockers']:
                rationale.extend(verification_row['blockers'])

            forward_guard = PATCH_FORWARD_GUARDS.get(verification_row['archetype_id'])
            player_facing_default = True
            recommendation_visibility = 'default'
            if forward_guard:
                player_facing_default = False
                recommendation_visibility = forward_guard['visibility']
                rationale.append(forward_guard['reason'])

            if forward_guard and forward_guard['visibility'] == 'hold':
                status = 'hold'
                recommendation_visibility = 'hold'

            row = {
                'candidate_id': candidate_id,
                'build_label': _title(candidate_id),
                'archetype_id': verification_row['archetype_id'],
                'status': status,
                'status_ko': STATUS_LABELS[status],
                'use_policy': USE_POLICY[status],
                'player_facing_default': player_facing_default,
                'recommendation_visibility': recommendation_visibility,
                'strict_verdict': verification_row['strict_verdict'],
                'guide_source_families': guide_families,
                'upgradeable_families': upgradeable_families,
                'rationale': rationale,
            }
            if forward_guard:
                row['forward_guard_note'] = forward_guard['note']
            patch_rows.append(row)
            overall_counts[status] += 1

        patches.append({
            'patch': patch,
            'league_name': patch_entry['league_name'],
            'rows': patch_rows,
            'counts': {
                'confirmed': sum(1 for row in patch_rows if row['status'] == 'confirmed'),
                'near_confirmed': sum(1 for row in patch_rows if row['status'] == 'near_confirmed'),
                'hold': sum(1 for row in patch_rows if row['status'] == 'hold'),
            },
        })

    return {
        'dataset_kind': 'poe1_representative_build_board',
        'overall_counts': overall_counts,
        'patches': patches,
    }


if __name__ == '__main__':
    data = build_representative_build_board()
    OUT_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(data['overall_counts'], ensure_ascii=False, indent=2))
