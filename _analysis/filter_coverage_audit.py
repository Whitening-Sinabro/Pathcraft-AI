# -*- coding: utf-8 -*-
"""필터 전체 coverage 감사 — BaseItemTypes vs generate_beta_overlay 매칭 BaseType 비교.

POE 게임 데이터의 valuable BaseType 카테고리를 하나씩 샘플링해서 필터에 매칭되는지 확인.
미매칭 항목(styling 없이 폴스루) 탐지 → 사용자 보고.

실행: python _analysis/filter_coverage_audit.py
"""
import json
import re
import sys
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "python"))

from sections_continue import generate_beta_overlay  # noqa: E402

# 제외할 InheritsFrom (필터 대상 아님)
SKIP_PREFIXES = (
    "Metadata/Items/Gems/",  # Skill Gems (layer_gems_quality 별도 처리)
    "Metadata/Items/QuestItems/",
    "Metadata/Items/MicrotransactionCurrency/",
    "Metadata/Items/ItemisedCorpse/",
    "Metadata/Items/Hideout",
    "Metadata/Items/Pets/",
    "Metadata/Items/PantheonSouls/",  # layer_heist/pantheon 처리
    "Metadata/Items/Labyrinth/",  # Labyrinth trinkets, not drops
    "Metadata/Items/Classic/",
    "Metadata/Items/Relics/",  # Sanctum Relics, 별도 취급
    "Metadata/Items/NecropolisPack/",
    "Metadata/Items/Archnemesis/",  # Retired league
    "Metadata/Items/Sentinel/",  # Retired league
)

# 제외할 이름 패턴
SKIP_NAME_PATTERNS = [
    re.compile(r"^\["),  # [DNT] 등 개발자 placeholder
    re.compile(r"Breachstone", re.I),  # handled differently?
]


def load_bases() -> list[dict]:
    path = ROOT / "data" / "game_data" / "BaseItemTypes.json"
    return json.load(open(path, encoding="utf-8"))


def build_filter_basetypes(mode: str) -> set[str]:
    """generate_beta_overlay에서 BaseType == "..." 리스트 모두 추출."""
    text = generate_beta_overlay(mode=mode)
    bases: set[str] = set()
    # BaseType == "X" "Y" ... 패턴
    for m in re.finditer(r'BaseType\s*(?:==|=)?\s*((?:"[^"]+"\s*)+)', text):
        for name in re.findall(r'"([^"]+)"', m.group(1)):
            bases.add(name)
    # Class "X" 패턴도 수집 (클래스 단위 매칭은 BaseType 나열 없음)
    classes: set[str] = set()
    for m in re.finditer(r'Class\s*(?:==|=)?\s*((?:"[^"]+"\s*)+)', text):
        for name in re.findall(r'"([^"]+)"', m.group(1)):
            classes.add(name)
    return bases, classes


def categorize(item: dict) -> str:
    """아이템을 대분류로 그룹핑 (InheritsFrom 기반)."""
    inh = item.get("InheritsFrom", "")
    parts = inh.split("/")
    if len(parts) >= 4 and parts[:3] == ["Metadata", "Items", "Currency"]:
        return f"Currency/{parts[3] if len(parts) > 3 else ''}"
    if len(parts) >= 3:
        return "/".join(parts[2:4])
    return "Unknown"


def main() -> int:
    bases = load_bases()
    filter_bases, filter_classes = build_filter_basetypes(mode="ssf")

    print(f"필터가 매칭하는 BaseType 수: {len(filter_bases)}")
    print(f"필터가 매칭하는 Class 수: {len(filter_classes)}")
    print(f"Class 목록: {sorted(filter_classes)}")
    print()

    # 게임 내 모든 아이템을 카테고리별로 분류
    by_cat = defaultdict(list)
    for b in bases:
        name = b.get("Name", "").strip()
        if not name:
            continue
        if any(p.search(name) for p in SKIP_NAME_PATTERNS):
            continue
        inh = b.get("InheritsFrom", "")
        if any(inh.startswith(p) for p in SKIP_PREFIXES):
            continue
        by_cat[categorize(b)].append(name)

    # 각 카테고리에서 필터 매칭 안된 베이스 찾기
    report = []
    for cat in sorted(by_cat):
        items = by_cat[cat]
        unmatched = [n for n in items if n not in filter_bases]
        total = len(items)
        matched = total - len(unmatched)
        coverage = matched / total * 100 if total else 0
        report.append((coverage, cat, total, matched, unmatched))

    # Coverage 낮은 순 정렬
    report.sort(key=lambda x: (x[0], -x[2]))

    print("=" * 80)
    print("카테고리별 coverage (낮은 순):")
    print("=" * 80)
    for coverage, cat, total, matched, unmatched in report:
        flag = "❌" if coverage < 50 else "⚠️" if coverage < 90 else "✅"
        print(f"{flag} {cat:50s} {matched}/{total} ({coverage:5.1f}%)")
        if unmatched and coverage < 100:
            # 샘플 10개만 표시
            sample = unmatched[:10]
            print(f"    미매칭 샘플: {sample}")
            if len(unmatched) > 10:
                print(f"    ... +{len(unmatched)-10}개 더")
        print()

    # 완전 미매칭 카테고리 (0%) 강조
    critical = [r for r in report if r[0] == 0 and r[2] > 0]
    if critical:
        print("\n" + "=" * 80)
        print(f"🚨 완전 미매칭 카테고리 ({len(critical)}개):")
        print("=" * 80)
        for _, cat, total, _, unmatched in critical:
            print(f"  {cat}: {total}종 전부 unstyled 폴스루")
            for n in unmatched[:5]:
                print(f"    - {n}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
