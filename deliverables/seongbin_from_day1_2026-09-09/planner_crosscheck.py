"""Audit actual local/installed Seongbin planners; write research copies only."""
from pathlib import Path
import copy, hashlib, json

PAIRS = [
 ('HC 1 Act1 - Seongbin.build','ACT 1 - [0.5.5 Hardcore] 젬링 리그 �.build'),
 ('HC 2 Act2 - Seongbin.build','ACT 2 - [0.5.5 Hardcore] 젬링 리그 �.build'),
 ('HC 3 Act3-4 - Seongbin.build','ACT 34 - [0.5.5 Hardcore] 젬링 리그.build'),
 ('HC 4b 실캐릭 막간 - 임성빈.build','LIVE Lv61 - poe.ninja.build'),
 ('HC 6 Endgame - Seongbin.build','Interludes  End Game - [0.5.5 Hardcore].build'),
]
NOTES = [
 {'Weapon1':'가이드 목표 연결과 실제 획득 시점은 다릅니다.\n6레벨 섬광 Lv3 등록 직후 두 보조는 빈칸이며 파편탄은 G창에 남습니다.\n14레벨: 민첩16→21, 가스 Lv5 등록 → 원소 병기 I → 다중 사격 I. 두 보조 완료는 A 01:29:53.5. 폭발·섬광의 기존 보조는 유지됩니다.\nA=https://www.youtube.com/watch?v=zKJQyBm4VnI&t=5393s',
  'BodyArmour1':'장비 예시를 실제 장착 수치나 생존 보장선으로 읽지 않습니다.\nA 01:24:56~01:25:10 의식에서 생명력350→24, ES18→0 후 일시정지·캐릭터 선택 이탈. 특정 생명력+ES 합계만으로 생존을 보장할 수 없습니다.\nhttps://www.youtube.com/watch?v=zKJQyBm4VnI&t=5096s',
  'Gloves1':'A 01:33:12~20: 장착 밧줄 수갑 빈 소켓에 룬 생명력+30 적용, 별도 퀘스트 보상+20으로 최대 생명력329→379. 가이드 예시 장갑 옵션과 실제 장갑은 다릅니다.\nhttps://www.youtube.com/watch?v=zKJQyBm4VnI&t=5594s'},
 {'Weapon1':'이 플래너의 다중 사격 II·원소 병기 II는 단계 목표입니다. 첫날 14레벨 최초 가스 연결은 I+I이며, II 승급 시점은 미확인입니다.\nhttps://www.youtube.com/watch?v=zKJQyBm4VnI&t=5393s',
  'Belt1':'플래너의 ACT2 전직 배치는 목표입니다. 실제 첫날은 혼돈 후43레벨 미덕의 정수·고결한 방어막, 세케마로 돌아가 퀄리티+2% 작은 노드·고급 마석학을 적용했습니다.\n첫 전직: B 01:46:59~01:47:02. 두 번째: B 01:56:35.75~01:56:37. 바이퍼 직전2차 완료라는 실황 순서가 아닙니다.\nB=https://www.youtube.com/watch?v=GtC5-b4QXec&t=6419s\n[구슬=전직 티끌] 이 전직으로 얻는 고결한 방어막이 버프 줄의 빨강·초록·파랑 티끌을 쌓습니다. 힘 티끌(빨강)=최대 생명력+2%/개, 민첩(초록)=방어도·회피·에너지 보호막+5%/개, 지능(파랑)=생명력·마나 재생+5%/개. 1.55초마다 무작위로 얻고 피격 시 하나 잃습니다. 전투 중 최대 생명력·보호막이 오르내리는 원인이며 서포트 젬이 아닙니다. D 05:21:46 툴팁.\nhttps://www.youtube.com/watch?v=39kHWKUhwhU&t=19306s',
  'Boots1':'[철 룬 삽입=방어구] 첫날 오후 킹스마치 대장간에서 기본 철 룬(요구 레벨15·방어구 방어도/회피/에너지 보호막 16%)을 방어구에 박습니다(자막 B 02:39:30 "철룬 박아 줘야죠"). 철 룬은 방어 목적이며, C의 상위 철 룬(요구30·무기/방어 겸용)도 같은 계열입니다. 장화 후보는 론 문자 발자취 직공 레깅스입니다.\nhttps://www.youtube.com/watch?v=GtC5-b4QXec&t=9576s',
  'BodyArmour1':'A 02:37:54~02:38:16, 23레벨: 카발라 뒤 일반+2·무기 세트+2 보상 알림. 기존 일반 노드2개 환불652골드 후 세트 I에 유탄 피해12% 한 개→재사용 대기시간 회복 속도15% 세 개를 배정했습니다. 일반1·I0(4)·II4(4), 골드11944가 남습니다. 척탄병 큰 노드는 아직 미배정입니다. 이 주석만으로 전체 트리 순서나 내부 노드 ID 대응이 검증된 것은 아닙니다.\nhttps://www.youtube.com/watch?v=zKJQyBm4VnI&t=9474s'},
 {'Weapon1':'가이드의 투사체 레벨+2는 목표이며 실제 포격 석궁 제작 성공 옵션으로 복사하지 않습니다.\nA 03:36:36.5~03:36:39 일반 엑잘티드1개로 물리21%+정확도30 복합 접두 추가. 최종 힘+6·동일 무기 이름·세트I 장착은 C 01:14:25 툴팁에서 확인했습니다. 전환 때 화염 피해가 있어 벗고 C 01:19:15 보관했던 합금 석궁(화염 추가 없음·투사체+2·힘16)으로 임시 대체합니다. 포격 베이스의 유탄 투사체+1은 없습니다.\nhttps://www.youtube.com/watch?v=C_tkSubXWDk&t=4465s\nhttps://www.youtube.com/watch?v=C_tkSubXWDk&t=4755s\n가스 신중 III는 A 03:38:00 등급 제약, A 03:56:40 세 번째 칸 비어 있음.\n52레벨 화염파Lv13 요구 지능92를 실제로 맞췄으며 준비 패시브 수정 구간 골드100175→49779(순감소50396), 일반20포인트는 남았습니다. 본체 퀄리티0→20%·추가4%, G창 화염파II·함성I·기름I 수정은 별도 실행입니다.\nhttps://www.youtube.com/watch?v=C_tkSubXWDk&t=4725s\nhttps://www.youtube.com/watch?v=C_tkSubXWDk&t=5460s\nhttps://www.youtube.com/watch?v=C_tkSubXWDk&t=5794s\n[세트II 지팡이] 첫 지팡이 구매는 D 00:39:31(키메라의 몰이 막대). 이후 세트II는 용의 돛대 - 차임벨 지팡이로 갈아탔습니다(F 00:40:00 툴팁: 모든 주문 스킬 레벨+5, 동결 축적78% T1, 상태 이상 강도56% T1, 피해47%를 추가 화염으로 획득). 무기 세트 전용 옵션은 세트II에만 넣어야 유탄 쪽에서 헛돌지 않습니다. 용의 돛대 획득 순간은 방송에 안 잡혀 9/8~9/9 사이 오프스트림 구매로 추정합니다.\nhttps://www.youtube.com/watch?v=rsKbeELo0TM&t=2400s',
  'Helm1':'[투구 실지불가] 거래소 즉시 구입 매물은 아이템당 1 엑잘티드 오브 + 골드 수수료(약10737~11314)입니다(C 02:30:00). 요구 레벨이 빨간 매물은 당시 착용 불가. 9/8에는 방어440+·ES127+ 조건으로 업그레이드하며 가격이 25 엑잘티드 또는 1 신성한 오브(수수료 3만~4만 골드)로 뜁니다(E 02:30:00). 후반 예산은 신성한 오브 단위입니다.\nhttps://www.youtube.com/watch?v=C_tkSubXWDk&t=9000s\nhttps://www.youtube.com/watch?v=xnREtaV3m1A&t=9000s',
  'Charm1':'[호신부] 토파즈 호신부(번개 저항+25%, 명중으로 번개 피해를 받을 때 자동 사용, 지속4초). 하드코어 번개 피해 대응 소모품입니다.\nhttps://www.youtube.com/watch?v=rsKbeELo0TM&t=3300s',
  'Boots1':'실제 첫날은 이동속도15% 장화를 벗고 이속 없는 악마 질주 털가죽 레깅스를 구매·장착했습니다. 가격1엑잘티드+3211골드. 방어도41→108·ES15→38·저항 증가와 이속15%/냉각 지속 감소39% 손실을 함께 비교합니다.\n이후 룬 생명력60·엑잘티드1개 요구사항15% 감소·훼손 공개 방어도/ES23%를 추가. 이속 필수라는 실황 단정은 제거합니다.\nhttps://www.youtube.com/watch?v=GtC5-b4QXec&t=2022s',
  'BodyArmour1':'변이하는 별은 가이드 목표입니다. 첫날은 희귀 망각 망토, 다음 방송47레벨 의식 헌정품에서 고유 확보 후 C 00:25:37 장착입니다.52레벨 전환 전에 확보한 실제 경로이며 모두의 고정 획득 조건은 아닙니다.\n같은 마을 전후: 생명력1021→954·ES443→482·생명력 재생2.7→30.5·ES 재충전64.2→104.8. 기존 갑옷의 생명력67·화염저항30%·번개7%·카오스12% 옵션을 잃습니다. 표시 저항은 화염75→59%·번개75→75%·카오스12→0%입니다. 상한 표시가 같아도 번개7% 손실은 있습니다. 고유는 품질6%·증강물 방어도/ES18% 상태입니다. 가격·정확한 재료 수량은 미확인입니다.\nhttps://www.youtube.com/watch?v=C_tkSubXWDk&t=1531s\nhttps://www.youtube.com/watch?v=C_tkSubXWDk&t=1535s\n[57레벨 장착 옵션] C 02:32:52 변이하는 별 - 성직자 법의 툴팁: 퀄20%·방어도646·ES189·요구45/41힘/41지능, 방어도및ES144%, ES재충전58%, 1초당 생명력27.9 재생, 점화 지속39% 감소(점화 빌드엔 역상성), 출혈 지속34% 감소.\n[9/9 라이브 전환] 이후 검은화염 계약 키스톤(화염 피해100%를 카오스로 전환, F 00:01:15 선택)으로 카오스 빌드가 되고, 발동 메타 스킬이 회피 구르기 시 시전→원소 상태 이상 시 시전(에너지 유지·무한한 에너지 II 보조)으로 바뀌며 회오리·절망이 추가됩니다. 상세는 planner/임성빈_빌드플래너_업데이트.md.\nhttps://www.youtube.com/watch?v=C_tkSubXWDk&t=9172s',
  'Gloves1':'B 02:38:06~10 새 갈고리 수갑으로 교체: 방어도+102·ES+35·민첩+11, 기존 회피23·명중 생명력4·번개저항20%·마나31·공격 원소 추가 피해 상실. 현재 장갑은 가이드 예시와 구분합니다.\nhttps://www.youtube.com/watch?v=GtC5-b4QXec&t=9486s'},
]

def read(p): return json.loads(p.read_text(encoding='utf-8'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def without_notes(d):
    d=copy.deepcopy(d); d.pop('name',None)
    for s in d['inventory_slots']:s.pop('additional_text',None)
    return d

def build_report(root,o,now):
    game=Path.home()/'Documents/My Games/Path of Exile 2/BuildPlanner'
    audit=[];copies=[];out=o/'planner';out.mkdir(exist_ok=True)
    lines=['## 실제 build_planner 및 게임 폴더 대조','',
      '저장소의 HC 이름 사본5개, 그에 대응하는 보존 원본5개, 게임 BuildPlanner에 있는 제작자 원본4개를 파일 내용으로 대조했다. 게임 UI를 열어 확인한 것은 아니다. 게임 폴더의4개는 보존 원본과 바이트 단위로 동일했다. HC 이름 주석 사본5개는 현재 게임 폴더에 없다.','',
      '| 저장소 사본 | 보존 원본 대비 | 현재 게임 폴더 |','|---|---|---|']
    for i,(repo_name,source_name) in enumerate(PAIRS):
        p=root/'build_planner'/repo_name;s=root/'.tmp/seongbin'/source_name
        a,b=read(p),read(s);g=game/source_name
        diff=[k for k in sorted(a.keys()|b.keys()) if a.get(k)!=b.get(k)]
        note_only_slots=len(a['inventory_slots'])==len(b['inventory_slots']) and all(
            {k:v for k,v in x.items() if k!='additional_text'}=={k:v for k,v in y.items() if k!='additional_text'}
            for x,y in zip(a['inventory_slots'],b['inventory_slots']))
        assert a['skills']==b['skills'] and a['passives']==b['passives']
        assert note_only_slots
        installed={'path':str(g),'exists':g.exists(),'sha256':sha(g) if g.exists() else None,
                   'same_bytes_as_source':g.exists() and g.read_bytes()==s.read_bytes()}
        row={'repository_file':p.relative_to(root).as_posix(),'repository_sha256':sha(p),
             'original_file':s.relative_to(root).as_posix(),'original_sha256':sha(s),
             'different_top_level_fields':diff,'skills_equal':True,'passives_equal':True,
             'inventory_structure_equal':note_only_slots,'installed_original':installed,
             'installed_annotated_copy_exists':(game/repo_name).exists(),
             'repository_content':a}
        audit.append(row)
        lines.append(f'| {repo_name} | 스킬·트리 동일. 차이: '+', '.join(diff)+f" | {'제작자 원본 동일' if installed['same_bytes_as_source'] else '해당 원본 없음'} |")
        if i>=3:continue
        new=copy.deepcopy(a);new['name']=a['name']+' - 연구대조'
        for slot in new['inventory_slots']:
            base=slot.get('additional_text','').split('— 방송 —')[0].rstrip()
            note=NOTES[i].get(slot['inventory_id'])
            if note:base+='\n— 원본 대조 —\n'+note
            if base:slot['additional_text']=base
            else:slot.pop('additional_text',None)
        dest=out/f'DAY1_{i+1}_Seongbin_reviewed_notes.build'
        dest.write_text(json.dumps(new,ensure_ascii=False,indent=2),encoding='utf-8')
        actual=read(dest);assert actual==new and without_notes(actual)==without_notes(a)
        copies.append({'file':dest.relative_to(o).as_posix(),'sha256':sha(dest),
                       'source':p.relative_to(root).as_posix(),'name':new['name'],
                       'changes':'name and inventory additional_text only; prior broadcast annotations replaced with verified-stage notes',
                       'skills_passives_inventory_structure_unchanged':True,'in_game_open_verified':False})
    result={'checked_utc':now,'files':audit,'research_copies':copies,
            'source_files_modified':False,'installed_files_modified':False,
            'scope':'Local .build parsing and field comparison. Does not prove live guide currency or game UI acceptance.'}
    (o/'planner_crosscheck.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    lines += ['','## 플래너 목표와 첫날 실황의 차이','',
     '| 항목 | 플래너/기존 주석 | 원본 대조 결과 |','|---|---|---|',
     '| ACT1 가스 | 다중 사격+원소 병기 | A 5393.5초에서 I+I 연결 확인. 원소 병기 다음 다중 사격 순서. 앞서 폭발·섬광에서 보조를 뺀 흔적은 없음. [완료 직후](mcp_session/A_5393.5.png) |',
     '| ACT2 보조 | 다중 사격 II·원소 병기 II | 첫 도입은 I+I. II 실제 승급 시각 미확인. level_interval은 캐릭터 단계 표시이며 젬 등급이 아님 |',
     '| ACT2 전직 | 고결한 방어막, 주석의 바이퍼 직전2차 | 실제 혼돈 후 미덕의 정수→세케마 후 고급 마석학. 계획·목표와 실행 순서를 분리. [큰 노드](mcp_session/B_6995.75.png) |',
     '| ACT2 세트 경로 | 단계별 최종 트리 | A9474~9496에서23레벨의 두 노드 환불652골드·세트I 네 노드 적용을 확인. 척탄병은 미배정, II 네 포인트는 미사용. 전체 트리 순서는 여전히 확인 중. [적용](mcp_session/A_09496.png) |',
     '| ACT3/4 신중 | 가스3보조 목표 | A 13080초 III 요구 확인, A 14200초 가스 세 번째 칸 비어 있음. 신중을 확보 전부터 요구하지 않음 |',
     '| ACT3/4 석궁 | +2 투사체 스킬 목표 | 실제 포격은 힘+6 타협, C4465초 최종 장착 툴팁 확인. 전환 때 화염 추가 없는 합금 석궁으로 임시 대체해 포격 베이스의 투사체+1을 포기 |',
     '| ACT3/4 장화 | 이동속도가 없으면 안 된다는 이전 주석 | 실황은 이속15%를 포기한 방어·저항 교체. [교체 손익](첫날_상세분석.md) |',
     '| ACT3/4 갑옷 | 변이하는 별 목표 | 첫날 희귀→다음 날47레벨 의식 헌정품 획득·장착. 생명력67·저항 옵션 손실과 방어/ES·재생 이득을 확인.52레벨 전환 전에 확보한 시점 차이 |',
     '| 실캐릭 Lv61·엔드게임 | 화염파4보조·5보조와 후기 장비 | 서로 다른 스냅샷/목표. 첫날과52레벨 최초 연결을 자동으로 채우는 근거가 아님 |',
     '|52레벨 전환 실행|Interludes / End Game 참고|실제 지능47→92·준비 패시브 골드 순감소50396, 일반20포인트 미사용. 퀄리티0→20% 및 스킬별 세트 지정 오류를 따로 수정. [전후](다음방송_전환분석.md)|',
     '', '## 연구용 주석 교정 사본','',
     '첫날3단계의 연구용 사본을 별도 출력했다. 예전 자동 자막 해석 주석 블록을 제거하고 위에서 대조한 시점·차이·한계를 장비 칸에 적었다. 제작자 스킬·트리·장비 구조는 유지했으므로 실제 육성 순서를 모두 재현하는 완성 플래너는 아니다. 원본과 게임 설치본은 보존한다.']
    for c in copies:lines.append(f"\n- [{c['name']}]({c['file']})")
    lines += ['','JSON 재파싱과 이름·additional_text 이외 필드 불변 검사를 통과했다. 게임에서 열기·적용 검증은 하지 않았다. [파일별 해시·필드 비교·기존 주석 원문](planner_crosscheck.json).']
    return '\n'.join(lines),copies
