"""HC Journey — 큐레이션 규칙 자동 초안(#1) 검증.

계약:
  * trigger_key 는 diff/PoB/설정에서만 온다(자막에서 이름 확정 금지).
  * 후보 text 는 자막 원문 그대로, evidence 에 (영상, 초)가 붙는다.
  * 승인 게이트 — CURATION_RULES 를 절대 바꾸지 않고 후보 파일만 쓴다.
  * 판독·자막은 크리에이터별로 묶인다(다른 크리에이터의 영상을 빌리지 않는다).
"""
import hashlib
import json
import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "hc_journey"))
import build_db  # noqa: E402
import rule_autodraft as ra  # noqa: E402

VID = "C_tkSubXWDk"  # 문자 C
T = "ACT3-4 → 엔드게임(계획)"


def _segs(*pairs):
    return [ra.Segment(float(s), 3.0, t) for s, t in pairs]


def _trigger(key, kind="skill_added", level_from=45, idx=2):
    return ra.Trigger("임성빈", idx, T, kind, key, level_from)


def test_classify_signals():
    assert "condition" in ra.classify("92지는 92가 필요하")
    hits = ra.classify("액잘티드도 이렇게 많을 필요가")
    assert "cost" in hits and "condition" not in hits  # "필요가 없다" 부정문은 조건 신호가 아니다
    assert "pitfall" in ra.classify("검은 화염이 버그였다")
    assert "survival" in ra.classify("저항을 하나만 대충")
    assert ra.classify("그래서 맞아요. 죽는 거 당연히") == {}  # 잡담 낱말은 신호가 아니다


def test_infer_levels_running_max_over_timeline():
    anchors = [ra.Anchor(VID, 100, "x"), ra.Anchor(VID, 200, "52레벨 y", 52), ra.Anchor(VID, 300, "z"),
               ra.Anchor("zKJQyBm4VnI", 10, "no level at all")]
    out = {(a.video_id, a.sec): a.level for a in ra.infer_levels(anchors)}
    assert out[(VID, 100)] == 52 and out[(VID, 200)] == 52 and out[(VID, 300)] == 52
    assert out[("zKJQyBm4VnI", 10)] is None  # 영상 A 는 타임라인 맨 앞이고 레벨 판독이 없다


def test_parse_character_level_rejects_ranges_thresholds_and_other_players():
    """캐릭터 레벨보다 큰 값이 될 수 있는 맥락은 버린다 — running max 는 위로만 틀리면 진짜 앵커를 잃는다."""
    p = ra.parse_character_level
    assert p("52레벨 패시브 화면에 스킬 포인트20") == 52
    assert p("9월7일 85레벨 스킬 창에서") == 85 and p("43레벨15%, 최대 생명력952") == 43
    assert p("저항 페널티가 레벨 구간별로54~59레벨40%·60~64레벨50%·65레벨 이상60%") is None
    assert p("전역 사망 알림에 다른 이름의 9레벨 캐릭터가 표시된다") is None
    assert p("스킬 부여 13레벨 권능 착취") is None and p("미가공 보조 젬 (1레벨)") is None
    assert p("요구 레벨52와 빨간 지능92") is None and p("몬스터 레벨65 지역") is None
    assert p("아무 레벨 언급 없음") is None


def test_infer_levels_gem_level_mentions_do_not_poison():
    """'13레벨 권능 착취'(젬 레벨)·'(1레벨)' 같은 판독이 캐릭터 레벨을 끌어내리면 안 된다. 다음 영상 초반도 앞 영상 최대를 잇는다."""
    anchors = [ra.Anchor(VID, 8900, "57레벨 알림", 57), ra.Anchor(VID, 8940, "스킬 부여 13레벨 권능 착취", 13),
               ra.Anchor(VID, 9000, "투구 거래소"), ra.Anchor("39kHWKUhwhU", 2420, "5레벨 부여", 5),
               ra.Anchor("39kHWKUhwhU", 2705, "보관함 투구")]
    out = {(a.video_id, a.sec): a.level for a in ra.infer_levels(anchors)}
    assert out[(VID, 8940)] == 57 and out[(VID, 9000)] == 57
    assert out[("39kHWKUhwhU", 2420)] == 57 and out[("39kHWKUhwhU", 2705)] == 57


def test_find_anchors_level_gate_and_character_name_ignore():
    tr = _trigger("Flameblast")
    anchors = [
        ra.Anchor("zKJQyBm4VnI", 1445, "캐릭터 임성빈_화염파_젬링, 4레벨", 4),
        ra.Anchor("zKJQyBm4VnI", 5110, "임성빈_화염파_젬링 13레벨 머서너리", 13),
        ra.Anchor(VID, 4540, "화염파Lv13 새기기 목록 툴팁에 요구 레벨52", 52),
        ra.Anchor(VID, 4950, "채팅에 캐릭터 임성빈_화염파_젬링이 보이고", 52),  # 이름 안에서만 별칭
    ]
    got = ra.find_anchors(tr, anchors, ignore=("임성빈_화염파_젬링",))
    assert [(a.video_id, a.sec) for a in got] == [(VID, 4540)]
    assert ra.find_anchors(_trigger("SigilOfPower"), anchors) == []  # 별칭 미등록


def test_draft_schema_verbatim_text_and_existing_flag():
    anchors = [ra.Anchor(VID, 100, "화염파Lv13 새기기 요구 레벨52", 52)]
    transcripts = {VID: _segs((80, "92지는 92가 필요하"), (95, "지능은 다 찍었고"), (300, "골드 골드 골드"))}
    r = ra.draft_candidates([_trigger("Flameblast")], anchors, transcripts, window_sec=30)
    assert r["unanchored"] == [] and r["skipped"] == []
    by_kind = {c["evidence"]["kind"]: c for c in r["candidates"]}
    assert set(by_kind) == {"caption", "readout"} and len(r["candidates"]) == 2
    c = by_kind["caption"]
    assert {"id", "trigger_kind", "trigger_key", "note_type", "text", "evidence"} <= set(c)
    assert (c["trigger_kind"], c["trigger_key"], c["note_type"]) == ("skill_added", "Flameblast", "condition")
    assert c["text"] == "92지는 92가 필요하 / 지능은 다 찍었고"  # 자막 원문 그대로
    ev = c["evidence"]
    assert (ev["video"], ev["sec"], ev["ref"]) == ("C", 80, "C 80초")
    assert ev["url"].endswith("&t=80s") and ev["anchor"]["sec"] == [100]
    assert c["existing_rule"] is True  # (skill_added, Flameblast, condition) 은 이미 규칙에 있다 → 사람이 본다
    assert c["status"] == "pending" and c["id"] == "skill_added/Flameblast/condition/caption/C 80"
    # 판독 줄은 한 줄로도 후보(화면 수치는 자막에 없다). text 는 판독 원문.
    rd = by_kind["readout"]
    assert rd["text"] == "화염파Lv13 새기기 요구 레벨52" and rd["note_type"] == "condition"
    assert rd["evidence"]["sec"] == 100 and rd["signals"] == ["요구 레벨"]


def test_decisions_merge_only_changes_status(tmp_path):
    anchors = [ra.Anchor(VID, 100, "화염파Lv13 새기기 요구 레벨52", 52)]
    transcripts = {VID: _segs((80, "92지는 92가 필요하"), (95, "지능은 다 찍었고"))}
    r = ra.draft_candidates([_trigger("Flameblast")], anchors, transcripts, window_sec=30)
    dec = {"skill_added/Flameblast/condition/caption/C 80": {"status": "rejected", "reason": "손노트와 중복"},
           "no/such/id": {"status": "adopted"}}
    ra.apply_decisions(r["candidates"], dec)
    st = {c["id"]: c["status"] for c in r["candidates"]}
    assert st["skill_added/Flameblast/condition/caption/C 80"] == "rejected"
    assert st["skill_added/Flameblast/condition/readout/C 100"] == "pending"
    assert len(r["candidates"]) == 2  # 기록이 후보를 만들거나 지우지 않는다
    p = tmp_path / "d.json"
    p.write_text(json.dumps({"decisions": dec}, ensure_ascii=False), encoding="utf-8")
    assert ra.load_decisions(p) == dec and ra.load_decisions(tmp_path / "missing.json") == {}


def test_min_hits_drops_single_line_windows():
    anchors = [ra.Anchor(VID, 100, "화염파 툴팁", 52)]
    transcripts = {VID: _segs((90, "지능이 필요하네요"), (95, "안녕하세요"))}
    r = ra.draft_candidates([_trigger("Flameblast")], anchors, transcripts, window_sec=30, min_hits=2)
    assert r["candidates"] == []
    r = ra.draft_candidates([_trigger("Flameblast")], anchors, transcripts, window_sec=30, min_hits=1)
    assert len(r["candidates"]) == 1


def test_same_evidence_attributed_once_with_also_matches():
    """스킬 창 판독은 스킬을 전부 나열한다 → 같은 자막 창이 여러 트리거에 걸린다. 앵커 많은 쪽 하나에만 귀속."""
    anchors = [ra.Anchor(VID, 100, "화염파Lv13 DPS, 섬광 유탄Lv14 목록", 52),
               ra.Anchor(VID, 120, "화염파Lv13 툴팁 요구 지능92", 52)]
    transcripts = {VID: _segs((90, "92지는 92가 필요하"), (95, "지능은 다 찍었고"))}
    r = ra.draft_candidates([_trigger("Flameblast"), _trigger("FlashGrenade")], anchors, transcripts, window_sec=30)
    caps = [c for c in r["candidates"] if c["evidence"]["kind"] == "caption"]
    assert len(caps) == 1
    c = caps[0]
    assert c["trigger_key"] == "Flameblast" and c["existing_rule"] is True
    assert c["also_matches"] == [{"trigger": "skill_added/FlashGrenade", "transition": T, "existing_rule": False}]


def test_same_key_in_several_transitions_is_owned_by_anchor_level():
    """Helm1 은 밴드마다 바뀐다(전환 0~3). 45레벨 앵커 창은 ACT1→ACT2 가 아니라 45 에서 시작하는 전환의 것이다."""
    trs = [ra.Trigger("임성빈", 0, "ACT1 → ACT2", "item_slot_change", "Helm1", 12),
           ra.Trigger("임성빈", 1, "ACT2 → ACT3-4", "item_slot_change", "Helm1", 22),
           ra.Trigger("임성빈", 2, T, "item_slot_change", "Helm1", 45),
           ra.Trigger("임성빈", 3, "엔드게임(계획) → 실캐릭 lv93", "item_slot_change", "Helm1", 45)]
    anchors = [ra.Anchor("GtC5-b4QXec", 9398, "투구 장착 45레벨", 45), ra.Anchor(VID, 9000, "투구 거래소 57레벨", 57)]
    transcripts = {"GtC5-b4QXec": _segs((9370, "지능이 모자라서 못 꼈구나"), (9380, "지능 대충 올려 놓겠습니다")),
                   VID: _segs((8990, "골드 76660"), (9010, "되게 싼데요"))}
    r = ra.draft_candidates(trs, anchors, transcripts, window_sec=30)
    got = {(c["evidence"]["video"], c["note_type"]): c["transition_idx"] for c in r["candidates"]}
    assert got == {("B", "condition"): 2, ("C", "cost"): 2}  # 둘 다 45 이상 → idx 2 (동률이면 이른 전환)


def test_unknown_alias_and_missing_transcript_are_reported_not_invented():
    anchors = [ra.Anchor("rsKbeELo0TM", 75, "검은화염 계약 키스톤 툴팁", 90)]
    r = ra.draft_candidates([_trigger("SigilOfPower"), _trigger("Blackflame Covenant", kind="keystone", idx=3)],
                            anchors, {}, window_sec=30)
    assert r["candidates"] == []
    assert [u["trigger_key"] for u in r["unanchored"]] == ["SigilOfPower"] and "alias" in r["unanchored"][0]["reason"]
    assert r["skipped"] == [{"trigger_key": "Blackflame Covenant", "video": "F", "sec": [75], "reason": "자막 없음"}]


def test_trigger_keys_come_from_diff_and_config_not_captions():
    trs = ra.transition_triggers()
    keys = {t.trigger_key for t in trs}
    assert {"Flameblast", "Weapon2", "Blackflame Covenant", "Gemling Legionnaire", "Warbringer", "Blood Magic"} <= keys
    assert all(not re.search(r"[가-힣]", k) for k in keys)  # 자막(한국어)이 trigger_key 로 새지 않는다
    assert not any(t.trigger_key.startswith("PlayerDefault") for t in trs)
    # 전환 인덱스·시작 레벨은 CREATORS 밴드에서 온다
    fb = [t for t in trs if t.trigger_key == "Flameblast"]
    assert fb and fb[0].transition_idx == 2 and fb[0].level_from == 45
    bf = [t for t in trs if t.trigger_key == "Blackflame Covenant"]
    assert bf and bf[0].transition_idx == 3 and bf[0].level_from == 45  # 엔드게임(계획) 레벨 없음 → 앞 밴드 45


def test_league_trigger_follows_build_ssf_flag():
    """거래 리그 빌드 → league/trade, SSF 빌드 → league/ssf. 둘 다 첫 전환. 트리거 키는 설정(ssf 플래그)에서 온다."""
    trade = [t for t in ra.transition_triggers() if t.trigger_kind == "league"]
    # 밴드 1개(탱정)는 전환이 없어 리그 트리거도 없다 — 첫 전환에 붙는 트리거는 전환이 있어야 생긴다.
    expected = {(c["name"], "ssf" if c["build"]["ssf"] else "trade", 0) for c in build_db.CREATORS if len(c["bands"]) >= 2}
    assert len(expected) < len(build_db.CREATORS)   # 전환 0 빌드가 실제로 하나 있다(탱정)
    assert {(t.creator, t.trigger_key, t.transition_idx) for t in trade} == expected
    cfg = json.loads(json.dumps(build_db.CREATORS[0], ensure_ascii=False))  # 깊은 복사
    cfg["name"], cfg["build"]["ssf"] = "SSF 가상", 1
    ssf = [t for t in ra.transition_triggers([cfg]) if t.trigger_kind == "league"]
    assert [(t.trigger_key, t.transition_idx, t.level_from) for t in ssf] == [("ssf", 0, 12)]
    # ssf 는 아직 소스/별칭이 없어 후보 대신 '앵커 없음' 으로 정직하게 남는다
    r = ra.draft_candidates(ssf, [], {}, window_sec=30)
    assert r["candidates"] == [] and r["unanchored"][0]["trigger_key"] == "ssf"


@pytest.mark.skipif(not ra.DELIVERABLE.exists(), reason="임성빈 자막/판독 deliverable 없음")
def test_real_seongbin_transcripts_yield_five_plus(tmp_path):
    out = tmp_path / "rule_candidates.json"
    r = ra.run(out=out, creator="임성빈")
    cands = r["candidates"]
    assert len(cands) >= 5, [c["trigger_key"] for c in cands]
    keys = {t.trigger_key for t in ra.transition_triggers()}
    for c in cands:
        assert c["creator"] == "임성빈" and c["trigger_key"] in keys
        assert c["evidence"]["video"] in ra.VIDEO_LETTERS and isinstance(c["evidence"]["sec"], int)
        assert c["note_type"] in ra.NOTE_SIGNALS and c["text"]
        assert c["status"] in {"pending", "adopted", "rejected", "deferred"}  # 승인 기록이 있으면 병합된다
    # 서로 다른 note_type 이 실제로 나온다 (조건 하나만 잔뜩이 아님)
    assert {c["note_type"] for c in cands} >= {"condition", "pitfall", "cost"}
    doc = json.loads(out.read_text(encoding="utf-8"))
    assert doc["_meta"]["n_candidates"] == len(cands) and "임성빈" in doc["_meta"]["sources"]
    assert "자동 반영 금지" in doc["_meta"]["purpose"]


@pytest.mark.skipif(not ra.DEFAULT_DECISIONS.exists(), reason="승인 기록 없음")
def test_decisions_are_consistent_with_rules_and_candidates():
    """채택 판정은 CURATION_RULES 에 실제 규칙이 있어야 하고, 판정은 존재하는 후보만 가리킨다(오래된 판정 금지)."""
    dec = ra.load_decisions(ra.DEFAULT_DECISIONS)
    rules = {(k, key, nt) for (k, key, nt, _t, _e) in build_db.CURATION_RULES}
    for cid, d in dec.items():
        assert d["status"] in {"adopted", "rejected", "deferred"}, cid
        assert d.get("reason"), cid
        if d["status"] == "adopted":
            assert tuple(d["rule"]) in rules, (cid, d["rule"])
    ids = {c["id"] for c in ra.run(out=None, decisions_path=None)["candidates"]}
    stale = set(dec) - ids
    assert not stale, stale
    # 채택 규칙의 근거는 (영상 초) 또는 패치노트/GGPK 로 추적 가능해야 한다
    for (_k, _key, _nt, _text, ev) in build_db.CURATION_RULES:
        assert "규칙(" in ev, ev


def test_creator_without_sources_gets_nothing_borrowed():
    r = ra.run(out=None, creator="Skadoosh")
    assert r["candidates"] == [] and r["unanchored"]
    assert all(u["reason"] == "자막/판독 소스 없음" for u in r["unanchored"])


def test_approval_gate_never_mutates_rules(tmp_path):
    src = Path(build_db.__file__)
    before_src = hashlib.sha256(src.read_bytes()).hexdigest()
    before_rules = [tuple(x) for x in build_db.CURATION_RULES]
    default_out = ra.DEFAULT_OUT
    before_out = default_out.read_bytes() if default_out.exists() else None
    ra.run(out=tmp_path / "c.json")
    assert hashlib.sha256(src.read_bytes()).hexdigest() == before_src
    assert [tuple(x) for x in build_db.CURATION_RULES] == before_rules
    assert (default_out.read_bytes() if default_out.exists() else None) == before_out  # 지정한 out 이외엔 안 쓴다
    st = build_db.build()
    assert st["curation_rule"] == len(before_rules)  # DB 규칙 수도 그대로
