"""Arserina's live PoB -> Korean planners, with an explicit FR_FBBurger bridge."""
from pathlib import Path
import collections, copy, hashlib, html, importlib.util, json, re, sys, xml.etree.ElementTree as E

sys.dont_write_bytecode = True
sys.stdout.reconfigure(encoding='utf-8')
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
OUT = HERE / 'BuildPlanner'
SOURCE = 'https://poe.ninja/poe2/pob/27e13'
CHAR = 'https://poe.ninja/poe2/profile/CololadoBurger-7117/forbiddenrites/character/FR_FBBurger'
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d): p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
spec = importlib.util.spec_from_file_location('planner_converter', REPO/'scripts/build_poe2_planner_files.py')
conv = importlib.util.module_from_spec(spec); spec.loader.exec_module(conv)
XML = (HERE/'sources/arserina_27e13.xml').read_text(encoding='utf-8')
CX = (HERE/'sources/FR_FBBurger_38.xml').read_text(encoding='utf-8')
ROOT, CR = E.fromstring(XML), E.fromstring(CX)
TREE = read(REPO/'data/_cache/tree_0_5.json')
NUM = {n['skill']:n for n in TREE['nodes'].values() if isinstance(n,dict) and 'skill' in n and 'stringId' in n}
N = {n['stringId']:n for n in NUM.values()}
IDX = {k:n['stringId'] for k,n in NUM.items()}
ADJ = collections.defaultdict(set)
for k,n in N.items():
    for c in n.get('connections',[]):
        if c['id'] in IDX:
            ADJ[k].add(IDX[c['id']]); ADJ[IDX[c['id']]].add(k)
KO = {r['name']:html.unescape(r['title'].split(' - PoE2DB')[0]) for r in read(HERE/'sources/gem_korean_titles.json')}
G = {g['Id']:g['Name'] for g in read(REPO/'data/game_data_poe2/BaseItemTypes.json')}
TRANS = read(REPO/'data/merged_translations.json')['items']
ITEM_KO = {
 'Ring':'반지', 'Chiming Staff':'종소리 지팡이', 'Bombard Crossbow':'폭격 석궁',
 'Cannonade Crossbow':'포격 석궁', "Kaom's Heart":'카옴의 심장',
 'Ultimate Life Flask':'궁극의 생명력 플라스크', 'Ultimate Mana Flask':'궁극의 마나 플라스크',
 'Thawing Charm':'해빙의 호신부', 'Stone Charm':'돌 호신부', 'Silver Charm':'은빛 호신부',
}
SLOT_KO = {'Weapon1':'세트 I 무기','Weapon2':'세트 II 무기','Helm1':'투구','BodyArmour1':'갑옷',
 'Gloves1':'장갑','Boots1':'장화','Amulet1':'목걸이','Belt1':'허리띠','Ring1':'반지 1','Ring2':'반지 2',
 'Flask1':'플라스크','Charm1':'호신부','Offhand1':'세트 I 보조무기','Offhand2':'세트 II 보조무기'}
STAT = {'Physical Damage':'물리 피해','Spell Damage':'주문 피해','Fire Damage':'화염 피해',
 'Armour and Evasion':'방어도 및 회피','Armour':'방어도','Energy Shield':'에너지 보호막',
 'Attack Speed':'공격 속도','Movement Speed':'이동 속도','Amount Recovered':'회복량',
 'maximum Life':'최대 생명력','maximum Mana':'최대 마나','Fire Resistance':'화염 저항',
 'Cold Resistance':'냉기 저항','Lightning Resistance':'번개 저항','Chaos Resistance':'카오스 저항',
 'Accuracy Rating':'정확도','Strength':'힘','Dexterity':'민첩','Intelligence':'지능',
 'Mana Regeneration Rate':'마나 재생 속도','Rarity of Items found':'발견하는 아이템 희귀도',
 'Critical Hit Chance':'치명타 확률','Light Radius':'시야 반경','Spirit':'정신력',
 'Flask Life Recovery rate':'플라스크 생명력 회복 속도','Stun Threshold':'기절 한계치',
 'maximum Energy Shield':'최대 에너지 보호막','Evasion Rating':'회피','Duration':'지속시간',
 'Charges':'최대 충전 수','Charges gained':'충전 획득량','Recovery rate':'회복 속도',
 'Armour and Energy Shield':'방어도 및 에너지 보호막','Cast Speed':'시전 속도'}
UNTRANSLATED = set()
def mod_ko(line):
    m=re.match(r'^(\d+\. )(.*)',line)
    if not m:return line
    prefix,s=m.groups()
    patterns=[
      (r'([+\d.]+) to Level of all (Fire Spell|Spell|Projectile) Skills',lambda a,b:f"모든 {dict({'Fire Spell':'화염 주문','Spell':'주문','Projectile':'투사체'})[b]} 스킬 레벨 {a}"),
      (r'([\d.]+)% increased (.+)',lambda a,b:f'{STAT[b]} {a}% 증가'),
      (r'([\d.]+)% reduced (.+)',lambda a,b:f'{STAT[b]} {a}% 감소'),
      (r'([+\d.]+)% to (.+)',lambda a,b:f'{STAT[b]} {a}%'),
      (r'([+\d.]+) to (.+)',lambda a,b:f'{STAT[b]} {a}'),
      (r'Adds ([\d.]+) to ([\d.]+) (Physical|Fire|Cold|Lightning) [Dd]amage( to Attacks)?',lambda a,b,c,d:f"{'공격 시 ' if d else ''}{dict(Physical='물리',Fire='화염',Cold='냉기',Lightning='번개')[c]} 피해 {a}~{b} 추가"),
      (r'Gain ([\d.]+)% of Damage as Extra Fire Damage',lambda a:f'피해의 {a}%를 추가 화염 피해로 획득'),
      (r'Grenades have ([\d.]+)% chance to activate a second time',lambda a:f'유탄이 {a}% 확률로 한 번 더 발동'),
      (r'([+\d.]+)% of Armour also applies to Elemental Damage',lambda a:f'방어도의 {a}%가 원소 피해에도 적용'),
      (r'([\d.]+) Life Regeneration per second',lambda a:f'생명력 초당 {a} 재생'),
      (r'([\d.]+) to ([\d.]+) Physical Thorns damage',lambda a,b:f'물리 가시 피해 {a}~{b}'),
      (r'Gain ([\d.]+) Life per enemy killed',lambda a:f'적 처치 시 생명력 {a} 획득'),
      (r'Gains ([\d.]+) Charges per Second',lambda a:f'매초 충전 {a} 획득'),
      (r'Recover ([\d.]+) Life when Used',lambda a:f'사용 시 생명력 {a} 회복'),
    ]
    for pat,fun in patterns:
        m=re.fullmatch(pat,s)
        if m:
            try:return prefix+fun(*m.groups())
            except KeyError:pass
    UNTRANSLATED.add(s)
    return prefix+'현재 장비 옵션: '+s

def display(g):
    en=g.get('nameSpec') or G[g['id']]
    assert en in KO and re.search('[가-힣]',KO[en]),en
    return KO[en]

def state(spec):
    out={IDX[int(i)]:0 for i in spec.get('nodes','').split(',') if i}
    for w in (1,2):
        for e in spec.findall('WeaponSet'+str(w)):
            for k in e.get('nodes','').split(','):
                if k:out[IDX[int(k)]]=w
    return out
def root_nodes(asc):return ('duelist597','Ascendancy'+asc+'Start')
def reachable(nodes,root):
    nodes=set(nodes)|{root};seen={root};front={root}
    while front:
        front=set().union(*(ADJ[n] for n in front))&nodes-seen;seen|=front
    return seen==nodes
def check_state(s,asc='Mercenary3'):
    assert set(s)<=set(N)
    for w in (1,2):
        selected={k for k,v in s.items() if v in (0,w)}
        reg={k for k in selected if not N[k].get('ascendancyName')}
        assert reachable(reg,'duelist597'),('regular disconnected',w)
        a=selected-reg
        assert reachable(a,'Ascendancy'+asc+'Start'),('asc disconnected',w)
def usage(s):
    reg={k:v for k,v in s.items() if not N[k].get('ascendancyName') and not N[k].get('classesStart')}
    asc=sum(bool(N[k].get('ascendancyName')) and not N[k].get('isAscendancyStart') and not N[k].get('isMultipleChoiceOption') for k in s)
    return {'ordinary':max(sum(v in (0,w) for v in reg.values()) for w in (1,2)),
      'weapon_sets':[sum(v==w for v in reg.values()) for w in (1,2)],'ascendancy':asc}

SPEC = ROOT.findall('Tree/Spec'); SETS=ROOT.findall('Skills/SkillSet')
CURRENT=state(CR.find('Tree/Spec')); check_state(CURRENT)
TARGET=state(SPEC[2]); check_state(TARGET)
# Thirteen level-up points (38 -> 51), no refund and no assumed quest reward.
# Every addition must be in the original grenade tree and reachable now.
bridge=dict(CURRENT);original_grenade=state(SPEC[1]); order=[]
for _ in range(13):
    candidates=[k for k in original_grenade if k not in bridge and not N[k].get('ascendancyName') and ADJ[k]&set(bridge)]
    assert candidates,'no connected continuation'
    candidates.sort(key=lambda k:(k not in TARGET,not bool(N[k].get('isNotable')),k))
    k=candidates[0];bridge[k]=0;order.append(k);check_state(bridge)

ROTATE='기름 유탄으로 기름 지대 생성 → 안전한 위치에서 화염파 최대 단계로 강한 점화 생성 → 기름 유탄으로 불붙은 지대를 이어 간다. 연결이 끊기거나 약한 점화로 바뀌면 새 위치에서 화염파로 다시 시작한다. 회오리는 공중 적을 처리할 때만 필요한 만큼 사용한다.'
GATE='52레벨은 화염파 사용 최소 조건이다. 고급 마석학, 화염파 품질 20%, 화염파 보조 4칸, 기름 유탄 보조 3칸, 사용할 젬의 능력치와 정신력을 먼저 확보한다. 원본 03 전체 트리는 일반 67점·전직 4점·무기 세트 포인트 각 17점이 필요하다. 포인트가 부족하면 퀘스트 보상을 받거나 레벨을 더 올리고 전환한다.'
MATERIAL='원본 영상의 최소 준비물: 2레벨 미가공 보조 젬 3개, 4레벨 3개, 5레벨 1개 / 상위 쥬얼러 오브 1개(화염파), 하위 쥬얼러 오브 1개(기름 유탄) / 세공사의 오브 4개(화염파 품질 20%). 약 47,000골드는 제작자 육성 경로의 예시이며 현재 캐릭터 환불 비용과 같다는 뜻이 아니다. 카옴의 심장은 52 전환 필수가 아니다.'
NAMES=['아르세리나 01 38-51 젬링 이어가기','아르세리나 02 52이상 화염파 전환','아르세리나 03 지도 성장 목표','아르세리나 04 후기 장비 목표']

def annotations(name,stage):
    if stage==0:
        if name=='Virtuous Barrier':return '전직에서 자동 부여. 현재 고급 마석학과 미덕의 정수 전직을 유지한다.'
        if name in ('Herald of Ash','Attrition'):return '현재 캐릭터의 버프 구성. 예약 가능한 정신력을 확인하고 유지한다.'
        return '현재 캐릭터 구성 유지. 유탄은 세트 I 석궁으로 사용한다.'
    common={
      'Flameblast':'세트 I 지팡이. 최대 단계로 강한 점화를 만드는 주력. 품질 20% 확보. 스킬 상세 무기 설정에서 I 사용.',
      'Oil Grenade':'세트 II 석궁. 기름 지대를 깔고 이어 간다. 스킬 상세 무기 설정에서 II 사용. 화염파 전환 후 이 스킬에 화염 피해가 섞이지 않도록 장비의 공격 시 화염 피해 추가를 점검한다.',
      'Blasphemy':'시간의 사슬을 이 스킬 안에 넣는다. 아래 시간의 사슬은 삽입할 액티브 젬을 표시하기 위한 별도 항목이다. 신성 모독의 연결을 게임에서 직접 완성한다. 정신력이 부족하면 필수 화염파/기름 유탄을 먼저 갖추고 추가한다.',
      'Elemental Weakness':'세트 I 지팡이. 희귀·보스에게 필요한 보조 저주. 기름 유탄 장판 유지가 우선이다.',
      'Tornado':'공중 적 처리용. 점화 지대를 흡수해서 약한 점화를 퍼뜨릴 수 있으므로 구르기 자동 연계나 상시 난사는 피한다. 지팡이 쪽 세트 I 사용을 권장한다(원본 장비 기준 배정).',
      'Arctic Armour':'버프 보조. 원소 집중을 연결한 원본 구성을 유지한다. 정신력과 무기 전환 후 활성 상태를 확인한다.',
      'Virtuous Barrier':'미덕의 정수가 자동 부여하는 버프. 켜고 유지한다. 원본 품질 수치는 성장 목표이며 지금 모두 맞추라는 뜻은 아니다.',
      'Sigil of Power':'세트 I 종소리 지팡이가 부여하는 스킬. 해당 지팡이가 없으면 이 스킬도 없다. 화염파를 준비할 때 사용할 수 있는 보조이며 필수 전환 장비를 이 베이스로 제한하지 않는다.',
      'Grenade':'세트 II 원본 포격 석궁의 유탄 스킬. 아래 보조는 후기 원본 연결이다. 기본 공격을 초반 폭발 유탄으로 혼동하지 않는다.',
    }
    if stage==3 and name in ('Infernal Cry','Seismic Cry','Shockwave Totem','Herald of Ash','Overwhelming Presence'):
        return '원본 05에서 고결한 방어막용으로 묶어 둔 보조 스킬. 주력은 화염파와 기름 유탄이다. 해당 스킬의 무기·정신력 조건을 충족할 때만 사용한다.'
    return common.get(name,'원본 성장 단계의 보조 구성. 주력 전환 조건을 갖춘 뒤 추가한다.')

def convert_skills(skillset,stage):
    result=[];represented=set();expected=[];omitted=[]
    for group in skillset.findall('Skill'):
        if group.get('enabled')=='false':continue
        allg=[g for g in group.findall('Gem') if g.get('gemId')]
        if not allg:continue
        if group.get('source') and allg[0].get('gemId') in represented:continue
        gems=[g for g in allg if g.get('enabled')!='false'];disabled=[g for g in allg if g.get('enabled')=='false']
        if not gems:continue
        first=gems[0];gid=first.get('gemId');name=first.get('nameSpec');represented.add(gid)
        expected.append(tuple(g.get('gemId') for g in gems))
        supports=[g for g in gems[1:] if 'SupportGem' in g.get('gemId')]
        nested=[g for g in gems[1:] if 'SupportGem' not in g.get('gemId')]
        linked=' + '.join(display(g.attrib) for g in gems[1:]) or '연결 보조 없음'
        text=f'{display(first.attrib)}\n{annotations(name,stage)}\n[연결] {linked}\n원본 젬 등급 {first.get("level","1")} / 품질 {first.get("quality","0")}%. 상위 단계의 등급은 최종 목표이며 현재 착용 가능한 등급을 사용한다.'
        if disabled:
            text+='\n[원본에서 비활성] '+', '.join(display(g.attrib) for g in disabled)+' — 자동 연결 목록에서 제외.'
            omitted += [g.get('gemId') for g in disabled]
        entry={'id':gid,'level_interval':[1,100],'additional_text':text}
        if supports:entry['support_skills']=[{'id':g.get('gemId'),'level_interval':[1,100],'additional_text':display(g.attrib)+' — '+display(first.attrib)+'에 연결'} for g in supports]
        result.append(entry)
        for g in nested:
            result.append({'id':g.get('gemId'),'level_interval':[1,100],
              'additional_text':display(g.attrib)+' — 신성 모독 안에 넣는 액티브 젬. 별도 시전 스킬칸에 두는 것으로 연결이 완성되지 않는다. 신성 모독과 그 보조 젬들을 함께 연결한다.'})
    return result,expected,omitted

def inv_from(xml,root,index):
    its=root.findall('Items/ItemSet')
    assert its
    return conv.inventory_slots(E.tostring(its[index],encoding='unicode'),conv.parse_items(xml),conv.base_names(),[])

def make_inv(original,stage):
    inv=copy.deepcopy(original)
    for x in inv:
        sid=x['inventory_id'];lines=x.get('additional_text','').splitlines();u=x.get('unique_name')
        name=u or (lines[0] if lines else SLOT_KO.get(sid,sid))
        label=ITEM_KO.get(name,TRANS.get(name))
        heading=(label+' ('+name+')') if label else SLOT_KO.get(sid,sid)+' ('+name+')'
        mods=[mod_ko(s) for s in lines[1:]]
        x['additional_text']=('[현재 캐릭터 장비 참고]\n' if stage==0 else '[원본 장비 예시 — 필수 최소 수치가 아님]\n')+heading+'\n'+'\n'.join(mods)
        if stage==0:
            tips={
             'Weapon1':'현재 석궁으로 유탄 육성을 이어 간다. 교체 시 실제 공격 피해와 공격 속도를 비교한다. 52 전환용 화폐를 모두 소모하지 않는다.',
             'Boots1':'이동 속도와 생명력, 부족한 저항을 함께 비교한다.',
            }
            tip=tips.get(sid,'구할 수 있는 범위에서 생명력과 부족한 저항을 보강한다. 현재 착용품은 그대로 사야 하는 추천 목록이 아니다.')
        else:
            tips={
             'Weapon1':'세트 I 지팡이. 우선 옵션: 화염 주문/모든 주문 스킬 레벨 → 주문·화염 피해. 예시와 같은 고급 지팡이를 사야 전환되는 것은 아니다.',
             'Weapon2':'세트 II 석궁. 기름 유탄용. 공격 시 화염 피해 추가를 제거하고 기존 화염 조율 보조가 남지 않았는지 확인한다.',
             'Boots1':'추천 옵션: 이동 속도, 최대 생명력, 부족한 원소 저항.',
             'Amulet1':'추천 옵션: 현재 필요한 능력치·생명력·저항. 주문 스킬 레벨은 이후 성장 목표.',
             'Flask1':'현재 레벨에 맞는 회복 플라스크를 먼저 사용한다. 원본의 궁극 플라스크는 52레벨 필수품이 아니다.',
             'Charm1':'해제하려는 상태이상과 현재 열린 호신부 칸에 맞춰 사용한다. 원본 세 칸을 모두 갖춰야 전환되는 것은 아니다.',
             'BodyArmour1':'생명력·저항을 우선한다. 카옴의 심장은 후기 목표이며 52레벨 전환 필수가 아니다.',
            }
            tip=tips.get(sid,'추천 옵션: 최대 생명력과 부족한 저항. 장비의 공격 시 화염 피해 추가·화염 가시가 약한 점화를 만들지 않는지 확인한다.')
        x['additional_text']+='\n\n[추천 옵션과 용도]\n'+tip
    by={x['inventory_id']:x for x in inv}
    if stage and 'Weapon1'in by:by['Weapon1']['additional_text']+='\n\n[사용 순서]\n'+ROTATE
    if 'BodyArmour1'in by:by['BodyArmour1']['additional_text']+='\n\n[다음 단계]\n'+(GATE+'\n'+MATERIAL if stage<2 else '표시된 패시브 전체는 성장 목표다. 필요한 포인트·젬 소켓·정신력을 확보한 만큼 진행한다. 최신 가이드의 회오리 사용 주의를 계속 적용한다.')
    return inv

OUT.mkdir(parents=True,exist_ok=True)
report={'source':SOURCE,'character':CHAR,'source_sha256':hashlib.sha256(XML.encode()).hexdigest(),
 'current_sha256':hashlib.sha256(CX.encode()).hexdigest(),'bridge_policy':'현재 젬링 유지, 환불 없이 원본 02 일반 노드 중 연결 가능한 13점을 선택. 아르세리나 원본 육성 경로와 구분.',
 'planners':[],'bridge_addition_order':order,'disabled_gems_removed':[],'runtime_verified':False}
plans=[];README=['# 아르세리나 화염파 젬링 — FR_FBBurger 소코 이어가기','',
 '현재 38레벨 젬링은 **01**부터 사용한다. 52레벨과 재료·포인트를 갖추면 **02**로 전환한다. 게임의 다른 플래너를 삭제하거나 캐릭터 패시브를 자동 변경하지 않는다.','',
 '필터는 지금 `Arserina-01-POE2-Act`를 선택한다. 액트 완료 후 `Pathcraft-Arserina-SC-02-EarlyMaps`, 장비가 안정되면 `Pathcraft-Arserina-SC-03-SettledMaps`로 바꾼다. 첫 파일은 아르세리나 원본, 지도용 두 파일은 Pathcraft 보완본이다. [필터 사용·설치 안내](필터사용안내.md)를 함께 읽는다. 플래너 번호와 필터 번호는 별개다.','',
 '원본은 택티션 육성 후 52레벨 젬링 전환이다. **01만 현재 캐릭터에 맞춘 Pathcraft 연결 단계**이며, 02~04의 패시브와 활성 젬은 아르세리나 PoB 03 Swap/04/05에 근거한다.','',
 '원본 링크: '+SOURCE,'현재 캐릭터: '+CHAR,'원본 영상: https://www.youtube.com/watch?v=I8GpKlVcq-s','52 전환 영상: https://youtu.be/rNIXxLrQY6E','약한 점화 후속 영상: https://youtu.be/O1wYj0cVcP0','',
 '## 먼저 알아둘 것','',GATE,'',MATERIAL,'',
 '플래너는 안내 파일이다. G 스킬창의 무기 세트 체크, 젬 연결, 품질·소켓 확장과 패시브 환불은 직접 해야 한다. 무기 아이템의 룬 홈에 보조 젬을 넣는 것이 아니다.','',
 '**무기 배정:** 02~04는 세트 I 지팡이로 화염파, 세트 II 석궁으로 기름 유탄. 이는 원본 PoB의 장비와 패시브 세트를 기준으로 한 배정이다. 현재 젬링의 무기 번호와 다를 수 있다.','',
 '**신성 모독:** 시간의 사슬을 그 안에 넣고 의식의 저주·느린 효력을 연결한다. 플래너에는 시간의 사슬을 별도 항목으로 표시하되, 실제로는 신성 모독 안에 넣어야 한다.','',
 '**회오리:** 공중 적에게 필요할 때 사용한다. 점화 지대 위에서 상시 난사하거나 구르기에 자동 연계하면 약한 점화가 퍼질 수 있다는 후속 영상의 주의를 반영했다.','',
 '## 38 → 51 연결 단계','',
 '현재 패시브를 환불하지 않고 레벨업 13점만 추가하는 연결이다. 추가 퀘스트 포인트를 이미 얻었다고 가정하지 않는다. 현재 젬링의 미덕의 정수·고급 마석학을 유지하고 택티션으로 되돌리지 않는다.','']
for j,k in enumerate(order,1): README.append(f'{j}. {N[k]["name"]} (`{k}`) — 현재 트리에 인접한 원본 유탄 노드')
README += ['', '추가 순서는 플래너의 해당 패시브 설명에도 표시되어 있다. 연결 단계에서 화염파 전환까지 새로 얻는 퀘스트 포인트는 전환 비용과 필요한 포인트를 확인해 사용한다.','']

for stage in range(4):
    original_index=stage+1
    s=bridge if stage==0 else state(SPEC[original_index])
    check_state(s);cost=usage(s)
    skills,expected,disabled=convert_skills(CR.find('Skills/SkillSet') if stage==0 else SETS[original_index],stage)
    inv=make_inv(inv_from(CX,CR,0) if stage==0 else inv_from(XML,ROOT,original_index),stage)
    if stage==0:
        description='[지금 할 일]\n38레벨 FR_FBBurger의 유탄 젬링을 이어 키운다. 전직은 그대로 유지한다. 현재 스킬 연결을 보존하고 신규 패시브 13점을 번호순으로 추가한다. 이 단계는 Pathcraft 연결안이며 제작자의 택티션 육성과 다르다.\n\n[사용 순서]\n섬광 유탄으로 제어 → 기름/가스 유탄 → 폭발 유탄 → 이동하며 재사용 대기. 현재 장비로 진행 가능한 구간에서 52 전환 재료를 모은다.\n\n[무기·스킬셋]\n유탄은 현재 세트 I 석궁. 52 전환 때는 플래너 02의 지팡이 I / 석궁 II 배정으로 옮긴다.\n\n'+MATERIAL
    else:
        description='[지금 할 일]\n'+(GATE if stage==1 else '아르세리나 원본 '+SPEC[original_index].get('title')+'의 성장 목표. 직전 단계를 플레이하면서 장비와 포인트를 갖춘 만큼 확장한다.')+'\n\n[무기·스킬셋]\n세트 I 지팡이: 화염파·원소 약화·힘의 부적. 세트 II 석궁: 기름 유탄. 버프는 양 세트에서 유지 가능한 정신력을 확인한다.\n\n[사용 순서]\n'+ROTATE
    description+=f'\n\n[전체 트리 비용]\n일반 {cost["ordinary"]}점 / 전직 {cost["ascendancy"]}점 / 무기 세트 전용 각 {cost["weapon_sets"]}점. 장비와 젬 등급·품질은 원본 목표이며 전부 최소 요구치가 아니다.'
    b={'name':NAMES[stage],'author':'Arserina / Pathcraft 한국어 변환','link':SOURCE,
       'description':description,'ascendancy':'Mercenary3',
       'passives':[dict(id=k,**({'weapon_set':w} if w else {}),**({'additional_text':f'38→51 추가 순서 {order.index(k)+1}/13. 현재 패시브 환불 없이 추가.'} if stage==0 and k in order else {})) for k,w in s.items()],
       'skills':skills,'inventory_slots':inv}
    assert len(b['name'])<=40
    path=OUT/(b['name']+'.build');path.write_bytes(json.dumps(b,ensure_ascii=False,separators=(',',':')).encode())
    plans.append(b)
    report['planners'].append({'file':path.name,'cost':cost,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
      'source_spec':'FR_FBBurger + original 02' if stage==0 else SPEC[original_index].get('title'),
      'expected_skill_groups':expected,'skills':len(skills),'inventory_slots':len(inv),'original_passives_preserved':stage>0})
    report['disabled_gems_removed'].append(disabled)
    README += ['## '+b['name'],'',description,'','| 스킬 | 연결할 젬 |','|---|---|']
    for g in skills:
        if g['id'].endswith('SkillGemTemporalChains'):continue
        children=[KO[G[c['id']]] for c in g.get('support_skills',[])]
        if g['id'].endswith('SkillGemBlasphemy'):children.insert(0,'시간의 사슬 (안에 넣을 액티브)')
        README.append('| '+KO[G[g['id']]]+' | '+' + '.join(children)+' |')
    README.append('')

def route(begin,target):
    current=dict(begin);operations=[];pool=max(usage(begin)['ordinary'],usage(target)['ordinary'])
    for _ in range(600):
        if current==target:break
        changed=False
        for k in sorted(k for k,v in current.items() if target.get(k)!=v):
            trial={a:b for a,b in current.items() if a!=k}
            try:check_state(trial)
            except AssertionError:continue
            operations.append({'action':'refund','id':k,'weapon_set':current[k]});current=trial;changed=True;break
        if changed:continue
        for k in sorted(set(target)-set(current),key=lambda k:(target[k]!=0,k)):
            trial={**current,k:target[k]}
            if usage(trial)['ordinary']>pool:continue
            try:check_state(trial)
            except AssertionError:continue
            operations.append({'action':'allocate','id':k,'weapon_set':target[k]});current=trial;changed=True;break
        if not changed:raise AssertionError(('transition blocked',len(current),len(target)))
    assert current==target
    return {'method':'공통 노드를 유지하며 다른 가지를 환불하고 새 경로를 연결한다. 매 조작 뒤 양 무기 세트 연결을 검증했다. 수학적 최소 골드 경로라고 주장하지 않는다.',
      'operations':operations,'refunds':sum(o['action']=='refund' for o in operations),'required_pool':pool,'target_cost':usage(target)}
states=[bridge,*[state(s) for s in SPEC[2:]]]
report['transitions']=[dict(from_stage=i+1,to_stage=i+2,**route(a,b)) for i,(a,b) in enumerate(zip(states,states[1:]))]
report['transition']=report['transitions'][0]
save(HERE/'transition.json',report['transitions'])
README+=['## 52 전환의 패시브 환불','',
 '동봉 transition.json은 공통 패시브를 유지하면서 다른 가지를 환불하고 새 경로를 연결하는 경로다. 매 조작 뒤 연결을 검증했지만 수학적 최소 환불 비용을 보장하지는 않는다. 미덕의 정수·고급 마석학은 유지한다. 실제 골드가 부족하면 즉시 환불하지 말고 기존 유탄 구성으로 재료를 더 모은다.','',
 '게임 파일 4개는 BuildPlanner 폴더에 복사한다. 기존 파일을 삭제할 필요는 없다. 플래너 목록에서 이름이 `아르세리나`로 시작하는 항목을 선택한다.','',
 '검증 범위: 최신 PoB 바이트 대조, 실제 38레벨 캐릭터 대조, 패시브 양 무기 세트 연결, 활성 젬과 보조 연결, 한국어 젬 이름, 플래너 JSON 구조. 전투 성능이나 죽지 않는다는 보장은 이 검증에 포함되지 않는다.']
(HERE/'먼저읽기.md').write_text('\n'.join(README)+'\n',encoding='utf-8')
report['untranslated_current_item_mods']=sorted(UNTRANSLATED)
save(HERE/'generation.json',report)
print(json.dumps({'files':[x['file'] for x in report['planners']],'costs':[x['cost'] for x in report['planners']],
 'bridge_added':len(order),'transition_refunds':report['transition']['refunds'],'untranslated':sorted(UNTRANSLATED)},ensure_ascii=False))
