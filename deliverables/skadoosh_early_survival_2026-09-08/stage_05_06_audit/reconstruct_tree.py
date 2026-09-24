"""VOD-directed reconstruction; do not label exact until frame audit completes."""
from pathlib import Path
import json,sys
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parents[1]/'skadoosh_hc_2026-09-07'))
import progression_core as p
plans=HERE.parent/'BuildPlanner'
old=p.state(json.loads(next(plans.glob('04*')).read_text(encoding='utf8')))
proposal=p.state(json.loads(next(plans.glob('05*')).read_text(encoding='utf8')))
s=dict(old)
for n in ['attributes51','strength61_']:s.pop(n)
s.update(dict.fromkeys(['armour6','strength26','strength25','strength24_','strength23'],0))
start=dict(s)
remove20=[n for n in s if n.startswith(('melee','attack_speed','life_costs')) or n in ['marauder_brute_notable1','reduced_attack_cost4','strength58','strength19','armour5']]
assert len(remove20)==20
for n in remove20:s.pop(n)
add_common=[n for n,w in proposal.items() if not w and n not in s and not p.NS[n].get('ascendancyName') and not n.startswith('physical') and n!='criticals93_']
s.update(dict.fromkeys(add_common,0))
for n in ['shield15','shield16','shield1','shield5','slow_attacks2_','slow_attacks3','slow_attacks5','slow_attacks10','totems1','totems8','totems26','totems25','armour_break37']:s.pop(n)
s.update(dict.fromkeys(['warcries1','warcries18'],1))
s.update(dict.fromkeys(['totems36','totems37','totems19','totems21','totems35','totems33_'],2))
assert p.legal(start) and p.costs(start)=={'ordinary':70,'sets':[16,16],'ascendancy':4}
assert p.legal(s) and p.costs(s)=={'ordinary':71,'sets':[14,14],'ascendancy':4},(p.legal(s),p.costs(s))
data={'kind':'VOD-directed candidate pending complete node review','costs':p.costs(s),'passives':p.entries(s),'initial54':p.entries(start),'remove20':remove20,'new_common':add_common}
(HERE/'tree54_candidate.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'costs':p.costs(s),'legal':p.legal(s),'new_common':add_common},ensure_ascii=False))
