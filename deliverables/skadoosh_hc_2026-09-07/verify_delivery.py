"""Independent filter evaluation and native planner shape / source acceptance checks."""
import base64, collections, contextlib, hashlib, importlib.util, io, json, re, sys, zipfile, zlib
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
OUT, SRC = HERE / 'ready', HERE / 'sources'
def read(path): return json.loads(path.read_text(encoding='utf-8-sig'))
def module(name, file):
    spec = importlib.util.spec_from_file_location(name, REPO / 'scripts' / file)
    mod = importlib.util.module_from_spec(spec); sys.modules[name] = mod; spec.loader.exec_module(mod)
    return mod

sweep = module('delivery_sweep', 'poe2_filter_sweep.py')
sweep.GAME_CLASS_TO_FILTER_CLASS['Sceptres'] = 'Sceptres'
ev = sweep.load_eval()
report = {'filters': [], 'planners': [], 'limits': ['게임 클라이언트 로딩/실전 플레이 미검증', '미가공 젬 GemLevel 등 기존 평가기가 모델링하지 않는 조건은 원본 보존으로 보호; 해당 조건의 시뮬레이션 통과를 주장하지 않음']}
log = io.StringIO()
for name, base in [('01-Campaign', 'soft'), ('02-EarlyMaps', 'regular'), ('03-SettledMaps', 'strict')]:
    original = SRC / f'neversink_0.10.4_{base}.filter'
    output = OUT / 'Filters' / f'Pathcraft-Skadoosh-HC-{name}.filter'
    with contextlib.redirect_stdout(log):
        bad = sweep.sweep(original, output, True)
    assert bad == 0, (name, log.getvalue()[-3000:])
    bb, ob = ev.load(original), ev.load(output)
    only = ev.parse(sweep.overlay_only(output))
    assert not ev.unmodelled_conditions(only)
    assert all(b.action == 'Show' for b in only)
    classes = sweep.class_index(ev, bb)
    for r in read(HERE / 'filter_spec.json')['rules']:
        if r.get('class') == ['Sceptres']:
            classes.update({b: 'Sceptres' for b in r['base_types']})
    samples = []
    for area in (35, 50, 52, 60, 65, 70, 80):
        for bt, cls, rarity in [('Shrine Sceptre', 'Sceptres', 'Rare'), ('Solar Amulet', 'Amulets', 'Rare'), ('Morning Star', 'One Hand Maces', 'Rare'), ('Amethyst Charm', 'Charms', 'Magic'), ("Jiquani's Soul Core of Rallying", 'Augment', 'Normal')]:
            # Morning Star's crafting band ends at AREA level 60, regardless of player level.
            if bt == 'Morning Star' and area > 60:
                continue
            result = ev.evaluate(ob, ev.Item(bt, cls, rarity, area_level=area, item_level=area))
            assert result.visible, (name, bt, area)
            samples.append({'base': bt, 'area': area, 'visible': True})
    unique_checks = 0
    for bt, cls in [('Flanged Mace', 'One Hand Maces'), ('Ruby', 'Jewels'), ('Shrine Sceptre', 'Sceptres'), ('Jade Amulet', 'Amulets')]:
        for area in (35, 65, 80):
            item = ev.Item(bt, cls, 'Unique', area_level=area, item_level=area)
            a, b = ev.evaluate(bb, item), ev.evaluate(ob, item)
            assert (a.visible, a.font, a.volume, a.sound_id, a.icon_size) == (b.visible, b.font, b.volume, b.sound_id, b.icon_size)
            unique_checks += 1
    report['filters'].append({'file': output.name, 'sweep_regressions': 0, 'overlay_unmodelled_conditions': {}, 'upstream_unmodelled_conditions': ev.unmodelled_conditions(bb), 'progression_samples': len(samples), 'unique_controls_equal': unique_checks})
(HERE / 'filter_sweep.txt').write_text(log.getvalue(), encoding='utf-8')

data = [read(p) for p in sorted((OUT / 'BuildPlanner').glob('*.build'))]
assert len(data) == 9
tree = read(SRC / 'tree_0_5.json')
known_nodes = {n['stringId'] for n in tree['nodes'].values() if 'stringId' in n}
known_gems = {b['Id'] for b in read(REPO / 'data/game_data_poe2/BaseItemTypes.json')}
with zipfile.ZipFile(SRC / 'mobalytics_original.zip') as archive:
    original = json.loads(archive.read(next(n for n in archive.namelist() if n.startswith('Imported -'))).decode('utf-8-sig'))
schema = set(original)
for d in data:
    assert set(d) == schema
    assert d['ascendancy'] == original['ascendancy'] == 'Warrior2'
    assert len(d['name']) <= 40
    assert len({(p['id'], p.get('weapon_set', 0)) for p in d['passives']}) == len(d['passives'])
    assert {p['id'] for p in d['passives']} <= known_nodes
    assert all(set(p) <= {'id', 'weapon_set'} and p.get('weapon_set', 1) in (1, 2) for p in d['passives'])
    count = 0
    for s in d['skills']:
        assert set(s) <= {'id', 'level_interval', 'support_skills'}
        for e in [s] + s.get('support_skills', []):
            assert e['id'] in known_gems
            assert 1 <= e['level_interval'][0] <= e['level_interval'][1] == 100
            count += 1
    report['planners'].append({'file': d['name'], 'native_export_shape': True, 'known_gem_entries': count, 'upper_level_100': True})
latest = data[-1]
original_awt = next(s for s in original['skills'] if s['id'].endswith('SkillGemAncestralWarriorTotem'))
our_awt = next(s for s in latest['skills'] if s['id'].endswith('SkillGemAncestralWarriorTotem'))
assert [s['id'] for s in our_awt['support_skills']] == [s['id'] for s in original_awt['support_skills']]
purities = [s for s in latest['skills'] if s['id'].endswith('SkillGemPurityOfFire')]
assert len(purities) == 2 and purities[0]['support_skills'] != purities[1]['support_skills']
report['AWT_nested_active_matches_creator_export'] = True
report['two_distinct_sceptre_Purity_groups_preserved'] = True
# Compare every explicit actual socket group with the decoded independent source XML.
sources = read(HERE / 'planner_sources.json')
for d, s in zip(data, sources):
    filename = s['source'].split(';')[0]
    if not filename.endswith('.json'):
        continue
    model = read(SRC / filename); encoded = model['pathOfBuildingExport']
    root = ET.fromstring(zlib.decompress(base64.urlsafe_b64decode(encoded + '='*(-len(encoded)%4))))
    expected = []
    for group in root.findall('.//Skill'):
        if group.get('source'):
            continue
        gems = tuple(g.get('gemId') for g in group.findall('Gem') if g.get('gemId'))
        if gems: expected.append(gems)
    actual = [(g['id'], *(s['id'] for s in g.get('support_skills', []))) for g in d['skills']]
    assert collections.Counter(expected) == collections.Counter(actual), d['name']
report['six_observed_stages_explicit_socket_groups_equal'] = True
(HERE / 'validation_acceptance.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(log.getvalue())
print('PASS: 9 planners, 3 filters, AWT nested Earthshatter, 2 distinct Purity groups, source socket groups, level-100 upper bounds.')
