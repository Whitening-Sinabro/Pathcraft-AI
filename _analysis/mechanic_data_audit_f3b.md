# Phase F3b 감사 리포트 — Ritual / Heist / Beyond / Metamorph

- 감사일: 2026-04-19
- 리그 앵커: 3.28 Mirage
- 감사 도메인: Heist (Contract/Blueprint/Trinket), Metamorph (organs), Ritual, Beyond
- 원칙: 감사만, 수정 X

## 감사 대상 매핑

| 도메인 | 필터 함수 | 데이터 소스 | 하드코딩 |
|--------|-----------|-------------|----------|
| **Heist** handpicked | `layer_heist` 2255+ | `_HEIST_HANDPICKED_AREAS` (9 영역) | ✅ 9 items |
| **Heist** 일반 Blueprint | line 2287 | `Class "Heist Blueprint"` (게임 native) | ❌ |
| **Heist** 일반 Contract | line 2297 | `Class "Heist Contract"` (게임 native) | ❌ |
| **Heist** Trinket | line 2306 | `Class "Heist Trinket"` (게임 native) | ❌ |
| **Heist** Objective 47 | line 2931 | `_HEIST_OBJECTIVES` (47 items) | ✅ 47 items |
| **Heist** Rogue's Marker | line 2314 | BaseType 단일 | ✅ 1 item |
| **Heist** Brooch | line 4457 | `Class == "Heist Brooch"` | ❌ |
| **Metamorph** organs | line 2770+ | `_METAMORPH_ORGANS` (5 organs) | ✅ 5 items |
| **Ritual** | 전용 블록 없음 | general currency + Ritual 스카랩(ScarabTypes) | - |
| **Beyond** | 전용 블록 없음 | ScarabTypes Beyond만 | - |

## D1-D7 체크리스트

### D1 — `_meta` 필드

**해당 없음** — F3b 데이터는 코드 내 하드코딩 리스트 또는 게임 native 속성. 별도 JSON 파일 없음.

### D2 — 데이터 신선도

| 메커닉 | 도입 리그 | 변동 이력 | 판정 |
|--------|-----------|-----------|------|
| Heist | 3.12 Heist (2020-09) | 이후 core structure 변동 없음 | ✅ |
| Metamorph | 3.9 Metamorph (2019-12) | 5 organs 불변 | ✅ |
| Ritual | 3.13 Ritual (2021-01) | 스카랩 통합, core 변동 없음 | ✅ |
| Beyond | 3.4 Legacy (2018-10) | 영구 메커닉화, 스카랩만 운영 | ✅ |

### D3 — GGPK 교차 대조

**`_METAMORPH_ORGANS` 5/5**:

| Organ | GGPK 존재 |
|-------|----------|
| Metamorph Brain | ✅ |
| Metamorph Eye | ✅ |
| Metamorph Heart | ✅ |
| Metamorph Liver | ✅ |
| Metamorph Lung | ✅ |

**`_HEIST_OBJECTIVES` 47/47** GGPK ✅ (0 missing, 전수 검증 2026-04-19)

**`_HEIST_HANDPICKED_AREAS` 9 영역 → `Blueprint: X` + `Contract: X` = 18 GGPK BaseType 전부 존재** ✅

### D4 — 하드코딩 dict + 출처 주석

| 위치 | 주석 상태 |
|------|----------|
| `_HEIST_HANDPICKED_AREAS` (2237) | 🟡 Wreckers 패턴 주석 있음. 9 영역 선정 근거(수익성) 명시되지 않음 |
| `_HEIST_OBJECTIVES` (2931) | 🟡 주석 "47종, 컨트랙트 타겟" 있음. 출처 없음 (Wiki? NeverSink?) |
| `_METAMORPH_ORGANS` (2657) | ✅ Metamorph 영구 5 organs 모두 canonical — 주석 간결하게 5종 명시 |

### D5 — 자동 재현 스크립트

**불필요** — 3.12/3.9 이후 stable. 3개 하드코딩 리스트 모두 6+년간 불변.

### D6 — 단위 테스트

| 항목 | 테스트 |
|------|--------|
| `layer_heist` | 기존 `TestLayerHeist`류 커버 (세부 스모크 수준) |
| Metamorph organs 포함 | `TestLayerSpecialBase`류 간접 커버 |

**D6 개선 권고 없음** (stable content + 간접 커버 충분).

### D7 — 필터 출력 통합 검증

Heist/Metamorph 블록 포함 여부 assert 1~2건 있음 (기존 `test_sections_continue.py`). 프로덕션 경로 기본 커버.

## ORPHAN 검증

**결과**: F3b 도메인 내 orphan 없음.

Farming-related orphan은 F3a에서 이미 식별/처리 예정 (farming_mechanics/strategies/farming_strategy_system).

## 발견 및 위험도

### 🟢 통과
- 3개 하드코딩 리스트 (5 + 47 + 9) 전부 GGPK 매칭 (2026-04-19 검증)
- 메커닉 전원 5~7년 stable → stale 위험 최소
- 프로덕션 경로 pytest 간접 커버
- Ritual/Beyond는 별도 블록 없음 — 제품 의사결정 (문제 아님)

### 🟡 MID
1. **`_HEIST_OBJECTIVES` 47 출처 주석 부재**
   - 선정 기준 (Wiki? NeverSink? 커뮤니티?) 불명
   - 권고 (F3b-fix-1, 10min): "POE Wiki Heist/Contract 페이지 + Wreckers L937 2026-04-19 확인" 주석 추가

2. **`_HEIST_HANDPICKED_AREAS` 9 영역 선정 근거 없음**
   - 왜 9개? 수익성 기준? 
   - 권고 (F3b-fix-2, 10min): 수익성 티어 근거 주석 추가

### 🟢 적극 권고 없음
- stable content → 재추출 파이프라인 불필요
- 프로덕션 경로 건전

## F3b 총괄 판정

**✅ PASS (하위 권고 2건)**

**근거**:
- 하드코딩 3개 리스트 전부 GGPK 100% 존재 검증
- 메커닉 stable (3.4~3.13 이후 core 변동 없음)
- 프로덕션 경로 건전, 테스트 커버
- Ritual/Beyond 별도 블록 부재는 설계 선택 (제품 의사결정)

**Fix 태스크 (backlog 등록)**:

| ID | 작업 | 시간 | 우선 |
|----|------|------|------|
| F3b-fix-1 | `_HEIST_OBJECTIVES` 출처 주석 추가 | 10min | 🟡 MID |
| F3b-fix-2 | `_HEIST_HANDPICKED_AREAS` 선정 근거 주석 추가 | 10min | 🟡 MID |

## 참조

- 선례: F2 감사 — 하드코딩 검증 동일 패턴 (`_analysis/mechanic_data_audit_f2.md`)
- F3a (Ultimatum/Blight/Delve): `_analysis/mechanic_data_audit_f3a.md`
