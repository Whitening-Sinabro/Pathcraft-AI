"""HC Journey — 여정 뷰(HTML). DB 를 사람이 클릭할 수 있는 한 장으로 렌더한다.

빌드마다: 스냅샷 타임라인 → 전환 카드(자동 diff · 손/규칙 노트 · 🛒 거래 링크 사다리 T1/T2/T3, 국제/한국).
매물 수는 live 검색 시각이 붙은 스냅샷으로만 보여 준다(24시간 지나면 숨김). 링크는 ?q= 무상태라 클릭한 사람의 계정으로 검색된다.

스타일은 문서 출력 규칙: 흑백 + 강조색 1개, rgb 만, 시스템 폰트, 그라데이션·그림자·블러 없음.

사용:
    python -X utf8 python/hc_journey/render_journey.py            # data/hc_journey/journey.html
    python -X utf8 python/hc_journey/render_journey.py --id 1 --open
"""
from __future__ import annotations

import argparse
import html
import json
import logging
import sqlite3
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_db  # noqa: E402

log = logging.getLogger("hc_journey.render")
DEFAULT_OUT = build_db.DB_PATH.parent / "journey.html"
LIVE_MAX_AGE = timedelta(hours=24)

CSS = """
:root{--fg:rgb(0,0,0);--bg:rgb(255,255,255);--mute:rgb(110,110,110);--line:rgb(225,225,225);--soft:rgb(245,245,245);--accent:rgb(10,132,255)}
*{box-sizing:border-box}body{margin:0;padding:24px 16px;font:14px/1.5 system-ui,sans-serif;color:var(--fg);background:var(--bg)}
main{max-width:1040px;margin:0 auto}h1{font-size:22px;margin:0 0 4px}h2{font-size:18px;margin:36px 0 6px;padding-top:16px;border-top:2px solid var(--fg)}
h3{font-size:15px;margin:0}.meta{color:var(--mute);font-size:13px}.timeline{margin:8px 0 16px;color:var(--mute);font-size:13px}
.card{border:1px solid var(--line);padding:14px 16px;margin:12px 0}.head{display:flex;flex-wrap:wrap;gap:8px 16px;align-items:baseline;justify-content:space-between}
.counts{color:var(--mute);font-size:13px}ul{margin:6px 0 0;padding-left:18px}li{margin:2px 0}
.note{margin:8px 0 0;padding:8px 10px;background:var(--soft);border-left:3px solid var(--fg)}.note.rule{border-left-color:var(--accent)}
.tag{display:inline-block;font-size:11px;padding:1px 6px;border:1px solid var(--fg);margin-right:6px}.tag.rule{border-color:var(--accent);color:var(--accent)}
.ev{color:var(--mute);font-size:12px}table{border-collapse:collapse;width:100%;margin-top:10px;font-size:13px}th,td{text-align:left;padding:6px 8px;border-bottom:1px solid var(--line);vertical-align:top}
th{font-weight:600;color:var(--mute)}.mods{color:var(--mute);font-size:12px}.tiers a{display:inline-block;margin:2px 6px 2px 0;padding:3px 8px;border:1px solid var(--accent);color:var(--accent);text-decoration:none;font-size:12px}
.tiers a:hover{background:var(--accent);color:var(--bg)}.live{color:var(--mute);font-size:11px;margin-left:4px}details summary{cursor:pointer;color:var(--mute);font-size:12px}
@media (max-width:600px){table,thead,tbody,tr,th,td{display:block}th{display:none}td{border:0;padding:2px 0}tr{border-bottom:1px solid var(--line);padding:8px 0}}
"""


def _e(s) -> str:
    return html.escape("" if s is None else str(s))


def _fresh(checked: str | None, now: datetime) -> bool:
    if not checked:
        return False
    try:
        return now - datetime.fromisoformat(checked) <= LIVE_MAX_AGE
    except ValueError:
        return False


def render_build(con: sqlite3.Connection, build_id: int, now: datetime) -> str:
    b = con.execute("SELECT * FROM build WHERE id=?", (build_id,)).fetchone()
    cr = con.execute("SELECT * FROM creator WHERE id=?", (b["creator_id"],)).fetchone()
    mode = ("HC" if b["hardcore"] else "SC") + (" SSF" if b["ssf"] else "")
    out = [f"<h2>{_e(cr['name'])} — {_e(b['name'])}</h2>",
           f"<div class='meta'>{_e(b['game'])} · {mode} · {_e(b['ascendancy'])} · 리그 {_e(b['league'])}"
           + (f" · <a href='{_e(cr['channel_url'])}'>출처</a>" if cr["channel_url"] else "") + "</div>"]
    if b["notes"]:
        out.append(f"<div class='meta'>{_e(b['notes'])}</div>")
    snaps = con.execute("SELECT * FROM snapshot WHERE build_id=? ORDER BY order_idx", (build_id,)).fetchall()
    out.append("<div class='timeline'>" + " → ".join(
        f"{_e(s['stage_label'])}{' (≤' + str(s['level_hint']) + ')' if s['level_hint'] else ''} · P{s['passives_n'] or '-'}" for s in snaps) + "</div>")
    seen_rules: set[int] = set()  # 같은 빌드 안에서 같은 규칙은 첫 전환에만 전문, 이후는 한 줄로 접는다(슬롯 규칙이 밴드마다 붙는다)
    for t in con.execute("SELECT * FROM transition WHERE build_id=? ORDER BY order_idx", (build_id,)).fetchall():
        f = con.execute("SELECT stage_label FROM snapshot WHERE id=?", (t["from_snapshot"],)).fetchone()[0]
        to = con.execute("SELECT stage_label, level_hint FROM snapshot WHERE id=?", (t["to_snapshot"],)).fetchone()
        changes = con.execute("SELECT * FROM transition_change WHERE transition_id=? ORDER BY id", (t["id"],)).fetchall()
        notes = con.execute("SELECT * FROM transition_note WHERE transition_id=? ORDER BY source DESC, id", (t["id"],)).fetchall()
        nh = sum(1 for n in notes if n["source"] == "hand")
        out.append("<div class='card'>")
        out.append(f"<div class='head'><h3>{_e(f)} → {_e(to['stage_label'])}</h3>"
                   f"<span class='counts'>자동 {len(changes)} · 손 {nh} · 규칙 {len(notes) - nh}</span></div>")
        by_kind: dict[str, list] = {}
        for c in changes:
            by_kind.setdefault(c["kind"], []).append(c)
        out.append("<details><summary>자동 diff " + " · ".join(f"{k} {len(v)}" for k, v in by_kind.items()) + "</summary><ul>")
        for c in changes:
            out.append(f"<li>{_e(c['detail'])}</li>")
        out.append("</ul></details>")
        repeated = []
        for n in notes:
            if n["source"] == "rule" and n["rule_id"] in seen_rules:
                repeated.append(n)
                continue
            if n["source"] == "rule":
                seen_rules.add(n["rule_id"])
            cls = "note rule" if n["source"] == "rule" else "note"
            tag = "규칙" if n["source"] == "rule" else "손"
            out.append(f"<div class='{cls}'><span class='tag {'rule' if n['source'] == 'rule' else ''}'>{tag} · {_e(n['note_type'])}</span>"
                       f"{_e(n['text'])} <span class='ev'>&lt;{_e(n['evidence_ref'])}&gt;</span></div>")
        if repeated:
            out.append("<details class='repeat'><summary>앞서 본 규칙 " + str(len(repeated)) + "건 (같은 지식이 이 전환에도 적용)</summary>")
            for n in repeated:
                out.append(f"<div class='note rule'><span class='tag rule'>규칙 · {_e(n['note_type'])}</span>{_e(n['text'][:70])}…</div>")
            out.append("</details>")
        targets = con.execute(
            "SELECT tt.*, c.subject AS slot FROM trade_target tt JOIN transition_change c ON c.id=tt.change_id "
            "WHERE c.transition_id=? ORDER BY c.id", (t["id"],)).fetchall()
        if targets:
            out.append("<table><thead><tr><th>🛒 슬롯</th><th>아이템 · 옵션</th><th>거래소 링크(즉시 구입, 요구 레벨 상한)</th></tr></thead><tbody>")
            for tg in targets:
                mods = json.loads(tg["mods_json"])
                unm = json.loads(tg["unmapped_json"])
                links = con.execute("SELECT * FROM trade_link WHERE change_id=? ORDER BY tier, realm", (tg["change_id"],)).fetchall()
                cells = []
                for tier in ("T1", "T2", "T3"):
                    rows = [l for l in links if l["tier"] == tier]
                    if not rows:
                        continue
                    label = {"T1": "그대로", "T2": "핵심", "T3": "같은 부위"}[tier]
                    parts = []
                    for l in rows:
                        realm = "국제" if l["realm"] == "int" else "한국"
                        live = ""
                        if l["live_total"] is not None and _fresh(l["live_checked_utc"], now):
                            live = f"<span class='live'>{l['live_total']}건</span>"
                        parts.append(f"<a href='{_e(l['url'])}' target='_blank' rel='noopener' title='{_e(l['note'])}'>{tier} {label} · {realm}{live}</a>")
                    cells.append("".join(parts))
                mods_html = "<div class='mods'>" + " · ".join(_e(m) for m in mods) + (
                    f" <span class='ev'>(미매핑: {_e(', '.join(unm))})</span>" if unm else "") + "</div>"
                out.append(f"<tr><td>{_e(tg['slot'])}</td><td><b>{_e(tg['base'])}</b>"
                           f"{' <span class=ev>유니크</span>' if tg['unique_base'] else ''}{mods_html}</td>"
                           f"<td class='tiers'>{''.join(cells)}<div class='ev'>요구 ≤ {tg['level_max'] or '-'}</div></td></tr>")
            out.append("</tbody></table>")
        out.append("</div>")
    return "\n".join(out)


def render(build_ids: list[int] | None = None, now: datetime | None = None) -> str:
    now = now or datetime.now(timezone.utc)
    con = sqlite3.connect(build_db.DB_PATH)
    con.row_factory = sqlite3.Row
    ids = build_ids or [r[0] for r in con.execute("SELECT id FROM build ORDER BY id")]
    st = {t: con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] for t in ("creator", "transition", "transition_note", "curation_rule", "trade_link")}
    body = "\n".join(render_build(con, i, now) for i in ids)
    con.close()
    return (f"<!doctype html><html lang='ko'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>"
            f"<title>PathcraftAI HC 여정</title><style>{CSS}</style></head><body><main>"
            f"<h1>PathcraftAI — POE2 하드코어 여정 DB</h1>"
            f"<div class='meta'>크리에이터 {st['creator']} · 전환 {st['transition']} · 노트 {st['transition_note']}(규칙 {st['curation_rule']}) · 거래 링크 {st['trade_link']} · "
            f"렌더 {now.isoformat(timespec='minutes')}. 링크는 클릭한 사람의 거래소 계정으로 검색되며 매물 수는 검색 시각의 스냅샷(24시간 뒤 숨김).</div>"
            f"{body}</main></body></html>")


COMPARE_KEYS = ("Flameblast", "OilGrenade", "Tornado", "ElementalWeakness", "Despair", "Blasphemy", "ArcticArmour",
                "CastOnElementalAilment", "HeraldOfAsh", "ShockwaveTotem", "VolcanicFissure", "ForgeHammer")


def render_comparison(con: sqlite3.Connection) -> str:
    """같은 전직 빌드가 2개 이상이면 핵심 스킬 도입 시점(전환·요구 레벨)을 제작자별로 나란히. '같은 빌드도 내부가 갈린다' 를 보여 주는 표."""
    groups: dict[str, list] = {}
    for b in con.execute("SELECT b.id, b.ascendancy, c.name AS creator FROM build b JOIN creator c ON c.id=b.creator_id ORDER BY b.id"):
        groups.setdefault(b["ascendancy"], []).append(b)
    out = []
    for asc, builds in groups.items():
        if len(builds) < 2:
            continue
        cells: dict[str, dict[int, str]] = {}
        for b in builds:
            for r in con.execute(
                "SELECT c.subject, s.stage_label, s.level_hint FROM transition_change c JOIN transition t ON t.id=c.transition_id "
                "JOIN snapshot s ON s.id=t.to_snapshot WHERE t.build_id=? AND c.kind='skill_added' ORDER BY t.order_idx", (b["id"],)):
                cells.setdefault(r["subject"], {}).setdefault(b["id"], f"{r['stage_label']}" + (f" (≤{r['level_hint']})" if r["level_hint"] else ""))
        keys = [k for k in COMPARE_KEYS if k in cells] + sorted(k for k in cells if k not in COMPARE_KEYS and len(cells[k]) >= 2)
        out.append(f"<h2>같은 전직 대조 — {_e(asc)}</h2><div class='meta'>스킬을 어느 전환에서 넣는지. 빈칸 = 그 제작자 밴드에는 없음.</div>")
        out.append("<table><thead><tr><th>스킬</th>" + "".join(f"<th>{_e(b['creator'])}</th>" for b in builds) + "</tr></thead><tbody>")
        for k in keys:
            out.append(f"<tr><td>{_e(k)}</td>" + "".join(f"<td>{_e(cells[k].get(b['id'], ''))}</td>" for b in builds) + "</tr>")
        out.append("</tbody></table>")
    return "\n".join(out)


def render_split(out_dir: Path, now: datetime | None = None) -> list[Path]:
    """빌드마다 journey_<id>.html + 목차 journey.html. ?q= 링크가 길어 한 장에 다 넣으면 0.5MB 를 넘는다."""
    now = now or datetime.now(timezone.utc)
    con = sqlite3.connect(build_db.DB_PATH)
    con.row_factory = sqlite3.Row
    builds = con.execute("SELECT b.id, b.name, b.hardcore, b.ssf, b.ascendancy, c.name AS creator FROM build b "
                         "JOIN creator c ON c.id=b.creator_id ORDER BY b.id").fetchall()
    comparison = render_comparison(con)
    con.close()
    out_dir.mkdir(parents=True, exist_ok=True)
    written = []
    items = []
    for b in builds:
        p = out_dir / f"journey_{b['id']}.html"
        p.write_text(render([b["id"]], now), encoding="utf-8")
        written.append(p)
        mode = ("HC" if b["hardcore"] else "SC") + (" SSF" if b["ssf"] else "")
        items.append(f"<li><a href='{p.name}'>{_e(b['creator'])} — {_e(b['name'])}</a> <span class='meta'>{mode} · {_e(b['ascendancy'])}</span></li>")
    index = out_dir / "journey.html"
    index.write_text(f"<!doctype html><html lang='ko'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>"
                     f"<title>PathcraftAI HC 여정</title><style>{CSS}</style></head><body><main><h1>PathcraftAI — POE2 하드코어 여정 DB</h1>"
                     f"<div class='meta'>빌드 {len(builds)} · 렌더 {now.isoformat(timespec='minutes')}</div><ul>{''.join(items)}</ul>"
                     f"{comparison}</main></body></html>",
                     encoding="utf-8")
    written.append(index)
    return written


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--id", type=int, action="append", help="빌드 id(반복 가능). 비우면 빌드별 파일 + 목차")
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT, help="--id 를 줬을 때의 출력 파일. 비우면 같은 폴더에 journey_<id>.html + journey.html")
    ap.add_argument("--open", action="store_true", help="렌더 후 기본 브라우저로 연다")
    a = ap.parse_args()
    if a.id:
        page = render(a.id)
        a.out.parent.mkdir(parents=True, exist_ok=True)
        a.out.write_text(page, encoding="utf-8")
        target = a.out
        log.info("여정 뷰 → %s (%d bytes)", a.out, len(page.encode("utf-8")))
    else:
        files = render_split(a.out.parent)
        target = files[-1]
        log.info("여정 뷰 → %s (%d 파일)", target, len(files))
    if a.open:
        subprocess.run(["powershell", "-NoProfile", "-Command", f"Start-Process '{target}'"], check=False)
