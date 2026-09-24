"""58포인트 이후 본 트리 나머지 + 서브트리별 하코 순서.

원칙: 이미 찍은 곳에 붙은 노드 중 안전 → 선택형 → 주의 → 위험 순으로 하나씩 고른다.
위험 노드 뒤에 안전 노드가 막혀 있으면 그때만 위험을 먼저 뚫는다(최소 경로 비용으로).
"""
import heapq
import json
import re
import sys

sys.path.insert(0, 'atlas_src')
from classify import N, cat as main_cat  # noqa: E402

XY = json.load(open('ninja/screen_xy.json'))

SUB_DANGER = re.compile(r'modifier_chance|affliction_modifier|lichborn|abyssal_modifier|corrupts_rare|'
                        r'rare_monster_modifiers|additional_affliction')
SUB_MORE = re.compile(r'monster_spawn_amount|magic_monsters_\+|rare_monsters_\+|additional_rare|enrage|boss|'
                      r'overrun|escalation|summon_enemies|at_least_magic|sentinels|black_knight|wildwood_packs|'
                      r'number_of_magic_and_rare_packs|additional_waves|secondary_encounter')
RANK = {'안전': 0, '선택형': 1, '주의': 2, '위험': 3, '시작점': -1}


def cat(nid):
    n = N[nid]
    if 'subTree' not in n:
        return main_cat(nid)
    if n.get('isRootOfAtlasTree'):
        return '시작점'
    if n.get('isKeystone'):
        return '선택형'
    s = ' '.join(x['id'] for x in n['stats'])
    if 'jewel' in s:
        return '안전'
    if 'ritual_rite_additional_modifier' in s:
        return '주의'
    if SUB_DANGER.search(s) and 'expedition2_remnant' not in s:
        return '위험'
    if SUB_MORE.search(s) or 'expedition2_remnant' in s:
        return '주의' if 'rare_monster_modifiers' not in s else '위험'
    return '안전'


def graph(members):
    adj = {k: set() for k in members}
    for k in members:
        for o in N[k]['out']:
            if o in members:
                adj[k].add(o)
                adj[o].add(k)
    return adj


def order(members, start):
    """start 에서 시작해 members 를 전부 찍는 순서. 안전한 것부터."""
    adj = graph(members)
    have = set(start)
    seq = []
    last = next(iter(start)) if len(start) == 1 else None
    while len(have) < len(members):
        frontier = {v for u in have for v in adj[u]} - have

        def near(v):
            # 같은 등급이면 방금 찍은 노드 옆 → 가까운 노드 순. 그래야 길을 따라 이어진다
            if last is None:
                return (1, 0.0)
            (x1, y1), (x2, y2) = XY[v], XY[last]
            return (0 if v in adj[last] else 1, (x1 - x2) ** 2 + (y1 - y2) ** 2)
        best = min(frontier, key=lambda v: (RANK[cat(v)], near(v), v))
        if RANK[cat(best)] >= 2:
            # 위험/주의를 뚫기 전에, 그 뒤에 숨은 안전 노드가 있으면 가장 싼 길로 한 칸만 연다
            target = cheapest_gate(adj, have)
            if target:
                best = target
        have.add(best)
        seq.append(best)
        last = best
    return seq


def cheapest_gate(adj, have):
    """남은 안전 노드로 가는 최소 비용 경로의 첫 칸."""
    cost = {'안전': 1, '선택형': 1, '주의': 5, '위험': 25, '시작점': 0}
    dist = {k: 0 for k in have}
    first = {}
    pq = [(0, k) for k in have]
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist.get(u, 1e9):
            continue
        if u not in have and cat(u) in ('안전', '선택형'):
            return first[u]
        for v in adj[u]:
            if v in have:
                continue
            nd = d + cost[cat(v)]
            if nd < dist.get(v, 1e9):
                dist[v] = nd
                first[v] = v if u in have else first[u]
                heapq.heappush(pq, (nd, v))
    return None


def phases(seq):
    out = []
    for i, k in enumerate(seq):
        c = cat(k)
        if not out or out[-1]['cat'] != c:
            out.append({'cat': c, 'from': i, 'names': []})
        out[-1]['names'].append(N[k]['name'])
        out[-1]['to'] = i
    return out


if __name__ == '__main__':
    R = json.load(open('atlas_src/hc_route_result.json', encoding='utf-8'))
    main = {k for k, n in N.items() if 'subTree' not in n}
    rest = order(main, set(R['nodes']))
    base = len(R['nodes']) - 1
    result = {'main_start': base, 'main_rest': rest}
    print(f'본 트리 {base} → {base + len(rest)}')
    for p in phases(rest):
        print(f"  {base + p['from'] + 1:>3}~{base + p['to'] + 1:<3} {p['cat']} x{len(p['names'])}  {p['names'][:4] if p['cat'] in ('위험', '주의') else ''}")
    for st in ['Expedition', 'Ritual', 'Breach', 'Abyss', 'Delirium', 'Incursion']:
        mem = {k for k, n in N.items() if n.get('subTree') == st}
        root = next(k for k in mem if N[k].get('isRootOfAtlasTree'))
        seq = order(mem, {root})
        result[st] = seq
        print(f'{st} {len(seq)}')
        for p in phases(seq):
            print(f"  {p['from'] + 1:>3}~{p['to'] + 1:<3} {p['cat']} x{len(p['names'])}  {p['names'] if p['cat'] in ('위험', '주의', '선택형') else ''}")
    json.dump(result, open('atlas_src/full_order.json', 'w', encoding='utf-8'), ensure_ascii=False)
