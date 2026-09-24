"""Read the DATAREADY Taengjung contract; write planner data and evidence only."""
from pathlib import Path
import json, hashlib, base64
P=Path(__file__).resolve().parent
E=P.parent
sha=lambda raw:hashlib.sha256(raw).hexdigest()
contract_path=E/'taengjung_progression/planner_contract.json'
c=json.loads(contract_path.read_text(encoding='utf8'))
pack_path=E/'planner_data/build_data.json'
pack=json.loads(pack_path.read_text(encoding='utf8'))
mapping=json.loads((E/'taengjung_progression/install_mapping.json').read_text(encoding='utf8'))
assert c['active_route']=='taengjung_progression'
old=json.loads((P/'planner-data.js').read_text(encoding='utf8').removeprefix('window.PLANNER_DATA=').removesuffix(';'))
refs=c['reference_stages']
# Route order = installed order: 00~02 별이슬 act trees, then 03~07 Taengjung. The 40-level alternative is not on the route.
zero=c.get('zero_track',[])
shared=[r['id'] for r in refs]+[s['id'] for s in c['stages'] if s['index']==2]
tracks={'zero':shared+[s['id'] for s in zero],'capital':shared+[s['id'] for s in c['stages'] if s['index']>=3]}
active_ids=shared+[s['id'] for s in zero]+tracks['capital'][len(shared):]
own_ids=set(active_ids)|{s['id'] for s in c['stages']}
ARCHIVE_PREFIX='이전 자료 · '
# Legacy stages stay loadable for saved user state, but are labelled as non-default reference.
archived=[{**s,'archived':True,'label':ARCHIVE_PREFIX+s['label'].removeprefix(ARCHIVE_PREFIX)} for s in old['stages'] if s['id'] not in own_ids]
items={};stages=[];native={};reference={};sources=[];ko_names={}
for source in c['sources']:
    path=E/'taengjung_progression'/source['local_copy'] if source.get('local_copy') else Path(source['file'])
    assert path.exists(),path
    actual=sha(path.read_bytes())
    assert actual==source['sha256'],str(path)+' source changed'
    sources.append({'id':source['id'],'path':str(path),'sha256':actual})
def download(entry_name,rel,expected,active):
    raw=(E/rel).read_bytes()
    assert sha(raw)==expected,rel
    return {'filename':entry_name,'downloadFilename':entry_name,'relativePath':rel,'base64':base64.b64encode(raw).decode('ascii'),'sha256':sha(raw),'isActive':active}
def skills_of(sid,groups):
    return [{**g,'id':sid+'-'+str(i),'weaponSet':str(g['weapon_set']) if g['weapon_set'] else '1+2','triggered':g.get('actives',[])[1:],'note':g.get('condition','')} for i,g in enumerate(groups)]
def equipment_of(sid,eqs):
    out=[]
    for e in eqs:
        en,_,ko=e['name'].partition(' / ')
        if ko:ko_names[en]=ko
        x={**e,'name':en,'mods':[],'levelReq':None,'source':'탱정 자료 기반 장비 조건 · 실제 착용 미확인'}
        out.append(x);items[sid+':'+e['slot']]=x
    return out
for r in refs:
    entry=next(x for x in mapping['files'] if x['source']==r['native_file'])
    assert entry['sha256']==r['native_sha256']
    native[r['id']]=download(entry['name'],r['native_file'],r['native_sha256'],True)
    stages.append({**r,'isRef':True,'kind':'byeolisul_act','creator':'별이슬골짜기','ascendancy':'Smith of Kitava (탱정 보정 · 원본은 워브링어)',
      'sourceLabel':'별이슬골짜기 0.5.5 액트 PoB 트리 — 탱정이 추천한 액트 가이드(9/20 방송)','passives':r['passives']+[{**n,'ascendancyName':'Smith of Kitava','isFreeAllocate':n['id'] in ['5852','9988']} for n in r['ascendancy_nodes']],'skills':skills_of(r['id'],r['skill_groups']),
      'equipment':equipment_of(r['id'],r['equipment']),'conditions':['액트는 별이슬 가이드 순서대로. 탱정 세팅(03)은 액트가 끝난 뒤(맵 진입).',r['ascendancy_order']],
      'weapon_set_nodes':{str(k):[n['id'] for n in r['passives'] if n['weapon_set']==k] for k in [1,2]},'grantedSkills':[]})
for s in [x for x in c['stages'] if x['index']<=2]+zero+[x for x in c['stages'] if x['index']>=3]:
    if s.get('display_number'):
        entry=next(x for x in mapping['files'] if x['source']==s['native_file'])
        assert entry['sha256']==s['native_sha256']
        native[s['id']]=download(entry['name'],s['native_file'],s['native_sha256'],True)
    else:
        name=Path(s['native_file']).name
        reference[s['id']]=download(name,s['native_file'],s['native_sha256'],False)
    nodes=s['passives']+[{**n,'ascendancyName':'Smith of Kitava','isFreeAllocate':n['id'] in ['5852','9988']} for n in s['ascendancy_nodes']]
    equipment=equipment_of(s['id'],s['equipment'])
    stages.append({**s,'ascendancy':'Smith of Kitava','sourceLabel':'Pathcraft · 탱정 자료 기반 구성안 / 저자의 정확한 액트 트리 아님','source':{'file':'../taengjung_progression/planner_contract.json'},'passives':nodes,'skills':skills_of(s['id'],s['skill_groups']),'equipment':equipment,'weapon_set_nodes':{str(k):[n['id'] for n in s['passives'] if n['weapon_set']==k] for k in [1,2]},'grantedSkills':[]})
# Author snapshots stay downloadable as optional, unnumbered references (never installed by default).
protected={Path(k).name:v for k,v in json.loads((E/'taengjung_progression/source_hashes.json').read_text(encoding='utf8')).items()}
REFERENCE={'kitava-28509':('archive-28509.build','탱정_참고_과거_일반갑옷과철퇴.build'),'kitava-285e2':('archive-285e2.build','탱정_참고_과거_방패와보조보강.build'),'kitava-28604':('archive-28604.build','탱정_참고_과거_황동철갑전환.build'),'kitava-28695':('archive-28695.build','탱정_참고_과거_투구교체_목죄이는명령.build'),'kitava-29d39':('current-kitava-29d39.build','탱정_참고_최신29d39_전체트리_선택.build')}
for sid,(src,name) in REFERENCE.items():
    reference[sid]=download(name,'native_planner/'+src,protected[src],False)
by_phase={s['index']:s['id'] for s in c['stages']}
data={**old,'stages':stages+archived,'items':items,'nodes':{str(n['id']):n for n in pack['tree']['nodes']},'edges':pack['tree']['edges'],'treeSource':pack['tree'],'sourceSHA256':sha(pack_path.read_bytes()),'contractSHA256':sha(contract_path.read_bytes()),'taengjung':c,'activeStageIds':active_ids,'tracks':tracks,'nativeFiles':native,'originalNativeFiles':{},'activeRouteManifest':mapping,'transitionPlan':None,'transitionStages':active_ids,'authoredStages':[],'koNames':ko_names,'referenceFiles':reference}
data['guideMap']={k:refs[0]['id'] for k in old['guideMap']}
data['guideMap'].update({'act4':refs[1]['id'],'interlude':refs[2]['id'],'low-budget':by_phase[4],'next-upgrades':by_phase[6]})
(P/'planner-data.js').write_text('window.PLANNER_DATA='+json.dumps(data,ensure_ascii=False,separators=(',',':'))+';',encoding='utf8')
manifest={'route':'taengjung_progression','pack_sha256':data['sourceSHA256'],'contract_sha256':data['contractSHA256'],'sources':sources,'downloads':[{k:v for k,v in f.items() if k!='base64'} for f in native.values()],'optional_reference_downloads':[{k:v for k,v in f.items() if k!='base64'} for f in reference.values()],'local_backup_excluded_from_publication':'planner/local-backups/'}
(P/'taengjung-source-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
print('Verified and embedded',len(native),'route downloads,',len(reference),'optional references and',len(sources),'source hashes')
