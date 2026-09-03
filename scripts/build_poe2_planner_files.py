"""Generate in-game Build Planner `.build` files from a Path of Building export.

The Fartfinder planner files were downloaded from Mobalytics, which publishes them
directly. Builds that only exist as a poe.ninja PoB snapshot -- the ignite build,
for instance -- have no such download, so the file has to be produced from the PoB
XML instead.

Three mappings make that possible:

  passives  PoB stores numeric tree node ids; the planner wants the `stringId`
            field of the same node in the official tree.json ("evasion11").
  skills    The Gem/Gems path segment is NOT a rule -- the planner's own files
            mix both, for actives (7 vs 5) and for supports (19 vs 7). It is a
            per-gem fact, and the GGPK-derived data/valid_gems_poe2.json carries
            it: 179 of the 179 gems shared with known-good planner files match.
  ascendancy read out of the allocated ascendancy nodes' stringIds
            (`AscendancyRanger3Notable4` -> "Ranger3"), because PoB's ascendClassId
            and the planner's numbering do not agree.
  weapon_set PoB's <Spec> attributes carry only `nodes`, but each <Spec> body
            holds <WeaponSet1>/<WeaponSet2> node lists, so the planner's per-node
            `weapon_set` is recoverable. It is per-spec, not per-file: the ignite
            PoB leaves sets 01/02 without any weapon swap and tags 17/23/23 nodes
            in 03/04/05.

`--verify-against` regenerates a known-good Mobalytics file from its own PoB and
diffs the two. That is the only honest way to know the mappings are right: a file
the game silently refuses to load looks exactly like a correct one on disk.

Usage:
    python scripts/build_poe2_planner_files.py --pob <file.xml> --out <dir> \
        --author "Arserina" --link <url> --prefix "Ignite" [--install]
    python scripts/build_poe2_planner_files.py --verify-against "<known-good.build>" \
        --pob data/_cache/pob/fartfinder_skadoosh.xml
"""

from __future__ import annotations

import argparse
import glob
import html
import io
import json
import re
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
GAME_DIR = Path.home() / "Documents/My Games/Path of Exile 2/BuildPlanner"

# The planner's `ascendancy` string is NOT PoB's ascendClassId with a class name
# glued on: Cursemaster is PoB ascendClassId 2 -> "Sorceress2", but Fartfinder is
# also PoB 2 (Pathfinder) -> "Ranger3". The two systems order ascendancies
# differently, and there is no constant offset.
#
# The tree itself settles it. Ascendancy nodes carry stringIds shaped
# `Ascendancy<Class><N>Notable4`, and that <Class><N> is exactly what the planner
# writes. So the value is read out of the allocated nodes rather than guessed.
ASC_ID = re.compile(r"^Ascendancy([A-Za-z]+?)(\d+)(?:Notable|Small|Start|$)")

SPEC = re.compile(r"<Spec\b([^>]*)>")
ATTR = lambda name, s: (re.search(rf'{name}="([^"]*)"', s) or [None, ""])[1]  # noqa: E731


def find_tree() -> Path:
    """The official PoB-PoE2 tree.json, wherever an earlier agent cached it."""
    local = REPO / "data" / "_cache" / "tree_0_5.json"
    if local.exists():
        return local
    hits = glob.glob(
        str(Path.home() / "AppData/Local/Temp/claude/D--Pathcraft-AI/*/scratchpad/**/tree_0_5.json"),
        recursive=True,
    )
    if not hits:
        raise SystemExit(
            "tree_0_5.json 을 찾지 못했다. PathOfBuildingCommunity/PathOfBuilding-PoE2 의 "
            "src/TreeData/0_5/tree.json 을 data/_cache/tree_0_5.json 으로 받아 둘 것"
        )
    dest = REPO / "data" / "_cache" / "tree_0_5.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(hits[0], dest)
    return dest


def node_index() -> dict[int, str]:
    tree = json.loads(find_tree().read_text(encoding="utf-8"))
    out: dict[int, str] = {}
    for n in tree["nodes"].values():
        if isinstance(n, dict) and "skill" in n and "stringId" in n:
            out[n["skill"]] = n["stringId"]
    return out


def weapon_sets(body: str) -> dict[int, int]:
    """tree node id -> 1 or 2, from one <Spec> body's <WeaponSet1>/<WeaponSet2>."""
    out: dict[int, int] = {}
    for which in (1, 2):
        marker = "<WeaponSet" + str(which)
        pos = 0
        while True:
            start = body.find(marker, pos)
            if start < 0:
                break
            end = body.find(">", start)
            for x in ATTR("nodes", body[start:end]).split(","):
                if x.strip().isdigit():
                    out[int(x)] = which
            pos = end + 1
    return out


def parse_specs(xml: str) -> list[dict]:
    specs = []
    bounds = [m.start() for m in SPEC.finditer(xml)] + [len(xml)]
    for i, m in enumerate(SPEC.finditer(xml)):
        a = m.group(1)
        # The body runs to </Spec>, or to the next <Spec> for a self-closing one.
        close = xml.find("</Spec>", m.end())
        body = xml[m.end():close if 0 <= close < bounds[i + 1] else bounds[i + 1]]
        specs.append({
            # 제목 없는 <Spec> 도 흔하다(Mobalytics 내보내기). 그때는 위치를 쓴다 —
            # "?" 같은 자리표시자는 Windows 파일명으로 나갈 수 없다.
            "title": ATTR("title", a) or f"{i + 1:02d}",
            "class_id": int(ATTR("classId", a) or 0),
            "ascend_id": int(ATTR("ascendClassId", a) or 0),
            "nodes": [int(x) for x in ATTR("nodes", a).split(",") if x.strip().isdigit()],
            "wsets": weapon_sets(body),
        })
    return specs


def gem_paths() -> dict[str, str]:
    """gem name -> full Metadata path, from the GGPK-derived table."""
    raw = (REPO / "data" / "valid_gems_poe2.json").read_text(encoding="utf-8")
    return {p.rsplit("/", 1)[1]: p
            for p in set(re.findall(r"Metadata/Items/Gems?/[A-Za-z0-9_]+", raw))}


def resolve_gem(gid: str, table: dict[str, str], notes: list[str]) -> str:
    """PoB 가 적은 경로를 그대로 쓴다. GGPK 표는 덮어쓰기가 아니라 교차검증용이다.

    한때 이 함수는 표를 정본으로 삼아 PoB 를 덮었다. 두 가지가 그 전제를 무너뜨린다:

    1. `data/valid_gems_poe2.json` 의 출처는 **GGPK 0.4.0d** 다. 이 빌드는 0.5.5 라
       표에 아예 없는 젬이 나온다(VirtuousBarrier · GrenadeLauncher). 그때 표는
       정본이 아니라 그냥 낡은 것이다.
    2. 두 PoE2 PoB 의 gemId 117개 중 표와 **불일치는 0**이고 표에 없는 것만 2개였다.
       즉 표는 교정해 준 적이 한 번도 없다. 덮어쓸 이유가 없다.

    계열 다수결도 근거가 못 된다 — `SkillGemAscendancy` 45개 중 2개
    (Apocalypse · SupportingFire)가 복수형이라 계열은 균질하지 않다.
    """
    name = gid.rsplit("/", 1)[1]
    known = table.get(name)
    if known and known != gid:
        # 실제로 갈리면 조용히 고르지 않고 드러낸다. 지금까지 0건이다.
        notes.append(f"{name}: PoB={gid} vs GGPK표={known} — PoB 를 따랐다")
    elif not known:
        notes.append(f"{name}: GGPK 표({'0.4.0d'})에 없음 — PoB 경로 {gid} 사용")
    return gid


def parse_skill_sets(xml: str, table: dict[str, str], inferred: list[str]) -> list[list[dict]]:
    """One entry per <Skills> set, each a list of {id, support_skills}."""
    sets_: list[list[dict]] = []
    for block in re.findall(r"<SkillSet\b[^>]*>(.*?)</SkillSet>", xml, re.S) or [xml]:
        skills = []
        for grp in re.findall(r"<Skill\b[^>]*>(.*?)</Skill>", block, re.S):
            gems = re.findall(r'<Gem\b([^>]*)/?>', grp)
            active, supports = None, []
            for g in gems:
                gid = ATTR("gemId", g)
                if not gid:
                    continue
                if "SupportGem" in gid:
                    supports.append({"id": resolve_gem(gid, table, inferred),
                                     "level_interval": [1, 100]})
                elif active is None:
                    active = resolve_gem(gid, table, inferred)
            if active:
                entry = {"id": active, "level_interval": [1, 100]}
                # The known-good files drop the key entirely rather than writing an
                # empty list (Fartfinder's Herald of Plague has no supports).
                if supports:
                    entry["support_skills"] = supports
                skills.append(entry)
        if skills:
            sets_.append(dedupe_skills(skills))
    return sets_


def dedupe_skills(skills: list[dict]) -> list[dict]:
    """같은 액티브 젬이 두 번 나오면 서포트가 많은 쪽만 남긴다.

    PoB 는 실제로 끼운 젬 말고도 `<Skill source="Tree:1988">`(어센던시가 주는 스킬)
    과 `<Skill source="Item:72:03, Chiming Staff">`(아이템 임플리싯이 주는 스킬)를
    자동으로 만들어 둔다. 그래서 종소리 지팡이가 주는 권능의 인장이 소켓에 낀
    권능의 인장과 겹쳐 한 파일에 두 번 나왔다 — 정본 25개 중 액티브 젬이 중복된
    파일은 0개다.

    `source` 가 붙은 그룹을 통째로 버리면 안 된다. 어센던시가 주는 스킬은 정본에도
    실려 있다(EASY Sorceress 6개 파일의 ElementalStorm). 그래서 그룹을 거르는 게
    아니라 중복만 접고, 서포트가 달린 쪽(=실제로 끼운 쪽)을 남긴다.
    """
    best: dict[str, dict] = {}
    order: list[str] = []
    for s in skills:
        prev = best.get(s["id"])
        if prev is None:
            best[s["id"]] = s
            order.append(s["id"])
        elif len(s.get("support_skills", [])) > len(prev.get("support_skills", [])):
            best[s["id"]] = s
    return [best[k] for k in order]


# PoB 슬롯 이름 -> 플래너 inventory_id (다중 슬롯은 slot_x 로 자리를 나눈다).
#
# 앵커는 추측이 아니라 실측이다: Fartfinder PoB 의 "Weapon 1 Swap" 에 있는 유니크
# Trenchtimbre 가 정본 .build 의 "Weapon2" 에 그대로 있다. 즉 Swap = 두 번째 무기
# 세트다. 세트 안의 Weapon 1/2 는 주무기/보조무기이므로 나머지 셋은 그 앵커와
# 모순 없는 유일한 배치다. Boots1(Corpsewade)·Belt1(Darkness Enthroned)도 같은
# 방식으로 확인했다. PoB 의 Ring 3 / Leg / Arm 은 플래너에 대응 슬롯이 없어 버린다.
SLOT_MAP = {
    "Weapon 1": ("Weapon1", 0), "Weapon 2": ("Offhand1", 0),
    "Weapon 1 Swap": ("Weapon2", 0), "Weapon 2 Swap": ("Offhand2", 0),
    "Helmet": ("Helm1", 0), "Body Armour": ("BodyArmour1", 0),
    "Gloves": ("Gloves1", 0), "Boots": ("Boots1", 0),
    "Amulet": ("Amulet1", 0), "Belt": ("Belt1", 0),
    "Ring 1": ("Ring1", 0), "Ring 2": ("Ring2", 0),
    "Charm 1": ("Charm1", 0), "Charm 2": ("Charm1", 1), "Charm 3": ("Charm1", 2),
    "Flask 1": ("Flask1", 0), "Flask 2": ("Flask1", 1),
}
TAG = re.compile(r"\{[^}]*\}")
RANGE_TAG = re.compile(r"\{range:([0-9.]+)\}")
SPAN = re.compile(r"\((\d+(?:\.\d+)?)-(\d+(?:\.\d+)?)\)")


def roll(line: str) -> str:
    """PoB 의 `{range:X}` 를 적용해 `(15-25)%` 같은 미확정 표기를 실제 값으로 만든다.

    PoB 는 굴림값을 모드 문구가 아니라 앞의 `{range:X}` 태그(그리고 `<ModRange>`)에
    따로 둔다. 태그만 떼고 문구를 그대로 쓰면 `(15-25)%` 가 그대로 나가는데, 정본
    25개에서 그런 표기는 **0건**이다. 실제 아이템은 굴려진 값 하나를 보여준다.
    """
    got = RANGE_TAG.search(line)
    frac = float(got.group(1)) if got else 0.5
    def one(m: re.Match) -> str:
        lo, hi = float(m.group(1)), float(m.group(2))
        val = lo + frac * (hi - lo)
        decimals = "." in m.group(1) or "." in m.group(2)
        return f"{val:.1f}" if decimals else str(int(round(val)))
    return SPAN.sub(one, line)
NOISE = ("Prefix:", "Suffix:", "Crafted:", "Quality:", "Sockets:", "Rune:", "LevelReq:",
         "Unique ID:", "Item Level:", "Note:", "Implicits:", "Requires", "Corrupted",
         "Enchant:", "Selected Variant:", "Has Alt Variant:", "League:", "Source:")


def base_names() -> list[str]:
    """긴 것부터 정렬한 베이스 이름 — 매직 아이템 이름에서 베이스를 떼는 데 쓴다."""
    d = json.loads((REPO / "data" / "base_items_poe2.json").read_text(encoding="utf-8"))
    names: set[str] = set()
    for key in ("weapons", "armours", "other"):
        section = d.get(key) or {}
        for group in (section.values() if isinstance(section, dict) else section):
            for it in (group if isinstance(group, list) else [group]):
                if isinstance(it, dict) and it.get("name"):
                    names.add(it["name"])
                elif isinstance(it, str):
                    names.add(it)
    return sorted(names, key=len, reverse=True)


def parse_items(xml: str) -> dict[str, dict]:
    """PoB item id -> {rarity, name, base, mods}."""
    out: dict[str, dict] = {}
    for m in re.finditer(r"<Item\b([^>]*)>(.*?)</Item>", xml, re.S):
        got = re.search(r'id="(\d+)"', m.group(1))
        if not got:
            continue
        body = html.unescape(m.group(2))
        lines = [ln.strip() for ln in body.splitlines() if ln.strip()]
        rarity = next((ln.split(":", 1)[1].strip() for ln in lines
                       if ln.startswith("Rarity:")), "")
        rest = [ln for ln in lines if not ln.startswith("Rarity:")]
        # Implicits: N 뒤의 N줄은 임플리싯, 그 뒤가 익스플리싯이다. <ModRange> 는
        # 바로 앞 모드에 딸린 XML 이라 줄 수에 세면 안 된다.
        implicits = next((int(ln.split(":", 1)[1]) for ln in rest
                          if ln.startswith("Implicits:")), None)
        mods: list[str] = []
        if implicits is not None:
            after = rest[rest.index(next(ln for ln in rest if ln.startswith("Implicits:"))) + 1:]
            after = [ln for ln in after
                     if not ln.startswith("<") and not ln.startswith(NOISE)]
            mods = [TAG.sub("", roll(ln)).strip() for ln in after[implicits:]]
            mods = [x for x in mods if x]
        out[got.group(1)] = {
            "rarity": rarity,
            "name": rest[0] if rest else "",
            "base": rest[1] if len(rest) > 1 else "",
            "mods": mods,
        }
    return out


def inventory_slots(body: str, items: dict[str, dict], bases: list[str],
                    skipped: list[str]) -> list[dict]:
    """하나의 <ItemSet> 을 플래너의 inventory_slots 배열로 옮긴다."""
    out = []
    for s in re.finditer(r"<Slot\b([^>]*?)/>", body):
        a = s.group(1)
        name = (re.search(r'name="([^"]*)"', a) or [None, ""])[1]
        item_id = (re.search(r'itemId="(\d+)"', a) or [None, "0"])[1]
        if item_id == "0":
            continue
        if name not in SLOT_MAP:
            skipped.append(name)
            continue
        inv, slot_x = SLOT_MAP[name]
        it = items.get(item_id)
        if not it:
            continue
        if it["rarity"].upper() == "UNIQUE":
            out.append({"inventory_id": inv, "slot_x": slot_x, "slot_y": 0,
                        "unique_name": it["name"]})
            continue
        # 레어는 2번째 줄이 베이스다. 매직은 접두/접미가 붙은 한 줄뿐이라
        # 베이스 표에서 가장 긴 부분일치를 떼어 낸다.
        base = it["base"]
        if it["rarity"].upper() == "MAGIC" or not base or base.startswith("Unique ID:"):
            base = next((b for b in bases if b in it["name"]), it["name"])
        text = base
        if it["mods"]:
            text += "\n" + "\n".join(f"{i}. {m}" for i, m in enumerate(it["mods"], 1))
        out.append({"additional_text": text, "inventory_id": inv,
                    "level_interval": [1, 100], "slot_x": slot_x, "slot_y": 0})
    # 정본 파일들은 무기 -> 방어구 -> 장신구 -> 참 순으로 적는다. 순서를 맞춰 둔다.
    order = ["Weapon1", "Weapon2", "Offhand1", "Offhand2", "Helm1", "BodyArmour1",
             "Gloves1", "Boots1", "Amulet1", "Belt1", "Ring1", "Ring2", "Flask1", "Charm1"]
    return sorted(out, key=lambda e: (order.index(e["inventory_id"])
                                      if e["inventory_id"] in order else 99, e["slot_x"]))


def spec_ascendancy(spec: dict, idx: dict[int, str]) -> str:
    """할당된 어센던시 노드의 stringId 에서 플래너 번호를 읽는다 (없으면 빈 문자열)."""
    for n in spec["nodes"]:
        m = ASC_ID.match(idx.get(n, ""))
        if m:
            return m.group(1) + m.group(2)
    return ""


def resolve_ascendancies(specs: list[dict], idx: dict[int, str]) -> list[str]:
    """어센던시 노드가 아직 없는 초반 세트는 뒤 세트의 값을 물려받는다.

    정본 25개 중 `ascendancy` 가 빈 문자열인 파일은 **0개**다. 어센던시 노드를
    하나도 안 찍은 파일조차 값을 적는다 — ED Contagion 의 ACT 1/2 는 어센던시
    노드 0개인데 `Witch3` 이다. 스키마에 클래스 필드가 따로 없으니 이 값이 유일한
    클래스 선언이고, 비우면 트리를 어느 클래스로 그릴지가 사라진다.

    그래서 값을 지어내지 않고 **같은 빌드의 다음 단계에서 가져온다**. 점화는 액트
    구간이 택티션(Mercenary1)이고 52레벨에 젬링(Mercenary3)으로 갈아타므로,
    1단계는 바로 다음 단계인 Mercenary1 을 물려받는 것이 맞다.
    """
    got = [spec_ascendancy(s, idx) for s in specs]
    for i in range(len(got) - 1, -1, -1):
        if not got[i] and i + 1 < len(got):
            got[i] = got[i + 1]
    return got


def build_file(spec: dict, skills: list[dict], idx: dict[int, str],
               author: str, link: str, name: str, inv: list[dict], asc: str) -> dict:
    unknown = [n for n in spec["nodes"] if n not in idx]
    if unknown:
        raise SystemExit(f"{spec['title']}: 트리에서 해석 못 한 노드 {len(unknown)}개 {unknown[:6]}")
    if not asc:
        raise SystemExit(
            f"{spec['title']}: 어센던시 문자열을 데이터로 확정하지 못했다. 정본 25개는 "
            "전부 값이 있으므로 빈 문자열을 내보내지 않는다"
        )
    return {
        "author": author,
        "link": link,
        "ascendancy": asc,
        "inventory_slots": inv,
        "name": name[:40],
        "passives": [
            {"id": idx[n], "weapon_set": spec["wsets"][n]} if n in spec["wsets"]
            else {"id": idx[n]}
            for n in spec["nodes"]
        ],
        "skills": skills,
    }


def verify(known_good: Path, pob: Path) -> int:
    """Reproduce a Mobalytics-published file from its own PoB and diff."""
    truth = json.loads(known_good.read_text(encoding="utf-8"))
    xml = pob.read_text(encoding="utf-8")
    idx = node_index()
    specs = parse_specs(xml)

    want = {p["id"] for p in truth["passives"]}
    best, score = None, -1
    for s in specs:
        got = {idx[n] for n in s["nodes"] if n in idx}
        overlap = len(want & got)
        if overlap > score:
            best, score = s, overlap
    got = {idx[n] for n in best["nodes"] if n in idx}
    print(f"  기준 파일: {known_good.name}  패시브 {len(want)}개")
    print(f"  가장 가까운 PoB 세트: '{best['title']}'  노드 {len(best['nodes'])}개")
    print(f"  일치 {len(want & got)} · 기준에만 {len(want - got)} · PoB에만 {len(got - want)}")
    if want - got:
        print(f"    기준에만: {sorted(want - got)[:8]}")
    if got - want:
        print(f"    PoB에만 : {sorted(got - want)[:8]}")
    gen_asc = spec_ascendancy(best, idx)
    print(f"  ascendancy: 기준 '{truth['ascendancy']}' vs 생성 '{gen_asc}' "
          f"-> {'일치' if gen_asc == truth['ascendancy'] else '불일치'}")

    # weapon_set: 겹치는 노드에 한해 우리가 도출한 값이 기준과 같은가.
    truth_ws = {p["id"]: p["weapon_set"] for p in truth["passives"] if "weapon_set" in p}
    gen_ws = {idx[n]: w for n, w in best["wsets"].items() if n in idx}
    shared_ws = truth_ws.keys() & gen_ws.keys()
    ws_bad = sorted(k for k in shared_ws if truth_ws[k] != gen_ws[k])
    print(f"  weapon_set: 기준 {len(truth_ws)} · 생성 {len(gen_ws)} · "
          f"공통 {len(shared_ws)} · 값 불일치 {len(ws_bad)}")
    if truth_ws.keys() - gen_ws.keys():
        print(f"    기준에만 태그: {sorted(truth_ws.keys() - gen_ws.keys())[:6]}")
    if gen_ws.keys() - truth_ws.keys():
        print(f"    생성에만 태그: {sorted(gen_ws.keys() - truth_ws.keys())[:6]}")
    if ws_bad:
        print(f"    값 다름: {[(k, truth_ws[k], gen_ws[k]) for k in ws_bad[:6]]}")

    # 젬 경로: 정본이 적은 경로와 PoB 가 적은 경로가 같은가. (우리는 PoB 를 그대로
    # 쓰므로, 이 대조가 곧 우리 출력의 대조다.)
    truth_gems, pob_gems = {}, {}
    for s in truth["skills"]:
        for g in [s["id"]] + [x["id"] for x in s.get("support_skills", [])]:
            truth_gems[g.rsplit("/", 1)[1]] = g
    for g in set(re.findall(r'gemId="([^"]+)"', xml)):
        pob_gems[g.rsplit("/", 1)[1]] = g
    shared = truth_gems.keys() & pob_gems.keys()
    gem_bad = sorted(k for k in shared if truth_gems[k] != pob_gems[k])
    print(f"  젬 경로: 정본 {len(truth_gems)} · PoB {len(pob_gems)} · 공통 {len(shared)} · "
          f"경로 불일치 {len(gem_bad)}")
    for k in gem_bad[:6]:
        print(f"    {k}: 정본 {truth_gems[k]} vs PoB {pob_gems[k]}")

    # 정본에서 액티브 젬이 중복된 적이 있는가 (우리 dedupe 가 정당한지의 근거).
    dup = len(truth["skills"]) - len({s["id"] for s in truth["skills"]})
    print(f"  정본의 액티브 젬 중복: {dup}건")
    empty_supports = [s["id"] for s in truth["skills"] if "support_skills" not in s]
    print(f"  support_skills 키 자체가 없는 스킬: {len(empty_supports)} "
          f"{[e.rsplit('/', 1)[1] for e in empty_supports[:3]]}")

    # 노드 집합이 정확히 같기를 요구하지 않는다: Mobalytics 파일은 같은 빌드의 다른
    # 저작이라 스냅샷이 어긋난다. 검증 대상은 세 매핑 — 어센던시 문자열 · weapon_set
    # 값 · 젬 경로 — 이고, 셋 다 "기준 파일에도 있는 항목"에 한해 비교한다.
    unresolved = [n for n in best["nodes"] if n not in idx]
    declared = ATTR("treeVersion", SPEC.search(xml).group(1)) or "(선언 없음)"
    print(f"  PoB 노드 해석: {len(best['nodes']) - len(unresolved)}/{len(best['nodes'])}"
          f"  (기준 PoB treeVersion={declared}, 로드한 트리=tree_0_5.json)")
    if unresolved:
        # 매핑 실패가 아니라 트리 버전 차이다. 우리가 실제로 쓰는 파일에서는
        # build_file 이 미해석 노드를 만나면 그대로 중단하므로 조용히 새지 않는다.
        print(f"    ! 트리에 없는 노드 {unresolved} — 기준 PoB 가 다른 트리 버전이면 "
              "정상이다. 우리가 생성하는 빌드에서 나오면 build_file 이 중단시킨다")
    ok = gen_asc == truth["ascendancy"] and not ws_bad and not gem_bad
    print(f"  판정: {'PASS' if ok else 'FAIL'}  (어센던시·weapon_set·젬 경로 3개 매핑)")
    return 0 if ok else 1


def main() -> int:
    # 이 스크립트는 한국어로 보고한다. Windows 기본 콘솔은 cp949 라 em dash 하나에
    # UnicodeEncodeError 로 죽는다 — 파일은 이미 다 쓴 뒤라 더 헷갈린다.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    ap = argparse.ArgumentParser()
    ap.add_argument("--pob", required=True)
    ap.add_argument("--out")
    ap.add_argument("--author", default="")
    ap.add_argument("--link", default="")
    ap.add_argument("--prefix", default="Build")
    # PoB 의 <Spec title> 은 "01", "03 Swap" 같은 작업용 라벨이라 인게임 플래너
    # 목록에서 쓸모가 없다. 세트 수만큼 이름을 직접 준다(쉼표 구분).
    ap.add_argument("--names", default="")
    ap.add_argument("--install", action="store_true")
    ap.add_argument("--verify-against")
    args = ap.parse_args()

    pob = Path(args.pob)
    if args.verify_against:
        return verify(Path(args.verify_against), pob)

    xml = pob.read_text(encoding="utf-8")
    idx = node_index()
    specs = parse_specs(xml)
    inferred: list[str] = []
    skill_sets = parse_skill_sets(xml, gem_paths(), inferred)
    ascendancies = resolve_ascendancies(specs, idx)
    items, bases, skipped = parse_items(xml), base_names(), []
    item_sets = [m.group(2) for m in re.finditer(r"<ItemSet\b([^>]*)>(.*?)</ItemSet>", xml, re.S)]
    out_dir = Path(args.out or (REPO / "build_planner"))
    out_dir.mkdir(parents=True, exist_ok=True)

    written = []
    for i, spec in enumerate(specs):
        skills = skill_sets[i] if i < len(skill_sets) else (skill_sets[-1] if skill_sets else [])
        names = [n.strip() for n in args.names.split(",") if n.strip()]
        if names and len(names) != len(specs):
            raise SystemExit(f"--names 는 {len(specs)}개여야 한다 (받은 것 {len(names)}개)")
        name = names[i] if names else f"{args.prefix} {spec['title']}"
        body = item_sets[i] if i < len(item_sets) else (item_sets[-1] if item_sets else "")
        inv = inventory_slots(body, items, bases, skipped) if body else []
        data = build_file(spec, skills, idx, args.author, args.link, name, inv,
                          ascendancies[i])
        stem = f"{name} - {args.author or 'build'}"
        path = out_dir / (re.sub(r'[<>:"/\\|?*]', "_", stem) + ".build")
        # 정본 25개는 전부 개행 없는 minify 형식이다. 파서는 둘 다 받겠지만
        # 게임이 읽는 파일에서 굳이 정본과 다른 모양을 만들 이유가 없다.
        path.write_bytes(json.dumps(data, ensure_ascii=False,
                                    separators=(",", ":")).encode("utf-8"))
        written.append(path)
        tagged = sum(1 for p in data["passives"] if "weapon_set" in p)
        print(f"  {path.name}: 패시브 {len(data['passives'])}"
              f"(무기세트 태그 {tagged}) · 스킬 {len(data['skills'])} · "
              f"장비 {len(data['inventory_slots'])} · "
              f"{data['ascendancy'] or '어센던시 없음'}")

    if skipped:
        print(f"\n  플래너에 대응 슬롯이 없어 버린 PoB 슬롯: {sorted(set(skipped))}")
    if inferred:
        print("\n  GGPK 표와 대조하지 못한 젬 (PoB 경로를 그대로 썼다):")
        for note in sorted(set(inferred)):
            print(f"    ~ {note}")

    if args.install:
        GAME_DIR.mkdir(parents=True, exist_ok=True)
        for p in written:
            shutil.copy2(p, GAME_DIR / p.name)
        print(f"  설치 -> {GAME_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
