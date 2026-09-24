"""Korean player-facing notes and explicit per-skill weapon/socket instructions."""
import copy, hashlib, json, re
from pathlib import Path
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
OUT = HERE / 'ready'
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
BASES = {b['Id']: b['Name'] for b in read(REPO / 'data/game_data_poe2/BaseItemTypes.json')}
TRANS = read(REPO / 'data/merged_translations.json')
KO = {r['name']: r['title'].split(' - PoE2DB')[0] for r in read(HERE / 'sources/gem_korean_titles.json')}
assert len(KO) == 52 and all(re.search('[가-힣]', v) for v in KO.values())
ITEMS = TRANS['items']
ITEMS.update({r['name']: r['title'].split(' - PoE2DB')[0] for r in read(HERE / 'sources/item_korean_titles.json')})
filters_before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (OUT/'Filters').glob('*.filter')}

STAT = {
 'Physical Damage': '물리 피해', 'Elemental Damage with Attacks': '공격의 원소 피해',
 'Armour and Evasion': '방어도 및 회피', 'Armour': '방어도', 'Attack Speed': '공격 속도',
 'Block chance': '막기 확률', 'Charges': '최대 충전 수', 'Charges gained': '충전 획득량',
 'Charm Effect Duration': '호신부 효과 지속시간', 'Flask Life Recovery rate': '플라스크 생명력 회복 속도',
 'Life Recovered': '생명력 회복량', 'Light Radius': '시야 반경', 'Mana Regeneration Rate': '마나 재생 속도',
 'Movement Speed': '이동 속도', 'Rarity of Items found': '발견하는 아이템 희귀도',
 'Recovery rate': '회복 속도', 'Spirit': '정신력', 'Amount Recovered': '회복량',
 'Accuracy Rating': '정확도', 'Dexterity': '민첩', 'Intelligence': '지능', 'Strength': '힘',
 'Evasion Rating': '회피', 'Stun Threshold': '기절 한계치', 'maximum Life': '최대 생명력',
 'maximum Mana': '최대 마나', 'Critical Damage Bonus': '치명타 피해 보너스', 'Critical Hit Chance': '치명타 확률',
 'Fire Resistance': '화염 저항', 'Cold Resistance': '냉기 저항', 'Lightning Resistance': '번개 저항', 'Chaos Resistance': '카오스 저항',
}

def mod_ko(s):
    prefix = re.match(r'^(\d+\. )(.*)', s)
    if not prefix: return s
    number, text = prefix.groups()
    patterns = [
      (r'([\d.]+)% increased (.+)', lambda a,b: f'{STAT[b]} {a}% 증가'),
      (r'([+\d.]+)% to (.+)', lambda a,b: f'{STAT[b]} {a}%'),
      (r'([+\d.]+) to (.+)', lambda a,b: f'{STAT[b]} {a}'),
      (r'([\d.]+) Life Regeneration per second', lambda a: f'생명력 초당 {a} 재생'),
      (r'([+\d.]+) to Level of all (Melee|Minion) Skills', lambda a,b: f"모든 {'근접' if b == 'Melee' else '소환수'} 스킬 레벨 {a}"),
      (r'Adds ([\d.]+) to ([\d.]+) (Physical|Fire|Cold|Lightning) [Dd]amage( to Attacks)?', lambda a,b,c,d: f"{'공격 시 ' if d else ''}{dict(Physical='물리',Fire='화염',Cold='냉기',Lightning='번개')[c]} 피해 {a}~{b} 추가"),
      (r'([\d.]+) to ([\d.]+) Physical Thorns damage', lambda a,b: f'물리 가시 피해 {a}~{b}'),
      (r'Gain ([\d.]+) Life per Enemy Hit with Attacks', lambda a: f'공격으로 적 명중 시 생명력 {a} 획득'),
      (r'Gains ([\d.]+) Charges per Second', lambda a: f'매초 충전 {a} 획득'),
      (r'Grants ([\d.]+)% of Life Recovery to Minions', lambda a: f'생명력 회복량의 {a}%를 소환수에게도 적용'),
      (r'([\d.]+)% additional Physical Damage Reduction', lambda a: f'추가 물리 피해 감소 {a}%'),
      (r'([+\d.]+)% of Armour also applies to Elemental Damage', lambda a: f'방어도의 {a}%가 원소 피해에도 적용'),
      (r'([\d.]+)% of Recovery applied Instantly', lambda a: f'회복량의 {a}% 즉시 적용'),
      (r'([\d.]+)% reduced Charges per use', lambda a: f'사용 시 소모 충전 {a}% 감소'),
      (r'Removes ([\d.]+)% of Life Recovered from Mana when used', lambda a: f'사용 시 생명력 회복량의 {a}%만큼 마나 제거'),
      (r'Allies in your Presence have ([\d.]+)% increased Cast Speed', lambda a: f'자신의 존재 범위 내 동료 시전 속도 {a}% 증가'),
    ]
    # Specific "skill levels" must precede the generic "to X" template.
    patterns.insert(0, patterns.pop(4))
    for pattern, func in patterns:
        match = re.fullmatch(pattern, text)
        if match:
            try: return number + func(*match.groups())
            except KeyError: continue
    raise AssertionError(('untranslated item mod', s))

def display(gid):
    en = BASES[gid]
    return f'{KO[en]} ({en})'

def slot(d, name):
    found = next((i for i in d['inventory_slots'] if i['inventory_id'] == name), None)
    if found is None:
        found = {'inventory_id': name, 'slot_x': 0, 'slot_y': 0, 'level_interval': [1,100]}
        d['inventory_slots'].append(found)
    return found

def append(d, inv, text):
    s = slot(d, inv)
    s['additional_text'] = s.get('additional_text', '') + '\n\n' + text

def group_set(name, stage, purity_index=0):
    if name == 'Ancestral Spirits': return '전직 자동 부여'
    if name == 'Harbinger of Madness': return '세트2 무기 자동 부여'
    if name == 'Purity of Fire': return '세트1' if purity_index == 0 else '세트2'
    if name in ('Mace Strike', 'Boneshatter', 'Shockwave Totem', 'Ancestral Warrior Totem'): return '세트2'
    return '세트1'

WEAPONS = {
 'early': ('한손 철퇴 + 방어도 방패', '양손 철퇴'),
 'shared': ('물리 피해 좋은 한손 철퇴 + 방어도 방패', '같은 한손 철퇴와 방패를 양 세트 공유'),
 'cry': ('근접 스킬 레벨을 높이는 한손 철퇴 + 방어도 방패', '물리 피해 좋은 한손 철퇴 + 공유 방패'),
 'final': ('정신력 셉터 + 방어도 방패', '물리 한손 철퇴 + 정신력 셉터'),
}
GATES = {
 1:'아직 토템 운용 전. 양손 철퇴가 없으면 한손 철퇴로 시작하고, 확보한 뒤 아래 세트 설정을 적용한다.',
 2:'충격파 토템과 기본 보조 확보. 양손 철퇴를 세트2에 장착하고 뼈 박살/토템을 세트2로 지정한다.',
 3:'응답받은 부름 1차 전직과 충격파 토템 링크 확보. 한손 철퇴+방패를 공유하는 권장 구성으로 전환한다.',
 4:'대장간 망치 제작과 요구 능력치 충족. 요철 지대 I 보조를 화산 균열에서 대장간 망치로 옮긴다.',
 5:'전쟁 소집자의 고함 2차 전직. 아직 타락시키는 비명이 없으면 충격파 토템 운영을 유지한다.',
 6:'보강하는 함성 + 타락시키는 비명 I + 방어도 방패 + 2차 전직 확보. 기존 지옥불 함성을 보강하는 함성으로 교체한다.',
 7:'함성에 효율 II를 추가할 소켓과 회복을 확보. 선대의 전사 토템/혈마법 전환 전의 캠페인 유지 구성.',
 8:'07의 일반 포인트 67점을 찍고도 포인트가 남을 때. 추가 방어/재생 14점은 동봉 패시브전환.md 순서대로 필요한 만큼만.',
 9:'양 무기 세트의 예약 후 정신력, 지속 회복, 선대의 전사 토템+지면 분쇄, 파콰테의 맹약을 모두 준비. 원본 전체 트리는 일반 97점/전직 6점의 목표이며 65레벨 전환표가 아님.',
}
ROTATIONS = {
 'early':'잡몹: 몰려오는 강타(1)로 기절 준비 → 뼈 박살(2) → 방패 세트1 복귀. 토템 도입 후 보스: 토템(2) 설치 → 지진(1)으로 요철 지대 → 이동. 지옥불 함성은 단일 대상 보조.',
 'shared':'토템(2) 설치 → 지진(1)으로 요철 지대 → 이동. 망치가 있으면 안전할 때 대장간 망치(1) → 지옥불 함성(1)으로 폭발. 충전이 없으면 요철 지대 I 보조는 지대를 만들지 못하므로 지진을 사용. 공명하는 방패는 필요할 때만.',
 'cry':'잡몹: 보강하는 함성(1) 1회 → 이동 → 남은 적 확인. 희귀/보스: 충격파 토템(2) 설치 → 보강하는 함성(1)으로 복귀 → 지진/망치는 여유가 있을 때 보조. 함성을 무조건 제자리 연타하지 않는다.',
 'final':'선대의 전사 토템(2) 설치 → 보강하는 함성(1)으로 방패 세트 복귀 → 토템의 지면 분쇄 가시를 함성으로 폭발 → 이동. 지진 함성(1)은 격노/보조 폭발용. 파콰테 반복 사용/발동의 생명력 비용을 감당 못 하면 이전 함성 유지 구성으로 돌아간다.',
}
all_doc = ['# 무기 세트와 젬을 꽂는 위치', '',
 '이 표는 각 플래너 안의 무기 슬롯 설명에도 들어 있다. **왼쪽 큰 스킬 젬의 보조 소켓에 오른쪽 젬들을 꽂는다.** 무기 아이템의 룬 소켓에 넣는 것이 아니다.', '',
 'G → 각 스킬의 상세 설정 → 사용할 무기 세트 I/II를 선택한다. 세트1 전용은 I만, 세트2 전용은 II만 선택한다. 플래너 파일은 체크박스 설정을 자동 적용하지 않는다.', '',
 '초반 02의 세트 배정은 제작자 가이드에서 확인했다. 03 이후 실측 API에는 스킬별 G 체크박스가 없으므로, 실제 장비·패시브·젬 구성을 바탕으로 정한 **Pathcraft 권장 배정**이다. 제작자와 모든 버튼이 동일하다고 주장하지 않는다.', '',
 '01 시작 직후 양손 철퇴가 없으면 한손 철퇴로 기본 공격/뼈 박살을 사용한다. 양손 철퇴를 구한 뒤 01~02의 세트2 배정을 적용한다. 03 이후에도 계속 양손을 써야 하는 빌드가 아니다.']
checks = []
for path in sorted((OUT/'BuildPlanner').glob('*.build')):
    d = read(path); before = copy.deepcopy(d); stage = int(d['name'][:2])
    family = 'early' if stage <= 2 else 'shared' if stage <= 5 else 'cry' if stage <= 8 else 'final'
    # Translate every original item stat, and replace old operation prose completely.
    for inv in d['inventory_slots']:
        text = inv.get('additional_text', '')
        if '[출처 장비 예시 — 같은 물건을 살 필요 없음]\n' in text:
            text = text.split('[출처 장비 예시 — 같은 물건을 살 필요 없음]\n', 1)[1]
        result = []
        for line in text.splitlines():
            if re.match(r'^\d+\. ', line): result.append(mod_ko(line))
            elif line in ITEMS: result.append(f'{ITEMS[line]} ({line})')
            else: result.append(line)
        if result: inv['additional_text'] = '\n'.join(result)
    weapon1, weapon2 = WEAPONS[family]
    append(d, 'Weapon1', f'[세트1 무기]\n{weapon1}\n아래 세트1 스킬을 G에서 I에만 체크. 세트2 공격 뒤 방패가 필요하면 방패 들기 또는 세트1 함성으로 복귀.')
    append(d, 'Weapon2', f'[세트2 무기]\n{weapon2}\n아래 세트2 스킬을 G에서 II에만 체크. 설치/공격 뒤 위험 구간에서는 세트1 복귀.')
    if family == 'shared':
        append(d, 'Offhand2', '[공유 장비 설정]\n인벤토리에서 무기 세트 아이콘을 우클릭해 한손 철퇴와 방패를 양 세트에 공유. 같은 아이템을 두 벌 살 필요 없음. 이 배포본은 03 이후 양손 철퇴를 필수로 잡지 않음.')
    if family == 'cry':
        append(d, 'Offhand2', '[방패 공유]\n세트1의 방어도 방패를 양 세트에 공유. 두 한손 철퇴는 각자 장착. 함성은 세트1, 충격파 토템은 세트2.')
    if family == 'final':
        append(d, 'Offhand2', '[최종 세트2]\n정신력 셉터 자리. 양손 철퇴를 끼우면 이 셉터를 함께 쓸 수 없으므로 이 단계의 정신력 설계가 깨짐. 원본 철퇴는 Sadist\'s Mercy이며 실제 장비 예시. 대체 철퇴는 물리 피해·공격 속도와 양 세트 정신력 충족을 확인.')
    append(d, 'BodyArmour1', f'[전환 조건]\n{GATES[stage]}\n\n[스킬 운영]\n{ROTATIONS[family]}\n\n[하드코어 진행]\n65레벨 이후라도 캠페인 중이면 01-Campaign 필터 유지. 장비는 최대 생명력·현재 지역 저항·방어도, 장화 이동 속도, 생명력 플라스크 우선. 출처 장비의 낮은 방어 수치를 그대로 복사하지 않는다.')
    append(d, 'Gloves1', '[보조 젬을 넣는 곳]\nG 스킬창에서 해당 큰 스킬 젬을 선택하고 그 스킬의 작은 보조 소켓에 연결. 아래 각 스킬의 연결 목록을 그대로 따른다. 무기 룬 소켓이 아니다.\n선대의 전사 토템 안의 지면 분쇄는 예외적으로 연결하는 액티브 젬이다. 별도 지면 분쇄 스킬칸만 만들면 토템 연결이 완성되지 않는다.\n보조 소켓이 부족하면 주얼러 오브로 확장. 무조건 오른쪽부터 모든 보조를 갖출 필요는 없으며 주력 토템/함성의 핵심 보조부터 확보.')
    set_notes = {'세트1': [], '세트2': [], '전직 자동 부여': [], '세트2 무기 자동 부여': []}
    rows = []; purity_index = 0
    for skill in d['skills']:
        en = BASES[skill['id']]
        group = group_set(en, stage, purity_index)
        if en == 'Purity of Fire': purity_index += 1
        linked = ' + '.join(display(s['id']) for s in skill.get('support_skills', [])) or '연결 보조 없음'
        hint = ' [토템 안에 연결하는 액티브]' if en == 'Ancestral Warrior Totem' else ''
        set_notes[group].append(f'{display(skill["id"])} → {linked}{hint}')
        rows.append(f'| {group} | {display(skill["id"])} | {linked} |')
    append(d, 'Weapon1', '[세트1 스킬과 그 안에 꽂을 보조]\n'+'\n'.join(set_notes['세트1']))
    append(d, 'Weapon2', '[세트2 스킬과 그 안에 꽂을 보조]\n'+'\n'.join(set_notes['세트2']))
    if set_notes['전직 자동 부여'] or set_notes['세트2 무기 자동 부여']:
        append(d, 'Helm1', '[자동으로 부여되는 스킬 — 따로 제작하지 않음]\n'+'\n'.join(set_notes['전직 자동 부여'] + set_notes['세트2 무기 자동 부여']))
    if stage == 9:
        append(d, 'Amulet1', '[정신력/회복 확인]\n토템 예약 전, 버프를 켠 상태의 남은 정신력이 양 세트 모두 토템 수 × 75 이상이어야 함. 4기라면 각 세트 300 이상. 셉터 두 개의 불의 순수함은 각각 다른 스킬칸이므로 활력 II/식인 II/따뜻한 피는 세트1, 활력 I/정밀함 II는 세트2의 불의 순수함에 연결.\n혈마법은 마나 비용을 생명력으로 바꿈. 파콰테 연타의 추가 생명력 비용까지 지속 회복으로 감당되는지 먼저 확인.')
    all_doc += ['', '## '+d['name'], '', GATES[stage], '', f'- 세트1: {weapon1}\n- 세트2: {weapon2}', '', ROTATIONS[family], '', '| G 무기 설정 | 큰 스킬 젬 | 그 스킬에 연결할 젬 |', '|---|---|---|'] + rows
    assert d['passives'] == before['passives'] and d['skills'] == before['skills']
    for inv in d['inventory_slots']:
        for line in inv.get('additional_text', '').splitlines():
            if re.match(r'^\d+\. ', line): assert re.search('[가-힣]', line), line
    path.write_text(json.dumps(d, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    checks.append({'file': path.name, 'original_passives_and_gem_paths_unchanged': True, 'korean_equipment_stats': True, 'weapon_sets_and_all_socket_groups_documented': True, 'maximum_note_characters': max(len(i.get('additional_text','')) for i in d['inventory_slots'])})
assert filters_before == {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (OUT/'Filters').glob('*.filter')}
(OUT/'무기세트와젬연결.md').write_text('\n'.join(all_doc)+'\n', encoding='utf-8')
(HERE/'validation_korean.json').write_text(json.dumps({'planners':checks, 'filters_unchanged_since_sweep':filters_before, 'korean_gem_names_checked':len(KO)}, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(f'Korean notes and weapon/socket instructions: {len(checks)} planners; {len(KO)} verified gem names.')
