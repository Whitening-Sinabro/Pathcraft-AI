"""Preserve downloaded author data; compose traceable displays and checked source-only transitions."""
from pathlib import Path
import collections
import copy
import hashlib
import json

ROOT=Path(__file__).resolve().parent
CORPUS=ROOT.parent
NATIVE=CORPUS/'native_planner'
DATA=Path('D:/Pathcraft-AI/data/game_data_poe2')
TREE_PATH=Path('D:/Pathcraft-AI/deliverables/skadoosh_hc_2026-09-07/sources/tree_0_5.json')
URL='https://mobalytics.gg/poe-2/builds/warrior-league-start-lundburgerr'
START=47175
ASC_START=5852

def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,obj):p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def rich_text(x):
    if isinstance(x,list):return ''.join(map(rich_text,x))
    if not isinstance(x,dict):return ''
    if x.get('type')=='static-data-widget':return x.get('label','')
    if x.get('type')=='linebreak':return '\n'
    if x.get('type')=='text':return x.get('text','')
    if 'children' in x:return rich_text(x['children'])+ ('\n' if x.get('type') in ('paragraph','listitem') else '')
    for k in ('value','root'):
        if k in x:return rich_text(x[k])
    return ''

class Composer:
    def __init__(self):
        self.doc=read(ROOT/'authored_document.json')
        self.tree=read(TREE_PATH)
        self.nodes={int(n['skill']):n for n in self.tree['nodes'].values() if isinstance(n,dict) and 'skill' in n and 'stringId' in n}
        self.by_string={n['stringId']:i for i,n in self.nodes.items()}
        self.adj={n:set() for n in self.nodes}
        for n,d in self.nodes.items():
            for e in d.get('connections',[]):
                v=int(e['id'])
                if v in self.adj:self.adj[n].add(v);self.adj[v].add(n)
        bases=read(DATA/'BaseItemTypes.json');self.bases={b['Id']:b for b in bases}
        self.gems={bases[g['BaseItemType']]['Id']:g for g in read(DATA/'SkillGems.json')}
        self.widgets={c['id']:c for c in self.doc['content']}
        self.variant_info=next(c['data']['childrenVariants'] for c in self.doc['content'] if 'childrenVariants' in c['data'])
        self.raw_files=sorted((ROOT/'raw_native').glob('*.build'))
        self.raw_builds=[(p,read(p)) for p in self.raw_files]
        self.review=[]
    def ids(self,v,key):return [int(x[5:]) for x in (v['passiveTree'][key]['selectedSlugs'] or [])]
    def map(self,v):
        result={}
        for k,w in [('mainTree',0),('set1Tree',1),('set2Tree',2)]:
            for n in self.ids(v,k):assert n not in result;result[n]=w
        return result
    def reach(self,ids,root=START):
        seen={root};queue=[root]
        for n in queue:
            for v in sorted(self.adj[n]&ids-seen):seen.add(v);queue.append(v)
        return seen
    def connected(self,mapping):
        return all((ids:={START}|{n for n,w in mapping.items() if w in (0,s)})==self.reach(ids) for s in (1,2))
    def budgets(self,mapping,asc=()):
        c=collections.Counter(mapping.values());paid=sum(not self.nodes[n].get('isAscendancyStart') and not self.nodes[n].get('isFreeAllocate') for n in asc)
        return {'ordinary_common':c[0],'weapon_set_1':c[1],'weapon_set_2':c[2],
                'active_1_ordinary':c[0]+c[1],'active_2_ordinary':c[0]+c[2],
                'ordinary_points_required':c[0]+max(c[1],c[2]),'weapon_specialization_capacity_required':max(c[1],c[2]),
                'ascendancy_points_required':paid,'free_ascendancy_nodes':len(asc)-paid,'free_class_start':1}
    def notes(self,vid):
        info=next(v for v in self.variant_info if v['id']==vid)
        notes={'overview':rich_text(info.get('description'))}
        for cid in info['childrenIds']:
            data=self.widgets[cid]['data']
            for key in ('descriptionPoeEquipment','descriptionPoeSkillGems','descriptionPoe2PassiveTree'):
                if key in data:notes[key]=rich_text(data[key])
        return notes
    def transition(self,old,target,label,monotone=False):
        """Numbered graph-safe operations, bounded by endpoint ordinary budgets; no invented nodes."""
        state=dict(old);ops=[];deferred=set()
        cap=max(self.budgets(old)['ordinary_points_required'],self.budgets(target)['ordinary_points_required'])
        weapon_cap=max(self.budgets(old)['weapon_specialization_capacity_required'],self.budgets(target)['weapon_specialization_capacity_required'])
        def emit(action,n,w,temporary=False):
            if action=='refund':assert state[n]==w;del state[n]
            else:assert n not in state;state[n]=w
            assert self.connected(state)
            b=self.budgets(state);assert b['ordinary_points_required']<=cap and b['weapon_specialization_capacity_required']<=weapon_cap
            ops.append({'number':len(ops)+1,'action':action,'numeric_id':n,'string_id':self.nodes[n]['stringId'],
                        'name':self.nodes[n]['name'],'weapon_set':w,'temporary_refund':temporary,'budget_after':b,
                        'both_active_trees_connected':True})
        if monotone:
            # Keep the largest endpoint-identical rooted core that is valid in BOTH sets.
            core={n:w for n,w in old.items() if target.get(n)==w}
            while True:
                disconnected=set()
                for w in (1,2):
                    active={START}|{n for n,v in core.items() if v in (0,w)}
                    disconnected |= active-self.reach(active)
                if not disconnected:break
                core={n:w for n,w in core.items() if n not in disconnected}
            assert self.connected(core)
            while state!=core:
                safe=[n for n in sorted(set(state)-set(core)) if self.connected({k:v for k,v in state.items() if k!=n})]
                assert safe, ('No monotone refund',label)
                n=safe[0];temporary=target.get(n)==state[n]
                emit('refund',n,state[n],temporary)
                if temporary:ops[-1]['temporary_refund_reason']={'type':'retained_dependency_outside_shared_rooted_core','explanation':'This retained node loses a root connection when the incompatible endpoint paths/categories are refunded. Refund it once in town and restore it once on the target tree; the endpoint-identical connected core is preserved.'}
            while state!=target:
                safe=[(w!=0,n,w) for n,w in target.items() if n not in state and self.connected({**state,n:w})]
                assert safe, ('No monotone add',label)
                _,n,w=min(safe);emit('add',n,w)
        for _ in range(1500):
            if state==target:break
            bad=[n for n,w in state.items() if target.get(n)!=w]
            if not bad:deferred.clear()
            removable=[n for n in sorted(bad) if self.connected({k:v for k,v in state.items() if k!=n})]
            if removable:n=removable[0];emit('refund',n,state[n]);continue
            additions=[]
            for n,w in target.items():
                if n in state or n in deferred:continue
                proposed={**state,n:w}
                budget=self.budgets(proposed)
                if self.connected(proposed) and budget['ordinary_points_required']<=cap and budget['weapon_specialization_capacity_required']<=weapon_cap:
                    unlocked=sum(self.connected({k:v for k,v in proposed.items() if k!=r}) for r in bad)
                    additions.append((-unlocked,w!=0,n,w))
            if additions:
                _,_,n,w=min(additions);emit('add',n,w);continue
            # A retained child can obstruct a category move, or temporary room may be needed.
            # Refund a graph-safe retained leaf, defer its re-add until incompatible old nodes are gone.
            safe={n for n in state if self.connected({k:v for k,v in state.items() if k!=n})}
            choices=[]
            for goal in bad:
                blockers=set()
                reduced={k:v for k,v in state.items() if k!=goal}
                for w in (1,2):
                    active={START}|{k for k,v in reduced.items() if v in (0,w)}
                    blockers.update(active-self.reach(active))
                for n in blockers&safe:
                    choices.append((len(blockers),n,goal))
            if choices:
                _,n,goal=min(choices)
                reason={'type':'dependent_subgraph','blocking_node':goal,'blocking_string_id':self.nodes[goal]['stringId'],
                        'explanation':'Removing/reassigning this blocking node disconnects the retained dependent node in an active set; refund dependent leaf first and restore after the connector is assigned.'}
            else:
                # Budget headroom fallback: refund an original retained leaf, not arbitrary new allocations.
                temp=sorted(safe&set(old)) or sorted(safe)
                assert temp, ('No source-only transition',label,state,target)
                n=temp[0]
                reason={'type':'point_budget_headroom','explanation':'All legal additions exceed the endpoint ordinary/specialization budget cap; temporarily refund a retained source leaf and restore after incompatible old nodes are removed.'}
            deferred.add(n);emit('refund',n,state[n],True)
            ops[-1]['temporary_refund_reason']=reason
        else:raise AssertionError(('Transition did not converge',label))
        assert state==target
        assert all(count==1 for count in collections.Counter((o['action'],o['numeric_id']) for o in ops).values()), 'Repeated refund/add cycle'
        return {'id':label,'from_budget':self.budgets(old),'to_budget':self.budgets(target),
                'ordinary_peak':max([self.budgets(old)['ordinary_points_required']]+[o['budget_after']['ordinary_points_required'] for o in ops]),
                'weapon_capacity_peak':max([self.budgets(old)['weapon_specialization_capacity_required']]+[o['budget_after']['weapon_specialization_capacity_required'] for o in ops]),
                'refund_count':sum(o['action']=='refund' for o in ops),'add_count':sum(o['action']=='add' for o in ops),
                'temporary_refunds':sum(o['temporary_refund'] for o in ops),'no_repeated_refund_or_add':True,'steps':ops,
                'gates':['Match the stated starting tree; actual current character allocation is not known','Actual ordinary and specialization points',
                         'Refund in town with actual gold available; amount not estimated','Check attributes, jewels, gear and both weapon sets after every operation'],
                'order_attribution':'Pathcraft graph-valid witness restricted to actual author endpoint IDs; not observed author click order'}
    def ascendancy_transition(self,old,target):
        state=set(old);ops=[]
        if not state:state={ASC_START}
        for action in ('refund','add'):
            while (pending:=((state-target) if action=='refund' else (target-state))):
                if action=='refund':valid=[n for n in sorted(pending) if n!=ASC_START and self.reach(state-{n},ASC_START)==state-{n}]
                else:valid=[n for n in sorted(pending) if self.adj[n]&state]
                assert valid,(action,pending)
                n=valid[0]
                if action=='refund':state.remove(n)
                else:state.add(n)
                ops.append({'number':len(ops)+1,'action':action,'numeric_id':n,'string_id':self.nodes[n]['stringId'],
                            'name':self.nodes[n]['name'],'paid':not bool(self.nodes[n].get('isFreeAllocate') or self.nodes[n].get('isAscendancyStart')),
                            'paid_ascendancy_after':self.budgets({},state)['ascendancy_points_required'],'connected':True})
        assert state==target
        return ops

def compose(pack,node):
    c=Composer();pack=copy.deepcopy(pack);oldpack=copy.deepcopy(pack)
    variants=c.doc['data']['buildVariants']['values'];stages=[];models={}
    ids={'default-variant':'lund-act1','3':'lund-act2-before22','2':'lund-shield-swap','4':'lund-act3','5':'lund-act4','6':'lund-interludes','7':'lund-maps','8':'lund-giga-reference'}
    common_notes=[
        'Lundburgerr 실제 저자 변형을 보존한 표시본입니다. Pathcraft가 임의 패시브를 추가하지 않았습니다.',
        '일반 포인트와 무기 특화 한도, 전직 포인트를 따로 확인합니다. 무기 특화 한도를 일반 포인트에 중복 더하지 않습니다.',
        '표시 범위 [1,100]은 획득·배분·사용 가능 레벨이 아닙니다. 실제 젬·장비 요구 레벨과 능력치·정신력·비용을 확인합니다.',
        'Smith’s Masterwork는 무료 분기이며 일반(흰색) 갑옷만 착용 가능합니다. 그 아래 선택한 옵션은 실제 전직 포인트가 필요합니다.',
        'Blood Rush가 있으면 마나 비용 일부가 생명력으로 전환됩니다. 생명력/마나 회복을 모두 확인하고 HC 안전이나 무한 회복을 가정하지 않습니다.',
        '저자 0.5.5 가이드이며 일부 트리 설명은0.4 경로를 유지합니다. 선택되지 않은 Vaal Pact 실험은 추가하지 않습니다.',
        '현재 데이터 기준 Molten Symbol은 물리 명중 피해25%를 화염으로 받는 효과입니다. 저자 설명의 반대 방향 표현을 수정하며 실제 배분·일반 갑옷 조건이 필요합니다.',
        '현재 데이터 최소 캐릭터 요구: 방패벽/도약 강타/동결 징표23, 보강 함성/지면 분쇄32, 재의 전령/Attrition11, 방패 돌진/지옥불 함성/충격파 토템7. 원본 내보내기의22/31 등은 오래된 값입니다.',
        '새 표시본의 실게임·DPS·HC 생존 검증은 없습니다. 예시 희귀 옵션을 전부 필수 구매로 해석하지 않습니다.'
    ]
    for v in variants:
        info=next(x for x in c.variant_info if x['id']==v['id']);title=info['title'];m=c.map(v);asc=c.ids(v,'ascendancyTree')
        assert c.connected(m)
        assert all(n in c.nodes for n in [*m,*asc])
        assert all(c.nodes[n].get('ascendancyName')=='Smith of Kitava' for n in asc)
        if asc:assert c.reach(set(asc),ASC_START)==set(asc)
        raw_path,raw=next((p,b) for p,b in c.raw_builds if b['name'].startswith(title[:30]))
        actual={(c.nodes[n]['stringId'],w) for n,w in m.items()}|{(c.nodes[n]['stringId'],0) for n in asc}
        raw_keys=[(p['id'],p.get('weapon_set',0)) for p in raw['passives']]
        assert actual<=set(raw_keys)
        attrs={int(a['nodeSlug'][5:]):a['attribute'] for a in (v['passiveTree']['attributeNodes'] or [])}
        passive_records=[]
        for n,w in [*m.items(),*((n,0) for n in asc)]:
            r=node(n);assert 'x'in r and not r.get('unresolved');r.update(level_interval=[1,100],allocation='common' if w==0 else 'weapon_set_'+str(w),source_variant=v['id'])
            if n in attrs:r['authored_attribute_choice']=attrs[n]
            passive_records.append(r)
        groups=[]
        assert len(raw['skills'])==len(v['skillGems']['gems'])
        for s,g in zip(raw['skills'],v['skillGems']['gems']):
            gems=[]
            for idx,sg in enumerate([s,*s.get('support_skills',[])]):
                gid=sg['id'];assert gid in c.gems and gid in c.bases
                name=g['activeSkill']['name'] if idx==0 else c.bases[gid]['Name']
                gems.append({'gemId':gid,'name':name,'nameSpec':name,'isSupport':idx>0,'enabled':True,
                             'level_interval':[1,100],'source_level_interval':sg.get('level_interval'),
                             'table_min_level':c.gems[gid]['MinLevelReq'],'source_gem_level':g['activeSkill'].get('level') if idx==0 else None})
            active=g['activeSkill']['name'];w='2' if active in ('Infernal Cry','Fortifying Cry') else '1'
            groups.append({'id':g['activeSkill']['gemSlug'],'active':active,'actives':[active],
                'supports':[g['name'] for g in gems[1:]],'gems':gems,'enabled':True,'weaponSet':w,'weapon_sets':{},'level_interval':[1,100],
                'note':'저자 Act3 설명: 함성 세트2 / 나머지 세트1. 실제 장착·능력치·점유·젬 요구조건 확인.',
                'source_type':'authored Mobalytics variant and actual native export'})
        equipment=[]
        native_slot_names={'Weapon1':'Weapon 1','Weapon2':'Weapon 1 Swap','Offhand1':'Weapon 2','Offhand2':'Weapon 2 Swap','BodyArmour1':'Body Armour','Helm1':'Helmet','Gloves1':'Gloves','Boots1':'Boots','Amulet1':'Amulet','Ring1':'Ring 1','Ring2':'Ring 2','Belt1':'Belt','Flask1':'Flask','Charm1':'Charm'}
        for e in raw['inventory_slots']:
            text=e.get('additional_text','');equipment.append({'slot':native_slot_names.get(e['inventory_id'],e['inventory_id']),
                'name':text.split('\n')[0],'mods':text.split('\n')[1:],'properties':{},'itemId':None,'source':'Lundburgerr authored variant '+v['id'],
                'source_level_interval':e.get('level_interval'),'source_inventory':copy.deepcopy(e)})
        b=c.budgets(m,asc);notes=c.notes(v['id'])
        stage={'id':ids[v['id']],'label':'Lundburgerr · '+title,'creator':'Lundburgerr','kind':'authored_smith_campaign','ascendancy':'Smith of Kitava',
            'source':{'file':'lundburgerr_authored/authored_document.json','sha256':sha(ROOT/'authored_document.json'),'url':URL,
                'variant_id':v['id'],'author_updated_at':c.doc['updatedAt'],'raw_native_file':str(raw_path.relative_to(CORPUS)),'raw_native_sha256':sha(raw_path)},
            'passives':passive_records,'weapon_set_nodes':{str(w):[str(n) for n,s in m.items() if s==w] for w in (1,2)},
            'skills':groups,'equipment':equipment,'conditions':[f"실제 일반 {b['ordinary_points_required']}점 / 특화 한도 {b['weapon_specialization_capacity_required']} / 유료 전직 {b['ascendancy_points_required']}점 조건."]+common_notes,
            'author_notes':notes,'author_equipment':copy.deepcopy(v['equipment']),
            'authored_checkpoint':{'variant_id':v['id'],'budgets':b,'native_file':None,'requirements':{'attributes':v['skillGems']['gemRequirements'],'attributes_interpretation':'Raw author gemRequirements metadata, not verified character or support-colour thresholds; actual item tooltips control eligibility',
                'attribute_choices':[{'numeric_id':n,'attribute':a,'allocated':n in m} for n,a in attrs.items()],
                'normal_body_armour_only':9988 in asc,'blood_rush_life_conversion':39083 in m,'actual_current_tree_unknown':True}}}
        models[stage['id']]={'normal':m,'ascendancy':set(asc)};stages.append(stage)
        c.review.append({'variant_id':v['id'],'title':title,'budgets':b,'raw_native_rows':len(raw_keys),'selected_unique_rows':len(actual),
            'duplicate_rows':len(raw_keys)-len(set(raw_keys)),'unselected_attribute_rows':[list(x) for x in sorted(set(raw_keys)-actual)],
            'normalization_authority':'Actual selectedSlugs main/set1/set2/ascendancy groups; extra attribute serialization tail is annotation-only, never a second common allocation',
            'raw_skill_range_vs_current_table':[{'id':g['gemId'],'source':g['source_level_interval'],'current_min':g['table_min_level']} for group in groups for g in group['gems'] if g['source_level_interval'] and g['source_level_interval'][0]!=g['table_min_level']],
            'selected_ids_exact':True,'both_active_trees_connected':True,'ascendancy_connected':True,'all_gem_ids_valid':True,
            'raw_native_file':str(raw_path),'raw_native_sha256':sha(raw_path)})
    baseline_campaign=copy.deepcopy(pack['campaign_stages'])
    pack['campaign_stages_previous_pathcraft']=baseline_campaign
    pack['authored_stages']=stages
    pack['campaign_stages']=[]
    for stage_id,filename in [('lund-act1','campaign-act1'),('lund-shield-swap','campaign-act2'),('lund-act3','campaign-act3'),('lund-act4','campaign-act4'),('lund-interludes','campaign-interlude')]:
        s=copy.deepcopy(next(s for s in stages if s['id']==stage_id));s['authored_id']=stage_id;s['id']=filename;s['authored_checkpoint']['native_file']=filename+'.build'
        pack['campaign_stages'].append(s)
    lv40=copy.deepcopy(next(s for s in stages if s['id']=='lund-act3'));lv40['id']='lund-lv40';lv40['label']='현재 Lv40 · Lundburgerr Act3 사용 조건';lv40['kind']='authored_lv40_gated'
    lv40['authored_checkpoint']['native_file']='current-lv40-lund-smith.build'
    lv40['skills']=[g for g in lv40['skills'] if g['active']!='Leap Slam']
    assert all(g['gems'][0]['table_min_level']<=40 for g in lv40['skills'])
    lv40['conditions']=[
        '현재 Lv40: 레벨 포인트39 + 실제 수령한 일반 보상. Act3 전체는44점이므로 보상 최소5점 필요하며, 모자라면 원본 연결 prefix를 따릅니다.',
        '저자 Act3의 특화9/9, 유료 전직4점은 별도 확보 조건입니다. 두 번째 전직 미완료라면 앞선 Shield Wall Swap의 유료2점 분기를 유지합니다.',
        '저자 설명에 따라 Leap Slam은 스킬 슬롯이 가득 차면 임시 제외합니다. Freezing Mark는 Act4 변경 전 유지합니다.',
        '방패벽 실제 젬의 요구 캐릭터 레벨·힘을 툴팁에서 확인합니다. 효과 표의 레벨을 젬 아이템 요구 레벨로 바꾸어 해석하지 않으며, 장비의 +스킬 레벨과도 구분합니다.',
        '정신력 보상 실제 수령 후 Attrition 또는 War Banner 중 선택합니다. 파일의 Attrition과 다른 점유 스킬이 동시에 사용 가능하다고 가정하지 않습니다.',
        'Fortifying Cry·Sunder는 저자의 첫 등급9+ 스킬젬 순서를 따릅니다. 마나/생명력 비용과 장비/젬 능력치 요구를 실제 캐릭터에서 확인합니다.'
    ]+lv40['conditions']
    lv40['level40']={'level':40,'base_ordinary':39,'full_variant_ordinary':44,'minimum_claimed_ordinary_rewards':5,
        'minimum_weapon_specialization_capacity':9,'paid_ascendancy_full_variant':4,'first_ascendancy_fallback_variant':'2',
        'removed_optional_skill':'Leap Slam','removal_evidence':'Act3 author skill notes explicitly permit temporary removal',
        'budget':{'divine':5,'chaos':17,'exalted':61,'greater_jeweller':3,'lesser_jeweller':29},'prices_or_exchange_assumed':False}
    maps=copy.deepcopy(next(s for s in stages if s['id']=='lund-maps'));maps['kind']='authored_mapping_later';maps['authored_checkpoint']['native_file']='lund-maps.build'
    maps['conditions'].insert(0,'저자 Maps 전체는109 일반점 목표로 첫 맵 진입85점과 다릅니다. Interludes85에서 검증된 추가/환불 prefix를 따라 실제 포인트만큼 진행합니다.')
    before22=copy.deepcopy(next(s for s in stages if s['id']=='lund-act2-before22'));before22['authored_checkpoint']['native_file']='campaign-act2-before22-lund.build'
    pack['transition_stages']=[lv40,maps,before22]
    order=[s['id'] for s in stages[:-1]]
    segments=[]
    # Author-to-author transitions, including source-only prefixes after the 85-point interlude.
    prev={};prev_asc=set()
    for stage_id in order:
        model=models[stage_id];seg=c.transition(prev,model['normal'],('start' if not segments else order[len(segments)-1])+'-to-'+stage_id)
        seg.update(from_stage='start' if not segments else order[len(segments)-1],to_stage=stage_id)
        seg['from_budget']=c.budgets(prev,prev_asc);seg['to_budget']=c.budgets(model['normal'],model['ascendancy'])
        for op in seg['steps']:
            op['budget_after'].update(ascendancy_points_required=seg['from_budget']['ascendancy_points_required'],free_ascendancy_nodes=seg['from_budget']['free_ascendancy_nodes'])
        seg['ascendancy_order']='Separate earned-ascendancy steps follow the ordinary segment; endpoint budget includes them'
        if model['ascendancy']:seg['ascendancy_steps']=c.ascendancy_transition(prev_asc,model['ascendancy'])
        else:seg['ascendancy_steps']=[]
        segments.append(seg);prev=model['normal'];prev_asc=model['ascendancy']
    latest=pack['stages'][-1];latest_ws={int(n):w for w in (1,2) for n in latest['weapon_set_nodes'][str(w)]}
    target={int(n['id']):latest_ws.get(int(n['id']),0) for n in latest['passives'] if not n.get('ascendancyName') and int(n['id'])!=START}
    target_asc={int(n['id']) for n in latest['passives'] if n.get('ascendancyName')}
    final=c.transition(models['lund-maps']['normal'],target,'lund-maps-to-kitava-29d39',monotone=True);final.update(from_stage='lund-maps',to_stage='kitava-29d39')
    final['from_budget']=c.budgets(models['lund-maps']['normal'],models['lund-maps']['ascendancy']);final['to_budget']=c.budgets(target,target_asc)
    for op in final['steps']:
        op['budget_after'].update(ascendancy_points_required=final['from_budget']['ascendancy_points_required'],free_ascendancy_nodes=final['from_budget']['free_ascendancy_nodes'])
    final['ascendancy_order']='Ordinary respec in town, then separate ascendancy refund/add witness, then conflicting body-armour swap only after Masterwork removed'
    final['ascendancy_steps']=c.ascendancy_transition(models['lund-maps']['ascendancy'],target_asc)
    final['gates'] += ['Town-only bounded respec: preserve the endpoint-identical rooted core, refund every incompatible/dependent node once, then add every target node once; combat and gear eligibility are not assured during refunds',
        'Major respec, not a small incremental swap: source Maps removes60 normal IDs and adds76 target IDs before set reassignment costs',
        'Stay with current full-life author setup until all target gates hold; do not equip a low-life belt prematurely',
        'Keep normal body armour during Masterwork refunds; remove all dependent Masterwork options and Masterwork itself before Brass Dome',
        'Cat O Nine Tails plus actual low-life maintenance; flasks can recover above low life; Execute III/Clash gated',
        'Constricting Command and actual surrounded condition before affected passive cluster',
        'Sacred Flame, Brass Dome, Defiance of Destiny and actual item level/attribute requirements; observed character97 is not a minimum',
        'Eternal Rage active plus Raging Cry/Enraged Warcry II and actual resources; no automatic permanent warcry loop',
        'Final Lifetap applies to its linked curse, not global Blood Magic; actual armour-break source and support-colour thresholds required']
    def skill_contract(stage):
        return [{'active':g['active'],'actives':g['actives'],'supports':g['supports'],
                 'gem_ids':[x.get('gemId',x.get('skillId')) for x in g['gems']], 'weaponSet':g.get('weaponSet'),
                 'weapon_sets':g.get('weapon_sets',{}),'enabled':g.get('enabled',True)} for g in stage['skills']]
    stages_by_id={s['id']:s for s in stages}
    for segment in segments:
        source=stages_by_id.get(segment['from_stage']);dest=stages_by_id[segment['to_stage']]
        segment['skill_setup_before']=skill_contract(source) if source else []
        segment['skill_setup_after']=skill_contract(dest)
        segment['skill_change_gate']='Use actual author notes and actual gem acquisition, socket, attribute, spirit and resource requirements; [1,100] only controls display. Act3 warcry-set2 assignment is an explicit recommendation for other variants, not proof of per-variant author assignments.'
    final['skill_setup_before']=skill_contract(stages_by_id['lund-maps'])
    final['skill_setup_after']=skill_contract(latest)
    before_names={g['active'] for g in final['skill_setup_before']};after_names={g['active'] for g in final['skill_setup_after']}
    final['skill_changes']={'removed_groups':sorted(before_names-after_names),'added_groups':sorted(after_names-before_names),
        'retained_group_changes':[{'active':n,'before':next(g for g in final['skill_setup_before'] if g['active']==n),
        'after':next(g for g in final['skill_setup_after'] if g['active']==n)} for n in sorted(before_names&after_names)],
        'set_assignment_authority':'Source Maps uses explicit Pathcraft recommendation from author Act3 notes; latest retains exact XML per-gem enableGlobal1/2 flags, not an invented universal warcry assignment'}
    final['target_equipment_requirements']=[{'slot':e['slot'],'name':e['name'],'base':e.get('base'),
        'observed_item_requirement_level':e.get('levelReq'),'mods':e.get('mods',[])} for e in latest['equipment']]
    final['respec_method']='Bounded full rebuild, not minimum refunds: endpoint-identical rooted core is empty. Refund125 unique source normal nodes once, then allocate141 unique target normal nodes once. Fifty unchanged-category retained nodes are restored once; fifteen shared IDs change category. Stay in town throughout and retain normal body until Masterwork removal.'
    segments.append(final)
    flat=[]
    for seg in segments:
        first=len(flat)+1
        for op in seg['steps']:
            flat.append({**op,'segment':seg['id'],'segment_step':op['number'],'number':len(flat)+1,'id':'authored-step-'+str(len(flat)+1),'gates':seg['gates']})
        seg['operation_range']=[first,len(flat)]
    for s in [*pack['campaign_stages'],*pack['transition_stages']]:
        target_id=s.get('authored_id',s['id']);target_id='lund-act3' if target_id=='lund-lv40' else target_id
        seg=next(x for x in segments if x['to_stage']==target_id)
        s['authored_checkpoint']['operation_range']=seg['operation_range']
        s['authored_checkpoint']['from_stage']=seg['from_stage']
    plan={'schema_version':2,'route_type':'actual_Lundburgerr_authored_variants_then_explicit_Taengjung_respec',
        'source':{'url':URL,'updated_at':c.doc['updatedAt'],'document_sha256':sha(ROOT/'authored_document.json'),'raw_zip_sha256':sha(ROOT/'author_download.raw.zip')},
        'level_budget_policy':{'formula':'ordinary_available = character_level - 1 + actually_claimed_ordinary_reward_points','current_level':40,'base_ordinary':39,
            'weapon_specialization_is_separate_capacity_not_additional_ordinary_points':True,'ascendancy_earned_separate':True,
            'interlude_levels62_to64_with_all24_rewards':[85,87],'all_rewards_assumed_claimed':False},
        'segments':segments,'steps':flat,'current_stage':'lund-lv40','author_maps_is_not_first_maps':True,
        'gear_gates':final['gates'],'current_level40':lv40['level40'],
        'quantified_diff':{'maps_normal_union':len(models['lund-maps']['normal']),'target_normal_union':len(target),
            'shared_numeric_ids':len(set(models['lund-maps']['normal'])&set(target)),
            'removed_numeric_ids':sorted(set(models['lund-maps']['normal'])-set(target)),
            'added_numeric_ids':sorted(set(target)-set(models['lund-maps']['normal'])),
            'final_budget':c.budgets(target,target_asc),'actual_refund_operations':final['refund_count'],'actual_add_operations':final['add_count'],
            'temporary_refunds':final['temporary_refunds'],'transient_ordinary_peak':final['ordinary_peak']},
        'limits':['Every displayed node belongs to an actual authored variant or preserved latest XML; no invented filler nodes',
            'Graph witness is a Pathcraft ordering, not author click-order evidence','Current player allocation/attributes/quest claims are not known',
            'No actual trade execution, HC market price, currency exchange, DPS or new-route game PASS',
            'Free start and free Masterwork cost zero; their dependent options consume earned ascendancy points',
            'Raw author export duplicate/stray attribute rows remain in raw files; selected tree controls allocations and attribute choices become annotations']}
    pack['transition_plan']=plan
    # Genuine source nodes and edges only; old coordinates/records and all old edges remain exact.
    oldnodes={n['id']:n for n in pack['tree']['nodes']};selected={int(n['id']) for s in stages for n in s['passives']}
    needed=selected|{v for n in selected for v in c.adj[n]}
    added=[node(n) for n in sorted(needed) if str(n) not in oldnodes]
    assert all('x'in n and not n.get('unresolved') for n in added)
    pack['tree']['nodes']+=added
    allowed={n['id'] for n in pack['tree']['nodes']};edges={tuple(e) for e in pack['tree']['edges']}
    extra={tuple(sorted((str(n),str(v)),key=int)) for n in needed for v in c.adj[n] if str(n) in allowed and str(v) in allowed}-edges
    pack['tree']['edges']+=sorted(extra)
    assert pack['tree']['nodes'][:len(oldpack['tree']['nodes'])]==oldpack['tree']['nodes']
    assert pack['tree']['edges'][:len(oldpack['tree']['edges'])]==oldpack['tree']['edges']
    for k,value in oldpack.items():
        if k not in ('campaign_stages','tree'):assert pack[k]==value,k
    review={'source':plan['source'],'variants':c.review,'all8_normal_and_ascendancy_graphs_connected':True,
        'display_normalization':'passives/skills/supports [1,100]; common0 explicit; source acquisition/item gates retained separately',
        'old_pack_metadata_preserved_except_authorized_campaign_replacement_and_genuine_graph_extension':True,
        'tree_added_nodes':len(added),'tree_added_edges':len(extra),'segments':[{k:v for k,v in s.items() if k!='steps'} for s in segments],
        'real_game_tested':False}
    return pack,review

def native_outputs(pack):
    from native_planner.generate import check_shape
    c=Composer();base=NATIVE/'versions/pre_transition_20260921/native_planner'
    frozen={p.name:sha(p) for p in NATIVE.glob('*.build') if p.name.startswith(('archive-','current-kitava-'))}
    assert len(frozen)==5 and all(d==sha(base/n) for n,d in frozen.items())
    owned_before={p.name:sha(p) for p in NATIVE.glob('*.build')}
    reports=[]
    for stage in pack['campaign_stages']+pack['transition_stages']:
        file=stage['authored_checkpoint']['native_file'];raw=read(CORPUS/stage['source']['raw_native_file']);out=copy.deepcopy(raw)
        out['name']=stage['label'];out['author']='Lundburgerr · 원본 / Pathcraft 표시·조건 주석'
        out['description']='\n'.join(stage['conditions'])+'\n원본 변형 '+stage['source']['variant_id']+' · '+stage['source']['author_updated_at']
        sets={int(n):w for w in (1,2) for n in stage['weapon_set_nodes'][str(w)]}
        out['passives']=[]
        for n in stage['passives']:
            note='Lundburgerr 원본 선택 노드. 실제 포인트·능력치 조건 충족 후 연결 순서 안내를 확인합니다.'
            if n.get('authored_attribute_choice'):note+=' 원본 능력치 선택: '+{'str':'힘','dex':'민첩','int':'지능'}[n['authored_attribute_choice']]+'.'
            if int(n['id'])==39083:note+=' 마나 비용6%가 생명력으로 전환되므로 실제 회복 여유를 확인합니다.'
            if int(n['id'])==9988:note+=' 무료 분기; 일반(흰색) 갑옷만 사용 가능합니다.'
            out['passives'].append({'id':n['stringId'],'weapon_set':sets.get(int(n['id']),0),'level_interval':[1,100],'additional_text':note})
        out['skills']=[]
        for group in stage['skills']:
            main=group['gems'][0];entry={'id':main['gemId'],'level_interval':[1,100],
                'additional_text':group['active']+' · 권장 세트'+group['weaponSet']+'. 실제 젬 레벨·능력치·정신력·마나/생명력 비용을 확인합니다.'}
            if stage['id']=='lund-lv40' and group['active']=='Shield Wall':entry['additional_text']+=' Lv40에서 실제 젬 아이템의 요구 레벨·힘을 확인; 효과 표 레벨을 구매 제한으로 해석하지 않습니다.'
            if group['active']=='Attrition':entry['additional_text']+=' 실제 정신력 보상 후 Attrition 또는 War Banner 선택. 모든 점유 동시 사용을 가정하지 않습니다.'
            if len(group['gems'])>1:entry['support_skills']=[{'id':g['gemId'],'level_interval':[1,100],'additional_text':g['name']+' · 실제 획득·속성/슬롯 조건 확인.'} for g in group['gems'][1:]]
            out['skills'].append(entry)
        for e in out['inventory_slots']:
            e['additional_text']=e.get('additional_text','')+'\n원본 예시입니다. 모든 옵션 필수 구매 아님; 실제 아이템 요구 레벨·능력치·등급을 확인합니다.'
        check_shape(out)
        assert len({(p['id'],p['weapon_set']) for p in out['passives']})==len(out['passives'])
        path=NATIVE/file;blob=(json.dumps(out,ensure_ascii=False,indent=2)+'\n').encode('utf8')
        if path.exists() and path.read_bytes()!=blob:
            previous=read(path)
            assert sha(path)==owned_before[file],('Concurrent output changed',file)
            assert ((base/file).exists() and sha(path)==sha(base/file)) or ((NATIVE/'versions/authored_pre_final_review_20260921'/file).exists() and sha(path)==sha(NATIVE/'versions/authored_pre_final_review_20260921'/file) and previous.get('author')=='Lundburgerr · 원본 / Pathcraft 표시·조건 주석' and previous.get('link')==URL),('Not an owned derived output',file)
        path.write_bytes(blob);assert read(path)==out
        reports.append({'file':file,'sha256':sha(path),'passives':len(out['passives']),'skills':len(out['skills']),'schema_ids_intervals':True})
    assert frozen=={n:sha(NATIVE/n) for n in frozen}
    dump(NATIVE/'authored_validation.json',{'status':'passed','frozen_latest_archive5':frozen,'outputs':reports,'game_pass':False})
    dump(CORPUS/'transition_plan.json',pack['transition_plan'])
    lines=['# Lundburgerr authored campaign → maps → Tangjung','',
        'Current level40 uses authored Act3: 35 common +9/9 specialization =44 ordinary, plus4 paid ascendancy and free Kitava start/Masterwork. Level40 gives39 ordinary before actually claimed rewards. Full tree needs at least5 claimed ordinary reward points,9 specialization capacity and the actual ascendancy points.',
        'Interludes is85 ordinary; Maps109 is a later target, not an instruction to spend109 upon first mapping. Follow connected source-only prefixes as points are earned.',
        'Normal body armour is mandatory while Masterwork is allocated; Blood Rush converts6% mana costs to life. Verify both resource recovery and actual gear/gem attributes. No HC or DPS PASS.','',
        'Raw author exports are preserved in lundburgerr_authored/raw_native and author_download.raw.zip. Display1..100 is not acquisition eligibility.','']
    for stage in [pack['transition_stages'][0],*pack['campaign_stages']]:
        lines += ['## '+stage['label'],'',*('- '+x for x in stage['conditions']),'','Author notes:']
        for key,val in stage['author_notes'].items():
            if val:lines+=['',key+':',val]
    for seg in pack['transition_plan']['segments']:
        lines+=['','## '+seg['id'],'',f"Refunds {seg['refund_count']}; additions {seg['add_count']}; temporary refunds {seg['temporary_refunds']}; peak ordinary {seg['ordinary_peak']}, specialization capacity {seg['weapon_capacity_peak']}.",'',*('- '+g for g in seg['gates']),'',
            '| # | Action | Numeric ID / string ID | Node | Set | Ordinary after |','|---:|---|---|---|---:|---:|']
        for op in seg['steps']:lines.append(f"| {op['number']} | {op['action']} | {op['numeric_id']} / {op['string_id']} | {op['name']} | {op['weapon_set']} | {op['budget_after']['ordinary_points_required']} |")
        if seg.get('respec_method'):lines+=['',seg['respec_method']]
        lines+=['','Skill/support and set changes (actual acquisition/resource gates still apply):']
        for side in ('before','after'):
            for group in seg['skill_setup_'+side]:lines.append('- '+side+': '+group['active']+' → '+', '.join(group['supports'])+'; set '+str(group['weaponSet'])+'; exact source flags '+json.dumps(group['weapon_sets'],ensure_ascii=False))
        if seg['ascendancy_steps']:
            lines+=['','Separate ascendancy (never ordinary points):']
            for op in seg['ascendancy_steps']:lines.append(f"{op['number']}. {op['action']} {op['numeric_id']} / {op['string_id']} — {op['name']}; paid total {op['paid_ascendancy_after']}.")
    (CORPUS/'transition_plan.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
    print(json.dumps({'status':'passed','outputs':len(reports),'frozen_latest_archive':5}))

