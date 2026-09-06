"""하코 젬링 필터 스펙을 세 제작자의 플래너 정본에서 유도해 만든다.

베이스 이름을 손으로 옮기면 오타 하나가 조용한 no-op 이 된다(그 룰은 영영 안 걸린다).
그래서 `.tmp/{seongbin,dslily,fubgun}/*.build` 의 `inventory_slots` 에서 직접 뽑고,
GGPK `BaseItemTypes.json` 으로 실재성을 확인한 것만 스펙에 넣는다.

역할 배치(사용자 결정):
  임성빈  = 기준. 트리 골격 + 방어 축(방어/생존 노드 38개)
  ds lily = 생존 보조(30개). 기절 임계값·회피->방어도
  fubgun  = 레벨링 해상도(7단계) + 능력치 경로. 방어 노드 3개뿐이라 생존 출처가 아니다
"""
from __future__ import annotations

import json
import pathlib
import sys

REPO = pathlib.Path("D:/Pathcraft-AI")
TMP = REPO / ".tmp"
IGNITE = REPO / "data" / "filter_build_targets" / "poe2_infinite_ignite_arserina_0_5_5.json"
OUT = REPO / "data" / "filter_build_targets" / "poe2_hc_gemling_seongbin_0_5_5.json"


def creator_bases(name: str) -> set[str]:
    out = set()
    for p in sorted((TMP / name).glob("*.build")):
        d = json.loads(p.read_text(encoding="utf-8"))
        for s in d.get("inventory_slots", []):
            first = (s.get("additional_text") or "").split("\n")[0].strip()
            if first:
                out.add(first)
    return out


SB, DL, FB = creator_bases("seongbin"), creator_bases("dslily"), creator_bases("fubgun")


def live_bases() -> list[str]:
    """poe.ninja 실캐릭이 **지금** 끼고 있는 베이스. 사용자가 정한 1순위 출처다
    (poe.ninja 실캐릭 > 라이브 방송 > 모발리틱스 가이드, 2026-09-06 지시).

    모발리틱스 단계 파일만 보면 마감 구간이 비뚤어진다 — 그 파일들의 몸통·장화 슬롯이
    비어 있어서 밴드가 그를 못 따라간다. 실제로 그의 61레벨 착용분 중 Hallowed Crown(54) ·
    Kalguuran Cuffs(45) · Pelt Leggings(33) · Solar Amulet(30) · Plate Belt(25) 가
    마감 필터에서 통째로 빠져 있었다(드롭 55 미만이라 마감 밴드에 안 들어간다).

    **`.build` 익스포트를 쓰면 안 된다.** 유니크를 낀 슬롯은 `unique_name` 만 담고
    **베이스 타입을 안 담는다** — 필터는 BaseType 으로 매칭하므로 그 이름으로는 못 쓴다.
    실측: The Mutable Star 는 있는데 그 베이스 `Cleric Vestments` 가 없고, 지혈/해독 호신부도
    같다. 주얼 슬롯(사파이어)은 아예 빠진다. 그래서 첫 줄만 읽으면 15종 중 11종만 나온다.
    (한때 이걸 "슬롯을 비워서 내보낸다"고 적었는데 틀렸다 — 외부 검증이 `unique_name` 을 짚었다.)
    ninja 응답의 `items`/`flasks`/`jewels` 가 정본이고, 추적기가 그것을
    `LIVE_ninja_items.json` 으로 떨궈 둔다.
    """
    side = TMP / "seongbin" / "LIVE_ninja_items.json"
    if not side.exists():
        sys.exit(f"{side} 가 없다 — 1순위 출처(poe.ninja 실캐릭) 없이 만들지 않는다. "
                 "scripts/track_poe2_character.py 로 스냅샷을 받아라.")
    payload = json.loads(side.read_text(encoding="utf-8"))
    out = [n for n in payload.get("bases") or [] if n]
    if not out:
        sys.exit(f"{side} 에 bases 가 비었다 — 조용히 통과시키지 않는다")
    meta = payload.get("_meta") or {}
    print(f"  [live] 실캐릭 Lv{meta.get('level')} 착용 {len(out)}종 ({meta.get('updatedUtc')})")
    return out


LIVE = live_bases()
KNOWN = {
    (b.get("Name") or "").strip()
    for b in json.loads((REPO / "data/game_data_poe2/BaseItemTypes.json").read_text(encoding="utf-8"))
}


def check(names: list[str], where: str) -> list[str]:
    """GGPK 에 없는 이름은 조용한 no-op 이 되므로 스펙에 넣지 않고 즉시 죽는다."""
    missing = [n for n in names if n not in KNOWN]
    if missing:
        sys.exit(f"[{where}] GGPK BaseItemTypes 에 없는 이름: {missing}")
    return names


# 사용자 지시(2026-09-06): "아예 그 임성빈꺼만 하게".
# 원래는 세 제작자(임성빈·ds lily·fubgun) 합집합이었다. 셋을 섞으면 한 사람의 빌드가 아니라
# "세 사람이 언젠가 입었던 것"이 되고, 그중 누구도 실제로 그 조합을 쓰지 않는다.
# 그래서 임성빈 플래너에 실제로 있는 베이스만 남긴다.
# 예외: 그의 플래너 형식이 담지 못하는 축(룬 소켓·화폐·소울 코어)은 SC 가이드에서 온 것이라
# ONLY_SEONGBIN 검사를 통과시킨다 — 그 목록은 seongbin_only(..., allow_guide=True) 로 표시한다.
def seongbin_only(names: list[str], where: str, allow_guide: bool = False) -> list[str]:
    keep, dropped = [], []
    for n in names:
        if n in SB or (allow_guide and n not in DL and n not in FB):
            keep.append(n)
        else:
            dropped.append(f"{n}({who(n)})")
    if dropped:
        print(f"  [{where}] 임성빈 외 제외: {dropped}")
    if not keep:
        sys.exit(f"[{where}] 임성빈 것만 남기니 베이스가 0 이다 — 룰이 조용히 죽는다")
    return keep


def who(name: str) -> str:
    tags = [t for t, s in (("임성빈", SB), ("ds lily", DL), ("fubgun", FB)) if name in s]
    return "·".join(tags) if tags else "SC 가이드"


def src(names: list[str]) -> str:
    return " / ".join(f"{n}({who(n)})" for n in names)


ignite = json.loads(IGNITE.read_text(encoding="utf-8"))

# --------------------------------------------------------------------------- #
# Crimson 팔레트 — 축이 셋이다.
#   종류 -> 색조(무기=순진홍 / 방어구=흑적 / 장신구=구리 / 호신부=더스티 로즈 /
#            룬·영혼핵=진홍) + 미니맵 모양
#   등급 -> 명도·폰트·소리
#   가치 -> 빔 (S만 영구, 나머지는 Temp, C는 없음)
# 근거: Docs/2026-08-18_LUMINARY_BOT_EXILEDCAT_CRIMSON_PROGRESSIVE_FILTER.md
#   (ExiledCat 3.29 영상 프레임에서 역산한 팔레트: 주색 #970707, 흑적 배경,
#    산호 테두리, 보조 강조는 뮤트 코퍼와 더스티 로즈 둘만 허용)
#
# **T0 자리는 비워 둔다.** NeverSink apex 는 "흰 배경 + 빨강 글자 45" 이고
# Crimson 문서의 T0 도 같은 배치다. 우리 최상위는 그 반대(진홍 배경 + 흰 글자)로
# 두어 미러급 경보와 안 겹치게 한다.
#
# 소리·빔·아이콘을 낮은 등급에서 끄는 이유: NeverSink 는 장비 블록의 22~23% 에만
# 붙이는데 우리가 100% 에 붙이고 있었다. 캠페인 455개 상황 중 289개(64%)가
# 베이스는 무음인데 우리만 소리를 냈다. 끄더라도 베이스가 요구하면 자동으로 켜진다.
CRIMSON = {
 "weapon_core": {
  "comment": "S급 무기 — 지팡이 3종·폭격/포격 석궁. 진홍 배경 + 흰 글자, 영구 빔",
  "text": [255, 255, 255], "border": [255, 255, 255], "background": [151, 7, 7],
  "font": 45, "sound": [1, 300], "beam": "Red", "icon": [0, "Red", "Kite"]},
 "charm_endgame": {
  "comment": "A급 생존 소모품 — 호신부·플라스크. 더스티 로즈. 모양은 물방울(소모품)",
  "text": [245, 175, 180], "border": [215, 110, 120], "background": [72, 24, 30],
  "font": 42, "sound": [3, 300], "beam": "Orange Temp", "icon": [1, "Orange", "Raindrop"]},
 "augment_endgame": {
  "comment": "A급 룬·영혼핵. Augment 는 화폐 계열이라 모양은 원(레퍼런스 관례)",
  "text": [245, 125, 95], "border": [215, 65, 50], "background": [58, 4, 7],
  "font": 42, "sound": [3, 300], "beam": "Red Temp", "icon": [1, "Red", "Circle"]},
 "weapon_gear": {
  "comment": "B급 초반 무기. 소리 없음 — 베이스가 요구할 때만 켜진다",
  "text": [235, 150, 130], "border": [200, 75, 55], "background": [62, 14, 10],
  "font": 42, "sound": None, "beam": "Red Temp", "icon": [2, "Red", "Kite"]},
 "armour_gear": {
  "comment": "B급 방어구. 소리·빔 없음 — 굴릴 그릇이지 경보 대상이 아니다",
  "text": [225, 160, 140], "border": [175, 80, 65], "background": [42, 3, 5],
  "font": 42, "sound": None, "beam": None, "icon": [2, "Red", "Kite"]},
 "armour_core": {
  "comment": ("S급 방어구 — 지금은 흰색 성직자의 법의 하나뿐이다(변이하는 별 기회 베이스). "
              "방어구 색조(흑적)를 유지하되 밝기·폰트·소리·빔만 S로 올린다 — "
              "Crimson 3축에서 종류는 색조, 등급은 명도/폰트/소리가 맡는다. "
              "무기 S(진홍 151,7,7)보다 어두운 흑적(110,6,8)이라 무기 경보와 구분된다"),
  "text": [255, 255, 255], "border": [255, 120, 110], "background": [110, 6, 8],
  "font": 45, "sound": [1, 300], "beam": "Red Temp", "icon": [0, "Red", "Kite"]},
 "jewellery_gear": {
  "comment": "B급 장신구 — 뮤트 코퍼로 방어구와 색조를 가른다. 소리·빔 없음",
  "text": [230, 180, 120], "border": [185, 120, 55], "background": [52, 26, 8],
  "font": 42, "sound": None, "beam": None, "icon": [2, "Orange", "Kite"]},
 "augment_craft": {
  "comment": "C급 제작 재료 — 가장 어둡고 조용하다. 소리·빔·미니맵 전부 없음",
  "text": [170, 110, 100], "border": [120, 45, 40], "background": [18, 10, 11],
  "font": 38, "sound": None, "beam": None, "icon": None},
}



# --------------------------------------------------------------------------- #
# 룰. 각 리스트는 위 표에서 뽑은 실제 착용 베이스다.

# 지팡이도 속성 룰이다. 그의 가이드 영상 원문(7:06~7:17):
#   "갑자기 화염파를 위한 좋은 옵션의 지팡이를 구하기가 어려울 수 있으니 미리미리
#    **화염 베이스 지팡이 또는 차인벨(Chiming) 지팡이**를 구해 두시면 빠른 전환에 도움이 됩니다."
# GGPK `Tags` 가 그 두 부류를 그대로 가른다. 지팡이 베이스는 주문 모드 계열을 태그로 막는다:
#   `no_fire_spell_mods` 가 있으면 화염 주문 모드를 못 굴린다 = 이 빌드에 쓸모없다.
#   화염 전용(나머지 4계열이 전부 막힌 것) = Ashen(드롭 1) · Pyrophyte(16). 그가 말한 "화염 베이스".
#   제약 없음(전 계열 가능) = Spriggan(11) · Chiming(25) · Roaring(49) · Sanctified(56) 등.
# 이름 목록일 때는 Chiming·Ashen 둘뿐이었다. 액트1에 뜨는 Spriggan(11)과 액트2 Pyrophyte(16)가
# 빠져 있어서 "미리미리 구해 두라"는 지시를 필터가 못 받쳐 줬다.
_BASE_ROWS = json.loads((REPO / "data/game_data_poe2/BaseItemTypes.json").read_text(encoding="utf-8"))
_TAG_ID = {i: (r.get("Id") or "") for i, r in
           enumerate(json.loads((REPO / "data/game_data_poe2/Tags.json").read_text(encoding="utf-8")))}
# 룬각인 변종은 어디서든 뺀다. 이유는 아래 방어구 절 주석 참조(어휘 게이트를 못 넘는다).
RUNE_VARIANT = ("Runeforged ", "Runemastered ")


# 사용자 지적(2026-09-06): "불저항지팡이랑 왜 자꾸 나오게 하는거야?"
#
# 처음엔 `no_fire_spell_mods` 태그가 **없으면** 통과시켰다. 그러면 아무 제약 없는 지팡이 9종이
# 전부 S 등급(폰트 45·소리·빔)으로 딸려 들어온다. 그런데 태그는 "무슨 주문 모드를 굴릴 수
# 있나"만 말하고, **지팡이의 정체는 부여 스킬**이다(poe2db 확인):
#   Permafrost = Heart of Ice(냉기) · Dark = Dark Pact · Ravenous = Feast of Flesh ·
#   Reflecting = Mirror of Refraction · Perching = Spiraling Conspiracy ·
#   Roaring = Unleash · Sanctified = Consecrate
# 전부 화염과 무관한데 "화염 모드도 굴릴 수 있다"는 이유로 최상위 경보를 달고 있었다.
#
# 그가 실제로 한 말은 훨씬 좁다(가이드 영상 7:06~7:17):
#   "미리미리 **화염 베이스 지팡이 또는 차인벨(Chiming) 지팡이**를 구해 두시면"
# 그래서 `no_fire_spell_mods` 가 없는 것 전부가 아니라, **화염으로 잠긴 것**(나머지 4계열이
# 막혀 굴리는 족족 화염) + 그가 이름 댄 Chiming 만 남긴다.
NAMED_STAFF = "Chiming Staff"


def fire_locked_staves() -> list[str]:
    """주문 모드가 화염으로 잠긴 지팡이. 나머지 4계열이 전부 막힌 것만."""
    blocked = {"no_cold_spell_mods", "no_lightning_spell_mods",
               "no_chaos_spell_mods", "no_physical_spell_mods"}
    out = []
    for row in _BASE_ROWS:
        if "/Staves/AbstractStaff" not in (row.get("InheritsFrom") or ""):
            continue
        name = (row.get("Name") or "").strip()
        if not name or name.startswith("[DNT]") or name.startswith(RUNE_VARIANT):
            continue
        tags = {_TAG_ID.get(t, "") for t in (row.get("Tags") or [])}
        if "no_fire_spell_mods" not in tags and blocked <= tags:
            out.append(name)
    if not out:
        sys.exit("[staves] 화염 전용 지팡이가 0종 — 태그 이름이 바뀌었는지 확인하라")
    return out


# 속성으로 뽑았어도 **`seongbin_only` 게이트는 통과시킨다.** 지팡이만 이 게이트를 건너뛰고
# 있었고, 그래서 fubgun 전용인 Pyrophyte Staff(그의 플래너 4개에 있다)가 딸려 들어왔다.
# 사용자가 잡았다("치임벨만 쓰는것같은데?"). 남는 것: Ashen(실캐릭 Lv61 세트2, ninja 확인)
# + Chiming(그의 엔드게임 플래너). 둘 다 그가 실제로 든 것이다.
STAVES = seongbin_only(fire_locked_staves() + [NAMED_STAFF], "staves")
STAVES_FIRE = [s for s in STAVES if s != NAMED_STAFF]
print(f"  [staves] 최종 {len(STAVES)}종 {STAVES}")
CROSSBOW_LATE = seongbin_only(["Bombard Crossbow", "Cannonade Crossbow"], "crossbow-late")
CROSSBOW_EARLY = seongbin_only(["Makeshift Crossbow", "Tense Crossbow", "Sturdy Crossbow", "Alloy Crossbow"],
                               "crossbow-early", allow_guide=True)
VARNISHED = ["Varnished Crossbow"]
# 세공사의 프리즘·주얼러는 52 전환 준비물이고, 뒤 둘은 액트 구간 상시 소모품이다.
# 방송 원문: "옵션 잘 뜬 아이템엔 숙련공의 오브를 아끼지 말고 바로 뚫어라"(소켓 추가, 드롭 5) ·
# "갑옷은 퀄리티도 올리면서 최고품질로"(장인의 고철, 드롭 5. 희귀몹 한 마리당 하나꼴로 나온다).
PREP_52 = ["Gemcutter's Prism", "Greater Jeweller's Orb", "Lesser Jeweller's Orb",
           "Artificer's Orb", "Armourer's Scrap"]
CHARMS = seongbin_only(["Sapphire Charm", "Stone Charm", "Thawing Charm", "Dousing Charm", "Silver Charm"],
                       "charms", allow_guide=True)
LIFE_FLASKS = seongbin_only(["Greater Life Flask", "Giant Life Flask", "Gargantuan Life Flask",
                             "Transcendent Life Flask"], "life-flasks", allow_guide=True)
# Grand Mana Flask(드롭 16)는 그의 실캐릭 61레벨이 실제로 끼고 있다. 플래너 4개에는 없어서
# 이름만 베끼던 시절에 빠져 있었다. 방송 원문: "유탄 좀 아껴두고 마나도 많이 다네요".
MANA_FLASKS = seongbin_only(["Greater Mana Flask", "Grand Mana Flask", "Gargantuan Mana Flask"],
                            "mana-flasks", allow_guide=True)
# 제작자 원문(mobalytics [0.5.5 Hardcore] 젬링 리그 스타터, 2026-09-03 갱신, Equipment Priority):
#   "장비는 회피를 사용하지 않습니다. **회피 믿다가 죽습니다.** 방어도, 에너지 보호막 베이스 장비 착용"
# 그래서 회피 수치가 붙은 베이스는 필터에서 뺀다. 플래너 inventory_slots 에서 자동으로 긁으면
# 그가 임시로 걸치고 있던 회피 베이스까지 딸려 들어온다 — 실제로 10종이 들어와 있었다.
# ArmourTypes 로 전수 검사해 회피가 0 인 것만 남긴다(방어도 단독 / ES 단독 / 방어도+ES 는 허용).
_ARMOUR_STATS = {r["BaseItemType"]: r for r in
                 json.loads((REPO / "data/game_data_poe2/ArmourTypes.json").read_text(encoding="utf-8"))}
_NAME_TO_ROW = {}
for _i, _r in enumerate(json.loads((REPO / "data/game_data_poe2/BaseItemTypes.json").read_text(encoding="utf-8"))):
    _n = (_r.get("Name") or "").strip()
    if _n:
        _NAME_TO_ROW.setdefault(_n, _i)


def no_evasion(names: list[str], where: str) -> list[str]:
    """회피가 붙은 베이스를 걷어낸다. 제작자가 명시적으로 금지한 축이다."""
    keep, dropped = [], []
    for n in names:
        row = _NAME_TO_ROW.get(n)
        st = _ARMOUR_STATS.get(row) if row is not None else None
        if st is None:
            sys.exit(f"[{where}] ArmourTypes 에 방어 수치가 없다: {n}")
        (dropped if st.get("Evasion") else keep).append(n)
    if dropped:
        print(f"  [{where}] 회피 베이스 제외: {dropped}")
    if not keep:
        sys.exit(f"[{where}] 회피 제외 후 남는 베이스가 없다 — 룰이 조용히 죽는다")
    return keep


# 이름 목록에서 속성 선택으로 바꾼 이유(2026-09-06).
#
# 위 원문은 **속성 룰**이다 — "방어도, 에너지 보호막 베이스". 그런데 우리는 그의 플래너
# `inventory_slots` 에 적힌 **이름**을 베꼈다. 플래너는 그가 그 순간 걸치고 있던 것만 담는다.
# 결과: 그의 실캐릭 61레벨 착용 10종 중 필터에 있는 것이 4종뿐이었다. 나머지 6종
# (Kalguuran Cuffs · Cleric Vestments · Hallowed Crown · Pelt Leggings · Solar Amulet ·
# Ashen Staff)은 전부 방어도/ES 베이스인데 그가 그 플래너를 찍을 때 안 입고 있었다는
# 이유만으로 빠져 있었다. 이름을 베끼면 룰이 아니라 스냅샷을 베끼는 것이다.
#
# 그래서 방어구는 GGPK 에서 직접 고른다: 회피 0 + (방어도 or ES) > 0.
#
# Runeforged/Runemastered 변종도 **넣는다**(2026-09-06 부터). 한때는 뺐는데, 이유가
# "파생 `base_items_poe2.json`(4/25 추출)에 0종이라 어휘 게이트를 못 넘는다" 였다.
# 그 파생 DB 를 9/4 GGPK 로 재생성해서 이제 469종 전부 통과한다.
# 빼면 안 되는 이유: 룬각인 변종은 같은 베이스에 룬 소켓만 달린 별개 드롭이다. 빼두면
# `Iron Cuirass` 는 켜지는데 `Runeforged Iron Cuirass` 는 조용히 안 켜진다 —
# 화면에 뜨는 아이템 수는 그대로인데 절반을 놓치는 셈이다. 이 빌드는 룬을 쓴다
# (그의 액트1 지침: "방어구에 하위 육체 룬으로 최대 생명력").
SLOT_INHERITS = {"BodyArmours": "몸통", "Helmets": "투구", "Gloves": "장갑", "Boots": "장화"}


def defensive_bases(lo: int, hi: int, where: str) -> list[str]:
    """드롭 레벨 [lo, hi] 구간의 **방어도 + 에너지 보호막 하이브리드** 방어구.

    한때 조건이 `회피 0 and (방어도 or ES)` 였다. 그러면 순수 ES 로브(방어도 0)가
    통째로 딸려 들어와 사용자가 "에너지 보호막 베이스가 자꾸 올라온다"고 잡아냈다.
    그의 원문 "방어도, 에너지 보호막 베이스"는 **둘 다 붙은 것**이라는 뜻이다.
    근거: 그의 플래너 5개가 실제로 낀 방어구 16종이 전부 AR>0 · ES>0 · EV=0 이다
    (방어도 단독 0종 · ES 단독 0종). 순수 ES 로브는 한 번도 채택하지 않았다.

    **다른 제작자 전용 베이스는 뺀다.** 이 함수는 속성으로 뽑으므로 `seongbin_only()` 를
    안 태우는데, 그 틈으로 fubgun 전용 3종(Runeforged Adherent Cuffs · Runeforged Cryptic
    Crown · Runeforged Cryptic Leggings)이 맵·마감 필터까지 들어갔다(외부 검증이 잡았다).
    밴드 전체에 게이트를 씌우면 속성 룰이 죽으니 — 아무도 이름 대지 않은 하이브리드가
    걸리는 게 이 룰의 목적이다 — **오직 다른 제작자만 쓰는 것**만 걷어낸다.
    """
    others_only = (DL | FB) - SB - set(LIVE)
    out, seen, dropped = [], set(), []
    for row_i, row in enumerate(_BASE_ROWS):
        st = _ARMOUR_STATS.get(row_i)
        if st is None or st.get("Evasion"):
            continue
        if not (st.get("Armour") and st.get("EnergyShield")):
            continue
        if not any(f"/{k}/" in (row.get("InheritsFrom") or "") for k in SLOT_INHERITS):
            continue
        name = (row.get("Name") or "").strip()
        if not name or name in seen:
            continue
        if not lo <= (row.get("DropLevel") or 0) <= hi:
            continue
        seen.add(name)
        if name in others_only:
            dropped.append(f"{name}({who(name)})")
            continue
        out.append(name)
    if dropped:
        print(f"  [{where}] 다른 제작자 전용 제외: {dropped}")
    if not out:
        sys.exit(f"[{where}] 드롭 {lo}~{hi} 에 방어도+ES 하이브리드 방어구가 하나도 없다 — 룰이 조용히 죽는다")
    print(f"  [{where}] 방어도+ES 하이브리드 {len(out)}종 (드롭 {lo}~{hi})")
    return out


# 밴드 경계는 WorldAreas 에서 뽑은 액트 진입 레벨이다: 액트1 1~15 · 액트2 16~31 ·
# 액트3 33~45 · 액트4 46~53. 드롭 레벨을 그 경계로 자른다.
ACT1_ARMOUR = defensive_bases(0, 16, "act1-armour")
ACT1_JEWEL = seongbin_only(["Rawhide Belt", "Iron Ring"], "act1-jewel")
ACT2_ARMOUR = defensive_bases(17, 33, "act2-armour")
# Solar Amulet(드롭 30)은 그의 실캐릭 61레벨 착용분이다. 플래너 4개에는 없다.
ACT2_JEWEL = seongbin_only(["Plate Belt", "Ruby Ring", "Topaz Ring", "Solar Amulet", "Sapphire Ring"],
                           "act2-jewel")
ACT34_ARMOUR = defensive_bases(34, 45, "act3/4-armour")
ACT34_JEWEL = seongbin_only(["Prismatic Ring", "Pearlescent Amulet"], "act3/4-jewel")
# 드롭 46~54 는 한때 어느 밴드에도 없었다. 그 구멍 때문에 그의 61레벨 착용 투구
# Hallowed Crown(드롭 54)이 필터에서 빠졌다. 밴드를 자를 때는 경계 자체를 검사해야 한다.
CRUEL_ARMOUR = defensive_bases(46, 54, "잔혹-armour")
# 마감은 드롭 46 부터 전부 열면 130종이 넘어 화면이 죽는다. 실제로 쫓는 것은 최상위라 55+.
ENDGAME_ARMOUR = defensive_bases(55, 999, "endgame-armour")
# 무보석 반지(드롭 44)는 그의 방송 트릭 때문에 넣는다: 반지를 끼고 그 슬롯에 스킬을 넣은 뒤
# 반지를 빼도 스킬이 장착된 채로 남고, 실제 사용은 안 되지만 **미덕의 정수 어센던시에는 그대로
# 적용된다**. 그의 가이드 영상도 같은 말을 한다("무보석 반지 두 개로 스킬 4개 추가").
JEWELLERY = seongbin_only(["Bloodstone Amulet", "Unset Ring", "Amber Amulet", "Absent Amulet", "Utility Belt",
                           "Double Belt", "Amethyst Ring", "Gold Ring"], "jewellery",
                          allow_guide=True)
# 그의 방송 원문: "방어구엔 우선 육신의 룬, 없으면 아무거나. 무기/장비 쪽엔 철 룬".
# 그런데 **하위 철 룬·철 룬은 넣으면 안 된다.** NeverSink 가 이미 폰트 40 + 음량 300 으로
# 켜는데(L2380) 이 룰은 C 등급이라 폰트 38 · 무음이라서 덮으면 조용해진다 — 실제로 넣었다가
# 스윕 REAL 회귀 108건이 났다. 상급 철 룬만 남는 이유가 이것이고, 두 번째로 밟은 지뢰다.
# 넣고 싶으면 룰을 지우는 게 아니라 **더 큰 등급으로** 따로 깔아야 한다.
RUNES = ["Lesser Body Rune", "Body Rune", "Greater Body Rune", "Greater Desert Rune", "Greater Iron Rune"]
SOUL_CORES = ["Soul Core of Ticaba", "Soul Core of Puhuarte"]

ALL_STAGES = ["campaign", "maps", "endgame"]

rules = [
    dict(style="armour_core", name="[액트 3~] 흰색 성직자의 법의 — 변이하는 별 기회 베이스",
         note=("이 빌드에서 캠페인 최고 드롭이다. 그의 방송 원문: '성직자의 법의를 (…) "
               "변이하는 별을 만드시는 게 진짜 중요합니다' / '요거는 이제 나중에 변이하는 별을 "
               "만들기 위해서 챙겨둬야 됩니다' — 아이템 줍다가 이 베이스만 따로 뺐다. "
               "poe2db 확인: 성직자의 법의를 베이스로 쓰는 유니크는 The Mutable Star 하나뿐이라 "
               "기회의 오브가 성공하면 다른 게 나올 여지가 없다. 그 유니크 옵션이 이 빌드의 방어 축 "
               "그대로다 — '현재 에너지 보호막 1%당 방어도 1% 더 있는 것처럼 피격 방어' + 출혈·점화 "
               "지속 30~50% 감소 + ES 재충전 50~100% 증가. 그가 1막에서 두 번 죽을 뻔한 원인이 "
               "출혈이었고 출혈은 ES 재충전을 막는데, 이 한 장이 그 사슬을 끊는다. "
               "**Normal 등급만 크게 띄운다** — 기회의 오브는 흰색에만 쓴다. Magic·Rare 는 "
               "액트3/4 하이브리드 밴드가 알아서 잡는다. 기회의 오브·기회의 파편은 건드리지 않았다: "
               "NeverSink 가 이미 폰트 45 + 음량 300(currency tier A)으로 켜고 있어서 덮으면 "
               "조용해진다 — 철 룬에서 회귀 108건으로 밟은 지뢰와 같은 함정이다. "
               "룬각인 성직자의 법의로 룬각인 유니크가 나오는지는 확인 못 했다(미검증)."),
         **{"class": ["Body Armours"]}, base_types=check(["Cleric Vestments"], "mutable-star-base"),
         rarity=["Normal"], stages=["campaign", "maps"]),

    dict(style="weapon_core", name="[전 구간] 화염 전용 지팡이 + 차인벨 — 52 전환의 전제",
         note=("52 전환이 이 빌드의 축인데 그때 가서 지팡이를 구하면 늦는다. 그의 가이드 영상 "
               "원문(7:06~7:17): '미리미리 **화염 베이스 지팡이 또는 차인벨 지팡이**를 구해 "
               "두시면 빠른 전환에 도움이 됩니다'. 딱 그것만 켠다 — "
               f"{', '.join(STAVES_FIRE)}(주문 모드가 화염으로 잠김) + {NAMED_STAFF}(그가 지목). "
               "한때 `no_fire_spell_mods` 태그가 **없으면** 통과시켜 제약 없는 지팡이 9종이 "
               "전부 최상위 경보를 달았다. 태그는 '무슨 모드를 굴릴 수 있나'만 말하고 지팡이의 "
               "정체는 **부여 스킬**이다 — Permafrost=Heart of Ice(냉기) · Dark=Dark Pact · "
               "Ravenous=Feast of Flesh · Reflecting=Mirror of Refraction · "
               "Perching=Spiraling Conspiracy · Roaring=Unleash · Sanctified=Consecrate. "
               "전부 화염과 무관한데 '화염도 굴릴 수 있다'는 이유로 켜져 있었다(사용자 지적). "
               "고유 등급은 NeverSink 고유 티어에 맡긴다."),
         **{"class": ["Staves"]}, base_types=check(STAVES, "staves"),
         rarity=["Normal", "Magic", "Rare"], stages=ALL_STAGES),

    dict(style="weapon_core", name="[액트 3~ · 마감] 폭격 · 포격 석궁",
         note=(f"유탄 축의 주무기. {src(CROSSBOW_LATE)}. 폭격 석궁은 셋 다 쓰고, "
               "포격 석궁은 임성빈·ds lily 의 마감 무기다."),
         **{"class": ["Crossbows"]}, base_types=check(CROSSBOW_LATE, "crossbow-late"),
         rarity=["Normal", "Magic", "Rare"], stages=ALL_STAGES),

    dict(style="charm_endgame", name="[생존] 호신부 5종 — 임성빈 축 + ds lily·fubgun 보강",
         note=("하코에서 사람을 죽이는 것은 평균 피해가 아니라 상태 이상 한 방이다. "
               f"{src(CHARMS)}. 임성빈은 액트1 사파이어 -> 액트3/4 돌·해동으로 가고, "
               "fubgun 은 해동·소화·은을 상시 낀다."),
         **{"class": ["Charms"]}, base_types=check(CHARMS, "charms"),
         rarity=["Normal", "Magic"], stages=ALL_STAGES),

    dict(style="charm_endgame", name="[생존] 생명력 플라스크 등급 진행",
         note=(f"임성빈이 액트별로 등급을 갈아탄다: {src(LIFE_FLASKS)}. "
               "fubgun 의 초월 생명력 플라스크(즉시 회복 20%)가 최종형이다. "
               "NeverSink 는 플라스크를 레벨로만 티어링해서 등급 진행이 눈에 안 띈다."),
         base_types=check(LIFE_FLASKS, "life-flasks"),
         rarity=["Normal", "Magic"], area_level_max=70, stages=["campaign", "maps"]),

    dict(style="charm_endgame", name="[생존] 마나 플라스크 등급",
         note=f"화염파는 마나 소모가 크다. {src(MANA_FLASKS)}.",
         base_types=check(MANA_FLASKS, "mana-flasks"),
         rarity=["Normal", "Magic"], area_level_max=70, stages=["campaign", "maps"]),

    dict(style="augment_endgame", name="[마감] 영혼핵 2종 — 티카바(치명타 방어) · 푸우아르테(장갑 화염저항)",
         note=("0.5.5 패치노트 원문. 티카바 = 몸통·방패에 '당신을 맞히는 피격의 치명타 피해 보너스 "
               "50% 감소'(이전 20%) — 하코에서 이번 패치 최대 수혜다. 푸우아르테는 장갑 "
               "'최대 화염 저항 +2%' 용도. 무장 무기 점화 40%는 이 빌드에 안 붙는다"
               "(지팡이가 캐스터 무기 + 석궁은 무기 세트가 다르다). 소프트코어 편 제8장 판정."),
         **{"class": ["Augment"]}, base_types=check(SOUL_CORES, "soul-cores"),
         stages=["maps", "endgame"]),

    dict(style="armour_gear", name="[전 구간] 실캐릭이 지금 끼고 있는 베이스 — poe.ninja",
         note=("사용자가 정한 1순위 출처(poe.ninja 실캐릭)를 밴드와 무관하게 항상 켠다. "
               f"현재 스냅샷 {len(LIVE)}종: {', '.join(LIVE)}. "
               "왜 따로 두나 — 드롭 레벨 밴드만으로는 마감에서 그를 못 따라간다. "
               "Hallowed Crown(54) · Kalguuran Cuffs(45) · Pelt Leggings(33) · Solar Amulet(30) · "
               "Plate Belt(25) 는 마감 밴드(드롭 55+)에 안 들어가서 endgame 필터에서 통째로 "
               "빠져 있었다. 그가 61레벨에 실제로 끼고 있는데도. 적대검증이 이 구멍을 짚었다. "
               "이 룰은 스냅샷이 갱신되면 같이 바뀐다 — 추적기가 플래너를 덮어쓰면 재실행하라."),
         base_types=check(LIVE, "live"), rarity=["Normal", "Magic", "Rare"], stages=ALL_STAGES),

         # 순서 주의: 이 룰은 **전용 룰(지팡이·석궁·호신부·플라스크·영혼핵) 뒤**에 와야 한다.
         # 앞에 두면 Ashen Staff·Bombard Crossbow 가 여기 먼저 걸려 S 경보를 잃는다.
    dict(style="armour_gear", name="[액트 1] 방어도+ES 하이브리드 방어구 — 회피·순수ES 제외",
         note=(f"드롭 1~16 의 방어도+에너지 보호막 하이브리드 {len(ACT1_ARMOUR)}종. 이름 목록이 아니라 "
               "GGPK 속성으로 골랐다 — 제작자 원문이 '방어도, 에너지 보호막 베이스 장비 착용, "
               "회피 믿다가 죽습니다' 라는 **속성 룰**이기 때문이다. 그의 플래너에 적힌 이름만 "
               "베끼면 그가 그 순간 안 입고 있던 같은 성질의 베이스가 통째로 빠진다. "
               "회피가 1이라도 붙은 베이스는 하이브리드까지 전부 뺐다. "
               "굴릴 그릇이지 요구사항이 아니다 — 생명력과 저항만 맞으면 된다."),
         base_types=check(ACT1_ARMOUR, "act1-armour"), rarity=["Normal", "Magic", "Rare"],
         area_level_max=45, stages=["campaign"]),

    dict(style="jewellery_gear", name="[액트 1] 장신구 · 허리띠 — 임성빈 착용",
         note=f"임성빈 액트1 장신구. {src(ACT1_JEWEL)}. 방어구와 색조를 갈라(뮤트 코퍼) "
              "슬롯을 한눈에 구분한다.",
         base_types=check(ACT1_JEWEL, "act1-jewel"), rarity=["Normal", "Magic", "Rare"],
         area_level_max=45, stages=["campaign"]),

    dict(style="armour_gear", name="[액트 2] 방어도+ES 하이브리드 방어구 — 회피·순수ES 제외",
         note=(f"드롭 17~33 의 방어도+에너지 보호막 하이브리드 {len(ACT2_ARMOUR)}종. 밴드 경계는 "
               "WorldAreas 에서 뽑은 액트 진입 레벨이다(액트2 = 지역 16~31). 회피 베이스는 제외."),
         base_types=check(ACT2_ARMOUR, "act2-armour"), rarity=["Normal", "Magic", "Rare"],
         area_level_max=65, stages=["campaign"]),

    dict(style="jewellery_gear", name="[액트 2] 장신구 · 허리띠 — 임성빈 착용",
         note=f"임성빈 액트2 장신구. {src(ACT2_JEWEL)}. 방어구와 색조를 갈라(뮤트 코퍼) "
              "슬롯을 한눈에 구분한다.",
         base_types=check(ACT2_JEWEL, "act2-jewel"), rarity=["Normal", "Magic", "Rare"],
         area_level_max=65, stages=["campaign"]),

    dict(style="armour_gear", name="[액트 3/4] 방어도+ES 하이브리드 방어구 — 회피·순수ES 제외",
         note=(f"드롭 34~45 의 방어도+에너지 보호막 하이브리드 {len(ACT34_ARMOUR)}종. 그의 실캐릭 "
               "61레벨 착용분 중 Kalguuran Cuffs(드롭 45) · Cleric Vestments(45)가 이 밴드다 — "
               "이름 목록 시절에는 둘 다 빠져 있었다. 회피 베이스는 제외."),
         base_types=check(ACT34_ARMOUR, "act3/4-armour"), rarity=["Normal", "Magic", "Rare"],
         area_level_max=80, stages=["campaign", "maps"]),

    dict(style="jewellery_gear", name="[액트 3/4] 장신구 · 허리띠 — 임성빈 착용",
         note=f"임성빈 액트3/4 장신구. {src(ACT34_JEWEL)}. 방어구와 색조를 갈라(뮤트 코퍼) "
              "슬롯을 한눈에 구분한다.",
         base_types=check(ACT34_JEWEL, "act3/4-jewel"), rarity=["Normal", "Magic", "Rare"],
         area_level_max=80, stages=["campaign", "maps"]),

    dict(style="armour_gear", name="[액트 4 · 잔혹] 방어도+ES 하이브리드 방어구 — 회피·순수ES 제외",
         note=(f"드롭 46~54 의 방어도+에너지 보호막 하이브리드 {len(CRUEL_ARMOUR)}종. 그의 실캐릭 "
               "61레벨 투구 Hallowed Crown(드롭 54)이 여기다 — 액트3/4(34~45)와 마감(55+) "
               "사이에 밴드가 없어서 통째로 빠져 있던 구간이다."),
         base_types=check(CRUEL_ARMOUR, "잔혹-armour"), rarity=["Normal", "Magic", "Rare"],
         area_level_max=80, stages=["campaign", "maps"]),

    dict(style="armour_gear", name="[마감] 방어도+ES 하이브리드 방어구 — 회피·순수ES 제외",
         note=(f"드롭 55 이상의 방어도+에너지 보호막 하이브리드 {len(ENDGAME_ARMOUR)}종. 드롭 46 부터 "
               "전부 열면 130종이 넘어 화면이 죽어서 최상위만 남겼다 — 마감에서 실제로 쫓는 것이 "
               "거기다. 룬각인(Runeforged/Runemastered) 변형은 GGPK 에 실재하지만 파생 "
               "`base_items_poe2.json`(4/25 추출)에 0종이고 NeverSink 도 그 이름을 안 써서 "
               "빌더 어휘 게이트를 못 넘는다 — 넣어도 조용히 떨어지므로 뺐다. "
               "파생 DB 재추출 뒤에 넣을 것. 아이템 레벨 65 문턱은 NeverSink 가 자기 방어구 "
               "블록에 실제로 쓰는 값이다(strict 기준 65 다섯 · 80 둘 · 82 둘). 문턱 없이 89종을 "
               "열었더니 NeverSink 가 숨기던 상태 1,225 개가 되살아났다 — 마감 화면이 죽는다."),
         base_types=check(ENDGAME_ARMOUR, "endgame-armour"), item_level_min=65,
         rarity=["Normal", "Magic", "Rare"], stages=["maps", "endgame"]),

    dict(style="jewellery_gear", name="[전 구간] 목걸이 · 허리띠 · 마감 반지",
         note=f"{src(JEWELLERY)}. 자수정 반지는 임성빈·ds lily 마감 공통(카오스 저항).",
         base_types=check(JEWELLERY, "jewellery"),
         rarity=["Normal", "Magic", "Rare"], stages=ALL_STAGES),

    dict(style="weapon_gear", name="[액트 1~2] 초반 석궁 — 갈아타며 쓰는 것",
         note=("아르세리나 2026-09-04 영상(youtu.be/rNIXxLrQY6E, 0:14~1:10): 임시(1)·팽팽한(4)·"
               "튼튼한(10)은 '화폐를 많이 투자할 필요가 없다, 좋은 게 나오면 가볍게 바꿔 쓴다'. "
               "10레벨에는 상점에서 원소 플랫 붙은 것을 확인. 합금(26)은 '잘 만든 광택 나는 석궁이 "
               "있으면 패스해도 된다' — 33레벨 미만은 DPS 차이가 크지 않다. "
               f"{src(CROSSBOW_EARLY)}"),
         **{"class": ["Crossbows"]}, base_types=check(CROSSBOW_EARLY, "crossbow-early"),
         rarity=["Normal", "Magic", "Rare"], stages=["campaign"]),

    dict(style="weapon_core", name="[액트 2~] 광택 나는 석궁 — 아이템 레벨 18 이상만",
         note=("같은 영상 0:36~1:03. 광택 나는 석궁은 16레벨부터 쓸 수 있지만 **아이템 레벨 18 "
               "이상 베이스를 추천**한다 — ilvl 18부터 투사체 스킬 레벨 옵션이 붙을 수 있기 "
               "때문이다. '16레벨에 급하게 만들기보다 지역레벨 18 이상에서 나온 베이스로 원소 플랫 + "
               "투사체 스킬 레벨을 같이 노리는 쪽이 훨씬 좋다.' 투사체 스킬 레벨 + 플랫 두 줄이면 합격. "
               "그래서 ilvl 조건을 걸어 **살 가치가 있는 것만** 최상위로 띄운다."),
         **{"class": ["Crossbows"]}, base_types=check(VARNISHED, "varnished"),
         rarity=["Normal", "Magic", "Rare"], item_level_min=18,
         stages=["campaign"]),

    dict(style="weapon_gear", name="[액트 2~] 광택 나는 석궁 — ilvl 18 미만 (임시용)",
         note=("위 룰이 ilvl 18 이상만 최상위로 띄우는데, 그가 **16레벨부터 낀다**"
               "(액트2 플래너 Weapon1 `level_interval=[16,100]`). 그래서 ilvl 16~17 구간이 "
               "세 필터 어디에도 안 걸려 NeverSink 기본(폰트 32)으로 떨어졌다 — 외부 검증이 잡았다. "
               "그 구간은 '제작할 가치는 없지만 지금 낄 것'이라 B 등급으로만 켠다. "
               "S 룰이 앞에 있으므로 18 이상은 그쪽이 먼저 이긴다."),
         **{"class": ["Crossbows"]}, base_types=check(VARNISHED, "varnished-early"),
         rarity=["Normal", "Magic", "Rare"], stages=["campaign"]),

    dict(style="augment_endgame", name="[52 전환 준비] 세공사의 프리즘 · 주얼러 오브",
         note=("같은 영상 2:44~3:22. 전환 전에 모아둬야 하는 소모품이다. "
               "**세공사의 프리즘 4개** — 화염파 퀄리티를 올리는 데 쓴다(2차 전직의 퀄리티 효과 강화가 "
               "이 빌드의 핵심이라 퀄리티가 곧 딜이다). '액트 단계에서 리그 콘텐츠를 진행하면서 미리 "
               "모아두라'고 명시. **상위 주얼러 오브**로 화염파 4소켓을 열고(액트 4장 리그 콘텐츠에서 "
               "나온다), 기름 유탄은 **하위 주얼러 오브**로 최소 3소켓. "
               "**상위가 하나뿐이면 무조건 화염파에 먼저 쓴다.** "
               "화폐를 건드리지 않는다는 원칙의 유일한 예외 — 이 셋은 화폐 가치가 아니라 "
               "**52 전환 게이트**라서 띄운다."),
         **{"class": ["Stackable Currency"]}, base_types=check(PREP_52, "prep-52"),
         stages=["campaign", "maps"]),

    dict(style="augment_craft", name="[전 구간] 룬 진행 — 하위 육체 -> 육체 -> 상급",
         note=("세 플래너 모두 룬 소켓 내용을 담지 않는다(플래너 형식의 한계). "
               "이 목록은 소프트코어 가이드 제4·7장에서 가져왔다 — 같은 아키타입이라 "
               f"룬은 동일하다. {', '.join(RUNES)}."),
         **{"class": ["Augment"]}, base_types=check(RUNES, "runes"),
         stages=ALL_STAGES),

    # ---- 숨김 --------------------------------------------------------------
    # NeverSink 는 이 규칙을 이미 다 써놓고 꺼서 배포한다(soft L687-L864,
    # `conditionalhiders` 14블록, 활성 0). 그대로 켤 수는 없다 -- 그쪽 무기 목록에
    # "Crossbows" 와 "Staves" 가 들어 있는데 그게 정확히 이 빌드의 무기다.
    # 그래서 클래스 목록만 갈아끼우고 안전장치 셋(Sockets 0 / Quality 0 /
    # UnidentifiedItemTier <= 3)은 NeverSink 것을 그대로 쓴다.
    dict(kind="hide", name="[정리] 이 빌드가 못 쓰는 무기·보조장비",
         note=("젬링은 석궁(무기 세트 1)과 지팡이(세트 2) 둘 다 양손이라 나머지 무기도 "
               "보조장비도 영영 못 쓴다. 노말·매직만, 룬 슬롯이 뚫렸거나 퀄리티가 붙었거나 "
               "상위 티어 미감정이면 남긴다 — NeverSink 의 안전장치 그대로. "
               "지역레벨 12부터: 그 전은 무기를 고를 여지가 있는 구간이다."),
         **{"class": ["Bows", "One Hand Maces", "Quarterstaves", "Quivers", "Sceptres",
                      "Spears", "Talismans", "Two Hand Maces", "Wands",
                      "Bucklers", "Foci", "Shields"]},
         rarity=["Normal", "Magic"], area_level_min=12, stages=ALL_STAGES),
]

def assert_no_shadowing(rules: list[dict]) -> None:
    """앞선 룰이 뒤 룰을 통째로 가리면 죽는다 — 필터는 처음 걸린 블록이 이긴다.

    실제로 밟았다: 흰색 성직자의 법의(변이하는 별 기회 베이스)를 S 등급으로 새로 깔았는데
    액트3/4 하이브리드 밴드가 스펙에서 먼저라 블록도 먼저 나갔고, 그 넓은 룰이
    `Rarity Normal Magic Rare` 로 같은 베이스를 이미 잡아서 새 룰은 한 번도 안 걸렸다.
    **스윕은 이걸 못 잡는다** — 조용해진 게 아니라 그냥 안 걸리는 것이라 회귀로 안 센다.

    **부분 가림도 가림이다.** 처음 쓴 판정은 "앞 룰의 지역 레벨 상한이 더 낮으면 뒤 룰이
    그 위에서 살아나니까 통과"였는데, 그러면 실제 사건을 못 잡는다 — 액트3/4 밴드는
    `AreaLevel <= 60` 이고 성직자의 법의는 드롭 45 라 **정확히 그 60 이하 구간에서만**
    의미가 있다. 위쪽에서 살아나 봐야 소용이 없다. 그래서 지역 레벨 창이 조금이라도
    겹치면 그 겹치는 구간에서 뒤 룰이 죽는 것으로 보고 실패시킨다.

    **집합 포함이 아니라 베이스별 교집합으로 본다.** 처음엔 뒤 룰의 베이스가 앞 룰에 통째로
    들어갈 때만 검사했는데, 그러면 일부만 가려지는 경우를 놓친다 — 실제로 그랬다.
    `[전 구간] 실캐릭 착용`(armour_gear, 무음) 이 앞에 있고 지팡이 룰이 `{Ashen, Chiming}` 인데
    Ashen 만 겹쳐서 집합 포함이 성립하지 않아 PASS 가 났다. 결과: 그가 지금 들고 있는
    **Ashen Staff 와 Bombard Crossbow 가 S 경보(폰트 45·음량 300) 대신 폰트 42·무음**으로
    떨어졌다. 외부 검증(codex gpt-6-astra)이 잡았다.

    **가림이 해로운 경우만 잡는다** — 앞 룰이 뒤 룰보다 **조용할 때**. 같거나 더 큰 등급이
    먼저 걸리는 것은 문제가 아니다(어차피 그게 이겨도 손해가 없다).
    """
    narrowing = ("sockets_min", "item_level_min", "quality_min")

    def window(rule: dict) -> tuple[int, float]:
        return int(rule.get("area_level_min") or 0), float(rule.get("area_level_max") or 1e9)

    def loudness(rule: dict) -> tuple[int, int, int]:
        s = CRIMSON.get(rule.get("style") or "", {})
        snd = s.get("sound") or [0, 0]
        return (int(s.get("font") or 0), int(snd[1] if len(snd) > 1 else 0),
                1 if s.get("beam") else 0)

    for i, later in enumerate(rules):
        lb, lr = set(later.get("base_types") or []), set(later.get("rarity") or [])
        if not lb:
            continue
        for earlier in rules[:i]:
            eb = set(earlier.get("base_types") or [])
            shared = lb & eb
            if not shared:
                continue
            er = set(earlier.get("rarity") or [])
            if lr and er and not lr & er:
                continue
            if any(earlier.get(k) for k in narrowing):
                continue
            if not set(later.get("stages") or []) & set(earlier.get("stages") or []):
                continue
            (e_lo, e_hi), (l_lo, l_hi) = window(earlier), window(later)
            lo, hi = max(e_lo, l_lo), min(e_hi, l_hi)
            if lo > hi:
                continue
            if loudness(earlier) >= loudness(later):
                continue  # 먼저 걸리는 쪽이 같거나 더 크다 — 손해가 없다
            sys.exit(
                f"룰 가림: '{later['name']}' 가 앞선 '{earlier['name']}' 에 먹힌다.\n"
                f"  죽는 구간: 지역 레벨 {lo}~{'무한' if hi >= 1e9 else int(hi)}\n"
                f"  겹치는 베이스 {len(shared)}종: {sorted(shared)[:6]}\n"
                f"  등급: 앞 {earlier.get('style')}{loudness(earlier)} "
                f"< 뒤 {later.get('style')}{loudness(later)}\n"
                f"  큰 등급 룰을 rules 리스트에서 더 앞으로 옮겨라."
            )


assert_no_shadowing(rules)

spec = {
    "_meta": {
        "build": "Flameblast + Oil Grenade Gemling Legionnaire 하드코어 — 임성빈 기준 / ds lily·fubgun 보조",
        "game": "poe2",
        "patch": "0.5 / 0.5.5 Forbidden Rites",
        "base_filter": ignite["_meta"]["base_filter"],
        "generated_by": "scripts/build_poe2_build_overlay.py (스펙은 scratchpad/make_hc_spec.py 가 플래너 정본에서 유도)",
        "sources": (
            "임성빈 Mobalytics 하드코어 4탭 https://mobalytics.gg/poe-2/profile/seongbin-poe2-hardcore-zaxjdu/builds/11f193d5-8baf-44ea-9938-579451232125 | "
            "ds lily Mobalytics 6탭 https://mobalytics.gg/poe-2/profile/ds_lily/builds/oil-flameblast-gemling | "
            "fubgun Mobalytics 7탭 https://mobalytics.gg/poe-2/builds/fubgun-flameblast-oil-grenade | "
            "세 사람의 인게임 플래너 다운로드본(build_planner/) inventory_slots 에서 베이스를 직접 유도했다 | "
            "룬·영혼핵은 소프트코어 가이드(Docs/2026-09-02_ARSERINA_...) 제4·7·8장 | "
            "실재성은 data/game_data_poe2/BaseItemTypes.json (GGPK, 2026-09-04 추출) 로 전수 확인"
        ),
        "palette": ignite["_meta"]["palette"],
        "notes": [
            "이 스펙은 hide 룰을 하나 선언한다(이 빌드가 못 쓰는 무기·보조장비, 지역레벨 12+). "
            "그 외에는 아무것도 숨기지 않는다 — 안 걸린 아이템은 NeverSink 규칙대로 흐른다. "
            "한때 이 줄이 '아무것도 숨기지 않는다' 였는데 숨김 룰이 들어온 뒤에도 안 고쳐져 "
            "산출물이 자기를 잘못 설명했다.",
            "역할 배치: 임성빈=기준(트리 골격+방어 축) / ds lily=생존 보조 / fubgun=레벨링 해상도+능력치 경로. "
            "fubgun 은 생존 출처가 아니다 — 엔드게임 방어/생존 노드가 3개뿐이고 반지 2개가 아이템 희귀도용 금 반지다.",
            "엔드게임 패시브 트리 실측: 넷(3인+아르세리나) 공통 84노드 / 합집합 269, 쌍별 자카드 48~59%. "
            "점화 노드는 넷 다 14~15개로 동일하고, 갈리는 축은 전적으로 방어다 — "
            "임성빈 38 · ds lily 30 · 아르세리나 15 · fubgun 3.",
            "방어구 베이스를 개별로 나열하는 축은 원래 약하다. 63종 합집합 중 셋 다 쓰는 것은 석궁 2종뿐이고, "
            "이는 취향 문제가 아니라 POE2 방어구가 '생명력+저항을 굴리는 그릇'이라 베이스가 중요하지 않기 때문이다. "
            "그래서 방어구 룰의 주석은 전부 '굴릴 그릇이지 요구사항이 아니다'라고 적었다.",
            "룬각인(Runeforged) 은 별개 BaseType 이다 — 메타데이터 경로가 `...Verisium` 으로 끝난다. "
            "`Cryptic Crown` 룰은 `Runeforged Cryptic Crown` 을 잡지 못하므로 양쪽 다 넣었다.",
            "제작자 셋 다 아이템 필터는 배포하지 않는다(세 페이지 모두 loot filter 언급 0건). 그래서 이 필터가 필요하다.",
            "NeverSink 베이스 필터는 vendoring 하지 않는다(.gitignore). `_meta.bases` 의 URL+SHA-256 핀으로 "
            "`python scripts/fetch_neversink_poe2_bases.py` 가 복원·검증한다.",
        ],
        "outputs": [
            {"stage": "campaign", "file": "PathcraftAI_HC-Gemling_1-Campaign_on_NeverSink-SOFT.filter",
             "base": "neversink_poe2_soft.filter",
             "why": "액트 1~4 하드코어 레벨링. 임성빈의 액트별 착용 베이스와 생존 키트(호신부·생명력 플라스크)를 봐야 한다. SOFT 가 가장 적게 숨긴다."},
            {"stage": "maps", "file": "PathcraftAI_HC-Gemling_2-EarlyMaps_on_NeverSink-REGULAR.filter",
             "base": "neversink_poe2_regular.filter",
             "why": "52 전환 직후 ~ 초반 맵. 지팡이 3종·마감 방어구·영혼핵이 켜지고 액트1/2 레벨링 베이스는 꺼진다."},
            {"stage": "endgame", "file": "PathcraftAI_HC-Gemling_3-Endgame_on_NeverSink-STRICT.filter",
             "base": "neversink_poe2_strict.filter",
             "why": "마감. VERY-STRICT 이 아니라 STRICT 인 이유는 점화 오버레이와 같다 — 하드코어에서 생존 소모품을 놓치면 안 된다."},
        ],
        "bases": ignite["_meta"]["bases"],
    },
    "styles": CRIMSON,
    "rules": rules,
}

OUT.write_text(json.dumps(spec, ensure_ascii=False, indent=1), encoding="utf-8")
names = {b for r in rules for b in (r.get("base_types") or [])}
print(f"{OUT.name} 생성 — 룰 {len(rules)}개 · 베이스 {len(names)}종")
print(f"  GGPK 실재성: {len(names & KNOWN)}/{len(names)}")
for tier in sorted({r.get("style") or "hide" for r in rules}):
    n = [r for r in rules if (r.get("style") or "hide") == tier]
    print(f"  {tier:<8} 룰 {len(n)} · 베이스 {sum(len(r.get('base_types') or []) for r in n)}")
