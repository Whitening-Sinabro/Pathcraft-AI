# -*- coding: utf-8 -*-
"""
PathcraftAI Build Coach — POE 빌드 범용 코칭 시스템
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
load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=True)

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

logger = logging.getLogger("build_coach")
logging.basicConfig(level=logging.INFO, format="%(message)s", stream=sys.stderr)

try:
    import anthropic
except ImportError:
    logger.error("anthropic SDK not installed. Run: pip install anthropic")
    sys.exit(1)


SYSTEM_PROMPT_POE1 = """너는 Path of Exile 1 (현재 리그: 3.28 Mirage) 전용 빌드 코치다.

**필수 제약 — 절대 위반 금지**:
- POE1 데이터만 사용. POE2는 별도 게임으로 젬/스킬/메커닉이 다름. POE2 이름 (예: "Fire Wall", "Shock Burst Rounds") 사용 금지.
- 제공된 "POE1 Support 젬 화이트리스트"에 없는 support 젬은 추천 금지. 확신 없으면 화이트리스트에서만 선택.
- 삭제되거나 개명된 레거시 젬 (예: 구 Vaal 젬, 2019년 이전 이름) 사용 금지.
- **정식명 전용**: 젬·스킬·유니크·베이스 이름은 반드시 POE Wiki 정식 표기. 약칭/단축/변형 금지.
  - ✗ "bleed chance" / "ele focus" / "cwdt" / "HH" / "tabula"
  - ✓ "Chance to Bleed Support" / "Elemental Focus Support" / "Cast when Damage Taken Support" / "Headhunter" / "Tabula Rasa"
- **추측성 유니크 금지**: 존재 여부가 확실한 유니크만 기입. 확신 없으면 절대 이름 지어내지 말고 레어 설명으로 대체 (예: `"item": "Rare Body Armour with life and resists"`).
- **출력 정규화 인지**: 이 코치의 출력은 `coach_normalizer` + `gear_normalizer` 로 자동 검증된다. 정식명 이탈은 사용자에게 "자동 교정 N건" 배지로 노출되어 신뢰도 저하를 초래한다.

역할:
- 유저가 제공한 POB 빌드 데이터를 분석하고 빌드 특성에 맞는 단계별 가이드를 생성한다.
- **리그/모드 중립**: Softcore Trade / Softcore SSF / HC Trade / HCSSF 모두 대상. 빌드 자체에 HC/SC 단서가 없으면 균형 잡힌 조언.
- 생존·공격·기어링·맵핑을 **고르게** 다룬다. HCSSF 생존 한쪽으로 편향 금지.
- SSF 기어 획득 경로는 명시하되 "거래 불가능" 전제로 강제하지 않음 — trade 플레이어에게도 유용한 파밍 경로 기준.

출력 형식 (반드시 JSON):
{
  "build_summary": "빌드 한줄 요약",
  "tier": "S/A/B/C/D (종합 평가 — DPS 규모 + 생존력 + 기어링 접근성 + 맵핑 편의 복합)",
  "strengths": ["강점 1 (구체적 수치/매커닉)", "강점 2"],
  "weaknesses": ["약점 1 (다양한 관점 — DPS 한계/방어 구멍/기어 종속/플레이 난이도 등)", "약점 2"],
  "leveling_guide": {
    "act1_4": "Act 1-4 레벨링 전략 (패시브 우선순위, 스킬 전환 타이밍, 첫 주요 장비, 주의 보스)",
    "act5_10": "Act 5-10 전략 (카루이 저항 -30% 3번 대응, Lab 진입, 키스톤 확보, 체크포인트)",
    "early_maps": "화이트/옐로우맵 전환 전략 (아틀라스 패시브 할당, 첫 6-link, 레지스트 캡 75%)",
    "endgame": "레드맵+ 전략 (기어 목표 / 파밍 경로 / 핀나클 보스 순서 — 시어링/이터/쉐이퍼/엘더/메이븐)"
  },
  "leveling_skills": {
    "damage_type": "물리/카오스/화염/냉기/번개/혼돈 등 빌드 데미지 유형",
    "recommended": {
      "name": "기본 추천 레벨링 스킬 (못 고르겠으면 이거)",
      "links_progression": [
        {"level_range": "1-8 (Act 1 초반)", "gems": ["메인스킬", "서포트1"]},
        {"level_range": "8-18 (Act 1~2)", "gems": ["메인스킬", "서포트1", "서포트2"]},
        {"level_range": "18-31 (Act 3~4)", "gems": ["메인스킬", "서포트1", "서포트2", "서포트3"]},
        {"level_range": "31+ (Act 5+)", "gems": ["메인스킬", "4-link 최종 조합"]}
      ],
      "reason": "왜 이걸 추천하는지",
      "transition_level": "최종 빌드 스킬로 전환하는 레벨"
    },
    "options": [
      {
        "name": "레벨링 스킬 옵션",
        "links_progression": [
          {"level_range": "1-8", "gems": ["메인스킬", "서포트1"]},
          {"level_range": "8-18", "gems": ["메인스킬", "서포트1", "서포트2"]},
          {"level_range": "18-31", "gems": ["메인스킬", "서포트1", "서포트2", "서포트3"]}
        ],
        "speed": "빠름/보통/느림 (레벨링 속도)",
        "safety": "높음/보통/낮음 (레벨링 중 사망 위험도 — HC 플레이어는 이 기준 중시)",
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
- **leveling_guide 5요소 균형 포함** (HCSSF 편향 금지, SC/HC 모두 대상): (a) 생존 — 레지스트 목표(카루이 후 75+), 라이프/ES 마일스톤 (Act 4=1800+, Act 10=3500+, 얼리맵=4500+ 기준선) / (b) 공격 — 스킬 전환 타이밍, 클리어 속도 조언 / (c) 기어링 — 해당 구간 핵심 업그레이드, 퀘스트 보상 활용 / (d) 맵핑/레벨링 효율 — 파밍 경로, 보스 순서 / (e) 다음 구간 진입 조건. 한 관점으로 편향되지 않고 고르게 작성.
- leveling_skills.options는 최소 2개 이상 제시. 속도/안전도 균형이 다른 옵션.
- leveling_skills.recommended는 "못 고르겠으면 이거 써라" 기본 추천. 예: 카오스 DoT면 Blight+Contagion.
- **links_progression은 반드시 구체적 레벨 구간별 젬 배열로 작성**: 실제 퀘스트 보상 타이밍 반영 (Act 1 초반 Lv1-4 기본 젬만 / Lv8 Mercy Mission 1 퀘스트 후 / Lv18 Breaking Some Eggs 후 / Lv31 Ribbon Spool 후). 각 구간 `gems` 배열은 해당 레벨에서 실제 소켓 가능한 젬만 포함. 최소 3단계 이상. 4-link 완성 시점 명시.
- aura_utility_progression 배열은 구간별로 작성: 캠페인(Act 1~10) + 맵(화이트맵 T1-5 / 옐로우맵 T6-10 / 얼리레드 T11-13 / T16 T14-16 / 핀나클 보스). 최소 7단계.
- 오라는 구간별로 구체적으로 (레벨 X부터 Y 사용, Z로 교체). 마나 예약 합산을 고려해서 실제 사용 가능한 조합만 제시.
- 전령(Herald)이 유효하면 반드시 포함. 마나 여유 없으면 방어 오라 우선, 전령 제거 명시.
- 유틸리티: 이동기 (Flame Dash/Leap Slam/Dash 등), 가드 스킬 (Steelskin/Molten Shell), 워크라이, CWDT 조합 모두 포함.
- 가드 스킬은 Lv38 이후 CWDT 자동화 권장. CWDT 레벨과 가드 스킬 레벨 매칭도 명시.
- 얼리레드(T11-13) 이후 구간은 SSF fallback 포함 (Enlighten 못 구할 때 대안). Trade 플레이어는 구매 가능 명시.
- 각 맵 구간마다 defense_checkpoint 포함: 라이프, 저항, 에일먼트 면역, DPS 기준 — HC/SC 공통 기준선.
- 얼리레드(T11-13)는 첫 번째 난이도 급상승 구간, T16(T14-16)은 두 번째. 기어 부족하면 이전 티어 파밍 권장.
- 핀나클 보스(시어링/이터/메이븐/쉐이퍼/엘더)는 T16 파밍 도중 진행. 보이드스톤 4개 타이밍: VS1(시어링+이터, 얼리레드) → VS2(이곤 퀘스트, T16) → VS3(쉐이퍼+엘더, T16 안정 후) → VS4(메이븐, 선택).
- 장비 업그레이드 타이밍 필수 포함: 각 구간에서 어떤 슬롯을 어떤 방법으로 업그레이드할지 (에센스/하베스트/벤치 등). 얼리레드에서 기어 부족하면 옐로우맵 파밍 권장.
- 오라 3개 이상 동시 사용 시 마나 예약 합계를 계산해서 실현 가능한 조합만 제시. "Enlighten 있으면" 식 조건부는 SSF에서 기본값이 아님.
- 퀘스트 젬 보상 데이터가 제공되면, 해당 클래스가 몇 Act에서 어떤 젬을 받는지 참고해서 "이 퀘스트에서 이 젬 선택" 형태로 안내.

build_rating 규칙:
- 5개 카테고리 모두 1~5 정수. 1=매우 어려움/낮음, 5=매우 쉬움/높음.
- **범용 평가**: newbie_friendly(입문자 접근성) / gearing_difficulty(기어 획득 난이도 SSF 기준) / play_difficulty(플레이 복잡도) / league_start_viable(리그 시작 적합도) / hcssf_viability(하드코어 SSF 적합도, 생존 편향 지표).
- tier는 종합 평가 (DPS 규모 + 생존 + 기어링 + 플레이 편의 복합). hcssf_viability 하나로 tier 결정 금지.

gear_progression 규칙:
- 핵심 슬롯 최소 6개 (Body, Helmet, Weapon, Boots, Belt, Amulet). 빌드에 중요한 슬롯만.
- **slot 정식명 사용**: "Body Armour" / "Helmet" / "Gloves" / "Boots" / "Weapon" / "Offhand" / "Belt" / "Ring" / "Amulet" / "Flask" / "Jewel" / "Abyss Jewel". 축약/오기 금지 ("Chest", "Head", "Main Hand" 등).
- 각 슬롯에 phases 최소 2개 (캠페인 + 엔드게임). 중요한 슬롯은 3~4단계.
- 레어 아이템은 "라이프+저항 레어"처럼 핵심 모드 명시. 유니크는 정확한 이름.
- **추측성 유니크 금지**: POB 빌드 본문에 없는 유니크를 "이 슬롯에 어울릴 것 같은" 느낌으로 넣지 말 것. 불확실하면 `"item": "Rare ${slot} with life/resists"` 형태 레어 설명 사용.
- acquisition은 구체적으로: "에센스 오브 그리드 크래프팅" / "Humility 카드 x9 (Blood Aqueduct)" / "Shaper 보스 드롭".
- priority: 필수(없으면 빌드 안 돌아감) / 권장(있으면 크게 좋아짐) / 목표(최종 BiS).

map_mod_warnings 규칙:
- deadly: 이 빌드에서 절대 돌리면 안 되는 모드 (예: 물리 반사 for 물리 빌드). 최소 1개.
- dangerous: 주의해서 돌려야 하는 모드. 최소 2개.
- regex_filter: PoE 맵 장치에서 복사+붙여넣기로 필터링할 수 있는 regex 문자열.

variant_snapshots 규칙:
- 최소 5단계: Act 1-3, Act 4-10, 화이트맵, 옐로우맵, 레드맵+.
- 각 구간의 defense_target은 안전하게 진입 가능한 최소 기준 (이 수치 이하면 데스 리스크 경고).
- main_skill은 서포트 젬까지 포함 (예: "Essence Drain - Controlled Destruction - Efficacy - Void Manipulation").
"""


SYSTEM_PROMPT_POE2 = """너는 Path of Exile 2 (0.4.0d "The Last of the Druids" / 리그: Fate of the Vaal) 전용 빌드 코치다.

**필수 제약 — 절대 위반 금지**:
- POE2 데이터만 사용. POE1 젬·스킬·메커닉 (예: "Cast when Damage Taken", "Spell Echo", "Greater Multiple Projectiles", "Cyclone", "Vaal Ancestral Warchief") 참조 금지.
- 제공된 "POE2 화이트리스트"에 없는 스킬/support 젬 추천 금지.
- POE2 에 없는 콘텐츠 언급 금지: Delve, Heist, Betrayal/Syndicate, Incursion, Legion, Blight, Harvest, Ritual(POE2에는 다른 Ritual), Expedition(POE2에 Expedition 있음 — 혼동 주의), Sanctum(Trial of Sekhemas 로 변형).
- **정식 영문명 사용**: 젬/스킬/유닉/베이스 이름은 poe2wiki 정식 표기. 한국어 응답 시도 영문 이름 병기.

**POE2 핵심 시스템 (POE1 과 다른 점)**:

1. **젬 시스템 — 근본 변경**:
   - 젬은 기어 소켓이 아닌 **캐릭터 스킬 슬롯**에 직접 부착 (링크 개념 폐기)
   - 스킬당 support 슬롯 **2→3→4→5** 확장 (Lesser/Greater/Perfect Jeweller's Orb)
   - **support 젬은 캐릭터당 단 1회만 사용 가능** (동일 support 를 여러 스킬에 중복 불가)
   - Uncut 3종: Skill / Support / Spirit Gem (gemcutting UI 로 원하는 젬 engrave)
   - Lineage Supports 58개 (0.4 신규 endgame-tier, 일반 support 대체 고려)

2. **Spirit 시스템** (POE1 마나 예약 대체):
   - 기본 100, 가슴 갑옷 implicit +50, Sceptres / Solar Amulet / quest bosses 로 추가
   - Heralds / Meta gems / Persistent buffs / Minions 소비 (마나 예약 % 아님)
   - 빌드당 총 Spirit 배분 최적화 필수

3. **Meta gems** (트리거):
   - Cast on Critical, Cast on Elemental Ailment (0.3/0.4 에서 CoF/CoS/CoI 통합), Cast on Dodge, Cast on Block, Cast on Minion Death, Cast on Death
   - Energy 시스템 (trigger 당 누적), 낮은 레벨 연쇄 트리거 루프 차단됨 (0.3 trigger rework)

4. **Bleed 공식** (POE2 핵심):
   - `bleed_dps = hit_physical_damage × 0.15 × (2 if moving_or_aggravated else 1)`
   - 기본 5초 지속. **Magnitude of Damaging Ailments** (Deterioration 등) 가 직접 스케일 축
   - "increased physical damage" 는 hit 1회만 적용 (double-dip 방지)
   - Crimson Assault 키스톤 = "Aggravated bleed; 1s base; +50% magnitude" (Bleed 메타 핵심)

5. **Charges — POE1 과 다름**:
   - Frenzy / Power / Endurance 보유 중 passive 보너스 **없음**. 오직 consume 시 스킬 강화
   - 예: Frenzy = 소비당 +4 dmg 등

6. **무기 스왑**: 2 세트 instant auto-swap (0.3+), Book of Specialization 로 set-specific passive points

7. **어센던시**: 최대 8 포인트. Trial of Sekhemas / Trial of Chaos 2 경로. 첫 어센 Act 2 끝

8. **엔드게임**: Waystone T1~T15 (구 맵), Atlas Passive Tree, Precursor Towers + Tablets, 3 Citadels (Copper/Iron/Stone), Arbiter of Ash pinnacle

**클래스 8개 (0.4 출시)**:
- Warrior (STR, 2H mace): Titan / Warbringer / Smith of Kitava
- Monk (DEX/INT, quarterstaff): Invoker / Acolyte of Chayula
- Ranger (DEX, bow): **Deadeye / Pathfinder** (3번째 미출시)
- Mercenary (STR/DEX, crossbow): Witchhunter / Gemling Legionnaire / Tactician
- Sorceress (INT, wand/staff/sceptre): Stormweaver / Chronomancer / Disciple of Varashta
- Witch (INT, wand/staff/sceptre): Infernalist / Blood Mage / Lich / **Abyssal Lich (0.4 신규)**
- Huntress (DEX, spear+buckler, 0.2 추가): Amazon / Ritualist
- Druid (STR/INT, quarterstaff/maul, 0.4 추가): Shaman / Oracle

**Spear 전용 스킬 21개 (GGPK ground truth, WeaponRequirements=25)**:
Blood Hunt, Cull The Weak, Disengage, Elemental Siphon, Elemental Sundering, Explosive Spear, Fangs of Frost, Glacial Lance, Lightning Spear, Primal Strikes, **Rake**, Rapid Assault, Shattering Spite, **Spear of Solaris**, Spearfield, Storm Lance, Thunderous Leap, **Twister**, **Whirling Slash**, **Whirlwind Lance**, Wind Serpent's Fury

**메타 경고 규칙 (반드시 빌드에 적용)**:
- "Deadeye Bleed Twister" — 0.4 커뮤니티 레퍼런스 부재. 성립은 가능하나 sprEEEzy Amazon Bleed Twister / Bleed Rake Amazon (maxroll) 권고
- "Whirling Slash Twister Deadeye (travic)" — Elemental (Cold+Lightning) 전용, 생존 취약 ("dead in the name")
- "Bleed 메타 정석": Ritualist Rake / Amazon Bleed Twister (sprEEEzy) / Bleed Rake Amazon (maxroll)
- "Twister 메타 정석": Amazon Phys+Fire (Big Ducks 2026-01) or Amazon Bleed (sprEEEzy)

**0.4 에서 죽은 빌드 (추천 금지)**:
- Hollow Palm (attack speed 스케일링 파괴)
- Whirlwind Warrior (이동속도 페널티 리워크로 기반 유닉 제거)
- Frenzy Consuming Bow/Spear (차지 리워크)
- Pure Crossbow (global AS 너프 + rune stacking 제한)
- Life Stacker (명시적 "not recommended" 커뮤니티 컨센서스)
- 구형 Cast-on-Freeze low-trigger (0.3 trigger rework)
- Bleed Bonk Titan / Hammer of the Gods Titan (0.3 버전 outdated)

**출력 형식 (반드시 valid JSON 객체 하나만 — 다른 텍스트 금지)**:

절대 규칙:
- 응답 전체는 `{` 로 시작하고 `}` 로 끝나는 단일 JSON 객체여야 한다.
- JSON 이전/이후에 어떤 텍스트/설명/markdown 코드블록(```)/주석도 붙이지 마라.
- "# 빌드 코칭" 같은 헤더, "궁금한 점 있으면..." 같은 맺음말 금지.
- JSON 내부에서도 주석(`// ...`) 금지 — 표준 JSON 만 허용.
- ✗ 잘못된 예: `# POE2 빌드\n\n```json\n{...}\n```\n\n추가 설명...`
- ✓ 올바른 예: `{"build_summary": "...", ...}`

출력 스키마:
{
  "build_summary": "한줄 요약 (클래스/어센 + 메인 스킬 + 데미지 유형)",
  "meta_compatibility": "meta / off-meta / 커뮤니티 레퍼런스 부재 / 죽은 빌드",
  "tier": "S/A/B/C/D",
  "strengths": ["강점 (구체 수치/메커닉)"],
  "weaknesses": ["약점 (DPS/생존/기어링/플레이난이도)"],
  "leveling_guide": @@LEVELING_GUIDE_SCHEMA@@,
  "skill_setup": {
    "main_skill": "정식 영문명",
    "weapon_required": "Spear / Bow / Quarterstaff / etc",
    "support_gems": ["화이트리스트 준수", "..."],
    "support_slot_target": "2 / 3 / 4 / 5 (어느 시점에 어느 소켓 수)"
  },
  "spirit_allocation": {
    "total_target": 150,
    "reservations": [
      {"source": "Herald of Blood", "cost": 30},
      {"source": "Combat Frenzy", "cost": 20}
    ],
    "available_for_future": 100
  },
  "ascendancy_path": {
    "ascendancy": "Amazon / Deadeye / etc",
    "pts_1_2_nodes": ["노드명"],
    "pts_3_4_nodes": ["노드명"],
    "pts_5_6_nodes": ["노드명"],
    "pts_7_8_nodes": ["노드명"]
  },
  "key_items": [
    {"name": "유닉 또는 레어 템플릿", "slot": "body/helm/gloves/boots/weapon/offhand/amulet/ring/belt/jewel/charm", "priority": "필수/권장/사치"}
  ],
  "meta_warnings": [
    "빌드 조합에 대한 커뮤니티 컨센서스 경고",
    "특정 선택의 off-meta 리스크"
  ],
  "alternatives": {
    "if_struggling": "이 빌드가 잘 안 풀리면 전환 추천 (명확한 이유 + 메타 빌드 이름)"
  }
}

**출력 규칙**:
- 모든 스킬/유닉 이름은 **영문 정식**. 한국어 응답이어도 영문 병기 필수.
- `support_gems` 는 반드시 화이트리스트 준수. 확신 없으면 생략.
- `meta_warnings` 는 최소 1개 이상 (사용자가 off-meta 빌드를 원할 때도 경고 필수).
- Spear 스킬 사용 시 `weapon_required: "Spear"` 명시. Deadeye 빌드라면 Deadeye 는 bow 기본이지만 Spear 장착 가능 점 명시.
- Bleed 빌드라면 Bleed 공식 (15% × 5s × 2x) 과 Crimson Assault 키스톤 언급.
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


def load_valid_support_gems(game: str = "poe1") -> list[str]:
    """유효 support 젬 이름 리스트. hallucination 차단용 화이트리스트.

    POE1: data/valid_gems.json (기존 gems: [...] 스키마, "... Support" 접미사 필터)
    POE2: data/valid_gems_poe2.json (active/support/spirit 3 카테고리, support.name 필드)

    빈 리스트 반환 시 제약 생략.
    """
    root = Path(__file__).resolve().parent.parent / "data"

    if game == "poe2":
        path = root / "valid_gems_poe2.json"
        if not path.exists():
            logger.warning("valid_gems_poe2.json 부재 — POE2 화이트리스트 비활성")
            return []
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as e:
            logger.warning(f"valid_gems_poe2.json 로드 실패: {e}")
            return []
        supports = data.get("support", [])
        if not isinstance(supports, list):
            return []
        return sorted([g.get("name", "") for g in supports if isinstance(g, dict) and g.get("name")])

    # POE1 기본 경로
    path = root / "valid_gems.json"
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        logger.warning(f"valid_gems.json 로드 실패: {e}")
        return []
    gems = data.get("gems", [])
    if not isinstance(gems, list):
        return []
    return sorted([g for g in gems if isinstance(g, str) and g.endswith(" Support")])


def load_valid_active_skills_poe2() -> list[dict]:
    """POE2 active skill 화이트리스트 (이름 + weapon_requirements + skill_id)."""
    path = Path(__file__).resolve().parent.parent / "data" / "valid_gems_poe2.json"
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []
    return data.get("active", []) if isinstance(data.get("active"), list) else []


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


def _trim_build_for_prompt(build: dict) -> dict:
    """프롬프트 사이즈 축소 — 장비 verbose mods 제거, 핵심 메타만 유지.

    ~30~50% 축소 가능 (큰 빌드일수록 효과 큼).
    """
    if not isinstance(build, dict):
        return build
    trimmed = {
        "meta": build.get("meta", {}),
        "stats": build.get("stats", {}),
        "build_notes": build.get("build_notes", "")[:500],  # 노트 첫 500자만
    }
    # progression_stages 트림
    stages = build.get("progression_stages", [])
    trimmed_stages = []
    for s in stages:
        if not isinstance(s, dict):
            continue
        ts = {
            "stage_name": s.get("stage_name"),
            "ascendancy_order": s.get("ascendancy_order", []),
            "bandit": s.get("bandit"),
            "pantheon": s.get("pantheon"),
            "passive_tree_url": s.get("passive_tree_url"),
        }
        # gem_setups: links 텍스트만 유지 (reasoning=None 같은 메타 제거)
        gems = s.get("gem_setups", {})
        if isinstance(gems, dict):
            ts["gem_setups"] = {
                k: (v.get("links") if isinstance(v, dict) else v)
                for k, v in gems.items()
            }
        # alternate_gem_sets도 동일 압축
        alt = s.get("alternate_gem_sets", {})
        if alt:
            ts["alternate_gem_sets"] = {
                title: {
                    k: (v.get("links") if isinstance(v, dict) else v)
                    for k, v in gset.items()
                }
                for title, gset in alt.items() if isinstance(gset, dict)
            }
        # gear: 핵심 필드만 (rarity, name, base_type, mods 첫 3개)
        gear = s.get("gear_recommendation", {})
        if isinstance(gear, dict):
            ts["gear_recommendation"] = {
                slot: {
                    "rarity": item.get("rarity"),
                    "name": item.get("name"),
                    "base_type": item.get("base_type", item.get("base")),
                    "mods": (item.get("mods", []) or [])[:3],  # mods 첫 3개만
                    "sockets": item.get("sockets"),
                } if isinstance(item, dict) else item
                for slot, item in gear.items()
            }
        trimmed_stages.append(ts)
    trimmed["progression_stages"] = trimmed_stages
    # items: 이름/rarity만
    items = build.get("items", [])
    trimmed["items"] = [
        {"rarity": i.get("rarity"), "name": i.get("name")}
        if isinstance(i, dict) else i
        for i in items
    ]
    return trimmed


def _build_leveling_guide_schema_poe2() -> str:
    """POE2 leveling_guide example JSON 을 campaign_structure_poe2.json 에서 동적 조립.

    패치 버전마다 Act 구조가 바뀌어도 GGPK 재추출 + build_poe2_campaign_structure.py 재실행 만으로
    SYSTEM_PROMPT 자동 갱신. 파일 없으면 최소 fallback (1-3 + endgame) 반환 — LLM 이 오작동
    하지 않도록 유효 JSON 유지.
    """
    struct_path = Path(__file__).resolve().parent.parent / "data" / "campaign_structure_poe2.json"
    if not struct_path.exists():
        logger.warning(
            "[campaign_structure_poe2.json 부재] — scripts/build_poe2_campaign_structure.py 재실행 필요. fallback 사용."
        )
        return (
            '{\n'
            '    "acts_1_3": "Act 1-3 전반 캠페인 (Lv 1~40)",\n'
            '    "endgame_maps": "Waystone / Atlas 엔드게임 (Lv 65+)"\n'
            '  }'
        )
    try:
        with struct_path.open(encoding="utf-8") as f:
            struct = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        logger.warning(f"[campaign_structure_poe2.json 로드 실패: {e}] — fallback 사용")
        return (
            '{\n'
            '    "acts_1_3": "Act 1-3 전반 캠페인 (Lv 1~40)",\n'
            '    "endgame_maps": "Waystone / Atlas 엔드게임 (Lv 65+)"\n'
            '  }'
        )
    lines = ["{"]
    phases = struct.get("phases", [])
    for i, p in enumerate(phases):
        key = p["key"]
        lvl = p.get("level_range") or [0, 0]
        towns = p.get("towns") or []
        note = p.get("note") or ""
        transient_tag = " (transient — 다음 패치 재편 가능)" if p.get("transient") else ""
        town_hint = f", towns: {', '.join(towns[:3])}" if towns else ""
        hint = f"Lv {lvl[0]}~{lvl[1]} 전략{town_hint}{': ' + note if note else ''}{transient_tag}"
        # JSON 문자열 escape
        hint_escaped = hint.replace("\\", "\\\\").replace('"', '\\"')
        comma = "," if i < len(phases) - 1 else ""
        lines.append(f'    "{key}": "{hint_escaped}"{comma}')
    lines.append("  }")
    return "\n".join(lines)


def get_system_prompt(game: str) -> str:
    """게임별 system prompt. POE2 는 campaign_structure 로부터 leveling_guide 스키마 동적 치환."""
    if game == "poe2":
        return SYSTEM_PROMPT_POE2.replace(
            "@@LEVELING_GUIDE_SCHEMA@@", _build_leveling_guide_schema_poe2()
        )
    return SYSTEM_PROMPT_POE1


def coach_build(build_data: dict, model: str = "claude-sonnet-4-6", game: str = "poe1") -> dict:
    client = anthropic.Anthropic()

    # 게임별 system prompt — POE2 는 GGPK 파생 campaign_structure 로 leveling_guide 동적 치환
    system_prompt = get_system_prompt(game)
    logger.info(f"코치 모드: {game} (prompt={len(system_prompt)}자)")

    archetype = detect_archetype(build_data)
    archetype_data = load_archetype_data(archetype) if game == "poe1" else {}

    logger.info(f"아키타입 감지: {archetype}")

    # 게임 데이터 로드 (추출된 .datc64 기반) — 게임별 디렉터리 분기 (I4 leak 차단)
    game_data_context = ""
    try:
        from game_data_provider import GameData
        gd = GameData(game=game)
        game_data_context = gd.build_context_for_coach(build_data)
        if game_data_context:
            logger.info("게임 데이터 컨텍스트 로드 완료 (%s)", game)
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

    # 4-stage progression 지원: __extra_builds__ 필드 있으면 보조 POB들의 skills/gear 요약 추출
    # get + 분리 dict 생성 — 원본 mutate 회피 (호출자가 동일 build_data 참조해도 안전)
    extra_builds = (build_data.get("__extra_builds__", [])
                    if isinstance(build_data, dict) else [])
    primary_build = (
        {k: v for k, v in build_data.items() if k != "__extra_builds__"}
        if isinstance(build_data, dict) else build_data
    )
    primary_build = _trim_build_for_prompt(primary_build)

    # pob_parser의 alternate_gem_sets (비활성 SkillSet) — 레벨링 SkillSet 정보 소스
    alternate_skill_info = ""
    if isinstance(primary_build, dict):
        stages = primary_build.get("progression_stages", [])
        if stages and isinstance(stages[0], dict):
            alt_sets = stages[0].get("alternate_gem_sets", {})
            if alt_sets:
                alt_lines = []
                for title, gems in alt_sets.items():
                    gems_text = ", ".join(
                        f"{label}({v.get('links','') if isinstance(v, dict) else v})"
                        for label, v in gems.items()
                    )
                    alt_lines.append(f"- **{title}**: {gems_text}")
                alternate_skill_info = "\n".join(alt_lines)

    # === Prompt caching 전략 ===
    # 프롬프트 캐싱은 prefix 매칭 — 안정 콘텐츠가 **반드시** 변동 콘텐츠 앞에 와야 한다.
    # render 순서: tools → system → messages. system은 SYSTEM_PROMPT (글로벌 안정).
    # messages에선 user content를 3 블록으로 분할:
    #   (1) stable_global: 전 사용자/빌드 공통 — support 젬, 보이드스톤, 패치노트
    #   (2) stable_class:  클래스·아키타입 공통 — archetype 데이터, 클래스 퀘스트 보상
    #   (3) variable:      POB 개별 — 빌드 JSON, 보조 SkillSet, extras, Wiki, game data
    # 각 stable 블록 끝에 cache_control ephemeral → 2회차부터 해당 구간 ~90% 할인.
    # variable은 매번 full price (어차피 POB마다 다름).
    stable_global_parts: list[str] = []
    stable_class_parts: list[str] = []
    variable_parts: list[str] = []

    # (3) VARIABLE — POB 빌드 본체
    variable_parts.append(
        "이 POB 빌드를 범용(SC/HC/SSF/Trade 전부) 관점으로 분석하고 고르게 코칭해줘 — 한 모드로 편향되지 않게:\n\n"
        + json.dumps(primary_build, ensure_ascii=False)
    )

    if alternate_skill_info:
        variable_parts.append(
            "\n\n**POB 내 보조 SkillSet** (주 스킬 외에 이 POB에 저장된 레벨링/전환 스킬 세트 — "
            "`leveling_skills.options` 및 `skill_transitions` 작성 시 반드시 반영):\n"
            + alternate_skill_info
        )
        logger.info("alternate_gem_sets: %d개 보조 SkillSet 컨텍스트 추가",
                    len(alt_sets) if isinstance(primary_build, dict) and primary_build.get("progression_stages") else 0)

    # 사용자가 2단계 보조 POB를 추가했으면, 그 POB들의 전체 progression을 AI에 전달 (VARIABLE)
    if extra_builds:
        progression_summary = []
        for i, eb in enumerate(extra_builds, start=2):
            if not isinstance(eb, dict):
                continue
            meta = eb.get("meta", {})
            name = meta.get("build_name", f"POB {i}")
            lvl = meta.get("class_level", "?")
            stage = eb.get("progression_stages", [{}])[0] if eb.get("progression_stages") else {}
            gems = stage.get("gem_setups", {})
            gear = stage.get("gear_recommendation", {})
            gems_text = ", ".join(
                f"{label}({v.get('links','') if isinstance(v, dict) else ', '.join(v) if isinstance(v, list) else v})"
                for label, v in gems.items()
            )
            uniques = [g.get("name") for g in gear.values() if isinstance(g, dict) and g.get("rarity") == "Unique"]
            progression_summary.append(
                f"### {i}단계 POB: {name} (Lv {lvl})\n"
                f"- 스킬 그룹: {gems_text or '(없음)'}\n"
                f"- 주요 유니크: {', '.join(uniques) if uniques else '(없음)'}"
            )
        if progression_summary:
            variable_parts.append(
                "\n\n**중요**: 유저가 제공한 **전체 스킬 전환 progression** — 1단계(최종 빌드) 외에도 "
                "여러 스테이지 POB가 있음. 레벨링 가이드 작성 시 이 progression 순서와 각 스테이지 "
                "스킬을 반드시 반영해라. `leveling_skills.options`에 아래 POB들의 스킬을 옵션으로 포함하고, "
                "`skill_transitions` 배열에 실제 전환 Lv/스킬 반영:\n\n"
                + "\n\n".join(progression_summary)
            )
            logger.info("4-stage progression: %d개 보조 POB 컨텍스트 추가", len(extra_builds))

    if wiki_item_info:
        variable_parts.append(f"\n\n유니크 아이템 실제 획득 정보 (Wiki 기준, 이 데이터를 반드시 참고):\n{json.dumps(wiki_item_info, ensure_ascii=False)}")

    # 게임 데이터 컨텍스트는 POB 빌드의 젬 목록에 의존 → VARIABLE
    if game_data_context:
        variable_parts.append(f"\n\n{game_data_context}")

    # (2) STABLE_CLASS — 클래스/아키타입 공통 (archetype 4개 × class 7개 = 최대 28 캐시 엔트리)
    if archetype_data:
        leveling = archetype_data.get("leveling_skill_progression", {})
        auras = archetype_data.get("aura_progression", {})
        aura_utility = archetype_data.get("aura_herald_utility_by_level", [])
        curses = archetype_data.get("curse_setup", {})
        movement = archetype_data.get("movement_skill", {})
        stable_class_parts.append(f"\n\n아키타입: {archetype}\n레벨링 스킬 데이터:\n{json.dumps(leveling, ensure_ascii=False)}")
        if aura_utility:
            stable_class_parts.append(f"\n오라/전령/유틸리티 구간별 추천 (이 데이터를 기반으로 aura_utility_progression 작성):\n{json.dumps(aura_utility, ensure_ascii=False)}")
        else:
            stable_class_parts.append(f"\n오라 추천 (요약):\n{json.dumps(auras, ensure_ascii=False)}")
        if curses:
            stable_class_parts.append(f"\n저주 추천:\n{json.dumps(curses, ensure_ascii=False)}")
        if movement:
            stable_class_parts.append(f"\n이동기 추천:\n{json.dumps(movement, ensure_ascii=False)}")

    # game_data 없으면 class_rewards 폴백 — 클래스별 stable
    if not game_data_context and class_rewards:
        char_class = build_data.get("meta", {}).get("class", "")
        stable_class_parts.append(f"\n\n{char_class} 클래스 퀘스트 젬 보상:\n{json.dumps(class_rewards, ensure_ascii=False)}")

    # (1) STABLE_GLOBAL — 전 사용자 공통 (support gems + 보이드스톤 + 패치노트)
    support_gems = load_valid_support_gems(game=game)
    if support_gems:
        game_label = "POE2" if game == "poe2" else "POE1"
        stable_global_parts.append(
            f"\n\n**{game_label} Support 젬 화이트리스트 ({len(support_gems)}개)** — "
            f"아래 목록에 없는 support 젬은 **절대 추천하지 마라**. "
            f"기본/각성(Awakened)/디바전트(Divergent) 등 quality variant은 이름이 다르면 별도 젬으로 취급:\n"
            + ", ".join(support_gems)
        )
        logger.info(f"{game_label} Support 젬 화이트리스트 주입: {len(support_gems)}개")

    # POE2 전용: Active 스킬 화이트리스트 + Spear 21 anchor
    if game == "poe2":
        active_skills = load_valid_active_skills_poe2()
        if active_skills:
            names = [s.get("name", "") for s in active_skills if s.get("name")]
            spear_skills = sorted(
                s.get("name", "") for s in active_skills
                if s.get("weapon_requirements") == 25
            )
            stable_global_parts.append(
                f"\n\n**POE2 Active 스킬 화이트리스트 ({len(names)}개)** — "
                f"이 목록에 없는 액티브 스킬 이름 절대 사용 금지:\n"
                + ", ".join(names[:300])  # 처음 300개 (나머지는 truncate, 토큰 절약)
            )
            stable_global_parts.append(
                f"\n\n**Spear 전용 스킬 {len(spear_skills)}개 (WeaponRequirements=25 GGPK 실측)** — "
                f"이 스킬 사용 시 반드시 Spear 장착 필요. Bow/Quarterstaff/기타 조합 추천 금지:\n"
                + ", ".join(spear_skills)
            )
            logger.info(
                "POE2 Active 화이트리스트 주입: %d개 (Spear %d)",
                len(names), len(spear_skills),
            )

    # 공통 템플릿에서 보이드스톤/장비 타이밍 로드 (GLOBAL, POE1 전용)
    if game == "poe1":
        common_path = Path(__file__).resolve().parent.parent / "data" / "guide_templates" / "common_template.json"
        common_data = {}
        if common_path.exists():
            with open(common_path, "r", encoding="utf-8") as f:
                common_data = json.load(f)
        if common_data:
            vs_data = common_data.get("voidstone_progression", {})
            gear_data = common_data.get("gear_upgrade_timeline", {})
            if vs_data:
                stable_global_parts.append(f"\n\n보이드스톤 진행 (3.28 미라지):\n{json.dumps(vs_data, ensure_ascii=False)}")
            if gear_data:
                stable_global_parts.append(f"\n장비 업그레이드 타이밍:\n{json.dumps(gear_data, ensure_ascii=False)}")

    # 최신 패치 컨텍스트 주입 (GLOBAL, 리그 전환 시만 변경) — POE1 전용 (POE2 는 SYSTEM_PROMPT 에 내장)
    patch_context = load_patch_context() if game == "poe1" else {}
    if patch_context:
        patch_ver = patch_context.get("version", "")
        logger.info(f"패치 컨텍스트 로드: {patch_ver}")
        stable_global_parts.append(f"\n\n최신 패치 정보 ({patch_ver}):\n{json.dumps(patch_context, ensure_ascii=False)}")
        stable_global_parts.append("\n위 패치 정보를 반드시 참고해서 답변해줘. 버프된 스킬은 추천도를 올리고, 너프된 스킬은 주의사항에 포함해.")

    # 캐시 효율 관측용 (디버깅 — 각 블록 대략 토큰 수 측정)
    stable_global = "\n".join(stable_global_parts)
    stable_class = "\n".join(stable_class_parts)
    variable_text = "\n".join(variable_parts)
    # 전체 문자열 (max_tokens 계산용 호환)
    user_message = stable_global + stable_class + variable_text

    # 프롬프트 크기에 따라 max_tokens 동적 조정 (4-stage 같은 큰 컨텍스트 → 출력도 커짐)
    prompt_chars = len(user_message) + len(system_prompt)
    # 대략 8192(기본) ~ 32000 (Sonnet 4.6 최대 output 64k까지 가능하나 32k로 안전)
    max_out = 32000 if prompt_chars > 30000 else 16384
    # 큰 요청은 SDK가 스트리밍 강제 (>10분 가능성). 30k자 또는 max_out>=16384면 스트리밍 사용.
    use_streaming = prompt_chars > 30000 or max_out >= 16384
    logger.info(
        f"Claude {model}에게 빌드 코칭 요청 중 "
        f"(prompt~{prompt_chars}자, max_out={max_out}, streaming={use_streaming})..."
    )

    # Prompt caching 적용 — 블록 구성:
    #  • system:  [SYSTEM_PROMPT + cache_control]  → 1 breakpoint (tools+system 전체 캐시)
    #  • messages[0].content[0]: stable_global     + cache_control → 2 breakpoint
    #  • messages[0].content[1]: stable_class      + cache_control → 3 breakpoint (없으면 skip)
    #  • messages[0].content[-1]: variable_text    (캐시 불가)
    # 같은 POB 재분석 / 같은 클래스 재분석 시 cache_read 경로로 입력 ~90% 할인.
    system_blocks = [{
        "type": "text",
        "text": system_prompt,
        "cache_control": {"type": "ephemeral"},
    }]

    user_content: list[dict] = []
    if stable_global:
        user_content.append({
            "type": "text",
            "text": stable_global,
            "cache_control": {"type": "ephemeral"},
        })
    if stable_class:
        user_content.append({
            "type": "text",
            "text": stable_class,
            "cache_control": {"type": "ephemeral"},
        })
    # Variable POB 블록 — cache_control 없음 (매번 달라서 의미 없음)
    user_content.append({
        "type": "text",
        "text": variable_text,
    })

    messages = [{"role": "user", "content": user_content}]

    if use_streaming:
        # 스트리밍 — chunk 누적
        raw_text = ""
        stop_reason = None
        with client.messages.stream(
            model=model,
            max_tokens=max_out,
            system=system_blocks,
            messages=messages,
        ) as stream:
            for text_chunk in stream.text_stream:
                raw_text += text_chunk
            final_msg = stream.get_final_message()
            stop_reason = getattr(final_msg, "stop_reason", None)
            # 토큰 정보 (logging용)
            response = final_msg
    else:
        response = client.messages.create(
            model=model,
            max_tokens=max_out,
            system=system_blocks,
            messages=messages,
        )
        raw_text = response.content[0].text
        stop_reason = getattr(response, "stop_reason", None)
    if stop_reason == "max_tokens":
        logger.warning(
            "Claude 응답이 max_tokens(%d) 에서 잘림 — JSON 복구 시도",
            max_out,
        )

    # JSON 파싱: 3단계 복구 시도
    def _parse_or_repair(text: str) -> dict:
        # 1) 그대로 파싱
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        # 2) 첫 '{' ~ 마지막 '}' 부분 추출
        s = text.find('{')
        e = text.rfind('}')
        if s != -1 and e > s:
            try:
                return json.loads(text[s:e + 1])
            except json.JSONDecodeError:
                pass
        # 3) Truncation 복구 — 마지막 완전한 키-값까지만 취하고 닫음
        if s != -1:
            segment = text[s:]
            # 마지막으로 닫힌 값 위치 추정 — 콤마 뒤 또는 닫는 괄호 전
            # 간단 휴리스틱: 깊이 tracking + 마지막 유효 offset 찾기
            depth = 0
            in_str = False
            escape = False
            last_valid = -1
            for i, ch in enumerate(segment):
                if escape:
                    escape = False
                    continue
                if ch == '\\' and in_str:
                    escape = True
                    continue
                if ch == '"' and not escape:
                    in_str = not in_str
                    continue
                if in_str:
                    continue
                if ch == '{' or ch == '[':
                    depth += 1
                elif ch == '}' or ch == ']':
                    depth -= 1
                    if depth == 0:
                        last_valid = i + 1
                elif ch == ',' and depth == 1:
                    last_valid = i  # 최상위 콤마는 객체 경계
            if last_valid > 0:
                candidate = segment[:last_valid].rstrip().rstrip(',')
                # 닫힘 부족 시 보충
                open_braces = candidate.count('{') - candidate.count('}')
                open_brackets = candidate.count('[') - candidate.count(']')
                candidate += ']' * open_brackets + '}' * open_braces
                try:
                    repaired = json.loads(candidate)
                    logger.warning("JSON truncation 복구 성공 (%d자 보존)", len(candidate))
                    return repaired
                except json.JSONDecodeError as e:
                    logger.error("JSON 복구 실패: %s", e)
        return {"error": "JSON 파싱 실패", "raw": text, "stop_reason": stop_reason}

    result = _parse_or_repair(raw_text)

    result.setdefault("aura_utility_progression", [])
    result.setdefault("leveling_skills", {})
    result.setdefault("build_rating", {})
    result.setdefault("gear_progression", [])
    result.setdefault("map_mod_warnings", {})
    result.setdefault("variant_snapshots", [])
    result.setdefault("passive_priority", [])

    # AI 출력 정규화 — 젬 이름 canonical 강제 (Phase H2) + gear (Phase H3)
    # 정규화 후 검증이라 hallucination 경고 대폭 감소.
    norm_warnings: list[str] = []
    norm_trace: list[dict] = []
    try:
        from coach_normalizer import normalize_coach_output
        gem_warnings, gem_trace = normalize_coach_output(result, game=game)
        norm_warnings.extend(gem_warnings)
        norm_trace.extend(gem_trace)
    except ImportError:
        pass

    # gear_normalizer 는 POE1 베이스/유닉 DB 기반 — POE2 DB 미구축 → skip.
    if game == "poe1":
        try:
            from gear_normalizer import normalize_gear
            gear_warnings, gear_trace = normalize_gear(result)
            norm_warnings.extend(gear_warnings)
            norm_trace.extend(gear_trace)
        except ImportError:
            pass

    # L3 Gate + Auto-retry (Phase H6) — drop 발견 시 1회 교정 재시도
    # blind retry 아님: 이전 응답의 invalid 젬을 구체적으로 명시한 corrective prompt.
    # Haiku 기본 모델 기준 최악 2x API call — 전형 케이스는 1회로 종결.
    first_attempt_dropped: list[str] = [
        t["from"] for t in norm_trace if t.get("match_type") == "dropped"
    ]
    retry_info: dict | None = None

    if first_attempt_dropped:
        logger.warning(
            "L3 retry 시작 — %d건 drop: %s",
            len(first_attempt_dropped), first_attempt_dropped,
        )
        game_label = "POE2" if game == "poe2" else "POE1"
        corrective_text = (
            f"이전 응답에 {game_label}에 존재하지 않는 젬 {len(first_attempt_dropped)}개가 포함돼 자동 제거됐습니다: "
            f"{', '.join(repr(g) for g in first_attempt_dropped)}. "
            f"이 젬들은 {game_label} valid_gems 화이트리스트에 없습니다 (hallucination). "
            f"이들을 제거하거나 유효한 대체 젬으로 바꿔서, 같은 JSON 스키마로 처음부터 다시 작성하세요. "
            f"확신 없는 젬은 추측하지 말고 생략하세요."
        )
        user_content_retry = list(user_content) + [{"type": "text", "text": corrective_text}]
        messages_retry = [{"role": "user", "content": user_content_retry}]

        if use_streaming:
            raw_text = ""
            stop_reason = None
            with client.messages.stream(
                model=model,
                max_tokens=max_out,
                system=system_blocks,
                messages=messages_retry,
            ) as stream:
                for text_chunk in stream.text_stream:
                    raw_text += text_chunk
                final_msg = stream.get_final_message()
                stop_reason = getattr(final_msg, "stop_reason", None)
                response = final_msg
        else:
            response = client.messages.create(
                model=model,
                max_tokens=max_out,
                system=system_blocks,
                messages=messages_retry,
            )
            raw_text = response.content[0].text
            stop_reason = getattr(response, "stop_reason", None)

        retry_result = _parse_or_repair(raw_text)
        retry_result.setdefault("aura_utility_progression", [])
        retry_result.setdefault("leveling_skills", {})
        retry_result.setdefault("build_rating", {})
        retry_result.setdefault("gear_progression", [])
        retry_result.setdefault("map_mod_warnings", {})
        retry_result.setdefault("variant_snapshots", [])

        retry_warnings: list[str] = []
        retry_trace: list[dict] = []
        try:
            from coach_normalizer import normalize_coach_output
            w, t = normalize_coach_output(retry_result, game=game)
            retry_warnings.extend(w)
            retry_trace.extend(t)
        except ImportError:
            pass
        if game == "poe1":
            try:
                from gear_normalizer import normalize_gear
                w, t = normalize_gear(retry_result)
                retry_warnings.extend(w)
                retry_trace.extend(t)
            except ImportError:
                pass

        final_dropped = [
            t["from"] for t in retry_trace if t.get("match_type") == "dropped"
        ]
        logger.info(
            "L3 retry 완료 — drop %d → %d",
            len(first_attempt_dropped), len(final_dropped),
        )

        # 재시도 결과 채택 — 교정 성공이든 실패든 두 번째 응답이 더 나은 근거
        result = retry_result
        norm_warnings = retry_warnings
        norm_trace = retry_trace
        retry_info = {
            "attempts": 2,
            "recovered_from": first_attempt_dropped,
            "final_dropped": final_dropped,
        }

    if norm_trace:
        logger.info("코치 출력 자동 교정 %d건:", len(norm_trace))
        for t in norm_trace:
            logger.info("  ✎ %s: %r -> %r (%s)",
                        t["field"], t["from"], t["to"], t["match_type"])
        result["_normalization_trace"] = norm_trace
    if norm_warnings:
        logger.info("코치 출력 정규화 — 매칭 실패 %d건", len(norm_warnings))
    if retry_info:
        result["_retry_info"] = retry_info
        recovered_count = len(retry_info.get("recovered_from") or [])
        final_dropped_count = len(retry_info.get("final_dropped") or [])
        recovery_success = final_dropped_count == 0 and recovered_count > 0
        logger.info(
            "L3_RETRY_METRIC attempts=%d recovered_from=%d final_dropped=%d success=%s",
            retry_info.get("attempts", 0),
            recovered_count,
            final_dropped_count,
            "true" if recovery_success else "false",
        )

    # AI 출력 검증 — quest_rewards cross-check + 스키마 + 범위
    try:
        from coach_validator import validate_coach_output
        validation_warnings = validate_coach_output(result, primary_build, game=game)
        combined = norm_warnings + validation_warnings
        if combined:
            logger.warning("AI 코치 출력 경고 %d건 (정규화 %d + 검증 %d):",
                           len(combined), len(norm_warnings), len(validation_warnings))
            for w in combined:
                logger.warning("  - %s", w)
            # 결과에 메타 포함 — UI에서 뱃지 표시 가능
            result["_validation_warnings"] = combined
        elif norm_warnings:
            result["_validation_warnings"] = norm_warnings
    except ImportError:
        if norm_warnings:
            result["_validation_warnings"] = norm_warnings

    # 토큰 사용량 + 캐시 히트 로그 — 캐시 동작 가시화.
    # input_tokens = 캐시 미적용 잔여 (full price)
    # cache_read_input_tokens = 캐시 hit (~10% price)
    # cache_creation_input_tokens = 첫 write (1.25x price)
    # 2회차부터 cache_read ↑ 이면 설계대로 동작.
    usage = response.usage
    cache_read = getattr(usage, "cache_read_input_tokens", 0) or 0
    cache_write = getattr(usage, "cache_creation_input_tokens", 0) or 0
    total_input = usage.input_tokens + cache_read + cache_write
    cache_ratio = (cache_read / total_input * 100) if total_input else 0
    logger.info(
        f"코칭 완료. 토큰: uncached={usage.input_tokens}, "
        f"cache_read={cache_read} ({cache_ratio:.0f}%), cache_write={cache_write}, "
        f"output={usage.output_tokens}"
    )
    return result


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="PathcraftAI Build Coach")
    ap.add_argument("input", help="POB JSON 파일 경로 또는 '-' (stdin)")
    ap.add_argument("--model", default="claude-sonnet-4-6", help="Claude 모델")
    # D6: --game poe1|poe2 분기 — POE2 시 SYSTEM_PROMPT_POE2 + valid_gems_poe2.json 사용
    ap.add_argument("--game", choices=["poe1", "poe2"], default="poe1",
                    help="대상 게임 (poe1=POE1 3.28 Mirage / poe2=POE2 0.4.0d Fate of the Vaal)")
    args = ap.parse_args()

    if args.input == "-":
        build_data = json.load(sys.stdin)
    else:
        with open(args.input, 'r', encoding='utf-8') as f:
            build_data = json.load(f)

    result = coach_build(build_data, model=args.model, game=args.game)
    # DEBUG (2026-04-22 S4): D6 해제 조건 관찰용 파일 덤프. 검증 끝나면 제거.
    try:
        import pathlib as _pl
        _dbg = _pl.Path(__file__).resolve().parent.parent / "_debug"
        _dbg.mkdir(exist_ok=True)
        (_dbg / f"coach_last_{args.game}.json").write_text(
            json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    except OSError as _e:
        logger.warning(f"[debug-dump] failed: {_e}")
    print(json.dumps(result, ensure_ascii=False))
