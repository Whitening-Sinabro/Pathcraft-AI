"""Render the inherited research and explicit resume verification into local reports."""
from pathlib import Path
from collections import Counter
import datetime, hashlib, html, json, re, sys
import markdown
import findings, later_findings, report_text, precision_findings, stash_notes, review_updates, planner_crosscheck, research_focus

sys.stdout.reconfigure(encoding='utf-8')
O=Path(__file__).resolve().parent
ROOT=O.parents[1]
NOW=datetime.datetime.now(datetime.timezone.utc).isoformat()
KST=datetime.timezone(datetime.timedelta(hours=9))
A,B,C='zKJQyBm4VnI','GtC5-b4QXec','C_tkSubXWDk'
D,E='39kHWKUhwhU','xnREtaV3m1A'
IDS=[A,B,C,D,E,'rsKbeELo0TM']
RESUME_WINDOWS={A:[(10,80),(2020,2170),(12180,12370),(12890,13140)],B:[(6300,6500),(7580,7650),(8890,8980)],C:[(1430,1570),(4320,4480),(5010,5160),(5480,5840)]}
def dump(name,obj):
    (O/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')
def load(path):return json.loads(path.read_text(encoding='utf-8'))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def sec(s):
    h,m,s=map(int,s.split(':'));return h*3600+m*60+s
def hms(t):
    if t is None:return '미확정'
    whole=int(t)
    fraction=(f'{t-whole:.3f}'[1:].rstrip('0') if t!=whole else '')
    return f'{whole//3600:02}:{whole//60%60:02}:{whole%60:02}'+fraction
def url(v,t=0):return f'https://www.youtube.com/watch?v={v}&t={int(t)}s'
def localtime(s):return datetime.datetime.fromisoformat(s).astimezone(KST).isoformat()
def cell(s):return str(s).replace('|','／').replace('\n','<br>')

# 2026-09-10 실제 MCP 브라우저 player에서 읽은 영상 길이. D·E는 기존 메타데이터와 일치했고 F는 기존이 None이라 이 값으로 채운다.
PLAYER_DURATION={'39kHWKUhwhU':22926.421,'xnREtaV3m1A':15695.201,'rsKbeELo0TM':9526.541}
metadata=[]
for v in IDS+['i6_tfxyQfeQ']:
    m=load(O/'sources'/f'{v}.metadata.json')
    player=load(O/'sources'/f'{v}.player.json')
    live=player.get('microformat',{}).get('playerMicroformatRenderer',{}).get('liveBroadcastDetails',{})
    m.update(start_kst=localtime(live['startTimestamp']) if live.get('startTimestamp') else None,
             end_kst=localtime(live['endTimestamp']) if live.get('endTimestamp') else None,
             classification='guide' if v=='i6_tfxyQfeQ' else ('first_day' if v in [A,B] else 'later_broadcast'),
             start_level_verified=None,end_level_verified=None,
             note='메타데이터 수집 당시 상태. 업로드 시각·방송 시작 시각·영상 길이를 구분한다.')
    if m.get('duration') is None and v in PLAYER_DURATION:
        m['duration']=int(PLAYER_DURATION[v])
        m['duration_source']='기존 메타데이터는 길이 미확정. 2026-09-10 실제 MCP 브라우저 player의 video.duration을 읽어 채웠다.'
    elif v in PLAYER_DURATION:
        m['duration_player_check']=PLAYER_DURATION[v]
    metadata.append(m)
dump('방송목록.json',{'generated_utc':NOW,'timezone':'Asia/Seoul','videos':metadata,'missing':'공개 목록 외 삭제·비공개 방송의 존재 및 전체 채널 완전성은 미확인'})

observations=[]
for n,(v,interval,category,finding,limit) in enumerate(findings.ROWS+later_findings.ROWS,1):
    start,end=map(sec,interval.split('-'))
    segments=load(O/'transcripts'/f'{v}.json')['segments']
    matches=[i for i,r in enumerate(segments) if r['start']<=end and r['start']+r.get('duration',0)>=start]
    assert matches,(v,interval)
    observations.append({'id':f'CAP-{n:03}','video_id':v,'start_seconds':start,'end_seconds':end,'url':url(v,start),
        'category':category,'observation':finding,'limitation':limit,'evidence_type':'automatic_caption_context',
        'confidence':'자막 문맥 검토; 음성 재청취 및 실행 확정 아님',
        'provenance':'이전 세션 findings.py / later_findings.py의 검토 기록을 보존',
        'resume_context_rechecked':any(a<=end and b>=start for a,b in RESUME_WINDOWS.get(v,[])),
        'caption_file':f'transcripts/{v}.json','caption_segment_indices':matches,'execution_verified':False})

VISUALS=[
 (A,1080,1250,'frames/day1_ritual.jpg','젬 메뉴 → 의식 전투 → 보상과 인벤토리 → 마을 상점·보관함 → 젬 메뉴 순서를 읽었다.','개별 옵션·소켓 보조명·가격·확정 클릭 미판독'),
 (B,710,820,'frames/crossbow_reveal.jpg','공개 선택 메뉴, 인벤토리 툴팁 비교, 메뉴 종료 후 이동이 보인다.','힘 선택·투사체 레벨 실패는 자막 근거. 옵션과 화폐는 화면에서 확정하지 못함'),
 (B,6300,6540,'frames/ascendancy.jpg','1:46:20~30 전직 선택 메뉴, 이후 패시브/인벤토리, 1:48:40 로딩 화면을 읽었다.','선택 노드·포인트 숫자 미판독. 세케마 복귀 목적은 자막으로 대조'),
 (C,1420,1630,'frames/mutable_star.jpg','의식 보상·갑옷 비교 후 마을 장비와 캐릭터 수치 창이 이어진다.','고유 이름·공물 비용·생명력/저항 손익 수치는 미판독'),
 (C,5670,5840,'frames/weapon_assignment.jpg','전투 후 1:36:30~40 스킬 목록과 세부 설정 화면으로 전환한다.','I/II 체크와 보조명은 미판독. 1:36:34~44 자동 자막에 화염파 II·함성 I·기름 I 정정이 있음'),
 (C,8970,9210,'frames/helmet_trade.jpg','투구 매물 검색 후 2:31:10 교환 패널로 보이는 창, 이후 보관함·장비 툴팁을 읽었다.','결제 가격·확정 클릭·장착 전후 수치는 미판독'),
 (A,0,1750,f'storyboards/{A}/survey_00000.jpg','초기 로그인/대기열 → 캐릭터 선택 → 해변 진행 → 전투와 메뉴를 읽었다.','70초 간격 표본. 정확한 최초 레벨과 모든 행동은 미판독'),
 (A,5400,7150,f'storyboards/{A}/survey_05400.jpg','1:39~1:41대 원형 전장의 보스전, 1:42:50 젬 메뉴와 이후 이동을 읽었다.','70초 간격이므로 입력 순서·회피 성공·처치 정확한 초는 확정하지 못함'),
 (C,10800,11850,f'storyboards/{C}/survey_10800.jpg','후반 패시브 창, 3:12:50 은신처 지도 장치 패널과 이후 지도 선택을 읽었다.','모든 퀘스트 회수·최종 레벨·목표 지도 티어 달성은 미확인')]
visuals=[]
for n,(v,a,b,path,finding,limit) in enumerate(VISUALS,1):
    player=load(O/'sources'/f'{v}.player.json')
    spec=player['storyboards']['playerStoryboardSpecRenderer']['spec'].split('|')[-1].split('#')
    assert spec[:6]==['320','180',spec[2],'3','3','10000']
    visuals.append({'id':f'VIS-{n:03}','video_id':v,'start_seconds':a,'end_seconds':b,'url':url(v,a),'file':path,
        'sha256':sha(O/path),'observation':finding,'limitation':limit,'evidence_type':'storyboard_visual_review',
        'reviewer':'Codex /root, resumed session','reviewed_utc':NOW,'source_tile_resolution':[320,180],
        'source_interval_seconds':10,'selection_interval_seconds':70 if 'survey_' in path else 10,
        'time_precision':'공개 storyboard 명세로 계산한 근사 시각; 연속 영상과 프레임 단위 동기화는 미검증',
        'execution_numbers_verified':False})
previous_path=O/'원본_화면대장.json'
previous_frames={r['id']:r for r in load(previous_path)['frames']} if previous_path.exists() else {}
precise=[]; revisions=[]
assert len({(r[0],r[1]) for r in precision_findings.ROWS})==len(precision_findings.ROWS),'duplicate original-frame key'
for n,(v,t,finding,kind,limit) in enumerate(sorted(precision_findings.ROWS,key=lambda r:(IDS.index(r[0]),r[1])),1):
    prefix={A:'A',B:'B',C:'C',D:'D',E:'E','rsKbeELo0TM':'F'}[v]
    file=f'mcp_session/{prefix}_{t:05}.png'
    frame_id=f'FRAME-{prefix}-{t:05}'
    original_finding,original_limit=finding,limit
    correction=review_updates.CORRECTIONS.get((v,t))
    if correction:
        new_finding,limit,reason,evidence=correction
        finding=new_finding or finding
        revisions.append({'frame_id':frame_id,'original_observation':original_finding,'original_limitation':original_limit,
                          'current_observation':finding,'current_limitation':limit,'reason':reason,
                          'evidence':[{'video_id':ev,'seconds':et,'url':url(ev,et)} for ev,et in evidence]})
    precise.append({'id':frame_id,'video_id':v,'start_seconds':t,'end_seconds':t,'url':url(v,t),'file':file,
        'sha256':sha(O/file),'observation':finding,'evidence_type':'original_video_frame_review','verification_class':kind,
        'limitation':limit,'source_resolution':[1280,720],'reviewer':'Codex /root',
        'reviewed_utc':previous_frames.get(frame_id,{}).get('reviewed_utc',NOW),
        'time_validation':'Actual Playwright MCP seek completion, currentTime, readyState and native video dimensions in response files.',
        'continuous_playback_verified':False})

frame_lookup={(r['video_id'],r['start_seconds']):r for r in precise}
event_rows=[]
for event in review_updates.EVENTS:
    event_rows.append({**event,'frames':[{'id':frame_lookup[k]['id'],'file':frame_lookup[k]['file'],'url':frame_lookup[k]['url'],'seconds':k[1]} for k in event['frames']]})
dump('교차검증_이력.json',{'generated_utc':NOW,'identity_key':['video_id','start_seconds'],
     'count_policy':'unique directly read frames; repeated reading is not a new frame; events have separate stable IDs',
     'inherited_93_backup':'session_backups/resume_20260909T164134Z/원본_화면대장.json',
     'revisions':revisions,'events':event_rows})
dump('원본_화면대장.json',{'generated_utc':NOW,'frames':precise})
dump('확인대장.json',{'generated_utc':NOW,'status':'partial_research_original_video_available','observations':observations,'visual_reviews':visuals,'original_video_frame_reviews':precise,
    'resume_caption_review_windows':RESUME_WINDOWS,'inherited_later_caption_review_windows':later_findings.REVIEW_WINDOWS,
    'audio_relistened_seconds':0,'full_resolution_video_verified_seconds':None,'original_video_reviewed_frame_count':len(precise),
    'coverage_note':'자막 확보, 이전 세션 검토, 이번 재검토, 미리보기 화면 판독을 별도로 기록. 캡처 생성 수를 검토 수로 세지 않는다.'})

def timeline(videos):
    followups={'CAP-078':'후속 원본 확인:47레벨 보상 소지·장착과 갑옷 손익은 해결. 지불 가격·제작 재료 개수만 미확정. [현재 결과](다음방송_전환분석.md).',
               'CAP-081':'후속 원본 확인: 지능47→92·패시브 준비 골드 순감소50396·일반20포인트 남음·보관한 합금 석궁 임시 장착. [현재 결과](다음방송_전환분석.md).',
               'CAP-083':'후속 원본 확인: 화염파Lv13 본체 퀄리티0→20%·추가4% 유지, 최종 단계당 상태 이상 강도48% 확인. 총 재료 차감은 미확정. [현재 결과](다음방송_전환분석.md).',
               'CAP-084':'후속 원본 확인: 화염파II·함성I로 실제 체크 해제, 기름I 및 세트별 정신력13/43 확인. [현재 결과](다음방송_전환분석.md).'}
    lines=['아래 내용·한계는 초기 자막 검토 기록이다. 이후 원본으로 해결한 항목은 후속 확인을 덧붙였으며 상세 본문의 최신 판정을 우선한다.','', '| 영상·시각 | 내용 | 초기 한계·후속 확인 |','|---|---|---|']
    for r in observations:
        if r['video_id'] not in videos:continue
        t=hms(r['start_seconds'])+'~'+hms(r['end_seconds'])
        current=followups.get(r['id'],'')
        lines.append(f"| [{r['video_id']} {t}]({r['url']}) · {r['id']} | **{cell(r['category'])}** — {cell(r['observation'])} | {cell(r['limitation'])} {'<br>**'+current+'**' if current else ''} |")
    return '\n'.join(lines)

status='''**플래너와 크게 다른 실제 선택과 플래너에 없는 실행 정보를 우선 조사한다.** 원본 720p 화면 관찰·자동 자막·미리보기 기록을 구분한다. 기본 연결의 전수 재확인은 필수 완료 조건에서 제외했으며, 전환 조건·거래와 제작·교체 손익 등 핵심 검증은 진행 중이다. [핵심 차이와 실전 보완](핵심차이_실전보완.md) · [원본 정밀 확인](원본_정밀확인.md) · [남은 항목](미확인_항목.md).
'''
docs={
 '첫날_상세분석':report_text.DAY1.format(status=status,timeline=timeline([A,B])),
 '다음방송_전환분석':report_text.NEXT.format(status=status,timeline=timeline([C])),
 '후속방송_추가조사':report_text.FOLLOW.format(timeline=timeline([D,E])),
 '단계별_따라하기':report_text.HOWTO}
# Anchor the actual correction instead of linking only to the earlier suspicion.
docs['다음방송_전환분석']=docs['다음방송_전환분석'].replace('## 투구 거래와 자원 손익',
    '정정 발언의 더 정확한 위치는 **01:36:34~01:36:44**다. 앞의 01:31대는 세팅을 의심하는 구간이다. [화염파 II·함성 I·기름 I 정정](https://www.youtube.com/watch?v=C_tkSubXWDk&t=5794s). 이번에 원자막을 재대조했다.\n\n## 투구 거래와 자원 손익')
docs['단계별_따라하기']=docs['단계별_따라하기'].replace('t=5510s','t=5794s')

lines=['# 방송목록','', '방송 시작은 한국 시각(KST)이다. 공개 영상의 업로드 날짜 대신 player의 liveBroadcastDetails.startTimestamp를 사용했다. 방송 길이는 보관 VOD 길이로, 시작/종료 벽시계 차이와 몇 초 다를 수 있다.','',
 '| 순서 | 시작 KST | 길이 | 방송 | 처리 범위 |','|---|---|---|---|---|']
for i,m in enumerate(metadata,1):
    v=m['id']; scope='첫날 자막 분석·선별 미리보기' if v in [A,B] else '전환 자막 분석·선별 미리보기' if v==C else '일부 자막 문맥 검토' if v in [D,E] else '원본 선별 판독 착수' if v=='rsKbeELo0TM' else '기존 가이드·플래너 대조'
    if any(r['video_id']==v for r in precise):scope+='·원본 선별 판독'
    lines.append(f"| {i if v!='i6_tfxyQfeQ' else '가이드'} | {m['start_kst'] or ('업로드 '+m['upload_date'])} | {hms(m['duration'])} | [{cell(m['title'])}]({m['webpage_url']})<br>{v} | {scope} |")
lines+=['','첫날 합계 **'+hms(sum(m['duration'] for m in metadata if m['id'] in [A,B]))+'**. 첫날 재개 방송의 33레벨은 발언 근거이며, 시작·종료 레벨 전체를 화면으로 확정하지 않았다.','',
 '채널 ID `UCvj_myZNbqdHBBFT2IjKJWw`, 채널명 `임성빈 POE2 하드코어`. 캐릭터 이름의 방송별 동일성·사망/재시작 여부 전체를 아직 확정하지 않았다. 현 조사에서는 무관한 옛 빌드를 합치지 않았다.','',
 '9월 9일 영상은 수집 시점에 진행 중이었다. 이 문서 작성 순간에도 계속 생방송이라고 보장하지 않는다. 삭제·비공개 방송이 없는 완전한 목록인지도 미확인이다.','',
 '[원 메타데이터](방송목록.json) · [공개 채널 목록 스냅샷](sources/channel_streams.json)']
docs['방송목록']='\n'.join(lines)
coverage_snapshot=load(O/'sources/channel_streams_20260910.json')
public_entries=coverage_snapshot['data'].get('entries',[])
frame_counts=Counter(r['video_id'] for r in precise)
coverage_lines=['## 실제 확보·검토 범위','',
    f"공개 라이브 목록을 {coverage_snapshot['retrieved_utc']}에 다시 조회해 **{len(public_entries)}편**을 받았다. 반환된6개 ID는 모두 기존 조사 목록에 있다. 목록 확보는 전체 영상 다운로드·전체 시청·내용 검증 완료를 뜻하지 않는다. 삭제·비공개 자료까지 포함한 과거 전체 아카이브의 완전성은 보장하지 않는다. [최신 목록 원자료](sources/channel_streams_20260910.json).",'',
    '| 방송 | 목록 | 자막 검토 | 직접 읽은 원본 화면 | 남은 핵심 |','|---|---|---|---:|---|']
coverage_stages={A:('첫날 오전','주요 구간 문맥 검토','핵심 차이 보완'),B:('첫날 오후','주요 구간 문맥 검토','동일 조건 무기 손익 등'),C:('다음 날 전환','전환 구간 문맥 검토','초기 보조·거래·세트 운용'),D:('9월7일','일부 변경 구간','지팡이·주얼·성유 원본'),E:('9월8일','일부 변경 구간','검은 화염 전환 원본'),'rsKbeELo0TM':('9월9일','원본 선별 판독 착수','검은 화염파 전환 상세·전체 흐름')}
for v,(label,caption_stage,remaining) in coverage_stages.items():
    coverage_lines.append(f'| [{label}]({url(v)}) | 확보 | {caption_stage} | {frame_counts[v]} | {remaining} |')
coverage_lines += ['',f"원본 **{len(precise)}건**은 서로 다른 시각의 정지 화면 수다. 연속 전체 시청·전투 재생 시간으로 환산하지 않는다. 자막 관찰110건·미리보기9개와 별도로 센다. 9월9일 영상은 최신 공개 목록에서 종료된 방송(was_live), 길이9527초로 표시된다. 이전 수집의 길이 미확정 메타데이터는 보존했다."]
coverage='\n'.join(coverage_lines)
docs['방송목록']+='\n\n'+coverage

planners=load(O/'sources/planner_parsed.json')
planner_audit=[]
lines=['# 플래너와 실황 대조','','이 표는 저장된 원본 파일 5개를 다시 JSON 파싱해 대조한 것이다. 가이드의 목표 연결, 과거 Lv61 스냅샷, 이번 방송에서 실제 실행한 연결은 다르다. `level_interval`을 젬 등급으로 읽지 않는다. `Two`·`Three`가 포함된 ID는 그대로 보존했다. 원본 파일명/표시명의 일부 깨진 글자도 기존 자료에 있던 상태다.','',
 'ACT2 가이드에는 전직 스킬이 있지만 첫날 오전 실황은 전직을 미뤘다. 후기 가이드에는 화염파 5보조가 있지만 Lv61 스냅샷은 4보조이며 격노 벼림이 없다. 이 차이를 실제 소켓 해제 시각이나 획득 순서로 소급하지 않는다.','']
for index,p in enumerate(planners):
    source=ROOT/p['source'];actual=load(source);assert actual==p['content']
    label=['ACT 1','ACT 2','ACT 3/4','막간·엔드게임 가이드','과거 Lv61 공개 스냅샷'][index]
    passives=actual.get('passives',[])
    counts=Counter(x.get('weapon_set','공통/미지정') for x in passives)
    planner_audit.append({'source':p['source'],'sha256':sha(source),'matches_saved_parse':True,'passive_rows':len(passives),'passive_unique_keys':len({(x['id'],str(x.get('weapon_set'))) for x in passives}),'skill_count':len(actual['skills'])})
    lines += [f'## {label}','',f'패시브 레코드 {len(passives)}개, 세트 필드별 레코드 {dict(counts)}. 중복 레코드가 있으므로 이 수를 사용 포인트로 해석하지 않는다.','',
      '| 스킬 ID | 플래너 표시 레벨 구간 | 연결 보조 ID | 스킬 세트 필드 |','|---|---|---|---|']
    for s in actual['skills']:
        name=s['id'].split('/')[-1].replace('SkillGem','')
        supports=' + '.join(x['id'].split('/')[-1].replace('SupportGem','') for x in s.get('support_skills',[])) or '없음'
        lines.append(f"| {name} | {s.get('level_interval','없음')} | {supports} | {s.get('weapon_set','없음')} |")
    lines+=['']
lines+=['## 적용 판단','','스킬별 세트 필드가 없다는 이유로 모두 공통 사용 또는 자동 전환이라고 해석하지 않는다. 실황의 G 설정·세트별 패시브 화면을 따로 검증해야 한다. 완전한 초기 트리·젬 이동표 재구성은 보류했다. 아래 연구용 사본은 대조가 끝난 주석만 교정하고 스킬·트리·장비 구조를 유지한다.','',
 '9월 9일 별도 공개 캐릭터 조회에는 레벨 90이 기록돼 있다. 데이터 갱신은 11:58:34 UTC, 수집은 12:39:11 UTC이며 실시간 생존 증거가 아니다. Lv61 비교표와 섞지 않는다. [조회 기록](sources/character_retrieval.json).','',
 '[원본 파싱·해시 확인](planner_source_validation.json) · [기존 파싱 내용](sources/planner_parsed.json)']
docs['플래너_대조']='\n'.join(lines)
planner_appendix,research_copies=planner_crosscheck.build_report(ROOT,O,NOW)
docs['플래너_대조']+='\n\n'+planner_appendix
dump('planner_source_validation.json',{'checked_utc':NOW,'files':planner_audit,'generated_modified_build_files':research_copies,'game_installation_modified':False})

lines=['# 화면 확인 기록','','아래 9개 이미지 표는 이번 재개 세션에서 직접 읽었다. 각 칸은 320×180이며, 원본 재생 영상이 아니다. 10초 storyboard 간격은 공개 player 명세와 대조했다. 정확한 클릭 시각·옵션 수치는 이 해상도로 보장할 수 없다.','']
for r in visuals:
    lines += [f"## {r['id']} · {r['video_id']} {hms(r['start_seconds'])}~{hms(r['end_seconds'])}",'',r['observation'],'',f"한계: {r['limitation']}",'',f"[원영상 위치]({r['url']})",'',f"![{r['id']} 화면 표]({r['file']})",'']
docs['화면_확인기록']='\n'.join(lines)

docs['핵심차이_실전보완']=research_focus.REPORT
docs['미확인_항목']=research_focus.PENDING

docs['CHECKPOINT']=f'''# 임성빈 조사 재개 체크포인트

작성 UTC: {NOW}

## 목표와 현재 상태

원 요청은 [전체 조사 지시문](../../Docs/2026-09-09_SEONGBIN_DAY1_RESEARCH_REQUEST.md)이며,2026-09-10 최신 지시는 플래너와 크게 다른 선택·플래너가 담지 않는 정보에 집중하는 것이다. [핵심 차이](핵심차이_실전보완.md)를 먼저 읽는다. 기본 젬 연결·모든 패시브 클릭의 전수 확인을 완료 조건에서 제외한다. 첫날 핵심 차이는 정리됐고 다음 우선순위는 전환 조건·실제 자원·세트 작동·중요 거래 손익이다. **전체 핵심 검증은 진행 중**이다.

사용자의 명시적 인계 지시로 새 세션이 직접 조사를 이어받았다. 추가 에이전트나 감독 작업은 생성하지 않았다. 기존93건과 문서50개를 session_backups/resume_20260909T164134Z에 백업했다.

## 저장한 결과

- 첫날 2편의 시간순 자막 분석, 다음 날 화염파 전환 분석, 9월 7~8일 후속 자막 기록을 Markdown/HTML로 정리.
- 전체 자막 관찰 {len(observations)}건. 기존 기록의 출처와 이번 핵심 문맥 재검토 여부를 분리.
- 이번에 미리보기 표 {len(visuals)}개 직접 검토. 화면 해상도 320×180, 원본 시간 간격 10초를 player 명세와 대조. 전체 영상 시청·고해상도 판독으로 계산하지 않음.
- 원본 플래너5개·HC 주석 사본5개·현재 게임 폴더의 원본4개를 파일 내용으로 대조. 연구용 주석 교정 사본3개만 별도 출력했으며 원본·게임 설치본·필터는 변경하지 않음.
- 정확한 정정 위치 보강: C 01:36:34~44 화염파 II, 지옥불 함성 I, 기름 I. A 03:24대 파편탄 유지 정정, B 01:47대 세케마 복귀 정정 원자막 재대조.

## 과거 접근 실패와 현재 회복

공개 YouTube 페이지/메타데이터와 자막·storyboard는 접근할 수 있었다. 원본 파일 첫 바이트 범위는 HTTP 206이나 중간 영상 구간은 HTTP 403. 새 공개 재생 주소 갱신 후에도 동일했고, 64KiB 작은 범위도 거절됐다. 직접 ffmpeg 추출은 실패. 별도 Playwright Python + headless Edge에서 B 01:46:10 이동은 준비 상태 0·영상 시간 0·길이 미정과 플레이어 오류 화면으로 끝났다. 로그인 제한을 우회하거나 다른 사용자 브라우저를 조작하지 않았다.

접근 근거: [재개 검사](sources/resume_media_probe.json), [접근 실패 정리](access_validation.json), [브라우저 오류 화면](frames/GtC5-b4QXec/browser_006370.00.png). media/의 작은 .dash.mp4는 초기 헤더만 받은 실패 부산물이며 재생 자료가 아니다. 보고서에 연결하지 않았다.

위 내용은 이전 경로의 실패 기록이다. 이후 Claude 글로벌 설정의 Playwright MCP를 발견하고 Codex에도 기존 설정을 보존해 등록했다. 실제 MCP ClientSession으로 서버에 연결하여 원본 1280×720 재생, currentTime·readyState 확인과 구간 캡처에 성공했다. 로그인 링크가 보이는 상태이므로 사용자 계정 인증 성공으로 보고하지 않는다. 양쪽 공통 지침과 확인 기록은 [연결 수정 기록](../../Docs/2026-09-09_MCP_BROWSER_CONNECTION_FIX.md)에 있다.

2026-09-10 Opus 5 xhigh 세션은 새 브라우저를 띄우지 않고 request_068 비파괴 조회로 기존 브리지 응답을 먼저 확인했다(C4750초·paused·readyState4·1280×720). 이후069~079로 C01:19~02:39 구간을 캡처했다.069~070은 급습 제거·화염파 장착·보조 홈·능력치 노드,071~072는 타바카이 전투와02:22~02:33 투구 거래,073~075는 대체 반지·거래 전후,076~079는 룬·장화 최종·최대치 변동이다.073·074는 응답 키 이름이 검증기 형식과 달라075로 같은 시각을 표준 형식으로 다시 받았다.080에서 같은 탭을 D(39kHWKUhwhU, 길이22926.421초)로 이동했고081~084로 D의 지팡이 거래·장막 해제·화폐 교환·후반 제작을 캡처했다.085에서 E(xnREtaV3m1A, 15695.201초),086~088에서 F(rsKbeELo0TM, 9526.541초)로 이동해 각각 원본 판독을 시작했다. F의 길이는 기존 메타데이터가 미확정이었고 이번에 player에서 실측했다. 다음 요청은 mcp_session/의 최대 번호를 확인한 뒤089부터다. [최신 재개 체크포인트](../../Docs/2026-09-09_SEONGBIN_RESEARCH_RESUME_CHECKPOINT.md)를 우선한다.

이전 findings.py/later_findings.py는 자막 문맥 검토 기록이다. 직접 재청취 0초이며 원본 정지 화면 {len(precise)}건을 별도로 읽었다. 정지 화면 수를 연속 시청 시간으로 환산하지 않는다. 근거는 [원본 화면대장](원본_화면대장.json), [원본 정밀 확인](원본_정밀확인.md), mcp_session/response_*.json이다. 9월 9일 방송은 본문 조사 미착수.

## 이번 원본 판독에서 해결한 항목

- C52레벨 화염파 요구 지능47→92·준비 패시브 골드 순감소50396·임시 합금 석궁, 본체 퀄리티0→20%·추가4%·최종 단계당 상태 이상 강도48%, 화염파II·함성I 수정과 기름I를 확인했다. 공개 목록은 재조회한6편 모두 기존 목록에 있으나 내용 전체 검증 완료는 아니다.
- C47레벨 변이하는 별 헌정품 후보→소지→품질·증강물→장착→희귀 보관과 같은 마을 캐릭터 수치 전후를 확인했다. 생명력-67·ES+39, 화염 표시75→59%·카오스12→0%이며 번개7% 옵션 손실은75% 상한 표시로 가려진다.
- 장화 구매1엑잘티드+3211골드, 기존 이속15% 상실, 상위 육신 룬+60, 추가 엑잘티드1개의 요구사항15% 감소와 훼손 공개 방어도/ES23%를 구분했다.
- 지능32에서 투구·갑옷 비활성 → 임시37 → 총2700골드 재분배 후42를 실제 화면으로 대조했다.
- STR_INT의13·14 내부, 기존 장갑·갑옷·투구 보관을 확인했다. 이름과 실제 요구 능력치가 일치하지 않는 장비도 들어 있다.
- 첫 전직 미덕의 정수·고결한 방어막 → 세케마 뒤 고급 마석학 적용을 확인했다. B6995.75초의 큰 노드 툴팁으로 이름 미확인을 해결했다.
- A5393.5초 G창으로 가스 원소 병기 I+다중 사격 I 연결 완료, 민첩 보조 사용2→3·DPS70.3→45.7을 확인했다. A12996.5초 일반 엑잘티드 오브6/20와 이후5를 대조해1개 사용으로 복합 접두가 붙음을 확인했다.
- 동일 영상·정확한 시각을 중복 계산하지 않으며 사건별 전후 근거와 정정 이력을 교차검증_이력.json에 보존한다. 석궁의 독립 정확도 접미/여섯 속성 오독은 본문에서 정정했다.
- A9474~9496에서 카발라 뒤 일반+2·세트+2 보상, 두 노드 환불652골드, 세트I 유탄 경로4개 적용을 확인했다. 일반1·I0(4)·II4(4), 골드11944가 남았다. 척탄병은 아직 미배정이며 케스 무기 퀘스트 완료와 구분한다.
- **2026-09-10 Opus 5 xhigh 세션 추가(C 66건).** 보조 젬 사용량 상한이 능력치를 5로 나눈 몫과 두 지점에서 일치한다(민첩44·지능92·힘62 → 힘12/민첩8/지능18, 민첩64·지능92·힘92 → 힘18/민첩12/지능18). 남은20포인트가 능력치 노드로 간 이유가 여기 있다.
- 전환 직후 급습 행에 "잘못된 무기 유형입니다" 경고가 떠 곧바로 제거했고, 그 자리에 화염파Lv13을 넣었다(DPS154.4 → 보조 채운 뒤235.5). 화염파 본체는 재사용 대기시간10.00초·1초당 마나27.8·최대10단계다.
- 상위 쥬얼러 오브(보유1개)로 화염파 보조 홈을4개로 만든 뒤 하나씩 채웠다. 보조마다 요구 능력치 종류가 다르다(폭발 투사체 I +5 민첩, 범위 집중·빠른 시전 III +5 지능, 이글거리는 화염 II +5 힘).
- 지속 스킬 정신력은 하나당30이다. 재의 전령만 켰을 때 세트I 43·세트II 73, 소모를 양쪽에 켜자 세트I 13·세트II 43이고 마을 HUD도 13/73으로 맞았다. 고결한 방어막은 항상 활성화라 예약이 없다.
- 투구 거래는 조건4줄로 결과0 → 방어도 및 ES 23~35 한 줄 + 총 ES 정렬로 매물 확보였다. 매물 수수료11314 골드, 구간 골드76660→65499다.
- 전환 뒤 대체 반지 후보 세 개를 훑고 자수정 계열을 장착했다(생명력1104→1123). 저항은 화염49·냉기41·번개45·카오스0이었다.
- 상위 철 룬은 한 번 박으면 회수가 안 되고 교체만 된다. 첫날 장화의 최종 상태(퀄리티20%·생명력+60·능력치 요구사항15% 감소 등)도 확인했다.
- 최대 생명력·보호막이 같은 정신력 표시에서 크게 오르내린다.02:37:30 1512/832 → 02:37:35 1189/690으로 5초 만에 떨어졌다. 원인은 미확정이며 어떤 생명력 수치도 구간 기준값으로 쓰지 않는다.
- **D(9월7일) 추가13건.** 지팡이는 검색을 세 번 고쳐 잡았다(화염 피해72~110+시전 속도20~30 → 7건 / 시전 속도 빼고 모든 화염 주문 스킬 레벨 추가 → 25건 / 그 레벨 최소4 → 결과 없음). 실제 확보한 것은 키메라의 몰이 막대 불저항 지팡이(13레벨 태양의 보주 부여·화염 피해133%·마나+42·모든 화염 주문 스킬 레벨+4·시전 속도32%)이며 툴팁 한 줄이 장막으로 가려져 영혼의 우물에서 해제를 준비했다.
- 화폐 교환소에서 숙련공의 오브2 ⇌ 엑잘티드 오브4(비율1:2)에 수수료2000골드가 붙는다. 체결 가능 거래의 비율별 재고도 함께 읽었다.
- 9월7일 후반 장갑 제작 화면에서 아이템 레벨79·각 옵션의 티어와 범위(T2·T3)를 확인했고, 같은 방송 끝의 자원은 생명력1412·보호막1765·마나816·정신력8/100이다.
- **E(9월8일) 8건.** 89레벨 스킬 창에서 지옥불 함성·절망·회피 구르기 시 시전·원소 융합·섬광 유탄·가스 유탄을 확인했다. 원소 융합은 점유60 정신력·요구 레벨72·지능126이고 8초마다 원소가 바뀌며 해당 원소 피해58% 증폭이다. 보조 젬 사용량은 힘7/23·민첩5/13·지능13/30이었다. 가모장의 전당 도전 전에는 다른 제작자 영상으로 보스 패턴을 먼저 봤다.
- **F(9월9일) 12건 — 이번 세션에서 처음 열었다.** 제목은 검은 화염파 빌드 전환 완료이고 실제 길이는9526.541초다. 91레벨,골드45만~50만, 보호막2936~3131이 생명력1566~1910보다 크다. 전직 포인트2를 추가로 얻었고, 요구 힘108인 고유 장화는 착용하지 못했으며, 제왕의 오브 사용 때 속성 부여 공간이 없다는 경고가 떴다.
- 최대 생명력·보호막 변동은 C·D·E·F 네 방송 모두에서 나타난다. 지도 안팎 가설과 카운트다운 아이콘 가설은 각각 반례로 깨졌다. 원인 확정 전까지 어떤 생명력 수치도 구간 기준값으로 쓰지 않는다.

## 다음 재개

1. 이 체크포인트와 미확인_항목.md, 확인대장.json부터 읽고 기존 결과를 보존한다.
2. 실제 MCP 연결을 이어서 사용한다. playwright_mcp_bridge.py가 응답 파일을 생성하는지 먼저 확인하고, 응답 중인 브라우저에 경쟁하는 새 인스턴스를 띄우지 않는다. 다음 요청 번호는 mcp_session/의 최대 번호 이후로 정한다.
3. 첫날과 다음 날의 시점은 구분하되, 기본 연결·전체 노드 클릭을 끝내느라 다음 날 전환 조건 조사를 막지 않는다. 플래너와 다른 점 또는 실행 판단에 필요한 질문이 있는 구간만 좁혀 확인한다.
4. 새 원본 화면을 직접 읽으면 precision_findings.py에 시각·관찰·근거 종류·한계를 추가하고 complete_report.py를 실행한다. 미리보기 9개와 원본 정지 화면을 구분한다.
5. validate_report.py로 링크·HTML·타임스탬프·모바일 폭·원본 해시를 재검사한다. 게임 적용 검증과 문서 검증을 구분한다.

## 보조 코드

complete_report.py는 문서/대장, validate_report.py는 검증, review_updates.py는 현재 판독 정정·사건 연결, planner_crosscheck.py는 실제 플래너 필드 비교와 연구용 주석 사본, research_focus.py는 사용자 지시에 따른 핵심 차이와 우선순위를 담당한다. resume_probe.py·refresh_media.py·range_extract.py의 과거 추출 실패도 보존한다. 외부 전송·공개 게시·컴퓨터 종료는 하지 않았다.
'''

docs['index']='''# 임성빈 화염파 젬링 · 첫날부터

**플래너와 크게 다른 선택과 플래너에 없는 실행 정보를 먼저 읽는다.** 전직·전환 시점, 임시 대체, 구매·제작 비용, 교체 손익, 위험 대처를9월5일 시작→6일 전환→후속 매핑의 흐름으로 정리했다. 기본 구성의 전수 재확인은 필수 작업에서 제외했고, 전환 조건 등 핵심 검증은 진행 중이다.

[핵심 차이와 실전 보완부터 보기](핵심차이_실전보완.md)

## 읽는 순서

1. [첫날 상세 분석](첫날_상세분석.md): 오전·오후 6시간 56분 49초의 자막 검토 기록, 장비·스킬·전직 시행착오.
2. [단계별 따라하기](단계별_따라하기.md): 유탄 → 전직 준비 → 52레벨 전환의 조건부 안내.
3. [다음 방송 전환 분석](다음방송_전환분석.md): 변이하는 별, 퀄리티 누락, 무기 세트 오류, 투구 거래.
4. [후속 변경](후속방송_추가조사.md): 초기 보조 우선순위 보완, 주얼·지팡이·목걸이, 검은 화염 전환 후보.

## 먼저 기억할 정정

- 섬광 유탄을 배웠다고 파편탄을 곧바로 버리지 않는다. 가스 유탄 전 보스의 공격 공백을 메웠다는 정정이 있다.
- 첫날에는 화염파 전환이 끝나지 않았다. 전환은 다음 날 52레벨 부근에서 시작했고 퀄리티·무기 지정 실수를 다시 고쳤다.
- 세케마를 건너뛰려던 계획은 혼돈의 시련 이후 되돌렸다. 실패한 계획을 추천 경로로 복사하지 않는다.
- 완성 플래너의 보조 5개와 레벨 100 트리는 초반 실제 보유·배정 기록이 아니다.

각 정정의 원영상 시간과 자막 근거는 위 상세 문서에 붙였다.

## 근거와 남은 작업

[방송목록](방송목록.md) · [플래너 대조](플래너_대조.md) · [직접 읽은 화면](화면_확인기록.md) · [확인대장 JSON](확인대장.json) · [미확인 항목](미확인_항목.md) · [체크포인트](CHECKPOINT.md).
'''

precise_table=['| 원영상·시각 | 실제 화면 판독 | 판정·한계 |','|---|---|---|']
docs['index']=docs['index'].replace('## 읽는 순서',coverage+'\n\n## 읽는 순서')
precise_sections=[]
for r in precise:
    precise_table.append(f"| [{r['video_id']} {hms(r['start_seconds'])}]({r['url']}) · [{r['id']}]({r['file']}) | {cell(r['observation'])} | **{cell(r['verification_class'])}**. {cell(r['limitation'])} |")
    precise_sections.extend([f"## {r['id']} · {r['video_id']} {hms(r['start_seconds'])}",'',r['observation'],'',r['verification_class']+' — '+r['limitation'],'',f"[원영상]({r['url']})",'',f"![{r['id']} 원본 영상 화면]({r['file']})",''])
docs['원본_정밀확인']='# 원본 영상 정밀 확인\n\n실제 Playwright MCP로 1280×720 영상을 재생하고 지정 시각으로 이동했다. 아래는 직접 읽은 정지 화면이며 연속 전체 시청을 뜻하지 않는다. 원본 해시와 시각 검증은 [화면대장](원본_화면대장.json)에 보존했다.\n\n'+'\n'.join(precise_table)+'\n\n'+'\n'.join(precise_sections)
event_md=['# 사건별 교차검증과 정정','',review_updates.POLICY,'','## 같은 사건에 연결한 전후 화면','']
for event in event_rows:
    event_md += ['### '+event['title'],'',event['result'],'',
        ' → '.join(f"[{r['id']}]({r['file']})" for r in event['frames']),'','남은 확인: '+event['remaining'],'']
event_md += ['## 정정 내역','','| 기존 화면 | 정정 이유 | 현재 설명 |','|---|---|---|']
for r in revisions:
    event_md.append(f"| {r['frame_id']} | {cell(r['reason'])} | {cell(r['current_observation'])}<br>{cell(r['current_limitation'])} |")
event_md += ['','이전 문구 전문과 정정 근거는 [기계 판독 이력](교차검증_이력.json)에 보존했다.']
docs['교차검증_정정']='\n'.join(event_md)
docs['원본_정밀확인']+='\n\n[겹치는 구간 처리와 사건별 정정](교차검증_정정.md)\n'
docs['보관함_정리방식']=stash_notes.TEXT
docs['index']+='\n\n## 보관함 분류와 실제 내부\n\n[보관함 정리 방식](보관함_정리방식.md)에서 기본·엔드 폴더 구조와 화폐·증강물·젬·심연, STR_INT의13·14 탭 내부 캡처를 크게 볼 수 있다. 기존 장갑·갑옷·투구를 보관하는 행동도 확인했다. 다른 장비 폴더는 이름과 실제 확인 범위를 구분했다.\n'
docs['index']+='\n\n## 이번에 해결한 교차검증\n\n가스의 원소 병기 I+다중 사격 I 장착 완료, 석궁 일반 엑잘티드1개 사용, 두 번째 전직 고급 마석학을 추가 확인했다. [사건별 근거와 정정](교차검증_정정.md) · [실제 플래너 비교와 연구용 주석 사본3개](플래너_대조.md).\n'
docs['첫날_상세분석']=docs['첫날_상세분석'].replace('## 첫날의 범위와 결론','## 원본 화면 추가 확인\n\n'+'\n'.join(precise_table)+'\n\n## 첫날의 범위와 결론')
docs['단계별_따라하기']+='\n\n## 원본 판독으로 보완한 초반 순서\n\n6레벨 섬광 Lv3 등록 직후에는 보조 두 칸이 비어 있었으며 파편 탄환 장전은 G창에 남아 있었다. 완성 플래너의 연결을 이 시점부터 요구하지 않는다. 다중 사격 I의 실제 영상 툴팁 피해 감폭은 35%다. 6레벨 패시브 화면에서는 무정 배정과 남은 포인트0을 읽었다. 각 화면과 이후 장착 확인은 [원본 정밀 확인](원본_정밀확인.md)에 누적한다.\n'
docs['단계별_따라하기']+='\n14레벨에는 민첩+5를 찍어 민첩16→21·지능7·힘36이 됐다. 가스 Lv5의 요구 조건은 레벨14·힘17·민첩17이다. 화면의 별도 지능1 부족 경고를 가스의 요구 조건으로 읽지 않는다. 이어 가스 Lv5를 등록했고 보조 두 칸은 비어 있었다. [민첩 배정](https://www.youtube.com/watch?v=zKJQyBm4VnI&t=5369s), [가스 요구 조건](https://www.youtube.com/watch?v=zKJQyBm4VnI&t=5373s). 이어 장착 장갑에 룬으로 생명력+30을 붙이고 별도 보상+20을 받아 최대 생명력329→379가 된다. 13레벨 의식 전투에서는 생명력350이3초 만에24까지 줄어 일시정지·캐릭터 선택으로 나갔다. 고정 생명력 합계를 안전 보장선으로 삼지 않는다. [생명력24 원본](https://www.youtube.com/watch?v=zKJQyBm4VnI&t=5099s).\n'
docs['화면_확인기록']=docs['화면_확인기록'].replace('아래 9개 이미지 표는','원본 720p 판독은 [원본 정밀 확인](원본_정밀확인.md)에 별도로 추가했다. 아래 9개 이미지 표는')
NAV=[('index','시작'),('핵심차이_실전보완','핵심 차이'),('첫날_상세분석','첫날'),('원본_정밀확인','원본 판독'),('보관함_정리방식','보관함'),('단계별_따라하기','따라하기'),('다음방송_전환분석','화염파 전환'),('후속방송_추가조사','후속 변경'),('플래너_대조','플래너'),('방송목록','방송목록'),('미확인_항목','남은 확인')]
CSS='''*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:#f6f3eb;color:#24332e;font-family:"Malgun Gothic",system-ui,sans-serif;line-height:1.85}header{background:#173f35;color:#fff;padding:30px max(20px,calc((100vw - 1160px)/2));border-bottom:5px solid #c9a458}header .eyebrow{letter-spacing:.13em;font-size:12px;color:#d7c9a7}header p{margin:8px 0 0;font-size:23px;font-weight:700}nav{display:flex;gap:8px;flex-wrap:wrap;margin-top:20px}nav a{color:#fff;text-decoration:none;padding:5px 12px;border:1px solid #668379;border-radius:8px;font-size:13px}nav a[aria-current]{background:#f6f3eb;color:#173f35}main{max-width:1200px;margin:30px auto;padding:0 20px 60px}article{background:#fffdf8;padding:35px 42px;border:1px solid #ddd8c9;border-radius:12px;min-width:0}h1{font-size:32px;line-height:1.4;margin:0 0 24px;letter-spacing:-.035em}h2{font-size:23px;margin:38px 0 14px;border-top:1px solid #ddd8c9;padding-top:24px}h3{font-size:18px;margin-top:27px}p,li{overflow-wrap:anywhere}a{color:#236755;text-underline-offset:3px}strong{color:#183f35}img{max-width:100%;height:auto;display:block;border:1px solid #ddd8c9;border-radius:8px}code{font-size:.9em;overflow-wrap:anywhere;background:#eeeade;padding:2px 4px}pre{overflow:auto}.table-scroll{overflow:auto;border:1px solid #ddd8c9;border-radius:8px;margin:20px 0}table{border-collapse:collapse;width:100%;font-size:13px;min-width:600px}th{background:#e8eee7;text-align:left}th,td{padding:12px;border-bottom:1px solid #deded2;vertical-align:top}tbody tr:nth-child(even){background:#f7f7ef}td:first-child{min-width:170px}footer{font-size:12px;color:#68736a;margin-top:25px}.search{width:100%;max-width:420px;padding:10px;border:1px solid #aaa;border-radius:6px;font:inherit}.toc{background:#f0f2e9;padding:14px 20px;border-radius:8px;font-size:14px}.toc ul{margin:5px 0;padding-left:20px}@media(max-width:650px){header{padding:22px 16px}header p{font-size:19px}main{padding:0 10px;margin:15px auto}article{padding:23px 17px}h1{font-size:26px}h2{font-size:21px}nav{gap:5px}nav a{font-size:12px;padding:4px 9px}table{min-width:650px}}@media print{header nav,.search,.toc{display:none}body{background:white}main,article{margin:0;padding:0;border:0}table{font-size:10px}a{color:inherit}}'''
JS='''document.querySelectorAll('table').forEach(t=>{const d=document.createElement('div');d.className='table-scroll';d.tabIndex=0;t.before(d);d.append(t)});const input=document.getElementById('filter');if(input)input.addEventListener('input',()=>{const q=input.value.trim().toLocaleLowerCase();document.querySelectorAll('tbody tr').forEach(r=>r.hidden=!!q&&!r.textContent.toLocaleLowerCase().includes(q))});'''
for stem,text in docs.items():
    (O/f'{stem}.md').write_text(text.rstrip()+'\n',encoding='utf-8')
    md=markdown.Markdown(extensions=['tables','fenced_code','toc'],extension_configs={'toc':{'toc_depth':'2-3'}})
    body=md.convert(text)
    body=re.sub(r'href="([^"#?]+)\.md([#?][^"]*)?"',lambda m:'href="'+m[1]+('.html' if (O/(m[1]+'.md')).resolve().parent==O else '.md')+(m[2] or '')+'"',body)
    title=text.splitlines()[0].lstrip('# ')
    nav=''.join(f'<a href="{name}.html"'+(' aria-current="page"' if name==stem else '')+f'>{label}</a>' for name,label in NAV)
    search='<p><label for="filter">표에서 내용 찾기</label><br><input id="filter" class="search" type="search" placeholder="예: 전직, 파편탄, 정신력"></p>' if '<table>' in body else ''
    page=f'<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)}</title><style>{CSS}</style></head><body><header><div class="eyebrow">POE2 · 0.5.5 · SEONGBIN</div><p>화염파 젬링, 첫날부터 따라 읽기</p><nav aria-label="보고서 탐색">{nav}</nav></header><main><article>{search}{body}</article><footer>자막·미리보기·실행 검증을 구분한 조사 기록 · <a href="CHECKPOINT.html">확인 범위</a> · <a href="{stem}.md">Markdown 원문</a></footer></main><script>{JS}</script></body></html>'
    (O/f'{stem}.html').write_text(page,encoding='utf-8')

dump('access_validation.json',{'checked_utc':NOW,'metadata_refresh':{'videos':[A,B],'status':'success'},
 'web_open':'YouTube watch pages: Online fetch throttled',
 'direct_ffmpeg':{'video_id':A,'seconds':[1445,2090],'status':'failed'},
 'range_download':{'video_id':A,'format':'299','requested_start_seconds':1435,'requested_duration':35,'initial_1MiB':'HTTP 206; ftyp/moov/sidx parsed','segment_byte_range':[657787140,661643821],'segment_response':403,'fresh_metadata_retry':403,'64KiB_retry':403,'usable_video_created':False},
 'browser':{'tool':'Python Playwright, isolated headless Edge','video_id':B,'requested_seconds':6370,'ready_state':0,'current_time':0,'duration':None,'result':'timeout and player error visible','screenshot':'frames/GtC5-b4QXec/browser_006370.00.png'},
 'actual_playwright_mcp':{'server':'@playwright/mcp 0.0.80','status':'original video playback and timestamped screenshot success','resolution':[1280,720],'logged_in_account_verified':False,'receipts_directory':'mcp_session','reviewed_frame_count':len(precise)},
 'claim':'기존 직접 다운로드와 headless 재생 실패를 보존한다. 이후 실제 Playwright MCP 원본 재생·캡처 성공으로 접근 상태를 갱신했다.'})
dump('report_manifest.json',{'generated_utc':NOW,'documents':[{'markdown':f'{n}.md','html':f'{n}.html'} for n in docs],
 'caption_observations':len(observations),'visual_review_sheets':len(visuals),'original_video_reviewed_frames':len(precise),'first_day_precise_research_complete':False,
 'planner_modified':False,'research_planner_copies':research_copies,'installed_game_files_modified':False})
print(json.dumps({'documents':len(docs),'caption_observations':len(observations),'visual_reviews':len(visuals)},ensure_ascii=False))
