"""Check delivery requirements and prove this presentation change preserves builds."""
from pathlib import Path
import hashlib,json,re,zipfile

HERE=Path(__file__).resolve().parent;OUT=HERE/'revision2'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def no_hints(value):
    if isinstance(value,dict):return {k:no_hints(v) for k,v in value.items() if k not in ('additional_text','description')}
    if isinstance(value,list):return [no_hints(v) for v in value]
    return value

basezip=HERE/'sources/before_equipment_readability.zip'
report={'official_spec':'https://www.pathofexile.com/developer/docs/game#buildplanner','planners':[]}
required={'Weapon1','Weapon2','Offhand1','Offhand2','Helm1','BodyArmour1','Gloves1','Boots1','Amulet1','Belt1','Ring1','Ring2','Flask1','Charm1'}
allowed_top={'name','author','link','description','ascendancy','passives','skills','inventory_slots'}
allowed_slot={'inventory_id','slot_x','slot_y','level_interval','unique_name','additional_text'}
allowed_skill={'id','level_interval','additional_text','support_skills'}
allowed_support={'id','level_interval','additional_text'}
with zipfile.ZipFile(basezip) as z:
    files=sorted((OUT/'BuildPlanner').glob('*.build'));assert len(files)==13
    for p in files:
        b=read(p);old=json.loads(z.read('revision2/BuildPlanner/'+p.name).decode('utf-8-sig'));code=b['name'].split()[0]
        assert b['name']==p.stem and set(b)==allowed_top
        assert no_hints(b['passives'])==no_hints(old['passives']),(code,'tree changed')
        assert no_hints(b['skills'])==no_hints(old['skills']),(code,'gem setup changed')
        assert b['ascendancy']==old['ascendancy'] and b['author']==old['author'] and b['link']==old['link']
        unique=lambda x:{(s['inventory_id'],s.get('slot_x',0),s['unique_name']) for s in x['inventory_slots'] if s.get('unique_name')}
        assert unique(b)==unique(old),(code,'optional original unique altered')
        assert set(s['inventory_id'] for s in b['inventory_slots'])==required
        assert len({(s['inventory_id'],s['slot_x'],s['slot_y']) for s in b['inventory_slots']})==len(b['inventory_slots'])
        assert 0<len(b['description'])<=1900 and b['description'].startswith('무기·스킬셋')
        assert '사용 순서' in b['description'] and '지금 할 일' in b['description']
        text=[b['description']]
        for s in b['inventory_slots']:
            assert set(s)<=allowed_slot and s['level_interval']==[1,100]
            n=s['additional_text'];assert '<b>{추천 옵션' in n and '\n1. ' in n and '\n2. ' in n
            weapon=s['inventory_id'] in ('Weapon1','Weapon2')
            assert len(n)<=(900 if weapon else 350) and '환불' not in n and '원본 대조' not in n
            if weapon:assert '사용 스킬 → 연결 젬' in n and 'G에서' in n
            text.append(n)
        for s in b['skills']:
            assert set(s)<=allowed_skill and s['additional_text'] and len(s['additional_text'])<=600
            assert '이 스킬 안에 넣을 젬' in s['additional_text'];text.append(s['additional_text'])
            for g in s.get('support_skills',[]):
                assert set(g)<=allowed_support and '연결할 스킬:' in g['additional_text'] and len(g['additional_text'])<=230
                text.append(g['additional_text'])
        for pnode in b['passives']:
            assert set(pnode)<={'id','weapon_set','additional_text'}
            text.append(pnode.get('additional_text',''))
        for n in text:
            assert n.count('{')==n.count('}')
            assert all(t=='b' for t in re.findall(r'<([^>]+)>',n))
            assert '\ufffd' not in n and not re.search(r'\\[nr]',n)
        find=lambda inv:next(s['additional_text'] for s in b['inventory_slots'] if s['inventory_id']==inv)
        assert '이동 속도' in find('Boots1') and '최대 생명력' in find('Helm1')
        assert '최대 생명력' in find('Ring1') and '원소' not in find('Weapon1').split('\n1.')[0]
        mana=[s for s in b['inventory_slots'] if s['inventory_id']=='Flask1' and s['slot_x']==1]
        assert bool(mana)==(code not in ('08C','09'))
        if code in ('08B','08C','09'):
            assert '성소 셉터' in find('Weapon1') and '성소 셉터' in find('Offhand2')
            assert '한손 철퇴' in find('Weapon2') and '정신력' in find('BodyArmour1')
        if code in ('05A','06','07','08','08A','08B','08C','09'):
            assert '모든 근접 스킬 레벨' in find('Gloves1')
        if code=='02':
            swt=next(s for s in b['skills'] if s['id'].endswith('SkillGemShockwaveTotem'))
            assert '3레벨' in swt['additional_text'] and '6레벨' in swt['additional_text'] and '보조를 다 모으기 전' in swt['additional_text']
            assert '충격파 토템 → 과잉 I + 포악함 I' in b['description']
            assert '충격파 토템 → 과잉 I + 포악함 I' in find('Weapon2')
        report['planners'].append({'file':b['name']+'.build','equipment_slots':len(b['inventory_slots']),
            'max_equipment_hint_before':max(len(s.get('additional_text','')) for s in old['inventory_slots']),
            'max_equipment_hint_after':max(len(s['additional_text'])for s in b['inventory_slots']),
            'native_skill_and_support_hints':sum(1+len(s.get('support_skills',[])) for s in b['skills']),
            'description_characters':len(b['description']),'allocation_and_gems_unchanged':True})
sim=read(HERE/'simulation/validation_simulation.json')
for name in ('pob_results.json','resource_results.json'):
    assert sha(HERE/'simulation'/name)==sim['files'][name]
report['previous_simulation_outputs_unchanged']=True
report['modified_revision_game_ui_checked']=False
(HERE/'validation_presentation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('PASS: 13 planners; all equipment targets present; short native skill hints; allocation, links and simulation outputs preserved.')
print('Maximum equipment hint: '+str(max(x['max_equipment_hint_before'] for x in report['planners']))+' -> '+str(max(x['max_equipment_hint_after'] for x in report['planners']))+' characters.')
