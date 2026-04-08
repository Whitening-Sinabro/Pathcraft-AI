# -*- coding: utf-8 -*-
"""
PathcraftAI Build Coach — HCSSF 빌드 코칭 시스템
POB 파싱 결과를 받아서 Claude Sonnet으로 단계별 가이드 생성
"""

import json
import sys
import os
import argparse
import logging
from pathlib import Path
import requests

from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

logger = logging.getLogger("build_coach")
logging.basicConfig(level=logging.INFO, format="%(message)s", stream=sys.stderr)

try:
    import anthropic
except ImportError:
    logger.error("anthropic SDK not installed. Run: pip install anthropic")
    sys.exit(1)


SYSTEM_PROMPT = """너는 Path of Exile HCSSF 전문 빌드 코치다.

역할:
- 유저가 제공한 POB 빌드 데이터를 분석하고 HCSSF 기준 단계별 가이드를 생성한다.
- 생존력 > 공격력 우선. 한 번 죽으면 끝이다.
- 모든 추천은 SSF(자급자족) 기준. 거래소 없다.

출력 형식 (반드시 JSON):
{
  "build_summary": "빌드 한줄 요약",
  "tier": "S/A/B/C/D (HCSSF 기준 생존력 등급)",
  "strengths": ["강점 1", "강점 2"],
  "weaknesses": ["약점 1 (HCSSF 관점)", "약점 2"],
  "leveling_guide": {
    "act1_4": "Act 1-4 레벨링 전략",
    "act5_10": "Act 5-10 전략",
    "early_maps": "화이트/옐로우맵 전략",
    "endgame": "레드맵+ 전략"
  },
  "leveling_skills": {
    "damage_type": "물리/카오스/화염/냉기/번개/혼돈 등 빌드 데미지 유형",
    "recommended": {
      "name": "기본 추천 레벨링 스킬 (못 고르겠으면 이거)",
      "links": "메인 + 서포트 조합",
      "reason": "왜 이걸 추천하는지",
      "transition_level": "최종 빌드 스킬로 전환하는 레벨"
    },
    "options": [
      {
        "name": "레벨링 스킬 옵션",
        "links": "서포트 조합",
        "speed": "빠름/보통/느림 (레벨링 속도)",
        "safety": "높음/보통/낮음 (HCSSF 안전도)",
        "reason": "이 옵션의 장단점"
      }
    ],
    "skill_transitions": [
      {"level": 12, "change": "스킬 A에서 B로 전환", "reason": "이유"}
    ]
  },
  "key_items": [
    {
      "name": "아이템명",
      "slot": "장비 슬롯",
      "importance": "필수/권장/사치",
      "acquisition": "획득 방법 (드롭/카드/보스/크래프팅)",
      "ssf_difficulty": "쉬움/보통/어려움/비현실적",
      "alternatives": ["대체 아이템 1", "대체 아이템 2"]
    }
  ],
  "aura_utility_progression": [
    {
      "phase": "Act 1",
      "auras": ["오라명 (예약%)"],
      "heralds": ["전령명 (예약%)"],
      "reservation_total": "합계 예약%",
      "utility": ["이동기 + 서포트", "워크라이/토템 등"],
      "guard": "가드 스킬 (수동/CWDT)",
      "reason": "이 구간에서 이렇게 세팅하는 이유"
    }
  ],
  "build_rating": {
    "newbie_friendly": 4,
    "gearing_difficulty": 2,
    "play_difficulty": 3,
    "league_start_viable": 5,
    "hcssf_viability": 4
  },
  "gear_progression": [
    {
      "slot": "장비 슬롯 (Body Armour / Helmet / Boots / Gloves / Weapon / Shield / Belt / Amulet / Ring)",
      "phases": [
        {
          "phase": "캠페인 / 초반맵 / 옐로우맵 / 레드맵 / 엔드게임",
          "item": "아이템명 (레어면 '라이프+저항 레어' 등 설명, 유니크면 정확한 이름)",
          "key_stats": ["핵심 스탯 1", "핵심 스탯 2"],
          "acquisition": "획득 방법 (드롭 / 디비카드명 x장수 / 보스명 / 에센스 크래프팅 등)",
          "priority": "필수/권장/목표"
        }
      ]
    }
  ],
  "map_mod_warnings": {
    "deadly": ["즉사 가능한 맵 모드 (이 빌드에서 절대 돌리면 안 되는 것)"],
    "dangerous": ["위험한 맵 모드 (주의 필요)"],
    "caution": ["약간 불편한 맵 모드"],
    "regex_filter": "맵 모드 필터링용 regex (예: reflect|regen|immune)"
  },
  "variant_snapshots": [
    {
      "phase": "구간명 (Act 1-3 / Act 4-6 / Act 7-10 / 화이트맵 / 옐로우맵 / 레드맵 / 엔드게임)",
      "level_range": "레벨 범위 (예: 1-30)",
      "main_skill": "메인 스킬 + 서포트 (예: Blight - Void Manipulation - Controlled Destruction)",
      "auras": "오라 세팅 요약 (예: Malevolence + Clarity)",
      "gear_priority": "이 구간에서 가장 중요한 장비 업그레이드",
      "passive_focus": "패시브 트리 방향 (예: Chaos DoT → Life wheel)",
      "defense_target": {
        "life": 1500,
        "energy_shield": 0,
        "resists": "30+",
        "armour_or_evasion": "해당 시 수치"
      }
    }
  ],
  "passive_priority": ["첫 번째로 찍을 노드 방향", "두 번째", "세 번째"],
  "danger_zones": ["주의할 맵 모드", "위험한 보스"],
  "farming_strategy": {
    "recommended_mechanics": ["이 빌드에 맞는 아틀라스 메카닉 1순위", "2순위", "3순위"],
    "atlas_passive_focus": "이 빌드의 아틀라스 패시브 투자 방향 요약",
    "early_atlas": "초반 아틀라스 전략 (T1-T10, 맵 서스테인 확보)",
    "mid_atlas": "중반 전략 (T14-T16, 1-2돌, 기어 크래프팅)",
    "late_atlas": "후반 전략 (4돌 후 풀 파밍 최적화)",
    "scarab_priority": ["자급자족 가능한 스카랍 1순위", "2순위"],
    "ssf_crafting_focus": "SSF에서 이 빌드의 기어 크래프팅 핵심 메카닉"
  }
}

규칙:
- 반드시 유효한 JSON만 출력. 마크다운이나 설명 텍스트 금지.
- 한국어로 작성.
- 아이템 획득 방법은 구체적으로 (어떤 보스, 어떤 디비니 카드, 어떤 맵).
- 레벨링 가이드는 HCSSF 생존 중심 (저항 캡, 라이프 확보 시점 명시).
- leveling_skills.options는 최소 2개 이상 제시. 속도/안전도 균형이 다른 옵션.
- leveling_skills.recommended는 "못 고르겠으면 이거 써라" 기본 추천. 예: 카오스 DoT면 Blight+Contagion.
- aura_utility_progression 배열은 구간별로 작성: 캠페인(Act 1~10) + 맵(화이트맵 T1-5 / 옐로우맵 T6-10 / 얼리레드 T11-13 / T16 T14-16 / 핀나클 보스). 최소 7단계.
- 오라는 구간별로 구체적으로 (레벨 X부터 Y 사용, Z로 교체). 마나 예약 합산을 고려해서 실제 사용 가능한 조합만 제시.
- 전령(Herald)이 유효하면 반드시 포함. 마나 여유 없으면 방어 오라 우선, 전령 제거 명시.
- 유틸리티: 이동기 (Flame Dash/Leap Slam/Dash 등), 가드 스킬 (Steelskin/Molten Shell), 워크라이, CWDT 조합 모두 포함.
- 가드 스킬은 Lv38 이후 CWDT 자동화 권장. CWDT 레벨과 가드 스킬 레벨 매칭도 명시.
- 얼리레드(T11-13) 이후 구간은 반드시 SSF fallback 포함: Enlighten 못 구할 경우 대안 (마나 예약 효율 패시브, Divine Blessing, Purity of Elements 등).
- 각 맵 구간마다 defense_checkpoint 포함: 라이프, 저항, 에일먼트 면역, DPS 기준.
- 얼리레드(T11-13)는 HCSSF 첫 번째 '벽', T16(T14-16)은 두 번째 '벽'. 기어 부족하면 이전 티어 파밍 권장.
- 핀나클 보스(시어링/이터/메이븐/쉐이퍼/엘더)는 T16 파밍 도중 진행. 보이드스톤 4개 타이밍: VS1(시어링+이터, 얼리레드) → VS2(이곤 퀘스트, T16) → VS3(쉐이퍼+엘더, T16 안정 후) → VS4(메이븐, 선택).
- 장비 업그레이드 타이밍 필수 포함: 각 구간에서 어떤 슬롯을 어떤 방법으로 업그레이드할지 (에센스/하베스트/벤치 등). 얼리레드에서 기어 부족하면 옐로우맵 파밍 권장.
- 오라 3개 이상 동시 사용 시 마나 예약 합계를 계산해서 실현 가능한 조합만 제시. "Enlighten 있으면" 식 조건부는 SSF에서 기본값이 아님.
- 퀘스트 젬 보상 데이터가 제공되면, 해당 클래스가 몇 Act에서 어떤 젬을 받는지 참고해서 "이 퀘스트에서 이 젬 선택" 형태로 안내.

build_rating 규칙:
- 5개 카테고리 모두 1~5 정수. 1=매우 어려움/낮음, 5=매우 쉬움/높음.
- HCSSF 관점에서 평가. SSF 기어링이 어려운 빌드는 gearing_difficulty 낮게.
- hcssf_viability와 tier는 일관성 유지 (S=5, A=4, B=3, C=2, D=1).

gear_progression 규칙:
- 핵심 슬롯 최소 6개 (Body, Helmet, Weapon, Boots, Belt, Amulet). 빌드에 중요한 슬롯만.
- 각 슬롯에 phases 최소 2개 (캠페인 + 엔드게임). 중요한 슬롯은 3~4단계.
- 레어 아이템은 "라이프+저항 레어"처럼 핵심 모드 명시. 유니크는 정확한 이름.
- acquisition은 구체적으로: "에센스 오브 그리드 크래프팅" / "Humility 카드 x9 (Blood Aqueduct)" / "Shaper 보스 드롭".
- priority: 필수(없으면 빌드 안 돌아감) / 권장(있으면 크게 좋아짐) / 목표(최종 BiS).

map_mod_warnings 규칙:
- deadly: 이 빌드에서 절대 돌리면 안 되는 모드 (예: 물리 반사 for 물리 빌드). 최소 1개.
- dangerous: 주의해서 돌려야 하는 모드. 최소 2개.
- regex_filter: PoE 맵 장치에서 복사+붙여넣기로 필터링할 수 있는 regex 문자열.

variant_snapshots 규칙:
- 최소 5단계: Act 1-3, Act 4-10, 화이트맵, 옐로우맵, 레드맵+.
- 각 구간의 defense_target은 HCSSF 최소 기준 (이 수치 이하면 다음 구간 진입 금지).
- main_skill은 서포트 젬까지 포함 (예: "Essence Drain - Controlled Destruction - Efficacy - Void Manipulation").
"""


def detect_archetype(build_data: dict) -> str:
    gems = build_data.get("progression_stages", [{}])[0].get("gem_setups", {})
    gem_names = " ".join(gems.keys()).lower()

    if any(k in gem_names for k in ["raise zombie", "raise spectre", "summon", "animate"]):
        return "minion"
    if any(k in gem_names for k in ["blight", "contagion", "essence drain", "toxic rain", "death aura", "corrupting fever", "caustic"]):
        return "dot"
    if any(k in gem_names for k in ["cyclone", "lacerate", "bladestorm", "lightning arrow", "tornado shot", "split arrow"]):
        return "attack"
    return "spell"


def load_archetype_data(archetype: str) -> dict:
    data_dir = Path(__file__).resolve().parent.parent / "data" / "guide_templates"
    filepath = data_dir / f"archetype_{archetype}.json"
    if filepath.exists():
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def load_quest_rewards() -> dict:
    filepath = Path(__file__).resolve().parent.parent / "data" / "quest_rewards.json"
    if filepath.exists():
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def load_patch_context() -> dict:
    """최신 패치노트 요약을 로드 (AI 컨텍스트용)"""
    patch_dir = Path(__file__).resolve().parent.parent / "data" / "patch_notes"
    index_file = patch_dir / "patch_index.json"

    if not index_file.exists():
        return {}

    try:
        with open(index_file, "r", encoding="utf-8") as f:
            index = json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}

    # 메이저 패치만 필터 (핫픽스/마이너 제외)
    major_versions = [
        v for v, info in index.items()
        if info.get("patch_type") == "major" and "hotfix" not in v
    ]
    if not major_versions:
        # patch_type이 없는 구버전 인덱스 폴백
        major_versions = [v for v in index.keys() if "hotfix" not in v]
    if not major_versions:
        return {}

    latest = sorted(major_versions, reverse=True)[0]

    # summary 파일 탐색
    summary_file = patch_dir / f"summary_{latest.replace('.', '_')}.json"
    if summary_file.exists():
        with open(summary_file, "r", encoding="utf-8") as f:
            return json.load(f)

    return {}


def coach_build(build_data: dict, model: str = "claude-sonnet-4-20250514") -> dict:
    client = anthropic.Anthropic()

    archetype = detect_archetype(build_data)
    archetype_data = load_archetype_data(archetype)

    logger.info(f"아키타입 감지: {archetype}")

    # 게임 데이터 로드 (추출된 .datc64 기반)
    game_data_context = ""
    try:
        from game_data_provider import GameData
        gd = GameData()
        game_data_context = gd.build_context_for_coach(build_data)
        if game_data_context:
            logger.info("게임 데이터 컨텍스트 로드 완료")
    except ImportError:
        logger.info("game_data_provider 없음 — 게임 데이터 스킵")
    except (OSError, json.JSONDecodeError) as e:
        logger.warning(f"게임 데이터 로드 실패: {e}")

    # 폴백: 게임 데이터 없으면 기존 quest_rewards.json 사용
    class_rewards = {}
    if not game_data_context:
        quest_data = load_quest_rewards()
        char_class = build_data.get("meta", {}).get("class", "")
        if quest_data and char_class:
            for quest in quest_data.get("quests", []):
                rewards = quest.get("rewards", {}).get(char_class, [])
                if rewards:
                    class_rewards[quest["name"]] = rewards

    # 유니크 아이템 Wiki 획득 정보 조회
    wiki_item_info = []
    try:
        from wiki_data_provider import get_build_items_info
        gear = build_data.get("progression_stages", [{}])[0].get("gear_recommendation", {})
        unique_names = [v["name"] for v in gear.values() if v.get("rarity") == "Unique" and v.get("name")]
        if unique_names:
            logger.info(f"Wiki에서 유니크 {len(unique_names)}개 조회 중...")
            wiki_item_info = get_build_items_info(unique_names)
    except (ImportError, ModuleNotFoundError):
        logger.info("wiki_data_provider 모듈 없음 — Wiki 조회 스킵")
    except requests.RequestException as e:
        logger.warning(f"Wiki 네트워크 오류: {e}")
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        logger.warning(f"Wiki 데이터 파싱 오류: {e}")

    context_parts = [f"이 POB 빌드를 HCSSF 기준으로 코칭해줘:\n\n{json.dumps(build_data, ensure_ascii=False, indent=2)}"]

    if wiki_item_info:
        context_parts.append(f"\n\n유니크 아이템 실제 획득 정보 (Wiki 기준, 이 데이터를 반드시 참고):\n{json.dumps(wiki_item_info, ensure_ascii=False, indent=2)}")

    if archetype_data:
        leveling = archetype_data.get("leveling_skill_progression", {})
        auras = archetype_data.get("aura_progression", {})
        aura_utility = archetype_data.get("aura_herald_utility_by_level", [])
        curses = archetype_data.get("curse_setup", {})
        movement = archetype_data.get("movement_skill", {})
        context_parts.append(f"\n\n아키타입: {archetype}\n레벨링 스킬 데이터:\n{json.dumps(leveling, ensure_ascii=False, indent=2)}")
        if aura_utility:
            context_parts.append(f"\n오라/전령/유틸리티 구간별 추천 (이 데이터를 기반으로 aura_utility_progression 작성):\n{json.dumps(aura_utility, ensure_ascii=False, indent=2)}")
        else:
            context_parts.append(f"\n오라 추천 (요약):\n{json.dumps(auras, ensure_ascii=False, indent=2)}")
        if curses:
            context_parts.append(f"\n저주 추천:\n{json.dumps(curses, ensure_ascii=False, indent=2)}")
        if movement:
            context_parts.append(f"\n이동기 추천:\n{json.dumps(movement, ensure_ascii=False, indent=2)}")

    # 공통 템플릿에서 보이드스톤/장비 타이밍 로드
    common_path = Path(__file__).resolve().parent.parent / "data" / "guide_templates" / "common_template.json"
    common_data = {}
    if common_path.exists():
        with open(common_path, "r", encoding="utf-8") as f:
            common_data = json.load(f)
    if common_data:
        vs_data = common_data.get("voidstone_progression", {})
        gear_data = common_data.get("gear_upgrade_timeline", {})
        if vs_data:
            context_parts.append(f"\n\n보이드스톤 진행 (3.28 미라지):\n{json.dumps(vs_data, ensure_ascii=False, indent=2)}")
        if gear_data:
            context_parts.append(f"\n장비 업그레이드 타이밍:\n{json.dumps(gear_data, ensure_ascii=False, indent=2)}")

    # 게임 데이터 컨텍스트 (추출된 실제 데이터 우선, 폴백으로 기존 quest_rewards)
    if game_data_context:
        context_parts.append(f"\n\n{game_data_context}")
    elif class_rewards:
        char_class = build_data.get("meta", {}).get("class", "")
        context_parts.append(f"\n\n{char_class} 클래스 퀘스트 젬 보상:\n{json.dumps(class_rewards, ensure_ascii=False, indent=2)}")

    # 최신 패치 컨텍스트 주입
    patch_context = load_patch_context()
    if patch_context:
        patch_ver = patch_context.get("version", "")
        logger.info(f"패치 컨텍스트 로드: {patch_ver}")
        context_parts.append(f"\n\n최신 패치 정보 ({patch_ver}):\n{json.dumps(patch_context, ensure_ascii=False, indent=2)}")
        context_parts.append("\n위 패치 정보를 반드시 참고해서 답변해줘. 버프된 스킬은 추천도를 올리고, 너프된 스킬은 주의사항에 포함해.")

    user_message = "\n".join(context_parts)

    logger.info(f"Claude {model}에게 빌드 코칭 요청 중...")

    response = client.messages.create(
        model=model,
        max_tokens=16384,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}]
    )

    raw_text = response.content[0].text

    try:
        result = json.loads(raw_text)
    except json.JSONDecodeError:
        start = raw_text.find('{')
        end = raw_text.rfind('}') + 1
        if start != -1 and end > start:
            result = json.loads(raw_text[start:end])
        else:
            result = {"error": "JSON 파싱 실패", "raw": raw_text}

    result.setdefault("aura_utility_progression", [])
    result.setdefault("leveling_skills", {})
    result.setdefault("build_rating", {})
    result.setdefault("gear_progression", [])
    result.setdefault("map_mod_warnings", {})
    result.setdefault("variant_snapshots", [])

    logger.info(f"코칭 완료. 토큰: input={response.usage.input_tokens}, output={response.usage.output_tokens}")
    return result


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="PathcraftAI Build Coach")
    ap.add_argument("input", help="POB JSON 파일 경로 또는 '-' (stdin)")
    ap.add_argument("--model", default="claude-sonnet-4-20250514", help="Claude 모델")
    args = ap.parse_args()

    if args.input == "-":
        build_data = json.load(sys.stdin)
    else:
        with open(args.input, 'r', encoding='utf-8') as f:
            build_data = json.load(f)

    result = coach_build(build_data, model=args.model)
    print(json.dumps(result, ensure_ascii=False, indent=2))
