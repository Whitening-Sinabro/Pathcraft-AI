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
    st = build_db.build()
    assert st["creator"] == 2 and st["build"] == 2, st
    assert st["snapshot"] == 10 and st["transition"] == 8, st
    assert st["curation_rule"] >= 5, st
    assert st["notes_rule"] >= 4, st        # 규칙에서 자동 부착된 노트
    assert st["notes_hand"] >= 6, st        # 빌드 고유 손노동


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
    assert rule >= 2, rule      # 그래도 키스톤 규칙(Blood Magic·Ancestral Bond)이 붙는다
    con.close()


def test_rule_reused_across_builds():
    """규칙은 한 번 정의되어 여러 빌드/전환에 재사용된다(rule_id 재사용)."""
    build_db.build()
    con = sqlite3.connect(build_db.DB_PATH)
    # Blackflame 규칙(임성빈)과 Blood Magic 규칙(Skadoosh)이 서로 다른 빌드에 붙어 있다.
    used = con.execute("SELECT COUNT(DISTINCT rule_id) FROM transition_note WHERE source='rule'").fetchone()[0]
    assert used >= 4, used
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
