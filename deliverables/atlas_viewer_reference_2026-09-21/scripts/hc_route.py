"""하코 초반 아틀라스 경로: 목표 노드를 순서대로, 위험 노드를 최소로 지나가게 잇는다."""
import heapq, json, sys
sys.path.insert(0, 'atlas_src')
from classify import cat, N
COST = {'위험': 8, '주의': 2, '안전': 1, '선택형': 1, '시작점': 0}
MAIN = {k for k, n in N.items() if 'subTree' not in n}
ADJ = {k: set() for k in MAIN}
for k in MAIN:
    for o in N[k]['out']:
        if o in MAIN: ADJ[k].add(o); ADJ[o].add(k)
ROOT = next(k for k in MAIN if N[k].get('isRootOfAtlasTree'))

def path_to(have, target):
    dist = {k: 0 for k in have}; prev = {}; pq = [(0, k) for k in have]
    while pq:
        dcur, u = heapq.heappop(pq)
        if u == target: break
        if dcur > dist.get(u, 1e9): continue
        for v in ADJ[u]:
            nd = dcur + COST[cat(v)]
            if nd < dist.get(v, 1e9): dist[v] = nd; prev[v] = u; heapq.heappush(pq, (nd, v))
    p = []; u = target
    while u not in have: p.append(u); u = prev[u]
    return p[::-1]

def route(targets):
    have = {ROOT}; steps = []
    for name in targets:
        t = next(k for k in MAIN if N[k]['name'] == name)
        if t in have: continue
        p = path_to(have, t); have |= set(p)
        steps.append({'target': name, 'points': len(have) - 1, 'added': [(N[x]['name'], cat(x)) for x in p], 'ids': p})
    return have, steps

if __name__ == '__main__':
    T = json.loads(sys.argv[1])
    have, steps = route(T)
    for s in steps:
        risk = [n for n, c in s['added'] if c in ('위험', '주의')]
        print(f"{s['points']:>3}  → {s['target']}  (+{len(s['added'])})  지나감: {risk if risk else '-'}")
