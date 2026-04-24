## 지금
- **POE2 D5 2단계 (2026-04-23 S7)**
  - `python/sections_continue.py` — POE1 하드코딩 Class 상수 5개 제거 + game-aware 헬퍼 신설
    - 모듈 레벨 헬퍼: `_load_item_class_map_poe2` / `_map_poe1_classes` / `_join_classes_quoted` / 5개 `_*_for(game)` 문자열 빌더 + 무기·방어구 헬퍼 + T1 보더 그룹 선택기
    - 시그니처 `game: str = "poe1"` 추가: `generate_beta_overlay` / `layer_progressive_hide` / `layer_endgame_rare` / `layer_endgame_rare_hide` / `layer_re_show` / `_unconditional_re_show_blocks` / `_leveling_help_blocks`
    - POE2 분기: Shields → Shields+Bucklers / Warstaves → Quarterstaves / Claws·Daggers·O1 Axes·O1 Swords·O2 Axes·O2 Swords·Thrusting·Rune Daggers drop / Hybrid Flasks drop / T1 보더 POE1 7 카테고리 → POE2 2 카테고리 (Trinket/Heist/Flask/Tincture/Cluster Jewel 은 POE1 전용이라 skip) / 매핑 결과 빈 리스트인 T1 melee 블록 skip
  - `python/filter_generator.py` — `args.game` 을 `generate_beta_overlay(game=)` 로 전달, D5 미완 경고 로그 제거
  - Rust `generate_filter_multi` — D0/D6 에서 이미 `game: Option<Game>` + `--game` CLI 전달 구현됨. 검증만
  - `python/tests/test_filter_poe2_class_mapping.py`: 21 테스트 (매핑 헬퍼 8 + 문자열 빌더 6 + 오버레이 E2E 7) — Shields/Bucklers 공존·Warstaves→Quarterstaves·POE1 기본값 regression·빈 Class 조건 부재·레이어별 POE1-only 누수
  - 검증: Python 697/697 (+21), cargo 42, vitest 110, CLI smoke PASS
  - **후속 D7 스코프로 이월**: `layer_id_mod_filtering` / `layer_heist` / `layer_flasks_quality` / `layer_special_uniques` 등 POE1 native 데이터 의존 레이어의 Class 조건 — POE2 native 데이터(top-mod / 리그 아이템) 수집 필요. 실런타임 파싱 실패는 없으나 dead block 남음
- **이전 세션 (S6, push 완료)**
  - `1d6e9d6` chore: current.md push 상태 반영 / `6e5f390` chore: 세션 종료 기록 / `741e732` feat: POE2 D5 1단계 — ItemClass 매핑 + 드리프트 검증
  - NeverSink POE2 0.9.1 (0-SOFT / 3-STRICT) 에서 40 Class 추출 (두 파일 교차 일치)
  - `data/item_class_map_poe2.json` + `scripts/verify_item_class_map_poe2.py` + `python/tests/test_item_class_map_poe2.py` (11)
- **이전 세션 (S5, push 완료)**
  - `b336016` POE2 D6 강화 / `cc4b201` D6 debug dump / `4ab9bb7` patch 3.28.0g / `5e1d4f7` S5 종료 기록 / `176238b` push 상태 반영
  - `b336016` feat: POE2 D6 강화 — campaign 구조 자동 파생 + normalizer 분기 + PassivePriority guard
  - `cc4b201` chore: D6 관찰용 debug dump 인프라 (임시)
  - `4ab9bb7` chore: POE1 patch notes 3.28.0g 수집
  - A. campaign 구조: `extract_data.rs` WorldAreas/Quest 추출 + `scripts/build_poe2_campaign_structure.py` + `data/campaign_structure_poe2.json` (6 phase, Act 1-4 + Interlude transient + Atlas) + `build_coach.py` `@@LEVELING_GUIDE_SCHEMA@@` 치환 + `LevelingGuide.tsx` POE2 phase 자동 매핑
  - B. normalizer POE2: `_normalize_coach_output_poe2` — skill_setup.main_skill / support_gems, `→/->/|/,/;` split + valid_gems_poe2 검증 + dedupe
  - C. PassivePriority guard: 빈 priorities 시 null 반환 + `setdefault("passive_priority", [])`
  - D. D6 debug dump: `_debug/coach_last_{game}.json` 덤프 (관찰용 임시)
  - E. POE1 patch 3.28.0g 수집 (orthogonal)
  - 검증: Python 665/665 (+14), vitest 110/110 (+3), tsc clean
- **이전 세션 (S4, push 완료)**
  - `38131ab` feat: POE2 D4 Canvas 통합 / `ec84680` chore: S4 종료 기록
- **직전 세션 (S3, push 완료)**
  - `83c805c` feat: POE2 D4 데이터 레이어 / `1c0133b` chore: S3 종료 기록

## 다음 세션 진입 절차
- **세션 계획**: D4 Canvas 통합 = 이번 세션(S4) / D5 = 또 다른 새 세션. 한 세션당 하나씩.
- 어느 세션이든 시작 시 `poe2_d6_dod.md` §4 해제 조건 3건 관찰 여부 먼저 체크 가능 (Tauri 실클릭 준비된 경우)

## 다음 할 것 (우선순위순)

0. [ ] **D4 Canvas Tauri 실렌더 검증** — POE2 모드 전환 시 tree_0_4.json 로딩 / 클래스 드롭다운 8개 / 어센던시 21개 / Abyssal Lich 선택 후 앵커 반영 확인. 사용자 실클릭.
1. [ ] **D6 해제 조건 수집** — Tauri 창 POE2 실사용. `_normalization_trace` / `_retry_info` 로그 수집 (백엔드는 이미 게재 중). 사용자 실클릭만 있으면 즉시 가능
   - S5 에서 `_debug/coach_last_{game}.json` 덤프 인프라 추가 — 관찰 후 `python/build_coach.py:1148-1158` 블록 제거 + `_debug/` 디렉토리 삭제
   - S5 추가: POE2 campaign 구조 자동 파생 + normalizer POE2 분기 완료 (L2 방어 공백 메움)
2. [ ] **POE2 D7** — POE1 native 데이터 의존 4레이어 game 분기 (D5 2단계 후속)
   - `layer_id_mod_filtering`: POE2 Mods (14841 rows) top-mod 추출 후 대응
   - `layer_heist`: POE2 미지원 → game 분기로 호출 skip
   - `layer_flasks_quality`: POE2 Charm 시스템 대응 재설계
   - `layer_special_uniques`: `uniques_poe2.json` 기반 카테고리 재분류
3. [ ] (후속, 선택) POE2 Mods schema Tags/SpawnWeight 필드 byte 재해석 — 3개 list 공백값 원인 파악. upstream schema.min.json 이슈라 로컬 override 로 보정 가능
4. [ ] (후속, 선택) uniques stash_type 매핑 — UniqueStashTypes 테이블 extract → stash type id → 유형 이름 (Weapons/Armour/etc)
5. [ ] (후속, 선택) base_items 필드 확장 — requirements (Str/Dex/Int) / damage / armour 추가
6. [ ] **VerbalBuildInput POE1 fallback 설계 명시** — 컴포넌트가 game prop 받지만 POE1 렌더 경로 없음 (audit medium 이슈)
7. [ ] **기존 POE1 잔여** (이월):
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
- **VerbalBuildInput POE1 fallback** — 컴포넌트가 game prop 받지만 POE1 렌더 경로 없음 (audit medium)
- **valid_gems 다른 카테고리 누락 가능성** — POE1 transfigured 사례, POE2 도 awakened/vaal alt 조사 필요
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
