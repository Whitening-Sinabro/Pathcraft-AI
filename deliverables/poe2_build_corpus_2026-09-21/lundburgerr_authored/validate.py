"""Independent replay of generated authored transition and preservation contracts."""
from pathlib import Path
import sys,json,hashlib,collections
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from lundburgerr_authored.compose import Composer,read,sha,dump,START
from native_planner.generate import check_shape
c=Composer();pack=read(ROOT/'planner_data/build_data.json');base=ROOT/'native_planner/versions/pre_transition_20260921'
old=read(base/'planner_data/build_data.json')
for key,val in old.items():
 if key not in ('campaign_stages','tree'):assert pack[key]==val,key
assert pack['campaign_stages_previous_pathcraft']==old['campaign_stages']
for k in ('nodes','edges'):assert pack['tree'][k][:len(old['tree'][k])]==old['tree'][k]
models={s['id']:c.map(v) for s,v in zip(pack['authored_stages'],c.doc['data']['buildVariants']['values'])}
latest=pack['stages'][-1];sets={int(n):w for w in (1,2) for n in latest['weapon_set_nodes'][str(w)]}
models['kitava-29d39']={int(n['id']):sets.get(int(n['id']),0) for n in latest['passives'] if not n.get('ascendancyName') and int(n['id'])!=START}
models['start']={};checks=[]
for seg in pack['transition_plan']['segments']:
 state=dict(models[seg['from_stage']]);seen=set()
 for op in seg['steps']:
  key=op['action'],op['numeric_id'];assert key not in seen;seen.add(key)
  n=op['numeric_id'];w=op['weapon_set']
  assert c.nodes[n]['stringId']==op['string_id']
  if op['action']=='refund':assert state.pop(n)==w
  else:assert n not in state;state[n]=w
  assert c.connected(state)
  budget=c.budgets(state)
  for k,val in budget.items():
   if k not in ('ascendancy_points_required','free_ascendancy_nodes'):assert op['budget_after'][k]==val,(seg['id'],op['number'],k)
  assert budget['ordinary_points_required']<=seg['ordinary_peak']
  assert budget['weapon_specialization_capacity_required']<=seg['weapon_capacity_peak']
  assert op['budget_after']['ascendancy_points_required']==seg['from_budget']['ascendancy_points_required']
  if op['temporary_refund']:assert op['temporary_refund_reason']
 assert state==models[seg['to_stage']]
 checks.append({'id':seg['id'],'steps':len(seen),'both_sets_every_step':True,'no_duplicate_action_id':True,'refunds':seg['refund_count'],'adds':seg['add_count'],'from_asc':seg['from_budget']['ascendancy_points_required'],'to_asc':seg['to_budget']['ascendancy_points_required']})
frozen={};native=[]
for p in sorted((ROOT/'native_planner').glob('*.build')):
 b=read(p);check_shape(b)
 if p.name.startswith(('archive-','current-kitava-')):
  assert p.read_bytes()==(base/'native_planner'/p.name).read_bytes();frozen[p.name]=sha(p)
 else:
  for passive in b['passives']:assert passive['level_interval']==[1,100] and passive['weapon_set'] in (0,1,2) and passive['id'] in c.by_string
  for skill in b['skills']:
   for g in [skill,*skill.get('support_skills',[])]:assert g['id'] in c.gems and g['level_interval']==[1,100]
 native.append({'file':p.name,'sha256':sha(p)})
assert len(frozen)==5 and len(native)==13
assert len(latest['passives'])==151 and [sum(n['weapon_set']==w for n in read(ROOT/'native_planner/current-kitava-29d39.build')['passives']) for w in (0,1,2)]==[104,24,23]
assert all('\ufffd' not in p.read_text(encoding='utf-8-sig') for p in [ROOT/'planner_data/build_data.json',*(ROOT/'native_planner').glob('*.build')])
result={'status':'passed','pack_sha256':sha(ROOT/'planner_data/build_data.json'),'native13':native,'frozen_latest_archive5':frozen,'segments':checks,'baseline_metadata_and_tree_prefix_exact':True,'authored_graphs':8,'game_pass':False}
dump(ROOT/'lundburgerr_authored/final_validation.json',result)
print(json.dumps(result))
