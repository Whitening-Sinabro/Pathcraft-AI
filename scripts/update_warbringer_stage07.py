"""단계 플래너 `07 지도 성장 - 후기 목표` 의 젬과 본문을 88레벨 실측으로 맞춘다.

왜 07 만인가: 04~06 은 46~65레벨 구간이고 새 근거는 86~88레벨 관찰이다.
07 만 "후기 목표" 라서 제작자가 실제로 도달한 구성이 정답이다.

무엇을 안 건드리나: `passives`(126점 목표 트리)와 슬롯 좌표·추천 옵션 문구.
세트 배속도 안 건드린다 — poe.ninja 스냅샷의 PoB 내보내기는 스킬 그룹에
무기 슬롯을 기록하지 않아서, 어떤 스킬이 세트 I 인지 II 인지 근거가 없다.
그래서 기존 세트 구분은 그대로 두고, 이미 그 자리에 있는 줄만 고친다.

`.build` 는 본문을 두 곳에 담는다 — 최상위 `description` 과 장비 슬롯의
`additional_text`. 둘 다 고쳐야 한다. 한쪽만 고치면 게임 화면에서 옛 글이 남는다.

치환은 줄 단위 완전 일치다. 부분 일치로 하면 옛 줄이 새 줄의 앞부분이라서
재실행 때마다 보조 젬이 한 번씩 더 붙는다(실제로 한 번 그렇게 망가뜨렸다).

근거: `deliverables/skadoosh_vod_2871483565_2026-09-12/creator_latest.json`
      (poe.ninja SkadooshShoutedHard 88레벨, 2026-09-12 08:03 갱신)
      + VOD 2869701205 / 2871483565 전체 전사
한국어 젬 이름: `data/merged_translations.json` 과 이 플래너의 기존 표기에서만 가져온다.
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import pathlib
import sys

log = logging.getLogger("stage07")

GAME_DIR = pathlib.Path(os.path.expandvars(
    r"%USERPROFILE%\Documents\My Games\Path of Exile 2\BuildPlanner"))
REPO_DIR = pathlib.Path("deliverables/skadoosh_early_survival_2026-09-08/BuildPlanner")
FILE = "07 지도 성장 - 후기 목표.build"

DROP_ACTIVES = {
    "Metadata/Items/Gems/SkillGemPurityOfFire",       # 실측은 번개의 순수함이다
    "Metadata/Items/Gem/SkillGemResonatingShield",    # 88레벨 구성에 없다
}
ADD_ACTIVES = [
    "Metadata/Items/Gems/SkillGemPurityOfLightning",
    "Metadata/Items/Gems/SkillGemPurityOfLightning",  # 세트마다 하나씩
    "Metadata/Items/Gem/SkillGemAscendancyEncasedInJade",
    "Metadata/Items/Gem/SkillGemScavengedPlating",
    "Metadata/Items/Gems/SkillGemSunder",
    "Metadata/Items/Gems/SkillGemLeapSlam",
]

# (옛 줄, 새 줄). 새 줄이 None 이면 그 줄을 지운다. 줄 단위 완전 일치.
LINE_FIXES: list[tuple[str, str | None]] = [
    ("기본 이동: 보강하는 함성(I)을 쓰고 이동하며 메아리·타락한 피를 이어간다. 그 사이 지진 함성(I)으로 시체 폭발·격노와 가시 폭발을 보탠다.",
     "기본 이동: 86~88레벨 방송에서는 지진 함성(I)을 계속 누르며 이동하고 토템은 가끔 보충해 5기를 유지한다. 보강하는 함성(I)은 파콰테를 물려 백색·대부분의 청색 몹 청소를 맡는다. 이 역할 분담은 86레벨 이후 관찰이다."),
    ("전사 토템(II) → 함성(I). 지면 분쇄는 전사 토템 내부에 넣는다. 불의 순수함 두 항목은 각각의 셉터 세트에 지정한다.",
     "전사 토템(II) → 함성(I). 지면 분쇄는 전사 토템 내부에 넣는다. 번개의 순수함 두 항목은 각각의 셉터 세트에 지정한다."),
    ("불의 순수함 → 활력 II + 식인 II + 따뜻한 피",
     "번개의 순수함 → 활력 II + 식인 II + 따뜻한 피 + 정밀함 II"),
    ("불의 순수함 → 활력 I + 정밀함 II",
     "번개의 순수함 → 활력 I + 정밀함 I"),
    ("공명하는 방패 → 격노 I + 방어구 철거자 I", None),
    ("보강하는 함성 → 파콰테의 맹약 + 메아리치는 함성 + 포악함 II + 고통 격화 II",
     "보강하는 함성 → 파콰테의 맹약 + 메아리치는 함성 + 포악함 II + 고통 격화 II + 물리 숙련"),
    ("지진 함성 → 우주의 영사 + 효율 II + 격노하는 함성",
     "지진 함성 → 우주의 영사 + 효율 II + 격노하는 함성 + 기동성"),
    ("선대의 전사 토템 → 지면 분쇄 [내부 액티브 젬] + 긴급한 토템 III + 파생하는 균열 I + 포악함 III",
     "선대의 전사 토템 → 지면 분쇄 [내부 액티브 젬] + 긴급한 토템 III + 파생하는 균열 II + 포악함 III + 출혈 IV"),
    ("선대의 혼백 → 연결 보조 없음",
     "선대의 혼백 → 육탄 방어 II + 힘줄 절단 + 실명 II + 방어구 파괴 I"),
    # Magnified Area 는 레포에 한국어 표기가 없다. 지어내지 않고 영문으로 둔다.
    ("광기의 선구자 → 연결 보조 없음",
     "광기의 선구자 → Magnified Area II"),
    ("이번 리그 제작자 74레벨 공개 스냅샷의 패시브와 젬 연결 목표. 메타 젬은 공식 형식 제약 때문에 별도 획득 항목으로 표시한다. 75레벨 최신 조회에서는 일부 젬이 더 올라갔으므로 시점을 섞지 않았다.",
     "패시브는 이번 리그 제작자 74레벨 공개 스냅샷 목표 그대로다. 젬 연결은 88레벨 공개 스냅샷(2026-09-12 08:03 갱신) 실측으로 바꿨다. 트리와 젬의 시점이 다르므로 섞어 읽지 않는다. 메타 젬은 공식 형식 제약 때문에 별도 획득 항목으로 표시한다."),
]

# 세트 배속 근거가 없어서 세트 목록에 넣지 않고 따로 적는 88레벨 실측 액티브.
APPEND_AFTER = ("자동 부여", [
    "",
    "88레벨 실측에 있고 이 문서에 자리가 없던 것 (세트 배속은 근거 없음)",
    "주운 판금 → 지속시간 연장 II",
    "비취에 갇힘 → 빠른 시전 II + 지속시간 연장 II",
    "Sunder → 지속시간 연장 II + 빠른 공격 III + 치고 빠지기 + 파생하는 균열 II",
    "도약 강타 → 연결 보조 없음",
])


def fix_lines(text: str, hits: list[str]) -> str:
    lines = text.split("\n")
    out: list[str] = []
    for line in lines:
        replaced = False
        for old, new in LINE_FIXES:
            if line.strip() == old:
                hits.append(old)
                if new is not None:
                    out.append(line.replace(old, new))
                replaced = True
                break
        if not replaced:
            out.append(line)
    anchor, extra = APPEND_AFTER
    if anchor in out and extra[1] not in out:
        idx = max(i for i, l in enumerate(out) if l.strip() == anchor)
        end = idx + 1
        while end < len(out) and out[end].strip():
            end += 1
        out[end:end] = extra
        hits.append(anchor)
    return "\n".join(out)


def update(path: pathlib.Path, dry: bool) -> dict:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    passives_before = json.dumps(data["passives"], ensure_ascii=False, sort_keys=True)

    kept = [s for s in data["skills"] if s["id"] not in DROP_ACTIVES]
    dropped = len(data["skills"]) - len(kept)
    have = [s["id"] for s in kept]
    added = []
    for gem in ADD_ACTIVES:
        if have.count(gem) < ADD_ACTIVES.count(gem):
            kept.append({"id": gem, "level_interval": [1, 100]})
            have.append(gem)
            added.append(gem)
    data["skills"] = kept

    hits: list[str] = []
    if data.get("description"):
        data["description"] = fix_lines(data["description"], hits)
    for slot in data.get("inventory_slots", []):
        if slot.get("additional_text"):
            slot["additional_text"] = fix_lines(slot["additional_text"], hits)

    if json.dumps(data["passives"], ensure_ascii=False, sort_keys=True) != passives_before:
        raise SystemExit(f"{path.name}: 패시브가 바뀌었다 — 젬과 본문만 고쳐야 한다")

    # 잔존 검사도 줄 단위다. 옛 줄이 새 줄의 앞부분이라 부분 일치로 보면 항상 걸린다.
    seen: set[str] = set()
    for text in [data.get("description") or ""] + [
            s.get("additional_text") or "" for s in data.get("inventory_slots", [])]:
        seen.update(line.strip() for line in text.split("\n"))
    stale = [old for old, _ in LINE_FIXES if old in seen]
    if not dry:
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"path": str(path), "dropped": dropped, "added": added,
            "hits": hits, "stale": stale, "skills": len(data["skills"])}


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    failed = False
    for d in (GAME_DIR, REPO_DIR):
        path = d / FILE
        if not path.exists():
            raise SystemExit(f"없는 플래너: {path}")
        r = update(path, args.dry_run)
        log.info("%s", r["path"])
        log.info("  액티브 제거 %d · 추가 %d · 최종 %d · 줄 수정 %d",
                 r["dropped"], len(r["added"]), r["skills"], len(r["hits"]))
        if r["stale"]:
            failed = True
            log.error("  옛 문구가 남았다 %d줄:", len(r["stale"]))
            for old in r["stale"]:
                log.error("    %s", old[:70])
    if failed:
        return 1
    log.info("완료%s", " (dry-run)" if args.dry_run else "")
    return 0


if __name__ == "__main__":
    sys.exit(main())
