# Phase F4 감사 리포트 — Sanavi 티어 데이터

- 감사일: 2026-04-19
- 리그 앵커: 3.28 Mirage
- 감사 도메인: Sanavi 필터 기반 32 카테고리 × 200+ tier 토큰 × 5530 items
- 원칙: 감사만, 수정 X

## 감사 대상 매핑

| 파일 | 역할 | 소비처 |
|------|------|--------|
| `data/sanavi_tier_data.json` | 32 카테고리 × 5530 items 티어 데이터 | ⚠️ `_analysis/gen_test_filter_v4.py` (DEPRECATED) |
| `python/sanavi_tier_parser.py` | Sanavi 3-STRICT filter 파싱 → 위 JSON 생성 | ❌ 누구도 import 안 함 |

## D1-D7 체크리스트 결과

### D1 — `_meta` 필드 완비

| 파일 | 상태 |
|------|------|
| `sanavi_tier_data.json` | 🔴 **`_meta` 키 없음** |

**세부**: top keys = 32 카테고리 ('6l', 'gold', 'influenced', 'rare', ...). `_meta` 필드 전무. 어떤 Sanavi 필터 버전에서 파싱했는지, 언제 뽑았는지 불명.

### D2 — 데이터 신선도

**판정 불가** — 버전 기록 없음.

**사실** (2026-04-19 재확인):
- `sanavi_tier_parser.py:28~29` 경로: `POE_FILTER_DIR / "Sanavi_3_Strict.filter"`
- 파싱 시점 Sanavi 필터 버전이 어떤 POE 리그에 맞춰졌는지 기록 없음
- Sanavi 필터는 매 리그 업데이트되므로 3.25/3.26/3.27/3.28 중 어느 시점인지 중요

### D3 — GGPK 교차 대조

**샘플 스팟체크** (2026-04-19):

**uniques.t1 (Sanavi T1 유니크)**:
- Sanavi 필터가 최고 티어로 분류한 유니크들
- GGPK UniqueStashLayout.json에 1525 rows 존재 — 교차검증 가능하나 이번 감사 미실행

**exoticbases.hightier (6l.hightier 47종)**:
- Sanavi BaseType 이름 리스트 → GGPK `BaseItemTypes.json` Name 대조 가능

**결론 (현 시점)**: 교차검증 가능한 데이터 접근 가능하나 Sanavi 소스 버전 불명으로 대조 가치 제한.

### D4 — 하드코딩 dict + 출처 주석

**해당 없음** — 데이터는 모두 JSON, 하드코딩 없음.

### D5 — 자동 재현 스크립트

✅ **존재**: `python/sanavi_tier_parser.py`. 사용자가 로컬 POE 폴더의 `Sanavi_3_Strict.filter` 파일을 가져야 재생성 가능.

### D6 — 단위 테스트

❌ **없음** — `test_sanavi_*.py` 파일 없음.

### D7 — 필터 출력 통합 검증

❌ **해당 없음** — 프로덕션 필터 파이프라인 (β Continue)이 sanavi 데이터를 소비하지 않음.

## ORPHAN 검증

**중대 발견**: 파이프라인 전체 orphan.

### 사실 (2026-04-19 재검증)

```bash
grep -rn "sanavi_tier_data\|sanavi_tier_parser" --include="*.py"
```

결과:
- `_analysis/gen_test_filter_v4.py:50` — 유일 소비처
- `python/sanavi_tier_parser.py:119` — 자기 자신 (생성자)

`_analysis/gen_test_filter_v4.py` 파일 헤더 확인:

> "DEPRECATED (2026-04-13): β-5b에서 pathcraft_sections / sections_* 삭제됨. 이 스크립트는 ImportError로 실행 불가."

**결론**: `sanavi_tier_data.json` + `sanavi_tier_parser.py` = **완전 orphan**.
- production 필터 파이프라인 (β Continue)이 사용하지 않음
- 유일한 소비처가 DEPRECATED 스크립트

## 발견 및 위험도

### 🔴 HIGH

1. **Sanavi 파이프라인 전체 ORPHAN (β-5b 이후 고아)**
   - **사실**: `sanavi_tier_data.json` (5530 items, 32 cat) + `sanavi_tier_parser.py` 생성자 모두 production 경로에서 분리됨
   - **WHY 문제**: mod_pool (F7)과 동일한 패턴. 정비되지 않은 데이터 파일 누적 → 혼란 + disk 공간 낭비 (JSON 수백KB)
   - **검증**: deprecated 스크립트(`_analysis/gen_test_filter_v4.py`)가 유일 소비자. 해당 스크립트는 ImportError로 실행 불가
   - **권고**: **삭제**. Sanavi 필터의 티어 분류를 재도입할 계획이 있다면 β Continue 아키텍처로 재설계 필요

2. **`_meta` 전무**
   - 파이프라인 orphan이므로 실영향 없음. #1에서 삭제 처리 시 자동 해소

### 🟡 MID (삭제하지 않는 경우)

3. **버전 추적 체계 부재**: Sanavi 필터 리그별 차이를 JSON이 반영하지 못함. 재도입 시 `_meta.sanavi_version` + `_meta.poe_league` 필수

### 🟢 통과 없음

전 파일 orphan 상태라 "통과" 판정 불가.

## F4 총괄 판정

**⚠️ CONDITIONAL (HIGH 1건, ORPHAN)**

**근거**:
- `sanavi_tier_data.json` + `sanavi_tier_parser.py` production 파이프라인에서 분리됨 (β-5b 2026-04-13)
- 유일 소비자 deprecated, 실행 불가
- `_meta` 부재 + 버전 추적 전무
- mod_pool과 동일한 orphan 패턴

**Fix 태스크 (backlog 등록)**:

| ID | 작업 | 시간 | 우선 |
|----|------|------|------|
| F4-fix-1 | `sanavi_tier_data.json` + `sanavi_tier_parser.py` 삭제 (또는 `_archive/` 이동) | 10min | 🔴 HIGH |
| F4-fix-2 (대안) | Sanavi 티어 체계를 β Continue에 재도입 (스코프 큼, 별도 task) | 4~6h | 🟢 LOW 우선도 |

**추천**: F4-fix-1 (삭제). Sanavi 필터 통합은 현재 β Continue가 Cobalt + Wreckers + NeverSink 3레퍼런스로 충분. Sanavi는 CustomAlertSound 경로만 소비 중 (sections_continue:477+, 사운드 참조).

## 참조

- β-5b 리그 아키텍처 전환: `.claude/status/continue_architecture.md`
- orphan 선례 (F7 mod_pool): `_analysis/mechanic_data_audit_f7.md`
- Sanavi 필터 사운드 연계 (현 활용): `sections_continue.py:477-500`
