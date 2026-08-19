"""가이드 번역 교정 회귀 가드.

이 도구의 위험은 하나다 — **근거 없이 치환하는 것**. `손상` 하나가 corrupt(타락)와
damage(피해) 양쪽에서 나오므로, 영문 대조 없이 고치면 반드시 절반이 틀린다.
그래서 테스트의 중심도 "근거 없으면 안 고친다" 에 있다.

교정 대상 docx 는 레포 밖(사용자 Downloads)에 있으므로 여기서는 합성 XML 로 검증한다.
"""

from __future__ import annotations

import sys
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "python" / "scripts"))

from fix_guide_translation import (  # noqa: E402
    RULES,
    Rule,
    applicable_rules,
    correct_document,
    paragraph_texts,
    read_document_xml,
    render_report,
    write_document,
)


def make_xml(paragraphs: list[list[str]], prefix: str = "w") -> str:
    """문단 = run 텍스트 목록. run 을 나눠 인라인 서식 상황을 재현한다."""
    body = ""
    for runs in paragraphs:
        body += f"<{prefix}:p>"
        for text in runs:
            body += f"<{prefix}:r><{prefix}:t>{text}</{prefix}:t></{prefix}:r>"
        body += f"</{prefix}:p>"
    return f"<{prefix}:document><{prefix}:body>{body}</{prefix}:body></{prefix}:document>"


# --- 핵심: 영문 근거가 없으면 고치지 않는다 -------------------------------------


def test_no_correction_without_english_evidence():
    """같은 한국어라도 원문 근거가 없으면 손대지 않는다."""
    xml = make_xml([["화염 해상도"]])
    corrected, changes = correct_document(xml, ["Monitor resolution settings"])
    assert "화염 해상도" in corrected, "근거 없는 문단을 고쳤다"
    assert changes == []


def test_correction_applies_with_english_evidence():
    xml = make_xml([["화염 해상도"]])
    corrected, changes = correct_document(xml, ["Fire res is capped"])
    assert "화염 저항" in corrected
    assert [c.applied for c in changes] == [True]


def test_ambiguous_word_resolves_by_english_context():
    """'손상' 은 corrupt 와 damage 양쪽에서 왔다 — 문단마다 다르게 풀려야 한다."""
    xml = make_xml([["AOE 손상"], ["헬멧에 좋은 손상이 많습니다"]])
    corrected, _ = correct_document(xml, [
        "crafted AOE/AOE damage",
        "A lot of good corruptions on helmets",
    ])
    assert "AOE 피해" in corrected, "damage 문맥이 '피해'로 안 풀렸다"
    assert "좋은 타락이" in corrected, "corruption 문맥이 '타락'으로 안 풀렸다"


# --- 용어 충돌: 균열은 Breach 다 -------------------------------------------------


def test_fractured_is_not_translated_as_breach_term():
    """Fractured=분열, Breach=균열. 둘을 같은 단어로 뭉개면 메커니즘이 섞인다."""
    fracture_rule = next(r for r in RULES if r.wrong == "골절")
    assert fracture_rule.right == "분열"
    assert "균열" not in fracture_rule.right

    xml = make_xml([["골절이 적중하면"]])
    corrected, _ = correct_document(xml, ["If Fracture hits"])
    assert "분열이 적중하면" in corrected
    assert "균열" not in corrected


def test_no_rule_outputs_breach_term_for_non_breach_source():
    for rule in RULES:
        if "균열" in rule.right:
            assert "reach" in rule.evidence, f"{rule.wrong}: 균열은 Breach 에만 쓸 것"


# --- 서식 보존 ------------------------------------------------------------------


def test_runs_are_preserved_not_merged():
    """run 을 합치면 굵게·링크가 날아간다. 구조가 그대로여야 한다."""
    xml = make_xml([["화염 해상도", " 그리고 ", "카오스 해상도"]])
    corrected, _ = correct_document(xml, ["Fire res and Chaos res"])
    assert corrected.count("<w:t>") == 3, "run 이 합쳐졌다 — 인라인 서식 손실"
    assert "화염 저항" in corrected and "카오스 저항" in corrected


def test_expression_split_across_runs_is_reported_not_silently_dropped():
    """run 경계에 걸려 못 고친 건 조용히 넘어가면 안 된다."""
    xml = make_xml([["화염 해", "상도"]])
    corrected, changes = correct_document(xml, ["Fire res"])
    assert changes and all(not c.applied for c in changes), "미적용인데 적용됐다고 보고"
    assert "화염 해" in corrected


def test_absorbed_rule_is_not_reported_as_skipped():
    """'무형성'→'비실체화' 뒤에 남지 않은 '무형' 을 미적용으로 오보하면 안 된다."""
    xml = make_xml([["무형성이 없는 결과"]])
    _, changes = correct_document(xml, ["without any intangibility"])
    assert all(c.applied for c in changes), (
        "앞 규칙에 흡수된 표현이 미적용으로 보고됐다: "
        + ", ".join(c.rule.wrong for c in changes if not c.applied)
    )


def test_other_docx_parts_are_copied_byte_for_byte(tmp_path):
    """이미지·스타일·링크는 한 바이트도 바뀌면 안 된다."""
    source = tmp_path / "source.docx"
    with zipfile.ZipFile(source, "w") as archive:
        archive.writestr("word/document.xml", make_xml([["원본"]]))
        archive.writestr("word/media/image1.png", b"\x89PNG\r\n\x1a\nBINARY")
        archive.writestr("word/styles.xml", "<styles/>")

    target = tmp_path / "out.docx"
    write_document(source, target, make_xml([["교정본"]]))

    with zipfile.ZipFile(source) as a, zipfile.ZipFile(target) as b:
        assert a.namelist() == b.namelist()
        for name in a.namelist():
            if name == "word/document.xml":
                continue
            assert a.read(name) == b.read(name), f"{name} 이 바뀌었다"
    assert "교정본" in read_document_xml(target)


# --- 규칙 자체의 무결성 ---------------------------------------------------------


def test_rules_are_ordered_longest_match_first():
    """짧은 규칙이 먼저 돌면 긴 표현의 속을 잘라먹어 교정이 반쪽이 된다."""
    for i, rule in enumerate(RULES):
        for later in RULES[i + 1:]:
            assert rule.wrong not in later.wrong or rule.wrong == later.wrong, (
                f"'{rule.wrong}' 가 '{later.wrong}' 보다 먼저다 — 순서를 뒤집을 것"
            )


def test_every_rule_declares_evidence_and_reason():
    for rule in RULES:
        assert rule.evidence, f"{rule.wrong}: 영문 근거 패턴이 비었다 — 맹목 치환이 된다"
        assert rule.reason, f"{rule.wrong}: 사유가 비었다"
        assert rule.wrong != rule.right


def test_rules_do_not_rewrite_official_item_names():
    """고유명사는 이미 공식 한국어명이다. 규칙이 그걸 덮으면 안 된다."""
    official = ("평범한 목걸이", "공허의 화석", "상형 문자 화석", "모순", "재단 오브",
                "닉타의 등불", "명계의 조임쇠", "화룡점정", "생명의 결실", "베렉의 유예")
    for rule in RULES:
        for name in official:
            assert name not in rule.wrong, f"{rule.wrong}: 공식 아이템명을 교정 대상으로 삼았다"


def test_prefix_detection_handles_rewritten_docx():
    """파이썬 도구로 다시 저장된 docx 는 접두사가 w: 가 아니라 ns0: 다."""
    xml = make_xml([["화염 해상도"]], prefix="ns0")
    corrected, changes = correct_document(xml, ["Fire res"])
    assert "화염 저항" in corrected
    assert [c.applied for c in changes] == [True]


def test_paragraph_texts_joins_runs():
    assert paragraph_texts(make_xml([["가", "나"], ["다"]])) == ["가나", "다"]


def test_report_lists_applied_and_skipped():
    xml = make_xml([["화염 해상도"], ["화염 해", "상도"]])
    _, changes = correct_document(xml, ["Fire res", "Fire res"])
    report = render_report(changes)
    assert "| O |" in report and "run 경계" in report
    assert "해상도" in report and "저항" in report


def test_applicable_rules_is_the_only_gate():
    custom = (Rule("가", "나", r"MATCH", "테스트"),)
    assert applicable_rules("가", "MATCH here", custom) == list(custom)
    assert applicable_rules("가", "no evidence", custom) == []
    assert applicable_rules("없음", "MATCH here", custom) == []


@pytest.mark.parametrize("korean,english,expected", [
    ("6월 찬스 100%", "for 100% Jun chance", "준(Jun) 확률 100%"),
    ("언덕을 어디든지 갈 수 있습니다", "Hillock to anywhere", "힐록은 아무 부서에나 배치"),
    ("상인 라비쉬 5:1", "Vendor Lavish 5 to 1", "화려한 생명의 결실 5개를 상인에게 판매(5→1 교환)"),
    ("41레벨 도박", "at level 41 gambling", "41레벨 셉터 도박"),
])
def test_betrayal_corrections_from_audit_table(korean, english, expected):
    """근거: Docs/2026-08-19_LUMINARY_BOT_SSF_ATLAS_TREE_AND_BETRAYAL.md §5 오역 교정표."""
    corrected, _ = correct_document(make_xml([[korean]]), [english])
    assert expected in corrected
