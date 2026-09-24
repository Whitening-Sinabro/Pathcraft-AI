"""Validate and publish only the two explicitly scoped planners and their guide sections."""
from pathlib import Path
import copy, datetime, hashlib, json, re, shutil, sys, zipfile
import markdown

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
ROOT = BASE.parents[1]
DEST = Path('C:/Users/User/Documents/My Games/Path of Exile 2/BuildPlanner')
sys.path.insert(0, str(BASE))
from stage_05_06_progression import apply_stage_05_06_progression, SEISMIC, PRECISION
from weapon_sets import BASES, validate_weapon_sets, write_weapon_set_guide
from combat_rotations import write_rotation_guide

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p, value): p.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
def strip_notes(x):
    if isinstance(x, dict): return {k:strip_notes(v) for k,v in x.items() if k not in ('additional_text','description')}
    if isinstance(x, list): return [strip_notes(v) for v in x]
    return x
def strings(x):
    if isinstance(x, str): yield x
    elif isinstance(x, dict):
        for v in x.values(): yield from strings(v)
    elif isinstance(x, list):
        for v in x: yield from strings(v)

paths = sorted(p for p in (BASE/'BuildPlanner').glob('*.build') if p.name[:2] in ('05','06'))
assert len(paths) == 2
names = {p.name for p in paths}
untouched = {p:sha(p) for p in (BASE/'BuildPlanner').glob('*.build') if p.name not in names}
untouched.update({p:sha(p) for p in DEST.glob('*.build') if p.name not in names})
untouched.update({p:sha(p) for p in DEST.parent.glob('*.filter')})
frozen = {p:sha(p) for p in (BASE.parent/'skadoosh_hc_2026-09-07/ready/BuildPlanner').glob('*.build')}
pending = []
for p in paths:
    stage = int(p.name[:2]); before = read(p); d = copy.deepcopy(before)
    changes = apply_stage_05_06_progression(d,stage)
    repeated = copy.deepcopy(d); assert apply_stage_05_06_progression(repeated,stage) == [] and repeated == d
    assert d['passives'] == before['passives'] and d['inventory_slots'] == before['inventory_slots']
    # Explicitly allow only the two observed structural additions.
    check = copy.deepcopy(d)
    if stage == 5 and not any(x['id']==SEISMIC for x in before['skills']):
        check['skills'] = [x for x in check['skills'] if x['id']!=SEISMIC]
    prior_purity = [x for x in before['skills'] if x['id'].endswith('SkillGemPurityOfFire')][1]
    if not any(x['id']==PRECISION for x in prior_purity['support_skills']):
        purity = [x for x in check['skills'] if x['id'].endswith('SkillGemPurityOfFire')][1]
        purity['support_skills'] = [x for x in purity['support_skills'] if x['id']!=PRECISION]
    assert strip_notes(check)==strip_notes(before), 'Unexpected non-note change'
    assert len(d['description'])<=1900
    for s in strings(d):
        assert '\ufffd' not in s and s.count('{')==s.count('}') and not re.search(r'\\[nr]',s)
    for s in d['skills']:
        assert s['id'] in BASES and len(s['additional_text'])<=600
        assert len({x['id'] for x in s['support_skills']})==len(s['support_skills'])
        for x in s['support_skills']: assert x['id'] in BASES and len(x['additional_text'])<=230
    sets = validate_weapon_sets(d)
    pending.append((p,d,{'file':p.name,'before_sha256':sha(p),'changes':changes,
                        'passives_unchanged':True,'only_authorized_gem_changes':True,
                        'description_length':len(d['description']),'weapon_sets':sets}))

# All two builds passed before either installation is changed.
backups = HERE/'planner_backups'; backups.mkdir(exist_ok=True)
rows = []
for p,d,row in pending:
    dest = DEST/p.name
    assert dest.resolve().parent==DEST.resolve()
    for existing in [p,dest]:
        if existing.exists():
            backup = backups/(existing.stem+'.'+sha(existing)[:12]+'.build')
            if not backup.exists(): shutil.copy2(existing,backup)
            assert sha(backup)==sha(existing)
    save(p,d); shutil.copy2(p,dest)
    assert read(dest)==d and sha(p)==sha(dest)
    row.update(sha256=sha(p),installed_path=str(dest));rows.append(row)

md = ROOT/'Docs/2026-09-05_SKADOOSH_CORRUPTING_CRY_TOTEM_WARBRINGER_0_5_5_RESEARCH.md'
page = ROOT/'Docs/2026-09-05_SKADOOSH_CORRUPTING_CRY_TOTEM_WARBRINGER_0_5_5_GUIDE_DOC.html'
text = md.read_text(encoding='utf-8')
link = '../deliverables/skadoosh_early_survival_2026-09-08/stage_05_06_audit/05_06_설명장면_재확인.html'
top = ('<!-- stage56-audit:start -->\n**05·06 추가 정정:** 05 지진 함성·우주의 영사·효율 I와 '
       '양 단계 II 불의 순수함의 정밀함 II 누락을 수정했다. '
       '**기존 69점 전환안은 54레벨 방송의 회복·토템 가지와 다르며, 전체 트리 복원은 미완료다.** '
       '아래 예전 69→80점 환불·확장 예시를 방송 배정 순서로 사용하지 않는다. '
       '[설명 장면과 수정 범위]('+link+').\n<!-- stage56-audit:end -->\n\n')
if '<!-- stage56-audit:start -->' in text:
    text = re.sub(r'<!-- stage56-audit:start -->.*?<!-- stage56-audit:end -->\n\n',lambda _:top,text,count=1,flags=re.S)
else:
    pos=text.index('\n\n')+2;text=text[:pos]+top+text[pos:]
for stage in (5,6):
    start=text.index(f'<a id="stage-{stage:02}"></a>')
    end=text.index(f'<a id="stage-{stage+1:02}"></a>',start)
    part=text[start:end]
    part=part.replace('| 불의 순수함 · 세트 II | 활력 I |','| 불의 순수함 · 세트 II | 활력 I + 정밀함 II |')
    warning=('**이번 대조에서 확인한 트리 차이:** 54레벨에 이미 Hard to Kill·Spirit Bond·Ancestral Conduits가 있다. '
             '이 파일의 69점 배정에는 누락돼 있으므로 전체 트리 복원 전까지 방송 복사용으로 사용하지 않는다. '
             '회복을 65레벨 이후에만 확보하는 순서로 읽지 않는다.\n\n')
    if warning not in part:
        pos=part.index('**이 단계 시작:**');part=part[:pos]+warning+part[pos:]
    if stage==5:
        if '| 지진 함성 · 세트 I |' not in part:
            pos=part.index('| 지면 분쇄 · 전사 토템 내부 |')
            part=part[:pos]+'| 지진 함성 · 세트 I | 우주의 영사 + 효율 I | 늦어도 방송 02:35:41에 연결. 최초 추가 시점은 미확정. I에서 적·가시 쪽에 사용하고 06에서 효율 II·격노하는 함성으로 보강한다. |\n'+part[pos:]
        part=re.sub(r'\*\*사용 순서:\*\*[^\n]*', '**사용 순서:** 보강하는 함성(I)을 쓰며 이동한다. 밀집 무리·희귀·보스에는 전사 토템(II)을 보태고 I로 복귀한다. 05 진행 중 지진 함성도 추가한다. 토템의 사망·만료·적 위치에 맞춰 보충하며 매 무리에 고정 세 버튼 순서를 강제하지 않는다.',part,count=1)
        part=re.sub(r'\*\*65레벨 이상이면:\*\*[^\n]*','**회복 준비:** 54레벨 방송에서 이미 회복 노드를 유지한다. 기존 69→80점 확장안은 실제 방송 순서가 아니다. 젬·장비·생명력 재생과 양 세트 정신력을 함께 준비한다.',part,count=1)
        part=part.replace('65레벨 이상에서 여유 점수가 있으면 패시브전환의 회복·방어 11점을 먼저 확장한다(총 80점). 이 확장에는 파콰테가 필요하지 않다. 실제 보유 포인트만 순서대로 사용한다.','회복 노드를 포함한 정확한 방송 트리 복원은 미완료다. 기존 회복 노드를 일괄 환불하지 않는다.')
    note=('05 후반에는 지진 함성·우주의 영사·효율 I가 이미 있다. 03:36:12에는 II 불의 순수함에 정밀함 II를 추가한다. 첫 전사 토템 설치와 이후 성장 연결을 구분한다.' if stage==5 else
          '기존 지진 함성의 효율 I를 보강에서 빼낸 효율 II로 바꾸고 격노하는 함성을 추가한다. II 불의 순수함의 정밀함 II는 05 후반에 이미 추가됐다. 65레벨 캐릭터 창의 초당 회복 115.7은 살아 있는 토템이 있는 당시 수치다.')
    mark=f'<!-- stage56-detail-{stage}:start -->'
    block=mark+'\n**추가 확인:** '+note+' [장면 근거]('+link+').\n'+f'<!-- stage56-detail-{stage}:end -->\n\n'
    if mark in part:part=re.sub(re.escape(mark)+rf'.*?<!-- stage56-detail-{stage}:end -->\n\n',lambda _:block,part,count=1,flags=re.S)
    else:
        pos=part.index('### 스킬에 넣을 젬');part=part[:pos]+block+part[pos:]
    text=text[:start]+part+text[end:]
md.write_text(text,encoding='utf-8')
outer=page.read_text(encoding='utf-8');assert outer.count('<main>')==outer.count('</main>')==1
body=markdown.markdown(text,extensions=['tables','fenced_code','md_in_html'])
page.write_text(outer.split('<main>',1)[0]+'<main>'+body+'</main>'+outer.split('</main>',1)[1],encoding='utf-8')
write_rotation_guide()
builds=sorted((BASE/'BuildPlanner').glob('*.build'));assert len(builds)==7
write_weapon_set_guide([read(p) for p in builds])

archive=BASE/'Skadoosh-현재플래너.zip'
with zipfile.ZipFile(archive) as old:readme=old.read('README.md').decode('utf-8')
readme=readme.split('\n## 05·06 설명 장면 추가 정정\n')[0]
readme+='\n## 05·06 설명 장면 추가 정정\n\n05 지진 함성·우주의 영사·효율 I, 05·06 II 불의 순수함의 정밀함 II를 추가했다. 전체 54/65레벨 패시브 복원은 미완료이며 기존 69점 전환안을 방송 트리 복사용으로 사용하지 않는다. 패시브 배정은 변경하지 않았다. 게임 재불러오기는 미검증이다.\n'
temp=HERE/'planners_updated.zip'
with zipfile.ZipFile(temp,'w',compression=zipfile.ZIP_DEFLATED) as out:
    for p in builds:out.write(p,'BuildPlanner/'+p.name)
    out.writestr('README.md',readme)
with zipfile.ZipFile(temp) as check:
    assert check.testzip() is None and len(check.namelist())==8
    for p in builds:assert check.read('BuildPlanner/'+p.name)==p.read_bytes()
temp.replace(archive)
assert all(p.exists() and sha(p)==h for p,h in untouched.items())
assert all(sha(p)==h for p,h in frozen.items())
record={'created_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'files':rows,'unrelated_hashes_preserved':{str(p):h for p,h in untouched.items()},
        'original_source_hashes_preserved':True,'archive_matches_installed':True,
        'game_parser_load_verified':False,'full_historical_passive_tree_verified':False,
        'reconstruction_candidate_installed':False,'backups':str(backups)}
save(HERE/'planner_validation.json',record)
installation_path=BASE/'planner_installation.json'
installation=read(installation_path)
for row in rows:
    entry=next(x for x in installation['files'] if x['file']==row['file'])
    entry['sha256']=row['sha256']
    entry['passives_and_gem_links_preserved']=False
    entry['passives_preserved']=True
    entry['stage_05_06_progression_validation']='stage_05_06_audit/planner_validation.json'
    entry['full_historical_passive_tree_verified']=False
    entry['combat_rotation_at_top']=False
installation['last_scoped_update_utc']=record['created_at_utc']
installation['last_scoped_update_files']=[x['file'] for x in rows]
save(installation_path,installation)
print(json.dumps({'installed':2,'preserved_files':len(untouched),'archive_matches':True,'passives_changed':False},ensure_ascii=False))
