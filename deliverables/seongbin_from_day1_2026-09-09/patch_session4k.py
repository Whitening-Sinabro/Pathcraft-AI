"""Tenth batch: the weapon-set-II staff tooltip and the hideout ES wipe."""
from pathlib import Path

HERE = Path(__file__).resolve().parent

NEW_ROWS = """ (F,600,'지도에서 은신처 거점으로 돌아온 직후 화면이다. 생명력1542/1572, **보호막0/2936**, 마나822/843, 정신력7/100이고 버프 줄에는 0%와 빨강1만 남아 있다.','보호막 전소 상태 확인','**초록 스택이 0일 때 최대 보호막이 정확히2936**으로, 마을·트리 화면의 기준값과 같다. 현재 보호막이0이라 이 지도에서 방어가 한 번 완전히 벗겨졌다는 뜻이다. 하드코어에서 위험 구간이지만 사망 여부는 이 프레임으로 판정하지 않는다.'),
 (F,2400,'90레벨 스킬 창에서 **용의 돛대 - 차임벨 지팡이** 툴팁 전문을 읽었다. 지팡이, 아이템 레벨81, 요구 사항 레벨60·46 지능이고 기본 속성은 주문 피해60% 증가다. **스킬 부여: 18레벨 힘의 부적**. 접두어는 주문 피해76(69-88)% 증가 T7 · 피해의47(43-48)%를 추가 화염 피해로 획득 T3 · 플레이어가 유발하는 피해를 주는 상태 이상의 강도56(40-64)% 증가 **T1**. 접미어는 **동결 축적78(71-80)% 증가 T1** · 시전 속도15(14-19)% 증가 T7 · **모든 주문 스킬 레벨 +5**(C 표기)다. 하단에 **장착 중: 무기 세트 II**와 장착 해제 버튼이 있다. 같은 화면 스킬 목록은 레벨18 힘의 부적, 레벨20 고결한 방어막, 레벨20 쇠뇌 사격 DPS1732.4, 레벨19 화염파 DPS922.6, 레벨15 기름 유탄 DPS149.9, 레벨19 절망, 레벨14 회오리이고 보조 젬 사용량은 힘(8/20)·민첩(5/13)·지능(15/30), 골드161894다.','세트II 무기 확정','**세트II 지팡이의 이름·옵션·장착 세트가 한 화면에 다 있다.** 9월7일 D에서 산 키메라의 몰이 막대가 아니라 다른 지팡이이므로 그 사이에 한 번 더 갈아탄 것이다. 정확한 교체 시점과 지불가는 아직 확인하지 않았다. **동결 축적78%**는 원소 상태 이상 시 시전이 동결 적 하나당 에너지10을 주는 것과 직접 맞물린다.'),
"""

ROW_STAFF = (
    '| **세트II 지팡이 = 용의 돛대 차임벨 지팡이** | 툴팁 전문(F00:40:00). 아이템 레벨81, 요구 레벨60·지능46, 기본 주문 피해 60% 증가, '
    '**스킬 부여 18레벨 힘의 부적**. 접두 주문 피해 76% T7 · 피해의 47%를 추가 화염 피해로 획득 T3 · '
    '**플레이어가 유발하는 피해를 주는 상태 이상의 강도 56% 증가 T1**. 접미 **동결 축적 78% 증가 T1** · 시전 속도 15% T7 · '
    '**모든 주문 스킬 레벨 +5**. 하단에 장착 중: 무기 세트 II 표기 '
    '| **이 지팡이는 딜 무기가 아니라 메타 스킬의 연료 공급기다.** 동결 축적 78%가 원소 상태 이상 시 시전의 '
    '"동결시킨 적 위세 하나당 에너지 10"과 직접 맞물리고, 상태 이상 강도 56%는 검은화염 계약으로 카오스가 된 점화의 강도를 올린다. '
    '9월7일에 산 키메라의 몰이 막대와는 다른 물건이므로 그 사이 한 번 더 갈아탔다. 교체 시점과 지불가는 미확인 |'
)


def replace_row(text, key, new_row):
    lines = text.split('\n')
    for i, line in enumerate(lines):
        if line.startswith(key):
            lines[i] = line + '\n' + new_row
            return '\n'.join(lines), True
    return text, False


def main():
    pf = HERE / 'precision_findings.py'
    src = pf.read_text(encoding='utf-8')
    if 'F,2400' not in src:
        cut = src.rstrip().rfind(']')
        pf.write_text(src[:cut] + NEW_ROWS + src[cut:], encoding='utf-8')
        print('rows added')
    else:
        print('rows already present')

    rf = HERE / 'research_focus.py'
    src = rf.read_text(encoding='utf-8')
    src, ok = replace_row(src, '| **세트II = 지팡이, 무기 세트 패시브도 세트II에만**', ROW_STAFF)
    rf.write_text(src, encoding='utf-8')
    print('staff row appended:', ok)


if __name__ == '__main__':
    main()
