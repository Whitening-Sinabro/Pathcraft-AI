## 지금
- **세션 종료 (2026-04-21, Priority 0+1+2+4 세션)** — current.md 우선순위 0/1/2 완결 + 4(POE2) 착수. Tier 2 C Fast/Strict 분리(훅 11건 테스트), L3_RETRY_METRIC 로그(코치 테스트 2건), valid_gems pollution 4건 제거(refresh 테스트 11건), extract_data.rs --game 플래그(Rust 테스트 8건). 전체 pytest 639/639 green.

## 다음 할 것 (우선순위순)

0. [ ] **L3 auto-retry 인게임 검증 (미검증)** — Tauri 에서 Onslaught Support 같은 hallucination 재분석 시 `L3_RETRY_METRIC success=true` 로그 찍히는지 확인. `_retry_info.final_dropped=[]` 비율 수집
1. [ ] **DoD 수동 검증 (미검증 대기)** — Tauri 창 `Ctrl+R` 후 FilterPanel / 오버레이 / 히스토리 각 항목
2. [ ] **POE2 D0 잔여** — `src-tauri/src/lib.rs` 10개 Tauri 커맨드 `game: Game` 인자 추가 + Python 스크립트(ai_build_analyzer/build_coach/pob_parser) `--game` 플래그. `extract_data.rs` 는 완료.
3. [ ] **POE2 D2/D3 drift 선해결** — Mods POE2 +24B / SkillGems POE2 +32B. backlog 4번 Option B (로컬 override) 권장
4. [ ] **POE2 D6 PRD** — 코치 프롬프트/support 재설계. backlog 7.3 요구
5. [ ] **Strict 모드 실측** — TEST_CLAIM ("all tests pass") 발언 세션에서 full pytest 실제 트리거 확인 (30~60s 예상)
5. [ ] **필터 생성 인게임 검증**
6. [ ] **P1 인게임 검증** — `npm run tauri dev`
7. [ ] **Passive P2~P6** — DAT 경로 추출 + DDS→PNG + manifest + renderer + UX
8. [ ] **Mode 승격 마무리** — FilterPanel mode state → useBuildAnalyzer 마이그레이션
9. [ ] **메인 창 LevelingGuide A형 적용 여부 결정**
10. [ ] **Syndicate empty state + mode 필터**
11. [ ] **Syndicate S4** — 골든 OCR + SHA-256 캐시 + Mastermind 추적
12. [ ] **Phase 5b/5c** — 오버레이 콘텐츠 + 위치 영속
13. [ ] **alias 맵 재감사 다음 스텝** — 이번 세션에서 valid_gems 는 깨끗함 확인(Awakened 38/38, Vaal 61/61, transfigured 210, meta 전부 커버). 다음은 `data/gem_aliases.json` 103개 엔트리 재검증 + POE2 alias 맵 설계

## 도메인 파일 포인터

- [코치 품질 Phase H 백로그](coach_quality_backlog.md) — H1~H5 + H6 완료, L3 인게임/alias 누적
- [POE2 통합 backlog](poe2_integration_backlog.md) — feasibility 완료, D0~D8 (제품 요구 확정 전 착수 금지)
- [디자인 Phase 0~5 플랜](design_phase_plan.md) — P5 미완
- [Syndicate 전면 개편 S1~S4](syndicate_phase_plan.md) — S1~S3 완료
- [패시브 asset 플랜](passive_tree_assets_plan.md) — P1 완료, P2~P6 대기
- [Syndicate 리서치 1/2차](../../../_analysis/syndicate_research_2026-04-20.md / syndicate_ux_research_2026-04-20.md)
- [POE2 테이블 카탈로그](../../../_analysis/poe2_tables.json)
- [Continue 아키텍처](continue_architecture.md)
- [패시브 트리 원 플랜](passive_tree_plan.md)
- _analysis/ggpk_truth_reference.json — POE1 19 테이블 진실 anchor
- docs/league_refresh.md

## Class Start 노드 매핑 (data.json 수동)
- 0: Scion (58833) / 1: Marauder (47175) / 2: Ranger (50459)
- 3: Witch (54447) / 4: Duelist (50986) / 5: Templar (61525) / 6: Shadow (44683)

## 잔존 이슈 (허용/추후 처리)

- **valid_gems 다른 카테고리 누락 가능성** — transfigured 발견 사례로 meta/awakened/vaal alt 등 추가 감사 필요 (우선순위 2)
- **L3 인게임 미검증** — 재시도 교정 프롬프트 실제 효과 측정 필요
- **Phase E subagent 제기 미패치 5건** — (1) ACTIVE_EVIDENCE_TOOLS 에 Task 미포함 의도적이지만 문서화 없음 (2) `_is_real_user_prompt` mixed event turn boundary (3) git status `line[3:]` rename/공백 파일명 (4) 한국어 문장 경계 edge case (5) Claude Code Stop 훅 실제 stdin 스키마 미확정 — 다음 세션 `CLAUDE_CLAIM_GATE_DEBUG=1` 켜고 hook_input.log 실측 대기
- **Tier 2 C 대기** — Fast/Strict 분리, 현 테스트 부하 문제 없으면 연기 가능
- **SyndicateBoard 내부 일관성** — ss22 deprecated flag UI 확인 (Tauri 실측)
- **Cmd+K palette UX** — 초보자 부적합 결정 보류
- **PassiveTreeCanvas 623줄** — 300 룰 초과, 복잡도로 허용
- **Syndicate Vision OCR** — 골든 스크린샷 테스트 부재 (S4)
- **Coach 좀비 cleanup on window close**
- **Model toggle frontend 테스트 부재**

## UX 결정 기록 (누적)
- 우클릭 dealloc 분리 → 되돌림 (왼클릭 토글 유지)
- 수동 URL import UI 스킵 (자동 디코드 대체)
- AI 이모지 제거, UI 이모지 → SVG 아이콘
- 전면 리디자인 = 다크 단일 + POE Rarity + Linear 레이아웃 + 2-창 오버레이
- 기본 리그 모드 = SC (SSF/HCSSF/Trade 3모드는 Wreckers 스타일 단일 파일 위에 경제·철학 조정만 차이)
- **빌드 분석 = 진입점** 원칙
- 패시브 class start = anchor only
- **코치 모델 기본 Haiku** — "빠름 / 느리지만 디테일 / 심층 분석" 3버튼
- **게임 토글 TopBar** (startup modal 아님) — POE1 기본, POE2는 경고 배너
- **빌드 히스토리 (pobb 스타일)** — localStorage 최근 20개, 자동 최신 복원
- **오버레이 레벨링 = 탭 네비 + 활성 phase bullet** — 4 phase 각 Lv range
- **FilterPanel 3모드 유지** — SSF/HCSSF/TRADE 공통 Wreckers 스타일 + 경제·철학 조정
- **코치 정식화 = 코드 레이어 hard constraint** — normalizer 가 주 제약 (Phase H)
- **4-Layer hallucination 방어** — L1 prompt + L2 strict + L3 retry + L4 풀스크린 블록 (Phase H6). **L3_RETRY_METRIC 로그 grep-friendly** (2026-04-21).
- **자가-PASS 방어 Tier 2** — A(Claim-gate) + B(Phase E audit-all subagent) + C(Fast/Strict 모드 분리: 기본 fast = changed-files, TEST_CLAIM 감지 시 strict = full suite). 전부 완료 (2026-04-21).
