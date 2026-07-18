# -*- coding: utf-8 -*-
"""
PathcraftAI — POE 공식 패치노트 크롤러 v2
pathofexile.com/forum/view-forum/patch-notes에서 직접 수집

메이저 패치: 전체 섹션 파싱 (Return to top 기준)
마이너 패치: 밸런스 변경 중심
핫픽스: 스킬 변경만

사용법:
  python patch_note_scraper.py --collect              # 최신 1페이지 수집
  python patch_note_scraper.py --collect --all         # 전체 수집 (5페이지)
  python patch_note_scraper.py --collect --pages 10    # 10페이지 수집
  python patch_note_scraper.py --latest                # 최신 메이저 패치 요약
  python patch_note_scraper.py --version 3.28.0        # 특정 버전
  python patch_note_scraper.py --track "Keepers of the Flame"  # 특정 메카닉 추적
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import sys
import time
import argparse
import logging
from pathlib import Path
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

logger = logging.getLogger("patch_scraper")
logging.basicConfig(level=logging.INFO, format="%(message)s", stream=sys.stderr)

FORUM_BASE = "https://www.pathofexile.com/forum"
PATCH_NOTES_FORUM = f"{FORUM_BASE}/view-forum/patch-notes"
HEADERS = {
    "User-Agent": "PathcraftAI/2.0 (Build Coach Tool)",
    "Accept-Language": "en-US,en;q=0.9",
}

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "patch_notes"
INDEX_FILE = DATA_DIR / "patch_index.json"

# 메이저 패치에서 공통적으로 쓰이는 섹션 헤더들
KNOWN_SECTION_HEADERS = [
    "Challenge League",
    "New Content and Features",
    "Endgame Changes",
    "Atlas Passive Tree Changes",
    "League Changes",
    "Player Changes",
    "Skill Gem Changes",
    "Vaal Gem Changes",
    "Support Gem Changes",
    "Ascendancy Changes",
    "Bloodline Changes",
    "Passive Skill Tree Changes",
    "Unique Item Changes",
    "Item Changes",
    "Ruthless-specific Changes",
    "Monster Changes",
    "Quest Reward Changes",
    "User Interface and Quality of Life Changes",
    "Microtransaction Updates",
    "Bug Fixes",
    "as a Core League",
    "Removed as a Core League",
]


def ensure_data_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True)


# ── 포럼 스캔 ──────────────────────────────────────────────

def fetch_forum_page(page: int = 1) -> list[dict]:
    """패치노트 포럼 목록에서 스레드 정보 추출"""
    url = f"{PATCH_NOTES_FORUM}/page/{page}" if page > 1 else PATCH_NOTES_FORUM
    logger.info(f"포럼 페이지 {page} 수집 중...")

    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"포럼 요청 실패: {e}")
        return []

    matches = re.findall(
        r'<a[^>]*href="[^"]*view-thread/(\d+)"[^>]*>([^<]+)</a>',
        resp.text,
    )

    threads = []
    seen = set()

    for thread_id, raw_title in matches:
        title = raw_title.strip()
        version = extract_version(title)
        if not version or thread_id in seen:
            continue
        seen.add(thread_id)

        threads.append({
            "thread_id": thread_id,
            "title": title,
            "version": version,
            "patch_type": classify_patch_type(title),
            "url": f"{FORUM_BASE}/view-thread/{thread_id}",
        })

    logger.info(f"  {len(threads)}개 스레드 발견")
    return threads


def extract_version(title: str) -> str:
    """제목에서 패치 버전 추출"""
    ver_match = re.search(r"(\d+\.\d+\.\d+[a-z]?)", title, re.IGNORECASE)
    if not ver_match:
        return ""
    version = ver_match.group(1)
    hotfix_match = re.search(r"hotfix\s*(\d+)", title, re.IGNORECASE)
    if hotfix_match:
        version = f"{version}-hotfix{hotfix_match.group(1)}"
    return version


def classify_patch_type(title: str) -> str:
    """패치 유형 판별: major / minor / hotfix"""
    lower = title.lower()
    if "content update" in lower:
        return "major"
    if "hotfix" in lower:
        return "hotfix"
    # "3.28.0b Patch Notes" 등
    return "minor"


# ── 본문 수집 ──────────────────────────────────────────────

def fetch_patch_content(thread_id: str) -> str:
    """스레드 첫 포스트(GGG 본문)만 추출"""
    time.sleep(0.5)  # rate limiting — 포럼 차단 방지
    url = f"{FORUM_BASE}/view-thread/{thread_id}"

    try:
        resp = requests.get(url, headers=HEADERS, timeout=60)
        resp.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"스레드 요청 실패: {e}")
        return ""

    soup = BeautifulSoup(resp.text, "html.parser")
    posts = soup.select("div.content")
    if not posts:
        logger.warning(f"본문 추출 실패: {url}")
        return ""

    text = posts[0].get_text(separator="\n", strip=True)

    # 댓글 제거
    for marker in ["Posted by", "Last bumped on"]:
        idx = text.find(marker)
        if idx > 100:  # 100자 이내면 본문 일부일 수 있음
            text = text[:idx]
            break

    # 네비게이션 잡음 제거
    text = re.sub(r"Forum Index.*?View Thread", "", text, flags=re.DOTALL)
    text = re.sub(r"\d+\s*\d*\s*Next\s*View Staff Posts\s*Post Reply", "", text)
    text = re.sub(r"Report Forum Post.*", "", text, flags=re.DOTALL)

    return text.strip()


# ── 섹션 파싱 (메이저 패치) ────────────────────────────────

def parse_sections(text: str) -> dict:
    """Return to top 기준으로 섹션 분리"""
    sections = {}
    current_section = "preamble"
    current_lines = []

    for line in text.split("\n"):
        stripped = line.strip()

        if stripped == "Return to top":
            if current_lines:
                sections[current_section] = "\n".join(current_lines).strip()
            current_lines = []
            continue

        # 섹션 헤더 매칭 (부분 일치)
        matched = False
        for header_pattern in KNOWN_SECTION_HEADERS:
            if header_pattern in stripped and len(stripped) < 80:
                if current_lines:
                    sections[current_section] = "\n".join(current_lines).strip()
                current_section = stripped
                current_lines = []
                matched = True
                break

        if not matched and stripped:
            current_lines.append(stripped)

    if current_lines:
        sections[current_section] = "\n".join(current_lines).strip()

    return sections


def extract_lines(text: str) -> list[str]:
    """텍스트에서 의미 있는 라인 추출"""
    return [line.strip() for line in text.split("\n") if line.strip() and len(line.strip()) > 10]


# ── 변경 분류 ──────────────────────────────────────────────

def classify_change(line: str) -> str:
    """buff / nerf / change 판정"""
    lower = line.lower()
    if any(w in lower for w in [
        "increased", "now deals", "more damage", "now has", "added a new",
        "now also", "now grants", "now fires", "now provides", "can now",
        "now have", "higher", "faster", "additional"
    ]):
        return "buff"
    if any(w in lower for w in [
        "decreased", "reduced", "less damage", "no longer has",
        "no longer grants", "can no longer", "removed", "lowered",
        "has been removed", "now has a limit", "slower", "fewer"
    ]):
        return "nerf"
    return "change"


# ── 파생 델타 인덱스 ──────────────────────────────────────

SECTION_DOMAINS = {
    "Challenge League": "challenge_league",
    "New Content and Features": "new_content",
    "Endgame Changes": "endgame",
    "Atlas Passive Tree Changes": "atlas",
    "League Changes": "league",
    "Player Changes": "player",
    "Skill Gem Changes": "skill_gem",
    "Vaal Gem Changes": "vaal_gem",
    "Support Gem Changes": "support_gem",
    "Ascendancy Changes": "ascendancy",
    "Bloodline Changes": "bloodline",
    "Passive Skill Tree Changes": "passive_tree",
    "Unique Item Changes": "unique_item",
    "Item Changes": "item",
    "Ruthless-specific Changes": "ruthless",
    "Monster Changes": "monster",
    "Quest Reward Changes": "quest_reward",
    "User Interface and Quality of Life Changes": "ui_qol",
    "Bug Fixes": "bugfix",
    "Core League": "core_league",
}

PATCH_WATCH_TERMS = {
    "scion": ["scion", "reliquarian", "luminary", "ascendant"],
    "mercenary": ["mercenary", "mercenaries", "trarthus"],
    "allflame": ["allflame", "chart", "voyage", "ducat", "valerie", "sovereign"],
    "atlas": ["atlas", "map", "voidstone", "scrying", "anomaly", "reflect", "thorns"],
    "socket_crafting": ["socket", "crafting bench", "reroll", "modifier", "crystallised rancour"],
    "skill_numbers": ["gem level", "cast time", "mana cost", "effectiveness", "damage"],
    "economy_reward": ["reward", "drop", "currency", "divination", "card", "unique"],
}


def classify_section_domain(section: str) -> str:
    """패치노트 섹션을 코치/DB용 도메인으로 축약."""
    for needle, domain in SECTION_DOMAINS.items():
        if needle.lower() in section.lower():
            return domain
    return "other"


def extract_entity_name(line: str) -> str:
    """'Arc: Now has ...' 같은 패치 라인에서 엔티티명을 추출."""
    prefix, sep, _ = line.partition(":")
    prefix = prefix.strip()
    if not sep or not prefix or len(prefix) > 80:
        return ""
    if any(prefix.lower().startswith(x) for x in ("the following", "added ", "removed ")):
        return ""
    return prefix


_NUMBER_RE = re.compile(
    r"(?<![\w.])"
    r"(?P<number>\d+(?:\.\d+)?(?:-\d+(?:\.\d+)?)?)"
    r"\s*(?P<unit>%|seconds?|metres?|meters?|projectiles?|targets?|charges?|stacks?|uses?|mana|life|damage|radius)?",
    re.IGNORECASE,
)


def extract_numeric_tokens(text: str) -> list[dict]:
    """라인에서 숫자/범위/단위를 보존해서 추출."""
    tokens = []
    for match in _NUMBER_RE.finditer(text):
        number = match.group("number")
        unit = (match.group("unit") or "").strip()
        tokens.append({
            "raw": match.group(0).strip(),
            "number": number,
            "unit": unit,
        })
    return tokens


def extract_numeric_delta(line: str) -> dict:
    """현재값과 previously 값을 분리한다. 완전한 수식 계산은 GGPK/PoB 검증 후 담당."""
    previous_chunks = re.findall(r"\(previously ([^)]+)\)", line, flags=re.IGNORECASE)
    previous_text = " ".join(previous_chunks)
    without_previous = re.sub(r"\(previously [^)]+\)", "", line, flags=re.IGNORECASE)
    current = extract_numeric_tokens(without_previous)
    previous = extract_numeric_tokens(previous_text)

    if current and previous and len(current) == len(previous):
        pairing = "paired_by_order"
    elif current and previous:
        pairing = "unpaired_review_required"
    elif current:
        pairing = "current_only"
    else:
        pairing = "none"

    return {
        "current": current,
        "previous": previous,
        "pairing": pairing,
        "has_previous": bool(previous),
    }


def infer_patch_tags(line: str, section: str) -> list[str]:
    lowered = line.lower()
    section_lower = section.lower()
    domain = classify_section_domain(section)
    tags = []
    for tag, needles in PATCH_WATCH_TERMS.items():
        if any(needle in lowered for needle in needles):
            tags.append(tag)
    if domain == "atlas":
        tags.append("atlas")
    if domain in {"skill_gem", "vaal_gem", "support_gem"} and extract_numeric_tokens(line):
        tags.append("skill_numbers")
    if "challenge league" in section_lower and "allflame" in section_lower:
        tags.append("allflame")
    return sorted(tags)


def _compact_high_impact_watchlist(entries: list[dict]) -> dict:
    def count(tag: str) -> int:
        return sum(1 for entry in entries if tag in entry.get("watch_tags", []))

    return {
        "scion_branch_lines": count("scion"),
        "mercenary_lines": count("mercenary"),
        "allflame_loop_lines": count("allflame"),
        "atlas_lines": count("atlas"),
        "socket_crafting_lines": count("socket_crafting"),
        "skill_number_lines": count("skill_numbers"),
        "economy_reward_lines": count("economy_reward"),
    }


def build_patch_delta_index(patch_data: dict) -> dict:
    """수집된 패치노트 JSON을 코치/검증용 델타 DB로 변환."""
    entries = []
    sections = patch_data.get("sections", {}) or {}
    source_url = patch_data.get("url", "")
    version = patch_data.get("version", "")

    for section, lines in sections.items():
        domain = classify_section_domain(section)
        for idx, line in enumerate(lines or [], start=1):
            if not isinstance(line, str) or len(line.strip()) <= 10:
                continue
            numeric_delta = extract_numeric_delta(line)
            change_type = classify_change(line)
            entry = {
                "id": f"{version}:{domain}:{idx:03d}",
                "version": version,
                "section": section,
                "domain": domain,
                "entity": extract_entity_name(line),
                "change_type": change_type,
                "line": line,
                "numeric_delta": numeric_delta,
                "has_numeric_delta": bool(numeric_delta["current"] or numeric_delta["previous"]),
                "watch_tags": infer_patch_tags(line, section),
                "source_url": source_url,
                "verification_state": "official_patch_note_text",
            }
            entries.append(entry)

    domain_counts: dict[str, int] = {}
    numeric_counts: dict[str, int] = {}
    for entry in entries:
        domain = entry["domain"]
        domain_counts[domain] = domain_counts.get(domain, 0) + 1
        if entry["has_numeric_delta"]:
            numeric_counts[domain] = numeric_counts.get(domain, 0) + 1

    return {
        "dataset_kind": "poe1_patch_delta_index",
        "schema_version": 1,
        "version": version,
        "title": patch_data.get("title", ""),
        "patch_type": patch_data.get("patch_type", ""),
        "source_url": source_url,
        "structured_at": datetime.now().isoformat(),
        "source_file": f"patch_{version.replace('.', '_').replace('-', '_')}.json",
        "summary": {
            "entry_count": len(entries),
            "numeric_delta_count": sum(1 for entry in entries if entry["has_numeric_delta"]),
            "previous_value_count": sum(1 for entry in entries if entry["numeric_delta"]["has_previous"]),
            "domain_counts": domain_counts,
            "numeric_domain_counts": numeric_counts,
            "high_impact_watchlist": _compact_high_impact_watchlist(entries),
        },
        "coach_context": {
            "rule": "Use this as official patch-note evidence, not as final GGPK/PoB truth. Later 3.29.x and hotfix overlays must supersede affected values.",
            "priority_domains": [
                "skill_gem",
                "support_gem",
                "ascendancy",
                "passive_tree",
                "atlas",
                "league",
                "item",
                "unique_item",
            ],
            "launch_status": "pre_launch_patch_notes_confirmed_live_client_pending",
        },
        "entries": entries,
    }


def build_early_patch_adjustment_policy(version: str, source_url: str) -> dict:
    """시즌 초반 패치/핫픽스가 기존 수치를 어떻게 덮는지 기록."""
    return {
        "dataset_kind": "poe1_early_season_patch_adjustment_policy",
        "schema_version": 1,
        "base_version": version,
        "source_url": source_url,
        "structured_at": datetime.now().isoformat(),
        "patch_flow": [
            {
                "stage": "base_patch_notes",
                "source": "official_forum_patch_notes",
                "role": "Initial text truth for changed systems and numeric intent.",
                "confidence": "official_text",
            },
            {
                "stage": "launch_client_ggpk",
                "source": "local_ggpk_extract_after_patch",
                "role": "Machine-readable implementation truth. Confirms or corrects patch-note numbers.",
                "confidence": "implementation_truth",
            },
            {
                "stage": "post_launch_ggpk_refresh",
                "source": "local_ggpk_extract_after_each_client_update",
                "role": "Repeatable implementation overlays for 3.29.0b, hotfix client pushes, server/client restarts, and silent data corrections.",
                "confidence": "implementation_truth_with_snapshot_manifest",
            },
            {
                "stage": "day0_hotfix",
                "source": "official_forum_hotfix_threads_and_client_restarts",
                "role": "Immediate overrides for broken drops, crashes, disabled cards/items, or severe balance issues.",
                "confidence": "official_hotfix_text_until_ggpk_refresh",
            },
            {
                "stage": "minor_patch",
                "source": "official_3_29_0b_or_later_patch_notes",
                "role": "Stable overlay that supersedes base patch lines for the affected entity/stat only.",
                "confidence": "official_text_then_ggpk_confirmed",
            },
            {
                "stage": "tooling_confirmation",
                "source": "Path of Building, PoEWiki, live trade/economy samples, measured map runs",
                "role": "Coach recommendation confidence upgrade. Does not override official/GGPK values by itself.",
                "confidence": "secondary_validation",
            },
        ],
        "numeric_overlay_rules": [
            "Never mutate the base patch note entry in place; append an overlay record with patch_version, source_url, affected_entry_id, old_value, new_value, unit, and reason.",
            "If GGPK and patch-note text disagree after launch, store both and mark effective_value_source as ggpk unless GGG publishes a correction.",
            "Hotfix entries may temporarily disable an item/card/gem/mechanic. Represent this as state_override=disabled instead of numeric_value=0.",
            "For ranges such as 10-15%, preserve min/max. Do not collapse to an average for build advice unless a separate expected-value model asks for it.",
            "For 'increased/reduced by X%' without an explicit previous value, store operation=relative_multiplier and require a base value from GGPK or prior patch DB.",
            "For 'now has X (previously Y)', store operation=set_value and compute delta only when units and token counts match.",
            "Apply overlays by newest semantic patch order, then hotfix number, then collected_at. Scope must match entity plus stat; unrelated lines remain inherited from base 3.29.0.",
        ],
        "ggpk_snapshot_rules": [
            "Every post-launch GGPK extract must be stored as a versioned snapshot before promotion. Do not overwrite the previous effective extract without a manifest and diff.",
            "Snapshot identity must include patch_version, client_build or collected_at, source_path, table row counts, file hashes, and extractor_version.",
            "Diff raw tables by stable semantic keys where possible: Id for Mods/BaseItemTypes/ActiveSkills, displayed name plus metadata id for SkillGems, graph id for PassiveSkills, map id/name for Maps.",
            "A GGPK value can supersede patch-note text only for the affected entity/stat and only after the table diff identifies the source row.",
            "If a hotfix is server-only and the GGPK tables do not change, keep the hotfix overlay as official_text_pending_client_data instead of inventing a GGPK value.",
            "Keep patch-note delta, GGPK row diff, PoB support state, and live measurement as separate evidence layers. The coach must report which layer it is using.",
        ],
        "ggpk_diff_targets": [
            {
                "table": "SkillGems",
                "purpose": "Gem level requirements, supportability, tags, quality/stat scaling, new or changed gems.",
                "stable_keys": ["BaseItemTypesKey", "Id", "DisplayedName"],
            },
            {
                "table": "ActiveSkills",
                "purpose": "Skill ids, stat references, weapon requirements, granted/triggered skills, behaviour flags.",
                "stable_keys": ["Id", "DisplayedName", "ActiveSkillTypes"],
            },
            {
                "table": "BaseItemTypes",
                "purpose": "New bases, item classes, tags, drop levels, sockets and crafting base gates.",
                "stable_keys": ["Id", "Name"],
            },
            {
                "table": "Mods",
                "purpose": "Explicit/implicit/enchantment modifier ranges, item mod eligibility, affix pool changes.",
                "stable_keys": ["Id", "Name", "StatsKey1", "StatsKey2", "StatsKey3", "StatsKey4"],
            },
            {
                "table": "PassiveSkills",
                "purpose": "Passive tree, ascendancy, atlas/passive values, graph connectivity and stat text.",
                "stable_keys": ["Id", "GraphId", "Name"],
            },
            {
                "table": "Ascendancy",
                "purpose": "Class/ascendancy availability, Scion branch separation, Bloodline-related class data.",
                "stable_keys": ["Id", "Name"],
            },
            {
                "table": "Maps",
                "purpose": "Atlas rotation, map tiers, map ids, special map availability.",
                "stable_keys": ["Id", "Name"],
            },
            {
                "table": "QuestRewards",
                "purpose": "Campaign/league-start gem access and vendor reward changes.",
                "stable_keys": ["Quest", "CharactersKey", "BaseItemTypesKey"],
            },
            {
                "table": "Scarabs",
                "purpose": "Atlas farming and mechanic access changes.",
                "stable_keys": ["Id", "Name"],
            },
        ],
        "coach_rules": [
            "When giving early-season advice, say whether the number is patch-note-only, GGPK-confirmed, PoB-confirmed, or live-measured.",
            "Do not promote a build solely because a line is a buff; require interaction checks, item access, passive pathing, and early economy.",
            "Keep Scion Ascendant, Reliquarian, and Luminary branches separated unless a build explicitly uses that branch.",
            "For farming strategy, do not rank Allflame, Fossil, Guardian Map, or Scrying paths until reward samples and map-time samples exist.",
        ],
        "required_overlay_fields": [
            "overlay_id",
            "patch_version",
            "patch_type",
            "source_url",
            "affected_entry_id",
            "entity",
            "stat",
            "operation",
            "old_value",
            "new_value",
            "unit",
            "effective_value_source",
            "verification_state",
            "ggpk_snapshot_id",
            "ggpk_table",
            "ggpk_row_key",
            "notes",
        ],
    }


def write_patch_derivatives(version: str) -> dict:
    ensure_data_dir()
    filename = f"patch_{version.replace('.', '_').replace('-', '_')}.json"
    path = DATA_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"{version} patch data not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        patch_data = json.load(f)

    delta_index = build_patch_delta_index(patch_data)
    delta_file = DATA_DIR / f"poe1_{version.replace('.', '_').replace('-', '_')}_patch_delta_index.json"
    with open(delta_file, "w", encoding="utf-8") as f:
        json.dump(delta_index, f, ensure_ascii=False, indent=2)
        f.write("\n")

    policy = build_early_patch_adjustment_policy(version, patch_data.get("url", ""))
    policy_file = DATA_DIR / f"poe1_{version.replace('.', '_').replace('-', '_')}_early_patch_adjustment_policy.json"
    with open(policy_file, "w", encoding="utf-8") as f:
        json.dump(policy, f, ensure_ascii=False, indent=2)
        f.write("\n")

    return {
        "delta_file": str(delta_file),
        "policy_file": str(policy_file),
        "entry_count": delta_index["summary"]["entry_count"],
        "numeric_delta_count": delta_index["summary"]["numeric_delta_count"],
    }


# ── 데이터 구조화 ─────────────────────────────────────────

def build_major_patch_data(version: str, title: str, url: str, text: str) -> dict:
    """메이저 패치 → 전체 섹션 구조화"""
    sections = parse_sections(text)

    data = {
        "version": version,
        "title": title,
        "url": url,
        "patch_type": "major",
        "collected_at": datetime.now().isoformat(),
        "sections": {},
        "coach_summary": {},
    }

    for key, val in sections.items():
        if key == "preamble":
            continue
        data["sections"][key] = extract_lines(val)

    # 코치 요약
    s = data["coach_summary"]
    s["version"] = version
    s["endgame_changes"] = data["sections"].get("Endgame Changes", [])
    s["atlas_passive_changes"] = data["sections"].get("Atlas Passive Tree Changes", [])

    skill_lines = data["sections"].get("Skill Gem Changes", [])
    classified = [{"raw": l, "type": classify_change(l)} for l in skill_lines]
    s["skill_buffs"] = [c for c in classified if c["type"] == "buff"]
    s["skill_nerfs"] = [c for c in classified if c["type"] == "nerf"]

    s["support_gem_changes"] = data["sections"].get("Support Gem Changes", [])
    s["ascendancy_changes"] = data["sections"].get("Ascendancy Changes", [])
    s["unique_item_changes"] = data["sections"].get("Unique Item Changes", [])
    s["item_currency_changes"] = data["sections"].get("Item Changes", [])
    s["league_mechanic_changes"] = data["sections"].get("League Changes", [])
    s["player_changes"] = data["sections"].get("Player Changes", [])
    s["quest_reward_changes"] = data["sections"].get("Quest Reward Changes", [])
    s["passive_tree_changes"] = data["sections"].get("Passive Skill Tree Changes", [])
    s["bloodline_changes"] = data["sections"].get("Bloodline Changes", [])

    # 리그 관련 섹션 (동적 이름)
    for key in data["sections"]:
        if "Core League" in key or "Challenge League" in key:
            safe_key = key.lower().replace(" ", "_").replace("'", "")
            s[safe_key] = data["sections"][key]

    s["key_numbers"] = {
        "total_sections": len(data["sections"]),
        "total_skill_buffs": len(s["skill_buffs"]),
        "total_skill_nerfs": len(s["skill_nerfs"]),
        "total_endgame_changes": len(s.get("endgame_changes", [])),
        "total_atlas_passive_changes": len(s.get("atlas_passive_changes", [])),
    }

    return data


def build_minor_patch_data(version: str, title: str, url: str, text: str) -> dict:
    """마이너 패치 → 밸런스 변경 중심"""
    lines = extract_lines(text)
    classified = [{"raw": l, "type": classify_change(l)} for l in lines if len(l) > 15]

    return {
        "version": version,
        "title": title,
        "url": url,
        "patch_type": "minor",
        "collected_at": datetime.now().isoformat(),
        "all_changes": lines,
        "skill_buffs": [c for c in classified if c["type"] == "buff"],
        "skill_nerfs": [c for c in classified if c["type"] == "nerf"],
        "total_changes": len(lines),
    }


def build_hotfix_data(version: str, title: str, url: str, text: str) -> dict:
    """핫픽스 → 변경사항만"""
    lines = extract_lines(text)

    return {
        "version": version,
        "title": title,
        "url": url,
        "patch_type": "hotfix",
        "collected_at": datetime.now().isoformat(),
        "changes": lines,
        "total_changes": len(lines),
    }


# ── 수집 ──────────────────────────────────────────────────

def collect_patches(max_pages: int = 1, force: bool = False):
    """패치노트 수집"""
    ensure_data_dir()
    index = load_index()
    collected = 0

    for page in range(1, max_pages + 1):
        threads = fetch_forum_page(page)
        if not threads:
            break

        for thread in threads:
            version = thread["version"]

            if version in index and not force:
                continue

            logger.info(f"  수집: {version} ({thread['patch_type']})")
            content = fetch_patch_content(thread["thread_id"])
            if not content:
                continue

            # 유형별 파싱
            if thread["patch_type"] == "major":
                data = build_major_patch_data(version, thread["title"], thread["url"], content)
            elif thread["patch_type"] == "minor":
                data = build_minor_patch_data(version, thread["title"], thread["url"], content)
            else:
                data = build_hotfix_data(version, thread["title"], thread["url"], content)

            # 저장
            filename = f"patch_{version.replace('.', '_').replace('-', '_')}.json"
            with open(DATA_DIR / filename, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            # 메이저 패치는 코치 요약도 별도 저장
            if thread["patch_type"] == "major" and "coach_summary" in data:
                summary_file = f"summary_{version.replace('.', '_')}.json"
                with open(DATA_DIR / summary_file, "w", encoding="utf-8") as f:
                    json.dump(data["coach_summary"], f, ensure_ascii=False, indent=2)

            # 인덱스
            index[version] = {
                "title": thread["title"],
                "file": filename,
                "url": thread["url"],
                "patch_type": thread["patch_type"],
                "collected": True,
            }

            collected += 1
            total = data.get("coach_summary", {}).get("key_numbers", {}).get("total_sections", data.get("total_changes", 0))
            logger.info(f"    완료 (섹션/변경: {total})")

    save_index(index)
    logger.info(f"\n수집 완료: {collected}개 신규, 총 {len(index)}개")


# ── 특정 메카닉 추적 ───────────────────────────────────────

def track_mechanic(keyword: str):
    """특정 메카닉 관련 변경사항을 모든 패치에서 추적"""
    index = load_index()
    results = []

    for version in sorted(index.keys()):
        info = index[version]
        filepath = DATA_DIR / info.get("file", "")
        if not filepath.exists():
            continue

        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        # 모든 텍스트에서 keyword 검색
        matches = []

        if data.get("patch_type") == "major":
            for section_name, lines in data.get("sections", {}).items():
                for line in lines:
                    if keyword.lower() in line.lower():
                        matches.append({"section": section_name, "change": line})
        else:
            for line in data.get("all_changes", data.get("changes", [])):
                if keyword.lower() in line.lower():
                    matches.append({"change": line})

        if matches:
            results.append({
                "version": version,
                "title": info.get("title", ""),
                "patch_type": info.get("patch_type", ""),
                "matches": matches,
            })

    return results


# ── IO ────────────────────────────────────────────────────

def load_index() -> dict:
    if INDEX_FILE.exists():
        with open(INDEX_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_index(index: dict):
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)


def get_latest_summary() -> dict:
    """최신 메이저 패치의 코치 요약"""
    index = load_index()
    major_versions = [v for v, info in index.items()
                      if info.get("patch_type") == "major" and "hotfix" not in v]
    if not major_versions:
        return {}

    latest = sorted(major_versions, reverse=True)[0]
    summary_file = DATA_DIR / f"summary_{latest.replace('.', '_')}.json"
    if summary_file.exists():
        with open(summary_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


# ── CLI ───────────────────────────────────────────────────

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="POE 공식 패치노트 크롤러 v2")
    ap.add_argument("--collect", action="store_true", help="패치노트 수집")
    ap.add_argument("--all", action="store_true", help="전체 페이지 수집")
    ap.add_argument("--pages", type=int, default=1, help="수집할 페이지 수")
    ap.add_argument("--force", action="store_true", help="이미 수집된 것도 재수집")
    ap.add_argument("--latest", action="store_true", help="최신 메이저 패치 요약")
    ap.add_argument("--version", type=str, help="특정 버전 조회")
    ap.add_argument("--track", type=str, help="특정 메카닉 변경사항 추적")
    ap.add_argument("--derive-version", type=str, help="수집된 패치 JSON에서 델타/초기보정 DB 생성")
    # POE2 D0 — Rust 가 --game poe1|poe2 전달. POE2 패치노트 소스/URL 분기는 D8 별도.
    ap.add_argument("--game", choices=["poe1", "poe2"], default="poe1",
                    help="대상 게임 (POE2 패치노트 소스 분기는 D8 에서 구현 예정)")
    args = ap.parse_args()

    if args.game == "poe2":
        logger.warning("--game poe2 는 D0 플래그 수용 단계 — POE1 패치노트 URL 로 처리 (D8 미완)")

    if args.collect:
        pages = 5 if args.all else args.pages
        collect_patches(max_pages=pages, force=args.force)
    elif args.latest:
        s = get_latest_summary()
        if s:
            print(json.dumps(s, ensure_ascii=False, indent=2))
        else:
            logger.info("수집된 메이저 패치 없음")
    elif args.version:
        filepath = DATA_DIR / f"patch_{args.version.replace('.', '_').replace('-', '_')}.json"
        if filepath.exists():
            with open(filepath, "r", encoding="utf-8") as f:
                print(json.dumps(json.load(f), ensure_ascii=False, indent=2))
        else:
            logger.info(f"{args.version} 데이터 없음")
    elif args.track:
        results = track_mechanic(args.track)
        if results:
            for r in results:
                print(f"\n=== {r['version']} ({r['patch_type']}) — {r['title']} ===")
                for m in r["matches"]:
                    section = m.get("section", "")
                    prefix = f"[{section}] " if section else ""
                    print(f"  {prefix}{m['change']}")
            print(f"\n총 {sum(len(r['matches']) for r in results)}건 in {len(results)}개 패치")
        else:
            logger.info(f"'{args.track}' 관련 변경사항 없음")
    elif args.derive_version:
        result = write_patch_derivatives(args.derive_version)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        ap.print_help()
