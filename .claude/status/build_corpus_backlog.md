# Build Corpus — Rule-Hardening Backlog

> classify_split(build_variant_model_v2) 룰 리파인 후보. 데이터 수정 아님 — 룰 개선 항목.

## 2026-07-17 Collection Handoff

**다음 세션의 중심 목표:** 특정 추천 빌드 하나가 아니라 `3.22`부터 `3.29`까지 실제 빌드 사례를 계속 수집하고, Pathcraft AI가 쓸 수 있는 파생 DB로 정리한다.

**수집 범위:**
- 래딧, 공식 포럼, 커뮤니티 글, 빌드 사이트, 유튜브, PoB/pobb 링크, 패치노트, poe.ninja류 랭킹/프로필 근거를 함께 본다.
- 각 패치별로 `stable_shell`, `transition_case`, `failure_edge_case`, `watchlist`를 나눠 채운다.
- 단순 인기 순위가 아니라 실제 플레이 가능한 근거, POB 유효성, 패치 변경 영향, 아이템 요구치, 패시브 트리 이동, 파밍 적합도를 같이 남긴다.

**이미 이어받아야 하는 데이터 축:**
- `data/build_corpus_collection_targets_v1.json`
- `data/build_corpus_expanded_collection_queue_v1.json`
- `data/build_variant_collection_queue_v1.json`
- `data/build_variant_real_cases_v1.json`
- `data/build_corpus_manual_pob_sources_v1.json`
- `data/guide_sources/`
- `data/patch_notes/`
- `data/ggpk_derived/`

**분류/파생 DB 렌즈:**
- archetype / sub_archetype / variant / phase_state
- source_evidence / source_family / confidence
- patch_delta impact
- item_mod_pressure and required unique gates
- passive_tree_shape and class/ascendancy routing
- leveling -> transition -> endgame path
- atlas/farming fit: early mapping, mid mapping, T16 comfort, Guardian maps, Delve/Fossil, bossing

**이번 대화에서 생긴 부분 발견:**
- 3.29 Spectre 약화와 Non-Spectre Minion 상향은 전체 빌드 수집 안의 `minion lane`으로 기록한다.
- `Dominating Blow Guardian`은 3.29 후보로 올리되, 전체 작업을 이 빌드 하나로 좁히면 안 된다.
- `Dominating Blow Scion/Reliquarian`은 실험 후보이며, 먼저 자료 수집과 비교군 검증이 필요하다.

## R1. transient-vs-durable state qualifier (분류기 과분할 방지)

**문제:** 현 field-diff 룰은 두 state의 `damage_engine / defense_engine / core_unique_gate / tree_shape_class / play_pattern` 차이를 세어 `sub_archetype_split`을 판정한다. 그런데 **캠페인 레벨링 → 엔드게임** 전환은 거의 모든 빌드에서 life→CI + 레벨링 스킬→엔드게임 스킬 스왑을 동반 → 이 정상적 gearing arc가 전부 `sub_archetype_split`로 잡힌다. 결과적으로 **레벨링 단계가 체계적으로 과분할**되어 라벨 신호가 희석된다.

**영향받는 케이스(선례):**
- `3.24_penance_brand_inquisitor_v1` — campaign_brand_leveling → endgame = sub_archetype_split
- `3.28_blight_of_contagion_trickster_v1` — campaign_blight_leveling → endgame_ci = sub_archetype_split

**제안:** `sub_archetype_split` 판정에 **transient(일시 캠페인 phase) vs durable(독립 파밍 아키타입)** 한정자 추가. 같은 class+ascendancy+broad identity를 유지하는 순수 레벨링→엔드게임 progression은, 엔드게임이 진짜로 구별되는 farmable sub-archetype가 아닌 한 자동 split하지 않는다.

**주의:** 기존 인스턴스는 **재분류하지 않는다** — 현 룰 하에선 라벨이 defensible(적대검증 판정: keep). 이건 데이터 fix가 아니라 룰 개선 항목.

**출처:** adversarial-verifier (2026-07-15), `3.28_blight_of_contagion_trickster_v1` 적재 검증 중 발견.
**상태:** backlog / 미착수. 착수 시 `build_variant_rules_v2.json` threshold/toggle + calibration log 연동, model v2 테스트 회귀 필수.
