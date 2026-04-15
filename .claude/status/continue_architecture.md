# Continue 체인 아키텍처 (β)

> Aurora Glow 단일 매칭 → Wreckers식 Continue 캐스케이드로 전면 전환.

## 원칙

1. **레이어 독립성**: 각 레이어는 단일 관심사(색/보더/아이콘/사운드 중 일부)만 수정
2. **순서 의존 명시**: 레이어 순서를 상수로 고정, 변경 시 반드시 문서 갱신
3. **Continue 기본**: 모든 레이어는 `Continue`로 종료 (마지막 Show 제외)
4. **디버그 주석**: 각 블록 주석에 `[layer:N]` 포함 → 최종 스타일 추적 가능
5. **SSF 철학**: 커런시/젬/플라스크/프래그먼트/디비카 절대 숨기지 않음
6. **레퍼런스 채택 순서**: **Wreckers 형식이 기본.** Cobalt/NeverSink 규칙은 그대로 이식 불가 — first-match 전제라 Continue 캐스케이드에서 상위 데코를 덮어쓰는 회귀가 나옴. Wreckers에 없고 Cobalt에만 있는 규칙은 리서치 → PathcraftAI 스타일로 재작성. 무조건 복붙 금지.

## 레이어 순서 (위 → 아래 = 먼저 평가 → 나중 평가)

| # | 이름 | 역할 | Continue | 상태 |
|---|------|------|----------|------|
| 0 | HARD_HIDE | 절대 숨김 (Scroll Fragment 등) | × (정지) | 구현 |
| 1 | CATCH_ALL | 오렌지 미분류 안전망 | ✓ | 구현 |
| 2 | DEFAULT_RARITY | Normal/Magic/Rare 기본 색 | ✓ | 구현 |
| 3 | SOCKET_BORDER | Chromatic RGB / Jeweller 6S 핑크 보더 | ✓ | 구현 |
| 4 | SPECIAL_BASE | 특수 베이스 오렌지 복원 | ✓ | 구현 (Wreckers L146) |
| 5 | CORRUPT_BORDER | 부패/타락/미러 빨강 보더 | ✓ | 구현 |
| 6 | T1_BORDER | ilvl≥86 + 크래프팅 베이스 → 레어리티색 보더 + Star | ✓ | 구현 |
| 7 | BUILD_TARGET | POB 빌드 타겟 아이템 강조 | ✓ | 구현 |
| 8 | CATEGORY_SHOW | 커런시/젬/플라스크/맵/디비카/유니크 (최종 스타일) | × | 구현 |
| 9 | PROGRESSIVE_HIDE | AL 기반 단계적 Hide (Normal AL≥14, Magic AL≥24 등) | ✓ (재Show 허용) | 구현 |
|10 | RE_SHOW | Jewel/Flask/Tincture/Cluster 등 예외 Show | × | 구현 |
|11 | ENDGAME_RARE | 엔드게임 레어 Hide (droplevel + blanket) | × | 구현 (Cobalt Strict [[2000]]/[[2200]]/[[2700]]) |
|12 | REST_EX | 미분류 최종 안전망 | × | backlog |

## 구현 현황 (2026-04-14)

**L4 SPECIAL_BASE** — 구현 완료 (β-4a)
- 레퍼런스: Wreckers SSF Filter L146 "Catch All, 'WTF is that?!' items"
- 단일 블록 + 108종 BaseType 오렌지 텍스트 복원
- L2316 "LEAGUE / NEW ITEMS" 섹션(오렌지 보더 + 사운드)은 카테고리 중복 위험으로 **제외** — 필요 시 L10 RE_SHOW 확장으로 처리

**L11 ENDGAME_RARE** — 구현 완료 (β-4a, 2026-04-14 audit 후 축소)
- 레퍼런스: Cobalt Strict `[[2000]]`/`[[2200]]`/`[[2700]]`
- 6개 Hide 블록 (Continue=False, 최종):
  - 부패 unidentified 임플리싯 없음 (Amulets/Belts/Rings 제외)
  - 미러 unidentified 임플리싯 없음 (동일)
  - DropLevel 3단계 (AL 80/DL<60, AL 78/DL<50, AL 73/DL<40)
  - Normal/Magic blanket (AL>=68)
- **`[[2700]] raresendgame` blanket Hide는 의도적으로 제외.**
  - 이유: Cobalt는 first-match 구조라 상위 Show(T1 crafts/sized rares/4-link)가 이미 최종 확정 후 blanket Hide 도달. 우리 β는 Continue 캐스케이드 → L6/L7/L8 rare Show가 전부 Continue=True 데코레이션. blanket Hide가 전부 덮어씀 = T1 크래프팅 베이스/sized rare/corrupted implicit rare 전부 숨김 회귀.
  - Wreckers SSF 원본에도 blanket Rare Hide 없음 — AL 기반 Normal/Magic hide만 있음. 우리 선택은 Wreckers 철학 쪽.
- L12 REST_EX는 현재 미구현

### 캐스케이드 충돌 처리 이력

**Scrap/Whetstone 전 AL styling 누락 fix (2026-04-15, 인게임 검증 발견):**
- 인게임에서 Armourer's Scrap (방어구 장인의 고철) / Blacksmith's Whetstone (무기 장인의 숫돌)이 AL>67 맵에서 unstyled 폴스루.
- 원인: 두 base가 `LEVELING_SUPPLY_BASES` 제외 셋에 포함 → layer_currency P5_MINOR/P6_LOW 처리 안 함. layer_leveling_supplies의 `leveling_supply_basic` 블록은 `AreaLevel <= 67` 조건 → AL>67에서 미매칭.
- Fix: LEVELING_SUPPLY_BASES에서 두 base 제거 (Wisdom/Portal Scroll만 남김). leveling_supply_basic 블록 제거. 결과: 전 AL에서 layer_currency가 P5/P6 코랄 팔레트로 styling.
- 회귀 테스트: `TestLevelingSupplyRouting` (3 mode 매트릭스 + 데드 블록 검증).

**T1 MAX 라우팅 dedup (2026-04-15, audit-all 발견):**
- `layer_currency`(L8 currency) → `layer_basic_orbs`(L8 basic_orbs) 순서 실행. 동일 BaseType이 두 레이어에서 매칭되면 먼저 매칭한 currency 블록이 `continue=False`로 잠겨 basic_orbs T1 MAX(흰BG+빨강+sound 6) 블록이 dead code 됨.
- `LEVELING_SUPPLY_BASES` 셋이 명시적 dedup 역할 — 여기 등록된 base는 layer_currency가 스킵 → layer_basic_orbs/leveling_supplies가 처리.
- **2026-04-15 fix**: `Awakener's Orb` 누락 발견. T1 MAX 블록에 추가했지만 LEVELING_SUPPLY_BASES에서 빠져있어 layer_currency P1_KEYSTONE이 먼저 잠금 → 추가됨.
- **회귀 테스트**: `TestT1MaxRouting.test_t1_max_orbs_route_only_to_basic_orbs` (3 mode × 5 base 매트릭스).
- **향후 T1 MAX 블록 base 추가 시 체크리스트**: ① layer_basic_orbs 블록에 base 추가 → ② LEVELING_SUPPLY_BASES 셋에도 추가 → ③ 회귀 테스트 base 리스트 갱신.

**적용된 수정 (2026-04-14):**
- L11 `normalmagic_blanket` Class 목록에서 `"Utility Flasks"` 제외. L8 `layer_flasks_quality`가 Utility Flask Magic을 Continue=True 데코(보더 `100 200 200`)로 표시 → L11이 덮어쓰면 맵핑에서 Utility Flask Magic 전부 숨김 회귀. Wreckers L232 철학(`Class "Flask" "Tincture" ...` 무조건 Show) 적용.
- L9 `leveling_bases_early` / `equipment_bases_midgame` 533블록에 `Rarity Normal Magic` 가드 추가. BaseType 전용 Hide가 Unique Tabula Rasa/Goldrim/Redbeak 등 67+개 유니크 드롭 숨김 회귀. Rarity 제약으로 Unique/Rare 보호.

**Phase 5 색 선택 기준 (2026-04-14):**
- **Cobalt 정확 매핑**: Mirror-tier 입장권 (Relic Keys, Vault Keys) — 흰BG + 빨강 + Red Star + Sound 6. T1 시각 convention이 POE 커뮤니티 common knowledge이므로 색 변경 시 가치 인식 저하.
- **Aurora 재해석**: 리그 컨텐츠 진입 (Expedition Logbook, Sanctum Research, Chronicle of Atzoatl, Inscribed Ultimatum) — Aurora unique/currency 팔레트 적용. Pathcraft의 카테고리별 hue 정체성 편입 + 시각 다양성.
- 판정 기준: "이 아이템의 시각 기호가 POE 커뮤니티 convention인가" → Yes = Cobalt, No = Aurora.

**Cobalt/Aurora 재검토 (2026-04-15):**
- 현 구현 audit 결과 기준에 정합. Relic/Vault Keys (흰BG+빨강)·Divine/Mirror/Mirror Shard/Sacred Orb (Crimson+red star+sound 6) Cobalt 정확 매핑. Expedition/Sanctum/Chronicle/Ultimatum Aurora palette.
- **발견**: `Awakener's Orb`이 `layer_basic_orbs` T1 MAX 블록에 누락 — Sirus 드롭+Influence 크래프팅용 Mirror-tier 커런시로 POE 커뮤니티 T1 convention 강함. `layer_currency` P1_KEYSTONE 등록은 있었으나 red star+sound 6 대신 Cyan cross 처리. T1 MAX 블록에 추가 (2026-04-15).
- `Hinekora's Lock`/`Reflecting Mist`: 신규/희귀 커런시로 커뮤니티 convention 미정착 — Aurora P1 유지가 안전.

**Unique tier 디듀플리케이션 (2026-04-14, Phase 3a audit):**
- Cobalt 원본이 first-match 기반이라 [4702] T1/T2가 먼저 Show+no-Continue로 잠기면 [4704]/[4707] 중복 BaseType은 트리거 안 됨. Raw JSON 그대로 우리 Continue=True 캐스케이드에 이식 시 **하위 티어가 상위 덮어쓰기** 회귀 (T2 Deicide Mask → P3_USEFUL 다운그레이드, T3 Bone Helmet → P4_SUPPORT 등 47 base 영향).
- 수정: `_load_unique_tiers()`에서 우선순위 t1 > multi_high > t2 > t3 > t4 > t5로 디듀플리케이션. Cobalt first-match 시맨틱을 Continue 캐스케이드에 이식.
- 향후 JSON 업데이트 시 동일 패턴 주의: 원본 필터의 Show 블록 순서가 곧 "우선순위"이므로 union 이식 금지 → 중복 제거 필수.

**Epic 6-Link Continue=False 예외 (2026-04-14, Phase 1c):**
- L3 `epic_6link` / `epic_6link_corrupted` 블록은 Continue=False로 최종 확정. 일반 L3 데코레이션 Continue=True 원칙의 **의도적 예외**.
- 이유: 6-Link Rare는 SSF 연간 최대 이벤트 드롭. L9 Hide / L11 droplevel이 Continue=True 데코레이션을 덮어씀 → 최종 확정 없이는 맵핑에서 숨김.
- Wreckers는 Epic 6-Link를 필터 끝(L2446)에 배치해 자연 우선권 확보. 우리는 L3에서 조기 final로 동일 결과.
- 순서 주의: `epic_6link_corrupted` → `epic_6link` 순서 (POE top-down, 첫 Continue=False 승리). 부패 먼저 매칭되어야 Red border 적용.

**UX 배포 의존성 — 6Link.mp3 (Phase 1c audit, 2026-04-14):**
- `CustomAlertSound "6Link.mp3" 300` 사용 → POE 엔진은 `%USERPROFILE%\Documents\My Games\Path of Exile\6Link.mp3` 파일 탐색.
- 파일 없으면: POE 기본 alert 사운드로 fallback (CustomAlertSoundOptional이 아닌 CustomAlertSound이므로 silent 아님).
- **배포 의존성**: Sanavi 공식 필터 설치 시 6Link.mp3 자동 포함. 우리 필터 단독 설치 사용자는 mp3 수동 복사 필요 — 없으면 Epic 6-Link 시그니처 사운드 상실.
- 향후 대안: `dist/` 또는 `audio/`에 mp3 포함시켜 배포 스크립트가 함께 복사하도록 확장.

### 의도적 미구현 결정 (Phase 7 audit, 2026-04-14)

**Hale/Healthy/Sanguine 제외 조건 — strictness=4 옵트인 구현 (2026-04-15):**
- Cobalt는 `HasExplicitMod 0 "Hale" "Healthy" "Sanguine"` 조건을 Show 블록에 추가하여 저급 생명력 접미사 보유 ID rare를 숨김.
- **기본 비활성 (strictness<=3)**: "Hale + T1 fire resist" 같은 혼합 mod rare missed 리스크 회피. 대부분 유저 안전.
- **strictness=4 (UberPlus) 활성**: `layer_id_mod_filtering`의 per-class Show 블록에 `HasExplicitMod 0 "Hale" "Healthy" "Sanguine"` 추가. Cobalt uberStrict 동등.
- 테스트: `TestIdModFilteringStrictness` 5개 (default/s3/s4/blocks count/beta overlay threading).

**L12 REST_EX — 구현 보류:**
- Cobalt의 RestEx는 first-match 엔진의 "어떤 Show에도 매칭 안 된 아이템" 핑크 안전망. 우리는 L1 CATCH_ALL이 시작부터 모든 아이템에 오렌지 기본 스타일 적용 + Continue=True → 이후 레이어가 덮어씀.
- **판단**: L1 오렌지 기본값이 이미 "미분류 = 눈에 띔" 역할. L12 REST_EX는 중복.
- 단 L11 blanket Hide를 통과한 항목은 최종 숨김 — restex-style "pink 재Show"는 Continue=False 이후 블록이 못 실행되는 구조상 불가.
- 카테고리별 RestEx(fragment_restex)은 이미 구현됨.

**Equipment bases midgame 455 → 599 확장 (2026-04-15):**
- Wreckers SSF 원본 필터 소스 미확보 상태에서 `BaseItemTypes.json` (POE 공식 game_data) 기반 보수적 확장 수행.
- 조건: DL 50~65 장비 (Helmet/BodyArmour/Boots/Gloves/Shield/1H/2H/Quiver) + 기존 entry에 없음 + Abstract/Race/Sovereign 경로 제외.
- 144개 추가 (OneHand 65, TwoHand 35, Shield 22, Helmet 10, Boots 9, Gloves 7, Quiver 6, BodyArmour 4).
- hide_above_al = `min(70, DL + 15)` (기존 median 패턴 정렬).
- 안전성: L9 `equipment_bases_midgame` 블록은 `Rarity Normal Magic` 가드 포함 → Unique/Rare 보호. Normal/Magic만 AL>=hide_al에서 숨김.
- 향후 Wreckers 원본 .filter 확보 시 합집합 재검증 가능.

### 알려진 잠재 충돌 (Normal/Magic T1 데코)

**문제**: `normalmagic_blanket` (L11)은 `AreaLevel >= 68` Normal/Magic 장비 전부 Hide.

Wreckers 원본 L266+에는 `Rarity Normal/Magic Class "Ring" "Glove" "Helmet" ItemLevel >= 85` 식의 T1 보더 데코 블록이 있음 (Life Flask/Mana Flask/Hybrid/Heist Brooch ilvl 84, Utility Flask/Tincture ilvl 85 등). 현재 우리 L6 T1_BORDER는 `Rarity Rare`만 처리 → Normal/Magic T1 데코 미구현 = 충돌 없음.

**미래 리스크**: Normal/Magic T1 보더 데코를 L6에 추가하는 순간 L11 normalmagic_blanket이 이를 덮어씀. `rare_blanket` 제거와 동일한 회귀 패턴.

**대응 원칙 (원칙 6 적용)**:
- Wreckers 원본: Normal/Magic T1 보더 블록은 **Hide Layer(AL 14/24 기반) 아래**에 위치 = Hide+Continue 뒤에 Show+Continue → 최종 Show. 우리 구조도 동일하게 하려면 L11이 아니라 **L10 RE_SHOW 계열** 레이어에서 처리.
- 즉 Normal/Magic T1 데코를 구현할 때는 L6가 아닌 L10 연장으로 넣거나, L10 뒤 L10.5 "T1_RESHOW" 레이어 신설. 그래야 L11 blanket이 먼저 먹고 T1_RESHOW가 되살리는 Wreckers 패턴 성립.
- Cobalt `[[2700]] normalmagicendgame` 단독 이식은 Wreckers T1 데코와 호환 안 됨 — 리서치 후 Pathcraft 스타일 결정 필요. 지금은 L6에 Normal/Magic 데코 없어서 안전.

## 블록 빌더 API (sections_continue.py)

```python
def make_layer_block(
    layer: int,           # 레이어 번호 (0~12)
    comment: str,         # 블록 주석 (layer 태그 자동 추가)
    conditions: list[str],
    style: dict,          # {text, border, bg, font, sound, effect, icon}
    action: str = "Show", # Show | Hide
    continue_: bool = True,
) -> str
```

**style 부분만 설정**: None인 필드는 출력 안 함 (이전 레이어 값 유지 = Continue 캐스케이드 핵심).

예) T1 보더 레이어는 `{"border": "255 255 0", "icon": "0 Yellow Star"}`만 설정. 텍스트 색/폰트는 이전 레이어 유지.

## 엄격도 재설계

기존: 주석 패턴 매칭으로 블록 제거/Hide 전환.
신규: 각 레이어별 `min_strictness` 속성 + **PROGRESSIVE_HIDE** 레이어에서 AL + Strictness 복합 조건.

```python
LAYERS_BY_STRICTNESS = {
    0: 전체 레이어,
    1: [8, 10, 11, ...] + AL 기반 Hide 강화,
    2: ..., 3: ..., 4: ...
}
```

## 디버그 지원

블록 주석 포맷:
```
Show # PathcraftAI [L3|socket] RGB 크로매틱 레시피
```
- `L3` = layer 3 (SOCKET_BORDER)
- `socket` = 카테고리 태그
- 본문 = 사람이 읽는 설명

인게임에서 이상한 스타일 보면 주석으로 어느 레이어가 영향 줬는지 추적.

## 마이그레이션 전략 (브리지 모델)

**핵심 원칙: 구 Aurora 경로를 β-5 완료까지 보존한다.** 중간 단계에서도 항상 동작하는 필터가 나온다.

### 공존 구조

```
filter_generator.py
  ├─ generate_overlay(arch="aurora")   ← 기존 경로 (default, β-5까지 보존)
  └─ generate_overlay(arch="continue") ← 신규 β 경로 (단계적 채움)

CLI: --arch aurora|continue (기본 aurora)
```

- 각 β-N 단계에서 `arch=continue` 출력이 점진적으로 풍부해짐
- `arch=aurora`는 손대지 않음 → 기존 인게임 검증 자산 보존
- β-5 완료 + 인게임 확인 후 `arch=aurora` 경로 삭제

### 단계별 산출물

| 단계 | continue 경로 출력 가능 여부 |
|------|------------------------------|
| β-0 | 빈 문자열 (빌더만 있음) |
| β-1 | Catch-All + Default Display만 |
| β-2 | + RGB/부패/T1 보더 |
| β-3 | + AL 기반 Hide |
| β-4 | + 커런시/맵/디비카 → **aurora 기능 동등** |
| β-5 | + 빌드 오버레이 → aurora 대체 준비 완료 |

### 파일별 변경 (β-5b 완료 기준)

| 파일 | 상태 |
|------|------|
| `sections_continue.py` | 현행 (β-0~β-5 전 레이어) |
| `data/t1_craft_bases.json` | 현행 (β-2에서 소비) |
| `filter_generator.py` | 재작성 (continue-only, 59줄) |
| `sections_*.py` (구 4개) | 삭제 완료 |
| `pathcraft_sections.py` facade | 삭제 완료 |
| `filter_merge.py` | docstring만 레거시 표기, 코드 보존 (_analysis 의존) |

## 기존 시스템과의 관계

### Sanavi 베이스 필터

**결정: β = standalone 전면 필터.** Sanavi 오버레이 주입 방식 폐기.
- 이유: Continue 체인은 전체 필터를 한 덩어리로 관리해야 레이어 순서 보장
- 영향: `filter_merge`는 production에서 미사용 (β-5b 완료, _analysis 스크립트만 참조)

### 팔레트(`pathcraft_palette.py`)

**결정: 팔레트 유지, LayerStyle 팩토리로 연결.**
- `sections_continue.style_from_palette(category, tier, **overrides) -> LayerStyle` 헬퍼 제공
- Aurora 색 자산 보존. 새 레이어에서도 기존 카테고리×티어 매핑 재사용
- 팔레트 자체는 "색/상수 데이터"로 계속 존재, `sections_*.py` 섹션 모듈만 삭제됨

### `apply_strictness()` (주석 패턴 매칭)

**결정: β-3에서 제거.**
- 대체: `sections_continue.apply_layer_strictness(filter_text, level) -> str`
  - 레이어 태그 `[L{n}|{cat}]` 기반 블록 제거/Hide 전환
  - AL + StackSize 복합 조건도 Hide 블록으로 직접 생성 (Wreckers 방식)
- 이유: 현재 주석 패턴 매칭은 Aurora 전용 주석 컨벤션. β 주석 포맷과 다름

## 성능

POE 엔진은 각 아이템마다 매칭되는 Continue 블록을 전부 평가. Wreckers 2,460줄 기준 문제 없음. PathcraftAI β 예상 2,000~3,000줄 → OK.

## 리스크

- **디버그 어려움**: L0~L12 중 어느 레이어가 최종 스타일을 결정했는지 불명확 → 주석 태그로 완화
- **순서 변경 파급**: 레이어 순서 변경 시 전체 재검증 필요 → 순서 고정, 변경 = 메이저 버전
- **인게임 검증 초기화**: Aurora Glow 2026-04-12 피드백 반영 분량 재검증 필요 → 검증 체크리스트 사전 준비
