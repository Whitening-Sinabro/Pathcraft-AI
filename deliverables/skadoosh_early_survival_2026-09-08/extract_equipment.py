"""Compact provenance-preserving extracts used by the survival report."""
from pathlib import Path
import hashlib
import json

OUT = Path(__file__).resolve().parent
SOURCE = OUT.parent / 'skadoosh_hc_2026-09-07/sources'
tree = json.loads((SOURCE / 'tree_0_5.json').read_text(encoding='utf-8'))['nodes']
files = ['ninja_hour18_lv24.json', 'lv34_0906_0320.json', 'lv43_0906_0523.json']
records = []
for filename in files:
    source = SOURCE / filename
    d = json.loads(source.read_text(encoding='utf-8'))
    row = {'source': str(source), 'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
           'character': d['name'], 'level_observed': d['level'], 'items': [], 'skills': [], 'passives': []}
    for entry in d['items'] + d['flasks']:
        item = entry['itemData']
        row['items'].append({k: item.get(k) for k in
            ['inventoryId', 'name', 'baseType', 'implicitMods', 'explicitMods', 'runeMods',
             'properties', 'requirements']})
    for skill in d['skills']:
        gem = skill['allGems'][0]
        row['skills'].append({'name': gem['name'], 'level': gem.get('level'),
            'supports': [x['typeLine'] for x in gem['itemData'].get('socketedItems', [])],
            'gem_tabs': gem['itemData'].get('gemTabs')})
    for key in ['passiveSelection', 'passiveSelectionSet1', 'passiveSelectionSet2']:
        for node_id in d[key]:
            n = tree[str(node_id)]
            if n.get('isNotable') or n.get('ascendancyName'):
                row['passives'].append({'allocation': key, 'name': n['name'],
                    'id': n['stringId'], 'stats': n['stats']})
    row['resistance_caveat'] = 'Raw defensiveStats have a -60 base elemental resistance term; not treated as campaign UI values.'
    row['bonded_caveat'] = 'ShamanOnlyMods/Bonded lines retained for provenance, not counted as active Warbringer stats.'
    records.append(row)
(OUT / 'equipment_evidence.json').write_text(json.dumps(records, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print('Extracted', len(records), 'observed snapshots; source hashes retained.')
