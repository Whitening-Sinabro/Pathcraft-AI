"""HC Journey DB 다중 크리에이터 적재 검증.

계약: (1) 여러 크리에이터/빌드가 적재된다 (2) 자동층·큐레이션층이 분리 채워진다
(3) 여정이 스냅샷 순서대로 관통 질의된다.
"""
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "hc_journey"))
import build_db  # noqa: E402


def _build_id(con, like):
    return con.execute("SELECT id FROM build WHERE name LIKE ?", (like,)).fetchone()[0]


def test_multi_creator_load():
    st = build_db.build()
    assert st["creator"] == 2, st
    assert st["build"] == 2, st
    assert st["snapshot"] == 10, st       # 5 + 5
    assert st["transition"] == 8, st      # 4 + 4
    assert st["transition_change"] >= 60, st
    assert st["transition_note"] >= 10, st


def test_two_layers_separated():
    build_db.build()
    con = sqlite3.connect(build_db.DB_PATH)
    bid = _build_id(con, "젬링%")
    tid = con.execute("SELECT id FROM transition WHERE build_id=? AND order_idx=2", (bid,)).fetchone()[0]
    n_auto = con.execute("SELECT COUNT(*) FROM transition_change WHERE transition_id=?", (tid,)).fetchone()[0]
    n_note = con.execute("SELECT COUNT(*) FROM transition_note WHERE transition_id=?", (tid,)).fetchone()[0]
    assert n_auto > 0 and n_note > 0, (n_auto, n_note)
    kinds = {r[0] for r in con.execute(
        "SELECT DISTINCT note_type FROM transition_note WHERE transition_id=?", (tid,))}
    assert {"cost", "condition", "pitfall"} <= kinds, kinds
    con.close()


def test_journeys_readable():
    build_db.build()
    con = sqlite3.connect(build_db.DB_PATH)
    seongbin = _build_id(con, "젬링%")
    skadoosh = _build_id(con, "워브링어%")
    con.close()
    j1 = build_db.query_journey(seongbin)
    assert "검은화염 계약" in j1 and "Flameblast" in j1 and j1.count("▶") == 4

    j2 = build_db.query_journey(skadoosh)
    assert "Warbringer" in j2 and "Blood Magic" in j2 and j2.count("▶") == 4
    # 서로 다른 어센던시/빌드가 한 DB 안에 공존한다.
    assert "Gemling" in j1 and "Warbringer" in j2
