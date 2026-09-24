"""Build review-only Pathcraft candidates from saved sources; never install/export native."""
from pathlib import Path
import collections
import hashlib
import json
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
TREE = Path('D:/Pathcraft-AI/deliverables/skadoosh_hc_2026-09-07/sources/tree_0_5.json')
XML = ROOT / 'linked_update_pob.xml'
START = 47175

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def build():
    tree = read(TREE)
    nodes = {int(n['skill']): n for n in tree['nodes'].values() if isinstance(n, dict) and 'skill' in n}
    assert 'Warrior' in nodes[START]['classesStart']
    specs = ET.parse(XML).getroot().findall('Tree/Spec')[:6]
    provenance = collections.defaultdict(list)
    for spec in specs:
        for n in map(int, spec.get('nodes').split(',')):
            provenance[n].append(spec.get('title'))
    pool = set(provenance)
    adjacency = {n: set() for n in pool}
    source_edges = set()
    for n in pool:
        for edge in nodes[n].get('connections', []):
            v = int(edge['id'])
            if v in pool:
                adjacency[n].add(v)
                adjacency[v].add(n)
                source_edges.add(tuple(sorted((n, v))))

    def exclusion(n, shield):
        d = nodes[n]
        text = ' '.join(d.get('stats', [])).lower()
        if d.get('ascendancyName') or d.get('isAscendancyStart') or d.get('stringId', '').startswith('Ascendancy'):
            return 'foreign_ascendancy'
        if shield and 'two handed' in text:
            return 'two_handed_incompatible_with_selected_one_hand_plus_shield'
        if 'broken armour' in text or ('break' in text and 'armour' in text):
            return 'armour_break_source_not_established_without_warbringer'
        if 'converted to life' in text:
            return 'life_cost_conversion_not_assumed'
        if 'support gems socketed' in text:
            return 'support_colour_threshold_not_established'
        if 'burning enemies' in text or n == 6544:
            return 'burning_uptime_not_established_for_branch'
        return None

    def connected(ids):
        seen = {START}
        q = collections.deque([START])
        while q:
            for v in adjacency[q.popleft()] & ids - seen:
                seen.add(v)
                q.append(v)
        return seen == ids

    def path_to(goal, shield):
        q = collections.deque([START])
        parents = {START: None}
        while q:
            n = q.popleft()
            if n == goal:
                path = []
                while n is not None:
                    path.append(n)
                    n = parents[n]
                return path[::-1]
            for v in sorted(adjacency[n]):
                if v not in parents and exclusion(v, shield) is None:
                    parents[v] = n
                    q.append(v)
        raise AssertionError(f'No source-supported path to {goal}')

    base_targets = ['Brutal', 'Smash', 'Beef', 'Relentless', 'Crushing Verdict']
    stages = [
        ('act1', 'Act 1 late two-handed mace checkpoint', 18, ['Brutal', 'Smash', 'Singular Purpose'], False),
        ('act2', 'Act 2 shield transition checkpoint', 26, base_targets, True),
        ('act3', 'Act 3 shield sustain checkpoint', 37, base_targets + ['Unyielding'], True),
        ('act4', 'Act 4 mobility and cry recovery checkpoint', 47, base_targets + ['Unyielding', 'Momentum', 'Admonisher'], True),
        ('interlude', 'Interlude mobility checkpoint', 56, base_targets + ['Unyielding', 'Momentum', 'Admonisher', 'Light on your Feet', 'Adrenaline Rush'], True),
    ]
    results = []
    previous = {START}
    for key, label, budget, target_names, shield in stages:
        ids, order, paths = {START}, [], []
        for name in target_names:
            goal = next(n for n in pool if nodes[n].get('name') == name)
            path = path_to(goal, shield)
            paths.append({'target': name, 'numeric_ids': path})
            for n in path:
                if n not in ids:
                    assert adjacency[n] & ids
                    order.append(n)
                    ids.add(n)
        assert connected(ids) and len(ids) - 1 == budget
        assert all(exclusion(n, shield) is None for n in ids)
        # Refund only removable nodes: every intermediate state remains connected.
        remaining = set(previous)
        refunds = []
        while remaining - ids:
            candidates = sorted(remaining - ids)
            removable = next((n for n in candidates if connected(remaining - {n})), None)
            assert removable is not None
            remaining.remove(removable)
            refunds.append(removable)
        additions = []
        for n in order:
            if n not in remaining:
                assert adjacency[n] & remaining
                remaining.add(n)
                assert connected(remaining)
                additions.append(n)
        assert remaining == ids
        records = []
        for n in sorted(ids - {START}):
            d = nodes[n]
            records.append({'numeric_id': n, 'string_id': d['stringId'], 'name': d['name'],
                            'stats': d.get('stats', []), 'allocation': 'common',
                            'source': {'file': XML.name, 'spec_titles': provenance[n]},
                            'attribute_choice': 'unresolved: choose against actual gear/gem requirements; no numeric-ID default inferred' if '+5 to any Attribute' in d.get('stats', []) else None,
                            'jewel_socket': bool(d.get('isJewelSocket') or 'jewel_slot' in d.get('stringId', ''))})
        results.append({'id': key, 'label': label, 'classification': 'Pathcraft composition, not author stage restoration',
                        'point_budget': {'common_spent': budget, 'weapon_set_1_extra': 0, 'weapon_set_2_extra': 0,
                                         'active_tree_set_1_total': budget, 'active_tree_set_2_total': budget,
                                         'ascendancy_spent': 0, 'class_start_cost': 0,
                                         'gate': 'Actual available ordinary passive budget >= common_spent; no act completion, character level, quest points or weapon-set points assumed'},
                        'weapon_condition': 'one-handed mace plus armour shield; maintain actual requirements on both sets' if shield else 'two-handed mace equipped; no shield phase yet',
                        'skill_condition': 'Shield Wall gem obtained and usable; Shockwave Totem and/or Shield Charge for wall breaking, Infernal Cry subject to real cooldown, no Warbringer cooldown-ignore assumed' if shield else 'Rolling Slam/Boneshatter with melee heavy-stun play; use Perfect Strike only after actual gem requirements',
                        'ids_including_start_for_graph': sorted(ids), 'nodes': records,
                        'native_candidate_ids_excluding_start': [r['string_id'] for r in records],
                        'path_witnesses': paths,
                        'allocation_witness_not_author_click_order': order,
                        'transition_from_previous': {'refund_numeric_ids_in_safe_order': refunds, 'refund_count': len(refunds),
                                                     'add_numeric_ids_in_safe_order': additions, 'add_count': len(additions),
                                                     'net_extra_points': len(ids) - len(previous),
                                                     'currency_cost': 'not derived; verify actual refund affordability before changing weapon'},
                        'validation': {'connected_from_warrior_start': True, 'all_steps_connected': True,
                                       'all_ids_from_saved_specs': True, 'all_path_edges_from_saved_tree': True,
                                       'no_foreign_ascendancy': True, 'no_shield_twohand_conflict': True,
                                       'both_weapon_sets_connected': True, 'no_extra_weapon_set_budget_required': True}})
        previous = ids
    bridge = set(results[0]['ids_including_start_for_graph']) - set(results[1]['transition_from_previous']['refund_numeric_ids_in_safe_order'])
    assert connected(bridge) and len(bridge) - 1 == 13
    assert all(exclusion(n, True) is None for n in bridge)
    effect_review = {
        'Brutal': 'Melee damage and stun buildup support the early mace hit/stun plan; no claim that every Shield Wall damage component is melee. Strength is a fixed stat.',
        'Smash': 'Melee damage supports mace melee hits; the larger bonus requires the enemy to be Heavy Stunned. Shield Wall component scaling remains unverified.',
        'Singular Purpose': 'Only the two-handed mace checkpoint; reduced attack speed is a real downside. Refund before one-handed mace plus shield.',
        'Beef': 'Fixed Strength supports requirements only after actual equipment/gem comparison; does not certify sufficient attributes.',
        'Relentless': 'Armour and life regeneration are generic defensive effects, independent of Warbringer. No survivability guarantee.',
        'Sturdy Metal': 'Increases armour from body armour, not armour from the shield. Requires actual body armour with armour; never label as direct shield damage scaling.',
        'Crushing Verdict': 'Generic attack damage and stun buildup target attack hits; reduced attack speed is a downside. Does not establish wall detonation/minion damage scaling or cry damage.',
        'Unyielding': 'Attack speed is conditional on having been hit recently; slow mitigation is separate. No permanent attack-speed or warcry-speed assumption.',
        'Momentum': 'Armour movement penalties and slowing debuffs only; not damage, not all movement penalties.',
        'Admonisher': 'Warcry speed and cooldown recovery support Infernal Cry subject to real cooldown. Does not grant Warbringer cooldown-ignore or corpse explosion.',
        'Light on your Feet': 'Movement speed plus Hinder/Maim immunity; not general immunity to every slow.',
        'Adrenaline Rush': 'Attack/movement bonuses require a recent kill; not reliable on an isolated boss.'
    }
    selected = set(n for s in results for n in s['ids_including_start_for_graph'])
    result = {'schema_version': 1, 'task': 'task_1cf1e68c4497', 'dispatch': 'ctx_856e8b405bae',
              'status': 'structurally_validated_review_candidates_not_game_verified',
              'sources': [{'path': str(p), 'sha256': sha(p)} for p in (TREE, XML)],
              'start': {'numeric_id': START, 'string_id': nodes[START]['stringId'], 'classes': nodes[START]['classesStart']},
              'composition_policy': 'Deterministic source-pool shortest paths to explicitly chosen targets; numeric Spec titles never mapped to acts; all allocations common',
              'notable_effect_review': effect_review,
              'insufficient_points_policy': 'Retain previous checkpoint AND its weapon setup; act arrival is not an instruction to spend unavailable points. If swapping to shield early, use only validated bridge after affordable refunds, then connected prefixes of the act2 witness.',
              'shield_bridge': {'ordinary_points': 13, 'ids_including_start_for_graph': sorted(bridge),
                                'native_candidate_ids_excluding_start': [nodes[n]['stringId'] for n in sorted(bridge - {START})],
                                'common': True, 'connected': True, 'foreign_ascendancy': False,
                                'note': 'Fallback, not a sixth act checkpoint or a damage/attribute guarantee'},
              'assumptions': ['Budgets are Pathcraft design choices and eligibility gates, not sourced act rewards or levels',
                              'Passive edges are treated as undirected as in the saved connection graph',
                              'Class start costs zero and is a graph anchor, not an exported spendable passive',
                              'Empty jewel sockets can be paid travel nodes; no jewel is required or assumed',
                              'Ascendancy and attribute choices remain separate from this common-tree candidate'],
              'selected_source_edges': [list(e) for e in sorted(source_edges) if set(e) <= selected],
              'shield_exclusions': [{'numeric_id': n, 'string_id': nodes[n].get('stringId'), 'name': nodes[n].get('name'), 'reason': exclusion(n, True)} for n in sorted(pool) if exclusion(n, True)],
              'checkpoints': results,
              'limits': ['No current-client rendering, damage calculation or live equipment validation',
                         'No claim that melee modifiers scale every Shield Wall component',
                         'Conditional heavy-stun/recent-hit/recent-kill bonuses are not guaranteed uptime',
                         'High-level endgame transition needs a separate diff and refund plan',
                         'Do not spend unavailable points or weapon-specific points as ordinary common points']}
    output = ROOT / 'campaign_checkpoint_candidates.json'
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'output': str(output), 'budgets': [s['point_budget']['common_spent'] for s in results],
                      'refunds': [s['transition_from_previous']['refund_count'] for s in results],
                      'status': result['status']}, ensure_ascii=False))

if __name__ == '__main__':
    build()
