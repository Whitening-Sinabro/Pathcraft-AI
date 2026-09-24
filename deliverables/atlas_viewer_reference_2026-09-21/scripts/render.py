"""poe.ninja POE2 atlas 데이터로 전체 트리를 그린다. 할당 상태는 인자로 받은 규칙대로 칠한다."""
import json, math, sys
from PIL import Image, ImageDraw
d = json.load(open('atlas_tree.json', encoding='utf-8'))
G, N = d['groups'], d['nodes']
R = [0,82,162,335,493,662,846,270,1050,1300]; P = [1,12,24,24,72,72,72,24,72,144]
def pos(n):
    g = G[n['group']]; r = R[n['orbit']]; a = 2*math.pi*n['orbitIndex']/P[n['orbit']]
    return g['x'] + r*math.sin(a), g['y'] - r*math.cos(a)
XY = {k: pos(n) for k, n in N.items()}
xs = [p[0] for p in XY.values()]; ys = [p[1] for p in XY.values()]
S = 0.12; pad = 60
W = int((max(xs)-min(xs))*S)+2*pad; H = int((max(ys)-min(ys))*S)+2*pad
def T(p): return ((p[0]-min(xs))*S+pad, (p[1]-min(ys))*S+pad)
json.dump({k: T(v) for k, v in XY.items()}, open('screen_xy.json','w'))
print(W, H)
