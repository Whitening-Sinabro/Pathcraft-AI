"""Evidence-backed transition notes for plans 03–07; completed links stay intact."""

TRANSITIONS = {
    3: '03 진입과 완성 연결\n34레벨 공개 기록의 망치는 요철 지대 I·유지되는 대지 I부터다. 전쟁의 주먹 II는 세 번째 소켓과 젬 확보 뒤 추가한다. 마그마 장벽의 활력 I도 정신력 여유가 생긴 뒤 추가한 43레벨 목표다. 아래 연결을 망치 습득 즉시 전부 요구하지 않는다.',
    4: '04 교체 순서\n지옥불 함성 → 보강하는 함성. 처음은 타락시키는 비명 I·포악함 II·고통 격화 II 3보조, 이후 네 번째 효율 I → II. 함성과 충격파 토템을 함께 완성하려면 포악함 II가 각각 1개씩 필요하다. 지진의 유지되는 대지 II는 별도 추가하며 망치의 I는 남긴다.',
    5: '05에서 빼고 옮길 것\n충격파 토템·망치·화산 균열·지진·뼈 박살을 빼고, 보강하는 함성·공명하는 방패는 유지한다. 기존 토템의 포악함 II를 전사 토템으로 옮기고 내부 지면 분쇄·파생하는 균열 I를 추가한다. 긴급한 토템 III는 초기 필수가 아니다. 마그마의 명상 II를 빼고 회복 보조는 각 셉터의 불의 순수함 쪽에 준비한다. 아래 회복 연결은 성장 목표다.',
    6: '06 보조 이동 확인\n보강의 타락시키는 비명 I → 파콰테, 효율 II → 메아리. 빼낸 효율 II는 지진 함성으로 옮긴다. 보강의 포악함 II·고통 격화 II는 유지한다. 방송 Day 3 03:57에 파콰테와 메아리, 04:03에 지진 함성의 격노하는 함성을 확인했다. 새 젬만 바꾸고 G의 I/II 체크를 빠뜨리지 않는다.',
    7: '07 후기 추가 순서\n전사 토템의 포악함 II만 III로 교체하고 긴급한 토템 III를 추가한다. 보강의 포악함 II는 유지한다. 방송은 II 철퇴를 Sadist’s Mercy로 교체한 뒤 세 번째 전직 나무 벽을 적용했다. 나무 벽은 근처 살아 있는 토템이 있어야 피격 피해를 나누며 지속 피해·스킬 비용을 막아주지 않는다. 회복 보조를 더 넣으면 양 세트의 남는 정신력을 재확인한다.',
}

HINTS = {
    3: {
        'SkillGemForgeHammer': '진입 연결은 요철 지대 I + 유지되는 대지 I(34레벨 공개 기록). 전쟁의 주먹 II는 소켓·젬을 확보한 뒤 추가하는 43레벨 목표다.',
        'SkillGemMagmaBarrier': '34레벨 공개 기록에는 보조가 없다. 활력 I는 이후 추가한 회복 목표이며 장벽 습득 즉시 필수가 아니다.',
    },
    4: {
        'SkillGemFortifyingCry': '방송 04:23에 지옥불 함성을 교체하고 3보조로 시작. 04:31의 네 번째는 효율 I이며 50레벨 공개 기록에는 II다. 충격파 토템에도 포악함 II를 쓰므로 2개를 준비한다.',
        'SkillGemShockwaveTotem': '함성으로 포악함 II를 옮기면 이 토템의 보조가 빈다. 방송도 추가 포악함 II를 다시 넣었다. 함성과 토템에 각각 연결할 2개를 준비한다.',
        'SkillGemEarthquake': '유지되는 대지 II는 이 지진에 별도로 추가한다. 망치의 유지되는 대지 I를 빼서 옮기는 단계가 아니다.',
    },
    5: {
        'SkillGemAncestralWarriorTotem': '방송 초기 연결: 내부 지면 분쇄 + 기존 충격파 토템의 포악함 II + 파생하는 균열 I. 긴급한 토템 III는 나중 목표다. 젬 13레벨은 캐릭터 52·힘 92 요구. 품질 20은 추가 성장 항목이다.',
        'SkillGemMagmaBarrier': '04의 명상 II는 제거한다. 혈마법 뒤 마나 재생은 회복 수단이 아니다. 활력은 정신력 여유에 맞춰 해당 세트의 불의 순수함으로 연결한다.',
        'SkillGemPurityOfFire': '표의 활력/식인은 이후 성장 연결이다. 첫 전사 토템 설치 장면에서 양쪽 완성 연결이 모두 갖춰졌다고 확인한 것은 아니다. 각 세트의 회복과 버프 점유 후 남는 정신력을 따로 확인한다.',
    },
    6: {
        'SkillGemFortifyingCry': '05에서 빼낸 효율 II를 지진 함성으로 옮긴다. 보강에는 파콰테·메아리를 넣고 포악함 II·고통 격화 II를 유지한다. 방송 03:57에 이 연결로 바뀐다.',
        'SkillGemSeismicCry': '방송은 효율 I를 거친 뒤 04:03:14에 효율 II를 확인한다. 보강에서 빼낸 II를 이쪽에 쓰고 우주의 영사·격노하는 함성을 함께 연결한다.',
    },
    7: {
        'SkillGemAncestralWarriorTotem': '기존 토템의 포악함 II를 III로 올리고 추가 소켓에 긴급한 토템 III. 보강하는 함성의 포악함 II는 그대로 둔다. 확보한 젬·소켓에 따라 앞당길 수 있는 성장 목표다.',
        'SkillGemHarbingerOfMadness': '방송 Day 3 06:16에 Sadist’s Mercy를 II에 장착했다. I의 셉터·방패는 유지한다. 장비가 부여하는 효과이며 별도 공격 젬을 만들지 않는다.',
        'SkillGemPurityOfFire': '따뜻한 피·정밀함 II 연결 뒤 버프를 켜고 G에서 실제 점유를 확인한다. 성소 셉터의 순수함에 연결한 보조는 툴팁 점유의 단순 합산과 다를 수 있다. 토템 설치 전 남는 정신력 300을 I와 II에서 각각 확보해야 4기를 유지한다.',
    },
}


def correct_later_skill_requirements(build, stage):
    """Fix only specific off-by-one minima; preserve stage placeholder [1,100]."""
    changes = []
    if stage < 3:
        return changes
    mapping = {'SkillGemInfernalCry': (7, 6), 'SkillGemShockwaveTotem': (7, 6),
               'SkillGemResonatingShield': (15, 14), 'SkillGemMagmaBarrier': (11, 10),
               'SkillGemFortifyingCry': (32, 31), 'SkillGemEarthshatter': (23, 22),
               'SkillGemSeismicCry': (42, 41)}
    for skill in build['skills']:
        pair = mapping.get(skill['id'].split('/')[-1])
        if pair and skill.get('level_interval', [None])[0] == pair[0]:
            skill['level_interval'][0] = pair[1]
            changes.append({'id': skill['id'], 'from': pair[0], 'to': pair[1]})
    return changes


def apply_later_transition_notes(build, stage):
    if stage not in TRANSITIONS:
        return False
    assert build['description'].count('지금 할 일\n') == 1
    build['description'] = build['description'].replace('지금 할 일\n', TRANSITIONS[stage] + '\n\n지금 할 일\n')
    build['description'] = build['description'].replace('무기·스킬셋\n', '무기·스킬셋 · 성장 후 연결 목표\n')
    if stage == 5:
        build['description'] = build['description'].replace('마을에서 트리·무기·젬을 맞추고 혈마법은 마지막에 찍는다.', '권장 작업 순서: 마을에서 트리·무기·젬을 맞춘 뒤 혈마법을 찍는다(방송의 클릭 순서와 다름).')
    for skill in build['skills']:
        hint = HINTS[stage].get(skill['id'].split('/')[-1])
        if hint:
            marker = '<b>{이 스킬 안에 넣을 젬}'
            assert skill['additional_text'].count(marker) == 1
            skill['additional_text'] = skill['additional_text'].replace(marker, '<b>{이번 단계의 교체·준비}\n' + hint + '\n' + marker)
    return True
