"""Install verified filters without replacing existing files; package with planners."""
from pathlib import Path
import hashlib, json, shutil, sys, zipfile

sys.stdout.reconfigure(encoding='utf-8')
HERE=Path(__file__).resolve().parent
GAME=Path.home()/'Documents/My Games/Path of Exile 2'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads(p.read_text(encoding='utf-8'))

validation=read(HERE/'filter_validation.json')
rows=[validation['creator_campaign']]+validation['maps']
assert len(rows)==3
assert all(r['sweep_regressions']==0 for r in validation['maps'])
files=[HERE/'Filters'/r['file']for r in rows]
for p,r in zip(files,rows): assert sha(p)==r['sha256']
before={p.name:sha(p)for p in GAME.glob('*.filter')}
planner_before={p.name:sha(p)for p in (GAME/'BuildPlanner').glob('*.build')}
config=GAME/'poe2_production_Config.ini'
config_before=sha(config)
for p in files:
    target=GAME/p.name
    if target.exists(): assert sha(target)==sha(p), f'Existing different file: {target}'

# Keep the existing sound files. The ZIP carries the exact copies whose names
# are referenced by the original filter; Windows resolves names case-insensitively.
sound_dir=HERE/'Sounds'
sound_dir.mkdir(exist_ok=True)
for row in validation['creator_campaign']['sound_files']:
    source=GAME/row['file']
    assert sha(source)==row['sha256']
    target=sound_dir/row['file']
    if target.exists(): assert sha(target)==row['sha256']
    else: shutil.copy2(source,target)
for p in files:
    target=GAME/p.name
    if not target.exists(): shutil.copy2(p,target)
    assert sha(target)==sha(p)
assert all(sha(GAME/n)==v for n,v in before.items())
assert all(sha(GAME/'BuildPlanner'/n)==v for n,v in planner_before.items())
assert sha(config)==config_before

plan_rows=read(HERE/'validation.json')['checks']
planners=sorted((HERE/'BuildPlanner').glob('*.build'))
assert len(planners)==4
expected={r['file']:r['sha256']for r in plan_rows}
for p in planners: assert sha(p)==expected[p.name]

manifest={'installed_filters':[{'file':p.name,'sha256':sha(p)}for p in files],
          'game_directory':str(GAME),'original_filters_preserved':before,
          'planners_preserved':planner_before,'configuration_unchanged':True,
          'sound_files_already_installed':validation['creator_campaign']['sound_files'],
          'creator_filter_followed_online':False,'game_runtime_verified':False,
          'select_now':files[0].name}
(HERE/'filter_installation.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

archive=HERE/'Arserina-SC-플래너와필터.zip'
entries=[]
for p in files: entries.append((p,p.name))
for p in sorted(sound_dir.glob('*.mp3')): entries.append((p,p.name))
for p in planners: entries.append((p,'BuildPlanner/'+p.name))
for name in ['먼저읽기.md','필터사용안내.md','패시브전환순서.md','transition.json',
             'validation.json','filter_validation.json','filter_installation.json']:
    entries.append((HERE/name,name))
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED)as z:
    for p,name in entries:z.write(p,name)
with zipfile.ZipFile(archive)as z:
    assert z.testzip() is None
    assert len(z.namelist())==len(set(n.casefold() for n in z.namelist()))
    for p,name in entries:assert hashlib.sha256(z.read(name)).hexdigest()==sha(p)
package={'file':archive.name,'sha256':sha(archive),'filters':3,'planners':4,
         'sound_files':len(validation['creator_campaign']['sound_files']),
         'zip_entries':len(entries),'all_entries_hash_verified':True}
(HERE/'package_manifest.json').write_text(json.dumps(package,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(package,ensure_ascii=False))
print('Installed 3 filters; preserved existing filters, planners, sounds and selected filter.')
