"""Apply the two VOD-checked passive states after the earlier gem corrections."""
from pathlib import Path
import copy
import json
from stage_05_06_progression import TREE_NOTE, SEISMIC
from weapon_sets import TREE

HERE = Path(__file__).resolve().parent
VERIFIED = json.loads((HERE / 'stage_05_06_verified_passives.json').read_text(encoding='utf-8'))
NOTES = {
    5: ('54레벨 방송 트리 · 00:29:54~00:30:28 화면 복원\n'
        '일반 71점 = 공통 57 + 특화 각 14, 전직 4점. Hard to Kill·Spirit Bond·Ancestral Conduits를 이미 갖춘다. '
        'I는 Lay Siege를 유지하고 Bolstering Yell은 제외한다. Carved Earth는 이때 환불한 상태다. '
        '방송 화면의 선택 경로·세트 색과 남은 포인트를 대조한 복원본이다. 당시 API 내보내기 파일은 아니다.\n\n'),
    6: ('65레벨 방송 트리 · 03:54:20~03:55:50 화면 복원\n'
        '일반 87점 = 공통 65 + 특화 각 22, 전직 4점. 방송에는 일반 1점과 특화 각 2점이 남는다. '
        '05 배정을 유지하며 회복·방어, I 함성·방패, II 토템 가지를 확장한다. '
        'Desensitisation·Battle Fever는 아직 배정하지 않는다. 화면 경로와 포인트를 대조한 복원본이며 당시 API 내보내기는 아니다.\n\n'),
}

def apply_verified_passives(build, stage):
    if stage not in (5, 6):
        return False
    old = {x['id']: x for x in build['passives']}
    nodes = copy.deepcopy(VERIFIED['stages'][str(stage)]['passives'])
    for node in nodes:
        previous = old.get(node['id'], {})
        if previous.get('weapon_set', 0) == node.get('weapon_set', 0) and previous.get('additional_text'):
            node['additional_text'] = previous['additional_text']
        elif node.get('weapon_set'):
            label = 'I' if node['weapon_set'] == 1 else 'II'
            node['additional_text'] = f'무기 세트 {label} 특화에 배정. 해당 세트로 스킬을 사용한다.'
            if TREE[node['id']].get('isNotable'):
                node['additional_text'] += '\n' + ' / '.join(TREE[node['id']]['stats'])
    build['passives'] = nodes
    if build['description'].startswith(TREE_NOTE):
        build['description'] = NOTES[stage] + build['description'][len(TREE_NOTE):]
    else:
        assert build['description'].startswith(NOTES[stage]), 'Apply gem progression first'
    old_timing = '늦어도 방송 02:35:41에는 이미 연결돼 있다. 최초 추가 시점은 미확정이며 06에서 처음 배우는 스킬이 아니다.'
    new_timing = '방송 00:52:21~23에 11레벨 지진 함성을 만들어 빈 칸에 장착한다. 우주의 영사·효율 I 연결은 늦어도 02:35:41에 확인된다.'
    build['description'] = build['description'].replace(old_timing, new_timing)
    if stage == 5:
        seismic = next(s for s in build['skills'] if s['id'] == SEISMIC)
        seismic['additional_text'] = seismic['additional_text'].replace(
            '늦어도 방송 02:35:41의 파콰테 전 단계에 우주의 영사·효율 I가 연결돼 있다. 최초 추가 시점은 미확정이다.',
            '방송 00:52:21~23에 11레벨 젬을 만들어 빈 스킬 칸에 장착한다. 우주의 영사·효율 I 연결은 늦어도 02:35:41에 확인된다. 장착과 보조 연결의 확인 시점을 구분한다.')
    return True
