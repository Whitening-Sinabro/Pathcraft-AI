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

STAVES = ["Chiming Staff", "Sanctified Staff", "Pyrophyte Staff"]
CROSSBOW_LATE = ["Bombard Crossbow", "Cannonade Crossbow"]
CROSSBOW_EARLY = ["Tense Crossbow", "Varnished Crossbow"]
CHARMS = ["Sapphire Charm", "Stone Charm", "Thawing Charm", "Dousing Charm", "Silver Charm"]
LIFE_FLASKS = ["Greater Life Flask", "Giant Life Flask", "Gargantuan Life Flask", "Transcendent Life Flask"]
MANA_FLASKS = ["Greater Mana Flask", "Gargantuan Mana Flask"]
ACT1_ARMOUR = ["Horned Crown", "Pelt Mantle", "Rope Cuffs", "Padded Leggings",
               "Face Mask", "Bronze Greaves", "Sombre Gloves"]
ACT1_JEWEL = ["Rawhide Belt", "Iron Ring"]
ACT2_ARMOUR = ["Martyr Crown", "Shaman Mantle", "Aged Cuffs", "Secured Leggings"]
ACT2_JEWEL = ["Plate Belt", "Ruby Ring", "Topaz Ring", "Sapphire Ring"]
ACT34_ARMOUR = ["Spiritbone Crown", "Braided Cuffs", "Weaver Leggings"]
ACT34_JEWEL = ["Prismatic Ring", "Pearlescent Amulet"]
ENDGAME_ARMOUR = ["Cryptic Crown", "Adherent Cuffs", "Cryptic Leggings", "Falconer's Jacket",
                  "Gallant Helm", "Golden Mail", "Commander Gauntlets", "Bastion Sabatons",
                  "Ancestral Mail", "Decorated Helm", "Champion Cuirass", "Adorned Wraps", "Bound Boots"]
JEWELLERY = ["Bloodstone Amulet", "Amber Amulet", "Absent Amulet", "Utility Belt", "Double Belt",
             "Amethyst Ring", "Gold Ring"]
RUNES = ["Lesser Body Rune", "Body Rune", "Greater Body Rune", "Greater Desert Rune", "Greater Iron Rune"]
SOUL_CORES = ["Soul Core of Ticaba", "Soul Core of Puhuarte"]

ALL_STAGES = ["campaign", "maps", "endgame"]

rules = [
    dict(style="weapon_core", name="[전 구간] 화염파 지팡이 3종 — 52 전환의 전제",
         note=("52 전환이 이 빌드의 축이고 셋 중 먼저 떨어지는 것을 쓰면 된다. "
               f"제작자마다 다른 지팡이를 쓴다: {src(STAVES)}. 셋 다 캐스터 무기라 "
               "화염파를 올리는 역할은 같다. 고유 등급은 뺀다 — 같은 베이스의 고유는 "
               "NeverSink 고유 티어 경보에 맡긴다."),
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

    dict(style="armour_gear", name="[액트 1] 방어구 베이스 — 임성빈 착용",
         note=f"임성빈 액트1 방어구. {src(ACT1_ARMOUR)}. 굴릴 그릇이지 요구사항이 아니다 — "
              "세 제작자가 방어구에서 겹치는 게 거의 없다. 생명력과 저항만 맞으면 된다.",
         base_types=check(ACT1_ARMOUR, "act1-armour"), rarity=["Normal", "Magic", "Rare"],
         area_level_max=20, stages=["campaign"]),

    dict(style="jewellery_gear", name="[액트 1] 장신구 · 허리띠 — 임성빈 착용",
         note=f"임성빈 액트1 장신구. {src(ACT1_JEWEL)}. 방어구와 색조를 갈라(뮤트 코퍼) "
              "슬롯을 한눈에 구분한다.",
         base_types=check(ACT1_JEWEL, "act1-jewel"), rarity=["Normal", "Magic", "Rare"],
         area_level_max=20, stages=["campaign"]),

    dict(style="armour_gear", name="[액트 2] 방어구 베이스 — 임성빈 착용",
         note=f"임성빈 액트2 방어구. {src(ACT2_ARMOUR)}. 굴릴 그릇이지 요구사항이 아니다 — "
              "세 제작자가 방어구에서 겹치는 게 거의 없다. 생명력과 저항만 맞으면 된다.",
         base_types=check(ACT2_ARMOUR, "act2-armour"), rarity=["Normal", "Magic", "Rare"],
         area_level_max=45, stages=["campaign"]),

    dict(style="jewellery_gear", name="[액트 2] 장신구 · 허리띠 — 임성빈 착용",
         note=f"임성빈 액트2 장신구. {src(ACT2_JEWEL)}. 방어구와 색조를 갈라(뮤트 코퍼) "
              "슬롯을 한눈에 구분한다.",
         base_types=check(ACT2_JEWEL, "act2-jewel"), rarity=["Normal", "Magic", "Rare"],
         area_level_max=45, stages=["campaign"]),

    dict(style="armour_gear", name="[액트 3/4] 방어구 베이스 — 임성빈 착용",
         note=f"임성빈 액트3/4 방어구. {src(ACT34_ARMOUR)}. 굴릴 그릇이지 요구사항이 아니다 — "
              "세 제작자가 방어구에서 겹치는 게 거의 없다. 생명력과 저항만 맞으면 된다.",
         base_types=check(ACT34_ARMOUR, "act3/4-armour"), rarity=["Normal", "Magic", "Rare"],
         area_level_max=60, stages=["campaign", "maps"]),

    dict(style="jewellery_gear", name="[액트 3/4] 장신구 · 허리띠 — 임성빈 착용",
         note=f"임성빈 액트3/4 장신구. {src(ACT34_JEWEL)}. 방어구와 색조를 갈라(뮤트 코퍼) "
              "슬롯을 한눈에 구분한다.",
         base_types=check(ACT34_JEWEL, "act3/4-jewel"), rarity=["Normal", "Magic", "Rare"],
         area_level_max=60, stages=["campaign", "maps"]),

    dict(style="armour_gear", name="[마감] 방어구 베이스 — 세 제작자 합집합",
         note=("셋이 서로 다른 베이스를 쓰므로 전부 켠다. "
               "fubgun·ds lily 의 마감 장비는 **룬각인(Runeforged) 변형**인데 그 이름은 "
               "뺐다 — GGPK 에는 535종 실재하지만 파생 `base_items_poe2.json`(4/25)에 0종이라 "
               "어휘 게이트를 통과하지 못하고, NeverSink 도 방어구 룬각인 이름을 쓰지 않는다"
               "(NeverSink 의 `Runeforged Blades` 는 혈통 젬이다). 대신 **룬각인 안 된 "
               "쌍둥이 베이스**를 넣었다: 지혜의 관/부착 소맷동/암호 각반/매잡이 상의/사령관 건틀릿. "
               "9/5 재추출로 파생 DB 를 갱신하면 룬각인 이름도 넣을 수 있다. "
               f"{src(ENDGAME_ARMOUR)}."),
         base_types=check(ENDGAME_ARMOUR, "endgame-armour"),
         rarity=["Normal", "Magic", "Rare"], stages=["maps", "endgame"]),

    dict(style="jewellery_gear", name="[전 구간] 목걸이 · 허리띠 · 마감 반지",
         note=f"{src(JEWELLERY)}. 자수정 반지는 임성빈·ds lily 마감 공통(카오스 저항).",
         base_types=check(JEWELLERY, "jewellery"),
         rarity=["Normal", "Magic", "Rare"], stages=ALL_STAGES),

    dict(style="weapon_gear", name="[액트 1~2] 초반 석궁",
         note=f"{src(CROSSBOW_EARLY)}. 임성빈 액트1/2, fubgun 1-32 구간과 일치한다.",
         **{"class": ["Crossbows"]}, base_types=check(CROSSBOW_EARLY, "crossbow-early"),
         rarity=["Normal", "Magic", "Rare"], area_level_max=45, stages=["campaign"]),

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
            "Show-only overlay. 아무것도 숨기지 않는다 — 안 걸린 아이템은 NeverSink 규칙대로 흐른다.",
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
