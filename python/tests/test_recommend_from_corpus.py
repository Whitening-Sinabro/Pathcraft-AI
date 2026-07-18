# -*- coding: utf-8 -*-
"""Regression tests for representative corpus recommendation runner."""

from __future__ import annotations

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from build_representative_build_profiles import build_representative_build_profiles  # noqa: E402
from recommend_from_corpus import (  # noqa: E402
    build_user_state_from_build_data,
    recommend_from_profile_corpus,
)
from recommendation_backend_guard import apply_recommendation_guard_to_corpus  # noqa: E402


def _make_user_state(
    *,
    patch: str = '3.25',
    class_name: str = 'Ranger',
    ascendancy: str = 'Deadeye',
    desired_skill: str = 'Lightning Arrow',
    max_input_style: str = '1_click_plus_movement',
    liquid_divines: float = 3.2,
    trade_mode: str = 'trade_league_start',
    character_locked: bool = True,
) -> dict:
    return {
        'character_state': {
            'patch': patch,
            'class_name': class_name,
            'ascendancy': ascendancy,
            'level': 71,
            'character_locked': character_locked,
        },
        'currency_state': {
            'liquid_divines': liquid_divines,
            'liquid_chaos': 180.0,
            'owned_uniques': [],
        },
        'preferences': {
            'desired_main_skill': desired_skill,
            'max_input_style': max_input_style,
            'target_contents': ['mapping', 'expedition'],
            'trade_mode': trade_mode,
            'death_tolerance': 'medium',
            'respec_tolerance_points': 30,
        },
        'constraints': {
            'must_use_skill': desired_skill,
            'forbidden_skills': [],
            'require_confirmed_leveling': False,
            'forbid_reroll': True,
        },
    }


def _make_build_data() -> dict:
    return {
        'meta': {
            'build_name': 'Ranger Deadeye Lvl 90',
            'class': 'Ranger',
            'ascendancy': 'Deadeye',
            'version': '3.25',
        },
        'stats': {
            'dps': 4000000,
            'life': 4300,
            'energy_shield': 0,
        },
        'progression_stages': [{
            'gem_setups': {
                'Main Clear': {'links': 'Lightning Arrow - Trinity Support - Inspiration Support'},
            },
            'alternate_gem_sets': {
                'Leveling': {
                    'Act Leveling': {'links': 'Rain of Arrows - Mirage Archer Support'},
                },
            },
        }],
    }


def test_build_user_state_from_build_data_uses_current_character_and_skill():
    user_state = build_user_state_from_build_data(_make_build_data(), mode='sc', liquid_divines=4.5)

    assert user_state['character_state']['patch'] == '3.25'
    assert user_state['character_state']['class_name'] == 'Ranger'
    assert user_state['character_state']['ascendancy'] == 'Deadeye'
    assert user_state['character_state']['level'] == 90
    assert user_state['preferences']['desired_main_skill'] == 'Lightning Arrow'
    assert user_state['preferences']['max_input_style'] == '1_click_plus_movement'
    assert user_state['preferences']['trade_mode'] == 'trade_league_start'
    assert user_state['currency_state']['liquid_divines'] == 4.5


def test_corpus_recommendation_picks_lightning_arrow_deadeye_for_sample_ranger():
    result = recommend_from_profile_corpus(_make_user_state())
    recommendation = result['recommendation']

    assert result['dataset_kind'] == 'poe1_representative_corpus_recommendation'
    assert result['active_scope'] == 'default_non_hold'
    assert recommendation['selected_plan'] == 'A'
    assert recommendation['selected_candidate']['candidate_id'] == '3.25_lightning_arrow_ranger'
    assert recommendation['selected_candidate']['board_status'] == 'confirmed'
    assert recommendation['selected_profile']['identity']['main_skill'] == 'Lightning Arrow'
    assert recommendation['selected_profile']['progression']['campaign_plan']
    assert recommendation['recommendations'][0]['profile_summary']['identity']['main_skill'] == 'Lightning Arrow'
    assert recommendation['deterministic_guards']
    assert recommendation['guardrails']['ai_policy']['mode'] == 'explain_only'
    assert recommendation['response_layers']['user_message']['template_id'] == 'plan_a_exact'
    assert recommendation['verification_loop']['recommended_plan'] == 'A'


def test_corpus_recommendation_blocks_practice_only_328_exsanguinate_miner_from_default(tmp_path):
    corpus_path = tmp_path / 'representative_profiles.json'
    corpus_path.write_text(
        json.dumps(build_representative_build_profiles(), ensure_ascii=False, indent=2) + '\n',
        encoding='utf-8',
    )
    user_state = _make_user_state(
        patch='3.28',
        class_name='Shadow',
        ascendancy='Trickster',
        desired_skill='Exsanguinate Mine',
        max_input_style='2_button',
        liquid_divines=3.0,
        trade_mode='trade_league_start',
        character_locked=True,
    )
    user_state['constraints']['require_confirmed_leveling'] = True

    raw_corpus = build_representative_build_profiles()
    guarded = apply_recommendation_guard_to_corpus(raw_corpus)
    result = recommend_from_profile_corpus(user_state, corpus_path=corpus_path)
    recommendation = result['recommendation']

    blocked_ids = set(guarded['backend_guard_summary']['blocked_candidate_ids'])
    assert result['active_scope'] == 'default_non_hold'
    assert 'backend_guard_summary' not in result
    assert '3.28_exsanguinate_reap_mines_trickster' in blocked_ids
    assert recommendation['selected_plan'] != 'A'
    assert (recommendation.get('selected_candidate') or {}).get('candidate_id') != (
        '3.28_exsanguinate_reap_mines_trickster'
    )
    assert all(
        item.get('candidate_id') != '3.28_exsanguinate_reap_mines_trickster'
        for item in recommendation.get('recommendations', [])
    )
    assert all(
        item.get('candidate_id') != '3.28_exsanguinate_reap_mines_trickster'
        for item in recommendation.get('proxy_candidates', [])
    )


def test_corpus_recommendation_result_does_not_expose_internal_backend_guard_keys():
    result = recommend_from_profile_corpus(_make_user_state())
    serialized = json.dumps(result, ensure_ascii=False)

    assert 'backend_guard' not in serialized
    assert 'backend_guard_summary' not in serialized
    assert 'player_facing_default' not in serialized
    assert 'recommendation_visibility' not in serialized
    assert 'forward_guard_note' not in serialized


def test_corpus_recommendation_can_fall_back_to_hold_profile_for_exact_hold_skill():
    user_state = _make_user_state(
        patch='3.28',
        class_name='Shadow',
        ascendancy='Trickster',
        desired_skill='Kinetic Fusillade of Detonation',
        max_input_style='1_click_plus_movement',
        liquid_divines=40.0,
        trade_mode='twink',
        character_locked=False,
    )

    result = recommend_from_profile_corpus(user_state)
    recommendation = result['recommendation']

    assert result['active_scope'] == 'fallback_with_hold'
    assert recommendation['selected_plan'] == 'B'
    assert recommendation['selected_candidate']['candidate_id'] == '3.28_kinetic_fusillade_of_detonation'
    assert recommendation['selected_candidate']['board_status'] == 'hold'
    assert recommendation['selected_profile']['identity']['main_skill'] == 'Kinetic Fusillade of Detonation'
    assert recommendation['ai_policy']['mode'] == 'verification_only'
    assert recommendation['response_layers']['user_message']['template_id'] == 'plan_b_hold_exact'
    assert recommendation['verification_loop']['recommended_plan'] == recommendation['selected_plan']


def test_no_hold_fallback_abstains_when_hold_only_exact_skill_has_no_in_place_proxy():
    user_state = _make_user_state(
        patch='3.28',
        class_name='Shadow',
        ascendancy='Trickster',
        desired_skill='Kinetic Fusillade of Detonation',
        max_input_style='1_click_plus_movement',
        liquid_divines=40.0,
        trade_mode='twink',
        character_locked=False,
    )

    result = recommend_from_profile_corpus(user_state, allow_hold_fallback=False)
    recommendation = result['recommendation']

    assert result['active_scope'] == 'default_non_hold'
    assert recommendation['selected_plan'] == 'D'
    assert recommendation['ai_policy']['mode'] == 'disabled'
    assert recommendation['response_layers']['user_message']['template_id'] == 'plan_d_proxy_scope_block'
    assert recommendation['blocking_candidate'] is not None


def test_patch_mismatch_case_abstains_with_plan_d_and_patch_template():
    user_state = _make_user_state(
        patch='3.27',
        class_name='Templar',
        ascendancy='Hierophant',
        desired_skill='Shock Nova of Procession',
        max_input_style='1_click_plus_movement',
        liquid_divines=40.0,
        trade_mode='twink',
        character_locked=True,
    )

    result = recommend_from_profile_corpus(user_state, allow_hold_fallback=False)
    recommendation = result['recommendation']

    assert result['active_scope'] == 'default_non_hold'
    assert recommendation['selected_plan'] == 'D'
    assert recommendation['ai_policy']['mode'] == 'disabled'
    assert recommendation['response_layers']['user_message']['template_id'] == 'plan_d_patch_block'
    assert recommendation['verification_loop']['loop_state'] == 'abstain'
    assert recommendation['blocking_candidate']['candidate_id'] == '3.28_shock_nova_of_procession_hierophant'
    assert recommendation['selected_profile'] is None
    assert recommendation['blocking_profile']['identity']['main_skill'] == 'Shock Nova of Procession'


def test_underfunded_exact_case_abstains_with_plan_d_and_budget_template():
    user_state = _make_user_state(
        patch='3.28',
        class_name='Templar',
        ascendancy='Hierophant',
        desired_skill='Shock Nova of Procession',
        max_input_style='1_click_plus_movement',
        liquid_divines=0.2,
        trade_mode='twink',
        character_locked=True,
    )

    result = recommend_from_profile_corpus(user_state, allow_hold_fallback=True)
    recommendation = result['recommendation']

    assert recommendation['selected_plan'] == 'D'
    assert recommendation['ai_policy']['mode'] == 'disabled'
    assert recommendation['response_layers']['user_message']['template_id'] == 'plan_d_budget_block'
    assert recommendation['verification_loop']['loop_state'] == 'abstain'
    assert recommendation['blocking_candidate']['candidate_id'] == '3.28_shock_nova_of_procession_hierophant'


def test_cross_class_skill_mismatch_surfaces_proxy_scope_block():
    user_state = _make_user_state(
        patch='3.28',
        class_name='Shadow',
        ascendancy='Trickster',
        desired_skill='Ball Lightning',
        max_input_style='1_click_plus_movement',
        liquid_divines=40.0,
        trade_mode='twink',
        character_locked=False,
    )

    result = recommend_from_profile_corpus(user_state, allow_hold_fallback=False)
    recommendation = result['recommendation']

    assert recommendation['selected_plan'] == 'D'
    assert recommendation['ai_policy']['mode'] == 'disabled'
    assert recommendation['response_layers']['user_message']['template_id'] == 'plan_d_proxy_scope_block'
    assert recommendation['blocking_candidate'] is not None
