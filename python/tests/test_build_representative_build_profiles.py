# -*- coding: utf-8 -*-
"""Regression tests for representative build profile assembly."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from build_representative_build_profiles import build_representative_build_profiles  # noqa: E402
from recommendation_contract_audit import audit_build_profile  # noqa: E402


# 이미 확보해 하위 테스트들이 의존하는 대표 빌드 후보들. board/supplemental 는
# append-only 라 총계를 숫자로 고정하면 후보 추가마다 깨지고, 삭제·추가가 상쇄되면
# 탐지도 못 한다. 총계는 하한만 두고, 이 후보들이 조용히 사라지는지로 검증한다.
REQUIRED_CANDIDATE_IDS = {
    '3.22_shockwave_totems_hierophant',
    '3.23_hexblast_miner_saboteur',
    '3.24_explosive_arrow_ballista_champion',
    '3.24_exsanguinate_mine_trickster',
    '3.25_hexblast_miner_saboteur',
    '3.25_lightning_arrow_ranger',
    '3.26_siege_ballista_hierophant',
    '3.27_pyroclast_mine_saboteur',
    '3.28_exsanguinate_reap_mines_trickster',
    '3.28_kinetic_fusillade_of_detonation',
    '3.28_shock_nova_of_procession_hierophant',
}


def _by_candidate(dataset: dict, candidate_id: str) -> dict:
    for row in dataset['profiles']:
        if row['candidate_id'] == candidate_id:
            return row
    raise KeyError(candidate_id)


def test_representative_build_profiles_cover_entire_board_and_keep_status_counts():
    data = build_representative_build_profiles()

    assert data['dataset_kind'] == 'poe1_representative_build_profiles'
    assert data['summary']['profile_count'] == len(data['profiles'])
    # ACCUMULATING: the representative-build board is append-only (new patches/
    # archetypes are added, board rows never pruned), so board_profile_count and
    # profile_count only grow. Floor-check the baselines, pin the internal
    # composition invariant (profile_count == board + supplemental), and guard the
    # seeded candidate ids below so silent deletion is still caught.
    assert data['summary']['board_profile_count'] >= 35
    assert data['summary']['supplemental_promoted_count'] == 1
    assert data['summary']['profile_count'] >= 36
    assert data['summary']['profile_count'] == (
        data['summary']['board_profile_count'] + data['summary']['supplemental_promoted_count']
    )
    present_ids = {row['candidate_id'] for row in data['profiles']}
    missing = REQUIRED_CANDIDATE_IDS - present_ids
    assert not missing, f'seeded representative build profiles disappeared: {sorted(missing)}'
    assert data['summary']['confirmed'] == 15
    assert data['summary']['near_confirmed'] == 15
    assert data['summary']['hold'] == 6


def test_hexblast_mines_are_held_after_forward_patch_guard():
    data = build_representative_build_profiles()

    for candidate_id in ['3.23_hexblast_miner_saboteur', '3.25_hexblast_miner_saboteur']:
        row = _by_candidate(data, candidate_id)
        profile = row['build_profile']

        assert row['board_status'] == 'hold'
        assert row['use_policy'] == 'do_not_default'
        assert profile['confidence']['representative_build_status'] == 'hold'
        assert any('post_3_26_hexblast_trigger_cooldown_guard' in item for item in profile['constraints']['pain_points'])


def test_patch_hit_engines_are_practice_only_not_player_default():
    data = build_representative_build_profiles()

    for candidate_id in [
        '3.22_shockwave_totems_hierophant',
        '3.24_explosive_arrow_ballista_champion',
        '3.24_exsanguinate_mine_trickster',
        '3.26_siege_ballista_hierophant',
        '3.27_pyroclast_mine_saboteur',
        '3.28_exsanguinate_reap_mines_trickster',
    ]:
        row = _by_candidate(data, candidate_id)

        assert row['player_facing_default'] is False
        assert row['recommendation_visibility'] == 'practice_only'
        assert row['forward_guard_note']


def test_lightning_arrow_profile_uses_real_case_seed_and_passes_contract_audit():
    data = build_representative_build_profiles()
    row = _by_candidate(data, '3.25_lightning_arrow_ranger')
    profile = row['build_profile']
    audit = audit_build_profile(profile)

    assert row['case_found'] is True
    assert profile['identity']['class_name'] == 'Ranger'
    assert profile['identity']['ascendancy'] == 'Deadeye'
    assert profile['identity']['main_skill'] == 'Lightning Arrow'
    assert profile['identity']['leveling_skill'] == 'Rain of Arrows'
    assert profile['progression']['campaign_plan'][0]['main_skill'] == 'Rain of Arrows'
    assert profile['progression']['transition_points'][0]['to_skill'] == 'Lightning Arrow'
    assert profile['confidence']['representative_build_status'] == 'confirmed'
    assert {item['type'] for item in profile['evidence']} >= {'maxroll', 'poe_vault'}
    assert audit['issues'] == []


def test_hold_profile_stays_provisional_and_retains_seeded_progression():
    data = build_representative_build_profiles()
    row = _by_candidate(data, '3.28_kinetic_fusillade_of_detonation')
    profile = row['build_profile']

    assert row['board_status'] == 'hold'
    assert profile['confidence']['representative_build_status'] == 'hold'
    assert profile['progression']['leveling_confidence'] == 'inferred'
    assert profile['identity']['main_skill'] == 'Kinetic Fusillade of Detonation'
    assert profile['evidence']


def test_shock_nova_profile_has_campaign_to_endgame_transition_shape():
    data = build_representative_build_profiles()
    row = _by_candidate(data, '3.28_shock_nova_of_procession_hierophant')
    profile = row['build_profile']

    assert profile['identity']['class_name'] == 'Templar'
    assert profile['identity']['ascendancy'] == 'Hierophant'
    assert profile['identity']['leveling_skill'] == 'Arc'
    assert profile['progression']['campaign_plan'][0]['main_skill'] == 'Arc'
    assert profile['progression']['campaign_plan'][-1]['main_skill'] == 'Shock Nova of Procession'
    assert any(step['stage'] == 'early_maps' for step in profile['progression']['campaign_plan'])


def test_supplemental_promoted_exsanguinate_miner_profile_uses_stage_pob():
    data = build_representative_build_profiles()
    row = _by_candidate(data, '3.28_exsanguinate_reap_mines_trickster')
    profile = row['build_profile']
    audit = audit_build_profile(profile)

    assert row['case_found'] is True
    assert row['board_status'] == 'near_confirmed'
    assert row['use_policy'] == 'label_as_provisional_meta'
    assert profile['identity']['patch'] == '3.28'
    assert profile['identity']['class_name'] == 'Shadow'
    assert profile['identity']['ascendancy'] == 'Trickster'
    assert profile['identity']['main_skill'] == 'Exsanguinate Mine'
    assert profile['identity']['leveling_skill'] == 'Rolling Magma'
    assert profile['progression']['leveling_confidence'] == 'confirmed'
    assert profile['progression']['campaign_plan'][0]['main_skill'] == 'Rolling Magma'
    assert profile['progression']['campaign_plan'][-1]['main_skill'] == 'Exsanguinate Mine'
    assert any(step['to_skill'] == 'Exsanguinate Mine' for step in profile['progression']['transition_points'])
    assert {item['type'] for item in profile['evidence']} >= {'youtube', 'pob_archive', 'manual_curated'}
    assert audit['issues'] == []


def test_representative_build_profiles_are_catalogued():
    catalog = json.loads((Path(__file__).resolve().parents[2] / 'data' / 'db_catalog.json').read_text(encoding='utf-8'))
    entry = catalog['derived']['poe1_representative_build_profiles.latest.json']

    assert entry['kind'] == 'operations'
    # ACCUMULATING: catalog row count mirrors the append-only profile collection,
    # so it only grows past 36. Floor-check the baseline and tie it to the live
    # dataset so the catalog stays in lockstep instead of pinning a stale literal.
    assert entry['rows'] >= 36
    assert entry['rows'] == len(build_representative_build_profiles()['profiles'])
    assert entry['path'] == 'poe1_representative_build_profiles.latest.json'
