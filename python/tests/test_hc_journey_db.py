"""HC Journey DB — 다중 크리에이터 + 재사용 큐레이션 규칙 검증.

핵심 계약(사용자 인사이트 반영):
  큐레이션 손노동은 DB가 커지면 안 따라온다. 그래서 일반 지식은 curation_rule 로 뽑아
  이후 빌드에 자동 적용되어야 한다. 새 크리에이터는 큐레이션을 '공짜로 상속'한다.
"""
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "hc_journey"))
import build_db  # noqa: E402


def _bid(con, like):
    return con.execute("SELECT id FROM build WHERE name LIKE ?", (like,)).fetchone()[0]


def test_multi_creator_and_rules():
    """크리에이터 수는 CREATORS 설정에 묶는다(숫자 리터럴이면 추가할 때마다 red, >= 면 삭제를 못 잡는다)."""
    st = build_db.build()
    names = {c["name"] for c in build_db.CREATORS}
    assert names == {"임성빈", "Skadoosh", "ds lily", "Fubgun", "탱정", "Blazeworks", "MisoxShiru", "디넬"}, names
    assert st["creator"] == st["build"] == len(build_db.CREATORS), st
    assert st["snapshot"] == sum(len(c["bands"]) for c in build_db.CREATORS), st
    assert st["transition"] == sum(len(c["bands"]) - 1 for c in build_db.CREATORS), st
    assert st["curation_rule"] >= 10, st
    assert st["notes_rule"] >= 8, st        # 규칙에서 자동 부착된 노트(커버리지 확장)
    assert st["notes_hand"] >= 6, st        # 빌드 고유 손노동


def test_new_creators_inherit_without_hand_notes():
    """ds lily·Fubgun 은 손노동 0, 키스톤 미확보인데도 전직·스킬 도입·슬롯·리그 규칙을 상속한다 — 확장의 증명.
    hardcore 는 그 빌드의 근거로만 1 — 둘 다 빌드 단위 HC 근거가 없어 0(ds lily 는 채널 정체성만 HC, 2026-09-10 내림)."""
    build_db.build()
    con = sqlite3.connect(build_db.DB_PATH)
    for like, hc in (("%ds lily%", 0), ("%Fubgun%", 0)):
        bid = _bid(con, like)
        assert con.execute("SELECT hardcore FROM build WHERE id=?", (bid,)).fetchone()[0] == hc
        hand = con.execute("SELECT COUNT(*) FROM transition_note n JOIN transition t ON n.transition_id=t.id "
                           "WHERE t.build_id=? AND n.source='hand'", (bid,)).fetchone()[0]
        kinds = {r[0] for r in con.execute(
            "SELECT DISTINCT r.trigger_kind FROM transition_note n JOIN transition t ON n.transition_id=t.id "
            "JOIN curation_rule r ON n.rule_id=r.id WHERE t.build_id=?", (bid,))}
        assert hand == 0 and {"ascendancy", "skill_added", "item_slot_change", "league"} <= kinds, (like, kinds)
        # 화염파 도입 규칙이 어느 전환엔가 붙는다(같은 빌드의 다른 제작자도 같은 지식을 상속)
        fb = con.execute("SELECT COUNT(*) FROM transition_note n JOIN transition t ON n.transition_id=t.id "
                         "JOIN curation_rule r ON n.rule_id=r.id WHERE t.build_id=? AND r.trigger_key='Flameblast'", (bid,)).fetchone()[0]
        assert fb >= 1, like
    # 일반화: 손노트 없는(notes == {}) 밴드 ≥2 크리에이터는 전부 손 0 + 규칙 노트 ≥1 (바라시타 2명 포함). 밴드 1개는 전환이 없어 규칙도 0 이 맞다.
    for cfg in build_db.CREATORS:
        if cfg["notes"]:
            continue
        bid = con.execute("SELECT b.id FROM build b JOIN creator c ON c.id=b.creator_id WHERE c.name=?", (cfg["name"],)).fetchone()[0]
        hand, rule = con.execute(
            "SELECT SUM(n.source='hand'), SUM(n.source='rule') FROM transition_note n JOIN transition t ON n.transition_id=t.id "
            "WHERE t.build_id=?", (bid,)).fetchone()
        assert (hand or 0) == 0, cfg["name"]
        if len(cfg["bands"]) >= 2:
            assert (rule or 0) >= 1, cfg["name"]
        else:
            assert (rule or 0) == 0, cfg["name"]
    con.close()


def test_skadoosh_inherits_curation_free():
    """새 크리에이터(Skadoosh)는 손노동 0인데도 규칙에서 큐레이션을 상속받는다."""
    build_db.build()
    con = sqlite3.connect(build_db.DB_PATH)
    bid = _bid(con, "워브링어%")
    hand = con.execute(
        "SELECT COUNT(*) FROM transition_note n JOIN transition t ON n.transition_id=t.id "
        "WHERE t.build_id=? AND n.source='hand'", (bid,)).fetchone()[0]
    rule = con.execute(
        "SELECT COUNT(*) FROM transition_note n JOIN transition t ON n.transition_id=t.id "
        "WHERE t.build_id=? AND n.source='rule'", (bid,)).fetchone()[0]
    assert hand == 0, hand      # 아직 손노동 안 함
    assert rule >= 4, rule      # 키스톤 2 + 어센던시(Warbringer) + 토템 등 규칙이 붙는다
    con.close()


def test_rule_reused_across_builds():
    """규칙은 한 번 정의되어 여러 빌드/전환에 재사용된다(rule_id 재사용)."""
    build_db.build()
    con = sqlite3.connect(build_db.DB_PATH)
    # Blackflame 규칙(임성빈)과 Blood Magic 규칙(Skadoosh)이 서로 다른 빌드에 붙어 있다.
    used = con.execute("SELECT COUNT(DISTINCT rule_id) FROM transition_note WHERE source='rule'").fetchone()[0]
    assert used >= 4, used
    con.close()


def test_league_trade_rules_attach_once_at_first_transition():
    """거래 지식은 슬롯이 아니라 리그 모드(league/trade)에 속한다. 거래 리그 빌드의 첫 전환에만 한 번 붙고, SSF 빌드엔 안 붙는다."""
    build_db.build()
    con = sqlite3.connect(build_db.DB_PATH)
    n_trade_rules = con.execute(
        "SELECT COUNT(*) FROM curation_rule WHERE trigger_kind='league' AND trigger_key='trade'").fetchone()[0]
    assert n_trade_rules >= 3, n_trade_rules
    for bid, ssf in con.execute("SELECT id, ssf FROM build"):
        rows = con.execute(
            "SELECT t.order_idx, COUNT(*) FROM transition_note n JOIN transition t ON n.transition_id=t.id "
            "JOIN curation_rule r ON n.rule_id=r.id WHERE t.build_id=? AND r.trigger_kind='league' AND r.trigger_key='trade' "
            "GROUP BY t.order_idx", (bid,)).fetchall()
        n_trans = con.execute("SELECT COUNT(*) FROM transition WHERE build_id=?", (bid,)).fetchone()[0]
        if ssf or n_trans == 0:
            assert rows == [], rows            # SSF 는 거래 규칙 없음 · 전환 0(밴드 1개)은 붙을 자리가 없음
        else:
            assert rows == [(0, n_trade_rules)], rows   # 첫 전환에 규칙 수만큼, 다른 전환엔 0
    con.close()


def test_single_band_build_has_no_transitions_notes_or_links():
    """밴드 1개(탱정 2.0 엔드게임)는 전환이 없다 → 규칙 노트·거래 링크도 0. 여정은 전환에 붙으므로 이것이 맞는 동작이고
    적재는 스냅샷(스킬·장비)만 남긴다. 조용히 비지 않도록 --query 가 '전환 없음' 을 명시한다. 하코 근거 없음 → hardcore=0."""
    build_db.build()
    con = sqlite3.connect(build_db.DB_PATH)
    bid = _bid(con, "방패벽 키타바%")
    assert con.execute("SELECT hardcore FROM build WHERE id=?", (bid,)).fetchone()[0] == 0
    assert con.execute("SELECT COUNT(*) FROM snapshot WHERE build_id=?", (bid,)).fetchone()[0] == 1
    assert con.execute("SELECT COUNT(*) FROM transition WHERE build_id=?", (bid,)).fetchone()[0] == 0
    sid = con.execute("SELECT id FROM snapshot WHERE build_id=?", (bid,)).fetchone()[0]
    cfg = next(c for c in build_db.CREATORS if c["name"] == "탱정")
    data = build_db.load_build(build_db.CREATORS_DIR / cfg["bands"][0][3])
    skills = {r[0] for r in con.execute("SELECT main_gem FROM snapshot_skill WHERE snapshot_id=?", (sid,))}
    assert "ShieldWall" in skills and skills == set(data["skills"])
    assert con.execute("SELECT COUNT(*) FROM snapshot_item WHERE snapshot_id=?", (sid,)).fetchone()[0] == len(data["items"])
    con.close()
    j = build_db.query_journey(bid)
    assert "전환 없음" in j and "★" not in j and "🛒" not in j


def test_trade_links_attach_to_item_changes(tmp_path, monkeypatch):
    """trade_links.json 이 있으면 item_changed 변화마다 trade_target 1 + tier×realm 링크가 붙고, 없으면 조용히 0 — 적재는 네트워크 없이 돈다."""
    import json
    build_db.build()
    con = sqlite3.connect(build_db.DB_PATH)
    con.row_factory = sqlite3.Row
    doc = json.loads(build_db.TRADE_LINKS.read_text(encoding="utf-8"))
    n_targets = con.execute("SELECT COUNT(*) FROM trade_target").fetchone()[0]
    assert n_targets == len(doc["entries"]) >= 50
    n_links = con.execute("SELECT COUNT(*) FROM trade_link").fetchone()[0]
    assert n_links == sum(len(t["links"]) for e in doc["entries"] for t in e["tiers"])
    # 링크는 item_changed 변화에만 붙는다
    bad = con.execute("SELECT COUNT(*) FROM trade_target tt JOIN transition_change c ON c.id=tt.change_id "
                      "WHERE c.kind!='item_changed'").fetchone()[0]
    assert bad == 0
    # 임성빈 마지막 전환 투구: 요구 상한 93, 사다리 3단, 국제/한국 링크에 리그 경로
    row = con.execute("SELECT tt.change_id, tt.level_max FROM trade_target tt JOIN transition_change c ON c.id=tt.change_id "
                      "JOIN transition t ON t.id=c.transition_id JOIN build b ON b.id=t.build_id "
                      "WHERE b.name LIKE '젬링%' AND t.order_idx=3 AND c.subject='Helm1'").fetchone()
    assert row["level_max"] == 93
    links = con.execute("SELECT tier, realm, url FROM trade_link WHERE change_id=? ORDER BY tier, realm", (row["change_id"],)).fetchall()
    assert [(r["tier"], r["realm"]) for r in links] == [("T1", "int"), ("T1", "kr"), ("T2", "int"), ("T2", "kr"), ("T3", "int"), ("T3", "kr")]
    assert all("/trade2/search/poe2/HC%20Forbidden%20Rites?q=" in r["url"] for r in links)
    assert "🛒 Helm1 Hallowed Crown (요구≤93)" in build_db.query_journey(_bid(con, "젬링%"))
    con.close()
    # 파일이 없으면 테이블은 비고 나머지 적재는 그대로
    st_before = build_db.build()
    monkeypatch.setattr(build_db, "TRADE_LINKS", tmp_path / "missing.json")
    st = build_db.build()
    assert st["trade_target"] == 0 and st["trade_link"] == 0
    assert st["transition_change"] == st_before["transition_change"] and st["transition_note"] == st_before["transition_note"]


def test_live_counts_merge_only_when_query_is_identical():
    """매물 수는 그 쿼리의 것 — 사다리 임계를 바꾸면 옛 live 숫자는 버려진다."""
    q_same = {"query": {"type": "X"}, "sort": {"price": "asc"}}
    q_new = {"query": {"type": "X", "stats": []}, "sort": {"price": "asc"}}
    out = {("c", 0, "Helm1"): {"tiers": [{"tier": "T1", "query": q_same, "links": {}}, {"tier": "T3", "query": q_new, "links": {}}]}}
    ldoc = {"_meta": {"generated_utc": "2026-09-10T12:00:00+00:00"}, "entries": [{"creator": "c", "transition_idx": 0, "slot": "Helm1", "tiers": [
        {"tier": "T1", "query": q_same, "live": {"int": {"id": "a", "total": 5}}},
        {"tier": "T3", "query": {"query": {"type": "X"}, "sort": {"price": "asc"}}, "live": {"int": {"id": "b", "total": 99}}},  # 옛 T3 쿼리
    ]}]}
    assert build_db.merge_live(out, ldoc) == 1
    tiers = out[("c", 0, "Helm1")]["tiers"]
    assert tiers[0]["live"]["int"] == {"id": "a", "total": 5, "checked_utc": "2026-09-10T12:00:00+00:00"}
    assert "live" not in tiers[1]


def test_support_added_rules_fire_where_the_support_is_socketed():
    """보조 젬 도입은 diff 의 support_added 로 잡히고, 그 보조를 새로 끼우는 전환에 규칙이 붙는다(다른 제작자도 상속)."""
    st = build_db.build()
    con = sqlite3.connect(build_db.DB_PATH)
    assert con.execute("SELECT COUNT(*) FROM transition_change WHERE kind='support_added'").fetchone()[0] > 20
    # 새 스킬(화염파)과 함께 들어온 보조도 support_added 다
    seongbin = _bid(con, "젬링%")
    rows = con.execute("SELECT c.subject FROM transition_change c JOIN transition t ON t.id=c.transition_id "
                       "WHERE t.build_id=? AND t.order_idx=2 AND c.kind='support_added'", (seongbin,)).fetchall()
    assert {"ConcentratedEffect", "SearingFlameTwo"} <= {r[0] for r in rows}
    hits = con.execute("SELECT b.name, t.order_idx FROM transition_note n JOIN transition t ON n.transition_id=t.id "
                       "JOIN build b ON b.id=t.build_id JOIN curation_rule r ON n.rule_id=r.id "
                       "WHERE r.trigger_kind='support_added' AND r.trigger_key='SearingFlameTwo'").fetchall()
    assert (next(h for h in hits if h[0].startswith("젬링"))[1]) == 2
    assert len({h[0] for h in hits}) >= 2, hits   # 같은 보조를 끼우는 다른 제작자 빌드도 상속
    con.close()


def test_two_layers_and_query():
    build_db.build()
    con = sqlite3.connect(build_db.DB_PATH)
    seongbin = _bid(con, "젬링%")
    tid = con.execute("SELECT id FROM transition WHERE build_id=? AND order_idx=2", (seongbin,)).fetchone()[0]
    kinds = {r[0] for r in con.execute(
        "SELECT DISTINCT note_type FROM transition_note WHERE transition_id=?", (tid,))}
    assert {"cost", "condition", "pitfall"} <= kinds, kinds   # 손노동
    skadoosh = _bid(con, "워브링어%")
    con.close()
    j1 = build_db.query_journey(seongbin)
    j2 = build_db.query_journey(skadoosh)
    assert "Flameblast" in j1 and "검은화염 계약" in j1 and "규칙" in j1
    assert "Warbringer" in j2 and "혈마법" in j2 and "[규칙]" in j2
