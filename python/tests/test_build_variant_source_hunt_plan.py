# -*- coding: utf-8 -*-
"""Regression checks for source hunt plan generation."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from build_variant_source_hunt_plan import build_source_hunt_plan  # noqa: E402


def test_source_hunt_plan_has_expected_shape():
    plan = build_source_hunt_plan()

    assert plan['dataset_kind'] == 'poe1_build_variant_source_hunt_plan'
    assert plan['item_count'] >= 15
    assert len(plan['by_patch']) >= 6


def test_source_hunt_plan_keeps_highest_priority_blocked_case_on_top():
    plan = build_source_hunt_plan()
    top = [item['candidate_id'] for item in plan['items'][:3]]

    assert '3.28_kinetic_fusillade_of_detonation' in top


def test_source_hunt_plan_tracks_promoted_penance_as_second_source_gap():
    plan = build_source_hunt_plan()
    items = {item['candidate_id']: item for item in plan['items']}
    penance = items['3.28_penance_brand_inquisitor']

    assert penance['strict_verdict'] == 'standard_only'
    assert penance['next_step'] == 'find_second_external_build_guide_source'
    assert 'creator_guide' in penance['existing_guide_source_families']


def test_source_hunt_plan_emits_query_templates_and_domains():
    plan = build_source_hunt_plan()
    items = {item['candidate_id']: item for item in plan['items']}

    kinetic = items['3.28_kinetic_fusillade_of_detonation']
    assert len(kinetic['query_templates']) >= 6
    assert 'maxroll.gg' in kinetic['preferred_domains']
    assert 'poe-vault.com' in kinetic['preferred_domains']


def test_source_hunt_plan_avoids_recounting_existing_guide_family_first():
    plan = build_source_hunt_plan()
    items = {item['candidate_id']: item for item in plan['items']}

    cold_snap = items['3.28_cold_snap_of_power_hierophant']
    assert 'poe_vault' in cold_snap['existing_guide_source_families']
    assert cold_snap['missing_target_families'][0] == 'maxroll'


def test_source_hunt_plan_defines_stop_conditions():
    plan = build_source_hunt_plan()
    items = {item['candidate_id']: item for item in plan['items']}

    kinetic = items['3.28_kinetic_fusillade_of_detonation']
    shockwave = items['3.22_shockwave_totems_hierophant']

    assert 'Add 1 external build guide family' in kinetic['stop_condition']
    assert 'different from existing poe_vault' in shockwave['stop_condition']
