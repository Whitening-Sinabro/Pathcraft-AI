"""Recalculate changed native stages with unmodified PoB2 and explicit proxy gear."""
from pathlib import Path
import base64,copy,json,sys,xml.etree.ElementTree as E,zlib
HERE=Path(__file__).resolve().parent;D=HERE.parent
sys.path.insert(0,str(D))
from revision3_data import BUILDS,BASES,IDS,DEFENCE_STATE
from progression_core import entries
from progression_core import NS
from pob_headless import Pob
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def xml(name):
    s=read(D/'sources'/name)['pathOfBuildingExport']
    return E.fromstring(zlib.decompress(base64.urlsafe_b64decode(s+'='*(-len(s)%4))))
ROOTS={'24':xml('ninja_hour18_lv24.json'),'43':xml('lv43_0906_0523.json'),'52':xml('lv52_0906_0744.json'),'74':xml('ninja_latest_74.json')}
META=read(HERE/'engine_gem_mapping.json')
LOOK={k:{g.get('nameSpec'):g for s in r.findall('Skills/SkillSet/Skill') if not s.get('source') for g in s.findall('Gem')} for k,r in ROOTS.items()}
OUT=HERE/'v3_inputs';OUT.mkdir(exist_ok=True)
def item_for(root,slot):
    id=root.find("Items/ItemSet/Slot[@name='"+slot+"']").get('itemId')
    return root.find("Items/Item[@id='"+id+"']")
def replace_item(root,slot,source,newid):
    n=copy.deepcopy(source);n.set('id',str(newid));root.find('Items').append(n)
    root.find("Items/ItemSet/Slot[@name='"+slot+"']").set('itemId',str(newid))
def create(index,gear,level,area,penalty,name,proxy=False,mana=False,old_fort=False,defence=False):
    b=copy.deepcopy(BUILDS[index]);r=copy.deepcopy(ROOTS[gear]);spec=r.find('Tree/Spec')
    if defence:b['passives']=entries(DEFENCE_STATE)
    if mana:b['passives']=[n for n in b['passives'] if n['id']!='passive_keystone_blood_magic']
    ids={NS[n['id']]['skill'] for n in b['passives']}|{NS['marauder594']['skill']}
    spec.set('nodes',','.join(map(str,sorted(ids))))
    for w in (1,2):
        old=spec.find('WeaponSet'+str(w))
        if old is not None:spec.remove(old)
        E.SubElement(spec,'WeaponSet'+str(w),nodes=','.join(str(NS[n['id']]['skill']) for n in b['passives'] if n.get('weapon_set')==w))
    for n in list(spec.find('Sockets')):
        if int(n.get('nodeId')) not in ids:spec.find('Sockets').remove(n)
    if index>=4:
        old=spec.find('Overrides')
        if old is not None:spec.remove(old)
        spec.append(copy.deepcopy(ROOTS['74'].find('Tree/Spec/Overrides')))
    proxy_notes=[]
    if proxy:
        for slot,num in [('Weapon 1',101),('Weapon 2 Swap',102),('Body Armour',103)]:
            replace_item(r,slot,item_for(ROOTS['74'],slot),num)
        proxy_notes=['52레벨 실측 장비에서 셉터 2개와 정신력 갑옷만 74레벨 보존본의 해당 아이템으로 교체. 실제 54레벨 전체 장비 복원 아님.',
          'II 철퇴는 52레벨 실측 희귀 Morning Star, I 방패도 52레벨 실측. 67레벨 고유 철퇴를 사용하지 않음.',
          '기본 정신력 100을 위해 Lythara 영구 보상 완료를 가정. 해당 보상 미완료라면 정신력 40이 줄어듦.',
          'AWT/함성 기본 젬 13레벨, 지면 분쇄 11레벨. 원본 이후 갑옷 옵션 전체를 적용한 대체 장비 시나리오.']
    if index<4:
        slots={s.get('name'):s for s in r.findall('Items/ItemSet/Slot')}
        for hand in (1,2):
            a=slots['Weapon '+str(hand)];sw=slots['Weapon '+str(hand)+' Swap']
            if sw.get('itemId')=='0':sw.set('itemId',a.get('itemId'))
    skills=r.find('Skills/SkillSet');skills.clear();skills.set('id','1')
    for g in b['skills']:
        title=BASES[g['id']]
        if title=='Earthshatter':continue
        s=E.SubElement(skills,'Skill',enabled='true',label=title,mainActiveSkill='1',mainActiveSkillCalcs='1')
        native=[g,*g.get('support_skills',[])]
        if title=='Ancestral Warrior Totem':native.insert(1,{'id':IDS['Earthshatter']})
        for n in native:
            en=BASES[n['id']];meta=META[n['id']]
            found=LOOK[gear].get(en)
            if found is None:found=next((LOOK[k][en] for k in ['74','52','43','24'] if en in LOOK[k]),None)
            lv=int(found.get('level','1')) if found is not None else 1;q=int(found.get('quality','0')) if found is not None else 0
            if proxy and en in ['Ancestral Warrior Totem','Fortifying Cry']:lv=13
            if proxy and en=='Earthshatter':lv=11;q=0
            if proxy and en=='Seismic Cry':lv=11;q=0
            if proxy and en=='Fortifying Cry' and old_fort:lv=12
            E.SubElement(s,'Gem',nameSpec=en,gemId=meta['gameId'],variantId=meta['variantId'],skillId=meta['skillId'],level=str(lv),quality=str(q),count='1',enabled='true',enableGlobal1='true',enableGlobal2='true')
    r.find('Build').set('level',str(level));r.find('Build').set('characterLevelAutoMode','false')
    c=r.find('Config/ConfigSet')
    for n in list(c):
        if not n.get('name','').startswith('quest'):c.remove(n)
    if proxy:
        for n in c:
            if n.get('name')=='questInterlude 3Kriar VillageLythara':n.set('boolean','true')
    for k,v in {'enemyLevel':area,'resistancePenalty':penalty,'conditionCorruptingCryStages':1,'multiplierWarcryUsedRecently':1,'multiplierNearbyEnemies':1,'multiplierNearbyRareOrUniqueEnemies':1}.items():E.SubElement(c,'Input',name=k,number=str(v))
    for k in ['conditionUsedWarcryRecently','conditionHaveTotem']:E.SubElement(c,'Input',name=k,boolean='true')
    E.SubElement(c,'Input',name='enemyIsBoss',string='Boss')
    if index>=4:E.SubElement(c,'Input',name='TotemsSummoned',number='4')
    for s in r.findall('Items/ItemSet/Slot'):
        if s.get('name','').startswith(('Flask','Charm')):s.set('active','false')
    path=OUT/(name+'.xml');E.indent(r);path.write_text(E.tostring(r,encoding='unicode'),encoding='utf-8')
    return {'case':name,'stage':index+1,'level':level,'enemy_level':area,'resistance_penalty':penalty,'gear_source':gear,'proxy':proxy_notes,'mana_bridge':mana,'nodes':sorted(ids),'path':str(path),'urgent_call':any(n['id']=='warcries34' for n in b['passives'])}

CASES=[create(1,'24',24,20,-10,'02_lv24'),create(2,'43',43,38,-20,'03_lv43'),
       create(3,'52',65,55,-30,'04_lv65_oldgear'),
       create(4,'52',54,54,-30,'05_lv54_proxy',True),
       create(4,'52',65,55,-30,'05_lv65_proxy',True),
       create(4,'52',65,55,-30,'05_lv65_defence80',True,defence=True),
       create(4,'52',65,55,-30,'05_lv65_old_fort',True,old_fort=True),
       create(4,'52',65,55,-30,'05_lv65_mana',True,True),
       create(5,'52',65,55,-30,'06_lv65_proxy',True),
       create(6,'74',74,65,-50,'07_lv74_source')]
only=sys.argv[sys.argv.index('--only')+1] if '--only' in sys.argv else None
engine=Pob();results=[x for x in read(HERE/'v3_pob_results.json') if x['case']!=only] if only else []
for case in CASES:
    if only and case['case']!=only:continue
    engine.load(case['path'])
    got=engine.json('(function() local a={} for id,n in pairs(build.spec.allocNodes) do a[#a+1]=id end return a end)()')
    assert set(case['nodes'])<=set(got)
    groups=engine.json('(function() local out={} for i,g in ipairs(build.skillsTab.socketGroupList) do local a={} for _,v in ipairs(g.gemList) do a[#a+1]=v.nameSpec end out[#out+1]={index=i,source=g.source,gems=a} end return out end)()')
    result={**case,'sets':{},'skills':[]}
    for w in (1,2):
        engine.run('build.itemsTab.activeItemSet.useSecondWeaponSet='+('true' if w==2 else 'false'))
        purity=0
        for g in groups:
            en=g['gems'][0] if g['gems'] else '';enabled=not g.get('source')
            if en=='Purity of Fire' and enabled:purity+=1;enabled=purity==w
            if en=='Harbinger of Madness':enabled=enabled and w==2
            if en in ['Raise Shield','Fortifying Cry','Resonating Shield','Seismic Cry']:enabled=enabled and w==1
            if en=='Magma Barrier':enabled=enabled and w==1 and case['stage']<5
            engine.run(f'build.skillsTab.socketGroupList[{g["index"]}].enabled='+('true' if enabled else 'false'))
        engine.run('build.configTab:BuildModList();build.buildFlag=true;runCallback("OnFrame")')
        result['sets'][str(w)]=engine.scalars('build.calcsTab.mainOutput')
        for g in groups:
            if g.get('source') or not g['gems']:continue
            en=g['gems'][0];expected=2 if en in ['Shockwave Totem','Ancestral Warrior Totem'] else 1
            if expected!=w or en not in ['Shockwave Totem','Ancestral Warrior Totem','Fortifying Cry','Seismic Cry']:continue
            idx=g['index'];active=engine.json(f'(function() local a={{}} for i,s in ipairs(build.skillsTab.socketGroupList[{idx}].displaySkillList or {{}}) do a[#a+1]={{index=i,name=s.activeEffect.grantedEffect.name,level=s.activeEffect.level}} end return a end)()')
            for sub in active:
                engine.run(f'build.mainSocketGroup={idx};build.skillsTab.socketGroupList[{idx}].mainActiveSkill={sub["index"]};build.skillsTab.socketGroupList[{idx}].mainActiveSkillCalcs={sub["index"]};build.buildFlag=true;runCallback("OnFrame")')
                result['skills'].append({'host':en,'active':sub['name'],'effective_level':sub['level'],'weapon_set':w,'output':engine.scalars('build.calcsTab.mainOutput')})
    results.append(result)
    results.sort(key=lambda x:next(i for i,c in enumerate(CASES) if c['case']==x['case']))
    (HERE/'v3_pob_results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Calculated '+case['case'],flush=True)
(HERE/'v3_scenarios.json').write_text(json.dumps(CASES,ensure_ascii=False,indent=2),encoding='utf-8')
