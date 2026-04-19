# Phase F3a 감사 리포트 — Ultimatum / Blight / Delve

- 감사일: 2026-04-19
- 리그 앵커: 3.28 Mirage
- 감사 도메인: Ultimatum + Blight + Delve (Delirium 포함 Harvest/Ritual은 F3b)
- 원칙: 감사만, 수정 X

## 감사 대상 매핑

### 프로덕션 경로 (β Continue)

| 도메인 | 필터 출력 | 데이터 소스 | 상태 |
|--------|-----------|-------------|------|
| Delirium Orbs | `load_ggpk_items.delirium_orbs` (24 orbs) | GGPK Name 매칭 | ✅ GGPK 기반 |
| Blight Maps | `layer_special_maps` line 2027 | `UberBlightedMap True` / `BlightedMap True` (게임 native 속성) | ✅ 게임 엔진 |
| Blight Oils | `load_ggpk_items.oils_top/high/mid/low/premium` | GGPK `mushrune` 태그 | ✅ GGPK 기반 |
| Ultimatum | `layer_endgame_content` line 2596 | `Inscribed Ultimatum` 단일 base | ✅ 하드코딩 1개 (Chronicle of Atzoatl 패턴) |
| Delve | 명시적 블록 없음 — Delve 통화는 general currency 블록에서 처리 | - | 🟡 별도 블록 없음 |

### Legacy 데이터 경로 (β-5b 이후 orphan?)

| 파일 | 라인/크기 | 프로덕션 사용 |
|------|----------|--------------|
| `data/farming_mechanics.json` | 3.27, 12 메커닉 도메인 | ❌ 누구도 로드 안 함 |
| `data/farming_strategies.json` | 3.27, 17 전략 × scarab/map_device | ❌ 누구도 로드 안 함 |
| `python/farming_strategy_system.py` | 1450 lines | ❌ `import farming_strategy_system` 0 히트 |

## D1-D7 체크리스트

### D1 — `_meta` 필드

| 파일 | 상태 |
|------|------|
| `farming_mechanics.json` | 🔴 `_meta` 키 없음. top-level에 `version: "3.27"`, `last_updated: "2025-01-23"`, `description` 평면 배치 |
| `farming_strategies.json` | 🔴 동일 (`version: "3.27"`, `last_updated: "2025-01-01"`) |

### D2 — 데이터 신선도 (현 리그 ±1)

| 파일 | 버전 | 판정 |
|------|------|------|
| `farming_mechanics.json` | **3.27** | 🔴 **1 리그 전** (3.28 Mirage 기준) |
| `farming_strategies.json` | **3.27** | 🔴 동일 |

**사실**: 3.28 Mirage는 2026-02-27 출시. 두 파일 last_updated 2025-01-xx (3.26 Settlers 시기).

### D3 — GGPK 교차 대조

**프로덕션 경로**: GGPK 기반이라 truth reference 계층으로 자동 검증. F2 감사에서 이미 확인 완료.

**Legacy 파일 (orphan)**: 대조 가치 없음 (사용처 없음).

### D4 — 하드코딩 dict + 출처 주석

| 위치 | 상태 |
|------|------|
| `sections_continue.py:2596` Inscribed Ultimatum | 🟡 주석 "Cobalt L6720 — Ultimatum 컨텐츠" 라인 번호 있음. 출처 버전 없음 |
| `sections_continue.py:2027-2046` Blight maps | ✅ 게임 native 속성 기반, 하드코딩 없음 |
| `sections_continue.py:3661+` Oils 티어 (Wreckers L1585-1674) | ✅ 주석 "Wreckers 13단계 계단식 이식" — 출처 라인 번호 명시 |

### D5 — 자동 재현 스크립트

| 파일 | 재현 |
|------|------|
| `delirium_orbs`, `oils_*` | `cargo run --bin extract_data` + `load_ggpk_items` 자동 |
| `farming_mechanics.json` / `farming_strategies.json` | ❌ 없음. 수동 작성 |

### D6 — 단위 테스트

프로덕션 경로: `test_sections_continue.py`에서 `layer_special_maps`, `layer_endgame_content` 스모크 커버.

Legacy 파일 테스트 없음 (orphan이라 적절).

### D7 — 필터 출력 통합 검증

Blighted Map / Oil 티어 / Inscribed Ultimatum 블록 filter output assert는 기존 pytest에 부분 커버.

## ORPHAN 검증

**중대 발견 (3번째 반복 orphan 패턴)**:

### 사실 (2026-04-19 재검증)

```bash
grep -rn "farming_strategy_system\|farming_mechanics\|farming_strategies" \
  --include="*.py" --include="*.ts" --include="*.tsx"
```

결과:
- `python/farming_strategy_system.py:1` — 자기 자신 (1450 lines)
- 다른 Python/TS/TSX 파일 0개

App.tsx는 `coaching.farming_strategy`를 렌더하지만, 이건 **build_coach.py의 Claude LLM 프롬프트 JSON 스키마 필드**(`build_coach.py:147`)로 LLM이 동적 생성. `farming_strategy_system.py`와 무관.

**결론**:
- `farming_mechanics.json` (3.27) → **ORPHAN**
- `farming_strategies.json` (3.27) → **ORPHAN**
- `farming_strategy_system.py` (1450 lines) → **ORPHAN**
- 실제 UI 표시되는 `farming_strategy`는 LLM 생성물

## 발견 및 위험도

### 🔴 HIGH

1. **Farming 파이프라인 전체 ORPHAN (세 번째 동일 패턴)**
   - **사실**: JSON 2개(3.27 stale) + Python 1개(1450 lines) 모두 사용처 없음
   - **비교**: F4 Sanavi, F7 mod_pool과 동일 패턴 — β-5b 재설계 과정에서 legacy 분리됨
   - **위험**: 1450 lines legacy 코드 유지 부담 + 3.27 stale 데이터 혼란
   - **권고**: 3개 파일 삭제 (또는 `_archive/`)

### 🟡 MID

2. **Delve 전용 블록 없음**
   - **사실**: Delve 통화(Fossils/Resonators)는 `load_ggpk_items.fossils_*`, `resonators_*`로 GGPK 기반
   - **영향**: Delve 메커닉 자체는 general currency 블록에서 커버. 전용 필터 블록은 없어도 실기능 동작.
   - **권고**: 현 상태 OK. 전용 블록 신설은 제품 기능 요구에 따라 별도 판단.

3. **Inscribed Ultimatum 출처 버전 주석 부재**
   - 🟡 라인 번호는 있지만 Cobalt 몇 버전인지 불명
   - 권고 (F3a-fix-3, 5min): `# Cobalt 8.19.x L6720 (2026-04-19 확인)` 형태로 보강

### 🟢 통과

- Oils, Delirium Orbs, Blight Maps 프로덕션 경로 GGPK + 게임 native 기반으로 건전

## F3a 총괄 판정

**⚠️ CONDITIONAL (HIGH 1건, ORPHAN 3파일)**

**근거**:
- 프로덕션 경로 (GGPK 기반) 건전
- Legacy farming_* 3파일 완전 orphan — F4 Sanavi / F7 mod_pool과 동일 패턴
- Delve 전용 블록 부재는 설계 선택 (제품 의사결정 대상)

**Fix 태스크 (backlog 등록)**:

| ID | 작업 | 시간 | 우선 |
|----|------|------|------|
| F3a-fix-1 | `farming_mechanics.json` + `farming_strategies.json` + `farming_strategy_system.py` 삭제 or `_archive/` | 15min | 🔴 HIGH |
| F3a-fix-2 | (선택) Delve 전용 필터 블록 신설 — 제품 기능 검토 후 | 2~3h | 🟢 LOW 우선 |
| F3a-fix-3 | Inscribed Ultimatum 주석에 Cobalt 버전 추가 | 5min | 🟡 MID |

## 참조

- F4 Sanavi orphan 선례: `_analysis/mechanic_data_audit_f4.md`
- F7 mod_pool orphan 선례: `_analysis/mechanic_data_audit_f7.md`
- β-5b 재설계 맥락: `.claude/status/continue_architecture.md`
