"""Read-only source conversion; all writes stay beside this script. Never installs."""
from pathlib import Path
import collections
import hashlib
import json
import re
import xml.etree.ElementTree as ET

OUT = Path(__file__).resolve().parent
CORPUS = OUT.parent
REPO = Path('D:/Pathcraft-AI')
DOC = 'https://www.pathofexile.com/developer/docs/game#buildplanner'
TREE_PATH = REPO / 'deliverables/skadoosh_hc_2026-09-07/sources/tree_0_5.json'
BASE_PATH = REPO / 'data/game_data_poe2/BaseItemTypes.json'
GEM_PATH = REPO / 'data/game_data_poe2/SkillGems.json'

def read(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))

def write(name, obj):
    (OUT / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

TREE = read(TREE_PATH)
NODES = {int(n['skill']): n for n in TREE['nodes'].values() if isinstance(n, dict) and 'skill' in n and 'stringId' in n}
BASES = read(BASE_PATH)
BASE_IDS = {b['Id'] for b in BASES}
GEMS = {BASES[g['BaseItemType']]['Id']: g for g in read(GEM_PATH)}
SLOTS = {'Weapon 1': ('Weapon1', 0), 'Weapon 2': ('Offhand1', 0),
         'Weapon 1 Swap': ('Weapon2', 0), 'Weapon 2 Swap': ('Offhand2', 0),
         'Helmet': ('Helm1', 0), 'Body Armour': ('BodyArmour1', 0),
         'Gloves': ('Gloves1', 0), 'Boots': ('Boots1', 0), 'Amulet': ('Amulet1', 0),
         'Belt': ('Belt1', 0), 'Ring 1': ('Ring1', 0), 'Ring 2': ('Ring2', 0),
         'Charm 1': ('Charm1', 0), 'Charm 2': ('Charm1', 1), 'Charm 3': ('Charm1', 2),
         'Flask 1': ('Flask1', 0), 'Flask 2': ('Flask1', 1)}
STAGES = [
    ('28509', '01-일반갑옷-28509.build', '과거 일반갑옷·철퇴', '일반 등급 갑옷과 해당 키타바 전직 분기, 방어도 방패, 방패벽·토템 및 마나 조달을 함께 준비한 당시 관측본.'),
    ('285e2', '02-일반갑옷보강-285e2.build', '과거 방패·보조 보강', '일반 갑옷 전직 유지 중 방패와 보조를 보강한 당시 관측본. Ahn\'s Citadel 등 원본 보조를 확보했는지 확인.'),
    ('28604', '03-황동철갑전환-28604.build', '과거 황동철갑 전환', 'Sacred Flame·The Brass Dome·Defiance of Destiny와 전직 개편, 시체 폭발 및 Gorge 관련 자원 조달 준비를 함께 확인. 일반갑옷 전직을 그대로 유지하지 않음.'),
    ('28695', '04-투구전환-28695.build', '과거 Constricting Command', 'Constricting Command 확보 후 관련 포위 노드 적용. 메타젬·Repulsion 연결은 별도 안내 확인. 함성 삭제 완료 단계가 아님.'),
    ('29d39', '05-최신저자본-29d39.build', '최신 저자본 2026-09-21', 'Cat O\' Nine Tails와 스킬·패시브를 함께 변경한 최신 저자본. 저생명력 유지와 플라스크 예외를 확인하고 Eternal Rage 활성 및 Raging Cry·Enraged Warcry II 운용 확인.')
]
EXTRACTS = read(CORPUS / 'priority_pob_extracts.json')

def ids(s):
    return [int(x) for x in s.split(',') if x.strip()]

def gem_note(g):
    return f"{g.get('nameSpec', g.get('gemId', g.get('skillId', '?')))} [원본 젬Lv {g.get('level', '?')}, enabled={g.get('enabled', '미지정')}, set1={g.get('enableGlobal1', '미지정')}, set2={g.get('enableGlobal2', '미지정')}]"

def player_note(name, code, support=False):
    if name in ('Execute III','Clash'):
        return name + (' · 아홉꼬리 장착 후 저생명력 유지가 실제로 되는지 확인한 뒤 사용. 플라스크 회복은 예외입니다.' if code=='29d39' else ' · 이 과거 구성의 저생명력 유지 수단을 갖춘 뒤 사용.')
    if name=='Shield Wall':
        return '방어도 방패와 젬 요구치를 충족한 뒤 사용.' + (' 권장: 방패벽 세트1 / 함성 세트2.' if code=='29d39' else '')
    if name=='Infernal Cry':
        return ('권장 세트2. Eternal Rage를 켜고 Raging Cry·Enraged Warcry II 보조를 빠뜨리지 마세요.' if code=='29d39' else '이 파일의 함성 보조를 연결하고 격노와 자원 회복을 확인하세요.')
    if name=='Eternal Rage':
        return '함성 운용 전에 활성 상태와 격노를 확인하세요.'
    if name in ('Raging Cry','Enraged Warcry II'):
        return name + ' · 함성에 연결하고 격노 상태를 확인하세요.'
    if support:
        return name
    return name + ' · 젬 요구치와 필요한 자원을 갖춘 뒤 사용.'

def player_connections(groups):
    """Explain unsupported links once; preserve every original group in validation."""
    best = {}
    for group in groups:
        if group['disposition'] not in ('meta_gem_unsupported','granted_or_noncraftable_active'):
            continue
        gems = [g for g in group['gems'] if g.get('gemId')]
        if not gems: continue
        key = gems[0]['gemId']
        if key not in best or len(gems)>len(best[key]): best[key]=gems
    lines=[]
    for gems in best.values():
        actives=[g['nameSpec'] for g in gems if GEMS[g['gemId']]['GemType']!=1]
        supports=[g['nameSpec'] for g in gems if GEMS[g['gemId']]['GemType']==1]
        line='스킬: '+' → '.join(actives)
        if supports: line+=' / 보조: '+', '.join(supports)
        lines.append(line)
    if not lines: return ''
    return '메타젬·장비/전직 부여 스킬은 자동 안내를 지원하지 않습니다. 해당 스킬을 얻은 뒤 게임에서 직접 연결하세요.\n'+'\n'.join(lines)

def clean_item(item):
    # Selected variants only; never flatten the entire template variant pool.
    selected = {item.get(k) for k in ('variant', 'variantAlt', 'variantAlt2', 'variantAlt3') if item.get(k)}
    text = item.text or ''
    selected.update(re.findall(r'^Selected Variant: (\d+)', text, re.M))
    lines = []
    for line in text.strip().splitlines():
        line = line.strip()
        if not line or line.startswith(('Variant:', 'Selected Variant:', 'Unique ID:', 'Item Level:', 'Quality:', 'LevelReq:', 'Implicits:', 'League:')):
            continue
        v = re.search(r'\{variant:([^}]+)\}', line)
        if v and not selected.intersection(v.group(1).split(',')):
            continue
        # Preserve numeric ranges as source examples, not rolled game values.
        line = re.sub(r'\{[^}]+\}', '', line)
        lines.append(line)
    return '\n'.join(lines)

def check_shape(build):
    allowed = {'build': {'name','author','link','description','ascendancy','passives','skills','inventory_slots'},
               'passive': {'id','level_interval','weapon_set','additional_text'},
               'skill': {'id','level_interval','additional_text','support_skills'},
               'support': {'id','level_interval','additional_text'},
               'slot': {'inventory_id','slot_x','slot_y','level_interval','unique_name','additional_text'}}
    def check(o, kind):
        assert isinstance(o, dict) and not set(o) - allowed[kind], (kind, o)
        for key, val in o.items():
            if key in ('passives','skills','inventory_slots','support_skills'):
                assert isinstance(val, list)
            elif key in ('weapon_set','slot_x','slot_y'):
                assert type(val) is int and val >= 0
                if key == 'weapon_set': assert val <= 2
            elif key == 'level_interval':
                assert type(val) is int and val >= 0 or isinstance(val,list) and len(val)==2 and all(type(x) is int and x>=0 for x in val) and val[0]<=val[1]
            else: assert isinstance(val,str), (key,val)
        required = 'name' if kind=='build' else 'inventory_id' if kind=='slot' else 'id'
        assert required in o
    check(build, 'build')
    for x in build['passives']: check(x,'passive')
    for x in build['skills']:
        check(x,'skill')
        for s in x.get('support_skills',[]): check(s,'support')
    for x in build['inventory_slots']: check(x,'slot')
    return allowed

def generate():
    results = []
    for code, filename, title, gate in STAGES:
        filename = f'archive-{code}.build' if code!='29d39' else 'current-kitava-29d39.build'
        source = CORPUS / 'priority_29d39.xml' if code=='29d39' else REPO / f'deliverables/tangjung_0_5_5_research_2026-09-07/sources/pob_{code}.xml'
        extract = next(x for x in EXTRACTS if Path(x['file']).name==source.name)
        assert sha(source)==extract['sha256'], source
        root = ET.parse(source).getroot()
        b = root.find('Build')
        assert b.get('ascendClassName')=='Smith of Kitava'
        tree = root.find('Tree')
        spec = tree.findall('Spec')[int(tree.get('activeSpec','1'))-1]
        raw_nodes = ids(spec.get('nodes',''))
        ws = {i: set(ids(spec.find(f'WeaponSet{i}').get('nodes',''))) if spec.find(f'WeaponSet{i}') is not None else set() for i in (1,2)}
        assert not ws[1] & ws[2]
        assert (ws[1] | ws[2]) <= set(raw_nodes)
        assert all(n in NODES for n in raw_nodes)
        passives = [{'id':NODES[n]['stringId'], 'weapon_set': 1 if n in ws[1] else 2 if n in ws[2] else 0,
                     'additional_text':'원본 목표 트리. 배열 순서는 클릭·획득 순서가 아닙니다.'} for n in raw_nodes]
        by_numeric = dict(zip(raw_nodes,passives))
        overrides = spec.find('Overrides')
        if overrides is not None:
            for override in overrides.findall('AttributeOverride'):
                for key,label in [('strNodes','힘'),('dexNodes','민첩'),('intNodes','지능')]:
                    for n in ids(override.get(key,'')):
                        if n in by_numeric: by_numeric[n]['additional_text'] += f' 원본 능력치 선택: {label}.'
        socket_report = []
        for socket in spec.findall('.//Socket'):
            node = int(socket.get('nodeId'))
            item = root.find(f"Items/Item[@id='{socket.get('itemId')}']")
            if item is not None and node in by_numeric:
                txt = clean_item(item)
                by_numeric[node]['additional_text'] += '\n원본 장착 주얼 예시(필수 구매 목록 아님):\n'+txt
                socket_report.append({'attributes':dict(socket.attrib),'selected_text':txt})
        asc = {re.match(r'^Ascendancy([A-Za-z]+\d+)', p['id']).group(1) for p in passives if re.match(r'^Ascendancy([A-Za-z]+\d+)',p['id'])}
        assert asc == {'Warrior3'} and spec.get('ascendancyInternalId')=='Warrior3'
        skills_root = root.find('Skills')
        active_skills = skills_root.find(f"SkillSet[@id='{skills_root.get('activeSkillSet')}']")
        assert active_skills is not None
        groups = active_skills.findall('.//Skill')
        granted = {g.get('gemId') for s in groups if s.get('source','').startswith(('Item:', 'Tree:')) for g in s.findall('Gem') if g.get('gemId')}
        group_report, skills, notes = [], [], []
        for num,s in enumerate(groups,1):
            gs = s.findall('Gem')
            for g in gs:
                if g.get('gemId'): assert g.get('gemId') in BASE_IDS and g.get('gemId') in GEMS, g.attrib
            parent = gs[0] if gs else None
            gid = parent.get('gemId') if parent is not None else None
            reason = None
            if not gid: reason='no_gem_id_or_empty_group'
            elif s.get('enabled')=='false': reason='disabled_group'
            elif any(GEMS.get(g.get('gemId'),{}).get('GemType')==2 or 'Meta' in g.get('skillId','') for g in gs): reason='meta_gem_unsupported'
            elif s.get('source') or gid in granted or not GEMS[gid].get('CraftingTypes'): reason='granted_or_noncraftable_active'
            elif parent.get('enabled')=='false': reason='disabled_parent'
            group_report.append({'index':num,'attributes':dict(s.attrib),'gems':[dict(g.attrib) for g in gs], 'disposition':reason or 'exported'})
            if not gid: continue
            text = ' → '.join(gem_note(g) for g in gs)
            if reason:
                notes.append(f'[{reason}] {s.get("source", "원본 수동 그룹")}: {text}')
                continue
            entry = {'id':gid,'additional_text':player_note(parent.get('nameSpec',''),code)}
            supports = []
            for g in gs[1:]:
                sgid = g.get('gemId')
                if not sgid: continue
                if g.get('enabled')=='false':
                    notes.append('[disabled_gem] '+gem_note(g));continue
                assert GEMS[sgid]['GemType']==1, ('non-support inside normal group',g.attrib)
                st = player_note(g.get('nameSpec',''),code,support=True)
                supports.append({'id':sgid,'additional_text':st})
            if supports: entry['support_skills']=supports
            skills.append(entry)
        items = root.find('Items')
        active_items = items.find(f"ItemSet[@id='{items.get('activeItemSet')}']")
        assert active_items is not None
        item_map = {i.get('id'):i for i in items.findall('Item')}
        inventory, item_report = [], []
        for slot in active_items.findall('Slot'):
            if slot.get('itemId') in ('0',None): continue
            item = item_map[slot.get('itemId')]
            record = {'slot':dict(slot.attrib),'item_id':item.get('id'),'item_attributes':dict(item.attrib),'selected_text':clean_item(item)}
            item_report.append(record)
            if slot.get('name') not in SLOTS or slot.get('active')=='false': continue
            inv,x = SLOTS[slot.get('name')]
            inventory.append({'inventory_id':inv,'slot_x':x,'additional_text':f"원본 관측 장비 예시 · {slot.get('name')} · 필수 구매 목록 아님\n{record['selected_text']}"})
        desc = (f'탱정-탱커의정석 / Smith of Kitava / {title}\n조건: {gate}\n'
                f'관측 캐릭터 Lv{b.get("level")}는 최소 전환 레벨이 아닙니다. 0.5.5 관련 가이드 자료.\n'
                '패시브는 목표 배분이며 클릭 순서가 아닙니다. 특수 보조는 별도로 확보하세요.\n'
                + ('과거 보관참고: 최신으로 가는 필수 전환 단계가 아닙니다.\n' if code!='29d39' else '')
                + player_connections(group_report))
        build = {'name':f'탱정 키타바 {title}', 'author':'탱정-탱커의정석', 'link':f'https://poe.ninja/poe2/pob/{code}',
                 'description':desc,'ascendancy':'Warrior3','passives':passives,'skills':skills,'inventory_slots':inventory}
        allowed = check_shape(build)
        write(filename,build)
        assert read(OUT/filename)==build
        assert {(p['id'],p['weapon_set']) for p in passives}=={(NODES[n]['stringId'],1 if n in ws[1] else 2 if n in ws[2] else 0) for n in raw_nodes}
        results.append({'code':code,'file':filename,'sha256':sha(OUT/filename),'source':str(source),'source_sha256':sha(source),
                        'source_hash_matches_extract':True,'author':'탱정-탱커의정석','snapshot_level':int(b.get('level')),
                        'gate_ko':gate,'source_build_attributes':dict(b.attrib),'tree_attributes':dict(spec.attrib),
                        'activeSpec':tree.get('activeSpec'),'activeSkillSet':skills_root.get('activeSkillSet'),'activeItemSet':items.get('activeItemSet'),
                        'useSecondWeaponSet':active_items.get('useSecondWeaponSet',items.get('useSecondWeaponSet')),
                        'passive_count':len(passives),'mapped_passive_count':len(passives),'weapon_set_counts':dict(collections.Counter(p['weapon_set'] for p in passives)),
                        'passive_mapping':[{'numeric_id':n,'id':p['id'],'weapon_set':p['weapon_set']} for n,p in zip(raw_nodes,passives)],
                        'tree_sockets':socket_report,'tree_overrides':ET.tostring(overrides,encoding='unicode') if overrides is not None else None,
                        'ascendancy':'Warrior3','skill_groups':group_report,'exported_skill_count':len(skills),'selected_items':item_report,
                        'inventory_count':len(inventory),'json_valid':True,'official_key_type_check':True,'all_gem_ids_in_base_and_skill_tables':True,
                        'level_intervals_omitted':'No evidence of stage minimum level; snapshot levels and gem-table minima are not transition gates.',
                        'limitations':notes})
    latest = results[-1]
    assert latest['passive_count']==151
    latest_text = (OUT/latest['file']).read_text(encoding='utf-8')
    for term in ("Cat O' Nine Tails",'SkillGemEternalRage','SupportGemRagingCry','SupportGemEnragedWarcryTwo','SupportGemExecuteThree','SupportGemClash'):
        assert term in latest_text,term
    assert 'Atziri' not in latest_text
    validation = {'status':'passed_static_validation','checked_on':'2026-09-21','official_documentation':DOC,
                  'documentation_checked_directly':True,'schema_version_description':'Version 1 Experimental; no version key in Build',
                  'schema_validation_scope':'Locally implemented allowed-key/type/required-field checks from current official documentation, not a GGG validator.',
                  'allowed_keys':{k:sorted(v) for k,v in allowed.items()},
                  'inputs':[{'path':str(p),'sha256':sha(p)} for p in (TREE_PATH,BASE_PATH,GEM_PATH,CORPUS/'priority_pob_extracts.json')],
                  'game_actual_load_tested':False,'game_installation_performed':False,'writes_confined_to':str(OUT),
                  'inventory_id_basis':'Existing converter SLOT_MAP; same mapping retained. Inventories table not present for independent table-ID verification.',
                  'meta_gems_supported_by_official_format':False,'skill_weapon_set_field_supported':False,
                  'special_support_crafting_warning':'Base/SkillGems ID validity is checked; empty CraftingTypes unique supports require separate acquisition. One player-facing reminder replaces repeated warnings.',
                  'stages':results}
    pack_path = CORPUS / 'planner_data/build_data.json'
    pack = read(pack_path)
    assert pack['tree']['sha256']==sha(TREE_PATH)
    comparisons = []
    for result in results:
        peer = next(s for s in pack['stages'] if s['id']=='kitava-'+result['code'])
        assert peer['source']['sha256']==result['source_sha256']
        assert peer['ascendancy']=='Smith of Kitava'
        assert {(int(n['id']),n['stringId']) for n in peer['passives']}=={(n['numeric_id'],n['id']) for n in result['passive_mapping']}
        for w in (1,2):
            assert set(map(int,peer['weapon_set_nodes'][str(w)]))=={n['numeric_id'] for n in result['passive_mapping'] if n['weapon_set']==w}
        assert peer['tree_attributes']==result['tree_attributes']
        # The pack may omit empty groups; compare actual gem-bearing groups in source order.
        raw_groups = [g for g in result['skill_groups'] if g['gems']]
        assert len(raw_groups)==len(peer['skills'])
        for raw, shared in zip(raw_groups,peer['skills']):
            assert raw['attributes']==shared['attributes']
            assert len(raw['gems'])==len(shared['gems'])
            for rg,sg in zip(raw['gems'],shared['gems']):
                for key,value in rg.items():
                    assert sg[key]==(value=='true' if key=='enabled' else value), (result['code'],key)
        assert {(e['slot'],e['itemId']) for e in peer['equipment']}=={(e['slot']['name'],e['item_id']) for e in result['selected_items']}
        comparisons.append({'code':result['code'],'source_hash':True,'passive_ids_and_weapon_sets':True,'ascendancy':True,'all_gem_attributes_and_group_flags':True,'selected_inventory_slots_and_ids':True})
    validation['html_common_pack_comparison']={'path':str(pack_path),'sha256':sha(pack_path),'status':'passed','stages':comparisons}
    campaign_results = []
    for stage in pack['campaign_stages']:
        assert not stage['passives']
        entries, annotations, group_checks = [], [], []
        for group in stage['skills']:
            gems = group['gems']
            for gem in gems:
                assert gem['gemId'] in BASE_IDS and gem['gemId'] in GEMS
                assert bool(gem['isSupport']) == (GEMS[gem['gemId']]['GemType']==1)
            main = gems[0]
            note = group['note'] + ' 실제 젬과 요구 능력치·정신력을 확보한 뒤 사용. '
            if group['weaponSet'] in ('1','2'):
                note += f"자료 권장 무기 세트{group['weaponSet']}; 게임에서 직접 확인·배정. "
            if main['name']=='Boneshatter': note += 'Impact Shockwave 이후 Magnified Area I을 추가하는 육성 안내.'
            if main['name']=='Herald of Ash': note += '프레이손 정신력 보상 이후 안내.'
            if stage['id']=='campaign-act1' and main['name']=='Rolling Slam': note += '몰려오는 강타 첫 타로 기절을 준비한 뒤 뼈박살. Brink I은 0.5.5 업데이트 보완.'
            if GEMS[main['gemId']]['GemType']==2 or not GEMS[main['gemId']]['CraftingTypes']:
                annotations.append('부여·기본 스킬 안내(구매 젬 아님): '+group['active']+' → '+', '.join(group['supports'])+'. '+note)
                disposition='description_only_granted_or_meta'
            else:
                entry={'id':main['gemId'],'additional_text':group['active']+' · '+note}
                if gems[1:]: entry['support_skills']=[{'id':g['gemId'],'additional_text':g['name']} for g in gems[1:]]
                entries.append(entry)
                disposition='exported'
            group_checks.append({'active':group['active'],'disposition':disposition,'ids':[g['gemId'] for g in gems],
                                 'table_min_levels_reference_only':{g['gemId']:GEMS[g['gemId']]['MinLevelReq'] for g in gems}})
        equipment=[]
        for e in stage['equipment']:
            inv,x=SLOTS[e['slot']]
            equipment.append({'inventory_id':inv,'slot_x':x,'additional_text':e['name']+'; '+e['source']+'; 관측 옵션·고유 장비 구매 필수 목록이 아닙니다.'})
        equipment.append({'inventory_id':'Boots1','additional_text':'이동 속도 장화를 확인하고 진행 중 방어·저항과 장비 요구 능력치를 보완하세요.'})
        desc=('별이슬골짜기 캠페인 가이드와 탱정 보정의 제한적 스킬 안내. 탱정의 실제 액트 스냅샷이 아닙니다. '
              '키타바 패시브 클릭 순서는 근거가 없어 생략했습니다. 다른 저자의 워브링어/타이탄 전직·패시브도 가져오지 않았습니다.\n'
              + '\n'.join(stage['conditions'])+'\n'+'\n'.join(annotations)+'\n'
              '방패벽 전환은 레벨7 스킬젬과 방어도 방패 준비 후이며, 7은 캐릭터 레벨이 아닙니다. 0.5 영상 + 0.5.5 업데이트 참고; 실게임 로드 미검증.\n'
              '최신 연결 XML의 Freezing Mark 조합은 실제 요구조건 충족 후 사용하며 옛 화면의 Pounce+징표 보조를 현재 조합으로 권하지 않습니다.\n'
              '탱정 보정: 키타바는 액트2 묻힌 성소 불 선택; 액트4 번개 골렘 다음 화염 골렘.\n업데이트: '+stage['source']['update'])
        build={'name':'캠페인 참조 '+stage['label'],'author':'별이슬골짜기 가이드 / 탱정 보정 / Pathcraft 정리',
               'link':stage['source']['url'],'description':desc,'passives':[],'skills':entries,'inventory_slots':equipment}
        check_shape(build)
        filename=stage['id']+'.build'
        write(filename,build)
        assert read(OUT/filename)==build
        campaign_results.append({'file':filename,'sha256':sha(OUT/filename),'common_pack_stage':stage['id'],
                                 'all_ids_checked':True,'official_key_type_check':True,'passives_and_ascendancy_omitted':True,
                                 'groups':group_checks,'common_pack_skills_and_support_ids_match':True,
                                 'source':stage['source'],'source_md_sha256':sha(CORPUS/stage['source']['file']),
                                 'linked_reference_xml_sha256':sha(CORPUS/'linked_update_pob.xml'),
                                 'limitation':'Evidence selection, not Kitava observed campaign snapshot; no inferred passive click order or ascendancy.'})
    validation['campaign_stages']=campaign_results
    validation['total_build_files']=len(results)+len(campaign_results)
    baseline_path=OUT/'ux_structure_baseline.json'
    if baseline_path.exists():
        def structure(x):
            if isinstance(x,dict): return {k:structure(v) for k,v in x.items() if k not in ('description','additional_text')}
            if isinstance(x,list): return [structure(v) for v in x]
            return x
        baseline=read(baseline_path)
        current={f.name:structure(read(f)) for f in OUT.glob('*.build')}
        assert current==baseline, 'UX-only correction must preserve filenames, structure and IDs'
        forbidden=('enabled=','set1=','set2=','[meta_gem_unsupported]','[granted_or_noncraftable_active]','[disabled_gem]','targetVersion=','원본 플래그')
        for f in OUT.glob('*.build'):
            raw=f.read_text(encoding='utf-8')
            assert not any(term in raw for term in forbidden), f.name
        validation['ux_correction']={'status':'passed','structural_baseline_sha256':sha(baseline_path),
                                     'all_10_build_structures_and_ids_unchanged':True,'debug_text_removed':True,
                                     'source_group_and_gem_flags_preserved_in_validation':True,
                                     'unsupported_connections_deduplicated_for_display_only':True}
    write('validation.json',validation)
    print(json.dumps({'files':len(results)+len(campaign_results),'passives':[r['passive_count'] for r in results],'status':validation['status']},ensure_ascii=False))

if __name__=='__main__':
    generate()
