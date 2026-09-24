"""Audit the Korean delivery and make a player-only archive."""
import hashlib, json, re, zipfile
from pathlib import Path
HERE = Path(__file__).resolve().parent
OUT = HERE / 'ready'
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
acceptance = read(HERE / 'validation_acceptance.json')
ko = read(HERE / 'validation_korean.json')
assert len(acceptance['filters']) == 3 and len(acceptance['planners']) == 9
assert all(f['sweep_regressions'] == 0 for f in acceptance['filters'])
for p in (OUT/'Filters').glob('*.filter'):
    assert hashlib.sha256(p.read_bytes()).hexdigest() == ko['filters_unchanged_since_sweep'][p.name]
tree = read(HERE/'sources/tree_0_5.json')
nodes = {n['stringId']:n for n in tree['nodes'].values() if 'stringId' in n}
counts = []
for p in sorted((OUT/'BuildPlanner').glob('*.build')):
    d = read(p)
    assert set(d) == {'author','link','ascendancy','inventory_slots','name','passives','skills'}
    assert all(n['id'] in nodes for n in d['passives'])
    assert len(d['name']) <= 40
    invs = set()
    for i in d['inventory_slots']:
        assert set(i) <= {'inventory_id','slot_x','slot_y','level_interval','additional_text','unique_name'}
        key = i['inventory_id'], i['slot_x'], i['slot_y']
        assert key not in invs
        invs.add(key)
        if i.get('additional_text'):
            assert re.search('[가-힣]',i['additional_text']), (p.name, i)
            assert not re.search(r'^\d+\. [^\n]*(?:increased|maximum|Regeneration|Adds|Resistance)',i['additional_text'],re.M)
    weapons = [i for i in d['inventory_slots'] if i['inventory_id'] in ('Weapon1','Weapon2')]
    assert len(weapons) == 2
    assert all('스킬과 그 안에 꽂을 보조' in w['additional_text'] for w in weapons)
    full_notes = '\n'.join(i.get('additional_text','') for i in d['inventory_slots'])
    assert '전환 조건' in full_notes and '스킬 운영' in full_notes and '보조 젬을 넣는 곳' in full_notes
    ws = [sum(n.get('weapon_set')==i for n in d['passives']) for i in (1,2)]
    counts.append((d['name'],ws))
    # Skill and support labels must each appear at least once in the notes.
    titles = {r['name']:r['title'].split(' - PoE2DB')[0] for r in read(HERE/'sources/gem_korean_titles.json')}
    bases = {b['Id']:b['Name'] for b in read(HERE.parents[1]/'data/game_data_poe2/BaseItemTypes.json')}
    for s in d['skills']:
        for g in [s]+s.get('support_skills',[]):
            assert titles[bases[g['id']]] in full_notes
            assert 1 <= g['level_interval'][0] <= g['level_interval'][1] == 100
# Source items may retain their English search names; all instructional prose is Korean.
for name in ('시작안내.md','무기세트와젬연결.md','패시브전환.md','검증결과.md'):
    assert (OUT/name).exists()
    for link in re.findall(r'\]\(([^)]+)\)',(OUT/name).read_text(encoding='utf-8')):
        if not re.match(r'https?://',link): assert (OUT/link).exists(), (name,link)
files = sorted(p for p in OUT.rglob('*') if p.is_file() and p.name != 'SHA256SUMS.txt')
assert len([p for p in files if p.suffix=='.build']) == 9
assert len([p for p in files if p.suffix=='.filter']) == 3
manifest = ''.join(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(OUT).as_posix()}\n' for p in files)
(OUT/'SHA256SUMS.txt').write_text(manifest, encoding='utf-8')
dest = HERE/'Skadoosh-HC-한국어-필터와플래너.zip'
with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED) as z:
    for p in sorted(p for p in OUT.rglob('*') if p.is_file()): z.write(p,p.relative_to(OUT).as_posix())
with zipfile.ZipFile(dest) as z:
    assert z.testzip() is None
    for p in sorted(p for p in OUT.rglob('*') if p.is_file()): assert z.read(p.relative_to(OUT).as_posix()) == p.read_bytes()
report = {'final_korean_notes_and_links_checked':True, 'inventory_slots_unique':True, 'all_gem_connections_documented':True,
          'weapon_set_points':counts, 'zip_crc_and_bytes_equal':True, 'zip_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),
          'zip_file':str(dest), 'bytes':dest.stat().st_size,'player_files':len(files)+1}
(HERE/'validation_final.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
