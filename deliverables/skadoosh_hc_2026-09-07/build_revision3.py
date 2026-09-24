"""Generate seven native planners, Korean guides and legal transition records."""
from revision3_data import *
from progression_core import NS, transaction_plan, dump
import hashlib, shutil

def plain(s):
    import re
    return re.sub(r'<[^>]+>\{([^{}]*)\}',r'\1',s)
def gear(index):
    late=index>=4;cry=index>=3
    defence=['최대 생명력','현재 부족한 화염·냉기·번개 저항','초당 생명력 재생','방어도']
    physical=['무기에 표시된 물리 피해와 공격 속도','모든 근접 스킬 레벨 +','명중률 / 필요한 능력치']
    rows={
      ('Weapon1',0):('세트 I · 성소 셉터' if late else '세트 I · 한손 철퇴', ['최종 정신력 수치','불의 순수함을 부여하는 성소 셉터'] if late else (['모든 근접 스킬 레벨 +','물리 피해','공격 속도'] if cry else physical)),
      ('Weapon2',0):('세트 II · 한손 철퇴',physical),
      ('Offhand1',0):('세트 I · 방어도 방패',['방패 방어도','최대 생명력','부족한 원소 저항','막기 확률']),
      ('Offhand2',0):('세트 II · 성소 셉터' if late else '세트 II · 공유 방패',['최종 정신력 수치','불의 순수함을 부여하는 성소 셉터'] if late else ['I의 방패 공유 또는 별도 방어도 방패','최대 생명력·부족한 저항']),
      ('Helm1',0):('투구',defence),('BodyArmour1',0):('갑옷',(['정신력 + (예약 부족분부터)'] if late else [])+defence+(['방어도가 원소 피해에도 적용되는 옵션'] if late else [])),
      ('Gloves1',0):('장갑',(['모든 근접 스킬 레벨 +'] if cry else [])+defence+['공격 속도']),
      ('Boots1',0):('장화',['이동 속도']+defence),
      ('Amulet1',0):('목걸이',(['정신력 + (예약 부족분부터)'] if late else [])+['최대 생명력','초당 생명력 재생','부족한 저항','모든 근접 스킬 레벨 + / 필요한 민첩·지능']),
      ('Belt1',0):('허리띠',['최대 생명력','부족한 저항','생명력 플라스크 회복 관련 옵션','호신부 관련 옵션']),
      ('Ring1',0):('반지 1',defence[:3]+['필요한 민첩·지능']),('Ring2',0):('반지 2',defence[:3]+['필요한 민첩·지능']),
      ('Flask1',0):('생명력 플라스크',['착용 가능한 높은 회복량','회복 속도 / 즉시 회복 부분','충전 유지 관련 옵션']),
      ('Charm1',0):('호신부',['현재 구간의 기절·동결 대응','효과 지속시간','충전 유지 관련 옵션'])}
    if not late:rows[('Flask1',1)]=('마나 플라스크',['현재 단계에서 충분한 회복량','회복 속도','충전 유지'])
    result=[]
    for (inv,x),(label,mods) in rows.items():
        text='<b>{'+label+'}\n추천 옵션\n'+'\n'.join(f'{i}. {v}' for i,v in enumerate(mods,1))
        if inv=='Weapon1' and cry and not late:text+='\n셉터로 전환하면 이 철퇴의 근접 젬 레벨이 사라진다. 함성의 실제 유효 레벨을 전환 전후 비교한다.'
        if inv=='Weapon2':text+='\n이번 하코 경로는 한손 철퇴를 사용한다. 양손 철퇴로 바꾸는 필수 단계는 없다.'
        if late and inv in ('Weapon1','Offhand2'):text+='\n버프를 켜고 토템 설치 전 I·II 각각 정신력 300 이상이 4기 목표다. 한쪽만 충분하면 교체 중 토템이 사라질 수 있다.'
        if inv=='Offhand1' and cry:text+='\n보강하는 함성은 방어도 방패가 필요하다. 셉터 전환 뒤에도 방패는 I에 유지한다.'
        if late and inv=='Gloves1':text+='\n양 세트에서 적용되는 근접 스킬 레벨은 함성과 토템의 젬 레벨을 보충한다.'
        if inv=='BodyArmour1' and late:text+='\n하코 전환 전 양 세트 저항·생명력·회복을 비교한다. 제작자의 54레벨 번개 저항 35%를 목표로 복사하지 않는다.'
        if inv=='Weapon2' and index==6:text+='\nSadist’s Mercy는 67레벨 이후 선택 예시. 필수 구매 목록이 아니다. 없으면 희귀 한손 철퇴를 유지한다.'
        result.append({'inventory_id':inv,'slot_x':x,'slot_y':0,'level_interval':[1,100],'additional_text':text})
    return result

ACTIONS={
 'Mace Strike':'마나가 모자랄 때 쓰는 기본 공격.', 'Rolling Slam':'기절 준비용. 목전 I를 연결하며 초반 기절 I와 혼동하지 않는다.',
 'Boneshatter':'기절 준비 표시가 뜬 적에게 사용한다.', 'Infernal Cry':'강한 적을 상대로 안전할 때 보조로 사용한다.',
 'Raise Shield':'방패 세트에서 막기. 토템 설치 후 이 세트로 복귀한다.',
 'Shockwave Totem':'적 앞에 설치한 뒤 이동한다. 지진의 요철 지대와 함께 사용한다.',
 'Earthquake':'토템을 보조할 요철 지대를 만든다. 방송에서 지대가 나타나지 않는 문제가 있었으므로 실제 바닥 표시를 확인한다.',
 'Volcanic Fissure':'보조 공격. 이 단계의 연결표를 따르고 없는 보조를 다른 스킬에서 임의로 빼지 않는다.',
 'Forge Hammer':'안전할 때 보조로 사용한다. 요철 지대 I 보조는 인내 충전을 소비하므로 충전 없이 지대가 생긴다고 가정하지 않는다.',
 'Resonating Shield':'필요할 때 쓰는 방패 보조 공격. 주력 토템/함성보다 먼저 연타할 필요는 없다.',
 'Fortifying Cry':'방어도 방패가 있는 I에서 사용한다. 토템 설치 뒤 I로 돌아오는 함성이다.',
 'Magma Barrier':'정신력 버프. 버프와 연결 보조의 예약량을 합산한다.',
 'Ancestral Spirits':'전직에서 자동 부여. 별도 젬을 만들지 않는다. 토템이 부르는 선조는 주로 보조 효과다.',
 'Purity of Fire':'성소 셉터가 부여한다. 해당 세트의 셉터 스킬에 보조를 연결한다.',
 'Harbinger of Madness':'Sadist’s Mercy가 부여한다. 희귀 철퇴에는 없는 선택 항목이다.',
 'Ancestral Warrior Totem':'지면 분쇄 액티브 젬을 반드시 이 토템의 내부 소켓에 넣는다. 아래 일반 보조도 같은 토템에 넣는다. 설치는 II만 체크하고 사용 직후 I로 복귀한다.',
 'Earthshatter':'획득한 뒤 선대의 전사 토템 안에 넣을 액티브 젬. 별도 수동 공격 버튼으로 사용하지 않는다. 공식 플래너의 메타 젬 미지원 때문에 획득 항목을 따로 표시했다.',
 'Seismic Cry':'토템이 만든 지면 분쇄 가시를 직접 터뜨리는 함성. 파콰테를 이쪽에 옮기지 않는다.'}

def render(b,index):
    b=copy.deepcopy(b);b['inventory_slots']=gear(index);sets={1:[],2:[],0:[],3:[]};purity=0
    for g in b['skills']:
        en=BASES[g['id']];w=weapon_set(en,purity)
        if en=='Purity of Fire':purity+=1
        where={1:'세트 I',2:'세트 II',0:'자동 부여',3:'전사 토템 내부'}[w]
        supports=g.get('support_skills',[])
        children=[KO[BASES[s['id']]] for s in supports]
        if en=='Ancestral Warrior Totem':children=['지면 분쇄 [내부 액티브 젬]',*children]
        line=KO[en]+' → '+(' + '.join(children) if children else '연결 보조 없음')
        sets[w].append(line)
        note='<b>{'+KO[en]+' · '+where+'}\n'+ACTIONS[en]
        if en=='Shockwave Totem' and index==1:note+='\n미가공 스킬 젬 3레벨에서 제작, 캐릭터 6레벨·힘 14부터 사용. 처음 과잉 I를 쓰다가 아래 완성 연결로 교체한다. 세 보조를 모두 모을 때까지 사용을 미루지 않는다.'
        if en=='Magma Barrier':note+=('\n후기 정신력 300 확보가 우선이다. 양 세트의 토템 예약량이 모자라면 이 버프를 먼저 끈다.' if index>=4 else '\n활력 I까지 합계 정신력 50, 명상 II까지 연결한 04는 70. 부족하면 명상 II부터 끈다.' if index>=2 else '\n정신력 30 확보 후 켠다.')
        if en=='Fortifying Cry' and index>=5:note+='\n파콰테 함성은 한 번 누른 뒤 이동. 메아리는 1.3초 간격 2회, 다음 직접 사용 전에 10미터 이동이 필요하다. 최대 생명력 추가 비용을 기본 비용과 따로 확인한다. 반복까지 회복으로 모두 상쇄된다고 가정하지 않는다.'
        if en=='Fortifying Cry' and index==4:note+='\n파콰테 전 단계. 비용이 부담되면 네 번째 효율 II를 확보하고 직접 사용 빈도를 줄인다. 효율 II가 없어도 전환을 강제하지 않는다.'
        if en=='Seismic Cry':note+='\n'+KO['Astral Projection']+'·효율 II·'+KO['Raging Cry']+'을 연결한다. 지진 함성 비용도 생명력 유지 계산에 포함한다.'
        note+='\n<b>{이 스킬 안에 넣을 젬}\n'+(' + '.join(children) if children else '현재 연결 보조 없음.')
        if w in (1,2):note+='\nG 무기 세트에서 '+('I만' if w==1 else 'II만')+' 체크한다. 파일이 체크박스를 자동 설정하지 않는다.'
        g['additional_text']=note
        for s in supports:
            title=KO[BASES[s['id']]]
            s['additional_text']='<b>{'+title+'}\n연결할 스킬: '+KO[en]+' ('+where+').\n해당 스킬의 보조 소켓에 넣는다. 무기의 룬 소켓이 아니다.'
            if index==1:s['additional_text']+='\n02의 성장 후 연결 목표. 미가공 보조 젬의 제작 목록과 소켓을 먼저 확보한다.'
            if BASES[s['id']]=="Paquate's Pact":s['additional_text']+='\n캐릭터 65레벨 필요. 타락시키는 비명 I와 같은 함성에 함께 넣지 않는다.'
            if BASES[s['id']]=='Clarity II':s['additional_text']+='\n정신력 합계 70이 부족하면 이 보조를 끈다.'
    weapons={1:'성소 셉터 + 방어도 방패' if index>=4 else '한손 철퇴 + 방어도 방패',2:'한손 철퇴 + 성소 셉터' if index>=4 else '한손 철퇴 + 공유 방패'}
    lines=['지금 할 일',GATES[index],'','무기·스킬셋']
    for w,inv in [(1,'Weapon1'),(2,'Weapon2')]:
        heading='세트 '+('I' if w==1 else 'II')+' · '+weapons[w]
        lines+=['',heading,*sets[w]]
        slot=next(x for x in b['inventory_slots'] if x['inventory_id']==inv)
        slot['additional_text']='<b>{'+heading+'}\n사용 스킬 → 연결 젬\n'+'\n'.join(sets[w])+'\n\n'+slot['additional_text']
    if sets[3]:lines+=['','토템 안에 넣을 액티브 젬',*sets[3]]
    if sets[0]:lines+=['','자동 부여',*sets[0]]
    c=costs(state(b));lines+=['','사용 순서',ROTATIONS[index],'','다음: '+NEXT[index],f"패시브 목표: 일반 {c['ordinary']}점 / 특화 I {c['sets'][0]}점·II {c['sets'][1]}점 / 전직 {c['ascendancy']}점.",'보유한 퀘스트 포인트와 전직만 사용한다. 65레벨 이상 캠페인에서도 준비가 안 됐으면 이전 단계를 유지한다.','',ORIGINS[index]]
    b['description']='\n'.join(lines)
    for n in b['passives']:
        sid=n['id'];text=''
        if NS[sid]['name']=='Attribute':text='기본은 힘. 현재 장비·젬에 부족한 민첩·지능을 양 세트에서 만족하도록 선택한다.'
        if sid=='passive_keystone_ancestral_bond':text='05 전환 때 추가. 토템당 정신력 75 예약. 4기는 버프 후 양 세트 각각 300이 필요하다. 별도의 설치 비용은 남는다.'
        if sid=='passive_keystone_blood_magic':text='05 전환의 마지막에 찍는다. 마나 비용이 생명력으로 바뀐다. 설치/함성 뒤 회복이 부족하면 이 1점을 되돌리고 전투를 멈춘다.'
        if sid=='warcries34':text='직접 함성 사용 시 최대 생명력·마나의 2% 회복. 메아리 회복의 정량 검증은 미완료이므로 추가 비용을 전부 상쇄한다고 계산하지 않는다.'
        if sid in ('reduced_attack_cost4','life_costs1','life_costs2','life_costs3','attack_speed55'):text='마나 비용 일부가 생명력으로 바뀐다. 혈마법 전에도 생명력과 마나가 함께 줄어들 수 있다. 두 자원의 회복을 확인한다.'
        if sid=='AscendancyWarrior2Notable7':text='세 번째 전직 후 나무 벽. 일반 97점 목표와 별개로 전직을 완료한 때에 찍는다.'
        if text:n['additional_text']=text
    return b

def plan(a,b):
    ops=transaction_plan(a,b)
    bm='passive_keystone_blood_magic'
    if bm not in state(a) and bm in state(b):
        last=[o for o in ops if o['id']==bm]
        ops=[o for o in ops if o['id']!=bm]+last
        current=state(a)
        for o in ops:
            if o['action']=='환불':del current[o['id']]
            else:current[o['id']]=o['to']
            assert legal(current)
            o['cost']=costs(current)
    cs=[costs(state(a)),costs(state(b))]+[o['cost'] for o in ops]
    return {'from':a['name'],'to':b['name'],'from_passives':a['passives'],'to_passives':b['passives'],
      'required_pool':{'ordinary':max(c['ordinary'] for c in cs),'sets':[max(c['sets'][i] for c in cs) for i in (0,1)]},
      'refunds':sum(o['action']=='환불' for o in ops),'operations':ops}

def main():
    (OUT/'BuildPlanner').mkdir(parents=True,exist_ok=True);(OUT/'Filters').mkdir(exist_ok=True)
    builds=[render(b,i) for i,b in enumerate(BUILDS)]
    for b in builds:dump(OUT/'BuildPlanner'/build_filename(b),b)
    intermediate=copy.deepcopy(OLD['06']);intermediate['name']='04 내부 경유 - 46레벨 실측'
    route=[BUILDS[0],BUILDS[1],BUILDS[2],intermediate,*BUILDS[3:]]
    plans=[plan(a,b) for a,b in zip(route,route[1:])]
    dump(HERE/'transition_operations_v3.json',plans)
    dump(HERE/'progression_v3.json',[{'file':build_filename(b),'origin':ORIGINS[i],**costs(state(b))} for i,b in enumerate(builds)])
    # Filters are generated independently by filters_revision3.py from its spec.
    gems=['# 무기 세트와 젬 연결','','7개 파일은 레벨 구간이 아닌 운영 변화 기준이다. G의 무기 세트 체크는 수동이다. 보조는 같은 스킬의 작은 소켓에 넣는다. 토템 내부의 지면 분쇄만 액티브 젬이다.','']
    equipment=['# 장비 추천 옵션','','각 장비 칸의 게임 내 설명에도 같은 우선순위를 넣었다. 모든 옵션을 동시에 갖추라는 뜻이 아니다. 부족한 저항·젬 요구치·정신력을 먼저 채운다.','']
    for b in builds:
        gems+=['## '+b['name'],'',b['description'],'']
        for g in b['skills']:gems+=['### '+KO[BASES[g['id']]],'',plain(g['additional_text']),'']
        equipment+=['## '+b['name'],'','| 장비 | 추천 옵션 |','|---|---|']
        for s in b['inventory_slots']:
            txt=plain(s['additional_text']);equipment+=['| '+s['inventory_id']+(' 마나' if s.get('slot_x') else '')+' | '+txt.replace('\n','<br>')+' |']
        equipment+=['']
    (OUT/'무기세트와젬연결.md').write_text('\n'.join(gems),encoding='utf-8')
    (OUT/'장비추천옵션.md').write_text('\n'.join(equipment),encoding='utf-8')
    txt=['# 패시브 전환','','점수는 이미 사용한 점수를 포함하는 총 보유 한도다. 무기 특화 포인트는 레벨업이 아니라 해당 퀘스트 보상으로 확보한다. 환불 개수는 노드 수이며 골드 비용은 자신의 레벨로 NPC에서 확인한다.','',
      '03→04는 46레벨 실측을 내부 경유한 뒤 52레벨 목표로 확장한다. 별도 플래너 파일을 늘리지 않았다. 05는 54레벨 전체 실측 트리가 아닌 69점 전환안이다. 05→06은 패시브 변경이 없다. 06→07은 기존 배정을 유지하며 확장한다.','',
      '장비와 젬을 모두 준비한 뒤 마을에서 아래 순서대로 한다. 05에서는 혈마법을 마지막에 추가하고, 그 전 상태로 무리하게 사냥하지 않는다.','']
    txt+=['## 65레벨 이상, 05에서 남는 포인트부터 쓰기','','05의 69점 이후에는 아래 11점을 07의 같은 위치에서 확장한다. 총 80점·특화 각 14점이며 파콰테 도입과 독립적이다. 일반 포인트가 생기는 대로 이어서 찍는다. 07의 나머지 딜 노드는 그 뒤에 확장한다.','']
    current=state(BUILDS[4]);pending=list(DEFENCE_FIRST);order=[]
    while pending:
        for sid in pending:
            test={**current,sid:state(BUILDS[6])[sid]}
            if legal(test):
                order.append(sid);current=test;pending.remove(sid);break
        else:raise AssertionError('disconnected defence extension')
    for i,sid in enumerate(order,1):txt+=[f'{i}. {NS[sid]["name"]} · `{sid}`']
    dump(HERE/'defence_extension_v3.json',{'order':order,'passives':entries(current),'cost':costs(current)})
    txt+=['']
    bind={None:'미할당',0:'공통',1:'I',2:'II'}
    for p in plans:
        txt+=['## '+p['from']+' → '+p['to'],'',f"전환 중 총 일반 {p['required_pool']['ordinary']}점 / 특화 I {p['required_pool']['sets'][0]}점·II {p['required_pool']['sets'][1]}점. 환불 {p['refunds']}개.",'']
        for j,o in enumerate(p['operations'],1):txt+=[f"{j}. {o['action']} {o['name']} · `{o['id']}` ({bind[o['from']]} → {bind[o['to']]})"]
        if not p['operations']:txt+=['패시브 변경 없음. 연결 젬과 운영만 바꾼다.']
        txt+=['']
    (OUT/'패시브전환.md').write_text('\n'.join(txt),encoding='utf-8')
    print('Generated 7 planners and '+str(len(plans))+' checked transition routes; not installed yet.')
if __name__=='__main__':main()
