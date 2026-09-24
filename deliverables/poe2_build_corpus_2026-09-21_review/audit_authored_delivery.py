import collections
import hashlib
import json
import sys
from pathlib import Path

CORPUS = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('C:/Users/User/orca/workspaces/Pathcraft-AI/readiness-audit-20260921/deliverables/poe2_build_corpus_2026-09-21')
OUT = Path(__file__).parent

def read(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))

tree = read(Path('D:/Pathcraft-AI/deliverables/skadoosh_hc_2026-09-07/sources/tree_0_5.json'))['nodes']
nodes = {int(k): v for k, v in tree.items()}
by_string = {v['stringId']: int(k) for k, v in tree.items() if 'stringId' in v}
adj = collections.defaultdict(set)
for k, n in nodes.items():
    for edge in n.get('connections', []):
        adj[k].add(edge['id'])
        adj[edge['id']].add(k)

def free(n):
    return bool(nodes[n].get('classesStart') or nodes[n].get('isAscendancyStart') or nodes[n].get('isFreeAllocate'))

def reachable(ids, start):
    seen = {start}
    queue = [start]
    for n in queue:
        for v in adj[n] & ids - seen:
            seen.add(v)
            queue.append(v)
    return seen

def budget(m):
    return max(sum(w in (0, s) for w in m.values()) for s in (1, 2))

def connected(m):
    for s in (1, 2):
        ids = {n for n, w in m.items() if w in (0, s)} | {47175}
        assert reachable(ids, 47175) == ids

pack = read(CORPUS / 'planner_data/build_data.json')
stage_index = {s['id']: s for s in [*pack['stages'], *pack['authored_stages']]}

def model(s):
    sets = {int(n): int(w) for w, ns in s.get('weapon_set_nodes', {}).items() for n in ns}
    normal, asc = {}, set()
    for row in s['passives']:
        n = int(row['id'])
        if nodes[n].get('ascendancyName'):
            asc.add(n)
        elif not free(n):
            normal[n] = sets.get(n, 0)
    return normal, asc

checks = []
for seg in pack['transition_plan']['segments']:
    start, old_asc = ({}, set()) if seg['from_stage'] == 'start' else model(stage_index[seg['from_stage']])
    target, new_asc = model(stage_index[seg['to_stage']])
    state = dict(start)
    allowed = start.keys() | target.keys()
    seen_actions = collections.Counter()
    peak, weapon_peak = budget(state), 0
    for op in seg['steps']:
        n, w = op['numeric_id'], op['weapon_set']
        assert n in allowed and by_string[op['string_id']] == n
        seen_actions[(op['action'], n, w)] += 1
        if op['action'] == 'refund':
            assert state.pop(n) == w
        else:
            assert n not in state
            state[n] = w
        connected(state)
        b = budget(state)
        assert b == op['budget_after']['ordinary_points_required']
        peak = max(peak, b)
        weapon_peak = max(weapon_peak, *(sum(v == s for v in state.values()) for s in (1, 2)))
    assert state == target
    assert peak == seg['ordinary_peak']
    assert weapon_peak <= seg['weapon_capacity_peak']
    paid_old = sum(not free(n) for n in old_asc)
    paid_new = sum(not free(n) for n in new_asc)
    assert seg['from_budget']['ascendancy_points_required'] == paid_old
    assert seg['to_budget']['ascendancy_points_required'] == paid_new
    asc = set(old_asc)
    if seg.get('ascendancy_steps') and not asc:
        asc = {5852}
    for op in seg.get('ascendancy_steps', []):
        n = op['numeric_id']
        if op['action'] == 'refund':
            asc.remove(n)
        else:
            assert n not in asc
            asc.add(n)
        assert reachable(asc, 5852) == asc
        assert sum(not free(v) for v in asc) == op['paid_ascendancy_after']
    assert asc == new_asc
    cycles = [k for k, count in seen_actions.items() if count > 1]
    assert not cycles, (seg['id'], cycles)
    checks.append({'segment': seg['id'], 'refunds': sum(o['action'] == 'refund' for o in seg['steps']), 'adds': sum(o['action'] == 'add' for o in seg['steps']), 'ordinary_peak': peak, 'specialization_peak': weapon_peak, 'paid_ascendancy': paid_new, 'repeated_actions': len(cycles), 'replay_connected': True})

native_checks = []
for stage in pack['campaign_stages'] + pack['transition_stages']:
    p = CORPUS / 'native_planner' / stage['authored_checkpoint']['native_file']
    native = read(p)
    normal, asc = model(stage)
    actual = {(by_string[r['id']], r.get('weapon_set', 0)) for r in native['passives']}
    expected = set(normal.items()) | {(n, 0) for n in asc}
    assert actual == expected and len(actual) == len(native['passives'])
    for r in native['passives'] + native['skills']:
        assert r['level_interval'] == [1, 100]
        for g in r.get('support_skills', []):
            assert g['level_interval'] == [1, 100]
    assert budget(normal) == stage['authored_checkpoint']['budgets']['ordinary_points_required']
    assert sum(not free(n) for n in asc) == stage['authored_checkpoint']['budgets']['ascendancy_points_required']
    assert len(native['skills']) == len(stage['skills'])
    native_checks.append({'file': p.name, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest(), 'skills': len(native['skills']), 'passives': len(native['passives']), 'ordinary': budget(normal)})

report = {'status': 'passed', 'corpus': str(CORPUS), 'pack_sha256': hashlib.sha256((CORPUS / 'planner_data/build_data.json').read_bytes()).hexdigest(), 'segments': checks, 'native': native_checks, 'limits': 'Static replay, graph, metadata and point accounting; no observed gameplay survival, actual user allocation, or trade prices.'}
(OUT / 'authored-delivery-independent-audit.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(report, ensure_ascii=True))
