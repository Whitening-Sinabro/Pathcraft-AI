"""PathcraftAI HC Journey DB — 스키마 생성 + 다중 크리에이터 적재 + 여정 질의.

POE2 하드코어 니치. 크리에이터별 발행 밴드 PoB + 실캐릭 ninja 스냅샷을 diff 해서
'따라 할 여정'(WHAT/WHEN)을 자동 생성하고, VOD/연구/실측에서 뽑은 비용·조건·함정·왜(20%)를
transition_note 로 붙인다. 자동층과 큐레이션층을 물리적으로 분리한다.

입력 .build 는 data/hc_journey/creators/<slug>/ 에 커밋된 픽스처를 쓴다(재현 가능).

사용:
    python -X utf8 python/hc_journey/build_db.py --build
    python -X utf8 python/hc_journey/build_db.py --query          # 전체 빌드 여정
    python -X utf8 python/hc_journey/build_db.py --query --id 2   # 특정 빌드
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
CREATORS_DIR = REPO / "data" / "hc_journey" / "creators"
SCHEMA = HERE / "schema.sql"


def _short(gid: str) -> str:
    base = gid.rsplit("/", 1)[-1]
    return re.sub(r"^(SkillGem|SupportGem|Skill|Support)", "", base) or gid


def load_build(path: Path) -> dict:
    d = json.loads(path.read_text(encoding="utf-8"))
    skills = {}
    for s in d.get("skills", []):
        skills[_short(s.get("id", ""))] = [_short(x.get("id", "")) for x in s.get("support_skills", [])]
    items = {sl.get("inventory_id"): (sl.get("additional_text", "") or "").split("\n")[0].strip()
             for sl in d.get("inventory_slots", [])}
    ps = d.get("passives")
    return {"skills": skills, "items": items,
            "passives_n": len(ps) if isinstance(ps, list) else None, "ascendancy": d.get("ascendancy")}


def diff_snapshots(a: dict, b: dict) -> list[tuple[str, str, str]]:
    out: list[tuple[str, str, str]] = []
    sa, sb = a["skills"], b["skills"]
    for k in sb:
        if k not in sa:
            out.append(("skill_added", k, f"스킬 추가: {k}"))
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


# --- 크리에이터 설정 (다중 적재) ----------------------------------------------
# notes: transition order_idx -> [(note_type, text, evidence)]  ← 검증된 20%만.
CREATORS = [
    {
        "name": "임성빈", "channel": "https://www.youtube.com/@임성빈", "ninja": "dtq03087-0345",
        "build": {"name": "젬링 화염파 -> 검은화염 카오스", "asc": "Gemling Legionnaire",
                  "league": "hc-forbidden-rites", "ssf": 0,
                  "notes": "유탄 육성 -> 52 화염파 전환 -> 검은화염 카오스"},
        "bands": [
            ("ACT1", 12, "planner_band", "seongbin/01_ACT1.build"),
            ("ACT2", 22, "planner_band", "seongbin/02_ACT2.build"),
            ("ACT3-4", 45, "planner_band", "seongbin/03_ACT34.build"),
            ("엔드게임(계획)", None, "planner_band", "seongbin/04_endgame_plan.build"),
            ("실캐릭 lv93", 93, "ninja_live", "seongbin/05_live_lv93.build"),
        ],
        "notes": {
            0: [
                ("why", "이 구간 전직 스킬 '고결한 방어막'이 버프 줄 빨강·초록·파랑 티끌을 쌓는다. "
                        "힘=최대 생명력+2%/개, 민첩=방어/ES+5%/개, 지능=재생+5%/개. 전투 중 최대치 변동의 원인.",
                 "D 19306초"),
                ("condition", "전직은 ACT2 진입만으로 안 되고 혼돈의 시련 완료 후. 실제로는 오후로 미룸.", "B 6419초"),
            ],
            2: [
                ("cost", "화염파 전환 리스펙 준비 골드 순감소 약 50396. 재분배 뒤에도 일반 20포인트 남음.", "C 4550·4725초"),
                ("condition", "화염파 요구 지능 92를 맞춰야 함(47->92), 요구 레벨 52.", "C 4540·4767초"),
                ("pitfall", "무기를 지팡이로 바꾸면 급습이 '잘못된 무기 유형'으로 죽음 -> 제거, 임시 합금 석궁 대체.", "C 4760·4755초"),
                ("why", "세트 전용 패시브(물리->화염)는 세트 II 지팡이에만 넣어야 화염파 쪽에서 먹는다.", "C 9787초"),
                ("cost", "투구 실지불가 = 1 엑잘티드 + 골드 수수료(약 10737~11314). 요구 빨간 매물 착용 불가.", "C 9000초"),
            ],
            3: [
                ("why", "검은화염 계약 키스톤 = 화염 주문 화염 피해 100% 카오스 전환. 저항·증폭 장비 값이 통째로 바뀜.", "F 75초"),
                ("cost", "90레벨 재분배로 시작, 골드 211147->145094(약 66053 감소). 무기 세트 포인트도 반환.", "F 30·90초"),
                ("survival", "카오스 저항 챙김(lv93 카오스 65). 후반은 생명력이 아니라 에너지 보호막 중심.", "실캐릭 defensiveStats"),
                ("offstream", "세트 II 용의 돛대(동결 축적78%) 획득 순간이 방송에 없음 -> 오프스트림 구매 추정.", "F 2400초 장착"),
            ],
        },
    },
    {
        "name": "Skadoosh", "channel": "https://www.youtube.com/@Skadoosh", "ninja": "ITheCon-2183",
        "build": {"name": "워브링어 타락 함성 토템", "asc": "Warbringer",
                  "league": "hc-forbidden-rites", "ssf": 0,
                  "notes": "충격파 토템 + Corrupting Cry, 혈마법. (임성빈과 다른 어센던시로 다중 적재 증명)"},
        "bands": [
            ("Lv01-10", 10, "planner_band", "skadoosh/01_Lv01-10.build"),
            ("Lv11-20", 20, "planner_band", "skadoosh/02_Lv11-20.build"),
            ("Lv21-30", 30, "planner_band", "skadoosh/03_Lv21-30.build"),
            ("Lv31-41", 41, "planner_band", "skadoosh/04_Lv31-41.build"),
            ("실캐릭 live", 86, "ninja_live", "skadoosh/05_live.build"),
        ],
        # 검증(ninja lv86 실측 키스톤)만 큐레이션. 나머지 20%(비용·함정)는 후속 VOD 채굴 대상.
        "notes": {
            3: [
                ("why", "Ancestral Bond 키스톤: 토템만 피해를 준다(본인 직접 타격 불가). 토템 중심 빌드의 전제.",
                 "ninja 키스톤 실측(lv86)"),
                ("why", "Blood Magic 키스톤: 마나 대신 생명력으로 스킬 비용 지불. 마나 예약·회복 설계가 통째로 바뀜.",
                 "ninja 키스톤 실측(lv86)"),
            ],
        },
    },
]


def build() -> dict:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    if DB_PATH.exists():
        DB_PATH.unlink()
    con = sqlite3.connect(DB_PATH)
    con.executescript(SCHEMA.read_text(encoding="utf-8"))

    for cfg in CREATORS:
        cur = con.execute("INSERT INTO creator(name, channel_url, ninja_account) VALUES(?,?,?)",
                          (cfg["name"], cfg["channel"], cfg["ninja"]))
        creator_id = cur.lastrowid
        b = cfg["build"]
        cur = con.execute(
            "INSERT INTO build(creator_id, game, league, hardcore, ssf, name, ascendancy, notes) "
            "VALUES(?,?,?,?,?,?,?,?)",
            (creator_id, "poe2", b["league"], 1, b["ssf"], b["name"], b["asc"], b["notes"]))
        build_id = cur.lastrowid

        snaps = []
        for order_idx, (label, lvl, stype, rel) in enumerate(cfg["bands"]):
            data = load_build(CREATORS_DIR / rel)
            cur = con.execute(
                "INSERT INTO snapshot(build_id, order_idx, stage_label, level_hint, source_type, "
                "source_ref, passives_n) VALUES(?,?,?,?,?,?,?)",
                (build_id, order_idx, label, lvl, stype, rel, data["passives_n"]))
            sid = cur.lastrowid
            for main, sup in data["skills"].items():
                con.execute("INSERT INTO snapshot_skill(snapshot_id, main_gem, supports) VALUES(?,?,?)",
                            (sid, main, json.dumps(sup, ensure_ascii=False)))
            for slot, nm in data["items"].items():
                con.execute("INSERT INTO snapshot_item(snapshot_id, slot, item_name) VALUES(?,?,?)", (sid, slot, nm))
            snaps.append((sid, data))

        for i in range(len(snaps) - 1):
            (fid, fa), (tid, tb) = snaps[i], snaps[i + 1]
            cur = con.execute(
                "INSERT INTO transition(build_id, order_idx, from_snapshot, to_snapshot) VALUES(?,?,?,?)",
                (build_id, i, fid, tid))
            trans_id = cur.lastrowid
            for kind, subject, detail in diff_snapshots(fa, tb):
                con.execute("INSERT INTO transition_change(transition_id, kind, subject, detail) VALUES(?,?,?,?)",
                            (trans_id, kind, subject, detail))
            for note_type, text, ev in cfg["notes"].get(i, []):
                con.execute("INSERT INTO transition_note(transition_id, note_type, text, evidence_ref) VALUES(?,?,?,?)",
                            (trans_id, note_type, text, ev))

    con.commit()
    stats = {t: con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
             for t in ("creator", "build", "snapshot", "transition", "transition_change", "transition_note")}
    con.close()
    return stats


def query_journey(build_id: int) -> str:
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    b = con.execute("SELECT * FROM build WHERE id=?", (build_id,)).fetchone()
    cr = con.execute("SELECT name FROM creator WHERE id=?", (b["creator_id"],)).fetchone()
    out = [f"# 여정: {cr['name']} — {b['name']}  [{b['game']} · "
           f"{'HC' if b['hardcore'] else 'SC'}{' SSF' if b['ssf'] else ''} · {b['ascendancy']}]"]
    snaps = con.execute("SELECT * FROM snapshot WHERE build_id=? ORDER BY order_idx", (build_id,)).fetchall()
    out.append("스냅샷: " + " → ".join(f"{s['stage_label']}({s['source_type']},P{s['passives_n']})" for s in snaps))
    for t in con.execute("SELECT * FROM transition WHERE build_id=? ORDER BY order_idx", (build_id,)).fetchall():
        f = con.execute("SELECT stage_label FROM snapshot WHERE id=?", (t["from_snapshot"],)).fetchone()[0]
        to = con.execute("SELECT stage_label FROM snapshot WHERE id=?", (t["to_snapshot"],)).fetchone()[0]
        changes = con.execute("SELECT detail FROM transition_change WHERE transition_id=? ORDER BY id", (t["id"],)).fetchall()
        notes = con.execute("SELECT note_type, text, evidence_ref FROM transition_note WHERE transition_id=? ORDER BY id", (t["id"],)).fetchall()
        out.append(f"\n▶ {f} → {to}   [자동 {len(changes)} · 큐레이션 {len(notes)}]")
        for c in changes[:4]:
            out.append(f"    · {c['detail'][:88]}")
        if len(changes) > 4:
            out.append(f"    · … 외 {len(changes) - 4}건")
        for n in notes:
            out.append(f"    ★ ({n['note_type']}) {n['text'][:104]}  <{n['evidence_ref']}>")
    con.close()
    return "\n".join(out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--query", action="store_true")
    ap.add_argument("--id", type=int, default=0)
    a = ap.parse_args()
    if a.build or not (a.build or a.query):
        print("적재 완료:", json.dumps(build(), ensure_ascii=False))
    if a.query:
        import sqlite3 as _s
        con = _s.connect(DB_PATH)
        ids = [a.id] if a.id else [r[0] for r in con.execute("SELECT id FROM build ORDER BY id")]
        con.close()
        for bid in ids:
            print(query_journey(bid))
            print()
