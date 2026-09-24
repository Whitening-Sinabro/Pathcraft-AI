"""Write Korean operating instructions from the actual revision-2 socket groups."""
from pathlib import Path
import copy, hashlib, json, re
from planner_presenter import render_planner, write_player_guides

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[1]
OUT=HERE/'revision2'
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,s): p.write_text(s,encoding='utf-8')
BASES={r['Id']:r['Name'] for r in read(REPO/'data/game_data_poe2/BaseItemTypes.json')}
KO={r['name']:r['title'].split(' - PoE2DB')[0] for r in read(HERE/'sources/gem_korean_titles.json')}
PLANS=read(HERE/'transition_operations_v2.json')
POOLS={p['to']:p for p in PLANS}
COUNTS={p['file']:p for p in read(HERE/'progression_v2.json')}
NINJA='https://poe.ninja/poe2/builds/forbiddenriteshc/character/ITheCon-2183/SkadooshShoutedHard'
SKADOOSH='https://mobalytics.gg/poe-2/builds/skadoosh-warbringer-leveling-41'
TREE=read(HERE/'sources/tree_0_5.json')
NODES={n['stringId']:n for n in TREE['nodes'].values() if 'stringId' in n}

def display(g):
    en=BASES[g['id']]
    return f'{KO[en]} ({en})'
def append(b,inv,text):
    slot=next((s for s in b['inventory_slots'] if s['inventory_id']==inv),None)
    if slot is None:
        slot={'inventory_id':inv,'slot_x':0,'slot_y':0,'level_interval':[1,100]}
        b['inventory_slots'].append(slot)
    old=slot.get('additional_text','').strip()
    slot['additional_text']=(old+'\n\n' if old else '')+text
def binding(w): return {0:'공통',1:'세트 I',2:'세트 II',None:'미할당'}[w]
def op_text(o):
    change=binding(o['from'])+' → '+binding(o['to'])
    return f"{o['action']} {o['name']} / {o['id']} ({change})"

GATES={
'01': '이번 리그 24레벨 실측에서 근접 피해 시작 경로를 뽑은 10점 목표. 기절 축적 우회는 제거했다. 1~10레벨 전체를 직접 관측한 트리는 아니다. 새로 시작할 때는 시작점과 연결된 노드부터 찍는다.',
'02': '충격파 토템·과잉 I·포악함 I과 각 2개 보조 소켓을 준비한다. 일반 포인트 25점, 세트별 4점이 최종 목표이므로 20레벨이 됐다고 완성을 강제하지 않는다. 토템 도입 자체는 이 트리 완성 전에도 가능하다.',
'03': '응답받은 부름 1차 전직 및 충격파 토템 보조 3칸을 준비한다. 02의 과잉 I를 빼면 별도 품질/장비 보정이 없는 경우 토템 한도가 1 줄어든다. 대신 50% 감폭 지속시간 제약이 사라지고 빠른 공격 I·긴급한 토템 I·포악함 II로 바뀐다. 낮은 지역에서 유지력과 처치 속도를 비교하고 부족하면 02의 토템 링크를 유지한다.',
'04': '대장간 망치와 요구 능력치를 준비한다. 화산 균열의 요철 지대 I, 지진의 유지되는 대지 I를 망치로 옮긴다. 몰려오는 강타는 이 실측부터 빠지므로 토템 중심으로 운영한다. 망치 보조에 쓸 인내 충전이 없으면 지진으로 지대를 만든다.',
'05': '전쟁 소집자의 고함 2차 전직을 마친 토템 유지 단계. 망치에 전쟁의 주먹 II, 마그마 장벽에 활력 I를 추가한다. 함성 젬이 없어도 이 단계로 계속 진행할 수 있다.',
'05A': '05의 트리와 장비를 그대로 두고 먼저 함성을 시험한다. 방어도 방패·보강하는 함성·타락시키는 비명 I 및 함성 보조 3칸을 준비한다. 지옥불 함성을 보강하는 함성으로 교체하고 포악함 II·재빠른 고통 II를 연결한다. 충격파 토템을 유지한다. 명상 II는 정신력과 능력치가 허용될 때 마그마 장벽에 추가한다. 이 단계에서는 패시브를 환불하지 않는다.',
'06': '05A에서 함성 피해와 자원 소모를 먼저 확인한다. 전환 중 총 일반 포인트 60점, 무기 세트 I 12점/II 14점의 사용 가능 한도가 필요하다. 이미 쓴 점수를 포함한 총량이며 60점 미사용을 뜻하지 않는다. 05A는 54점을 쓰므로 일반 여유 6점이 필요하다. 환불 16개 비용을 NPC에서 확인한 뒤 동봉 순서대로 작업한다. 완성 후 배정은 일반 55점/I 4점/II 13점이다. 점수가 모자라면 05A를 유지한다.',
'07': '06에서 트리를 확장한다. 함성 4번째 보조 소켓에 효율 II를 추가하고, 지진에는 유지되는 대지 II, 뼈 박살에는 효율 I를 추가한다. 소켓이나 젬이 없으면 이전 링크를 유지하며 트리만 늘린다. 토템 피해 노드 totems43은 세트 II 전용에서 공통으로 전환한다.',
'08': '07 이후 후반 전환 준비가 늦을 때의 선택 단계. 일반 포인트 67점 이후 남는 점수를 방어/재생 경로에 최대 14점 투자한다. 65레벨에 81점이 생긴다고 가정하지 않는다. 가능한 점수만 연결 순서대로 찍고 기존 함성·충격파 토템을 유지한다.',
'08A': '08B에 쓸 성소 셉터 2개·한손 철퇴·방어도 방패·AWT/지면 분쇄·보조 소켓과 정신력을 먼저 준비한다. 이 파일 배정은 일반 95점이지만 다음 두 단계의 핵심 노드까지 이어가려면 총 일반 97점, 양 세트 각각 22점의 사용 한도와 38개 환불 비용을 확보한 뒤 시작한다. 기존 함성·충격파 토템·마나 사용은 유지한다. 아직 선대의 유대와 혈마법을 찍지 않는다. 기존 토템의 특화가 줄어드는 준비 단계이므로 이 상태로 무리하게 사냥하지 않는다. 장비나 점수가 없으면 07/08에서 기다린다.',
'08B': '선대의 유대 1점만 추가한다. 세트 I는 셉터+방어도 방패, II는 한손 철퇴+셉터로 바꾼다. 양손 철퇴는 여기서 종료한다. 모든 버프를 켜고 토템을 놓기 전 남은 정신력이 양 세트 모두 75×목표 토템 수 이상인지 확인한다. AWT 보조 3칸에 지면 분쇄·긴급한 토템 I·포악함 II를 넣는다. 혈마법·파콰테 없이 마나로 먼저 시험한다. 셉터 교체로 함성의 유효 젬 레벨이 낮아지면 해결 후 전환한다.',
'08C': '08B의 공격·함성·정신력 운영이 되는 상태에서 혈마법 1점만 추가한다. 마나 비용이 생명력으로 바뀌므로 마을에서 1회 사용 비용을 확인하고 낮은 지역에서 평소 설치/함성 빈도로 회복이 따라오는지 본다. 플라스크를 계속 눌러야 버티면 혈마법 1점을 되돌리고 08B를 유지한다. 파콰테와 메아리치는 함성은 아직 사용하지 않는다.',
'09': '08C가 안정된 뒤 타락시키는 비명 I를 파콰테의 맹약으로 교체한다. 두 보조를 같은 함성에 함께 넣지 않는다. 파콰테만 먼저 시험한 다음 효율 II 자리에 메아리치는 함성을 넣고 다시 소모를 확인한다. AWT는 보조 4칸 확보 후 긴급한 토템 III·가지치기 균열 I·포악함 III로 업그레이드한다. 트리의 나무 벽과 직전 작은 전직 노드는 3차 전직을 실제로 얻었을 때만 추가한다. 일반 패시브를 다시 갈아엎는 단계가 아니다.',
}
# Confirmed Korean titles are used below for the actual groups. Gate text names
# are normalised by the verified mapping to prevent hand-typed translations.
GATES['03']='응답받은 부름 1차 전직 및 충격파 토템 보조 3칸을 준비한다. 02의 과잉 I를 빼는 효과는 한도 -1·50% 감폭 지속시간 해제이며, 응답받은 부름에서 토템 한도 +1을 얻으므로 두 변화는 상쇄된다. 전직 전에 보조만 먼저 바꾸지 않는다. 빠른 공격 I·긴급한 토템 I·포악함 II로 연결하고 낮은 지역에서 설치 수와 처치 속도를 확인한다. PoB2는 이 조합의 한도 계산이 불완전하므로 게임의 한도 표시를 기준으로 한다.'
GATES['05A']+=' 기본 파일에서는 명상 II를 제외했다. 원본 43레벨 장비의 정신력 60으로는 마그마 장벽·활력 I·명상 II의 합계 70을 감당하지 못한다. 함성은 연타하지 말고 토템을 유지하며 마나 플라스크로 보충한다.'
GATES['06']+=' 트리 변경만으로 딜이 올라간다고 가정하지 않는다. 동일한 구장비 계산에서는 함성 1중첩 DPS가 261에서 254로 내려갔다. 제작자 46레벨 장비에서는 유효 함성 레벨 16으로 475였으므로, 무기의 스킬 레벨과 젬을 먼저 확보한 뒤 현재 장비로 다시 비교한다. 명상 II는 마그마 장벽·활력 I와 합계 정신력 70 이상일 때만 활성화한다.'
GATES['08A']+=' 구장비 비교에서 세트 I 재생이 초당 106.5에서 81.2로 줄었다. 다음 장비·젬 전환을 마을에서 연속 처리하는 준비 단계이며 회복 개선용 사냥 단계가 아니다.'
GATES['08B']+=' 원본 후기 무기로 바꾸면서 구형 함성 젬을 유지하면 유효 레벨 16에서 14로 낮아져 1중첩 피해가 847에서 689로 줄었다. 예시 장비에서는 기본 15레벨 함성 젬으로 유효 17레벨·1중첩 1090을 얻었다. 자신의 장비에서 전환 전후 유효 레벨과 실제 자원 소모를 비교한다.'
GATES['08C']+=' 원본 후기 장비·유효 함성 17레벨 계산은 함성 1회 생명력 52, AWT 1기 설치 72다. 토템 내부 지면 분쇄의 공격 비용을 플레이어가 공격마다 내는 것으로 계산하지 않는다. 이 수치는 장비와 젬이 같은 경우의 예시다.'
GATES['09']+=' 이 단계는 현재 자동 추천 대상이 아니다. PoB2가 파콰테의 최대 생명력 추가 비용을 빠뜨려 기본 비용만으로 유지력을 판정할 수 없다. 메아리치는 함성은 1.3초 간격으로 2회 반복하고 다음 직접 사용 전에 10미터를 이동해야 한다. 한 번 누른 뒤 이동하며 반복을 기다린다. 같은 자리에서 연타하는 운영은 성립하지 않는다. 실제 1회·반복 비용과 회복을 확인하기 전에는 08C를 유지한다.'
GATES['08B']+=' 이 단계는 마나 플라스크를 포함한 짧은 전환 시험이다. 예시 장비로 AWT 4기·함성 초당 1회는 플라스크 없이 약 13초에 마나가 부족했다. 자연 마나 재생만으로 무한 유지되는 단계로 안내하지 않는다.'
GATES['08C']+=' 동일 장비에 함성 초당 1회·AWT 4기 재설치·양 세트 중 낮은 재생 108.6/초·직접 함성의 긴급한 부름 2% 회복을 적용하면, 적 피해와 플라스크 없이 90초 동안 비용을 지불했고 최소 생명력은 약 87%였다. 이는 자원 유지 계산이며 피격 생존이나 20마리 의식을 검증한 결과가 아니다.'
GATES['01']+=' 충격파 토템은 미가공 스킬 젬 3레벨부터 제작할 수 있고, 3레벨 스킬 젬의 캐릭터 요구 레벨은 6이다. 확보하면 01의 10점 완성이나 액트 1 완료를 기다리지 말고 02의 토템 스킬 운영을 도입한다. 근접 스킬도 함께 유지한다.'
GATES['02']='충격파 토템은 미가공 스킬 젬 3레벨부터 제작하며 3레벨 젬은 캐릭터 6레벨·힘 14부터 사용한다. 확보 즉시 세트 II의 무기로 소환하도록 추가한다. 과잉 I·포악함 I는 확보하는 대로 충격파 토템의 보조 소켓에 넣는다. 두 보조가 모두 있어야 토템을 처음 쓸 수 있는 것은 아니다. 01의 10점이나 이 파일의 일반 25점·세트별 4점은 트리 목표이며 스킬 사용 진입 조건이 아니다. 기존 몰려오는 강타·뼈 박살과 병행한다.'
REPLACE={
 '재빠른 고통 II':KO['Swift Affliction II'],
 '명상 II':KO['Clarity II'], '선대의 유대':'선대의 유대 (Ancestral Bond)',
 '가지치기 균열 I':KO['Branching Fissures I'], '메아리치는 함성':KO['Echoing Cry'],
}
for key in GATES:
    for a,b in REPLACE.items(): GATES[key]=GATES[key].replace(a,b)

EARLY_ROT='몰려오는 강타(I)로 기절을 준비하고 뼈 박살(II) 사용 → 방패 세트 I로 복귀. 지옥불 함성은 안전할 때 강한 적을 상대로 사용한다. 양손 철퇴가 없는 시작 직후에는 한손 철퇴로 진행하고 확보 후 II를 지정한다.'
TOTEM_ROT='충격파 토템(II) 설치 → 지진(I)으로 요철 지대 생성 → 이동. 충전이 없을 때도 지진은 자체 지대를 만든다. 대장간 망치가 있는 단계에서는 안전할 때 망치(I) → 함성(I)으로 폭발. 요철 지대 I 보조는 인내 충전을 소비하므로 충전 없이 망치만 눌러 지대가 생긴다고 가정하지 않는다.'
CRY_ROT='잡몹은 보강하는 함성(I) 1회 → 이동 → 남은 적 확인. 희귀/보스는 충격파 토템(II)을 먼저 놓고 함성(I)으로 방패 세트에 복귀한다. 지진/망치는 여유가 있을 때 보조한다. 같은 자리에서 함성을 계속 연타하지 않는다.'
AWT_ROT='선대의 전사 토템(II) 설치 → 보강하는 함성(I)으로 방패 세트 복귀 → 토템이 만든 지면 분쇄 가시를 함성으로 폭발 → 이동. 지진 함성(I)은 보조 함성으로 사용한다. II는 방패가 없는 세트이므로 설치 후 I로 돌아간다.'
HC='하코에서는 레벨보다 현재 액트·퀘스트 보상·장비를 기준으로 고른다. 65레벨 이후라도 캠페인이면 01-Campaign 필터를 유지한다. 의식 시작 전 돌아다닐 공간과 출구를 확보하고, 가속 희귀가 뭉치면 설치/함성 한 번 뒤 바로 이동해 간격을 유지한다. 기절시킨 적도 회복 후 다시 접근한다.'
ATTR='모든 능력치 선택 노드는 필요한 젬/장비의 힘·민첩·지능에 맞춰 선택한다. 양 무기 세트에서 비활성화되는 젬이나 장비가 없는지 확인한다. 아이템 예시의 낮은 생명력·저항을 목표치로 삼지 않는다.'
ORIGIN={
'01':'Pathcraft 재구성: 이번 리그 제작자 24레벨 실측의 근접 피해 시작 경로. 스킬 운영의 출발점은 구버전 제작자 초반 가이드이므로 이번 리그 1~10레벨을 그대로 관측한 자료는 아니다.',
'02':'Pathcraft 재구성: 이번 리그 제작자 24레벨 트리의 부분집합. 초반 스킬 연결은 제작자 초반 가이드를 바탕으로 하며 24레벨 실측 연결과의 차이는 03 진입 조건에 명시했다.',
'03':'제작자 이번 리그 24레벨 스냅샷의 트리·스킬 연결. 24레벨에 전환하라는 뜻이 아니다.',
'04':'제작자 이번 리그 34레벨 스냅샷의 트리·스킬 연결.',
'05':'제작자 이번 리그 43레벨 스냅샷의 트리·스킬 연결.',
'05A':'Pathcraft가 추가한 시험 단계: 제작자 43레벨 트리/장비에 46레벨 함성 연결을 먼저 도입하되 정신력이 부족한 명상 II는 기본 연결에서 제외했다. 제작자가 이 조합으로 플레이한 실측은 아니다.',
'06':'제작자 이번 리그 46레벨 스냅샷의 완성 트리·스킬 연결. 환불 도중 연결을 유지하는 작업은 총 일반 60점이 필요하므로 하코에서는 실제 전환을 늦춘다.',
'07':'제작자 이번 리그 52레벨 스냅샷의 트리·스킬 연결.',
'08':'Pathcraft가 추가한 방어/재생 투자 선택지. 제작자 실측 스냅샷은 아니다.',
'08A':'Pathcraft가 추가한 준비 단계: 제작자 74레벨 트리에서 선대의 유대·혈마법·3차 전직 2점을 제외하고 기존 함성/토템을 잠시 유지한다.',
'08B':'Pathcraft가 추가한 마나 시험 단계. 제작자 최종 장비 구조에 낮은 등급의 AWT 보조와 기존 타락시키는 비명 I를 사용한다.',
'08C':'Pathcraft가 추가한 혈마법 시험 단계. 08B에서 혈마법 1점만 추가하고 마나 플라스크를 제거했다.',
'09':'제작자 이번 리그 74레벨 스냅샷의 트리·스킬 연결. 원본 장비는 구입 의무가 아닌 실제 사용 예시다.',
}

docs=['# 무기 세트와 젬 연결', '',
'G 스킬창의 큰 스킬 젬을 선택하고, 같은 스킬의 작은 보조 소켓에 표 오른쪽 젬을 넣는다. 무기 룬 소켓이 아니다. 선대의 전사 토템에는 액티브 젬인 지면 분쇄를 안에 넣는 예외가 있다.', '',
'세트 I 전용 스킬은 I만, II 전용은 II만 체크한다. `.build`에는 이 G 체크박스가 저장되지 않으므로 직접 설정해야 한다. 초반 02의 제작자 가이드 배정 외에, API에서 확인할 수 없는 버튼 배정은 장비·스킬 요구 조건에 근거한 Pathcraft 권장안이다.', '',
'각 파일은 자동 레벨 전환 프로그램이 아닌 단계별 목표다. 65+ 캠페인에서도 조건이 안 맞으면 07/08을 유지한다. 전환 중에는 마을에서 장비·트리·연결을 맞춘 뒤 낮은 지역에서 확인한다.', '']
manifest=[]
for p in sorted((OUT/'BuildPlanner').glob('*.build')):
    b=read(p); old=copy.deepcopy(b); code=b['name'].split()[0]
    # Preserve Korean item examples, discarding every old operational paragraph.
    for i in b['inventory_slots']:
        first=i.get('additional_text','').split('\n\n',1)[0].strip()
        if first.startswith(('HC 생존','[','스킬','세트')): first=''
        if first: i['additional_text']=first
        else: i.pop('additional_text',None)
    if code in ('01','02'): b['link']=NINJA
    late=code in ('08B','08C','09')
    cry=code in ('05A','06','07','08','08A')
    if late:
        w1='정신력 높은 성소 셉터(Shrine Sceptre) + 방어도 방패'
        w2='물리 피해 좋은 한손 철퇴 + 정신력 높은 성소 셉터(Shrine Sceptre). 양손 철퇴 사용 종료.'
        off='세트 II 보조 무기는 성소 셉터다. 이 베이스가 불의 순수함을 부여한다. 다른 셉터라면 이 파일의 순수함 연결을 그대로 사용할 수 없다. 양손 철퇴와 함께 착용할 수 없다. 원본의 Sadist\'s Mercy는 예시이며 다른 철퇴라면 토템 피해와 정신력을 다시 확인한다.'
    else:
        w1=('근접 스킬 레벨과 함성 레벨을 확보한 ' if cry else '물리 피해 좋은 ')+'한손 철퇴 + 방어도 방패'
        w2='현재 쓰던 양손 철퇴 유지 가능. 한손 철퇴+공유 방패는 실제 토템 피해를 비교한 후 선택한다.'
        off='양손 철퇴를 세트 II에 쓰면 이 보조 무기 칸은 비운다. 한손 철퇴로 바꿀 때만 방어도 방패를 공유한다. 인벤토리 무기 세트 아이콘 우클릭으로 공유 설정. 한손 전환을 특정 레벨에 강제하지 않는다.'
    append(b,'Weapon1','[무기 세트 I]\n'+w1+'\n이쪽 스킬은 G에서 I만 체크한다. 방패 들기와 주력 함성을 I로 지정해 II 사용 뒤 방패 세트로 복귀한다.')
    append(b,'Weapon2','[무기 세트 II]\n'+w2+'\n뼈 박살/충격파 토템/AWT는 아래 목록에 있는 단계에서만 II로 지정한다. 지면 분쇄는 AWT 안의 젬이며 별도 수동 공격 버튼이 아니다.')
    append(b,'Offhand2','[보조 무기 자리]\n'+off)
    rotation=AWT_ROT if late else CRY_ROT if cry else EARLY_ROT if code=='01' else TOTEM_ROT
    count=COUNTS[p.name]; plan=POOLS.get(b['name'])
    budget=f"최종 배정: 일반 {count['ordinary']}점 / 세트 I {count['sets'][0]}점·II {count['sets'][1]}점 / 전직 {count['ascendancy']}점."
    if plan:
        pool=plan['required_pool']
        budget+=f" 전환 중 필요 총량: 일반 {pool['ordinary']}점 / I {pool['sets'][0]}점·II {pool['sets'][1]}점. 환불 {plan['refunded_entries']}개."
    append(b,'BodyArmour1','[진입 조건과 변경 순서]\n'+GATES[code]+'\n\n[포인트]\n'+budget+'\n\n[스킬 운영]\n'+rotation)
    append(b,'Gloves1','[젬을 넣는 위치]\nG에서 아래 큰 스킬 젬의 보조 소켓에 연결한다. 연결할 스킬은 무기 I/II 슬롯 설명에 모두 적었다. AWT의 지면 분쇄는 토템 내부에 넣는다.\n보조 3칸은 하위 쥬얼러 오브, 4칸은 상위 쥬얼러 오브로 확장한다. 미가공 젬 등급·캐릭터/능력치 요구를 충족하지 못한 보조는 기존 등급을 유지한다. 핵심 타락시키는 비명/AWT 내부 지면 분쇄는 생략하지 않는다.\n'+ATTR)
    groups={'세트 I':[],'세트 II':[],'자동 부여':[]};rows=[]; purity=0
    for g in b['skills']:
        en=BASES[g['id']]
        if en=='Ancestral Spirits': group='자동 부여'
        elif en=='Harbinger of Madness': group='자동 부여'
        elif en=='Purity of Fire': group='세트 I' if purity==0 else '세트 II';purity+=1
        elif en in ('Mace Strike','Boneshatter','Shockwave Totem','Ancestral Warrior Totem'):group='세트 II'
        else:group='세트 I'
        supports=' + '.join(display(x) for x in g.get('support_skills',[])) or '연결 보조 없음'
        groups[group].append(display(g)+' → '+supports)
        rows.append(f'| {group} | {display(g)} | {supports} |')
    append(b,'Weapon1','[세트 I 스킬 → 해당 스킬에 꽂을 젬]\n'+'\n'.join(groups['세트 I']))
    append(b,'Weapon2','[세트 II 스킬 → 해당 스킬에 꽂을 젬]\n'+'\n'.join(groups['세트 II']))
    append(b,'Helm1','[출처와 적용 범위]\n'+ORIGIN[code]+'\n\n[하드코어 운영]\n'+HC)
    if code=='08A':
        append(b,'Helm1','[07에서 직행 / 방어 일부만 투자한 경우]\n아래 장화·허리띠·반지의 순서는 08의 방어 14점을 전부 찍은 경우다. 07에서 바로 오거나 07→08 순서의 첫 1~13점만 찍었다면 동봉 패시브전환.md의 해당 점수 전용 경로를 사용한다. 안 찍은 방어 노드를 먼저 찍을 필요 없다.')
    if groups['자동 부여']:
        append(b,'Helm1','[자동 부여 — 별도 젬 제작 불필요]\n'+'\n'.join(groups['자동 부여'])+('\n광기의 선구자는 원본 고유 무기에서 부여된다. 대체 무기라면 이 스킬이 없어도 별도 젬으로 만들지 않는다.' if late else ''))
    if late:
        append(b,'Amulet1','[정신력과 버프]\n모든 버프 활성화 후, 토템 설치 전 남은 정신력을 I와 II 각각 확인한다. 2기=각 150, 3기=각 225, 4기=각 300 이상. 부족하면 목표 수를 줄이고 새 소환 때 기존 토템이 사라지지 않는지 확인한다. 옛 충격파 토템도 선대의 유대의 예약 대상이므로 마을에서 사라진 후 작업한다.\n불의 순수함 두 개는 각 셉터에서 따로 부여되는 스킬이다. I의 순수함에 활력 II·식인 II·따뜻한 피, II의 순수함에 활력 I·정밀함 II를 연결한다. 실제 요구 정신력과 생명력 재생은 각 세트의 게임 표기를 기준으로 확인한다.')
    if code=='09':
        append(b,'Belt1','[파콰테 소모 점검]\n최근 사용/발동 횟수에 따라 최대 생명력의 10%씩, 최대 30%가 추가 비용으로 붙는다. 메아리치는 함성의 발동도 고려해야 한다. 반복 사용 중 순수 재생이 소모를 따라가지 못하면 메아리치는 함성을 빼거나 08C의 타락시키는 비명 I·효율 II 조합으로 복귀한다. 젬 레벨을 예전 3레벨에 고정하는 가이드는 쓰지 않는다.')
    if plan and plan['refunded_entries']:
        operations=plan['operations']; chunk=(len(operations)+3)//4
        for part,slot in enumerate(('Boots1','Belt1','Ring1','Ring2')):
            portion=operations[part*chunk:(part+1)*chunk]
            if portion:
                lines=[f'{part*chunk+j+1}. {op_text(o)}' for j,o in enumerate(portion)]
                append(b,slot,f'[이전 단계에서 패시브 변경 순서 {part+1}/4]\n마을에서 순서대로 진행. 영어 노드명/ID는 동명 노드 구분용이다.\n'+'\n'.join(lines))
    assert b['skills']==old['skills'] and b['passives']==old['passives']
    # Final UI presentation uses the official per-skill and build-description
    # fields. Equipment popups show equipment priorities, not a full manual.
    b=render_planner(b,count,plan,KO,BASES,NODES)
    write(p,json.dumps(b,ensure_ascii=False,indent=2)+'\n')
    docs+=['## '+b['name'],'',ORIGIN[code],'',GATES[code],'',budget,'',f'- 세트 I: {w1}',f'- 세트 II: {w2}','',rotation,'','| G 지정 | 큰 스킬 젬 | 안에 연결할 젬 |','|---|---|---|',*rows,'']
    manifest.append({'file':p.name,'notes_in_korean':True,'all_socket_groups_documented':True,'max_note_length':max(len(i.get('additional_text','')) for i in b['inventory_slots'])})
write(OUT/'무기세트와젬연결.md','\n'.join(docs))

passive=['# 패시브 전환 순서','','새 01→02→03은 기절 축적 우회 없이 근접 피해 시작 경로로 이어지며 환불이 없다. 01/02는 이번 리그 24레벨 실측의 부분집합으로 재구성했다. 제작자의 1레벨부터 실제 클릭 순서를 관측한 자료는 아니다.','',
'아래 일반 포인트는 공통 배정 + 두 무기 세트 배정 중 큰 쪽이다. 세트별 포인트는 일반 점수에 더하는 별도 보너스가 아니라 무기 특화에 사용할 수 있는 한도다. 퀘스트 보상을 받지 않았다면 레벨만 올려서 이 한도가 늘지는 않는다. 전환 중 총량은 이미 쓴 점수와 미사용 점수를 합한 값이다.','',
'**전환 중 핵심 조건:** 05A→06은 일반 60점/I 12점/II 14점이다. 08→08A의 트리 작업 자체는 일반 95점/I·II 각 22점으로 되지만, 다음 선대의 유대·혈마법 각 1점까지 바로 연결하도록 실제 진입은 총 일반 97점을 확보한 뒤 한다. 준비가 안 됐으면 앞 파일을 유지한다. 65레벨 자동 전환표가 아니다.','',
'무기 세트 선택을 해제한 공통 모드 또는 I/II 모드를 표대로 선택한다. 06→07의 `totems43`은 공통 모드로 재배정한다. 실제 UI에서 변경이 허용되지 않으면 무리하게 다른 연결 노드를 환불하지 말고 적용 전 상태를 유지한다. 모든 순서는 공개 트리의 공통/각 세트 연결을 매 단계 확인한 것이며 게임 UI 클릭을 실연한 결과는 아니다.','',
'08은 선택 단계다. 07에서 바로 오거나 07→08 순서의 첫 1~13점만 찍었다면 문서 아래의 전용 경로를 사용한다. 14점을 전부 찍은 경우에만 기본 08→08A 표를 사용한다. 준비물과 총 일반 97점은 08A에 들어가기 전에 모은다.','',
'| 전환 | 최종 일반 | 작업 중 일반 | 작업 중 I/II | 환불 노드 수 |','|---|---:|---:|---:|---:|']
for p in PLANS:
    c=p['required_pool']
    passive.append(f"| {p['from'].split()[0]} → {p['to'].split()[0]} | {p['to_cost']['ordinary']} | {c['ordinary']} | {c['sets'][0]}/{c['sets'][1]} | {p['refunded_entries']} |")
passive+=['','환불 수는 삭제되는 노드 수다. 무기 세트 전용 노드 하나를 환불해도 일반 미사용 점수가 즉시 1 오르는 것은 아니다. 실제 골드 비용은 캐릭터 레벨과 UI에 따라 확인한다.','']
for p in PLANS:
    passive+=['## '+p['from']+' → '+p['to'],'']
    if not p['operations']: passive+=['트리 변경 없음. 함성 젬만 시험한다.',''];continue
    for n,o in enumerate(p['operations'],1):passive.append(f'{n}. {op_text(o)}')
    passive.append('')
passive+=['## 07에서 직행하거나 선택 방어를 일부만 찍은 경우','',
'아래의 “방어 n점”은 이 문서의 **07→08 추가 순서에서 처음 n개를 찍은 상태**다. 임의로 다른 순서로 찍은 상태를 같은 점수라는 이유만으로 적용하지 않는다. 0점은 07에서 바로 08A로 가는 경로다. 14점 전부 찍었다면 위의 기본 08→08A 경로를 쓴다. 준비 조건은 모두 일반 총 97점, 양 세트 각 22점과 후기 준비물이다.','',
'| 07 이후 선택 방어 | 후반 트리 이동 시 환불 |','|---:|---:|']
alternatives=read(HERE/'partial_transitions_v2.json')
for route in alternatives:passive.append(f"| {route['defence_points_used']}점 | {route['refunded_entries']}개 |")
passive.append('')
for route in alternatives:
    passive+=['<details>',f"<summary>07 + 선택 방어 {route['defence_points_used']}점 → 08A: 클릭하여 순서 보기</summary>",'']
    for n,o in enumerate(route['operations'],1):passive.append(f'{n}. {op_text(o)}')
    passive+=['','</details>','']
passive+=['## 출처','','- [제작자 현재 리그 캐릭터]('+NINJA+')','- [제작자 초반 가이드]('+SKADOOSH+')','- [공식 0.3 패치: 무기 공유와 스킬 변경](https://www.pathofexile.com/forum/view-thread/3826682)','- [선대의 전사 토템 데이터](https://poe2db.tw/us/Ancestral_Warrior_Totem)','- [과잉 I 데이터](https://poe2db.tw/us/Overabundance_I)','- [선대의 유대 데이터](https://poe2db.tw/us/Ancestral_Bond)','- [혈마법 데이터](https://poe2db.tw/us/Blood_Magic)','- [파콰테의 맹약 데이터](https://poe2db.tw/us/Paquates_Pact)','']
write(OUT/'패시브전환.md','\n'.join(passive))
write(HERE/'validation_notes_v2.json',json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
write_player_guides(OUT,[read(p) for p in sorted((OUT/'BuildPlanner').glob('*.build'))],KO,BASES)
print(f'Annotated {len(manifest)} planners and wrote socket/transition guides.')
