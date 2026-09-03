# -*- coding: utf-8 -*-
"""Regression checks for representative build board export."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from build_representative_build_board import build_representative_build_board  # noqa: E402


# 이 보드의 입력 절반은 maxroll·poe-vault 의 **오늘자** 색인 페이지다. 그대로 두면
# 테스트가 남의 사이트 개편에 따라 red/green 을 오간다 — 실제로 3.28 Shock Nova 가
# poe-vault 색인에서 빠지면서 confirmed -> near_confirmed 로 내려가 깨졌다.
# 그래서 추적 중인 스냅샷을 주입해 판정 로직만 검사한다.
SITE_PROBE_SNAPSHOT = json.loads(
    (ROOT / 'data' / 'build_variant_site_index_probe.latest.json').read_text(encoding='utf-8')
)


def _board():
    return build_representative_build_board(site_probe=SITE_PROBE_SNAPSHOT)


def test_representative_build_board_has_expected_shape():
    board = _board()

    assert board['dataset_kind'] == 'poe1_representative_build_board'
    assert len(board['patches']) == 7
    assert sum(board['overall_counts'].values()) == 35


def test_representative_build_board_keeps_3_25_fully_confirmed():
    board = _board()
    patch = next(item for item in board['patches'] if item['patch'] == '3.25')

    assert patch['counts']['confirmed'] == 4
    assert patch['counts']['hold'] == 1


def test_representative_build_board_holds_hexblast_after_3_26_guard():
    board = _board()

    for patch_id, candidate_id in [
        ('3.23', '3.23_hexblast_miner_saboteur'),
        ('3.25', '3.25_hexblast_miner_saboteur'),
    ]:
        patch = next(item for item in board['patches'] if item['patch'] == patch_id)
        row = next(item for item in patch['rows'] if item['candidate_id'] == candidate_id)

        assert row['status'] == 'hold'
        assert row['use_policy'] == 'do_not_default'
        assert 'post_3_26_hexblast_trigger_cooldown_guard' in row['rationale']
        assert 'current PoB/live proof' in row['forward_guard_note']


def test_representative_build_board_blocks_patch_hit_engines_from_default_cards():
    board = _board()
    rows = {
        row['candidate_id']: row
        for patch in board['patches']
        for row in patch['rows']
    }

    for candidate_id in [
        '3.22_shockwave_totems_hierophant',
        '3.24_explosive_arrow_ballista_champion',
        '3.24_exsanguinate_mine_trickster',
        '3.26_siege_ballista_hierophant',
        '3.27_pyroclast_mine_saboteur',
    ]:
        row = rows[candidate_id]

        assert row['player_facing_default'] is False
        assert row['recommendation_visibility'] == 'practice_only'
        assert row['forward_guard_note']


def test_representative_build_board_marks_3_28_shock_nova_confirmed():
    board = _board()
    patch = next(item for item in board['patches'] if item['patch'] == '3.28')
    row = next(item for item in patch['rows'] if item['candidate_id'] == '3.28_shock_nova_of_procession_hierophant')

    assert row['status'] == 'confirmed'
    assert 'direct_index_two_family_match' in row['rationale'] or 'strict_two_source_pass' in row['rationale']


def test_representative_build_board_marks_3_28_kinetic_hold_and_penance_near_confirmed():
    board = _board()
    patch = next(item for item in board['patches'] if item['patch'] == '3.28')

    kinetic = next(item for item in patch['rows'] if item['candidate_id'] == '3.28_kinetic_fusillade_of_detonation')
    penance = next(item for item in patch['rows'] if item['candidate_id'] == '3.28_penance_brand_inquisitor')

    assert kinetic['status'] == 'hold'
    assert penance['status'] == 'near_confirmed'


def test_representative_build_board_marks_3_26_ball_lightning_hold():
    board = _board()
    patch = next(item for item in board['patches'] if item['patch'] == '3.26')
    row = next(item for item in patch['rows'] if item['candidate_id'] == '3.26_ball_lightning_caster')

    assert row['status'] == 'hold'
    assert row['use_policy'] == 'do_not_default'
