"""Resource-only stress cases. Echo cost alternatives remain explicitly unresolved."""
from pathlib import Path
import heapq,json,math
HERE=Path(__file__).resolve().parent
DATA={r['case']:r for r in json.loads((HERE/'v3_pob_results.json').read_text(encoding='utf-8'))}
def skill(r,name):return next(s['output'] for s in r['skills'] if s['active']==name)
def simulate(case,interval=1,incoming=0,policy='normal',echo_heal=False,totems=4):
    r=DATA[case];sets=list(r['sets'].values());life=min(x['Life'] for x in sets);mana=min(x['Mana'] for x in sets)
    regen=min(x['LifeRegen'] for x in sets);mr=min(x['ManaRegen'] for x in sets);hp=life;mp=mana;minimum=life;last=0;recent=[];events=[];busy=0;trace=[];seq=0
    cry=skill(r,'Fortifying Cry');t=skill(r,'Ancestral Warrior Totem' if r['stage']>=5 else 'Shockwave Totem')
    pact=r['stage']>=6;seismic=skill(r,'Seismic Cry') if pact else None
    direct_heal=life*.02 if r['urgent_call'] else 0;mana_heal=mana*.02 if r['urgent_call'] else 0
    def add(tm,kind):
        nonlocal seq
        heapq.heappush(events,(round(tm,6),seq,kind));seq+=1
    place=t['TotemPlacementTime'];cycle=t['TotemDuration']+place
    for n in range(totems):
        tm=n*place
        while tm<90:add(tm,'totem');tm+=cycle
    start=totems*place+.2;tm=start
    while tm<90:add(tm,'fort');tm+=interval
    if pact:
        tm=start+.5
        while tm<90:add(tm,'seismic');tm+=1
    add(90,'end');failure=None
    while events:
        now,_,kind=heapq.heappop(events)
        if now>90:break
        if kind in ('fort','seismic','totem') and now<busy-1e-5:add(busy,kind);continue
        if incoming>regen and hp-(incoming-regen)*(now-last)<=0:
            failure={'time':round(last+hp/(incoming-regen),2),'reason':'피격 가정'};minimum=0;break
        hp=min(life,hp+(regen-incoming)*(now-last));mp=min(mana,mp+mr*(now-last));last=now
        if kind=='end':break
        recent=[x for x in recent if x>now-4]
        s=t if kind=='totem' else seismic if kind=='seismic' else cry
        lc=s.get('LifeCost',0);mc=s.get('ManaCost',0)
        if kind=='echo':lc=mc=0
        if pact and kind in ('fort','echo'):
            if policy=='manual_only':
                if kind=='fort':lc+=life*.1*min(3,len(recent));recent.append(now)
            else:
                lc+=life*.1*min(3,len(recent)+1)
                if kind=='echo':lc+=cry['LifeCost']
                recent.append(now)
        if (lc>0 and hp<=lc) or mc>mp:
            failure={'time':round(now,2),'reason':'생명력 비용' if hp<=lc and lc>0 else '마나 비용','next_cost':round(lc,2)};break
        hp-=lc;mp-=mc;minimum=min(minimum,hp)
        if kind in ('fort','seismic') or kind=='echo' and echo_heal:
            hp=min(life,hp+direct_heal);mp=min(mana,mp+mana_heal)
        if kind=='fort' and pact:add(now+1.3,'echo');add(now+2.6,'echo')
        if kind=='totem':busy=now+place
        if kind in ('fort','seismic'):busy=now+1/s['Speed']
        trace.append({'t':round(now,2),'event':kind,'life':round(hp,2),'mana':round(mp,2),'life_cost':round(lc,2)})
    return {'case':case,'fort_interval':interval,'seismic_interval':1 if pact else None,'totems':totems,'incoming_after_mitigation':incoming,'policy':policy,'echo_heal':echo_heal,
       'life':life,'regen_conservative':regen,'direct_warcry_heal':round(direct_heal,2),'totem_duration':cycle-place,'totem_cost_life':t['LifeCost'],'fort_base_life_cost':cry['LifeCost'],
       'completed_90_seconds':failure is None,'failure':failure,'minimum_life_percent':round(minimum/life*100,2),'trace':trace}
CASES=[]
for code in ['05_lv54_proxy','05_lv65_proxy','05_lv65_defence80','05_lv65_old_fort','05_lv65_mana']:
    for interval in [.5,1,2]:CASES.append(simulate(code,interval))
for code in ['05_lv65_proxy','05_lv65_defence80']:
    for dmg in [25,50,100]:CASES.append(simulate(code,1,dmg))
for code in ['06_lv65_proxy','07_lv74_source']:
    for interval in [4,8,12]:
        for policy in ['manual_only','echo_cost_stress']:
            for heal in [False,True]:CASES.append(simulate(code,interval,policy=policy,echo_heal=heal))
assert all(0<=c['minimum_life_percent']<=100 for c in CASES)
assert all(e['life']>0 for c in CASES for e in c['trace'])
for code in ['05_lv54_proxy','05_lv65_proxy','06_lv65_proxy','07_lv74_source']:
    r=DATA[code]
    # PoB reports one reserved totem, so restore its 75 before testing four.
    available=[x['SpiritUnreserved']+75 for x in r['sets'].values()]
    assert min(available)>=300,(code,available)
result={'engine':'PoB2 v0.23.1, unmodified equations','model':'90초 자원 사건 계산, 적 AI/가시 전체 DPS/한방 생존 계산 아님','echo_cost_confirmed':False,
  'echo_alternatives':'manual_only는 반복 추가 비용 없음과 직접 사용의 과거 횟수만 가정. echo_cost_stress는 현재 사용·모든 반복에 최대 생명력 비용과 반복 기본 비용까지 부과. 양쪽 모두 게임에서 확정한 규칙이 아닌 민감도 시나리오.',
  'exclusions':['토템의 지면 분쇄 매 공격 비용은 플레이어 비용으로 더하지 않음','플라스크·처치 회복·흡수·토템 피격 회생·막기 회복 제외','메아리 회복은 켬/끔 양쪽 비교','동시 다수 피격과 기절/위치/렉 재현 없음'], 'cases':CASES,'checks_passed':True}
(HERE/'v3_resource_results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
for c in CASES:
    if c['case']=='05_lv65_proxy' or c['case']=='06_lv65_proxy' and c['fort_interval']==8:print(json.dumps({k:v for k,v in c.items() if k!='trace'},ensure_ascii=True))
print('Calculated '+str(len(CASES))+' resource cases.')
