"""Skadoosh 워브링어(함성 토템) 0.5.5 하드코어 필터 스펙을 플래너 정본 + GGPK 에서 유도한다.

젬링 스펙(make_hc_gemling_spec.py)과 같은 원칙: 베이스 이름을 손으로 옮기지 않는다.
  가이드 착용   `build_planner/Warbringer Lv*.build` (Mobalytics 다운로드 원본) inventory_slots
  실캐릭 착용   poe.ninja SkadooshShoutedHard 24렙 스냅샷(2026-09-05) — 이름만 옮기고 GGPK 로 확인
  힘 방어구     GGPK ArmourTypes 에서 방어도만 있는 베이스(회피·에너지 보호막 0)를 드롭 레벨 밴드로
  철퇴          GGPK ItemClass 12/17 을 드롭 레벨 밴드로
  0.5.5 신규    Jiquani's Soul Core of Rallying/Automation/Quaking 은 9/4 GGPK 추출본에 없다 —
                캐시된 0.5.5 패치노트 원문(L123~)에서 이름을 읽어 2차 출처로 받는다

제작자 본인 발언(Discord 09-02, 방송 1일차): 레어 장비만, 유니크 불필요, 함성 젬 레벨이 곧 피해.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

REPO = pathlib.Path("D:/Pathcraft-AI")
PLANNER = REPO / "build_planner"
GEMLING = REPO / "data" / "filter_build_targets" / "poe2_hc_gemling_seongbin_0_5_5.json"
PATCH_055 = REPO / "data" / "_cache" / "patchnotes" / "poe2" / "4000864_0.5.5_Patch_Notes.txt"
OUT = REPO / "data" / "filter_build_targets" / "poe2_warbringer_skadoosh_0_5_5_hc.json"

GGPK = json.loads((REPO / "data/game_data_poe2/BaseItemTypes.json").read_text(encoding="utf-8"))
ARMOUR = {r["BaseItemType"]: r for r in
          json.loads((REPO / "data/game_data_poe2/ArmourTypes.json").read_text(encoding="utf-8"))}
KNOWN = {(b.get("Name") or "").strip() for b in GGPK}
NEW_055 = set(re.findall(r"^([A-Z][A-Za-z']+ Soul Core of [A-Z][a-z]+)$",
                         PATCH_055.read_text(encoding="utf-8"), re.M))


def usable(row: dict) -> bool:
    n = row.get("Name") or ""
    return bool(n) and not n.startswith("[DNT") and "Runeforged" not in n and "Runemastered" not in n


def by_class(cls: int, lo: int, hi: int) -> list[str]:
    return [r["Name"] for r in GGPK if usable(r) and r["ItemClass"] == cls and lo <= r["DropLevel"] <= hi]


DROP = {(r.get("Name") or "").strip(): r.get("DropLevel") for r in GGPK if r.get("Name")}

# 막 경계(GGPK WorldAreas): 1막 1~15 · 2막 16~31 · 3막 33~45 · 4막 46~53 · 잔혹 54~
# 한 베이스는 "떨어진 막의 다음 막 끝"까지만 크게 띄운다. 그 뒤로는 흘려보낸다.
#
# 이게 없으면 드롭 4 짜리 대장장이 망치가 지역 45 까지 계속 크게 뜬다 — 티어 구분이 사라져
# "뭐가 떨어져도 크다"가 되고, 그게 곧 필터가 없는 것과 같다. NeverSink 는 플라스크에만
# 이 졸업 처리를 해 두고(soft L4475~L4519) 장비는 지역 65 에서 한 번에 죽이므로,
# 초반 장비 구간의 티어 관리는 전적으로 이 오버레이 책임이다.
# 수명은 NeverSink 의 플라스크 졸업 간격에서 가져왔다: 각 티어가 드롭 후 11~20레벨을 살고 죽는다
# (Lesser 1→15 · Grand 16→30 · Giant 23→42 · Gargantuan 40→52). 그래서 드롭 + 12 를 상한으로 잡고
# 10 단위로 반올림해 묶는다. 드롭 68 이상은 상한 없음 — 그 위로는 티어가 더 없다.
BAND_LIFE = 12


def band_cap(drop_level: int) -> int | None:
    """드롭 레벨 -> 크게 띄울 지역 레벨 상한(None = 상한 없음)."""
    cap = -(-(drop_level + BAND_LIFE) // 10) * 10  # 10 단위 올림
    return None if cap >= 80 else cap


def banded(names: list[str], where: str) -> list[tuple[list[str], int | None, str]]:
    """베이스 목록을 드롭 레벨 밴드로 쪼갠다. 같은 상한끼리 묶어 룰 수를 줄인다."""
    buckets: dict[int | None, list[str]] = {}
    for n in names:
        d = DROP.get(n)
        if d is None:
            sys.exit(f"[{where}] GGPK 에 드롭 레벨이 없다: {n}")
        buckets.setdefault(band_cap(d), []).append(n)
    order = sorted(buckets, key=lambda c: (c is None, c or 0))
    out = []
    for c in order:
        bases = sorted(buckets[c])
        lo, hi = min(DROP[n] for n in bases), max(DROP[n] for n in bases)
        out.append((bases, c, f"드롭 {lo}~{hi}" if lo != hi else f"드롭 {lo}"))
    return out


def str_armour(lo: int, hi: int) -> list[str]:
    """방어도만 있는 베이스 — 장갑·장화·갑옷·투구·방패(타워). 회피/ES 가 붙은 하이브리드는 뺀다."""
    out = []
    for i, r in enumerate(GGPK):
        a = ARMOUR.get(i)
        if not a or not usable(r) or r["ItemClass"] not in (22, 23, 24, 25, 26):
            continue
        if a["Armour"] and not a["Evasion"] and not a["EnergyShield"] and lo <= r["DropLevel"] <= hi:
            out.append(r["Name"])
    return out


def guide_bases() -> dict[str, set[str]]:
    out: dict[str, set[str]] = {}
    for p in sorted(PLANNER.glob("Warbringer Lv*.build")):
        d = json.loads(p.read_text(encoding="utf-8"))
        band = p.stem.split(" - ")[0].replace("Warbringer ", "")
        for s in d.get("inventory_slots", []):
            first = (s.get("additional_text") or "").split("\n")[0].strip()
            if first:
                out.setdefault(first, set()).add(band)
    return out


GUIDE = guide_bases()
LIVE_24 = ["Spiked Club", "Braced Tower Shield", "Horned Crown", "Maraketh Cuirass",
           "Ringmail Gauntlets", "Threaded Shoes", "Jade Amulet", "Topaz Ring", "Amethyst Ring",
           "Rawhide Belt", "Ruby"]  # poe.ninja 24렙 스냅샷 2026-09-05, Bronzebeard·Surefooted Sigil 은 유니크
FROM_PATCH: list[str] = []


def check(names: list[str], where: str) -> list[str]:
    """GGPK 에 없는 이름은 조용한 no-op 이 되므로 즉시 죽는다. 0.5.5 신규 소울 코어만 패치노트로 받는다."""
    missing = [n for n in names if n not in KNOWN and n not in NEW_055]
    if missing:
        sys.exit(f"[{where}] GGPK BaseItemTypes 에도 0.5.5 패치노트에도 없는 이름: {missing}")
    FROM_PATCH.extend(n for n in names if n not in KNOWN)
    return names


def who(name: str) -> str:
    tags = sorted(GUIDE.get(name, set()))
    if name in LIVE_24:
        tags.append("실캐릭24")
    return "·".join(tags) if tags else "GGPK"


def src(names: list[str]) -> str:
    return " / ".join(f"{n}({who(n)})" for n in names)


gemling = json.loads(GEMLING.read_text(encoding="utf-8"))
ALL = ["campaign", "maps", "endgame"]

ONE_HAND_EARLY = by_class(12, 4, 28)          # Smithing Hammer ~ Plated Mace
TWO_HAND_EARLY = by_class(17, 4, 28)          # Oak Greathammer ~ Temple Maul
# 한손·양손을 한 룰에 섞으면 빌더가 NeverSink 의 `Sockets >= 2` 블록(soft L401, 한손 철퇴만 해당)에
# 맞춘 변형 블록을 못 만들어 소켓 2개 상태가 회귀한다 — 클래스당 룰 하나.
ONE_HAND_MID, TWO_HAND_MID = by_class(12, 33, 44), by_class(17, 33, 44)
ONE_HAND_LATE, TWO_HAND_LATE = by_class(12, 45, 99), by_class(17, 45, 99)
ARMOUR_ACT12 = str_armour(4, 28) + ["Horned Crown", "Ringmail Gauntlets", "Threaded Shoes"]
ARMOUR_ACT34 = str_armour(33, 44)
ARMOUR_MAPS = str_armour(45, 62)
ARMOUR_END = str_armour(65, 99)
JEWELLERY = ["Jade Amulet", "Amber Amulet", "Bloodstone Amulet", "Stellar Amulet",
             "Ruby Ring", "Sapphire Ring", "Topaz Ring", "Amethyst Ring", "Rawhide Belt", "Heavy Belt"]
CHARMS = ["Sapphire Charm", "Ruby Charm", "Amethyst Charm", "Thawing Charm", "Stone Charm"]
# 플라스크는 "지금 쓸 수 있는 티어"만 크게 띄워야 한다. 일곱 티어를 한 덩어리로 묶으면
# NeverSink 의 티어 졸업 처리(soft L4475~L4513: Lesser/Medium 은 지역 15, Grand/Greater 는 30,
# Colossal/Giant 는 42, Gargantuan 은 52 부터 폰트 18 + 무음으로 죽인다)를 오버레이가 통째로
# 덮어써서, 이미 쓸모없는 티어까지 영영 크게 뜬다. 그래서 NeverSink 가 죽이기 직전까지만 맡는다.
FLASK_BANDS = [
    (["Lesser Life Flask", "Lesser Mana Flask"], 14, "1막 시작 — 첫 플라스크"),
    (["Medium Life Flask", "Medium Mana Flask"], 14, "1막"),
    (["Greater Life Flask", "Greater Mana Flask"], 29, "1막 후반~2막"),
    (["Grand Life Flask", "Grand Mana Flask"], 29, "2막"),
    (["Giant Life Flask", "Giant Mana Flask"], 41, "3막"),
    (["Colossal Life Flask", "Colossal Mana Flask"], 41, "3막 후반"),
    (["Gargantuan Life Flask", "Gargantuan Mana Flask"], 51, "4막"),
    (["Transcendent Life Flask", "Transcendent Mana Flask"], None, "잔혹~"),
    (["Ultimate Life Flask", "Ultimate Mana Flask"], None, "엔드게임"),
]
# 하위·일반 아이언/저항 룬은 NeverSink 가 이미 폰트 40 + 소리로 띄운다(soft L2380, 지역 64 이하).
# 거기에 C급(38, 무음)을 덮으면 회귀만 난다 — 그래서 육체 3단 + 상급 4종만 이 빌드 색으로 잡는다.
RUNES = ["Lesser Body Rune", "Body Rune", "Greater Body Rune",
         "Greater Iron Rune", "Greater Desert Rune", "Greater Glacial Rune", "Greater Storm Rune"]
SOUL_CORES = ["Jiquani's Soul Core of Rallying", "Jiquani's Soul Core of Automation",
              "Jiquani's Soul Core of Quaking", "Vorana's Carnage"]
JEWELLERS = ["Lesser Jeweller's Orb", "Greater Jeweller's Orb"]
JEWELS = ["Ruby", "Time-Lost Ruby"]

rules = [
    # --- 무기 · 방어구 · 장신구 · 호신부: 전부 드롭 레벨 밴드로 -------------------- #
    # 예전에는 "액트 1~2 한손 철퇴"를 한 덩어리로 묶어 지역 45 까지 띄웠다. 그러면 드롭 4 짜리가
    # 41레벨 동안 계속 크게 뜬다. banded() 가 드롭 레벨별로 쪼개 각자 제 수명만 살게 한다.
    *[dict(style="weapon_gear", name=f"[한손 철퇴] {label}",
           note=(f"세트 1(토템·함성) 무기. {src(bases)}. "
                 + (f"지역 {cap} 까지 크게 — 그 뒤는 흘려보낸다." if cap else "상한 없음 — 마지막 구간.")),
           **{"class": ["One Hand Maces"]}, base_types=check(bases, f"1h-{label}"),
           rarity=["Rare"] if min(DROP[n] for n in bases) >= 45 else ["Normal", "Magic", "Rare"],
           **({"area_level_max": cap} if cap else {}), stages=ALL)
      for bases, cap, label in banded(by_class(12, 1, 99), "1h")],

    *[dict(style="weapon_gear", name=f"[양손 철퇴] {label}",
           note=(f"세트 2(지진·강타, 53+ AWT) 무기. {src(bases)}. "
                 + (f"지역 {cap} 까지 크게." if cap else "상한 없음.")),
           **{"class": ["Two Hand Maces"]}, base_types=check(bases, f"2h-{label}"),
           rarity=["Rare"] if min(DROP[n] for n in bases) >= 45 else ["Normal", "Magic", "Rare"],
           **({"area_level_max": cap} if cap else {}), stages=ALL)
      for bases, cap, label in banded(by_class(17, 1, 99), "2h")],

    *[dict(style="armour_gear", name=f"[힘 방어구] {label}",
           note=(f"방어도 전용 베이스 + 실캐릭 착용 하이브리드. {src(bases)}. "
                 "굴릴 그릇이지 요구사항이 아니다 — 생명력·저항만 맞으면 된다. "
                 + (f"지역 {cap} 까지 크게." if cap else "상한 없음.")),
           base_types=check(bases, f"armour-{label}"),
           rarity=["Rare"] if min(DROP[n] for n in bases) >= 45 else ["Normal", "Magic", "Rare"],
           **({"area_level_max": cap} if cap else {}), stages=ALL)
      for bases, cap, label in banded(
          sorted(set(str_armour(1, 99)) | {"Horned Crown", "Ringmail Gauntlets", "Threaded Shoes"}), "armour")],

    *[dict(style="jewellery_gear", name=f"[장신구·허리띠] {label}",
           note=(f"{src(bases)}. 24렙 실캐릭이 옥 목걸이·토파즈·자수정 반지·생가죽 허리띠를 썼다. "
                 "호박·혈석·항성 목걸이와 무거운 허리띠는 힘 빌드 관례로 추가(제작자 발언 아님). "
                 + (f"지역 {cap} 까지 크게." if cap else "상한 없음.")),
           base_types=check(bases, f"jewellery-{label}"), rarity=["Normal", "Magic", "Rare"],
           **({"area_level_max": cap} if cap else {}), stages=ALL)
      for bases, cap, label in banded(JEWELLERY, "jewellery")],

    *[dict(style="charm_endgame", name=f"[호신부] {label}",
           note=(f"가이드 진행: 사파이어(5)→루비(5)→자수정(40). {src(bases)}. "
                 "해동·돌 호신부는 HC 동결·기절 사망 방지용 추가(제작자 발언 아님). "
                 + (f"지역 {cap} 까지 크게." if cap else "상한 없음.")),
           **{"class": ["Charms"]}, base_types=check(bases, f"charms-{label}"),
           rarity=["Normal", "Magic"],
           **({"area_level_max": cap} if cap else {}), stages=ALL)
      for bases, cap, label in banded(CHARMS, "charms")],

    *[dict(style="charm_endgame",
           name=f"[플라스크] {bases[0].split(' ')[0]} — {where}",
           note=(f"{src(bases)}. 지금 쓸 수 있는 티어만 크게 띄운다. "
                 + (f"지역 {cap} 까지 — 그 뒤는 NeverSink 가 폰트 18·무음으로 졸업시킨다(soft L4475~L4513)."
                    if cap else "상한 없음 — 마지막 티어.")
                 + " HC 는 플라스크 티어가 곧 목숨이라, 한 덩어리로 묶어 전부 크게 띄우면 "
                   "'뭐가 떨어져도 크다'가 되어 신호가 죽는다."),
           **{"class": ["Life Flasks", "Mana Flasks"]},
           base_types=check(bases, f"flask-{bases[0]}"),
           rarity=["Normal", "Magic"],
           **({"area_level_max": cap} if cap else {}),
           stages=ALL)
      for bases, cap, where in FLASK_BANDS],

    dict(style="augment_endgame", name="[맵~] 0.5.5 소울 코어 — 함성/토템/강타 +1 · Vorana's Carnage",
         note="0.5.5 패치노트 L123~: Jiquani's Soul Core of Rallying(함성 젬 +1) / Automation(토템 젬 +1) / "
              "Quaking(강타 젬 +1) — 무기 소켓 하나를 두고 경쟁, 레벨 50 요구(poe2db), 출처 Trial of Chaos. "
              "Corrupting Cry 피해 = 소켓 함성 젬 레벨이라 Rallying 이 직접 레버. Vorana's Carnage 는 투구 룬 "
              "슬롯: 함성 시 생명력 회복(방송 1:21:06 발언). 이 넷 중 셋은 9/4 GGPK 추출본에 없어 패치노트 원문으로 "
              "이름을 확인했다 — 게임 내 표기가 다르면 그 룰은 조용히 안 걸린다(재추출 후 재확인).",
         **{"class": ["Augment"]}, base_types=check(SOUL_CORES, "soul-cores"), stages=["maps", "endgame"]),
    dict(style="augment_endgame", name="[전 구간] 루비 주얼 — 실캐릭 착용",
         note=f"{src(JEWELS)}. 24렙 실캐릭이 루비 1개 착용. 토템·근접·함성 옵션이 붙는 힘 주얼.",
         **{"class": ["Jewels"]}, base_types=check(JEWELS, "jewels"), stages=ALL),
    dict(style="augment_endgame", name="[액트~맵 초반] 주얼러 오브 — 함성·AWT 링크 준비",
         note=f"{src(JEWELLERS)}. 보강하는 함성(32)·AWT(53) 서포트 4~5개를 꽂을 소켓. "
              "화폐를 건드리지 않는 원칙의 유일한 예외 — 전환 게이트라서 띄운다.",
         **{"class": ["Stackable Currency"]}, base_types=check(JEWELLERS, "jewellers"),
         stages=["campaign", "maps"]),
    *[dict(style="augment_craft", name=f"[룬] {label}",
           note=("아이언=무기 물리 % / 육체=방어구 생명력 / 사막·빙하·폭풍=저항. "
                 f"{src(bases)}. 하위·일반 아이언·저항 룬은 NeverSink 가 이미 폰트 40+소리로 띄우므로 "
                 "여기서 건드리지 않는다. 플래너 형식은 룬 소켓을 담지 않아 제작자 선택은 미확인. "
                 + (f"지역 {cap} 까지 크게." if cap else "상한 없음.")),
           **{"class": ["Augment"]}, base_types=check(bases, f"runes-{label}"),
           **({"area_level_max": cap} if cap else {}), stages=ALL)
      for bases, cap, label in banded(RUNES, "runes")],

    dict(kind="hide", name="[정리] 이 빌드가 못 쓰는 무기·보조장비",
         note="워브링어 세트 1 = 한손 철퇴 + 타워 방패, 세트 2 = 양손 철퇴. 나머지 무기·버클러·포커스는 "
              "영영 못 쓴다. 노말·매직만, 룬 슬롯·퀄리티·상위 티어 미감정이면 남긴다(NeverSink 안전장치). "
              "지역레벨 12부터. 방패 클래스는 타워 방패가 섞여 있어 숨기지 않는다. 셉터도 숨기지 않는다 — "
              "선대의 유대가 토템당 정신력 75를 예약하는데 제작자의 정신력 확보 경로가 미확인(문서 0.5)이라 "
              "셉터를 쓸 가능성을 닫지 않는다.",
         **{"class": ["Bows", "Crossbows", "Quarterstaves", "Quivers", "Spears",
                      "Staves", "Talismans", "Wands", "Bucklers", "Foci"]},
         rarity=["Normal", "Magic"], area_level_min=12, stages=ALL),
]

spec = {
    "_meta": {
        "build": "Corrupting Cry / Warcry Totem Warbringer 하드코어 — Skadoosh 0.5.5 (OG Warbringer Warcry Totems)",
        "game": "poe2",
        "patch": "0.5.5 Forbidden Rites",
        "base_filter": gemling["_meta"]["base_filter"],
        "generated_by": "scripts/build_poe2_build_overlay.py (스펙은 scripts/make_hc_warbringer_spec.py 가 플래너 정본 + GGPK 에서 유도)",
        "sources": (
            "Skadoosh Mobalytics 레벨링 가이드 4밴드 다운로드본 build_planner/Warbringer Lv*.build | "
            "poe.ninja SkadooshShoutedHard 24렙 스냅샷 2026-09-05 (HC Forbidden Rites) | "
            "제작자 Discord #build-help 2026-09-02/03 + 방송 1일차 VOD 전사(Docs/2026-09-05_SKADOOSH_... 0.0절) | "
            "0.5.5 패치노트 원문 data/_cache/patchnotes/poe2/4000864_0.5.5_Patch_Notes.txt (신규 소울 코어) | "
            "실재성은 data/game_data_poe2/BaseItemTypes.json + ArmourTypes.json (GGPK 2026-09-04 추출)"
        ),
        "palette": gemling["_meta"]["palette"],
        "notes": [
            "Show-only overlay. 숨김은 못 쓰는 무기 클래스 한 룰뿐 — 나머지는 NeverSink 규칙대로 흐른다.",
            "단계 의미: campaign=1~45(액트, Corrupting Cry 전) / maps=46~64(Corrupting Cry·AWT 53·혈마법) / endgame=65+.",
            "미가공 젬(Uncut Skill Gem)은 GemLevel 조건이 필요한데 빌더가 아직 지원하지 않는다 — NeverSink 의 레벨별 "
            "티어링을 그대로 쓴다. 함성 젬 레벨이 곧 피해이므로 미가공 스킬 젬 9(32렙)·11(42)·13(53)은 놓치지 말 것.",
            "유니크는 필터로 이름을 못 잡는다(BaseType 만). Bronzebeard(Horned Crown)·Surefooted Sigil(Jade Amulet)은 "
            "베이스 룰로 대신 띄운다. NeverSink 는 유니크를 어차피 전부 보여준다.",
            f"0.5.5 패치노트로만 확인한 이름: {sorted(set(FROM_PATCH))}. GGPK 재추출 후 KNOWN 에 들어오면 이 목록은 비어야 한다.",
            "NeverSink 베이스 필터는 vendoring 하지 않는다(.gitignore). `_meta.bases` 의 URL+SHA-256 핀으로 "
            "`python scripts/fetch_neversink_poe2_bases.py` 가 복원·검증한다.",
        ],
        "outputs": [
            {"stage": "campaign", "file": "PathcraftAI_HC-Warbringer_1-Campaign_on_NeverSink-SOFT.filter",
             "base": "neversink_poe2_soft.filter",
             "why": "액트 1~4 하드코어 레벨링(가이드 1~41 밴드 + 실캐릭). SOFT 가 가장 적게 숨긴다."},
            {"stage": "maps", "file": "PathcraftAI_HC-Warbringer_2-EarlyMaps_on_NeverSink-REGULAR.filter",
             "base": "neversink_poe2_regular.filter",
             "why": "45+ Corrupting Cry 전환 ~ 초반 맵. 소울 코어·45+ 레어 철퇴·맵 방어구가 켜지고 액트 베이스는 꺼진다."},
            {"stage": "endgame", "file": "PathcraftAI_HC-Warbringer_3-Endgame_on_NeverSink-STRICT.filter",
             "base": "neversink_poe2_strict.filter",
             "why": "65+ 마감. STRICT 인 이유는 젬링과 같다 — 하드코어에서 생존 소모품을 놓치면 안 된다."},
        ],
        "bases": gemling["_meta"]["bases"],
    },
    "styles": gemling["styles"],
    "rules": rules,
}

OUT.write_text(json.dumps(spec, ensure_ascii=False, indent=1), encoding="utf-8")
sys.stdout.reconfigure(encoding="utf-8")  # Windows 콘솔(cp949)에서 요약 출력이 죽지 않게
names = {b for r in rules for b in (r.get("base_types") or [])}
print(f"{OUT.name} 생성 — 룰 {len(rules)}개 · 베이스 {len(names)}종 · 가이드 착용 {len(GUIDE)}종")
print(f"  GGPK 실재성: {len(names & KNOWN)}/{len(names)} · 패치노트 2차 출처: {sorted(set(FROM_PATCH))}")
for tier in sorted({r.get("style") or "hide" for r in rules}):
    n = [r for r in rules if (r.get("style") or "hide") == tier]
    print(f"  {tier:<16} 룰 {len(n)} · 베이스 {sum(len(r.get('base_types') or []) for r in n)}")
