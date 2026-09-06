"""poe.ninja 실캐릭을 따라가며 변화마다 인게임 플래너를 다시 만든다.

제작자가 방송하는 동안에만 관측 가능한 것이 있다 — 33레벨 리스펙에서 무엇을 찍는지,
Corrupting Cry 를 어느 함성에 꽂는지, 선대의 유대를 언제 가는지. 사람이 붙어 있지 않아도
그 순간이 남도록 이 스크립트가 폴링하고, 바뀔 때마다 스냅샷·PoB·플래너를 갱신한다.

핵심 사실 두 가지(2026-09-06 실측):
  - `latest` 별칭이 스냅샷 id 없이 동작해서 브라우저 없이 폴링된다.
  - 응답의 `pathOfBuildingExport` 는 **base64url + zlib** 이고 장비까지 실려 있다.
    표준 base64 로 풀면 `invalid bit length repeat` 로 죽는다.

산출물:
  <out>/snapshots/lvNN_HHMM.json   변화 시점의 원본 응답
  <out>/timeline.md               사람이 읽는 변화 이력
  build_planner/<live-name>.build 항상 최신 (설치까지)
  build_planner/<prefix> LvNN.build  전환 레벨 도달 시 영구 보존본

Usage:
    python scripts/track_poe2_character.py --account ITheCon-2183 \
        --name SkadooshShoutedHard --overview hc-forbidden-rites \
        --out <dir> --live-name "Warbringer live - Skadoosh" \
        --milestone-prefix "Warbringer" --hours 8
"""
from __future__ import annotations

import argparse
import base64
import json
import logging
import subprocess
import sys
import time
import urllib.parse
import urllib.request
import zlib
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
KST = timezone(timedelta(hours=9))

# 막 경계는 GGPK WorldAreas 에서 유도했다(마을·은신처·맵·디버그 지역 제외한 캠페인 지역의 AreaLevel).
#   1막 1~15(The Riverbank~Root Hollow) · 2막 16~31(Vastiri Outskirts~Dreadnought)
#   3막 33~45(Sandswept Marsh~) · 4막 46~53(Abandoned Prison~Ngakanu)
#   **막간 54~56** — GGPK 는 이 구간을 `Act=6` 으로 두고 월드맵 이름이 문자 그대로
#   `Interlude`(G6_WorldMap)다. 한때 여기를 "잔혹"이라고 적었는데 그건 **내가 붙인 이름**이고
#   게임·가이드·패치노트 어디에도 없다(외부 검증이 잡았다). 출처의 이름을 쓴다.
# 레벨이 아니라 막으로 부르는 이유: 인게임에서 사람이 아는 좌표가 막이다.
#
# **주의: 이것은 레벨 밴드이지 그가 지금 어디 있는지가 아니다.** WorldAreas.AreaLevel 은
# 지역 레벨이라 캐릭터 레벨만으로 체류 지역을 확정할 수 없다. 이름은 "그 레벨대의 구간"을
# 가리키는 라벨로만 쓴다.
ACT_ENTRY = ((16, "Act2"), (33, "Act3"), (46, "Act4"), (54, "막간"), (65, "엔드게임"))

log = logging.getLogger("track")


def act_of(level: int | None) -> str:
    """레벨 -> 그 레벨대 구간의 이름. 경계는 GGPK WorldAreas 실측값이다.

    체류 지역을 단정하지 않는다 — 레벨 밴드 라벨이다.
    """
    name = "Act1"
    for entry, label in ACT_ENTRY:
        if (level or 0) >= entry:
            name = label
    return name


class RateLimited(Exception):
    """429. 같은 주기로 계속 두드리면 차단이 길어지므로 호출부가 물러서야 한다."""


def fetch(account: str, name: str, overview: str) -> dict:
    # 한글 캐릭터 이름은 그대로 붙이면 urllib 이 헤더를 ascii 로 인코딩하다 죽는다
    # (UnicodeEncodeError, HTTP 오류가 아니라 요청 자체가 안 나간다). 여기서 인코딩한다.
    # `safe=""` 로 `#` 까지 퍼센트 인코딩한다 — 계정 구분자가 `#` 인 경우 프래그먼트로 잘린다.
    query = urllib.parse.urlencode({"account": account, "name": name, "overview": overview},
                                   quote_via=urllib.parse.quote, safe="")
    url = f"https://poe.ninja/poe2/api/builds/latest/character?{query}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        return json.load(urllib.request.urlopen(req, timeout=30))
    except urllib.error.HTTPError as exc:
        if exc.code == 429:
            raise RateLimited(str(exc)) from exc
        raise


def fetch_patiently(account: str, name: str, overview: str,
                    tries: int = 8, wait: int = 60) -> dict:
    """429 를 만나면 물러섰다 다시 온다. 시작 조회가 여기서 죽으면 밤새 아무것도 안 남는다."""
    for attempt in range(1, tries + 1):
        try:
            return fetch(account, name, overview)
        except RateLimited:
            if attempt == tries:
                raise
            log.warning("시작 조회 429 (%d/%d) — %d초 후 재시도", attempt, tries, wait)
            time.sleep(wait)
            wait = min(wait * 2, 1800)
    raise RuntimeError("unreachable")


def decode_pob(code: str) -> str:
    """ninja 의 PoB 익스포트는 base64url + zlib 이다."""
    fixed = code.replace("-", "+").replace("_", "/")
    raw = base64.b64decode(fixed + "=" * (-len(fixed) % 4))
    return zlib.decompress(raw).decode("utf-8", errors="replace")


def fingerprint(d: dict) -> tuple:
    """무엇이 바뀌면 '변화'인가. 방어 수치의 미세 흔들림은 제외한다."""
    ds = d.get("defensiveStats") or {}
    return (
        d.get("level"),
        (d.get("passiveCounts") or {}).get("passives"),
        (d.get("passiveCounts") or {}).get("ascendancy"),
        tuple(sorted(d.get("keystones") or [])),
        tuple(sorted("+".join(g["name"] for g in (s.get("allGems") or []))
                     for s in d.get("skills") or [])),
        tuple(sorted(f'{i["itemSlot"]}:{(i.get("itemData") or {}).get("name")}'
                     for i in d.get("items") or [])),
        ds.get("life"), ds.get("spirit"),
    )


def summary(d: dict) -> str:
    ds = d.get("defensiveStats") or {}
    res = "/".join(str(ds.get(k)) for k in
                   ("fireResistance", "coldResistance", "lightningResistance", "chaosResistance"))
    return (f"Lv{d.get('level')} · 패시브 {(d.get('passiveCounts') or {}).get('passives')}"
            f"(전직 {(d.get('passiveCounts') or {}).get('ascendancy')}) · 생명력 {ds.get('life')} · "
            f"방어도 {ds.get('armour')} · 막기 {ds.get('blockChance')}% · EHP {ds.get('effectiveHealthPool')} · "
            f"저항 {res} · 정신력 {ds.get('spirit')} · 키스톤 {d.get('keystones') or '없음'}")


def diff_lines(old: dict, new: dict) -> list[str]:
    out: list[str] = []
    if old.get("level") != new.get("level"):
        out.append(f"레벨 {old.get('level')} -> {new.get('level')}")
    for label, key in (("패시브", "passives"), ("전직", "ascendancy")):
        a = (old.get("passiveCounts") or {}).get(key)
        b = (new.get("passiveCounts") or {}).get(key)
        if a != b:
            out.append(f"{label} {a} -> {b}")
    ka, kb = sorted(old.get("keystones") or []), sorted(new.get("keystones") or [])
    if ka != kb:
        out.append(f"**키스톤 {ka or '없음'} -> {kb or '없음'}**")

    def gems(d):
        return {" + ".join(g["name"] for g in (s.get("allGems") or [])) for s in d.get("skills") or []}
    for g in sorted(gems(new) - gems(old)):
        out.append(f"+ 젬 `{g}`")
    for g in sorted(gems(old) - gems(new)):
        out.append(f"- 젬 `{g}`")

    def items(d):
        return {i["itemSlot"]: ((i.get("itemData") or {}).get("baseType"),
                                (i.get("itemData") or {}).get("name")) for i in d.get("items") or []}
    ia, ib = items(old), items(new)
    for slot in sorted(set(ia) | set(ib), key=str):
        if ia.get(slot) != ib.get(slot):
            out.append(f"장비 {slot}: {ia.get(slot)} -> {ib.get(slot)}")
    return out


def write_ninja_items(data: dict, dest: Path) -> None:
    """착용 베이스 목록을 필터 스펙이 읽을 사이드카로 떨군다.

    왜 `.build` 로 안 되나: 유니크를 낀 슬롯은 `unique_name`(예: The Mutable Star)만 담고
    **베이스 타입**(Cleric Vestments)을 안 담는다. 필터는 BaseType 으로 매칭하니 그걸로는 못 쓴다.
    주얼 슬롯은 아예 빠진다. 그래서 첫 줄만 읽으면 15종 중 11종이다.
    ninja 응답의 `items`/`flasks`/`jewels` 가 정본이다.
    """
    bases: list[str] = []
    for key in ("items", "flasks", "jewels"):
        for entry in data.get(key) or []:
            item = entry.get("itemData") or entry
            base = (item.get("baseType") or item.get("typeLine") or "").strip()
            if base and base not in bases:
                bases.append(base)
    if not bases:
        log.warning("착용 베이스가 0 이다 — 사이드카를 덮어쓰지 않는다(%s)", dest.name)
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps({
        "_meta": {"source": "poe.ninja character API", "account": data.get("account"),
                  "name": data.get("name"), "level": data.get("level"),
                  "updatedUtc": data.get("updatedUtc"),
                  "why": "`.build` 는 유니크 슬롯에 unique_name 만 담고 베이스 타입을 안 담는다(주얼은 아예 빠진다). 필터는 BaseType 으로 매칭한다"},
        "bases": bases}, ensure_ascii=False, indent=1), encoding="utf-8")
    log.info("실캐릭 착용 %d종 -> %s", len(bases), dest.name)


def build_planner(pob_xml: Path, tmp: Path, name: str, author: str, link: str, install: bool) -> bool:
    """PoB XML -> 생성기 -> 정규화·검증 -> build_planner/ (+ 게임 폴더)."""
    for stale in tmp.glob("*.build"):
        stale.unlink()
    gen = subprocess.run(
        [sys.executable, str(REPO / "scripts/build_poe2_planner_files.py"),
         "--pob", str(pob_xml), "--out", str(tmp), "--author", author, "--link", link, "--prefix", "WB"],
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    made = sorted(tmp.glob("*.build"))
    if gen.returncode or not made:
        log.error("생성기 실패 rc=%s %s", gen.returncode, (gen.stderr or gen.stdout or "")[-400:])
        return False
    cmd = [sys.executable, str(REPO / "scripts/import_poe2_planner_files.py"),
           "--src", str(made[0]), "--name", name, "--author", author, "--link", link]
    if install:
        cmd.append("--install")
    imp = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if imp.returncode:
        log.error("검증·설치 실패: %s", (imp.stderr or imp.stdout or "")[-400:])
        return False
    log.info("플래너 갱신: %s", name)
    return True


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--account", required=True)
    ap.add_argument("--name", required=True)
    ap.add_argument("--overview", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--live-name", required=True, help="항상 최신을 담는 플래너 이름(레벨 없음)")
    ap.add_argument("--milestone-prefix", default="", help="전환 레벨 보존본 접두사. 비우면 보존 안 함")
    ap.add_argument("--author", default="Skadoosh (poe.ninja)")
    ap.add_argument("--link", default="")
    ap.add_argument("--interval", type=int, default=180)
    ap.add_argument("--hours", type=float, default=8.0)
    ap.add_argument("--no-install", action="store_true")
    args = ap.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s",
                        datefmt="%H:%M:%S")
    out = Path(args.out)
    snaps, tmp = out / "snapshots", out / "_tmp"
    snaps.mkdir(parents=True, exist_ok=True)
    tmp.mkdir(parents=True, exist_ok=True)
    timeline = out / "timeline.md"
    if not timeline.exists():
        timeline.write_text(f"# {args.name} 진행 이력 (poe.ninja `latest` 폴링)\n\n", encoding="utf-8")

    # 기준선은 지연 확보한다. 시작 조회가 429 로 막혔다고 죽으면 밤샘 추적이 통째로 사라지므로,
    # 첫 성공 응답이 기준선이 되고 그 전까지는 백오프만 한다.
    prev: dict | None = None
    prev_fp = None
    seen_milestones: set[int] = set()
    deadline = time.time() + args.hours * 3600
    fails, backoff = 0, 0
    while time.time() < deadline:
        time.sleep(backoff)
        backoff = args.interval
        try:
            cur = fetch(args.account, args.name, args.overview)
            fails = 0
        except RateLimited:
            fails += 1
            backoff = min(backoff * 2, 1800)  # 429 는 물러서야 풀린다 — 최대 30분
            log.warning("429 (%d회 연속) — 다음 조회까지 %d초 대기", fails, backoff)
            continue
        except Exception as exc:
            fails += 1
            log.warning("조회 실패(%d회 연속): %r", fails, exc)
            if fails >= 20:
                log.error("연속 실패 한도 초과 — 종료")
                break
            continue

        fp = fingerprint(cur)
        if prev is None:
            prev, prev_fp = cur, fp
            seen_milestones = {e for e, _ in ACT_ENTRY if e <= (cur.get("level") or 0)}
            log.info("기준 %s", summary(cur))
            with timeline.open("a", encoding="utf-8") as fh:
                fh.write(f"## {datetime.now(KST):%m-%d %H:%M KST} 추적 시작\n\n- {summary(cur)}\n\n")
            continue
        if fp == prev_fp:
            continue

        stamp = datetime.now(KST)
        lvl = cur.get("level")
        log.info("변화 감지 -> %s", summary(cur))
        (snaps / f"lv{lvl}_{stamp:%m%d_%H%M}.json").write_text(
            json.dumps(cur, ensure_ascii=False), encoding="utf-8")

        lines = diff_lines(prev, cur)
        with timeline.open("a", encoding="utf-8") as fh:
            fh.write(f"### {stamp:%m-%d %H:%M KST} — {summary(cur)}\n\n")
            for line in lines:
                fh.write(f"- {line}\n")
            fh.write("\n")

        pob = cur.get("pathOfBuildingExport")
        if pob:
            xml = out / "live_pob.xml"
            try:
                xml.write_text(decode_pob(pob), encoding="utf-8")
            except Exception as exc:
                log.error("PoB 디코드 실패: %r", exc)
                xml = None
            if xml:
                build_planner(xml, tmp, args.live_name, args.author, args.link, not args.no_install)
                # 필터 스펙이 읽는 착용 목록. 플래너와 함께 갱신해야 둘이 안 갈린다.
                write_ninja_items(cur, REPO / ".tmp" / "seongbin" / "LIVE_ninja_items.json")
                crossed = [e for e, _ in ACT_ENTRY if e not in seen_milestones and e <= (lvl or 0)]
                if crossed and args.milestone_prefix:
                    seen_milestones.update(crossed)
                    entry = max(crossed)
                    label = act_of(entry)
                    keep = f"{args.milestone_prefix} {label} - Skadoosh"
                    build_planner(xml, tmp, keep, args.author, args.link, not args.no_install)
                    log.info("%s 진입(Lv%d) 보존본: %s", label, entry, keep)
                    with timeline.open("a", encoding="utf-8") as fh:
                        fh.write(f"- **{label} 진입(Lv{entry}) — 플래너 보존본 `{keep}` 생성**\n\n")

        prev, prev_fp = cur, fp

    if prev is None:
        log.error("기준선을 한 번도 못 잡았다 — 전 구간 조회 실패")
        with timeline.open("a", encoding="utf-8") as fh:
            fh.write(f"## {datetime.now(KST):%m-%d %H:%M KST} 추적 종료 — 조회 실패로 기준선 미확보\n\n")
        return 1
    log.info("추적 종료. 마지막 %s", summary(prev))
    with timeline.open("a", encoding="utf-8") as fh:
        fh.write(f"## {datetime.now(KST):%m-%d %H:%M KST} 추적 종료 — {summary(prev)}\n\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
