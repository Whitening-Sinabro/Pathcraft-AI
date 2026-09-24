"""Bounded independent validation of the delivered five, no app/install mutations."""
from pathlib import Path
import collections, hashlib, json, re, subprocess, sys, xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parent
CORPUS=ROOT.parent
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
contract=read(ROOT/'planner_contract.json')
tree=read(Path(next(s['file'] for s in contract['sources'] if s['id']=='tree_0_5')))
nodes={int(n['skill']):n for n in tree['nodes'].values() if isinstance(n,dict) and 'stringId'in n}
by_string={n['stringId']:i for i,n in nodes.items()}
adj={n:set() for n in nodes}
for n,d in nodes.items():
    for e in d.get('connections',[]):
        v=int(e['id'])
        if v in adj:adj[n].add(v);adj[v].add(n)
def reach(selected,start):
    seen={start};q=[start]
    for n in q:
        for v in adj[n]&selected-seen:seen.add(v);q.append(v)
    return seen
def connected(m):
    return all(reach(s:={47175}|{n for n,w in m.items() if w in (0,k)},47175)==s for k in (1,2))
def paid(a):return {n for n in a if not nodes[n].get('isFreeAllocate') and not nodes[n].get('isAscendancyStart')}
base=read(Path(next(s['file'] for s in contract['sources'] if s['id']=='BaseItemTypes')))
gem_rows=read(Path(next(s['file'] for s in contract['sources'] if s['id']=='SkillGems')))
gems={base[g['BaseItemType']]['Id']:g for g in gem_rows}
source_xml={s['id']:ET.parse(ROOT/s['local_copy']).getroot() for s in contract['sources'] if 'local_copy'in s}
sp=source_xml['xml-29d39'].find('Tree/Spec')
pool=set(map(int,sp.get('nodes').split(',')))
wsets={w:set(map(int,sp.find('WeaponSet'+str(w)).get('nodes').split(','))) for w in (1,2)}
baseline=read(ROOT/'source_hashes.json')
assert all(Path(p).exists() and sha(Path(p))==h for p,h in baseline.items())
for s in contract['sources']:
    assert sha(Path(s['file']))==s['sha256']
    if 'local_copy'in s:assert sha(ROOT/s['local_copy'])==s['sha256']
allowed={'build':{'name','author','link','description','ascendancy','passives','skills','inventory_slots'},'passive':{'id','weapon_set','level_interval','additional_text'},'skill':{'id','level_interval','additional_text','support_skills'},'support':{'id','level_interval','additional_text'},'slot':{'inventory_id','slot_x','slot_y','unique_name','level_interval','additional_text'}}
def shape(o,kind):
    assert set(o)<=allowed[kind]
    for k,v in o.items():
        if k in ['passives','skills','inventory_slots','support_skills']:assert isinstance(v,list)
        elif k=='level_interval':assert v==[1,100]
        elif k in ['weapon_set','slot_x','slot_y']:assert type(v)==int and v>=0
        else:assert isinstance(v,str)
assert len(contract['stages'])==6
expected=[(37,0,4),(61,4,6),(61,4,6),(61,4,6),(70,4,6),(118,24,8)]
stage_results=[];previous={};prev_asc=set()
for ix,(s,expect) in enumerate(zip(contract['stages'],expected),1):
    p=CORPUS/s['native_file'];b=read(p);assert sha(p)==s['native_sha256'];shape(b,'build')
    assert b['ascendancy']=='Warrior3'
    assert b['name'].startswith(f"{s['display_number']:02d} ") if s.get('display_number') else b['name'].startswith('대안')
    assert s.get('display_number')==({1:None,2:3,3:4,4:5,5:6,6:7}[ix])
    m={int(p['id']):p['weapon_set'] for p in s['passives']};a={int(p['id']) for p in s['ascendancy_nodes']}
    assert len(m)==len(s['passives']);assert connected(m);assert reach(a,5852)==a
    assert set(m)<=pool
    for n,w in m.items():assert w==(1 if n in wsets[1] else 2 if n in wsets[2] else 0)
    assert a<=set(map(int,source_xml['xml-28509' if ix<3 else 'xml-29d39'].find('Tree/Spec').get('nodes').split(',')))
    count=collections.Counter(m.values());actual=(count[0]+max(count[1],count[2]),max(count[1],count[2]),len(paid(a)))
    assert actual==expect
    assert [s['budgets'][k] for k in ['ordinary_points_required','weapon_specialization_capacity_required','ascendancy_points_required']]==list(actual)
    native_nodes={by_string[p['id']]:p['weapon_set'] for p in b['passives']}
    assert len(native_nodes)==len(b['passives']);assert native_nodes=={**m,**{n:0 for n in a-{5852}}}
    for p in b['passives']:shape(p,'passive');assert 0<=p['weapon_set']<=2
    # in-game text stays terse (user 9/22): no passive tooltips, short skill notes, short description
    assert len(b['description'])<=400 and not any('additional_text' in p for p in b['passives']) and all(len(x.get('additional_text',''))<=80 for x in b['skills'])
    for p in b['inventory_slots']:shape(p,'slot')
    for native_group,group in zip(b['skills'],s['skill_groups']):
        shape(native_group,'skill');assert native_group['id']==group['gems'][0]['id']
        assert gems[native_group['id']]['GemType']==0
        assert len(native_group['support_skills'])==len(group['supports'])<=4
        for support in native_group['support_skills']:shape(support,'support');assert gems[support['id']]['GemType']==1
        for gem in group['gems']:assert gem['min_character_level']==gems[gem['id']]['MinLevelReq']
        if ix==1:assert max(g['min_character_level'] for g in group['gems'])<=40
    assert len(b['skills'])==len(s['skill_groups'])
    # lineage supports: 65+, named on the group; in the gem slots exactly when in_slots (capital track, within 4 sockets); Kaom only next to Ahn's Citadel
    for native_group,group in zip(b['skills'],s['skill_groups']):
        lin=[l['name'] for l in group['lineage']];ids_in={x['id'] for x in native_group['support_skills']}
        for l in group['lineage']:
            assert gems[l['id']]['MinLevelReq']==l['min_character_level']>=65  # visibility: shield-slot check below
            assert (l['id'] in ids_in)==l['in_slots']==(l['name'] in group['supports'])
        assert ("Kaom's Madness" not in lin) or ("Ahn's Citadel" in lin)
    lin_all=[l['name'] for g in s['skill_groups'] for l in g['lineage'] if l['in_slots']];assert len(lin_all)==len(set(lin_all)),('lineage gem in two skills',s['id'])
    lin_by={g['active']:{l['name']:l['in_slots'] for l in g['lineage']} for g in s['skill_groups']}
    shield_text=next((x.get('additional_text','') for x in b['inventory_slots'] if x['inventory_id']=='Offhand1'),'')
    assert all(l['ko'] in shield_text for g in s['skill_groups'] for l in g['lineage']),('lineage not visible on the shield slot',s['id'])
    sw=next(g for g in s['skill_groups'] if g['active']=='Shield Wall')['supports']
    if s['index']==2:assert lin_by['Shield Wall']=={"Ahn's Citadel":False} and 'Concentrated Area' in sw and len(sw)==4
    # price-driven (HC 2026-09-22): only Daresso's Passion is slotted; Ahn's/Kaom/Uhtred are 'if you can buy'
    if s['index']==3:assert lin_by['Shield Wall']=={"Ahn's Citadel":False,"Kaom's Madness":False} and 'Concentrated Area' in sw and len(sw)==4 and lin_by['War Banner']=={"Daresso's Passion":True}
    if s['index']>=4:assert lin_by['Shield Wall']=={"Ahn's Citadel":False,"Kaom's Madness":False} and sw[-1]=='Armour Break III' and len(sw)==4 and lin_by['Infernal Cry']=={"Uhtred's Rite":False} and lin_by['War Banner']=={"Daresso's Passion":True}
    if ix<4:assert not {'Execute III','Clash','Eternal Rage'}&{g['name'] for group in s['skill_groups'] for g in group['gems']}
    if ix<5:assert not {24766,25711,59208,17825}&set(m)
    if ix>=3:assert 9988 not in a
    else:assert 9988 in a and 'Normal body' in s['equipment'][2]['name']
    state=dict(previous)
    for op in s['diff_from_previous']['operations']:
        assert op['action']=='allocate' and op['numeric_id'] not in state
        state[op['numeric_id']]=op['weapon_set'];assert connected(state)
    assert state==m
    ast=set(prev_asc)
    for op in s['diff_from_previous']['ascendancy_operations']:
        if op['action']=='refund':ast.remove(op['numeric_id'])
        else:ast.add(op['numeric_id'])
        assert reach(ast,5852)==ast
    assert ast==a
    assert s['diff_from_previous']['ascendancy_paid_refunds']==len(paid(prev_asc-a))
    assert s['socket_budget']['lesser_from_base']<=29 and s['socket_budget']['greater_from_base']<=3 and s['socket_budget']['perfect_from_base']==0
    stage_results.append(dict(id=s['id'],native_file=s['native_file'],native_sha256=sha(CORPUS/s['native_file']),ordinary=actual[0],specialization=actual[1],paid_ascendancy=actual[2],both_sets_connected=True,ascendancy_connected=True,native_rows=len(b['passives']),core_max_gem_min_character_level=s['eligibility']['max_selected_gem_min_character_level'],support_attribute_floor=s['support_attribute_floor'],stage_diff=s['diff_from_previous']))
    previous=m;prev_asc=a
waitmap={int(p['id']):p['weapon_set'] for p in contract['normal_growth_core48']}
for ext in contract['waiting_for_equipment_growth']:
    for op in ext['operations']:waitmap[op['numeric_id']]=op['weapon_set'];assert connected(waitmap);assert op['numeric_id'] in pool-wsets[1]-wsets[2]
    c=collections.Counter(waitmap.values());assert c[0]+max(c[1],c[2])==ext['ordinary_points_required']
assert [e['ordinary_points_required'] for e in contract['waiting_for_equipment_growth']]==[55,61]
assert waitmap=={int(p['id']):p['weapon_set'] for p in contract['stages'][1]['passives']}
pack=read(CORPUS/'planner_data/build_data.json');assert pack['taengjung_progression']==contract;assert pack['active_stages']==contract['stages']
js=(CORPUS/'planner_data/build_data.js').read_text(encoding='utf-8');assert json.loads(js.removeprefix('window.PATHCRAFT_BUILD_DATA = ').strip().removesuffix(';'))==pack
# 00~02 reference stages: exact 별이슬 act specs; the interlude tree's town transition replays connected into day-1 (phase 2 = 03).
refs=contract['reference_stages'];ref_xml=ET.parse(CORPUS/'linked_update_pob.xml').getroot()
assert [r['spec_title'] for r in refs]==['3','4','Interlude'] and [r['display_number'] for r in refs]==[0,1,2]
for ref in refs:
    assert sha(CORPUS/'linked_update_pob.xml')==ref['source_sha256']
    rsp=next(s for s in ref_xml.findall('Tree/Spec') if s.get('title')==ref['spec_title'])
    rws={w:set(map(int,filter(None,((rsp.find('WeaponSet'+str(w)).get('nodes') if rsp.find('WeaponSet'+str(w)) is not None else '') or '').split(',')))) for w in (1,2)}
    rstart={int(p['id']):p['weapon_set'] for p in ref['passives']}
    assert rstart=={n:1 if n in rws[1] else 2 if n in rws[2] else 0 for n in set(map(int,rsp.get('nodes').split(',')))-{47175} if not nodes[n].get('ascendancyName')}
    assert connected(rstart)
    rb=read(CORPUS/ref['native_file']);assert sha(CORPUS/ref['native_file'])==ref['native_sha256'];shape(rb,'build')
    assert rb['name'].startswith(f"{ref['display_number']:02d} ")
    assert len(rb['description'])<=400 and all(len(x.get('additional_text',''))<=160 for x in rb['inventory_slots']+rb['skills']) and not any('additional_text' in p for p in rb['passives'])
    assert {by_string[p['id']]:p['weapon_set'] for p in rb['passives'] if not nodes[by_string[p['id']]].get('ascendancyName')}==rstart
    rasc={by_string[p['id']] for p in rb['passives'] if nodes[by_string[p['id']]].get('ascendancyName')}
    # act gear: shield + white body armour rule once Smith's Masterwork is in the file
    rslots={e['slot'] for e in ref['equipment']}
    assert {'Weapon 1','Weapon 2','Body Armour','Ring 1','Ring 2','Amulet','Helmet','Gloves','Belt','Boots'}<=rslots and len(rb['inventory_slots'])==len(ref['equipment'])
    body=next(e for e in ref['equipment'] if e['slot']=='Body Armour')
    assert body['name'].startswith('Normal body armour')==(9988 in rasc) and '방어도' in next(e for e in ref['equipment'] if e['slot']=='Weapon 2')['condition']
    assert rasc=={int(x['id']) for x in ref['ascendancy_nodes']}-{5852} and reach(rasc|{5852},5852)==rasc|{5852}
    # paid Kitava points = paid points in the 별이슬 spec (Warbringer there), taken in Taengjung's 8/17 order
    bpaid={n for n in set(map(int,rsp.get('nodes').split(','))) if nodes[n].get('ascendancyName') and not nodes[n].get('isFreeAllocate') and not nodes[n].get('isAscendancyStart')}
    kpaid={n for n in rasc if not nodes[n].get('isFreeAllocate')}
    assert {57959,14960}<=rasc and len(kpaid)==len(bpaid)==ref['byeolisul_paid_ascendancy'] and (9988 in rasc)==(len(kpaid)>2)
    for g in rb['skills']:
        shape(g,'skill');assert gems[g['id']]['GemType']==0 and len(g['support_skills'])<=4 and '/Unique' not in g['id']
        for x in g['support_skills']:assert gems[x['id']]['GemType']==1 and gems[x['id']]['CraftingLevel']>0
    orig={g['active']:g['supports'] for g in ref['source_skill_groups']}
    assert all(g['supports']==orig[g['active']] for g in ref['skill_groups'] if g['active'] not in ('Shield Wall','Infernal Cry','Shockwave Totem')),'act: 별이슬 non-core groups must stay as the source'
    rg={g['active']:g['supports'] for g in ref['skill_groups']}
    assert rg['Shield Wall']==['Rapid Attacks II','Fire Attunement','Armour Break III','Magnified Area I'] and rg['Infernal Cry']==['Raging Cry','Tireless','Enraged Warcry I']
    assert sum(len(v)==4 for v in rg.values())<=3
    if ref['spec_title']=='Interlude':
        st=dict(rstart)
        for op in ref['transition_to_03']:
            if op['action']=='refund':assert st.pop(op['numeric_id'])==op['weapon_set']
            else:assert op['numeric_id'] not in st;st[op['numeric_id']]=op['weapon_set']
            assert connected(st)
        assert st=={int(p['id']):p['weapon_set'] for p in contract['stages'][1]['passives']}
    else:assert ref['transition_to_03']==[]
# 03+ zero2hero track: 03 kept, additions only, all inside 07; no Surrounded/Low Life node, no unique, no lineage; ascendancy 03 + 110 + 60913
zt=contract['zero_track'];assert len(zt)==1;z=zt[0];s03=contract['stages'][1];s07=contract['stages'][5]
zb=read(CORPUS/z['native_file']);assert sha(CORPUS/z['native_file'])==z['native_sha256'];shape(zb,'build');assert zb['name'].startswith('03+ ') and z['display_label']=='03+' and z['track']=='zero'
zm={int(p['id']):p['weapon_set'] for p in z['passives']};za={int(p['id']) for p in z['ascendancy_nodes']}
m03={int(p['id']):p['weapon_set'] for p in s03['passives']};m07={int(p['id']):p['weapon_set'] for p in s07['passives']}
assert connected(zm) and all(zm.get(n)==w for n,w in m03.items()) and all(m07.get(n)==w for n,w in zm.items()) and len(zm)>len(m03)
assert not any(re.search('Surrounded|Low Life',' '.join(nodes[n].get('stats',[]))) for n in set(zm)-set(m03))
assert {x['numeric_id'] for x in z['excluded_nodes']}=={n for n in set(m07)-set(m03) if re.search('Surrounded|Low Life',' '.join(nodes[n].get('stats',[])))}
assert za=={int(p['id']) for p in s03['ascendancy_nodes']}|{110,60913} and reach(za,5852)==za and len(paid(za))==8
assert {by_string[p['id']]:p['weapon_set'] for p in zb['passives']}=={**zm,**{n:0 for n in za-{5852}}}
st=dict(m03)
for op in z['diff_from_previous']['operations']:
    assert op['numeric_id'] not in st;st[op['numeric_id']]=op['weapon_set'];assert connected(st)
assert st==zm
for p in zb['inventory_slots']:shape(p,'slot');assert 'unique_name' not in p
assert not any(e.get('unique') for e in z['equipment']) and z['equipment'][2]['name'].startswith('Normal body')
for native_group,group in zip(zb['skills'],z['skill_groups']):
    shape(native_group,'skill');assert native_group['id']==group['gems'][0]['id'] and len(native_group['support_skills'])==len(group['supports'])<=4
    assert not group['lineage'] and all(gems[x['id']]['CraftingLevel']>0 for x in native_group['support_skills'])
assert len(zb['skills'])==len(z['skill_groups'])
assert z['socket_budget']['greater_from_base']<=3 and z['socket_budget']['perfect_from_base']==0
zc=collections.Counter(zm.values());assert z['budgets']['ordinary_points_required']==zc[0]+max(zc[1],zc[2]) and z['budgets']['ascendancy_points_required']==8
im=read(ROOT/'install_mapping.json')
assert [f['source'] for f in im['files']]==[r['native_file'] for r in refs]+[s['native_file'] for s in contract['stages'] if s.get('display_number')]+[z['native_file']]
assert [f['name'][:2] for f in im['files']]==['00','01','02','03','04','05','06','07','03']
# Rebuild once, compare concrete outputs; no broad tests or installation.
outputs=[ROOT/'planner_contract.json',ROOT/'install_mapping.json',ROOT/'source_evidence.json',CORPUS/'planner_data/build_data.json',CORPUS/'planner_data/build_data.js']+list((ROOT/'native').glob('*.build'))
before={str(p):sha(p) for p in outputs}
subprocess.run([sys.executable,str(ROOT/'generate.py')],check=True,stdout=subprocess.DEVNULL)
assert before=={str(p):sha(p) for p in outputs}
assert all(sha(Path(p))==h for p,h in baseline.items())
result=dict(status='passed',protected_files_checked=len(baseline),source_hashes_unchanged=True,deterministic_outputs_checked=len(outputs),native_payloads_parsed=9,checks=['strict native schema shape','real node/gem IDs','both-set rooted graph','ascendancy graph and free/paid counts','source memberships and exact set categories','every recommended transition intermediate connected','source-supported waiting branch55/61','core gem minimums and support types','conditional absence of lowlife/surround groups','no mandatory fifth socket','planner JSON/JS parity','byte-for-byte deterministic rebuild'],stages=stage_results,limits=['No actual player export: attribute totals, actual gem levels, spirit, gear, quest points and paid ascendancy remain unknown.','No live gameplay/DPS/HC claim; condition bundles require actual character confirmation.','Full optional latest and historical Lund sources remain untouched; no install performed.'])
dump(ROOT/'validation.json',result)
print(json.dumps({k:v for k,v in result.items() if k!='stages'},ensure_ascii=False,indent=2))
