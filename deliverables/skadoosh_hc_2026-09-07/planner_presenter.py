"""Player-facing hints using GGG's documented description/additional_text fields.

Equipment slots contain ranked equipment targets; skills contain their own
socket instructions. Allocation and gem links remain unchanged.
"""
from pathlib import Path
import copy,json,re

SCHEMA_URL='https://www.pathofexile.com/developer/docs/game#buildplanner'
LATE={'08B','08C','09'}
CRY={'05A','06','07','08','08A'}

STEPS={
'01':('몰려오는 강타로 기절을 준비하고 뼈 박살로 마무리한다.', '미가공 스킬 젬 3레벨을 얻으면 충격파 토템을 제작하고 02를 선택한다.', '3레벨 충격파 토템은 캐릭터 6레벨·힘 14부터 사용한다. 패시브 10점 완성이나 액트 1 완료를 기다리지 않는다.'),
'02':('충격파 토템을 세트 II에 지정하고 적 앞에 설치한다.', '과잉 I → 포악함 I 순서로 확보해 토템에 넣는다. 보조가 없어도 토템부터 쓸 수 있다.', '기존 근접 스킬을 함께 쓴다. 일반 25점은 앞으로 찍을 트리 목표이며 진입 조건이 아니다.'),
'03':('1차 전직 응답받은 부름을 얻은 뒤 토템 연결을 바꾼다.', '충격파 토템에 빠른 공격 I·긴급한 토템 I·포악함 II를 연결한다.', '과잉 제거로 줄어드는 토템 1기는 전직에서 얻는 1기로 상쇄된다. 전직 전에 보조만 먼저 바꾸지 않는다.'),
'04':('대장간 망치를 배우고 요철 지대 I·유지되는 대지 I를 연결한다.', '충격파 토템을 설치하고, 안전할 때 망치와 함성을 보조로 쓴다.', '인내 충전이 없으면 망치의 요철 지대 보조가 작동하지 않는다. 이때는 지진으로 지대를 만든다.'),
'05':('2차 전직 전쟁 소집자의 고함을 얻고 충격파 토템으로 진행한다.', '망치에 전쟁의 주먹 II, 마그마 장벽에 활력 I를 추가한다.', '함성 전환 젬이 준비되면 05A에서 먼저 시험한다. 젬이 없으면 이 단계로 계속 진행한다.'),
'05A':('패시브는 05 그대로 둔다. 지옥불 함성을 보강하는 함성으로 교체한다.', '보강하는 함성에 타락시키는 비명 I·포악함 II·재빠른 고통 II를 넣고 토템과 함께 시험한다.', '마그마 장벽+활력 I에 정신력 50이 필요하다. 명상 II는 기본 연결에서 제외했다. 마나 플라스크를 유지한다.'),
'06':('무기·장갑의 모든 근접 스킬 레벨 옵션과 함성 젬을 먼저 준비한다.', '일반 총 60점, 세트 I 12점/II 14점과 환불 16개 비용을 확보한 뒤 전환한다.', '트리만 바꾸면 딜이 늘지 않을 수 있다. 마나 플라스크를 유지하고, 명상 II는 정신력 합계 70 이상일 때 켠다.'),
'07':('기존 함성과 충격파 토템을 유지하며 트리를 확장한다.', '보강하는 함성의 네 번째 보조 소켓에 효율 II를 넣는다.', '캐릭터 65레벨을 넘겨도 캠페인 중이면 이 구성과 캠페인 필터를 계속 써도 된다.'),
'08':('후기 장비가 아직 없으면 07의 공격 구성을 유지한다.', '여유 패시브만 방어·재생 경로에 순서대로 투자한다. 최대 14점이며 전부 찍을 의무는 없다.', '후기 전환 준비물과 일반 총 97점·양 세트 각 22점이 준비되면 08A로 간다.'),
'08A':('성소 셉터 2개·한손 철퇴·방어도 방패와 선대의 전사 토템 젬을 먼저 모은다.', '일반 총 97점·양 세트 각 22점을 확보하고 마을에서 후기 트리로 바꾼다.', '회복이 줄어드는 준비 단계다. 여기서 사냥하지 말고 08B까지 이어간다. 08 방어 14점 완성 상태는 환불 38개, 일부 투자 상태는 전용 순서를 쓴다.'),
'08B':('선대의 유대 1점만 추가하고 무기를 후기 구성으로 교체한다.', '선대의 전사 토템 안에 지면 분쇄·긴급한 토템 I·포악함 II를 넣는다.', '모든 버프 후 양 세트에 토템당 정신력 75가 남아야 한다. 함성 젬 레벨을 유지하고 마나 플라스크로 짧게 시험한다.'),
'08C':('08B가 작동하면 혈마법 1점만 추가한다. 파콰테는 아직 넣지 않는다.', '토템과 함성의 비용이 생명력으로 바뀐다. 설치·함성 뒤 회복이 따라오는지 확인한다.', '회복이 부족하면 혈마법 1점을 되돌리고 08B로 돌아간다. 제작자 장비로 한 계산이 자기 장비에도 그대로 적용되지는 않는다.'),
'09':('참고 단계다. 추가 생명력 비용을 직접 확인하기 전에는 08C를 유지한다.', '전환할 때만 타락시키는 비명 I를 파콰테로, 효율 II를 메아리치는 함성으로 교체한다.', '메아리는 1.3초 간격으로 2회 반복한다. 다음 직접 사용 전 10미터 이동이 필요하다. 반복 비용이 감당되는지 먼저 확인한다.'),
}

NEXT={
'01':'충격파 토템 확보 → 02', '02':'1차 전직과 토템 보조 3칸 → 03',
'03':'대장간 망치와 요구 능력치 확보 → 04','04':'2차 전직 → 05',
'05':'방어도 방패·함성 전환 젬·보조 3칸 → 05A','05A':'장비·젬·포인트·환불 비용 준비 → 06',
'06':'함성 보조 네 번째 소켓·효율 II → 07','07':'후기 준비가 늦으면 선택 방어 08',
'08':'후기 장비·젬·일반 총 97점 확보 → 08A','08A':'마을에서 곧바로 08B',
'08B':'설치·정신력·회복 확인 → 혈마법 시험 08C','08C':'파콰테 실제 비용 확인 전까지 유지',
'09':'추가 비용을 감당하지 못하면 08C 복귀',
}

def plain(s):return re.sub(r'<[^>]+>\{([^{}]*)\}',r'\1',s)

def skill_sets(build,ko,bases):
    """One source for the overview, weapon popups and each gem's own hint."""
    grouped={'세트 I':[],'세트 II':[],'자동 부여':[]};purity=0
    for g in build['skills']:
        en=bases[g['id']]
        if en=='Purity of Fire':purity+=1;where='세트 I' if purity==1 else '세트 II'
        elif en in ('Mace Strike','Boneshatter','Shockwave Totem','Ancestral Warrior Totem'):where='세트 II'
        elif en in ('Ancestral Spirits','Harbinger of Madness'):where='자동 부여'
        else:where='세트 I'
        name=ko[en]
        if en=='Magma Barrier':name+=' [버프]'
        if en=='Purity of Fire':name+=' [셉터 부여]'
        if en=='Mace Strike':name+=' [기본 공격]'
        children=[]
        for child in g.get('support_skills',[]):
            title=ko[bases[child['id']]]
            if bases[child['id']]=='Earthshatter':title+=' [토템 내부 공격]'
            children.append(title)
        line=name+' → '+(' + '.join(children) if children else '연결 보조 없음')
        grouped[where].append((g,where,line))
    return grouped

def weapon_loadout(code):
    if code in LATE:return {'세트 I':'성소 셉터 + 방어도 방패','세트 II':'한손 철퇴 + 성소 셉터'}
    return {'세트 I':'한손 철퇴 + 방어도 방패','세트 II':'양손 철퇴'}

def rotation(code):
    if code=='01':return '몰려오는 강타(I) → 기절 준비된 적에게 뼈 박살(II) → 방패 I 복귀.'
    if code=='02':return '충격파 토템(II) 설치 → 지진(I)으로 지대 생성 → 이동. 기절 준비된 적은 뼈 박살(II)로 마무리하고 I로 복귀.'
    if code in ('03','04','05'):return '충격파 토템(II) 설치 → 방패 I 복귀 → 여유가 있을 때 지진·함성(I) 보조. 망치가 있는 단계는 망치(I)도 보조로 사용.'
    if code in CRY:return '충격파 토템(II) 설치 → 보강하는 함성(I)으로 방패 복귀 → 이동 → 남은 적 확인.'
    return '선대의 전사 토템(II) 설치 → 보강하는 함성(I)으로 방패 복귀·가시 폭발 → 이동. 지진 함성(I)은 보조.'
def priority(title,options,extra=''):
    return '<b>{추천 옵션 · '+title+'}\n'+'\n'.join(f'{i}. {s}' for i,s in enumerate(options,1))+ ('\n\n'+extra if extra else '')

def equipment(code,existing):
    late=code in LATE;cry=code in CRY or late;bm=code in ('08C','09')
    phys=['물리 피해 추가','물리 피해 % 증가','공격 속도 증가','명중률 / 모든 근접 스킬 레벨']
    defence=['최대 생명력','부족한 화염·냉기·번개 저항','방어도','초당 생명력 재생']
    shield=['최대 생명력','부족한 원소 저항','방어도 / 막기 확률','초당 생명력 재생']
    items={
      ('Weapon1',0):priority('세트 I · 한손 철퇴',(['모든 근접 스킬 레벨 +','물리 피해 추가·물리 피해 % 증가','공격 속도 / 명중률'] if cry else phys),
          '함성은 유효 젬 레벨, 함께 쓰는 공격은 물리 피해를 비교한다.' if cry else '한손 철퇴+방패. 물리 피해 범위와 공격 속도를 함께 비교한다.'),
      ('Weapon2',0):priority('세트 II · 양손 철퇴',phys,'물리 피해가 좋은 무기로 뼈 박살·충격파 토템을 사용한다. 한손 철퇴+공유 방패로 바꾸려면 먼저 토템 피해를 비교한다.' if code!='01' else '뼈 박살용. 아직 양손 철퇴가 없으면 한손 철퇴로 진행한다.'),
      ('Offhand1',0):priority('세트 I · 방어도 방패',shield,'보강하는 함성에는 방어도 방패가 필요하다.' if cry else '한손 철퇴와 함께 사용한다. 새 방패로 바꿀 때 생명력·저항 손실도 비교한다.'),
      ('Offhand2',0):priority('세트 II · 보조 무기', ['양손 철퇴 사용 중에는 비워 둔다','한손 철퇴로 바꿀 때만 방패 공유를 검토한다'], '한손 철퇴 전환 시 방패 옵션: 최대 생명력 → 부족한 원소 저항 → 방어도 / 막기.'),
      ('Helm1',0):priority('투구 · 방어도 장비',defence),
      ('BodyArmour1',0):priority('갑옷 · 방어도 장비',(['정신력 + (토템 예약량이 부족할 때)','최대 생명력','부족한 원소 저항','초당 생명력 재생 / 방어도','방어도의 일부를 원소 피해에도 적용'] if late else defence)),
      ('Gloves1',0):priority('장갑',(['모든 근접 스킬 레벨 +','최대 생명력','부족한 원소 저항','공격 속도 / 방어도'] if cry else ['최대 생명력','부족한 원소 저항','공격 속도 / 공격 시 물리 피해 추가','모든 근접 스킬 레벨 +']),
          '함성 단계의 핵심 딜 옵션이다. 원본 장갑은 모든 근접 스킬 레벨 +2를 사용했다.' if cry else '생명력·저항이 크게 떨어지는 공격 옵션만 있는 장갑은 신중하게 비교한다.'),
      ('Boots1',0):priority('장화',['이동 속도 증가','최대 생명력','부족한 원소 저항','초당 생명력 재생 / 방어도']),
      ('Amulet1',0):priority('목걸이',(['정신력 + (예약량이 부족할 때)','최대 생명력 / 초당 생명력 재생','부족한 원소 저항','모든 근접 스킬 레벨 + / 필요한 민첩·지능'] if cry else ['최대 생명력','부족한 원소 저항','젬에 부족한 민첩·지능','모든 근접 스킬 레벨 +']),
          '후기 토템 4기라면 모든 버프 후 I와 II 각각 정신력 300 이상이 필요하다.' if late else ''),
      ('Belt1',0):priority('허리띠',['최대 생명력','부족한 원소 저항','플라스크 생명력 회복량 / 회복 속도','호신부 효과 지속시간'], '사용할 수 있는 호신부 칸 수를 확인한다.'),
      ('Flask1',0):priority('생명력 플라스크',['현재 착용 가능한 높은 회복량','회복 속도 / 즉시 회복 부분','충전 유지에 도움이 되는 옵션'], '플라스크를 사용한 회복은 장비의 초당 생명력 재생과 별개다.'),
      ('Charm1',0):priority('호신부',['기절 대응용 호신부 우선 검토','동결이 문제인 구간에는 동결 대응용','효과 지속시간 / 충전 유지'], '열린 호신부 칸 수와 지금 마주치는 위험에 맞춰 고른다.'),
    }
    for ring in ('Ring1','Ring2'):
        items[(ring,0)]=priority('반지',['최대 생명력','부족한 화염·냉기·번개 저항','초당 생명력 재생',
                   '필요한 민첩·지능' if bm else '마나 재생 / 필요한 민첩·지능'],
                   '근접·토템 초반에는 공격 시 물리 피해 추가도 딜 옵션이다.' if not cry else '공격 시 원소 피해 추가는 타락한 피의 우선 딜 옵션이 아니다.')
    if not bm:
        items[('Flask1',1)]=priority('마나 플라스크',['현재 착용 가능한 높은 마나 회복량','회복 속도','충전 유지에 도움이 되는 옵션'],
                         '05A·06·08B는 자연 재생만으로 함성을 계속 쓰기 어렵다. 혈마법 전까지 유지한다.' if cry else '연속 공격·토템 설치에 쓴 마나를 보충한다.')
    if late:
        for key,label in [(('Weapon1',0),'세트 I · 성소 셉터'),(('Offhand2',0),'세트 II · 성소 셉터')]:
            items[key]=priority(label,['정신력 % 증가 → 무기에 표시된 최종 정신력 비교','불의 순수함을 부여하는 성소 셉터 베이스'],
                '핵심은 양 세트의 예약량 확보다. 다른 셉터는 이 파일의 불의 순수함 연결을 그대로 쓰지 못한다.')
        items[('Weapon2',0)]=priority('세트 II · 한손 철퇴',phys,
            '선대의 전사 토템용. 반대 손에 성소 셉터를 들어야 하므로 양손 철퇴는 사용하지 않는다. 원본 고유는 선택 예시이며 대체 무기는 토템 피해를 다시 비교한다.')
    # Retain original optional unique metadata; never turn its specific rolled
    # affixes into a mandatory shopping list. All generic hints are visible at
    # the current stage, regardless of snapshot item requirement levels.
    old={(s['inventory_id'],s.get('slot_x',0)):s for s in existing}
    result=[]
    for (inv,x),note in items.items():
        s={'inventory_id':inv,'slot_x':x,'slot_y':0,'level_interval':[1,100],'additional_text':note}
        if old.get((inv,x),{}).get('unique_name'):
            s['unique_name']=old[(inv,x)]['unique_name']
            s['additional_text']+='\n표시된 고유는 원본 예시다. 희귀 장비로 대체할 때는 위 옵션을 비교한다.'
        result.append(s)
    return result

def render_planner(build,counts,plan,ko,bases,nodes):
    b=copy.deepcopy(build);code=b['name'].split()[0]
    words=list(STEPS[code])
    for i,s in enumerate(words):
        words[i]=s.replace('재빠른 고통 II',ko['Swift Affliction II'])
    weapons=('I: 성소 셉터+방어도 방패 / II: 한손 철퇴+성소 셉터' if code in LATE else 'I: 한손 철퇴+방어도 방패 / II: 양손 철퇴 또는 피해를 확인한 한손 철퇴')
    b['description']='지금 할 일\n'+'\n'.join(f'{i}. {s}' for i,s in enumerate(words,1))+'\n\n'+weapons+'\n다음: '+NEXT[code]
    b['description']+=f"\n패시브 목표: 일반 {counts['ordinary']}점 / 무기 특화 I {counts['sets'][0]}점·II {counts['sets'][1]}점."
    if plan and plan['refunded_entries']:
        b['description']+='\n환불은 마을에서 동봉 패시브전환.md의 해당 순서대로 한다.'
    b['inventory_slots']=equipment(code,b['inventory_slots'])
    actions={
      'Mace Strike':'마나가 부족할 때 쓰는 기본 공격이다.',
      'Boneshatter':'기절 준비 표시가 뜬 적에게 사용한 뒤 방패 세트 I로 복귀한다.',
      'Rolling Slam':'첫 타격으로 기절을 준비한다. 뼈 박살과 함께 쓴다.',
      'Infernal Cry':'안전할 때 강한 적에게 보조로 사용한다. 충격파 토템을 먼저 확보한다.',
      'Raise Shield':'방패 세트 I에서 사용한다.',
      'Shockwave Totem':'적 앞에 설치하고 방패 I로 돌아온다. 지진의 요철 지대를 함께 이용한다.',
      'Earthquake':'요철 지대를 만드는 보조 스킬이다. 충격파 토템을 먼저 놓는다.',
      'Magma Barrier':'정신력이 허용될 때 켠다. 연결한 활력·명상도 정신력을 예약한다.',
      'Ancestral Spirits':'전직에서 자동으로 부여한다. 별도 젬을 제작하지 않는다.',
      'Resonating Shield':'안전할 때 쓰는 방패 보조 공격이다. 주력 함성·토템보다 우선하지 않는다.',
      'Volcanic Fissure':'기존 토템을 보조하는 공격이다. 현재 단계의 연결만 유지한다.',
      'Forge Hammer':'안전할 때 내려찍고 함성으로 보조한다. 요철 지대 I는 인내 충전이 있어야 작동한다.',
      'Fortifying Cry':'방어도 방패를 들고 쓴다. 토템을 놓은 뒤 I로 복귀하는 주력 함성이다.',
      'Purity of Fire':'성소 셉터가 부여하는 스킬이다. 해당 무기 세트에서 연결한 버프를 유지한다.',
      'Harbinger of Madness':'원본 고유 철퇴가 부여한다. 대체 무기에 없으면 별도 젬으로 제작하지 않는다.',
      'Ancestral Warrior Totem':'선대의 전사 토템 안에 지면 분쇄를 넣는다. 토템이 대신 공격한다. 설치 뒤 방패 I로 복귀한다.',
      'Seismic Cry':'지면 분쇄 가시를 터뜨리는 보조 함성이다. 추가 비용까지 확인하며 사용한다.',
    }
    groups=skill_sets(b,ko,bases)
    assignment={id(g):where for members in groups.values() for g,where,line in members}
    for g in b['skills']:
        en=bases[g['id']]
        where=assignment[id(g)]
        note='<b>{'+ko[en]+' · '+where+'}\n'+actions[en]
        if en=='Shockwave Totem' and code=='02':note+='\n미가공 스킬 젬 3레벨부터 제작. 캐릭터 6레벨·힘 14면 사용한다. 보조를 다 모으기 전에도 추가한다.'
        if en=='Fortifying Cry' and code=='09':note+='\n메아리: 1.3초 간격 2회 반복. 다음 직접 사용 전 10미터 이동. 비용 확인 전 08C 유지.'
        if en=='Magma Barrier' and code in ('05','05A'):note+='\n마그마 장벽+활력 I = 정신력 50. 명상 II는 이 파일에서 추가하지 않는다.'
        if en=='Magma Barrier' and code in ('02','03','04'):
            note='<b>{'+ko[en]+' · '+where+'}\n정신력 30을 확보한 뒤 켠다. 아직 없으면 공격·토템만 사용한다.'
        if en=='Magma Barrier' and code in ('06','07','08','08A'):note+='\n마그마 장벽+활력 I+명상 II = 정신력 70. 부족하면 명상 II를 끈다.'
        supports=g.get('support_skills',[])
        note+='\n<b>{이 스킬 안에 넣을 젬}'
        if not supports:note+='\n현재 단계 연결 보조 없음.'
        for i,s in enumerate(supports,1):
            sn=bases[s['id']];note+=f'\n{i}. {ko[sn]}'
            s['additional_text']=f'<b>{{{ko[sn]}}}\n연결할 스킬: {ko[en]} ({where})\n이 스킬의 {i}번째 보조 위치에 넣는다.'
            if sn=='Earthshatter':s['additional_text']+='\n선대의 전사 토템 내부에 넣는 공격 젬이다. 별도 수동 공격 버튼으로 쓰지 않는다.'
            if sn=='Clarity II':s['additional_text']+='\n정신력이 부족하면 이 보조부터 비활성화한다.'
        note+='\nG의 무기 세트 체크는 직접 지정한다.' if where!='자동 부여' else ''
        g['additional_text']=note
    for n in b['passives']:
        n.pop('additional_text',None)
        node=nodes[n['id']]
        if n['id'].startswith(('attributes','strength')):
            n['additional_text']='기본은 힘을 선택한다. 장비·젬에 민첩이나 지능이 부족하면 필요한 만큼 해당 능력치를 선택한다.'
        if n['id']=='passive_keystone_ancestral_bond':n['additional_text']='08B에서 추가. 토템당 정신력 75 예약. 모든 버프 후 I·II 각각 예약량을 확인한다. 설치 마나/생명력 비용은 남는다.'
        if n['id']=='passive_keystone_blood_magic':n['additional_text']='08C에서 회복 확인 후 추가. 스킬 마나 비용이 생명력으로 바뀐다. 유지가 안 되면 이 1점을 되돌린다.'
        if n['id']=='warcries34':n['additional_text']='직접 함성 사용 시 최대 생명력·마나의 2% 회복. 반복 사용의 비용까지 전부 해결한다고 가정하지 않는다.'
        if n['id']=='totems14':n['additional_text']='토템 한도에 관여하는 노드다. 세트 II의 배정을 유지한다.'
    loadout=weapon_loadout(code)
    overview=['무기·스킬셋','G에서 세트 I 목록은 I만, 세트 II 목록은 II만 체크한다. 아래는 권장 배정이며 자동 설정되지 않는다.']
    for where,inv in [('세트 I','Weapon1'),('세트 II','Weapon2')]:
        lines=[line for g,w,line in groups[where]]
        overview+=['',where+' · '+loadout[where],*lines]
        slot=next(s for s in b['inventory_slots'] if s['inventory_id']==inv)
        slot['additional_text']='<b>{'+where+' · '+loadout[where]+'}\nG에서 '+('I' if where=='세트 I' else 'II')+'만 체크.\n<b>{사용 스킬 → 연결 젬}\n'+'\n'.join(lines)+'\n\n'+slot['additional_text']
    if code not in LATE:
        overview+=['','세트 II를 한손 철퇴+공유 방패로 바꾸려면 토템 피해를 비교한 뒤 대체한다. 양손 철퇴를 쓰는 동안 보조 무기 II는 비운다.']
    if groups['자동 부여']:
        overview+=['','자동 부여 · 별도 젬 제작 불필요',*[line for g,w,line in groups['자동 부여']]]
        if code in LATE:overview+=['광기의 선구자는 원본 고유 철퇴를 사용할 때만 부여된다.']
    overview+=['','사용 순서',rotation(code),'',b['description']]
    b['description']='\n'.join(overview)
    return b

def write_player_guides(out,builds,ko,bases):
    gear=['# 장비 추천 옵션','','게임의 각 장비 칸에도 아래 우선순위를 넣었다. 위에서부터 비교하되, 젬 요구 능력치·현재 부족한 저항·필요 정신력을 먼저 충족한다. 같은 아이템에 모든 옵션이 붙어 있어야 하는 체크리스트는 아니다. 수치가 없는 항목은 현재 구간에서 얻을 수 있는 값을 비교한다.','',
          '딜·회복 시뮬레이션은 원본 장비 수치를 사용한 예시다. 아래 추천 옵션을 새로 조합한 장비 전체를 다시 계산한 것은 아니다.','']
    gems=['# 무기·스킬셋과 사용 순서','','빌드 설명 맨 앞에 무기 I/II, 해당 스킬과 연결 젬, 사용 순서를 모았다. 무기 칸에도 해당 세트의 전체 연결표와 추천 옵션을 함께 표시한다. 각 스킬·보조의 개별 설명도 유지했다. G의 무기 세트는 직접 지정한다.','']
    for b in builds:
        gear+=['## '+b['name'],'','| 장비 칸 | 추천 옵션과 조건 |','|---|---|']
        for s in b['inventory_slots']:
            label={'Weapon1':'무기 I','Weapon2':'무기 II','Offhand1':'보조 무기 I','Offhand2':'보조 무기 II','Helm1':'투구','BodyArmour1':'갑옷','Gloves1':'장갑','Boots1':'장화','Amulet1':'목걸이','Belt1':'허리띠','Ring1':'반지 1','Ring2':'반지 2','Charm1':'호신부','Flask1':'마나 플라스크' if s.get('slot_x')==1 else '생명력 플라스크'}[s['inventory_id']]
            gear.append('| '+label+' | '+plain(s['additional_text']).replace('\n','<br>')+' |')
        gear.append('')
        gems+=['## '+b['name'],'',b['description'],'','| 무기 세트 | 스킬 | 연결할 젬 |','|---|---|---|']
        for where,members in skill_sets(b,ko,bases).items():
            for s,w,line in members:
                gems.append('| '+where+' | '+ko[bases[s['id']]]+' | '+(' + '.join(ko[bases[x['id']]] for x in s.get('support_skills',[])) or '현재 단계 연결 보조 없음')+' |')
        gems+=['','스킬별 사용법은 아래에 있다.','']
        for s in b['skills']:gems+=['<details><summary>'+ko[bases[s['id']]]+' 사용법</summary>','',plain(s['additional_text']),'','</details>','']
    gear+=['## 근거와 형식','','- 제작자 24·43·46·52·74레벨 실제 장비 보존본에서 무기·장갑의 모든 근접 스킬 레벨, 셉터·갑옷·목걸이 정신력, 생명력·저항·재생 옵션을 확인했다. 원본의 불필요한 공격 원소 피해나 치명타 옵션까지 필수로 권장하지 않는다.',
           '- [제작자 현재 리그 캐릭터](https://poe.ninja/poe2/builds/forbiddenriteshc/character/ITheCon-2183/SkadooshShoutedHard)',
           '- [GGG 공식 빌드 플래너 형식]('+SCHEMA_URL+'): 일반 장비 옵션 추천은 장비 칸의 설명으로 표시한다. 별도의 자동 옵션 선택 필드는 없다. 스킬·보조·패시브는 각각의 설명 필드를 지원한다.','']
    (out/'장비추천옵션.md').write_text('\n'.join(gear),encoding='utf-8')
    (out/'무기세트와젬연결.md').write_text('\n'.join(gems),encoding='utf-8')
