# POE2 통합 Backlog

> **현 상태: feasibility 완료, 기능 통합 0%.** 본 문서는 차후 POE2 제품 요구가 발생했을 때 재착수할 수 있도록 현황/단계/의존을 정리한다.
> 현재 PathcraftAI는 **POE1 전용**으로 scope 유지. 아래 항목은 _제품 요구 확정 전까지 착수하지 않는다_.

---

## 1. 완료된 인프라 (feasibility Phase A~C, 2026-04-20 세션)

| Phase | 산출물 | 위치 |
|-------|--------|------|
| A | POE2 GGPK/Bundle 추출 100% 재사용 (Oodle/BundleIndex/parse_paths) | `src-tauri/src/bin/probe_poe2.rs` |
| A2 | 942 unique base + 9 locale 테이블 카탈로그 | `_analysis/poe2_tables.json` |
| B | UI 토글 (ActiveGameContext + TopBar + localStorage + 경고 배너) | `src/contexts/ActiveGameContext.tsx`, `src/App.tsx:127`, `src/components/shell/TopBar.tsx` |
| C | SchemaStore `Game` enum + `validFor` 비트마스크 필터 + 중복 테이블 dedup | `src-tauri/src/schema.rs` |
| C 검증 | `probe_poe2_schema` — 11/13 핵심 테이블 row_size 즉시 호환 (85%) | `src-tauri/src/bin/probe_poe2_schema.rs` |

**upstream 현황 (2026-04-20 확인)**
- `poe-tool-dev/dat-schema` 최신: 2026-04-08, version 7, createdAt 1775663541
- 로컬 `data/schema/schema.min.json`: 2026-04-07 버전
- 컬럼 레벨 diff (Mods/SkillGems POE2): **동일 — drift 원인 아님**
- upstream fetch만으로 drift 해소 불가 (upstream 자체에 POE2 Mods 24B / SkillGems 32B 컬럼 누락)

---

## 2. 미통합 상태 — 솔직 요약

현재 `activeGame` 값을 실제로 소비하는 코드는 **단 1곳**: `src/App.tsx:127` 경고 배너 분기.

**빌드 분석 파이프라인 (POB parser / ai_build_analyzer / build_coach / FilterPanel / PassiveTreeView / SyndicateBoard) 전량 POE1 데이터 참조**, `activeGame`/`Game::Poe2` 참조 0건.

즉 TopBar에서 POE2 토글해도:
- POB 파싱 → POE1 valid_gems.json 참조
- 코치 프롬프트 → POE1 270 support 젬 화이트리스트
- 필터 생성 → POE1 ItemClass/BaseType
- 패시브 뷰어 → POE1 tree 구조
- Syndicate → POE1 전용 메커닉 (POE2 없음)

변하는 것은 **상단 경고 배너 문구 하나**뿐.

---

## 3. 통합 단계 (Phase D~)

**D0. 데이터 레이어 라우팅** — 기반 작업, 이후 모든 단계의 선행 조건
- 각 Tauri 커맨드에 `game: Game` 인자 추가 (lib.rs)
- `SchemaStore` 게임별 lazy 로드 캐시 (두 번 파싱 비효율 방지)
- Python 스크립트 (ai_build_analyzer/build_coach/pob_parser) `--game` CLI 플래그 추가
- 추정 작업량: 0.5~1 세션

**D0 진행 상황 (2026-04-21 세션):**
- [x] `extract_data.rs` — `--game poe1|poe2` 플래그, 게임별 출력 디렉터리(data/game_data_poe2/), `SchemaStore::load_for_game` 사용, POE2 경로 auto-detect (Daum/Grinding Gear/Steam). 단위 테스트 8건 추가.
- [ ] `lib.rs` 10개 Tauri 커맨드 game 인자 미적용
- [ ] Python 스크립트 --game 플래그 미적용

**D1. POB 포맷 POE2 대응**
- POE2용 Path of Building fork (SnosMe: PathOfBuilding-PoE2) 포맷 확인
- `python/pob_parser.py` POE2 XML 스키마 분기 추가
- POE2 POB URL 디코더 검증 (pastebin 호환성)
- 추정 작업량: 1~2 세션 (fork 포맷 조사 포함)

**D2. 젬 DB POE2 전용 수집**
- `data/valid_gems_poe2.json` 신규 (POE2 GGPK → SkillGems 테이블에서 추출)
- **drift 선해결 필요**: SkillGems 32B 누락 컬럼 중 gem 타입/weapon restriction 컬럼 여부 확인
- support 젬 POE2 포맷 확인 (POE2는 support 시스템이 gem 내장형으로 바뀜 — 게임 자체 설계 차이)
- 추정 작업량: 1 세션

**D3. 아이템 base DB POE2 전용**
- `data/base_items_poe2.json` — POE2 BaseItemTypes 추출
- POE2는 무기 카테고리/방어구 타입이 POE1과 다름 (quarterstaff, focus 등 신설)
- ItemClass 명칭 매핑 테이블 필요
- 추정 작업량: 1 세션

**D4. 패시브 트리 POE2 재구축**
- POE2 트리는 구조 완전 다름 (cluster jewel 없음, class start 좌표 다름, passive node 수 다름)
- `src/utils/passiveTreeRender.ts` POE2 전용 렌더 분기
- `data/passive_tree_poe2.json` 신규 (POE2 PassiveSkills 테이블 추출)
- 추정 작업량: 2 세션 (데이터 추출 + 렌더 조정 + UX 검증)

**D5. 필터 생성 POE2**
- `.filter` 문법 POE2 호환성 확인 (POE1/POE2 filter 포맷 동일한지 GGG 공식 문서 검증)
- ItemClass 이름 변경 매핑 (예: "Two Hand Axes" → "Two-Handed Axes" 등)
- `src/components/FilterPanel.tsx` 게임별 itemClass 리스트 분기
- 추정 작업량: 0.5~1 세션

**D6. 코치 POE2 프롬프트**
- `python/build_coach.py` SYSTEM_PROMPT 재작성 (POE2 메커닉 기반: souls, specters, charm 등 POE1에 없는 시스템)
- POE2 270 support → POE2는 support gem 시스템 다름, 재설계 필요
- `coach_validator.py` 이중 화이트리스트 (게임별 젬 세트)
- 추정 작업량: 1 세션

**D7. Syndicate 비활성화**
- POE2에 Syndicate 메커닉 **없음** (Betrayal 리그 POE1 전용)
- `src/components/SyndicateBoard.tsx` game==='poe2' 시 렌더 skip
- 상위 네비에서도 Syndicate 탭 숨김
- 추정 작업량: 0.1 세션

**D8. 리그 anchor POE2 전용 프로세스**
- POE1: `Docs/league_refresh.md` — Mirage 기준 갱신 절차
- POE2: 별도 프로세스 필요 (POE2 패치 주기/리그 이름 independent)
- `_analysis/ggpk_truth_reference.json` POE2 버전 신규 — 별도 anchor
- 추정 작업량: 0.5 세션

---

## 4. 알려진 drift 2건 (D0 착수 시 재점검)

| 테이블 | actual (parser) | schema | drift | 추정 누락 |
|--------|----------------|--------|-------|----------|
| Mods (POE2) | 677B | 653B | **+24B** | Key(16) + Row(8) 또는 U64×3 등 |
| SkillGems (POE2) | 239B | 207B | **+32B** | List(16)×2 또는 String(8)×4 등 |

**해결 경로 3개 (D0 단계에서 선택):**
- A. upstream `poe-tool-dev/dat-schema` 이슈 등록 후 대기 (수동 개입 0, 기약 없음)
- B. 로컬 override 스키마 (`data/schema/schema_poe2_override.json`) + 실데이터 byte pattern 스캔으로 누락 컬럼 타입 역추적. upstream 패치 시 merge 우선순위 조정
- C. 부분 호환 허용 (끝 24B/32B 미파싱). Mods 저수준 경고, SkillGems gem.weapon_restriction 누락 가능성 수용

**우선 권장: B** — 제품 통합 시 drift 0 필수, 역추적 비용 1 세션 이내

---

## 5. 외부 의존 / 환경

| 항목 | 값 |
|------|-----|
| upstream schema | github.com/poe-tool-dev/dat-schema (MIT, SnosMe 유지) |
| upstream 최신 확인 | 2026-04-20 — 2026-04-08 release |
| POE2 본체 경로 (로컬) | `C:\Daum Games\Path of Exile2` |
| POE2 POB fork | PathOfBuilding-PoE2 (별도 fork, 포맷 상이) |
| poe.ninja POE2 API | 별도 엔드포인트 — 빌드 통계/가격 다름 |

---

## 6. 참고 파일 인덱스

| 경로 | 역할 |
|------|------|
| `_analysis/poe2_tables.json` | 942 테이블 카탈로그 (row_count / size / locale_variants / estimated_row_size) |
| `_analysis/schema_upstream.min.json` | upstream 2026-04-08 snapshot (drift 비교용, 제품 배포용 아님) |
| `src-tauri/src/bin/probe_poe2.rs` | GGPK feasibility probe |
| `src-tauri/src/bin/probe_poe2_schema.rs` | schema drift 측정 |
| `src-tauri/src/schema.rs` | Game enum + load_for_game |
| `src/contexts/ActiveGameContext.tsx` | UI 토글 state |

---

## 7. 우선순위 원칙 (재착수 판단 기준)

1. **POE2 제품 요구가 명시적으로 확정되기 전까지 본 backlog 착수 금지**. POE1 완성도(필터/코치/패시브/Syndicate) 우선
2. 제품 요구 확정 시 **D0 → D1 → D2~D6 병렬** 순서
3. D4(패시브)와 D6(코치)은 UX/데이터 모두 복잡 → 별도 PRD 필요
4. Syndicate 비활성화(D7)는 저비용이나 POE2 통합 전에 손대지 말 것 (현재 POE1에서만 동작하므로 분기 없이도 안전)

---

## 8. 회귀 방지 (선택적 투자 — 1/3 세션)

다음 조치는 **향후 POE2 재착수 시 상태 파악 시간을 1초로 줄임**:
- `SchemaStore::load_for_game(Poe2)` doc comment에 "Mods/SkillGems 부분 호환 (24B/32B 누락)" 명시
- drift 값이 24/32에서 이탈하면 fail하는 integration test 추가 (upstream 패치 감지 자동화)
- 본 backlog 파일에 drift 값 변동 이력 append

현재 세션에서는 **투자 보류** (POE1 원 세션 목표 복귀 우선).
