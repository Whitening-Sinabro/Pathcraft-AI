# -*- coding: utf-8 -*-
"""
PathcraftAI — POE 공식 패치노트 크롤러
pathofexile.com/forum/view-forum/patch-notes에서 직접 수집

사용법:
  python patch_note_scraper.py --collect          # 최신 패치노트 수집
  python patch_note_scraper.py --collect --all     # 전체 수집
  python patch_note_scraper.py --latest            # 최신 패치 보기
  python patch_note_scraper.py --version 3.28.0    # 특정 버전 보기
  python patch_note_scraper.py --summary 3.28.0    # AI 코치용 요약 생성
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import sys
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


def ensure_data_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def fetch_forum_page(page: int = 1) -> list[dict]:
    """패치노트 포럼 목록에서 스레드 정보 추출"""
    url = f"{PATCH_NOTES_FORUM}/page/{page}" if page > 1 else PATCH_NOTES_FORUM
    logger.info(f"포럼 페이지 {page} 수집 중: {url}")

    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"포럼 페이지 요청 실패: {e}")
        return []

    # 정규식으로 thread ID + title 추출 (HTML 구조 변경에 강건)
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
            "url": f"{FORUM_BASE}/view-thread/{thread_id}",
            "date": "",  # 포럼 목록에서는 날짜 별도 파싱 필요 — 본문에서 추출
        })

    logger.info(f"  {len(threads)}개 패치노트 스레드 발견")
    return threads


def extract_version(title: str) -> str:
    """제목에서 패치 버전 추출

    3.28.0 Hotfix 15 → 3.28.0-hotfix15
    Content Update 3.28.0 → 3.28.0
    3.28.0b Patch Notes → 3.28.0b
    """
    ver_match = re.search(r"(\d+\.\d+\.\d+[a-z]?)", title, re.IGNORECASE)
    if not ver_match:
        return ""

    version = ver_match.group(1)

    # 핫픽스 번호 추출
    hotfix_match = re.search(r"hotfix\s*(\d+)", title, re.IGNORECASE)
    if hotfix_match:
        version = f"{version}-hotfix{hotfix_match.group(1)}"

    return version


def fetch_patch_content(thread_id: str) -> str:
    """스레드 첫 번째 포스트(GGG 본문)만 추출"""
    url = f"{FORUM_BASE}/view-thread/{thread_id}"
    logger.info(f"패치노트 본문 수집: {url}")

    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"스레드 요청 실패: {e}")
        return ""

    soup = BeautifulSoup(resp.text, "html.parser")

    # 첫 번째 포스트만 추출 (GGG 공식 본문)
    # 포럼 구조: div.post 여러 개 중 첫 번째
    first_post = soup.select_one("div.content-container")
    if not first_post:
        # 대안: 모든 포스트 중 첫 번째
        posts = soup.select("div.content")
        first_post = posts[0] if posts else None

    if not first_post:
        # 최후 수단: 정규식으로 GGG 포스트 본문 추출
        # "Posted by ... Grinding Gear Games" 이후 ~ 다음 "Posted by" 이전
        match = re.search(
            r"Grinding Gear Games.*?</div>(.*?)(?:Posted by|Report Forum Post)",
            resp.text,
            re.DOTALL,
        )
        if match:
            inner_soup = BeautifulSoup(match.group(1), "html.parser")
            return inner_soup.get_text(separator="\n", strip=True)
        logger.warning("본문 추출 실패")
        return ""

    text = first_post.get_text(separator="\n", strip=True)

    # 댓글 잘라내기: "Last bumped on" 또는 두 번째 "Posted by" 이후 제거
    cutoff_markers = ["Last bumped on", "Last edited by"]
    for marker in cutoff_markers:
        idx = text.find(marker)
        if idx > 0:
            text = text[:idx]
            break

    # 포럼 네비게이션 잡음 제거
    noise_patterns = [
        r"Forum Index.*?View Thread",
        r"\d+\s*\d*\s*Next\s*View Staff Posts\s*Post Reply",
        r"Report Forum Post.*",
    ]
    for pattern in noise_patterns:
        text = re.sub(pattern, "", text, flags=re.DOTALL)

    return text.strip()


def categorize_changes(text: str) -> dict:
    """패치노트 텍스트를 카테고리별로 분류"""
    categories = {
        "skill_gem_changes": [],
        "item_changes": [],
        "atlas_map_changes": [],
        "mechanic_changes": [],
        "currency_changes": [],
        "balance_changes": [],
        "bug_fixes": [],
        "other": [],
    }

    lines = text.split("\n")
    current_section = "other"

    section_mapping = {
        "skill gem": "skill_gem_changes",
        "gem change": "skill_gem_changes",
        "active skill": "skill_gem_changes",
        "support gem": "skill_gem_changes",
        "item": "item_changes",
        "unique": "item_changes",
        "divination": "item_changes",
        "atlas": "atlas_map_changes",
        "map": "atlas_map_changes",
        "voidstone": "atlas_map_changes",
        "endgame": "atlas_map_changes",
        "nightmare": "atlas_map_changes",
        "league": "mechanic_changes",
        "mirage": "mechanic_changes",
        "mechanic": "mechanic_changes",
        "currency": "currency_changes",
        "chisel": "currency_changes",
        "scarab": "currency_changes",
        "essence": "currency_changes",
        "balance": "balance_changes",
        "monster": "balance_changes",
        "damage": "balance_changes",
        "defence": "balance_changes",
        "defense": "balance_changes",
        "bug fix": "bug_fixes",
        "fixed a bug": "bug_fixes",
        "fix": "bug_fixes",
    }

    for line in lines:
        line = line.strip()
        if not line:
            continue

        lower = line.lower()

        # 섹션 헤더 감지
        for keyword, category in section_mapping.items():
            if keyword in lower and len(line) < 100:
                current_section = category
                break

        # 실질적 변경사항 라인 (- 또는 • 로 시작)
        if line.startswith(("-", "•", "*")) or re.match(r"^\d+\.", line):
            change = line.lstrip("-•* ").strip()
            if len(change) > 5:
                categories[current_section].append(change)

    return categories


def extract_skill_changes(text: str) -> list[dict]:
    """스킬 젬 버프/너프를 구조화"""
    changes = []

    # 패턴: "SkillName now has/deals/provides X (previously Y)"
    patterns = [
        r"(.+?)\s+now\s+(?:has|deals|provides|grants)\s+(.+?)(?:\s*\((?:previously|was|from)\s+(.+?)\))?",
        r"(.+?)\s+(?:has been|was)\s+(?:increased|decreased|changed|reduced|buffed|nerfed)\s+(.+)",
        r"(.+?):\s+(.+?)(?:\s*→\s*(.+))?",
    ]

    for line in text.split("\n"):
        line = line.strip().lstrip("-•* ")
        for pattern in patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                change = {
                    "skill": match.group(1).strip(),
                    "change": match.group(2).strip() if match.group(2) else "",
                    "previous": match.group(3).strip() if match.lastindex >= 3 and match.group(3) else "",
                    "raw": line,
                }

                # 버프/너프 판정
                lower = line.lower()
                if any(w in lower for w in ["increased", "added", "now also", "buff", "more", "higher"]):
                    change["type"] = "buff"
                elif any(w in lower for w in ["decreased", "reduced", "removed", "nerf", "less", "lower", "no longer"]):
                    change["type"] = "nerf"
                else:
                    change["type"] = "change"

                changes.append(change)
                break

    return changes


def build_coach_summary(patch_data: dict) -> dict:
    """AI 코치에 주입할 패치 요약 생성"""
    categories = patch_data.get("categories", {})

    summary = {
        "version": patch_data.get("version", ""),
        "date": patch_data.get("date", ""),
        "atlas_changes": categories.get("atlas_map_changes", [])[:20],
        "skill_buffs": [c for c in patch_data.get("skill_changes", []) if c.get("type") == "buff"][:15],
        "skill_nerfs": [c for c in patch_data.get("skill_changes", []) if c.get("type") == "nerf"][:15],
        "currency_changes": categories.get("currency_changes", [])[:10],
        "mechanic_changes": categories.get("mechanic_changes", [])[:10],
        "item_changes": categories.get("item_changes", [])[:10],
        "key_takeaways": [],
    }

    # 핵심 요약 자동 생성
    n_buffs = len(summary["skill_buffs"])
    n_nerfs = len(summary["skill_nerfs"])
    n_atlas = len(summary["atlas_changes"])

    if n_buffs > 0:
        summary["key_takeaways"].append(f"스킬 {n_buffs}개 버프됨")
    if n_nerfs > 0:
        summary["key_takeaways"].append(f"스킬 {n_nerfs}개 너프됨")
    if n_atlas > 0:
        summary["key_takeaways"].append(f"아틀라스/맵 변경 {n_atlas}건")

    return summary


def collect_patches(max_pages: int = 1):
    """패치노트 수집"""
    ensure_data_dir()

    index = load_index()
    collected = 0

    for page in range(1, max_pages + 1):
        threads = fetch_forum_page(page)

        for thread in threads:
            version = thread["version"]

            # 이미 수집된 버전 스킵
            if version in index and index[version].get("full_text"):
                logger.info(f"  {version} — 이미 수집됨, 스킵")
                continue

            # 본문 수집
            content = fetch_patch_content(thread["thread_id"])
            if not content:
                continue

            # 분류
            categories = categorize_changes(content)
            skill_changes = extract_skill_changes(content)

            patch_data = {
                "version": version,
                "title": thread["title"],
                "date": thread["date"],
                "url": thread["url"],
                "full_text": content[:50000],  # 최대 50K자
                "categories": categories,
                "skill_changes": skill_changes,
                "collected_at": datetime.now().isoformat(),
            }

            # 저장
            filename = f"patch_{version.replace('.', '_')}.json"
            filepath = DATA_DIR / filename
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(patch_data, f, ensure_ascii=False, indent=2)

            # 코치 요약도 저장
            summary = build_coach_summary(patch_data)
            summary_file = DATA_DIR / f"summary_{version.replace('.', '_')}.json"
            with open(summary_file, "w", encoding="utf-8") as f:
                json.dump(summary, f, ensure_ascii=False, indent=2)

            # 인덱스 업데이트
            index[version] = {
                "title": thread["title"],
                "date": thread["date"],
                "file": filename,
                "summary_file": f"summary_{version.replace('.', '_')}.json",
                "url": thread["url"],
                "full_text": True,
                "skill_changes_count": len(skill_changes),
            }

            collected += 1
            logger.info(f"  {version} 수집 완료 (스킬 변경 {len(skill_changes)}건)")

    save_index(index)
    logger.info(f"수집 완료: {collected}개 신규, 총 {len(index)}개")


def load_index() -> dict:
    if INDEX_FILE.exists():
        with open(INDEX_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_index(index: dict):
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)


def get_latest_summary() -> dict:
    """최신 패치의 코치 요약 반환"""
    index = load_index()
    if not index:
        return {}

    # 버전 번호로 정렬 (3.28.0e > 3.28.0d > 3.28.0)
    sorted_versions = sorted(index.keys(), reverse=True)

    for version in sorted_versions:
        info = index[version]
        summary_file = DATA_DIR / info.get("summary_file", "")
        if summary_file.exists():
            with open(summary_file, "r", encoding="utf-8") as f:
                return json.load(f)

    return {}


def get_version_data(version: str) -> dict:
    """특정 버전의 패치 데이터 반환"""
    index = load_index()
    info = index.get(version, {})
    if not info:
        return {}

    filepath = DATA_DIR / info.get("file", "")
    if filepath.exists():
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="POE 공식 패치노트 크롤러")
    ap.add_argument("--collect", action="store_true", help="패치노트 수집")
    ap.add_argument("--all", action="store_true", help="전체 페이지 수집 (--collect과 함께)")
    ap.add_argument("--latest", action="store_true", help="최신 패치 요약")
    ap.add_argument("--version", type=str, help="특정 버전 조회")
    ap.add_argument("--summary", type=str, help="특정 버전 코치 요약")
    args = ap.parse_args()

    if args.collect:
        pages = 5 if args.all else 1
        collect_patches(max_pages=pages)
    elif args.latest:
        summary = get_latest_summary()
        if summary:
            print(json.dumps(summary, ensure_ascii=False, indent=2))
        else:
            logger.info("수집된 패치노트 없음. --collect 먼저 실행하세요.")
    elif args.version:
        data = get_version_data(args.version)
        if data:
            print(json.dumps(data, ensure_ascii=False, indent=2))
        else:
            logger.info(f"{args.version} 데이터 없음")
    elif args.summary:
        data = get_version_data(args.summary)
        if data:
            summary = build_coach_summary(data)
            print(json.dumps(summary, ensure_ascii=False, indent=2))
        else:
            logger.info(f"{args.summary} 데이터 없음")
    else:
        ap.print_help()
