"""Generate this delivery only; existing project/game files are read-only inputs."""
from __future__ import annotations
import base64, collections, copy, hashlib, importlib.util, io, json, re, sys, zlib
import contextlib, xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
SRC = HERE / 'sources'
OUT = HERE / 'ready'
for folder in ('BuildPlanner', 'Filters'):
    (OUT / folder).mkdir(parents=True, exist_ok=True)

def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))

def write(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, REPO / 'scripts' / filename)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod

TREE = read(SRC / 'tree_0_5.json')
NODES = {int(k): n for k, n in TREE['nodes'].items() if 'stringId' in n}
BY_ID = {n['stringId']: k for k, n in NODES.items()}
ADJ = collections.defaultdict(set)
for k, node in NODES.items():
    for edge in node.get('connections', []):
        ADJ[k].add(edge['id'])
        ADJ[edge['id']].add(k)
BASES = read(REPO / 'data/game_data_poe2/BaseItemTypes.json')
GEMS = {BASES[g['BaseItemType']]['Id']: (BASES[g['BaseItemType']]['Name'], max(1, g['MinLevelReq']))
        for g in read(REPO / 'data/game_data_poe2/SkillGems.json')}
BASE_IDS = {b['Id'] for b in BASES}
PLANNER = module('delivery_planner_base', 'build_poe2_planner_files.py')
LINK = 'https://poe.ninja/poe2/builds/forbiddenriteshc/character/ITheCon-2183/SkadooshShoutedHard'
BUILDS, SOURCES, REPORT = [], [], {'planner_checks': [], 'filter_checks': []}

def gem_entry(gid):
    assert gid in BASE_IDS, ('unknown gem', gid)
    return {'id': gid, 'level_interval': [GEMS.get(gid, ('', 1))[1], 100]}

def clean_skills(root):
    """Preserve explicit duplicate grants AND nested active gems (AWT Earthshatter)."""
    groups = []
    for group in root.findall('.//Skill'):
        ids = [g.get('gemId') for g in group.findall('Gem') if g.get('gemId')]
        if not ids:
            continue
        groups.append((group.get('source', ''), ids))
    explicit_ids = {ids[0] for source, ids in groups if not source}
    entries = []
    for source, ids in groups:
        if source and ids[0] in explicit_ids:
            continue
        entry = gem_entry(ids[0])
        if len(ids) > 1:
            entry['support_skills'] = [gem_entry(gid) for gid in ids[1:]]
        entries.append(entry)
    return entries

def canonical_passives(entries):
    common = {e['id'] for e in entries if not e.get('weapon_set')}
    seen, result = set(), []
    for e in entries:
        key = (e['id'], e.get('weapon_set', 0))
        if key in seen or key[1] and key[0] in common:
            continue
        seen.add(key)
        result.append(copy.deepcopy(e))
    return result

def note(build, slot, text):
    target = next((i for i in build['inventory_slots'] if i['inventory_id'] == slot), None)
    if target is None:
        target = {'inventory_id': slot, 'slot_x': 0, 'slot_y': 0, 'level_interval': [1, 100]}
        build['inventory_slots'].append(target)
    target['additional_text'] = text + '\n\n[출처 장비 예시 — 같은 물건을 살 필요 없음]\n' + target.get('additional_text', target.get('unique_name', ''))
    target['level_interval'] = [1, 100]

def add_build(build, title, source, gate, operation):
    build['name'] = title
    build['author'] = 'Skadoosh / Pathcraft'
    build['passives'] = canonical_passives(build['passives'])
    note(build, 'Weapon1', f'{title}\n진행 기준: {gate}\n캐릭터 레벨로 다음 파일로 넘어가지 않음. 상세 운영은 동봉 시작안내.md.\n{operation}')
    note(build, 'BodyArmour1', 'HC 장비 우선: 최대 생명력·현재 지역 원소 저항·방어도, 장화 이동 속도, 최신 생명력 플라스크.\n스냅샷의 낮은 방어 옵션을 그대로 복사하지 말 것. 장비 예시는 구매 필수 목록이 아님.\n캠페인 중이면 캐릭터 65+도 01-Campaign 필터 유지. 전직/정신력/회복 준비를 먼저 확인.')
    for skill in build['skills']:
        for entry in [skill] + skill.get('support_skills', []):
            assert entry['id'] in BASE_IDS, entry['id']
            entry['level_interval'] = gem_entry(entry['id'])['level_interval']
    assert len(title) <= 40
    BUILDS.append(build)
    SOURCES.append({'file': title + '.build', 'source': source, 'gate': gate})

EARLY = [('WB 가이드 Act1 - Skadoosh.build', '01 시작-근접 기초', '충격파 토템 운용 전',
          'Rolling Slam으로 기절 준비 → Boneshatter. 위험한 공격에는 방패/회피와 이동을 우선.'),
         ('WB 가이드 Act1말-Act2 - Skadoosh.build', '02 초반-토템 도입', '충격파 토템과 기본 보조 확보, 1차 전직 전후',
          'Shockwave Totem → Earthquake 요철 지대 → 이동. 기절 준비된 적만 Boneshatter. 원 가이드의 1손+방패 / 2손철퇴 무기 세트 예시.')]
for file, title, gate, op in EARLY:
    build = read(REPO / 'build_planner' / file)
    add_build(build, title, 'Skadoosh 0.4 초반 가이드의 1–10 / 11–20 참고안; 0.5 트리 ID와 젬 ID 검증, 관측 캐릭터 기록 아님', gate, op)

STAGES = [
    ('ninja_hour18_lv24.json', '03 1차전직-충격파 토템', 'Answered Call 1차 전직, 토템 3링크 준비',
     '세트2 Shockwave Totem 설치 → 세트1 Earthquake → 이동/필요시 Boneshatter. 지진이 요철 지대를 만들고 토템이 터뜨림.'),
    ('lv34_0906_0320.json', '04 캠페인-대장간 망치 추가', 'Forge Hammer 제작과 요구 능력치 충족',
     '토템 → Earthquake → 여유가 있을 때 Forge Hammer → Infernal Cry로 망치 폭발. Jagged Ground I은 인내 충전 소비가 있어야 지대를 만듦.'),
    ('lv43_0906_0523.json', '05 2차전직-함성 전환 준비', 'Warcaller\'s Bellow 2차 전직, 아직 타락시키는 비명 전',
     '충격파 토템 운영 유지. 함성 쿨다운 무시를 얻어도 Corrupting Cry 보조 없이는 함성이 주력 지속 피해가 되지 않음.'),
    ('lv46_0906_0634.json', '06 타락 함성-첫 전환', '보강하는 함성 + Corrupting Cry I + 방어도 방패 + 2차 전직 확보',
     '세트1 Fortifying Cry로 타락한 피 부여 → 이동. 단단한 적에게 세트2 Shockwave Totem 설치 → 세트1 복귀. Infernal Cry를 주력으로 쓰지 않음.'),
    ('lv52_0906_0744.json', '07 타락 함성-캠페인 유지', '함성 비용 보조·재생 보강, AWT 전환 준비 중',
     '06과 같은 전투 방식. Efficiency II로 비용 완화. 레벨이 65를 넘어도 회복·정신력이 부족하면 이 구조 유지. 선대의 유대/혈마법 없음.'),
    ('ninja_latest_74.json', '09 준비완료-AWT와 파콰테', '양 세트의 정신력, 지속 회복, AWT+Earthshatter, Paquate\'s Pact와 무기 세트 준비 완료',
     '세트2 AWT(Earthshatter 내장) 설치 → 세트1 방패로 복귀 → Fortifying Cry로 가시 폭발/타락한 피 → 이동. Seismic Cry는 보조. 파콰테 연타는 생명력 비용 확인.')
]
RAW = {}
for filename, title, gate, op in STAGES:
    model = read(SRC / filename)
    RAW[model['level']] = model
    encoded = model['pathOfBuildingExport']
    xml = zlib.decompress(base64.urlsafe_b64decode(encoded + '=' * (-len(encoded) % 4))).decode()
    root = ET.fromstring(xml)
    spec = PLANNER.parse_specs(xml)[0]
    # PoB includes the implicit class start; the native planner / ninja selections do not.
    spec['nodes'] = [k for k in spec['nodes'] if not NODES[k].get('classesStart')]
    inv = PLANNER.inventory_slots(xml, PLANNER.parse_items(xml), PLANNER.base_names(), [])
    build = PLANNER.build_file(spec, clean_skills(root), {k: n['stringId'] for k, n in NODES.items()},
                               'Skadoosh / Pathcraft', LINK, title, inv, 'Warrior2')
    expected = {(NODES[k]['stringId'], 0) for k in model['passiveSelection']}
    for weapon in (1, 2):
        expected |= {(NODES[k]['stringId'], weapon) for k in model[f'passiveSelectionSet{weapon}']}
    actual = {(e['id'], e.get('weapon_set', 0)) for e in build['passives']}
    assert actual == expected, (filename, 'extra', actual-expected, 'missing', expected-actual)
    add_build(build, title, f"{filename}; 실측 Lv{model['level']}; updatedUtc={model.get('updatedUtc', '보존본에 필드 없음; 파일명은 수집 시각')}; 레벨은 출처 시점이며 적용 상한 아님", gate, op)
    REPORT['planner_checks'].append({'file': title, 'raw_nodes_equal': True, 'explicit_skill_groups': len(build['skills'])})

# A bounded HC overlevelling extension: keep the observed Lv52 structure and add
# nearby defensive paths. First two targets also occur in the latest creator tree.
bridge = copy.deepcopy(BUILDS[-2])
bridge['inventory_slots'] = readjust_inv = PLANNER.inventory_slots(
    zlib.decompress(base64.urlsafe_b64decode(RAW[52]['pathOfBuildingExport'] + '=' * (-len(RAW[52]['pathOfBuildingExport']) % 4))).decode(),
    PLANNER.parse_items(zlib.decompress(base64.urlsafe_b64decode(RAW[52]['pathOfBuildingExport'] + '=' * (-len(RAW[52]['pathOfBuildingExport']) % 4))).decode()), PLANNER.base_names(), [])
present = set(RAW[52]['passiveSelection'])
allowed = set(NODES) - set(RAW[52]['passiveSelectionSet1']) - set(RAW[52]['passiveSelectionSet2']) - {k for k, n in NODES.items() if n.get('isKeystone') or n.get('ascendancyName') or n.get('classesStart')}
added = []
for goal_name in ('Tempered Defences', 'Battle-hardened', "Titan's Determination", 'Unbending', 'Necromantic Ward'):
    goal = next(k for k in allowed if NODES[k]['name'] == goal_name)
    queue = collections.deque([(n, []) for n in sorted(present & allowed)])
    seen = set(present & allowed)
    path = None
    while queue:
        n, route = queue.popleft()
        if n == goal:
            path = route
            break
        for nxt in sorted(ADJ[n] & allowed):
            if nxt not in seen:
                seen.add(nxt); queue.append((nxt, route + [nxt]))
    assert path is not None, goal_name
    for n in path:
        if n not in present:
            added.append(n); present.add(n)
            bridge['passives'].append({'id': NODES[n]['stringId']})
add_build(bridge, '08 함성 유지-추가 방어 투자', 'Pathcraft 제안: 실측 Lv52 구조에 0.5 트리의 인접 방어/재생 경로 추가. Tempered Defences와 Battle-hardened는 최신 Lv74에도 있음. 제작자의 해당 레벨 실측 기록이 아님',
          '캠페인 과레벨링으로 07 트리를 찍고도 포인트가 남음; AWT 미준비',
          '스킬/무기/자원 운영은 07 그대로. 추가점수 순서는 패시브전환.md의 08 전용 경로. 선대의 유대와 혈마법 없이 함성 유지.')
BUILDS[-1], BUILDS[-2] = BUILDS[-2], BUILDS[-1]
SOURCES[-1], SOURCES[-2] = SOURCES[-2], SOURCES[-1]
REPORT['extension'] = [{'id': NODES[k]['stringId'], 'name': NODES[k]['name'], 'stats': NODES[k]['stats']} for k in added]

def components(nodes):
    left, result = set(nodes), []
    while left:
        component, todo = set(), [min(left)]
        while todo:
            n = todo.pop()
            if n in component:
                continue
            component.add(n); todo.extend((ADJ[n] & nodes) - component)
        left -= component; result.append(component)
    return result

for build, source in zip(BUILDS, SOURCES):
    assert set(build) == {'author', 'link', 'ascendancy', 'inventory_slots', 'name', 'passives', 'skills'}
    assert build['ascendancy'] == 'Warrior2'
    counts = []
    for weapon in (1, 2):
        selected = {BY_ID[p['id']] for p in build['passives'] if p.get('weapon_set', weapon) == weapon}
        normal = {k for k in selected if not NODES[k].get('ascendancyName')}
        asc = selected - normal
        assert len(components(normal)) == 1, (build['name'], weapon, components(normal))
        assert len(components(asc)) <= 1
        assert any(k in normal for k in (46325, 38646)), (build['name'], 'missing Warrior start route')
        counts.append(len(normal))
    source['ordinary_points_by_weapon_set'] = counts
    source['ascendancy_points'] = sum(bool(NODES[BY_ID[p['id']]].get('ascendancyName')) and not NODES[BY_ID[p['id']]].get('isAscendancyStart') for p in build['passives'])
    write(OUT / 'BuildPlanner' / (build['name'] + '.build'), build)
latest = BUILDS[-1]
awt = next(s for s in latest['skills'] if s['id'].endswith('SkillGemAncestralWarriorTotem'))
assert any(g['id'].endswith('SkillGemEarthshatter') for g in awt['support_skills'])
assert sum(s['id'].endswith('SkillGemPurityOfFire') for s in latest['skills']) == 2
assert not any(NODES[BY_ID[p['id']]].get('isKeystone') for p in BUILDS[-2]['passives'])
write(HERE / 'planner_sources.json', SOURCES)

lines = ['# 패시브 전환과 추가 포인트', '',
         '레벨표가 아니라 각 파일의 **목표 트리**다. 일반 포인트와 무기 세트 포인트는 퀘스트 진행에 따라 달라진다. 전직 포인트는 따로 계산한다.', '',
         '아래 전환 차이는 원본들의 차집합이며, 한꺼번에 환불하라는 실행 순서가 아니다. 연결 경로를 남겨 두고 마을에서 바꾼다. 06→07도 공통/무기 세트 사이 이동이 있으므로 개수를 먼저 확인한다.', '',
         '| 파일 | 일반 포인트 세트1 / 세트2 | 전직 |', '|---|---:|---:|']
for s in SOURCES:
    lines.append(f"| {s['file']} | {s['ordinary_points_by_weapon_set'][0]} / {s['ordinary_points_by_weapon_set'][1]} | {s['ascendancy_points']} |")
lines += ['', '## 08: 함성을 유지하면서 남는 포인트 사용', '',
          '07에서 아래 순서대로 **공통 포인트**로 추가한다. 뒤 경로를 먼저 찍지 않는다. 현재 가진 포인트까지만 찍고 나머지는 다음 레벨/퀘스트에서 이어 간다. 09와 다른 독립적인 방어 확장안이다.']
for i, k in enumerate(added, 1):
    n = NODES[k]
    lines.append(f"{i}. {n['name']} (`{n['stringId']}`): {'; '.join(n['stats'])}")
for before, after in zip(BUILDS, BUILDS[1:]):
    a = {(p['id'], p.get('weapon_set', 0)) for p in before['passives']}
    b = {(p['id'], p.get('weapon_set', 0)) for p in after['passives']}
    lines += ['', f"## {before['name']} → {after['name']}", '', '| 변경 | 배정 | 노드 | 효과 |', '|---|---|---|---|']
    for verb, entries in [('환불/재배정 전 확인', a-b), ('추가/재배정 목표', b-a)]:
        for sid, w in sorted(entries):
            n = NODES[BY_ID[sid]]
            lines.append(f"| {verb} | {'공통' if not w else f'세트{w}'} | {n['name']} (`{sid}`) | {'; '.join(n['stats']).replace('|', '/')} |")
(OUT / '패시브전환.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')

# Generate all three filters from one spec and pinned NeverSink 0.10.4 bases.
SPEC = copy.deepcopy(read(REPO / 'data/filter_build_targets/poe2_warbringer_skadoosh_0_5_5_hc.json'))
SPEC['_meta'] = {'build': 'Skadoosh HC Corrupting Cry / Totems — progression, not character level',
                 'game': 'poe2', 'patch': '0.5.5', 'base_filter': 'NeverSink 0.10.4',
                 'progression': {'campaign': '캠페인 완료 전. 캐릭터 65+ 포함', 'maps': '캠페인 완료, 초반 지도 및 장비 보강', 'endgame': '지도 진행과 장비가 안정되고 드롭 정리가 필요할 때'},
                 'palette': '기존 Warbringer 역할별 진홍/로즈 계열 시각 토큰 유지',
                 'notes': ['추가 Hide 없음. 미일치 아이템은 각 NeverSink 원본으로 처리.', 'AreaLevel은 몬스터 지역 레벨. 캐릭터 레벨에 따른 자동 전환 없음.', '미감정 장비의 생명력/저항/이동속도를 필터가 판별하지 못함.', '신규 리그 코어, 유니크 가치, 미가공 젬 티어 규칙은 최신 원본 유지.']}
for key, style in SPEC['styles'].items():
    style['comment'] = key + ' — 기존 Warbringer 시각/소리 토큰'
SPEC['rules'] = [r for r in SPEC['rules'] if r.get('kind') != 'hide']
for rule in SPEC['rules']:
    rule['stages'] = ['campaign', 'maps', 'endgame']
    rule['name'] = rule['name'].replace('[맵~]', '[전 구간]').replace('잔혹~', '후반 캠페인~')
    rule['note'] = '지역 레벨에 맞는 후보. 감정 후 옵션 비교; 장착 필수 아님.'
    if rule.get('class') == ['Charms']:
        rule.pop('area_level_max', None)
    if rule.get('class') == ['Jewels']:
        rule['rarity'] = ['Normal', 'Magic', 'Rare']

sceptres = sorted({b['Name'] for b in BASES if '/Weapons/OneHandWeapons/Sceptres/' in b['Id']})
new_rules = [
    {'name': '[정신력 준비] Shrine Sceptre — 최종 양 세트 후보', 'base_types': ['Shrine Sceptre'], 'class': ['Sceptres'], 'rarity': ['Normal', 'Magic', 'Rare'], 'style': 'weapon_gear'},
    {'name': '[정신력 준비] 그 외 셉터 — 정신력 옵션 감정', 'base_types': sceptres, 'class': ['Sceptres'], 'rarity': ['Magic', 'Rare'], 'style': 'weapon_gear'},
    {'name': '[정신력 준비] Solar Amulet', 'base_types': ['Solar Amulet'], 'class': ['Amulets'], 'rarity': ['Normal', 'Magic', 'Rare'], 'style': 'jewellery_gear'},
    {'name': '[캠페인 제작] 소켓 있는 후반 철퇴', 'base_types': sorted({b for r in SPEC['rules'] if r.get('class') in (['One Hand Maces'], ['Two Hand Maces']) for b in r['base_types']}), 'rarity': ['Normal', 'Magic'], 'sockets_min': 1, 'style': 'weapon_gear', 'stages': ['campaign', 'maps']},
]
for r in new_rules:
    r.setdefault('stages', ['campaign', 'maps', 'endgame'])
    r['note'] = '레벨 65+ 캠페인에서도 유지. 슬롯과 접미/접두 옵션을 감정해서 선택.'
SPEC['rules'] = new_rules + SPEC['rules']
write(HERE / 'filter_spec.json', SPEC)
overlay = module('delivery_overlay', 'build_poe2_build_overlay.py')
overlay.GAME_CLASS_TO_FILTER_CLASS['Sceptres'] = 'Sceptres'
stage_inputs = [('campaign', 'soft', '01-Campaign'), ('maps', 'regular', '02-EarlyMaps'), ('endgame', 'strict', '03-SettledMaps')]
for stage, base, name in stage_inputs:
    path = SRC / f'neversink_0.10.4_{base}.filter'
    base_text = path.read_text(encoding='utf-8')
    blocks = overlay.parse_base_blocks(base_text)
    classes = overlay.class_index(base_text)
    classes.update({b: 'Sceptres' for b in sceptres})
    vocab = overlay.base_vocabulary(base_text) | overlay.game_base_names() | set(sceptres)
    style_values = overlay.base_value_vocabulary(base_text)
    for key, style in SPEC['styles'].items():
        overlay.check_contrast(key, style)
        overlay.check_style_values(key, style, style_values)
    output, raised, shadowed = [], [], []
    for rule in SPEC['rules']:
        if stage not in rule['stages']:
            continue
        assert set(rule['base_types']) <= vocab, set(rule['base_types']) - vocab
        assert set(rule.get('class', [])) <= vocab, rule.get('class')
        generated, r, s = overlay.build_rule_blocks(rule, SPEC['styles'][rule['style']], blocks, classes)
        output += generated; raised += r; shadowed += s
    header = f'# Pathcraft Skadoosh HC 0.5.5 | {name} | NeverSink 0.10.4\n# Manual progression switch. Campaign includes character level 65+.\n# Added rules only Show; unmatched items follow the pinned base filter.\n\n'
    text = header + '\n\n'.join(output) + '\n\n' + base_text
    dest = OUT / 'Filters' / f'Pathcraft-Skadoosh-HC-{name}.filter'
    dest.write_text(text, encoding='utf-8', newline='\n')
    assert text.endswith(base_text)
    assert 'Hide' not in '\n\n'.join(output)
    assert not re.search(r'^\s*(?:CharacterLevel|PlayerLevel)\b', text, re.M)
    REPORT['filter_checks'].append({'file': dest.name, 'overlay_blocks': len(output), 'upstream_sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'base_tail_unchanged': True, 'additional_hide_blocks': 0, 'loudness_adjustments': len(raised), 'conditional_shadow_pairs': len(shadowed)})
write(HERE / 'validation_generation.json', REPORT)
print(json.dumps({'builds': len(BUILDS), 'filters': len(stage_inputs), 'extension_points': len(added), 'point_budgets': [(s['file'], s['ordinary_points_by_weapon_set']) for s in SOURCES]}, ensure_ascii=False, indent=2))
