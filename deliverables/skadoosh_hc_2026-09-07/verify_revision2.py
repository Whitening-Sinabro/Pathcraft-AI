"""Read-only independent acceptance checks on serialised planners and operations."""
import base64, collections, copy, hashlib, json, re, sys, zipfile, zlib
import xml.etree.ElementTree as ET
from pathlib import Path
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[1]
OUT=HERE/'revision2'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
TREE=read(HERE/'sources/tree_0_5.json')
N={v['stringId']:v for v in TREE['nodes'].values() if 'stringId' in v}
ID={v['skill']:k for k,v in N.items()}
EDGES=collections.defaultdict(set)
for a,v in N.items():
    for e in v.get('connections',[]):
        if e['id'] in ID:
            b=ID[e['id']];EDGES[a].add(b);EDGES[b].add(a)
ROOT='marauder594';ASC='AscendancyWarrior2Start'
def st(b):return {v['id']:v.get('weapon_set',0) for v in b['passives']}
def reached(nodes,root):
    nodes=set(nodes)|{root};visited={root};frontier={root}
    while frontier:
        frontier=set.union(set(),*(EDGES[n] for n in frontier))&nodes-visited
        visited.update(frontier)
    return visited==nodes
def assert_connected(s):
    assert set(s)<=N.keys()
    assert reached({n for n,w in s.items() if not w and not N[n].get('ascendancyName')},ROOT),'common path'
    for weapon in (1,2):
        alloc={n for n,w in s.items() if w in (0,weapon)}
        regular={n for n in alloc if not N[n].get('ascendancyName')}
        assert reached(regular,ROOT),('regular',weapon)
        assert reached(alloc-regular,ASC),('ascendancy',weapon)
def usage(s):
    # Count each effective tree independently instead of using the generator's
    # common + max expression; these must give the same budget.
    ordinary=[sum(w in (0,i) and not N[n].get('ascendancyName') for n,w in s.items()) for i in (1,2)]
    return {'ordinary':max(ordinary),'sets':[sum(w==i for w in s.values()) for i in (1,2)],
            'ascendancy':sum(bool(N[n].get('ascendancyName')) and n!=ASC for n in s)}
BUILD={p.stem:read(p) for p in sorted((OUT/'BuildPlanner').glob('*.build'))}
assert len(BUILD)==13
BY_CODE={n.split()[0]:b for n,b in BUILD.items()}
GEMS={g['Id']:g['Name'] for g in read(REPO/'data/game_data_poe2/BaseItemTypes.json')}
KO={r['name']:r['title'].split(' - PoE2DB')[0] for r in read(HERE/'sources/gem_korean_titles.json')}
REPORT={'planners':[],'transitions':[],'source_comparisons':[]}
with zipfile.ZipFile(HERE/'sources/mobalytics_original.zip') as z:
    creator=json.loads(z.read(next(n for n in z.namelist() if n.startswith('Imported -'))).decode('utf-8-sig'))
for name,b in BUILD.items():
    assert set(b)==set(creator)|{'description'} and b['ascendancy']=='Warrior2' and len(name)<=40
    s=st(b);assert len(s)==len(b['passives']);assert_connected(s)
    for p in b['passives']:
        assert set(p)<={'id','weapon_set','additional_text'} and p.get('weapon_set',0) in (0,1,2)
    note='\n'.join(i.get('additional_text','') for i in b['inventory_slots'])+'\n'+b['description']
    note+='\n'+'\n'.join(g.get('additional_text','') for s in b['skills'] for g in [s,*s.get('support_skills',[])])
    assert all(token in note for token in ('지금 할 일','추천 옵션','이 스킬 안에 넣을 젬','세트 I','세트 II'))
    assert '재빠른 고통' not in note and '가지치기 균열' not in note
    assert all('level_interval' not in x or 1<=x['level_interval'][0]<=x['level_interval'][1]==100 for x in b['inventory_slots'])
    total_gems=0
    for skill in b['skills']:
        assert set(skill)<={'id','level_interval','support_skills','additional_text'}
        for gem in [skill,*skill.get('support_skills',[])]:
            assert gem['id'] in GEMS
            assert 1<=gem['level_interval'][0]<=gem['level_interval'][1]==100
            assert KO[GEMS[gem['id']]] in note
            total_gems+=1
    REPORT['planners'].append({'file':name+'.build','usage':usage(s),'gem_entries':total_gems,'common_and_both_sets_connected':True,'native_schema':True,'all_gems_named_in_Korean_notes':True,'equipment_recommendations_and_native_gem_hints':True})
for a,b in [('01','02'),('02','03')]:assert st(BY_CODE[a]).items()<=st(BY_CODE[b]).items()
assert not ({'stun4_','stun5'}&(st(BY_CODE['01']).keys()|st(BY_CODE['02']).keys()))

PLANS=read(HERE/'transition_operations_v2.json')
assert len(PLANS)==12
for plan in PLANS:
    current=st(BUILD[plan['from']]);goal=st(BUILD[plan['to']]);pool=plan['required_pool']
    costs=[usage(current)];refunds=0
    for number,o in enumerate(plan['operations'],1):
        assert current.get(o['id'])==o['from'],(plan['to'],number,'unexpected initial binding')
        if o['action']=='환불':
            assert o['id'] not in goal
            del current[o['id']];refunds+=1
        elif o['action']=='추가':
            assert o['id'] not in current and goal[o['id']]==o['to']
            current[o['id']]=o['to']
        else:
            assert o['action']=='재배정' and goal[o['id']]==o['to']
            current[o['id']]=o['to']
        assert_connected(current)
        c=usage(current);assert c==o['cost'];costs.append(c)
        assert c['ordinary']<=pool['ordinary'] and all(c['sets'][j]<=pool['sets'][j] for j in (0,1))
    assert current==goal and refunds==plan['refunded_entries']
    assert max(c['ordinary'] for c in costs)==pool['ordinary']
    assert [max(c['sets'][j] for c in costs) for j in (0,1)]==pool['sets']
    REPORT['transitions'].append({'from':plan['from'],'to':plan['to'],'steps':len(plan['operations']),'refunds':refunds,'required_pool':pool,'each_step_connected_and_within_pool':True})

# Compare against the external snapshot, not merely against the prior delivery.
REPORT['optional_defence_routes']=[]
optional=next(p for p in PLANS if p['from'].startswith('07 '))['operations']
for route in read(HERE/'partial_transitions_v2.json'):
    expected=st(BY_CODE['07'])
    for o in optional[:route['defence_points_used']]:expected[o['id']]=o['to']
    current={p['id']:p.get('weapon_set',0) for p in route['initial_passives']}
    assert current==expected
    refunds=0
    for o in route['operations']:
        assert current.get(o['id'])==o['from']
        if o['action']=='환불':del current[o['id']];refunds+=1
        else:current[o['id']]=o['to']
        assert_connected(current)
        c=usage(current);assert c==o['cost']
        assert c['ordinary']<=97 and all(n<=22 for n in c['sets'])
    assert current==st(BY_CODE['08A']) and refunds==route['refunded_entries']
    REPORT['optional_defence_routes'].append({'defence_points_used':route['defence_points_used'],'refunds':refunds,'steps':len(route['operations']),'verified':True})
assert len(REPORT['optional_defence_routes'])==14

SOURCES={'03':'ninja_hour18_lv24.json','04':'lv34_0906_0320.json','05':'lv43_0906_0523.json','06':'lv46_0906_0634.json','07':'lv52_0906_0744.json','09':'ninja_latest_74.json'}
for code,filename in SOURCES.items():
    model=read(HERE/'sources'/filename);expected={}
    for field,w in [('passiveSelection',0),('passiveSelectionSet1',1),('passiveSelectionSet2',2)]:
        expected.update({ID[n]:w for n in model[field]})
    assert st(BY_CODE[code])==expected,(code,'source nodes',set(st(BY_CODE[code]).items())^set(expected.items()))
    encoded=model['pathOfBuildingExport']
    xml=ET.fromstring(zlib.decompress(base64.urlsafe_b64decode(encoded+'='*(-len(encoded)%4))))
    groups=[]
    for group in xml.findall('.//Skill'):
        if group.get('source'):continue
        gems=tuple(g.get('gemId') for g in group.findall('Gem') if g.get('gemId'))
        if gems:groups.append(gems)
    actual=[(s['id'],*(g['id'] for g in s.get('support_skills',[]))) for s in BY_CODE[code]['skills']]
    assert collections.Counter(groups)==collections.Counter(actual),(code,'source links')
    REPORT['source_comparisons'].append({'stage':code,'source':filename,'source_sha256':sha(HERE/'sources'/filename),'passives_equal':True,'explicit_gem_groups_equal':True})

AB='passive_keystone_ancestral_bond';BM='passive_keystone_blood_magic'
def strip_hints(obj):
    if isinstance(obj,dict):return {k:strip_hints(v) for k,v in obj.items() if k!='additional_text'}
    if isinstance(obj,list):return [strip_hints(x) for x in obj]
    return obj
assert st(BY_CODE['05'])==st(BY_CODE['05A'])
trial_expected=json.loads(json.dumps(BY_CODE['06']['skills']))
for skill in trial_expected:
    if skill['id'].endswith('SkillGemMagmaBarrier'):
        skill['support_skills']=[g for g in skill['support_skills'] if not g['id'].endswith('SupportGemClarityTwo')]
assert strip_hints(BY_CODE['05A']['skills'])==strip_hints(trial_expected)
assert AB not in st(BY_CODE['08A']) and BM not in st(BY_CODE['08A'])
assert st(BY_CODE['08B'])=={**st(BY_CODE['08A']),AB:0}
assert st(BY_CODE['08C'])=={**st(BY_CODE['08B']),BM:0}
assert strip_hints(BY_CODE['08B']['skills'])==strip_hints(BY_CODE['08C']['skills'])
def group(b,suffix):return next(s for s in b['skills'] if s['id'].endswith(suffix))
for code in ('08B','08C','09'):
    b=BY_CODE[code];awt=group(b,'SkillGemAncestralWarriorTotem')
    assert awt['support_skills'][0]['id'].endswith('SkillGemEarthshatter')
    assert len(awt['support_skills'])==(4 if code=='09' else 3)
    purities=[g for g in b['skills'] if g['id'].endswith('SkillGemPurityOfFire')]
    assert len(purities)==2 and purities[0]['support_skills']!=purities[1]['support_skills']
    cry=group(b,'SkillGemFortifyingCry')
    assert GEMS[cry['support_skills'][0]['id']]==("Paquate's Pact" if code=='09' else 'Corrupting Cry I')
    assert len([g for g in cry['support_skills'] if 'CorruptingCry' in g['id']])==1
assert [s['id'] for s in group(BY_CODE['09'],'SkillGemAncestralWarriorTotem')['support_skills']]==[s['id'] for s in group(creator,'SkillGemAncestralWarriorTotem')['support_skills']]

# Negative control: a valid node identifier with a broken connection must fail.
broken=st(BY_CODE['03']);broken['passive_keystone_chaos_inoculation']=0
assert 'passive_keystone_chaos_inoculation' in N
try:assert_connected(broken)
except AssertionError:REPORT['disconnected_known_node_rejected']=True
else:raise AssertionError('validator accepted an isolated keystone')

FILTERS={p.name:sha(p) for p in (OUT/'Filters').glob('*.filter')}
assert len(FILTERS)==3
assert FILTERS=={p.name:sha(p) for p in (HERE/'ready/Filters').glob('*.filter')}
REPORT['filters_unchanged_from_previously_swept_version']=FILTERS
REPORT['previous_revision_loading_user_confirmed']=True
REPORT['limitations']=['이전 배포본 로딩은 사용자 확인; 이번 수정본 게임 재로딩과 실제 전투는 미검증','중간 05A/08A/08B/08C는 Pathcraft 구성안이며 제작자 실측이 아님','UI 버튼과 실제 골드 소모는 실연하지 않음','PoB2의 미구현 효과와 조건부 계산 한계는 시뮬레이션결과.md에 기재','필터 원본의 미모델링 조건은 기존 검증 한계 유지']
(HERE/'validation_revision2.json').write_text(json.dumps(REPORT,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('PASS: 13 native planners, 12 legal transitions, 6 external snapshot comparisons, staged AB/BM/Pact, 3 unchanged filters.')
