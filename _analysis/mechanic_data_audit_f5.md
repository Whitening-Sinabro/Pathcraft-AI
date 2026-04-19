# Phase F5 감사 리포트 — Syndicate (Jun Betrayal)

- 감사일: 2026-04-19
- 리그 앵커: 3.28 Mirage (Betrayal 3.5~ 이후 영구 메커닉)
- 감사 도메인: Syndicate 18 members + layouts + POB-based advisor + Vision 파이프라인
- 원칙: 감사만, 수정 X

## 감사 대상 매핑

| 파일 | 역할 | 코드 연결 |
|------|------|----------|
| `data/syndicate_members.json` | 18 member × division × rank 보상 | `syndicate_advisor._load_members` |
| `data/syndicate_layouts.json` | 5 프리셋 레이아웃 (SS22 / Aisling / Leo 등) | `syndicate_advisor._load_layouts` |
| `python/syndicate_advisor.py` | POB 빌드 → 레이아웃 추천 휴리스틱 (166 lines) | `SyndicateTutorial.tsx` |
| `python/syndicate_vision.py` | Claude Vision 스크린샷 → members/Rank 추출 (268 lines) | 별도 ingest 경로 |
| `src/utils/syndicateEngine.ts` | 액션 추천 엔진 (current → target) | `SyndicateTutorial` UI |

## D1-D7 체크리스트 결과

### D1 — `_meta` 필드 완비

| 파일 | 상태 | 필드 |
|------|------|------|
| `syndicate_members.json` | ✅ | description + divisions + ranks + **source="POE Wiki + 커뮤니티 가이드 (2024-2025)"** |
| `syndicate_layouts.json` | 🟡 | description + format + tip. **source/version/collected_at 없음** |

### D2 — 데이터 신선도

| 데이터 | 기준 리그 | 판정 |
|--------|-----------|------|
| Syndicate members 18명 | Betrayal 3.5 도입, 이후 리워크 최소 | ✅ Mirage 3.28에도 동일 구성 |
| Safehouse ranks (Member/Leader/Mastermind) | 3.5 이후 변동 없음 | ✅ |
| 5 프리셋 layouts | 커뮤니티 최적 루틴 (SS22, Aisling craft 등) | ✅ 현역 사용 |

**사실**: Betrayal 메커닉은 3.14~3.15 경미한 밸런스 조정 외 core 구조 변경 없음. 3.5~3.28 6년간 18 members + 4 divisions + 3 ranks 고정.

### D3 — GGPK 교차 대조

| 18 member | GGPK Mods.Name 포함 mod 수 |
|-----------|---------------------------|
| Aisling Laffrey | 2 ✅ |
| Cameria the Coldblooded | 2 ✅ |
| Catarina Neus (Mastermind) | 33 ✅ |
| Elreon | 7 ✅ |
| Gravicius | 4 ✅ |
| Guff 'Tiny' Grenn | 1 ✅ |
| Haku | 3 ✅ |
| Hillock | 2 ✅ |
| It That Fled | 1 ✅ |
| Janus Perandus | 2 ✅ |
| Jorgin the Banished | 2 ✅ |
| Korell Goya | 3 ✅ |
| Leo Redmane | 4 ✅ |
| Riker Maloney | 2 ✅ |
| Rin Yuushu | 6 ✅ |
| Tora | 5 ✅ |
| Vagan | 3 ✅ |
| Vorici | 3 ✅ |

**18/18 canonical** — GGPK Veiled mod Name에 각 member 이름 1+ rows 존재.

### D4 — 하드코딩 dict + 출처 주석

| 위치 | 상태 |
|------|------|
| `syndicate_advisor._detect_build_needs` 휴리스틱 점수 (line 27~) | ✅ 주석 "기본값 — 모든 빌드가 웬만큼 필요". 설계 근거 명확 |
| `syndicate_advisor._match_layout` 가중치 | ✅ 휴리스틱이므로 데이터 stale 위험 없음 |

Betrayal 메커니즘이 stable하고 advisor는 데이터가 아닌 로직이므로 하드코딩 D4 위반 없음.

### D5 — 자동 재현 스크립트

| 데이터 | 생성 방법 |
|--------|-----------|
| `syndicate_members.json` | ❌ 없음. POE Wiki + 가이드 참조 수동 작성 |
| `syndicate_layouts.json` | ❌ 없음. 커뮤니티 SS22 등 검증된 루틴 수동 |

**판단**: Betrayal 6년 stable 구조. 자동 재생성 파이프라인 구축 비용 > 편익. **수동 유지 정당**.

### D6 — 단위 테스트

| 영역 | 테스트 |
|------|--------|
| `syndicate_advisor` | ✅ `test_syndicate_advisor.py` 통과 |
| `syndicate_vision` | ✅ `test_syndicate_vision.py` 통과 |
| 합산 | **28/28 PASS** (2026-04-19 재실행 확인) |

### D7 — 필터 출력 통합 검증

**해당 없음** — Syndicate는 POE 아이템 필터 레이어가 아니라 POB 빌드 기반 advisor + Vision 파이프라인. 필터 출력 assert 적용 대상 아님.

## 발견 및 위험도

### 🟢 통과
- 18 members GGPK 교차 검증 100%
- 28 pytest PASS
- Betrayal 메커니즘 3.5 이후 6년 stable — stale 위험 최소
- `syndicate_members.json` _meta에 source 명시

### 🟡 LOW 리스크
1. **`syndicate_layouts.json` _meta에 source/version 없음**
   - 사실: description + format + tip만 존재. 원 출처 (어느 커뮤니티 가이드? SS22 출처 URL?) 불명
   - 영향: 실무 영향 미미 (레이아웃 자체는 검증됨). 참조 추적만 어려움
   - 권고 (F5-fix-1, 15min): `_meta.source = "SS22 community consensus + crafting guides"` + 참조 URL 1~2개 추가

### 🟢 적극 권고 없음
- Mechanic stable → 재추출 스크립트 불필요
- GGPK 18/18 매치 → 내용 수정 불필요

## F5 총괄 판정

**✅ PASS (하위 권고 1건)**

**근거**:
- 플랜의 "🟢 LOW — 기존 검증" 예상대로 건전 상태 확인
- D1/D2/D3/D4/D6 통과, D5는 합리적 예외, D7은 해당 없음
- Betrayal 안정성 + 테스트 커버리지 + GGPK 100% 교차 검증

**Fix 태스크 (backlog 등록)**:
- **F5-fix-1 (🟡, 15min)**: `syndicate_layouts.json` `_meta.source` + 참조 URL 추가

## 참조

- syndicate_members 출처: POE Wiki Jun Ortoi 시리즈 페이지
- 선례: `project_mechanic_data_audit_required.md` (F5는 LOW 분류된 도메인)
