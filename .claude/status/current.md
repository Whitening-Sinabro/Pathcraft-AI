## 지금
- **POE2 D4 Canvas 통합 완료 (2026-04-22 S4)** — 데이터 레이어 + UI 통합 통합 커밋 대기.
  - `PassiveTreeCanvas` `game?: "poe1"|"poe2"` prop, `poe1DataUrl`/`poe2DataUrl` 분기, `normalizePoe2Tree` 적용
  - `TreeControls` classNames/ascendancies 를 props 로 받도록 리팩터 (POE1 7 / POE2 8)
  - `POE2_CLASS_START_IDS_BY_INDEX` + `POE2_ASCENDANCIES` (21 어센던시, Abyssal Lich / Disciple of Varashta 포함)
  - `PassiveTreeView` `useActiveGame` 연결, key 에 `${game}:${url}` 반영, POE1-only decodeTreeUrl
  - Portrait overlay POE1 전용 가드 (POE2 는 disc 만)
  - `localStorage` 키 game 별 분리 (`pathcraftai_passive_class_poe2` 등)
  - 앵커 계산 `classesStart` fallback 추가
  - 테스트 107/107 PASS (+11 POE2 상수 케이스), tsc clean
- **이전 세션 (S3)**
  - `83c805c` feat: POE2 D4 데이터 레이어 — tree.json 어댑터 + 테스트
- **직전 세션 (S2, 이미 push 완료)**
  - `3547553` 디자인 enforcement / `2dcbb80` POE2 D6 코치 + D3 / `c1c4ba0` S2 종료 기록

## 다음 세션 진입 절차
- **세션 계획**: D4 Canvas 통합 = 새 세션 / D5 = 또 다른 새 세션. 한 세션당 하나씩.
- 어느 세션이든 시작 시 `poe2_d6_dod.md` §4 해제 조건 3건 관찰 여부 먼저 체크 가능 (Tauri 실클릭 준비된 경우)

## 다음 할 것 (우선순위순)

0. [ ] **D4 Canvas Tauri 실렌더 검증** — POE2 모드 전환 시 tree_0_4.json 로딩 / 클래스 드롭다운 8개 / 어센던시 21개 / Abyssal Lich 선택 후 앵커 반영 확인. 사용자 실클릭.
1. [ ] **D6 해제 조건 수집** — Tauri 창 POE2 실사용. `_normalization_trace` / `_retry_info` 로그 수집 (백엔드는 이미 게재 중). 사용자 실클릭만 있으면 즉시 가능
2. [ ] **POE2 D5 필터** (별도 세션) — NeverSink POE2 공식 import + ItemClass 명칭 매핑 (Focus/Charm/Spear/Quarterstaff 신규). 2~3시간 scope
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
