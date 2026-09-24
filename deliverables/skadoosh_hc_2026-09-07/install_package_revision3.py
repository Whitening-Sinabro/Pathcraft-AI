"""Install only owned files after validation; archive all replaced versions."""
from pathlib import Path
import datetime,hashlib,json,shutil,zipfile
HERE=Path(__file__).resolve().parent;OUT=HERE/'revision3';GAME=Path('C:/Users/User/Documents/My Games/Path of Exile 2')
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,data):p.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
r=read(HERE/'validation_revision3.json');view=read(HERE/'simulation/v3_viewer_korean_validation.json')
assert len(r['planners'])==7 and len(r['transitions'])==7 and len(r['source_comparisons'])==4
assert view['count']==45 and view['labelsKorean'] and not view['errors']
for row in r['planners']:assert sha(OUT/'BuildPlanner'/row['file'])==row['sha256']
for row in r['filters']:assert sha(OUT/'Filters'/row['file'])==row['sha256']
check=['# 검증 결과 · v3','','플래너 7개, 필터 3개, 한국어 문서와 오프라인 그래프를 배포한다. 원본 방송 18시간 52분 54초의 두 전사 문맥 대조와 2,301개 탐색 화면, 핵심 32개 근거를 기록했다.','',
 '## 통과한 검사','','- 저장한 JSON을 독립 검사기로 다시 읽어 공식 필드·노드/젬 ID·한글 사용법·추천 옵션을 확인했다.\n- 7개 트리의 공통/I/II 연결과 환불·추가의 매 단계 비용을 검증했다. 46레벨 실측 내부 경유를 포함해 경로 7개다.\n- 24·43·52·74레벨 공개 원본 4개와 실제 노드/연결을 비교했다. 토템 내부 액티브는 공식 메타 미지원에 맞춘 표시 변환을 되돌려 대조했다.\n- 일부러 고립된 키스톤을 추가한 대조 사례가 검사에서 거부되는지 확인했다.\n- 69점에서 회복·방어를 먼저 더한 80점 경로의 각 연결을 검증했다. 05→06 패시브 동일, 06→07은 기존 배정을 유지하는 확장이다.\n- 3개 필터의 원본 끝부분 일치·추가 Hide 없음·지원되는 드롭 상태 전수 검사·정신력/한손 철퇴 표시·고유 대조 검사를 통과했다.\n- PoB 입력 10개와 자원 조건 45개를 계산했고, 같은 Playwright 브라우저에서 그래프 45개 조건과 한글 라벨/실패 표시를 확인했다.','',
 '## 아직 확정하지 않은 것','','- 05의 69점 트리는 영상의 54레벨 전체 배정을 복원한 원본이 아니라 방송 기반 재구성안이다.\n- 파콰테/메아리의 모든 반복 비용·회복량은 미확정이다. 06을 조건부 단계로 유지한다.\n- PoB는 전체 가시 폭발과 실제 이동/명중 상황, 몬스터 AI·기절·다수 동시 피격을 재현하지 않는다.\n- 필터 평가기가 모델링하지 않는 원본 조건은 원본 보존으로 보호했으며 그 조건까지 시뮬레이션했다고 주장하지 않는다.\n- 이전 배포본이 읽히는 것은 사용자 확인을 받았지만 이번 수정본의 실제 게임 재로딩·실전 전투는 직접 확인하지 않았다.','',
 '## 설치와 보존','','설치 후 모든 새 파일의 해시를 검사하고 다른 빌드/필터의 해시도 대조한다. 기존 13개 플래너와 3개 필터는 installed_before_revision3에 백업한다. 기존 플래너 13개는 .build.v2-backup 확장자로 바꿔 활성 목록에서 제외한다. ready 폴더의 이전 버전은 sources/ready_before_v3에 보존한다. 작업용 방송·원본 전사는 ZIP에 포함하지 않는다.','']
(OUT/'검증결과.md').write_text('\n'.join(check),encoding='utf-8')
old=read(HERE/'installation_revision2.json');owned={Path(x['installed']).resolve():x for x in old['installed']}
for p,x in owned.items():assert p.exists() and sha(p)==x['sha256'],('owned file changed',p)
other={p.resolve():sha(p) for p in (GAME/'BuildPlanner').glob('*.build') if p.resolve() not in owned}
other.update({p.resolve():sha(p) for p in GAME.glob('*.filter') if p.resolve() not in owned})
backup=HERE/'installed_before_revision3';backup.mkdir(exist_ok=True)
for p in owned:
    dest=backup/p.name
    if not dest.exists():shutil.copy2(p,dest)
    assert sha(dest)==sha(p)
newpairs=[(p,GAME/'BuildPlanner'/p.name) for p in sorted((OUT/'BuildPlanner').glob('*.build'))]+[(p,GAME/p.name) for p in sorted((OUT/'Filters').glob('*.filter'))]
assert len(newpairs)==10
# Never retire a selected owned path. A display-name edit is not permission to
# invalidate the character's persisted build ID.
new_paths={dest.resolve() for _,dest in newpairs}
config=GAME/'poe2_production_Config.ini'
active_line=next((line for line in config.read_text(encoding='utf-8-sig').splitlines() if line.startswith('active_builds=')),None)
if active_line:
    for selected in json.loads(active_line.split('=',1)[1]):
        if selected['path'].startswith('file:'):
            selected_path=Path(selected['path'][5:]).resolve()
            assert selected_path not in owned or selected_path in new_paths,('selected build path must be preserved',selected['character'],selected_path)
for src,dest in newpairs:
    assert dest.resolve().is_relative_to(GAME.resolve())
    assert not dest.exists() or dest.resolve() in owned,('unowned destination',dest)
    shutil.copy2(src,dest);assert sha(src)==sha(dest)
disabled=[]
for p in owned:
    if p.suffix!='.build':continue
    if p in new_paths:continue
    assert p.parent== (GAME/'BuildPlanner').resolve()
    dest=p.with_suffix('.build.v2-backup');assert not dest.exists()
    p.rename(dest);disabled.append(str(dest))
assert all(p.exists() and sha(p)==digest for p,digest in other.items())
# Both absolute targets are checked inside the named delivery before moving the
# previous ready directory. No recursive deletion or broad cleanup is performed.
ready=(HERE/'ready').resolve();archive=(HERE/'sources/ready_before_v3').resolve()
assert ready.is_relative_to(HERE.resolve()) and archive.is_relative_to(HERE.resolve())
assert ready.name=='ready' and not archive.exists()
if ready.exists():ready.rename(archive)
shutil.copytree(OUT,ready)
zipname=HERE/'Skadoosh-HC-한국어-필터와플래너.zip';oldzip=HERE/'sources/Skadoosh-HC-before-broadcast-audit-v2.zip'
if zipname.exists():
    assert not oldzip.exists();shutil.copy2(zipname,oldzip)
files=sorted(p for p in OUT.rglob('*') if p.is_file())
assert len(files)==18,(len(files),[p.name for p in files])
with zipfile.ZipFile(zipname,'w',zipfile.ZIP_DEFLATED) as z:
    for p in files:z.write(p,p.relative_to(OUT).as_posix())
with zipfile.ZipFile(zipname) as z:
    assert z.testzip() is None and len(z.namelist())==18
    for p in files:assert z.read(p.relative_to(OUT).as_posix())==p.read_bytes()==(ready/p.relative_to(OUT)).read_bytes()
manifest={'installed_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'installed':[{'path':str(dest),'sha256':sha(dest)} for src,dest in newpairs],
  'disabled_old_planners':disabled,'unrelated_files_preserved':{str(p):h for p,h in other.items()},'backup':str(backup),'ready_archive':str(archive),
  'zip':str(zipname),'zip_sha256':sha(zipname),'zip_members':18,'new_game_UI_loaded':False,'verification':str(HERE/'validation_revision3.json')}
dump(HERE/'installation_revision3.json',manifest)
print(json.dumps({'installed_planners':7,'installed_filters':3,'old_planners_archived':len(disabled),'unrelated_preserved':len(other),'zip_members':18,'zip_sha256':sha(zipname)},ensure_ascii=False))
