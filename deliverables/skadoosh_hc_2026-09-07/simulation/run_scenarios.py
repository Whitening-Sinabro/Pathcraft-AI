"""Generate explicit PoB inputs from preserved gear plus delivered stage trees/gems."""
from pathlib import Path
import base64,copy,hashlib,json,sys,time,xml.etree.ElementTree as ET,zlib
from pob_headless import Pob
HERE=Path(__file__).resolve().parent; DELIVERY=HERE.parent; REPO=DELIVERY.parents[1]
OUT=HERE/'inputs';OUT.mkdir(exist_ok=True)
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def decoded(model):
    e=model['pathOfBuildingExport'];return ET.fromstring(zlib.decompress(base64.urlsafe_b64decode(e+'='*(-len(e)%4))))
NATIVE={p.stem.split()[0]:read(p) for p in (DELIVERY/'revision2/BuildPlanner').glob('*.build')}
BASES={g['Id']:g['Name'] for g in read(REPO/'data/game_data_poe2/BaseItemTypes.json')}
NS={n['stringId']:n for n in read(DELIVERY/'sources/tree_0_5.json')['nodes'].values() if 'stringId' in n}
SOURCES={'24':'ninja_hour18_lv24.json','34':'lv34_0906_0320.json','43':'lv43_0906_0523.json','46':'lv46_0906_0634.json','52':'lv52_0906_0744.json','74':'ninja_latest_74.json'}
MODELS={k:read(DELIVERY/'sources'/v) for k,v in SOURCES.items()}
MODELS['user']=read(sorted((HERE/'sources').glob('HCFR_CCTBurger_*.json'))[-1])['charModel']
XML={k:decoded(v) for k,v in MODELS.items()}
def gem_lookup(root):
    return {g.get('nameSpec'):g for group in root.findall('Skills/SkillSet/Skill') if not group.get('source') for g in group.findall('Gem')}
GEM_LOOK={k:gem_lookup(v) for k,v in XML.items()}
CASES=[]
engine=Pob()
GEM_META=engine.json('(function() local out={} for id,g in pairs(data.gems) do out[id]={gameId=g.gameId,variantId=g.variantId,skillId=g.grantedEffectId,name=g.name} end return out end)()')
for meta in list(GEM_META.values()):GEM_META.setdefault(meta['gameId'],meta)

def configure(root,level,area,penalty):
    root.find('Build').set('level',str(level));root.find('Build').set('characterLevelAutoMode','false')
    c=root.find('Config/ConfigSet')
    # Preserve only actual quest choices; discard copied assumptions about buffs,
    # debuffs, pinnacle armour and maximum stacks.
    for n in list(c):
        if not n.get('name','').startswith('quest'):c.remove(n)
    for k,v in {'enemyLevel':area,'resistancePenalty':penalty,'conditionCorruptingCryStages':1,'multiplierWarcryUsedRecently':1,'multiplierNearbyEnemies':1,'multiplierNearbyRareOrUniqueEnemies':1}.items():ET.SubElement(c,'Input',name=k,number=str(v))
    ET.SubElement(c,'Input',name='enemyIsBoss',string='Boss')
    for k in ['conditionUsedWarcryRecently','conditionHaveTotem']:
        ET.SubElement(c,'Input',name=k,boolean='true')
    for slot in root.findall('Items/ItemSet/Slot'):
        if slot.get('name','').startswith(('Flask','Charm')):slot.set('active','false')
    root.find('Items/ItemSet').set('useSecondWeaponSet','false')

def create(code,gear,gem_source,level,area,penalty,name=None,fort_level=None,drop_echo=False,drop_clarity=False):
    b=NATIVE[code];r=copy.deepcopy(XML[gear]);spec=r.find('Tree/Spec')
    # The native planner has no chosen attribute values. Use the source tree's
    # observed choices, then assign added travel nodes to Strength by default.
    tree_source='74' if code in ('08A','08B','08C','09') else gem_source
    overrides=copy.deepcopy(XML[tree_source].find('Tree/Spec/Overrides'))
    old=spec.find('Overrides')
    if old is not None:spec.remove(old)
    if overrides is not None:spec.append(overrides)
    ids={NS[p['id']]['skill'] for p in b['passives'] if code not in ('01','02') or not NS[p['id']].get('ascendancyName')}
    ids.add(NS['marauder594']['skill']);spec.set('nodes',','.join(map(str,sorted(ids))))
    for w in (1,2):
        old=spec.find('WeaponSet'+str(w))
        if old is not None:spec.remove(old)
        ET.SubElement(spec,'WeaponSet'+str(w),nodes=','.join(str(NS[p['id']]['skill']) for p in b['passives'] if p.get('weapon_set')==w))
    for socket in list(spec.find('Sockets')):
        if int(socket.get('nodeId')) not in ids:spec.find('Sockets').remove(socket)
    asc=code not in ('01','02')
    spec.set('ascendClassId','2' if asc else '0');spec.set('ascendancyInternalId','Warrior2' if asc else '')
    r.find('Build').set('ascendClassName','Warbringer' if asc else 'None')
    skills=r.find('Skills/SkillSet');skills.clear();skills.set('id','1')
    for s in b['skills']:
        en=BASES[s['id']]
        g=ET.SubElement(skills,'Skill',enabled='true',label=en,mainActiveSkill='1',mainActiveSkillCalcs='1')
        for native in [s,*s.get('support_skills',[])]:
            meta=GEM_META[native['id']];title=BASES[native['id']]
            if drop_echo and title=='Echoing Cry':continue
            if drop_clarity and title=='Clarity II':continue
            source=GEM_LOOK[gem_source].get(title)
            if source is None:
                source=next((GEM_LOOK[k].get(title) for k in ('user','24','34','43','46','52','74') if title in GEM_LOOK[k]),None)
            level_g=int(source.get('level','1')) if source is not None else 1
            quality=int(source.get('quality','0')) if source is not None else 0
            # AWT keeps the final snapshot's active gems; the main warcry in
            # the mana/BM bridges deliberately uses the old Lv52 gem unless
            # an explicit upgraded-gem comparison is requested.
            if code in ('08B','08C') and title=='Fortifying Cry':
                level_g=int(GEM_LOOK['52'][title].get('level'))
            if title=='Fortifying Cry' and fort_level is not None:level_g=fort_level
            ET.SubElement(g,'Gem',nameSpec=title,gemId=meta['gameId'],variantId=meta['variantId'],skillId=meta['skillId'],
                          level=str(level_g),quality=str(quality),count='1',enabled='true',enableGlobal1='true',enableGlobal2='true')
    # Shared weapon slots absent in the API are explicit here. If no swap mace
    # is recorded, share both currently equipped items for the calculation.
    slots={s.get('name'):s for s in r.findall('Items/ItemSet/Slot')}
    if code not in ('08B','08C','09'):
        if slots['Weapon 1 Swap'].get('itemId')=='0':slots['Weapon 1 Swap'].set('itemId',slots['Weapon 1'].get('itemId'))
        if slots['Weapon 2 Swap'].get('itemId')=='0':slots['Weapon 2 Swap'].set('itemId',slots['Weapon 2'].get('itemId'))
    configure(r,level,area,penalty)
    if code in ('08B','08C','09'):
        ET.SubElement(r.find('Config/ConfigSet'),'Input',name='TotemsSummoned',number='4')
    label=name or code;path=OUT/(label+'.xml');ET.indent(r);path.write_text(ET.tostring(r,encoding='unicode'),encoding='utf-8')
    CASES.append({'case':label,'stage':code,'gear_source':gear,'gem_source':gem_source,'character_level':level,'enemy_level':area,'resistance_penalty':penalty,'path':str(path),'native_node_ids':sorted(ids),'fort_level_override':fort_level})

# Same enemy level/character level for each sensitive transition pair.
for row in [('01','user','user',11,8,0),('02','24','24',24,20,-10),('03','24','24',24,20,-10),('04','34','34',34,28,-10),
            ('05','43','43',49,40,-20),('05A','43','46',49,40,-20),('06','46','46',49,40,-20),
            ('07','52','52',65,55,-30),('08','52','52',74,65,-50),('08A','52','52',74,65,-50),
            ('08B','74','74',74,65,-50),('08C','74','74',74,65,-50),('09','74','74',74,65,-50)]:create(*row)
create('06','43','46',49,40,-20,name='06_same_05A_gear')
create('08B','74','74',74,65,-50,name='08B_gem15',fort_level=15)
create('08C','74','74',74,65,-50,name='08C_gem15',fort_level=15)
create('09','74','74',74,65,-50,name='09_no_echo',drop_echo=True)
create('05A','43','46',49,40,-20,name='05A_no_clarity',drop_clarity=True)
create('06','43','46',49,40,-20,name='06_same_05A_no_clarity',drop_clarity=True)
user=copy.deepcopy(XML['user']);configure(user,int(MODELS['user']['level']),int(MODELS['user']['level']),0)
path=OUT/'user_current.xml';path.write_text(ET.tostring(user,encoding='unicode'),encoding='utf-8')
CASES.insert(0,{'case':'user_current','stage':'user','path':str(path),'character_level':int(MODELS['user']['level']),'enemy_level':int(MODELS['user']['level']),'resistance_penalty':0,'gear_source':'user','gem_source':'user'})

ONLY=set(sys.argv[sys.argv.index('--only')+1].split(',')) if '--only' in sys.argv else None
RESULTS=[r for r in read(HERE/'pob_results.json') if r['case'] not in ONLY] if ONLY else []
calculated=0
for case in CASES:
    if ONLY and case['case'] not in ONLY:continue
    engine.load(case['path'])
    # Item-granted/ascendancy groups duplicated in ninja exports are disabled;
    # the explicit planner group remains. Purity groups apply only in their set.
    groups=engine.json('(function() local out={} for i,g in ipairs(build.skillsTab.socketGroupList) do local gems={} for _,v in ipairs(g.gemList) do gems[#gems+1]=v.nameSpec end out[#out+1]={index=i,source=g.source,slot=g.slot,gems=gems} end return out end)()')
    result={**case,'sets':{},'skills':[],'groups':groups}
    if 'native_node_ids' in case:
        allocated=engine.json('(function() local a={} for id,n in pairs(build.spec.allocNodes) do a[#a+1]=id end return a end)()')
        assert set(case['native_node_ids'])<=set(allocated),(case['case'],'missing allocation',set(case['native_node_ids'])-set(allocated))
    for weapon in (1,2):
        engine.run('build.itemsTab.activeItemSet.useSecondWeaponSet='+('true' if weapon==2 else 'false'))
        purity=0
        for g in groups:
            title=g['gems'][0] if g['gems'] else ''
            enable=not g.get('source')
            if title=='Purity of Fire' and enable:
                purity+=1;enable=purity==weapon
            if title=='Harbinger of Madness':enable=enable and weapon==2
            if title in ('Magma Barrier','Raise Shield','Fortifying Cry','Resonating Shield'):enable=enable and weapon==1
            engine.run(f'build.skillsTab.socketGroupList[{g["index"]}].enabled='+('true' if enable else 'false'))
        engine.run('build.configTab:BuildModList();build.buildFlag=true;runCallback("OnFrame")')
        result['sets'][weapon]=engine.scalars('build.calcsTab.mainOutput')
        for g in groups:
            if g.get('source') or not g['gems']:continue
            en=g['gems'][0]
            expected=2 if en in ('Shockwave Totem','Ancestral Warrior Totem','Boneshatter','Mace Strike') else 1
            # ninja does not publish actual G weapon binding. Calculate both
            # equipped sets for the user; never present that as observed binding.
            if case['case']=='user_current':
                if weapon==2 and user.find("Items/ItemSet/Slot[@name='Weapon 1 Swap']").get('itemId')=='0':continue
            elif weapon!=expected:continue
            if en not in ('Shockwave Totem','Ancestral Warrior Totem','Fortifying Cry','Boneshatter','Rolling Slam','Earthquake','Seismic Cry'):continue
            idx=g['index']
            active=engine.json(f'(function() local a={{}} for i,s in ipairs(build.skillsTab.socketGroupList[{idx}].displaySkillList or {{}}) do a[#a+1]={{index=i,name=s.activeEffect.grantedEffect.name,level=s.activeEffect.level}} end return a end)()')
            for sub in active:
                engine.run(f'build.mainSocketGroup={idx};build.skillsTab.socketGroupList[{idx}].mainActiveSkill={sub["index"]};build.skillsTab.socketGroupList[{idx}].mainActiveSkillCalcs={sub["index"]};build.buildFlag=true;runCallback("OnFrame")')
                output=engine.scalars('build.calcsTab.mainOutput')
                result['skills'].append({'host':en,'active':sub['name'],'effective_gem_level':sub['level'],'weapon_set':weapon,'output':output})
    RESULTS.append(result)
    calculated+=1
    RESULTS.sort(key=lambda x:next(i for i,c in enumerate(CASES) if c['case']==x['case']))
    (HERE/'pob_results.json').write_text(json.dumps(RESULTS,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Calculated '+case['case'],flush=True)
(HERE/'scenarios.json').write_text(json.dumps(CASES,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(HERE/'engine_gem_mapping.json').write_text(json.dumps(GEM_META,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'Calculated {calculated} PoB cases; {len(RESULTS)} total preserved.',flush=True)
