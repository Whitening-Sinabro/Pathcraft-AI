"""Publish the audited, serialized planners into the existing Korean Docs guide."""
from pathlib import Path
import collections, datetime, hashlib, html, json, re, shutil
import markdown

ROOT=Path('D:/Pathcraft-AI')
HERE=Path(__file__).resolve().parent
SOURCE=HERE/'revision3'
DOCS=ROOT/'Docs'
STEM='2026-09-05_SKADOOSH_CORRUPTING_CRY_TOTEM_WARBRINGER_0_5_5'
MD=DOCS/(STEM+'_RESEARCH.md')
HTML=DOCS/(STEM+'_GUIDE_DOC.html')
ARCHIVE=DOCS/'archive'/(STEM+'_RESEARCH_before_2026-09-07_v3.md')
REL='../deliverables/skadoosh_hc_2026-09-07/'

def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def plain(s):
    s=s.replace('\\n','\n')
    return re.sub(r'<[^>]+>\{([^{}]*)\}',r'\1',s).strip()
def cell(s):return html.escape(s).replace('|','&#124;').replace('\n','<br>')
def link(label,name):return f'[{label}]({REL}revision3/{name})'
def table(headers,rows):
    return '\n'.join(['| '+' | '.join(headers)+' |','|'+'|'.join('---' for _ in headers)+'|',*['| '+' | '.join(cell(str(c)) for c in row)+' |' for row in rows]])

validation=read(HERE/'validation_revision3.json')
paths=sorted((SOURCE/'BuildPlanner').glob('*.build'))
assert len(paths)==7
builds=[read(p) for p in paths]
assert all(sha(p)==next(r['sha256'] for r in validation['planners'] if r['file']==p.name) for p in paths)
assert paths[0].name=='01 시작-근접 기초.build'
installation=read(HERE/'installation_revision3.json')
installed_before={r['path']:sha(Path(r['path'])) for r in installation['installed']}
assert all(installed_before[r['path']]==r['sha256'] for r in installation['installed'])
progress=read(HERE/'progression_v3.json')
transitions=read(HERE/'transition_operations_v3.json')
assert [r['file'] for r in progress]==[p.name for p in paths]

if not ARCHIVE.exists():
    assert '## 0. 오늘부터 따라 하기' in MD.read_text(encoding='utf-8')
    ARCHIVE.parent.mkdir(exist_ok=True)
    shutil.copy2(MD,ARCHIVE)
    assert sha(MD)==sha(ARCHIVE)
original_sha=sha(ARCHIVE)

INTRO=f'''# Skadoosh 타락 함성·전사 토템 워브링어 — 하코 플레이 가이드

POE2 0.5.5 Forbidden Rites · **2026-09-07 개정 · 설치된 플래너 7단계 기준**

[브라우저용 가이드]({HTML.name}) · [필터·플래너 ZIP]({REL}Skadoosh-HC-한국어-필터와플래너.zip) · [개정 전 리서치](archive/{ARCHIVE.name})

근접으로 시작해 충격파 토템을 추가하고, 보강하는 함성을 거쳐 선대의 전사 토템으로 넘어간다. 후기에는 **보강하는 함성에 파콰테**, **지진 함성으로 지면 분쇄 가시 폭발**을 맡긴다. 이번 경로는 한손 철퇴와 방패로 진행하며 양손 철퇴로 갈아타는 필수 단계가 없다.

**충격파 토템을 만들 수 있으면 02부터 보면 된다.** 미가공 스킬 젬 3레벨, 캐릭터 6레벨, 힘 14가 조건이다. 토템을 얻은 뒤에도 해당 플래너의 모든 스킬·보조·패시브를 한꺼번에 갖출 필요는 없다.

이 문서에서 24·43·52·74레벨은 제작자의 관찰 시점이다. 내 캐릭터의 강제 전환 레벨이 아니다. **65레벨 이상이어도 캠페인을 진행 중이면 캠페인 필터를 쓰고, 준비되지 않은 전환은 미룬다.**

<a id="choose"></a>

## 지금 볼 단계

'''
WHEN=[
 '충격파 토템을 얻기 전',
 '충격파 토템을 배운 직후부터 1차 전직까지',
 '대장간 망치를 확보한 뒤 2차 전직까지',
 '방어도 방패·보강하는 함성·타락시키는 비명 연결이 준비됨',
 '전사 토템·셉터 2개·정신력·회복과 환불 준비가 됨',
 '65레벨 이상, 파콰테와 두 함성의 비용 시험을 통과함',
 '현재 운영이 안정되어 후기 장비와 패시브를 확장함',
]
items=['| 단계 | 이때 사용 | 패시브 완성 목표: 일반 / 특화 I·II / 전직 |','|---|---|---|']
for i,(b,r) in enumerate(zip(builds,progress)):
    code=f'{i+1:02}'
    items.append(f"| [{b['name']}](#stage-{code}) | {WHEN[i]} | {r['ordinary']} / {r['sets'][0]}·{r['sets'][1]} / {r['ascendancy']} |")
parts=[INTRO,'\n'.join(items),f'''
표의 점수는 단계가 완성됐을 때의 목표다. 예를 들어 **02는 29점이 되기 전부터 사용**하고, 07의 97점은 지도 진입 조건으로 요구하지 않는다. 특화 포인트는 해당 퀘스트 보상으로 확보한다.

1차 전직은 **응답받은 부름**, 2차는 **전쟁 소집자의 고함**, 3차는 **나무 벽**이다. 첫 패시브는 이번 방송에서 확인한 **근접 피해 시작 경로**를 따른다. 첫 단계 10점은 24레벨 실측의 하위 경로이며 초기 모든 클릭 순서를 영상에서 복원했다는 뜻은 아니다.

<a id="controls"></a>

## 젬과 무기 세트 설정

**G의 스킬 설정에서 토템은 II, 방패·함성은 I에 지정한다.** 각 단계 표의 세트를 확인해 체크박스를 직접 맞춘다. 버프도 해당 셉터와 무기 세트에 맞춰 지정한다.

- **01~04:** I = 한손 철퇴 + 방어도 방패, II = 한손 철퇴 + 공유 방패. 철퇴가 하나뿐인 시작 구간은 무기를 공유한다.
- **05~07:** I = 성소 셉터 + 방어도 방패, II = 한손 철퇴 + 성소 셉터. 전사 토템을 II로 설치한 뒤 I의 함성으로 돌아온다.
- **선대의 전사 토템 안에 지면 분쇄 액티브 젬을 넣는다.** 포악함·파생하는 균열 같은 보조도 같은 토템에 연결한다. 지면 분쇄를 별도 수동 공격 버튼으로 운용하지 않는다.
- **불의 순수함은 성소 셉터가 부여한다.** I와 II에 보이는 각각의 불의 순수함에 해당 보조를 넣는다. 선대의 혼백은 전직이 부여한다.
- 연결표의 보조는 **적힌 스킬의 보조 소켓**에 넣는다. 무기의 룬 소켓에 넣는 것이 아니다. 같은 보조가 두 스킬에 적혀 있으면 필요한 젬을 각각 준비한다.

아래 연결표는 **각 단계의 완성 목표**다. 아직 해금하지 못한 스킬, 상위 보조, 추가 소켓은 얻는 순서대로 채운다. 핵심 토템을 배우는 일을 그 때문에 미루지 않는다. 자세한 개별 설명은 {link('무기세트와 젬 연결', '무기세트와젬연결.md')}에도 있다.
''']

stage_evidence=[
 ('첫날 02:13:30 — 근접 피해 시작','2865212551','2h13m30s'),
 ('첫날 02:00:52 — 충격파 토템 요구 조건','2865212551','2h0m52s'),
 ('둘째 방송 02:56:00 — 2차 전직','2866065347','2h56m0s'),
 ('둘째 방송 04:27:30 — 함성 전환','2866065347','4h27m30s'),
 ('셋째 방송 00:35:00 — 54레벨 전사 토템 전환','2866749730','0h35m0s'),
 ('셋째 방송 04:03:00 — 두 함성 연결','2866749730','4h3m0s'),
 ('셋째 방송 07:03:00 — 3차 전직','2866749730','7h3m0s'),
]
catalog=[]
priority=[['몰려오는 강타','뼈 박살'],['충격파 토템','지진','뼈 박살'],['충격파 토템','대장간 망치','지진'],['보강하는 함성','충격파 토템'],['선대의 전사 토템','보강하는 함성','지면 분쇄'],['선대의 전사 토템','보강하는 함성','지진 함성','지면 분쇄'],['선대의 전사 토템','보강하는 함성','지진 함성','지면 분쇄']]
for i,(p,b,r) in enumerate(zip(paths,builds,progress)):
    code=f'{i+1:02}'
    description=plain(b['description'])
    gate=description.split('지금 할 일\n',1)[1].split('\n\n무기·스킬셋',1)[0]
    if i==0:gate=gate.replace('뼈 박살에 충격파를','뼈 박살에 충돌 충격파를')
    rotation=description.split('사용 순서\n',1)[1].split('\n\n다음:',1)[0]
    next_step=description.split('\n\n다음:',1)[1].split('\n',1)[0].strip()
    weapons=[plain(next(x for x in b['inventory_slots'] if x['inventory_id']==slot)['additional_text']).splitlines()[0] for slot in ['Weapon1','Weapon2']]
    parts += [f'<a id="stage-{code}"></a>\n\n## {b["name"]}',
              f'**이 단계 시작:** {WHEN[i]}\n\n{gate}',
              f'**사용 순서:** {rotation}',
              '**무기 세트:** '+weapons[0]+' / '+weapons[1],
              f'**패시브 목표:** 일반 {r["ordinary"]}점 · 특화 I/II {r["sets"][0]}/{r["sets"][1]}점 · 전직 {r["ascendancy"]}점.']
    if i==1:
        parts += ['**토템 보조를 채우는 순서:** 처음에는 무보조로 시작해도 된다. 과잉 I를 얻으면 사용할 수 있지만 지속시간이 절반으로 줄어 재설치가 잦다. 이후 빠른 공격 I·긴급한 토템 I·포악함 II의 아래 목표로 바꾼다. 이 세 보조가 처음부터 있어야 02를 쓰는 것은 아니다.']
    if i==4:
        parts += ['**전환 전 확인:** 버프를 켜고 토템을 아직 설치하지 않은 상태에서 I·II 각각 남는 정신력 300 이상을 확인한다. 토템 4기의 예약은 각 75다. 한쪽만 맞추면 무기 교체 때 토템이 사라질 수 있다. 필요하면 마그마 장벽 등 예약을 조절한다. 보강하는 함성의 유효 젬 레벨은 셉터로 바꾸면서 떨어질 수 있으므로 전후를 비교한다.\n\n**65레벨 이상이면:** 69점 안에서 남는 점수를 회복·방어 11점으로 먼저 확장한다. 총 80점 경로이며 파콰테가 필요하지 않다. 원소 저항은 현재 최대치까지 맞추고, 설치·함성 후 회복이 따라오는지 확인한 뒤 진행한다.']
    if i==5:
        parts += ['**이 단계는 조건부다.** 파콰테를 보강하는 함성에 두고, 지진 함성은 직접 가시를 터뜨리는 데 쓴다. 메아리는 1.3초 간격 2회이며 다음 직접 사용 전 10미터 이동 조건을 확인한다. 반복의 실제 추가 비용과 회복량은 아직 정량 확정하지 못했다. 생명력이 누적해서 내려가면 보강하는 함성을 05의 타락시키는 비명 I·효율 II 연결로 되돌린다.']
    skill_rows=[];skill_data=[]
    def skill_order(g):
        name=plain(g['additional_text']).splitlines()[0].rsplit(' · ',1)[0]
        return priority[i].index(name) if name in priority[i] else 100
    for g in sorted(b['skills'],key=skill_order):
        text=plain(g['additional_text'])
        heading=text.splitlines()[0]
        name,role=heading.rsplit(' · ',1)
        pre,post=text.split('이 스킬 안에 넣을 젬\n',1)
        usage='\n'.join(pre.splitlines()[1:]).strip()
        supports=post.split('\nG 무기 세트',1)[0].strip().replace('현재 연결 보조 없음.','연결 보조 없음')
        skill_rows.append((name+' · '+role,supports,usage))
        skill_data.append({'id':g['id'],'name':name,'role':role,'support_ids':[s['id'] for s in g.get('support_skills',[])],'display_links':supports})
    parts += ['### 스킬에 넣을 젬',table(['스킬 · 사용할 세트','이 스킬 안에 넣을 젬','사용법'],skill_rows)]
    gear_rows=[]
    for slot in b['inventory_slots']:
        text=plain(slot['additional_text'])
        before,options=text.rsplit('추천 옵션\n',1)
        title=before.rstrip().splitlines()[-1]
        gear_rows.append((title,options.strip()))
    parts += ['<details markdown="1">\n<summary>이 단계의 장비 추천 옵션 펼치기</summary>\n',table(['장비','추천 옵션 · 위에서부터 확인'],gear_rows),'\n</details>',
              f'**다음 단계:** {next_step}\n\n**구성 근거:** {r["origin"]}']
    label,vod,time=stage_evidence[i]
    parts += [f'[{label}](https://www.twitch.tv/videos/{vod}?t={time}) · [이 단계 플래너](<{REL}revision3/BuildPlanner/{p.name}>)']
    catalog.append({'stage':code,'file':p.name,'name':b['name'],'sha256':sha(p),'skills':skill_data,'gear_slots':len(gear_rows)})

parts += [f'''<a id="transition"></a>

## 패시브와 전환 준비

장비·젬·소켓과 환불 비용을 준비한 뒤 마을에서 전환한다. **03→04는 46레벨 실측 트리를 내부 경유**하고 52레벨 목표로 확장한다. 중간 과정을 별도 플래너 파일로 늘리지 않았다. **05에서는 혈마법을 마지막에 찍는다.**

아래 표는 각 경로를 끝까지 바꿀 때의 총 보유 한도다. 신규로 더 벌어야 할 점수가 아니다. 또한 01→02처럼 점진적으로 성장하는 단계의 사용 시작 조건이 아니다. 실제 환불 골드는 자기 레벨에서 확인한다.
''',table(['경로','일반 총 한도','특화 I / II 총 한도','환불 노드 수'],[
    (t['from']+' → '+t['to'],t['required_pool']['ordinary'],f"{t['required_pool']['sets'][0]} / {t['required_pool']['sets'][1]}",t['refunds']) for t in transitions]),
f'''04→05는 완성 후 특화 각 14점이지만, 제시한 환불 순서를 진행할 때는 **특화 각 16점 한도**가 필요하다. 05→06은 패시브가 같고 06→07은 기존 배정을 유지하는 확장이다. 05에서 이미 회복·방어 11점을 더했다면 그 노드를 다시 환불할 필요가 없다.

{link('노드별 환불·추가 순서와 회복·방어 80점 경로', '패시브전환.md')}를 보면서 진행한다. 이 순서는 연결과 포인트 한도를 검사한 경로이며 제작자의 매 클릭을 그대로 전사한 순서는 아니다.

<a id="hc"></a>

## 하코에서 딜·회복을 판단하는 기준

05의 69점 트리는 **방송 기반 재구성안**이다. 제작자의 54레벨 당시 전체 트리를 정확히 복제한 파일이 아니다. 그의 전환 당시 생명력·저항 수치를 권장 최소치로 복사하지 않는다.

65레벨 대체 장비로 계산했을 때 토템 1기 설치는 생명력 61, 보강하는 함성 기본 비용은 46이었다. 이 수치는 예시 장비의 결과이며 내 캐릭터의 비용을 대신하지 않는다. 90초 유지 계산에서는 아래처럼 회복·방어 확장의 차이가 컸다.

| 65레벨 예시 | 일반 69점 | 회복·방어 확장 80점 |
|---|---|---|
| 적 피해 없음 | 최저 생명력 87.71% | 최저 생명력 90.00% |
| 경감 후 초당 50 피해 가정 | 최저 생명력 1.88% | 최저 생명력 84.96% |

토템 4기와 함성 초당 1회 조건의 자원 계산이다. 실제 몬스터 AI, 기절, 이동 중 명중 수, 다수 동시 피격을 재현하지 않는다. 따라서 80점을 찍으면 가속 마법·희귀 20마리를 버틴다는 뜻으로 읽지 않는다.

전사 토템 전환 뒤에는 타락한 피만 보고 딜을 비교하지 않는다. 예시에서 함성의 타락한 피 1중첩 DPS는 04 약 668에서 05 약 410으로 내려갔다. 05의 주된 변화는 토템의 지면 분쇄와 가시 폭발이다. 기본 지면 분쇄 공격 DPS를 가시 전체가 맞은 실전 총 DPS로 더하지 않았다.

파콰테·메아리는 반복 비용 해석에 따라 유지 성공/실패가 갈렸다. **06은 유지력이 충분하다고 확정한 단계가 아니다.** 실제 비용을 확인하기 전에는 05 연결을 유지하고, 이후에도 비용이 누적되면 되돌린다. 05 자체도 회복이 부족하면 혈마법을 되돌리고 장비·회복부터 보강한다. 혈마법 전 마나 상태 역시 플라스크 없이 무한 유지되는 세팅으로 제시하지 않는다.

{link('계산 입력·조건·한계', '시뮬레이션결과.md')} · {link('45개 조건을 비교하는 그래프', '시뮬레이션그래프.html')}

### 의식에서의 사용 순서

의식 전에 토템을 설치할 자리와 이동할 공간을 정한다. 토템 설치 → 함성 → 이동을 기본으로 하고, 몰려드는 무리 앞에서 토템·함성을 연타하느라 멈추는 시간을 줄인다. 기절한 적도 회복 후 다시 추격하므로 기절만 믿고 같은 위치에 남아 있지 않는다. 토템이 사라지면 보충하되 위험한 위치에서 한꺼번에 다시 설치하려고 머물지 않는다.

<a id="install"></a>

## 필터·플래너 설치와 파일 선택

| 필터 | 사용할 구간 |
|---|---|
| Pathcraft-Skadoosh-HC-01-Campaign.filter | 캠페인 전체. 65레벨 이상으로 올려 진행하는 경우 포함 |
| Pathcraft-Skadoosh-HC-02-EarlyMaps.filter | 캠페인 완료 후 초반 지도·장비 보강 |
| Pathcraft-Skadoosh-HC-03-SettledMaps.filter | 지도와 장비가 안정된 뒤 |

필터는 미감정 장비의 생명력·저항 옵션을 알 수 없다. 감정 후 각 단계의 추천 옵션과 비교한다. 한손 철퇴·방패·정신력 후보의 추가 강조가 들어 있다.

플래너는 `C:/Users/User/Documents/My Games/Path of Exile 2/BuildPlanner`, 필터는 그 상위 `Path of Exile 2` 폴더에 설치되어 있다. [배포 ZIP]({REL}Skadoosh-HC-한국어-필터와플래너.zip)을 풀어 같은 위치에 넣을 수도 있다.

**첫 단계만 실제 파일명을 `01 시작-근접 기초.build`로 유지한다.** 게임 표시명은 `01 시작 - 근접과 방패`이고 내용은 최신본이다. 캐릭터가 기억한 파일 경로를 보존하기 위한 처리다. 다른 6개는 표시명과 파일명이 같다.

이번 `unrecognised build plan id` 오류 때에는 게임이 새 7개를 정상 로드했지만 저장된 선택이 이전 파일명을 가리키고 있었다. 그 경로를 복구했다. 오류창이 남아 있으면 닫고 현재 단계의 플래너를 다시 선택한다. 최신 7개 정상 로드 로그와 실제 게임의 02 트리 화면을 확인했다.

플래너는 무기 세트 체크박스를 자동으로 설정하지 않는다. 선대의 전사 토템 안의 지면 분쇄가 별도 스킬 항목에도 보이는 것은 획득 안내를 위한 표시다. 실제로는 토템 내부에 넣는다. 이 제한은 [GGG 공식 Build Planner 형식](https://www.pathofexile.com/developer/docs/game#buildplanner)에 따른다.

<a id="evidence"></a>

## 방송 근거와 개정 기록

이번 가이드는 24·43·46·52·74레벨 공개 보존본과 아래 세 방송의 대조 결과를 사용한다. 조회 시점이 다른 후기 젬을 과거 단계에 섞지 않았다.

| 방송 | 길이 | 확인 방법 |
|---|---|---|
| [첫 방송](https://www.twitch.tv/videos/2865212551) | 04:42:33 | 전체 음성 두 번 전사·문맥 비교, 주요 화면 재확인 |
| [둘째 방송](https://www.twitch.tv/videos/2866065347) | 05:44:38 | 같은 방법 |
| [셋째 방송](https://www.twitch.tv/videos/2866749730) | 08:42:23 | 같은 방법 |

합계 **18시간 52분 54초**, 30초 간격 탐색 화면 **2,301장**, 주요 장면은 고해상도 프레임으로 대조했다. 원본에 자막 트랙이 없어 음성 인식을 사용했다. 두 전사는 같은 음성에서 나온 것이며 독립적인 출처 두 개가 아니다. 사람이 원음을 18시간 전부 듣거나 영상을 매초 재생했다는 의미도 아니다.

{link('장면별 원본 시각과 판정', '방송대조보고서.md')} · {link('파일·트리·게임 로드 검사', '검증결과.md')} · [제작자 캐릭터](https://poe.ninja/poe2/builds/forbiddenriteshc/character/ITheCon-2183/SkadooshShoutedHard)

2026-09-07 개정에서는 첫날 계획·0.4 가이드 중심의 본문을 현재 설치된 7단계로 교체했다. 전직 순서, 한손 철퇴·방패 운영, 토템 시작 조건, 보강하는 함성/지진 함성의 연결, 69→80점 방어 확장, 파콰테의 조건부 사용을 반영했다. **현재 확정하지 못한 핵심은 05의 정확한 54레벨 원본 트리와 파콰테·메아리의 반복 비용·회복량, 실전 총 DPS·다수 피격 생존이다.**

이전 0.4 계보·패치·커뮤니티 조사와 당시 인용은 [개정 전 리서치](archive/{ARCHIVE.name})에 보존했다. 그 문서의 레벨별 지시는 2026-09-05 당시 조사 기록이며 현재 플레이 순서는 이 문서를 따른다.

스킬·보조·장비 표는 설치본과 해시가 같은 `revision3/BuildPlanner` 파일에서 생성했다. 동기화 도구는 `deliverables/skadoosh_hc_2026-09-07/sync_docs_guide.py`, 내용 대조 기록은 같은 폴더의 `docs_guide_sync.json`에 있다.
''']
document='\n\n'.join(parts).rstrip()+'\n'
MD.write_text(document,encoding='utf-8')
body=markdown.markdown(document,extensions=['tables','md_in_html'])
# Keep the standalone view's opening link useful instead of linking to itself.
body=body.replace(f'href="{HTML.name}"',f'href="{MD.name}"').replace('브라우저용 가이드','마크다운 원문',1)
nav=''.join(f'<a href="#stage-{i+1:02}"><b>{i+1:02}</b> {html.escape(b["name"][3:])}</a>' for i,b in enumerate(builds))
style='''*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:24px}body{margin:0;background:#111923;color:#e9eef5;font:16px/1.75 system-ui,"Malgun Gothic",sans-serif}a{color:#8adbc7;text-underline-offset:3px}a:hover{color:#fff}header{border-bottom:1px solid #344250;padding:18px 32px;color:#becad9;font-size:14px}header strong{color:#e9eef5}.layout{display:grid;grid-template-columns:240px minmax(0,1040px);gap:36px;max-width:1400px;margin:auto;padding:32px}aside{align-self:start;position:sticky;top:22px}aside a{display:block;padding:8px 12px;border-left:2px solid #354959;text-decoration:none;font-size:14px}aside b{color:#adc2dc;margin-right:6px}aside a:hover{background:#1a2a38}main{min-width:0}h1{font-size:32px;line-height:1.35;margin:0 0 22px}h2{font-size:25px;margin:40px 0 16px;padding-top:16px;border-top:1px solid #3a4b5d;color:#b4e4d5}h3{font-size:19px;margin:22px 0 12px}p{margin:0 0 18px}strong{color:#fff}table{width:100%;border-collapse:collapse;margin:18px 0 24px;table-layout:fixed;font-size:14px;overflow-wrap:anywhere}th,td{text-align:left;vertical-align:top;padding:11px 13px;border:1px solid #3a4b5d}th{background:#203343;color:#fff}tr:nth-child(even){background:#16232f}details{margin:20px 0;padding:14px 18px;background:#1a2835;border:1px solid #3a4b5d;border-radius:8px}summary{cursor:pointer;color:#b9e5d9;font-weight:600}code{font:13px/1.7 ui-monospace,monospace;background:#253447;padding:2px 4px;overflow-wrap:anywhere}li{margin-bottom:8px}a[id]{display:block;scroll-margin-top:22px}footer{padding:24px 32px;border-top:1px solid #344250;color:#bdc9d8;font-size:13px}@media(max-width:900px){.layout{display:block;padding:22px 16px}aside{position:static;display:flex;flex-wrap:wrap;gap:4px;margin-bottom:28px}aside a{border:1px solid #354959;padding:5px 8px}h1{font-size:25px}h2{font-size:22px}th,td{padding:7px 6px;font-size:12px}header{padding:15px 16px}table{font-size:12px}}@media print{body{color:#111;background:white}.layout{display:block;padding:0}aside,header,footer{display:none}main{width:100%}a,strong,h2{color:#111}th,tr:nth-child(even),details,code{background:#f5f5f5;color:#111}th,td{border-color:#999}h2{break-after:avoid}tr{break-inside:avoid}}'''
HTML.write_text(f'<!doctype html>\n<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Skadoosh 하코 워브링어 — 7단계 가이드</title><style>{style}</style></head><body><header><strong>PATHCRAFT</strong> / POE2 · 0.5.5 Forbidden Rites · 2026-09-07</header><div class="layout"><aside aria-label="가이드 목차"><a href="#choose">지금 볼 단계</a>{nav}<a href="#transition">패시브 전환</a><a href="#hc">딜·회복과 의식</a><a href="#install">설치·오류 안내</a><a href="#evidence">방송 근거</a></aside><main>{body}</main></div><footer>방송 관찰과 Pathcraft 전환안을 구분합니다. 파콰테 반복 비용은 확인 중입니다.</footer></body></html>',encoding='utf-8')
assert all(sha(Path(path))==digest for path,digest in installed_before.items())
assert sha(ARCHIVE)==original_sha
report={'updated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'markdown':str(MD),'html':str(HTML),'archive':str(ARCHIVE),'archive_sha256':original_sha,'planner_count':7,'stages':catalog,'installed_files_unchanged':True,'markdown_sha256':sha(MD),'html_sha256':sha(HTML),'browser_verified':False}
(HERE/'docs_guide_sync.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'planners':7,'skill_rows':sum(len(s['skills']) for s in catalog),'equipment_rows':sum(s['gear_slots'] for s in catalog),'markdown':str(MD),'html':str(HTML),'old_research_preserved':True},ensure_ascii=False))
