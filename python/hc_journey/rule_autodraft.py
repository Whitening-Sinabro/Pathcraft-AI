"""HC Journey DB — 큐레이션 규칙 자동 초안 (#1).

전환점(자동 diff 가 아는 "어느 스킬/슬롯/키스톤/전직이 언제 바뀌나") 근처의 자막 창에서
비용·조건·함정·왜·생존 신호를 뽑아 `curation_rule` 후보를 만든다. 사람은 승인만 한다.

정직성 계약 (어기면 지어낸 라벨이 파생물로 번진다):
  * trigger_key 는 언제나 diff/PoB/CREATORS 설정에서 온다. 자막에서 이름을 확정하지 않는다.
  * 자막은 수치·주장·정황의 근거로만 쓴다. 후보 text 는 자막 원문 그대로다(요약·의역 없음).
  * 이 모듈은 CURATION_RULES 를 읽기만 한다. 후보 파일만 쓰고 규칙에 자동 반영하지 않는다(승인 게이트).
  * 시각 앵커는 사람 판독(precision_findings.ROWS: (영상, 초, 관측))에서 잡는다. 자막을 통째로 훑지 않는다.
  * 판독·자막은 크리에이터별로 묶는다. 다른 크리에이터의 영상을 앵커로 빌리지 않는다.

앵커 선택: 판독의 "N레벨" 을 영상별로 forward-fill 해 전환 시작 레벨보다 앞선 판독은 버리고,
영상 시간순으로 앞쪽 클러스터(기본 2개)만 본다 — 전환 '순간' 이 그 근처다.

사용:
    python -X utf8 python/hc_journey/rule_autodraft.py            # data/hc_journey/rule_candidates.json 생성
    python -X utf8 python/hc_journey/rule_autodraft.py --dry-run  # 파일 안 쓰고 요약만
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import logging
import re
import sys
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))
import build_db  # noqa: E402  (읽기 전용으로만 쓴다)

log = logging.getLogger("hc_journey.rule_autodraft")

DELIVERABLE = REPO / "deliverables" / "seongbin_from_day1_2026-09-09"
DEFAULT_OUT = REPO / "data" / "hc_journey" / "rule_candidates.json"

# 크리에이터별 자막·판독 소스. 여기 없는 크리에이터는 트리거가 전부 '소스 없음' 으로 남는다.
# ignore_in_readout: 판독 안의 캐릭터 이름 등 — 별칭이 이 문자열 안에서만 나오면 앵커가 아니다.
CREATOR_SOURCES: dict[str, dict] = {
    "임성빈": {
        "transcripts": DELIVERABLE / "transcripts",
        "readouts": DELIVERABLE / "precision_findings.py",
        "ignore_in_readout": ("임성빈_화염파_젬링",),
    },
}

# 영상 문자 ↔ id. 손노트 evidence("C 4550초")와 같은 표기. 순서 = 방송 시간순. F 는 자막이 없다.
VIDEO_LETTERS = {
    "A": "zKJQyBm4VnI", "B": "GtC5-b4QXec", "C": "C_tkSubXWDk",
    "D": "39kHWKUhwhU", "E": "xnREtaV3m1A", "F": "rsKbeELo0TM",
}
_LETTER_OF = {v: k for k, v in VIDEO_LETTERS.items()}
_ORDER_OF = {v: i for i, v in enumerate(VIDEO_LETTERS.values())}

# 검색 힌트 전용. 판독 관측(사람이 화면 보고 적은 한국어)에서 앵커를 찾을 때만 쓴다.
# 출력 trigger_key 로는 절대 쓰지 않는다. 출처: build_db 규칙 텍스트·precision_findings 관측·.claude/status/poe2_hc_gemling.md.
SEARCH_ALIASES: dict[str, tuple[str, ...]] = {
    "Flameblast": ("화염파",),
    "Tornado": ("회오리",),
    "Despair": ("절망",),
    "ArcticArmour": ("한기의 방어구",),
    "AscendancyVirtuousBarrier": ("고결한 방어막",),
    "HeraldOfAsh": ("재의 전령",),
    "Attrition": ("소모Lv", "소모(", "소모30"),
    "OilGrenade": ("기름 유탄",),
    "FlashGrenade": ("섬광 유탄",),
    "ExplosiveGrenade": ("폭발 유탄",),
    "GasGrenade": ("가스 유탄",),
    "ShockwaveTotem": ("충격파 토템",),
    "CastOnElementalAilment": ("발동",),
    "Blackflame Covenant": ("검은화염 계약", "검은화염"),
    "Gemling Legionnaire": ("젬링 리저네어", "젬링 전직"),
    "Warbringer": ("워브링어",),
    "Ancestral Bond": ("선대의 유대",),
    "Blood Magic": ("혈마법",),
    "Weapon2": ("무기 세트II", "무기 세트 II", "세트II", "세트 II", "무기 세트 2번", "세트 2번"),
    "Weapon1": ("무기 세트I ", "무기 세트I의", "세트I "),
    "Helm1": ("투구",),
}

# note_type 신호(자막 한 줄 단위). 지시서 §2 의 목록을 정규식으로 옮긴 것. 잡담에 흔한 낱말(그래서·맞아요·죽)은 뺐다.
NOTE_SIGNALS: dict[str, re.Pattern[str]] = {
    "cost": re.compile(r"골드|엑잘|액잘|신성한|수수료|가격|비싸|싸게|싼데|구매|매물|팔아|팔고|\d{1,3}(?:,\d{3})+|\d{4,}|\d+만"),
    "condition": re.compile(r"요구|필요하|필요한|찍어 ?줘야|찍어야|맞춰야|지능|민첩|\d+ ?레벨|레벨 ?\d+"),
    "pitfall": re.compile(r"죽었|죽음|죽어|죽을|죽지|안 먹|안 돼|안 되|안됨|바꿔야|잘못|실수|조심|위험|주의|빼고|못 쓰|사용 불가|충족되지|버그|포기해야"),
    "why": re.compile(r"때문|이유|효과|전환|변환|증폭|감폭|키스톤|메커니즘|원리"),
    "survival": re.compile(r"저항|부활|플라스크|생명력|보호막|보막|피통|맞아가지고|맞아서|맞으면|맞았|생존|탱|회복|한 방"),
}
NOISE_SUBJECT = re.compile(r"^PlayerDefault")  # 기본 공격 스킬 — 전환점이 아니다.
# 판독의 "N레벨" 중 캐릭터 레벨만. 구간 끝("54~59레벨")·임계("65레벨 이상")는 정규식으로, 타인·젬·지역 맥락은 낱말로 뺀다.
# 과대추정은 진짜 앵커를 버리고 전환 귀속을 틀리게 하므로(과소추정은 앞쪽 앵커가 몇 개 더 통과할 뿐) 제외를 공격적으로 둔다.
_LEVEL_RE = re.compile(r"(?<![~\-\d])(\d{1,3})레벨(?! ?(?:이상|미만|구간|까지|부터))")
_LEVEL_NOISE = ("다른 이름", "다른 캐릭터", "사망 알림", "구간별", "몬스터", "지역 레벨", "미가공", "권능", "부여", "요구")


def parse_character_level(readout: str) -> int | None:
    vals = []
    for m in _LEVEL_RE.finditer(readout):
        ctx = readout[max(0, m.start() - 16):m.end() + 8]
        if any(n in ctx for n in _LEVEL_NOISE):
            continue
        vals.append(int(m.group(1)))
    return max(vals) if vals else None


@dataclass(frozen=True)
class Segment:
    start: float
    duration: float
    text: str


@dataclass(frozen=True)
class Anchor:
    video_id: str
    sec: float
    readout: str
    level: int | None = None  # 판독에 적힌(또는 forward-fill 된) 캐릭터 레벨


@dataclass(frozen=True)
class Trigger:
    creator: str
    transition_idx: int
    transition_label: str
    trigger_kind: str
    trigger_key: str
    level_from: int | None  # 전환 시작 스냅샷의 레벨 힌트(앵커 하한)


# --- 입력 적재 ------------------------------------------------------------------

def load_transcripts(directory: Path) -> dict[str, list[Segment]]:
    out: dict[str, list[Segment]] = {}
    for p in sorted(directory.glob("*.json")):
        d = json.loads(p.read_text(encoding="utf-8"))
        segs = d.get("segments") if isinstance(d, dict) else None
        if not isinstance(segs, list):
            log.warning("자막 형식 아님(segments 없음): %s", p.name)
            continue
        out[d.get("video_id") or p.stem] = [
            Segment(float(s["start"]), float(s.get("duration", 0.0)), str(s.get("text", "")).strip()) for s in segs]
    return out


def load_readouts(path: Path) -> list[Anchor]:
    """precision_findings.py 의 ROWS[(video, sec, observation, ...)] 를 파일 경로로 import 해 앵커로 만든다."""
    spec = importlib.util.spec_from_file_location("hc_readouts", path)
    if spec is None or spec.loader is None:
        raise FileNotFoundError(path)
    mod = importlib.util.module_from_spec(spec)
    prev = sys.dont_write_bytecode
    sys.dont_write_bytecode = True  # 판독 파일 옆에 __pycache__ 를 남기지 않는다(읽기 전용 입력)
    try:
        spec.loader.exec_module(mod)
    finally:
        sys.dont_write_bytecode = prev
    rows = getattr(mod, "ROWS", None)
    if not isinstance(rows, list):
        raise ValueError(f"ROWS 없음: {path}")
    anchors = []
    for r in rows:
        if len(r) < 3:
            continue
        anchors.append(Anchor(str(r[0]), float(r[1]), str(r[2]), parse_character_level(str(r[2]))))
    return infer_levels(anchors)


def infer_levels(anchors: list[Anchor]) -> list[Anchor]:
    """캐릭터 레벨은 방송 타임라인(영상 순서·초) 전체에서 단조증가하므로 running max 로 채운다.

    판독의 "N레벨" 에는 젬 레벨("13레벨 권능 착취", "(1레벨)")이 섞이는데 그 값은 캐릭터 레벨보다 작으므로 running max 를
    끌어올리지 못한다 — 그래서 직전 값 forward-fill 대신 max 를 쓴다. 캐릭터 레벨보다 큰 값이 나올 수 있는 맥락(저항 페널티
    구간 "54~59레벨", 타인 사망 알림 "다른 이름의 9레벨")은 parse_character_level 이 미리 걸러야 한다. 타임라인 맨 앞에서
    아직 레벨이 없는 판독은 같은 영상의 첫 레벨로 채우고, 그것도 없으면 None(미상 → 게이트 통과).
    """
    ordered = sorted(anchors, key=lambda a: (_ORDER_OF.get(a.video_id, 99), a.video_id, a.sec))
    first_in_video: dict[str, int] = {}
    for a in ordered:
        if a.level is not None:
            first_in_video.setdefault(a.video_id, a.level)
    out: list[Anchor] = []
    running: int | None = None
    for a in ordered:
        if a.level is not None:
            running = a.level if running is None else max(running, a.level)
        level = running if running is not None else first_in_video.get(a.video_id)
        out.append(a if level == a.level else replace(a, level=level))
    return out


def _level_from(bands: list, i: int) -> int | None:
    for j in range(i, -1, -1):  # 시작 스냅샷 레벨 힌트, 없으면 그 앞에서 가장 가까운 것
        if bands[j][1] is not None:
            return bands[j][1]
    return None


def transition_triggers(creators: list[dict] | None = None) -> list[Trigger]:
    """build_db 와 같은 방식으로 전환점을 세어 트리거를 만든다. 이름은 전부 diff/설정에서 온다."""
    out: list[Trigger] = []
    for cfg in (creators if creators is not None else build_db.CREATORS):
        bands = cfg["bands"]
        snaps = [build_db.load_build(build_db.CREATORS_DIR / rel) for (_l, _lv, _st, rel) in bands]
        labels = [b[0] for b in bands]
        for i in range(len(snaps) - 1):
            label = f"{labels[i]} → {labels[i + 1]}"
            lv = _level_from(bands, i)
            for kind, subject, _detail in build_db.diff_snapshots(snaps[i], snaps[i + 1]):
                if kind == "skill_added" and not NOISE_SUBJECT.match(subject):
                    out.append(Trigger(cfg["name"], i, label, "skill_added", subject, lv))
                elif kind == "item_changed":
                    out.append(Trigger(cfg["name"], i, label, "item_slot_change", subject, lv))
        if len(snaps) >= 2:
            first = f"{labels[0]} → {labels[1]}"
            last = f"{labels[-2]} → {labels[-1]}"
            out.append(Trigger(cfg["name"], 0, first, "ascendancy", cfg["build"]["asc"], _level_from(bands, 0)))
            for ks in cfg.get("keystones", []):
                out.append(Trigger(cfg["name"], len(snaps) - 2, last, "keystone", ks, _level_from(bands, len(snaps) - 2)))
    return out


# --- 앵커 → 창 → 신호 ------------------------------------------------------------

def find_anchors(trigger: Trigger, anchors: list[Anchor], ignore: tuple[str, ...] = ()) -> list[Anchor]:
    """별칭이 판독에 나오고(캐릭터 이름 등 제외), 레벨이 전환 시작 레벨 이상인 앵커. 영상·시간순."""
    aliases = SEARCH_ALIASES.get(trigger.trigger_key, ())
    if not aliases:
        return []
    hits = []
    for a in anchors:
        text = a.readout
        for ig in ignore:
            text = text.replace(ig, "")
        if not any(al in text for al in aliases):
            continue
        if trigger.level_from is not None and a.level is not None and a.level < trigger.level_from:
            continue
        hits.append(a)
    return sorted(hits, key=lambda a: (_ORDER_OF.get(a.video_id, 99), a.video_id, a.sec))


def cluster_anchors(anchors: list[Anchor], gap: float) -> list[list[Anchor]]:
    """같은 영상에서 gap 초 이내로 이어지는 앵커를 한 창으로 묶는다. 입력 순서(영상·시간순)를 지킨다."""
    clusters: list[list[Anchor]] = []
    for a in anchors:
        cur = clusters[-1] if clusters else None
        if cur and cur[-1].video_id == a.video_id and a.sec - cur[-1].sec <= gap:
            cur.append(a)
        else:
            clusters.append([a])
    return clusters


def window(segments: list[Segment], lo: float, hi: float) -> list[Segment]:
    return [s for s in segments if lo <= s.start <= hi and s.text]


def classify(text: str) -> dict[str, list[str]]:
    """한 자막 줄이 어느 note_type 신호를 담는지. {note_type: [매칭 문자열...]}"""
    hits: dict[str, list[str]] = {}
    for nt, pat in NOTE_SIGNALS.items():
        found = pat.findall(text)
        if found:
            hits[nt] = found
    return hits


def _yt(video_id: str, sec: float) -> str:
    return f"https://www.youtube.com/watch?v={video_id}&t={int(sec)}s"


def _owner(group: list[Trigger], level: int | None, default: Trigger) -> Trigger:
    """같은 trigger_key 가 여러 전환에 있으면(Helm1 은 밴드마다 바뀐다) 앵커 레벨 이하에서 가장 늦게 시작하는 전환이 주인.
    레벨 미상이면 지금 처리 중인 트리거, 전부 레벨 위면 가장 이른 전환."""
    if len(group) == 1 or level is None:
        return default
    eligible = [t for t in group if t.level_from is None or t.level_from <= level]
    if not eligible:
        return min(group, key=lambda t: t.transition_idx)
    best = max((t.level_from if t.level_from is not None else -1) for t in eligible)
    return min((t for t in eligible if (t.level_from if t.level_from is not None else -1) == best),
               key=lambda t: t.transition_idx)


def draft_candidates(triggers: list[Trigger], anchors: list[Anchor], transcripts: dict[str, list[Segment]],
                     window_sec: float = 90.0, min_hits: int = 2, max_lines: int = 8, max_clusters: int = 2,
                     ignore: tuple[str, ...] = ()) -> dict:
    existing = {(k, key, nt) for (k, key, nt, _t, _e) in build_db.CURATION_RULES}
    groups: dict[tuple, list[Trigger]] = {}
    for tr in triggers:
        groups.setdefault((tr.creator, tr.trigger_kind, tr.trigger_key), []).append(tr)
    candidates: list[dict] = []
    unanchored: list[dict] = []
    skipped: list[dict] = []
    seen: set[tuple] = set()
    for tr in triggers:
        hits_anchor = find_anchors(tr, anchors, ignore)
        if not hits_anchor:
            reason = "alias 없음(검색 힌트 미등록)" if tr.trigger_key not in SEARCH_ALIASES else "판독에 언급 없음(레벨 게이트 포함)"
            unanchored.append({"creator": tr.creator, "transition": tr.transition_label,
                               "trigger_kind": tr.trigger_kind, "trigger_key": tr.trigger_key, "reason": reason})
            continue
        for cl in cluster_anchors(hits_anchor, window_sec)[:max_clusters]:
            vid = cl[0].video_id
            letter = _LETTER_OF.get(vid, vid)
            segs = transcripts.get(vid)
            lo, hi = cl[0].sec - window_sec, cl[-1].sec + window_sec
            if segs is None:
                skipped.append({"trigger_key": tr.trigger_key, "video": letter, "sec": [int(a.sec) for a in cl],
                                "reason": "자막 없음"})
                continue
            per_type: dict[str, list[tuple[Segment, list[str]]]] = {}
            for s in window(segs, lo, hi):
                for nt, found in classify(s.text).items():
                    per_type.setdefault(nt, []).append((s, found))
            for nt, rows in per_type.items():
                if len(rows) < min_hits:
                    continue
                dedupe_key = (tr.trigger_kind, tr.trigger_key, nt, vid, int(lo))
                if dedupe_key in seen:
                    continue
                seen.add(dedupe_key)
                shown = rows[:max_lines]
                first = shown[0][0]
                owner = _owner(groups[(tr.creator, tr.trigger_kind, tr.trigger_key)], cl[0].level, tr)
                candidates.append({
                    "trigger_kind": tr.trigger_kind,
                    "trigger_key": tr.trigger_key,
                    "note_type": nt,
                    "text": " / ".join(s.text for s, _f in shown),
                    "evidence": {
                        "video": letter, "video_id": vid, "sec": int(first.start),
                        "ref": f"{letter} {int(first.start)}초",
                        "url": _yt(vid, first.start),
                        "lines": [{"sec": int(s.start), "text": s.text} for s, _f in shown],
                        "anchor": {"n": len(cl), "sec": [int(a.sec) for a in cl], "level": cl[0].level,
                                   "readout": cl[0].readout[:160]},
                    },
                    "signals": sorted({f for _s, found in shown for f in found}),
                    "hits": len(rows),
                    "creator": owner.creator,
                    "transition_idx": owner.transition_idx,
                    "transition": owner.transition_label,
                    "existing_rule": (tr.trigger_kind, tr.trigger_key, nt) in existing,
                    "also_matches": [],
                    "status": "pending",
                })
    candidates = _dedupe_by_evidence(candidates)
    candidates.sort(key=lambda c: (c["creator"], c["transition_idx"], c["trigger_kind"], c["trigger_key"], -c["hits"]))
    return {"candidates": candidates, "unanchored": unanchored, "skipped": skipped}


def _dedupe_by_evidence(candidates: list[dict]) -> list[dict]:
    """같은 (note_type, 영상, 초) 자막 근거가 여러 트리거에 붙으면(스킬 창 판독은 스킬을 전부 나열한다)
    앵커가 가장 많은 트리거 하나에만 주고 나머지 트리거는 also_matches 로 남긴다. 귀속은 사람이 확정한다."""
    groups: dict[tuple, list[dict]] = {}
    for c in candidates:
        groups.setdefault((c["creator"], c["note_type"], c["evidence"]["video_id"], c["evidence"]["sec"]), []).append(c)
    out: list[dict] = []
    for rows in groups.values():
        rows.sort(key=lambda c: -c["evidence"]["anchor"]["n"])
        keep = rows[0]
        keep["also_matches"] = [{"trigger": f"{c['trigger_kind']}/{c['trigger_key']}", "transition": c["transition"],
                                 "existing_rule": c["existing_rule"]} for c in rows[1:]]
        out.append(keep)
    return out


def write_candidates(path: Path, result: dict, meta: dict) -> Path:
    doc = {"_meta": {
        "purpose": "curation_rule 승인 대기 후보. 사람이 골라 build_db.CURATION_RULES 에 옮긴다. 자동 반영 금지.",
        "honesty": "trigger_key 는 diff/PoB/설정에서, text 는 자막 원문 그대로. 자막으로 고유명사를 확정하지 않는다.",
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        **meta,
        "n_candidates": len(result["candidates"]),
        "n_unanchored": len(result["unanchored"]),
        "n_skipped": len(result["skipped"]),
    }, **result}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    return path


def _rel(p: Path) -> str:
    return (p.relative_to(REPO) if p.is_relative_to(REPO) else p).as_posix()


def run(out: Path | None = DEFAULT_OUT, window_sec: float = 90.0, min_hits: int = 2, max_clusters: int = 2,
        creator: str | None = None, sources: dict[str, dict] | None = None) -> dict:
    sources = CREATOR_SOURCES if sources is None else sources
    all_triggers = [t for t in transition_triggers() if creator is None or t.creator == creator]
    result: dict = {"candidates": [], "unanchored": [], "skipped": []}
    used: dict[str, dict] = {}
    for name in sorted({t.creator for t in all_triggers}):
        triggers = [t for t in all_triggers if t.creator == name]
        src = sources.get(name)
        if src is None:
            result["unanchored"] += [{"creator": t.creator, "transition": t.transition_label, "trigger_kind": t.trigger_kind,
                                      "trigger_key": t.trigger_key, "reason": "자막/판독 소스 없음"} for t in triggers]
            continue
        transcripts = load_transcripts(Path(src["transcripts"]))
        anchors = load_readouts(Path(src["readouts"]))
        part = draft_candidates(triggers, anchors, transcripts, window_sec=window_sec, min_hits=min_hits,
                                max_clusters=max_clusters, ignore=tuple(src.get("ignore_in_readout", ())))
        for k in result:
            result[k] += part[k]
        used[name] = {"transcripts": _rel(Path(src["transcripts"])), "readouts": _rel(Path(src["readouts"])),
                      "n_triggers": len(triggers), "n_anchors": len(anchors), "videos": sorted(transcripts)}
    if out is not None:
        write_candidates(out, result, {"window_sec": window_sec, "min_hits": min_hits, "max_clusters": max_clusters,
                                       "sources": used})
        log.info("후보 %d · 앵커 없음 %d · 자막 없음 %d → %s",
                 len(result["candidates"]), len(result["unanchored"]), len(result["skipped"]), _rel(out))
    return result


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--window", type=float, default=90.0, help="앵커 전후 자막 창(초)")
    ap.add_argument("--min-hits", type=int, default=2, help="후보로 올리는 최소 신호 줄 수")
    ap.add_argument("--max-clusters", type=int, default=2, help="트리거당 보는 앵커 클러스터 수(시간순 앞에서부터)")
    ap.add_argument("--creator", default=None)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    r = run(None if a.dry_run else a.out, a.window, a.min_hits, a.max_clusters, a.creator)
    for c in r["candidates"]:
        log.info("[%s] %s/%s (%s) <%s> %s", c["creator"], c["trigger_kind"], c["trigger_key"], c["note_type"],
                 c["evidence"]["ref"], c["text"][:70])
    log.info("후보 %d · 앵커 없음 %d · 자막 없음 %d", len(r["candidates"]), len(r["unanchored"]), len(r["skipped"]))
