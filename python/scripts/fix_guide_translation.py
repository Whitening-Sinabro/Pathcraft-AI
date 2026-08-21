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
    - 어순·문장 구조는 치환 규칙으로 손대지 않는다. 그건 재번역이지 용어 교정이 아니다.
      어순이 무너져 문장이 성립하지 않는 문단은 `guide_retranslations.RETRANSLATIONS`
      가 영문 원문을 키로 통째로 교체한다 — 두 층은 서로 침범하지 않는다.
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
from xml.sax.saxutils import escape

sys.path.insert(0, str(Path(__file__).resolve().parent))
from guide_terms import RULES, Rule  # noqa: E402  (하위 호환 재수출)
from guide_retranslations import (  # noqa: E402
    RETRANSLATIONS,
    Retranslation,
    normalize_english,
    retranslation_index,
)

logger = logging.getLogger("fix_guide_translation")


class Change(NamedTuple):
    paragraph: int
    rule: Rule
    applied: bool


class Rewrite(NamedTuple):
    """문단 통째 교체 한 건. 미적용이면 왜 못 했는지가 남는다."""

    paragraph: int
    retranslation: Retranslation
    applied: bool
    skipped_because: str = ""


def _namespace_prefix(xml: str) -> str:
    """docx 를 파이썬 도구로 다시 저장하면 접두사가 w: 가 아니라 ns0: 가 된다."""
    return "ns0" if "<ns0:p" in xml else "w"


def _paragraph_pattern(prefix: str) -> re.Pattern[str]:
    return re.compile(rf"<{prefix}:p[ >].*?</{prefix}:p>", re.S)


def _text_run_pattern(prefix: str) -> re.Pattern[str]:
    """여는 `<w:t>` 만 잡는다.

    두 종류의 오탐을 막아야 한다. `[^>]*` 로 열어두면 `<w:tcPr>` 같은 표 서식 태그를
    여는 태그로 착각하고, 자기완결 태그 `<w:t xml:space="preserve" />` 도 여는 태그로
    본다. 어느 쪽이든 `.*?` 가 다음 `</w:t>` 까지 마크업을 통째로 삼켜서, 본문인 줄 알고
    거기에 글자를 써 넣으면 문서가 깨진다.
    """
    return re.compile(
        rf"(<{prefix}:t(?![^>]*/>)(?:\s[^>]*)?>)(.*?)(</{prefix}:t>)", re.S
    )


def _hyperlink_spans(paragraph: str, prefix: str) -> list[tuple[int, int]]:
    pattern = re.compile(rf"<{prefix}:hyperlink[ >].*?</{prefix}:hyperlink>", re.S)
    return [m.span() for m in pattern.finditer(paragraph)]


def replaceable_run_spans(paragraph: str, prefix: str,
                          include_links: bool = False) -> list[tuple[int, int]]:
    """통째 교체해도 안전한 run 본문 구간.

    링크 안의 run 은 손대지 않는다 — 텍스트를 갈면 링크 표시 문구가 사라진다.
    글자가 있는 run 을 먼저 후보로 세우고, 하나도 없으면 그때만 공백 run 을 쓴다.
    링크만 있는 문단(`https://... for Breach and Div cards wheel`)은 설명이 링크 뒤
    공백 run 자리에 들어가야 하므로, 이 대체 경로가 없으면 설명을 영영 못 붙인다.

    후보가 둘 이상이면 포기한다. 어느 run 이 굵게이고 어느 run 이 링크 색인지 모르는
    상태에서 하나로 합치면 인라인 서식이 조용히 뭉개진다.
    """
    links = [] if include_links else _hyperlink_spans(paragraph, prefix)
    outside = [
        (match.span(2), match.group(2))
        for match in _text_run_pattern(prefix).finditer(paragraph)
        if not any(low <= match.span(2)[0] < high for low, high in links)
    ]
    written = [span for span, body in outside if body.strip()]
    return written or [span for span, _ in outside]


def hyperlink_text(paragraph: str, prefix: str) -> str:
    """링크 run 이 그대로 들고 남을 문구.

    문단을 통째로 다시 써도 이 글자는 화면에 그대로 남는다. 재번역이 이 사실을 모르면
    두 가지로 망가진다 — 새 번역이 같은 말을 또 담으면 화면에 두 번 나오고, 링크가 옛
    오역을 들고 있으면 새 문장 옆에 유령 문구가 붙는다. 그래서 이 값을 표의 선언과
    맞춰본다.
    """
    links = _hyperlink_spans(paragraph, prefix)
    return "".join(
        match.group(2)
        for match in _text_run_pattern(prefix).finditer(paragraph)
        if any(low <= match.span(2)[0] < high for low, high in links)
    )


def read_document_xml(path: Path) -> str:
    with zipfile.ZipFile(path) as archive:
        return archive.read("word/document.xml").decode("utf-8")


def paragraph_texts(xml: str) -> list[str]:
    prefix = _namespace_prefix(xml)
    pattern = _text_run_pattern(prefix)
    return [
        "".join(body for _, body, _ in pattern.findall(para))
        for para in _paragraph_pattern(prefix).findall(xml)
    ]


def applicable_rules(korean: str, english: str, rules: tuple[Rule, ...] = RULES) -> list[Rule]:
    """근거가 확인된 규칙만. 이 함수 하나가 오역 교정의 안전장치 전부다."""
    return [r for r in rules if r.wrong in korean and re.search(r.evidence, english)]


def _link_conflict(paragraph: str, prefix: str,
                   entry: Retranslation, parts: tuple[str, ...]) -> str:
    """링크 run 이 남기는 문구와 새 번역이 충돌하면 사유를, 아니면 빈 문자열을 준다.

    `include_links` 가 켜진 자리는 링크 문구까지 다시 쓰므로 남는 글자가 없다 — 검사 대상이
    아니다. 나머지는 링크가 들고 있는 글자를 표가 `link_label` 로 **선언했을 때만** 통과시킨다.
    선언을 강제하는 이유는, 링크에 옛 오역이 남는 사고(`럭셔리 업그레이드` + `사치 업그레이드`)를
    기계가 스스로 알아볼 방법이 없기 때문이다. 링크 문구가 라벨(`[제작 가이드 보기]`)인지 갈아야
    할 오역인지는 사람만 구분할 수 있으므로, 사람이 한 번 보고 적어두게 만든다.
    """
    if entry.include_links:
        return ""

    kept = hyperlink_text(paragraph, prefix).strip()
    declared = entry.link_label.strip()

    if kept and kept in "".join(parts):
        return (f"링크 run 이 이미 '{kept}' 를 보여주는데 새 번역도 같은 글자를 담고 있다 "
                "— 화면에 두 번 나온다")
    if kept != declared:
        return (f"링크 run 이 '{kept}' 를 그대로 들고 남는데 표의 link_label 선언은 "
                f"'{declared}' 다 — 선언이 맞는지 확인하기 전에는 쓰지 않는다")
    return ""


def retranslate_document(
    xml: str, english_paragraphs: list[str],
    table: tuple[Retranslation, ...] = RETRANSLATIONS,
) -> tuple[str, list[Rewrite]]:
    """어순이 무너진 문단을 영문 원문 대조로 통째 교체한다.

    치환 규칙(`correct_document`)보다 먼저 돌린다. 여기서 다시 쓴 문단에는 애초에
    고칠 오역이 남지 않으므로 두 층이 같은 자리를 두고 다투지 않는다.
    """
    prefix = _namespace_prefix(xml)
    index = retranslation_index(table)

    rewrites: list[Rewrite] = []
    matched: set[str] = set()
    position = -1

    def rewrite_paragraph(match: re.Match) -> str:
        nonlocal position
        position += 1
        para = match.group(0)
        english = english_paragraphs[position] if position < len(english_paragraphs) else ""
        key = normalize_english(english)
        entry = index.get(key)
        if entry is None:
            return para
        matched.add(key)

        parts = entry.korean if isinstance(entry.korean, tuple) else (entry.korean,)

        refusal = _link_conflict(para, prefix, entry, parts)
        if refusal:
            rewrites.append(Rewrite(position, entry, applied=False, skipped_because=refusal))
            return para

        targets = replaceable_run_spans(para, prefix, entry.include_links)
        if len(targets) != len(parts):
            rewrites.append(Rewrite(
                position, entry, applied=False,
                skipped_because=(f"교체 대상 run {len(targets)}개 vs 준비된 조각 {len(parts)}개 "
                                 "— 인라인 서식 경계를 모르는 채 합치지 않는다"),
            ))
            return para

        # 뒤에서부터 갈아야 앞 구간의 좌표가 밀리지 않는다.
        updated = para
        for (start, end), text in sorted(zip(targets, parts), key=lambda x: -x[0][0]):
            updated = updated[:start] + escape(text) + updated[end:]
        rewrites.append(Rewrite(position, entry, applied=True))
        return updated

    rewritten = _paragraph_pattern(prefix).sub(rewrite_paragraph, xml)

    # 표에는 있는데 원문에서 못 찾은 항목을 조용히 넘기면, 원본이 개정됐을 때
    # "고쳤다" 는 착각만 남는다. 미적용으로 세워서 보고한다.
    for key, entry in index.items():
        if key not in matched:
            rewrites.append(Rewrite(-1, entry, applied=False,
                                    skipped_because="영문 원문에 이 문단이 없다"))

    return rewritten, rewrites


def correct_document(xml: str, english_paragraphs: list[str],
                     rules: tuple[Rule, ...] = RULES) -> tuple[str, list[Change]]:
    prefix = _namespace_prefix(xml)
    para_pattern = _paragraph_pattern(prefix)
    run_pattern = _text_run_pattern(prefix)

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


def render_report(changes: list[Change], rewrites: list[Rewrite] | None = None) -> str:
    lines = ["# 가이드 교정 대조표", ""]

    if rewrites is not None:
        lines += [
            "## 1. 문단 재번역 (어순이 무너져 통째로 다시 쓴 것)", "",
            "| 문단 | 사유 | 적용 |", "|---|---|---|",
        ]
        for rewrite in rewrites:
            where = "-" if rewrite.paragraph < 0 else str(rewrite.paragraph)
            mark = "O" if rewrite.applied else f"X ({rewrite.skipped_because})"
            lines.append(f"| {where} | {rewrite.retranslation.reason} | {mark} |")
        lines += ["", "### 재번역 전문", ""]
        for rewrite in rewrites:
            if not rewrite.applied:
                continue
            lines += [
                f"- **p{rewrite.paragraph}** EN: {rewrite.retranslation.english}",
                f"  - KO: {rewrite.retranslation.korean}",
            ]
        lines += ["", "## 2. 용어 치환", ""]

    lines += ["| 문단 | 오역 | 교정 | 사유 | 적용 |", "|---|---|---|---|---|"]
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

    rewritten, rewrites = retranslate_document(korean_xml, english)
    corrected, changes = correct_document(rewritten, english)
    write_document(args.korean, args.out, corrected)

    applied = [c for c in changes if c.applied]
    skipped = [c for c in changes if not c.applied]
    rewritten_ok = [r for r in rewrites if r.applied]
    rewritten_no = [r for r in rewrites if not r.applied]
    if args.report:
        args.report.write_text(render_report(changes, rewrites), encoding="utf-8")
        logger.info("대조표 %s", args.report)

    logger.info("문단 %d | 재번역 %d건(미적용 %d) | 용어 교정 %d건(미적용 %d)",
                len(korean), len(rewritten_ok), len(rewritten_no), len(applied), len(skipped))
    for rewrite in rewritten_no:
        logger.warning("재번역 미적용 [%s]: %s", rewrite.skipped_because,
                       rewrite.retranslation.english[:70])
    for change in skipped:
        logger.warning("미적용 p%d: %s -> %s", change.paragraph, change.rule.wrong, change.rule.right)
    logger.info("출력 %s", args.out)
    return 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s", stream=sys.stderr)
    raise SystemExit(main())
