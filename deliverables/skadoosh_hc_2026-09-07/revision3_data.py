"""Broadcast-audited player stages. Importing this module never installs files."""
from pathlib import Path
import copy, json
from progression_core import read, state, entries, costs, legal
HERE=Path(__file__).resolve().parent
OUT=HERE/'revision3'
BASES={g['Id']:g['Name'] for g in read(HERE.parents[1]/'data/game_data_poe2/BaseItemTypes.json')}
IDS={v:k for k,v in BASES.items()}
KO={g['name']:g['title'].split(' - PoE2DB')[0] for g in read(HERE/'sources/gem_korean_titles.json')}
OLD={p.stem.split()[0]:read(p) for p in (HERE/'revision2/BuildPlanner').glob('*.build')}
def gem(name, supports=(), minimum=1):
    return {'id':IDS[name],'level_interval':[minimum,100], 'support_skills':[{'id':IDS[n],'level_interval':[65 if n=="Paquate's Pact" else 1,100]} for n in supports]}
def group(b,name):return next(g for g in b['skills'] if BASES[g['id']]==name)
NAMES=['01 시작 - 근접과 방패','02 충격파 토템 - 1차 전직까지','03 토템과 망치 - 2차 전직까지','04 타락 함성 - 마나 사용','05 전사 토템 - 혈마법 전환','06 파콰테 - 두 함성 운영','07 지도 성장 - 후기 목표']
def build_filename(build):
    # The client stores file:<absolute path> in active_builds. Preserve the
    # existing character's selected path independently of the displayed name.
    return '01 시작-근접 기초.build' if build['name']==NAMES[0] else build['name']+'.build'
BUILDS=[copy.deepcopy(OLD[c]) for c in ['01','03','05','07','08C','09','09']]
for b,n in zip(BUILDS,NAMES):
    b['name']=n;b['author']='Skadoosh / Pathcraft 한국어 방송 대조 v3'
    b['link']='https://poe.ninja/poe2/builds/forbiddenriteshc/character/ITheCon-2183/SkadooshShoutedHard'
    for g in b['skills']:
        g.pop('additional_text',None)
        for s in g.get('support_skills',[]):s.pop('additional_text',None)
    for n in b['passives']:n.pop('additional_text',None)
group(BUILDS[0],'Rolling Slam')['support_skills']=gem('Rolling Slam',['Brink I'])['support_skills']
group(BUILDS[1],'Shockwave Totem')['level_interval']=[6,100]
# This is a legal, lower-budget transition proposal. It is never labelled an
# exact reconstruction of every off-screen node at the creator's level 54.
proposal=read(HERE/'broadcast_audit/awt_transition_proposal.json')['passives']
BUILDS[4]['passives']=copy.deepcopy(proposal)
BUILDS[5]['passives']=copy.deepcopy(proposal)
BUILDS[4]['skills']=[gem('Ancestral Spirits'),gem('Purity of Fire',['Vitality II','Cannibalism II']),gem('Raise Shield'),
    gem('Purity of Fire',['Vitality I']),gem('Resonating Shield',['Rage I','Armour Demolisher I']),gem('Magma Barrier'),
    gem('Fortifying Cry',['Corrupting Cry I','Brutality II','Swift Affliction II','Efficiency II']),
    gem('Ancestral Warrior Totem',['Brutality II','Branching Fissures I'],52),gem('Earthshatter',minimum=23)]
BUILDS[5]['skills']=copy.deepcopy(BUILDS[4]['skills'])
group(BUILDS[5],'Fortifying Cry')['support_skills']=gem('Fortifying Cry',["Paquate's Pact",'Echoing Cry','Brutality II','Swift Affliction II'])['support_skills']
BUILDS[5]['skills'].append(gem('Seismic Cry',['Astral Projection','Efficiency II','Raging Cry']))
# Official native planner currently does not support meta gems. The inner active
# gem is a separate acquisition hint; both entries explain its manual placement.
awt=group(BUILDS[6],'Ancestral Warrior Totem')
awt['support_skills']=[s for s in awt['support_skills'] if BASES[s['id']]!='Earthshatter']
awt['level_interval']=[52,100]
BUILDS[6]['skills'].append(gem('Earthshatter',minimum=23))
DEFENCE_FIRST=['strength39_','strength38','strength36','life_regeneration25','life_regeneration17_','life_regeneration24','duelist_mercenary_notable1','armour47','armour48','armour46','armour49']
# Allocation order within the unchanged observed final node set prioritises
# connected recovery/armour branches for HC overlevelling.
BUILDS[6]['passives'].sort(key=lambda n:(DEFENCE_FIRST.index(n['id']) if n['id'] in DEFENCE_FIRST else 100))
DEFENCE_STATE=state(BUILDS[4])
for sid in DEFENCE_FIRST:DEFENCE_STATE[sid]=state(BUILDS[6])[sid]
assert legal(DEFENCE_STATE) and costs(DEFENCE_STATE)['ordinary']==80

ORIGINS=[
 '이번 리그 24레벨 실측의 근접 피해 시작 경로에서 추린 10점 목표. 첫날 02:13:30 화면의 근접 피해 시작과 대조했다. 초기 매 포인트의 정확한 클릭 순서는 복원하지 않았다.',
 '이번 리그 제작자 24레벨 공개 스냅샷의 트리·완성 연결. 처음 토템을 배우는 시점부터 이 완성 상태까지 한 파일에서 안내한다.',
 '이번 리그 제작자 43레벨 공개 스냅샷의 트리·완성 연결. 망치를 배운 뒤 2차 전직까지의 목표다.',
 '이번 리그 제작자 52레벨 공개 스냅샷의 트리·연결. 첫 함성 전환은 46레벨 실측 트리를 경유하도록 환불 순서에 넣었다.',
 '방송 기반 Pathcraft 전환안: 일반 69점·무기 특화 각 14점. 제작자는 실제 54레벨에 전환했지만 이 파일은 당시 전체 트리의 정확한 복제본이 아니다. 74레벨 실측의 연결된 하위 트리로 만들고 별도로 계산했다.',
 '방송에서 확인한 65레벨 파콰테·두 함성 운영을 05의 동일 트리에 적용한 Pathcraft 전환안. 65레벨 당시 전체 트리 실측본은 아니다.',
 '이번 리그 제작자 74레벨 공개 스냅샷의 패시브와 젬 연결 목표. 메타 젬은 공식 형식 제약 때문에 별도 획득 항목으로 표시한다. 75레벨 최신 조회에서는 일부 젬이 더 올라갔으므로 시점을 섞지 않았다.'
]
GATES=[
 '한손 철퇴와 방패로 시작한다. 몰려오는 강타에 목전 I, 뼈 박살에 충격파를 넣는다. 미가공 스킬 젬 3레벨을 얻고 캐릭터 6레벨·힘 14를 만족하면 바로 02로 간다. 10점 완성을 기다리지 않는다.',
 '충격파 토템은 젬 3레벨/캐릭터 6레벨부터 추가한다. 처음에는 보조 없이도 쓸 수 있고 과잉 I를 확보하면 넣는다. 과잉 I의 지속시간 50% 감폭 때문에 자주 다시 설치해야 한다. 이후 빠른 공격 I·긴급한 토템 I·포악함 II를 확보해 표의 완성 연결로 바꾼다. 1차 전직 응답받은 부름은 전직 후에만 찍는다. 29점은 사용 시작 조건이 아니다.',
 '미가공 스킬 젬 9레벨에서 대장간 망치를 얻고 요구 능력치를 맞춘다. 이 파일은 43레벨 시점의 성장 목표이므로 2차 전직과 상위 보조는 얻는 순서대로 추가한다. 2차 전직은 전쟁 소집자의 고함이다. 함성 전환 재료가 없으면 이 단계로 계속 진행한다.',
 '방어도 방패·보강하는 함성·타락시키는 비명 I·보조 소켓을 먼저 준비한다. 03 트리에서 지옥불 함성 대신 새 함성을 넣고 토템과 함께 시험한 뒤 패시브전환 문서대로 46레벨 실측 경유 트리와 이 52레벨 목표로 진행한다. 네 번째 소켓/효율 II는 나중에 추가해도 된다. 마나 플라스크를 유지한다. 65레벨 이상 캠페인에서도 준비가 안 됐으면 이 단계를 유지한다.',
 '선대의 전사 토템 젬 13레벨(캐릭터 52레벨·힘 92), 지면 분쇄, 성소 셉터 2개, 한손 철퇴, 방어도 방패를 먼저 준비한다. 모든 버프를 켠 뒤 토템 설치 전 양 세트 각각 정신력 300 이상이 있어야 4기를 유지한다. 일반 69점·특화 각 14점은 완성 배정이며 실제 환불 중 필요한 여유는 패시브전환 문서를 따른다. 마을에서 트리·무기·젬을 맞추고 혈마법은 마지막에 찍는다. 낮은 지역에서 설치/함성 뒤 생명력이 회복되는지 확인하고 부족하면 혈마법을 되돌린다.',
 '캐릭터 65레벨과 파콰테·메아리치는 함성·두 함성의 소켓을 확보한 뒤에만 시험한다. 보강하는 함성의 타락시키는 비명 I를 파콰테로, 효율 II를 메아리치는 함성으로 바꾼다. 지진 함성에 천체 투영·효율 II·격노의 함성을 넣는다. 05 트리를 그대로 쓰며 97점 완성은 필요하지 않다. 파콰테 함성은 한 번 쓰고 이동하며 반복을 기다린다. 비용이 누적되거나 플라스크 의존이 커지면 즉시 05 연결로 돌아간다.',
 '06 운영이 안정된 뒤 남는 포인트로 확장한다. 일반 97점·특화 각 22점은 후기 완성 목표이며 지도나 파콰테 진입 조건이 아니다. 긴급한 토템 III·포악함 III와 추가 소켓은 확보한 뒤 바꾼다. 세 번째 전직에서 나무 벽을 얻는다. Sadist’s Mercy는 67레벨 이후 선택 고유이며 없어도 05/06의 희귀 한손 철퇴로 진행한다.'
]
ROTATIONS=[
 '몰려오는 강타로 기절 준비 → 표시가 뜨면 뼈 박살 → 이동. 한손 철퇴+방패를 계속 사용한다.',
 '충격파 토템(II) 설치 → 지진(I)으로 요철 지대 → 이동. 기절 준비가 뜨면 뼈 박살. 토템은 방치해 영구 유지되는 스킬이 아니므로 사라지면 다시 설치한다.',
 '충격파 토템(II) 설치 → 지진(I)으로 지대 → 이동. 여유가 있을 때 대장간 망치(I), 함성(I)을 보조로 쓴다. 주력 토템 설치보다 망치 연타를 우선하지 않는다.',
 '희귀/보스는 충격파 토템(II)부터 설치 → 보강하는 함성(I) → 이동 → 남은 적과 마나 확인. 잡몹은 함성 한 번 후 이동한다. 토템이 살아 있는 동안 제자리 연타를 줄인다.',
 '선대의 전사 토템(II) 설치 → 보강하는 함성(I)으로 방패 세트 복귀·가시 폭발 → 이동. 만료된 토템만 보충한다. 지면 분쇄는 토템이 대신 쓰므로 수동 공격 버튼에 둘 필요가 없다.',
 '전사 토템(II) 설치 → 보강하는 함성(I) 한 번 → 이동하며 메아리 2회 기다리기. 사이에 지진 함성(I)으로 토템의 지면 분쇄 가시를 폭발시키고 격노를 얻는다. 파콰테를 넣은 보강하는 함성을 지진 함성처럼 연타하지 않는다.',
 '06과 같은 두 함성 운영. 토템이 가시를 만들면 지진 함성으로 터뜨린다. 보강하는 함성은 타락한 피/방어 보조와 메아리, 지진 함성은 직접 조작하는 가시 폭발을 맡는다. 토템 설치 뒤 I의 방패로 돌아간다.'
]
NEXT=['충격파 토템 확보 → 02','대장간 망치 확보 → 03','타락 함성 연결 시험 성공 → 04','정신력·장비·회복 준비 → 05','65레벨·파콰테 준비와 비용 시험 → 06','두 함성 운영이 안정되면 → 07','현재 캠페인/지도 진행에 맞춰 유지']
GATES[4]+=' 65레벨 이상에서 여유 점수가 있으면 패시브전환의 회복·방어 11점을 먼저 확장한다(총 80점). 이 확장에는 파콰테가 필요하지 않다. 실제 보유 포인트만 순서대로 사용한다.'
GATES[3]+=' 이 트리에는 마나 비용 일부를 생명력으로 바꾸는 노드도 있으므로 혈마법 전이라도 생명력이 소모된다. 마나와 생명력을 함께 확인한다.'
for i in range(len(GATES)):
    GATES[i]=GATES[i].replace('천체 투영',KO['Astral Projection']).replace('격노의 함성',KO['Raging Cry'])

def weapon_set(name, occurrence=0):
    if name=='Purity of Fire':return 1 if occurrence==0 else 2
    if name in ('Ancestral Spirits','Harbinger of Madness'):return 0
    if name=='Earthshatter':return 3
    if name in ('Shockwave Totem','Ancestral Warrior Totem'):return 2
    return 1

for b in BUILDS:assert legal(state(b))
