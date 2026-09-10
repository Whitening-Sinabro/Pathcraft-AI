"""HC Journey DB 적재 증명 검증.

핵심 계약: 자동층(transition_change)과 큐레이션층(transition_note)이 둘 다 채워지고,
여정이 스냅샷 순서대로 관통 질의된다.
"""
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "hc_journey"))
import build_db  # noqa: E402


def test_build_and_query():
    stats = build_db.build()
    assert stats["creators"] == 1
    assert stats["builds"] == 1
    assert stats["snapshots"] == 5, stats
    assert stats["transitions"] == 4, stats
    # 자동층: 밴드 diff 가 실제로 나와야 한다(피벗 구간만 20건 이상).
    assert stats["auto_changes"] >= 40, stats
    # 큐레이션 20%: 비용/조건/함정/왜가 붙어야 한다.
    assert stats["curated_notes"] >= 8, stats


def test_two_layers_separated():
    build_db.build()
    con = sqlite3.connect(build_db.DB_PATH)
    # 화염파 전환(ACT3-4 -> 엔드게임계획, order_idx=2)에 자동+큐레이션이 둘 다 있어야 한다.
    tid = con.execute("SELECT id FROM transition WHERE order_idx=2").fetchone()[0]
    n_auto = con.execute("SELECT COUNT(*) FROM transition_change WHERE transition_id=?", (tid,)).fetchone()[0]
    n_note = con.execute("SELECT COUNT(*) FROM transition_note WHERE transition_id=?", (tid,)).fetchone()[0]
    assert n_auto > 0 and n_note > 0, (n_auto, n_note)
    # 큐레이션에 비용/조건/함정이 실제로 있어야 한다(HC 니치 핵심).
    kinds = {r[0] for r in con.execute(
        "SELECT DISTINCT note_type FROM transition_note WHERE transition_id=?", (tid,))}
    assert {"cost", "condition", "pitfall"} <= kinds, kinds
    con.close()


def test_journey_query_readable():
    build_db.build()
    txt = build_db.query_journey(1)
    assert "여정:" in txt
    assert "검은화염 계약" in txt  # 큐레이션 why 가 관통되어 나온다
    assert "Flameblast" in txt     # 자동 diff 가 관통되어 나온다
    assert txt.count("▶") == 4     # 전환 4개
