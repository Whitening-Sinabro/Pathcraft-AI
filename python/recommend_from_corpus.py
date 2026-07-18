# -*- coding: utf-8 -*-
"""Corpus-level recommendation runner for representative POE1 build profiles."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from build_extractor import extract_build_gems
from recommendation_backend_guard import (
    apply_recommendation_guard_to_corpus,
    is_player_facing_default_row,
)
from recommendation_engine import extract_main_skill, infer_input_style, recommend_profiles

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CORPUS_PATH = ROOT / 'data' / 'poe1_representative_build_profiles.latest.json'
DEFAULT_USER_STATE_PATH = ROOT / 'data' / 'user_state.example.json'
LEVEL_RE = re.compile(r'Lvl\s+(\d+)', re.IGNORECASE)
TRADE_MODE_BY_UI = {
    'sc': 'trade_league_start',
    'ssf': 'ssf',
    'hcssf': 'ssf',
}


def _load_json(path: Path) -> dict:
    with open(path, 'r', encoding='utf-8-sig') as f:
        return json.load(f)


def _candidate_meta(row: dict[str, Any]) -> dict[str, Any]:
    profile = row['build_profile']
    return {
        'candidate_id': row.get('candidate_id'),
        'league_name': row.get('league_name'),
        'board_status': row.get('board_status'),
        'use_policy': row.get('use_policy'),
        'source_confidence': row.get('source_confidence'),
        'build_id': profile.get('build_id'),
        'build_name': profile.get('identity', {}).get('build_name'),
        'main_skill': profile.get('identity', {}).get('main_skill'),
        'class_name': profile.get('identity', {}).get('class_name'),
        'ascendancy': profile.get('identity', {}).get('ascendancy'),
    }


def _compact_profile_for_recommendation(profile: dict[str, Any]) -> dict[str, Any]:
    progression = profile.get('progression', {}) if isinstance(profile, dict) else {}
    return {
        'build_id': profile.get('build_id'),
        'identity': profile.get('identity', {}),
        'playstyle': profile.get('playstyle', {}),
        'budget_curve': profile.get('budget_curve', {}),
        'availability': profile.get('availability', {}),
        'suitability': profile.get('suitability', {}),
        'constraints': {
            'banned_map_mods': profile.get('constraints', {}).get('banned_map_mods', []),
            'pain_points': profile.get('constraints', {}).get('pain_points', []),
        },
        'confidence': profile.get('confidence', {}),
        'progression': {
            'leveling_confidence': progression.get('leveling_confidence'),
            'early_mapping_ready': progression.get('early_mapping_ready'),
            'transition_points': (progression.get('transition_points') or [])[:4],
            'campaign_plan': (progression.get('campaign_plan') or [])[:5],
            'passive_plan': (progression.get('passive_plan') or [])[:4],
            'gear_stages': (progression.get('gear_stages') or [])[:4],
        },
        'evidence': (profile.get('evidence') or [])[:4],
    }


def _index_rows(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for row in rows:
        profile = row.get('build_profile', {})
        build_id = profile.get('build_id')
        if build_id:
            indexed[build_id] = row
    return indexed


def _attach_meta(result: dict[str, Any], row_index: dict[str, dict[str, Any]]) -> dict[str, Any]:
    def _profile_summary(build_id: str | None) -> dict[str, Any] | None:
        row = row_index.get(build_id or '')
        if not row:
            return None
        return _compact_profile_for_recommendation(row.get('build_profile', {}))

    def _merge(item: dict[str, Any], *, include_profile_summary: bool = False) -> dict[str, Any]:
        build_id = item.get('build_id')
        if build_id in row_index:
            merged = dict(_candidate_meta(row_index[build_id]))
            merged.update(item)
            if include_profile_summary:
                merged['profile_summary'] = _profile_summary(build_id)
            return merged
        return item

    result = dict(result)
    selected_profile = _profile_summary(result.get('selected_build_id'))
    if result.get('selected_build_id') in row_index:
        result['selected_candidate'] = _candidate_meta(row_index[result['selected_build_id']])
        result['selected_profile'] = selected_profile
    else:
        result['selected_profile'] = None
    if result.get('blocking_candidate'):
        result['blocking_candidate'] = _merge(result['blocking_candidate'])
        result['blocking_profile'] = _profile_summary(result['blocking_candidate'].get('build_id'))
    else:
        result['blocking_profile'] = None
    result['recommendations'] = [
        _merge(item, include_profile_summary=True)
        for item in result.get('recommendations', [])
    ]
    result['proxy_candidates'] = [
        _merge(item, include_profile_summary=True)
        for item in result.get('proxy_candidates', [])
    ]
    result['rejections'] = [_merge(item) for item in result.get('rejections', [])]
    return result


def _desired_skill(user_state: dict) -> str | None:
    constraints = user_state.get('constraints', {})
    preferences = user_state.get('preferences', {})
    return constraints.get('must_use_skill') or preferences.get('desired_main_skill')


def _rows_with_exact_skill(rows: list[dict[str, Any]], desired_skill: str | None) -> list[dict[str, Any]]:
    if not desired_skill:
        return []
    return [
        row for row in rows
        if row.get('build_profile', {}).get('identity', {}).get('main_skill') == desired_skill
    ]


def _normalize_patch(version: str | None) -> str:
    text = str(version or '').strip()
    if not text:
        return 'unknown'
    if '_' in text and text.replace('_', '').isdigit():
        return text.replace('_', '.')
    return text


def _infer_level(build_data: dict) -> int:
    meta = build_data.get('meta', {})
    match = LEVEL_RE.search(str(meta.get('build_name', '')))
    if match:
        return int(match.group(1))
    return 90


def build_user_state_from_build_data(
    build_data: dict,
    *,
    mode: str = 'sc',
    liquid_divines: float = 3.0,
) -> dict:
    meta = build_data.get('meta', {})
    skills, supports = extract_build_gems(build_data)
    main_skill = extract_main_skill(build_data)
    input_style, _manual_buttons = infer_input_style(main_skill, skills, supports, None)
    return {
        'schema_version': '1.0.0',
        'dataset_kind': 'poe1_user_state',
        'character_state': {
            'patch': _normalize_patch(meta.get('version')),
            'class_name': meta.get('class', 'Unknown'),
            'ascendancy': meta.get('ascendancy', 'Unknown'),
            'level': _infer_level(build_data),
            'character_locked': True,
        },
        'currency_state': {
            'liquid_divines': liquid_divines,
            'liquid_chaos': 0.0,
            'owned_uniques': [],
            'can_self_link_5l': False,
            'can_self_craft_basic_rares': True,
        },
        'preferences': {
            'desired_main_skill': main_skill,
            'max_input_style': input_style,
            'target_contents': ['mapping'],
            'trade_mode': TRADE_MODE_BY_UI.get(mode, 'trade_league_start'),
            'death_tolerance': 'medium',
            'respec_tolerance_points': 24,
        },
        'constraints': {
            'must_use_skill': main_skill,
            'forbidden_skills': [],
            'require_confirmed_leveling': False,
            'forbid_reroll': True,
        },
    }


def recommend_from_profile_corpus(
    user_state: dict,
    *,
    corpus_path: Path | None = None,
    allow_hold_fallback: bool = True,
) -> dict:
    corpus = _load_json(corpus_path or DEFAULT_CORPUS_PATH)
    corpus = apply_recommendation_guard_to_corpus(corpus)
    rows = corpus.get('profiles', [])
    preferred_rows = [row for row in rows if is_player_facing_default_row(row)]
    preferred_profiles = [row['build_profile'] for row in preferred_rows]

    recommendation = recommend_profiles(preferred_profiles, user_state)
    active_rows = preferred_rows
    active_scope = 'default_non_hold'

    desired_skill = _desired_skill(user_state)
    default_exact_rows = _rows_with_exact_skill(preferred_rows, desired_skill)
    hold_exact_rows = _rows_with_exact_skill(
        [row for row in rows if row.get('use_policy') == 'do_not_default'],
        desired_skill,
    )
    should_try_hold = (
        allow_hold_fallback
        and bool(hold_exact_rows)
        and not default_exact_rows
        and recommendation.get('selected_plan') in {'C', 'D'}
    )

    if should_try_hold:
        preferred_ids = {
            row.get('build_profile', {}).get('build_id')
            for row in preferred_rows
        }
        hold_rows = [
            row for row in rows
            if row.get('use_policy') == 'do_not_default'
            and row.get('build_profile', {}).get('build_id') not in preferred_ids
        ]
        fallback_rows = preferred_rows + hold_rows
        fallback_profiles = [row['build_profile'] for row in fallback_rows]
        fallback_recommendation = recommend_profiles(fallback_profiles, user_state)
        selected_id = fallback_recommendation.get('selected_build_id')
        hold_exact_ids = {row['build_profile'].get('build_id') for row in hold_exact_rows}
        if fallback_recommendation.get('selected_plan') in {'A', 'B', 'C'} and selected_id in hold_exact_ids:
            recommendation = fallback_recommendation
            active_rows = fallback_rows
            active_scope = 'fallback_with_hold'

    row_index = _index_rows(active_rows)
    recommendation = _attach_meta(recommendation, row_index)

    return {
        'dataset_kind': 'poe1_representative_corpus_recommendation',
        'corpus_summary': corpus.get('summary', {}),
        'active_scope': active_scope,
        'candidate_pool_size': len(active_rows),
        'recommendation': recommendation,
    }


def build_corpus_recommendation_result(
    *,
    user_state_path: str | None = None,
    build_json_path: str | None = None,
    corpus_path: str | None = None,
    mode: str = 'sc',
    liquid_divines: float = 3.0,
    allow_hold_fallback: bool = True,
) -> dict:
    if bool(user_state_path) == bool(build_json_path):
        raise ValueError('Provide exactly one of --user-state or --build-json')

    if user_state_path:
        user_state = _load_json(Path(user_state_path))
    else:
        build_data = _load_json(Path(build_json_path))
        user_state = build_user_state_from_build_data(
            build_data,
            mode=mode,
            liquid_divines=liquid_divines,
        )

    return recommend_from_profile_corpus(
        user_state,
        corpus_path=Path(corpus_path) if corpus_path else None,
        allow_hold_fallback=allow_hold_fallback,
    )


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Recommend from representative POE1 build profile corpus.')
    parser.add_argument('--user-state', help='User state JSON path.')
    parser.add_argument('--build-json', help='Parsed build_data JSON path used to derive a user_state.')
    parser.add_argument('--mode', default='sc', choices=['sc', 'ssf', 'hcssf'], help='League mode when deriving user state from build_json.')
    parser.add_argument('--liquid-divines', type=float, default=3.0, help='Liquid divines when deriving user state from build_json.')
    parser.add_argument('--corpus', default=str(DEFAULT_CORPUS_PATH), help='Representative build profile corpus JSON path.')
    parser.add_argument('--no-hold-fallback', action='store_true', help='Disable fallback that includes hold-status profiles.')
    return parser.parse_args()


if __name__ == '__main__':
    args = _parse_args()
    user_state_path = args.user_state or (str(DEFAULT_USER_STATE_PATH) if not args.build_json else None)
    result = build_corpus_recommendation_result(
        user_state_path=user_state_path,
        build_json_path=args.build_json,
        corpus_path=args.corpus,
        mode=args.mode,
        liquid_divines=args.liquid_divines,
        allow_hold_fallback=not args.no_hold_fallback,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
