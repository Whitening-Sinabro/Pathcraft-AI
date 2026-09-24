"""Publish only the VOD-checked 05/06 trees, their notes, report and current ZIP."""
from pathlib import Path
import copy, datetime, hashlib, json, re, shutil, sys, zipfile
import markdown

HERE = Path(__file__).resolve().parent
BASE = HERE.parents[1]
ROOT = BASE.parents[1]
OLD = BASE.parent / 'skadoosh_hc_2026-09-07'
DEST = Path('C:/Users/User/Documents/My Games/Path of Exile 2/BuildPlanner')
sys.path[:0] = [str(BASE), str(OLD)]
import progression_core as core
from stage_05_06_passives import apply_verified_passives, VERIFIED
from weapon_sets import BASES, validate_weapon_sets, write_weapon_set_guide
from combat_rotations import write_rotation_guide

def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p, x): p.write_text(json.dumps(x, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
def structure(x):
    if isinstance(x,dict): return {k:structure(v) for k,v in x.items() if k not in ('description','additional_text','passives')}
    if isinstance(x,list): return [structure(v) for v in x]
    return x
def strings(x):
    if isinstance(x,str): yield x
    elif isinstance(x,dict):
        for v in x.values(): yield from strings(v)
    elif isinstance(x,list):
        for v in x: yield from strings(v)

files=sorted((BASE/'BuildPlanner').glob('*.build')); assert len(files)==7
selected=[p for p in files if p.name[:2] in ('05','06')]; assert len(selected)==2
names={p.name for p in selected}
untouched={p:sha(p) for p in files if p.name not in names}
untouched.update({p:sha(p) for p in DEST.glob('*.build') if p.name not in names})
untouched.update({p:sha(p) for p in DEST.parent.glob('*.filter')})
frozen={p:sha(p) for p in (OLD/'ready/BuildPlanner').glob('*.build')}
source_validation={r['file']:r['sha256'] for r in read(OLD/'validation_revision3.json')['planners']}
assert len(frozen)==7 and all(sha(p)==source_validation[p.name] for p in frozen)
visual=read(HERE/'visual_review.json')
assert visual['all_atlases_visually_inspected'] and len(visual['atlas_files'])==13
assert all(sha(HERE/r['file'])==r['sha256'] for r in visual['atlas_files'])

pending=[]
for p in selected:
    stage=int(p.name[:2]); before=read(p); d=copy.deepcopy(before)
    assert apply_verified_passives(d,stage)
    repeat=copy.deepcopy(d); apply_verified_passives(repeat,stage); assert repeat==d
    assert structure(d)==structure(before), 'Only passive allocations and notes may change'
    state=core.state(d); assert len(state)==len(d['passives']) and core.legal(state)
    assert state==core.state(VERIFIED['stages'][str(stage)])
    assert core.costs(state)==VERIFIED['stages'][str(stage)]['costs']
    assert len(d['description'])<=1900
    for t in strings(d):
        assert '\ufffd' not in t and t.count('{')==t.count('}') and not re.search(r'\\[nr]',t)
    for slot in d['inventory_slots']: assert len(slot['additional_text'])<=900
    for s in d['skills']:
        assert s['id'] in BASES and len(s['additional_text'])<=600
        assert len({x['id'] for x in s['support_skills']})==len(s['support_skills'])
        for x in s['support_skills']: assert x['id'] in BASES and len(x['additional_text'])<=230
    sets=validate_weapon_sets(d)
    pending.append((p,d,dict(file=p.name,before_sha256=sha(p),costs=core.costs(state),description_length=len(d['description']),weapon_sets=sets)))

plans={int(p.name[:2]):read(p) for p in files}
for p,d,row in pending: plans[int(p.name[:2])]=d
assert core.state(plans[5]).items()<=core.state(plans[6]).items()
assert core.state(plans[6]).items()<=core.state(plans[7]).items()
transitions={}
for a,z in ((4,5),(5,6),(6,7)):
    ops=core.transaction_plan(plans[a],plans[z])
    baseline=core.costs(core.state(plans[a]))
    transitions[f'{a:02}_{z:02}']={'operations':ops,'refunds':sum(x['action']=='환불' for x in ops),
        'peak_ordinary':max([baseline['ordinary']]+[x['cost']['ordinary'] for x in ops]),
        'peak_sets':[max([baseline['sets'][i]]+[x['cost']['sets'][i] for x in ops]) for i in (0,1)]}
assert transitions['04_05']['refunds']==35 and transitions['05_06']['refunds']==0

# Stage both validated builds, then replace only the two exact authorised paths.
backups=HERE/'planner_backups'; backups.mkdir(exist_ok=True)
rows=[]
for p,d,row in pending:
    dest=DEST/p.name; assert dest.resolve().parent==DEST.resolve()
    for existing in (p,dest):
        if existing.exists():
            backup=backups/(existing.stem+'.'+sha(existing)[:12]+'.build')
            if not backup.exists(): shutil.copy2(existing,backup)
            assert sha(backup)==sha(existing)
    save(p,d); shutil.copy2(p,dest)
    assert read(dest)==d and sha(p)==sha(dest)
    row.update(sha256=sha(p),installed_path=str(dest),vod_passive_reconstruction_checked=True,contemporaneous_api_export=False)
    rows.append(row)

md=ROOT/'Docs/2026-09-05_SKADOOSH_CORRUPTING_CRY_TOTEM_WARBRINGER_0_5_5_RESEARCH.md'
page=ROOT/'Docs/2026-09-05_SKADOOSH_CORRUPTING_CRY_TOTEM_WARBRINGER_0_5_5_GUIDE_DOC.html'
text=md.read_text(encoding='utf-8')
link='../deliverables/skadoosh_early_survival_2026-09-08/stage_05_06_audit/remaining_audit/05_06_남은항목_확인.html'
top=('<!-- stage56-audit:start -->\n**05·06 후속 복원 완료:** 방송 화면의 선택 경로·세트 색·남은 포인트를 대조해 '
     '**05를 일반 71점·특화 각 14점, 06을 일반 87점·특화 각 22점**으로 수정했다. '
     '당시 API 내보내기 파일이 아닌 VOD 복원본이다. 지진 함성 첫 제작·장착은 **00:52:21~23**이다. '
     '이전 69→80점 예시는 현재 트리에 적용하지 않는다. [대조 장면·수정 파일·남은 항목]('+link+').\n<!-- stage56-audit:end -->\n\n')
text=re.sub(r'<!-- stage56-audit:start -->.*?<!-- stage56-audit:end -->\n\n',lambda _:top,text,count=1,flags=re.S)
text=text.replace('| 69 / 14·14 / 4 |','| 71 / 14·14 / 4 |',1)
text=text.replace('| 69 / 14·14 / 4 |','| 87 / 22·22 / 4 |',1)
for stage in (5,6):
    start=text.index(f'<a id="stage-{stage:02}"></a>'); end=text.index(f'<a id="stage-{stage+1:02}"></a>',start)
    part=text[start:end]
    verified=('**패시브 대조 완료:** 54레벨 방송 화면에서 Hard to Kill·Spirit Bond·Ancestral Conduits를 포함해 복원했다. I는 Lay Siege를 유지하고 Bolstering Yell은 제외한다.' if stage==5 else
              '**패시브 대조 완료:** 54레벨 배정을 유지하며 공통 8·I 특화 8·II 특화 8노드를 추가한 65레벨 트리다. Desensitisation·Battle Fever는 아직 포함하지 않는다.')
    part=re.sub(r'\*\*이번 대조에서 확인한 트리 차이:\*\*[^\n]*',verified,part)
    part=part.replace('일반 69점·특화 각 14점은 완성 배정이며 실제 환불 중 필요한 여유는 패시브전환 문서를 따른다.',
                      '일반 71점·특화 각 14점이 목표이며 현재 04에서 전환하는 검사 경로에는 특화 각 16점 한도가 필요하다.')
    part=part.replace('회복 노드를 포함한 정확한 방송 트리 복원은 미완료다. 기존 회복 노드를 일괄 환불하지 않는다.',
                      '방송에 이미 있던 회복·토템 가지를 복원했다. 아래 후속 대조 자료의 전환 경로를 따른다.')
    part=part.replace('**패시브 목표:** 일반 69점 · 특화 I/II 14/14점 · 전직 4점.',
                      '**패시브 목표:** '+('일반 71점 · 공통 57점 · 특화 I/II 14/14점 · 전직 4점.' if stage==5 else '일반 87점 · 공통 65점 · 특화 I/II 22/22점 · 전직 4점. 방송 당시 일반 1점·특화 각 2점 미사용.'))
    part=part.replace('늦어도 방송 02:35:41에 연결. 최초 추가 시점은 미확정.',
                      '00:52:21~23에 11레벨 지진 함성 제작·장착. 우주의 영사·효율 I 연결은 늦어도 02:35:41에 확인.')
    part=part.replace('05 트리를 그대로 쓰며 97점 완성은 필요하지 않다.',
                      '05 배정을 유지하며 일반 사용량 71→87점, 특화 각 14→22점으로 확장한다. 97점 후기 완성은 필요하지 않다.')
    part=re.sub(r'\*\*구성 근거:\*\*[^\n]*',
                '**구성 근거:** '+('54레벨 00:29:54~00:30:28의 선택 경로·세트 색·남은 포인트를 대조한 71점 복원본.' if stage==5 else '65레벨 03:54:20~03:55:50의 선택 경로·세트 색·남은 포인트를 대조한 87점 복원본.')+' 당시 API 내보내기 파일은 아니다. [노드별 대조 근거]('+link+').',part)
    if stage==5:
        part=part.replace('05 후반에는 지진 함성·우주의 영사·효율 I가 이미 있다.',
                          '00:52:21~23에 지진 함성을 처음 장착하며 우주의 영사·효율 I 연결은 늦어도 02:35:41에 확인된다.')
    else:
        part=re.sub(r'\*\*사용 순서:\*\*[^\n]*',
                    '**사용 순서:** 보강하는 함성(I)을 쓰며 이동하고 메아리 사이에 지진 함성(I)을 보탠다. 밀집 무리·희귀·보스에는 전사 토템(II)을 추가한 뒤 함성(I)으로 복귀한다. 토템이 죽거나 만료되거나 적이 벗어나면 보충한다. 매 무리에 같은 세 버튼 순서를 강제하지 않는다.',part,count=1)
    text=text[:start]+part+text[end:]
text=text.replace('| 04 타락 함성 - 마나 사용 → 05 전사 토템 - 혈마법 전환 | 69 | 16 / 16 | 44 |',
                  '| 04 타락 함성 - 마나 사용 → 05 전사 토템 - 혈마법 전환 | 71 | 16 / 16 | 35 |')
text=text.replace('| 05 전사 토템 - 혈마법 전환 → 06 파콰테 - 두 함성 운영 | 69 | 14 / 14 | 0 |',
                  '| 05 전사 토템 - 혈마법 전환 → 06 파콰테 - 두 함성 운영 | 87 | 22 / 22 | 0 |')
text=text.replace('05→06은 패시브가 같고 06→07은 기존 배정을 유지하는 확장이다. 05에서 이미 회복·방어 11점을 더했다면 그 노드를 다시 환불할 필요가 없다.',
                  '05→06은 기존 배정을 유지하며 공통 8·I 8·II 8노드를 추가한다. 일반 사용량은 16점 늘어난다. 06→07도 환불 없는 확장이며 후기 전직 2점이 추가된다.')
old='[노드별 환불·추가 순서와 회복·방어 80점 경로](../deliverables/skadoosh_hc_2026-09-07/revision3/패시브전환.md)를 보면서 진행한다. 이 순서는 연결과 포인트 한도를 검사한 경로이며 제작자의 매 클릭을 그대로 전사한 순서는 아니다.'
new='01~04는 [기존 노드별 전환 자료](../deliverables/skadoosh_hc_2026-09-07/revision3/패시브전환.md), 04→05→06→07은 [복원 후 새 전환 경로]('+link+')를 따른다. 연결과 포인트 한도를 검사한 경로이며 제작자의 매 클릭을 전사한 순서는 아니다. 기존 자료의 69→80점 확장안은 현재 목표에서 제외한다.'
text=text.replace(old,new)
start=text.index('05의 69점 트리는 **방송 기반 재구성안**이다.') if '05의 69점 트리는 **방송 기반 재구성안**이다.' in text else -1
if start>=0:
    end=text.index('### 의식에서의 사용 순서',start)
    historical=text[start:end]
    current=('현재 목표는 54레벨 71점·65레벨 87점의 방송 복원본이다. 65레벨 방송의 생명력 1624·초당 회복 115.7은 토템이 살아 있던 당시 장비·버프 상태의 표시값이다. 메아리 1회당 회복과 비용 상쇄는 분리 측정하지 못했다. 실제 장비·재생·활력과 사용 비용을 함께 확인한다.\n\n'
             '<details markdown="1">\n<summary>이전 69/80점 전환안의 계산 기록 — 현재 71/87점에 미적용</summary>\n\n'
             '아래는 이전 입력으로 계산한 보존 자료다. 현재 트리의 피해·회복 검증 결과로 사용하지 않는다.\n\n'+historical+'\n</details>\n\n')
    text=text[:start]+current+text[end:]
text=text.replace('[배포 ZIP](../deliverables/skadoosh_hc_2026-09-07/Skadoosh-HC-한국어-필터와플래너.zip)을 풀어 같은 위치에 넣을 수도 있다.',
                  '플래너는 [현재 플래너 ZIP](../deliverables/skadoosh_early_survival_2026-09-08/Skadoosh-현재플래너.zip)을 사용한다. [09-07 필터·플래너 묶음](../deliverables/skadoosh_hc_2026-09-07/Skadoosh-HC-한국어-필터와플래너.zip)은 당시 보존본이다.')
text=text.replace('최신 7개 정상 로드 로그와 실제 게임의 02 트리 화면을 확인했다.',
                  '당시 7개 정상 로드 로그와 실제 게임의 02 트리 화면을 확인했다. 이는 이전 파일 검사 기록이며 이번에 수정한 05·06의 게임 내부 재불러오기는 아직 확인하지 않았다.')
text=text.replace('**현재 확정하지 못한 핵심은 05의 정확한 54레벨 원본 트리와 파콰테·메아리의 반복 비용·회복량, 실전 총 DPS·다수 피격 생존이다.**',
                  '**09-08 후속 조사에서 54·65레벨 선택 경로와 포인트를 대조해 71/87점 트리를 복원했다. 남은 핵심은 파콰테·메아리의 반복 비용·회복량, 실전 총 DPS·다수 피격 생존이다.**')
assert '최초 추가 시점은 미확정' not in text and '전체 트리 복원은 미완료' not in text
md.write_text(text,encoding='utf-8')
outer=page.read_text(encoding='utf-8'); assert outer.count('<main>')==outer.count('</main>')==1
body=markdown.markdown(text,extensions=['tables','fenced_code','md_in_html'])
page.write_text(outer.split('<main>',1)[0]+'<main>'+body+'</main>'+outer.split('</main>',1)[1],encoding='utf-8')

# Keep the previous report as an audit trail with an explicit superseding note.
oldmd=HERE.parent/'05_06_설명장면_재확인.md'; oldpage=oldmd.with_suffix('.html')
notice=('<!-- subsequent-passives -->\n**후속 확인 완료:** 아래의 “패시브 복원 미완료·지진 함성 최초 시점 미확정”은 이전 조사 상태다. '
        '54·65레벨은 71/87점으로 복원했고 지진 함성 첫 장착은 00:52:21~23으로 확인했다. '
        '[최신 결과와 파일](remaining_audit/05_06_남은항목_확인.html).\n<!-- subsequent-passives:end -->\n\n')
s=oldmd.read_text(encoding='utf-8')
if '<!-- subsequent-passives -->' not in s:
    pos=s.index('\n\n')+2; oldmd.write_text(s[:pos]+notice+s[pos:],encoding='utf-8')
s=oldpage.read_text(encoding='utf-8')
if '<!-- subsequent-passives -->' not in s:
    s=s.replace('<main>','<main>'+markdown.markdown(notice),1); oldpage.write_text(s,encoding='utf-8')

write_rotation_guide(); write_weapon_set_guide([read(p) for p in files])
archive=BASE/'Skadoosh-현재플래너.zip'
with zipfile.ZipFile(archive) as z: readme=z.read('README.md').decode('utf-8')
readme=readme.split('\n## 05·06 설명 장면 추가 정정\n')[0].split('\n## 05·06 방송 패시브 복원\n')[0]
readme+='\n## 05·06 방송 패시브 복원\n\n05는 54레벨 일반 71점·특화 각 14점, 06은 65레벨 일반 87점·특화 각 22점으로 복원했다. 방송의 선택 경로·무기 세트 색·남은 포인트를 대조한 배정이며 당시 API 내보내기 파일은 아니다. 지진 함성 첫 장착은 00:52:21~23. 05→06은 환불 없이 확장한다. 01~04·07 파일은 유지했다. 게임 내부 재불러오기는 미검증이다.\n'
temp=HERE/'planners_updated.zip'
with zipfile.ZipFile(temp,'w',compression=zipfile.ZIP_DEFLATED) as z:
    for p in files: z.write(p,'BuildPlanner/'+p.name)
    z.writestr('README.md',readme)
with zipfile.ZipFile(temp) as z:
    assert z.testzip() is None and len(z.namelist())==8
    for p in files: assert z.read('BuildPlanner/'+p.name)==p.read_bytes()==(DEST/p.name).read_bytes()
temp.replace(archive)
assert all(p.exists() and sha(p)==h for p,h in untouched.items())
assert all(sha(p)==h for p,h in frozen.items())
record=dict(created_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),files=rows,
    unrelated_hashes_preserved={str(p):h for p,h in untouched.items()},original_source_hashes_preserved=True,
    archive_matches_installed=True,vod_passive_reconstruction_checked=True,contemporaneous_api_export=False,
    game_parser_load_verified=False,backups=str(backups),transition_validation=transitions)
save(HERE/'planner_validation.json',record)
manifest=read(BASE/'planner_installation.json')
for row in rows:
    entry=next(x for x in manifest['files'] if x['file']==row['file'])
    entry.update(sha256=row['sha256'],passives_preserved=False,vod_passive_reconstruction_checked=True,
        contemporaneous_api_export=False,stage_05_06_passive_validation='stage_05_06_audit/remaining_audit/planner_validation.json',
        weapon_set_validation={'sets':row['costs']['sets'],'both_sets_connected':True})
manifest.update(last_scoped_update_utc=record['created_at_utc'],last_scoped_update_files=[r['file'] for r in rows],game_parser_load_verified=False)
save(BASE/'planner_installation.json',manifest)
print(json.dumps(dict(installed=2,costs=[r['costs'] for r in rows],preserved_files=len(untouched),source_hashes_matched=True,archive_matches=True,game_parser_load_verified=False),ensure_ascii=False))
