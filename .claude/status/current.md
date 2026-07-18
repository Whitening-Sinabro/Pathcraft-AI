## 2026-07-18 Handoff — CWS 가이드 재설계 완료 + 별건 fix (미커밋)

**이번 세션 = POE1 CWS 가이드 구조 재설계 (완료, master 병합).**
- 크리에이터 빌드가이드 = **단일 템플릿** `poe1_external_guide_source` (JSON). 하드코딩 dict 소멸.
  템플릿 `data/guide_sources/_template.poe1_external_guide_source.json`, 인스턴스 CWS + zeeboub.
  검증기+투영기 `python/cws_guide_loader.py`. 다음 가이드는 JSON만 추가. 상세 → 메모리 [[project-build-guide-template]].
- master 커밋 `c1c7072`~`41911c7` (9커밋) + `84a017a` (Pohx RF Chieftain PoB `pobb.in/Sit6hlQU1uuZ`
  레벨링 링크 추가, 87+ 스왑 게이트 강화). 전체 스위트 1092 passed / 0 failed.
- 설계·플랜 문서: `~/.claude/projects/D--Pathcraft-AI/2026-07-17-cws-guide-structure-redesign-{design,plan}.md`.

**[2026-07-18 S2] build-corpus WIP 전체 커밋 완료 (5 레이어 커밋, 로컬 only, 미푸시).**
`06207d4` chore(gitignore) → `953d918` data(코퍼스 41MB) → `58c46bd` rust(+993) →
`14e952e` python(46 신규모듈 + 2 fix) → `7ccac32` ui(+3026). 별건 2 fix 포함:
- PoB probe 패치 누수 fix (커밋 `14e952e`). 상세 → 메모리 [[project-pob-probe-patch-leak]].
- 잠복 스냅샷 단언 fix 4파일 (커밋 `14e952e`). 상세 → [[project-snapshot-assert-trap]].
제외(gitignore): `data/ggpk_derived/`(69MB 재생성) · `tmp/` · `data/.claude/` · 검증 png.
스위트 1091 passed / 1 fail(env: `data/game_data/` gitignore 부재, 회귀 아님).

**아래 2026-07-17 핸드오프 숫자 정정** (그대로 두면 스냅샷 단언 함정 재발):
- expanded queue `161→163`, 3.28 `21→23` (누적, 정상).
- 골렘 `3.28_poison_carrion_golem_witch` = 3.28 direct PoB 3개 확보로 `ready_for_pob_parse` 승격됨
  (line 14 의 `needs_direct_pob_link`/3.26-only 기술은 낡음). 3.26 PoB 는 이제 패치 가드로 3.28 후보 승격 불가.

---

## 2026-07-17 Handoff — POE1 Build Corpus Collection
- 현재 큰 목표는 `3.22`부터 `3.29`까지 실제 빌드를 넓게 수집해서 Pathcraft AI 전용 build corpus / candidate queue / source evidence DB로 정리하는 것.
- 다음 세션은 특정 빌드 하나를 고정하지 말고 `래딧 / 커뮤니티 / 빌드 사이트 / 유튜브 / PoB 링크 / 패치노트 / poe.ninja류`를 같이 보며 부족한 빌드군을 계속 채우는 수집 세션으로 시작한다.
- 기존 데이터 축: `data/build_corpus_collection_targets_v1.json`, `data/build_corpus_expanded_collection_queue_v1.json`, `data/build_variant_collection_queue_v1.json`, `data/build_variant_real_cases_v1.json`, `data/build_corpus_manual_pob_sources_v1.json`, `data/guide_sources/`.
- 목표 구조는 단순 인기 빌드 5개가 아니라 `archetype / sub_archetype / variant / phase_state / source_evidence / patch_delta / item_mod_pressure / passive_tree_shape / farming_fit`까지 파생 DB로 연결하는 것.
- 이번 이어가기에서 수동 PoB source를 `6 -> 28`건으로 늘렸고, promoted artifact는 `6 -> 50`, promoted state snapshot은 `83 -> 403`으로 갱신했다. 세부 기록은 `Docs/2026-07-08_BUILD_CORPUS_PROGRESS_REPORT.md`의 `2026-07-17 Manual PoB Source Expansion` 섹션.
- poe.ninja 빌드 탭은 같은 archetype 안의 사람별 커스터마이징을 보는 `variant_evidence_candidate` 소스로 분리했다. 계약 파일은 `data/poe_ninja_build_variant_sampling_plan_v1.json`, 레벨링 caveat는 `Docs/POE1_LEVELING_CONFIRMATION_PACK.md`에 반영했다.
- poe.ninja evidence 큐는 `data/poe_ninja_build_variant_evidence_queue_v1.json`로 추가했고, 레벨링 route family 계획은 `data/poe1_leveling_archetype_route_plan_v1.json`로 추가했다. caster/minion/totem은 3.27~3.28 stage PoB 근거가 강하고, ranger hit bow/melee 최신화는 추가 stage PoB가 필요하다. mine lane은 Hexblast가 아니라 `Exsanguinate/Reap Miner Trickster` 기준이며, Cptn Garbage / Maxroll Exsanguinate Miner Trickster를 1순위 source hunt로 둔다. 토리센세는 mine 보조 확인과 소환수/Spectre creator source로 별도 추적한다.
- creator-first 수집 레지스트리는 `data/poe1_creator_source_registry_v1.json`로 추가했다. CWS=`emiracle`, mine=`Cptn Garbage/Jorgen/Conner Converse/FearlessDumb0`, experimental=`CaptainLance9`, minion=`GhazzyTV/토리센세/Dconnic`, HC=`Zizaran`, one-build specialists=`POEGuy/ZeeBoub/Sanavixx`. `Goblin`은 검색상 Goblin-Inc가 유력하지만 POE1 source로 쓰기 전 확인 필요.
- 최신 promotion 상태: manual PoB source `33`, direct PoB candidate `68`, promoted artifact `57`, state snapshot `501`. `3.28` mine transition slot은 `Exsanguinate Reap Mines Trickster`로 교체했고, Exsang mine 7개 PoB + 토리센세 Spectre 1개 PoB가 parser 검증을 통과했다.
- `poe1_representative_build_profiles.latest.json`에 `3.28_exsanguinate_reap_mines_trickster` supplemental profile을 추가했다. 3.28 Shadow Trickster + `Exsanguinate Mine` + confirmed leveling required smoke에서 `Plan A / plan_a_exact`로 선택된다. 추천 API는 이제 `selected_profile` / 후보별 `profile_summary`로 leveling route, passive direction, source evidence를 UI에 전달한다.
- `poe_ninja_build_variant_evidence_queue_v1.json`에는 creator source track 10개를 추가했다: CWS/emiracle, mine/Jorgen+Conner+Cptn+Fearless, experimental/CaptainLance9, minion/Ghazzy+토리센세+Dconnic, current Tori Poison Carrion Golem, HC/Zizaran, variety/Goblin, one-build specialists.
- 2026-07-17 correction: 수집 queue는 패치당 20개 상한이 아니라 최소 baseline이다. 새 후보는 기존 후보를 빼지 않고 누적한다. `3.28_poison_carrion_golem_witch`를 추가했고 `3.28_volatile_dead_spellslinger_necromancer`는 유지했다. expanded queue는 `161`, 3.28은 `21`개.
- 토리센세 current-season minion lane은 사용자 제보 기준 `Poison Carrion Golem`로 분리했다. 과거 공개 reference는 3.26 영상/PoB `https://pobb.in/Gji0uiu1Aoog`; 이번 시즌 direct PoB는 아직 `needs_direct_pob_link`.
- creator registry는 `34`명으로 확장했다. 추가 discovery set: Kankar, anime princess, LLYD, Palsteron, Fubgun, Ruetoo, Crouching_Tuna, Big Ducks, subtractem, Pohx, Jungroan, Goratha, Tatiantel2, Ventrua, Ben_, Steelmage, Carn, ds lily, Mathil, Travic.
- 현재 작업 범위에서 POE2는 일단 보류한다. POE1 build corpus 추천 UI 연결, 전략/레벨링 상태 표시 수정, POE1 passive tree 개선 1차는 완료했다.
- 방금 이야기한 Spectre 약화와 Dominating Blow 가능성은 전체 수집 작업 안의 `3.29 minion lane` 부분 발견일 뿐이다. `Dominating Blow Guardian`은 후보로 올리되, 다음 세션의 주 작업은 전체 빌드 콜렉트와 근거 정규화다.
- 세부 기록: `Docs/2026-07-08_BUILD_CORPUS_PROGRESS_REPORT.md`의 `2026-07-17 Handoff: Continue Corpus Collection` 섹션, `Docs/2026-07-16_SCION_RELIQUARIAN_3_29_RESEARCH.md`의 `2026-07-17 Subfinding: 3.29 Minion Lane` 섹션.

## 지금
- **[2026-07-18 S2] build-corpus WIP 전체를 5 레이어 커밋으로 확정** (상단 핸드오프 참조). 로컬 only, 미푸시. 유실 리스크 해소.
- 다음 세션 = 코퍼스 추가 수집 재개 (아래 "다음 할 것" 3) 또는 커밋된 backend/frontend 컴파일 헬스 확인.
- **이전 세션 (S12, 2026-04-26)**: POE2 패시브 트리 거미줄 부분 해소 + 갭 매핑 (8-에이전트 분석)
  - **근본 원인 1 (data)**: PoB-PoE2 `tree_0_4.json` 의 `groups` 가 sparse list (1497 슬롯 중 16 null). `normalizePoe2Tree` 가 null 슬롯도 그대로 인덱싱 → `TypeError: Cannot read properties of null (reading 'x')` 로 트리 로드 실패
  - **근본 원인 2 (render)**: POE2 `connection.orbit` 메타데이터 (외부 호 반지름 인덱스 + 방향 부호) 가 normalizer 단계에서 손실. `passiveTreeRender` 가 PoB 의 3-branch BuildConnector (외부 호 / 내부 호 / 직선) 분기 없이 직선만 그림 + POE1 하드코딩 SKILLS_PER_ORBIT 사용 → cross-group 거미줄 sweep 발생
  - **수정 1 (data)**: `passiveTree.ts` null 가드 + `TreeNode.outConn?: Array<{id:string;orbit:number}>` 신설. `connections` 메타 보존. 회귀 가드 3건 추가 (sparse null skip / orbit metadata / out·outConn index alignment) → 22→25 테스트
  - **수정 2 (render)**: `passiveTreeRender.ts` 에서 `SKILLS_PER_ORBIT` 제거, RenderState 에 `skillsPerOrbit: number[]` / `edgeMaxDist` 동적 주입. PoB pre-filter 이식 (classStart skip + ascendancyName 불일치 skip), 외부 호 분기 (perp 부호 = `connOrbit > 0 ? 1 : -1`), straight cutoff 후 viewport culling (Cohen-Sutherland). POE2=5000 / POE1=1500
  - **CSS 토큰화**: `PassiveTreeCanvas.tsx` 8 hex literal → 기존 var + `--passive-notable: #E8C068` / `--passive-notable-border: #4A3F2A` 2개 신규 토큰 (POE notable gold/brown). design-exception #1 등록 (cap 2 의 1)
  - **검증 한계**: 거미줄 부분 해소만. sweep 일부 잔존 — sprite atlas 도입 또는 viewer 재설계 필요. **D4 DoD #11 인게임 검증 미완** (사용자 영역, deferred)
  - **갭 매핑**: 8-에이전트 병렬 (PoB / mobalytics / maxroll / community / POE1 own / POE2 own / 한국어 / 차별화) → `passive_tree_gap_audit.md` 신규 (Tier 0/1/2 + POE1+POE2 양쪽 매핑). 핵심 발견 = 커뮤니티 뷰어 시각 차별화 zero / 한국어 로컬라이제이션 갭 / heatmap×planner 갭
  - **커밋**: `a847ef0` data fix → `ddea176` WIP render + viewport culling → `8c85472` docs (8-agent gap audit). 워킹 트리 클린
  - **검증**: vitest 96 → **99** (+3 sparse null/orbit/index alignment) / pytest 745 / cargo unaffected / tsc 0
- **이전 세션 (S11, 2026-04-26)**: dat64 schema parser fix — POE2 Mods Tags/SpawnWeight 3 list 공백 해소 + List element-type 분기. 커밋 `ed23e75` / `9792033` / `0121d9c`. Rust 45 / pytest 745 / vitest 110 / tsc 0
- **이전 세션 (S3~S10)** — git log 참조. 주제별 도메인 파일 포인터로 이관

## 다음 세션 진입 절차
- 한 세션당 주제 하나. 현재는 POE2 보류, POE1 우선.
- build corpus / recommendation result UI 연결은 완료했다.
- 전략/레벨링 상태 표시는 corpus evidence 기준으로 수정 완료했다.
- passive tree는 POE1만 대상으로 1차 개선 완료했다. POE2 D4/D6 후속은 사용자가 다시 요청할 때까지 건드리지 않는다.

## 다음 할 것 (우선순위순)

0. [x] **POE1 recommendation UI 연결** — `poe1_representative_build_profiles.latest.json` / `recommend_from_corpus` 결과를 UI에 노출. Plan A/B/C/D, confidence, leveling status, source evidence 표시. 검증: `pytest test_recommend_from_corpus`, 코퍼스 추천 회귀 68개, `pnpm test`, `pnpm build`.
1. [x] **POE1 전략/레벨링 표시 수정** — poe.ninja=endgame variant, creator/stage PoB=leveling evidence 구분을 UI/문구에 반영. 레벨링/스킬/파밍/패시브 우선순위 섹션이 `selected_profile`을 받아 corpus route, transition point, passive direction, suitability/evidence split을 표시한다.
2. [x] **POE1 passive tree 개선** — POE1 tree 표시/전환/마일스톤 UX부터 정리. 트리 탭은 current PoB tree URL, representative passive plan, class/ascendancy fallback을 함께 사용한다. POE2 passive tree 후속은 보류.
3. [ ] **POE1 corpus 추가 수집** — creator registry 34명 기준으로 current-season PoB를 계속 누적. 기존 후보는 빼지 않는다.
4. [ ] **기존 POE1 잔여** (이월):
   - L3 auto-retry 인게임 검증 (POE1)
   - DoD 수동 검증 (FilterPanel / 오버레이 / 히스토리)
   - Strict 모드 실측
   - 필터 생성 인게임 검증
   - Passive P2~P6 / Syndicate S4 / Phase 5b/5c
   - alias 맵 재감사

## 도메인 파일 포인터

- [패시브 트리 시각/UX 갭 매핑](passive_tree_gap_audit.md) — 2026-04-26 S12: 8-에이전트 병렬 분석. Tier 0/1/2 + POE1+POE2 양쪽 매핑
- [POE2 통합 Diff (2026-04-22)](poe2_integration_diff.md) — §0 scope-bounded claim / §6.6 spirit gems / §7 마이닝 실측 / §8 drift / §10 빌드 방향
- [POE2 D6 DoD](poe2_d6_dod.md) — 인프라 체크리스트 + 해제 조건 3건
- [코치 품질 Phase H 백로그](coach_quality_backlog.md) — H1~H6 완료, L3 인게임/alias 누적
- [POE2 D7 플랜+Phase2 회고](poe2_d7_plan.md) — Phase 1 (S8) + Phase 2 (S9) 완료 기록
- [POE2 통합 backlog](poe2_integration_backlog.md) — D0+D6(CONDITIONAL) / D1/D2/D3/D4/D5/D7/D8 대기
- [POE2 D4 패시브 트리 계획](passive_tree_poe2_plan.md) — 데이터 소스/schema 매핑/Canvas 통합 (2026-04-22 S3)
- [디자인 Phase 0~5 플랜](design_phase_plan.md) — P5 미완. **Design enforcement 2026-04-22 설치 완료**
- [Syndicate 전면 개편 S1~S4](syndicate_phase_plan.md) — S1~S3 완료
- [패시브 asset 플랜](passive_tree_assets_plan.md) — P1 완료, P2~P6 대기
- [Continue 아키텍처](continue_architecture.md)
- [Design Exceptions](design-exceptions.md) — Exception #1 (--passive-notable*) 등록 (cap 2 의 1)
- _analysis/ggpk_truth_reference.json — POE1 19 테이블 진실 anchor
- _analysis/poe2_tables.json — POE2 942 테이블 카탈로그
- data/game_data_poe2/ — GGPK 실측 19 datc64 + **19 JSON** (S11 dat64 fix 후 Tags/SpawnWeight 정상 채워짐)
- data/base_items_poe2.json — 283 무기 + 562 방어구 + 98 기타 + 791 entry attribute requirements
- data/uniques_poe2.json — 393 visible uniques (stash_type_label 100%)
- data/valid_gems_poe2.json — 1079 gems (active 477 / support 600 / spirit 2)
- data/schema/schema_poe2_override.json — drift 보정 (SchemaStore auto-merge)
- data/id_mod_filtering_poe2.json — D7 Phase 2 Recombinator [[0400]]
- docs/league_refresh.md

## Class Start 노드 매핑 (POE1, data.json 수동)
- 0: Scion (58833) / 1: Marauder (47175) / 2: Ranger (50459)
- 3: Witch (54447) / 4: Duelist (50986) / 5: Templar (61525) / 6: Shadow (44683)

## POE2 클래스·어센던시 실측 (2026-04-22 GGPK)
- 출시 8: Warrior / Monk / Ranger / Mercenary / Sorceress / Witch / Huntress (0.2) / Druid (0.4)
- 미출시 4 (Characters 테이블 잔존): Marauder / Duelist / Shadow / Templar
- 정식 어센 21: Warrior 3 / Ranger 2 / Huntress 2 / Witch 4 (**Abyssal Lich 확정**) / Sorceress 3 (**Disciple of Varashta 확정**) / Mercenary 3 / Druid 2 / Monk 2

## 잔존 이슈 (허용/추후 처리)

- **D4 거미줄 sweep 부분 해소만** (우선순위 0) — PoB pre-filter + viewport culling 적용 후에도 일부 잔존. sprite atlas 또는 viewer 재설계 필요
- **D4 DoD #11 인게임 검증 미완** (우선순위 1) — 사용자 영역
- **D6 해제 조건 3건 중 2건 이상 관찰 대기**
- **GameData POE2 QuestRewards 구조 차이** — `Characters` / `Reward` 필드 호환성 미검증
- **GameData POE2 SkillGems `is_support` 판별** — POE2 는 `IsSupport` 필드 없음, `GemType` 으로 판별 추후
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
- **schema drift override auto-merge** — `SchemaStore::load_for_game(Poe2)` 자동 로드 + append (2026-04-22 S2)
- **extract_data `--reuse-datc64`** — GGPK 재파싱 없이 schema 적용 (2026-04-22 S2)
- **dat64 List/String 방어적 reject** — 45 GB OOM 차단 (2026-04-22 S2)
- **dat64 interval 8B + List element-type 분기** (2026-04-26 S11) — `interval: true` = 8B (i32 min/max), `array` = element type 별 16/8/4 B. POE2 Mods 6 list 공백 해소
- **POE2 D3 base_items / uniques** — BaseItemTypes + UniqueStashLayout × Words JOIN (2026-04-22 S2)
- **POE2 구두 빌드 입력 경로** — VerbalBuildInput → analyzeVerbalBuild → coach_build 직행 (2026-04-22)
- **Design enforcement** 2026-04-22 설치 (contract 4필드: Primary Action / mobalytics ref / #0A84FF / Pretendard)
- **POE2 D7 필터 레이어 완료** — heist/special_uniques POE2 skip + flasks_quality 재설계 + id_mod_filtering Recombinator [[0400]] 실구현 (S8/S9, 2026-04-24)
- **VerbalBuildInput POE2 전용 확정** (2026-04-25 S9) — `game` prop 제거, POE2 상수 고정. POE1 은 `PobInputSection` 유지
- **POE2 D4 viewer PoB BuildConnector 부분 이식** (2026-04-26 S12) — null 가드 + outConn 메타 보존 + PoB pre-filter (classStart/ascendancy) + 외부 호 분기 + viewport culling. 거미줄 부분 해소만, sprite atlas 후속 필요
- **--passive-notable* 도메인 토큰** (2026-04-26 S12, design-exception #1) — POE notable gold/brown 시각 언어 보존. accent 1개로 표현 불가
