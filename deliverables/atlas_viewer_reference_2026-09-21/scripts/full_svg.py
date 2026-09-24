"""본 트리 + 서브트리 전체의 하코 찍는 순서 그림. 단계별 모양, 툴팁에 순번."""
import html
import json
import sys

sys.path.insert(0, 'atlas_src')
from full_order import N, cat  # noqa: E402

XY = json.load(open('ninja/screen_xy.json'))
R = json.load(open('atlas_src/hc_route_result.json', encoding='utf-8'))
F = json.load(open('atlas_src/full_order.json', encoding='utf-8'))
KO = {'Expedition': '탐험', 'Ritual': '의식', 'Breach': '균열', 'Abyss': '심연', 'Delirium': '환영', 'Incursion': '인커전'}

idx = {}
import hc_route  # noqa: E402
hc_route.COST.update({'위험': 30, '주의': 2})
_, _steps = hc_route.route(R['targets'])
early = [k for st in _steps for k in st['ids']]
assert set(early) == set(R['nodes']) - {k for k in R['nodes'] if N[k].get('isRootOfAtlasTree')}, 'early route mismatch'
for i, k in enumerate(early, start=1):
    idx[k] = ('본', i, '초록')
for i, k in enumerate(F['main_rest'], start=len(early) + 1):
    stage = '파랑' if i <= 205 else '노랑' if i <= 265 else '주황' if i <= 299 else '빨강'
    idx[k] = ('본', i, stage)
for st, ko in KO.items():
    seq = F[st]
    risky_from = next((j for j, k in enumerate(seq) if cat(k) in ('주의', '위험')), len(seq))
    for j, k in enumerate(seq, start=1):
        idx[k] = (ko, j, '초록' if j <= risky_from else '빨강')

STAGE_CLS = {'초록': 'g', '파랑': 'b', '노랑': 'y', '주황': 'o', '빨강': 'r'}
local = {}
labels = []
def stg(k):
    return STAGE_CLS[idx[k][2]] if k in idx else 'root'
out = ['<svg id="stagesvg" viewBox="0 0 1444 1489" role="img" aria-label="하코 아틀라스 전체 찍는 순서">']
for k, n in N.items():
    for o in n['out']:
        if o in N and n.get('subTree') == N[o].get('subTree'):
            (a, b), (c, d) = XY[k], XY[o]
            ls = stg(k) if stg(k) == stg(o) else (stg(o) if stg(k) == 'root' else stg(k) if stg(o) == 'root' else 'mix')
            out.append(f'<line class="fl" data-s="{ls}" x1="{a:.1f}" y1="{b:.1f}" x2="{c:.1f}" y2="{d:.1f}"/>')
for k, n in N.items():
    x, y = XY[k]
    r = 9 if n.get('isRootOfAtlasTree') else 7 if n.get('isKeystone') else 5 if n.get('isNotable') else 3.4
    if k not in idx:
        out.append(f'<circle class="fn root" data-s="root" cx="{x:.1f}" cy="{y:.1f}" r="{r}"><title>{html.escape(n["name"])} — 시작점</title></circle>')
        continue
    tree, i, stage = idx[k]
    pos = f'{i}번째'
    tip = f'{n["name"]} — {tree} 트리 {pos} · {stage} · {cat(k)}'
    local[STAGE_CLS[stage]] = local.get(STAGE_CLS[stage], 0) + 0
    labels.append((x, y, STAGE_CLS[stage], i, k))
    out.append(f'<circle class="fn {STAGE_CLS[stage]}" data-s="{STAGE_CLS[stage]}" data-k="{k}" data-i="{i}" data-t="{tree}" cx="{x:.1f}" cy="{y:.1f}" r="{r}"><title>{html.escape(tip)}</title></circle>')
out.append('<g id="numlayer">')
for x, y, st, i, k in labels:
    out.append(f'<text class="nl" data-s="{st}" data-k="{k}" x="{x:.1f}" y="{y - 9:.1f}">{i}</text>')
out.append('</g><circle id="cursor" r="16" cx="-100" cy="-100"/>')
out.append('</svg>')
lists = {c: [] for c in STAGE_CLS.values()}
for k, (tree, i, stage) in idx.items():
    lists[STAGE_CLS[stage]].append({'t': tree, 'i': i, 'n': N[k]['name'], 'c': cat(k), 'k': k})
for c in lists:
    lists[c].sort(key=lambda r: (r['t'] != '본', r['t'], r['i']))
json.dump(lists, open('atlas_src/stage_lists.json', 'w', encoding='utf-8'), ensure_ascii=False)
open('atlas_src/full_order.svg', 'w', encoding='utf-8').write('\n'.join(out))
print('ok', len(idx))
