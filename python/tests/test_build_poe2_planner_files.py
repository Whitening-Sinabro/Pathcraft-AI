"""Tests for the in-game Build Planner file generator.

Every test here pins a fact that was learned by diffing a generated file against
a planner file the game already reads. They exist because each of these was
wrong at some point and the wrongness was invisible on disk -- a `.build` the
game silently refuses to load looks exactly like a correct one.
"""

from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "build_poe2_planner_files.py"
IGNITE_POB = REPO / "data" / "_cache" / "pob" / "arserina_gemling_ignite_055.xml"
FART_POB = REPO / "data" / "_cache" / "pob" / "fartfinder_skadoosh.xml"


def _load():
    spec = importlib.util.spec_from_file_location("planner_gen", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


gen = _load()

needs_ignite = pytest.mark.skipif(not IGNITE_POB.exists(), reason="점화 PoB 캐시 없음")
needs_fart = pytest.mark.skipif(not FART_POB.exists(), reason="Fartfinder PoB 캐시 없음")


@pytest.fixture(scope="module")
def ignite_xml() -> str:
    return IGNITE_POB.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def gem_table() -> dict[str, str]:
    return gen.gem_paths()


class TestWeaponSet:
    """`weapon_set` 은 스펙마다 따로다 — 파일 전체로 합치면 안 된다."""

    @needs_ignite
    def test_tags_are_per_spec_not_global(self, ignite_xml):
        # PoB 원문: 01/02 는 무기 교체가 없고 03 은 17+17, 04·05 는 23+23 이다.
        # 전역으로 합쳐 파싱하면 01·02 에도 46개가 붙어 이 단언이 깨진다.
        counts = [len(s["wsets"]) for s in gen.parse_specs(ignite_xml)]
        assert counts == [0, 0, 34, 46, 46]

    @needs_ignite
    def test_values_are_only_1_or_2(self, ignite_xml):
        for s in gen.parse_specs(ignite_xml):
            assert set(s["wsets"].values()) <= {1, 2}

    @needs_ignite
    def test_tagged_nodes_are_a_subset_of_allocated_nodes(self, ignite_xml):
        # 배분하지 않은 노드에 무기 세트를 붙이면 플래너가 읽을 수 없다.
        for s in gen.parse_specs(ignite_xml):
            assert set(s["wsets"]) <= set(s["nodes"]), s["title"]

    def test_spec_body_without_weaponset_yields_nothing(self):
        assert gen.weapon_sets('<Spec nodes="1,2,3"></Spec>') == {}

    def test_both_sets_are_read(self):
        body = '<WeaponSet1 nodes="10,11"/><WeaponSet2 nodes="20,21"/>'
        assert gen.weapon_sets(body) == {10: 1, 11: 1, 20: 2, 21: 2}


class TestGemPaths:
    """PoB 가 적은 경로가 정본이고, GGPK 표는 교차검증용이다.

    이 클래스는 한 번 반대로 쓰여 있었다. 표를 정본으로 삼아 PoB 의 복수형을
    단수형으로 덮었고, 테스트가 그 잘못된 동작을 고정하고 있었다.
    """

    def test_pob_path_is_kept_verbatim(self, gem_table):
        name, path = next(iter(gem_table.items()))
        notes: list[str] = []
        assert gen.resolve_gem(path, gem_table, notes) == path
        assert notes == []

    def test_table_disagreement_is_reported_not_silently_applied(self, gem_table):
        name, path = next(iter(gem_table.items()))
        other = ("Metadata/Items/Gems/" if "/Gem/" in path else "Metadata/Items/Gem/") + name
        notes: list[str] = []
        assert gen.resolve_gem(other, gem_table, notes) == other  # PoB 를 따른다
        assert len(notes) == 1 and "PoB 를 따랐다" in notes[0]

    def test_gem_missing_from_the_stale_table_keeps_pobs_plural_form(self, gem_table):
        # 표의 출처는 GGPK 0.4.0d 라 0.5.5 젬이 빠져 있다. 그때 표는 정본이 아니다.
        notes: list[str] = []
        src = "Metadata/Items/Gems/SkillGemAscendancyVirtuousBarrier"
        assert src.rsplit("/", 1)[1] not in gem_table
        assert gen.resolve_gem(src, gem_table, notes) == src
        assert len(notes) == 1

    @needs_ignite
    def test_pob_and_the_ggpk_table_never_disagree(self, ignite_xml, gem_table):
        # 표가 교정해 준 적이 한 번도 없다는 사실이 "PoB 를 따른다"의 근거다.
        # 이게 깨지면 어느 쪽이 맞는지 사람이 판단해야 한다.
        for gid in set(re.findall(r'gemId="([^"]+)"', ignite_xml)):
            known = gem_table.get(gid.rsplit("/", 1)[1])
            assert known in (None, gid), gid

    @needs_ignite
    def test_only_two_gems_are_missing_from_the_table(self, ignite_xml, gem_table):
        # 이 집합이 커지면 표가 더 낡았다는 뜻이다. 조용히 늘게 두지 않는다.
        notes: list[str] = []
        gen.parse_skill_sets(ignite_xml, gem_table, notes)
        assert {n.split(":")[0] for n in notes} == {
            "SkillGemAscendancyVirtuousBarrier",
            "SkillGemPlayerDefaultGrenadeLauncher",
        }

    @needs_ignite
    def test_emitted_paths_match_pob_exactly(self, ignite_xml, gem_table):
        pob = {g.rsplit("/", 1)[1]: g for g in re.findall(r'gemId="([^"]+)"', ignite_xml)}
        for skills in gen.parse_skill_sets(ignite_xml, gem_table, []):
            for s in skills:
                for gid in [s["id"]] + [x["id"] for x in s.get("support_skills", [])]:
                    assert pob[gid.rsplit("/", 1)[1]] == gid

    @needs_ignite
    def test_every_emitted_path_is_a_gem_metadata_path(self, ignite_xml, gem_table):
        for skills in gen.parse_skill_sets(ignite_xml, gem_table, []):
            for s in skills:
                for gid in [s["id"]] + [x["id"] for x in s.get("support_skills", [])]:
                    assert re.fullmatch(r"Metadata/Items/Gems?/[A-Za-z0-9_]+", gid), gid


class TestSkillShape:
    @needs_ignite
    def test_empty_support_skills_key_is_dropped(self, ignite_xml, gem_table):
        # 정본 파일은 서포트가 없으면 빈 리스트가 아니라 키 자체를 안 쓴다.
        for skills in gen.parse_skill_sets(ignite_xml, gem_table, []):
            for s in skills:
                assert s.get("support_skills") != []

    @needs_ignite
    def test_some_skill_actually_has_no_supports(self, ignite_xml, gem_table):
        # 위 단언이 "서포트 없는 스킬이 하나도 없어서" 통과하는 것을 막는다.
        sets_ = gen.parse_skill_sets(ignite_xml, gem_table, [])
        assert any("support_skills" not in s for skills in sets_ for s in skills)

    @needs_ignite
    def test_level_interval_is_always_a_two_int_list(self, ignite_xml, gem_table):
        for skills in gen.parse_skill_sets(ignite_xml, gem_table, []):
            for s in skills:
                for entry in [s] + s.get("support_skills", []):
                    assert entry["level_interval"] == [1, 100]

    @needs_ignite
    def test_no_active_gem_appears_twice_in_a_set(self, ignite_xml, gem_table):
        # PoB 는 어센던시/아이템이 주는 스킬을 별도 <Skill> 로 자동 생성한다.
        # 그대로 옮기면 종소리 지팡이가 주는 권능의 인장이 소켓의 것과 겹친다.
        # 정본 25개 중 액티브 젬이 중복된 파일은 0개다.
        for skills in gen.parse_skill_sets(ignite_xml, gem_table, []):
            ids = [s["id"] for s in skills]
            assert len(ids) == len(set(ids)), ids

    def test_dedupe_keeps_the_socketed_copy_not_the_granted_one(self):
        granted = {"id": "g/Sigil", "level_interval": [1, 100]}
        socketed = {"id": "g/Sigil", "level_interval": [1, 100],
                    "support_skills": [{"id": "s/A"}, {"id": "s/B"}]}
        assert gen.dedupe_skills([granted, socketed]) == [socketed]
        assert gen.dedupe_skills([socketed, granted]) == [socketed]

    def test_dedupe_preserves_order_of_distinct_skills(self):
        a = {"id": "g/A"}, {"id": "g/B"}, {"id": "g/C"}
        assert [s["id"] for s in gen.dedupe_skills(list(a))] == ["g/A", "g/B", "g/C"]


class TestItems:
    @needs_ignite
    def test_mods_carry_no_pob_markup(self, ignite_xml):
        banned = ("{range:", "{enchant}", "{rune}", "{variant:", "{crafted}", "<ModRange")
        for item in gen.parse_items(ignite_xml).values():
            for m in item["mods"]:
                assert m, "빈 모드 줄"
                for b in banned:
                    assert b not in m, f"{b} 누출: {m}"
                assert not m.startswith(("Prefix:", "Suffix:", "Unique ID:", "Implicits:"))

    @needs_ignite
    def test_unrolled_ranges_never_reach_the_output(self, ignite_xml):
        # 정본 25개에 `(15-25)%` 같은 미확정 표기는 0건이다. 실제 아이템은
        # 굴려진 값 하나를 보여준다.
        span = re.compile(r"\(\d+(?:\.\d+)?-\d+(?:\.\d+)?\)")
        for item in gen.parse_items(ignite_xml).values():
            for m in item["mods"]:
                assert not span.search(m), m

    def test_roll_applies_the_range_tag(self):
        assert gen.roll("{range:0.5}Grenades have (15-25)% chance") == \
            "{range:0.5}Grenades have 20% chance"
        assert gen.roll("{range:1}Adds (10-20) damage") == "{range:1}Adds 20 damage"
        assert gen.roll("{range:0}Adds (10-20) damage") == "{range:0}Adds 10 damage"
        # 태그가 없으면 중앙값. 소수 범위는 소수로 남긴다.
        assert gen.roll("Adds (1.5-2.5) damage") == "Adds 2.0 damage"

    @needs_ignite
    def test_implicit_lines_are_excluded_from_mods(self, ignite_xml):
        # 임플리싯을 익스플리싯으로 세면 룬 문구가 아이템 요구사항처럼 보인다.
        items = gen.parse_items(ignite_xml)
        assert not any("Bonded" in m for it in items.values() for m in it["mods"])

    @needs_ignite
    def test_uniques_emit_unique_name_and_nothing_else(self, ignite_xml):
        sets_ = re.findall(r"<ItemSet\b([^>]*)>(.*?)</ItemSet>", ignite_xml, re.S)
        items, bases = gen.parse_items(ignite_xml), gen.base_names()
        rows = gen.inventory_slots(sets_[-1][1], items, bases, [])
        uniques = [r for r in rows if "unique_name" in r]
        assert uniques, "엔드게임 세트에 유니크가 하나도 없을 리 없다"
        for r in uniques:
            assert set(r) == {"inventory_id", "slot_x", "slot_y", "unique_name"}
            assert r["unique_name"] and "\n" not in r["unique_name"]

    @needs_ignite
    def test_non_uniques_carry_base_and_numbered_mods(self, ignite_xml):
        sets_ = re.findall(r"<ItemSet\b([^>]*)>(.*?)</ItemSet>", ignite_xml, re.S)
        items, bases = gen.parse_items(ignite_xml), gen.base_names()
        rows = gen.inventory_slots(sets_[-1][1], items, bases, [])
        rares = [r for r in rows if "additional_text" in r]
        assert rares
        for r in rares:
            assert set(r) == {"additional_text", "inventory_id", "level_interval",
                              "slot_x", "slot_y"}
            lines = r["additional_text"].splitlines()
            assert lines[0].strip(), "첫 줄은 베이스 이름"
            for i, ln in enumerate(lines[1:], 1):
                assert ln.startswith(f"{i}. "), ln

    @needs_ignite
    def test_charm_and_flask_slots_get_distinct_positions(self, ignite_xml):
        sets_ = re.findall(r"<ItemSet\b([^>]*)>(.*?)</ItemSet>", ignite_xml, re.S)
        items, bases = gen.parse_items(ignite_xml), gen.base_names()
        rows = gen.inventory_slots(sets_[-1][1], items, bases, [])
        seen = [(r["inventory_id"], r["slot_x"]) for r in rows]
        assert len(seen) == len(set(seen)), f"슬롯 충돌: {seen}"

    def test_unmapped_pob_slot_is_reported_not_silently_dropped(self):
        skipped: list[str] = []
        body = '<Slot itemId="1" name="Ring 3"/>'
        assert gen.inventory_slots(body, {"1": {}}, [], skipped) == []
        assert skipped == ["Ring 3"]


class TestBuildFile:
    @needs_ignite
    def test_unresolvable_node_aborts_rather_than_dropping(self, ignite_xml):
        spec = dict(gen.parse_specs(ignite_xml)[0])
        spec["nodes"] = spec["nodes"] + [999999999]
        with pytest.raises(SystemExit):
            gen.build_file(spec, [], gen.node_index(), "a", "l", "n", [], "Mercenary1")

    @needs_ignite
    def test_ascendancy_comes_from_allocated_nodes(self, ignite_xml):
        idx = gen.node_index()
        got = [gen.spec_ascendancy(s, idx) for s in gen.parse_specs(ignite_xml)]
        # 01 은 어센던시 이전, 02 는 Tactician, 03 이후는 Gemling Legionnaire 다.
        assert got == ["", "Mercenary1", "Mercenary3", "Mercenary3", "Mercenary3"]

    @needs_ignite
    def test_early_set_inherits_the_next_sets_ascendancy(self, ignite_xml):
        # 정본 25개 중 ascendancy 가 빈 문자열인 파일은 0개다. 어센던시 노드가
        # 0개인 정본(ED Contagion ACT 1/2)조차 값을 적는다.
        idx = gen.node_index()
        got = gen.resolve_ascendancies(gen.parse_specs(ignite_xml), idx)
        assert got == ["Mercenary1", "Mercenary1", "Mercenary3", "Mercenary3", "Mercenary3"]
        assert "" not in got

    def test_empty_ascendancy_is_refused_rather_than_written(self):
        with pytest.raises(SystemExit):
            gen.build_file({"title": "x", "nodes": [], "wsets": {}}, [], {},
                           "a", "l", "n", [], "")

    @needs_ignite
    def test_weapon_set_lands_on_the_right_passives(self, ignite_xml):
        idx = gen.node_index()
        spec = gen.parse_specs(ignite_xml)[2]
        data = gen.build_file(spec, [], idx, "a", "l", "n", [], "Mercenary3")
        tagged = {p["id"]: p["weapon_set"] for p in data["passives"] if "weapon_set" in p}
        assert tagged == {idx[n]: w for n, w in spec["wsets"].items()}

    def test_untitled_spec_gets_a_positional_title(self):
        # 제목 없는 <Spec> 이 "?" 가 되면 Windows 파일명으로 나갈 수 없다.
        specs = gen.parse_specs('<Spec nodes="1"></Spec><Spec nodes="2"></Spec>')
        assert [s["title"] for s in specs] == ["01", "02"]
        assert not any(c in s["title"] for s in specs for c in '<>:"/\\|?*')


class TestAgainstKnownGoodFile:
    """게임이 실제로 읽는 Mobalytics 파일로 매핑을 되짚는다."""

    @needs_fart
    def test_fartfinder_mappings_reproduce(self):
        truth = Path.home() / (
            "Documents/My Games/Path of Exile 2/BuildPlanner/"
            "Fartfinder 2 Endgame - Skadoosh.build"
        )
        if not truth.exists():
            pytest.skip("Fartfinder 정본 파일이 이 기기에 없음")
        data = json.loads(truth.read_text(encoding="utf-8"))
        xml = FART_POB.read_text(encoding="utf-8")
        idx = gen.node_index()
        spec = gen.parse_specs(xml)[0]

        asc = next(m.group(1) + m.group(2) for m in
                   filter(None, (gen.ASC_ID.match(idx[n]) for n in spec["nodes"] if n in idx)))
        assert asc == data["ascendancy"]

        truth_ws = {p["id"]: p["weapon_set"] for p in data["passives"] if "weapon_set" in p}
        ours = {idx[n]: w for n, w in spec["wsets"].items() if n in idx}
        shared = truth_ws.keys() & ours.keys()
        assert shared, "겹치는 태그가 없으면 비교 자체가 무의미하다"
        assert {k: ours[k] for k in shared} == {k: truth_ws[k] for k in shared}

        table = gen.gem_paths()
        for s in data["skills"]:
            for gid in [s["id"]] + [x["id"] for x in s.get("support_skills", [])]:
                assert gen.resolve_gem(gid, table, []) == gid, gid
