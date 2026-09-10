"""PathcraftAI HC Journey DB — 스키마 생성 + 적재 증명 + 여정 질의.

POE2 하드코어 니치. 크리에이터의 발행 밴드 PoB + 실캐릭 ninja 스냅샷을 diff 해서
'따라 할 여정'(WHAT/WHEN)을 자동으로 만들고, VOD/연구에서 뽑은 비용·조건·함정·왜(20%)를
transition_note 로 붙인다. 자동층과 큐레이션층을 물리적으로 분리한다.

사용:
    python -X utf8 python/hc_journey/build_db.py --build   # DB 생성 + 임성빈 1건 적재
    python -X utf8 python/hc_journey/build_db.py --query    # 적재된 여정 출력
"""
from __future__ import annotations

import argparse
import json
import re
import sqlite3
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
DB_PATH = REPO / "data" / "hc_journey" / "pathcraft_hc.db"
SCHEMA = HERE / "schema.sql"


# --- PoB .build 파싱 (자동층 원천) -------------------------------------------
def _short(gid: str) -> str:
    """Metadata/Items/Gem/SkillGemFlameblast -> Flameblast."""
    base = gid.rsplit("/", 1)[-1]
    return re.sub(r"^(SkillGem|SupportGem|Skill|Support)", "", base) or gid


def load_build(path: Path) -> dict:
    d = json.loads(path.read_text(encoding="utf-8"))
    skills = {}
    for s in d.get("skills", []):
        main = _short(s.get("id", ""))
        sup = [_short(x.get("id", "")) for x in s.get("support_skills", [])]
        skills[main] = sup
    items = {}
    for sl in d.get("inventory_slots", []):
        first = (sl.get("additional_text", "") or "").split("\n")[0].strip()
        items[sl.get("inventory_id")] = first
    passives = d.get("passives")
    return {
        "skills": skills,
        "items": items,
        "passives_n": len(passives) if isinstance(passives, list) else None,
        "ascendancy": d.get("ascendancy"),
    }


def diff_snapshots(a: dict, b: dict) -> list[tuple[str, str, str]]:
    """연속 스냅샷 자동 diff -> (kind, subject, detail)."""
    out: list[tuple[str, str, str]] = []
    sa, sb = a["skills"], b["skills"]
    for k in sb:
        if k not in sa:
            out.append(("skill_added", k, f"주력/스킬 추가: {k}"))
    for k in sa:
        if k not in sb:
            out.append(("skill_removed", k, f"스킬 제거: {k}"))
    for k in sb:
        if k in sa and set(sb[k]) != set(sa[k]):
            new = sorted(set(sb[k]) - set(sa[k]))
            gone = sorted(set(sa[k]) - set(sb[k]))
            if new or gone:
                out.append(("support_changed", k, f"{k} 보조 +{new} -{gone}"))
    ia, ib = a["items"], b["items"]
    for slot, v in ib.items():
        if ia.get(slot) != v and (v or ia.get(slot)):
            out.append(("item_changed", slot, f"{slot}: {ia.get(slot) or '-'} -> {v or '-'}"))
    pa, pb = a.get("passives_n"), b.get("passives_n")
    if pa is not None and pb is not None and pa != pb:
        out.append(("passive_delta", "passives", f"배정 패시브 {pa} -> {pb} (+{pb - pa})"))
    return out


# --- 적재 대상: 임성빈 젬링 화염파 HC (밴드 발행본 + 실캐릭) -------------------
BANDS = [
    ("ACT1", 12, "planner_band", ".tmp/seongbin/ACT 1 - [0.5.5 Hardcore] 젬링 리그 �.build"),
    ("ACT2", 22, "planner_band", ".tmp/seongbin/ACT 2 - [0.5.5 Hardcore] 젬링 리그 �.build"),
    ("ACT3-4", 45, "planner_band", ".tmp/seongbin/ACT 34 - [0.5.5 Hardcore] 젬링 리그.build"),
    ("엔드게임(계획)", None, "planner_band", ".tmp/seongbin/Interludes  End Game - [0.5.5 Hardcore].build"),
    ("실캐릭 lv93", 93, "ninja_live",
     "deliverables/seongbin_from_day1_2026-09-09/planner/임성빈 엔드게임 Lv93 검은화염 카오스.build"),
]

# 검증된 20% (VOD/연구 판독). transition order_idx -> [(note_type, text, evidence)]
NOTES = {
    0: [  # ACT1 -> ACT2
        ("why", "이 구간에서 얻는 전직 스킬 '고결한 방어막'이 버프 줄 빨강·초록·파랑 티끌을 쌓는다. "
                "힘 티끌=최대 생명력+2%/개, 민첩=방어/ES+5%/개, 지능=재생+5%/개. 전투 중 최대치가 오르내리는 원인.",
         "D 19306초 툴팁"),
        ("condition", "전직은 ACT2 진입만으로 되는 게 아니라 혼돈의 시련 완료 후. 실제로는 오후에 미뤄서 함.",
         "B 6419초"),
    ],
    2: [  # ACT3-4 -> 엔드게임(계획): 52 화염파 전환
        ("cost", "화염파 전환 리스펙: 준비 구간 골드 순감소 약 50396(100175->49779). 재분배 뒤에도 일반 20포인트 남음.",
         "C 4550·4725초"),
        ("condition", "화염파 요구 지능 92를 맞춰야 함(지능 47->92). 요구 레벨 52.",
         "C 4540·4767초"),
        ("pitfall", "무기를 지팡이로 바꾸면 급습이 '잘못된 무기 유형'으로 죽는다 -> 즉시 제거. 화염 피해 있는 포격 석궁을 벗고 "
                    "임시 합금 석궁으로 대체(투사체+1 포기).",
         "C 4760·4755초"),
        ("why", "세트 전용 패시브(물리->화염 전환)는 세트 II 지팡이에만 넣어야 화염파 쪽에서 먹는다. 유탄 세트에 넣으면 헛돈다.",
         "C 9787초 본인 발언"),
        ("cost", "투구 실지불가 = 아이템당 1 엑잘티드 오브 + 골드 수수료(약 10737~11314). 요구 레벨 빨간 매물은 착용 불가.",
         "C 9000초"),
    ],
    3: [  # 엔드게임(계획) -> 실캐릭 lv93: 검은화염 카오스 전환
        ("why", "검은화염 계약 키스톤 = 화염 주문 화염 피해 100%를 카오스로 전환. 화염 저항 계산·화염 증폭 장비 값이 통째로 바뀜.",
         "F 75초 선택 화면"),
        ("cost", "9/9 방송 시작 직후 90레벨 재분배로 시작. 골드 211147->145094(관찰 구간 약 66053 감소). 무기 세트 포인트도 반환.",
         "F 30·90초"),
        ("survival", "카오스 저항을 챙긴다(실캐릭 lv93 카오스 저항 65). 후반은 생명력이 아니라 에너지 보호막 중심.",
         "실캐릭 defensiveStats"),
        ("offstream", "세트 II 용의 돛대(동결 축적78%·모든 주문 레벨+5) 획득 순간은 방송에 없음 -> 9/8~9/9 오프스트림 구매 추정.",
         "F 2400초 장착 확정"),
    ],
}


def build() -> dict:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    if DB_PATH.exists():
        DB_PATH.unlink()
    con = sqlite3.connect(DB_PATH)
    con.executescript(SCHEMA.read_text(encoding="utf-8"))

    cur = con.execute(
        "INSERT INTO creator(name, channel_url, ninja_account, notes) VALUES(?,?,?,?)",
        ("임성빈", "https://www.youtube.com/@임성빈", "dtq03087-0345", "POE2 하코 젬링 화염파"))
    creator_id = cur.lastrowid
    cur = con.execute(
        "INSERT INTO build(creator_id, game, league, hardcore, ssf, name, ascendancy, notes) "
        "VALUES(?,?,?,?,?,?,?,?)",
        (creator_id, "poe2", "hc-forbidden-rites", 1, 0,
         "젬링 화염파 -> 검은화염 카오스", "Gemling Legionnaire",
         "유탄 육성 -> 52 화염파 전환 -> 검은화염 카오스"))
    build_id = cur.lastrowid

    snaps = []
    for order_idx, (label, lvl, stype, rel) in enumerate(BANDS):
        b = load_build(REPO / rel)
        cur = con.execute(
            "INSERT INTO snapshot(build_id, order_idx, stage_label, level_hint, source_type, "
            "source_ref, passives_n, ascendancy_n) VALUES(?,?,?,?,?,?,?,?)",
            (build_id, order_idx, label, lvl, stype, rel, b["passives_n"], None))
        sid = cur.lastrowid
        for main, sup in b["skills"].items():
            con.execute("INSERT INTO snapshot_skill(snapshot_id, main_gem, supports) VALUES(?,?,?)",
                        (sid, main, json.dumps(sup, ensure_ascii=False)))
        for slot, nm in b["items"].items():
            con.execute("INSERT INTO snapshot_item(snapshot_id, slot, item_name) VALUES(?,?,?)",
                        (sid, slot, nm))
        snaps.append((sid, b))

    n_changes = 0
    for i in range(len(snaps) - 1):
        (fid, fa), (tid, tb) = snaps[i], snaps[i + 1]
        cur = con.execute(
            "INSERT INTO transition(build_id, order_idx, from_snapshot, to_snapshot) VALUES(?,?,?,?)",
            (build_id, i, fid, tid))
        trans_id = cur.lastrowid
        for kind, subject, detail in diff_snapshots(fa, tb):
            con.execute("INSERT INTO transition_change(transition_id, kind, subject, detail) VALUES(?,?,?,?)",
                        (trans_id, kind, subject, detail))
            n_changes += 1
        for note_type, text, ev in NOTES.get(i, []):
            con.execute("INSERT INTO transition_note(transition_id, note_type, text, evidence_ref) VALUES(?,?,?,?)",
                        (trans_id, note_type, text, ev))

    con.commit()
    stats = {
        "creators": con.execute("SELECT COUNT(*) FROM creator").fetchone()[0],
        "builds": con.execute("SELECT COUNT(*) FROM build").fetchone()[0],
        "snapshots": con.execute("SELECT COUNT(*) FROM snapshot").fetchone()[0],
        "transitions": con.execute("SELECT COUNT(*) FROM transition").fetchone()[0],
        "auto_changes": con.execute("SELECT COUNT(*) FROM transition_change").fetchone()[0],
        "curated_notes": con.execute("SELECT COUNT(*) FROM transition_note").fetchone()[0],
    }
    con.close()
    return stats


def query_journey(build_id: int = 1) -> str:
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    b = con.execute("SELECT * FROM build WHERE id=?", (build_id,)).fetchone()
    cr = con.execute("SELECT name FROM creator WHERE id=?", (b["creator_id"],)).fetchone()
    lines = [f"# 여정: {cr['name']} — {b['name']}  [{b['game']} · "
             f"{'HC' if b['hardcore'] else 'SC'}{' SSF' if b['ssf'] else ''} · {b['ascendancy']}]"]
    snaps = con.execute("SELECT * FROM snapshot WHERE build_id=? ORDER BY order_idx", (build_id,)).fetchall()
    lines.append("스냅샷: " + " → ".join(
        f"{s['stage_label']}({s['source_type']},P{s['passives_n']})" for s in snaps))
    trans = con.execute("SELECT * FROM transition WHERE build_id=? ORDER BY order_idx", (build_id,)).fetchall()
    for t in trans:
        f = con.execute("SELECT stage_label FROM snapshot WHERE id=?", (t["from_snapshot"],)).fetchone()[0]
        to = con.execute("SELECT stage_label FROM snapshot WHERE id=?", (t["to_snapshot"],)).fetchone()[0]
        lines.append(f"\n▶ {f} → {to}")
        changes = con.execute("SELECT kind, detail FROM transition_change WHERE transition_id=? ORDER BY id",
                              (t["id"],)).fetchall()
        lines.append(f"  [자동 diff] {len(changes)}건")
        for c in changes[:5]:
            lines.append(f"    · {c['detail'][:90]}")
        if len(changes) > 5:
            lines.append(f"    · … 외 {len(changes) - 5}건")
        notes = con.execute("SELECT note_type, text, evidence_ref FROM transition_note WHERE transition_id=? ORDER BY id",
                            (t["id"],)).fetchall()
        if notes:
            lines.append(f"  [큐레이션 20%] {len(notes)}건")
            for n in notes:
                lines.append(f"    · ({n['note_type']}) {n['text'][:110]}  <{n['evidence_ref']}>")
    con.close()
    return "\n".join(lines)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--query", action="store_true")
    a = ap.parse_args()
    if a.build or not (a.build or a.query):
        st = build()
        print("적재 완료:", json.dumps(st, ensure_ascii=False))
    if a.query:
        print(query_journey(1))
