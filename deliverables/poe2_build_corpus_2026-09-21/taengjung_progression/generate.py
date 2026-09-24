"""Deterministic Taengjung progression adaptation. Never installs or edits source payloads."""
from pathlib import Path
import collections, copy, hashlib, json, re, xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parent
CORPUS=ROOT.parent
DATA=Path('D:/Pathcraft-AI/data/game_data_poe2')
TREE_PATH=Path('D:/Pathcraft-AI/deliverables/skadoosh_hc_2026-09-07/sources/tree_0_5.json')
START=47175
ASC_START=5852
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,x): p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def ids(x): return set(map(int,filter(None,(x or '').split(','))))

tree=read(TREE_PATH)
nodes={int(n['skill']):n for n in tree['nodes'].values() if isinstance(n,dict) and 'stringId' in n}
adj={n:set() for n in nodes}
for n,d in nodes.items():
    for e in d.get('connections',[]):
        v=int(e['id'])
        if v in adj: adj[n].add(v);adj[v].add(n)
bases=read(DATA/'BaseItemTypes.json')
# Some names have a unique-item variant row (e.g. Herald of Ash); the regular gem row must win the name lookup.
gems={bases[g['BaseItemType']]['Name']:{**g,'id':bases[g['BaseItemType']]['Id']} for g in sorted(read(DATA/'SkillGems.json'),key=lambda g:not bases[g['BaseItemType']]['Id'].rsplit('/',1)[-1].startswith('Unique'))}
extracts=read(CORPUS/'priority_pob_extracts.json')[:5]
source_paths={next(k for k in ['28509','285e2','28604','28695','29d39'] if k in Path(x['file']).name):Path(x['file']) for x in extracts}
roots={k:ET.parse(p).getroot() for k,p in source_paths.items()}
spec=roots['29d39'].find('Tree/Spec')
source_ids=ids(spec.get('nodes'))
weapon={w:ids(spec.find('WeaponSet'+str(w)).get('nodes')) for w in (1,2)}
common=source_ids-weapon[1]-weapon[2]

def path(target,pool,root=START):
    q=collections.deque([[root]]);seen={root}
    while q:
        p=q.popleft()
        if p[-1]==target:return p
        for v in sorted(adj[p[-1]]&pool-seen):seen.add(v);q.append(p+[v])
    raise AssertionError(('unreachable',target))
def reach(selected,root=START):
    seen={root};q=[root]
    for n in q:
        for v in sorted(adj[n]&selected-seen):seen.add(v);q.append(v)
    return seen
def connected(mapping):
    return all((s:={START}|{n for n,w in mapping.items() if w in (0,k)})==reach(s) for k in (1,2))
def paid_asc(a):return {n for n in a if not nodes[n].get('isFreeAllocate') and not nodes[n].get('isAscendancyStart')}
def budget(m,a):
    c=collections.Counter(m.values())
    return dict(ordinary_common=c[0],weapon_set_1=c[1],weapon_set_2=c[2],active_1_ordinary=c[0]+c[1],active_2_ordinary=c[0]+c[2],ordinary_points_required=c[0]+max(c[1],c[2]),weapon_specialization_capacity_required=max(c[1],c[2]),ascendancy_points_required=len(paid_asc(a)),free_ascendancy_nodes=len(a)-len(paid_asc(a)),free_class_start=1)
def node(n,w=0):
    d=nodes[n]
    return dict(id=str(n),numeric_id=n,stringId=d['stringId'],name=d['name'],stats=d.get('stats',[]),weapon_set=w,kind='ascendancy' if d.get('ascendancyName') else 'notable' if d.get('isNotable') else 'passive',source='xml-29d39' if not d.get('ascendancyName') else 'xml-28509 / xml-29d39')

CLAIMS=[
 dict(id='normal-asc',source='priority_taengjeong_kitava_shield_wall.md:66-70',url='https://www.youtube.com/watch?v=QcSeQ0OOENI&t=225s',scope='03:45–07:33 Coal Stoker first 2 points; then Masterwork NORMAL body. Branch priority fire resistance, physical taken as fire, armour to chaos, damaging ailments, crit, life. XML28509 resolves branch IDs.'),
 dict(id='weapon-alternatives',source='priority_taengjeong_kitava_shield_wall.md:79',url='https://www.youtube.com/watch?v=QcSeQ0OOENI&t=575s',scope='09:35–10:13 rare mace, cheaper sceptre, then Sacred Flame; Sacred Flame is optional, unnamed cheaper unique not fabricated.'),
 dict(id='helmet-gate',source='priority_taengjeong_kitava_shield_wall.md:80',url='https://www.youtube.com/watch?v=QcSeQ0OOENI&t=614s',scope='10:14–10:40 do not preallocate surround nodes before helmet. Acquired is not equipped; actual conditions and accuracy matter.'),
 dict(id='defense-order',source='priority_taengjeong_kitava_shield_wall.md:83',url='https://www.youtube.com/watch?v=QcSeQ0OOENI&t=728s',scope='12:08–12:55 Defiance of Destiny then Brass Dome then Olroth; change normal-body ascendancy with body. Olroth is an optional later upgrade.'),
 dict(id='pre-lowlife-supports',source='priority_taengjeong_kitava_shield_wall.md / cafe_playwright saved article208',url='https://cafe.naver.com/f-e/cafes/31644155/articles/208',scope='Creator 2026-09-17: Rapid Attacks II / Fire Attunement / Armour Break III before functioning lowlife mechanism; check campaign rewards.'),
 dict(id='latest-bundle',source='priority_taengjeong_kitava_shield_wall.md:5-11; priority_29d39.xml',url='https://cafe.naver.com/f-e/cafes/31644155/articles/224',scope='Creator 2026-09-21: Cat O Nine Tails AND skills/passives change together. Eternal Rage enabled, Raging Cry and Enraged Warcry II, Shield Wall set1 / cry set2. Flask recovery exception remains.'),
 dict(id='prefix-adaptation',source='priority_29d39.xml / tree_0_5.json',scope='Pathcraft deterministic unions of rooted source paths, not Taengjung act-tree or tested character. Select useful destinations; no point padding.'),
    dict(id='gem-minimums',source='D:/Pathcraft-AI/data/game_data_poe2/SkillGems.json + BaseItemTypes.json',scope='MinLevelReq is character eligibility; CraftingLevel is gem crafting tier. Neither saved XML gem level nor native [1,100] is an acquisition gate.'),
    dict(id='manual-rage',source='xml-28509; D:/Pathcraft-AI/.tmp/skadoosh-simulation/pob2/src/Data/Skills/sup_str.lua:2983,5930',scope='Source has Infernal Cry + Raging Cry + Tireless + Enraged Warcry I without Eternal Rage. Local effect data: Raging Cry grants4 rage per5 counted monster Power; Enraged I bypass costs20 rage. This is conditional, not perpetual rage: wait normal cooldown or use Fortifying Cry/totem when insufficient.'),
]

# Support gems are cut from an uncut support gem of at least their crafting level; its DropLevel is the area-level gate.
UNCUT_SUPPORT_DROP={int(m.group(1)):x['DropLevel'] for x in bases if (m:=re.search(r'SupportGemUncut(\d+)$',x.get('Id') or ''))}
def gem(name):
    g=gems[name]
    # Lineage supports (CraftingLevel 0) are never cut from uncut gems.
    extra=dict(uncut_support_drop_level=UNCUT_SUPPORT_DROP[g['CraftingLevel']]) if g['GemType']==1 and g['CraftingLevel']>0 else dict(lineage=True) if g['GemType']==1 else {}
    return dict(name=name,id=g['id'],min_character_level=g['MinLevelReq'],crafting_level=g['CraftingLevel'],**extra,tier=g['Tier'],gem_type=g['GemType'],colour=g['GemColour'],attribute_requirement_percent={k:g[k+'RequirementPercent'] for k in ['Strength','Dexterity','Intelligence']},actual_level_attribute_requirement='Check actual selected gem tooltip; percentage is colour weighting, NOT required attribute amount.')
def group(active,supports=(),source='xml-28509',condition='실제 젬 레벨·능력치·무기·자원으로 사용 가능한지 확인.',weapon_set=0,lineage=()):
    return dict(active=active,actives=[active],supports=list(supports),gems=[gem(n) for n in [active,*supports]],source=source,condition=condition,weapon_set=weapon_set,enabled=True,lineage=list(lineage))

# Lineage (혈통) supports cannot be cut from uncut gems (CraftingLevel 0). Capital-track files put them in the gem slots within 4 sockets
# (user: 3 Greater Jeweller's, 0 Perfect); ones that would need a 5th socket stay as text.
LINEAGE_KO={"Ahn's Citadel":'안의 성채',"Kaom's Madness":'카옴의 광기',"Uhtred's Rite":'우트레드의 의례',"Daresso's Passion":'다레소의 열정',"Atziri's Communion":'앗지리의 성찬식'}
def lineage(name,note,in_slots,hint=''):
    g=gems[name];assert g['GemType']==1 and g['CraftingLevel']==0
    return dict(name=name,ko=LINEAGE_KO[name],id=g['id'],min_character_level=g['MinLevelReq'],in_slots=in_slots,note=note,hint=hint)
# HC Forbidden Rites price snapshot that decided which lineage gems sit in a slot (user budget 5 Divine).
LINEAGE_PRICE_HC='poe.ninja HC Forbidden Rites 2026-09-22 06:39 UTC: 안의 성채 3 Divine · 카옴의 광기 3 Divine · 다레소의 열정 0.06 Divine · 우트레드의 의례 매물 없음 (사용자 확인: 안의 성채 비쌈)'
def lineage_text(g):
    if not g.get('lineage'):return ''
    one=lambda l:f"{l['ko']}({l['name']}, 캐릭터 {l['min_character_level']}부터){' · 젬 칸에 넣음' if l['in_slots'] else ' · 선택, 젬 칸엔 없음'} — {l['note']}"
    return '혈통 젬: '+' / '.join(one(l) for l in g['lineage'])+'\n'
KAOM_NOTE=('5칸째가 있어야 함(완벽한 세공사의 오브 · 지금 보유 0). 안의 성채가 있어야 작동: 카옴은 균열을 만드는 스킬만 보조하는데 방패의 벽은 안의 성채가 균열 타입을 붙여 줌(PoB 스킬 타입). '
           '효과: 균열 여러 개 추가, 대신 피해·속도·범위 감소(poe2db). 탱정 카페 답변 9/9(글 190, 개인 상담): 당시 보스에서는 카옴을 다른 보조로 바꾸라고 함.')
def add_lineage(stage,out):
    """Stage = phase index. 03 day-1 = 2 (shared), 04 Brass Dome = 3, 05~07 low-life = 4~6 (capital), 03+ = 7 (zero: none)."""
    by={g['active']:g for g in out}
    if stage==7:
        for g in out:g['condition']+=' 무자본: 미가공 보조 젬만(혈통 젬 없음).'
        return out
    ahn_note='비싸서 젬 칸엔 안 넣음('+LINEAGE_PRICE_HC+'). 탱정은 1일차에 샀다고 함(9/20 1부 1:46:59~1:47:04). 효과: 벽이 균열을 따라 생성(poe2db).'
    if stage in (2,3):by['Shield Wall']['lineage'].append(lineage("Ahn's Citadel",ahn_note+' 살 수 있으면 Concentrated Area 자리에.',False,'Concentrated Area 자리'))
    if stage==3:by['Shield Wall']['lineage'].append(lineage("Kaom's Madness",'황동 철갑·전직 변경 때쯤부터 낄 수 있다고 함(9/20 1부 2:00:05~2:00:18), 저장본 28695는 Concentrated Area 자리에 카옴(5칸 구성). '+KAOM_NOTE,False))
    if stage>=4:
        by['Shield Wall']['lineage'].append(lineage("Ahn's Citadel",ahn_note+' 살 수 있으면 Armour Break III 자리에(저장본 29d39는 5칸 + 카옴의 광기).',False,'Armour Break III 자리'))
        by['Shield Wall']['lineage'].append(lineage("Kaom's Madness",KAOM_NOTE,False))
        by['Infernal Cry']['lineage'].append(lineage("Uhtred's Rite",'HC 매물 없음('+LINEAGE_PRICE_HC+'). 저장본 29d39(07)의 4번째 보조. 재사용 대기가 있는 스킬(지옥불 함성 8초)에 붙어 사용 시 넘치는 성배를 주고, 생명력 플라스크 효과 중 피해 증폭 · 마나 플라스크 효과 중 마나 소모 효율 증가(poe2db).',False,'4번째 칸'))
        by['Eternal Rage']['condition']+=' 8/17 영상의 앗지리의 성찬식(혈통, 캐릭터 65)은 필요 없음: 9/20 개편에서 원소 약화로 피를 깎는 방식이 "아찌리 성찬식을 대신하는 거예요"(2부 2:14:49~2:15:49).'
    if stage>=3:
        out.append(group('War Banner',['Prolonged Duration II',"Daresso's Passion"],'xml-28604 · 28695 · 29d39',
            '저장본 28604·28695·29d39 모두 사용. 공격으로 영광을 모아 깃발을 세움(PoB). 정신력 30(PoB). '
            +('액트 정신력 100(PoB 퀘스트 보상 30+30+40) 안에 들어감.' if stage==3 else
              '영원한 격노 100과 합치면 130인데 액트 정신력은 100(PoB 퀘스트 보상 30+30+40)이라 셉터 정신력 없이는 둘 다 못 켬 — 전쟁 깃발을 쓰는 저장본 28604·28695·29d39는 모두 신성한 불꽃 셉터를 듦. 셉터 전이면 깃발을 끄고 05 묶음의 영원한 격노를 먼저(Pathcraft 판단). 탱정 9/20도 정신력이 모자랄 때 판금·깃발을 끄는 얘기를 하며 "전쟁 깃발을 빼는 건 너무 아쉬운데"라고 함(2부 2:43:58~2:44:09).'),
            lineage=[lineage("Daresso's Passion",'깃발에 필요한 영광 50% 감소(poe2db). 저장본 28604·28695·29d39 모두 장착. 싸서 젬 칸에 넣음('+LINEAGE_PRICE_HC+').',True)]))
    return out
def skill_groups(stage):
    low=4<=stage<=6  # 05~07 low-life; 7 = 03+ zero track (white armour)
    sw=['Execute III','Clash','Rapid Attacks II'] if low else ['Rapid Attacks II','Fire Attunement','Armour Break III']
    # 4th slot: Concentrated Area on white armour and 04; Armour Break III in 05~07 until the wolf charm (8/17 12:01-12:05, cafe 204)
    sw+=['Armour Break III'] if low else ['Concentrated Area'] if stage in (2,3,7) else []
    out=[group('Shield Wall',sw,'cafe208 + xml-285e2' if not low else 'cafe224 + xml-29d39',
        '방어도 방패. '+('저생명력·회복·방어·격노 묶음 확인 후.' if low else '저생명력 보조 미사용. 방패벽을 함성/토템으로 직접 파괴.'),1),
        group('Infernal Cry',['Raging Cry','Tireless','Enraged Warcry II' if low else 'Enraged Warcry I'],'xml-29d39' if low else 'xml-28509',
        '세트2. 벽이 안 터지면 함성으로 터뜨림(9/20 2부 2:50:44~2:51:51). 재사용 대기 8초(PoB). '+('Eternal Rage가 격노를 계속 채워 Enraged Warcry II로 대기를 더 자주 건너뜀.' if low else '직접 함성 사용. Raging Cry는 몬스터 위세5마다 격노4, Enraged I 재사용 대기 우회는 격노20 소모(저장 데이터). 부족하면 정상 재사용 대기시간을 기다리거나 Fortifying Cry/토템으로 벽을 파괴. 상시 함성/영원한 격노를 가정하지 않음.'),2)]
    if not low:out += [group('Fortifying Cry',condition='세트 2(9/20 방송: 함성은 전부 세트 2). 지옥불 함성이 재사용 대기(8초) 중일 때 두 번째 벽 파괴 수단. Guard + 이후 방패 공격 적중 시 Shield Wave(PoB). 05 아홉꼬리 묶음 때 뺌.',weapon_set=2),
        group('Shockwave Totem',['Urgent Totems III','Hardy Totems II','Rapid Attacks III'] if stage in (2,7) else [],'xml-28509',TOTEM_WEAPONS+'. 3일차에 셉터로 바꾸면 못 쓰고, 그때는 두 함성으로 벽을 터뜨림.'+(' 보조는 탱정 28509(흰색 갑옷 시절): Urgent Totems III · Hardy Totems II(레벨 4) · Rapid Attacks III(레벨 5) 미가공 보조.' if stage in (2,7) else ''))]
    if low:out += [group('Eternal Rage',source='xml-29d39',condition='캐릭터59부터 젬 자격; 실제 젬 레벨·힘·정신력과 활성 상태를 확인. 전체 빌드 준비 완료를 뜻하지 않음.'),
        group('Elemental Weakness',['Lifetap','Magnified Area II','Heightened Curse'],'xml-29d39 + 9/20 방송','체크포인트에서 세네 번 걸어 생명력을 깎음(9/20 2부 2:14:32, Lifetap이 저주 비용을 생명력으로). 저장본의 Impending Doom · Focused Curse는 소켓 여유가 있을 때. 지능 요구치 확인.'),
        group('Freezing Mark',['Mark for Death II','Mark of Siphoning II'],'xml-29d39 + 9/20 방송','아홉꼬리 묶음 때 같이 추가(9/20 방송 1부 2:01:49~2:09:47).')]
    return add_lineage(stage,out)

DISPLAY={1:None,2:3,3:4,4:5,5:6,6:7}  # phase -> installed number; phase 1 is the uninstalled 40-level alternative
UNIQUE_ITEMS={"Olroth's Resolve",'Defiance of Destiny','The Brass Dome',"Cat O' Nine Tails",'Constricting Command'}
def equipment(stage):
    out=[dict(slot='Weapon 1',name='Usable rare mace / 사용 가능한 희귀 철퇴',status='equipped_condition',condition=('3일차에 돈이 조금 모이면 셉터부터(9/20 1부 2:00:41~2:01:03, 최신 저장본 무기 = 신성한 불꽃). 셉터로 바꾸면 충격파 토템은 못 씀. ' if stage>=3 else '')+'우선 옵션: +모든 근접 스킬 레벨(방패의 벽은 근접 스킬 · 탱정 철퇴 +3) > 함성 재사용 대기 회복(한손 철퇴 Desecrated 접미사 17~25%, 탱정 저장본엔 없음). 방패의 벽은 무기가 아니라 방패 방어도로 피해를 내고 공격 시간도 방패 기준 고정이라(PoB) 철퇴의 공격 속도·피해 옵션은 다른 공격 스킬용 부가. 실제 요구 레벨·능력치 확인. 저렴한 셉터·Sacred Flame은 선택.'),
         dict(slot='Weapon 2',name='Armour shield / 방어도 방패',status='equipped_condition',condition='방어도 최우선: 방패의 벽 피해 = 방패 방어도 15당 물리 피해 추가(PoB 스킬 데이터)'+(', Greatest Defence = 방패 방어도·회피 75당 공격 피해 4%(세트 1 노드라 세트 2 함성으로 터뜨릴 때 적용되는지는 미확인)' if stage>=2 else '')+'. 우선 옵션: 고정 방어도 + 방어도 % 증가 > 화염 저항·최대 화염 저항 > 생명력 > 기절 한계치 > 힘. 탱정 저장본 베이스: 초반 Goldworked Tower Shield → 이후 Tawhoan Tower Shield. 저장본 방어도 1186/1463/1896은 예시일 뿐 기준선 아님. 탱정 9/20: 방어도 1000이면 T15 맵까지 충분, 10 Divine 넘는 경우 거의 없음, 사지 말고 제작 권장.'),
         dict(slot='Body Armour',name='Normal body armour / 일반 등급 갑옷' if stage<3 else 'The Brass Dome / 황동 철갑',status='equipped_condition',condition='Masterwork를 찍은 동안은 일반(흰색) 등급만 → 옵션 없음. 방어도 높은 베이스 + 품질 · 룬으로 고름(탱정 저장본: Superior Warlord Cuirass 방어도 595 · 9/20 방송 1일차 예: 전쟁군주 흉갑). Masterwork에 연결된 전직 노트블 1개당 방어도 +200.' if stage<3 else '저장본 요구 레벨 58은 단서일 뿐, 실제 베이스·요구치 확인. 착용 전에 Masterwork 분기와 Masterwork를 모두 환불하고, 잃는 화염 저항·피해 전환·회복을 다시 확인.'),
         dict(slot='Amulet',name='Usable life/resistance amulet / 생명력·저항 목걸이' if stage==1 else 'Defiance of Destiny / 운명의 저항',status='prepare_not_equip' if stage==2 else 'equipped_condition',condition='저장본 요구 레벨 56은 지금 착용해도 된다는 뜻이 아님. 준비하는 동안 현재 쓸 수 있는 목걸이 유지.' if stage==2 else '생명력 · 부족한 저항 · 힘(요구 능력치). 탱정 저장본 근거 없는 일반 기준.' if stage==1 else '실제 비예약 생명력과 받는 피해에서 피격 전 회복이 작동해야 함. 저장본 옵션: 힘 · 민첩 · 최대 생명력 % 증가. 요구 레벨 56은 빌드 전체 준비 완료를 뜻하지 않음.'),
         dict(slot='Helmet',name='Usable defensive helmet / 방어 투구' if stage<5 else 'Constricting Command / 목 죄이는 명령',status='equipped_condition',condition='생명력 · 부족한 저항 · 방어도(탱정 저장본 근거 없는 일반 기준). 포위 노드를 전제하지 않음. 목 죄이는 명령은 미리 사 둬도 06 전엔 착용 조건 확인.' if stage<5 else '사용 가능한 목 죄이는 명령을 실제로 착용. 포위 상태와 Frantic Fighter 이후 명중률을 함께 확인. 저장본 요구 레벨은 최신 38 / 과거 55로 베이스에 따라 다름.'),
         dict(slot='Belt',name='Usable resistance/life belt / 저항·생명력 허리띠' if stage<4 else "Cat O' Nine Tails / 아홉꼬리",status='equipped_condition',condition='우선 옵션: 화염·번개 저항 > 방어도 > 플라스크 마나 회복 > 가시 피해(탱정 28509~28695 희귀 허리띠). 일반 생명력 기반 보조 구성 유지.' if stage<4 else '저장본 요구 레벨 55는 착용 자격 단서일 뿐. 플라스크 외 회복은 저생명력 위로 못 올라가고 플라스크는 예외. 실제 운용 중 저생명력 유지와 안전한 회복을 확인.'),
         *([dict(slot='Flask 1',name="Olroth's Resolve / 올로스의 결의",status='equipped_condition',condition='황동 철갑 직후에 곧바로 챙기는 필수 생존템(8/17 영상 12:43–12:53). 05 아홉꼬리 묶음 때 생명력 플라스크는 빼도 되고 안 빼도 됨(9/20 2부 2:14:49). 최신 저장본 29d39는 플라스크 1이 비어 있음.')] if stage==3 else []),
         *[dict(slot=s,name=n,status='equipped_condition',condition=c) for s,n,c in [
           ('Ring 1','Rare ring / 희귀 반지','1일차(맵 진입): 액트 보상 루비 반지(화염 품질 10+) 2개면 됨(9/20 방송). 베이스: 최종 저장본은 루비 반지, 이전 저장본은 프리즈매틱·자수정 반지도 씀. 우선 옵션: 화염 저항 대량(Coal Stoker로 냉기·번개도 절반씩) > 화염·카오스 복합 저항 > 생명력 > 공격에 화염·물리 피해 추가 > 생명력 흡수·재생(초반 저장본).'),
           ('Ring 2','Rare ring / 희귀 반지','반지 1과 같은 기준. 탱정 최종 반지 2개 화염 저항 합계 86% · 76%(각각 화염·카오스 복합 16% · 15% 포함).'),
           ('Boots','Rare boots / 희귀 장화','우선 옵션: 이동 속도(저장본 25% → 35%) > 생명력 > 카오스·냉기·번개 저항 > 방어도 > 힘 > 기절 한계치 · 빙결/감전 지속 감소.'),
           ('Gloves','Rare gloves / 희귀 장갑','우선 옵션: +2 모든 근접 스킬 레벨(탱정 저장본 28509·285e2·28695·29d39 모두) > 방어도 > 공격에 원소 피해 추가 > 물리 공격 피해 마나 흡수(마나 유지) > 카오스·화염 저항. 함성용: 룬 Boar Idol(Bonded: 함성 재사용 대기 회복 25%) 소켓 가능.')]]]
    # Named uniques are shown by the in-game planner through unique_name (same shape as poe.ninja exports).
    for e in out:
        en=e['name'].split(' / ')[0]
        if en in UNIQUE_ITEMS and e['status']!='prepare_not_equip':e['unique']=en
    if stage==6:
        # Author's saved 29d39 flask/charms: optional reference, not an entry requirement.
        out+=[dict(slot=s,name=n,unique=n,status='optional_reference',condition='탱정 29d39 저장본 장비 · 선택. 필수 구매 아님, 가격 미확인.') for s,n in [('Flask 2',"Uhtred's Chalice"),('Charm 1','The Fall of the Axe'),('Charm 2','Rite of Passage'),('Charm 3','For Utopia')]]
    return out

def optional_branches():
    return [dict(id='sacred-flame',label='선택: Sacred Flame / 저렴한 셉터 경로',source_claims=['weapon-alternatives','xml-28604','xml-29d39'],conditions=['쓸 수 있는 셉터를 실제로 착용하고 정신력·스킬 무기 호환을 확인. 호환되지 않으면 철퇴 전용 토템·행동을 빼야 함.','Sacred Flame은 진입이나 저생명력 전환에 필수가 아님. Purity of Fire는 아이템이 주는 스킬이라 희귀 철퇴로는 가정할 수 없음.'],groups=[group('Purity of Fire',['Cool Headed','Warm Blooded','Vitality II'],'xml-29d39','실제 Sacred Flame 부여와 충분한 정신력이 있을 때만. 부여 스킬 연결은 수동.')]),
            dict(id='fire-spell-on-hit',label='선택: 수동 회복·발동 확장',source_claims=['xml-28604','xml-29d39'],conditions=['Heat of the Forge를 실제로 찍은 뒤 에너지 생성·마나/생명력 회복·발동 동작·보조 연결을 확인.','게임 빌드 파일 형식으로는 메타 연결 전체를 표현할 수 없음: Detonate Dead + Gorge + Fire Mastery + Energy Retention(액티브 1 + 보조 3)을 직접 연결.','다섯 번째 Boundless Energy II는 추가 소켓이 필요한 선택 분기이며 핵심이 아님. 시험 전 작동을 가정하지 말 것.'],groups=[group('Detonate Dead',['Gorge','Fire Mastery','Energy Retention'],'xml-29d39','부여된 Fire Spell on Hit 아래에 들어가는 연결이며 독립 추천 스킬이 아님.')]),
            dict(id='spirit-defense',label='선택: 방어용 정신력 젬',source_claims=['xml-28509'],conditions=['실제 정신력 여유가 있을 때만. 모든 오라가 들어간다고 가정하지 않음.'],groups=[group('Time of Need'),group('Scavenged Plating')]),
            dict(id='later-supports',label='선택: 저장본의 5보조 방패의 벽',source_claims=['xml-29d39'],conditions=["저장본 5보조: Execute III / Clash / Rapid Attacks II / Ahn's Citadel / Kaom's Madness.",'상급 세공사의 오브는 소켓 4개. 완벽(Perfect)은 보유 신고 없음. 다섯 번째 보조는 모든 게임 파일 핵심에서 제외.',"안의 성채(캐릭터 65)는 비싸서 젬 칸에 넣지 않음, 살 수 있으면 4번째 칸. Kaom 다섯 번째는 소켓 등급이 하나 더 필요하며, 65가 빌드 최소치라는 뜻이 아님."]),
            dict(id='olroth',label="선택: 올로스의 결의(Olroth's Resolve)",source_claims=['defense-order'],conditions=['운명의 저항·황동 철갑 이후의 방어 업그레이드. 진입 필수 장비가 아니며 현재 가격·환산을 가정하지 않음.'])]

def author_resists():
    """Resistance lines on the author's saved 29d39 items, summed per element (hybrid lines count for both)."""
    items={it.get('id'):(it.text or '') for it in roots['29d39'].findall('./Items/Item')}
    total=collections.Counter();by_slot={}
    for s in roots['29d39'].findall('./Items/ItemSet/Slot'):
        text=items.get(s.get('itemId'))
        if not text:continue
        found=collections.Counter()
        for m in re.finditer(r'([+-]\d+)% to (?:(Maximum) )?(Fire|Cold|Lightning|Chaos)(?: and (Chaos))? Resistances?',text):
            for el in filter(None,(m.group(3),m.group(4))):found[('max ' if m.group(2) else '')+el]+=int(m.group(1))
        if found:by_slot[s.get('name')]=dict(found);total.update(found)
    return dict(total),by_slot
KO_RES={'Fire':'화염','Cold':'냉기','Lightning':'번개','Chaos':'카오스','max Fire':'최대 화염','max Cold':'최대 냉기','max Lightning':'최대 번개','max Chaos':'최대 카오스'}
KO_SLOT={'Ring 1':'반지 1','Ring 2':'반지 2','Weapon 2':'방패','Boots':'장화','Gloves':'장갑','Helmet':'투구','Belt':'허리띠','Amulet':'목걸이','Body Armour':'갑옷','Weapon 1':'무기'}
def resistance_plan(index):
    """Stage resistance guidance derived from ascendancy node stats and the author's saved items."""
    total,by_slot=author_resists()
    rule='저항(탱정 9/20 방송): 원소 저항 75% 이상, 카오스 60%(1일차는 40%도 괜찮음), 화염 저항 합계 250~260%를 목표. 화염·냉기·번개 상한 75%. Coal Stoker(전직)로 장비의 화염 저항 옵션이 냉기·번개 저항도 절반씩 줍니다 → 반지·방패·허리띠·장갑의 화염 저항 위주로 맞추고 모자란 냉기·번개만 따로. 실제 값은 캐릭터 창 기준(액트 저항 페널티는 로컬 자료에 없음).'
    if index<=2:
        return [rule,'Tantalum Alloy(일반 갑옷 분기)가 갑옷으로 화염 저항 +75%, Coal Stoker로 냉기·번개 +37.5%씩. 유료 전직 2포인트뿐이면 이 저항이 없으니 장비로 채움.']
    out=[rule]
    if index==3:out.append('황동 철갑으로 바꾸면 Tantalum Alloy·Dedication to Kitava가 빠져 화염 -75%, 냉기·번개 -37.5%씩, 방어도의 카오스 적용도 사라짐. 바꾸기 전에 장비만으로 화염 저항 75% 이상을 먼저 확보.')
    out.append('황동 철갑 저장본 옵션: 최대 원소 저항 -1%. Forged in Flame: 최대 화염 저항 옵션이 최대 냉기·번개 저항도 올림.')
    if index==6:out.append('저장본 장비 저항 합계(복합 옵션은 양쪽에 계산): '+', '.join(f'{KO_RES[k]} {v:+d}%' for k,v in sorted(total.items()))+' · 칸별 '+'; '.join(f'{KO_SLOT.get(s,s)} '+'/'.join(f'{KO_RES[k]} {v:+d}' for k,v in d.items()) for s,d in by_slot.items())+'.')
    return out
def weapon_set_roles(mapping,groups):
    """What each weapon set carries: its skills and its set-only notables."""
    role={}
    for w in (1,2):
        notables=sorted(nodes[n]['name'].strip() for n,s in mapping.items() if s==w and nodes[n].get('isNotable'))
        role[str(w)]=dict(skills=[g['active'] for g in groups if g['weapon_set']==w],passive_count=sum(s==w for s in mapping.values()),notables=notables)
    role['0']=dict(skills=[g['active'] for g in groups if g['weapon_set']==0])
    return role
# Low-budget purchase order and whether each swap can be done alone or must be done as one town bundle.
LOWBUDGET_SWAPS=[
 dict(order=1,stage=2,item='맵 진입 전환: 별이슬 막간 트리 → 탱정 1일차',slot='트리 · 전직 · 갑옷',swap='한꺼번에',how='액트가 끝나면 마을에서 한 번에 재분배. 흰색 갑옷 + Masterwork, 방패 방어도(1000이면 T15까지), 액트 루비 반지 2개, 저항 75%+ · 카오스 60%(1일차 40%도 괜찮음). 1일차는 흰템으로 끝냄(1:31:23). 2일차에 싼 게 많다(1:31:37)지만 첫날도 생각보다 싸다(1:39:05)고도 함.',source='9/20 방송 1부 0:07:12 · 1:16:19~1:39:25'),
 dict(order=2,stage=3,item='운명의 저항 (Defiance of Destiny)',slot='목걸이',swap='하나씩',how='2일차에 목걸이만 먼저 바꿔도 됨. 저장본 요구 레벨 56.',source='9/20 방송 1부 1:48:12 · 2:48:02'),
 dict(order=3,stage=3,item='화염 저항 장비 (반지 · 방패 · 허리띠 · 장갑)',slot='여러 칸',swap='하나씩',how='황동 철갑 전에 장비만으로 화염 75% 이상, 탱정 목표는 화염 저항 합계 250~260%. 일반 갑옷 분기의 화염 +75%가 빠지기 때문.',source='9/20 방송 1부 3:32:09 · 2부 0:07:01 · 전직 노드 효과(tree_0_5.json)'),
 dict(order=4,stage=3,item='황동 철갑 (The Brass Dome)',slot='갑옷',swap='한꺼번에',how='노드 제거 · 전직 변경을 같이: Masterwork 분기 + Masterwork 환불 → 황동 철갑 착용 → Forged in Flame · Heat of the Forge. 한 번 황동을 입었으면 흰색 갑옷으로 돌아가지 않음. 저장본 요구 레벨 58.',source='9/20 방송 1부 1:56:49~2:00:08 · 1:20:39 · 8/17 영상 12:08–12:55'),
 dict(order=5,stage=3,item='올로스의 결의 (Olroth\'s Resolve)',slot='플라스크',swap='하나씩',how='황동 철갑 직후 필수 생존템. 05 아홉꼬리 묶음 때 생명력 플라스크는 빼도 되고 안 빼도 됨.',source='8/17 영상 12:43–12:53 · 9/20 방송 1부 2:50:18 · 2:51:09(시청자 세팅 점검) · 2부 2:14:49'),
 dict(order=6,stage=3,item='셉터 (최신 저장본: 신성한 불꽃 Sacred Flame)',slot='무기',swap='하나씩',how='3일차에 돈이 조금 모이면 셉터부터 맞추기 시작. 셉터로 바꾸면 충격파 토템(셉터는 PoB 무기 목록에 없음)은 못 쓰고 두 함성으로 벽을 터뜨림.',source='9/20 방송 1부 2:00:41~2:01:03 · 29d39 저장본 무기 · PoB 충격파 토템 weaponTypes'),
 dict(order=7,stage=4,item='아홉꼬리 묶음: 아홉꼬리 (Cat O\' Nine Tails) + 영원한 격노 + Elemental Weakness(Lifetap) · 동결의 징표 · Execute III · Clash',slot='허리띠 · 젬 · 트리',swap='한꺼번에',how='미리 사 두고 한 번에: 허리띠 + 저항용 Desert Rune + 트리 재조정(지능 요구치 확인) + 체크포인트에서 Elemental Weakness를 세네 번 걸어 생명력 깎기 + 영원한 격노 켜기 + 방패의 벽 보조 교체. 생명력 플라스크는 빼도 되고 안 빼도 됨. "저자본의 모토는 편의성을 갖다 버린다". 탱정 발언: 교체 1 Divine 미만, 전체 10~15 Divine(9/20 시세).',source='9/20 방송 1부 2:02:56~2:09:47 · 0:24:03 · 2:27:09 · 2부 2:13:23 · 2:14:32 · 2:14:49 · 2:15:22 · 2:17:00 · 카페 224'),
 dict(order=8,stage=5,item='목 죄이는 명령 (Constricting Command)',slot='투구',swap='하나씩',how='투구(2소켓 고유 Viper Cap)만 먼저 착용한 뒤 원형(포위) 노드 약 5개. 탱정 발언 9~11 Divine(9/20 시세).',source='9/20 방송 1부 4:39:57 · 2부 1:52:11 · 8/17 영상 10:14–10:40'),
 dict(order=9,stage=6,item='선택: 우물 심장(Heart of the Well) 주얼 · 신성모독 · 호신부 · Uhtred\'s Chalice',slot='주얼 · 젬 · 호신부 · 플라스크',swap='하나씩',how='자본 여유가 있으면 우물 심장(싸다고 함). 저자본은 신성모독(Blasphemy)을 안 써도 되고 후반에 씀(자막 "신성부독", 같은 방송 4:43:25 "신석모독 퀄리티 효과로 저주 강도"). 고자본은 이중인격 주얼(100~150 Divine 발언).',source='9/20 방송 1부 4:55:56 · 4:40:08 · 4:43:25 · 3:53:45'),
]
GEAR_NOTE='장비 기준: 방패의 벽 피해는 방패 방어도에서 나옵니다(방패 방어도 15당 물리 피해 추가). 방패 방어도 → 장갑·철퇴의 +근접 스킬 레벨 → 저항 → 생명력 순. 함성 옵션: 일반 희귀 옵션으로는 거의 없고, 한손 철퇴 Desecrated 접미사(함성 재사용 대기 회복 17~25%) · 장갑 룬 Boar Idol(25%) · 특수(Berserk) 옵션 정도입니다. 탱정 저장본 장비에는 함성 옵션이 없어 함성은 주로 트리(07 세트 2)와 보조 젬으로 키웁니다. 부위별 우선 옵션은 장비 칸 설명에 있습니다.'
KO_SKILL={'Shield Wall':'방패의 벽','Infernal Cry':'지옥불 함성','Fortifying Cry':'보강하는 함성','Shockwave Totem':'충격파 토템','Eternal Rage':'영원한 격노'}
def weapon_set_text(role):
    ko=lambda a:'·'.join(KO_SKILL.get(x,x) for x in a)
    def one(w,what):
        r=role[w];return f'세트 {w} = {ko(r["skills"])}({what})'+(f', 세트 전용 패시브 {r["passive_count"]}개: '+'·'.join(r['notables']) if r['passive_count'] else ', 세트 전용 패시브 없음')
    return ('무기 세트: '+one('1','방패로 벽 세우기')+' / '+one('2','함성으로 벽 터뜨리기')+' / 양쪽 공통 = '+ko(role['0']['skills'])
            +'. 스킬을 세트에 배정하면 쓸 때 그 세트로 바뀝니다. 저장본에는 세트 2 무기 칸이 비어 있어 세트 2에 무엇을 드는지는 확인 안 됨.')
REF_POB=CORPUS/'linked_update_pob.xml'
def transition_ops(start,target):
    """Town respec from start to target: connectivity-preserving refunds first, connected additions when refunds stall."""
    state=dict(start);ops=[]
    while state!=target:
        refunds=[n for n in state if target.get(n)!=state[n] and connected({k:v for k,v in state.items() if k!=n})]
        if refunds:
            n=min(refunds);ops.append(dict(action='refund',numeric_id=n,stringId=nodes[n]['stringId'],name=nodes[n]['name'],weapon_set=state.pop(n)));continue
        adds=[n for n in target if n not in state and connected({**state,n:target[n]})]
        assert adds,'transition stalled'
        n=min(adds);state[n]=target[n];ops.append(dict(action='allocate',numeric_id=n,stringId=nodes[n]['stringId'],name=nodes[n]['name'],weapon_set=target[n]))
    return ops
def reference_skills(root,upto_interlude):
    """Reference 'Swap' skill set: real gems only, enabled supports only, labels skipped; act files stop at the Interlude label."""
    groups=[];skipped=[]
    for sk in next(s for s in root.findall('Skills/SkillSet') if s.get('title')=='Swap').findall('Skill'):
        if upto_interlude and (sk.get('label') or '').startswith('^4Interlude'):break
        gs=[g for g in sk.findall('Gem') if g.get('enabled')!='false']
        if not gs:continue
        names=[g.get('nameSpec') for g in gs]
        if sk.get('slot'):skipped.append(dict(gems=names,reason='item-granted slot group ('+sk.get('slot')+'), not a socketed gem group'));continue
        if not all(n in gems for n in names):skipped.append(dict(gems=names,reason='not a gem in SkillGems'));continue
        groups.append(group(names[0],names[1:],'별이슬 0.5.5 PoB Swap','별이슬 액트 구성 그대로.'))
    return groups,skipped
# Taengjung 8/17 low-budget guide 4:32-7:15: 1st ascension (2) = Fire Resistance -> Coal Stoker; from the 2nd, Smith's Masterwork (free, normal body)
# then Tantalum Alloy -> Molten Symbol -> Dedication to Kitava -> Heatproofing -> Internal Layer -> Kitavan Engraving 60913 (+15% life; not Imprint 16276).
KITAVA_ORDER=[14960,57959,9988,61039,9997,64962,25438,110,60913]
def spec_paid_asc(root,title):
    """Paid ascendancy points in the 별이슬 spec (Warbringer there; only the count carries over to Kitava)."""
    spec=next(s for s in root.findall('Tree/Spec') if s.get('title')==title)
    return len(paid_asc({n for n in ids(spec.get('nodes')) if nodes[n].get('ascendancyName')}))
def kitava_prefix(paid):
    """Taengjung's order, cut after `paid` paid points (free Masterwork rides along when reached)."""
    out=[]
    for n in KITAVA_ORDER:
        if len(paid_asc(set(out)))==paid:break
        out.append(n)
    assert len(paid_asc(set(out)))==paid
    return out
ASC_NOTE={14960:'1차 전직 ①(2장 · 별이슬 26:04~26:34): 화염 저항(석탄 때기로 가는 길). 탱정 8/17 영상 4:32.',
          57959:'1차 전직 ②: 석탄 때기 — 화염 저항 옵션이 냉기·번개 저항도 50% 줌. 탱정 8/17 영상 4:36~5:02.',
          9988:'2차 전직(3장 혼돈의 사원 · 별이슬 33:18~33:24)부터: 대장장이의 걸작(무료). 찍는 순간 흰색(일반) 갑옷만 입을 수 있음. 8/17 영상 5:03~5:30.',
          61039:'2차 전직 ①: 탄탈룸 합금 — 갑옷이 화염 저항 +75%(석탄 때기로 냉기·번개 +37.5%씩). 8/17 영상 6:11.',
          9997:'2차 전직 ②: 녹아내린 상징 — 받는 물리 피해 25%를 화염으로. 8/17 영상 6:22.',
          64962:'3차 전직 ①: 키타바에 대한 헌신 — 방어도가 카오스 피해에도 100%. 8/17 영상 6:35.',
          25438:'3차 전직 ②: 내열 처리 — 피해 주는 상태 이상 무시. 8/17 영상 6:50.'}
ASC_ORDER='전직(탱정 8/17 영상 4:32~7:15): 1차 2포인트 = 화염 저항 → 석탄 때기. 2차부터 대장장이의 걸작(무료, 흰색 갑옷만) 아래로 탄탈룸 합금 → 녹아내린 상징 → 키타바에 대한 헌신 → 내열 처리 → 내부 층 → 키타바의 각인(최대 생명력 15%, Kitavan Engraving). 한국어로 "키타바의 각인"이 두 개라 영광 생성 60% 쪽(Kitavan Imprint)은 아님. 순서는 취향대로 바꿔도 된다고 함(5:11~5:19). 전직 시기는 사람마다 달라 탱정도 생략(4:09~4:21). '
ASC_PLACED=('이 파일에는 별이슬 트리와 같은 유료 전직 {paid}포인트만큼 이 순서대로 넣었습니다. 별이슬 영상의 전직 시점: 1차 = 2장 드레드노트 전(26:04~26:34), 2차 = 3장 혼돈의 사원(33:18~33:24). '
            '막간에서 자도가 주는 60레벨 진 바리아로 3차 전직도 할 수 있습니다(1:02:14~1:02:20) → 키타바에 대한 헌신 → 내열 처리.')
SLOTS={'Weapon 1':('Weapon1',0),'Weapon 2':('Offhand1',0),'Body Armour':('BodyArmour1',0),'Amulet':('Amulet1',0),'Helmet':('Helm1',0),'Belt':('Belt1',0),'Flask 1':('Flask1',0),'Flask 2':('Flask1',1),'Ring 1':('Ring1',0),'Ring 2':('Ring2',0),'Boots':('Boots1',0),'Gloves':('Gloves1',0),'Charm 1':('Charm1',0),'Charm 2':('Charm1',1),'Charm 3':('Charm1',2)}
# Act gear (00-02). "별이슬 m:ss" = 별이슬 act video dcSWTFyF9TQ, "별이슬 업데이트 m:ss" = zaft1U-7klQ, "8/17" = Taengjung QcSeQ0OOENI, "9/20" = Taengjung live cpSnWuxzcRI.
# Kitava constraints: Coal Stoker (fire res mods also grant cold/lightning at 50%), Smith's Masterwork = normal body armour only.
TOTEM_WEAPONS='충격파 토템은 PoB 무기 목록(철퇴·도끼·검·창·도리깨·단검·클로·활·쇠뇌·지팡이·부적)에 있는 무기로만 씀 — 셉터는 목록에 없음'
ACT_LINEAGE_NOTE='혈통 젬: 액트에서는 안 씁니다. 안의 성채 · 카옴의 광기 · 우트레드의 의례 · 다레소의 열정 · 앗지리의 성찬식 모두 캐릭터 65부터(게임 데이터). 맵 진입(03)부터 스킬 칸 설명을 보세요.'
ACT_GEAR_NOTE=('액트 장비(별이슬 액트 영상 dcSWTFyF9TQ · 0.5.5 업데이트 zaft1U-7klQ, 탱정 영상·방송의 키타바 조건). 별이슬 액트 영상은 0.5.5 전 판이고 업데이트 영상이 바뀐 점만 짚습니다. '
               '방패 방어도가 먼저입니다: 방패의 벽 피해가 방패 방어도에서 나옵니다(PoB). 저항은 화염 저항부터(석탄 때기로 냉기·번개도 절반, 8/17 4:36~5:02). '
               '액트 저항 보상: 냉기 10%(1장, 별이슬 2:15) · 2장은 별이슬이 번개 10%(25:49), 탱정 9/20은 2막 원소 공물에서 루비 화염의 공물(루비 반지)을 고름(1:38:34~1:38:40, 같은 선택지인지 확인 안 됨) · 화염 10%(3장 검은 턱, 34:19) · 4장 죽음의 전당은 저항 선택(49:48~49:54). '
               '4장 카이마나 상어 지느러미 보상은 방어도 30% 증가(별이슬 업데이트 1:52~2:03).')
def ref_equipment(title):
    """Per-slot act gear for 00 (act 3), 01 (act 4), 02 (interlude). Only what the sources say, plus Kitava node rules."""
    act3,act4,inter=title=='3',title=='4',title=='Interlude'
    body=dict(slot='Body Armour',name='Normal body armour / 일반 등급 갑옷',condition=('3장 혼돈의 사원 2차 전직(별이슬 33:18~33:24)에서 대장장이의 걸작을 찍기 전까지는 희귀 갑옷도 됩니다. 찍는 순간 흰색만이니 방어도 높은 흰색 갑옷을 미리 챙겨 두세요. ' if act3 else '대장장이의 걸작을 찍었으니 흰색만 입습니다. ')
              +'옵션이 없으니 방어도 높은 힘 베이스를 고르고 방어구 장인의 고철로 품질을 올립니다(노드 문구 · 8/17 5:23~5:29). '
              '탄탈룸 합금이 이 갑옷에 화염 저항 +75%를 붙이고, 석탄 때기로 냉기·번개에도 그 절반(+37.5%)씩 붙습니다(노드 문구). 탱정은 "대부분의 원소 저항이 한 번에 보완"된다고 했습니다(8/17 6:16~6:22). 걸작에 연결된 전직 노트블 1개당 방어도 +200(노드 문구 · 8/17 5:37~5:45).')
    ring=('1일차(맵 진입) 반지는 화염 품질 10 이상 루비 반지 2개(탱정 9/20 1:35:43~1:36:16). 입수: 2막 원소 공물에서 루비 화염의 공물(9/20 1:38:34~1:38:40) · '
          '4장 화산 땅굴 희귀 반지 — 번개 희귀 몹을 먼저, 화염 희귀 몹을 마지막에 잡으면 루비 반지(별이슬 43:44~43:56 · 9/20 1:37:22~1:38:11). 화염 저항 우선(석탄 때기로 냉기·번개도 절반) > 생명력.'
          +(' 막간에서 뱀 몹이 주는 바리아 2개 중 하나는 반지 소원(별이슬 1:02:26~1:02:35).' if inter else ''))
    out=[dict(slot='Weapon 1',name='One-hand mace / 한손 철퇴',condition='방패를 들므로 한손 무기. 무기 세트 1·2를 같은 장비로 고정(마우스 클릭, 별이슬 28:27~28:40). '+TOTEM_WEAPONS+'. '
              '별이슬은 워브링어 전직(함성 재사용 대기 무시 노드) 뒤 토템을 뺐지만(26:34~26:47) 키타바에는 그 노드가 없습니다. 업그레이드는 진화·확장의 오브만 쓰는 선에서(15:38), 대장장이의 숫돌로 품질(16:03), 홈 있는 철퇴 베이스로 교체(34:33).'
              +(' 4장 섬 보상 철퇴가 한손이면 꼭 확인(48:23).' if act4 else '')+' 옵션: +근접 스킬 레벨 우선(방패의 벽은 근접 스킬).'),
         dict(slot='Weapon 2',name='Armour shield / 방어도 방패',condition='방어도 최우선: 방패의 벽 피해 = 방패 방어도 15당 물리 피해 추가(PoB). 방패는 계속 바꾸며 올립니다(별이슬 25:20 · 29:13). 방패가 약하면 보스가 오래 걸립니다(25:35'
              +(' · 4장 디아모르 석화 패턴을 두 번 보면 방패가 약한 것, 46:13~46:31' if act4 else '')+(' · 갈라임 1:01:04' if inter else '')+'). 방어구 장인의 고철로 품질. '
              '룬은 철 룬(방어도 % 증가) — 하위 철 룬(1장 11:24 · 2장 거신 석굴 23:53)'+(', 4장 눈먼 짐승의 상위 룬은 상위 철 룬으로 받기(43:19 · 45:14)' if not act3 else '')
              +('. 막간 뱃사공에게서 룬을 전부 삽니다(59:05). 방패가 약하면 바꾸고, 쓰던 방패는 분해해 방어구 장인의 고철을 돌려받습니다(1:04:03~1:04:15).' if inter else '.')),
         body,
         dict(slot='Ring 1',name='Fire resistance ring / 화염 저항 반지',condition=ring),
         dict(slot='Ring 2',name='Fire resistance ring / 화염 저항 반지',condition='반지 1과 같은 기준.'),
         dict(slot='Amulet',name='Life/resistance amulet / 생명력·저항 목걸이',condition=('3장 보라 몬스터가 목걸이 확정 드롭(별이슬 33:12~33:18). ' if act3 else '4장 진주 목걸이 퀘스트는 목걸이가 좋으면 생략(46:07~46:13). ' if act4 else '막간에서 뱀 몹이 주는 바리아 2개 중 하나는 목걸이 소원(별이슬 1:02:26). ')+'생명력 · 부족한 저항 · 힘.'),
         dict(slot='Helmet',name='Defensive helmet / 방어 투구',condition=('3장 야영지 희귀 투구 확정(별이슬 33:12). ' if act3 else '')+'생명력 · 부족한 저항 · 방어도.'),
         dict(slot='Gloves',name='Rare gloves / 희귀 장갑',condition=('3장 밀림 유적 야영지 희귀 장갑 확정(별이슬 29:42~29:48). ' if act3 else '')+'+근접 스킬 레벨이 붙으면 최우선(방패의 벽은 근접 스킬, 탱정 저장본 장갑 +2) > 방어도 > 저항.'),
         dict(slot='Belt',name='Rare belt / 희귀 허리띠',condition=('3장 희귀 허리띠 퀘스트(별이슬 30:07). 0.5.5에서 이 퀘스트는 마틀란 수로 쪽으로 옮겨졌습니다(별이슬 업데이트 1:19~1:24). ' if act3 else '')+'화염·번개 저항 > 방어도 > 생명력.'),
         dict(slot='Boots',name='Movement speed boots / 이동 속도 장화',condition=('3장 야영지 희귀 신발 확정(별이슬 32:19). ' if act3 else '')+'이동 속도 옵션이 나올 때까지 감정(별이슬 2:40~2:46) > 생명력 > 저항.'),
         dict(slot='Flask 1',name='Life flask / 생명력 플라스크',condition='플라스크를 꾸준히 올립니다(별이슬 41:30).'+(' 4장 정의의 여신상은 플라스크 생명력 회복 증가 선택(47:00).' if act4 else ''))]
    if act3:out.append(dict(slot='Charm 1',name='Thawing Charm / 해동 호신부',condition='3장 보상(별이슬 31:54).'))
    for e in out:e['status']='equipped_condition'
    return out

# ---- In-game text (user 9/22: ".build가 너무 구구절절"). Taengjung's own .build has no description, uniques by name, rares as base + numbered mods.
def nlist(*xs):return '\n'.join(f'{i}. {x}' for i,x in enumerate(xs,1))
GAME_NAME={'ref:3':'00 액트3 · 별이슬 트리','ref:4':'01 액트4 · 별이슬 트리','ref:Interlude':'02 막간 → 03 전환 · 별이슬 트리',
    1:'대안 · 40레벨 조기 전환',2:'03 맵 진입 · 흰 갑옷 (공통)',3:'04 자본 · 운명의 저항 → 황동 철갑',4:'05 자본 · 아홉꼬리 묶음',5:'06 자본 · 목 죄이는 명령',6:'07 자본 · 저자본 완성 (29d39)',7:'03+ 무자본 · 흰 갑옷 성장'}
def game_desc(key,s):
    b=s.get('budgets') or {}
    pts=f"포인트: 일반 {b.get('ordinary_points_required')} · 무기 특화 {b.get('weapon_specialization_capacity_required')} · 전직 {b.get('ascendancy_points_required')}" if b else ''
    L={'ref:3':['키타바 전직: 화염 저항 → 석탄 때기 → 대장장이의 걸작 → 탄탈룸 합금 → 녹아내린 상징','대장장이의 걸작부터 흰색 갑옷만','방패의 벽 세트 1 · 함성 세트 2','다음: 01'],
       'ref:4':['전직: 00과 같음','다음: 02'],
       'ref:Interlude':['3차 전직(60 진 바리아): 키타바에 대한 헌신 → 내열 처리',f"액트 끝나면 마을에서 03으로 한 번에 전환 (환불 {s.get('refunds')} · 추가 {s.get('adds')})"],
       1:['40레벨에서 바로 탱정 트리로 가는 대안 (기본 경로 아님)'],
       2:['02 → 03 트리 한 번에 전환 (마을)','흰색 방어도 갑옷 · 방패 방어도 1000 · 루비 반지 2개','저항 75% · 카오스 40~60%','포인트가 남으면 무기 세트 노드부터','다음: 무자본 03+ / 자본 04'],
       3:['운명의 저항 먼저','장비로 화염 저항 75% 채운 뒤 황동 철갑 (마을에서 걸작 분기 환불)','황동 철갑 바로 뒤 올로스의 결의','돈이 모이면 신성한 불꽃 셉터','다음: 05'],
       4:['한꺼번에: 아홉꼬리 + Desert Rune + 트리 재조정','영원한 격노 켜기 · 체크포인트에서 원소 약화로 생명력 깎기','생명력 플라스크는 빼도 되고 안 빼도 됨','다음: 06'],
       5:['목 죄이는 명령 착용 → 포위 노드','Frantic Fighter는 명중 확인 후','다음: 07'],
       6:['탱정 29d39 저장본 트리 그대로','06에서 더하기만'],
       7:['사는 것 없이 03 그대로 성장','무기 세트 노드부터 · 전직 8 (내부 층 → 키타바의 각인)','돈이 모이면 04 (일반 노드 환불 없음)']}[key]
    if key in ('ref:3','ref:4','ref:Interlude'):
        c=s['counts'];pts=f"포인트: 일반 {c['ordinary_common']} · 무기 세트 {c['weapon_set_1']}/{c['weapon_set_2']} · 전직 {s['paid']}"
    return '\n'.join(L+([pts] if pts else []))
SKILL_GAME={'Shield Wall':{'act':'세트 1 · 보스전: Magnified Area I → Concentrated Area',2:'세트 1',
                           3:'세트 1',4:'세트 1 · 늑대 호신부 생기면 Armour Break III → Concentrated Area',5:'세트 1 · 늑대 호신부 생기면 Armour Break III → Concentrated Area',6:'세트 1 · 늑대 호신부 생기면 Armour Break III → Concentrated Area','*':'세트 1'},
            'Infernal Cry':{'*':'세트 2 · 벽이 안 터지면'},'Fortifying Cry':{'*':'세트 2 · 지옥불 함성 대기 중일 때'},'Shockwave Totem':{'*':'셉터로는 못 씀'},
            'War Banner':{4:'정신력 모자라면 끄기',5:'정신력 모자라면 끄기',6:'정신력 모자라면 끄기'},'Eternal Rage':{'*':'캐릭터 59부터 · 켜 두기'},
            'Elemental Weakness':{'*':'체크포인트에서 3~4번 걸어 생명력 깎기'}}
def skill_game(active,key):
    m=SKILL_GAME.get(active,{})
    if key=='act':return m.get('act',m.get('*','')) if active in ('Shield Wall','Infernal Cry','Shockwave Totem') else ''
    return m.get(key,m.get('*',''))
ARMOUR_SHIELD=nlist('방어도 (고정 + %)','최대 화염 저항 · 화염 저항','생명력','기절 한계치')
def item_game(slot,key,e):
    """Rare/normal slot text; None = unique by name only."""
    act=key in ('ref:3','ref:4','ref:Interlude');a3,a4,ai=key=='ref:3',key=='ref:4',key=='ref:Interlude'
    if e.get('unique') and e.get('status')!='prepare_not_equip':return None
    if slot=='Weapon 1':
        if act:return '한손 철퇴 · 무기 세트 1·2 같은 무기\n'+nlist('+근접 스킬 레벨')
        return ('희귀 철퇴 → 신성한 불꽃 셉터\n'+nlist('+근접 스킬 레벨')+'\n셉터면 충격파 토템 불가') if 3<=key<=5 else '희귀 철퇴\n'+nlist('+근접 스킬 레벨','함성 재사용 대기 회복')
    if slot=='Weapon 2':
        if act:return '방어도 방패\n'+nlist('방어도','화염 저항','생명력')+'\n룬: 철 룬'+('\n눈먼 짐승 상위 룬 → 상위 철 룬' if a4 else '\n뱃사공 룬 전부 구매' if ai else '')
        return '방어도 방패\n'+ARMOUR_SHIELD+('\n목표: 방어도 1000 (T15)' if key in (1,2,7) else '')
    if slot=='Body Armour':
        if a3:return '방어도 갑옷 → 대장장이의 걸작 찍으면 흰색만\n'+nlist('방어도','화염 저항')
        return '흰색 방어도 갑옷 (대장장이의 걸작)\n품질 · 룬'
    if slot in ('Ring 1','Ring 2'):
        extra='' if slot=='Ring 2' else ('\n화산 땅굴: 번개 희귀 몹 → 화염 희귀 몹 순서' if a4 else '\n뱀 몹 바리아 소원 1개' if ai else '')
        return '루비 반지\n'+(nlist('화염 저항','생명력') if act else nlist('화염 저항','화염 · 카오스 저항','생명력'))+extra
    if slot=='Amulet':return '희귀 목걸이\n'+nlist('생명력','부족한 저항','힘')+('\n뱀 몹 바리아 소원 1개' if ai else '\n자본: 운명의 저항' if key==2 else '')
    if slot=='Helmet':return nlist('생명력','저항','방어도')
    if slot=='Gloves':return nlist('+2 근접 스킬 레벨' if not act else '+근접 스킬 레벨','방어도','저항')
    if slot=='Belt':return nlist('화염 · 번개 저항','방어도','생명력')
    if slot=='Boots':return nlist('이동 속도','생명력','저항')
    if slot=='Flask 1':return '생명력 플라스크'+('\n정의의 여신상: 생명력 회복' if a4 else '')
    if slot=='Charm 1':return '해동 호신부'
    return e['name'].split(' / ')[-1]
def pob_items(root):
    """Taengjung's saved items as his own .build shows them: uniques by name, rares as base + numbered explicit mods."""
    items={it.get('id'):(it.text or '') for it in root.findall('Items/Item')};act=root.find('Items').get('activeItemSet');out=[]
    for sl in next(s for s in root.findall('Items/ItemSet') if s.get('id')==act).findall('Slot'):
        lines=[l.strip() for l in items.get(sl.get('itemId'),'').strip().splitlines()]
        if sl.get('name') not in SLOTS or len(lines)<3:continue
        if lines[0]=='Rarity: UNIQUE':out.append(dict(slot=sl.get('name'),unique=lines[1]));continue
        k=next(i for i,l in enumerate(lines) if l.startswith('Implicits:'));n=int(lines[k].split(':')[1])
        mods=[l for l in lines[k+1+n:] if l and not l.startswith('{') and l!='Corrupted']
        out.append(dict(slot=sl.get('name'),text=lines[2]+'\n'+nlist(*mods)))
    return sorted(out,key=lambda e:list(SLOTS).index(e['slot']))
def terse(native,key,s):
    native['name']=GAME_NAME[key];native['description']=game_desc(key,s)
    for p in native['passives']:p.pop('additional_text',None)
    for ns,gr in zip(native['skills'],s['skill_groups']):
        t=skill_game(gr['active'],'act' if str(key).startswith('ref:') else key)
        if t:ns['additional_text']=t
        else:ns.pop('additional_text',None)
        for x in ns.get('support_skills',[]):x.pop('additional_text',None)
    slots=[]
    source=pob_items(roots['29d39']) if key==6 else [dict(slot=e['slot'],e=e) for e in s['equipment'] if e['slot'] in SLOTS]
    for e in source:
        inv,x=SLOTS[e['slot']]
        if key==6:
            slots.append(dict(inventory_id=inv,slot_x=x,slot_y=0,unique_name=e['unique']) if 'unique' in e else dict(inventory_id=inv,slot_x=x,slot_y=0,level_interval=[1,100],additional_text=e['text']));continue
        t=item_game(e['slot'],key,e['e'])
        slots.append(dict(inventory_id=inv,slot_x=x,slot_y=0,unique_name=e['e']['unique']) if t is None else dict(inventory_id=inv,slot_x=x,slot_y=0,level_interval=[1,100],additional_text=t))
    # Lineage supports never show in the in-game gem recommendations (those live in uncut-gem crafting; lineage gems are not cut),
    # so the shield slot hover, which the planner does show, lists them.
    LK={'Shield Wall':'방패의 벽','Infernal Cry':'지옥불 함성','War Banner':'전쟁 깃발'}
    lines=[]
    for gr in s['skill_groups']:
        for l in gr.get('lineage',[]):
            if l['in_slots']:lines.append(f"· {LK[gr['active']]}: {l['ko']} (젬 칸에 있음)")
            elif l['name']=="Kaom's Madness":lines.append('· 5칸 생기면 방패의 벽: 카옴의 광기 (안의 성채 필요)')
            else:lines.append(f"· 살 수 있으면 {LK[gr['active']]}: {l['ko']} ({l['hint']})")
    if lines:
        shield=next(x for x in slots if x['inventory_id']=='Offhand1')
        head=shield.get('additional_text','')
        shield['additional_text']='\n'.join(([head,''] if head else [])+['혈통 젬 (캐릭터 65 · 젬 추천엔 안 뜸)',*lines])
        shield.setdefault('level_interval',[1,100])
    native['inventory_slots']=slots
    return native
REF_STAGES=[('3','00','byeolisul-act3','00_별이슬액트3_지금.build','별이슬 액트3 · 지금 트리',True),
            ('4','01','byeolisul-act4','01_별이슬액트4.build','별이슬 액트4',True),
            ('Interlude','02','byeolisul-interlude','02_별이슬막간_맵진입전환출발.build','별이슬 막간 · 맵 진입 때 03으로 전환',False)]
def spec_mapping(root,title):
    spec=next(s for s in root.findall('Tree/Spec') if s.get('title')==title)
    all_ids=ids(spec.get('nodes'));assert START in all_ids
    ws={w:ids(spec.find('WeaponSet'+str(w)).get('nodes') if spec.find('WeaponSet'+str(w)) is not None else '') for w in (1,2)}
    m={n:1 if n in ws[1] else 2 if n in ws[2] else 0 for n in all_ids-{START} if not nodes[n].get('ascendancyName')}
    assert connected(m)
    return m
def make_reference_stages(target):
    """00~02 = 별이슬골짜기 0.5.5 act trees (Taengjung: acts follow 별이슬, 9/20 live P1 0:07:12). 02 carries the town respec into 03."""
    root=ET.parse(REF_POB).getroot();out=[]
    for title,num,sid,filename,label,act in REF_STAGES:
        start=spec_mapping(root,title);c=collections.Counter(start.values())
        paid=spec_paid_asc(root,title);asc_nodes=kitava_prefix(paid)
        ops=transition_ops(start,target) if not act else []
        refunds=sum(o['action']=='refund' for o in ops);adds=len(ops)-refunds;kept=sum(target.get(n)==w for n,w in start.items())
        groups,skipped=reference_skills(root,act);source_groups=[dict(active=g['active'],supports=g['supports']) for g in groups];groups=act_core(groups)
        desc=(f'탱정은 액트를 별이슬골짜기 방패벽 액트 가이드로 하라고 했습니다(9/20 방송 1부 0:07:12 · 2부 1:06:44). 이 파일은 별이슬 0.5.5 PoB(5vFvXihk9x0q)의 트리 "{title}"입니다.\n'
          f'일반 {c[0]} · 무기 세트 1 {c[1]} · 무기 세트 2 {c[2]}.'+(' 게임 화면의 무기 세트 포인트 10/10과 같아 지금 트리로 추정(확인 안 됨).' if title=='3' else '')+'\n'
          '별이슬 원본 전직은 워브링어입니다. 탱정 보정대로 키타바를 고른다는 전제입니다.\n'+ASC_ORDER+ASC_PLACED.format(paid=paid)+'\n'
          +(f'액트가 끝나 맵에 들어갈 때 마을에서 03(탱정 1일차)으로 전환: 환불 {refunds} → 추가 {adds}, 겹치는 노드 {kept}개. 번호 순서는 HTML "02 → 03 전환"에 있습니다.\n' if not act else '액트 동안은 별이슬 가이드 순서대로 진행하세요. 탱정 세팅(03)은 액트가 끝난 뒤입니다.\n')
          +ACT_GEAR_NOTE+'\n'
          +ACT_LINEAGE_NOTE+'\n'
          +'1~100은 표시 호환 범위이며 습득 레벨이 아닙니다.')
        gear=ref_equipment(title)
        native=dict(name=f'{num} {label} · 탱정 경로',author='별이슬골짜기 원본 트리 / Pathcraft 경로 안내',link='https://pobb.in/5vFvXihk9x0q',ascendancy='Warrior3',description=desc,passives=[],skills=[],inventory_slots=[])
        order={o['numeric_id']:i for i,o in enumerate(ops,1) if o['action']=='refund'}
        for n,w in sorted(start.items()):
            tail=(f'03 전환 때 환불(순서 {order[n]}).' if n in order else '03에서도 유지.') if not act else '별이슬 액트 노드.'
            native['passives'].append(dict(id=nodes[n]['stringId'],weapon_set=w,level_interval=[1,100],additional_text='별이슬 트리 '+title+' · '+nodes[n]['name']+'. '+tail))
        for eq in gear:
            inv,x=SLOTS[eq['slot']]
            native['inventory_slots'].append(dict(inventory_id=inv,slot_x=x,slot_y=0,level_interval=[1,100],additional_text=eq['name']+'\n'+eq['condition']))
        for n in asc_nodes:
            native['passives'].append(dict(id=nodes[n]['stringId'],weapon_set=0,level_interval=[1,100],additional_text=ASC_NOTE[n]))
        for g in groups:
            native['skills'].append(dict(id=g['gems'][0]['id'],level_interval=[1,100],additional_text=g['condition'],support_skills=[dict(id=x['id'],level_interval=[1,100],additional_text=x['name']) for x in g['gems'][1:]]))
        native=terse(native,'ref:'+title,dict(budgets=None,counts=dict(ordinary_common=c[0],weapon_set_1=c[1],weapon_set_2=c[2]),paid=paid,refunds=refunds,adds=adds,skill_groups=groups,equipment=gear))
        dump(ROOT/'native'/filename,native)
        out.append(dict(id=sid,equipment=gear,gear_note=ACT_GEAR_NOTE,lineage_note=ACT_LINEAGE_NOTE,ascendancy_nodes=[node(n) for n in [ASC_START,*asc_nodes]],ascendancy_order=ASC_ORDER+ASC_PLACED.format(paid=paid),byeolisul_paid_ascendancy=paid,display_number=int(num),label=f'{num} {label}',spec_title=title,source=f'별이슬골짜기 0.5.5 액트 PoB https://pobb.in/5vFvXihk9x0q (linked_update_pob.xml, Tree/Spec {title})',source_sha256=sha(REF_POB),
          source_ascendancy='Warbringer (Warrior2); Taengjung correction: choose Kitava',native_file='taengjung_progression/native/'+filename,native_sha256=sha(ROOT/'native'/filename),
          counts=dict(ordinary_common=c[0],weapon_set_1=c[1],weapon_set_2=c[2],kept=kept,refunds=refunds,allocations=adds),
          passives=[node(n,w) for n,w in sorted(start.items())],skill_groups=groups,source_skill_groups=source_groups,skipped_skill_groups=skipped,transition_to_03=ops,
          evidence=('In-game weapon set points observed 10/10 at level 40 match spec 3 (set1 10 / set2 10); actual tree not exported.' if title=='3' else 'Act route per Taengjung 9/20 live; switch at map entry.')))
    return out


# 00~02: the user holds 3 Greater Jeweller's Orbs and level 4/5 uncut supports, so the core act skills take Taengjung's own support sets.
# 별이슬's other groups keep their supports: in 0.5 only lineage supports are limited to one copy (PoB CalcSetup MaxLineageCount).
ACT_CORE={'Shield Wall':(['Rapid Attacks II','Fire Attunement','Armour Break III','Magnified Area I'],'cafe208 + 별이슬',
            '상위 세공사의 오브로 4칸: 탱정 카페 답변 9/17(글 208)의 Rapid Attacks II · Fire Attunement · Armour Break III + 별이슬의 Magnified Area I(보스에선 Concentrated Area로 바꿈, 별이슬 24:04~24:16). Rapid Attacks II · Armour Break III는 레벨 4 미가공 보조 젬. 03부터는 Magnified Area I 자리에 Concentrated Area(탱정).'),
          'Infernal Cry':(['Raging Cry','Tireless','Enraged Warcry I'],'xml-28509','탱정 28509(흰색 갑옷 시절) 구성. Enraged Warcry I은 레벨 4 미가공 보조 젬. 함성은 세트 2(별이슬 28:27).'),
          'Shockwave Totem':(['Urgent Totems III','Hardy Totems II','Rapid Attacks III'],'xml-28509','탱정 28509 구성: Urgent Totems III · Hardy Totems II(레벨 4) · Rapid Attacks III(레벨 5) 미가공 보조 젬.')}
def act_core(groups):
    out=[]
    for g in groups:
        if g['active'] in ACT_CORE:
            sup,src,cond=ACT_CORE[g['active']]
            out.append(group(g['active'],sup,src,cond+(' '+TOTEM_WEAPONS+'.' if g['active']=='Shockwave Totem' else ''),g['weapon_set']));continue
        out.append(g)
    return out

ZERO_EXCLUDE=re.compile(r'Surrounded|Low Life')
def sockets_of(groups):
    s=dict(groups=[dict(active=g['active'],supports=len(g['supports']),lesser_from_base=int(len(g['supports'])==3),greater_from_base=int(len(g['supports'])==4),perfect_from_base=int(len(g['supports'])==5)) for g in groups])
    for tier in ['lesser','greater','perfect']:s[tier+'_from_base']=sum(x[tier+'_from_base'] for x in s['groups'])
    assert s['greater_from_base']<=3 and s['lesser_from_base']<=29 and s['perfect_from_base']==0
    return s
def make_zero_stage(stages):
    """03+ 무자본(zero2hero): 03's white-armour Masterwork setup, no purchases. Tree = 29d39 (07) minus nodes that only work with
    Constricting Command (Surrounded) or Cat O' Nine Tails (Low Life), added onto 03 only. Ascendancy = 03 + Internal Layer + Kitavan Engraving."""
    s03,s07=stages[1],stages[5]
    base={p['numeric_id']:p['weapon_set'] for p in s03['passives']};full={p['numeric_id']:p['weapon_set'] for p in s07['passives']}
    excluded=sorted(n for n in full if n not in base and ZERO_EXCLUDE.search(' '.join(nodes[n].get('stats',[]))))
    pending=[n for n in full if n not in base and n not in excluded]
    mapping=dict(base);operations=[]
    while True:
        cand=[n for n in pending if n not in mapping and connected({**mapping,n:full[n]})]
        if not cand:break
        n=min(cand,key=lambda n:(0 if full[n] in (1,2) else 1,n));mapping[n]=full[n]
        operations.append(dict(action='allocate',numeric_id=n,stringId=nodes[n]['stringId'],name=nodes[n]['name'],weapon_set=full[n],both_sets_connected=True))
    unreachable=sorted(set(pending)-set(mapping))
    asc_prev={p['numeric_id'] for p in s03['ascendancy_nodes']};asc=asc_prev|{110,60913};assert reach(asc,ASC_START)==asc
    asc_ops=[dict(action='allocate',numeric_id=n,name=nodes[n]['name'],paid=True) for n in (110,60913)]
    groups=skill_groups(7);b=budget(mapping,asc)
    eq=equipment(2)
    for e in eq:
        if e['slot']=='Amulet':e.update(name='Usable life/resistance amulet / 생명력·저항 목걸이',status='equipped_condition',condition='생명력 · 부족한 저항 · 힘. 무자본: 운명의 저항은 자본 버전(04)에서.')
    surround=sum(1 for n in excluded if 'Surrounded' in ' '.join(nodes[n]['stats']));lowlife=len(excluded)-surround
    conditions=['무자본(리그 스타터 · zero2hero) 버전: 고유 장비·혈통 젬을 사지 않고 03의 흰색 갑옷 + 대장장이의 걸작 구성 그대로 키웁니다. 돈이 모이면 04(운명의 저항)부터 자본 버전으로 넘어가면 됩니다 — 여기서 더 찍은 일반·무기 세트 노드는 모두 07 트리에 있어 환불할 필요가 없고, 전직은 04에서 대장장이의 걸작 분기 전체(여기서 찍은 내부 층 · 키타바의 각인 포함)를 환불합니다.',
        f'트리: 탱정 29d39(07)에서 포위 노드 {surround}개와 저생명력 노드 {lowlife}개를 뺀 Pathcraft 구성입니다(탱정이 만든 트리 아님). 포위는 주변 적 5마리 이상(PoB)이고 목 죄이는 명령이 필요한 적 수를 4 줄여 줍니다 — 탱정은 "이 장비를 구매하시기 전까지는 포위 관련 노드를 절대 미리 찍지 마셔야" 한다고 했습니다(8/17 영상 10:28~10:34). 저생명력은 아홉꼬리 묶음(05)의 조건입니다. 03에서 더하기만 하며, 포인트가 생기는 대로 무기 세트 노드(세트 1 공격 속도 · 세트 2 함성)부터 — 탱정 9/20 1부 1:19:52 · 1:20:32.',
        '전직: 03의 유료 6 + 4차 전직 내부 층 → 키타바의 각인(최대 생명력 15%) = 유료 8(탱정 8/17 영상 7:00~7:15).',
        '스킬: 미가공 보조 젬만, 혈통 젬 없음. 상위 세공사의 오브 3개 → 4칸 스킬은 최대 3개(여기선 방패의 벽 1개), 완벽한 세공사의 오브 0개 → 5칸 없음. '+'일반 보조 젬은 여러 스킬에 겹쳐 써도 됩니다 — 0.5 PoB는 혈통 젬만 종류별 1개로 막고(0.4.0 패치노트 Solus Ipse도 혈통 젬만 언급), 탱정 저장본도 일반 보조를 겹쳐 씁니다.',
        '장비: 03과 같은 흰색 방어도 갑옷 + 희귀 장비, 고유 장비 없이. 탱정의 흰색 갑옷 시절 저장본 28509(레벨 90)도 고유 장비는 운명의 저항 · The Hollow Mask 두 개뿐이었습니다.',
        '포인트는 실제로 얻은 만큼만 순서대로. 방패 방어도 · 저항 · 생명력이 계속 조건입니다.']
    filename='03무자본_흰갑옷성장_구매없이.build';label='흰색 갑옷 성장(구매 없이)'
    stage=dict(id='taengjung-zero-growth',label=label,index=7,track='zero',display_number=3,display_label='03+',creator='탱정 / Taengjung',kind='pathcraft_source_adaptation',native_file='taengjung_progression/native/'+filename,
        source_claims=['xml-28509','normal-asc','prefix-adaptation','xml-29d39'],conditions=conditions,budgets=b,passives=[node(n,w) for n,w in sorted(mapping.items())],ascendancy_nodes=[node(n) for n in sorted(asc)],
        skill_groups=groups,skills=groups,equipment=eq,socket_budget=sockets_of(groups),
        excluded_nodes=[dict(numeric_id=n,name=nodes[n]['name'],stats=nodes[n].get('stats',[])) for n in excluded],unreachable_without_excluded=[dict(numeric_id=n,name=nodes[n]['name']) for n in unreachable],
        eligibility=dict(max_selected_gem_min_character_level=max(x['min_character_level'] for g in groups for x in g['gems'])),
        diff_from_previous=dict(ordinary_additions=len(operations),ordinary_refunds=0,set_reassignments=0,ascendancy_paid_refunds=0,ascendancy_paid_additions=2,free_ascendancy_removed=[],operations=operations,ascendancy_operations=asc_ops,interpretation='From 03; additions only, weapon-set nodes first. Connection-keeping witness, not an author click order.'))
    stage['weapon_set_roles']=weapon_set_roles(mapping,groups);stage['resistance_plan']=resistance_plan(2);stage['gear_note']=GEAR_NOTE;stage['swaps']=[]
    native=dict(name='03+ [무자본] '+label+' · 탱정',author='탱정 원문 / Pathcraft 무자본 구성',link='https://poe.ninja/poe2/pob/29d39',ascendancy='Warrior3',
        description='\n'.join(conditions)+f'\n포인트: 일반 {b["ordinary_points_required"]}, 무기특화 {b["weapon_specialization_capacity_required"]}, 유료 전직 {b["ascendancy_points_required"]}.\n'+weapon_set_text(stage['weapon_set_roles'])+'\n'+'\n'.join(stage['resistance_plan'])+'\n'+GEAR_NOTE+'\n1~100은 표시 호환 범위이며 실제 습득/장착 레벨이 아닙니다.',passives=[],skills=[],inventory_slots=[])
    order={o['numeric_id']:i for i,o in enumerate(operations,1)}
    asc_note={110:'4차 전직 ①: 내부 층 — 받는 치명타 추가 피해 100% 감소. 탱정 8/17 영상 7:00.',60913:'4차 전직 ②: 키타바의 각인(Kitavan Engraving) — 최대 생명력 15%. 탱정 8/17 영상 7:08~7:15. 같은 한국어 이름의 영광 60% 노드가 아님.'}
    for p in stage['passives']+stage['ascendancy_nodes']:
        n=p['numeric_id']
        if n==ASC_START:continue
        note=asc_note.get(n) or (('탱정 저장본 전직 노드 · ' if p['kind']=='ascendancy' else '03과 같음 · ' if n in base else f'무자본 성장 순서 {order[n]} · ')+p['name']+'.')
        native['passives'].append(dict(id=p['stringId'],weapon_set=p['weapon_set'],level_interval=[1,100],additional_text=note))
    for g in groups:
        native['skills'].append(dict(id=g['gems'][0]['id'],level_interval=[1,100],additional_text=g['condition']+f' 실제 기본 젬 최소 캐릭터 {g["gems"][0]["min_character_level"]}. 무기세트{g["weapon_set"]}.',support_skills=[dict(id=x['id'],level_interval=[1,100],additional_text=x['name']+(f' · 미가공 보조 젬 레벨 {x["crafting_level"]} 이상에서 만듦(드롭 레벨 {x["uncut_support_drop_level"]}).' if x['crafting_level']>1 else '')) for x in g['gems'][1:]]))
    for e in eq:
        if e['slot'] not in SLOTS or e['status']=='prepare_not_equip':continue
        inv,x=SLOTS[e['slot']];assert not e.get('unique')
        native['inventory_slots'].append(dict(inventory_id=inv,slot_x=x,slot_y=0,level_interval=[1,100],additional_text=e['name']+'\n'+e['condition']))
    native=terse(native,7,stage)
    dump(ROOT/'native'/filename,native);stage['native_sha256']=sha(ROOT/'native'/filename)
    return stage
def make():
    (ROOT/'sources').mkdir(exist_ok=True);(ROOT/'native').mkdir(exist_ok=True)
    protected=list(source_paths.values())+[CORPUS/'priority_taengjeong_kitava_shield_wall.md',CORPUS/'priority_pob_extracts.json']+list((CORPUS/'native_planner').rglob('*.build'))
    baseline=ROOT/'source_hashes.json'
    if not baseline.exists():dump(baseline,{str(p):sha(p) for p in sorted(set(protected))})
    for p,h in read(baseline).items():assert sha(Path(p))==h,('protected source changed',p)
    for k,p in source_paths.items():(ROOT/'sources'/('pob_'+k+'.xml')).write_bytes(p.read_bytes())
    source_rows=[dict(id='xml-'+k,file=str(p),local_copy='sources/pob_'+k+'.xml',sha256=sha(p),url='https://poe.ninja/poe2/pob/'+k) for k,p in source_paths.items()]
    for p in [TREE_PATH,DATA/'SkillGems.json',DATA/'BaseItemTypes.json',DATA/'AttributeRequirements.json',Path('D:/Pathcraft-AI/.tmp/skadoosh-simulation/pob2/src/Modules/CalcSetup.lua'),Path('D:/Pathcraft-AI/.tmp/skadoosh-simulation/pob2/src/Data/Skills/sup_str.lua')]:
        source_rows.append(dict(id=p.stem,file=str(p),sha256=sha(p)))
    dump(ROOT/'source_evidence.json',dict(claims=CLAIMS,sources=source_rows))
    targets=[7721,48006,32354,28542,18157,27687,24766,25711,59208]
    paths={n:path(n,common|(weapon[1] if n==27687 else set())) for n in targets}
    chosen={START}
    for n in targets[:5]:chosen.update(paths[n])
    prep={n:0 for n in chosen-{START}}
    growth=dict(prep)
    for n in paths[27687]:
        if n!=START:growth[n]=1 if n in weapon[1] else 0
    surround=dict(growth)
    for target in [24766,25711,59208]:
        for n in paths[target]:
            if n!=START:surround[n]=0
    defs=[
        ('current40','대안_40조기전환_탱정_일반갑옷준비.build','대안 · 40레벨 조기 전환 · 일반갑옷 준비',prep,[5852,14960,57959,9988,61039,9997],['normal-asc','pre-lowlife-supports','prefix-adaptation','manual-rage'],
         ['전사 / Smith of Kitava는 작업 가정입니다. 실제 클래스·전직과 획득 포인트를 확인하세요.','일반 37포인트는 레벨40 기본 39포인트 안에 들어가며 2포인트는 일부러 남깁니다. 퀘스트 보상 포인트는 가정하지 않았고, 실제 현재 트리는 모릅니다.','표시된 일반 갑옷 분기에는 유료 전직 4포인트가 필요합니다. 2포인트뿐이면 Coal Stoker만 두고 Masterwork 분기는 미루세요.','실제로 쓸 수 있는 일반 갑옷·희귀 철퇴·방어도 방패 기준입니다. 엔드게임 아이템 베이스를 복사하지 않았고 40레벨 필수 고유 아이템은 없습니다.']),
        ('normal-growth','03_탱정_1일차_흰갑옷_맵진입.build','탱정 1일차 · 흰색 갑옷 + Masterwork · 맵 진입',growth,[5852,14960,57959,9988,61039,9997,64962,25438],['normal-asc','defense-order','xml-28509','xml-285e2','prefix-adaptation'],
         ['일반 48 / 무기 특화 4. 포인트를 실제로 얻은 뒤에만 진행하세요. 캐릭터 레벨을 추정하지 않습니다.','유료 전직 6포인트: 저자 우선순위대로 카오스 방어도·상태 이상 보호 분기를 추가합니다.','운명의 저항 목걸이는 실제 요구치를 충족할 때까지 준비만 합니다. 저장본의 요구 레벨 56 예시를 40레벨에 착용하지 마세요.','방패의 벽 네 번째 보조 Concentrated Area는 상급 세공사의 오브 소켓과 실제 보조 젬이 있어야 합니다. 없으면 3보조를 유지하세요.']),
        ('defensive-entry','04_탱정_운명의저항_황동철갑.build','운명의 저항 → 황동 철갑 + 전직 → 올로스의 결의',growth,[5852,14960,57959,63401,48537,5386,22541],['defense-order','weapon-alternatives','xml-28604'],
         ['실제로 착용 가능한 운명의 저항 → 황동 철갑 순서입니다. 저장본 요구 레벨 56/58은 착용 자격 단서이며 전환 조건으로 충분하지 않습니다.','황동 철갑을 입기 전에 마을에서 Masterwork와 일반 갑옷 분기를 먼저 환불하고, 연결된 Coal Stoker·Forged in Flame·Heat of the Forge로 바꾸세요.','일반 갑옷 분기의 저항·물리→화염 전환·카오스 방어도가 빠집니다. 실제 저항 상한·생명력·피해 감소·회복·자원을 다시 확인하세요.','희귀 철퇴 + 직접 쓰는 함성·토템이 계속 핵심입니다. Sacred Flame·Purity of Fire·메타 발동·Olroth는 각각 조건이 따로 있는 선택 분기입니다.','저생명력 이전 방패의 벽 보조를 유지합니다. 이 단계는 아홉꼬리도 영원한 격노도 전제하지 않습니다.']),
        ('lowlife-entry','05_탱정_아홉꼬리_저생명력묶음.build','아홉꼬리 · 저생명력 묶음(플라스크 제거 · 저주 · 영원한 격노)',growth,[5852,14960,57959,63401,48537,5386,22541],['latest-bundle','xml-29d39','gem-minimums'],
         ['04의 방어 전환 묶음을 그대로 가져갑니다. 55레벨에 아홉꼬리만 차는 것은 이 전환이 아닙니다.','쓸 수 있는 아홉꼬리를 실제로 착용하고, 실제 받는 피해·비예약 생명력으로 저생명력 유지와 운명의 저항 회복을 확인하세요. 플라스크 회복은 상한을 넘을 수 있습니다.','영원한 격노는 캐릭터 59부터 젬 자격이 생깁니다. 실제 젬 능력치·정신력·활성 상태가 필요하며, 59레벨이라고 빌드 전체가 준비된 것은 아닙니다.','방패의 벽 보조를 Execute III / Clash / Rapid Attacks II로 바꾸는 것은 허리띠·회복·방어·격노/함성 구성과 동시에 합니다.','지옥불 함성 세트2: Raging Cry / Tireless / Enraged Warcry II. 실제 격노·자원 운용을 확인하세요.','투구 의존 노드는 아직 없습니다. Defiance 노드의 추가 80% 방어도/회피는 실제 저생명력일 때만 적용됩니다.']),
        ('conditional-growth','06_탱정_목죄이는명령_원형노드.build','목 죄이는 명령 착용 → 원형(포위) 노드',surround,[5852,14960,57959,63401,48537,5386,22541],['helmet-gate','latest-bundle','xml-28695','xml-29d39'],
         ['일반 57 / 무기 특화 4 / 유료 전직 6. 저장본 끝점까지 임의로 채우지 않습니다.','목 죄이는 명령을 실제로 착용·사용할 수 있어야 합니다. 저장본 요구 레벨 최신 38 / 과거 55는 베이스가 다른 단서입니다.','이제서야 Paranoia·Thrill of Battle·Frantic Fighter를 찍습니다. Frantic Fighter는 포위 시 명중 30% 감소가 있으니 실제 명중 확률을 확인한 뒤 찍으세요.','방패의 벽은 보조 3개 + Armour Break III(늑대 호신부 뒤엔 Concentrated Area). 안의 성채는 살 수 있을 때 Armour Break III 자리에.','저장본 97레벨·전체 트리·비싼 주얼·다섯 번째 Kaom 보조는 선택 참고 목적지이며, 빌드 전체의 고정 최소치로 해석하지 않습니다.'])]
    # If item gates are still unmet during interlude, continue the existing normal-body setup.
    # These are named benefits on source paths, not padding to a level-derived budget.
    core48=dict(growth)
    waiting=dict(growth);waiting_extensions=[]
    for target in [11392,13482]:
        route=path(target,common)
        additions=[n for n in route if n!=START and n not in waiting]
        ops=[]
        for n in additions:
            waiting[n]=0;assert connected(waiting)
            ops.append(dict(action='allocate',numeric_id=n,stringId=nodes[n]['stringId'],name=nodes[n]['name'],weapon_set=0,both_sets_connected=True))
        waiting_extensions.append(dict(target=target,name=nodes[target]['name'],stats=nodes[target]['stats'],added_nodes=len(additions),operations=ops,
          ordinary_points_required=budget(waiting,set())['ordinary_points_required'],weapon_specialization_capacity_required=4,
          condition='실제로 얻은 포인트만. 생명력·저항·자원이 계속 조건. Punctured Lung/Pile On 효과는 적 방어도를 실제로 완전히 파괴해야 적용.',
          retention='추가 노드는 모두 최신 저장본 공통 노드이며 표시 목표 61/70에 이미 포함됩니다. 환불 없이 유지하고, 이미 포함된 합계에 13을 다시 더하지 마세요.'))
    # The game files must expose the continuation too, not only a web appendix.
    # defs intentionally holds these same mapping objects; extend all later native targets.
    extension_nodes=set(waiting)-set(core48)
    growth.update(waiting)
    surround.update({n:0 for n in extension_nodes})
    # Stage 06 = the author's exact latest low-budget tree. 05 is a same-set subset, so 05 -> 06 only adds nodes.
    complete_asc={n for n in source_ids if nodes[n].get('ascendancyName')}
    complete={n:1 if n in weapon[1] else 2 if n in weapon[2] else 0 for n in source_ids-{START}-complete_asc}
    assert all(complete.get(n)==w for n,w in surround.items()),'05 must be a same-set subset of 29d39'
    defs.append(('lowbudget-complete','07_탱정_저자본완성_29d39.build','저자본 완성 · 탱정 29d39 전체 트리',complete,sorted(complete_asc),['latest-bundle','xml-29d39'],
         ['탱정 최신 저자본(29d39) 저장본의 트리 그대로입니다: 일반 118 / 무기 특화 24 / 유료 전직 8. 저장 캐릭터는 97레벨이며 진입 최소치가 아닙니다.',
          '06에서 환불 없이 더하기만 합니다. 일반 +48, 무기 특화 한도 4 → 24(07은 세트 1 노드 24 · 세트 2 노드 23), 유료 전직 +2. 포인트를 얻는 대로 채우세요.',
          "스킬은 06과 같습니다: 방패의 벽 보조 3개 + Armour Break III · 지옥불 함성 · 영원한 격노 · 전쟁 깃발 + 다레소의 열정. 안의 성채 · 우트레드의 의례는 살 수 있을 때. 저장본의 5칸째 카옴의 광기(완벽한 세공사의 오브 필요), Sacred Flame·Purity of Fire, Fire Spell on Hit 메타 등은 선택이며 HTML 참고 원본에서 확인하세요.",
          '무기 세트 2 노드는 함성 세트(세트 2)용입니다. 실제 무기 특화 포인트를 확인하세요.']))
    stages=[];previous={};previous_asc=set()
    for index,(key,filename,label,mapping,asc,claims,conditions) in enumerate(defs,1):
        conditions=list(conditions)
        if index==2:
            conditions[0]='일반 갑옷 성장 표시 목표: 일반 61 / 무기 특화 4. 연결된 중간 목표 48(방패) → 55(Molten Being) → 61(Punctured Lung·Pile On). 실제로 얻은 포인트만 배분하세요. 퀘스트 완료나 캐릭터 레벨을 추정하지 않습니다.'
        if index==2:
            conditions.insert(0,'맵 진입(액트 끝) 때 별이슬 막간 트리에서 마을에서 한 번에 전환합니다(탱정 9/20 방송 1부 0:07:12 · 1:16:19 "1일차 액트가 끝났다는 전제"). 전직은 액트에 이어 키타바에 대한 헌신 → 내열 처리까지(유료 6), 전직 포인트 8이면 내부 층 → 키타바의 각인(생명력 15%, 탱정 8/17 영상 6:35~7:15). 포인트가 61보다 많으면 07 트리의 세트 1 공격 속도 · 세트 2 함성 노드부터(1부 1:19:52 · 1:20:32 "무기세트 2는 여기를 챙깁니다"). 무기 세트 노드도 일반 포인트를 쓰고 세트당 한도가 있습니다. 다음 단계: 무자본이면 03+(구매 없이 성장), 자본이 있으면 04.')
        if 3<=index<=5:
            conditions.insert(0,'표시 목표는 일반 갑옷 성장 노드 13개를 유지한 일반 '+str(70 if index==5 else 61)+'포인트입니다. 진입 최소치가 아닙니다. 성장 노드를 아직 안 찍었다면 연결된 48포인트 핵심(포위 추가 시 57)으로도 됩니다. 이미 찍은 성장 노드는 환불하지 말고 유지하세요.')
        if index==5:
            conditions[1]='표시 목표 일반 70 / 무기 특화 4 / 유료 전직 6은 유지한 성장 분기를 포함합니다. 투구 확장 자체는 일반 9포인트이며, 임의로 채운 포인트나 빌드 최소치가 아닙니다.'
        assert connected(mapping)
        asc=set(asc);assert reach(asc,ASC_START)==asc
        groups=skill_groups(index);b=budget(mapping,asc)
        c=collections.Counter(gems[n]['GemColour'] for g in groups for n in g['supports'])
        sockets=dict(groups=[dict(active=g['active'],supports=len(g['supports']),lesser_from_base=int(len(g['supports'])==3),greater_from_base=int(len(g['supports'])==4),perfect_from_base=int(len(g['supports'])==5)) for g in groups])
        for tier in ['lesser','greater','perfect']:sockets[tier+'_from_base']=sum(x[tier+'_from_base'] for x in sockets['groups'])
        sockets['meaning']='Direct upgrades from base: Lesser sets3, Greater directly sets4 (NO Lesser prerequisite), Perfect sets5. Optional branches separate. Reuse upgrades on same gem; never charge all stages repeatedly.'
        sockets['cumulative_following_route_same_gems']=dict(Lesser=2,Greater=0 if index==1 else 1,Perfect=0,reason='Stage1 upgrades Shield Wall and Infernal Cry to3, stage2 upgrades same Shield Wall directly to4; later support replacements reuse that socket capacity.')
        assert sockets['greater_from_base']<=3 and sockets['lesser_from_base']<=29 and sockets['perfect_from_base']==0
        # Ordering is a graph witness, not an observed author click order.
        state=dict(previous);operations=[]
        assert all(mapping.get(n)==w for n,w in previous.items())
        while state!=mapping:
            candidates=[n for n,w in mapping.items() if n not in state and connected({**state,n:w})]
            assert candidates
            first_growth={o['numeric_id'] for o in waiting_extensions[0]['operations']}
            n=min(candidates,key=lambda n:(0 if n in core48 else 1 if n in first_growth else 2 if n in extension_nodes else 3,n));state[n]=mapping[n]
            operations.append(dict(action='allocate',numeric_id=n,stringId=nodes[n]['stringId'],name=nodes[n]['name'],weapon_set=mapping[n],both_sets_connected=True))
        asc_remove=previous_asc-asc;asc_add=asc-previous_asc
        # Ascendancy leaf refunds then root-outward additions also maintain connectivity.
        ast=set(previous_asc);asc_ops=[]
        while ast-asc:
            candidates=[n for n in ast-asc if reach(ast-{n},ASC_START)==ast-{n}]
            assert candidates;n=min(candidates);ast.remove(n);asc_ops.append(dict(action='refund',numeric_id=n,name=nodes[n]['name'],paid=n in paid_asc({n})))
        while asc-ast:
            candidates=[n for n in asc-ast if n==ASC_START or adj[n]&ast]
            assert candidates;n=min(candidates);ast.add(n);asc_ops.append(dict(action='allocate',numeric_id=n,name=nodes[n]['name'],paid=n in paid_asc({n})))
        stage=dict(id='taengjung-'+key,label=label,index=index,creator='탱정 / Taengjung',kind='pathcraft_source_adaptation',native_file='taengjung_progression/native/'+filename,
          source_claims=claims,conditions=conditions,budgets=b,passives=[node(n,w) for n,w in sorted(mapping.items())],ascendancy_nodes=[node(n) for n in sorted(asc)],
          skill_groups=groups,skills=groups,equipment=equipment(index),socket_budget=sockets,
          support_attribute_floor=dict(Strength=c[1]*5,Dexterity=c[2]*5,Intelligence=c[3]*5,interpretation='Conservative sum of all selected core support colours at5 each, across both sets; actual active-gem/item requirements may be higher. Local PoB CalcSetup.lua:2138-2140; no claim actual player meets these.'),
          eligibility=dict(current_player='unknown_actual_gear_gems_attributes_spirit_points',max_selected_gem_min_character_level=max(x['min_character_level'] for g in groups for x in g['gems']),native_interval='[1,100] is display compatibility only',actual_gem_levels='Use actually available eligible low-level gems, not saved19/20. Tooltip requirements control active-gem attributes; exact totals unknown without actual gem levels/items.',spirit='No fixed aura fit assumed; Eternal Rage is a core spirit gate in stages4/5; all other spirit groups optional.'),
          diff_from_previous=dict(ordinary_additions=len(operations),ordinary_refunds=0,set_reassignments=0,ascendancy_paid_refunds=len(paid_asc(asc_remove)),ascendancy_paid_additions=len(paid_asc(asc_add)),free_ascendancy_removed=sorted(asc_remove-paid_asc(asc_remove)),operations=operations,ascendancy_operations=asc_ops,interpretation='Recommended-stage diff only; actual current player tree unknown. No gold refund price invented.'),
          optional_branches=optional_branches(),waiting_for_equipment_growth=waiting_extensions if index>=2 else [],
          growth_subtargets=([dict(ordinary=48,meaning='Shield scaling, before optional long growth',passives=[node(n,w) for n,w in sorted(core48.items())]),dict(ordinary=55,meaning='Add Molten Being',added_operations=waiting_extensions[0]['operations']),dict(ordinary=61,meaning='Add Punctured Lung and Pile On',added_operations=waiting_extensions[1]['operations'])] if 2<=index<=5 else []),
          attributes=dict(travel_nodes=[n for n in sorted(mapping) if nodes[n]['name']=='Attribute'],choice='Pathcraft adaptation: choose actual Strength/Dexterity/Intelligence requirements first, then Strength; saved endpoint attribute choices are not imposed at40.'))
        if index==6:stage['entry_minimum']=dict(ordinary=70,weapon=4,ascendancy=6,meaning='05 target; 06 only adds nodes as points are earned')
        if 3<=index<=5:
            stage['ascendancy_alternative']=dict(paid_points=4,defer_nodes=[5386,22541],reason='표시된 유료 전직 6 중 2포인트는 Heat of the Forge로, 따로 조건이 있는 수동 발동 확장용 Fire Spell on Hit을 줍니다. 그 확장을 안 쓰면 이 2포인트를 미루고 Coal Stoker + Forged in Flame 연결 4포인트로 유지할 수 있습니다. 이 전직 스킬 때문에 Sacred Flame이 필요해지지는 않습니다.')
        display=DISPLAY[index];stage['display_number']=display
        native=dict(name=(f'{display:02d} ' if display else '')+('[공통] ' if index==2 else '[자본] ' if index>=3 else '')+label+' · 탱정',author='탱정 원문 / Pathcraft 조건부 진행 구성',link='https://poe.ninja/poe2/pob/29d39',ascendancy='Warrior3',description=('Pathcraft 표시본 — 트리와 전직은 탱정 최신 저자본 29d39 저장본 그대로, 스킬은 06과 같은 핵심만 넣었습니다.\n' if index==6 else 'Pathcraft 구성안 — 탱정 저자의 액트별 트리가 아닙니다. 일반 트리는 탱정 최신 29d39에서 연결된 일부, 03(과 대안) 전직의 일반 갑옷 분기는 과거 저장본 28509에서 가져왔습니다.\n')+'\n'.join(conditions)+f'\n포인트: 일반 {b["ordinary_points_required"]}, 무기특화 {b["weapon_specialization_capacity_required"]}, 유료 전직 {b["ascendancy_points_required"]}.\n1~100은 표시 호환 범위이며 실제 습득/장착 레벨이 아닙니다. 실제 능력치·젬·정신력·회복 조건을 확인하세요.\nSacred Flame 및 부여/메타 스킬은 선택 확장; 희귀 철퇴 기본 진행에서 필수 아님.',passives=[],skills=[],inventory_slots=[])
        if 2<=index<=5:
            native['description']+='\n장비 조건이 아직 안 되면 03 일반갑옷·기존 보조를 유지하세요. 이 파일 트리에 48→55→61 진행 노드가 실제 포함되며 해당 노드 설명에 구간을 표시했습니다. 48부터 Molten Being 경로 +7(총55), 이어 Punctured Lung/Pile On 경로 +6(총61). 퀘스트 완료나 특정 레벨을 가정하지 않고 실제 획득한 만큼만 배분하세요. 04/05는 이13포인트를 유지한61, 06은 유지한70 표시목표입니다. 전환 필수 최소포인트가 아니며 아직 성장분을 배분하지 않았다면 연결된48(포위추가57) 경로로 조건부 전환 가능합니다.'
        if 3<=index<=5:
            native['description']+='\n전직6 중 Heat of the Forge 경로2는 Fire Spell on Hit 부여 및 선택 메타 연결을 위한 투자입니다. 이 기능을 아직 사용하지 않으면 Fire Damage5386/Heat of the Forge22541 두 포인트를 보류하고 연결된 Coal Stoker+Forged in Flame 4포인트로 유지하세요.'
        stage['weapon_set_roles']=weapon_set_roles(mapping,groups);stage['resistance_plan']=resistance_plan(index)
        stage['gear_note']=GEAR_NOTE
        stage['swaps']=[x for x in LOWBUDGET_SWAPS if x['stage']==index]
        native['description']+='\n'+weapon_set_text(stage['weapon_set_roles'])+'\n'+'\n'.join(stage['resistance_plan'])+'\n'+GEAR_NOTE
        if stage['swaps']:native['description']+='\n이 단계 교체: '+' / '.join(f"{x['item']} = {x['swap']} ({x['how']})" for x in stage['swaps'])
        for p in stage['passives']+stage['ascendancy_nodes']:
            if p['numeric_id']==ASC_START:continue
            note=('탱정 저장본 전직 노드 · ' if p['kind']=='ascendancy' else '탱정 29d39 트리 노드 · ')+p['name']+'. '
            if p['numeric_id']==32354:note+='방어도/회피 20%는 항상, 추가 80%는 저생명력일 때만. '
            if p['numeric_id'] in (5386,22541):note+='Fire Spell on Hit 선택 연결을 사용할 때의 전직 투자. 아직 사용하지 않으면 이 경로2포인트 보류 가능. '
            if p['numeric_id'] in extension_nodes:
                ext=next(e for e in waiting_extensions if any(o['numeric_id']==p['numeric_id'] for o in e['operations']))
                order=next(i for i,o in enumerate(ext['operations'],1) if o['numeric_id']==p['numeric_id'])
                note+=f'일반갑옷 성장 {ext["ordinary_points_required"]}포인트 구간 / 연결순서 {order} / 실제 획득분만 배분, 다음 파일에도 유지. '
            elif index>=2 and p['numeric_id'] in core48:note+='48포인트 연결 준비 구간. '
            if 'Surrounded' in ' '.join(p['stats']) or p['numeric_id']==24766:note+='실착 투구/포위 조건 및 명중률 확인 후. '
            if p['name']=='Attribute':note+='실제 장비/젬 힘·민첩·지능 요구치를 우선 충족. '
            native['passives'].append(dict(id=p['stringId'],weapon_set=p['weapon_set'],level_interval=[1,100],additional_text=note))
        for g in groups:
            native['skills'].append(dict(id=g['gems'][0]['id'],level_interval=[1,100],additional_text=lineage_text(g)+g['condition']+f' 실제 기본 젬 최소 캐릭터 {g["gems"][0]["min_character_level"]}; 저장 고레벨 젬을 복사하지 마세요. 무기세트{g["weapon_set"]}.',support_skills=[dict(id=x['id'],level_interval=[1,100],additional_text=x['name']+' · 실제 보조 보유·소켓·능력치 확인.'+(f' 미가공 보조 젬 레벨 {x["crafting_level"]} 이상에서 만듦(게임 데이터 드롭 레벨 {x["uncut_support_drop_level"]}). 아직 못 구하면 구매하거나 지금 쓰는 보조 유지.' if x['crafting_level']>1 else '')) for x in g['gems'][1:]]))
        slots=SLOTS
        for eq in stage['equipment']:
            if eq['slot'] not in slots or eq['status']=='prepare_not_equip':continue
            inv,x=slots[eq['slot']]
            if eq.get('unique'):native['inventory_slots'].append(dict(inventory_id=inv,slot_x=x,slot_y=0,unique_name=eq['unique'],additional_text=eq['name']+'\n'+eq['condition']))
            else:native['inventory_slots'].append(dict(inventory_id=inv,slot_x=x,slot_y=0,level_interval=[1,100],additional_text=eq['name']+'\n'+eq['condition']))
        native=terse(native,index,stage)
        dump(ROOT/'native'/filename,native);stage['native_sha256']=sha(ROOT/'native'/filename)
        stages.append(stage);previous=mapping;previous_asc=asc
    reference_stages=make_reference_stages({int(p['id']):p['weapon_set'] for p in stages[1]['passives']})
    zero_track=[make_zero_stage(stages)]
    endpoint_asc={n for n in source_ids if nodes[n].get('ascendancyName')}
    endpoint={n:1 if n in weapon[1] else 2 if n in weapon[2] else 0 for n in source_ids-{START}-endpoint_asc}
    endpoint_budget=budget(endpoint,endpoint_asc)
    item_clues=[]
    for k,r in roots.items():
        for it in r.findall('./Items/Item'):
            text=it.text or '';lines=text.strip().splitlines();name=lines[1] if len(lines)>1 else ''
            if name in ['Constricting Command',"Cat O' Nine Tails",'Defiance of Destiny','The Brass Dome','Sacred Flame']:
                item_clues.append(dict(source='xml-'+k,name=name,base=lines[2],saved_level_req=(re.search(r'^LevelReq: (.+)$',text,re.M).group(1) if re.search(r'^LevelReq: (.+)$',text,re.M) else None),meaning='Saved item eligibility clue, not equip instruction or whole-build minimum.'))
    contract=dict(schema_version=1,active_route='taengjung_progression',stages=stages,sources=source_rows,source_claims=CLAIMS,
      user_constraints=dict(current_level=40,class_assumption='Warrior / Smith of Kitava, verify actual',currency=dict(Divine=5,Chaos=17,Exalted=61),jewellers=dict(Greater=3,Lesser=29,Perfect_declared=0),prices='unknown; no automatic conversion'),
      root_paths=[dict(target=n,name=nodes[n]['name'],individual_distance=len(paths[n])-1,ids=paths[n],not_combined_budget=True) for n in targets],
      item_eligibility_clues=item_clues,normal_growth_core48=[node(n,w) for n,w in sorted(core48.items())],waiting_for_equipment_growth=waiting_extensions,full_latest_optional=dict(native_file='native_planner/current-kitava-29d39.build',source='xml-29d39',budgets=endpoint_budget,saved_level=97,entry_requirement=False,additional_allocated_ids_beyond_stage5=len(set(endpoint)-set(surround)),additional_ordinary_budget_beyond_stage5=endpoint_budget['ordinary_points_required']-budget(surround,set())['ordinary_points_required'],description='Byte-frozen reference only. Its complete budget and saved level are not entry requirements; no instruction to rebuild to it.'),
      validation_scope='Graph, source memberships, exact counts, format, gem table eligibility, protected hashes and deterministic generation; not in-game DPS/survivability validation.',
      readiness=dict(current40='Usable contingent on actual gear, eligible gems/attributes, ordinary allocation and earned ascendancy. Base39 >= prefix37; no quest points needed for this prefix.',bundle='Dependency-consistent conditional recommendation; actual character readiness remains unverified.',install='Manager installs corrected five; this generator never writes game/canonical/ZIP/UI.'))
    contract['reference_stages']=reference_stages
    contract['zero_track']=zero_track
    contract['lowbudget_swaps']=LOWBUDGET_SWAPS
    dump(ROOT/'planner_contract.json',contract)
    pack=read(CORPUS/'planner_data/build_data.json')
    pack['taengjung_progression']=contract
    pack['active_route']='taengjung_progression'
    pack['active_stages']=stages
    dump(CORPUS/'planner_data/build_data.json',pack)
    (CORPUS/'planner_data/build_data.js').write_text('window.PATHCRAFT_BUILD_DATA = '+json.dumps(pack,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')
    dump(ROOT/'install_mapping.json',dict(files=[dict(source=s['native_file'],name=Path(s['native_file']).name,sha256=s['native_sha256']) for s in [*reference_stages,*[s for s in stages if s.get('display_number')],*zero_track]],destination='Manager controlled; no installation performed'))
    return contract

if __name__=='__main__':
    c=make()
    print(json.dumps([dict(id=s['id'],budgets=s['budgets'],socket_budget=s['socket_budget']) for s in c['stages']],ensure_ascii=False,indent=2))
