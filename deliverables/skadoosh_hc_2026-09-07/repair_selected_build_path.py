"""Bounded repair of the v3 filename migration; never edits game settings."""
from pathlib import Path
import datetime, hashlib, json, shutil, zipfile

HERE=Path(__file__).resolve().parent
GAME=Path('C:/Users/User/Documents/My Games/Path of Exile 2').resolve()
OUT=HERE/'revision3'
READY=HERE/'ready'
BACKUP=HERE/'before_selected_path_repair'
OLD='01 시작-근접 기초.build'
RENAMED='01 시작 - 근접과 방패.build'
LOG=Path('C:/Program Files (x86)/Grinding Gear Games/Path of Exile 2 - poe2_production/logs/Client.txt')

def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
def archive(p,label):
    dest=BACKUP/label
    assert p.is_file() and dest.resolve().is_relative_to(HERE)
    if dest.exists():assert sha(dest)==sha(p),dest
    else:shutil.copy2(p,dest)
    assert sha(dest)==sha(p)

assert not BACKUP.exists(), 'One-shot repair already started; inspect its manifest before proceeding.'
manifest=read(HERE/'installation_revision3.json')
for row in manifest['installed']:
    assert sha(Path(row['path']))==row['sha256'],row['path']
for path,digest in manifest['unrelated_files_preserved'].items():assert sha(Path(path))==digest
original_payload=(OUT/'BuildPlanner'/RENAMED).read_bytes()
assert (READY/'BuildPlanner'/RENAMED).read_bytes()==original_payload
assert (GAME/'BuildPlanner'/RENAMED).read_bytes()==original_payload
selected_line=next(x for x in (GAME/'poe2_production_Config.ini').read_text(encoding='utf-8-sig').splitlines() if x.startswith('active_builds='))
selected=next(x for x in json.loads(selected_line.split('=',1)[1]) if x['character']=='HCFR_CCTBurger')
assert selected['path']=='file:'+str(GAME/'BuildPlanner'/OLD).replace('\\','/')
assert not (GAME/'BuildPlanner'/OLD).exists()
BACKUP.mkdir()
archive(HERE/'installation_revision3.json','installation_revision3.json')
archive(HERE/'validation_revision3.json','validation_revision3.json')
archive(HERE/'Skadoosh-HC-한국어-필터와플래너.zip','package.zip')
dump(BACKUP/'selected_build_reference.json',selected)
lines=LOG.read_text(encoding='utf-8',errors='replace').splitlines()
evidence=[line for line in lines if line.startswith('2026/09/07 16:39:32') and '[BuildPlanner]' in line]
assert all(any('Successfully loaded build' in line and Path(x['path']).name in line for line in evidence) for x in manifest['installed'] if x['path'].endswith('.build'))
(BACKUP/'client_load_before.txt').write_text('\n'.join(evidence)+'\n',encoding='utf-8')
screenshot=Path('C:/Users/User/AppData/Local/Temp/orca-computer-use/ef29ee26-818d-45d8-bf50-7c0add37e678-screenshot.png')
shutil.copy2(screenshot,BACKUP/'game_stage02_loaded.png')

# Restore the selected path first. The contents and displayed title stay v3.
for label,folder in [('canonical',OUT/'BuildPlanner'),('ready',READY/'BuildPlanner'),('game',GAME/'BuildPlanner')]:
    assert folder.resolve().is_relative_to(HERE) or folder.resolve()==GAME/'BuildPlanner'
    src=folder/RENAMED;dest=folder/OLD
    assert src.read_bytes()==original_payload and not dest.exists()
    archive(src,label+'_'+RENAMED)
    dest.write_bytes(original_payload)
    assert dest.read_bytes()==src.read_bytes()
    # One exact, archived owned file; no directory or wildcard deletion.
    assert src.resolve().parent==folder.resolve() and sha(BACKUP/(label+'_'+RENAMED))==sha(src)
    src.unlink()

guide_old='이전 13개 플래너는 백업 후 활성 폴더에서 제외하고 새 7개만 설치한다. 다른 빌드 파일은 유지한다. 게임이 열려 있으면 플래너 목록을 다시 확인하고 필터를 다시 선택한다. 실제 게임에서 이 수정본을 다시 읽는 확인은 아직 수행하지 않았다.'
guide_new='플래너는 7개다. 첫 단계의 실제 파일명은 기존 캐릭터의 선택 경로를 보존하기 위해 `01 시작-근접 기초.build`를 유지하며 게임 표시명은 `01 시작 - 근접과 방패`다. 내용은 최신 방송 대조본이다. 나머지 6개는 표의 표시명과 파일명이 같다. 기존 파일 13개의 원본을 백업했고, 첫 단계 경로를 제외한 이전 12개는 활성 목록에서 제외했다. 게임 로그에서 7개 모두 정상 로드를 확인했고 실제 게임의 02 단계 트리 표시도 확인했다. `unrecognised build plan id`는 이번 설치에서 선택 중이던 파일 경로를 바꾼 뒤 남은 참조와 일치했으며, 첫 단계의 원래 경로를 복원했다.'
for path in [OUT/'시작안내.md',HERE/'reports_revision3.py']:
    content=path.read_text(encoding='utf-8');assert guide_old in content,path
    archive(path,'source_'+path.name)
    path.write_text(content.replace(guide_old,guide_new),encoding='utf-8')
check=OUT/'검증결과.md'
archive(check,'검증결과.md')
content=check.read_text(encoding='utf-8').replace('이전 배포본이 읽히는 것은 사용자 확인을 받았지만 이번 수정본의 실제 게임 재로딩·실전 전투는 직접 확인하지 않았다.','실제 게임 로그에서 7개 정상 로드와 게임 화면에서 02 트리 표시를 확인했다. 실전 전투 성능은 직접 검증하지 않았다.')
content=content.replace('기존 플래너 13개는 .build.v2-backup 확장자로 바꿔 활성 목록에서 제외한다.','기존 13개 원본은 보존한다. 첫 단계는 저장된 선택 경로인 01 시작-근접 기초.build에서 최신 내용을 제공하며, 나머지 12개 이전 경로는 활성 목록에서 제외한다.')
content+='\n## 선택 경로 오류 수정\n\n캐릭터 HCFR_CCTBurger의 active_builds가 가리키던 01 시작-근접 기초.build 경로를 복원했다. JSON·패시브·스킬·장비 내용은 수정 전 v3와 바이트 단위로 동일하다. 실제 파일명과 게임 표시명을 분리하고 생성기·검사기·설치기에 선택 경로 보존 검사를 추가했다. 새 파일 7개의 정상 로드 로그와 02 단계 게임 화면은 before_selected_path_repair에 보존했다.\n'
check.write_text(content,encoding='utf-8')
for name in ['시작안내.md','검증결과.md']:shutil.copy2(OUT/name,READY/name)
progress=read(HERE/'progression_v3.json');assert progress[0]['file']==RENAMED
progress[0]['file']=OLD;dump(HERE/'progression_v3.json',progress)
for row in manifest['installed']:
    if Path(row['path']).name==RENAMED:row['path']=str(GAME/'BuildPlanner'/OLD)
    assert sha(Path(row['path']))==row['sha256']
for path,digest in manifest['unrelated_files_preserved'].items():assert sha(Path(path))==digest
assert len(list((GAME/'BuildPlanner').glob('*.build')))==12
assert len(list((OUT/'BuildPlanner').glob('*.build')))==7
files=sorted(p for p in OUT.rglob('*') if p.is_file());assert len(files)==18
zipname=HERE/'Skadoosh-HC-한국어-필터와플래너.zip'
with zipfile.ZipFile(zipname,'w',zipfile.ZIP_DEFLATED) as z:
    for p in files:z.write(p,p.relative_to(OUT).as_posix())
with zipfile.ZipFile(zipname) as z:
    assert z.testzip() is None and len(z.namelist())==18
    for p in files:assert z.read(p.relative_to(OUT).as_posix())==p.read_bytes()==(READY/p.relative_to(OUT)).read_bytes()
manifest.update(zip_sha256=sha(zipname),selected_path_repair_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),game_parser_loaded_planners=7,new_game_UI_loaded=True,new_game_UI_verified_stage='02',selected_path_restored=str(GAME/'BuildPlanner'/OLD),repair_evidence=str(BACKUP))
dump(HERE/'installation_revision3.json',manifest)
print(json.dumps({'restored':str(GAME/'BuildPlanner'/OLD),'planner_payloads_unchanged':True,'planners':7,'zip_members':18,'zip_sha256':sha(zipname),'unrelated_files_unchanged':len(manifest['unrelated_files_preserved'])},ensure_ascii=False))
