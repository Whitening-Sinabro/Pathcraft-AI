# -*- coding: utf-8 -*-
"""Assemble representative build profiles from build board + real cases."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
BOARD_PATH = ROOT / 'data' / 'poe1_representative_build_board.latest.json'
CASES_PATH = ROOT / 'data' / 'build_variant_real_cases_v1.json'
QUEUE_PATH = ROOT / 'data' / 'build_variant_collection_queue_v1.json'
PROMOTED_CASE_SNAPSHOTS_PATH = ROOT / 'data' / 'build_corpus_promoted_case_snapshots.latest.json'
OUT_PATH = ROOT / 'data' / 'poe1_representative_build_profiles.latest.json'

KEEP_LOWER = {'of', 'and', 'or'}
ASC_TO_CLASS = {
    'Assassin': 'Shadow',
    'Berserker': 'Marauder',
    'Champion': 'Duelist',
    'Chieftain': 'Marauder',
    'Deadeye': 'Ranger',
    'Elementalist': 'Witch',
    'Gladiator': 'Duelist',
    'Guardian': 'Templar',
    'Hierophant': 'Templar',
    'Inquisitor': 'Templar',
    'Juggernaut': 'Marauder',
    'Necromancer': 'Witch',
    'Pathfinder': 'Ranger',
    'Saboteur': 'Shadow',
    'Slayer': 'Duelist',
    'Trickster': 'Shadow',
    'Warden': 'Ranger',
}
KNOWN_ARCHETYPE = {
    'ball_lightning_caster': {'class_name': 'Templar', 'ascendancy': 'Hierophant', 'main_skill': 'Ball Lightning', 'leveling_skill': 'Stormblast Mine'},
    'boneshatter_juggernaut': {'class_name': 'Marauder', 'ascendancy': 'Juggernaut', 'main_skill': 'Boneshatter', 'leveling_skill': 'Sunder'},
    'cold_snap_of_power_hierophant': {'class_name': 'Templar', 'ascendancy': 'Hierophant', 'main_skill': 'Cold Snap of Power', 'leveling_skill': 'Freezing Pulse'},
    'corrupting_fever_champion': {'class_name': 'Duelist', 'ascendancy': 'Champion', 'main_skill': 'Corrupting Fever', 'leveling_skill': 'Spectral Throw'},
    'detonate_dead_caster': {'class_name': 'Witch', 'ascendancy': 'Elementalist', 'main_skill': 'Detonate Dead', 'leveling_skill': 'Rolling Magma'},
    'dominating_blow_guardian': {'class_name': 'Templar', 'ascendancy': 'Guardian', 'main_skill': 'Dominating Blow', 'leveling_skill': 'Smite'},
    'explosive_arrow_ballista_champion': {'class_name': 'Duelist', 'ascendancy': 'Champion', 'main_skill': 'Explosive Arrow', 'leveling_skill': 'Rain of Arrows'},
    'exsanguinate_mine_trickster': {'class_name': 'Shadow', 'ascendancy': 'Trickster', 'main_skill': 'Exsanguinate Mine', 'leveling_skill': 'Stormblast Mine'},
    'hexblast_miner_saboteur': {'class_name': 'Shadow', 'ascendancy': 'Saboteur', 'main_skill': 'Hexblast Mine', 'leveling_skill': 'Pyroclast Mine'},
    'ice_nova_caster': {'class_name': 'Templar', 'ascendancy': 'Hierophant', 'main_skill': 'Ice Nova', 'leveling_skill': 'Rolling Magma'},
    'ice_shot_deadeye': {'class_name': 'Ranger', 'ascendancy': 'Deadeye', 'main_skill': 'Ice Shot', 'leveling_skill': 'Rain of Arrows'},
    'kinetic_fusillade_of_detonation_wander': {'class_name': 'Shadow', 'ascendancy': 'Trickster', 'main_skill': 'Kinetic Fusillade of Detonation', 'leveling_skill': 'Power Siphon'},
    'lacerate_duelist': {'class_name': 'Duelist', 'ascendancy': 'Gladiator', 'main_skill': 'Lacerate', 'leveling_skill': 'Splitting Steel'},
    'lightning_arrow_deadeye': {'class_name': 'Ranger', 'ascendancy': 'Deadeye', 'main_skill': 'Lightning Arrow', 'leveling_skill': 'Rain of Arrows'},
    'lightning_strike_deadeye_or_warden': {'class_name': 'Ranger', 'ascendancy': 'Deadeye or Warden', 'main_skill': 'Lightning Strike', 'leveling_skill': 'Spectral Throw'},
    'penance_brand_inquisitor': {'class_name': 'Templar', 'ascendancy': 'Inquisitor', 'main_skill': 'Penance Brand', 'leveling_skill': 'Storm Brand'},
    'pyroclast_mine_saboteur': {'class_name': 'Shadow', 'ascendancy': 'Saboteur', 'main_skill': 'Pyroclast Mine', 'leveling_skill': 'Stormblast Mine'},
    'shock_nova_of_procession_hierophant': {'class_name': 'Templar', 'ascendancy': 'Hierophant', 'main_skill': 'Shock Nova of Procession', 'leveling_skill': 'Arc'},
    'shockwave_totems_hierophant': {'class_name': 'Templar', 'ascendancy': 'Hierophant', 'main_skill': 'Shockwave Totem', 'leveling_skill': 'Holy Flame Totem'},
    'siege_ballista_hierophant': {'class_name': 'Templar', 'ascendancy': 'Hierophant', 'main_skill': 'Siege Ballista', 'leveling_skill': 'Shrapnel Ballista'},
    'toxic_rain_pathfinder': {'class_name': 'Ranger', 'ascendancy': 'Pathfinder', 'main_skill': 'Toxic Rain', 'leveling_skill': 'Toxic Rain'},
    'toxic_rain_ranger': {'class_name': 'Ranger', 'ascendancy': 'Pathfinder', 'main_skill': 'Toxic Rain', 'leveling_skill': 'Toxic Rain'},
}
AURA_PACKAGE_HINTS = {
    'early_bow_reservation': (['Precision'], ['Dash'], []),
    'wrath_caster_reservation': (['Wrath'], ['Flame Dash'], ['Steelskin']),
    'optimized_lightning_reservation': (['Wrath', 'Zealotry'], ['Flame Dash'], ['Steelskin']),
    'early_caster_reservation': (['Clarity'], ['Flame Dash'], []),
    'mid_mine_reservation': (['Skitterbots'], ['Flame Dash'], ['Steelskin']),
    'optimized_mine_reservation': (['Skitterbots', 'Grace'], ['Flame Dash'], ['Steelskin']),
    'determination_purity_rf': (['Determination', 'Purity of Fire'], ['Shield Charge'], ['Molten Shell']),
    'optimized_rf_reservation': (['Determination', 'Purity of Fire', 'Malevolence'], ['Shield Charge'], ['Molten Shell']),
    'early_fire_reservation': (['Clarity'], ['Flame Dash'], []),
    'early_caster_brand_reservation': (['Clarity'], ['Flame Dash'], []),
    'mid_brand_reservation': (['Hatred'], ['Flame Dash'], ['Steelskin']),
    'early_melee_reservation': (['Precision'], ['Leap Slam'], ['Steelskin']),
    'low_reservation_melee': (['Precision'], ['Leap Slam'], ['Steelskin']),
}
PHASE_TO_STAGE = {
    'campaign_start': ('act_1_3', '1-33'),
    'campaign_mid': ('act_4_6', '34-51'),
    'campaign_late': ('act_7_10', '52-67'),
    'maps_entry': ('early_maps', '68-79'),
    'early_endgame': ('midgame', '80-89'),
    'mid_endgame': ('midgame', '80-92'),
    'late_endgame': ('late_endgame', '93-100'),
    'high_end': ('late_endgame', '93-100'),
}
SPECIALIZATION_SCORE = {
    'generic': {'mapping': 80, 'bossing': 65, 'sanctum': 60, 'heist': 65, 'expedition': 70, 'simulacrum': 50},
    'bossing': {'mapping': 70, 'bossing': 88, 'sanctum': 72, 'heist': 55, 'expedition': 60, 'simulacrum': 58},
    'mapping': {'mapping': 92, 'bossing': 58, 'sanctum': 62, 'heist': 78, 'expedition': 80, 'simulacrum': 42},
    'sanctum': {'mapping': 68, 'bossing': 74, 'sanctum': 90, 'heist': 58, 'expedition': 55, 'simulacrum': 45},
}
BUDGET_ENTRY = {'starter': 0.5, 'budget': 1.5, 'mid': 6.0, 'high_end': 25.0, 'mirror': 120.0}
BUDGET_COMFORT = {'starter': 4.0, 'budget': 8.0, 'mid': 20.0, 'high_end': 80.0, 'mirror': 250.0}
BUDGET_ASP = {'starter': 25.0, 'budget': 40.0, 'mid': 80.0, 'high_end': 200.0, 'mirror': 500.0}
SUPPLEMENTAL_PROMOTED_PROFILE_SPECS = {
    '3.28_exsanguinate_reap_mines_trickster': {
        'preferred_case_id': '3.28_exsanguinate_reap_mines_trickster.3J6Dm6pkA6-5',
        'league_name': 'Mirage',
        'board_status': 'near_confirmed',
        'use_policy': 'label_as_provisional_meta',
        'player_facing_default': False,
        'recommendation_visibility': 'practice_only',
        'forward_guard_note': '3.29 changes Blastchain Mine, High-Impact Mine, and Charged Mines cost/damage/throw-speed values; Exsanguinate/Reap Miner remains a practice/source lane until refreshed with 3.29 PoB.',
        'source_confidence': 'high',
        'build_name': 'Exsanguinate/Reap Mines Trickster',
        'main_skill': 'Exsanguinate Mine',
        'leveling_skill': 'Rolling Magma',
        'damage_tags': ['physical', 'spell', 'mine'],
        'budget_curve': {
            'entry_cost_divines': 1.0,
            'comfortable_cost_divines': 8.0,
            'aspirational_cost_divines': 40.0,
            'respec_cost_points': 20,
            'notes': 'Supplemental profile from parser-validated promoted PoB stages; Pyroclast Mines bridges into Exsanguinate/Reap mines.',
        },
        'availability': {
            'league_start_viable': True,
            'ssf_viable': 'medium',
            'hc_viable': 'medium',
            'twink_required': False,
            'mandatory_uniques': [],
            'mandatory_transfigured_gems': [],
        },
        'progression': {
            'leveling_confidence': 'confirmed',
            'early_mapping_ready': True,
            'transition_points': [
                {
                    'stage': 'act_1_3',
                    'main_skill': 'Rolling Magma',
                    'trigger': 'Use Cobra Lash only until Rolling Magma is available, then level with Rolling Magma and Flame Wall.',
                    'required_links': 3,
                    'required_item': None,
                    'from_skill': 'Cobra Lash',
                    'to_skill': 'Rolling Magma',
                    'level': 4,
                    'source': 'promoted_pob_skill_set',
                },
                {
                    'stage': 'act_4_6',
                    'main_skill': 'Pyroclast Mine',
                    'trigger': 'Switch after the Library setup when Pyroclast Mine plus mine supports are available.',
                    'required_links': 4,
                    'required_item': None,
                    'from_skill': 'Rolling Magma',
                    'to_skill': 'Pyroclast Mine',
                    'level': 31,
                    'source': 'promoted_pob_skill_set',
                },
                {
                    'stage': 'midgame',
                    'main_skill': 'Exsanguinate Mine',
                    'trigger': 'Swap from Pyroclast Mine once Exsanguinate/Reap mine links and the map transition tree are ready.',
                    'required_links': 5,
                    'required_item': None,
                    'from_skill': 'Pyroclast Mine',
                    'to_skill': 'Exsanguinate Mine',
                    'level': 80,
                    'source': 'promoted_pob_skill_set',
                },
            ],
            'campaign_plan': [
                {
                    'stage': 'act_1_3',
                    'stage_label': 'Acts 1-3',
                    'level_range': '1-30',
                    'main_skill': 'Rolling Magma',
                    'support_links': ['Elemental Proliferation', 'Combustion'],
                    'auras': [],
                    'utility': ['Flame Wall', 'Frostblink', 'Shield Charge', 'Bear Trap'],
                    'guard': [],
                    'source': 'promoted_pob_skill_set',
                    'notes': 'PoB keeps Cobra Lash as a level-1 bridge, then runs Rolling Magma/Flame Wall before mines.',
                },
                {
                    'stage': 'act_4_6',
                    'stage_label': 'Acts 4-6',
                    'level_range': '31-55',
                    'main_skill': 'Pyroclast Mine',
                    'support_links': ['Charged Mines', 'Added Cold Damage', 'Minefield'],
                    'auras': ['Grace', 'Summon Skitterbots'],
                    'utility': ['Automation', 'Detonate Mines', 'Shield Charge', 'Bear Trap'],
                    'guard': [],
                    'source': 'promoted_pob_skill_set',
                    'notes': 'Library stage and Act 4 stage both use Pyroclast Mine before the Exsanguinate swap.',
                },
                {
                    'stage': 'act_7_10',
                    'stage_label': 'Acts 7-10',
                    'level_range': '56-67',
                    'main_skill': 'Pyroclast Mine',
                    'support_links': ['Charged Mines', 'Minefield', 'Elemental Focus'],
                    'auras': ['Grace', 'Summon Skitterbots'],
                    'utility': ['Automation', 'Detonate Mines', 'Shield Charge', 'Bear Trap'],
                    'guard': [],
                    'source': 'promoted_pob_skill_set',
                    'notes': 'PoB labels this stage A8-10 and keeps Pyroclast Mine through campaign completion.',
                },
                {
                    'stage': 'early_maps',
                    'stage_label': 'Early Maps',
                    'level_range': '68-79',
                    'main_skill': 'Pyroclast Mine',
                    'support_links': ['Charged Mines', 'Minefield', 'Elemental Focus', 'Trap and Mine Damage'],
                    'auras': ['Grace', 'Summon Skitterbots'],
                    'utility': ['Automation', 'Detonate Mines', 'Shield Charge', 'Bear Trap'],
                    'guard': [],
                    'source': 'promoted_pob_skill_set',
                    'notes': 'Stay Pyroclast in early maps while assembling the physical mine swap.',
                },
                {
                    'stage': 'midgame',
                    'stage_label': 'Exsanguinate/Reap Swap',
                    'level_range': '80-92',
                    'main_skill': 'Exsanguinate Mine',
                    'support_links': ['Reap', 'High-Impact Mine', 'Charged Mines', 'Minefield', 'Trap and Mine Damage'],
                    'auras': ['Grace', 'Hatred', 'Summon Skitterbots'],
                    'utility': ['Automation', 'Detonate Mines', 'Shield Charge', 'Arcanist Brand'],
                    'guard': ['Steelskin'],
                    'source': 'promoted_pob_skill_set',
                    'notes': 'PoB stage labels the final damage setup Exsanguinate Reap; Frostblink is ignored as parser noise for main-skill selection.',
                },
            ],
            'aura_plan': [],
            'passive_plan': [
                {
                    'stage': 'act_1_3',
                    'stage_label': 'Rolling Magma Trees',
                    'level_range': '1-30',
                    'tree_url': '',
                    'active': False,
                    'source': 'promoted_pob_tree_spec',
                    'priorities': ['early caster pathing', 'life', 'damage'],
                    'notes': 'PoB includes Level 9 and Level 16 Rolling Magma trees.',
                },
                {
                    'stage': 'act_4_6',
                    'stage_label': 'Pyroclast Mine Trees',
                    'level_range': '31-67',
                    'tree_url': '',
                    'active': False,
                    'source': 'promoted_pob_tree_spec',
                    'priorities': ['mine damage', 'mine throwing speed', 'life'],
                    'notes': 'PoB includes Level 31, 45, 55, 64, and 70 Pyroclast Mine trees.',
                },
                {
                    'stage': 'midgame',
                    'stage_label': 'Exsanguinate/Reap Transition',
                    'level_range': '80-92',
                    'tree_url': '',
                    'active': True,
                    'source': 'promoted_pob_tree_spec',
                    'priorities': ['physical spell damage', 'mine scaling', 'suppression', 'energy shield'],
                    'notes': 'PoB includes Level 80 and maps transition trees for Exsanguinate/Reap Mines.',
                },
            ],
            'gear_stages': [
                {
                    'stage': 'early_maps',
                    'stage_label': 'Pyroclast Entry Gear',
                    'level_range': '68-79',
                    'priorities': ['life/resistance rares', 'mine damage weapon or shield', 'movement speed boots'],
                    'requirements': [],
                    'source': 'promoted_pob_summary',
                    'notes': 'No mandatory unique gate was detected for the entry route.',
                },
                {
                    'stage': 'midgame',
                    'stage_label': 'Exsanguinate/Reap Swap Gear',
                    'level_range': '80-92',
                    'priorities': ['gem levels', 'crit scaling', 'suppression', 'chaos resistance'],
                    'requirements': [],
                    'source': 'promoted_pob_summary',
                    'notes': 'Static screen marks runtime inputs unknown; validate deaths per map and flask uptime before HC wording.',
                },
            ],
        },
        'suitability': {'mapping': 86, 'bossing': 82, 'sanctum': 62, 'heist': 65, 'expedition': 72, 'simulacrum': 55},
        'constraints': {
            'banned_map_mods': [],
            'pain_points': [
                'swap_timing_from_pyroclast_to_exsanguinate_reap',
                'mine_playstyle_requires_detonation_automation_or_manual_comfort',
                'static_pob_runtime_inputs_unverified',
            ],
            'reroll_recommended_over_respec': False,
        },
        'evidence': [
            {
                'type': 'youtube',
                'label': 'FearlessDumb0 Exsanguinate/Reap Miner 3.28',
                'url': 'https://www.youtube.com/watch?v=ZEvuQ5krLwQ',
                'notes': 'Creator video for the 3.28 Exsanguinate/Reap Miner route.',
            },
            {
                'type': 'pob_archive',
                'label': 'PoB Archives BBcLLRaw',
                'url': 'https://pobarchives.com/build/BBcLLRaw',
                'notes': 'Archive page exposing the league-start PoB.',
            },
            {
                'type': 'manual_curated',
                'label': 'Parser-validated pobb.in 3J6Dm6pkA6-5',
                'url': 'https://pobb.in/3J6Dm6pkA6-5',
                'notes': 'Promoted PoB with campaign, early-map, and Exsanguinate/Reap stage sets.',
            },
        ],
    },
}


def _load_json(path: Path) -> dict:
    with open(path, 'r', encoding='utf-8-sig') as f:
        return json.load(f)


def _title_from_slug(slug: str) -> str:
    parts = []
    for token in slug.split('_'):
        parts.append(token if token in KEEP_LOWER else token.capitalize())
    return ' '.join(parts)


def _extract_skill_from_state_id(state_id: str) -> str:
    prefixes = ('campaign_', 'act_', 'maps_', 'map_', 'endgame_', 'high_end_', 'mid_end_', 'late_end_')
    skill_slug = state_id
    for prefix in prefixes:
        if state_id.startswith(prefix):
            skill_slug = state_id[len(prefix):]
            break
    return _title_from_slug(skill_slug)


def _infer_build_phase(state: dict[str, Any]) -> str:
    explicit = state.get('build_phase')
    if explicit:
        return explicit
    state_id = str(state.get('state_id', '')).lower()
    budget = state.get('budget_tier')
    if state_id.startswith(('campaign_', 'act_')):
        if 'late' in state_id:
            return 'campaign_late'
        if 'mid' in state_id:
            return 'campaign_mid'
        return 'campaign_start'
    if state_id.startswith(('maps_', 'map_')):
        return 'maps_entry' if budget in {'starter', 'budget'} else 'early_endgame'
    if state_id.startswith('high_end_') or budget == 'high_end':
        return 'high_end'
    if state_id.startswith('late_end_'):
        return 'late_endgame'
    if state_id.startswith('mid_end_') or budget == 'mid':
        return 'mid_endgame'
    if budget == 'budget':
        return 'maps_entry'
    return 'campaign_start'


def _phase_order(build_phase: str) -> int:
    order = ['campaign_start', 'campaign_mid', 'campaign_late', 'maps_entry', 'early_endgame', 'mid_endgame', 'late_endgame', 'high_end']
    return order.index(build_phase) if build_phase in order else 99


def _evidence_type(raw_type: str) -> str:
    lowered = raw_type.lower()
    if lowered.startswith('maxroll'):
        return 'maxroll'
    if lowered.startswith('poe_vault'):
        return 'poe_vault'
    if lowered.startswith('youtube') or lowered.startswith('video'):
        return 'youtube'
    if lowered.startswith('forum'):
        return 'forum_guide'
    if lowered.startswith('reddit'):
        return 'reddit'
    return 'manual_curated'


def _unique_evidence(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[tuple[str, str]] = set()
    out = []
    for item in items:
        key = (item['type'], item['label'])
        if key in seen:
            continue
        seen.add(key)
        out.append(item)
    return out


def _infer_identity(row: dict[str, Any], case: dict[str, Any] | None) -> dict[str, str]:
    archetype_id = row['archetype_id']
    combined = ' '.join(filter(None, [archetype_id, row.get('candidate_id', ''), row.get('build_label', '')]))
    override = KNOWN_ARCHETYPE.get(archetype_id, {})
    ascendancy = override.get('ascendancy', 'Unknown')
    class_name = override.get('class_name', ASC_TO_CLASS.get(ascendancy, 'Unknown'))
    for asc in ASC_TO_CLASS:
        if asc.lower().replace(' ', '_') in combined.lower().replace(' ', '_'):
            ascendancy = asc
            class_name = ASC_TO_CLASS[asc]
            break
    if class_name == 'Unknown':
        for token, candidate in [('ranger', 'Ranger'), ('duelist', 'Duelist'), ('marauder', 'Marauder'), ('templar', 'Templar'), ('shadow', 'Shadow'), ('witch', 'Witch')]:
            if token in combined.lower():
                class_name = candidate
                break
    return {
        'class_name': class_name,
        'ascendancy': ascendancy,
        'main_skill': override.get('main_skill') or _title_from_slug(archetype_id),
        'leveling_skill': override.get('leveling_skill') or override.get('main_skill') or _title_from_slug(archetype_id),
    }


def _sorted_states(case: dict[str, Any] | None) -> list[dict[str, Any]]:
    states = list((case or {}).get('states', []))
    for state in states:
        state['_build_phase'] = _infer_build_phase(state)
    states.sort(key=lambda item: _phase_order(item.get('_build_phase', '')))
    return states


def _main_and_leveling_skill(identity_seed: dict[str, str], states: list[dict[str, Any]]) -> tuple[str, str]:
    if not states:
        return identity_seed['main_skill'], identity_seed['leveling_skill']
    leveling_skill = _extract_skill_from_state_id(states[0]['state_id'])
    final_skill = _extract_skill_from_state_id(states[-1]['state_id'])
    return final_skill or identity_seed['main_skill'], leveling_skill or identity_seed['leveling_skill']


def _infer_playstyle(main_skill: str) -> tuple[str, int, str, str]:
    lower = main_skill.lower()
    if 'righteous fire' in lower or 'death aura' in lower:
        return '0_button', 0, 'medium', 'low'
    if any(keyword in lower for keyword in ('mine', 'totem', 'ballista', 'brand')):
        return '2_button', 2, 'medium', 'low'
    if any(keyword in lower for keyword in ('lightning arrow', 'ice shot', 'toxic rain')):
        return '1_click_plus_movement', 2, 'high', 'medium'
    if any(keyword in lower for keyword in ('boneshatter', 'lacerate', 'lightning strike', 'dominating blow')):
        return '1_click', 1, 'medium', 'medium'
    return '1_click', 1, 'medium', 'low'


def _budget_curve(states: list[dict[str, Any]], board_status: str, transitions: list[dict[str, Any]]) -> dict[str, Any]:
    budget_tiers = [state.get('budget_tier', 'budget') for state in states] or ['budget']
    entry_tier = budget_tiers[0]
    end_tier = budget_tiers[-1]
    respec_cost = 8 if len(states) <= 2 else 18
    if any(item.get('decision') == 'sub_archetype_split' for item in transitions):
        respec_cost = max(respec_cost, 20)
    if board_status == 'hold':
        respec_cost += 4
    return {
        'entry_cost_divines': BUDGET_ENTRY.get(entry_tier, 2.0),
        'comfortable_cost_divines': BUDGET_COMFORT.get(end_tier, 10.0),
        'aspirational_cost_divines': BUDGET_ASP.get(end_tier, 40.0),
        'respec_cost_points': respec_cost,
        'notes': 'Representative seed inferred from phase budget tiers and transition structure.',
    }


def _availability(states: list[dict[str, Any]], board_row: dict[str, Any], class_name: str, ascendancy: str) -> dict[str, Any]:
    first_state = states[0] if states else {}
    unique_gate = first_state.get('core_unique_gate', 'none')
    league_start_viable = first_state.get('budget_tier') == 'starter' and board_row['status'] != 'hold' and unique_gate == 'none'
    defense_text = ' '.join(str(state.get('defense_engine', '')) for state in states).lower()
    if any(token in defense_text for token in ('armour', 'regen', 'juggernaut', 'champion', 'guardian')):
        hc = 'high'
    elif any(token in defense_text for token in ('trickster', 'hierophant', 'inquisitor', 'evasion')):
        hc = 'medium'
    else:
        hc = 'low'
    ssf = 'high' if unique_gate == 'none' and board_row['status'] == 'confirmed' else 'medium' if unique_gate == 'none' else 'low'
    if ascendancy == 'Deadeye or Warden':
        hc = 'low'
    return {
        'league_start_viable': league_start_viable,
        'ssf_viable': ssf,
        'hc_viable': hc,
        'twink_required': not league_start_viable,
        'mandatory_uniques': [] if unique_gate == 'none' else [unique_gate],
        'mandatory_transfigured_gems': [board_row['build_label']] if ' of ' in board_row['build_label'] else [],
    }


def _campaign_plan(states: list[dict[str, Any]]) -> list[dict[str, Any]]:
    plan = []
    for state in states:
        stage, level_range = PHASE_TO_STAGE.get(state.get('_build_phase'), ('unknown', None))
        auras, utility, guard = AURA_PACKAGE_HINTS.get(state.get('aura_package_id', ''), ([], [], []))
        plan.append({
            'stage': stage,
            'stage_label': _title_from_slug(state.get('_build_phase', 'unknown')),
            'level_range': level_range,
            'main_skill': _extract_skill_from_state_id(state.get('state_id', '')),
            'support_links': [],
            'auras': list(auras),
            'utility': list(utility),
            'guard': list(guard),
            'source': 'real_case_seed',
            'notes': state.get('damage_engine', ''),
        })
    return plan


def _aura_plan(states: list[dict[str, Any]]) -> list[dict[str, Any]]:
    plan = []
    for state in states:
        stage, level_range = PHASE_TO_STAGE.get(state.get('_build_phase'), ('unknown', None))
        auras, utility, guard = AURA_PACKAGE_HINTS.get(state.get('aura_package_id', ''), ([], [], []))
        plan.append({
            'stage': stage,
            'stage_label': _title_from_slug(state.get('_build_phase', 'unknown')),
            'level_range': level_range,
            'auras': list(auras),
            'utility': list(utility),
            'guard': list(guard),
            'source': 'aura_package_seed',
            'notes': state.get('aura_package_id', ''),
        })
    return plan


def _passive_plan(states: list[dict[str, Any]]) -> list[dict[str, Any]]:
    plan = []
    for state in states:
        stage, level_range = PHASE_TO_STAGE.get(state.get('_build_phase'), ('unknown', None))
        priorities = [part.strip() for part in str(state.get('tree_shape_class', '')).split() if part.strip()][:4]
        plan.append({
            'stage': stage,
            'stage_label': _title_from_slug(state.get('_build_phase', 'unknown')),
            'level_range': level_range,
            'tree_url': '',
            'active': stage in {'early_maps', 'midgame', 'late_endgame'},
            'source': 'real_case_seed',
            'priorities': priorities,
            'notes': state.get('tree_shape_class', ''),
        })
    return plan


def _gear_stages(states: list[dict[str, Any]]) -> list[dict[str, Any]]:
    stages = []
    for state in states:
        stage, level_range = PHASE_TO_STAGE.get(state.get('_build_phase'), ('unknown', None))
        requirements = []
        unique_gate = state.get('core_unique_gate', 'none')
        if unique_gate != 'none':
            requirements.append(f'Unique gate: {unique_gate}')
        stages.append({
            'stage': stage,
            'stage_label': _title_from_slug(state.get('_build_phase', 'unknown')),
            'level_range': level_range,
            'priorities': [item for item in [state.get('gear_package_id', ''), state.get('cluster_package_id', '')] if item and item != 'none'],
            'requirements': [item for item in requirements if item],
            'source': 'real_case_seed',
            'notes': state.get('defense_engine', ''),
        })
    return stages


def _transition_points(states: list[dict[str, Any]]) -> list[dict[str, Any]]:
    points = []
    for left, right in zip(states, states[1:]):
        stage, level_range = PHASE_TO_STAGE.get(right.get('_build_phase'), ('unknown', None))
        level = None
        if level_range and level_range[0].isdigit():
            level = int(level_range.split('-')[0].rstrip('+'))
        points.append({
            'stage': stage,
            'main_skill': _extract_skill_from_state_id(right.get('state_id', '')),
            'trigger': f"Transition from {_extract_skill_from_state_id(left.get('state_id', ''))} into {_extract_skill_from_state_id(right.get('state_id', ''))}.",
            'required_links': 4 if stage in {'early_maps', 'midgame', 'late_endgame'} else None,
            'required_item': None if right.get('core_unique_gate') == 'none' else right.get('core_unique_gate'),
            'from_skill': _extract_skill_from_state_id(left.get('state_id', '')),
            'to_skill': _extract_skill_from_state_id(right.get('state_id', '')),
            'level': level,
            'source': 'real_case_seed',
        })
    return points


def _suitability(states: list[dict[str, Any]], main_skill: str) -> dict[str, int]:
    specialization = states[-1].get('content_specialization', 'generic') if states else 'generic'
    result = dict(SPECIALIZATION_SCORE.get(specialization, SPECIALIZATION_SCORE['generic']))
    lower = main_skill.lower()
    if any(token in lower for token in ('mine', 'totem', 'brand')):
        result['bossing'] = min(100, result['bossing'] + 10)
        result['mapping'] = max(0, result['mapping'] - 5)
    if any(token in lower for token in ('lightning arrow', 'ice shot', 'kinetic')):
        result['mapping'] = min(100, result['mapping'] + 10)
    if 'boneshatter' in lower or 'lacerate' in lower:
        result['bossing'] = min(100, result['bossing'] + 6)
    return result


def _confidence(board_row: dict[str, Any], evidence_count: int, case: dict[str, Any] | None) -> dict[str, Any]:
    return {
        'representative_build_status': 'near_confirmed' if board_row['status'] == 'near_confirmed' else board_row['status'],
        'source_count': evidence_count,
        'notes': (case or {}).get('source_status', 'board_only_seed'),
    }


def _constraints(board_row: dict[str, Any], states: list[dict[str, Any]]) -> dict[str, Any]:
    pain_points = list(board_row.get('rationale', [])) or ['representative_seed_without_live_pob']
    if any(state.get('core_unique_gate') not in {None, 'none'} for state in states):
        pain_points.append('core_unique_gate_present')
    return {
        'banned_map_mods': [],
        'pain_points': pain_points[:5],
        'reroll_recommended_over_respec': len(states) >= 3,
    }


def _load_promoted_case_snapshots() -> dict[str, dict[str, Any]]:
    if not PROMOTED_CASE_SNAPSHOTS_PATH.exists():
        return {}
    data = _load_json(PROMOTED_CASE_SNAPSHOTS_PATH)
    return {case['case_id']: case for case in data.get('cases', [])}


def _supplemental_profile_from_promoted_case(candidate_id: str, spec: dict[str, Any], case: dict[str, Any]) -> dict[str, Any]:
    parsed_summary = case.get('parsed_summary', {})
    parsed_identity = parsed_summary.get('identity', {})
    evidence = list(spec['evidence'])
    source_pob = case.get('source_pob')
    if source_pob and all(item.get('url') != source_pob for item in evidence):
        evidence.append({
            'type': 'manual_curated',
            'label': 'Parser-validated supplemental PoB',
            'url': source_pob,
            'notes': 'Direct promoted PoB attached to the supplemental representative profile.',
        })
    evidence = _unique_evidence(evidence)

    profile = {
        'schema_version': '1.1.0',
        'dataset_kind': 'poe1_build_profile',
        'build_id': candidate_id.replace('.', '_').replace('-', '_'),
        'identity': {
            'build_name': spec['build_name'],
            'patch': candidate_id.split('_', 1)[0],
            'class_name': parsed_identity.get('class', 'Unknown'),
            'ascendancy': parsed_identity.get('ascendancy', 'Unknown'),
            'main_skill': spec['main_skill'],
            'leveling_skill': spec['leveling_skill'],
            'damage_tags': list(spec['damage_tags']),
            'weapon_preferences': [],
        },
        'playstyle': {
            'input_style': _infer_playstyle(spec['main_skill'])[0],
            'manual_buttons': _infer_playstyle(spec['main_skill'])[1],
            'movement_dependence': _infer_playstyle(spec['main_skill'])[2],
            'aim_requirement': _infer_playstyle(spec['main_skill'])[3],
            'notes': f"Supplemental promoted PoB profile from {case['case_id']}",
        },
        'budget_curve': dict(spec['budget_curve']),
        'availability': dict(spec['availability']),
        'progression': json.loads(json.dumps(spec['progression'])),
        'suitability': dict(spec['suitability']),
        'constraints': json.loads(json.dumps(spec['constraints'])),
        'confidence': {
            'representative_build_status': spec['board_status'],
            'source_count': len(evidence),
            'notes': f"supplemental_promoted_case:{case['case_id']}",
        },
        'evidence': evidence,
    }
    return {
        'candidate_id': candidate_id,
        'league_name': spec['league_name'],
        'build_profile': profile,
        'board_status': spec['board_status'],
        'use_policy': spec['use_policy'],
        'player_facing_default': spec.get('player_facing_default', True),
        'recommendation_visibility': spec.get('recommendation_visibility', 'default'),
        'forward_guard_note': spec.get('forward_guard_note'),
        'case_found': True,
        'source_confidence': spec['source_confidence'],
    }


def build_representative_build_profiles() -> dict:
    board = _load_json(BOARD_PATH)
    cases = _load_json(CASES_PATH)
    queue = _load_json(QUEUE_PATH)
    promoted_case_index = _load_promoted_case_snapshots()

    board_rows = [
        {'patch': patch['patch'], 'league_name': patch['league_name'], **row}
        for patch in board['patches']
        for row in patch['rows']
    ]
    case_index = {(case['patch'], case['archetype_id']): case for case in cases['cases']}
    queue_index = {}
    for patch in queue['patches']:
        for item in patch['queue']:
            queue_index[item['candidate_id']] = item

    profiles = []
    summary = {'confirmed': 0, 'near_confirmed': 0, 'hold': 0}
    for row in board_rows:
        case = case_index.get((row['patch'], row['archetype_id']))
        queue_row = queue_index.get(row['candidate_id'], {})
        identity_seed = _infer_identity(row, case)
        states = _sorted_states(case)
        main_skill, leveling_skill = _main_and_leveling_skill(identity_seed, states)
        transitions = _transition_points(states)
        input_style, manual_buttons, movement_dependence, aim_requirement = _infer_playstyle(main_skill)

        evidence = []
        for family in row.get('guide_source_families', []):
            evidence.append({'type': _evidence_type(family), 'label': f'{family} guide family', 'url': None, 'notes': 'Representative board verified guide family.'})
        for family in row.get('upgradeable_families', []):
            evidence.append({'type': _evidence_type(family), 'label': f'{family} upgradeable family', 'url': None, 'notes': 'Direct index family match for representative board.'})
        for item in (case or {}).get('evidence', []):
            evidence.append({'type': _evidence_type(item.get('type', 'manual_curated')), 'label': item.get('label', 'case evidence'), 'url': None, 'notes': item.get('type')})
        if not evidence:
            evidence.append({'type': 'manual_curated', 'label': 'board-only seed', 'url': None, 'notes': 'No real-case evidence was attached.'})
        evidence = _unique_evidence(evidence)

        progression = {
            'leveling_confidence': 'near_confirmed' if row['status'] != 'hold' else 'inferred',
            'early_mapping_ready': bool(states),
            'transition_points': transitions,
            'campaign_plan': _campaign_plan(states),
            'aura_plan': _aura_plan(states),
            'passive_plan': _passive_plan(states),
            'gear_stages': _gear_stages(states),
        }

        profile = {
            'schema_version': '1.1.0',
            'dataset_kind': 'poe1_build_profile',
            'build_id': row['candidate_id'].replace('.', '_').replace('-', '_'),
            'identity': {
                'build_name': row['build_label'],
                'patch': row['patch'],
                'class_name': identity_seed['class_name'],
                'ascendancy': identity_seed['ascendancy'],
                'main_skill': main_skill,
                'leveling_skill': leveling_skill,
                'damage_tags': [states[-1].get('damage_engine', 'unknown').split()[0]] if states else ['unknown'],
                'weapon_preferences': [],
            },
            'playstyle': {
                'input_style': input_style,
                'manual_buttons': manual_buttons,
                'movement_dependence': movement_dependence,
                'aim_requirement': aim_requirement,
                'notes': f"Representative seed from archetype {row['archetype_id']}",
            },
            'budget_curve': _budget_curve(states, row['status'], (case or {}).get('expected_pairwise_decisions', [])),
            'availability': _availability(states, row, identity_seed['class_name'], identity_seed['ascendancy']),
            'progression': progression,
            'suitability': _suitability(states, main_skill),
            'constraints': _constraints(row, states),
            'confidence': _confidence(row, len(evidence), case),
            'evidence': evidence,
        }
        profiles.append({
            'candidate_id': row['candidate_id'],
            'league_name': row['league_name'],
            'build_profile': profile,
            'board_status': row['status'],
            'use_policy': row['use_policy'],
            'player_facing_default': row.get('player_facing_default', row['status'] != 'hold'),
            'recommendation_visibility': row.get('recommendation_visibility', 'default' if row['status'] != 'hold' else 'hold'),
            'forward_guard_note': row.get('forward_guard_note'),
            'case_found': case is not None,
            'source_confidence': queue_row.get('source_confidence'),
        })
        summary[row['status']] += 1

    supplemental_count = 0
    existing_candidate_ids = {row['candidate_id'] for row in profiles}
    for candidate_id, spec in SUPPLEMENTAL_PROMOTED_PROFILE_SPECS.items():
        if candidate_id in existing_candidate_ids:
            continue
        promoted_case = promoted_case_index.get(spec['preferred_case_id'])
        if not promoted_case:
            continue
        row = _supplemental_profile_from_promoted_case(candidate_id, spec, promoted_case)
        profiles.append(row)
        summary[row['board_status']] += 1
        supplemental_count += 1

    return {
        'dataset_kind': 'poe1_representative_build_profiles',
        'schema_version': '1.0',
        'summary': {
            'profile_count': len(profiles),
            'board_profile_count': len(board_rows),
            'supplemental_promoted_count': supplemental_count,
            **summary,
        },
        'profiles': profiles,
    }


if __name__ == '__main__':
    data = build_representative_build_profiles()
    OUT_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(data['summary'], ensure_ascii=False, indent=2))
