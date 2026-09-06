"""Bring a third-party `.build` file into `build_planner/` and the game folder.

Two kinds of source exist and neither is ready to install as-is:

  Mobalytics download  the creator's original (author/link already filled in).
                       Correct by construction (the game loads it), but the `name`
                       is truncated to 40 characters mid-word ("Skadoosh's Warrior
                       Leveli"), so the in-game list is unreadable. Only the name
                       changes; passives/skills/inventory must stay deep-equal.
  poe.ninja export     the "Build Planner" dialog on a character page. Carries
                       passives (with weapon_set) and skills, but no
                       `level_interval` on skills or supports, no `inventory_slots`,
                       no link. Every creator original has `level_interval` on every
                       skill AND every support, and omits `support_skills` when
                       empty (status/poe2_guides.md), so the export is normalised
                       to that shape before it is trusted.

Both are validated against the same ground truth the generator uses
(scripts/build_poe2_planner_files.py): passive ids must be `stringId`s of the
official tree.json, and gem ids must be the GGPK-derived Metadata paths. A file
the game silently refuses to load looks exactly like a correct one on disk, so
this is the only check that happens before the user sees an empty planner.

Usage:
    python scripts/import_poe2_planner_files.py --src "<file.build>" \
        --name "Warbringer Lv01-10 - Skadoosh" --author Skadoosh --link <url> \
        [--out build_planner] [--install]
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_poe2_planner_files import GAME_DIR, gem_paths, node_index  # noqa: E402

log = logging.getLogger("import_planner")

NAME_MAX = 40  # Mobalytics truncates here; the game's list is no wider
GEM_PATH = re.compile(r"^Metadata/Items/Gems?/([A-Za-z0-9_]+)$")


def normalize(data: dict, name: str, author: str, link: str) -> dict:
    """Return a copy shaped like a creator original."""
    if len(name) > NAME_MAX:
        raise ValueError(f"name is {len(name)} chars; the planner shows at most {NAME_MAX}: {name!r}")
    out = {
        "author": author,
        "link": link,
        "ascendancy": data["ascendancy"],
        "inventory_slots": list(data.get("inventory_slots") or []),
        "name": name,
        "passives": [dict(p) for p in data["passives"]],
        "skills": [],
    }
    for skill in data.get("skills") or []:
        out["skills"].append(_shape_skill(skill))
    return out


def _shape_skill(skill: dict) -> dict:
    """Creator originals: `id, level_interval, support_skills` in that order, every
    support is `{id, level_interval}`, and a skill without supports has NO
    `support_skills` key at all (the repo's generator drops the empty list too --
    test_empty_support_skills_key_is_dropped). poe.ninja's export breaks all three."""
    entry = {"id": skill["id"], "level_interval": skill.get("level_interval") or [1, 100]}
    supports = [
        {"id": s["id"], "level_interval": s.get("level_interval") or [1, 100],
         **{k: v for k, v in s.items() if k not in ("id", "level_interval")}}
        for s in skill.get("support_skills") or []
    ]
    if supports:
        entry["support_skills"] = supports
    entry.update({k: v for k, v in skill.items() if k not in entry and k != "support_skills"})
    return entry


def validate(data: dict, tree_ids: set[str], gem_table: dict[str, str]) -> list[str]:
    """Check ids against ground truth. Repairs Gem/Gems path drift in place and
    returns human-readable problems; an empty list means the file is clean."""
    problems: list[str] = []
    for p in data["passives"]:
        if p.get("id") not in tree_ids:
            problems.append(f"passive id not in tree.json: {p.get('id')!r}")
    for skill in data["skills"]:
        for gem in [skill, *skill.get("support_skills", [])]:
            problems.extend(_check_gem(gem, gem_table))
    if not data["skills"]:
        problems.append("no skills")
    if not data["passives"]:
        problems.append("no passives")
    return problems


def _check_gem(gem: dict, gem_table: dict[str, str]) -> list[str]:
    gid = gem.get("id") or ""
    m = GEM_PATH.match(gid)
    if not m:
        return [f"gem id is not a Metadata gem path: {gid!r}"]
    truth = gem_table.get(m.group(1))
    if truth is None:
        # 표에 없음은 젬이 가짜라는 뜻이 아니다. `data/valid_gems_poe2.json` 의 출처는
        # GGPK 0.4.0d 이고 지금 빌드는 0.5.5 다 — 전직이 주는 VirtuousBarrier 처럼
        # 표가 아예 모르는 젬이 나온다. 제작자 원본 플래너 6개에도 그 젬이 들어 있다.
        # 그래서 generator 의 resolve_gem 과 같은 기준을 쓴다: 부재는 경고, 불일치는 교정.
        log.warning("gem not in valid_gems_poe2.json (표가 0.4.0d 라 낡은 쪽일 수 있다): %s", gid)
        return []
    if truth != gid:
        log.warning("gem path repaired to the GGPK form: %s -> %s", gid, truth)
        gem["id"] = truth
    return []


def import_file(src: Path, name: str, author: str, link: str, out_dir: Path,
                tree_ids: set[str], gem_table: dict[str, str], install: bool) -> Path:
    data = json.loads(src.read_text(encoding="utf-8"))
    shaped = normalize(data, name, author, link)
    problems = validate(shaped, tree_ids, gem_table)
    if problems:
        raise SystemExit(f"{src.name}: " + " | ".join(problems))
    out_dir.mkdir(parents=True, exist_ok=True)
    dest = out_dir / f"{name}.build"
    dest.write_text(json.dumps(shaped, ensure_ascii=False, indent=2), encoding="utf-8")
    log.info("%s <- %s (passives %d, skills %d, items %d)", dest.name, src.name,
             len(shaped["passives"]), len(shaped["skills"]), len(shaped["inventory_slots"]))
    if install:
        GAME_DIR.mkdir(parents=True, exist_ok=True)
        shutil.copy2(dest, GAME_DIR / dest.name)
        log.info("installed -> %s", GAME_DIR / dest.name)
    return dest


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--name", required=True)
    ap.add_argument("--author", required=True)
    ap.add_argument("--link", default="")
    ap.add_argument("--out", default="build_planner")
    ap.add_argument("--install", action="store_true")
    args = ap.parse_args()

    tree_ids = set(node_index().values())
    import_file(Path(args.src), args.name, args.author, args.link, Path(args.out),
                tree_ids, gem_paths(), args.install)
    return 0


if __name__ == "__main__":
    sys.exit(main())
