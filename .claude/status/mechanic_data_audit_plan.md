# 메커닉 데이터 감사 플랜 (Phase F)

> 2026-04-16 착수 사유: weapon/skill gem 감사에서 GGPK ActiveSkills.WeaponRestriction이
> 실게임과 다름을 발견 (Sunder Axe 누락 등). 같은 리스크가 다른 메커닉 도메인에도
> 있을 것. 사용자 요구: "디비전 카드, 브리치, 레기온 등 관련된 것들 다
> 더블/트리플 체크".

## 원칙

1. **데이터는 출처 메타데이터 없으면 신뢰 불가** — `_meta.source` + `_meta.version` + `_meta.collected_at`이 없으면 감사 대상
2. **코드 하드코딩 dict는 기본 의심** — 패치로 변경되는 게임 데이터를 하드코딩하면 stale 리스크
3. **Ground truth 3순위**:
   1. GGPK 추출본 (현재 클라이언트, 단 ActiveSkills처럼 부정확한 필드 있음)
   2. POB Community 소스 (Lua 데이터, 빌드 툴 기준)
   3. POE Wiki Cargo API (커뮤니티 관리, 버전 명시)
4. **리그 시작 직후 + 월 1회 재검증** 기본 cadence

## 공통 체크리스트 (각 도메인 공통 적용)

| # | 항목 | 합격 기준 |
|---|------|-----------|
| D1 | 데이터 파일 `_meta` 필드 | `source`, `version`, `collected_at` 중 최소 2개 |
| D2 | 파일 신선도 | 현재 POE 리그 기준 ±1 리그 이내 데이터 |
| D3 | GGPK/POB/Wiki 대조 샘플 | 10개 무작위 entry 실 게임과 일치 확인 |
| D4 | 하드코딩 dict 존재 여부 | 소스 파일 grep. 있으면 출처 근거 주석 필수 |
| D5 | 생성 스크립트 유무 | 재현 가능한 파이프라인 (수동 dict이라도 출처 문서화) |
| D6 | 단위 테스트 | 최소 스모크 1건 (데이터 존재 + 필수 키) |
| D7 | 필터 출력 검증 | 해당 도메인 샘플 3개(unique/base/currency 각 1)를 build_data fixture에 inject → `filter_generator` 출력 문자열에 `assert '<sample_name>' in overlay` 최소 3건. `test_sections_continue.py` 기존 스모크 패턴 따름 |

통과: **D1-D7 전부** (D7만 필터 통합 후 가능, Phase 말미에 확인)

## 진행 권고 순서

**1순위 (병합 감사):** F1 Divcard + F6 Unique/Chanceable base — 둘 다 `build_extractor.py`
모듈에 하드코딩 dict 있음. 함께 감사하면 효율. 예상 6~8h.

**2순위:** F2 Breach/Legion/Scarab/Incursion/Expedition — GGPK BaseItemTypes 태그 자동 추출로
4 Phase 일괄 처리 가능.

**3순위:** F3 기타 메커닉 (Ultimatum/Blight/Delve 등), F4 Sanavi, F5 Syndicate, F7 Mod — 독립 병렬.

## 우선순위 Phase

### F1: Divination Card (🔴 HIGH)

**대상:**
- `data/hc_divcard_tiers.json` — `_meta: {}` **비어있음**
- `python/build_extractor.py` — `UNIQUE_TO_DIVCARD` 하드코딩 dict (Death's Oath, Mageblood 등 ~20개 매핑)
- `get_target_divcards()` / `get_chanceable_bases()` 함수
- `sections_continue.py` — L8 divination card 블록

**구체 위험:**
- 하드코딩 유니크-카드 매핑이 POE 리그별로 변경됨 (카드 rotation, 유니크 rebalance)
- `hc_divcard_tiers.json` 출처 불명 — 리그 중 경제 기준인지 SSF 기준인지 모름

**해결 방향:**
- POE Wiki Cargo API `divination_cards` 테이블 → 자동 추출 스크립트
- 또는 poedb.tw 스크래핑 (정기)
- `UNIQUE_TO_DIVCARD` 하드코딩 제거 → 동적 로드

**예상: 4~6h**

### F2: Breach / Legion / Scarab / Incursion / Expedition (🟡 MID)

**대상:**
- GGPK `BaseItemTypes` (splinter, scarab, lifeforce 등은 GGPK가 truth)
- `sections_continue.py` — 각 메커닉별 Show 블록 (L8)
- Category 하드코딩 리스트 (scarab 종류, breachstone 등급 등)

**구체 위험:**
- 새 scarab/splinter 추가 시 필터에서 누락
- Breachstone 등급 변화 (Uber Breach 등)

**해결 방향:**
- GGPK `BaseItemTypes`에서 태그별 자동 추출 (`Breach`, `Legion`, `Scarab` 태그)
- 자동 추출 스크립트 → `data/category_items.json` 같은 단일 테이블

**예상: 3~4h**

### F3: Ultimatum / Blight / Delve / Heist / Ritual / Essence / Metamorph / Beyond (🟡 MID)

**대상:**
- 각 메커닉의 currency, consumable, splinter
- `data/farming_mechanics.json`, `data/farming_strategies.json`
- `python/farming_strategy_system.py`

**구체 위험:**
- `farming_mechanics.json` / `farming_strategies.json`의 `_meta` 미확인
- 메커닉별 currency 아이콘/이름 stale 가능

**예상: 3~5h (도메인당 30분)**

### F4: Sanavi 티어 데이터 (🟡 MID)

**대상:**
- `data/sanavi_tier_data.json` (32 카테고리)
- `python/sanavi_tier_parser.py`
- 섹션 `t1high`, `t1`, `t2high`, `t2`, `t3high`, `t3` 등 분류

**구체 위험:**
- Sanavi 필터 버전 업데이트 시 stale
- 버전 추적 없음 (`_meta` 부재 가능)

**예상: 2h**

### F5: Syndicate (🟢 LOW — 기존 검증)

**대상:**
- `data/syndicate_{layouts,members}.json`
- `python/syndicate_advisor.py`, `syndicate_vision.py`

**기존 상황:** Claude Vision으로 인게임 스크린샷 검증 파이프라인 있음 (`syndicate_vision.py`).

**추가 필요:** `_meta` 정합성 + Vision 정확도 샘플링

**예상: 1h**

### F6: Unique 아이템 & Chanceable base (🔴 HIGH — F1과 함께 진행 권고)

**대상:**
- `python/build_extractor.py` — `UNIQUE_TO_BASE` 하드코딩 26 entries
- `get_chanceable_bases()` 의존
- L10 re_show 블록의 chanceable base 의존

**구체 위험:**
- 유니크 rebalance / 신규 유니크 추가 시 하드코딩 miss
- `UNIQUE_TO_BASE`가 현재 26개만 — POE1 유니크 전체 ~1500개 대비 미미. 나머지는 POB `gear_recommendation`의 `base_type` 필드에 의존
- 누락 시 L10 re_show에 chanceable base 미포함 → 빌드 유니크 체이싱 실패

**해결 방향:**
- POE Wiki Cargo `items` 테이블 또는 GGPK `Unique*.json` 전수 매핑
- **F1과 같은 `build_extractor.py` 모듈이라 병합 감사 효율적** — F1 실행 시 함께 처리 권고

**예상: 3~4h (F1과 합치면 6~8h)**

### F7: 마스터 크래프팅 / Veiled mod / Exalted influence (🟢 LOW)

**대상:**
- `data/mod_pool.json`, `data/id_mod_filtering.json`
- mod 이름 기반 필터링 (HasExplicitMod)

**예상: 2h**

## DoD (Phase F 전체)

1. 각 Phase 완료 시 해당 데이터 파일에 `_meta` 필드 완비 (D1 통과)
2. 발견된 하드코딩 dict 5개 이상 → 자동 로드 체계로 전환 (D4 통과)
3. 각 도메인 최소 1개 자동 추출 스크립트 존재 (D5 통과)
4. 리그 업데이트 체크리스트 `docs/league_refresh.md` 작성
5. 필터 출력 회귀 테스트: 각 도메인 샘플 아이템이 L8 블록에 포함되는지 1 assert
6. 발견된 부정확/stale 데이터는 **이슈 리포트** (`_analysis/mechanic_data_audit_{domain}.md`)

## 실행 규칙

- 한 Phase 완료 전까지 다음 Phase 착수 금지 ("1~2개씩 구현→확인" 규칙)
- 발견된 큰 부정확성은 즉시 memory entry로 박제 (무기 감사 때 `project_weapon_filter_ground_truth.md`처럼)
- 각 Phase 커밋 분리: `chore: Phase F{N} 감사 — {domain}`
- 감사만 하고 수정 안 할 것 (단순 스코프 폭증 방지). 수정 필요 항목은 별도 task

## 후속 TODO (이번 플랜 범위 외)

- **리그 시작 자동 감지** — `python/patch_note_scraper.py`가 새 POE 리그 버전 감지 시
  `current.md`에 "Phase F 재감사 필요" 자동 append. 수동 재검증 누락 방지. 별도 task로 backlog 등록

## 진행 로그 (발견 사항 기록)

### F1 + F6 — 감사 완료 (2026-04-17)

리포트: `_analysis/mechanic_data_audit_divcard_unique.md`

주요 발견:
1. **`hc_divcard_tiers.json` orphan** — β Continue 파이프라인에서 미사용, `_analysis/gen_test_filter_v4.py` HCSSF 모드만 소비. 삭제 or 연결 결정 필요
2. **디비카 하드코딩 3곳 분산 + 중복** — `build_extractor.UNIQUE_TO_DIVCARD`(21) + `wiki_data_provider.KNOWN_DIV_CARDS`(5 서브셋) + `hc_divcard_tiers.json`. 단일 진실원 부재
3. **`neversink_filter_rules.json` `_meta` 부재** — 런타임 실사용 파일인데 버전 추적 불가
4. **`UNIQUE_TO_BASE` 22개** — 플랜 "26개" 기재 오류. POE1 ~1500 유니크 대비 1.5%이나 POB 필드로 대부분 커버 (실전 영향 제한적)
5. **재현 가능한 생성 스크립트 전무** — 5개 데이터 소스 전부 수동 관리
6. **Wiki Cargo 인프라 이미 존재** (`wiki_data_provider.cargo_query`) — 자동화 가능

DoD: **감사 통과 불가** (D1/D4/D5 모두 FAIL). 수정 4 task 분리 등록.

Fix 태스크 진행 현황:
- ✅ F1-fix-1 Step A (2026-04-17): `data/divcard_mapping.json` + `divcard_data.py` 로더 + 2 소비처 마이그 + 5 테스트
- ✅ F1-fix-1/F6 Step B (2026-04-17): `scripts/refresh_unique_base_mapping.py` (642 엔트리 자동 생성) + `scripts/validate_divcard_mapping.py` (Wiki 대조). Cargo API 제약(`stack_size` 미정의)으로 divcard는 validate만 자동, generate는 수동
- ✅ divcard 6건 stale 정정 (2026-04-17): 16 엔트리 100% Wiki 정합. 5 제거(Aegis Aurora/Badge of the Brotherhood/Inpulsa's/Cospri's Malice/Hyrri's Ire) + 1 오타
- ✅ F1-fix-3 (2026-04-17): `neversink_filter_rules.json` `_meta` (NeverSink 8.19.2a.2026.102.11 출처)
- ✅ F6-fix-1 Step A (2026-04-17): `data/unique_base_mapping.json` + `unique_base_data.py` + build_extractor 마이그 + 6 테스트
- [ ] F1-fix-2 (B안 확정): HCSSF 파이프라인 — `hc_divcard_tiers.json` `_meta` + refresh + β Continue 분기 (4~6h, 다음 세션)
- [ ] F1-fix-4: `docs/league_refresh.md` (0.5h)

회귀: pytest 425 → **436 PASS** (신규 11 케이스)

### F0 — GGPK 추출 완전성 감사 (2026-04-17)

리포트: `_analysis/ggpk_extraction_completeness_audit.md`

**발단**: 사용자 지적 — "GGPK 모든 데이터를 가져온다고 했는데 체크리스트 없이 '이정도면 됐지' 하고 끝났을 가능성". 확인 결과 **사실**.

**핵심 발견**:
1. 체크리스트 근거 = `poe-tool-dev/dat-schema` (`data/schema/schema.min.json`, v7, 이미 repo 로드됨)
2. POE1 applicable 테이블 **921개** vs 현재 `extract_data.rs` TARGETS **7개** → **커버리지 0.76%**
3. `Tags` 테이블 부재로 `load_ggpk_items`가 Name 패턴 매칭 휴리스틱 의존 (🔴)
4. `Mods` 테이블 부재로 NeverSink mod 이름 검증 완전 불가 (🔴)
5. `Characters/Ascendancy` 부재로 클래스 정보 수동 관리 (🟡)

**Fix 태스크 분리**:
- F0-fix-1: `extract_data.rs` TARGETS 확장 (Tier 1: Tags/Mods/ModType/ModFamily/Characters/Ascendancy + Tier 2: GemTags/ArmourTypes/Scarabs/ScarabTypes/Essences/Flasks). 30~45min (Rust build 별도)
- F0-fix-2: `load_ggpk_items` 태그 기반 재작성 (F0-fix-1 후). 1.5h
- F0-fix-3: `validate_mod_names.py` mod 이름 GGPK 대조 스크립트. 1h

**Phase F2~F7 전제 재정의**: F0-fix-1 완료 후 각 도메인 필요 테이블 확보됨 → 그때 감사 착수.

**Phase F1 재평가**: DivinationCards 테이블 schema에 없음 → Wiki Cargo 의존 전략 유효 유지.

**Phase D 재평가**: ArmourTypes 추출 후 BaseItemTypes.Id 휴리스틱 업그레이드 가능 (현재 동작 OK이지만 정확도 향상).

### F2~F7 — F0-fix-1 후 착수 대기

## 참조

- Phase B+C 무기 감사 선례: `_analysis/gem_weapon_restriction_audit.md`
- 메모리: `C:\Users\User\.claude\projects\D--Pathcraft-AI\memory\project_weapon_filter_ground_truth.md`
- Ground truth 원칙: `C:\Users\User\.claude\projects\D--Pathcraft-AI\memory\project_mechanic_data_audit_required.md` (이번 Phase 등록)
