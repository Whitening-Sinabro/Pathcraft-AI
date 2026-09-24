"""Package the verified and installed revision with no stale user-facing files."""
import hashlib,json,shutil,zipfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
OUT=HERE/'revision2'; READY=HERE/'ready'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
check=read(HERE/'validation_revision2.json')
install=read(HERE/'installation_revision2.json')
assert len(check['planners'])==13 and len(install['installed'])==16
for entry in install['installed']:
    assert sha(Path(entry['source']))==entry['sha256']==sha(Path(entry['installed']))
for p,h in install['unrelated_files_preserved'].items():assert sha(Path(p))==h
docs=['시작안내.md','무기세트와젬연결.md','장비추천옵션.md','패시브전환.md','검증결과.md','시뮬레이션결과.md','시뮬레이션그래프.html']
files=sorted((OUT/'BuildPlanner').glob('*.build'))+sorted((OUT/'Filters').glob('*.filter'))+[OUT/n for n in docs]
assert len(files)==16+len(docs) and all(p.is_file() for p in files)
assert len(list((OUT/'BuildPlanner').glob('*.build')))==13
archive=HERE/'Skadoosh-HC-한국어-필터와플래너.zip'
backup=HERE/'sources/first_delivery_complete.zip'
if archive.exists() and not backup.exists():shutil.copy2(archive,backup)
for src in files:
    dest=READY/src.relative_to(OUT);dest.parent.mkdir(exist_ok=True)
    shutil.copy2(src,dest)
    assert src.read_bytes()==dest.read_bytes()
manifest='\n'.join(f'{sha(p)}  {p.relative_to(OUT).as_posix()}' for p in files)+'\n'
(OUT/'SHA256SUMS.txt').write_text(manifest,encoding='utf-8')
shutil.copy2(OUT/'SHA256SUMS.txt',READY/'SHA256SUMS.txt')
files.append(OUT/'SHA256SUMS.txt')
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
    for p in files:z.write(p,p.relative_to(OUT).as_posix())
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None and len(z.namelist())==len(files)
    for p in files:assert z.read(p.relative_to(OUT).as_posix())==p.read_bytes()
assert {p.name for p in (READY/'BuildPlanner').glob('*.build')}=={p.name for p in (OUT/'BuildPlanner').glob('*.build')}
sim=read(HERE/'simulation/validation_simulation.json')
presentation=read(HERE/'validation_presentation.json')
assert len(presentation['planners'])==13 and presentation['previous_simulation_outputs_unchanged']
result={'revision':'2.3-weapon-and-skill-overview','planners':13,'filters':3,'guides':docs,'zip':str(archive),'zip_bytes':archive.stat().st_size,'zip_sha256':sha(archive),'zip_members':len(files),
        'validated_external_stages':6,'validated_adjacent_transitions':12,'validated_optional_defence_routes':14,'installation_matches_package':True,'unrelated_files_preserved':8,'previous_revision_loading_user_confirmed':True,'modified_revision_game_reload_tested':False,'pob_cases':sim['pob_cases'],'resource_cases':sim['resource_cases'],'combat_playtested':False,'equipment_and_gem_hints_checked':True,'max_equipment_hint_characters':max(x['max_equipment_hint_after'] for x in presentation['planners'])}
(HERE/'validation_final_v2.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,ensure_ascii=True,indent=2))
