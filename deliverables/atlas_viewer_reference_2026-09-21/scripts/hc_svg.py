"""하코 초반 경로를 본 트리 위에 그린다. 찍는 노드 = 위험도 색, 목표 = 순서 번호."""
import json, html, sys
sys.path.insert(0, 'atlas_src')
from classify import cat, N
XY = json.load(open('ninja/screen_xy.json'))
R = json.load(open('atlas_src/hc_route_result.json', encoding='utf-8'))
have = set(R['nodes'])
order = {}
for i, s in enumerate(R['steps'], 1):
    order[next(k for k in N if N[k]['name'] == s['target'] and 'subTree' not in N[k])] = i
MAIN = [k for k, n in N.items() if 'subTree' not in n]
xs = [XY[k][0] for k in MAIN]; ys = [XY[k][1] for k in MAIN]
x0, y0, x1, y1 = min(xs) - 20, min(ys) - 20, max(xs) + 20, max(ys) + 20
CLS = {'위험': 'dg', '주의': 'cu', '안전': 'sf', '선택형': 'ch', '시작점': 'sf'}
out = [f'<svg viewBox="{x0:.0f} {y0:.0f} {x1-x0:.0f} {y1-y0:.0f}" role="img" aria-label="하코 초반 아틀라스 경로">']
for k in MAIN:
    for o in N[k]['out']:
        if o not in N or 'subTree' in N[o]: continue
        on = k in have and o in have
        (a, b), (c, d) = XY[k], XY[o]
        out.append(f'<line class="{"r-on" if on else "r-off"}" x1="{a:.1f}" y1="{b:.1f}" x2="{c:.1f}" y2="{d:.1f}"/>')
for k in MAIN:
    x, y = XY[k]; n = N[k]; c = cat(k)
    r = 9 if n.get('isRootOfAtlasTree') else 7 if n.get('isKeystone') else 5 if n.get('isNotable') else 3.2
    st = '; '.join(f"{t['id']} {t['v']}" for t in n['stats'])[:150]
    klass = f"rn {CLS[c]}" if k in have else "rn off"
    tip = f"{n['name']} — {c}" + (f" · 목표 {order[k]}" if k in order else '') + ('' if k in have else ' (이 경로에선 안 찍음)') + f"\n{st}"
    out.append(f'<circle class="{klass}" cx="{x:.1f}" cy="{y:.1f}" r="{r}"><title>{html.escape(tip)}</title></circle>')
for k, i in order.items():
    x, y = XY[k]
    out.append(f'<circle class="tg" cx="{x:.1f}" cy="{y-17:.1f}" r="10"/><text class="tn" x="{x:.1f}" y="{y-13:.1f}">{i}</text>')
out.append('</svg>')
open('atlas_src/hc_route.svg', 'w', encoding='utf-8').write('\n'.join(out)); print('ok', len(have))
