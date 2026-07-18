# -*- coding: utf-8 -*-
"""Regression checks for two-lane research strategy."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from build_variant_research_strategy import build_research_strategy  # noqa: E402


def test_research_strategy_has_expected_shape():
    strategy = build_research_strategy()

    assert strategy['dataset_kind'] == 'poe1_build_variant_research_strategy'
    assert strategy['foundation_lane_count'] >= 4
    assert strategy['conversion_lane_count'] >= 10
    assert len(strategy['by_patch']) >= 6


def test_research_strategy_separates_foundation_and_conversion():
    strategy = build_research_strategy()

    assert all(item['min_hits_to_strict'] >= 2 for item in strategy['foundation_lane'])
    assert all(item['min_hits_to_strict'] <= 1 for item in strategy['conversion_lane'])


def test_research_strategy_keeps_3_28_kinetic_in_foundation_lane():
    strategy = build_research_strategy()
    top = [item['candidate_id'] for item in strategy['foundation_lane'][:2]]

    assert '3.28_kinetic_fusillade_of_detonation' in top


def test_research_strategy_exposes_one_hit_conversion_targets():
    strategy = build_research_strategy()
    top_conversion = [item['candidate_id'] for item in strategy['conversion_lane'][:6]]

    assert '3.28_cold_snap_of_power_hierophant' in top_conversion
    assert '3.27_pyroclast_mine_saboteur' in top_conversion
    assert '3.26_boneshatter_juggernaut' in top_conversion
    assert any(item['candidate_id'] == '3.28_penance_brand_inquisitor' for item in strategy['conversion_lane'])


def test_research_strategy_patch_breakdown_highlights_weak_clusters():
    strategy = build_research_strategy()
    by_patch = {item['patch']: item for item in strategy['by_patch']}

    assert by_patch['3.28']['foundation_count'] == 1
    assert by_patch['3.26']['foundation_count'] == 2
    assert by_patch['3.27']['foundation_count'] == 1
