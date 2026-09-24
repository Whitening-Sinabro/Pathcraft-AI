"""poe.ninja POE2 아틀라스 데이터 + 방송 화면 판독 결과로 임성빈 최종 트리를 SVG 로 만든다."""
import json, html
d = json.load(open('atlas_tree.json', encoding='utf-8')); N = d['nodes']
XY = json.load(open('screen_xy.json'))
FULL = {'MAIN', 'Ritual', 'Abyss', 'Expedition'}
DL_OFF = {'317', '25235', '55418', '61491', '56053'}
DL_UNKNOWN = {'45796', '41958', '36773', '35619', '41113', '47144', '58666', '62042', '22753', '55157'}
CHOICE = {'4728': 2, '38492': 3, '7116': 2, '31008': 1, '15634': 3, '41868': 2, '26766': 3,
          '965': 1, '25524': 2, '35469': 2, '42673': 1, '379': 6, '21420': 2}
def st(n): return n.get('subTree', 'MAIN')
def state(k, n):
    s = st(n)
    if s in FULL: return 'on'
    if s == 'Delirium':
        if k in DL_OFF: return 'off'
        if k in DL_UNKNOWN: return 'unk'
        return 'on'
    return 'off'
cls = {'MAIN': 'm', 'Ritual': 'ri', 'Abyss': 'ab', 'Expedition': 'ex', 'Delirium': 'de', 'Breach': 'br', 'Incursion': 'in'}
out = ['<svg viewBox="0 0 1444 1489" role="img" aria-label="임성빈 최종 아틀라스 트리 전체">']
for k, n in N.items():
    for o in n['out']:
        if o not in N: continue
        a, b = state(k, n), state(o, N[o])
        c = 'e-on ' + cls[st(n)] if a == 'on' and b == 'on' and st(n) == st(N[o]) else 'e-off'
        (x1, y1), (x2, y2) = XY[k], XY[o]
        out.append(f'<line class="{c}" x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}"/>')
for k, n in N.items():
    x, y = XY[k]; s = st(n); stt = state(k, n)
    r = 9 if n.get('isRootOfAtlasTree') else 7.5 if n.get('isKeystone') else 5 if n.get('isNotable') else 3.2
    stats = '; '.join(f"{t['id']} {t['v']}" for t in n['stats'])[:160]
    tip = n['name'] + (f' — 선택 {CHOICE[k]}번' if k in CHOICE else '') + {'on': '', 'off': ' (미할당)', 'unk': ' (할당 여부 미확인)'}[stt]
    out.append(f'<circle class="n {stt} {cls[s]}" cx="{x:.1f}" cy="{y:.1f}" r="{r}"><title>{html.escape(tip)}</title></circle>')
    if k in CHOICE:
        out.append(f'<text class="ch" x="{x:.1f}" y="{y+4:.1f}">{CHOICE[k]}</text>')
labels = [('본 트리 336/336', 729, 30), ('의식 36/36', 180, 915), ('인커전 0/36', 1254, 905), ('환영 22/31', 210, 1475), ('균열 0/32', 566, 1475), ('심연 35/35', 906, 1475), ('탐험 24/24', 1234, 1475)]
for t, x, y in labels:
    out.append(f'<text class="lb" x="{x}" y="{y}">{t}</text>')
out.append('</svg>')
open('tree.svg', 'w', encoding='utf-8').write('\n'.join(out))
on = sum(1 for k, n in N.items() if state(k, n) == 'on' and not n.get('isRootOfAtlasTree'))
print('allocated(non-root, confirmed):', on, ' unknown:', len(DL_UNKNOWN))
