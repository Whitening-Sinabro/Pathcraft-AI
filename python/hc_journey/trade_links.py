"""HC Journey — 전환마다 '무엇을 사라'를 거래소 검색 링크로 (옵션 포함).

자동 diff 가 아는 item_changed(슬롯, 제작자가 그 시점에 낀 아이템)를 공식 trade2 검색 쿼리로 바꿔 링크를 낸다.
링크 하나로는 안 된다는 것이 실측이다: 같은 베이스 + 옵션 전부 AND 는 HC 온라인 매물 0건, 카테고리 + "6개 중 3개, 60% 하한"은 353건.
그래서 완화 사다리를 낸다 — T1 그대로(베이스 + 옵션 전부, 80%) → T2 핵심(베이스 + 절반 이상, 60%) → T3 카테고리(같은 부위, 3개 이상, 60%).

정직성:
  * 옵션 → 스탯 id 는 공식 trade2 stats 인덱스와 정확 일치할 때만. 못 맞춘 옵션은 `unmapped` 로 남기고 필터에서 뺀다(지어내지 않음).
  * 베이스 → 카테고리는 GGPK BaseItemTypes 의 Metadata 경로에서 유도. 경로를 모르면 T3 를 내지 않는다.
  * 요구 레벨 상한 = 그 스냅샷의 level_hint. 거래소 필터가 빨간 매물을 못 거른 화면(C 8990~9040)이 있었으니 소비자도 매물 요구를 다시 본다.
  * 즉시 구입(status=securable)이 기본. 한국 서버(poe.kakaogames.com)는 별도 시장이라 검색 id 를 공유할 수 없고 `?q=` 링크만 같다.

사용:
    python -X utf8 python/hc_journey/trade_links.py                      # ?q= 링크(무상태) → data/hc_journey/trade_links.json
    python -X utf8 python/hc_journey/trade_links.py --live --realm both   # API 에 POST 해 검색 id·매물 수까지 (1.5초 간격)
"""
from __future__ import annotations

import argparse
import json
import logging
import math
import re
import sys
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))
import build_db  # noqa: E402

log = logging.getLogger("hc_journey.trade_links")

USER_AGENT = "PathcraftAI/0.1 (+https://github.com/Whitening-Sinabro/Pathcraft-AI; contact: vnddns999@gmail.com)"
HOSTS = {"int": "www.pathofexile.com", "kr": "poe.kakaogames.com"}
CACHE_DIR = REPO / "data" / "_cache" / "trade2"           # gitignore. 공식 /api/trade2/data/{stats,items,filters,leagues}
BASE_ITEM_TYPES = REPO / "data" / "game_data_poe2" / "BaseItemTypes.json"
DEFAULT_OUT = REPO / "data" / "hc_journey" / "trade_links.json"
DEFAULT_LEAGUE = "HC Forbidden Rites"
DEFAULT_STATUS = "securable"  # 즉시 구입. available = 즉시 구입 + 대면, online = 대면(온라인), any
POST_INTERVAL_SEC = 1.5

# GGPK Metadata 경로 조각 → 거래소 카테고리. 경로에 없는 부위는 None(T3 없음).
_PATH_CATEGORY = [
    ("/Armours/Helmets/", "armour.helmet"), ("/Armours/BodyArmours/", "armour.chest"), ("/Armours/Gloves/", "armour.gloves"),
    ("/Armours/Boots/", "armour.boots"),
    ("/Armours/Shields/FourShieldDex", "armour.buckler"),  # 버클러는 GGPK 에서 Shields 폴더의 Dex 계열
    ("/Armours/Shields/", "armour.shield"), ("/Armours/Focii/", "armour.focus"), ("/Quivers/", "armour.quiver"),
    ("/Rings/", "accessory.ring"), ("/Amulets/", "accessory.amulet"), ("/Belts/", "accessory.belt"),
    ("FlaskLife", "flask.life"), ("FlaskMana", "flask.mana"), ("Charm", "flask.charm"),
    ("/Weapons/OneHandWeapons/Claws/", "weapon.claw"), ("/Weapons/OneHandWeapons/Daggers/", "weapon.dagger"),
    ("/Weapons/OneHandWeapons/OneHandSwords/", "weapon.onesword"), ("/Weapons/OneHandWeapons/OneHandAxes/", "weapon.oneaxe"),
    ("/Weapons/OneHandWeapons/OneHandMaces/", "weapon.onemace"), ("/Weapons/OneHandWeapons/Spears/", "weapon.spear"),
    ("/Weapons/OneHandWeapons/Flails/", "weapon.flail"), ("/Weapons/OneHandWeapons/Wands/", "weapon.wand"),
    ("/Weapons/OneHandWeapons/Sceptres/", "weapon.sceptre"),
    ("/Weapons/TwoHandWeapons/Staves/FourQuarterstaff", "weapon.warstaff"),  # 쿼터스태프는 Staves 폴더 안
    ("/Weapons/TwoHandWeapons/Staves/", "weapon.staff"),
    ("/Weapons/TwoHandWeapons/TwoHandSwords/", "weapon.twosword"), ("/Weapons/TwoHandWeapons/TwoHandAxes/", "weapon.twoaxe"),
    ("/Weapons/TwoHandWeapons/TwoHandMaces/", "weapon.twomace"), ("/Weapons/TwoHandWeapons/Bows/", "weapon.bow"),
    ("/Weapons/TwoHandWeapons/Crossbows/", "weapon.crossbow"), ("/Weapons/OneHandWeapons/Talismans/", "weapon.talisman"),
]
_NUM = re.compile(r"\+?(-?\d+(?:\.\d+)?)")
_RANGE = re.compile(r"\((-?\d+(?:\.\d+)?)\s*[–\-~]\s*(-?\d+(?:\.\d+)?)\)")  # Mobalytics export 의 "(9–15)%" 범위 표기


@dataclass(frozen=True)
class Item:
    first: str                      # 첫 줄 = 베이스 또는 유니크 이름
    mods: tuple[str, ...]


@dataclass
class ModFilter:
    text: str
    ids: list[str]
    value: float | None             # 숫자 옵션이면 대표값(두 숫자면 평균), 아니면 None


@dataclass
class StatIndex:
    by_text: dict[str, list[str]] = field(default_factory=dict)

    @classmethod
    def from_trade_data(cls, stats_doc: dict, groups: tuple[str, ...] = ("explicit",)) -> "StatIndex":
        idx = cls()
        for g in stats_doc.get("result", []):
            if g.get("id") not in groups:
                continue
            for e in g.get("entries", []):
                idx.by_text.setdefault(normalize_mod(e["text"]), []).append(e["id"])
        return idx

    def lookup(self, mod: str, prefer_local: bool = False) -> list[str]:
        """정확 일치. prefer_local 이면 같은 문구의 '(Local)' 변형이 인덱스에 있을 때 그것을 앞세운다.
        (거래소는 방어구의 방어도/ES/회피/막기, 무기의 명중/공격 속도를 전역과 다른 로컬 id 로 둔다.)"""
        key = normalize_mod(mod)
        ids = list(self.by_text.get(key, []))
        if prefer_local:
            local = self.by_text.get(key + " (Local)", [])
            if local:
                ids = list(local) + ids
        return ids


# 카테고리별로 로컬 변형을 앞세울 옵션 낱말. 인덱스에 '(Local)' 변형이 실제로 있을 때만 적용된다.
_LOCAL_WORDS = {
    "armour": ("Armour", "Energy Shield", "Evasion", "Block"),
    "weapon": ("Accuracy", "Attack Speed", "Critical"),
}


def prefer_local_for(mod: str, category: str | None) -> bool:
    if not category:
        return False
    top = category.split(".")[0]
    if top == "armour" and category == "armour.quiver":
        return False
    return any(w in mod for w in _LOCAL_WORDS.get(top, ()))


# --- 텍스트 처리 ---------------------------------------------------------------

def _collapse_ranges(text: str) -> str:
    """'(9–15)%' 같은 범위 표기를 중간값 하나로. 정규화·값 추출 양쪽이 같은 텍스트를 본다."""
    return _RANGE.sub(lambda m: str((float(m.group(1)) + float(m.group(2))) / 2).rstrip("0").rstrip("."), text)


def normalize_mod(text: str) -> str:
    """숫자(부호 포함)를 # 로, '+#' 도 # 로, 범위 '(a–b)' 는 값 하나로, 공백 정리. 아이템 옵션과 trade2 stats text 양쪽에 같은 규칙."""
    s = _NUM.sub("#", _collapse_ranges(text))
    s = s.replace("+#", "#")
    return re.sub(r"\s+", " ", s).strip()


def mod_value(text: str) -> float | None:
    text = _collapse_ranges(text)
    nums = [float(x) for x in _NUM.findall(text)]
    if not nums:
        return None
    if len(nums) >= 2 and re.match(r"^Adds \d+ to \d+ ", text.strip()):
        return (nums[0] + nums[1]) / 2   # "Adds # to # Fire Damage" 만 평균(거래소 비교 기준은 미검증 — 추정)
    return nums[0]


def parse_item_text(text: str) -> Item | None:
    lines = [ln.strip() for ln in (text or "").split("\n") if ln.strip()]
    if not lines:
        return None
    mods = tuple(re.sub(r"^\d+\.\s*", "", ln) for ln in lines[1:])
    return Item(lines[0], mods)


def load_base_paths(path: Path = BASE_ITEM_TYPES) -> dict[str, str]:
    doc = json.loads(path.read_text(encoding="utf-8"))
    rows = doc if isinstance(doc, list) else doc.get("rows", [])
    return {r["Name"]: r["Id"] for r in rows if r.get("Name") and r.get("Id")}


def category_of(base: str, base_paths: dict[str, str]) -> str | None:
    p = base_paths.get(base, "")
    for frag, cat in _PATH_CATEGORY:
        if frag in p:
            return cat
    return None


def _league_key(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", s.lower())


def resolve_league(slug: str, leagues_doc: dict) -> str:
    """빌드의 리그 슬러그(ninja 식 'hc-forbidden-rites')를 공식 trade2 리그 id('HC Forbidden Rites')로.
    리그 이름은 시즌마다 바뀌므로 코드에 박지 않고 /api/trade2/data/leagues 캐시와 대조한다. 못 찾으면 후보 목록과 함께 실패."""
    ids = [x.get("id") for x in leagues_doc.get("result", []) if x.get("id")]
    want = _league_key(slug)
    for lid in ids:
        if _league_key(lid) == want:
            return lid
    raise ValueError(f"리그 슬러그 '{slug}' 에 맞는 trade2 리그 없음. 후보: {ids}")


def unique_names(items_doc: dict) -> dict[str, str]:
    """trade2 items 카탈로그의 유니크 {이름: 베이스}."""
    out = {}
    for c in items_doc.get("result", []):
        for e in c.get("entries", []):
            if e.get("flags", {}).get("unique") and e.get("name") and e.get("type"):
                out.setdefault(e["name"], e["type"])
    return out


# --- 쿼리 사다리 ------------------------------------------------------------------

def map_mods(item: Item, index: StatIndex, category: str | None = None) -> tuple[list[ModFilter], list[str]]:
    """정확 일치(카테고리에 맞는 로컬 변형 우선) → 없으면 'reduced'↔'increased' 한 번만 바꿔 재조회
    (거래소는 감소를 증가 스탯의 음수로 둔다). 그래도 없으면 unmapped."""
    mapped, unmapped = [], []
    for m in item.mods:
        local = prefer_local_for(m, category)
        ids = index.lookup(m, local)
        if ids:
            mapped.append(ModFilter(m, ids, mod_value(m)))
            continue
        flipped = None
        if " reduced " in f" {m} ":
            flipped = m.replace("reduced", "increased", 1)
        elif " increased " in f" {m} ":
            flipped = m.replace("increased", "reduced", 1)
        ids = index.lookup(flipped, local) if flipped else []
        if ids:
            v = mod_value(m)
            mapped.append(ModFilter(m, ids, -v if v is not None else None))  # 부호 반전 = 하한 대신 존재만 거른다
        else:
            unmapped.append(m)
    return mapped, unmapped


def _stat_filter(mf: ModFilter, ratio: float) -> dict:
    f: dict = {"id": mf.ids[0]}
    if mf.value is not None and mf.value > 0:
        v = mf.value * ratio
        f["value"] = {"min": int(math.floor(v)) if float(v).is_integer() or v >= 10 else round(v, 1)}
    return f


def build_ladder(item: Item, mapped: list[ModFilter], category: str | None, level_max: int | None,
                 status: str = DEFAULT_STATUS, unique_base: str | None = None) -> list[dict]:
    """T1 그대로 / T2 핵심 / T3 카테고리. 각 tier 는 {tier, label, query, note}."""
    def base_query() -> dict:
        q: dict = {"status": {"option": status}, "filters": {}}
        if level_max:
            q["filters"]["req_filters"] = {"filters": {"lvl": {"max": int(level_max)}}}
        return q

    tiers: list[dict] = []
    if unique_base:
        q = base_query()
        q["name"], q["type"] = item.first, unique_base
        q["filters"]["type_filters"] = {"filters": {"rarity": {"option": "unique"}}}
        tiers.append({"tier": "T1", "label": "유니크 이름", "query": {"query": q, "sort": {"price": "asc"}},
                      "note": "유니크는 이름으로 충분"})
        return tiers

    n = len(mapped)
    q1 = base_query()
    q1["type"] = item.first
    q1["filters"]["type_filters"] = {"filters": {"rarity": {"option": "nonunique"}}}
    if n:
        q1["stats"] = [{"type": "and", "filters": [_stat_filter(m, 0.8) for m in mapped]}]
    tiers.append({"tier": "T1", "label": "그대로", "query": {"query": q1, "sort": {"price": "asc"}},
                  "note": f"베이스 {item.first} + 옵션 {n}개 전부, 각 80% 하한"})
    if n >= 2:
        q2 = base_query()
        q2["type"] = item.first
        q2["filters"]["type_filters"] = {"filters": {"rarity": {"option": "nonunique"}}}
        k = max(1, math.ceil(n / 2))
        q2["stats"] = [{"type": "count", "value": {"min": k}, "filters": [_stat_filter(m, 0.6) for m in mapped]}]
        tiers.append({"tier": "T2", "label": "핵심", "query": {"query": q2, "sort": {"price": "asc"}},
                      "note": f"베이스 {item.first} + 옵션 {n}개 중 {k}개 이상, 각 60% 하한"})
    if category:
        q3 = base_query()
        q3["filters"]["type_filters"] = {"filters": {"category": {"option": category}, "rarity": {"option": "nonunique"}}}
        if n:
            k = min(3, n)
            q3["stats"] = [{"type": "count", "value": {"min": k}, "filters": [_stat_filter(m, 0.6) for m in mapped]}]
        tiers.append({"tier": "T3", "label": "같은 부위", "query": {"query": q3, "sort": {"price": "asc"}},
                      "note": f"{category} 전체 + 옵션 {n}개 중 {min(3, n) if n else 0}개 이상, 각 60% 하한"})
    return tiers


def q_url(realm: str, league: str, query: dict) -> str:
    return (f"https://{HOSTS[realm]}/trade2/search/poe2/{urllib.parse.quote(league)}?q="
            + urllib.parse.quote(json.dumps(query, separators=(",", ":"), ensure_ascii=False)))


def id_url(realm: str, league: str, search_id: str) -> str:
    return f"https://{HOSTS[realm]}/trade2/search/poe2/{urllib.parse.quote(league)}/{search_id}"


# --- 공식 API ----------------------------------------------------------------------

def _http(url: str, data: bytes | None = None) -> tuple[int, bytes, dict]:
    req = urllib.request.Request(url, data=data, headers={"User-Agent": USER_AGENT, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, r.read(), dict(r.headers)
    except urllib.error.HTTPError as e:
        return e.code, e.read(), dict(e.headers)


def load_trade_data(kind: str, realm: str = "int", refresh: bool = False) -> dict:
    """공식 /api/trade2/data/{kind}. 캐시(data/_cache/trade2)에 있으면 그것, 없으면 받아서 저장."""
    p = CACHE_DIR / f"{realm}_{kind}.json"
    if p.exists() and not refresh:
        return json.loads(p.read_text(encoding="utf-8"))
    status, body, _ = _http(f"https://{HOSTS[realm]}/api/trade2/data/{kind}")
    if status != 200:
        raise RuntimeError(f"trade2 data {kind}@{realm} http {status}")
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(body)
    (CACHE_DIR / f"{realm}_{kind}.retrieved").write_text(datetime.now(timezone.utc).isoformat(timespec="seconds"), encoding="utf-8")
    return json.loads(body.decode("utf-8"))


def post_search(realm: str, league: str, query: dict) -> dict:
    """검색 생성. 429 면 Retry-After 만큼 쉬고 한 번 재시도. 반환 {id,total} 또는 {error}."""
    url = f"https://{HOSTS[realm]}/api/trade2/search/poe2/{urllib.parse.quote(league)}"
    body = json.dumps(query, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    for attempt in (1, 2):
        status, raw, headers = _http(url, body)
        if status == 429 and attempt == 1:
            wait = float(headers.get("Retry-After", "10") or 10)
            log.warning("429 — %.0f초 대기", wait)
            time.sleep(wait)
            continue
        rate = {k: v for k, v in headers.items() if k.lower().startswith("x-rate-limit")}  # 한도 정책·현재 상태
        try:
            d = json.loads(raw.decode("utf-8"))
        except ValueError:
            return {"error": f"http {status}", "rate": rate}
        if status != 200:
            return {"error": d.get("error") or f"http {status}", "rate": rate}
        return {"id": d.get("id"), "total": d.get("total"), "rate": rate}
    return {"error": "429 twice"}


# --- 전환 순회 ---------------------------------------------------------------------

def _load_item_texts(path: Path) -> dict[str, str]:
    d = json.loads(path.read_text(encoding="utf-8"))
    return {sl.get("inventory_id"): (sl.get("additional_text") or "") for sl in d.get("inventory_slots", [])}


def generate(creators: list[dict] | None = None, league: str | None = None, status: str = DEFAULT_STATUS,
             live: bool = False, realms: tuple[str, ...] = ("int",), index: StatIndex | None = None,
             base_paths: dict[str, str] | None = None, uniques: dict[str, str] | None = None,
             creator: str | None = None, live_tiers: tuple[str, ...] | None = None,
             interval: float = POST_INTERVAL_SEC, leagues_doc: dict | None = None) -> dict:
    """league=None 이면 빌드마다 cfg["build"]["league"] 슬러그를 trade2 리그 id 로 푼다(시즌마다 바뀌므로 박지 않는다).
    live_tiers 로 POST 할 단계를 제한한다(예: ("T1","T3")). 거래 API 는 IP 단위 속도 제한이 엄격해(429 에 Retry-After 300~1800초)
    전부 묻지 말고 답이 필요한 단계만, interval 은 넉넉히(7초 이상 권장)."""
    index = index or StatIndex.from_trade_data(load_trade_data("stats"))
    base_paths = base_paths if base_paths is not None else load_base_paths()
    uniques = uniques if uniques is not None else unique_names(load_trade_data("items"))
    if league is None and leagues_doc is None:
        leagues_doc = load_trade_data("leagues")
    entries: list[dict] = []
    n_unmapped = 0
    leagues_used: set[str] = set()
    for cfg in (creators if creators is not None else build_db.CREATORS):
        if creator and cfg["name"] != creator:
            continue
        build_league = league or resolve_league(cfg["build"]["league"], leagues_doc or {})
        leagues_used.add(build_league)
        bands = cfg["bands"]
        snaps = [build_db.load_build(build_db.CREATORS_DIR / rel) for (_l, _lv, _st, rel) in bands]
        texts = [_load_item_texts(build_db.CREATORS_DIR / rel) for (_l, _lv, _st, rel) in bands]
        for i in range(len(snaps) - 1):
            to_label, to_level = bands[i + 1][0], bands[i + 1][1]
            for kind, slot, _detail in build_db.diff_snapshots(snaps[i], snaps[i + 1]):
                if kind != "item_changed":
                    continue
                item = parse_item_text(texts[i + 1].get(slot, ""))
                if item is None:
                    continue  # 슬롯이 비워진 변화 — 살 것이 없다
                unique_base = uniques.get(item.first)
                category = None if unique_base else category_of(item.first, base_paths)
                mapped, unmapped = ([], []) if unique_base else map_mods(item, index, category)
                n_unmapped += len(unmapped)
                tiers = build_ladder(item, mapped, category, to_level, status, unique_base)
                for t in tiers:
                    t["links"] = {r: q_url(r, build_league, t["query"]) for r in realms}
                    if live and (live_tiers is None or t["tier"] in live_tiers):
                        t["live"] = {}
                        for r in realms:
                            res = post_search(r, build_league, t["query"])
                            if res.get("id"):
                                res["url"] = id_url(r, build_league, res["id"])
                            t["live"][r] = res
                            time.sleep(interval)
                if live:
                    log.info("live [%s] %s %s %s | %s", cfg["name"], f"{bands[i][0]}→{to_label}", slot, item.first,
                             " ".join(f"{t['tier']}={t['live'].get(realms[0], {}).get('total', t['live'].get(realms[0], {}).get('error'))}"
                                      for t in tiers if "live" in t))
                    for h in logging.getLogger().handlers:
                        h.flush()  # 파이프로 볼 때 항목마다 바로 보이게
                entries.append({
                    "creator": cfg["name"], "transition_idx": i, "transition": f"{bands[i][0]} → {to_label}",
                    "slot": slot, "level_max": to_level, "league": build_league,
                    "item": {"first": item.first, "unique_base": unique_base, "category": category,
                             "mods": list(item.mods),
                             "mapped": [{"text": m.text, "id": m.ids[0], "alt_ids": m.ids[1:], "value": m.value} for m in mapped],
                             "unmapped": unmapped},
                    "tiers": tiers,
                })
    return {"_meta": {
        "purpose": "전환마다 제작자가 그 시점에 낀 아이템을 거래소 검색 링크로. T1 그대로 → T2 핵심 → T3 같은 부위 순으로 완화.",
        "honesty": "옵션→스탯 id 는 공식 stats 인덱스 정확 일치만(unmapped 는 필터에서 뺌). 요구 레벨 상한 = 스냅샷 레벨. "
                   "한국 서버는 별도 시장이라 ?q= 링크만 공유하고 검색 id 는 서버별.",
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "leagues": sorted(leagues_used), "status": status, "realms": list(realms), "live": live,
        "n_entries": len(entries), "n_unmapped_mods": n_unmapped,
    }, "entries": entries}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--league", default=None, help="비우면 빌드마다 리그 슬러그를 trade2 리그 목록에서 푼다(시즌마다 바뀌므로 기본값 없음)")
    ap.add_argument("--status", default=DEFAULT_STATUS, choices=["securable", "available", "online", "onlineleague", "any"])
    ap.add_argument("--realm", default="int", choices=["int", "kr", "both"])
    ap.add_argument("--live", action="store_true", help="공식 API 에 POST 해 검색 id 와 매물 수를 받는다")
    ap.add_argument("--tiers", default=None, help="live 로 물을 단계만, 예: T1,T3 (기본 전부)")
    ap.add_argument("--interval", type=float, default=7.0, help="POST 간격 초. IP 속도 제한(429 → 300~600초 벌칙) 때문에 7초 이상 권장")
    ap.add_argument("--creator", default=None)
    ap.add_argument("--refresh", action="store_true", help="trade2 data 캐시를 다시 받는다")
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    a = ap.parse_args()
    if a.refresh:
        for k in ("stats", "items", "filters", "leagues"):
            load_trade_data(k, refresh=True)
    realms = ("int", "kr") if a.realm == "both" else (a.realm,)
    doc = generate(league=a.league, status=a.status, live=a.live, realms=realms, creator=a.creator,
                   live_tiers=tuple(a.tiers.split(",")) if a.tiers else None, interval=a.interval)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    m = doc["_meta"]
    log.info("링크 %d건(unmapped 옵션 %d) → %s", m["n_entries"], m["n_unmapped_mods"], a.out)
    if a.live:
        for e in doc["entries"]:
            tot = [f"{t['tier']}={t['live'].get(realms[0], {}).get('total')}" for t in e["tiers"] if "live" in t]
            log.info("[%s] %s %s %s | %s", e["creator"], e["transition"], e["slot"], e["item"]["first"], " ".join(tot))
