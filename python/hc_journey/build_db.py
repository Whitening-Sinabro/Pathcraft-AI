"""PathcraftAI HC Journey DB — 스키마 생성 + 다중 크리에이터 적재 + 여정 질의.

POE2 하드코어 니치. 크리에이터별 발행 밴드 PoB + 실캐릭 ninja 스냅샷을 diff 해서
'따라 할 여정'(WHAT/WHEN)을 자동 생성하고, VOD/연구/실측에서 뽑은 비용·조건·함정·왜(20%)를
transition_note 로 붙인다. 자동층과 큐레이션층을 물리적으로 분리한다.

입력 .build 는 data/hc_journey/creators/<slug>/ 에 커밋된 픽스처를 쓴다(재현 가능).

사용:
    python -X utf8 python/hc_journey/build_db.py --build
    python -X utf8 python/hc_journey/build_db.py --query          # 전체 빌드 여정
    python -X utf8 python/hc_journey/build_db.py --query --id 2   # 특정 빌드
"""
from __future__ import annotations

import argparse
import json
import re
import sqlite3
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
DB_PATH = REPO / "data" / "hc_journey" / "pathcraft_hc.db"
CREATORS_DIR = REPO / "data" / "hc_journey" / "creators"
SCHEMA = HERE / "schema.sql"
TRADE_LINKS = REPO / "data" / "hc_journey" / "trade_links.json"          # trade_links.py 산출물(커밋됨)
TRADE_LIVE_GLOB = "trade_links_live_*.json"                               # --live 결과(검색 id·매물 수), 있으면 병합


def load_trade_links(path: Path | None = None, live_dir: Path | None = None) -> dict[tuple, dict]:
    """{(creator, transition_idx, slot): entry}. live 파일이 있으면 같은 키·tier·realm 의 live 결과를 얹는다.
    파일이 없으면 빈 dict — DB 적재는 네트워크·캐시 없이도 돌아야 한다."""
    path = path or TRADE_LINKS   # 호출 시점에 읽어야 테스트가 경로를 바꿀 수 있다
    if not path.exists():
        return {}
    doc = json.loads(path.read_text(encoding="utf-8"))
    out = {(e["creator"], e["transition_idx"], e["slot"]): e for e in doc.get("entries", [])}
    live_dir = live_dir or path.parent
    for lp in sorted(live_dir.glob(TRADE_LIVE_GLOB)):
        merge_live(out, json.loads(lp.read_text(encoding="utf-8")))
    return out


def merge_live(out: dict[tuple, dict], ldoc: dict) -> int:
    """live 결과를 같은 (creator, idx, slot, tier) 이면서 **쿼리 JSON 이 같을 때만** 얹는다.
    매물 수는 그 쿼리의 것이다 — 사다리 임계를 바꾸면 옛 숫자는 버려져야 한다. 반환: 얹은 (tier, realm) 수."""
    checked = ldoc.get("_meta", {}).get("generated_utc")
    n = 0
    for le in ldoc.get("entries", []):
        e = out.get((le["creator"], le["transition_idx"], le["slot"]))
        if not e:
            continue
        by_tier = {t["tier"]: t for t in e["tiers"]}
        for lt in le["tiers"]:
            t = by_tier.get(lt["tier"])
            if t is None or "live" not in lt:
                continue
            if json.dumps(lt.get("query"), sort_keys=True) != json.dumps(t.get("query"), sort_keys=True):
                continue  # 쿼리가 달라졌다 — 이 매물 수는 지금 링크의 것이 아니다
            t.setdefault("live", {})
            for realm, res in lt["live"].items():
                t["live"][realm] = {**res, "checked_utc": checked}
                n += 1
    return n


def _short(gid: str) -> str:
    base = gid.rsplit("/", 1)[-1]
    return re.sub(r"^(SkillGem|SupportGem|Skill|Support)", "", base) or gid


def load_build(path: Path) -> dict:
    d = json.loads(path.read_text(encoding="utf-8"))
    skills = {}
    for s in d.get("skills", []):
        skills[_short(s.get("id", ""))] = [_short(x.get("id", "")) for x in s.get("support_skills", [])]
    items = {sl.get("inventory_id"): (sl.get("additional_text", "") or "").split("\n")[0].strip()
             for sl in d.get("inventory_slots", [])}
    ps = d.get("passives")
    return {"skills": skills, "items": items,
            "passives_n": len(ps) if isinstance(ps, list) else None, "ascendancy": d.get("ascendancy")}


def diff_snapshots(a: dict, b: dict) -> list[tuple[str, str, str]]:
    out: list[tuple[str, str, str]] = []
    sa, sb = a["skills"], b["skills"]
    for k in sb:
        if k not in sa:
            out.append(("skill_added", k, f"스킬 추가: {k}"))
    for k in sa:
        if k not in sb:
            out.append(("skill_removed", k, f"스킬 제거: {k}"))
    for k in sb:
        if k in sa and set(sb[k]) != set(sa[k]):
            new = sorted(set(sb[k]) - set(sa[k]))
            gone = sorted(set(sa[k]) - set(sb[k]))
            if new or gone:
                out.append(("support_changed", k, f"{k} 보조 +{new} -{gone}"))
    ia, ib = a["items"], b["items"]
    for slot, v in ib.items():
        if ia.get(slot) != v and (v or ia.get(slot)):
            out.append(("item_changed", slot, f"{slot}: {ia.get(slot) or '-'} -> {v or '-'}"))
    pa, pb = a.get("passives_n"), b.get("passives_n")
    if pa is not None and pb is not None and pa != pb:
        out.append(("passive_delta", "passives", f"배정 패시브 {pa} -> {pb} (+{pb - pa})"))
    return out


# --- 재사용 큐레이션 규칙 (초반 손노동을 여기로 뽑아내면 이후 빌드에 자동 적용) ---
# (trigger_kind, trigger_key, note_type, text, evidence)
CURATION_RULES = [
    # 키스톤 — 한 번 쓰면 그 키스톤을 든 모든 빌드에 자동으로 붙는다.
    ("keystone", "Blackflame Covenant", "why",
     "검은화염 계약(툴팁 3줄): ①화염 주문의 화염 피해 100%를 카오스로 전환 ②화염 주문의 카오스 피해가 인화성·점화 강도에 반영 "
     "③화염 주문의 점화가 화염 대신 카오스 피해. 화염 저항 계산·화염 증폭 장비 값이 통째로 바뀐다.",
     "규칙(임성빈 E 8876·F 75초 툴팁 판독)"),
    ("keystone", "Blood Magic", "why",
     "혈마법: 마나 대신 생명력으로 스킬 비용 지불. 마나 예약·회복 설계가 통째로 바뀐다. HC에서 생명력 관리가 곧 자원 관리.", "규칙(Skadoosh ninja 실측)"),
    ("keystone", "Ancestral Bond", "why",
     "선대의 유대: 토템만 피해를 준다(본인 직접 타격 불가). 토템 중심 빌드의 전제 — 딜 스킬을 직접 쓰지 않는다.", "규칙(Skadoosh ninja 실측)"),
    # 스킬 도입 — 그 스킬을 쓰는 어떤 빌드든 자동으로 붙는다.
    ("skill_added", "Flameblast", "condition",
     "화염파는 집중 유지형 주문 — 마나가 초당 빠지고 재사용 대기시간이 길다. 요구 지능이 높아 능력치 세팅을 먼저 맞춰야 한다.", "규칙(임성빈 C4767 실측)"),
    # 장비 슬롯 변화 — 세트 II 무기가 생기는 어떤 빌드든 자동으로 붙는다.
    ("item_slot_change", "Weapon2", "why",
     "세트 II(두 번째 무기) 도입: 세트 전용 패시브는 세트 II 에만 넣어야 주력에서 먹는다. R2 로 세트 전환.", "규칙(임성빈 C9787 실측)"),
    # 어센던시 — 그 전직을 쓰는 모든 빌드에 자동.
    ("ascendancy", "Gemling Legionnaire", "why",
     "젬링 리저네어: 젬 레벨·능력치 보너스 중심 전직. 능력치 투자가 곧 딜이자 보조 젬 슬롯(보조 상한 = 능력치 ÷ 5).", "규칙(임성빈 실측)"),
    ("ascendancy", "Warbringer", "why",
     "워브링어: 함성·토템 중심 전사 어센던시. 함성으로 버프/발동을 굴리고 토템으로 딜을 낸다.", "규칙(Skadoosh 실측)"),
    # 추가 키스톤/스킬 규칙 — 커버리지 확장(신규 빌드가 더 많이 상속).
    ("keystone", "Blackflame Covenant", "survival",
     "화염 피해가 카오스가 되므로 적의 화염 저항이 무의미해지고 카오스 저항·관통이 중요해진다. 몬스터 카오스 저항이 높으면 딜이 빠진다.", "규칙(카오스 전환 메커니즘)"),
    ("skill_added", "CastOnElementalAilment", "why",
     "발동형 메타 스킬(툴팁): 동결 위세당 에너지 10, 점화·감전 위세당 1(점화는 상태 이상 한계치 비율로 조정), 에너지 획득 51% 증가(Lv17·퀄리티 0 관측). "
     "최대 에너지 도달 시 장착된 모든 주문을 발동하고 에너지를 전부 잃음. 장착 주문 기본 시전 시간 0.1초당 최대 에너지 10 — 느린 주문일수록 최대치가 크다.",
     "규칙(임성빈 F 207초 툴팁 판독)"),
    ("skill_added", "ShockwaveTotem", "condition",
     "토템 배치 스킬 — 재설치·위치가 딜에 직결. 선대의 유대 계열이면 유일 딜원이라 토템 생존이 곧 딜이다.", "규칙(토템 운용)"),
    ("skill_added", "Despair", "why",
     "저주(절망). 기본은 저주 1개만 활성 — 2개를 쓰려면 관련 패시브(멸망 등)가 필요하다.", "규칙(임성빈 D19366 발언)"),
    # --- 2026-09-10 규칙 자동 초안 #1 채택분 (판정 기록: data/hc_journey/rule_decisions.json) ---
    ("keystone", "Blackflame Covenant", "pitfall",
     "임성빈 발언: 검은화염 계약을 찍으면 '화염 피해 % 증가' 옵션이 이 스킬에 적용되지 않는다 — 점화 강도·상태 이상 강도·카오스 피해로 챙길 것. "
     "스킬 레벨은 화염 스킬 레벨도 되지만 카오스 % 가 안 나오므로 '모든 주문 스킬 레벨'이 낫다. '피해의 X%를 추가 화염 피해로 획득'(gain) 접사는 괜찮다.",
     "규칙(임성빈 F 2319~2401초 발언)"),
    ("keystone", "Blackflame Covenant", "condition",
     "점화에 의존하는 검은화염 빌드는 0.5.1 핫픽스 5(키스톤의 '화염 주문 점화 → 카오스' 판정을 카오스 피해 가능 여부로 수정) 이후에야 성립 — 그 전엔 버그. "
     "대안인 Blackflame 유니크 반지 경로는 희귀 반지 슬롯 하나를 포기한다(임성빈 발언) — 키스톤 경로는 패시브로 지불.",
     "규칙(패치노트 3955108 + 임성빈 E 8818~8889초 발언)"),
    ("ascendancy", "Gemling Legionnaire", "condition",
     "젬링 전직 트리: 작은 노드 = 장비·스킬 젬 능력치 요구 4% 감소, 미덕의 정수 = 고결한 방어막 스킬 부여. "
     "임성빈은 43레벨 첫 2포인트를 이 순서로 배정(그의 시점이지 게임 조건은 아님).",
     "규칙(임성빈 B 6410~6422초 판독)"),
    ("skill_added", "AscendancyVirtuousBarrier", "why",
     "고결한 방어막(미덕의 정수 부여, 유지형 버프, Lv19 툴팁 관측): 1.55초마다 무작위 티끌 획득, 명중당하면 무작위 티끌 하나 잃음. "
     "능력치별 최대치 = 3 + 그 능력치를 요구하는 보유 스킬 수(단일 능력치 스킬은 2배). "
     "힘 티끌당 생명력 최대치 +2%, 민첩 티끌당 방어도·회피·ES +5%, 지능 티끌당 생명력·마나 재생 +5%.",
     "규칙(임성빈 D 19306초 툴팁 판독, 손노트 승격)"),
    ("skill_added", "Flameblast", "why",
     "화염파(툴팁): 집중 유지형 주문, 단계당 주문 피해 75% 증폭·최대 10단계, 폭발 반경 단계당 0.6m, 재사용 대기 10초(Lv13·Lv19 동일). "
     "초당 마나 소모 Lv13 27.8, Lv19 52.1(퀄리티 20%·시전 속도 24% 증폭 상태 — 시전 속도가 비용에도 영향). 요구 Lv13 52레벨·지능 92, Lv19 84레벨·지능 147.",
     "규칙(임성빈 C 4540·4767·F 160초 툴팁 판독)"),
    ("skill_added", "Tornado", "why",
     "회오리(툴팁 Lv14): 적을 빨아들이며 지속 물리 피해를 주는 폭풍. 원소 지대와 겹치면 그 지대의 디버프를 흡수해 안의 적에게 해당 원소 추가 피해. "
     "요구 58레벨·힘 57·지능 57, 마나 59, 시전 0.75초.",
     "규칙(임성빈 E 15150초 툴팁 판독)"),
    ("skill_added", "Tornado", "pitfall",
     "흡수의 양날: GGPK 원문대로 겹친 원소 지대의 디버프를 흡수해 안의 적에게 적용한다. 기름 유탄 약한 점화 빌드에선 약한 점화가 지대로 번지는 오염이 된다"
     "(아르세리나 직접 테스트 추론, .claude/status/poe2_hc_gemling.md — 구르기 연결 자동 시전이 제일 위험하다는 것도 그 발언). "
     "임성빈은 '제일 불편했던 회오리'를 한때 뺐다가 같은 방송에서 다시 넣어 Lv90 빌드에 남겼는데, 그가 밝힌 이유는 전염이 못 번지는 "
     "공중 몹 처리다(카오스 장판 흡수 활용은 판독자 추정일 뿐 발언 없음).",
     "규칙(GGPK tornado 설명 + .claude/status/poe2_hc_gemling.md + 임성빈 E 13039·15101~15135초 발언, E 15150·F 160초 판독)"),
    ("skill_added", "CastOnElementalAilment", "condition",
     "원소 상태 이상 시 시전(Lv17 툴팁): 요구 72레벨·지능 126. 툴팁의 '점유 100 정신력' 표기가 같은 방송 HUD(7/100·11/100)와 맞지 않아 "
     "실제 점유량은 미확인 — 장착 전 정신력 여유를 직접 확인할 것.",
     "규칙(임성빈 F 207초 툴팁 판독, 점유량 불일치는 판독 한계 원문)"),
    ("item_slot_change", "Helm1", "condition",
     "방어구 교체 시 요구 능력치 미충족이면 장착돼 있어도 비활성(빨간 슬롯·'아이템 효과 미적용'). "
     "임성빈은 요구 지능 36 미달인 왕관이 비활성이었고 지능을 32→37로 올리자 활성됐다. 능력치 노드·장비로 요구를 먼저 채울 것.",
     "규칙(임성빈 B 9380~9398초 판독·발언)"),
    ("item_slot_change", "Weapon1", "pitfall",
     "무기 교체 시 무기 유형에 묶인 스킬은 '충족되지 않은 스킬 요구사항: 잘못된 무기 유형'으로 죽는다(임성빈: 석궁→지팡이 전환 때 급습 제거). "
     "요구 레벨·힘·민첩과 함께 스킬별 무기 제한을 먼저 확인할 것.",
     "규칙(임성빈 C 4755~4763초 판독)"),
    ("item_slot_change", "Flask1", "survival",
     "생명력 플라스크 교체 기준(임성빈 발언, 37레벨): 회복량보다 '즉시 회복'이 진짜 중요하다 — 가르강튀아 생명력 플라스크는 요구 40레벨이라 "
     "그 전엔 낄 게 없다. 실캐릭 lv93 플라스크도 Instant Recovery(회복량 50% 감소 감수).",
     "규칙(임성빈 B 1920초 판독 · B 1927~1942초 발언 · 05_live_lv93.build Flask1)"),
    # --- 리그 모드 트리거 (league/trade | league/ssf) — 슬롯 무관 거래 지식은 여기. 빌드 첫 전환에 한 번 붙는다. ---
    ("league", "trade", "cost",
     "거래소 즉시 구입 = 오브 단위 가격(엑잘티드·신성한 오브 등, 매물마다 다름) + 매물별 골드 수수료. 임성빈 사례: 장화 1 엑잘 + 3211골드(구입 직후 골드 "
     "26725→23514 로 수수료 실차감), 57레벨 투구 열람 매물 1 엑잘 + 10737~11314골드, 88레벨 투구 업그레이드 매물 25 엑잘 + 35836골드·1 신성 + 41751골드. "
     "화폐 교환 주문에도 수수료가 표시된다(2000·1000·3200골드, 체결 전 화면). 오브만 보고 예산을 잡으면 골드가 빈다 — 후반은 수수료가 3~4만 골드 단위.",
     "규칙(임성빈 B 2000~2020 · C 9000·9040 · E 9000 · D 2650 · E 14710·14820초 판독)"),
    ("league", "trade", "pitfall",
     "요구 레벨·능력치가 빨간 매물은 사도 껴도 비활성(효과 미적용)이다(임성빈 C 9000: 첫 매물 요구 59, 당시 57레벨; E 9000: 요구 80 매물). "
     "검색 패널의 요구사항 상한(45 이하)을 걸었는데도 59·80 매물이 표시된 화면이 있으니 필터를 믿지 말고 매물마다 요구 레벨을 직접 보고 빨간 것은 거른다.",
     "규칙(임성빈 C 8990·9000·9040 · E 9000초 판독)"),
    ("league", "trade", "condition",
     "거래소 검색 요령(임성빈): 유형·희귀도·퀄리티 하한·방어구/ES 하한·요구사항·능력치 필터를 걸고, 결과가 0이면 능력치 필터를 한 줄로 줄인다(4줄 0건 → 1줄 13건). "
     "후보가 뜨면 정렬을 '총 ES 높은 것부터'로 바꿔 고른다. 판매자 유형은 '즉시 구입'.",
     "규칙(임성빈 C 8990→9000→9040 · E 9000초 판독)"),
]


# --- 크리에이터 설정 (다중 적재) ----------------------------------------------
# keystones: ninja 실측(keystone 규칙 매칭용). notes: 그 빌드 고유의 손노동만(초반 창).
CREATORS = [
    {
        "name": "임성빈", "channel": "https://www.youtube.com/@임성빈", "ninja": "dtq03087-0345",
        "build": {"name": "젬링 화염파 -> 검은화염 카오스", "asc": "Gemling Legionnaire",
                  "league": "hc-forbidden-rites", "ssf": 0,
                  "notes": "유탄 육성 -> 52 화염파 전환 -> 검은화염 카오스"},
        "keystones": ["Blackflame Covenant"],
        "bands": [
            ("ACT1", 12, "planner_band", "seongbin/01_ACT1.build"),
            ("ACT2", 22, "planner_band", "seongbin/02_ACT2.build"),
            ("ACT3-4", 45, "planner_band", "seongbin/03_ACT34.build"),
            ("엔드게임(계획)", None, "planner_band", "seongbin/04_endgame_plan.build"),
            ("실캐릭 lv93", 93, "ninja_live", "seongbin/05_live_lv93.build"),
        ],
        # 손노트 = 그 빌드에만 해당하는 고유 수치·함정·오프스트림. (일반 지식은 규칙으로 이동됨)
        "notes": {
            # 0: 고결한 방어막 버프 손노트(D 19306)는 2026-09-10 규칙(skill_added/AscendancyVirtuousBarrier/why)으로 승격.
            2: [
                ("cost", "화염파 전환 리스펙 준비 골드 순감소 약 50396. 재분배 뒤에도 일반 20포인트 남음.", "C 4550·4725초"),
                ("condition", "화염파 요구 지능 92를 맞춰야 함(47->92), 요구 레벨 52.", "C 4540·4767초"),
                ("pitfall", "무기를 지팡이로 바꾸면 급습이 '잘못된 무기 유형'으로 죽음 -> 제거, 임시 합금 석궁 대체.", "C 4760·4755초"),
                ("cost", "투구 실지불가 = 1 엑잘티드 + 골드 수수료(약 10737~11314). 요구 빨간 매물 착용 불가.", "C 9000초"),
            ],
            3: [
                ("cost", "90레벨 재분배로 시작, 골드 211147->145094(약 66053 감소). 무기 세트 포인트도 반환.", "F 30·90초"),
                ("survival", "카오스 저항 챙김(lv93 카오스 65). 후반은 생명력이 아니라 에너지 보호막 중심.", "실캐릭 defensiveStats"),
                ("offstream", "세트 II 용의 돛대(동결 축적78%) 획득 순간이 방송에 없음 -> 오프스트림 구매 추정.", "F 2400초 장착"),
            ],
        },
    },
    {
        "name": "Skadoosh", "channel": "https://www.youtube.com/@Skadoosh", "ninja": "ITheCon-2183",
        "build": {"name": "워브링어 타락 함성 토템", "asc": "Warbringer",
                  "league": "hc-forbidden-rites", "ssf": 0,
                  "notes": "충격파 토템 + Corrupting Cry, 혈마법. (임성빈과 다른 어센던시)"},
        "keystones": ["Ancestral Bond", "Blood Magic"],
        "bands": [
            ("Lv01-10", 10, "planner_band", "skadoosh/01_Lv01-10.build"),
            ("Lv11-20", 20, "planner_band", "skadoosh/02_Lv11-20.build"),
            ("Lv21-30", 30, "planner_band", "skadoosh/03_Lv21-30.build"),
            ("Lv31-41", 41, "planner_band", "skadoosh/04_Lv31-41.build"),
            ("실캐릭 live", 86, "ninja_live", "skadoosh/05_live.build"),
        ],
        # 손노동 아직 0. 큐레이션은 전부 규칙(키스톤 등)에서 자동 상속 — 이게 확장의 핵심.
        "notes": {},
    },
    # --- 같은 빌드(화염파 젬링)의 다른 제작자 2명 — "같은 빌드도 내부가 갈린다" 대조용. 손노동 0, 규칙 상속만. ---
    {
        "name": "ds lily", "channel": "https://mobalytics.gg/poe-2/profile/ds_lily/builds/oil-flameblast-gemling", "ninja": None,
        "build": {"name": "기름 유탄 화염파 젬링 (ds lily)", "asc": "Gemling Legionnaire",
                  "league": "hc-forbidden-rites", "ssf": 0,
                  "notes": "Mobalytics 5탭(Lvl 25/47/51/72/93). Lvl 51 탭은 패시브만 있어(스킬·장비 없음) 밴드에서 제외 — "
                           "화염파 전환은 47→72 구간으로 잡힌다. 릴리리그(사설 HC GSF) 운영자(명부). 키스톤은 ninja 미확보로 비움."},
        "hardcore": 1,
        "keystones": [],
        "bands": [
            ("Lvl25", 25, "planner_band", "dslily/01_Lvl25.build"),
            ("Lvl47", 47, "planner_band", "dslily/02_Lvl47.build"),
            ("Lvl72", 72, "planner_band", "dslily/04_Lvl72.build"),
            ("Lvl93", 93, "planner_band", "dslily/05_Lvl93.build"),
        ],
        "notes": {},
    },
    {
        "name": "Fubgun", "channel": "https://mobalytics.gg/poe-2/builds/fubgun-flameblast-oil-grenade", "ninja": None,
        "build": {"name": "화염파 기름 유탄 젬링 (Fubgun)", "asc": "Gemling Legionnaire",
                  "league": "hc-forbidden-rites", "ssf": 0,
                  "notes": "Mobalytics 7탭. 하코 명부에 없는 일반 가이드(리그 표기 미확인, 페이지 403) — hardcore=0. "
                           "임성빈 HC 필터의 보조 소스로 쓰였던 가이드. 키스톤은 ninja 미확보로 비움."},
        "hardcore": 0,
        "keystones": [],
        "bands": [
            ("lvl 1-14", 14, "planner_band", "fubgun/01_lvl1-14.build"),
            ("lvl 15-32", 32, "planner_band", "fubgun/02_lvl15-32.build"),
            ("lvl 33-51", 51, "planner_band", "fubgun/03_lvl33-51.build"),
            ("lvl 52 Swap", 52, "planner_band", "fubgun/04_lvl52_swap.build"),
            ("lvl 53-68", 68, "planner_band", "fubgun/05_lvl53-68.build"),
            ("lvl 85", 85, "planner_band", "fubgun/06_lvl85.build"),
            ("Endgame", None, "planner_band", "fubgun/07_endgame.build"),
        ],
        "notes": {},
    },
]


def build() -> dict:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    if DB_PATH.exists():
        DB_PATH.unlink()
    con = sqlite3.connect(DB_PATH)
    con.executescript(SCHEMA.read_text(encoding="utf-8"))

    # 규칙 라이브러리 적재 (한 번 정의 -> 모든 빌드에 자동 적용).
    # 한 트리거에 note_type 이 다른 규칙이 여러 개일 수 있어 (kind,key) -> [rule_id...] 로 담는다.
    rule_ids: dict = {}
    for kind, key, nt, text, ev in CURATION_RULES:
        cur = con.execute(
            "INSERT INTO curation_rule(trigger_kind, trigger_key, note_type, text, evidence_ref) VALUES(?,?,?,?,?)",
            (kind, key, nt, text, ev))
        rule_ids.setdefault((kind, key), []).append(cur.lastrowid)

    def add_rule_note(trans_id, kind, key):
        n = 0
        for r in rule_ids.get((kind, key), []):
            if con.execute("SELECT 1 FROM transition_note WHERE transition_id=? AND rule_id=?",
                           (trans_id, r)).fetchone():
                continue  # 같은 규칙을 같은 전환에 중복으로 붙이지 않는다.
            rr = con.execute("SELECT note_type, text, evidence_ref FROM curation_rule WHERE id=?", (r,)).fetchone()
            con.execute("INSERT INTO transition_note(transition_id, note_type, text, evidence_ref, source, rule_id) "
                        "VALUES(?,?,?,?,'rule',?)", (trans_id, rr[0], rr[1], rr[2], r))
            n += 1
        return n

    trade = load_trade_links()

    def add_trade(change_id, creator, idx, slot):
        e = trade.get((creator, idx, slot))
        if not e:
            return 0
        it = e["item"]
        con.execute("INSERT INTO trade_target(change_id, base, unique_base, category, level_max, mods_json, mapped_json, unmapped_json) "
                    "VALUES(?,?,?,?,?,?,?,?)",
                    (change_id, it["first"], it.get("unique_base"), it.get("category"), e.get("level_max"),
                     json.dumps(it["mods"], ensure_ascii=False), json.dumps(it["mapped"], ensure_ascii=False),
                     json.dumps(it["unmapped"], ensure_ascii=False)))
        n = 0
        for t in e["tiers"]:
            for realm, url in t["links"].items():
                live = (t.get("live") or {}).get(realm) or {}
                con.execute("INSERT INTO trade_link(change_id, tier, label, note, realm, url, query_json, live_id, live_total, "
                            "live_url, live_checked_utc) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                            (change_id, t["tier"], t["label"], t.get("note"), realm, url,
                             json.dumps(t["query"], ensure_ascii=False, separators=(",", ":")),
                             live.get("id"), live.get("total"), live.get("url"), live.get("checked_utc")))
                n += 1
        return n

    for cfg in CREATORS:
        cur = con.execute("INSERT INTO creator(name, channel_url, ninja_account) VALUES(?,?,?)",
                          (cfg["name"], cfg["channel"], cfg["ninja"]))
        creator_id = cur.lastrowid
        b = cfg["build"]
        cur = con.execute(
            "INSERT INTO build(creator_id, game, league, hardcore, ssf, name, ascendancy, notes) "
            "VALUES(?,?,?,?,?,?,?,?)",
            (creator_id, "poe2", b["league"], cfg.get("hardcore", 1), b["ssf"], b["name"], b["asc"], b["notes"]))
        build_id = cur.lastrowid
        for ks in cfg.get("keystones", []):
            con.execute("INSERT INTO build_keystone(build_id, keystone) VALUES(?,?)", (build_id, ks))

        snaps = []
        for order_idx, (label, lvl, stype, rel) in enumerate(cfg["bands"]):
            data = load_build(CREATORS_DIR / rel)
            cur = con.execute(
                "INSERT INTO snapshot(build_id, order_idx, stage_label, level_hint, source_type, "
                "source_ref, passives_n) VALUES(?,?,?,?,?,?,?)",
                (build_id, order_idx, label, lvl, stype, rel, data["passives_n"]))
            sid = cur.lastrowid
            for main, sup in data["skills"].items():
                con.execute("INSERT INTO snapshot_skill(snapshot_id, main_gem, supports) VALUES(?,?,?)",
                            (sid, main, json.dumps(sup, ensure_ascii=False)))
            for slot, nm in data["items"].items():
                con.execute("INSERT INTO snapshot_item(snapshot_id, slot, item_name) VALUES(?,?,?)", (sid, slot, nm))
            snaps.append((sid, data))

        trans_ids = []
        for i in range(len(snaps) - 1):
            (fid, fa), (tid, tb) = snaps[i], snaps[i + 1]
            cur = con.execute(
                "INSERT INTO transition(build_id, order_idx, from_snapshot, to_snapshot) VALUES(?,?,?,?)",
                (build_id, i, fid, tid))
            trans_id = cur.lastrowid
            trans_ids.append(trans_id)
            for kind, subject, detail in diff_snapshots(fa, tb):
                cur = con.execute("INSERT INTO transition_change(transition_id, kind, subject, detail) VALUES(?,?,?,?)",
                                  (trans_id, kind, subject, detail))
                # 규칙 자동 매칭: 스킬 도입 / 슬롯 변화. 슬롯 변화엔 거래소 링크(있으면)도 붙는다.
                if kind == "skill_added":
                    add_rule_note(trans_id, "skill_added", subject)
                elif kind == "item_changed":
                    add_rule_note(trans_id, "item_slot_change", subject)
                    add_trade(cur.lastrowid, cfg["name"], i, subject)
            for note_type, text, ev in cfg["notes"].get(i, []):
                con.execute("INSERT INTO transition_note(transition_id, note_type, text, evidence_ref, source) "
                            "VALUES(?,?,?,?,'hand')", (trans_id, note_type, text, ev))

        # 빌드 단위 규칙: 어센던시·리그 모드 -> 첫 전환(기초), 키스톤 -> 마지막 전환(엔드게임)
        if trans_ids:
            add_rule_note(trans_ids[0], "ascendancy", b["asc"])
            add_rule_note(trans_ids[0], "league", "ssf" if b["ssf"] else "trade")
            for ks in cfg.get("keystones", []):
                add_rule_note(trans_ids[-1], "keystone", ks)

    con.commit()
    stats = {t: con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
             for t in ("creator", "build", "snapshot", "transition", "transition_change",
                       "transition_note", "curation_rule", "trade_target", "trade_link")}
    stats["trade_live"] = con.execute("SELECT COUNT(*) FROM trade_link WHERE live_total IS NOT NULL").fetchone()[0]
    stats["notes_hand"] = con.execute("SELECT COUNT(*) FROM transition_note WHERE source='hand'").fetchone()[0]
    stats["notes_rule"] = con.execute("SELECT COUNT(*) FROM transition_note WHERE source='rule'").fetchone()[0]
    con.close()
    return stats


def query_journey(build_id: int) -> str:
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    b = con.execute("SELECT * FROM build WHERE id=?", (build_id,)).fetchone()
    cr = con.execute("SELECT name FROM creator WHERE id=?", (b["creator_id"],)).fetchone()
    out = [f"# 여정: {cr['name']} — {b['name']}  [{b['game']} · "
           f"{'HC' if b['hardcore'] else 'SC'}{' SSF' if b['ssf'] else ''} · {b['ascendancy']}]"]
    snaps = con.execute("SELECT * FROM snapshot WHERE build_id=? ORDER BY order_idx", (build_id,)).fetchall()
    out.append("스냅샷: " + " → ".join(f"{s['stage_label']}({s['source_type']},P{s['passives_n']})" for s in snaps))
    for t in con.execute("SELECT * FROM transition WHERE build_id=? ORDER BY order_idx", (build_id,)).fetchall():
        f = con.execute("SELECT stage_label FROM snapshot WHERE id=?", (t["from_snapshot"],)).fetchone()[0]
        to = con.execute("SELECT stage_label FROM snapshot WHERE id=?", (t["to_snapshot"],)).fetchone()[0]
        changes = con.execute("SELECT detail FROM transition_change WHERE transition_id=? ORDER BY id", (t["id"],)).fetchall()
        notes = con.execute("SELECT note_type, text, evidence_ref, source FROM transition_note "
                            "WHERE transition_id=? ORDER BY source DESC, id", (t["id"],)).fetchall()
        nh = sum(1 for n in notes if n["source"] == "hand")
        nr = len(notes) - nh
        out.append(f"\n▶ {f} → {to}   [자동 {len(changes)} · 손 {nh} · 규칙 {nr}]")
        for c in changes[:4]:
            out.append(f"    · {c['detail'][:88]}")
        if len(changes) > 4:
            out.append(f"    · … 외 {len(changes) - 4}건")
        # 거래소 링크: 슬롯마다 사다리 요약(매물 수는 live 검색 시점 값). URL 은 DB trade_link.url.
        targets = con.execute(
            "SELECT c.subject AS slot, tt.base, tt.level_max, tt.change_id FROM trade_target tt "
            "JOIN transition_change c ON c.id=tt.change_id WHERE c.transition_id=? ORDER BY c.id", (t["id"],)).fetchall()
        for tg in targets:
            tiers = con.execute("SELECT tier, live_total FROM trade_link WHERE change_id=? AND realm='int' ORDER BY tier",
                                (tg["change_id"],)).fetchall()
            summary = " · ".join(f"{r['tier']}" + (f"={r['live_total']}건" if r["live_total"] is not None else "") for r in tiers)
            out.append(f"    🛒 {tg['slot']} {tg['base']} (요구≤{tg['level_max'] or '-'}) {summary}")
        for n in notes:
            tag = "손" if n["source"] == "hand" else "규칙"
            out.append(f"    ★[{tag}] ({n['note_type']}) {n['text'][:98]}  <{n['evidence_ref']}>")
    con.close()
    return "\n".join(out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--query", action="store_true")
    ap.add_argument("--id", type=int, default=0)
    a = ap.parse_args()
    if a.build or not (a.build or a.query):
        print("적재 완료:", json.dumps(build(), ensure_ascii=False))
    if a.query:
        import sqlite3 as _s
        con = _s.connect(DB_PATH)
        ids = [a.id] if a.id else [r[0] for r in con.execute("SELECT id FROM build ORDER BY id")]
        con.close()
        for bid in ids:
            print(query_journey(bid))
            print()
