# -*- coding: utf-8 -*-
"""한국어 번역 가이드 docx 의 게임 용어 오역을 영문 원본 대조로 교정한다.

왜 대조가 필요한가:
    기계번역 결과에는 한 단어가 두 뜻으로 뭉개진 자리가 있다. `손상` 은 corrupt(타락)와
    damage(피해) 양쪽에서 나왔고, `해상도` 는 resistance 다. 맹목적 find/replace 로는
    반드시 한쪽을 틀린다. 영문 원본과 문단이 1:1 로 맞으므로, **같은 문단의 영문에
    근거 단어가 있을 때만** 치환해서 이 문제를 없앤다.

무엇을 하지 않는가:
    - 아이템·유니크·스킬 고유명사는 건드리지 않는다. 이미 공식 한국어명이 들어가 있다
      (레포 `data/poe_translations.json` 대조로 확인).
    - 어순·문장 구조는 손대지 않는다. 그건 재번역이지 용어 교정이 아니다.
    - 공식 한국어명을 확인하지 못한 영문은 그대로 둔다. 추측 번역은 오역보다 나쁘다.

서식 보존:
    치환은 run(`<w:t>`) 내부에서만 한다. run 을 합치면 굵게·링크 같은 인라인 서식이
    날아간다. run 경계에 걸린 표현은 고치지 않고 보고한다.

실행:
    python python/scripts/fix_guide_translation.py --english EN.docx --korean KO.docx --out OUT.docx
    python python/scripts/fix_guide_translation.py ... --report corrections.md
"""

from __future__ import annotations

import argparse
import logging
import re
import sys
import zipfile
from pathlib import Path
from typing import NamedTuple

logger = logging.getLogger("fix_guide_translation")


class Rule(NamedTuple):
    """(틀린 표현 → 바른 표현), 단 같은 문단 영문이 `evidence` 에 걸릴 때만 적용."""

    wrong: str
    right: str
    evidence: str
    reason: str


# 적용 순서가 의미를 가진다 — 긴 표현을 먼저 둬야 짧은 규칙이 그 안을 잘라먹지 않는다.
RULES: tuple[Rule, ...] = (
    # --- 저항(resistance) ---
    Rule("All Elemental 해상도", "모든 원소 저항", r"All Elemental res", "미번역 + res 오역"),
    Rule("All Elemental Res", "모든 원소 저항", r"All Elemental Res", "미번역"),
    Rule("입술 문신", "저항 문신", r"res tattoo", "res 를 '입술'로 오역"),
    Rule("화염 입술", "화염 저항", r"[Ff]ire res", "res 를 '입술'로 오역"),
    Rule("화염 res", "화염 저항", r"[Ff]ire res", "res 미번역"),
    Rule("해상도", "저항", r"\bres\b|\bRes\b|resist", "resistance 를 '해상도'로 오역"),

    # --- 생명력(Life) / 막기(Block) ---
    Rule("블록당 750 라이프", "막기당 생명력 750", r"750 life", "Life 음차"),
    Rule("블록에서 % 생명력 회복", "막기 시 생명력 % 회복", r"Life on Block", "Block 음차"),
    Rule("블록 수명", "막기 시 생명력", r"life-on-block", "life-on-block 오역"),
    Rule("블록을 제한하면", "막기를 최대치로 올리면", r"cap block", "cap block 오역"),
    Rule("블록도 없고", "막기도 없고", r"[Nn]o block", "Block 음차"),
    Rule("Block Chance", "막기 확률", r"Block Chance", "미번역"),
    Rule("라이프 캐릭터", "생명력 캐릭터", r"life character", "Life 음차"),
    Rule("수명", "생명력", r"\bLife\b|\blife\b", "Life 를 '수명'으로 오역"),

    # --- 재조합(Recombinator) ---
    Rule("재결합", "재조합", r"recomb", "Recombinator 는 '재조합'"),

    # --- 분열(Fractured) ---
    # 공식 한국어에서 균열 = Breach 다. Fractured 를 '균열'로 옮기면 두 메커니즘이 겹친다.
    Rule("골절", "분열", r"[Ff]racture", "Fracture 오역. Fractured=분열, 균열은 Breach"),

    # --- 타락(Corrupted) vs 피해(Damage) — 둘 다 '손상'으로 뭉개져 있었다 ---
    Rule("이중으로 손상된 고유 아이템", "이중 타락 유니크", r"[Dd]ouble corrupt", "corrupt 를 '손상'으로 오역"),
    Rule("손상된 카옴의 심장", "타락한 카옴의 심장", r"corrupted Kaom", "corrupted 를 '손상'으로 오역"),
    Rule("이중 손상됨", "이중 타락", r"[Dd]ouble corrupt", "corrupt 를 '손상'으로 오역"),
    Rule("좋은 손상이", "좋은 타락이", r"corruption", "corruption 을 '손상'으로 오역"),
    Rule("AOE 손상", "AOE 피해", r"AOE damage", "damage 를 '손상'으로 오역"),
    Rule("데미지", "피해", r"damage", "damage 음차"),

    # --- 엑잘트 슬램(Exalt slam) / 제작(craft) ---
    Rule("보트 승영 강타", "보트 엑잘트 슬램", r"Exalt Slam|Exalt slam", "Exalt 를 '승영'으로 오역"),
    Rule("보트 승영 슬램", "보트 엑잘트 슬램", r"Exalt slam|Exalt Slam", "Exalt 를 '승영'으로 오역"),
    Rule("보트 승강 슬램", "보트 엑잘트 슬램", r"Exalt slam|Exalt Slam", "Exalt 를 '승강'으로 오역"),
    Rule("보트 승강 강타", "보트 엑잘트 슬램", r"Exalt Slam|Exalt slam", "Exalt 를 '승강'으로 오역"),
    Rule("Ducat 공예", "Ducat 제작", r"Ducat craft", "craft 를 '공예'로 오역"),
    Rule("보트 공예", "보트 제작", r"[Bb]oat craft", "craft 표기가 갈림"),
    Rule("공예를 사용", "제작을 사용", r"craft", "craft 를 '공예'로 오역"),

    # --- 기타 게임 어휘 ---
    Rule("강도 문신", "힘 문신", r"Strength tattoo", "Strength 를 '강도'로 오역"),
    Rule("전쟁도 없습니다", "전투의 함성도 없습니다", r"warcr", "warcries 를 '전쟁'으로 오역"),
    Rule("나무를 구부리는 방법", "트리를 어떻게 배분하는지", r"flex your tree", "tree 를 '나무'로 오역"),
    Rule("다목적 Combatant", "다재다능한 전투가", r"Versatile Combatant", "미번역"),
    Rule("무형성", "비실체화", r"ntangib", "intangibility 직역"),
    Rule("무형", "비실체화", r"ntangib", "intangibility 직역"),

    # --- 배신(Betrayal) — 근거: Docs/2026-08-19_LUMINARY_BOT_SSF_ATLAS_TREE_AND_BETRAYAL.md §5 ---
    Rule("6월 찬스 100%", "준(Jun) 확률 100%", r"Jun chance", "배신 마스터 Jun 을 '6월'로 오역"),
    Rule("언덕을 어디든지 갈 수 있습니다", "힐록은 아무 부서에나 배치",
         r"Hillock to anywhere", "배신 멤버 Hillock 을 '언덕'으로 오역"),
    Rule("고대 오브 30개 충돌 연구입니다",
         "고대의 오브 30개를 슬램하기 위한 연구(Research) 부서입니다",
         r"Research for 30 Ancient Orbs slamming", "slam 을 '충돌'로 오역"),
    Rule("Riker에서 Research OR Forti OR Transport로",
         "Riker 를 연구(Research) / 요새(Fortification) / 운송(Transportation) 중 하나로",
         r"Riker to Research", "배신 부서명 미번역"),
    Rule("Leo에서 Forti까지", "Leo 를 요새(Fortification) 부서로", r"Leo to Forti", "배신 부서명 미번역"),
    Rule("상인 라비쉬 5:1", "화려한 생명의 결실 5개를 상인에게 판매(5→1 교환)",
         r"Vendor Lavish 5 to 1", "Lavish 를 'Ravish' 로 오독한 음차"),
    Rule("41레벨 도박", "41레벨 셉터 도박", r"level 41 gambling", "닉타의 등불 요구 레벨 41 셉터 도박"),
)


class Change(NamedTuple):
    paragraph: int
    rule: Rule
    applied: bool


def _namespace_prefix(xml: str) -> str:
    """docx 를 파이썬 도구로 다시 저장하면 접두사가 w: 가 아니라 ns0: 가 된다."""
    return "ns0" if "<ns0:p" in xml else "w"


def read_document_xml(path: Path) -> str:
    with zipfile.ZipFile(path) as archive:
        return archive.read("word/document.xml").decode("utf-8")


def paragraph_texts(xml: str) -> list[str]:
    prefix = _namespace_prefix(xml)
    texts = []
    for para in re.findall(rf"<{prefix}:p[ >].*?</{prefix}:p>", xml, re.S):
        joined = "".join(re.findall(rf"<{prefix}:t[^>]*>(.*?)</{prefix}:t>", para, re.S))
        texts.append(re.sub(r"<[^>]+>", "", joined))
    return texts


def applicable_rules(korean: str, english: str, rules: tuple[Rule, ...] = RULES) -> list[Rule]:
    """근거가 확인된 규칙만. 이 함수 하나가 오역 교정의 안전장치 전부다."""
    return [r for r in rules if r.wrong in korean and re.search(r.evidence, english)]


def correct_document(xml: str, english_paragraphs: list[str],
                     rules: tuple[Rule, ...] = RULES) -> tuple[str, list[Change]]:
    prefix = _namespace_prefix(xml)
    para_pattern = re.compile(rf"<{prefix}:p[ >].*?</{prefix}:p>", re.S)
    run_pattern = re.compile(rf"(<{prefix}:t[^>]*>)(.*?)(</{prefix}:t>)", re.S)

    changes: list[Change] = []
    index = -1

    def correct_paragraph(match: re.Match) -> str:
        nonlocal index
        index += 1
        para = match.group(0)
        english = english_paragraphs[index] if index < len(english_paragraphs) else ""
        korean = "".join(body for _, body, _ in run_pattern.findall(para))

        selected = applicable_rules(korean, english, rules)
        if not selected:
            return para

        def correct_run(run: re.Match) -> str:
            open_tag, body, close_tag = run.groups()
            for rule in selected:
                body = body.replace(rule.wrong, rule.right)
            return f"{open_tag}{body}{close_tag}"

        updated = run_pattern.sub(correct_run, para)

        # 남았는지는 치환 **후** 본문으로 본다. 치환 전으로 보면 앞 규칙에 흡수된
        # 표현('무형성'→'비실체화' 뒤의 '무형')까지 미적용으로 오보한다.
        remaining = "".join(body for _, body, _ in run_pattern.findall(updated))
        for rule in selected:
            changes.append(Change(index, rule, applied=rule.wrong not in remaining))
        return updated

    return para_pattern.sub(correct_paragraph, xml), changes


def write_document(source: Path, target: Path, document_xml: str) -> None:
    """document.xml 만 갈아끼우고 나머지 파트(이미지·스타일·링크)는 바이트 그대로 옮긴다."""
    with zipfile.ZipFile(source) as archive:
        parts = [(info, archive.read(info.filename)) for info in archive.infolist()]
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as out:
        for info, payload in parts:
            body = document_xml.encode("utf-8") if info.filename == "word/document.xml" else payload
            out.writestr(info, body)


def render_report(changes: list[Change]) -> str:
    lines = ["# 용어 교정 대조표", "", "| 문단 | 오역 | 교정 | 사유 | 적용 |", "|---|---|---|---|---|"]
    for change in changes:
        mark = "O" if change.applied else "X (run 경계)"
        lines.append(
            f"| {change.paragraph} | {change.rule.wrong} | {change.rule.right} "
            f"| {change.rule.reason} | {mark} |"
        )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--english", type=Path, required=True, help="영문 원본 docx (근거)")
    parser.add_argument("--korean", type=Path, required=True, help="교정할 한국어 번역 docx")
    parser.add_argument("--out", type=Path, required=True, help="교정본 출력 경로")
    parser.add_argument("--report", type=Path, help="변경 대조표 마크다운 출력 경로")
    args = parser.parse_args(argv)

    for path in (args.english, args.korean):
        if not path.is_file():
            logger.error("파일 없음: %s", path)
            return 2

    english_xml = read_document_xml(args.english)
    korean_xml = read_document_xml(args.korean)
    english = paragraph_texts(english_xml)
    korean = paragraph_texts(korean_xml)

    if len(english) != len(korean):
        logger.error(
            "문단 정렬 불일치 EN=%d KO=%d — 대조 교정을 할 수 없다. "
            "두 문서가 같은 판본에서 나온 것인지 확인할 것.", len(english), len(korean),
        )
        return 2

    corrected, changes = correct_document(korean_xml, english)
    write_document(args.korean, args.out, corrected)

    applied = [c for c in changes if c.applied]
    skipped = [c for c in changes if not c.applied]
    if args.report:
        args.report.write_text(render_report(changes), encoding="utf-8")
        logger.info("대조표 %s", args.report)

    logger.info("문단 %d | 교정 %d건 | run 경계로 미적용 %d건", len(korean), len(applied), len(skipped))
    for change in skipped:
        logger.warning("미적용 p%d: %s -> %s", change.paragraph, change.rule.wrong, change.rule.right)
    logger.info("출력 %s", args.out)
    return 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s", stream=sys.stderr)
    raise SystemExit(main())
