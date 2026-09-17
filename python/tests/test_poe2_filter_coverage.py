"""poe2_filter_coverage: 정본 장비의 '쓸모 창'을 어떻게 유도하는가.

이 게이트가 묻는 것은 "이 베이스가 쓸모 있는 순간에 내가 그때 켜 둘 필터가 띄우나" 다.
그래서 창(window)이 틀리면 게이트가 통째로 거짓말을 한다 — 창이 짧으면 구멍을 못 보고,
창이 길면 마감 지역에서 2막 몸통을 찾으라며 없는 결함을 만든다.

**픽스처 주의**: 경계값을 서로 다르게 잡는다. 후계자-1 과 탭 끝이 우연히 같은 픽스처를 쓰면
"후계자가 탭 경계를 이긴다"를 검증하지 못한다(적대검증이 이 동어반복을 짚었다).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from poe2_filter_coverage import CAMPAIGN, creator_gear, stage_end, stage_ends  # noqa: E402

INF = 10 ** 6


def slot(inventory_id: str, base: str, drop: int) -> dict:
    return {"inventory_id": inventory_id,
            "additional_text": f"{base}\n1. +12 to maximum Life",
            "level_interval": [drop, 100]}


def make_source(tmp_path: Path, tabs: dict[str, list[dict]], live_bases: list[str],
                live_level: int, past_live: dict[int, list[dict]] | None = None) -> Path:
    """탭 `.build` + 지난 실캐릭 스냅샷 + 사이드카를 갖춘 최소 소스 폴더."""
    for fname, slots in tabs.items():
        (tmp_path / fname).write_text(json.dumps({"inventory_slots": slots}, ensure_ascii=False),
                                      encoding="utf-8")
    snapshots = dict(past_live or {})
    snapshots.setdefault(live_level, [])
    for level, slots in snapshots.items():
        (tmp_path / f"LIVE Lv{level} - poe.ninja.build").write_text(
            json.dumps({"inventory_slots": slots}, ensure_ascii=False), encoding="utf-8")
    (tmp_path / "LIVE_ninja_items.json").write_text(
        json.dumps({"_meta": {"level": live_level}, "bases": live_bases}, ensure_ascii=False),
        encoding="utf-8")
    return tmp_path


def window(gear, base):
    return next((s, e) for n, s, e, _f in gear if n == base)


def test_stage_ends_are_read_from_the_campaign_structure_not_hardcoded():
    """막 경계를 스크립트에 적어 두면 다음 패치에서 조용히 어긋난다.
    정본은 GGPK WorldAreas 에서 유도한 `data/campaign_structure_poe2.json` 이다."""
    phases = {p["key"]: p for p in json.loads(CAMPAIGN.read_text(encoding="utf-8"))["phases"]}
    ends = stage_ends()
    assert ends["ACT 1"] == phases["act_1"]["level_range"][1]
    assert ends["ACT 2"] == phases["act_2"]["level_range"][1]
    # ACT 34 탭은 4막에서 끊지 않는다 — 그의 Lv61 스냅샷이 3/4막급 베이스를 그대로 낀다.
    assert ends["ACT 34"] == phases["interlude_acts"]["level_range"][1]
    assert ends["ACT 34"] > phases["act_4"]["level_range"][1]
    assert stage_end("Interludes  End Game - x.build") == INF
    assert stage_end("LIVE Lv97 - poe.ninja.build") == INF


def test_replaced_gear_closes_at_its_tab_not_at_the_live_level(tmp_path):
    """제작자가 레벨을 올린다고 2막 몸통의 수명이 같이 늘어나지 않는다.

    실측 사고: 실캐릭이 61 -> 97 로 오르자 Shaman Mantle(2막 탭, 교체됨) 창이 [28, 97] 이 되어
    마감 지역 82·97 에서 '세 단계 어디도 안 잡음' 으로 찍혔다. 마감 필터는 2막 몸통을
    일부러 안 띄운다 — 결함은 필터가 아니라 창이었다.
    """
    src = make_source(tmp_path,
                      {"ACT 2 - x.build": [slot("BodyArmour1", "Shaman Mantle", 28)]},
                      live_bases=["Cleric Vestments"], live_level=97)
    assert window(creator_gear(src), "Shaman Mantle") == (28, stage_ends()["ACT 2"])


def test_a_past_snapshot_extends_the_window_past_the_tab_boundary(tmp_path):
    """지난 스냅샷에 착용 증거가 있으면 탭 경계보다 그 증거가 우선이다.
    반례(적대검증): Lv61 실캐릭이 3/4막급 베이스를 그대로 끼고 있었다 —
    탭 끝에서 닫으면 그 구간이 검사에서 통째로 빠진다."""
    src = make_source(tmp_path,
                      {"ACT 2 - x.build": [slot("Belt1", "Plate Belt", 25)]},
                      live_bases=["Rawhide Belt"], live_level=97,
                      past_live={61: [slot("Belt1", "Plate Belt", 25)]})
    assert stage_ends()["ACT 2"] < 61  # 픽스처 전제: 증거가 탭 경계 바깥이다
    assert window(creator_gear(src), "Plate Belt") == (25, 61)


def test_the_window_never_passes_the_live_level(tmp_path):
    """마감 탭은 상한이 없지만 실캐릭 시점을 넘겨 열어 두면 안 된다 — 그가 이미 벗었다."""
    src = make_source(tmp_path,
                      {"Interludes  End Game - x.build": [slot("Amulet1", "Lunar Amulet", 30)]},
                      live_bases=["Gold Amulet"], live_level=70)
    assert window(creator_gear(src), "Lunar Amulet") == (30, 70)


def test_gear_he_still_wears_keeps_an_open_window(tmp_path):
    """지금도 끼고 있으면 자르지 않는다 — 마감에서도 띄워야 하는 것들이다."""
    src = make_source(tmp_path,
                      {"ACT 34 - x.build": [slot("BodyArmour1", "Cleric Vestments", 34)]},
                      live_bases=["Cleric Vestments"], live_level=97)
    assert window(creator_gear(src), "Cleric Vestments") == (34, INF)


def test_a_slot_replaced_inside_the_tabs_closes_at_the_successor_not_the_tab_end(tmp_path):
    """같은 슬롯의 다음 단계가 있으면 그게 우선이다 — 탭 경계로 **더** 자르면 안 된다.

    픽스처는 후계자-1(27)과 탭 끝(1막 15)이 다르게 잡았다. 같게 잡으면 이 구분이 검증되지
    않고, 후계자 창을 탭 끝까지 줄이는 변형이 테스트·게이트를 모두 통과한다(실데이터에서
    16개 창이 조용히 줄었다).
    """
    src = make_source(tmp_path,
                      {"ACT 1 - x.build": [slot("Helm1", "Horned Crown", 10)],
                       "ACT 2 - x.build": [slot("Helm1", "Martyr Crown", 28)]},
                      live_bases=["Imperial Greathelm"], live_level=97)
    gear = creator_gear(src)
    assert window(gear, "Horned Crown") == (10, 27)
    assert 27 != stage_ends()["ACT 1"]


def test_gear_that_starts_after_the_live_level_is_left_alone(tmp_path):
    """실캐릭 시점 뒤에 드롭되는 장비는 실캐릭이 말해 줄 게 없다.
    이 가드가 빠지면 드롭 80 짜리를 61 로 잘라 창이 통째로 사라진다(실사고)."""
    src = make_source(tmp_path,
                      {"ACT 2 - x.build": [slot("Helm1", "Cryptic Crown", 80)]},
                      live_bases=["Hallowed Crown"], live_level=61)
    assert window(creator_gear(src), "Cryptic Crown") == (80, INF)


def test_window_never_inverts_when_the_tab_ends_before_the_drop_level(tmp_path):
    """드롭 레벨이 탭 경계보다 높은 표기가 있어도 창이 뒤집히면 안 된다(평가 0회가 된다)."""
    src = make_source(tmp_path,
                      {"ACT 1 - x.build": [slot("Helm1", "Cryptic Crown", 40)]},
                      live_bases=["Imperial Greathelm"], live_level=97)
    start, end = window(creator_gear(src), "Cryptic Crown")
    assert start == 40 and end >= start


def test_live_only_bases_enter_with_an_open_window(tmp_path):
    """사이드카에만 있는 착용분(탭에 없는 것)은 전 구간 대상으로 들어온다."""
    src = make_source(tmp_path,
                      {"ACT 2 - x.build": [slot("BodyArmour1", "Shaman Mantle", 28)]},
                      live_bases=["Trarthan Cannon"], live_level=97)
    assert window(creator_gear(src), "Trarthan Cannon") == (1, INF)


def test_probes_never_ask_about_an_area_level_that_does_not_exist():
    """창 끝은 **캐릭터** 레벨인데 프로브는 **지역** 레벨로 던진다. 안 가르면 '지역 97' 처럼
    없는 지역에서 '안 잡힌다'가 나온다 — 존재하지 않는 결함이다(적대검증이 짚었다)."""
    from poe2_filter_coverage import max_area_level, probe_levels

    top = max_area_level()
    phases = {p["key"]: p for p in json.loads(CAMPAIGN.read_text(encoding="utf-8"))["phases"]}
    assert top == phases["endgame_maps"]["level_range"][1]
    assert max(probe_levels(30, 97)) <= top
    assert max(probe_levels(1, INF)) <= top


def test_probes_still_hit_both_edges_of_a_short_window():
    """짧은 창이 격자 사이에 끼어 평가 0회로 통과하던 사고를 고정한다."""
    from poe2_filter_coverage import probe_levels

    assert probe_levels(8, 11) and set(probe_levels(8, 11)) >= {8, 9, 11}
