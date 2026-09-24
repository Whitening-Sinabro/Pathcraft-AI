"""목표 순서를 바꿔 가며 위험 노드가 가장 적은 하코 초반 경로를 찾는다."""
import json, random, sys, collections
sys.path.insert(0, 'atlas_src')
import hc_route
from classify import cat, N
hc_route.COST.update({'위험': 30, '주의': 2})
T = ["Valuable Paths", "Eons of Domination", "Essence Dowsing", "Divined Blessing", "Eons of Contamination",
     "Specialised Seeker", "Archaeological Interest", "The Chosen Path", "Reverse Transcription",
     "Industrial Improvements", "Hidden Scars"]
def score(order):
    have, steps = hc_route.route(order)
    c = collections.Counter(cat(x) for x in have)
    return (c['위험'], c['주의'], len(have) - 1), have, steps
random.seed(7)
best = None
for i in range(1500):
    o = T[:] if i == 0 else random.sample(T, len(T))
    sc, have, steps = score(o)
    if best is None or sc < best[0]: best = (sc, o, have, steps)
sc, o, have, steps = best
print('best (위험, 주의, 포인트):', sc)
for s in steps:
    risk = [f"{n}({c})" for n, c in s['added'] if c in ('위험', '주의')]
    print(f"{s['points']:>3} → {s['target']}  지나감: {risk or '-'}")
json.dump({'targets': o, 'nodes': sorted(have), 'steps': steps, 'score': sc}, open('atlas_src/hc_route_result.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
