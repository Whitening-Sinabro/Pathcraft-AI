"""Independent serialized-file acceptance checks, including source comparisons."""
from pathlib import Path
import base64,collections,hashlib,json,re,xml.etree.ElementTree as E,zlib
HERE=Path(__file__).resolve().parent;OUT=HERE/'revision3'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
N={n['stringId']:n for n in read(HERE/'sources/tree_0_5.json')['nodes'].values() if 'stringId'in n};NUM={n['skill']:k for k,n in N.items()};adj=collections.defaultdict(set)
for k,n in N.items():
    for c in n.get('connections',[]):
        if c['id']in NUM:adj[k].add(NUM[c['id']]);adj[NUM[c['id']]].add(k)
def state(b):return {n['id']:n.get('weapon_set',0) for n in b['passives']}
def reach(selected,root):
    nodes=set(selected)|{root};seen={root};front={root}
    while front:
        front=set().union(*(adj[n] for n in front))&nodes-seen;seen|=front
    return seen==nodes
def valid(s):
    assert set(s)<=set(N)
    assert reach({k for k,w in s.items() if w==0 and not N[k].get('ascendancyName')},'marauder594')
    for w in (1,2):
        nodes={k for k,v in s.items() if v in (0,w)};regular={k for k in nodes if not N[k].get('ascendancyName')}
        assert reach(regular,'marauder594');assert reach(nodes-regular,'AscendancyWarrior2Start')
def usage(s):
    return {'ordinary':max(sum(w in (0,i) and not N[k].get('ascendancyName') for k,w in s.items()) for i in (1,2)),
       'sets':[sum(w==i for w in s.values()) for i in (1,2)],'ascendancy':sum(bool(N[k].get('ascendancyName')) and k!='AscendancyWarrior2Start' for k in s)}
G={g['Id']:g['Name'] for g in read(HERE.parents[1]/'data/game_data_poe2/BaseItemTypes.json')}
KO={g['name']:g['title'].split(' - PoE2DB')[0] for g in read(HERE/'sources/gem_korean_titles.json')}
build_paths={p.stem[:2]:p for p in sorted((OUT/'BuildPlanner').glob('*.build'))}
assert len(list((OUT/'BuildPlanner').glob('*.build')))==len(build_paths)==7
builds={code:read(p) for code,p in build_paths.items()}
assert build_paths['01'].name=='01 시작-근접 기초.build'
report={'planners':[],'source_comparisons':[],'transitions':[]}
for code,b in builds.items():
    assert set(b)=={'name','author','link','description','ascendancy','passives','skills','inventory_slots'}
    assert b['ascendancy']=='Warrior2' and len(b['name'])<=40
    s=state(b);assert len(s)==len(b['passives']);valid(s)
    text=b['description']+'\n'+'\n'.join(x['additional_text'] for x in b['inventory_slots'])
    assert all(k in text for k in ['지금 할 일','무기·스킬셋','사용 순서','세트 I','세트 II','추천 옵션'])
    assert not any(k in text for k in ['천체 투영','격노의 함성','재빠른 고통','가지치기 균열','08A','08B','08C'])
    for n in b['passives']:assert set(n)<={'id','weapon_set','additional_text'} and n.get('weapon_set',0) in (0,1,2)
    for x in b['inventory_slots']:
        assert set(x)<={'inventory_id','slot_x','slot_y','level_interval','additional_text','unique_name'}
        assert x['level_interval']==[1,100]
    for g in b['skills']:
        assert set(g)<={'id','level_interval','support_skills','additional_text'}
        for child in [g,*g.get('support_skills',[])]:
            assert child['id']in G and KO[G[child['id']]] in child['additional_text']
            assert 1<=child['level_interval'][0]<=child['level_interval'][1]==100
        if G[g['id']]=='Ancestral Warrior Totem':
            assert '지면 분쇄' in g['additional_text'] and 'II만' in g['additional_text']
            assert all('SupportGem' in x['id'] for x in g['support_skills'])
            inner=next(x for x in b['skills'] if G[x['id']]=='Earthshatter');assert '토템 안에 넣을' in inner['additional_text'] and not inner['support_skills']
    report['planners'].append({'file':build_paths[code].name,'usage':usage(s),'schema_and_Korean_hints':True,'both_sets_connected':True,'sha256':hashlib.sha256(build_paths[code].read_bytes()).hexdigest()})
assert not any(k.startswith('stun') for k in state(builds['01']))
assert next(g for g in builds['01']['skills'] if G[g['id']]=='Rolling Slam')['support_skills'][0]['id'].endswith('SupportGemBrink')
assert next(g for g in builds['02']['skills'] if G[g['id']]=='Shockwave Totem')['level_interval'][0]==6
assert usage(state(builds['05']))=={'ordinary':69,'sets':[14,14],'ascendancy':4}
assert state(builds['05'])==state(builds['06'])
assert state(builds['06']).items()<=state(builds['07']).items()

for code,file in [('02','ninja_hour18_lv24.json'),('03','lv43_0906_0523.json'),('04','lv52_0906_0744.json'),('07','ninja_latest_74.json')]:
    m=read(HERE/'sources'/file);expected={}
    for key,w in [('passiveSelection',0),('passiveSelectionSet1',1),('passiveSelectionSet2',2)]:expected.update({NUM[k]:w for k in m[key]})
    assert state(builds[code])==expected
    e=m['pathOfBuildingExport'];root=E.fromstring(zlib.decompress(base64.urlsafe_b64decode(e+'='*(-len(e)%4))))
    groups=[tuple(g.get('gemId') for g in s.findall('Gem') if g.get('gemId')) for s in root.findall('Skills/SkillSet/Skill') if not s.get('source')];groups=[g for g in groups if g]
    actual=[]
    for g in builds[code]['skills']:
        if G[g['id']]=='Earthshatter':continue
        children=[x['id'] for x in g.get('support_skills',[])]
        if G[g['id']]=='Ancestral Warrior Totem':children.insert(0,next(k for k,v in G.items() if v=='Earthshatter'))
        actual.append((g['id'],*children))
    assert collections.Counter(groups)==collections.Counter(actual),(code,'gem source mismatch')
    report['source_comparisons'].append({'stage':code,'source':file,'passives_exact':True,'gem_groups_exact_after_documented_meta_display_adaptation':True})

plans=read(HERE/'transition_operations_v3.json');assert len(plans)==7
for p in plans:
    current=state({'passives':p['from_passives']});goal=state({'passives':p['to_passives']});valid(current)
    for i,o in enumerate(p['operations']):
        assert current.get(o['id'])==o['from']
        if o['action']=='환불':del current[o['id']]
        else:current[o['id']]=o['to']
        valid(current);u=usage(current);assert u==o['cost'];assert u['ordinary']<=p['required_pool']['ordinary'];assert all(u['sets'][j]<=p['required_pool']['sets'][j] for j in (0,1))
    assert current==goal
    if p['to'].startswith('05'):assert p['operations'][-1]['id']=='passive_keystone_blood_magic'
    report['transitions'].append({'from':p['from'],'to':p['to'],'operations':len(p['operations']),'refunds':p['refunds'],'pool':p['required_pool'],'every_step_connected':True})
extension=read(HERE/'defence_extension_v3.json');current=state(builds['05'])
for sid in extension['order']:current[sid]=state(builds['07'])[sid];valid(current)
assert current==state(extension) and usage(current)==extension['cost'] and extension['cost']['ordinary']==80
broken={**state(builds['02']),'passive_keystone_chaos_inoculation':0}
try:valid(broken)
except AssertionError:report['negative_disconnected_node_rejected']=True
else:raise AssertionError('disconnected negative control accepted')

filters=read(HERE/'validation_filters_v3.json');assert len(filters)==3
for f in filters:assert f['sweep_regressions']==0 and f['base_tail_exact'] and f['sha256']==hashlib.sha256((OUT/'Filters'/f['file']).read_bytes()).hexdigest()
report['filters']=filters
pob=read(HERE/'simulation/v3_pob_results.json');res=read(HERE/'simulation/v3_resource_results.json')
assert len(pob)==10 and len(res['cases'])==45 and res['checks_passed']
report['simulation']={'pob_cases':len(pob),'resource_cases':len(res['cases']),'echo_cost_confirmed':False,'live_combat_verified':False}
evidence=read(HERE/'broadcast_audit/key_scene_evidence.json');assert len(evidence['coverage'])==3 and sum(x['scan_frames'] for x in evidence['coverage'])==2301
report['audit']={'duration':67974,'key_findings':len(evidence['events']),'two_full_asr_comparisons':True,'scan_frames':2301}
report['defence_extension']=extension['cost'];report['new_game_UI_load_verified']=False
repair=HERE/'before_selected_path_repair'
if repair.exists() and (repair/'selected_build_reference.json').exists():
    selected=read(repair/'selected_build_reference.json')
    selected_path=Path(selected['path'].removeprefix('file:'))
    assert selected_path.read_bytes()==build_paths['01'].read_bytes()
    assert selected_path.read_bytes()==(repair/'canonical_01 시작 - 근접과 방패.build').read_bytes()
    # The observed UI is stage 02. Do not imply all seven views were inspected.
    assert (repair/'game_stage02_loaded.png').is_file()
    log=(repair/'client_load_before.txt').read_text(encoding='utf-8')
    assert all(any('Successfully loaded build' in line and b['name']+'.build' in line for line in log.splitlines()) for b in builds.values())
    report.update(new_game_UI_load_verified=True,game_UI_verified_stage='02',game_parser_loaded_planners=7,selected_path_restored=True,planner_payload_unchanged_by_path_repair=True)
(HERE/'validation_revision3.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print('PASS: seven planners, four source snapshots, seven legal routes, defence extension, filters and revised simulation artifacts.')
