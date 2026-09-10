"""Session 5g: 9/8 pre-F meta skill (회피 구르기 시 시전) support window, cleanly anchored."""
from pathlib import Path
HERE = Path(__file__).resolve().parent

NEW_ROWS = """ (E,13160,'9월8일 89레벨 스킬 창에서 **회피 구르기 시 시전의 보조 젬 선택 창**을 열었다(빌드 검색 결과 창에는 "선택한 빌드 계획에 이 유형의 항목이 포함되어 있지 않습니다"). 좌측에 **범위 확대 II** 보조 툴팁이 떠 있다(유형 봉인, 효과 범위 증가, 소모 배율130%, 보조 요구사항 +5 지능(65), 효과 범위가 있는 격발에 적용되어 효과 범위45% 증가). 좌측 스킬 목록은 지옥불 함성Lv9·가스 유탄Lv12 등이고 보조 젬 사용량은 힘(7/23)·민첩(5/13)·지능(12/30), 빌드 필터 Interludes / End Game, 골드23034다. 우측 소지품에 지팡이 한 자루가 보인다.','9월8일 메타 스킬 보조 선택 확인','**9월8일의 발동 메타 스킬은 회피 구르기 시 시전이고 그 보조를 고르는 화면이다.** 범위 확대 II(효과 범위45%)는 지대형 발동에 넓힘을 주는 후보다. 이 스킬은 F에서 원소 상태 이상 시 시전으로 교체되므로, 여기 보조 후보를 F 최종 보조와 같다고 단정하지 않는다.'),
"""

def main():
    pf = HERE / 'precision_findings.py'
    src = pf.read_text(encoding='utf-8')
    if '(E,13160,' in src:
        print('already patched'); return
    cut = src.rstrip().rfind(']')
    pf.write_text(src[:cut] + NEW_ROWS + src[cut:], encoding='utf-8')
    print('rows added')

if __name__ == '__main__':
    main()
