# Phase F7 감사 리포트 — 크래프팅 / Veiled / Influence mods

- 감사일: 2026-04-19
- 리그 앵커: 3.28 Mirage (truth reference)
- 감사 도메인: master craft, essence, Veiled, Influence (Shaper/Elder/Conq/Elevated), fossils, t1 base whitelist
- 원칙: 감사만, 수정 X

## 감사 대상 매핑

| 파일 | 역할 | 코드 연결 |
|------|------|----------|
| `data/mod_pool.json` | Wiki 스크래핑 695 mod 사전 (3.25) | ⚠️ **ORPHAN** (코드 미사용, 플랜 문서에만) |
| `data/id_mod_filtering.json` | NeverSink ID Mod 112 블록 394 mod | `sections_continue.layer_id_mod_filtering` |
| `data/t1_craft_bases.json` | T1 craft 가치 base 화이트리스트 | `sections_continue.load_t1_bases` |
| `data/defense_mod_tiers.json` | NeverSink 방어 5 slots × life/es | `layer_defense_proxy` (F0-fix-3 완료) |
| `data/accessory_mod_tiers.json` | NeverSink 악세 3 slots × axes | `layer_accessory_proxy` (F0-fix-3 완료) |
| `data/weapon_mod_tiers.json` | NeverSink 무기 mod | `layer_weapon_phys_proxy` (F0-fix-3 완료) |
| `data/game_data/Mods.json` | GGPK 전체 mod (5206 distinct Name, 39291 rows) | 직접 소비 없음 (F0-fix-3 검증 용) |

## D1-D7 체크리스트 결과

### D1 — `_meta` 필드 완비

| 파일 | 상태 | 누락 필드 |
|------|------|----------|
| `mod_pool.json` | ⚠️ | `_meta` 키 없음. top-level에 `version: "3.25"`, `source: "poewiki.net"`만 |
| `id_mod_filtering.json` | 🔴 | description, total_blocks, total_unique_mods만. **source/version/collected_at 전부 없음** |
| `t1_craft_bases.json` | 🟡 | description, source, ilvl_threshold, influence_types. **version/collected_at 없음** |
| `defense/accessory/weapon_mod_tiers.json` | ✅ | F1+F6 fix에서 정비 완료 |

### D2 — 데이터 신선도 (현 리그 ±1)

| 파일 | 버전 | 판정 |
|------|------|------|
| `mod_pool.json` | **3.25** | 🔴 **3 리그 전** (3.25 → 3.26 → 3.27 → 3.28 Mirage) |
| `id_mod_filtering.json` | 미기록 | 🟡 판정 불가, 추정 NeverSink 8.19.x |
| `t1_craft_bases.json` | 미기록 | 🟡 판정 불가 |
| `data/game_data/*.json` | 3.28.0.8 | ✅ 현 리그 최신 |

### D3 — GGPK 교차 대조

| 데이터 | 대조 결과 |
|--------|----------|
| `mod_pool.json` 695 entries | exact 511 (73.5%) / 포맷차이로 미매치 184 (Wiki-style Ids, e.g. `FireDamagePercentage`) |
| `id_mod_filtering.json` 394 distinct | exact **391 (99.2%)** / 3 substring (Veil/Tacati/Elevated  — F0-fix-3 확인) |
| `defense/accessory/weapon_mod_tiers.json` 326 entries | **326/326 resolve** (F0-fix-3 PASS) |
| `mod_pool` veiled 카테고리 20 | GGPK Veiled 16 row — 4 리그별 변동 의심 (3.25→3.28) |

### D4 — 하드코딩 + 출처 주석

| 위치 | 상태 |
|------|------|
| `sections_continue.py:1322` `_CORRUPT_ESSENCE_NAMES` (5 items) | ✅ 주석 "T0 부패 에센스" |
| `sections_continue.py:1344` `HIGH_FOSSILS` (12 items) | ❌ 출처/버전 주석 없음 |
| `sections_continue.py:1374-1378` `OILS_TOP/HIGH/MID/LOW/PREMIUM` | ❌ 출처/버전 주석 없음 |
| `sections_continue.py:1431` `LOW_LIFE_SUFFIX_MODS` ("Hale", "Healthy", "Sanguine") | ✅ Cobalt uberStrict convention 주석 |

### D5 — 자동 재현 스크립트

| 파일 | 생성 방법 |
|------|-----------|
| `mod_pool.json` | ❌ 없음. 수동 Wiki 스크래핑 (3.25) |
| `id_mod_filtering.json` | ❌ 생성 스크립트 없음. NeverSink `[[0600]/[0700]/[0800]]` 수동 파싱 |
| `t1_craft_bases.json` | ❌ 수동. 커뮤니티 가이드 기반 |
| `defense/accessory/weapon_mod_tiers.json` | ✅ `scripts/extract_*_mod_tiers.py` (F1-fix에서 자동화) |

### D6 — 단위 테스트

| 항목 | 테스트 |
|------|--------|
| `load_t1_bases` 로딩 | 기존 테스트 있음 |
| `layer_id_mod_filtering` 출력 | 있음 |
| `mod_pool.json` | ❌ 사용처 없어 테스트도 없음 |
| Mods 교차 검증 | F0-fix-3 `test_validate_mod_names.py` (3 parametrized) |

### D7 — 필터 출력 검증

| 항목 | 상태 |
|------|------|
| id_mod filter → NeverSink top-mod rare show 블록 생성 | 기존 `TestLayerIdModFiltering` 있음 |
| t1 craft base border → LAYER_T1_BORDER 출력 | 기존 테스트 있음 |
| mod_pool 출력 | ❌ 소비처 없음 |

## 발견 및 위험도

### 🔴 HIGH

1. **`mod_pool.json` ORPHAN + 3.25 stale**
   - **사실** (2026-04-19 재검증): `grep -rn "mod_pool\|all_mods"` `**/*.{py,ts,tsx,js,jsx,rs}` → **모두 0건**. 문서 3건(current/plan/본 리포트)만 히트. 코드 사용처 0 확정.
   - **사실**: version 3.25 (3.28 Mirage 기준 3 리그 전)
   - 위험: 정비 안 된 데이터 파일 누적 → 혼란 + 부정확한 의사결정
   - 권고: **삭제** (F6-fix-1에서 unique_base_mapping이 실질 대체 + t1_craft_bases가 craft 커버)
   - 또는 Wiki Cargo에서 자동 재생성 파이프라인 구축 (F7-fix-A 별도 task)

2. **`id_mod_filtering.json` source/version/collected_at 전부 없음**
   - 사실: 런타임 실제 사용되는 데이터인데 어떤 NeverSink 버전에서 뽑았는지 불명
   - 위험: NeverSink 8.19.x 업데이트 시 탐지 불가. 재추출 기준 부재
   - 권고: `_meta.source = "NeverSink {version} {filter-strictness}"` + `collected_at` + 재추출 스크립트 추가 (F7-fix-B)

### 🟡 MID

3. **`t1_craft_bases.json` version/collected_at 없음**
   - 출처는 "커뮤니티 크래프팅 가이드"로 모호. 특정 가이드/리그 snapshot 불명
   - 권고: 참조 가이드 URL + snapshot 날짜 기록 (F7-fix-C, 15min)

4. **`mod_pool.json` veiled 20 vs GGPK 16 Name-level**
   - **불확실**: mod_pool veiled 20은 Wiki Cargo Id 포맷("Catarina's", "Vorici's" 등), GGPK 16은 Mods.Name 포맷. 4 차이가 실제 리그 변동인지 포맷 차이인지 불명
   - **검증 방법**: mod_pool veiled 20 keys → Wiki Cargo `mods` 테이블에서 실제 Name 조회 → GGPK Mods.Name과 매핑 대조. 현재 미실행
   - 해당 파일이 orphan이라 실영향 없음 — #1에서 처리하면 자동 해소

5. **HIGH_FOSSILS / OILS_TOP/HIGH/MID/LOW/PREMIUM 출처 주석 없음**
   - Wreckers SSF 레퍼런스 티어링이나 주석 없어 확인 불가
   - 권고: 주석 추가 (F7-fix-D, 10min)

### 🟢 LOW

6. **`defense/accessory/weapon_mod_tiers.json` 326/326 GGPK resolve**
   - F0-fix-3에서 이미 검증. F7 감사 범위 내에서 추가 조치 불필요.

## F7 총괄 판정

**⚠️ CONDITIONAL (HIGH 2건 존재)**

**근거**:
- GGPK 활용 가능한 데이터 소스는 대부분 건전 (id_mod 99.2%, tier files 100%)
- 그러나 `mod_pool.json` orphan + 3 리그 stale은 명확한 부채
- `id_mod_filtering.json` 버전 추적 부재는 리그 업데이트 팔로우업 원천 차단

**Fix 태스크 (우선순위순, 별도 task)**:

| ID | 작업 | 시간 | 우선 |
|----|------|------|------|
| F7-fix-1 | `mod_pool.json` orphan 처리 (삭제 or Wiki Cargo 자동 재생성) | 0.5h or 2h | 🔴 HIGH |
| F7-fix-2 | `id_mod_filtering.json` `_meta` 완비 + 재추출 스크립트 | 1h | 🔴 HIGH |
| F7-fix-3 | `t1_craft_bases.json` _meta 보강 (version/collected_at/ref_url) | 15min | 🟡 MID |
| F7-fix-4 | `HIGH_FOSSILS` / `OILS_*` 주석 보강 | 10min | 🟡 MID |

## 참조

- Mods.json 감사 기반: `python/scripts/validate_mod_names.py` (F0-fix-3)
- Truth reference: `_analysis/ggpk_truth_reference.json`
- F1+F6 mod-tier 정비 선례: `_analysis/mechanic_data_audit_divcard_unique.md`
