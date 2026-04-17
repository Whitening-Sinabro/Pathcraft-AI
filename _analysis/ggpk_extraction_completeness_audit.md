# GGPK 추출 완전성 감사 (Phase F0)

**감사일**: 2026-04-17
**계기**: 사용자 지적 — "GGPK 모든 데이터를 가져온다고 했는데 체크리스트 없이 '이정도면 됐지' 하고 끝났을 가능성"
**결과**: 지적 사실 확인. 커버리지 **0.76%** (7/921).

## 근거 (방법론)

**체크리스트 출처**: `data/schema/schema.min.json` (`poe-tool-dev/dat-schema`, version 7).
- Active maintenance, POE 1/2 지원, `validFor` 플래그로 분기 (1=POE1, 2=POE2, 3=both)
- `src-tauri/src/schema.rs:4` 이미 참조 중 (런타임 스키마 로드용)
- 이것이 **GGPK 테이블 모수의 단일 진실원**

**절차**:
1. schema.min.json POE1 applicable 테이블 전체 덤프
2. 테이블명 keyword 기반 메커닉 카테고리화
3. PathcraftAI feature → 필요 테이블 매트릭스
4. Gap 분석 + 확장 우선순위

## 핵심 수치

| 항목 | 값 |
|------|---|
| schema version | 7 (createdAt 2026-04-01 경) |
| POE1 applicable tables | **921** |
| 현재 `extract_data.rs` TARGETS | **7** |
| **커버리지** | **0.76%** |
| 카테고리화된 테이블 | 555 (utility/visual 등 466 uncategorized) |

## 현재 TARGETS (7개)

`src-tauri/src/bin/extract_data.rs:19-27`:
- ActiveSkills
- BaseItemTypes
- Maps
- PassiveSkills
- QuestRewards
- SkillGems
- UniqueStashLayout

## 카테고리별 분포 (POE1 921 → 카테고리화 555)

| 카테고리 | 테이블 수 | 현재 추출 | 주요 테이블 예시 |
|----------|----------|----------|----------------|
| **League Mechanics** | | | |
| Heist | 29 | 0 | HeistAreas, HeistJobs, HeistContracts |
| Blight | 18 | 0 | BlightTowers, BlightChestTypes |
| Delve | 17 | 0 | DelveBiomes, DelveAzuriteShop |
| Necropolis | 13 | 0 | — |
| Expedition | 12 | 0 | ExpeditionAreas, ExpeditionCurrency |
| Delirium/Affliction | 10 | 0 | — |
| Harvest | 10 | 0 | HarvestCraftOptions, HarvestCraftTiers |
| Synthesis | 9 | 0 | SynthesisGlobalMods |
| Legion | 8 | 0 | LegionChestTypes |
| Ultimatum | 8 | 0 | UltimatumEncounters |
| Sentinel | 8 | 0 | — |
| Incursion | 7 | 0 | IncursionArchitect, IncursionRooms |
| Breach | 5 | 0 | BreachArtVariations, BreachElement |
| Crucible | 5 | 0 | CrucibleTags |
| Ritual | 5 | 0 | RitualRuneTypes |
| Essence | 3 | 0 | **Essences** (직접 데이터 원본) |
| Scarab | 2 | 0 | **Scarabs**, **ScarabTypes** |
| Metamorph | 1 | 0 | — |
| Beyond | 1 | 0 | — |
| **Items** | | | |
| Maps | 29 | 1 (Maps만) | MapSeries, AtlasNode |
| Atlas | 26 | 0 | — |
| Unique | 14 | 1 (UniqueStashLayout만) | UniqueMapInfo, 각종 Unique 서브셋 |
| Currency | 10 | 0 | — |
| Jewel | 9 | 0 | PassiveTreeExpansionJewels |
| Weapon | 9 | 0 | — |
| BaseType | 6 | 1 | — |
| Divination | 5 | 0 | DivinationCardArt |
| Flask | 2 | 0 | **Flasks** |
| **Armour** | 2 | 0 | **ArmourTypes** ← Phase D 때 필요했음 |
| Fossil | 0 | 0 | (Delve에 포함 추정) |
| **Crafting** | | | |
| Mod (Crafting_Mod) | 3 | 0 | **Mods**, ModType, ModFamily |
| ModEffect | 2 | 0 | — |
| Mod 관련 (grep) | 42 | 0 | 메커닉별 mod 테이블 다수 |
| **Skills** | | | |
| Passive | 26 | 1 | — |
| Gem | 11 | 1 (SkillGems만) | GemTags, GrantedEffects |
| Active | 4 | 1 | — |
| Tag | 1 (`Tags` 단독) | 0 | **Tags** ← 모든 카테고리화 기초 |
| **Character** | | | |
| Character | 15 | 0 | **Characters**, **Ascendancy** |
| **Quest** | 19 | 1 (QuestRewards만) | — |
| **Monster/Syndicate** | | | |
| Monster | 55 | 0 | — |
| Syndicate | 13 | 0 | — |
| Stash | 20 | 1 (UniqueStashLayout만) | — |
| **Misc (low priority)** | | | |
| Visual | 66 | 0 | — |
| Audio | 19 | 0 | — |
| Achievement | 18 | 0 | — |
| **Uncategorized** | **466** | — | 대부분 utility/low-priority |

## PathcraftAI Feature × 필요 테이블 매트릭스

| Feature | 현재 사용 (GGPK) | 필요한데 부재 |
|---------|----------------|--------------|
| build_parsing (pob_parser) | — (XML 직접) | Characters, Ascendancy, Tags, GemTags |
| filter L7 weapon (Phase B+C) | BaseItemTypes, ActiveSkills, SkillGems | Mods (HasExplicitMod 검증) |
| filter L7 defense (Phase D) | BaseItemTypes (Id naming 휴리스틱) | **ArmourTypes**, Mods |
| filter L7 accessory (Phase E) | — (POB Lua + NeverSink) | Mods, ModType, ModFamily, GemTags |
| filter L8 mechanics (GGPKItems) | BaseItemTypes (Name 패턴) | **Tags** (정확한 카테고리화), Scarabs, Essences, Flasks |
| filter maps | Maps | MapSeries, AtlasNode |
| filter divcard (F1) | — (수동 + Wiki Cargo) | ShopTag (DivinationCards 테이블 없음) |
| build_coach | — | Characters, Ascendancy, PassiveSkills |
| passive_tree | PassiveSkills | Characters, Ascendancy, PassiveTreeExpansionJewels |
| F2 Breach 감사 | — | BreachArtVariations, BreachElement |
| F2 Legion 감사 | — | LegionChestTypes, LegionChestCounts |
| F2 Scarab 감사 | — | **Scarabs**, ScarabTypes |
| F2 Incursion 감사 | — | IncursionChestRewards, IncursionArchitect, IncursionRooms |
| F2 Expedition 감사 | — | ExpeditionAreas, ExpeditionCurrency, ExpeditionRelicMods |
| F3 Heist 감사 | — | HeistJobs, HeistAreas, HeistContracts |
| F3 Delve 감사 | — | DelveBiomes, DelveAzuriteShop |
| F3 Blight 감사 | — | BlightTowers |
| F7 Crafting Mods 감사 | — | Mods, ModType, ModFamily |

## Gap 분석 — 확장 우선순위 (feature 참조 빈도 순)

| 순위 | 테이블 | 참조 feature 수 | 이유 | 심각도 |
|------|--------|---------------|------|--------|
| 1 | **Mods** | 4 | HasExplicitMod 검증 + Phase D/E/F7 공통 필요 | 🔴 HIGH |
| 2 | **Characters** | 3 | 빌드 파싱/코치/패시브 트리 각도 | 🔴 HIGH |
| 3 | **Ascendancy** | 3 | 동일 | 🔴 HIGH |
| 4 | **Tags** | 2 | BaseItemTypes.TagsKeys 해결 → L8 mechanic 정확도 근본 개선 | 🔴 HIGH |
| 5 | **GemTags** | 2 | Phase E damage_type 추출에서 POB Lua 대체 가능성 | 🟡 MID |
| 6 | **ModType** | 2 | Mods와 쌍, ModFamily와 함께 크래프팅 감사 | 🟡 MID |
| 7 | **ModFamily** | 2 | 동일 | 🟡 MID |
| 8 | **Scarabs** | 2 | `GGPKItems.scarabs_*` Name 패턴 대신 직접 테이블 | 🟡 MID |
| 9 | **ArmourTypes** | 1 | Phase D BaseItemTypes.Id 휴리스틱 정확도 개선 | 🟢 LOW (이미 대체됨) |
| 10 | **Essences** | 1 | `GGPKItems.essence_*` 대체 | 🟢 LOW |
| 11 | **Flasks** | 1 | 현재 쓰이는 곳 적음 | 🟢 LOW |
| 12 | MapSeries | 1 | Atlas 확장 | 🟢 LOW |
| 13 | BreachArtVariations | 1 | F2 전용 | 🟢 LOW |
| 14 | LegionChestTypes | 1 | F2 전용 | 🟢 LOW |
| 15-20 | Incursion/Expedition/Heist/Delve/Blight 세부 | 1 each | 해당 phase 도달 시 추출 | 🟢 LOW |

## Critical 이슈

### 🔴 Critical 1: Tags 테이블 부재로 전체 카테고리화 휴리스틱 의존

**현상**:
- `BaseItemTypes.json` entry에 `TagsKeys: [38, 0, 1048]` 인덱스만 있고 Tags 테이블 없어 **태그 이름을 모름**
- `sections_continue.load_ggpk_items()` (line 1246+) — BaseItemTypes의 **Name 패턴 매칭**으로 breach/scarab/essence 분류
- 예: `"'Crystallised Lifeforce' in Name"` 같은 문자열 매칭

**위험**:
- 게임 업데이트로 Name 변경 시 stale
- 신규 아이템(신규 타입 추가) 누락
- 번역된 클라이언트에서 Name 다를 수 있음 (현재 한국 POE 사용)

**해결**:
- `Tags` 테이블 추출 → `BaseItemTypes.TagsKeys`를 실제 태그명으로 해결
- `load_ggpk_items`를 **태그 기반** 분류로 재작성 가능

### 🔴 Critical 2: Mods 테이블 부재로 HasExplicitMod 검증 불가

**현상**:
- Phase B(무기), D(방어), E(악세서리) 모두 NeverSink mod 이름 리스트에 의존
- 실제 mod 이름이 GGPK `Mods.Id` 또는 `Name`과 일치하는지 검증 절대 불가
- NeverSink stale 시 조용히 필터 누락

**해결**:
- `Mods` + `ModType` + `ModFamily` 3개 테이블 추출
- `defense_mod_tiers.json` / `accessory_mod_tiers.json`의 mod 이름을 GGPK와 교차 검증하는 스크립트 추가

### 🟡 Critical 3: Characters/Ascendancy 부재로 빌드 파싱 완전성 제약

**현상**:
- pob_parser는 XML의 `className`, `ascendClassName` 텍스트만 사용
- 해당 클래스의 실제 **base stats, passive start node, 어센던시 목록** GGPK에서 못 가져옴
- 현재 패시브 트리 Phase는 클라이언트 data.json에서 class start node 매핑을 **수동**으로 관리 (current.md:50-52)

**해결**:
- `Characters` + `Ascendancy` 추출 → 자동 매핑 (current.md class start dict 폐기 가능)

### 🟡 Verification Failure

매트릭스 작성 중 **schema 부재 테이블** 1개 발견:
- `BlightRewards` → schema에 없음. 실제 테이블명 다름 (추정: `BlightRewardTypes` 또는 `BlightChestTypes`)

**교훈**: 각 phase fix 착수 전 테이블명 **정확성 재확인** 필요 (schema.min.json로 검증).

## 권고 조치

### Task F0-fix-1 (우선순위 1): `extract_data.rs` TARGETS 확장

**대상 확장** (Critical 1/2/3 해결 + 누적 feature 5+ 커버):

```rust
const TARGETS: &[&str] = &[
    // 기존
    "Data/ActiveSkills.datc64",
    "Data/BaseItemTypes.datc64",
    "Data/Maps.datc64",
    "Data/PassiveSkills.datc64",
    "Data/QuestRewards.datc64",
    "Data/SkillGems.datc64",
    "Data/UniqueStashLayout.datc64",
    // 신규 Tier 1 (Critical 1/2/3)
    "Data/Tags.datc64",
    "Data/Mods.datc64",
    "Data/ModType.datc64",
    "Data/ModFamily.datc64",
    "Data/Characters.datc64",
    "Data/Ascendancy.datc64",
    // Tier 2 (다중 feature 활용)
    "Data/GemTags.datc64",
    "Data/ArmourTypes.datc64",
    "Data/Scarabs.datc64",
    "Data/ScarabTypes.datc64",
    "Data/Essences.datc64",
    "Data/Flasks.datc64",
];
```

**예상 시간**:
- 코드 수정: 5분 (배열 확장)
- `cargo run --bin extract_data` 재추출: 5~10분 (수백 MB GGPK 재읽기)
- 검증: 새 JSON 로드 스모크 + 기존 LoadCategoryData 회귀
- 합계: **30~45분** (별도 Rust build + 재추출 session)

### Task F0-fix-2 (우선순위 2): `load_ggpk_items` 태그 기반 재작성

Tags.json 추출 후, `sections_continue.load_ggpk_items()` (line 1246+)의 Name 패턴 매칭을
**TagsKeys → Tags 해결**로 대체. breach/scarab/essence 분류 정확성 근본 개선.

**예상 시간**: 1.5h (F0-fix-1 완료 후)

#### 완료 (2026-04-17)

- `_TAGS_CACHE` 추가 + `_tags(b)` 헬퍼로 TagsKeys→Tags.Id 해결.
- 태그 기반 분류:
  - `breachstone_splinter` → 5 Breach ✅ (기존과 동일)
  - `legion_splinter` → 5 Legion ✅
  - `scarab` → 190 전체 스카랩 ✅
  - `uber_scarab | uniques_scarab | influence_scarab` ∪ Name prefix(Horned/Titanic/Influencing) → 14 고가
  - `essence` → 105 전체 에센스 (티어는 Name 접두사)
- Name 유지 (태그 없음): `lifeforce` (Id prefix `HarvestSeed` 추가 검증), `splinter_simulacrum`, fossils/resonators/oils
- **Triple-check (POE Wiki)**: `Influencing Scarab of Shaper/Elder/Hordes/Interference` 4종 모두 Wiki disambiguation 상 동일 family. GGPK는 1종만 `influence_scarab` 태그, 3종은 `scarab_grants_extra_content` — 드롭 메커니즘 차이 반영일 뿐 사용자 분류 아님. **최종: 태그∪Wiki Name union으로 14 유지** (태그 전용 11 버전 폐기).
- 스냅샷 테스트: `test_snapshot_tag_based_classification` (pytest 313 PASS)

### Task F0-fix-3 (우선순위 3): mod 검증 스크립트

`scripts/validate_mod_names.py` — `defense_mod_tiers.json` / `accessory_mod_tiers.json` /
`weapon_mod_tiers.json`의 mod 이름이 GGPK `Mods.Name`과 일치하는지 스팟체크.

**예상 시간**: 1h

### 후속 방향 재정의

- **Phase F2~F7 전제 변경**: F0-fix-1 완료 후 각 phase가 필요 테이블 갖춤 → 그때 감사 착수
- **Phase F1 재평가**: DivinationCards 테이블 schema에 없음 → 현재 Wiki Cargo 의존이 **유일한 경로** 확정. 전략 유효
- **Phase D 재평가**: ArmourTypes 추출 후 BaseItemTypes.Id 휴리스틱 대체 가능. 현재 동작은 OK이지만 정확도 업그레이드 가능

## DoD 충족

| # | 기준 | 결과 |
|---|------|------|
| 1 | `_analysis/ggpk_extraction_completeness_audit.md` 산출 | ✅ 본 문서 |
| 2 | feature 매트릭스 (빌드/필터/코치/F1~F7) | ✅ `_analysis/_ggpk_feature_matrix.json` + 본 문서 섹션 |
| 3 | Top 20 확장 후보 | ✅ Gap 분석 표 (14개 유효 + 나머지 low) |
| 4 | `extract_data.rs` TARGETS 확장은 별도 task | ✅ F0-fix-1로 분리 |
| 5 | `.claude/status/mechanic_data_audit_plan.md` + F0 전제 명시 | ⏸️ 리포트 완료 후 갱신 |
| 6 | Phase F2~F7 의존 테이블 pre-check | ✅ 매트릭스에 도메인별 명시 |

## 참조

- `poe-tool-dev/dat-schema`: https://github.com/poe-tool-dev/dat-schema
- 현재 schema: `data/schema/schema.min.json` (v7)
- raw 데이터: `_analysis/_ggpk_inventory_raw.json`, `_analysis/_ggpk_feature_matrix.json`
- 추출기 소스: `src-tauri/src/bin/extract_data.rs:19-27`
