"""One assignment table for native planner hints and the weapon-set guide."""
from pathlib import Path
import collections
import json
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASES = {x['Id']: x['Name'] for x in json.loads((ROOT / 'data/game_data_poe2/BaseItemTypes.json').read_text(encoding='utf-8-sig'))}
TREE = {x['stringId']: x for x in json.loads((HERE.parent / 'skadoosh_hc_2026-09-07/sources/tree_0_5.json').read_text(encoding='utf-8'))['nodes'].values() if 'stringId' in x}
NUM = {x['skill']: key for key, x in TREE.items()}
ADJ = collections.defaultdict(set)
for key, node in TREE.items():
    for c in node.get('connections', []):
        if c['id'] in NUM:
            other = NUM[c['id']]
            ADJ[key].add(other)
            ADJ[other].add(key)


def assignments(build):
    rows = []
    purity = 0
    for index, skill in enumerate(build['skills']):
        name = BASES[skill['id']]
        if name in ('Ancestral Spirits', 'Harbinger of Madness'):
            target = 'automatic'
        elif name == 'Earthshatter':
            target = 'inside_totem'
        elif name == 'Purity of Fire':
            purity += 1
            assert purity <= 2
            target = purity
        elif name in ('Shockwave Totem', 'Ancestral Warrior Totem'):
            target = 2
        else:
            target = 1
        title = re.sub(r'<[^>]+>|[{}]', '', skill['additional_text'].splitlines()[0]).split(' · ')[0]
        rows.append({'index': index, 'id': skill['id'], 'english_name': name, 'display_name': title, 'target': target})
    return rows


def profile(stage):
    if stage == 1:
        return {'I': '한손 철퇴 + 방어도 방패 · 근접 피해와 기절', 'II': '토템 도입 전에는 별도 사용 스킬 없음',
                'rotation': '몰려오는 강타(I) → 기절 준비 표시 → 뼈 박살(I). 02에서 토템을 추가하면 II를 설정한다.'}
    if stage <= 3:
        return {'I': '한손 철퇴 + 방어도 방패 · 근접·지진·보조 공격', 'II': '한손 철퇴 + 공유 방패 · 충격파 토템',
                'rotation': '충격파 토템은 II만, 지진·화산·근접·방패 스킬은 I만 체크. 토템 사용 뒤 I 스킬로 복귀. 뼈 박살은 기절 준비 표시가 뜰 때 사용한다.'}
    if stage == 4:
        return {'I': '한손 철퇴 + 방어도 방패 · 보강하는 함성', 'II': '한손 철퇴 + 공유 방패 · 충격파 토템',
                'rotation': '충격파 토템(II) → 보강하는 함성(I). 지진·망치·방패 스킬도 I에 지정한다.'}
    return {'I': '성소 셉터 + 방어도 방패 · 함성', 'II': '한손 철퇴 + 성소 셉터 · 선대의 전사 토템',
            'rotation': '전사 토템(II) → 함성(I). 지면 분쇄는 전사 토템 내부에 넣는다. 불의 순수함 두 항목은 각각의 셉터 세트에 지정한다.'}


def validate_weapon_sets(build):
    state = {p['id']: p.get('weapon_set', 0) for p in build['passives']}
    assert len(state) == len(build['passives']) and set(state) <= set(TREE)
    assert set(state.values()) <= {0, 1, 2}
    def connected(nodes, root):
        nodes = set(nodes) | {root}
        seen = {root}
        front = {root}
        while front:
            front = set().union(*(ADJ[n] for n in front)) & nodes - seen
            seen |= front
        return seen == nodes
    for weapon_set in (1, 2):
        active = {key for key, value in state.items() if value in (0, weapon_set)}
        regular = {key for key in active if not TREE[key].get('ascendancyName')}
        assert connected(regular, 'marauder594')
        assert connected(active - regular, 'AscendancyWarrior2Start')
    for skill in build['skills']:
        # GGG supports weapon_set on passives, not on BuildSkill.
        assert set(skill) <= {'id', 'level_interval', 'additional_text', 'support_skills'}
    rows = assignments(build)
    assert all(x['target'] == 2 for x in rows if x['english_name'] in ('Shockwave Totem', 'Ancestral Warrior Totem'))
    assert all(x['target'] == 1 for x in rows if x['english_name'] in ('Earthquake', 'Boneshatter', 'Raise Shield', 'Shield Block', 'Infernal Cry', 'Seismic Cry'))
    return {'sets': [sum(value == n for value in state.values()) for n in (1, 2)], 'both_sets_connected': True, 'skills': rows}


def apply_weapon_sets(build, stage):
    p = profile(stage)
    counts = [sum(n.get('weapon_set', 0) == w for n in build['passives']) for w in (1, 2)]
    prefix = ('무기 세트 설정\nI: ' + p['I'] + '\nII: ' + p['II'] + '\n' + p['rotation'] +
              f'\n특화 목표 I {counts[0]}점 / II {counts[1]}점. 보유 특화 포인트 안에서 배정한다.\n\n')
    build['description'] = prefix + build['description']
    for row in assignments(build):
        skill = build['skills'][row['index']]
        target = row['target']
        if target == 'automatic':
            note = '자동 부여 효과. 별도 무기 세트 체크 대상으로 만들지 않는다.'
        elif target == 'inside_totem':
            note = '전사 토템 내부 공격. 무기 세트 체크는 선대의 전사 토템을 II로 지정한다.'
        else:
            label = 'I' if target == 1 else 'II'
            note = f'G 무기 세트 체크: {label}만. 플래너 파일이 실제 체크 상태를 자동 변경하지는 않는다.'
        lines = skill['additional_text'].splitlines()
        lines = [line for line in lines if not line.startswith('G 무기 세트에서 ')]
        lines.insert(1, note)
        skill['additional_text'] = '\n'.join(lines)
    for slot in build['inventory_slots']:
        inv = slot['inventory_id']
        if inv in ('Weapon1', 'Weapon2'):
            label = 'I' if inv == 'Weapon1' else 'II'
            slot['additional_text'] = f'<b>{{무기 세트 {label} 설정}}\n{p[label]}\n{p["rotation"]}\n\n' + slot['additional_text']
            if stage == 1 and inv == 'Weapon2':
                slot['additional_text'] = '<b>{세트 II · 토템 도입 후 설정}\n01에서는 별도 사용 스킬·특화 패시브가 없다. 02에서 충격파 토템을 배우면 II에 지정한다.\n현재는 한손 철퇴·방패 I로 기절 연계와 근접 피해를 확보한다.'
    for node in build['passives']:
        target = node.get('weapon_set', 0)
        if target:
            label = 'I' if target == 1 else 'II'
            old = node.get('additional_text', '')
            detail = ' / '.join(TREE[node['id']]['stats']) if TREE[node['id']].get('isNotable') else ''
            node['additional_text'] = f'무기 세트 {label} 특화에 배정. 해당 세트로 스킬을 사용한다.'
            if old:
                node['additional_text'] += '\n' + old
            elif detail:
                node['additional_text'] += '\n' + detail
    return validate_weapon_sets(build)


def write_weapon_set_guide(builds):
    guide = ['# 무기 세트 I·II 설정', '',
             '초반은 I의 근접·지진·방패와 II의 토템 화력을 나눠 사용한다. 같은 한손 철퇴·방패 구성을 써도 특화 패시브와 스킬 체크를 나누는 의미가 있다.', '',
             '**플래너의 특화 패시브 배정은 파일에 들어 있다. 실제 캐릭터의 스킬 I·II 체크와 장비 장착은 게임에서 설정해야 한다.** 파일 생성·설치가 실제 캐릭터 설정을 변경하지는 않는다.', '',
             '02~07의 스킬 교체와 잡몹·보스별 운영은 [스킬 로테이션](타락함성_토템_스킬로테이션.md)을 함께 본다.', '',
             '스킬 체크는 G에서 해당 스킬의 무기 세트 설정을 확인한다. 아래 표의 I만/II만에 맞춘다. 사용할 스킬의 장비·능력치·정신력 조건을 해당 세트에서 충족해야 한다.', '']
    records = []
    for build in builds:
        stage = int(build['name'][:2])
        p = profile(stage)
        result = validate_weapon_sets(build)
        guide += ['## ' + build['name'], '', '**I:** ' + p['I'] + '  ', '**II:** ' + p['II'], '', p['rotation'], '',
                  f'특화 목표: I {result["sets"][0]}점 / II {result["sets"][1]}점. 현재 보유한 특화 포인트만 사용한다.', '',
                  '| 스킬 | 무기 세트 체크 |', '| --- | --- |']
        for row in result['skills']:
            target = row['target']
            text = {1: 'I만', 2: 'II만', 'automatic': '자동 부여', 'inside_totem': '전사 토템 내부 · 별도 수동 사용 제외'}[target]
            guide.append('| ' + row['display_name'] + ' | ' + text + ' |')
        for target in (1, 2):
            notable = [TREE[n['id']]['name'] for n in build['passives'] if n.get('weapon_set') == target and TREE[n['id']].get('isNotable')]
            if notable:
                guide += ['', ('I' if target == 1 else 'II') + ' 특화 주요 노드: ' + ', '.join(notable) + '.']
        guide += ['']
        records.append({'stage': stage, 'name': build['name'], 'loadout': p, **result})
    guide += ['## 설정 후 확인', '',
              '장비·젬·포인트를 맞춘 뒤 낮은 지역에서 토템을 한 번 쓰고 II가 선택되는지, 지진이나 함성을 쓰면 I로 돌아오는지 확인한다. 특화 II의 토템 한도와 설치 가능 상태도 확인한다. 무기가 하나뿐인 시작 구간은 게임의 공유 상태를 먼저 확인하며, 플래너 파일이 무기 두 개를 만들어 주지는 않는다.', '',
              '05 이후에는 버프를 켜고 토템 설치 전 남는 정신력이 양 세트 각각 300 이상이어야 토템 4기 목표를 유지한다. 지면 분쇄는 선대의 전사 토템 안에 넣는다.', '',
              '[GGG 공식 형식](https://www.pathofexile.com/developer/docs/game#buildplanner)은 패시브의 weapon_set과 장비 슬롯을 지원한다. 스킬의 실제 I·II 체크를 자동 설정하는 필드는 없어 게임 내 설정과 구분했다.', '']
    (HERE / '무기세트_설정표.md').write_text('\n'.join(guide), encoding='utf-8')
    (HERE / 'weapon_set_mapping.json').write_text(json.dumps({'character_configuration_applied': False, 'reason': 'Planner generation and installation do not change character equipment or skill weapon-set checkboxes.', 'stages': records}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
