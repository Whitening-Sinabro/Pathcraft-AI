"""Event-based resource/Corrupted Blood sensitivity study, not a combat engine.

Inputs are preserved upstream PoB outputs. Costs absent from PoB are explicit
scenario assumptions, never silent patches to the upstream calculation engine.
"""
from pathlib import Path
import heapq, json, math

HERE=Path(__file__).resolve().parent
RESULTS={x['case']:x for x in json.loads((HERE/'pob_results.json').read_text(encoding='utf-8'))}

def skill(case,active):
    return next(s['output'] for s in RESULTS[case]['skills'] if s['active']==active)

def simulate(case, interval, totems=4, incoming=0, policy='normal', horizon=90):
    r=RESULTS[case]; sets=list(r['sets'].values())
    # Use the lower value of either weapon set throughout. This deliberately
    # excludes the better shield-set regeneration during most of the rotation.
    life=min(s['Life'] for s in sets); mana=min(s['Mana'] for s in sets)
    lr=min(s['LifeRegen'] for s in sets); mr=min(s['ManaRegen'] for s in sets)
    cry=skill(case,'Fortifying Cry')
    pact=policy!='normal'; echo=pact and case!='09_no_echo'
    dot=skill(case,'Twisted Pact' if pact else 'Corrupted Cry')
    host='Ancestral Warrior Totem' if r['stage'] in ('08B','08C','09') else 'Shockwave Totem'
    totem=skill(case,host); duration=totem['TotemDuration']; place=totem['TotemPlacementTime']
    assert interval>=1/cry['Speed']
    # Only a direct warcry receives the observed Urgent Call recovery. Echo
    # recovery and life/mana on kill, flask, leech, guard and hit avoidance = 0.
    native=json.loads(next((HERE.parent/'revision2/BuildPlanner').glob(r['stage']+' *.build')).read_text(encoding='utf-8'))
    urgent=any(p['id']=='warcries34' and p.get('weapon_set',0) in (0,1) for p in native['passives'])
    heal_l=life*.02 if urgent else 0; heal_m=mana*.02 if urgent else 0
    hp=life; mp=mana; last=0.; minlife=life; recent=[]; stacks=[]; events=[]; trace=[]
    cost_l=cost_m=regenerated_l=manual_recovery_l=dot_integral=0.
    first_failure=None; total_manual=0; max_stacks=0; busy_until=0.
    count=0
    def add(t,kind):
        nonlocal count
        heapq.heappush(events,(round(t,8),count,kind));count+=1
    # Initial installation precedes warcries. Subsequent installations are
    # scheduled after the previous totem expires, to avoid double reserving.
    cycle=duration+place
    for n in range(totems):
        t=n*place
        while t<horizon:add(t,'totem');t+=cycle
    t=totems*place+.1
    while t<horizon:
        add(t,'manual')
        t+=interval
    add(horizon,'end')
    while events:
        t,_,kind=heapq.heappop(events)
        if t>horizon:break
        if kind in ('manual','totem') and t<busy_until-1e-7:
            add(busy_until,kind);continue
        dt=t-last
        # Integrate each individual stack until its own expiry. The oldest
        # stacks are replaced at cap 10. A shared-duration refresh would differ.
        dot_integral+=sum(max(0,min(t,end)-last) for end in stacks)*dot['CorruptingBloodDPS']*(.6 if echo else 1)
        hp=min(life,hp+(lr-incoming)*dt);mp=min(mana,mp+mr*dt)
        regenerated_l+=lr*dt
        if hp<=0:
            first_failure={'time':last+max(0,(hp-(lr-incoming)*dt)/max(incoming-lr,1e-9)),'reason':'incoming_damage'};minlife=0;break
        stacks=[x for x in stacks if x>t]
        recent=[x for x in recent if x>t-4]
        if kind=='end':last=t;break
        lc=mc=0.
        if kind=='totem':lc=totem['LifeCost'];mc=totem['ManaCost']
        elif kind in ('manual','echo'):
            if kind=='manual' or policy in ('pact_repeated_base','pact_stress'):
                lc=cry['LifeCost'];mc=cry['ManaCost']
            if pact:
                # Lower/upper interpretations: prior uses only versus including
                # the current use; charging base again on echoes; an additional
                # x1.5 stress multiplier. These are scenario assumptions, NOT
                # asserted game rules or rigorous universal lower/upper bounds.
                current=0 if policy=='pact_prior_only' else 1
                percent=.1*min(3,len(recent)+current)
                if policy=='pact_stress':percent*=1.5
                lc+=life*percent
        if lc>=hp and lc>0 or mc>mp:
            first_failure={'time':round(t,3),'reason':'life_cost' if lc>=hp and lc>0 else 'mana_cost','life':round(hp,2),'mana':round(mp,2),'next_life_cost':round(lc,2),'next_mana_cost':round(mc,2)}
            break
        hp-=lc;mp-=mc;cost_l+=lc;cost_m+=mc;minlife=min(minlife,hp)
        if kind in ('manual','echo'):
            recent.append(t)
            stacks.extend([t+dot['Duration']]*(5 if pact else 1));stacks=sorted(stacks)[-10:]
            max_stacks=max(max_stacks,len(stacks))
        if kind=='manual':
            total_manual+=1;hp=min(life,hp+heal_l);mp=min(mana,mp+heal_m);manual_recovery_l+=heal_l
            busy_until=t+1/cry['Speed']
            if echo:add(t+1.3,'echo');add(t+2.6,'echo')
        if kind=='totem':busy_until=t+place
        trace.append({'t':round(t,3),'event':kind,'life':round(hp,2),'mana':round(mp,2),'stacks':len(stacks),'life_cost':round(lc,2)})
        last=t
    elapsed=first_failure['time'] if first_failure else horizon
    return {'case':case,'interval':interval,'totems':totems,'incoming_post_mitigation_dps':incoming,'policy':policy,
            'duration_seconds':horizon,'completed':first_failure is None,'first_failure':first_failure,
            'life':life,'mana':mana,'life_regen_conservative':lr,'mana_regen_conservative':mr,'manual_warcry_life_recovery':round(heal_l,3),
            'min_life_percent':round(minlife/life*100,2),'end_life_percent':round(hp/life*100,2),
            'max_stacks':max_stacks,'average_corrupted_blood_dps_until_stop':round(dot_integral/max(elapsed,1e-9),1),
            'base_life_cost_per_cry':cry['LifeCost'],'base_mana_cost_per_cry':cry['ManaCost'],
            'totem_life_cost':totem['LifeCost'],'totem_mana_cost':totem['ManaCost'],
            'movement_prerequisite': '10 metres before every direct use; echoes assumed to reach target' if echo else None,
            'trace':trace}

cases=[]
for code in ('05A','06','07','08','08A'):
    for interval in (1.,2.,4.):cases.append(simulate(code,interval,totems=2))
for code in ('08B_gem15','08C_gem15'):
    for interval in (.5,1.,2.):
        for totems in (2,4):cases.append(simulate(code,interval,totems=totems))
for incoming in (50,100,150):cases.append(simulate('08C_gem15',1,totems=4,incoming=incoming))
for code in ('09_no_echo','09'):
    for interval in (4.,6.,8.,10.):
        for policy in ('pact_prior_only','pact_current','pact_repeated_base','pact_stress'):
            cases.append(simulate(code,interval,policy=policy))

# Focused checks: reservation cap, stack cap, resource accounting, and expected
# ordering of the explicitly stronger cost scenarios.
assert all(x['max_stacks']<=10 for x in cases)
for x in cases:
    assert all(e['life']>0 and e['life']<=x['life']+.001 for e in x['trace'])
for code in ('09','09_no_echo'):
    for interval in (4.,6.,8.,10.):
        pair=[next(x for x in cases if x['case']==code and x['interval']==interval and x['policy']==p) for p in ('pact_prior_only','pact_stress')]
        assert pair[1]['min_life_percent']<=pair[0]['min_life_percent'] or pair[1]['first_failure'] is not None
late=RESULTS['09']['sets'];free_before=[v['SpiritUnreserved']+75 for v in late.values()]
assert min(math.floor(x/75) for x in free_before)==4
summary={'model':'explicit resource and independent-stack sensitivity, no monster AI',
         'pob_version':'v0.23.1','pob_commit':'7d6f530cbdab20389ff8bc6ba97a37ac27f74e41',
         'awt_spirit_before_placement':free_before,'awt_four_left':[x-300 for x in free_before],
         'pact_cost_semantics_confirmed':False,'echo_damage_multiplier_manual_assumption':.6,
         'tests_passed':True,'cases':cases}
(HERE/'resource_results.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for c in cases:
    if c['case'] in ('08C_gem15','09') and c['totems']==4 and (c['policy'] in ('normal','pact_prior_only','pact_repeated_base') and c['interval'] in (1,4,8)):
        print(json.dumps({k:v for k,v in c.items() if k!='trace'},ensure_ascii=True))
print(f'Calculated {len(cases)} resource cases; focused checks passed.')
