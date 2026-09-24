"""Build a progression revision, with every passive transaction checked for legality."""
from __future__ import annotations
import collections, copy, hashlib, json, re, shutil, zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
OUT = HERE / 'revision2'
GAME = Path('C:/Users/User/Documents/My Games/Path of Exile 2')
for folder in ('BuildPlanner', 'Filters'):
    (OUT/folder).mkdir(parents=True, exist_ok=True)
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def dump(p,d): p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
archive = HERE/'sources/first_delivery_planners.zip'
if not archive.exists():
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted((HERE/'ready/BuildPlanner').glob('*.build')): z.write(p,p.name)
with zipfile.ZipFile(archive) as z:
    ORIGINAL = [json.loads(z.read(n).decode('utf-8')) for n in sorted(z.namelist())]
tree = read(HERE/'sources/tree_0_5.json')
NS = {n['stringId']: n for n in tree['nodes'].values() if 'stringId' in n}
NUM = {n['skill']:sid for sid,n in NS.items()}
ADJ = collections.defaultdict(set)
for sid,n in NS.items():
    for c in n.get('connections',[]):
        if c['id'] in NUM: ADJ[sid].add(NUM[c['id']]); ADJ[NUM[c['id']]].add(sid)
CLASS_ROOT = 'marauder594'
ASC_ROOT = 'AscendancyWarrior2Start'
BASES = {r['Id']: r['Name'] for r in read(REPO/'data/game_data_poe2/BaseItemTypes.json')}
NAMES = {r['name']: r['title'].split(' - PoE2DB')[0] for r in read(HERE/'sources/gem_korean_titles.json')}
def state(d): return {p['id']:p.get('weapon_set',0) for p in d['passives']}
def entries(s): return [{'id':k,**({'weapon_set':w} if w else {})} for k,w in s.items()]
def linked(selected,root):
    selected=set(selected)|{root}; seen=set(); todo=[root]
    while todo:
        n=todo.pop()
        if n in seen: continue
        seen.add(n); todo.extend((ADJ[n]&selected)-seen)
    return seen==selected
def legal(s):
    if not s: return False
    common={k for k,w in s.items() if w==0 and not NS[k].get('ascendancyName')}
    if not linked(common,CLASS_ROOT): return False
    for w in (1,2):
        allocated={k for k,binding in s.items() if binding in (0,w)}
        regular={k for k in allocated if not NS[k].get('ascendancyName')}
        ascendancy=allocated-regular
        if not regular or not linked(regular,CLASS_ROOT) or not linked(ascendancy,ASC_ROOT): return False
    return True
def costs(s):
    common=sum(not w and not NS[k].get('ascendancyName') for k,w in s.items())
    sets=[sum(w==i for w in s.values()) for i in (1,2)]
    asc=sum(bool(NS[k].get('ascendancyName')) and k!=ASC_ROOT for k in s)
    return {'ordinary':common+max(sets),'sets':sets,'ascendancy':asc}
def remove_to(s, predicate, budget, protected):
    s=dict(s)
    while predicate(s)>budget:
        candidates=[k for k in s if k not in protected and k!=ASC_ROOT]
        # Preserve notables when small optional leaves are enough.
        candidates.sort(key=lambda k:(bool(NS[k].get('isNotable')),k))
        changed=False
        for k in candidates:
            test={n:w for n,w in s.items() if n!=k}
            if legal(test) and predicate(test)<predicate(s): s=test;changed=True;break
        if not changed: raise AssertionError(('unable to trim',budget,costs(s)))
    return s

# Early targets are subsets of the current league's observed Lv24 allocation.
# The old 0.4 stun detour is removed, including the two obsolete first nodes.
early=copy.deepcopy(ORIGINAL[0]); live24=state(ORIGINAL[2])
melee={k:w for k,w in live24.items() if k.startswith('melee') or k=='marauder_brute_notable1' or k==ASC_ROOT}
assert legal(melee) and len([k for k in melee if k!=ASC_ROOT])==10
early['passives']=entries(melee)
second=copy.deepcopy(ORIGINAL[1])
s={k:w for k,w in live24.items() if not NS[k].get('ascendancyName') or k==ASC_ROOT}
protected=set(melee)|{'totems14','totems34'}
for w in (1,2): s=remove_to(s,lambda a,w=w:costs(a)['sets'][w-1],4,protected)
s=remove_to(s,lambda a:costs(a)['ordinary'],25,protected)
assert set(melee.items())<=set(s.items())<=set(live24.items())
second['passives']=entries(s)
# Raise Shield is an equipment grant, retained in the guide when introducing totems.
if not any(g['id'].endswith('SkillGemShieldBlock') for g in second['skills']):
    second['skills'].append(copy.deepcopy(next(g for g in early['skills'] if g['id'].endswith('SkillGemShieldBlock'))))
for b in (early,second):
    src=OUT/'BuildPlanner'/(b['name']+'.build');dest=GAME/'BuildPlanner'/src.name
    dump(src,b)
    backup=HERE/'installed_before_revision2'/src.name
    backup.parent.mkdir(exist_ok=True)
    if dest.exists() and not backup.exists():shutil.copy2(dest,backup)
    shutil.copy2(src,dest)
    assert src.read_bytes()==dest.read_bytes()

# First try the new warcry on the current tree; the old damage source remains equipped.
cry_trial=copy.deepcopy(ORIGINAL[4])
cry_trial['name']='05A 함성 시험-환불 전'
cry_trial['skills']=copy.deepcopy(ORIGINAL[5]['skills'])
# The Lv43 gear has 60 Spirit: Magma Barrier + Vitality I uses 50.
# Clarity II would bring the reservation to 70; leave it optional in the notes.
for skill in cry_trial['skills']:
    if skill['id'].endswith('SkillGemMagmaBarrier'):
        skill['support_skills']=[g for g in skill['support_skills'] if not g['id'].endswith('SupportGemClarityTwo')]

# Keep the original proven final allocation as the destination, but separate the
# large respec, the totem/spirit change, Blood Magic and the lineage support.
prepare=copy.deepcopy(ORIGINAL[6]); prepare['name']='08A 후반 트리-기존 함성 유지'
late=state(ORIGINAL[8])
AB='passive_keystone_ancestral_bond'; BM='passive_keystone_blood_magic'
WOOD={'AscendancyWarrior2Small7_','AscendancyWarrior2Notable7'}
base_late={k:w for k,w in late.items() if k not in {AB,BM}|WOOD}
assert legal(base_late)
prepare['passives']=entries(base_late)
awt=copy.deepcopy(ORIGINAL[8]);awt['name']='08B AWT 도입-마나 사용'
awt['passives']=entries({**base_late,AB:0})
fort=copy.deepcopy(next(g for g in ORIGINAL[6]['skills'] if g['id'].endswith('SkillGemFortifyingCry')))
awt['skills']=[fort if g['id'].endswith('SkillGemFortifyingCry') else copy.deepcopy(g) for g in awt['skills']]
awt_skill=next(g for g in awt['skills'] if g['id'].endswith('SkillGemAncestralWarriorTotem'))
shock=next(g for g in ORIGINAL[6]['skills'] if g['id'].endswith('SkillGemShockwaveTotem'))
earth=next(g for g in awt_skill['support_skills'] if g['id'].endswith('SkillGemEarthshatter'))
urgent=next(g for g in shock['support_skills'] if g['id'].endswith('SupportGemAncestralUrgency'))
brutal=next(g for g in shock['support_skills'] if g['id'].endswith('SupportGemBrutalityTwo'))
awt_skill['support_skills']=copy.deepcopy([earth,urgent,brutal])
# Keep the mana flask until the separately gated Blood Magic transition.
awt['inventory_slots']=[i for i in awt['inventory_slots'] if i['inventory_id']!='Flask1']+copy.deepcopy([i for i in ORIGINAL[6]['inventory_slots'] if i['inventory_id']=='Flask1'])
blood=copy.deepcopy(awt);blood['name']='08C 혈마법-회복 확인 후'
blood['passives']=entries({**state(awt),BM:0})
blood['inventory_slots']=[i for i in blood['inventory_slots'] if not(i['inventory_id']=='Flask1' and i['slot_x']==1)]

BUILDS=[early,second,copy.deepcopy(ORIGINAL[2]),copy.deepcopy(ORIGINAL[3]),copy.deepcopy(ORIGINAL[4]),cry_trial,
        copy.deepcopy(ORIGINAL[5]),copy.deepcopy(ORIGINAL[6]),copy.deepcopy(ORIGINAL[7]),prepare,awt,blood,copy.deepcopy(ORIGINAL[8])]
assert len(BUILDS)==13

def try_transaction_plan(a,b,ordinary_spare=0,weapon_spare=0):
    current=state(a); goal=state(b); max_cost=max(costs(current)['ordinary'],costs(goal)['ordinary'])
    max_cost+=ordinary_spare
    max_ws=[max(costs(current)['sets'][i],costs(goal)['sets'][i])+weapon_spare for i in (0,1)]
    operations=[]
    while current!=goal:
        options=[('환불',k,None) for k in current if k not in goal]
        options += [('재배정',k,goal[k]) for k in current if k in goal and current[k]!=goal[k]]
        options += [('추가',k,goal[k]) for k in goal if k not in current]
        for action,k,new_binding in options:
            test=dict(current);old_binding=current.get(k)
            if action in ('환불','임시 환불'): del test[k]
            else:test[k]=new_binding
            c=costs(test)
            if legal(test) and c['ordinary']<=max_cost and all(c['sets'][i]<=max_ws[i] for i in (0,1)):
                operations.append({'action':action,'id':k,'name':NS[k]['name'],'from':old_binding,'to':new_binding,'cost':c})
                current=test;break
        else: return None
        assert len(operations)<1500, ('transition loop',a['name'],b['name'])
    return operations

def transaction_plan(a,b):
    # A spare allocation point is not the same as a refund. Require and report
    # the actual peak pool instead of temporarily refunding useful skills over
    # and over, or assuming that levelling grants weapon-set quest rewards.
    for allowance in range(17):
        for ordinary_spare in range(allowance+1):
            weapon_spare=allowance-ordinary_spare
            if ordinary_spare>8 or weapon_spare>8:continue
            got=try_transaction_plan(a,b,ordinary_spare,weapon_spare)
            if got is not None:return got
    raise AssertionError(('no bounded transition',a['name'],b['name']))

plans=[]
for a,b in zip(BUILDS,BUILDS[1:]):
    assert legal(state(a)) and legal(state(b))
    operations=transaction_plan(a,b)
    all_costs=[costs(state(a)),costs(state(b))]+[o['cost'] for o in operations]
    pool={'ordinary':max(c['ordinary'] for c in all_costs),'sets':[max(c['sets'][i] for c in all_costs) for i in (0,1)]}
    plans.append({'from':a['name'],'to':b['name'],'from_cost':costs(state(a)),'to_cost':costs(state(b)),
                  'required_pool':pool,'refunded_entries':sum(o['action']=='환불' for o in operations),'operations':operations})
for b in BUILDS:
    assert len(b['name'])<=40
    assert all(k not in state(b) for k in ['stun4_','stun5']) if b['name'].startswith(('01 ','02 ')) else True
    dump(OUT/'BuildPlanner'/(b['name']+'.build'),b)
dump(HERE/'transition_operations_v2.json',plans)
dump(HERE/'progression_v2.json',[{'file':b['name']+'.build',**costs(state(b))} for b in BUILDS])
for p in (HERE/'ready/Filters').glob('*.filter'): shutil.copy2(p,OUT/'Filters'/p.name)
# Apply the urgent early-tree correction immediately to the game installation.
for b in (early,second):
    src=OUT/'BuildPlanner'/(b['name']+'.build');dest=GAME/'BuildPlanner'/src.name
    assert dest.exists()
    backup=HERE/'installed_before_revision2'/src.name
    backup.parent.mkdir(exist_ok=True)
    if not backup.exists():shutil.copy2(dest,backup)
    shutil.copy2(src,dest)
    assert src.read_bytes()==dest.read_bytes()
print(json.dumps({'early_trees_installed':True,'progression':[{'from':p['from'],'to':p['to'],'refunds':p['refunded_entries'],'operations':len(p['operations']),'pool':p['required_pool']} for p in plans]},ensure_ascii=False,indent=2))
