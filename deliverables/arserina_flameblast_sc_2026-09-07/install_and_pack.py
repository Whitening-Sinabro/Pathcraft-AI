"""Install only the verified new files; preserve every pre-existing planner."""
from pathlib import Path
import hashlib, json, shutil, sys, zipfile
sys.stdout.reconfigure(encoding='utf-8')
H=Path(__file__).resolve().parent
GAME=Path.home()/'Documents/My Games/Path of Exile 2/BuildPlanner'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8'))
checks=read(H/'validation.json')['checks']
sources=sorted((H/'BuildPlanner').glob('*.build'))
assert len(sources)==len(checks)==4
expected={r['file']:r['sha256'] for r in checks}
for p in sources:assert sha(p)==expected[p.name]
GAME.mkdir(parents=True,exist_ok=True)
before={p.name:sha(p) for p in GAME.glob('*.build')}
for p in sources:
 target=GAME/p.name
 if target.exists():assert sha(target)==sha(p),f'Existing different file: {target}'
for p in sources:
 target=GAME/p.name
 if not target.exists():shutil.copy2(p,target)
 assert sha(target)==sha(p)
assert all(sha(GAME/name)==digest for name,digest in before.items())
manifest={'game_directory':str(GAME),'installed':[{'file':p.name,'sha256':sha(p)} for p in sources],
 'existing_files_unchanged':before,'game_runtime_verified':False,
 'start_with':sources[0].name,'source_original_files_modified':False}
(H/'installation.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
# Human-readable transition table; the detailed machine-readable route remains
# available for replay verification. Native planner node names are localized by
# the game; English source names are retained beside IDs for exact matching.
repo=H.parents[1]
tree=read(repo/'data/_cache/tree_0_5.json')
names={n['stringId']:n['name'] for n in tree['nodes'].values() if isinstance(n,dict) and 'stringId'in n}
rows=['# 단계별 패시브 전환 순서','',
 '원본과 현재 캐릭터 사이의 연결을 유지하도록 검증한 순서다. 캐릭터를 자동 변경하지 않는다. 실제 골드는 게임의 환불창에서 확인한다.','',
 '유지할 노드도 새 경로를 먼저 연결해야 남길 수 있으므로, 환불만 한꺼번에 하지 말고 표시된 순서를 따른다. 무기 세트는 0=공통, 1=세트 I, 2=세트 II다.','']
for t in read(H/'transition.json'):
 rows += [f'## {t["from_stage"]:02d} → {t["to_stage"]:02d}','',
  f'환불 {t["refunds"]}개. 진행에 필요한 일반 포인트 총량 {t["required_pool"]}점. 전직은 목표 단계의 포인트도 확보해야 한다.','',
  '| 순서 | 조작 | 노드 이름·식별자 | 무기 세트 |','|---|---|---|---|']
 for i,op in enumerate(t['operations'],1):
  label='환불' if op['action']=='refund' else '할당'
  rows.append(f'| {i} | {label} | {names[op["id"]]} (`{op["id"]}`) | {op["weapon_set"]} |')
 rows.append('')
(H/'패시브전환순서.md').write_text('\n'.join(rows)+'\n',encoding='utf-8')
archive=H/'Arserina-SC-한국어-빌드플래너.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
 for p in sources:z.write(p,'BuildPlanner/'+p.name)
 for name in ['먼저읽기.md','패시브전환순서.md','transition.json','validation.json','installation.json']:
  z.write(H/name,name)
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None
 for p in sources:assert hashlib.sha256(z.read('BuildPlanner/'+p.name)).hexdigest()==sha(p)
print(json.dumps({'installed':len(sources),'preserved':len(before),'archive':str(archive),
 'archive_sha256':sha(archive),'start_with':sources[0].name,'runtime_verified':False},ensure_ascii=False))
