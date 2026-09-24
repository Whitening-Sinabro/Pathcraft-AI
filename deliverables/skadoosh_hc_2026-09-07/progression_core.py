from __future__ import annotations
import collections,copy,hashlib,json,re,shutil,zipfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text(encoding="utf-8-sig"))
tree = read(HERE/'sources/tree_0_5.json')
NS = {n['stringId']: n for n in tree['nodes'].values() if 'stringId' in n}
NUM = {n['skill']:sid for sid,n in NS.items()}
ADJ = collections.defaultdict(set)
for sid,n in NS.items():
    for c in n.get('connections',[]):
        if c['id'] in NUM: ADJ[sid].add(NUM[c['id']]); ADJ[NUM[c['id']]].add(sid)
CLASS_ROOT = 'marauder594'
ASC_ROOT = 'AscendancyWarrior2Start'
def dump(p,d): p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
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
