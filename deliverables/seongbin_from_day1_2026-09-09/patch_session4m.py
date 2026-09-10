"""Twelfth batch: an ailment node he could not take yet, and the uncut support stock."""
from pathlib import Path

HERE = Path(__file__).resolve().parent

NEW_ROWS = """ (F,5590,'91레벨 패시브 트리에서 **한계점** 노드 툴팁을 읽었다. 적에게 적용되는 원소 상태 이상 지속시간10% 증가, 플레이어가 유발하는 비-피해 상태 이상의 강도30% 증가이고 아래에 붉은 글씨로 **요구사항 미충족**이 떠 있다. 스킬 포인트1, 무기 세트 I·II 모두 0(24), 전직 포인트0이고 능력치는 민첩66·지능152·**힘103**이다.','후보 노드와 요구 미충족 확인','**5600·5690초의 힘은108인데 여기는103**이다. 같은 방송 안에서도 능력치가 오가므로 한 프레임의 능력치를 그 방송의 고정값으로 쓰지 않는다. 요구사항 미충족은 아직 못 찍는다는 뜻이고, 찍었다는 뜻이 아니다.'),
 (F,7240,'젬 보관함 **미가공** 탭이다. **미가공 보조 젬(5레벨)** 툴팁에 보조 젬 생성하기·사용하여 보조 젬을 새깁니다가 적혀 있고 버튼은 보조 젬 새기기·보관함에서 꺼내기다. 레벨별로1~5레벨 미가공 보조 젬이 쌓여 있고 특히1레벨이 세 줄 가득이다. 젬 탭은101/500, 골드는**507727**이다.','후반 보조 젬 재고 확인','전환 시점에 상위 쥬얼러 오브가1개뿐이라 홈이 제약이던 것과 달리, 이 시점에는 미가공 보조 젬 재고가 넉넉하다. 재고가 있다고 원하는 보조가 나오는 것은 아니므로 새기기 결과까지는 이 화면으로 알 수 없다.'),
"""


def main():
    pf = HERE / 'precision_findings.py'
    src = pf.read_text(encoding='utf-8')
    if 'F,5590' in src:
        print('already patched')
        return
    cut = src.rstrip().rfind(']')
    pf.write_text(src[:cut] + NEW_ROWS + src[cut:], encoding='utf-8')
    print('rows added')


if __name__ == '__main__':
    main()
