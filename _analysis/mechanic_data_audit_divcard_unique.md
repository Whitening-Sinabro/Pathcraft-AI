# Phase F1+F6 감사 — Divination Card + Unique Base

> 2026-04-17 실시. 감사만. 수정은 별도 task.
> 플랜: `.claude/status/mechanic_data_audit_plan.md`

## 범위

- **F1 Divcard**: `data/hc_divcard_tiers.json`, `build_extractor.UNIQUE_TO_DIVCARD`, `wiki_data_provider.KNOWN_DIV_CARDS`, `neversink_filter_rules.json::divination_cards`
- **F6 Unique base**: `build_extractor.UNIQUE_TO_BASE`, `extract_build_unique_bases` fallback path, L10 re_show `chanceable_bases` 소비

## 주요 발견 요약 (Critical)

| # | 항목 | 상태 | 심각도 |
|---|------|------|--------|
| 1 | `hc_divcard_tiers.json` 실시간 파이프라인에서 미사용 (orphan) | ❌ | HIGH (혼동 유발) |
| 2 | 하드코딩 디비카 dict 3곳 분산 + 중복 | ❌ | HIGH (단일 진실원 부재) |
| 3 | `neversink_filter_rules.json` `_meta` 부재 (런타임 실사용 파일) | ❌ | HIGH |
| 4 | `UNIQUE_TO_BASE` 22개 — 전체 POE1 유니크 ~1500개 대비 1.5% | 🟡 | MID (POB 경로로 대부분 커버) |
| 5 | 재현 가능한 생성 스크립트 전무 | ❌ | HIGH |
| 6 | Wiki Cargo API 인프라는 이미 존재 (`wiki_data_provider.py`) | ✅ | 긍정 |

## D1~D7 체크리스트 결과

### `data/hc_divcard_tiers.json`

| 항목 | 결과 | 근거 |
|------|------|------|
| D1 `_meta` | ❌ FAIL | 파일 최상위에 `_meta` 키 없음. `"excustomstack"`부터 시작 |
| D2 신선도 | ⚠️ 불명 | mtime 2026-04-12, 하지만 어느 리그 기준인지 명시 없음 |
| D3 GGPK/POB/Wiki 대조 | ⏸️ 연기 | 우선순위 낮음 (하단 "Critical 1" 참조) |
| D4 하드코딩 | N/A | 파일 자체는 dict 아님 |
| D5 생성 스크립트 | ❌ FAIL | `find` 결과 생성 스크립트 0건 |
| D6 단위 테스트 | ❌ FAIL | 직접 테스트 없음 |
| D7 필터 출력 | ⏸️ 연기 | Phase F 말미 |

**구조**: `excustomstack(1) + t1(51) + t2(41) + t3(74) + t4c(47) + t5c(14) + t4(121) + t5(103) = 452 cards`

**실사용 여부**: `grep -rn hc_divcard_tiers` 결과 production 코드 0건. `_analysis/gen_test_filter_v4.py:266` (HCSSF 모드 오버라이드) 만 소비. β Continue 아키텍처(`sections_continue.py`)는 이 파일 참조하지 않음.

**판단**: **Orphan 데이터**. 삭제 또는 명시적 HCSSF 오버라이드 파이프라인 연결 필요. 현재 상태로는 "있긴 한데 안 쓰이는" 혼동 원천.

### `data/neversink_filter_rules.json` (실제 런타임 사용)

| 항목 | 결과 | 근거 |
|------|------|------|
| D1 `_meta` | ❌ FAIL | `python -c "json.load(...).get('_meta')"` → `None` |
| D2 신선도 | ⚠️ 불명 | mtime 2026-04-06, NeverSink 버전 정보 없음 |
| D3 대조 | ⏸️ 연기 | 필요 |
| D4 하드코딩 | N/A | |
| D5 생성 스크립트 | ❌ FAIL | NeverSink git에서 복사한 것으로 추정되나 추적 불가 |
| D6 단위 테스트 | 부분 | `test_sections_continue.py`에 divcard 블록 스모크 존재 |

**구조**: 디비카 티어 `t1_top(52) + t2_high(60) + t3_good(89) + t4_medium(121) + t5_common(14) = 336 cards`. `hc_divcard_tiers.json`과 **다른 스키마** (t1_top vs t1, t4c 같은 HC 변형 티어는 이 파일에 없음).

**소비처**: `sections_continue.py:944 load_category_data` → `layer_divcards`(line 1106) → L8 블록.

### `build_extractor.UNIQUE_TO_DIVCARD` (build_extractor.py:81-103)

| 항목 | 결과 |
|------|------|
| D4 하드코딩 | ❌ FAIL. 21 entries, 출처 근거 주석 없음 |
| 엔트리 예시 | `Mageblood → The Apothecary stack=13`, `Headhunter → [The Doctor×8, The Fiend×11]` |
| 리스크 | 유니크 rebalance / stack 리밸런스 / 신규 유니크 카드 rotation 시 stale |
| 소비처 | `get_target_divcards()` → `StageData.target_cards` → `sections_continue.py:3998` 빌드 타겟 디비카 블록 |

### `wiki_data_provider.KNOWN_DIV_CARDS` (wiki_data_provider.py:68-74)

**🔴 Critical 2 — 중복 dict 발견**:

`UNIQUE_TO_DIVCARD`의 5개 엔트리(Death's Oath, Shavronne's, Headhunter, Mageblood, Aegis Aurora)만 복제. 나머지 16개 누락. `build_coach.py`가 소비.

**문제**:
- 단일 진실원(single source of truth) 부재
- `UNIQUE_TO_DIVCARD`에 추가해도 `KNOWN_DIV_CARDS` 업데이트 안 되면 coach는 stale 데이터로 응답
- 두 dict가 조용히 divergence

### `build_extractor.UNIQUE_TO_BASE` (build_extractor.py:106-129)

| 항목 | 결과 |
|------|------|
| 엔트리 수 | **22** (플랜 문서는 "26개"라 기재 — 플랜 기재 오류) |
| 커버리지 | POE1 유니크 ~1500개 대비 **1.5%** |
| 소비처 1 | `extract_build_unique_bases` POB 없을 때 fallback (line 199, 207, 218) |
| 소비처 2 | `get_chanceable_bases()` → L10 re_show chanceable block |
| 실용 리스크 | **실전 낮음** — 정상 POB에는 `base_type` 필드가 채워짐. 이 dict는 주로 `coaching_data.key_items`처럼 이름만 있는 케이스의 fallback |

**주요 유니크 중 누락 예시**: Lightpoise, Hyrri's Bite, Voidforge, Sign of the Sin Eater, Bottled Faith, Watcher's Eye (POB 필드로 커버되므로 실전 영향은 제한적)

## Critical 상세

### Critical 1: `hc_divcard_tiers.json` orphan 처리 결정 필요

현재 상태:
- β Continue 아키텍처에서 참조 없음
- `_analysis/gen_test_filter_v4.py` HCSSF 모드만 참조 (분석/테스트용 스크립트)
- HCSSF 모드 자체가 현재 활성 기능인지 불명

**결정 후보**:
- (A) HCSSF 모드 미사용 → 파일 및 analysis 스크립트 섹션 삭제
- (B) HCSSF 모드 유지 → `sections_continue.py`에 HCSSF 분기 추가 + `_meta` 완비 + 출처 명시
- (C) 보류 → current.md에 "orphan 상태" 명시, 나중 결정

**권고**: 사용자 확인 후 결정. 단순 삭제는 HCSSF 요구사항 재등장 시 손실.

### Critical 2: 디비카 하드코딩 dict 3곳 분산

현재:
- `build_extractor.UNIQUE_TO_DIVCARD` (21) — 필터 생성용
- `wiki_data_provider.KNOWN_DIV_CARDS` (5) — 코치/Wiki 조회용, 서브셋
- (잠재) `hc_divcard_tiers.json` — HCSSF 티어 데이터

**권고**: 단일 JSON 파일로 통합.
```
data/divcard_mapping.json
{
  "_meta": {
    "source": "poewiki.net Cargo:items + manual_curation",
    "version": "Phrecia 0.1",
    "collected_at": "2026-04-17",
    "script": "scripts/refresh_divcard_mapping.py"
  },
  "unique_to_cards": {
    "Mageblood": [{"card": "The Apothecary", "stack": 13}],
    ...
  }
}
```
`wiki_data_provider.KNOWN_DIV_CARDS`와 `UNIQUE_TO_DIVCARD` 둘 다 이 파일에서 로드.

### Critical 3: 재현 가능한 파이프라인 부재

- `hc_divcard_tiers.json`, `neversink_filter_rules.json`, `UNIQUE_TO_DIVCARD`, `UNIQUE_TO_BASE`, `KNOWN_DIV_CARDS` — 5개 데이터 소스 **전부 수동 관리**
- 리그 바뀔 때 전부 수동 업데이트해야 — 누락 확률 높음
- `wiki_data_provider.cargo_query` 인프라 존재 → 자동화 가능

**권고 스크립트**:
- `scripts/refresh_divcard_mapping.py` — Wiki Cargo `items` + `item_drops` 조인으로 유니크-카드-스택 자동 생성
- `scripts/refresh_unique_bases.py` — Wiki Cargo `items` 쿼리로 유니크 전체 → base_item 매핑
- `scripts/refresh_neversink_rules.py` — NeverSink GitHub release에서 최신 filter tier pull 후 JSON 변환

## 수정 권고 (별도 task로 분리)

### Task F1-fix-1: 디비카 단일 진실원 구축 (3h)

1. `data/divcard_mapping.json` 신규 (_meta 포함)
2. `UNIQUE_TO_DIVCARD`, `KNOWN_DIV_CARDS` 제거 → 파일 로드로 대체
3. `scripts/refresh_divcard_mapping.py` Wiki Cargo 기반
4. 테스트: 21개 엔트리 전수 검증

### Task F1-fix-2: `hc_divcard_tiers.json` orphan 결정 (0.5~1h)

사용자 확인 후 삭제 or 파이프라인 연결.

### Task F1-fix-3: `neversink_filter_rules.json` `_meta` 보강 (1h)

NeverSink upstream 버전 확인 → `_meta` 추가 + `scripts/refresh_neversink_rules.py`.

### Task F6-fix-1: `UNIQUE_TO_BASE` 파일화 + 자동 생성 (2h)

- `data/unique_to_base.json` (_meta 포함)
- `scripts/refresh_unique_bases.py` Wiki Cargo 또는 GGPK `UniqueItems.dat64`
- POE1 유니크 전수 커버 목표 (현재 1.5% → 95%+)

### Task F1-fix-4: 정기 재검증 cadence 문서화 (0.5h)

`docs/league_refresh.md` 신규 — 리그 시작 시 refresh 스크립트 실행 순서.

**총 예상: 7~8.5h** (플랜 예상 6~8h와 일치)

## DoD 통과 여부 요약

| 기준 | 결과 |
|------|------|
| D1 _meta 완비 | ❌ 3개 파일 모두 부재 |
| D2 신선도 | ⚠️ 버전 추적 불가 → 판단 보류 |
| D3 대조 샘플 | ⏸️ 수정 단계에서 refresh 스크립트로 자동 검증 |
| D4 하드코딩 + 출처 주석 | ❌ 3개 dict 모두 출처 주석 없음 |
| D5 생성 스크립트 | ❌ 전무 |
| D6 단위 테스트 | 🟡 부분 (`test_target_divcards_block` 있음) |
| D7 필터 출력 | ⏸️ Phase F 말미 |

**현 상태: 감사 통과 불가**. 위 4개 fix task 완료 후 재평가.

## 참조

- 플랜: `.claude/status/mechanic_data_audit_plan.md` (F1, F6 섹션)
- 선례: `_analysis/gem_weapon_restriction_audit.md` (F1 참고한 감사 패턴)
- Wiki Cargo 인프라: `python/wiki_data_provider.py::cargo_query`
