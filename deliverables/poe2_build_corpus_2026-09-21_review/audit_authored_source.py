import collections
import hashlib
import json
from pathlib import Path

SOURCE = Path('C:/Users/User/orca/workspaces/Pathcraft-AI/readiness-audit-20260921/deliverables/poe2_build_corpus_2026-09-21/lundburgerr_authored')
OUT = Path(__file__).parent
GAME = Path('D:/Pathcraft-AI/data/game_data_poe2')
TREE = Path('D:/Pathcraft-AI/deliverables/skadoosh_hc_2026-09-07/sources/tree_0_5.json')

def read(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))

tree = read(TREE)['nodes']
nodes = {n['stringId']: n for n in tree.values() if 'stringId' in n}
id_to_string = {int(k): n['stringId'] for k, n in tree.items() if 'stringId' in n}
adj = collections.defaultdict(set)
for key, n in tree.items():
    a = id_to_string.get(int(key))
    if a is None:
        continue
    for edge in n.get('connections', []):
        b = id_to_string.get(edge['id'])
        if b:
            adj[a].add(b)
            adj[b].add(a)

base = read(GAME / 'BaseItemTypes.json')
gems = {base[g['BaseItemType']]['Id']: g for g in read(GAME / 'SkillGems.json') if 0 <= g['BaseItemType'] < len(base)}
base_by_id = {n['Id']: n for n in base}

def free(n):
    return bool(n.get('classesStart') or n.get('isAscendancyStart') or n.get('isFreeAllocate'))

def reach(allowed, start):
    seen = {start}
    todo = [start]
    while todo:
        for nxt in adj[todo.pop()] & allowed - seen:
            seen.add(nxt)
            todo.append(nxt)
    return sorted(allowed - seen)

results = []
for f in sorted((SOURCE / 'raw_native').glob('*.build')):
    d = read(f)
    groups = {s: {n['id'] for n in d['passives'] if n.get('weapon_set', 0) == s} for s in (0, 1, 2)}
    all_ids = set.union(*groups.values())
    unknown = sorted(all_ids - nodes.keys())
    assert not unknown, (f, unknown)
    ordinary = {i for i in all_ids if not nodes[i].get('ascendancyName') and not free(nodes[i])}
    asc = {i for i in all_ids if nodes[i].get('ascendancyName')}
    active = {}
    for s in (1, 2):
        paid = (groups[0] | groups[s]) & ordinary
        active[str(s)] = {'ordinary_points': len(paid), 'specialized_points': len(groups[s] & ordinary), 'disconnected': reach(paid | {'marauder594'}, 'marauder594')}
    skill_rows = []
    for g in d.get('skills', []):
        skill_rows.append({'id': g['id'], 'name': base_by_id[g['id']]['Name'], 'minimum_character_level': gems.get(g['id'], {}).get('MinLevelReq'), 'supports': [{'id': z['id'], 'name': base_by_id.get(z['id'], {}).get('Name'), 'metadata_exists': z['id'] in gems} for z in g.get('support_skills', [])]})
    row = {'file': f.name, 'sha256': hashlib.sha256(f.read_bytes()).hexdigest(), 'raw_rows': len(d['passives']), 'unique_allocations': sum(map(len, groups.values())), 'common_ordinary': len(groups[0] & ordinary), 'active_sets': active, 'paid_ascendancy': sum(not free(nodes[i]) for i in asc), 'free_ids': sorted(i for i in all_ids if free(nodes[i])), 'ascendancy_disconnected': reach(asc | {'AscendancyWarrior3Start'}, 'AscendancyWarrior3Start'), 'skills': skill_rows}
    results.append(row)
    print(f.name, 'ordinary', [active[str(s)]['ordinary_points'] for s in (1, 2)], 'asc', row['paid_ascendancy'], 'disconnected', [len(active[str(s)]['disconnected']) for s in (1, 2)], 'skills', len(skill_rows))

report = {'source': str(SOURCE), 'tree_sha256': hashlib.sha256(TREE.read_bytes()).hexdigest(), 'scope': 'Independent static verification of original author exports. Graph connectivity and metadata do not prove combat safety, affordability, current earned points, or exact author allocation order.', 'variants': results}
(OUT / 'authored-source-independent-audit.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')

doc_results = []
for v in read(SOURCE / 'authored_document.json')['data']['buildVariants']['values']:
    groups = {k: {id_to_string[int(s.split('-')[-1])] for s in (z.get('selectedSlugs') or [])} for k, z in v['passiveTree'].items() if isinstance(z, dict)}
    common = groups['mainTree']
    asc = groups['ascendancyTree']
    row = {'variant_id': v['id'], 'paid_ascendancy': sum(not free(nodes[i]) for i in asc), 'ascendancy_disconnected': reach(asc | {'AscendancyWarrior3Start'}, 'AscendancyWarrior3Start'), 'sets': {}}
    for s in (1, 2):
        group = groups['set' + str(s) + 'Tree']
        active = common | group
        row['sets'][str(s)] = {'common': len(common), 'specialized': len(group), 'common_overlap': sorted(common & group), 'ordinary_points': sum(not free(nodes[i]) for i in active), 'disconnected': reach(active | {'marauder594'}, 'marauder594')}
    doc_results.append(row)
print('Authored document:', json.dumps(doc_results))
(OUT / 'authored-document-independent-audit.json').write_text(json.dumps(doc_results, indent=2), encoding='utf-8')
