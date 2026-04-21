## 지금
- **POE1 회고 완료 (2026-04-21)** — 미커밋 쌓임을 A-2 도메인 분할 6커밋으로 정리, Phase H 완료 메모리 작성, stale 메모리 업데이트
- **다음 단계:** Phase H 인게임 검증 → POE2 착수 준비

## 다음 할 것 (우선순위순)

1. [ ] **Phase H 인게임 검증** — `npm run tauri dev` → 실빌드 분석 → ① 배너 메인/오버레이 노출 ② 젬 약칭 자동 교정 ("bleed chance" → "Chance to Bleed Support") ③ 유니크 약칭 교정 ("hh" → "Headhunter") ④ 슬롯 정식화 ("chest" → "Body Armour") ⑤ 자연어 설명 경고 없이 통과 ⑥ SYSTEM_PROMPT H4 반영 후 trace 수 감소 A/B
2. [ ] **DoD 수동 검증 (미검증 대기)** — 기존 Tauri 창 `Ctrl+R` 후:
   - FilterPanel: 소개 문구 / 엄격도 안내 / 모드 툴팁 / ".filter 다운로드됨" 피드백
   - 오버레이: 4 phase 탭 / 활성 phase bullet / 젬 링크 `Cleave - Bleed Chance - Ruthless` 형식 / 스킬 전환 inline
   - 히스토리: 분석 후 자동 저장 / 새로고침 즉시 복원 / 다른 빌드 선택 복원 / × 삭제 / 20개 초과 자동 trim
3. [ ] **POE2 착수** — 구두 설명 only. 데이터 선결(D0+D2+D3+D6) → Bleed Twister. `project_next_session_poe2.md` + `poe2_integration_backlog.md` 참조. Phase H 인프라 재사용(`reference_normalizer_infra_patterns.md`)
4. [ ] **필터 생성 인게임 검증** — 원래 세션 목표 계속 (실필터 문법 점검)
5. [ ] **P1 인게임 검증** — `npm run tauri dev` → 7 클래스 start 포트레이트 + 호버 링 + 줌/팬 sync
6. [ ] **Passive P2~P6** — DAT 경로 추출 + DDS→PNG + manifest + renderer + UX
7. [ ] **Mode 승격 마무리** — FilterPanel mode state → useBuildAnalyzer 마이그레이션
8. [ ] **메인 창 LevelingGuide A형 적용 여부 결정** — 오버레이와 동일화할지 / 체크리스트 방식 유지할지
9. [ ] **Syndicate empty state + mode 필터** — 빌드 분석 전 "먼저 분석하세요" / 모드별 프리셋
10. [ ] **Syndicate S4** — 골든 OCR + SHA-256 캐시 + Mastermind 추적
11. [ ] **Phase 5b/5c** — 오버레이 콘텐츠 + 위치 영속

## 도메인 파일 포인터

- [코치 품질 Phase H 백로그](coach_quality_backlog.md) — Normalizer 파이프라인 (H1~H5 구현 완료, 인게임 검증/alias 누적만 남음)
- [POE2 통합 backlog](poe2_integration_backlog.md) — feasibility 완료, D0~D8 단계별 통합 (제품 요구 확정 전까지 착수 금지)
- [디자인 Phase 0~5 플랜](design_phase_plan.md) — 어플 리디자인 (P5 미완)
- [Syndicate 전면 개편 S1~S4](syndicate_phase_plan.md) — S1/S2/S3 완료
- [패시브 asset 플랜](passive_tree_assets_plan.md) — run-time + SVG fallback, P1 완료, P2~P6 대기
- [Syndicate 리서치 1/2차](../../../_analysis/syndicate_research_2026-04-20.md / syndicate_ux_research_2026-04-20.md)
- [POE2 테이블 카탈로그](../../../_analysis/poe2_tables.json) — 942 base tables (row_count/size/locale_variants)
- [Continue 아키텍처](continue_architecture.md)
- [패시브 트리 원 플랜](passive_tree_plan.md)
- _analysis/ggpk_truth_reference.json — POE1 19 테이블 진실 anchor
- docs/league_refresh.md — 리그 교체 순서

## Class Start 노드 매핑 (data.json 수동)
- 0: Scion (58833) / 1: Marauder (47175) / 2: Ranger (50459)
- 3: Witch (54447) / 4: Duelist (50986) / 5: Templar (61525) / 6: Shadow (44683)

## 잔존 이슈 (허용/추후 처리)

- **test_syndicate_advisor.py 1건 실패** — ss22 deprecated 이후 meta_2x2_5 반환, 테스트 기대값 업데이트 누락. 별건
- **SyndicateBoard 내부 일관성**: ss22 deprecated flag UI 확인 필요 (다음 세션 Tauri 실측)
- **Cmd+K palette UX**: 초보자 부적합 → 고인물 모드 뒤로 숨김 or 삭제 결정 보류
- **PassiveTreeCanvas 623줄**: 300 룰 초과, 기능 복잡도로 허용
- **Syndicate Vision OCR**: 골든 스크린샷 테스트 없음 (S4에서 추가)
- **Coach 좀비 cleanup on window close** — 후속 백로그 (앱 종료 hook에서 cancel_coach 호출)
- **Model toggle frontend 테스트 부재** — 후속 백로그

## UX 결정 기록 (누적)
- 우클릭 dealloc 분리 → 되돌림 (왼클릭 토글 유지)
- 수동 URL import UI 스킵 (자동 디코드 대체)
- AI 이모지 제거, UI 이모지 → SVG 아이콘
- 전면 리디자인 = 다크 단일 + POE Rarity + Linear 레이아웃 + 2-창 오버레이
- 기본 리그 모드 = SC (SSF/HCSSF/Trade 3모드는 Wreckers 스타일 단일 파일 아키텍처 위에 경제·철학 조정만 차이)
- **빌드 분석 = 진입점** 원칙
- 패시브 class start = anchor only
- **코치 모델 기본 Haiku** (비용 민감) — "빠름 / 느리지만 디테일 / 심층 분석" 3버튼
- **게임 토글 TopBar** (startup modal 아님) — POE1 기본, POE2는 경고 배너
- **빌드 히스토리 (pobb 스타일)** — localStorage 최근 20개, 자동 최신 복원, 수동 선택 복원. 30일 경과 압축은 Phase B로 분리
- **오버레이 레벨링 = 탭 네비 + 활성 phase bullet 노트** — 4 phase(Act1-4/5-10/초반맵/엔드게임) 각 Lv range로 links_progression + skill_transitions 필터
- **FilterPanel 3모드 유지** — SSF/HCSSF/TRADE 모두 Wreckers 스타일 단일 파일 위에 조정. 소개 문구에 명기
- **코치 정식화 = 코드 레이어 hard constraint** — prompt engineering은 보완, normalizer가 주 제약 (Phase H 원칙)
