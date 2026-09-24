"""Source-backed 05/06 gem corrections; deliberately does not reconstruct passives."""
import copy

SEISMIC = 'Metadata/Items/Gems/SkillGemSeismicCry'
PRECISION = 'Metadata/Items/Gems/SupportGemPrecisionTwo'
INSPIRATION = 'Metadata/Items/Gems/SupportGemInspiration'
ASTRAL = 'Metadata/Items/Gem/SupportGemAstralProjection'
TREE_NOTE = ('트리 대조 미완료\n이 파일의 일반 69점·특화 각 14점은 Pathcraft 전환안이며 방송 54/65레벨 복제본이 아니다. '
             '54레벨 화면에는 Hard to Kill·Spirit Bond·Ancestral Conduits가 이미 있으나 이 전환안에는 빠져 있다. '
             '기존 회복 노드를 일괄 환불하거나 방송과 같은 회복량이 나온다고 가정하지 않는다. 전체 배정 복원 전까지 트리를 그대로 복사하는 용도로 쓰지 않는다.\n\n')
COMMON = ('무기 세트 · G에서 직접 지정\nI: 성소 셉터 + 방어도 방패, 보강·지진 함성. '
          'II: 한손 철퇴 + 성소 셉터, 선대의 전사 토템. 지면 분쇄는 토템 내부 액티브 젬이다. '
          '불의 순수함은 각 셉터의 항목에 I/II를 따로 지정한다. 플래너가 실제 체크 상태를 자동 변경하지는 않는다.\n\n')
LINKS = ('양 단계 공통 성장 연결\nI 불의 순수함: 활력 II + 식인 II. II 불의 순수함: 활력 I + 정밀함 II. '
         '정밀함 II는 방송 03:36:12에 추가되며 54레벨 전환 즉시 필수로 확인된 것은 아니다. '
         '성소 셉터의 순수함은 보조 툴팁 점유를 실제 추가 점유로 단정하지 않는다. 버프를 켠 뒤 G에서 토템 설치 전 I·II 각각 실제 남는 정신력을 확인한다. 4기 목표는 각 300이다.\n'
         'II 전사 토템: 내부 지면 분쇄 + 포악함 II + 파생하는 균열 I. 긴급한 토템 III는 후기 성장 항목이다.\n\n')
DESCRIPTIONS = {
    5: (TREE_NOTE + COMMON +
        '05 진입과 이후 성장\n선대의 전사 토템 젬 13레벨(캐릭터 52·힘 92), 셉터 2개·철퇴·방패·정신력과 생명력 재생을 준비한다. '
        '방송은 54레벨에 전환했다. 충격파 토템·망치·화산 균열·지진·뼈 박살을 빼고 보강·공명하는 방패를 유지한다. '
        '기존 토템의 포악함 II를 전사 토템으로 옮긴다. 마그마 장벽의 명상 II를 제거하고 불의 순수함에 회복 보조를 준비한다. '
        '혈마법 뒤 설치·함성이 생명력을 소모하므로 사용 후 회복이 따라오는지 확인한다.\n\n'
        '05 함성 연결 · 파콰테 전\n보강: 타락시키는 비명 I + 포악함 II + 고통 격화 II + 효율 II.\n'
        '지진 함성: 우주의 영사 + 효율 I. 늦어도 방송 02:35:41에는 이미 연결돼 있다. 최초 추가 시점은 미확정이며 06에서 처음 배우는 스킬이 아니다.\n\n'
        '실전 사용\n일반 무리는 보강(I)을 쓰며 이동한다. 밀집 무리·희귀·보스에는 전사 토템(II)을 보태고 함성(I)으로 방패 세트에 복귀한다. '
        '지진 함성을 추가한 뒤에는 적·가시 쪽에 보조 함성으로 사용한다. 가시는 토템이 만들며 직접 지면 분쇄를 누르지 않는다. '
        '토템이 죽거나 만료되거나 적이 벗어나면 보충한다. 매 무리마다 동일한 세 버튼 순서를 강제하지 않는다.\n\n' + LINKS +
        '회복 참고\n54레벨 전환 전 갑옷에 생명력 +113·초당 재생 16.2·정신력 +42가 보였다. 이 수치는 방송 장비 사례이며 필수 기준이 아니다. '
        '회복·저항을 갖춘 뒤 65레벨·파콰테·메아리 준비와 비용 시험 → 06.'),
    6: (TREE_NOTE + COMMON +
        '06에서 교체할 보조\n65레벨과 파콰테·메아리치는 함성, 필요한 소켓을 확보한다. '
        '보강의 타락시키는 비명 I를 파콰테의 맹약으로, 효율 II를 메아리치는 함성으로 바꾼다(방송 03:57). '
        '보강의 포악함 II·고통 격화 II는 유지한다. 빼낸 효율 II를 기존 지진 함성의 효율 I 자리에 넣고 격노하는 함성을 추가한다(04:03:14). '
        '지진 함성 완성 연결은 우주의 영사 + 효율 II + 격노하는 함성이다.\n\n'
        '실전 사용\n보강(I)을 쓰고 이동하며 메아리·타락한 피를 이어간다. 사이에 지진 함성(I)으로 시체·가시 폭발과 격노를 보탠다. '
        '밀집 무리·희귀·보스에는 토템(II)을 설치하고 함성(I)으로 복귀한다. 살아 있는 토템을 유지하며 회피하고 만료·사망·적 이동에 맞춰 보충한다. '
        '함성만으로 정리되는 무리는 이동한다. 모든 함성 이펙트를 직접 연타로 읽지 않는다.\n'
        '메아리는 1.3초 간격 2회이며 보강 재사용에는 10m 이동이 필요하다. 이동·남은 적·생명력 비용을 보고 갱신하며 고정 초 단위 순서를 외우지 않는다.\n\n' + LINKS +
        '회복과 진입 판단\n방송 03:55:42의 65레벨 I 세트 창에는 생명력 1624·초당 회복 115.7이 표시된다. 살아 있는 토템이 있는 당시 상태의 수치다. '
        '장비·재생·활력까지 함께 준비한 결과로 보며 같은 젬만 넣어 재현된다고 가정하지 않는다. '
        '04:59:33에는 메아리도 회복시킨다는 설명이 있으나 회복량과 비용 상쇄는 정량 확인되지 않았다. '
        '생명력이 계속 내려가면 05의 보강 연결로 되돌린다. 안정된 뒤 후기 성장 → 07.'),
}

def support(ident, name, skill):
    return {'id': ident, 'level_interval': [1, 100],
            'additional_text': f'<b>{{{name}}}\n연결할 스킬: {skill}. 해당 스킬의 보조 소켓에 넣는다.'}

def apply_stage_05_06_progression(build, stage):
    if stage not in (5, 6):
        return []
    before_passives = copy.deepcopy(build['passives'])
    changes = []
    if stage == 5:
        seismic = next((s for s in build['skills'] if s['id'] == SEISMIC), None)
        if seismic is None:
            seismic = {'id': SEISMIC, 'level_interval': [41, 100], 'support_skills': []}
            build['skills'].append(seismic)
            changes.append('05 Seismic Cry + Astral Projection + Inspiration I')
        seismic['support_skills'] = [support(ASTRAL, '우주의 영사', '지진 함성 (세트 I)'),
                                    support(INSPIRATION, '효율 I', '지진 함성 (세트 I)')]
        seismic['additional_text'] = ('<b>{지진 함성 · 세트 I}\nG 무기 세트 체크: I만. '
            '늦어도 방송 02:35:41의 파콰테 전 단계에 우주의 영사·효율 I가 연결돼 있다. 최초 추가 시점은 미확정이다.\n'
            '<b>{전투에서 누르는 때}\n보강을 쓰며 이동하다 적·토템의 지면 분쇄 가시 쪽에 보조 함성으로 사용한다. '
            '생명력 비용과 이동·회피를 함께 확인한다. 06에서 효율 I를 II로 교체하고 격노하는 함성을 추가한다.\n'
            '<b>{이 스킬 안에 넣을 젬}\n우주의 영사 + 효율 I')
    purity = [s for s in build['skills'] if s['id'].endswith('SkillGemPurityOfFire')]
    assert len(purity) == 2
    if not any(s['id'] == PRECISION for s in purity[1]['support_skills']):
        purity[1]['support_skills'].append(support(PRECISION, '정밀함 II', '불의 순수함 (세트 II)'))
        changes.append(f'{stage:02} set II Purity of Fire + Precision II')
    purity[1]['additional_text'] = ('<b>{불의 순수함 · 세트 II}\nG 무기 세트 체크: II만. 해당 셉터 스킬에 연결한다.\n'
        '<b>{이번 단계의 교체·준비}\n정밀함 II는 방송 03:36:12에 이미 추가됐다. 07에서 처음 넣는 보조가 아니다. '
        '보조 툴팁의 추가 점유 20을 성소 셉터의 실제 추가 점유로 단정하지 않는다. 9월 9일 방송의 순수함 연결은 단순 합산과 맞지 않으므로, 버프를 켠 뒤 G에서 양 세트의 실제 남는 정신력을 확인한다. 54레벨 진입 즉시 완성 연결이 있었다는 뜻은 아니다.\n'
        '<b>{이 스킬 안에 넣을 젬}\n활력 I + 정밀함 II')
    if stage == 6:
        seismic = next(s for s in build['skills'] if s['id'] == SEISMIC)
        seismic['additional_text'] = ('<b>{지진 함성 · 세트 I}\nG 무기 세트 체크: I만.\n'
            '<b>{이번 단계의 교체·준비}\n05에서 이미 사용하던 지진 함성의 효율 I를 II로 바꾼다. '
            '보강에서 빼낸 효율 II를 이쪽에 옮기고 격노하는 함성을 추가한다(방송 04:03:14).\n'
            '<b>{전투에서 누르는 때}\n보강의 메아리 사이에 적·가시 쪽으로 사용한다. 시체·가시 폭발과 격노를 보태고 이동·회피를 섞는다. '
            '지진 함성 비용도 생명력 유지에 포함한다. 파콰테는 보강에 둔다.\n'
            '<b>{이 스킬 안에 넣을 젬}\n우주의 영사 + 효율 II + 격노하는 함성')
    build['description'] = DESCRIPTIONS[stage]
    assert build['passives'] == before_passives
    return changes
