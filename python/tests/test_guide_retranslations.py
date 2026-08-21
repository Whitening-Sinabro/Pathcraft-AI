"""문단 재번역 층 회귀 가드.

이 층의 위험은 용어 치환과 다르다. 치환은 틀려도 단어 하나가 틀리지만, 재번역은
**문단 전체를 남의 자리에 써 넣을 수 있다**. 그래서 테스트의 중심이 두 가지다.

1. 엉뚱한 자리에 쓰지 않는가 — 영문 원문이 키이므로, 못 찾으면 조용히 넘어가지 않고
   미적용으로 보고되어야 한다.
2. 서식을 조용히 뭉개지 않는가 — 링크 run 을 갈아치우거나, 서식 경계를 모르는 채
   여러 run 을 하나로 합치면 안 된다.

교정 대상 docx 는 레포 밖(사용자 Downloads)이므로 여기서는 합성 XML 로 검증한다.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "python" / "scripts"))

from fix_guide_translation import (  # noqa: E402
    RULES,
    applicable_rules,
    _namespace_prefix,
    _text_run_pattern,
    paragraph_texts,
    render_report,
    replaceable_run_spans,
    retranslate_document,
)
from guide_retranslations import (  # noqa: E402
    RETRANSLATIONS,
    Retranslation,
    normalize_english,
    retranslation_index,
)

def apply_rules(korean: str, english: str) -> str:
    """`correct_document` 가 문단 하나에 하는 일과 같은 치환을 문자열에 적용한다."""
    for rule in applicable_rules(korean, english, RULES):
        korean = korean.replace(rule.wrong, rule.right)
    return korean


def korean_text(entry: Retranslation) -> str:
    """조각 형태(튜플)든 통짜 문자열이든 한 덩어리로 본다."""
    return "".join(entry.korean) if isinstance(entry.korean, tuple) else entry.korean


SAMPLE = Retranslation("Spam Ancient Wombgift for uniques.",
                       "유니크를 노린다면 고대 생명의 결실을 도배한다.",
                       "어순 붕괴")


def wrap(body: str, prefix: str = "ns0") -> str:
    return f"<{prefix}:document><{prefix}:body>{body}</{prefix}:body></{prefix}:document>"


def para(*runs: str, prefix: str = "ns0") -> str:
    inner = "".join(f"<{prefix}:r><{prefix}:t>{t}</{prefix}:t></{prefix}:r>" for t in runs)
    return f"<{prefix}:p>{inner}</{prefix}:p>"


def linked_para(link_text: str, *plain: str, prefix: str = "ns0") -> str:
    inner = (f"<{prefix}:hyperlink ns5:id=\"rId9\">"
             f"<{prefix}:r><{prefix}:t>{link_text}</{prefix}:t></{prefix}:r>"
             f"</{prefix}:hyperlink>")
    inner += "".join(f"<{prefix}:r><{prefix}:t>{t}</{prefix}:t></{prefix}:r>" for t in plain)
    return f"<{prefix}:p>{inner}</{prefix}:p>"


# --- 자리를 틀리지 않는가 -------------------------------------------------------


def test_rewrite_replaces_the_whole_paragraph():
    xml = wrap(para("고유 아이템에 대한 스팸 고대 생명의 결실입니다."))
    out, rewrites = retranslate_document(xml, [SAMPLE.english], (SAMPLE,))
    assert paragraph_texts(out) == [SAMPLE.korean]
    assert [(r.paragraph, r.applied) for r in rewrites] == [(0, True)]


def test_no_rewrite_when_english_does_not_match():
    """영문이 조금이라도 다르면 손대지 않는다 — 원본 개정 시 엉뚱한 자리에 쓰지 않기 위해서다."""
    xml = wrap(para("건드리면 안 되는 문단"))
    out, rewrites = retranslate_document(xml, ["Spam Ancient Wombgift for rares."], (SAMPLE,))
    assert paragraph_texts(out) == ["건드리면 안 되는 문단"]
    assert [r.applied for r in rewrites] == [False]
    assert rewrites[0].paragraph == -1


def test_unmatched_entry_is_reported_not_dropped():
    """표에는 있는데 원문에 없으면 '고쳤다'는 착각이 남는다. 반드시 보고돼야 한다."""
    xml = wrap(para("아무거나"))
    _, rewrites = retranslate_document(xml, ["Something else entirely"], (SAMPLE,))
    assert rewrites[0].skipped_because == "영문 원문에 이 문단이 없다"


def test_matching_ignores_typography_and_entities():
    """곱슬 따옴표·엔티티는 판본마다 흔들린다. 그 흔들림으로 매칭이 깨지면 안 된다."""
    entry = Retranslation("Don't spam & pray -> just farm", "그냥 파밍해라", "테스트")
    xml = wrap(para("원문"))
    english = "Don’t spam &amp; pray -&gt;  just farm"
    out, rewrites = retranslate_document(xml, [english], (entry,))
    assert paragraph_texts(out) == ["그냥 파밍해라"]
    assert rewrites[0].applied


def test_duplicate_keys_fail_loudly():
    twin = Retranslation(SAMPLE.english, "다른 번역", "중복")
    with pytest.raises(ValueError, match="중복"):
        retranslation_index((SAMPLE, twin))


# --- 서식을 뭉개지 않는가 -------------------------------------------------------


def test_hyperlink_run_is_never_rewritten():
    """링크 텍스트를 갈면 표시 문구가 사라진다. 링크 밖 run 만 대상이다."""
    entry = Retranslation("https://example.com for Breach", " — 균열용", "설명 누락",
                          link_label="https://example.com")
    xml = wrap(linked_para("https://example.com", " -> "))
    out, rewrites = retranslate_document(xml, ["https://example.com for Breach"], (entry,))
    assert rewrites[0].applied
    assert paragraph_texts(out) == ["https://example.com — 균열용"]


def test_blank_run_is_used_only_when_no_written_run_exists():
    """링크만 있는 문단은 뒤 공백 run 이 유일한 자리다. 여기서 포기하면 설명을 못 붙인다."""
    entry = Retranslation("https://example.com for Breach", " — 균열용", "설명 누락",
                          link_label="https://example.com")
    xml = wrap(linked_para("https://example.com", " "))
    out, _ = retranslate_document(xml, ["https://example.com for Breach"], (entry,))
    assert paragraph_texts(out) == ["https://example.com — 균열용"]


def test_undeclared_link_label_is_refused():
    """링크가 남길 문구를 사람이 적어두지 않았으면 쓰지 않는다.

    선언을 강제하지 않으면 링크에 남은 옛 오역('럭셔리 업그레이드')이 새 문장 옆에
    유령처럼 붙는데, 기계는 그게 살려둘 라벨인지 갈아야 할 오역인지 구분할 수 없다.
    """
    entry = Retranslation("https://example.com for Breach", " — 균열용", "설명 누락")
    xml = wrap(linked_para("https://example.com", " -> "))
    out, rewrites = retranslate_document(xml, ["https://example.com for Breach"], (entry,))
    assert not rewrites[0].applied
    assert "link_label" in rewrites[0].skipped_because
    assert paragraph_texts(out) == ["https://example.com -> "]


def test_link_label_mismatch_is_refused():
    """선언과 실물이 어긋나면 원본이 바뀐 것이다 — 조용히 엉뚱한 자리에 붙이지 않는다."""
    entry = Retranslation("https://example.com for Breach", " — 균열용", "설명 누락",
                          link_label="https://example.org")
    xml = wrap(linked_para("https://example.com", " -> "))
    _, rewrites = retranslate_document(xml, ["https://example.com for Breach"], (entry,))
    assert not rewrites[0].applied
    assert "example.org" in rewrites[0].skipped_because


def test_new_text_repeating_the_link_label_is_refused():
    """링크가 이미 보여주는 글자를 새 번역이 또 담으면 화면에 두 번 나온다."""
    entry = Retranslation("https://example.com for Breach",
                          " https://example.com 균열용", "설명 누락",
                          link_label="https://example.com")
    xml = wrap(linked_para("https://example.com", " -> "))
    _, rewrites = retranslate_document(xml, ["https://example.com for Breach"], (entry,))
    assert not rewrites[0].applied
    assert "두 번" in rewrites[0].skipped_because


def test_two_written_runs_are_left_alone():
    """어느 run 이 굵게인지 모르는 채 합치면 인라인 서식이 조용히 죽는다."""
    xml = wrap(para("앞부분 ", "뒷부분"))
    out, rewrites = retranslate_document(xml, [SAMPLE.english], (SAMPLE,))
    assert paragraph_texts(out) == ["앞부분 뒷부분"]
    assert not rewrites[0].applied
    assert "2개" in rewrites[0].skipped_because


def test_korean_is_xml_escaped():
    """< 로 시작하는 문단이 원문에 있다. 그대로 넣으면 문서가 깨진다."""
    entry = Retranslation("Do not do this", "<골드가 부족하면> 하지 마라 & 넘어가라", "테스트")
    xml = wrap(para("원문"))
    out, _ = retranslate_document(xml, ["Do not do this"], (entry,))
    assert "&lt;골드가 부족하면&gt;" in out and "&amp;" in out
    assert paragraph_texts(out) == ["&lt;골드가 부족하면&gt; 하지 마라 &amp; 넘어가라"]


# --- run 인식 자체의 회귀 (실제로 두 번 물렸던 자리) -----------------------------


def test_text_run_pattern_ignores_table_and_self_closing_tags():
    """`<w:tcPr>`(표 서식)과 `<w:t ... />`(빈 텍스트)를 여는 태그로 착각하면
    다음 `</w:t>` 까지 마크업을 통째로 본문으로 읽는다. 실제 문서에서 둘 다 터졌다."""
    prefix = "ns0"
    paragraph = (
        f"<{prefix}:p><{prefix}:tcPr><{prefix}:top {prefix}:val=\"nil\" /></{prefix}:tcPr>"
        f"<{prefix}:r><{prefix}:t xml:space=\"preserve\" /></{prefix}:r>"
        f"<{prefix}:r><{prefix}:t>본문</{prefix}:t></{prefix}:r></{prefix}:p>"
    )
    bodies = [m.group(2) for m in _text_run_pattern(prefix).finditer(paragraph)]
    assert bodies == ["본문"], f"마크업을 본문으로 읽었다: {bodies}"
    assert len(replaceable_run_spans(paragraph, prefix)) == 1


def test_namespace_prefix_detection_still_holds():
    assert _namespace_prefix(wrap(para("가"), )) == "ns0"
    assert _namespace_prefix(wrap(para("가", prefix="w"), )) == "w"


# --- 두 층이 서로 침범하지 않는가 -----------------------------------------------


def test_only_poedb_rules_may_rewrite_a_retranslation():
    """재번역 문단은 그다음에 도는 용어 치환의 먹잇감이 되면 안 된다 — 딱 한 경우만 빼고.

    예외는 poedb.tw/kr 에서 회수한 공식 이름이다. 재번역 표는 영문 원문을 **키**로 쓰므로
    표 안의 영문 이름(Blade Ambusher 등)을 한국어로 바꿔 버리면 원문 대조가 깨진다.
    그래서 그 이름들은 표에서 영문으로 두고, 문서에 적용되는 규칙이 덮어쓰게 한다.

    그 밖의 규칙이 재번역에 걸리면 잘 써 놓은 문장이 다시 잘린다는 뜻이므로 실패다.
    (실제로 이 검사가 '보석이 박힌 펜싱 검' 이 '주얼이 박힌' 으로 잘리는 걸 잡았다.)
    """
    offenders = [
        (entry.english[:40], rule.wrong, rule.right)
        for entry in RETRANSLATIONS
        for rule in applicable_rules(korean_text(entry), entry.english, RULES)
        if "poedb.tw/kr" not in rule.reason
    ]
    assert not offenders, f"재번역이 그다음 치환에 다시 잘린다: {offenders}"


def test_rule_pass_over_retranslations_converges():
    """치환을 두 번 돌려도 결과가 같아야 한다 — 규칙끼리 서로의 출력을 물면 문장이 무너진다."""
    for entry in RETRANSLATIONS:
        once = apply_rules(korean_text(entry), entry.english)
        assert apply_rules(once, entry.english) == once, entry.english[:50]


def test_jewelled_foil_survives_the_jewel_rule():
    """'보석이 박힌 펜싱 검'(Jewelled Foil)은 주얼이 아니라 무기 베이스다. 회귀 가드."""
    english = "Collect A LOT of Jewelled Foils (i77+)."
    assert apply_rules("보석이 박힌 펜싱 검을 잔뜩 모은다", english) == "보석이 박힌 펜싱 검을 잔뜩 모은다"


# --- 표 자체의 위생 -------------------------------------------------------------


def test_table_entries_are_complete():
    for entry in RETRANSLATIONS:
        assert entry.english.strip(), "영문 키가 비었다"
        assert korean_text(entry).strip(), f"한국어가 비었다: {entry.english[:40]}"
        assert entry.reason.strip(), f"사유가 비었다: {entry.english[:40]}"


def test_keys_are_normalized_form_stable():
    """키를 정규화한 결과가 다시 정규화해도 같아야 색인이 흔들리지 않는다."""
    for entry in RETRANSLATIONS:
        once = normalize_english(entry.english)
        assert once == normalize_english(once)


def test_no_english_key_collides_after_normalization():
    assert len(retranslation_index()) == len(RETRANSLATIONS)


def test_report_separates_rewrites_from_term_changes():
    xml = wrap(para("고유 아이템에 대한 스팸 고대 생명의 결실입니다."))
    _, rewrites = retranslate_document(xml, [SAMPLE.english], (SAMPLE,))
    report = render_report([], rewrites)
    assert "## 1. 문단 재번역" in report
    assert "## 2. 용어 치환" in report
    assert SAMPLE.korean in report
