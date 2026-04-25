## 지금
- **세션 종료 대기** — S10 종료 (`7761c39`) push 완료. 다음 세션 진입 시 "다음 할 것" 우선순위 0~5 중 택일.
- **이전 세션 (S10, 종료 commit `7761c39`, push 완료, 2026-04-25)**: GGPK 추출 트리거 → 두 선행 데이터 자동 부착 + valid_gems 회귀 가드 + catalog fingerprint hardening
  - GGPK 추출 (`cargo run --bin extract_data --release -- --game poe2 --json`) 23/24 성공. UniqueStashTypes 34 rows + AttributeRequirements 892 rows 신규.
  - `uniques_poe2.json`: 393 uniques 전부 `stash_type_label` 부착 (34 labels, unknown 0).
  - `base_items_poe2.json`: 791 entry 에 `req_str/req_dex/req_int` 부착 (`attribute_requirements_count: 839`).
  - `valid_gems_poe2`: Awakened/Vaal 부재 확정 + GemType=2 메타 젬 36건 active 포함 — 5 회귀 가드 (`test_valid_gems_poe2_categories.py`).
  - `_analysis/poe2_tables.json`: `_meta.ggpk` (size + mtime) + `_meta.generated_at_unix` fingerprint. catalog 생성기 hardening 은 .gitignore (로컬 전용).
  - 커밋: `39a89d4` (valid_gems 가드) → `7ae77d8` (AttributeRequirements 선행) → `35c9c8d` (data 자동 부착) → `7761c39` (catalog 재생성).
  - 검증: pytest 727 → **745** (+18) / cargo check / tsc 0 / vitest 110.
- **이전 세션 (S9, 종료 commit `6d041b9`)**: D7 Phase 2 + VerbalBuildInput POE2 전용 + uniques stash_type 선행 + audit-all POE2 fix (silent failure logger + '7 blocks' 이중 의미 해소). 검증 pytest 727 / tsc 0 / vitest 110.
- **이전 세션 (S8, push 완료)**
  - `58ae093` S8 반영 / `f49520c` feat: POE2 D7 Phase 1 — 4레이어 POE2 game 분기 / `24c2d31` push 반영 + D7 진입 / `3f36164` S7 종료
  - heist / special_uniques / id_mod POE2 skip + flasks_quality POE2 재설계 (Ultimate Life/Mana Flask Q11+/baseline + Charm Q18+, NeverSink [[0800]]/[[0900]])
  - `generate_beta_overlay` 호출부 4개 game 전파. 15 테스트 신규 (skip + POE1 regression + overlay E2E leak)
  - 검증: Python 697→712 (+15) / cargo 50 / vitest 110 / CLI smoke PASS. Plan: `poe2_d7_plan.md`
- **이전 세션 (S7, push 완료)**
  - `3f36164` chore: S7 종료 기록 / `9b2b475` feat: POE2 D5 2단계 — 필터 생성 game-aware ItemClass 분기
  - `sections_continue.py` POE1 Class 하드코딩 5개 → `game: str = "poe1"` 시그니처 + 헬퍼 10개
  - POE2 분기: Shields+Bucklers / Warstaves→Quarterstaves / 8종 drop (Claws·Daggers·O1/O2 Axes/Swords·Thrusting·Rune Daggers) / Hybrid Flasks drop / T1 보더 POE1 7→POE2 2 카테고리
  - 21 테스트. 검증: Python 697/697 cargo 42 vitest 110
- **이전 세션 (S6, push 완료)**
  - `1d6e9d6` push 반영 / `6e5f390` S6 종료 / `741e732` feat: POE2 D5 1단계 — ItemClass 매핑 + 드리프트 검증
  - NeverSink POE2 0.9.1 (0-SOFT / 3-STRICT) 40 Class 추출. `data/item_class_map_poe2.json` + `scripts/verify_item_class_map_poe2.py` + 11 테스트
- **이전 세션 (S5, push 완료)**
  - `176238b` push 반영 / `5e1d4f7` S5 종료 / `4ab9bb7` patch 3.28.0g / `cc4b201` D6 debug dump / `b336016` feat: POE2 D6 강화
  - campaign 구조 자동 파생 + normalizer POE2 분기 + PassivePriority guard. 검증: Python 665 vitest 110
- **이전 세션 (S4, push 완료)**
  - `38131ab` feat: POE2 D4 Canvas 통합 / `ec84680` chore: S4 종료 기록
- **직전 세션 (S3, push 완료)**
  - `83c805c` feat: POE2 D4 데이터 레이어 / `1c0133b` chore: S3 종료 기록

## 다음 세션 진입 절차
- 한 세션당 주제 하나. D7 Phase 1+2 종료, 다음은 D6 해제 조건 관찰 또는 D4 Canvas 실렌더 검증
- 세션 시작 시 `poe2_d6_dod.md` §4 해제 조건 3건 관찰 여부 먼저 체크 가능 (Tauri 실클릭 준비된 경우)

## 다음 할 것 (우선순위순)

0. [ ] **D4 Canvas Tauri 실렌더 검증** — POE2 모드 전환 시 tree_0_4.json 로딩 / 클래스 드롭다운 8개 / 어센던시 21개 / Abyssal Lich 선택 후 앵커 반영 확인. 사용자 실클릭.
1. [ ] **D6 해제 조건 수집** — Tauri 창 POE2 실사용. `_normalization_trace` / `_retry_info` 로그 수집 (백엔드는 이미 게재 중). 사용자 실클릭만 있으면 즉시 가능
   - S5 에서 `_debug/coach_last_{game}.json` 덤프 인프라 추가 — 관찰 후 `python/build_coach.py:1148-1158` 블록 제거 + `_debug/` 디렉토리 삭제
   - S5 추가: POE2 campaign 구조 자동 파생 + normalizer POE2 분기 완료 (L2 방어 공백 메움)
2. [ ] (후속, 선택) POE2 Mods schema Tags/SpawnWeight 필드 byte 재해석 — 3개 list 공백값 원인 파악. upstream schema.min.json 이슈라 로컬 override 로 보정 가능
3. [x] ~~**uniques stash_type 라벨 매핑**~~ — **완료 (2026-04-25 S10)**. 393 uniques 전부 `stash_type_label` 부착, 34 라벨, unknown 0
4. [x] ~~**base_items 필드 확장 (Str/Dex/Int)**~~ — **완료 (2026-04-25 S10)**. 791 entry 에 `req_str`/`req_dex`/`req_int` 부착. damage / armour 는 후속 (별도 GGPK 테이블 필요)
5. [ ] **기존 POE1 잔여** (이월):
   - L3 auto-retry 인게임 검증 (POE1)
   - DoD 수동 검증 (FilterPanel / 오버레이 / 히스토리)
   - Strict 모드 실측
   - 필터 생성 인게임 검증
   - Passive P2~P6 / Syndicate S4 / Phase 5b/5c
   - alias 맵 재감사 + POE2 alias 맵 설계

## 도메인 파일 포인터

- [POE2 통합 Diff (2026-04-22)](poe2_integration_diff.md) — 오늘 세션 세부. §0 scope-bounded claim 8항 / §6.6 spirit gems 의도 / §7 마이닝 실측 / §8 drift / §10 빌드 방향
- [POE2 D6 DoD](poe2_d6_dod.md) — 인프라 체크리스트 + 해제 조건 3건
- [코치 품질 Phase H 백로그](coach_quality_backlog.md) — H1~H6 완료, L3 인게임/alias 누적
- [POE2 D7 플랜+Phase2 회고](poe2_d7_plan.md) — Phase 1 (S8) + Phase 2 (S9) 완료 기록
- [POE2 통합 backlog](poe2_integration_backlog.md) — D0+D6(CONDITIONAL) / D1/D2/D3/D4/D5/D7/D8 대기
- [POE2 D4 패시브 트리 계획](passive_tree_poe2_plan.md) — 데이터 소스/schema 매핑/Canvas 통합 단계 (2026-04-22 S3)
- [디자인 Phase 0~5 플랜](design_phase_plan.md) — P5 미완. **Design enforcement 2026-04-22 설치 완료** (contract 4필드 기입)
- [Syndicate 전면 개편 S1~S4](syndicate_phase_plan.md) — S1~S3 완료
- [패시브 asset 플랜](passive_tree_assets_plan.md) — P1 완료, P2~P6 대기
- [Continue 아키텍처](continue_architecture.md)
- _analysis/ggpk_truth_reference.json — POE1 19 테이블 진실 anchor
- _analysis/poe2_tables.json — POE2 942 테이블 카탈로그
- data/game_data_poe2/ — GGPK 실측 19 datc64 + **19 JSON** (Words 3213 rows 추가, Mods 14841 rows 포함, Tags/SpawnWeight 3 list 만 schema 오인지로 공백)
- data/base_items_poe2.json — 283 무기 (15 classes) + 562 방어구 (6 classes) + 98 기타 (Amulets/Belts/Charms/Flasks/Jewels/Quivers/Rings)
- data/uniques_poe2.json — 393 visible uniques + 10 hidden (total 403, 리서치 일치)
- data/valid_gems_poe2.json — 1079 gems (active 477 / support 600 / spirit 2)
- data/schema/schema_poe2_override.json — drift 보정 정의 (SchemaStore auto-merge 적용 완료 2026-04-22 S2)
- data/id_mod_filtering_poe2.json — D7 Phase 2: NeverSink POE2 0.9.1 [[0400]] Recombinator Mods (11 classes / 소스 7 Show 블록 → 출력 11 블록 / 19 mods, SOFT/STRICT cross-verified)
- docs/league_refresh.md

## Class Start 노드 매핑 (POE1, data.json 수동)
- 0: Scion (58833) / 1: Marauder (47175) / 2: Ranger (50459)
- 3: Witch (54447) / 4: Duelist (50986) / 5: Templar (61525) / 6: Shadow (44683)

## POE2 클래스·어센던시 실측 (2026-04-22 GGPK)
- 출시 8: Warrior / Monk / Ranger / Mercenary / Sorceress / Witch / Huntress (0.2) / Druid (0.4)
- 미출시 4 (Characters 테이블 잔존): Marauder / Duelist / Shadow / Templar
- 정식 어센 21: Warrior 3 / Ranger 2 / Huntress 2 / Witch 4 (**Abyssal Lich 확정**) / Sorceress 3 (**Disciple of Varashta 확정**) / Mercenary 3 / Druid 2 / Monk 2

## 잔존 이슈 (허용/추후 처리)

- **D6 해제 조건 3건 중 2건 이상 관찰 대기** (우선순위 0, 다음 세션)
- **Mods Tags/SpawnWeight_Tags/SpawnWeight_Values 3 list 공백** — 주 데이터는 정상. schema field 위치/타입 재매핑 필요 (upstream schema.min.json POE2 Mods 엔트리 이슈)
- **GameData POE2 QuestRewards 구조 차이** — `Characters` / `Reward` 필드 호환성 미검증
- **GameData POE2 SkillGems `is_support` 판별** — POE2 는 `IsSupport` 필드 없음, `GemType` 으로 판별 추후
- ~~**valid_gems 다른 카테고리 누락 가능성**~~ — POE2 부분 해소 (2026-04-25): GGPK 2026-04-22 0.4.0d 기준 Awakened 0건 / Vaal 0건 확정. `python/tests/test_valid_gems_poe2_categories.py` 5 회귀 가드 (sentinel 깨질 시 즉시 탐지). POE1 transfigured 사례는 별도 추적
- **L3 인게임 미검증** (POE1) — 재시도 교정 프롬프트 실 효과 측정 필요
- **Phase E subagent 제기 미패치 5건** (이전 세션 이월) — Claim gate / hook stdin 스키마 실측 대기
- **Tier 2 C / SyndicateBoard ss22 / Cmd+K / PassiveTreeCanvas 623줄 / Syndicate OCR / Coach zombie / Model toggle test** — 전부 이전 이월

## UX 결정 기록 (누적)
- 우클릭 dealloc 분리 → 되돌림 (왼클릭 토글 유지)
- 수동 URL import UI 스킵 (자동 디코드 대체)
- AI 이모지 제거, UI 이모지 → SVG 아이콘
- 전면 리디자인 = 다크 단일 + POE Rarity + Linear 레이아웃 + 2-창 오버레이
- 기본 리그 모드 = SC
- **빌드 분석 = 진입점** 원칙
- 패시브 class start = anchor only
- **코치 모델 기본 Haiku** — 3버튼
- **게임 토글 TopBar** — POE1 기본, POE2는 경고 배너 + VerbalBuildInput 폼
- **빌드 히스토리 (pobb 스타일)** — localStorage 최근 20개
- **오버레이 레벨링 = 탭 네비 + 활성 phase bullet**
- **FilterPanel 3모드 유지**
- **코치 정식화 = 코드 레이어 hard constraint** — normalizer 가 주 제약 (Phase H)
- **4-Layer hallucination 방어** — L1 prompt + L2 strict + L3 retry + L4 풀스크린 블록. **POE2 이식 완료 (2026-04-22)**
- **자가-PASS 방어 Tier 2** — Claim-gate + Phase E audit-all subagent + Fast/Strict 모드 분리 (2026-04-21)
- **POE2 D6 인프라** — SYSTEM_PROMPT_POE2 + valid_gems_poe2 + normalizer/validator POE2 분기 + VerbalBuildInput + activeGame invoke 전파 + GameData POE2 분기 (2026-04-22, CONDITIONAL DONE)
- **schema drift override auto-merge** — `schema_poe2_override.json` 을 `SchemaStore::load_for_game(Poe2)` 가 자동 로드 + append. Mods/SkillGems 끝 컬럼 보정 (2026-04-22 S2)
- **extract_data `--reuse-datc64`** — GGPK 재파싱 없이 schema 적용 + JSON 만 재생성. drift/schema 수정 사이클 단축 (2026-04-22 S2)
- **dat64 List/String 방어적 reject** — count/offset garbage (MAX_LIST_ITEMS=10k, MAX_STR_U16=4096, 물리 용량 초과) 시 빈 값 즉시 반환. 45 GB OOM 차단 (2026-04-22 S2)
- **POE2 D3 base_items / uniques** — BaseItemTypes 에서 무기/방어구 분류, UniqueStashLayout × Words JOIN. `scripts/build_base_items_poe2.py` / `build_uniques_poe2.py` (2026-04-22 S2)
- **POE2 구두 빌드 입력 경로** — POB 없이 VerbalBuildInput 폼 → analyzeVerbalBuild → coach_build 직행. D6 통합 UI (2026-04-22)
- **Design enforcement** 2026-04-22 설치 (contract 4필드: Primary Action / mobalytics ref / #0A84FF / Pretendard)
- **POE2 D7 필터 레이어 완료** — heist/special_uniques POE2 skip + flasks_quality POE2 재설계 (Ultimate Flask/Charm) + id_mod_filtering POE2 Recombinator [[0400]] 실구현 (11 classes, 소스 7 Show 블록 → 출력 11 블록). Phase 1 (S8) + Phase 2 (S9, 2026-04-24)
- **VerbalBuildInput POE2 전용 확정** (2026-04-25 S9) — `game` prop 제거, POE2 상수 고정. POE1 은 `PobInputSection` 유지. PoB2 포맷 확정(D1) 전 POE2 임시 우회로 스코프 JSDoc 명시
