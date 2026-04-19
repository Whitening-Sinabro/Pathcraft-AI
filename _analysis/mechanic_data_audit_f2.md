# Phase F2 감사 리포트 — Breach / Legion / Scarab / Incursion / Expedition

- 감사일: 2026-04-18
- 리그 앵커: 3.28 Mirage (truth reference anchored_at 2026-04-17)
- 감사 도메인: Breach, Legion, Scarab, Incursion, Expedition, (보조) Harvest/Lifeforce
- 원칙: 감사만, 수정 X (수정은 별도 task)

## 감사 대상 매핑

| 도메인 | 필터 출력 함수 | 데이터 소스 | 하드코딩 여부 |
|--------|----------------|-------------|--------------|
| Breach (splinter) | `layer_splinters` → `d.splinter_breach` | GGPK (`breachstone_splinter` 태그) | ❌ |
| Breach (Wombgifts) | `generate_beta_overlay` line 2330 | `Class "Wombgifts"` (게임 native) | ❌ (class 기반) |
| Legion (splinter) | `layer_splinters` → `d.splinter_legion` | GGPK (`legion_splinter` 태그) | ❌ |
| Scarab (전체) | `layer_scarabs` → `d.scarabs_all` | GGPK (`scarab` 태그) | ❌ |
| Scarab (고가) | `layer_scarabs` → `d.scarabs_special` | GGPK (`uber/uniques/influence_scarab` ∪ Name prefix) | ❌ (F0-fix-2 후) |
| Incursion | `layer_endgame_content` line 2583 | `Chronicle of Atzoatl` 단일 | ✅ 1 item |
| Expedition (Logbook) | `layer_endgame_content` line 2513 | `Expedition Logbook` | ✅ 1 item |
| Expedition (Exceptional) | `layer_stacked_currency` line 2892 | `_EXCEPTIONAL` 6 items | ✅ 6 items |
| Expedition (Artifacts 일반) | 기타 Artifact/Ember/Ichor | GGPK (tag 검증 대상) | 미확인 |
| Harbinger (Unique Fragments) | `layer_stacked_currency` line 2911 | `_UNIQUE_FRAGMENTS` 8 items | ✅ 8 items |
| Harvest (Lifeforce) | `layer_lifeforce` → `d.lifeforce` | GGPK (Id prefix `HarvestSeed`) | ❌ |

## D1-D7 체크리스트 결과

### D1 — `_meta` 필드 완비

| 파일 | 상태 | 비고 |
|------|------|------|
| `data/game_data/*.json` (F0 산출) | ✅ | `_analysis/ggpk_truth_reference.json`에서 `anchored_to`로 통합 관리 |
| 하드코딩 블록 (sections_continue.py) | ❌ | 4개 블록 주석은 있으나 `source:` 메타 없음 |

### D2 — 데이터 신선도 (현 리그 ±1)

| 데이터 | 리그 | 상태 |
|--------|------|------|
| GGPK 추출 (`data/game_data/`) | 3.28 Mirage | ✅ 현 리그 |
| `_EXCEPTIONAL` 6 items | Expedition 3.16~ 영구 (변동 없음) | ✅ |
| `_UNIQUE_FRAGMENTS` 8 items | Harbinger 3.1~ 영구 (변동 없음) | ✅ |
| `Chronicle of Atzoatl` | Incursion 3.7~ 영구 (변동 없음) | ✅ |

### D3 — GGPK/POB/Wiki 대조

**Count 기반 대조:**

| 항목 | 대조 결과 |
|------|----------|
| Wombgifts 5종 | GGPK: 5/5 (Provisioning/Lavish/Ancient/Growing/Mysterious) ✅ |
| Exceptional 6종 | GGPK: 6/6 (Black Scythe/Broken Circle/Ember/Ichor/Order/Sun Artifact) ✅ |
| Chronicle of Atzoatl | GGPK: 1/1 ✅ |
| Harbinger fragments 8종 | GGPK: 8/8 (multi-variant rows, 전부 존재) ✅ |
| splinter_breach 5 / splinter_legion 5 | F0-fix-2 Wiki triple-check 통과 ✅ |
| scarabs_all 190 / scarabs_special 14 | 독립 추출기(pathofexile-dat) 교차 검증 일치 ✅ |

**무작위 10 샘플 (scarabs, seed=42):**
```
Blight Scarab                        Polished Shaper Scarab
Gilded Bestiary Scarab               Divination Scarab of The Cloister
Breach Scarab of Instability         Horned Scarab of Glittering
Horned Scarab of Pandemonium         Rusted Bestiary Scarab
Gilded Ambush Scarab                 Gilded Torment Scarab
```
전부 PoE Wiki `Scarab` 카테고리에 존재하는 canonical 이름 — 사실 확인.

**Breach splinter 전수 (5):** Xoph / Tul / Esh / Uul-Netol / Chayula — Breach 5 영주 정확 ✅
**Legion splinter 전수 (5):** Karui / Maraketh / Eternal Empire / Templar / Vaal — Legion 5 군단 정확 ✅

### D4 — 하드코딩 dict 출처 주석

| 블록 | 출처 주석 상태 |
|------|----------------|
| `_EXCEPTIONAL` (line 2892) | 주석 1줄 "Expedition 최고 티어". ❌ 출처/버전 없음 |
| `_UNIQUE_FRAGMENTS` (line 2911) | 주석 "Harbinger shards (5 shards per unique) + 특수". ❌ 출처 없음 |
| Chronicle of Atzoatl (line 2583) | 주석 "(Cobalt L6710) — Incursion 최종". ✅ Cobalt 라인 번호 근거 |
| Wombgifts 블록 (line 2332) | 주석 "Breach 특수 아이템 (5종)". ❌ 출처 없음 |

### D5 — 자동 재현 스크립트

| 도메인 | 재현 방법 |
|--------|-----------|
| Breach/Legion/Scarab/Lifeforce | `cargo run --bin extract_data -- --json` → `load_ggpk_items` 자동 |
| Wombgifts | `Class "Wombgifts"`로 게임 엔진이 자동 — 코드 재현 불필요 |
| Exceptional/Unique Fragments | ❌ 수동 리스트. 자동 추출 스크립트 없음 |
| Chronicle of Atzoatl | 단일 base, 자동화 불필요 |

### D6 — 단위 테스트

| 항목 | 테스트 |
|------|--------|
| `load_ggpk_items` 결과 | `TestLoadGGPKItems::test_load_extracts_nonempty` + `test_snapshot_tag_based_classification` ✅ |
| `layer_splinters` 출력 | `TestLayerSplinters::test_generates_all_three_subcategories` ✅ |
| `layer_scarabs` 출력 | `TestLayerScarabs::test_generates_special_and_regular` ✅ |
| `layer_endgame_content` | ❌ 전용 스모크 없음 (Chronicle/Exceptional/Harbinger 포함 여부 검증 부재) |
| `_EXCEPTIONAL` 존재 여부 | ❌ |
| `_UNIQUE_FRAGMENTS` 존재 여부 | ❌ |

### D7 — 필터 출력 통합 검증

| 도메인 | 현 커버 | 제안 |
|--------|---------|------|
| Scarab special | `layer_scarabs` 테스트에 `"Horned "` 포함 검증 있음 | OK |
| Breach/Legion splinter | `layer_splinters`에 `"[L8|splinter_breach_s80]"` 확인 | OK |
| Expedition Exceptional | 없음 | `"Exceptional Black Scythe Artifact" in output` 추가 권장 |
| Chronicle of Atzoatl | 없음 | `"Chronicle of Atzoatl" in output` 추가 권장 |

## 발견 및 위험도

### 🟢 통과 (감사 OK)
- **Breach/Legion/Scarab/Lifeforce** — GGPK 태그 기반 + truth reference content_hash + Wiki triple-check + 독립 추출기 교차 검증. 다층 검증 완료.
- **Chronicle of Atzoatl** — 단일 base, Incursion 3.7 이후 영구.

### 🟡 LOW 리스크
1. **Expedition `_EXCEPTIONAL` 6 항목 하드코딩** — GGPK 존재 확인 완료. 신규 Exceptional 변종 추가 시 누락 리스크. 역사적으로 Expedition(3.16) 이후 확장 없음 → low.
2. **Harbinger `_UNIQUE_FRAGMENTS` 8 항목 하드코딩** — 동일. Harbinger 3.1 이후 변동 없음.
3. **Wombgifts 블록 출처 주석 없음** — 동작은 `Class "Wombgifts"` 기반이라 GGPK 변경에 자동 추종. 주석 추가만 필요.

### 🔴 HIGH 리스크
- **없음** (F2 도메인 내에서).

## F2 총괄 판정

**✅ PASS (하위 권고 있음)**

**근거**:
- 주력 데이터(splinter/scarab/lifeforce) GGPK 기반 + truth reference 5계층 검증 + 독립 추출기 교차 일치
- 하드코딩 4개 블록 전부 GGPK 존재 확인, 모두 stable content (3.7/3.16/3.1 이후 변동 없음)
- 기존 pytest 스모크 핵심 경로 커버

**권고 (별도 task)**:
- **F2-fix-1 (30min, nice-to-have)**: `_EXCEPTIONAL` / `_UNIQUE_FRAGMENTS` 출처 주석 추가 (예: "Expedition 3.16 이후 영구, Wiki:Exceptional_Currency 2026-04-18 확인")
- **F2-fix-2 (15min, low priority)**: `layer_endgame_content` / `layer_stacked_currency` 스모크 테스트 추가 (Chronicle/Exceptional/Harbinger BaseType 포함 확인)

## 참조

- Truth reference: `_analysis/ggpk_truth_reference.json`
- F0-fix-2 태그 전환: `python/sections_continue.py:1246+`
- 독립 추출기 교차검증: `_analysis/crosscheck/README.md`
