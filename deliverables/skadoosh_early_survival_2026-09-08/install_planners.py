"""Build and install the seven verified Skadoosh plans with survival hints."""
from pathlib import Path
import copy
import datetime
import hashlib
import json
import re
import shutil
from weapon_sets import apply_weapon_sets, validate_weapon_sets, write_weapon_set_guide
from combat_rotations import apply_combat_rotation, apply_volcanic_fissure_hint, correct_early_skill_requirements, write_rotation_guide
from later_transitions import apply_later_transition_notes, correct_later_skill_requirements
from stage_05_06_progression import apply_stage_05_06_progression
from stage_05_06_passives import apply_verified_passives

HERE = Path(__file__).resolve().parent
OLD = HERE.parent / 'skadoosh_hc_2026-09-07'
SOURCE = OLD / 'ready/BuildPlanner'
OUT = HERE / 'BuildPlanner'
GAME = Path('C:/Users/User/Documents/My Games/Path of Exile 2')
DEST = GAME / 'BuildPlanner'
LOG = Path('C:/Program Files (x86)/Grinding Gear Games/Path of Exile 2 - poe2_production/logs/Client.txt')


def read(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def structure(x):
    if isinstance(x, dict):
        return {k: structure(v) for k, v in x.items() if k not in ('description', 'additional_text', 'unique_name')}
    if isinstance(x, list):
        return [structure(v) for v in x]
    return x


def strings(x):
    if isinstance(x, dict):
        for v in x.values():
            yield from strings(v)
    elif isinstance(x, list):
        for v in x:
            yield from strings(v)
    elif isinstance(x, str):
        yield x


def normalize_support_order(x):
    """Compare game data while allowing only the documented support reordering."""
    data = structure(x)
    for skill in data.get('skills', []):
        if skill['id'].endswith('SkillGemShockwaveTotem'):
            skill['support_skills'] = sorted(skill.get('support_skills', []), key=lambda s: s['id'])
    return data


validated = {r['file']: r['sha256'] for r in read(OLD / 'validation_revision3.json')['planners']}
sources = sorted(SOURCE.glob('*.build'))
assert len(sources) == 7 and {p.name for p in sources} == set(validated)
assert all(sha(p) == validated[p.name] for p in sources), 'Previously validated source changed'
assert (SOURCE / '01 시작-근접 기초.build').exists(), 'Preserve the original selected file path'
OUT.mkdir(exist_ok=True)
DEST.mkdir(exist_ok=True)
other = {p: sha(p) for p in DEST.glob('*.build') if p.name not in validated}
other.update({p: sha(p) for p in GAME.glob('*.filter')})
log_start = LOG.stat().st_size if LOG.exists() else None

intro = ('초반 생존 준비\n'
         '황동의 턱수염은 생명력 +100의 우선 확보 후보다. 10레벨·힘 10·지능 10부터 착용하며 이속 신발을 함께 챙긴다. '
         '생명력 플라스크를 갱신하고 필요한 원소 저항을 보완한다. '
         '이벤트 보스 의식 연전은 미루되 프레이쏜의 정신력 +30 영구 보상은 챙긴다. '
         '전투 중 질주를 줄이고 설치할 때 퇴로를 남긴다. 보스 패턴 대응을 우선한다.\n\n')
damage_intro = ('초반 목표 · 빠른 타격과 처치\n'
                '지속 회복이 부족한 동안에는 주력 피해와 타격 속도, 기절 연계로 전투를 짧게 끝낸다. '
                '주력 젬과 보조를 갱신한다. 근접 시작 구간에서는 한손 철퇴의 물리 피해·공격 속도도 비교한다. '
                '생명력 +100 황동의 턱수염은 10레벨·힘 10·지능 10부터 우선 확보 후보이며, 이속 신발·필요 저항·플라스크를 함께 챙긴다. '
                '이벤트 보스 의식 연전은 미루고 프레이쏜 정신력 +30 영구 보상은 챙긴다.\n\n')
helmet = ('<b>{초반 우선 확보 · 황동의 턱수염}\n'
          'Bronzebeard · 최대 생명력 +100. 10레벨·힘 10·지능 10부터 착용.\n'
          '이동 속도 10% 감소가 있으므로 이속 신발도 함께 챙긴다. 구할 수 있으면 우선 사용한다.\n'
          '<b>{없을 때 추천 옵션}\n1. 최대 생명력\n2. 부족한 화염·냉기·번개 저항\n3. 방어도\n'
          '획득하려고 자꾸 죽는 보스 의식 연전을 반복하지 않는다.')
boots = ('<b>{장화 · 이동 속도 우선}\n'
         '추천 옵션\n1. 이동 속도 10~15%부터 확보할 후보로 찾는다.\n2. 최대 생명력\n'
         '3. 부족한 화염·냉기·번개 저항\n4. 방어도 / 생명력 재생\n'
         '황동의 턱수염을 쓰면 이속을 함께 확인한다. 위 수치는 권장 후보이며 필수 통과 수치가 아니다.')
life_flask = ('<b>{생명력 플라스크 · 자주 갱신}\n'
              '추천 옵션\n1. 현재 레벨에 맞는 베이스와 충분한 회복량\n2. 회복 속도\n'
              '3. 사용 충전 감소 / 충전 획득\n'
              '새 베이스를 얻으면 기존 회복량·시간·충전과 비교한다. 보스 전에 충전을 채운다.')
charm = ('<b>{호신부 · 현재 위험에 맞춰 선택}\n'
         '추천 옵션\n1. 현재 지역의 원소 피해·상태 이상 대응\n2. 효과 지속시간\n3. 충전 관련 옵션\n'
         '연속 기절에는 Stone Charm을 후보로 검토한다. 기절 후 발동하는 효과이며 상시 면역은 아니다. '
         '벨트의 활성 슬롯과 충전을 확인한다.')
passive_hints = {
    'totems34': '토템이 있을 때 플레이어 최대 생명력의 1%를 초당 재생한다. 다른 재생 보정 전 생명력 400이면 이 효과는 초당 4인 보조 회복이다. 맞으며 버티는 운영의 근거로 삼지 않는다. 토템의 3% 재생은 토템 자신에게 적용되며 토템이 모두 사라지면 플레이어의 조건부 재생도 끊긴다.',
    'marauder_brute_notable2': '방어도 15% 증가, 최대 생명력 0.5% 초당 재생, 힘 +10. 현재 경로에서 도달하면 장비 방어도·생명력과 함께 확인한다.',
    'armour35': '착용한 갑옷에서 얻는 방어도 80% 증가. 모든 부위의 방어도에 80%가 붙는 효과는 아니다. 갑옷의 실제 방어도·생명력·저항을 함께 갱신한다.',
    'attack_speed55': '스킬 속도 6% 증가. 스킬 마나 비용의 6%가 생명력 비용으로 바뀐다. 최대 생명력의 6%를 쓰는 효과가 아니다. 혈마법 전에도 생명력·마나 회복을 함께 확인한다.',
    'life_regeneration17_': '플라스크 생명력 회복 속도 40% 증가, 최대 생명력 0.75% 초당 재생. 총 회복량 40% 증가로 읽지 않는다. 생명력 플라스크 베이스도 현재 레벨에 맞게 갱신한다.',
}

rows = []
for src in sources:
    original = read(src)
    d = copy.deepcopy(original)
    stage = int(src.name[:2])
    if stage <= 4:
        d['description'] = (damage_intro if stage <= 3 else intro) + d['description']
        for slot in d['inventory_slots']:
            inv = slot['inventory_id']
            if inv == 'Helm1':
                slot['unique_name'] = 'Bronzebeard'
                slot['additional_text'] = helmet
            elif inv == 'Boots1':
                slot['additional_text'] = boots
            elif inv == 'Flask1' and slot.get('slot_x', 0) == 0:
                slot['additional_text'] = life_flask
            elif inv == 'Charm1':
                slot['additional_text'] = charm
            elif inv == 'BodyArmour1':
                slot['additional_text'] += '\n빈 룬 소켓이 있으면 현재 부족한 저항을 보완한다.'
                if stage >= 3:
                    slot['additional_text'] += '\nSturdy Metal은 이 갑옷에서 얻는 방어도를 강화한다. 갑옷의 방어도도 함께 갱신한다.'
        for skill in d['skills']:
            if skill['id'].endswith('SkillGemEarthquake'):
                skill['additional_text'] += '\n지대가 실제로 생성되지 않을 때 젬·세트와 지역 변경·재접속을 점검한다. 현재도 항상 발생하는 버그라고 단정하지 않는다.'
            elif skill['id'].endswith('SkillGemShockwaveTotem'):
                skill['additional_text'] += '\n토템이 남아 있는지 확인하고 필요한 만큼 갱신한다. 적에게 둘러싸인 뒤 재설치를 연타하지 않는다.'
    for node in d['passives']:
        if node['id'] in passive_hints:
            node['additional_text'] = passive_hints[node['id']]
    if stage == 2:
        before = ('처음에는 보조 없이도 쓸 수 있고 과잉 I를 확보하면 넣는다. '
                  '과잉 I의 지속시간 50% 감폭 때문에 자주 다시 설치해야 한다.')
        after = ('처음에는 보조 없이도 쓸 수 있다. 과잉 I는 지속시간 50% 감폭 때문에 재설치가 잦다. '
                 '빠른 공격 I로 타격 속도를 챙기고, 포악함 II를 확보하면 물리 피해를 보강한다. '
                 '보조 소켓이 2개라면 이 둘을 먼저 검토한다. 긴급한 토템 I는 설치 속도 보완용이다. '
                 '포악함 II 확보 전에는 가진 보조로 진행하며 설치가 느려 맞으면 긴급한 토템 I의 우선순위를 높인다.')
        assert before in d['description']
        d['description'] = d['description'].replace(before, after)
        for skill in d['skills']:
            if skill['id'].endswith('SkillGemShockwaveTotem'):
                skill['additional_text'] = skill['additional_text'].replace(
                    '처음 과잉 I를 쓰다가 아래 완성 연결로 교체한다.',
                    '과잉 I는 지속시간을 줄이므로 재설치가 버거우면 우선순위를 낮춘다. 타격 속도와 물리 피해 보조를 우선 검토한다.')
            if skill['id'].endswith('SkillGemMagmaBarrier'):
                skill['additional_text'] = skill['additional_text'].replace(
                    '정신력 30 확보 후 켠다.',
                    '프레이쏜의 안개 속의 왕에서 정신력 +30 영구 보상을 챙기고 켠다. 활력 I 추가는 정신력 여유가 생긴 뒤 확인한다.')
    if stage <= 3:
        order = ['Metadata/Items/Gems/SupportGemMartialTempo',
                 'Metadata/Items/Gems/SupportGemBrutalityTwo',
                 'Metadata/Items/Gem/SupportGemAncestralUrgency']
        previous_link = '빠른 공격 I + 긴급한 토템 I + 포악함 II'
        damage_link = '빠른 공격 I + 포악함 II + 긴급한 토템 I'
        d['description'] = d['description'].replace(previous_link, damage_link)
        d['description'] = d['description'].replace(
            '이후 빠른 공격 I·긴급한 토템 I·포악함 II를 확보해 표의 완성 연결로 바꾼다.',
            '보조 3개가 준비되면 아래 완성 연결을 사용한다.')
        for slot in d['inventory_slots']:
            slot['additional_text'] = slot['additional_text'].replace(previous_link, damage_link)
            if slot['inventory_id'] == 'Weapon1' and stage == 1:
                slot['additional_text'] += '\n초반 근접 처치가 느리면 무기 물리 피해·공격 속도부터 갱신한다. 기절 준비 뒤 뼈 박살로 무리를 정리한다.'
        for skill in d['skills']:
            if skill['id'].endswith('SkillGemShockwaveTotem'):
                assert {s['id'] for s in skill['support_skills']} == set(order)
                skill['support_skills'].sort(key=lambda s: order.index(s['id']))
                skill['additional_text'] = skill['additional_text'].replace(previous_link, damage_link)
                skill['additional_text'] += '\n소켓 2개·포악함 II 확보 시 빠른 공격 I + 포악함 II부터 검토한다. 설치 동작이 병목이면 긴급한 토템 I를 앞당긴다.'
                for support in skill['support_skills']:
                    if support['id'] == order[0]:
                        support['additional_text'] = '<b>{빠른 공격 I}\n연결할 스킬: 충격파 토템 (세트 II).\n해당 스킬의 보조 소켓에 넣는다.\n타격 속도 보강. 현재 옵션은 공격 속도 15% 증가다.'
                    elif support['id'] == order[1]:
                        support['additional_text'] = '<b>{포악함 II}\n연결할 스킬: 충격파 토템 (세트 II).\n해당 스킬의 보조 소켓에 넣는다.\n물리 피해 30% 증폭. 원소·카오스 피해 불가, 비용 배율 120%. 해당 등급 젬 확보 뒤 마나 유지도 확인한다.'
                    else:
                        support['additional_text'] = '<b>{긴급한 토템 I}\n연결할 스킬: 충격파 토템 (세트 II).\n해당 스킬의 보조 소켓에 넣는다.\n설치 속도 80% 증가. 토템 타격 속도를 올리는 효과는 아니다. 설치 동작이 길어 맞을 때 우선순위를 높인다.'
    weapon_check = apply_weapon_sets(d, stage)
    rotation_added = apply_combat_rotation(d, stage)
    volcanic_hint_added = apply_volcanic_fissure_hint(d, stage)
    requirement_changes = correct_early_skill_requirements(d)
    later_notes_added = apply_later_transition_notes(d, stage)
    later_requirement_changes = correct_later_skill_requirements(d, stage)
    progression_changes = apply_stage_05_06_progression(d, stage)
    passive_reconstruction_applied = apply_verified_passives(d, stage)
    weapon_check = validate_weapon_sets(d) if passive_reconstruction_applied else weapon_check
    expected = copy.deepcopy(original)
    assert correct_early_skill_requirements(expected) == requirement_changes
    assert correct_later_skill_requirements(expected, stage) == later_requirement_changes
    apply_stage_05_06_progression(expected, stage)
    apply_verified_passives(expected, stage)
    assert normalize_support_order(d) == normalize_support_order(expected), 'Unexpected allocation, skill link membership, requirement, identity or slot layout change'
    assert len(d['description']) <= 1900, (src.name, 'description', len(d['description']))
    for value in strings(d):
        assert '\ufffd' not in value and value.count('{') == value.count('}')
        assert not re.search(r'\\[nr]', value)
    for slot in d['inventory_slots']:
        assert len(slot['additional_text']) <= 900
    for skill in d['skills']:
        assert len(skill['additional_text']) <= 600, (src.name, skill['id'], len(skill['additional_text']))
        for support in skill.get('support_skills', []):
            assert len(support['additional_text']) <= 230
    allowed_added = [('Helm1', 'Bronzebeard')] if stage <= 4 else []
    assert [(s['inventory_id'], s['unique_name']) for s in d['inventory_slots'] if s.get('unique_name')] == allowed_added
    out = OUT / src.name
    out.write_text(json.dumps(d, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    assert read(out) == d
    rows.append({'file': src.name, 'display_name': d['name'], 'source_sha256': sha(src),
                 'sha256': sha(out), 'passives_preserved': stage not in (5, 6),
                 'vod_passive_reconstruction_checked': passive_reconstruction_applied,
                 'gem_links_preserved': stage not in (5, 6),
                 'stage_05_06_progression_changes': progression_changes,
                 'survival_hints': stage <= 4, 'early_damage_priority': stage <= 3,
                 'combat_rotation_at_top': rotation_added and stage not in (5, 6),
                 'volcanic_fissure_timing_and_charge_condition': volcanic_hint_added,
                 'verified_skill_requirement_corrections': requirement_changes,
                 'later_transition_notes': later_notes_added,
                 'later_skill_requirement_corrections': later_requirement_changes,
                 'shockwave_support_priority_reordered': stage in (2, 3),
                 'weapon_set_validation': {'sets': weapon_check['sets'], 'both_sets_connected': weapon_check['both_sets_connected']},
                 'unique_target': 'Bronzebeard' if stage <= 4 else None})

write_weapon_set_guide([read(OUT / row['file']) for row in rows])
write_rotation_guide()

# Install only these seven paths after all generated files have passed validation.
backups = []
for row in rows:
    src = OUT / row['file']
    dest = DEST / row['file']
    assert dest.resolve().parent == DEST.resolve()
    if dest.exists() and sha(dest) != sha(src):
        backup = HERE / 'planner_backups' / (dest.stem + '.' + sha(dest)[:12] + '.build')
        backup.parent.mkdir(exist_ok=True)
        if not backup.exists():
            shutil.copy2(dest, backup)
        assert sha(backup) == sha(dest)
        backups.append(str(backup))
    shutil.copy2(src, dest)
    assert sha(dest) == row['sha256']
    row['installed'] = str(dest)
assert all(p.exists() and sha(p) == digest for p, digest in other.items())
manifest = {'installed_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'installed_count': 7, 'files': rows, 'unrelated_hashes_preserved': {str(p): h for p, h in other.items()},
            'backups': backups, 'game_log': str(LOG), 'game_log_start_offset': log_start,
            'game_parser_load_verified': False,
            'schema_reference': 'https://www.pathofexile.com/developer/docs/game#buildplanner'}
(HERE / 'planner_installation.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'installed': 7, 'survival_notes_and_helmet_target': 4,
                  'existing_other_planners_preserved': sum(p.suffix == '.build' for p in other),
                  'source_validation_hashes_matched': True,
                  'destination_hashes_matched': True,
                  'game_log_start_offset': log_start}, ensure_ascii=False))
