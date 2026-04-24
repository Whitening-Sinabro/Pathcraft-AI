# POE2 D7 — POE1 native 의존 4레이어 game 분기 플랜

> 범위: `sections_continue.py` 4레이어의 POE1 하드코딩 ItemClass/조건을 POE2 실측 ground truth 로 재설계. S7 (D5 2단계) 후속.
>
> Ground truth: NeverSink POE2 필터 0.9.1 (`_analysis/neversink_poe2_0.9.1/`) 에서 직접 추출한 실제 Class/조건 패턴.

## §0. 조사 결과 (sufficient-evidence, 2026-04-24)

NeverSink POE2 필터 0-SOFT 전수 스캔 (5075 lines, Python count 기준):

| 키워드 | POE2 count | POE1 layer 사용 | 결론 |
|---|---|---|---|
| `Trinket` | 0 | layer_heist | POE2 미존재 → **skip** |
| `Blueprint` | 0 | layer_heist | POE2 미존재 → **skip** |
| `Contract` | 0 | layer_heist | POE2 미존재 → **skip** |
| `Wombgift` | 0 | layer_heist | POE2 미존재 → **skip** |
| `Rogue's Marker` | 0 | layer_heist | POE2 미존재 → **skip** |
| `Replica True` | 0 | layer_special_uniques | POE2 미존재 → **skip** |
| `Foulborn True` | 0 | layer_special_uniques | POE2 미존재 → **skip** |
| `Flask` | 64 | layer_flasks_quality | POE2 재설계 필요 (Endgame Flasks) |
| `Charm` | 89 | (POE1 Utility Flask 대체) | POE2 신규 Class 블록 |
| `Quality` | 58 | layer_flasks_quality | POE2 Flask/Charm Quality 실사용 |
| `HasExplicitMod` | 10 | layer_id_mod_filtering | POE2 재설계 필요 (Recombinator Mods) |
| `Identified` | 10 | layer_id_mod_filtering | POE2 재설계 필요 |

## §1. 구현 범위 (2단계 분리)

### Phase 1 — 이번 세션 (S8)

저위험 + 데이터 수집 없이 즉시 구현 가능:

1. **D7-A layer_heist**: POE2 전체 skip
2. **D7-D layer_special_uniques**: POE2 전체 skip (Replica/Foulborn 조건 POE2 부재)
3. **D7-B layer_flasks_quality**: POE2 재설계 (Ultimate Life/Mana Flask + Charm Quality)
4. **D7-C layer_id_mod_filtering**: POE2 **임시 skip** (Phase 2 에서 실제 구현으로 교체)
   - 이유: POE2 로 호출 시 POE1 Class ("Claws"/"Warstaves"/"Rune Daggers" 등) 가 Show 블록에 누수 확인됨. overlay 깨끗함 유지 목적.

### Phase 2 — 후속 세션

데이터 추출 스크립트 필요. 별도 스코프.

5. **D7-C layer_id_mod_filtering 실구현**: Phase 1 임시 skip 을 POE2 Recombinator Mods per-class 데이터로 교체
   - 스크립트: `scripts/extract_id_mod_filtering_poe2.py` (NeverSink POE2 필터 [[0400]] 파싱)
   - 데이터: `data/id_mod_filtering_poe2.json`
   - 코드: `_load_id_mod_filtering_poe2()` + game 분기 블록 생성 경로

## §2. Phase 1 상세 설계

### §2.1 D7-A layer_heist

**현재 (POE1)**:
- `layer_heist(mode)` — Class `Blueprints/Contracts/Trinkets/Wombgifts/Stackable Currency(Rogue's Marker)` Show 블록 7개

**변경**:
- 시그니처 추가: `layer_heist(mode: str = "ssf", game: str = "poe1") -> str`
- `game == "poe2"` 시 즉시 빈 문자열 반환 (guard clause)
- `generate_beta_overlay` 에서 `layer_heist(mode=mode, game=game)` 호출

### §2.2 D7-D layer_special_uniques

**현재 (POE1)**:
- `layer_special_uniques(mode)` — `Rarity Unique + Replica True` / `Rarity Unique + Foulborn True` Show 블록 2개

**변경**:
- 시그니처 추가: `layer_special_uniques(mode: str = "ssf", game: str = "poe1") -> str`
- `game == "poe2"` 시 즉시 빈 문자열 반환
- `generate_beta_overlay` 호출부 전달

### §2.3 D7-B layer_flasks_quality

**현재 (POE1)**:
- `Class "Flasks" + Quality >= 10/20/21` — 3블록
- `Class "Utility Flasks" + Rarity Magic` — 1블록

**POE2 대응 (NeverSink 실측)**:
- Life/Mana Flask:
  - `BaseType == "Ultimate Life Flask" "Ultimate Mana Flask"` + `Quality > 10` + `ItemLevel >= 83` + `Rarity Normal Magic` + `AreaLevel >= 65` — top quality
  - 동일 BaseType + `ItemLevel >= 83` (no Quality) — toplevel
  - Quality 임계 2단계 (`>10` 만 쓰이고, POE1 `>= 20/21` 없음)
- Charm (POE1 Utility Flask 대체):
  - `Class == "Charms"` + `Quality >= 18` + `ItemLevel >= 82` + `Rarity Normal Magic` + `AreaLevel >= 65` — top quality

**변경**:
- 시그니처: `layer_flasks_quality(mode: str = "ssf", game: str = "poe1") -> str`
- `game == "poe1"` 분기: 현재 POE1 블록 4개 유지 (regression 방지)
- `game == "poe2"` 분기:
  - Block1: Ultimate Life/Mana Flask + Quality > 10 + IL>=83 → 강조
  - Block2: Ultimate Life/Mana Flask + IL>=83 (no Quality) → 일반 highlight
  - Block3: Charms + Quality >= 18 + IL>=82 → top quality Charm 강조
- `generate_beta_overlay` 호출부 전달

## §3. 테스트 계획

파일: `python/tests/test_filter_poe2_d7.py` (신규)

| 테스트 | 검증 |
|---|---|
| `test_heist_poe2_empty` | `layer_heist(game="poe2")` → `""` |
| `test_heist_poe1_regression` | `layer_heist(game="poe1")` 기존 블록 개수·Class 문자열 변화 없음 |
| `test_special_uniques_poe2_empty` | `layer_special_uniques(game="poe2")` → `""` |
| `test_special_uniques_poe1_regression` | POE1 Replica/Foulborn 블록 보존 |
| `test_flasks_quality_poe2_charm_present` | POE2 출력에 `Class == "Charms"` + `Quality >= 18` 포함 |
| `test_flasks_quality_poe2_ultimate_flask_present` | POE2 출력에 `BaseType == "Ultimate Life Flask" "Ultimate Mana Flask"` 포함 |
| `test_flasks_quality_poe2_no_utility_flasks` | POE2 출력에 `"Utility Flasks"` 문자열 부재 (POE1 전용 Class 누수 없음) |
| `test_flasks_quality_poe1_regression` | POE1 `Class "Flasks"` + `Quality >= 10/20/21` 블록 보존 |
| `test_overlay_e2e_poe2_no_heist` | `generate_beta_overlay(game="poe2")` 결과에 `Blueprints`/`Contracts`/`Trinkets` 전무 |
| `test_overlay_e2e_poe2_no_replica` | `generate_beta_overlay(game="poe2")` 결과에 `Replica True`/`Foulborn True` 전무 |

## §4. PASS 조건 (DoD)

- [x] `layer_heist(game="poe2") == ""` / `layer_special_uniques(game="poe2") == ""` / `layer_id_mod_filtering(game="poe2") == ""`
- [x] `layer_flasks_quality(game="poe2")` 에 Ultimate Life/Mana Flask + Charm 블록 존재
- [x] `generate_beta_overlay(game="poe2")` 에 POE1-only 문자열 (`Blueprints`/`Contracts`/`Trinkets`/`Wombgifts`/`Replica True`/`Foulborn True`/`Utility Flasks`/`Claws`/`Daggers`/`Warstaves`/`Rune Daggers`/`Thrusting One Hand Swords`) 전무
- [x] Python 테스트: 697 → 712 (+15) 전체 PASS
- [x] cargo test 50 (42+8 doc) PASS (Rust 변경 없음)
- [x] vitest 110 PASS (frontend 변경 없음)
- [x] `python filter_generator.py --game poe2` CLI smoke PASS (6577 줄 출력)

## §5. 수정 파일 목록

| 파일 | 변경 내용 |
|---|---|
| `python/sections_continue.py` | `layer_heist` / `layer_special_uniques` / `layer_flasks_quality` / `layer_id_mod_filtering` 시그니처 + game 분기 + `generate_beta_overlay` 호출부 |
| `python/tests/test_filter_poe2_d7.py` | 신규 — 15 테스트 |

생성 없음. 데이터 파일 추가 없음.

## §6. Phase 2 예비 스펙 (D7-C, 다음 세션)

| 항목 | 내용 |
|---|---|
| 스크립트 | `scripts/extract_id_mod_filtering_poe2.py` — NeverSink POE2 필터 섹션 [[0400]] 파싱 → per-class top mod 리스트 |
| 데이터 | `data/id_mod_filtering_poe2.json` — `{"by_class": {"Boots": ["Hellion's"], ...}}` |
| 코드 | `_load_id_mod_filtering_poe2()` + `layer_id_mod_filtering(game="poe2")` 분기 |
| POE2 조건 특이점 | `Rarity Normal Magic Rare` (POE1 = Rare only), `ItemLevel` 조건 없음, `Mirrored False + Corrupted False` 추가 |
| 테스트 | id_mod per-class 기본 출력 + POE1 regression + POE2 Recombinator 패턴 검증 |

Phase 2 는 본 세션 범위 외. Phase 1 완료 후 별도 plan 문서 확장.
