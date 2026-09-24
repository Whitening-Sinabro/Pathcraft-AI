"""Install only this delivery's named outputs; preserve and verify other files."""
from pathlib import Path
import datetime, hashlib, json, shutil
HERE=Path(__file__).resolve().parent
OUT=HERE/'revision2'
GAME=Path('C:/Users/User/Documents/My Games/Path of Exile 2')
BACKUP=HERE/'installed_before_revision2'
BACKUP.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
report=json.loads((HERE/'validation_revision2.json').read_text(encoding='utf-8'))
assert len(report['planners'])==13 and len(report['transitions'])==12 and len(report['source_comparisons'])==6
planners=sorted((OUT/'BuildPlanner').glob('*.build'))
filters=sorted((OUT/'Filters').glob('*.filter'))
assert len(planners)==13 and len(filters)==3
pairs=[(p,GAME/'BuildPlanner'/p.name) for p in planners]+[(p,GAME/p.name) for p in filters]
targets={b.resolve() for a,b in pairs}
other={p.resolve():sha(p) for p in (GAME/'BuildPlanner').glob('*.build') if p.resolve() not in targets}
other.update({p.resolve():sha(p) for p in GAME.glob('*.filter') if p.resolve() not in targets})
installed=[]
for src,dest in pairs:
    dest.parent.mkdir(exist_ok=True)
    backup=BACKUP/dest.name
    if dest.exists() and not backup.exists():shutil.copy2(dest,backup)
    shutil.copy2(src,dest)
    assert src.read_bytes()==dest.read_bytes()
    installed.append({'source':str(src),'installed':str(dest),'sha256':sha(dest)})
assert all(p.exists() and sha(p)==digest for p,digest in other.items())
manifest={'installed_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'installed':installed,
          'unrelated_files_preserved':{str(p):h for p,h in other.items()},'game_UI_loaded':False,'backup_directory':str(BACKUP)}
(HERE/'installation_revision2.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'Installed and hash-verified {len(planners)} planners and {len(filters)} filters; preserved {len(other)} other planner/filter files.')
