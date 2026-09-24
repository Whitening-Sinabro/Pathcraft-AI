"""Read the serialized planners and independently compare them to source XML."""
from pathlib import Path
import collections, hashlib, json, re, sys, xml.etree.ElementTree as E
sys.stdout.reconfigure(encoding='utf-8')
H=Path(__file__).resolve().parent; R=H.parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
X=E.parse(H/'sources/arserina_27e13.xml').getroot(); C=E.parse(H/'sources/FR_FBBurger_38.xml').getroot()
raw=read(R/'data/_cache/tree_0_5.json')
N={n['stringId']:n for n in raw['nodes'].values() if isinstance(n,dict) and 'stringId'in n}
I={n['skill']:k for k,n in N.items()};A=collections.defaultdict(set)
for k,n in N.items():
 for edge in n.get('connections',[]):
  if edge['id'] in I:A[k].add(I[edge['id']]);A[I[edge['id']]].add(k)
def xmlstate(s):
 out={I[int(k)]:0 for k in s.get('nodes').split(',')}
 for w in (1,2):
  for elem in s.findall('WeaponSet'+str(w)):
   out.update({I[int(k)]:w for k in elem.get('nodes','').split(',') if k})
 return out
def state(b):return {n['id']:n.get('weapon_set',0) for n in b['passives']}
def walk(nodes,root):
 todo=[root];visited=set()
 while todo:
  k=todo.pop()
  if k in visited:continue
  visited.add(k);todo.extend(A[k]&nodes-visited)
 return nodes<=visited
def check(s):
 assert set(s)<=set(N)
 for w in (1,2):
  nodes={k for k,v in s.items() if v in (0,w)}
  asc={k for k in nodes if N[k].get('ascendancyName')}
  assert walk(nodes-asc,'duelist597'),('disconnected regular',w)
  assert walk(asc,'AscendancyMercenary3Start'),('disconnected ascendancy',w)
def cost(s):
 regular={k:v for k,v in s.items() if not N[k].get('ascendancyName') and not N[k].get('classesStart')}
 return max(sum(v in (0,w) for v in regular.values()) for w in (1,2))
def groups(ss):
 out=[];seen=set()
 for s in ss.findall('Skill'):
  if s.get('enabled')=='false':continue
  gs=tuple(g.get('gemId') for g in s.findall('Gem') if g.get('gemId') and g.get('enabled')!='false')
  if not gs:continue
  if s.get('source') and gs[0] in seen:continue
  out.append(gs);seen.add(gs[0])
 return collections.Counter(out)
G={g['Id']:g['Name'] for g in read(R/'data/game_data_poe2/BaseItemTypes.json')}
P=sorted((H/'BuildPlanner').glob('*.build'));assert len(P)==4
B=[read(p) for p in P];states=[state(b) for b in B]
report={'checks':[],'transitions':[],'game_runtime_verified':False}
for i,(p,b) in enumerate(zip(P,B)):
 assert set(b)=={'name','author','link','description','ascendancy','passives','skills','inventory_slots'}
 assert b['ascendancy']=='Mercenary3' and len(b['name'])<=40
 assert len(states[i])==len(b['passives']);check(states[i])
 assert all(q in b['description'] for q in ['지금 할 일','무기·스킬셋','사용 순서'])
 actual=[];sgids=[]
 for g in b['skills']:
  assert set(g)<={'id','level_interval','support_skills','additional_text'}
  sgids.append(g['id'])
  for child in [g,*g.get('support_skills',[])]:
   assert child['id'] in G,child['id']
   assert re.search('[가-힣]',child['additional_text'])
   assert child['level_interval']==[1,100]
  children=[c['id'] for c in g.get('support_skills',[])]
  assert all('SupportGem'in c for c in children)
  if g['id'].endswith('SkillGemTemporalChains'):
   assert '신성 모독 안에' in g['additional_text'];continue
  if g['id'].endswith('SkillGemBlasphemy'):
   tc=next(x['id'] for x in b['skills'] if x['id'].endswith('SkillGemTemporalChains'))
   children.insert(0,tc)
  actual.append((g['id'],*children))
 assert len(sgids)==len(set(sgids)),('duplicate skill',p.name)
 ss=C.find('Skills/SkillSet') if i==0 else X.findall('Skills/SkillSet')[i+1]
 assert collections.Counter(actual)==groups(ss),('source gems mismatch',p.name)
 for inv in b['inventory_slots']:
  assert set(inv)<={'inventory_id','slot_x','slot_y','level_interval','additional_text','unique_name'}
  assert inv['slot_x']>=0 and inv['slot_y']>=0
  assert re.search('[가-힣]',inv['additional_text'])
 if i:assert states[i]==xmlstate(X.findall('Tree/Spec')[i+1])
 else:
  current=xmlstate(C.find('Tree/Spec'));assert current.items()<=states[0].items()
  adds=set(states[0])-set(current);assert len(adds)==13
  assert adds<=set(xmlstate(X.findall('Tree/Spec')[1]))
  assert all(not N[k].get('ascendancyName') for k in adds)
  assert not any('AscendancyMercenary1' in k for k in states[0])
  assert not any('SupportingFire'in k for k in sgids)
  ordered=read(H/'generation.json')['bridge_addition_order']
  for k in ordered:current[k]=0;check(current)
  assert current==states[0] and cost(current)==60
 report['checks'].append({'file':p.name,'source_gems_match':True,'source_tree_match_or_explicit_bridge':True,
    'all_ids_valid':True,'both_weapon_sets_connected':True,'ordinary_points':cost(states[i]),
    'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
for t in read(H/'transition.json'):
 s=dict(states[t['from_stage']-1]);maxcost=cost(s)
 for op in t['operations']:
  if op['action']=='refund':assert s.pop(op['id'])==op['weapon_set']
  else:assert op['id'] not in s;s[op['id']]=op['weapon_set']
  check(s);maxcost=max(maxcost,cost(s));assert maxcost<=t['required_pool']
 assert s==states[t['to_stage']-1]
 report['transitions'].append({'from':t['from_stage'],'to':t['to_stage'],'operations':len(t['operations']),
    'refunds':t['refunds'],'peak_ordinary':maxcost,'every_step_connected':True})
assert not read(H/'generation.json')['untranslated_current_item_mods']
bad={**states[0],'not_a_valid_poe2_node':0}
try:check(bad)
except AssertionError:report['invalid_node_rejected']=True
else:raise AssertionError('bad node accepted')
(H/'validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
