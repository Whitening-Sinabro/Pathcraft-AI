"""Ninth batch: rune stash context, the boss-carried-item label, and the rune verdict."""
from pathlib import Path

HERE = Path(__file__).resolve().parent

NEW_ROWS = """ (C,9150,'화폐 보관함에서 **숙련공의 오브** 툴팁을 읽었다. 중첩 개수2/20이고 설명은 무도 무기·마법봉·지팡이 또는 방어구에 **증강물 홈을 추가**한다는 것이다. 우측 장비 창에는 새 투구가 들어가 있고 소지품에는 기존 회색 투구·지팡이·장갑이 있다. 골드65499다.','룬을 박기 전 홈 확보 수단 확인','상위 철 룬을 쓰려면 먼저 증강물 홈이 있어야 한다. 보유는2개다. 이 프레임은 툴팁 확인이고 실제 사용이 아니다.'),
 (C,9158,'**증강물 보관함 탭**을 연 화면이다. 파란 룬 아이콘이 격자로 가득 차 있고 위쪽에 특수 아이콘 다섯 개가 따로 있으며 아래에 **업그레이드** 버튼이 있다. 골드65499다.','룬 재고 화면 확인','룬은 보관함에서 업그레이드할 수 있는 것으로 보이나 이 화면만으로 재료·비율을 단정하지 않는다. 9160초 상위 철 룬 툴팁 직전 화면이다.'),
 (F,5500,'혐오스러운 자 아오타 처치 지도에서 **인간사냥꾼 브로나크**(체력4238406)와 교전 중이다. 보스 이름 아래에 **덤불 매혹 장착됨** 표시와 속성 아이콘들, -16%·100%가 있다. 생명력1910/1910, 보호막2878/3131, 마나480/847, 정신력7/100이고 버프 줄 구슬은12·12·초록7에 0%·25(0:08·0:04)다. 의식 인카운터는 0 공물 점수·의식0회 남음이다.','대형 보스전 확인','**5380초의 탐욕의 포옹 장착됨과 같은 형식**이다. 이 표시는 보스 이름표 영역에 붙으므로 몬스터가 아이템을 지니고 있다는 뜻으로 읽고 플레이어 버프로 세지 않는다. 초록7에서 최대 보호막3131로 기준값 규칙과 맞는다.'),
"""

PENDING_RUNE = (
    '| 보완 | 상위 철 룬을 어느 장비에 박았는가 | C02:32:26~02:33:10 (9146~9190초) '
    '| **이 구간에는 삽입 장면이 없다.** 증강물 보관함에서 룬 재고를 훑고(9158) 상위 철 룬 툴팁을 읽은 뒤(9160) '
    '장착 중인 장갑(9166)과 장화(9170)를 차례로 열어 봤고, 그 사이에 투구를 새것으로 교체했다(9176). '
    '9150초에는 **숙련공의 오브**(증강물 홈 추가, 보유 2개) 툴팁도 확인했다. '
    '즉 이 구간은 후보 검토와 홈 확보 수단 확인까지이고, 실제로 어느 장비에 박았는지는 다른 구간에서 확인해야 한다. '
    '룬은 회수가 안 되므로 대상 선택 자체가 판단 정보라는 점은 그대로다 |'
)


def replace_row(text, key, new_row):
    lines = text.split('\n')
    for i, line in enumerate(lines):
        if line.startswith(key):
            lines[i] = new_row
            return '\n'.join(lines), True
    return text, False


def main():
    pf = HERE / 'precision_findings.py'
    src = pf.read_text(encoding='utf-8')
    if 'C,9158' not in src:
        cut = src.rstrip().rfind(']')
        pf.write_text(src[:cut] + NEW_ROWS + src[cut:], encoding='utf-8')
        print('rows added')
    else:
        print('rows already present')

    rf = HERE / 'research_focus.py'
    src = rf.read_text(encoding='utf-8')
    src, ok = replace_row(src, '| 2 | 상위 철 룬을 어느 장비에 박았는가', PENDING_RUNE)
    rf.write_text(src, encoding='utf-8')
    print('rune pending replaced:', ok)


if __name__ == '__main__':
    main()
