"""Generate exact late transition routes from each optional defence prefix."""
from pathlib import Path
import ast,collections,json
HERE=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
TREE=read(HERE/'sources/tree_0_5.json')
NS={n['stringId']:n for n in TREE['nodes'].values() if 'stringId' in n}
NUM={n['skill']:sid for sid,n in NS.items()}
ADJ=collections.defaultdict(set)
for sid,n in NS.items():
    for c in n.get('connections',[]):
        if c['id'] in NUM:ADJ[sid].add(NUM[c['id']]);ADJ[NUM[c['id']]].add(sid)
CLASS_ROOT='marauder594';ASC_ROOT='AscendancyWarrior2Start'
# Load pure planner functions only. Do not run the generator's installation code.
source=ast.parse((HERE/'smooth_transitions.py').read_text(encoding='utf-8'))
names={'state','entries','linked','legal','costs','try_transaction_plan','transaction_plan'}
functions=[n for n in source.body if isinstance(n,ast.FunctionDef) and n.name in names]
exec(compile(ast.Module(body=functions,type_ignores=[]),'passive_planning_functions','exec'),globals())
builds={p.stem.split()[0]:read(p) for p in (HERE/'revision2/BuildPlanner').glob('*.build')}
all_plans=read(HERE/'transition_operations_v2.json')
expansion=next(p for p in all_plans if p['from'].startswith('07 '))['operations']
assert len(expansion)==14 and all(o['action']=='추가' for o in expansion)
alternatives=[]
initial=state(builds['07']);goal=builds['08A']
for used in range(14):
    current={**builds['07'],'name':f'07 + 선택 방어 {used}점','passives':entries(initial)}
    operations=transaction_plan(current,goal)
    track=[costs(initial)]+[o['cost'] for o in operations]
    pool={'ordinary':max(c['ordinary'] for c in track),'sets':[max(c['sets'][i] for c in track) for i in (0,1)]}
    assert pool['ordinary']<=97 and pool['sets']==[22,22]
    alternatives.append({'defence_points_used':used,'from':current['name'],'to':goal['name'],'initial_passives':current['passives'],
                         'required_pool':pool,'refunded_entries':sum(o['action']=='환불' for o in operations),'operations':operations})
    op=expansion[used];initial[op['id']]=op['to']
(HERE/'partial_transitions_v2.json').write_text(json.dumps(alternatives,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'Prepared {len(alternatives)} optional-defence routes (0 through 13 points); 14-point route remains the main 08 transition.')
