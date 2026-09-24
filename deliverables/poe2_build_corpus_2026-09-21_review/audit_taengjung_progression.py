"""Independent review of delivered native files against raw source/tree tables."""
import collections
import hashlib
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

BASE = Path(sys.argv[1])
OUT = Path(__file__).parent
CANON = Path('D:/Pathcraft-AI/deliverables/poe2_build_corpus_2026-09-21')
DATA = Path('D:/Pathcraft-AI/data/game_data_poe2')

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

raw = read(Path('D:/Pathcraft-AI/deliverables/skadoosh_hc_2026-09-07/sources/tree_0_5.json'))['nodes']
nodes = {int(k): v for k, v in raw.items()}
by_string = {v['stringId']: n for n, v in nodes.items() if 'stringId' in v}
edges = collections.defaultdict(set)
for n, v in nodes.items():
    for edge in v.get('connections', []):
        edges[n].add(int(edge['id']))
        edges[int(edge['id'])].add(n)

def reached(selected, start):
    seen, queue = {start}, [start]
    for n in queue:
        for v in (edges[n] & selected) - seen:
            seen.add(v)
            queue.append(v)
    return seen

def is_free(n):
    v = nodes[n]
    return bool(v.get('classesStart') or v.get('isAscendancyStart') or v.get('isFreeAllocate'))

def verify_graph(mapping):
    for w in (1, 2):
        selected = {47175} | {n for n, s in mapping.items() if s in (0, w)}
        assert reached(selected, 47175) == selected, ('ordinary disconnected', w)

source = ET.parse(CANON / 'priority_29d39.xml').getroot().find('Tree/Spec')
source_ids = {int(v) for v in source.get('nodes').split(',') if v}
source_sets = {w: {int(v) for v in source.find('WeaponSet' + str(w)).get('nodes').split(',') if v} for w in (1, 2)}
source_mapping = {n: 1 if n in source_sets[1] else 2 if n in source_sets[2] else 0 for n in source_ids}
base_items = read(DATA / 'BaseItemTypes.json')
gem_table = {base_items[g['BaseItemType']]['Id']: g for g in read(DATA / 'SkillGems.json')}
contract_path = BASE / 'taengjung_progression/planner_contract.json'
contract = read(contract_path)
results, previous, previous_asc = [], {}, set()
for stage in contract['stages']:
    path = BASE / stage['native_file']
    native = read(path)
    assert sha(path) == stage['native_sha256']
    # Installed stages carry their game-list number; phase 1 is the uninstalled 40-level alternative.
    prefix = f"{stage['display_number']:02d}" if stage.get('display_number') else '대안'
    assert native['name'].startswith(prefix), ('unsequenced native name', path.name)
    actual_rows = [(by_string[p['id']], p.get('weapon_set', 0)) for p in native['passives']]
    assert len(actual_rows) == len(set(actual_rows)), 'duplicate native passive'
    actual = dict(actual_rows)
    expected = {p['numeric_id']: p['weapon_set'] for p in stage['passives'] + stage['ascendancy_nodes'] if p['numeric_id'] != 5852}
    assert actual == expected
    ordinary = {n: w for n, w in actual.items() if not nodes[n].get('ascendancyName')}
    asc = {5852} | {n for n in actual if nodes[n].get('ascendancyName')}
    assert all(not is_free(n) for n in ordinary)
    assert ordinary.keys() <= source_ids
    assert all(source_mapping[n] == w for n, w in ordinary.items()), 'changed author weapon membership'
    verify_graph(ordinary)
    assert reached(asc, 5852) == asc, 'ascendancy disconnected'
    normal_count = max(sum(w in (0, s) for w in ordinary.values()) for s in (1, 2))
    weapon_count = max(sum(w == s for w in ordinary.values()) for s in (1, 2))
    paid_asc = sum(not is_free(n) for n in asc)
    budget = stage['budgets']
    assert normal_count == budget['ordinary_points_required']
    assert weapon_count == budget['weapon_specialization_capacity_required']
    assert paid_asc == budget['ascendancy_points_required'] <= 8
    state = dict(previous)
    for operation in stage['diff_from_previous']['operations']:
        n, w = operation['numeric_id'], operation['weapon_set']
        assert operation['action'] == 'allocate' and n not in state
        state[n] = w
        verify_graph(state)
    assert state == ordinary, 'stage replay mismatch'
    assert stage['diff_from_previous']['ordinary_refunds'] == 0
    asc_state = set(previous_asc)
    for operation in stage['diff_from_previous']['ascendancy_operations']:
        n = operation['numeric_id']
        if operation['action'] == 'refund':
            asc_state.remove(n)
        else:
            assert n not in asc_state
            asc_state.add(n)
        assert reached(asc_state, 5852) == asc_state
    assert asc_state == asc
    groups = stage['skill_groups']
    assert len(native['skills']) == len(groups)
    minimum, socket_groups = 0, []
    for native_group, group in zip(native['skills'], groups):
        native_gems = [native_group, *native_group.get('support_skills', [])]
        assert [g['id'] for g in native_gems] == [g['id'] for g in group['gems']]
        assert len(native_gems) - 1 <= 4, 'requires undeclared Perfect Jeweller'
        socket_groups.append({'active': group['active'], 'supports': len(native_gems) - 1})
        for row, gem in zip(native_gems, group['gems']):
            assert row['level_interval'] == [1, 100]
            current = gem_table[row['id']]
            assert gem['min_character_level'] == current['MinLevelReq']
            minimum = max(minimum, current['MinLevelReq'])
    assert all(p['level_interval'] == [1, 100] for p in native['passives'])
    if stage['index'] == 1:
        assert normal_count <= 39 and minimum <= 40
        assert not ({24766, 25711, 59208} & ordinary.keys()), 'premature surround nodes'
    results.append({'stage': stage['id'], 'file': path.name, 'sha256': sha(path), 'ordinary': normal_count, 'weapon_capacity': weapon_count, 'ascendancy_paid': paid_asc, 'core_min_character_level': minimum, 'skills': socket_groups, 'ordinary_refunds': 0, 'direct_author_subset': True, 'each_step_connected': True})
    previous, previous_asc = ordinary, asc

protected = read(BASE / 'taengjung_progression/source_hashes.json')
for path, expected in protected.items():
    assert sha(Path(path)) == expected, ('changed protected source', path)
report = {'status': 'passed', 'contract_sha256': sha(contract_path), 'stages': results, 'protected_files': len(protected), 'limits': 'Static source, graph, format, points and minimum base-gem requirements. Actual player allocation, selected gem levels, attributes, equipment, Spirit and combat survival are not inferred.'}
(OUT / 'taengjung-independent-audit.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(report, ensure_ascii=False))
