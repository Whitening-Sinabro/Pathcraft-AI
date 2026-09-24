"""Read existing evidence only; create the shared, source-attributed planner data pack."""
import hashlib, json, math, re
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TREE = Path('D:/Pathcraft-AI/deliverables/skadoosh_hc_2026-09-07/sources/tree_0_5.json')
tree = json.loads(TREE.read_text(encoding='utf-8-sig'))
groups_by_node = {str(n): g for g in tree['groups'] if g for n in g.get('nodes', [])}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def ids(s): return [x for x in (s or '').split(',') if x]
def node(nid):
    n = tree['nodes'].get(str(nid))
    if not n: return {'id': str(nid), 'name': str(nid), 'unresolved': True}
    result = {'id': str(nid), 'name': n.get('name', str(nid)), 'stats': n.get('stats', []),
              'stringId': n.get('stringId'), 'kind': 'ascendancy' if n.get('ascendancyName') else 'notable' if n.get('isNotable') else 'keystone' if n.get('isKeystone') else 'passive',
              'ascendancyName': n.get('ascendancyName'), 'connections': [str(c['id']) for c in n.get('connections', [])]}
    g = groups_by_node.get(str(nid))
    if g and 'orbit' in n and 'orbitIndex' in n:
        a = tree['constants']['orbitAnglesByOrbit'][n['orbit']][n['orbitIndex']]
        radius = tree['constants']['orbitRadii'][n['orbit']]
        result.update(x=round(g['x'] + radius * math.sin(a), 3), y=round(g['y'] - radius * math.cos(a), 3))
    return result

def item(el):
    lines = [x.strip() for x in (el.text or '').strip().splitlines() if x.strip()]
    props = dict(x.split(': ', 1) for x in lines if ': ' in x and not x.startswith('{'))
    start = next((i for i,x in enumerate(lines) if x.startswith('Implicits:')), len(lines))
    mods, omitted = [], []
    selected = props.get('Selected Variant')
    for line in lines[start+1:]:
        m = re.search(r'\{variant:([^}]+)\}', line)
        if m and (not selected or selected not in m.group(1).split(',')):
            omitted.append(line); continue
        # Tags such as {range:0.5} contain unresolved roll ranges, not a resolved numeric value.
        mods.append(line)
    return {'itemId': el.get('id'), 'name': lines[1] if len(lines)>1 else '',
            'base': lines[2] if len(lines)>2 and ': ' not in lines[2] else '',
            'rarity': props.get('Rarity'), 'levelReq': props.get('LevelReq'), 'properties': props,
            'mods': mods, 'omitted_variant_lines': len(omitted), 'raw': '\n'.join(lines)}

def skills(skillset):
    out=[]
    if skillset is None: return out
    for i,s in enumerate(skillset.findall('Skill')):
        gems=[]
        for g in s.findall('Gem'):
            a=dict(g.attrib)
            a.update(name=a.get('nameSpec',''), isSupport='SupportGem' in a.get('gemId','') or a.get('skillId','').startswith('Support'), enabled=a.get('enabled')!='false')
            gems.append(a)
        act=[g['name'] for g in gems if not g['isSupport']]
        support=[g['name'] for g in gems if g['isSupport'] and g['enabled']]
        if not act: continue
        out.append({'id': '+'.join(g.get('skillId',g['name']) for g in gems if not g['isSupport']),
                    'active': ' + '.join(act), 'actives': act, 'supports':support, 'gems':gems,
                    'enabled':s.get('enabled')!='false', 'weaponSet':'XML 개별 젬 플래그',
                    'weapon_sets':{str(k):[g['name'] for g in gems if g.get('enableGlobal'+str(k))=='true'] for k in (1,2)},
                    'attributes':dict(s.attrib), 'source_type':s.get('source','gem group')})
    return out

extracts=json.loads((ROOT/'priority_pob_extracts.json').read_text(encoding='utf-8-sig'))
stages=[]
labels={'28509':'초기 매핑 · 일반 갑옷', '285e2':'일반 갑옷 · 개선', '28604':'Brass Dome · Fire Spell on Hit', '28695':'Constricting Command 단계', '29d39':'최신 저자본 · 벨트·격노 개편'}
for row in extracts[:5]:
    p=Path(row['file']); root=ET.parse(p).getroot()
    key=next(k for k in labels if k in p.name)
    ss=root.find('Skills'); selected=ss.find("SkillSet[@id='%s']"%ss.get('activeSkillSet','1'))
    if selected is None: selected=ss
    its=root.find('Items'); selected_items=its.find("ItemSet[@id='%s']"%its.get('activeItemSet','1'))
    allitems={i.get('id'): item(i) for i in its.findall('Item')}
    equipment=[]
    for sl in selected_items.findall('Slot'):
        if sl.get('itemId') in allitems:
            it=allitems[sl.get('itemId')]
            equipment.append({'slot':sl.get('name'),**it,'item':it,'slot_attributes':dict(sl.attrib)})
    tr=root.find('Tree'); specs=tr.findall('Spec'); spec=specs[int(tr.get('activeSpec','1'))-1]
    passive_ids=ids(spec.get('nodes'))
    ws={str(k):ids(spec.find('WeaponSet'+str(k)).get('nodes')) if spec.find('WeaponSet'+str(k)) is not None else [] for k in (1,2)}
    stage={'id':'kitava-'+key,'label':labels[key], 'creator':'탱정', 'kind':'kitava_snapshot', 'patch':'0.5 / tree 0_5',
           'level':root.find('Build').get('level'), 'ascendancy':root.find('Build').get('ascendClassName'),
           'source':{'file':str(p),'sha256':sha(p),'pob':'https://poe.ninja/poe2/pob/'+key},
           'skills':skills(selected),'equipment':equipment,'passives':[node(n) for n in passive_ids],
           'weapon_set_nodes':ws,'tree_attributes':dict(spec.attrib),
           'tree_sockets':[dict(x.attrib) for x in spec.findall('./Sockets/Socket')],
           'tree_overrides':ET.tostring(spec.find('Overrides'),encoding='unicode') if spec.find('Overrides') is not None else '',
           'conditions':['표시 레벨은 원문 스냅샷이며 최소 전환 레벨이 아닙니다.'],
           'weapon_set_recommendation':{'1':'Shield Wall','2':'Infernal Cry','source':'저자 카페 설명; XML의 global 플래그와 별도'}}
    if key in ('28604','28695','29d39'): stage['conditions'].append('Brass Dome 착용 전 일반 갑옷 전용 Smith’s Masterwork 전직 경로를 재배분합니다.')
    if key in ('28695','29d39'): stage['conditions'].append('Constricting Command 확보 후 포위 조건 패시브를 사용합니다.')
    if key=='29d39': stage['conditions']+=['Cat O’ Nine Tails와 Eternal Rage·Raging Cry·Enraged Warcry II 연결을 함께 확인합니다.', '벨트의 생명력 회복 상한은 플라스크 회복에 적용되지 않습니다.', '이전 Atziri’s Communion 보조 연결을 최신 세팅으로 이어 붙이지 않습니다.']
    stages.append(stage)

# Different creator reference: preserve each tree title/ascendancy without inventing stage-to-item mapping.
lp=ROOT/'linked_update_pob.xml'; lr=ET.parse(lp).getroot()
refs=[]
for i,s in enumerate(lr.findall('./Tree/Spec'),1):
    refs.append({'id':'reference-tree-'+str(i), 'label':s.get('title',str(i)), 'creator':'별이슬골짜기',
                 'kind':'other_creator_tree_reference','ascendancy':{'0':'미전직','1':'Titan','2':'Warbringer'}.get(s.get('ascendClassId'),s.get('ascendClassId')),
                 'passives':[node(n) for n in ids(s.get('nodes'))], 'tree_attributes':dict(s.attrib),
                 'source':{'file':str(lp),'sha256':sha(lp)}, 'conditions':['탱정 Kitava 패시브가 아닙니다. 트리 제목은 액트별 장비/젬의 자동 매핑을 보장하지 않습니다.']})
union={n['id'] for s in stages+refs for n in s['passives']}
neighbor=union|{c for nid in union for c in node(nid).get('connections',[])}
nodes=[node(n) for n in sorted(neighbor,key=int)]
edges=sorted({tuple(sorted((n['id'],c),key=int)) for n in nodes for c in n.get('connections',[]) if c in neighbor})
pack={'version':1,'stages':stages,'reference_trees':refs,
      'reference_skill_sets':[{'id':s.get('id'),'label':s.get('title'), 'creator':'별이슬골짜기','skills':skills(s)} for s in lr.findall('./Skills/SkillSet')],
      'tree':{'version':'0_5','source':str(TREE),'sha256':sha(TREE),'nodes':nodes,'edges':edges,
              'coordinate_method':'Membership-resolved group center + original orbitAnglesByOrbit radians; x += r*sin(a), y -= r*cos(a).',
              'scope':'스냅샷 노드와 직접 연결된 이웃. 실제 연결이며 습득 순서가 아닙니다.'}}
# Campaign is an accepted Pathcraft composition, never an author act snapshot.
candidates_path = ROOT/'campaign_checkpoint_candidates.json'
candidates = json.loads(candidates_path.read_text(encoding='utf-8'))
assert sha(candidates_path) == '98cdec142151594fa358e448149a449202041e2d0be854045e3939ef9803d241'
assert [c['point_budget']['common_spent'] for c in candidates['checkpoints']] == [18,26,37,47,56]
assert all(sha(Path(s['path'])) == s['sha256'] for s in candidates['sources'])
all_ref_gems={g['name']:g for s in pack['reference_skill_sets'] for group in s['skills'] for g in group['gems']}
def cg(active, supports=(), weapon='미확인', note=''):
    gems=[dict(all_ref_gems[n]) for n in [active,*supports] if n in all_ref_gems]
    # Snapshot gem levels are deliberately not made campaign requirements.
    for g in gems:
        g.pop('level',None);g.pop('quality',None)
    return {'id':active,'active':active,'actives':[active],'supports':list(supports),'gems':gems,
            'weaponSet':weapon,'weapon_sets':{},'enabled':True,'source_type':'campaign evidence selection',
            'note':note,'source':'priority_taengjeong_kitava_shield_wall.md · 별이슬 영상/업데이트 및 탱정 카페130/179 참조'}
act1=[cg('Rolling Slam',['Brink I']),cg('Mace Strike',['Concentrated Area']),cg('Boneshatter',['Impact Shockwave','Magnified Area I']),cg('Frost Bomb'),cg('Infernal Cry'),cg('Herald of Ash')]
act2=[cg('Shield Wall',['Rapid Attacks I','Magnified Area I'],'1','보스에서는 Magnified Area I → Concentrated Area. 최신 Swap에는 Fire Attunement도 있지만 모든 전환 시점의 필수 보조로 고정하지 않습니다.'),cg('Shockwave Totem'),cg('Infernal Cry',weapon='2'),cg('Shield Charge',['Rapid Attacks I']),cg('Herald of Ash')]
later=act2+[cg('Freezing Mark',['Mark of Siphoning','Mark for Death'],note='Pounce에 징표 보조를 연결하지 않습니다. 실제 젬 요구조건을 만족할 때 사용합니다.'),cg('Magma Barrier',note='정신력 확보 후 사용합니다.')]
campaign=[]
for slug,label,sk in [('act1','액트 1 · 철퇴 육성',act1),('act2','액트 2 · 방패벽 전환',act2),('act3','액트 3 · 방패벽 유지',later),('act4','액트 4 · 보상·장비 보완',later),('interlude','막간 · 보상·방패 개선',later)]:
    candidate = next(c for c in candidates['checkpoints'] if c['id']==slug)
    budget = candidate['point_budget']['common_spent']
    equip=[{'slot':'Weapon 1','name':('Two Hand Mace · 양손 철퇴' if slug=='act1' else 'One Hand Mace · 한손 철퇴')+' 유형 목표','itemId':None,'levelReq':None,'mods':[],'properties':{},'source':'참조 영상 · 개별 장비 옵션 미확인'}]
    if slug!='act1':equip.append({'slot':'Weapon 2','name':'Armour Shield · 방어도 방패 유형 목표','itemId':None,'levelReq':None,'mods':[],'properties':{},'source':'방패벽 전환 영상 · 방어도 수치 최소값 미확인'})
    campaign.append({'id':'campaign-'+slug,'label':label,'creator':'별이슬골짜기 참조 + 탱정 보정; Pathcraft 구성','kind':'campaign_adaptation','ascendancy':'Smith of Kitava (전직 선택 목표)',
         'source':{'file':'priority_taengjeong_kitava_shield_wall.md','url':'https://www.youtube.com/watch?v=dcSWTFyF9TQ','update':'https://www.youtube.com/watch?v=zaft1U-7klQ'},
         'skills':sk,'equipment':equip,'passives':[{**node(n['numeric_id']), 'composition_source':n['source'], 'allocation':'common', 'attribute_choice':n['attribute_choice']} for n in candidate['nodes']],'weapon_set_nodes':{'1':[],'2':[]},
         'campaign_checkpoint':{**candidate, 'shield_bridge':candidates['shield_bridge'], 'insufficient_points_policy':candidates['insufficient_points_policy'], 'approval':'HQ msg_61c2d37901fa'},
         'conditions':[f'Pathcraft 구성 · 일반 패시브 {budget}점 확보 후 적용합니다. 숫자는 캐릭터 레벨·액트 보상 수가 아닙니다.',
                       '모든 노드는 공통 배분입니다. 무기 세트 추가 포인트·무료 클래스 시작점·타 전직은 포함하지 않습니다.',
                       '포인트가 부족하면 이전 체크포인트와 호환 무기 구성을 유지합니다. 액트 진입만으로 전환하지 않습니다.',
                       '각 젬·보조의 실제 사용 요구 능력치와 정신력·자원을 충족한 뒤 연결합니다. 능력치 선택은 실제 장비와 비교합니다.',
                       '탱정의 액트별 Kitava 패시브 스냅샷 복원이 아닙니다. DPS·HC 생존·새 캠페인 게임 표시 검증은 하지 않았습니다.']+
                       (['양손 철퇴와 실제 사용 가능한 강타·기절 스킬을 준비합니다.'] if slug=='act1' else ['한손 철퇴와 방어도 방패, 사용 가능한 Shield Wall을 준비합니다. 워브링어 효과를 가정하지 않습니다.'])+
                       (['액트1 양손 분기 5개 환불 후 13개 추가합니다. 실제 환불 비용과 능력치·젬·방패 조건부터 확인합니다.',
                         '조기 방패 전환은 검증된 13점 공통 연결부와 액트2 연결 추가 순서만 사용합니다. 여섯 번째 단계가 아니며 충분한 피해·능력치를 보장하지 않습니다.',
                         '레벨 7 스킬젬과 방어도 방패를 준비합니다. 스킬젬 등급 7은 캐릭터 레벨 7이 아닙니다.'] if slug=='act2' else [])})
pack['campaign_stages']=campaign
pack['campaign_composition']={k:candidates[k] for k in ('sources','start','composition_policy','insufficient_points_policy','shield_bridge','notable_effect_review','assumptions','limits')}
pack['campaign_composition'].update(approval='HQ msg_61c2d37901fa',candidate_file=candidates_path.name,candidate_sha256=sha(candidates_path))
# Extend with actual tree nodes/coordinates and direct neighbors, including the free graph anchor.
union.update(str(n) for c in candidates['checkpoints'] for n in c['ids_including_start_for_graph'])
neighbor=union|{c for nid in union for c in node(nid).get('connections',[])}
nodes=[node(n) for n in sorted(neighbor,key=int)]
edges=sorted({tuple(sorted((n['id'],c),key=int)) for n in nodes for c in n.get('connections',[]) if c in neighbor})
pack['tree'].update(nodes=nodes,edges=edges,scope='원본 스냅샷·참조 및 승인된 Pathcraft 캠페인 노드와 직접 연결 이웃. 실제 좌표·연결이며 저자 습득 순서가 아닙니다.')
pack['display_compatibility']={'skills_and_supports':{'level_interval':[1,100],'meaning':'observed B-compatible display convention only, never acquisition or transition levels; omission is not a proven root cause','evidence':'User-observed B skills visible (msg_db4b49567e07); original unchanged act3 also showed five recommendations (HQ msg_ccc4f724cad0, relayed msg_ba97abe53f22)'},'passives':{'status':'user_confirmed_A2_display','production_level_interval':[1,100],'evidence':'HQ msg_0f2e79de7708 user now sees passives; manager relay msg_ae87d801be97; original weapon_set 0/1/2 retained','meaning':'display only, never allocation levels or new-campaign gameplay PASS'}}
for stage in stages+campaign:
    for passive in stage['passives']: passive['level_interval']=[1,100]
    for group in stage['skills']:
        group['level_interval']=[1,100]
        for gem in group['gems']: gem['level_interval']=[1,100]
assert all(not n.get('unresolved') and 'x' in n and 'y' in n for s in campaign for n in s['passives'])
from lundburgerr_authored.compose import compose
pack, authored_review = compose(pack, node)
(ROOT/'lundburgerr_authored/validation.json').write_text(json.dumps(authored_review,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
out=ROOT/'planner_data';out.mkdir(exist_ok=True)
payload=json.dumps(pack,ensure_ascii=False,separators=(',',':'))
(out/'build_data.json').write_text(payload,encoding='utf-8')
(out/'build_data.js').write_text('window.PATHCRAFT_BUILD_DATA = '+payload+';\n',encoding='utf-8')
assert all(not n.get('unresolved') and 'x' in n for s in stages for n in s['passives'])
latest=stages[-1]
assert len(latest['passives'])==151
assert any(x['name']=="Cat O' Nine Tails" and x['slot']=='Belt' for x in latest['equipment'])
assert any(s['actives']==['Fire Spell on Hit','Detonate Dead'] for s in latest['skills'])
validation={'kitava_stages':len(stages),'kitava_node_counts':{s['id']:len(s['passives']) for s in stages},'unresolved_kitava_nodes':0,'tree_nodes_with_neighbors':len(nodes),'edges':len(edges),'json_sha256':sha(out/'build_data.json'),'source_files':[{s['id']:s['source']['sha256']} for s in stages],'game_load_test':False}
validation.update(tree_nodes_with_neighbors=len(pack['tree']['nodes']),edges=len(pack['tree']['edges']),authored_variants=8,authored_graph_validation='lundburgerr_authored/validation.json',transition_segments=len(pack['transition_plan']['segments']))
(out/'validation.json').write_text(json.dumps(validation,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(validation,ensure_ascii=False))
