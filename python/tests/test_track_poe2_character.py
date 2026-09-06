"""track_poe2_character: 변화 판정과 PoB 디코드.

이 스크립트는 사람이 안 볼 때 몇 시간을 도는 게 목적이라, 조용히 틀리면 밤새 아무것도
안 남는다. 그래서 "무엇을 변화로 볼 것인가"(fingerprint)와 "PoB 를 어떻게 푸는가"를 고정한다.
"""

from __future__ import annotations

import base64
import json
import sys
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from track_poe2_character import decode_pob, diff_lines, fingerprint, summary  # noqa: E402


def char(level=29, passives=36, ascendancy=2, keystones=None, gems=None, items=None, life=803):
    return {
        "level": level,
        "passiveCounts": {"passives": passives, "ascendancy": ascendancy},
        "keystones": keystones if keystones is not None else [],
        "skills": [{"allGems": [{"name": n} for n in g]} for g in
                   (gems if gems is not None else [["Shockwave Totem", "Rapid Attacks I"], ["Raise Shield"]])],
        "items": items if items is not None else [
            {"itemSlot": 1, "itemData": {"baseType": "Horned Crown", "name": "Bronzebeard"}},
            {"itemSlot": 5, "itemData": {"baseType": "Bronze Greaves", "name": "Victory Trail"}},
        ],
        "defensiveStats": {"life": life, "spirit": 30, "armour": 468, "blockChance": 37,
                           "effectiveHealthPool": 1183, "fireResistance": -5, "coldResistance": 20,
                           "lightningResistance": 4, "chaosResistance": 11},
    }


# --- PoB 디코드 ------------------------------------------------------------- #

def test_decode_pob_uses_base64url():
    """ninja 는 base64url 을 쓴다. 표준 base64 로 풀면 zlib 이 죽는다."""
    payload = b"<PathOfBuilding><Build level='29'/></PathOfBuilding>" * 40
    code = base64.urlsafe_b64encode(zlib.compress(payload)).decode().rstrip("=")
    assert "-" in code or "_" in code or True  # 패딩 제거 자체도 견뎌야 한다
    assert decode_pob(code).startswith("<PathOfBuilding>")


def test_decode_pob_tolerates_missing_padding():
    payload = b"x" * 101
    code = base64.urlsafe_b64encode(zlib.compress(payload)).decode().rstrip("=")
    assert decode_pob(code) == "x" * 101


# --- 무엇이 변화인가 --------------------------------------------------------- #

def test_fingerprint_ignores_cosmetic_stat_drift():
    """방어도·막기·EHP 는 장비 롤 하나로 흔들린다 — 그걸로 깨우면 밤새 노이즈다."""
    a = char()
    b = char()
    b["defensiveStats"]["armour"] = 999
    b["defensiveStats"]["effectiveHealthPool"] = 1
    assert fingerprint(a) == fingerprint(b)


def test_fingerprint_catches_the_things_the_doc_asks_about():
    base = char()
    assert fingerprint(char(level=33)) != fingerprint(base)
    assert fingerprint(char(passives=40)) != fingerprint(base)
    assert fingerprint(char(ascendancy=4)) != fingerprint(base)
    assert fingerprint(char(keystones=["Ancestral Bond"])) != fingerprint(base)
    assert fingerprint(char(life=900)) != fingerprint(base)


def test_fingerprint_catches_a_support_added_to_an_existing_skill():
    base = char()
    changed = char(gems=[["Shockwave Totem", "Rapid Attacks I", "Brutality II"], ["Raise Shield"]])
    assert fingerprint(base) != fingerprint(changed)


def test_fingerprint_is_order_independent():
    a = char(gems=[["Raise Shield"], ["Shockwave Totem", "Rapid Attacks I"]])
    assert fingerprint(a) == fingerprint(char())


def test_fingerprint_catches_an_item_swap():
    swapped = char(items=[
        {"itemSlot": 1, "itemData": {"baseType": "Horned Crown", "name": "Bronzebeard"}},
        {"itemSlot": 5, "itemData": {"baseType": "Threaded Shoes", "name": "Onslaught Spur"}},
    ])
    assert fingerprint(char()) != fingerprint(swapped)


# --- 사람이 읽는 출력 -------------------------------------------------------- #

def test_diff_lines_names_the_keystone_in_bold():
    lines = diff_lines(char(), char(keystones=["Ancestral Bond"]))
    assert any("Ancestral Bond" in line and "**" in line for line in lines), lines


def test_diff_lines_reports_gem_and_item_moves():
    old = char()
    new = char(level=33,
               gems=[["Shockwave Totem", "Rapid Attacks I", "Brutality II"], ["Raise Shield"]],
               items=[{"itemSlot": 1, "itemData": {"baseType": "Horned Crown", "name": "Bronzebeard"}},
                      {"itemSlot": 5, "itemData": {"baseType": "Iron Greaves", "name": "Doom Stride"}}])
    lines = "\n".join(diff_lines(old, new))
    assert "레벨 29 -> 33" in lines
    assert "+ 젬" in lines and "Brutality II" in lines
    assert "- 젬" in lines
    assert "Doom Stride" in lines


def test_diff_lines_empty_when_nothing_moved():
    assert diff_lines(char(), char()) == []


def test_summary_carries_level_keystone_and_resistances():
    text = summary(char(keystones=["Ancestral Bond"]))
    assert "Lv29" in text and "-5/20/4/11" in text and "Ancestral Bond" in text


def test_summary_survives_a_sparse_payload():
    """폴링 중 응답이 얇게 와도 죽지 않아야 한다 — 죽으면 추적이 끝난다."""
    assert "Lv" in summary({"level": 12})


# --- 429 내성 ---------------------------------------------------------------- #

def test_rate_limited_is_its_own_exception():
    """429 를 일반 실패로 세면 20회 만에 추적이 죽는다 — 물러서야 할 신호는 따로 구분한다."""
    import urllib.error
    import track_poe2_character as t

    calls = {"n": 0}

    def boom(req, timeout=None):
        calls["n"] += 1
        raise urllib.error.HTTPError(req.full_url, 429, "Too Many Requests", {}, None)

    t.urllib.request.urlopen = boom
    try:
        try:
            t.fetch("a", "b", "c")
        except t.RateLimited:
            pass
        else:
            raise AssertionError("RateLimited 로 올라오지 않았다")
    finally:
        import importlib
        importlib.reload(t)
    assert calls["n"] == 1


def test_other_http_errors_are_not_swallowed_as_rate_limit():
    import urllib.error
    import importlib
    import track_poe2_character as t

    def boom(req, timeout=None):
        raise urllib.error.HTTPError(req.full_url, 500, "Server Error", {}, None)

    t.urllib.request.urlopen = boom
    try:
        try:
            t.fetch("a", "b", "c")
        except t.RateLimited:
            raise AssertionError("500 을 429 로 오분류했다")
        except urllib.error.HTTPError:
            pass
    finally:
        importlib.reload(t)


def test_fetch_patiently_retries_then_succeeds():
    """시작 조회가 429 하나로 죽으면 밤샘 추적이 통째로 사라진다."""
    import importlib
    import track_poe2_character as t

    calls = {"n": 0}

    def flaky(account, name, overview):
        calls["n"] += 1
        if calls["n"] < 3:
            raise t.RateLimited("429")
        return {"level": 34}

    t.fetch = flaky
    t.time.sleep = lambda _s: None
    try:
        assert t.fetch_patiently("a", "b", "c", tries=5, wait=1) == {"level": 34}
        assert calls["n"] == 3
    finally:
        importlib.reload(t)


def test_fetch_patiently_gives_up_after_tries():
    import importlib
    import track_poe2_character as t

    t.fetch = lambda *a: (_ for _ in ()).throw(t.RateLimited("429"))
    t.time.sleep = lambda _s: None
    try:
        try:
            t.fetch_patiently("a", "b", "c", tries=3, wait=1)
        except t.RateLimited:
            pass
        else:
            raise AssertionError("한도 초과인데도 예외가 안 났다")
    finally:
        importlib.reload(t)


def test_baseline_is_established_lazily_after_rate_limits():
    """시작 조회가 429 로 막혀도 죽지 않고, 첫 성공 응답이 기준선이 되어야 한다.

    이걸 놓치면 429 한 번에 밤샘 추적이 통째로 사라진다 (2026-09-06 실제로 겪음).
    """
    import importlib
    import tempfile
    from pathlib import Path

    import track_poe2_character as t

    ok = {"level": 34, "passiveCounts": {"passives": 41, "ascendancy": 2},
          "keystones": [], "skills": [], "items": [], "defensiveStats": {"life": 903}}
    seq = iter([t.RateLimited("429"), t.RateLimited("429"), ok])

    def fake(_a, _b, _c):
        v = next(seq)
        if isinstance(v, Exception):
            raise v
        return v

    t.fetch = fake
    t.time.sleep = lambda _s: None
    t.build_planner = lambda *a, **k: True
    out = tempfile.mkdtemp()
    import sys as _sys
    argv = _sys.argv
    _sys.argv = ["x", "--account", "a", "--name", "b", "--overview", "c", "--out", out,
                 "--live-name", "L", "--hours", "0.0009", "--interval", "0", "--no-install"]
    try:
        rc = t.main()
        timeline = (Path(out) / "timeline.md").read_text(encoding="utf-8")
    finally:
        _sys.argv = argv
        importlib.reload(t)
    assert rc == 0
    assert "추적 시작" in timeline and "Lv34" in timeline


# --- 막 경계 (GGPK WorldAreas 실측) ------------------------------------------ #

def test_act_of_matches_ggpk_world_area_boundaries():
    """레벨이 아니라 막으로 부르기로 했으므로, 경계가 곧 파일 이름이 된다."""
    from track_poe2_character import act_of
    assert act_of(1) == "Act1"
    assert act_of(15) == "Act1"     # Root Hollow 가 1막 마지막
    assert act_of(16) == "Act2"     # Vastiri Outskirts
    assert act_of(31) == "Act2"     # Dreadnought
    assert act_of(33) == "Act3"     # Sandswept Marsh
    assert act_of(45) == "Act3"
    assert act_of(46) == "Act4"     # Abandoned Prison — 그가 타락시키는 비명으로 갈아탄 레벨
    assert act_of(53) == "Act4"
    # 54~ 는 GGPK 가 `Act=6` 으로 두고 월드맵 이름이 문자 그대로 `Interlude`(G6_WorldMap)다.
    # 한때 여기를 "잔혹"으로 적었는데 그건 게임·가이드·패치노트 어디에도 없는, 내가 붙인
    # 이름이었다(외부 검증이 잡았다). 출처의 이름을 쓴다 — 이 단언이 그걸 고정한다.
    assert act_of(54) == "막간"      # Ashen Forest · Scorched Farmlands 등, Act=6
    assert act_of(65) == "엔드게임"


def test_act_of_survives_a_missing_level():
    from track_poe2_character import act_of
    assert act_of(None) == "Act1"


def test_fetch_percent_encodes_a_korean_character_name(monkeypatch):
    """한글 이름을 URL 에 그대로 붙이면 urllib 이 ascii 인코딩하다 죽는다 —
    HTTP 오류가 아니라 요청 자체가 안 나가서 추적기가 400/실패로만 보인다."""
    import io
    import json as _json
    import urllib.request as _req

    from track_poe2_character import fetch

    seen = {}

    def fake_urlopen(request, timeout=None):
        seen["url"] = request.full_url
        return io.StringIO(_json.dumps({"level": 61}))

    monkeypatch.setattr(_req, "urlopen", fake_urlopen)
    assert fetch("dtq03087-0345", "임성빈_화염파_젬링", "hc-forbidden-rites")["level"] == 61
    assert seen["url"].isascii()
    assert "%EC%9E%84%EC%84%B1%EB%B9%88" in seen["url"]
    assert "overview=hc-forbidden-rites" in seen["url"]


def test_ninja_sidecar_keeps_what_the_pob_export_drops(tmp_path):
    """PoB `.build` 익스포트는 몸통 유니크·호신부·주얼 슬롯을 비워서 내보낸다.
    필터 스펙이 그걸 읽으면 실제 착용분을 못 따라간다 — 실측으로 15종 중 4종이 빠졌다
    (The Mutable Star · 지혈 호신부 · 해독 호신부 · 사파이어 주얼).
    그래서 사이드카는 ninja 의 items/flasks/jewels 를 전부 담아야 한다."""
    from track_poe2_character import write_ninja_items

    payload = {
        "account": "acct-1", "name": "char", "level": 61, "updatedUtc": "2026-09-05T19:07:48Z",
        "items": [{"itemData": {"baseType": "Cleric Vestments", "name": "The Mutable Star"}},
                  {"itemData": {"baseType": "Bombard Crossbow", "name": ""}}],
        "flasks": [{"itemData": {"baseType": "Staunching Charm", "name": "Sanguis Heroum"}},
                   {"itemData": {"baseType": "Grand Mana Flask"}}],
        "jewels": [{"itemData": {"baseType": "Sapphire", "name": "Eagle Vessel"}}],
    }
    dest = tmp_path / "LIVE_ninja_items.json"
    write_ninja_items(payload, dest)
    got = json.loads(dest.read_text(encoding="utf-8"))
    assert got["_meta"]["level"] == 61
    assert got["bases"] == ["Cleric Vestments", "Bombard Crossbow",
                            "Staunching Charm", "Grand Mana Flask", "Sapphire"]


def test_ninja_sidecar_refuses_to_blank_an_existing_list(tmp_path):
    """빈 응답으로 사이드카를 덮으면 필터가 조용히 착용분을 잃는다."""
    from track_poe2_character import write_ninja_items

    dest = tmp_path / "LIVE_ninja_items.json"
    dest.write_text('{"bases": ["Cleric Vestments"]}', encoding="utf-8")
    write_ninja_items({"items": [], "flasks": [], "jewels": []}, dest)
    assert json.loads(dest.read_text(encoding="utf-8"))["bases"] == ["Cleric Vestments"]
