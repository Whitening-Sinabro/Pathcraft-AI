"""HC Journey — 거래소 링크 생성기 검증.

계약:
  * 옵션 → 스탯 id 는 공식 인덱스 정확 일치만. 못 맞춘 옵션은 unmapped 로 남고 필터에 안 들어간다.
  * 사다리 T1(그대로) → T2(핵심) → T3(같은 부위). 요구 레벨 상한 = 스냅샷 레벨. 즉시 구입이 기본.
  * ?q= 링크는 쿼리 JSON 을 그대로 실어 나른다(왕복 동일). 한국 서버는 호스트만 다르다.
"""
import json
import os
import sys
import urllib.parse
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "hc_journey"))
import trade_links as tl  # noqa: E402

STATS = {"result": [{"id": "explicit", "entries": [
    {"id": "explicit.stat_809229260", "text": "# to Armour"},
    {"id": "explicit.stat_3484657501", "text": "# to Armour (Local)"},
    {"id": "explicit.stat_803737631", "text": "# to Accuracy Rating"},
    {"id": "explicit.stat_691932474", "text": "# to Accuracy Rating (Local)"},
    {"id": "explicit.stat_3321629045", "text": "#% increased Armour and Energy Shield"},
    {"id": "explicit.stat_4220027924", "text": "#% to Cold Resistance"},
    {"id": "explicit.stat_X", "text": "Adds # to # Fire Damage"},
    {"id": "explicit.stat_INSTANT", "text": "Instant Recovery"},
]}, {"id": "implicit", "entries": [{"id": "implicit.stat_809229260", "text": "# to Armour"}]}]}
BASE_PATHS = {"Hallowed Crown": "Metadata/Items/Armours/Helmets/FourHelmetStrInt4Cruel",
              "Chiming Staff": "Metadata/Items/Weapons/TwoHandWeapons/Staves/FourStaff6",
              "Ultimate Life Flask": "Metadata/Items/Flasks/FourFlaskLife9",
              "Dousing Charm": "Metadata/Items/Flasks/FourCharm4"}
HELM = "Hallowed Crown\n1. +95 to Armour\n2. 31% increased Armour and Energy Shield\n3. +34% to Cold Resistance\n4. 9% increased Rarity of Items found"


def test_normalize_and_lookup_exact_only():
    idx = tl.StatIndex.from_trade_data(STATS)
    assert tl.normalize_mod("+95 to Armour") == "# to Armour"
    assert tl.normalize_mod("+34% to Cold Resistance") == "#% to Cold Resistance"
    assert tl.normalize_mod("Adds 5 to 10 Fire Damage") == "Adds # to # Fire Damage"
    assert idx.lookup("+95 to Armour") == ["explicit.stat_809229260"]   # implicit 그룹은 안 섞인다
    assert idx.lookup("9% increased Rarity of Items found") == []        # 인덱스에 없으면 빈 값(지어내지 않음)
    assert tl.mod_value("Adds 5 to 10 Fire Damage") == 7.5 and tl.mod_value("Instant Recovery") is None
    # Mobalytics export 의 범위 표기는 중간값 하나로 접힌다
    assert tl.normalize_mod("Gain (9–15)% of Damage as Extra Fire Damage") == "Gain #% of Damage as Extra Fire Damage"
    assert tl.mod_value("Gain (9–15)% of Damage as Extra Fire Damage") == 12


def test_parse_item_and_map_mods_keep_unmapped():
    item = tl.parse_item_text(HELM)
    assert item.first == "Hallowed Crown" and len(item.mods) == 4 and item.mods[0] == "+95 to Armour"
    mapped, unmapped = tl.map_mods(item, tl.StatIndex.from_trade_data(STATS))  # 카테고리 없음 → 전역
    assert [m.ids[0] for m in mapped] == ["explicit.stat_809229260", "explicit.stat_3321629045", "explicit.stat_4220027924"]
    assert unmapped == ["9% increased Rarity of Items found"]
    assert tl.parse_item_text("") is None and tl.parse_item_text("\n\n") is None


def test_local_variant_preferred_by_category():
    """투구의 '+# to Armour' 는 (Local) id, 벨트/반지의 것은 전역 id. 무기의 명중은 (Local), 투구의 명중은 전역."""
    idx = tl.StatIndex.from_trade_data(STATS)
    helm = tl.parse_item_text("Hallowed Crown\n1. +95 to Armour\n2. +75 to Accuracy Rating")
    mapped, _ = tl.map_mods(helm, idx, "armour.helmet")
    assert [m.ids[0] for m in mapped] == ["explicit.stat_3484657501", "explicit.stat_803737631"]
    assert mapped[0].ids[1:] == ["explicit.stat_809229260"]  # 전역 id 는 대안으로 보존
    belt = tl.parse_item_text("Plate Belt\n1. +20 to Armour")
    assert tl.map_mods(belt, idx, "accessory.belt")[0][0].ids[0] == "explicit.stat_809229260"
    mace = tl.parse_item_text("Slim Mace\n1. +113 to Accuracy Rating")
    assert tl.map_mods(mace, idx, "weapon.onemace")[0][0].ids[0] == "explicit.stat_691932474"
    assert tl.prefer_local_for("+10 to Armour", "armour.quiver") is False


def test_quarterstaff_and_buckler_paths_resolve_to_trade_categories():
    paths = {"Wrapped Quarterstaff": "Metadata/Items/Weapons/TwoHandWeapons/Staves/FourQuarterstaff1",
             "Ashen Staff": "Metadata/Items/Weapons/TwoHandWeapons/Staves/FourStaff1",
             "Plank Buckler": "Metadata/Items/Armours/Shields/FourShieldDex1",
             "Tower Shield": "Metadata/Items/Armours/Shields/FourShieldStr1"}
    assert tl.category_of("Wrapped Quarterstaff", paths) == "weapon.warstaff"
    assert tl.category_of("Ashen Staff", paths) == "weapon.staff"
    assert tl.category_of("Plank Buckler", paths) == "armour.buckler"
    assert tl.category_of("Tower Shield", paths) == "armour.shield"
    assert tl.mod_value("10% chance to gain 1 Rage on Hit") == 10  # Adds 형만 평균


def test_ladder_tiers_thresholds_and_requirement_cap():
    item = tl.parse_item_text(HELM)
    mapped, _ = tl.map_mods(item, tl.StatIndex.from_trade_data(STATS))
    tiers = tl.build_ladder(item, mapped, tl.category_of("Hallowed Crown", BASE_PATHS), level_max=57)
    assert [t["tier"] for t in tiers] == ["T1", "T2", "T3"]
    q1, q2, q3 = (t["query"]["query"] for t in tiers)
    # T1: 베이스 + AND 전부, 80% 하한(95→76, 31→24, 34→27), 즉시 구입, 요구 레벨 ≤ 57, 유니크 제외
    assert q1["type"] == "Hallowed Crown" and q1["status"] == {"option": "securable"}
    assert q1["filters"]["req_filters"] == {"filters": {"lvl": {"max": 57}}}
    assert q1["filters"]["type_filters"] == {"filters": {"rarity": {"option": "nonunique"}}}
    assert q1["stats"][0]["type"] == "and" and [f["value"]["min"] for f in q1["stats"][0]["filters"]] == [76, 24, 27]
    # T2: 3개 중 2개 이상, 60% 하한(57, 18, 20)
    assert q2["stats"][0]["type"] == "count" and q2["stats"][0]["value"] == {"min": 2}
    assert [f["value"]["min"] for f in q2["stats"][0]["filters"]] == [57, 18, 20]
    # T3: 카테고리 전체(베이스 없음), 3개 중 2개 이상(live 실측 후 완화)
    assert "type" not in q3 and q3["filters"]["type_filters"]["filters"]["category"] == {"option": "armour.helmet"}
    assert q3["stats"][0]["value"] == {"min": 2}
    # 레벨 미상이면 요구 상한 없음, 카테고리 미상이면 T3 없음
    tiers2 = tl.build_ladder(item, mapped, None, level_max=None)
    assert [t["tier"] for t in tiers2] == ["T1", "T2"] and "req_filters" not in tiers2[0]["query"]["query"]["filters"]


def test_nonnumeric_mod_is_presence_only_and_flask_category():
    item = tl.parse_item_text("Ultimate Life Flask\n1. Instant Recovery\n2. 31% Chance to gain a Charge when you kill an enemy")
    mapped, unmapped = tl.map_mods(item, tl.StatIndex.from_trade_data(STATS))
    assert [m.text for m in mapped] == ["Instant Recovery"] and len(unmapped) == 1
    tiers = tl.build_ladder(item, mapped, tl.category_of("Ultimate Life Flask", BASE_PATHS), level_max=45)
    assert tiers[0]["query"]["query"]["stats"][0]["filters"] == [{"id": "explicit.stat_INSTANT"}]  # 값 없음
    assert tiers[-1]["query"]["query"]["filters"]["type_filters"]["filters"]["category"] == {"option": "flask.life"}
    assert tl.category_of("Dousing Charm", BASE_PATHS) == "flask.charm" and tl.category_of("Nope", BASE_PATHS) is None


def test_reduced_mod_falls_back_to_increased_stat_as_presence_only():
    stats = {"result": [{"id": "explicit", "entries": [{"id": "explicit.stat_REC", "text": "#% increased Amount Recovered"}]}]}
    item = tl.parse_item_text("Ultimate Life Flask\n1. 50% reduced Amount Recovered")
    mapped, unmapped = tl.map_mods(item, tl.StatIndex.from_trade_data(stats))
    assert unmapped == [] and mapped[0].ids == ["explicit.stat_REC"] and mapped[0].value == -50
    assert tl._stat_filter(mapped[0], 0.8) == {"id": "explicit.stat_REC"}   # 음수는 하한을 걸지 않는다


def test_unique_is_searched_by_name():
    item = tl.parse_item_text("Blackflame\n1. Withered you inflict also increases Fire Damage taken")
    tiers = tl.build_ladder(item, [], None, level_max=80, unique_base="Amethyst Ring")
    q = tiers[0]["query"]["query"]
    assert len(tiers) == 1 and q["name"] == "Blackflame" and q["type"] == "Amethyst Ring"
    assert q["filters"]["type_filters"] == {"filters": {"rarity": {"option": "unique"}}}


def test_league_resolved_from_build_slug_not_hardcoded():
    leagues = {"result": [{"id": "Forbidden Rites"}, {"id": "HC Forbidden Rites"}, {"id": "Standard"}, {"id": "Hardcore"}]}
    assert tl.resolve_league("hc-forbidden-rites", leagues) == "HC Forbidden Rites"
    assert tl.resolve_league("forbidden-rites", leagues) == "Forbidden Rites"
    with pytest.raises(ValueError):
        tl.resolve_league("hc-next-season", leagues)   # 다음 시즌 슬러그는 목록에 없으면 실패해야 한다(조용히 지난 리그로 가지 않음)
    doc = tl.generate(index=tl.StatIndex.from_trade_data(STATS), base_paths=BASE_PATHS, uniques={}, creator="임성빈", leagues_doc=leagues)
    assert doc["_meta"]["leagues"] == ["HC Forbidden Rites"]
    assert all(e["league"] == "HC Forbidden Rites" and "HC%20Forbidden%20Rites" in e["tiers"][0]["links"]["int"] for e in doc["entries"])


def test_pace_from_rate_limit_headers():
    """2026-09-10 실측 헤더. 정책 5:10 / 15:60 / 30:300 / 600:21600 → 지속 간격은 가장 느린 300초 버킷(10초×1.15)."""
    policy = "5:10:60,15:60:300,30:300:1800,600:21600:3600"
    assert tl.parse_rate_triples(policy) == [(5, 10, 60), (15, 60, 300), (30, 300, 1800), (600, 21600, 3600)]
    assert tl.parse_rate_triples("") == [] and tl.parse_rate_triples("garbage") == []
    mid = {"X-Rate-Limit-Ip": policy, "X-Rate-Limit-Ip-State": "1:10:0,7:60:0,20:300:0,173:21600:0"}
    assert tl.pace_seconds(mid) == 300 / 30 * 1.15
    full = {"X-Rate-Limit-Ip": policy, "X-Rate-Limit-Ip-State": "2:10:0,8:60:0,29:300:0,183:21600:0"}
    assert tl.pace_seconds(full) == 300.0                      # 300초 버킷이 한도-1 → 창이 빌 때까지
    long = {"X-Rate-Limit-Ip": policy, "X-Rate-Limit-Ip-State": "1:10:0,1:60:0,1:300:0,500:21600:0"}
    assert tl.pace_seconds(long) == 21600 / 600 * 1.15         # 6시간 버킷 80% 넘으면 그 속도
    assert tl.pace_seconds(None) == tl.DEFAULT_PACE_SEC and tl.pace_seconds({}) == tl.DEFAULT_PACE_SEC


def test_q_url_roundtrips_query_and_hosts_differ():
    query = {"query": {"status": {"option": "securable"}, "type": "Hallowed Crown"}, "sort": {"price": "asc"}}
    u_int, u_kr = tl.q_url("int", "HC Forbidden Rites", query), tl.q_url("kr", "HC Forbidden Rites", query)
    assert u_int.startswith("https://www.pathofexile.com/trade2/search/poe2/HC%20Forbidden%20Rites?q=")
    assert u_kr.startswith("https://poe.kakaogames.com/trade2/search/poe2/HC%20Forbidden%20Rites?q=")
    back = json.loads(urllib.parse.unquote(u_int.split("?q=", 1)[1]))
    assert back == query
    assert tl.id_url("int", "HC Forbidden Rites", "abc") == "https://www.pathofexile.com/trade2/search/poe2/HC%20Forbidden%20Rites/abc"


def test_generate_on_fixtures_with_tiny_index():
    """실 픽스처 63건 전환-아이템에 링크가 붙고, 못 맞춘 옵션은 unmapped 로 남는다(작은 인덱스라 대부분 unmapped)."""
    doc = tl.generate(index=tl.StatIndex.from_trade_data(STATS), base_paths=BASE_PATHS, uniques={}, creator="임성빈")
    es = doc["entries"]
    assert es and all(e["creator"] == "임성빈" for e in es)
    helm = [e for e in es if e["slot"] == "Helm1" and e["item"]["first"] == "Hallowed Crown"]
    assert helm and helm[0]["level_max"] == 93 and [t["tier"] for t in helm[0]["tiers"]] == ["T1", "T2", "T3"]
    assert "int" in helm[0]["tiers"][0]["links"] and "live" not in helm[0]["tiers"][0]
    assert doc["_meta"]["n_unmapped_mods"] > 0 and doc["_meta"]["live"] is False


@pytest.mark.skipif(not (tl.CACHE_DIR / "int_stats.json").exists(), reason="trade2 캐시 없음")
def test_generate_with_real_index_maps_most_mods():
    doc = tl.generate(realms=("int", "kr"))
    es = doc["entries"]
    assert len(es) >= 50   # item_changed 63 중 슬롯이 비워진 변화는 살 것이 없어 빠진다
    total = sum(len(e["item"]["mods"]) for e in es)
    unmapped = doc["_meta"]["n_unmapped_mods"]
    assert unmapped / max(1, total) < 0.25, (unmapped, total)   # 실 인덱스로는 옵션 대부분이 맞아야 한다
    assert all("kr" in t["links"] for e in es for t in e["tiers"])
    no_cat = [e["item"]["first"] for e in es if e["item"]["category"] is None and not e["item"]["unique_base"]]
    assert not no_cat, no_cat   # 픽스처 베이스는 전부 카테고리를 유도할 수 있어야 한다


@pytest.mark.skipif(os.environ.get("HC_TRADE_LIVE") != "1", reason="HC_TRADE_LIVE=1 일 때만 공식 API 에 POST")
def test_live_search_returns_id_and_total():
    res = tl.post_search("int", tl.DEFAULT_LEAGUE, {"query": {"status": {"option": "securable"},
                         "filters": {"type_filters": {"filters": {"category": {"option": "armour.helmet"}}}}}, "sort": {"price": "asc"}})
    assert res.get("id") and isinstance(res.get("total"), int)
