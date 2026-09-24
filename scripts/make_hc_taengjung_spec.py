"""탱정 키타바 방패벽(Smith of Kitava) 0.5.5 하드코어 필터 스펙을 플래너 계약 + 저장본 + GGPK 에서 유도한다.

워브링어 스펙(make_hc_warbringer_spec.py)과 같은 원칙: 베이스 이름을 손으로 옮기지 않는다.
  저장본 착용   탱정 PoB 28509/285e2/28604/28695/29d39 의 Items/ItemSet 베이스 (방패·장갑·장화·반지·허리띠·목걸이)
  목표 고유     플래너 계약 stages[*].equipment[*].unique 의 베이스(운명의 저항·황동 철갑·아홉꼬리·목 죄이는 명령)
  힘 방어구     GGPK ArmourTypes 에서 방어도만 있는 베이스를 드롭 레벨 밴드로
  흰색 갑옷     Smith's Masterwork 는 일반(흰색) 갑옷만 입을 수 있다 → 01~02 동안 방어도 전용 흰색 갑옷
  철퇴          GGPK ItemClass 12(한손 철퇴)를 드롭 레벨 밴드로

탱정은 필터를 배포하지 않는다(카페 217글 제목 · 읽은 본문 93 · 방송 자막 확인, 2026-09-22).
방패의 벽 피해는 방패 방어도 15당 물리 피해(PoB act_str.lua ShieldWallPlayer) — 방패가 무기보다 먼저다.
"""
from __future__ import annotations

import json
import pathlib
import sys
import xml.etree.ElementTree as ET

REPO = pathlib.Path("D:/Pathcraft-AI")
CORPUS = REPO / "deliverables" / "poe2_build_corpus_2026-09-21"
CONTRACT = CORPUS / "taengjung_progression" / "planner_contract.json"
SAVES = [CORPUS / "taengjung_progression" / "sources" / f"pob_{k}.xml" for k in ("28509", "285e2", "28604", "28695", "29d39")]
WARBRINGER = REPO / "data" / "filter_build_targets" / "poe2_warbringer_skadoosh_0_5_5_hc.json"
OUT = REPO / "data" / "filter_build_targets" / "poe2_hc_taengjung_kitava_shieldwall_0_5_5.json"

GGPK = json.loads((REPO / "data/game_data_poe2/BaseItemTypes.json").read_text(encoding="utf-8"))
ARMOUR = {r["BaseItemType"]: r for r in
          json.loads((REPO / "data/game_data_poe2/ArmourTypes.json").read_text(encoding="utf-8"))}
KNOWN = {(b.get("Name") or "").strip() for b in GGPK}
DROP = {(r.get("Name") or "").strip(): r.get("DropLevel") for r in GGPK if r.get("Name")}
BAND_LIFE = 12  # 워브링어 스펙과 같은 졸업 간격(NeverSink 플라스크 티어 수명에서 유도)


def usable(row: dict) -> bool:
    n = row.get("Name") or ""
    return bool(n) and not n.startswith("[DNT") and "Runeforged" not in n and "Runemastered" not in n


def by_class(cls: int, lo: int, hi: int) -> list[str]:
    return [r["Name"] for r in GGPK if usable(r) and r["ItemClass"] == cls and lo <= r["DropLevel"] <= hi]


def armour_only(classes: tuple[int, ...]) -> list[str]:
    """방어도만 있는 베이스(회피·에너지 보호막 0)."""
    out = []
    for i, r in enumerate(GGPK):
        a = ARMOUR.get(i)
        if a and usable(r) and r["ItemClass"] in classes and a["Armour"] and not a["Evasion"] and not a["EnergyShield"]:
            out.append(r["Name"])
    return out


def band_cap(drop_level: int) -> int | None:
    cap = -(-(drop_level + BAND_LIFE) // 10) * 10
    return None if cap >= 80 else cap


def banded(names: list[str], where: str) -> list[tuple[list[str], int | None, str]]:
    buckets: dict[int | None, list[str]] = {}
    for n in names:
        d = DROP.get(n)
        if d is None:
            sys.exit(f"[{where}] GGPK 에 드롭 레벨이 없다: {n}")
        buckets.setdefault(band_cap(d), []).append(n)
    out = []
    for c in sorted(buckets, key=lambda c: (c is None, c or 0)):
        bases = sorted(buckets[c])
        lo, hi = min(DROP[n] for n in bases), max(DROP[n] for n in bases)
        out.append((bases, c, f"드롭 {lo}~{hi}" if lo != hi else f"드롭 {lo}"))
    return out


def check(names: list[str], where: str) -> list[str]:
    """GGPK 에 없는 이름은 필터에서 조용한 no-op 이 되므로 즉시 죽는다."""
    missing = [n for n in names if n not in KNOWN]
    if missing:
        sys.exit(f"[{where}] GGPK BaseItemTypes 에 없는 이름: {missing}")
    return names


def saved_bases() -> dict[str, set[str]]:
    """탱정 저장본 5개의 슬롯별 베이스(희귀·일반·고유 모두)."""
    out: dict[str, set[str]] = {}
    for p in SAVES:
        root = ET.parse(p).getroot()
        items = {it.get("id"): (it.text or "").strip().splitlines() for it in root.findall("./Items/Item")}
        for s in root.findall("./Items/ItemSet/Slot"):
            lines = items.get(s.get("itemId"))
            if not lines or len(lines) < 3:
                continue
            rarity = lines[0].split(": ")[-1]
            base = lines[2] if rarity in ("RARE", "UNIQUE") else lines[1]
            base = base.removeprefix("Superior ").strip()
            if base in KNOWN:
                out.setdefault(s.get("name"), set()).add(base)
    return out


SAVED = saved_bases()
contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
UNIQUE_TARGETS = sorted({e["unique"] for s in contract["stages"] for e in s["equipment"] if e.get("unique")})
UNIQUE_BASES = check(sorted(SAVED.get("Amulet", set()) & {"Jade Amulet"}
                            | {"Runeforged Champion Cuirass", "Utility Belt", "Viper Cap", "Runemastered Viper Cap",
                               "Shrine Sceptre", "Ultimate Life Flask", "Transcendent Mana Flask",
                               "Diamond", "Time-Lost Diamond"}), "unique-bases")


def src(names: list[str]) -> str:
    tag = {b: s for s, bs in SAVED.items() for b in bs}
    return " / ".join(f"{n}({'저장본 ' + tag[n] if n in tag else 'GGPK'})" for n in names)


warbringer = json.loads(WARBRINGER.read_text(encoding="utf-8"))
ALL = ["campaign", "maps", "endgame"]
SHIELDS = armour_only((26,))
BODY_NORMAL = armour_only((24,))
OTHER_ARMOUR = sorted(set(armour_only((22, 23, 25))) | SAVED.get("Gloves", set()) | SAVED.get("Boots", set()))
JEWELLERY = sorted(SAVED.get("Ring 1", set()) | SAVED.get("Ring 2", set()) | {"Jade Amulet", "Amber Amulet", "Linen Belt", "Heavy Belt"})
CHARMS = sorted({"Stone Charm", "Thawing Charm", "Silver Charm", "Golden Charm"})
FLASK_BANDS = [
    (r["base_types"], r.get("area_level_max"), r["name"].split(" — ")[-1])
    for r in warbringer["rules"] if r["name"].startswith("[플라스크]")]
RUNES = ["Lesser Body Rune", "Body Rune", "Greater Body Rune",
         "Greater Iron Rune", "Greater Desert Rune", "Greater Glacial Rune", "Greater Storm Rune"]
JEWELLERS = ["Lesser Jeweller's Orb", "Greater Jeweller's Orb"]


def gear(style: str, label: str, bases: list[str], cap: int | None, note: str, klass: list[str] | None = None,
         rarity: list[str] | None = None, stages: list[str] | None = None) -> dict:
    rule = dict(style=style, name=label, note=note + (f" 지역 {cap} 까지 크게 — 그 뒤는 흘려보낸다." if cap else " 상한 없음."),
                base_types=check(bases, label),
                rarity=rarity or (["Rare"] if min(DROP[n] for n in bases) >= 45 else ["Normal", "Magic", "Rare"]),
                stages=stages or ALL)
    if klass:
        rule["class"] = klass
    if cap:
        rule["area_level_max"] = cap
    return rule


rules = [
    *[gear("weapon_core", f"[타워 방패 · 방어도] {label}", bases, cap,
           f"방패의 벽 피해 = 방패 방어도 15당 물리 피해(PoB). 방어도가 곧 공격력. {src(bases)}.")
      for bases, cap, label in banded(SHIELDS, "shields")],
    *[gear("weapon_gear", f"[한손 철퇴] {label}", bases, cap,
           f"세트 1·2 공통 무기. 방패의 벽엔 무기 피해가 안 들어가서 +근접 스킬 레벨이 핵심(탱정 Bandit Mace +3). {src(bases)}.",
           klass=["One Hand Maces"])
      for bases, cap, label in banded(by_class(12, 1, 99), "1h")],
    *[gear("armour_gear", f"[흰색 갑옷 · Masterwork] {label}", bases, cap,
           f"01~02: Smith's Masterwork 는 일반(흰색) 갑옷만 입는다 → 방어도 높은 흰색 갑옷. 03 황동 철갑 뒤엔 필요 없음. {src(bases)}.",
           rarity=["Normal"], stages=["campaign", "maps"])
      for bases, cap, label in banded(BODY_NORMAL, "normal-body")],
    *[gear("armour_gear", f"[힘 방어구 · 장갑·장화·투구] {label}", bases, cap,
           f"방어도 베이스. 장갑은 +2 근접 스킬 레벨(탱정 저장본 4개 모두), 장화는 이동 속도 · 카오스 저항. {src(bases)}.")
      for bases, cap, label in banded(OTHER_ARMOUR, "armour")],
    *[gear("jewellery_gear", f"[장신구·허리띠] {label}", bases, cap,
           f"반지는 화염 저항(Coal Stoker로 냉기·번개 절반씩). {src(bases)}. 호박 목걸이 · 무거운 허리띠는 힘 빌드 관례(탱정 발언 아님).",
           rarity=["Normal", "Magic", "Rare"])
      for bases, cap, label in banded(JEWELLERY, "jewellery")],
    *[gear("charm_endgame", f"[호신부] {label}", bases, cap,
           f"돌 · 해동은 HC 기절 · 동결 대비, 은 · 황금은 저장본 고유 호신부 베이스. {src(bases)}.",
           klass=["Charms"], rarity=["Normal", "Magic"])
      for bases, cap, label in banded(CHARMS, "charms")],
    *[dict(style="charm_endgame", name=f"[플라스크] {bases[0].split(' ')[0]} — {where}",
           note=f"워브링어 스펙과 같은 졸업 밴드. 지금 쓸 수 있는 티어만 크게. {src(bases)}.",
           **{"class": ["Life Flasks", "Mana Flasks"]}, base_types=check(bases, f"flask-{bases[0]}"),
           rarity=["Normal", "Magic"], **({"area_level_max": cap} if cap else {}), stages=ALL)
      for bases, cap, where in FLASK_BANDS],
    dict(style="augment_endgame", name="[액트~맵 초반] 주얼러 오브 — 방패의 벽 · 함성 보조 소켓",
         note=f"{src(JEWELLERS)}. 01 하급 2개 · 02 상급 1개. 화폐를 건드리지 않는 원칙의 예외 — 전환 게이트라서 띄운다.",
         **{"class": ["Stackable Currency"]}, base_types=check(JEWELLERS, "jewellers"), stages=["campaign", "maps"]),
    # 액트 경로(00 별이슬)는 11레벨부터 양손 철퇴 · 부적(급습)을 쓰므로 캠페인에서는 그 둘을 숨기지 않는다.
    *[dict(kind="hide", name=f"[정리] 이 빌드가 못 쓰는 무기·보조장비 · {where}",
           note="탱정 세트 1 = 한손 철퇴 + 타워 방패, 세트 2 = 함성. 노말·매직만, 지역레벨 12부터(NeverSink 안전장치 유지). "
                "셉터는 숨기지 않는다 — Sacred Flame(셉터)은 선택지다." + extra,
           **{"class": classes}, rarity=["Normal", "Magic"], area_level_min=12, stages=stages)
      for where, classes, stages, extra in [
          ("캠페인", ["Bows", "Crossbows", "Quarterstaves", "Quivers", "Spears", "Staves", "Wands", "Bucklers", "Foci"], ["campaign"],
           " 양손 철퇴 · 부적은 액트 경로가 쓰므로 캠페인에선 남긴다."),
          ("맵~", ["Bows", "Crossbows", "Quarterstaves", "Quivers", "Spears", "Staves", "Talismans", "Wands", "Two Hand Maces", "Bucklers", "Foci"],
           ["maps", "endgame"], "")]],
]

spec = {
    "_meta": {
        "build": "탱정 키타바 방패벽 (Smith of Kitava, Shield Wall + Infernal Cry) 하드코어 — 0.5.5",
        "game": "poe2",
        "patch": "0.5.5 Forbidden Rites",
        "base_filter": warbringer["_meta"]["base_filter"],
        "generated_by": "scripts/build_poe2_build_overlay.py (스펙은 scripts/make_hc_taengjung_spec.py 가 플래너 계약 + 탱정 저장본 + GGPK 에서 유도)",
        "sources": ("탱정 PoB 28509/285e2/28604/28695/29d39 (deliverables/poe2_build_corpus_2026-09-21/taengjung_progression/sources) | "
                    "플래너 계약 taengjung_progression/planner_contract.json | PoB act_str.lua ShieldWallPlayer · ModRunes.lua Boar Idol | "
                    "data/game_data_poe2/BaseItemTypes.json + ArmourTypes.json"),
        "palette": warbringer["_meta"]["palette"],
        "notes": [
            "탱정은 필터를 배포하지 않는다 — 이 필터는 Pathcraft 가 그의 저장본 장비와 빌드 규칙에서 만든 것.",
            "Show-only overlay. 숨김은 못 쓰는 무기 클래스 한 룰뿐 — 나머지는 NeverSink 규칙대로 흐른다.",
            "단계 의미: campaign=1~45(액트) / maps=46~64(03 황동 철갑 · 04 저생명력 묶음) / endgame=65+.",
            "미가공 젬은 GemLevel 조건이 필요한데 빌더가 지원하지 않는다 — NeverSink 의 레벨별 티어링을 그대로 쓴다.",
            "고유 · 룬 · Boar Idol · 주얼은 건드리지 않는다 — NeverSink 가 이미 빔 · 미니맵 아이콘 · 등급 색으로 띄우고, 덮으면 그 표시가 사라진다(검증 #6).",
        ],
        "outputs": [
            {"stage": "campaign", "file": "PathcraftAI_HC-Taengjung_1-Campaign_on_NeverSink-SOFT.filter",
             "base": "neversink_poe2_soft.filter", "why": "액트 · 막간. 흰색 갑옷(Masterwork) · 타워 방패 · 한손 철퇴가 켜진다."},
            {"stage": "maps", "file": "PathcraftAI_HC-Taengjung_2-EarlyMaps_on_NeverSink-REGULAR.filter",
             "base": "neversink_poe2_regular.filter", "why": "03~05 전환 구간. 목표 고유 베이스 · 45+ 레어 방패가 켜진다."},
            {"stage": "endgame", "file": "PathcraftAI_HC-Taengjung_3-Endgame_on_NeverSink-STRICT.filter",
             "base": "neversink_poe2_strict.filter", "why": "65+ 06 저자본 완성. 하드코어라 생존 소모품은 놓치지 않는다."},
        ],
        "bases": warbringer["_meta"]["bases"],
    },
    "styles": warbringer["styles"],
    "rules": rules,
}

OUT.write_text(json.dumps(spec, ensure_ascii=False, indent=1), encoding="utf-8")
sys.stdout.reconfigure(encoding="utf-8")
names = {b for r in rules for b in (r.get("base_types") or [])}
print(f"{OUT.name} 생성 — 룰 {len(rules)}개 · 베이스 {len(names)}종 · 저장본 슬롯 {len(SAVED)}")
print(f"  GGPK 실재성: {len(names & KNOWN)}/{len(names)} · 목표 고유: {UNIQUE_TARGETS}")
