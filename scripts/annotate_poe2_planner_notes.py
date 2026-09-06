"""설치된 젬링 플래너의 장비 슬롯에 제작자 방송 발언을 주석으로 붙인다.

왜 슬롯에 붙이나: `.build` 포맷에서 자유 텍스트를 담을 수 있는 곳은 장비 슬롯의
`additional_text` 하나뿐이다. 최상위에 note 필드가 없고, 패시브는 id 만, 스킬은
id + level_interval 만 갖는다. 그래서 "액트2 EHP 600" 같은 슬롯과 무관한 지침도
가장 가까운 슬롯(몸통 = 생존)에 붙인다.

무엇을 건드리지 않나: `passives` · `skills` · `inventory_id` · `level_interval` ·
슬롯 좌표. 오직 `additional_text` 끝에만 덧붙인다. 그래서 트리와 젬은 제작자 정본
그대로 남고, 이 스크립트를 여러 번 돌려도 결과가 같다(붙인 블록을 먼저 걷어낸다).

출처: `Docs/2026-09-06_SEONGBIN_FLAMEBLAST_GEMLING_0_5_5_LIVE_MINING_RAW.json` (방송 3편 자막 채굴 293건을
GGPK·패치노트·플래너 정본으로 판정한 것) + 그의 가이드 영상 자막.
문장은 그의 말을 줄인 것이고, 내 판단을 섞지 않는다.
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import pathlib
import sys

log = logging.getLogger("annotate")

GAME_DIR = pathlib.Path(os.path.expandvars(
    r"%USERPROFILE%\Documents\My Games\Path of Exile 2\BuildPlanner"))

MARK = "— 방송 —"  # 이 줄부터 아래가 우리가 붙인 블록. 재실행 때 이걸로 잘라낸다.

# 파일 -> 슬롯 -> 줄 목록. 슬롯이 여러 개인 id(Flask1·Charm1·Ring1)는 첫 번째에만 붙는다.
NOTES: dict[str, dict[str, list[str]]] = {
    "HC 1 Act1 - Seongbin.build": {
        "Weapon1": [
            "화폐는 방어구보다 석궁에 먼저 쓴다. 옵션은 상관없고 피해량만.",
            "사다리 임시1 · 팽팽4 · 튼튼10 · 광택16.",
            "10레벨 튼튼한 석궁 하나로 액트1 최종보스까지 간다.",
            "파편탄(요구 1)은 가스 유탄 습득 전, 특히 보스전의 유탄 쿨 공백을 메운다.",
            "가스 유탄을 배운 뒤 공백이 거의 없으면 빼도 되고, 남으면 유지한다.",
        ],
        "Helm1": [
            "회피가 붙은 베이스는 버린다. 초반엔 튕겨내기가 없어 의미가 없다.",
            "%보다 플랫이 낫다. 특히 에너지 보호막 플랫이 효율이 좋다.",
            "생명력이 안 달린 장비는 후보에서 뺀다.",
        ],
        "BodyArmour1": [
            "임계치(그의 말 · 추정) — 초반 그 무렵 생명력 200.",
            "오검 마을 진입 생명력+ES 300(단두대에 안 죽는 선).",
            "처형자 직전 400. 지오노 백작은 300 넘으면 한 방에 안 죽는다.",
            "백작 회피 패턴 3개 — 내려찍기 · 칼 치기 · 칼 크게 휘두르기.",
        ],
        "Gloves1": [
            "뒤에 하위 육신의 룬(드롭 11)을 낄 자리라 소켓을 미리 뚫어 둔다.",
            "옵션 잘 뜬 아이템엔 숙련공의 오브를 아끼지 말고 바로 쓴다.",
        ],
        "Boots1": [
            "이동 속도 + 에너지 보호막 두 개 붙은 게 최고.",
        ],
        "Amulet1": [
            "장신구는 뜨는 대로 껴도 충분하다. 반지는 플랫 피해를 본다.",
        ],
        "Flask1": [
            "즉시 회복 옵션을 챙긴다.",
            "수시로 마시고 업그레이드를 미루지 마라 — 미뤘다가 죽을 뻔했다.",
        ],
        "Charm1": [
            "하드코어에서 사람을 죽이는 건 평균 피해가 아니라 상태이상 한 방이다.",
        ],
        "Belt1": [
            "위험 지역 — 저택 성벽은 출혈로 두 번 죽을 뻔했다. 파밍 없이 스킵.",
            "출혈에 걸리면 에너지 보호막이 재충전을 안 한다.",
            "집정관 계열이 까는 바닥 장판이 잔디밭에서는 아예 안 보인다.",
        ],
        "Ring1": [
            "동선 — 까마귀 잡고 프레이손(11)부터. 재의 전령을 먼저 먹는다.",
            "오검 농지(12)는 찍어만 두고 나중. 처형자 전에 대장장이 랠리부터.",
        ],
    },
    "HC 2 Act2 - Seongbin.build": {
        "Weapon1": [
            "광택 나는 석궁(16)으로 갈아타되 롤이 안 따라주면 기존 것을 유지한다.",
            "베이스 레벨보다 롤이 우선. 물리 피해 티어를 본다.",
            "33레벨 폭격 석궁이 뜰 때까지 이걸로 버틴다.",
        ],
        "BodyArmour1": [
            "임계치(그의 말 · \"체감상\") — 이 구간에서 600. 거신 내려찍기를 한 방에 안 맞는 선.",
            "액트2 최종보스도 600이면 아슬아슬하다.",
            "보스 회피 패턴 — 대검 내리꽂기 · 등 뒤 창 꽂기 · 크게 휘두르기.",
        ],
        "Helm1": [
            "액트2 진입 직후 첫 의식에서 초반 러너들이 대거 죽었다.",
            "은주 한 방이 약 900. 생명력+ES 900이면 한 대 견딘다 — 단 그가 바로 뒤에",
            "\"방어도에 따라 달라진다\"고 덧붙였다. 그는 여유로 1100 확보.",
            "은주 · 바이퍼 · 베네딕투스 셋은 지금 잡지 않는다.",
            "맵핑 가서 화염파 배우고 돌아와서 처리한다. 목숨 걸 보상이 아니다.",
        ],
        "Gloves1": [
            "갑옷은 퀄리티도 올려 최고품질로. 재료는 희귀몹 한 마리당 하나꼴.",
        ],
        "Boots1": [
            "창 든 잡몹에 이동 속도가 깎인 상태에서 희귀몹 슬램은 미니 은주급이다.",
        ],
        "Amulet1": [
            "목걸이는 생명력과 저항을 챙기기 좋은 부위다. 둘 다 신경 쓴다.",
        ],
        "Ring2": [
            "액트2는 화염 보스가 많다. 냉기 저항을 내리고 루비 반지로 바꾼다.",
        ],
        "Belt1": [
            "전직 — 세케마 시련이 1차. 그의 플래너는 여기서 미덕의 정수를 찍는다.",
            "2차는 저절로 안 열린다. 시련을 한 번 더 깨야 한다(스킵했다가 되돌아갔다).",
            "2차 타이밍은 바이퍼 직전. 그 구간부터 불안해진다.",
            "퀄리티 화폐는 화염파에 쓸 것이라 아껴 둔다.",
        ],
        "Flask1": [
            "즉시 회복. 이 옵션이 없었으면 세 번은 죽었다고 했다.",
        ],
    },
    "HC 3 Act3-4 - Seongbin.build": {
        "Weapon1": [
            "폭격 석궁을 낀 뒤로는 무기를 안 건드리고 방어구만 챙긴다.",
            "실제로 33~58 구간에 무기 교체 계획이 0건이다.",
            "투사체 레벨 옵션이 붙으면 그걸로 강화한다.",
        ],
        "BodyArmour1": [
            "접두는 생명력보다 방어도와 에너지 보호막이 중요해진다.",
            "접미는 원소·카오스 저항 + '방어도가 원소 피해에도 적용'을 추천.",
            "이 구간에 변이하는 별(성직자의 법의)을 낄 수 있다. 구하면 15등급 프리패스.",
        ],
        "Boots1": [
            "신발은 최우선 교체 대상. 38레벨에 16레벨 신발이면 매우 답답하다.",
            "이동 속도가 없으면 안 된다.",
        ],
        "Flask1": [
            "플라스크 접미어가 이 시점부터 중요해진다.",
            "회복량 50% 감소 + 즉시 회복 — 급락할 때 즉각 회복이 생존을 만든다.",
        ],
        "Ring1": [
            "카오스 피해가 아프기 시작한다. 카오스 저항을 챙긴다.",
        ],
        "Amulet1": [
            "주얼러 오브로 소켓을 늘려 보조젬을 추가한다.",
        ],
        "Helm1": [
            "젬링은 능력치 요구치가 병목이다. 못 껴서 트리에서 지능을 더 찍는 일이 잦다.",
        ],
    },
    "HC 4b 실캐릭 막간 - 임성빈.build": {
        "Weapon2": [
            "52 전환 전에 미리 지팡이를 구해 둔다. 그때 가서 구하면 늦는다.",
            "화염 전용 = Ashen(1) · Pyrophyte(16). 범용 = Spriggan(11) · Chiming(25) 등.",
            "Gelid · Voltaic · Rending · Reaping · Icicle · Paralysing 은 화염이 안 굴러 죽은 카드.",
        ],
        "Weapon1": [
            "세트1 = 기름 유탄 + 회오리. 세트2 = 화염파.",
        ],
        "Helm1": [
            "로테이션 — 기름 유탄으로 기름 지대를 깔고 화염파 최대 집중으로 점화 지대를 만든다.",
            "이후 기름 유탄으로 점화 지대를 넓혀 간다. 공중 몹에만 회오리.",
        ],
        "Gloves1": [
            "약한 점화 오염 — 아르세리나 2026-09-06 테스트. 회오리가 주범이다.",
            "회오리는 원소 지대 디버프를 흡수해 안의 적에게 건다(스킬 원문). 점화 지대에서",
            "쓰면 3~6%씩 쌓이다 약한 점화가 나고, 그게 기름 지대로 전달된다.",
            "구르기에 회오리를 연결한 자동 시전이 제일 위험하다. 공중 몹에만 최소로 쓴다.",
        ],
        "Charm1": [
            "약한 점화 원인 점검 — 기름 유탄 스킬창에 화염 피해가 뜨면 안 된다.",
            "가시처럼 스킬창에 안 뜨는 피해는 장비를 직접 본다.",
            "한기의 방어구(Arctic Armour)는 피격 시 냉기 주문 피해를 주는데,",
            "지팡이에 '화염 피해로 추가'가 있으면 거기에도 화염이 섞여 점화를 만든다.",
        ],
        "Belt1": [
            "맵의 점화 지대와 '불의 발자취' 몹이 만든 점화는 기름 지대로 안 옮겨붙는다(테스트).",
            "오염됐다 싶으면 그 지대를 이어가지 말고 자리를 옮겨 화염파로 새로 강한 점화를 만든다.",
        ],
        "BodyArmour1": [
            "트리 전환에 골드가 든다. 가이드 영상은 최소 10만, 방송은 3~5만이라 했다.",
            "(내 권고) 두 숫자가 갈리니 하드코어면 10만으로 잡는다.",
            "액트1부터 잡템을 팔아 모으는 이유가 이것.",
        ],
        "Boots1": [
            "그가 꼽은 주 사인 — 기름 유탄 깔고 구르는 조작이 몸을 앞으로 끌어",
            "채널링이 끊기고 둘러싸여 죽는다.",
        ],
        "Ring1": [
            "무보석 반지를 끼고 스킬을 넣은 뒤 반지를 빼도 스킬이 장착된 채로 남는다.",
            "실제 사용은 안 되지만 미덕의 정수 어센던시에는 그대로 적용된다.",
        ],
    },
    "HC 6 Endgame - Seongbin.build": {
        "Weapon1": [
            "화염파만으로 94~96레벨까지는 무난하다.",
            "전환 아이템 수급이 늦으면 100레벨까지도 화염파로 간다.",
        ],
        "Helm1": [
            "시즌 첫날부터 15티어까지 갈 수 있는 드문 빌드라고 본인이 평가한다.",
        ],
    },
}


def strip_block(text: str) -> str:
    """이전에 붙인 블록을 걷어낸다 — 재실행해도 같은 결과가 나오게."""
    idx = text.find(MARK)
    return text if idx < 0 else text[:idx].rstrip("\n")


def annotate(path: pathlib.Path, notes: dict[str, list[str]], dry: bool) -> int:
    data = json.loads(path.read_text(encoding="utf-8"))
    before = json.dumps([data["passives"], data["skills"]], ensure_ascii=False, sort_keys=True)
    used: set[str] = set()
    touched = 0
    for slot in data.get("inventory_slots", []):
        sid = slot.get("inventory_id") or ""
        lines = notes.get(sid)
        if not lines or sid in used:
            continue
        used.add(sid)
        body = strip_block(slot.get("additional_text") or "")
        # 빈 슬롯이면 첫 줄을 비워 둔다 — 첫 줄은 베이스 이름 자리라
        # 여기에 글이 들어가면 `creator_bases` 가 그것을 베이스로 읽는다.
        head = body if body else ""
        slot["additional_text"] = "\n".join([head, MARK, *lines]).lstrip("\n") if body \
            else "\n".join(["", MARK, *lines])
        touched += 1
    missing = set(notes) - used
    if missing:
        # 슬롯 이름이 틀리면 그 주석은 영영 안 보인다. 조용히 넘기지 않는다.
        raise SystemExit(f"{path.name}: 플래너에 없는 슬롯 {sorted(missing)}")
    after = json.dumps([data["passives"], data["skills"]], ensure_ascii=False, sort_keys=True)
    if before != after:
        raise SystemExit(f"{path.name}: 트리나 젬이 바뀌었다 — 주석만 붙여야 한다")
    if not dry:
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    log.info("%s: 슬롯 %d개에 주석", path.name, touched)
    return touched


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=str(GAME_DIR))
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    root = pathlib.Path(args.dir)
    total = 0
    for fname, notes in NOTES.items():
        path = root / fname
        if not path.exists():
            raise SystemExit(f"없는 플래너: {path}")
        total += annotate(path, notes, args.dry_run)
    log.info("합계 슬롯 %d개%s", total, " (dry-run)" if args.dry_run else "")
    return 0


if __name__ == "__main__":
    sys.exit(main())
