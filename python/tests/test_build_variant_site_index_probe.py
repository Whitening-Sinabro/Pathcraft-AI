# -*- coding: utf-8 -*-
"""Regression checks for direct site index probe helpers."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from build_variant_site_index_probe import candidate_aliases, classify_archetype_match, classify_temporal_match  # noqa: E402


def test_candidate_aliases_use_overrides_for_key_cases():
    assert candidate_aliases('3.28_penance_brand_inquisitor')[0] == 'penance brand'
    assert 'shockwave totem' in candidate_aliases('3.22_shockwave_totems_hierophant')
    assert 'cold snap' in candidate_aliases('3.28_cold_snap_of_power_hierophant')


def test_candidate_aliases_fallback_strips_class_words():
    aliases = candidate_aliases('3.99_example_skill_hierophant')
    assert aliases[0] == 'example skill'



def test_classify_temporal_match_is_conservative_for_old_patches():
    assert classify_temporal_match('3.28', 'mirage 3.28 league starter page', 'kinetic fusillade') == 'current_patch_compatible'
    assert classify_temporal_match('3.26', 'mirage 3.28 league starter page', 'boneshatter juggernaut') == 'family_presence_only'
    assert classify_temporal_match('3.26', 'generic page', 'boneshatter 3.26 secrets of the atlas') == 'historical_patch_compatible'



def test_classify_archetype_match_rejects_known_mismatches():
    assert classify_archetype_match('3.28_kinetic_fusillade_of_detonation', 'kinetic_fusillade_of_detonation_wander', 'kinetic fusillade ballista hierophant league starter') == 'delivery_mismatch'
    assert classify_archetype_match('3.28_penance_brand_inquisitor', 'penance_brand_inquisitor', 'penance brand ignite elementalist league starter') == 'class_mismatch'
    assert classify_archetype_match('3.28_shock_nova_of_procession_hierophant', 'shock_nova_of_procession_hierophant', 'shock nova of procession archmage hierophant league starter') == 'compatible'
