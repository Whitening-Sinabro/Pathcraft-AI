# Build-aware 무기 필터 플랜 (Phase B+C 통합)

> 목표: POB의 착용 장비 + 메인 스킬에서 무기 클래스를 유도하고, 레어 드롭 중
> T1/T2 물리 mod가 붙은 것만 자동 강조한다.
> 필터 문법에 `PhysicalDPS`는 없지만 `HasExplicitMod` mod-tier 프록시로 근사.
> 레퍼런스: NeverSink `1-REGULAR.filter:814-828` weapon_phys 블록 (mod-tier 룰).

## 실측 요약 (Step 0 결과, 플랜 확정 전 검증 완료)

- **pob_parser 스키마** (`pob_parser.py:196-283`):
  - gear slot: `gear["Weapon 1"] = {name, rarity, base_type, sockets, mods, reasoning}`
  - base_type 예: `"Stone Axe"`, `"Destroyer Regalia"` (베이스 이름, **Class 아님**)
  - **skill tag 정보 파싱 안 함** — `gem_setups`에는 `nameSpec`(젬 이름)만 저장
  - 결과: 무기 클래스 유도는 **(a) 착용 무기 base_type → Class 매핑 사전 1순위,
    (b) 젬 이름 → 예상 weapon requirement 사전 2순위(fallback)** 로 전환
- **NeverSink 라이선스**: `_analysis/neversink_8.19.0b/` 안에 LICENSE 파일 **없음**.
  필터 헤더는 AUTHOR만 명시. 공식 repo: github.com/NeverSinkDev/NeverSink-Filter.
  → 라이선스 단정 불가. 보수적으로 **mod 이름 리스트만 참조** (GGG 게임 데이터이며
  mod 이름 자체는 저작물 아님) + NeverSink 룰 구조를 참고했다는 출처 기록만.
- **filter_generator CLI** (`filter_generator.py:32-45`): positional `build_json` +
  옵션 `--strictness/--stage/--mode/--al-split/--json/--coaching/--out`. **`--pob` 없음.**
  → 검증 커맨드는 `pob_parser` + `filter_generator` 2단 파이프라인으로 수정
- **기존 fixture 패턴**: `python/tests/test_build_extractor_n_stage.py:20` `_mk()` 헬퍼가
  `progression_stages[0].gear_recommendation` 스키마로 build_data 생성. 무기 테스트에
  **그대로 재사용** (slot 키를 `"Weapon 1"` 로 주면 실전 케이스 커버)

## Step 1 완료 (2026-04-16) — POB ground truth 전환 근거

Step 1 착수 중 **GGPK 데이터 부정확성 발견**:
- `ActiveSkills.WeaponRestriction_ItemClassesKeys`에 Sunder = `[12, 32, 14, 17]` (Mace/Sceptre/Staff만, **Axe 누락**)
- Cleave, Earthquake, Heavy Strike, Lacerate 다수 스킬에서 **2H 변형 누락**
- 전수 조사: `_analysis/gem_weapon_restriction_audit.md` (187 스킬)
- 추정: GGPK `ActiveSkills`는 일부 restriction만 저장. 나머지는 현재 추출본에 없는 테이블 (GrantedEffects/GemEffects)에 정의될 가능성

**해결: POB Community `src/Data/Skills/*.lua`의 `weaponTypes` 필드로 전환**
- 8 파일 (`act_str/dex/int.lua`, `other.lua`, `glove.lua`, `sup_str/dex/int.lua`) 자동 다운로드 + 파싱
- 231 젬에 physical weapon class 매핑 (실게임 일치, Sunder Axe 포함 ✓)
- Transfigured 변형도 자동 포함 (Sunder of Earthbreaking, Cleave of Rage 등)
- 캐시: `data/pob_skills_cache/` (gitignore)
- POE 패치 시 스크립트 재실행 → 자동 반영

**중요 경고**: 향후 세션에서 gem → weapon class 매핑이 필요할 때 **GGPK `ActiveSkills` 절대 사용 금지**. `data/gem_weapon_requirements.json`만 소비. 생성 스크립트는 POB 전용.

관련 메모리: `C:\Users\User\.claude\projects\D--Pathcraft-AI\memory\project_weapon_filter_ground_truth.md`

## DoD (Definition of Done)

1. **build_data → 무기 클래스 추출** — 대표 fixture(Sunder 2H, Sunder+Bonesplitter
   듀얼 stage, CoC Ice Spear, Spell Wand 각 1개)에서 기대 클래스 set이 반환. 스냅샷
   테스트 박제
2. **mod-tier 사전** — T1/T2 flat phys + % phys prefix + 저티어 배제 mod 리스트가
   JSON으로 정리되고, NeverSink `1-REGULAR.filter:814-828` 라인과 1:1 매핑
3. **base_type → Class 매핑 사전** — 플랜 대상 무기 클래스 7종(One/Two Hand Axes,
   Swords, Maces, Bows, Wands, Daggers, Claws, Warstaves, Thrusting 1H Swords)에
   해당하는 base_type 전부 매핑. 출처: `src-tauri/src/bin/extract_data.rs` GGPK
   추출본 `BaseItemTypes` 또는 POE 위키 수동 수집
4. **L7 필터 출력** — 빌드 무기 클래스가 유도되면 L7에 mod-tier 프록시 블록 생성,
   미유도 시 블록 생략 (regression 없음). **L7 내 블록 순서 박제**: unique >
   chanceable > weapon_phys_proxy > gem > base (first-match 순서)
5. **엄격도 연동** — strictness 0~1: mod count >=2, strictness 2+: >=3
6. **유닛 테스트** — weapon class extractor + base_type → Class 매핑 + sections_continue
   L7 블록 출력 커버
7a. **자동 스모크 (필터 텍스트 검사)** — 생성된 필터 문자열에 대해:
   - 빌드 무기 클래스(set)와 일치하는 `Class ==` 라인 포함 확인
   - `HasExplicitMod "Tyrannical"` 등 mod-tier 룰 라인 포함
   - 빌드 무기 없는 케이스에서 weapon_phys_proxy 블록이 emit 안 됨 (regression)
7b. **인게임 스모크 (육안)** — Lv10~30 구간에서:
   - Tyrannical 1H Axe 레어 → 시안 스타, 큰 폰트
   - Heavy/Serrated 1H Axe 레어 → L8 일반 레어색
   - 빌드가 2H 전용일 때 1H Axe 레어는 프록시 블록에 안 걸림

## 범위 + 후속 Phase 타임라인

이번 플랜은 **무기만** 해결. 같은 패턴(POB 파싱 → 사전 유도 → HasExplicitMod 프록시)
을 방어/악세서리로 확장하는 후속 Phase는 본 Phase 완료 후 즉시 착수 (예상 각 4~6h):
- **Phase D**: 방어 타입 유도 (착용 장비 `gear["Body Armour"].base_type` → Armour/Evasion/ES 분류)
  + HasExplicitMod defense mod tier 프록시
- **Phase E**: 악세서리 강조 — Ring/Amulet/Belt 슬롯별 좋은 suffix (of the Whelpling, of Radiance 등) 프록시

본 Phase에서 구축한 `weapon_mod_tiers.json` + base-to-class 매핑 구조를 그대로
재사용하므로 신규 데이터만 추가.

## 파일 변경 (수정/생성/삭제)

### 신규

| 파일 | 역할 |
|------|------|
| `data/weapon_mod_tiers.json` | T1/T2 물리 mod 사전 + 배제 mod. NeverSink 룰 **구조 참고** 출처 기록 (라이선스 단정 없음, mod 이름만 사용) |
| `data/weapon_base_to_class.json` | 무기 base_type → POE 필터 Class 매핑 사전 (예: `"Stone Axe": "One Hand Axes"`). 9 Class × 베이스 전부 |
| `data/gem_weapon_requirements.json` | 젬 이름 → 해당 젬이 요구하는 weapon class set (예: `"Sunder": ["One Hand Axes","Two Hand Axes","One Hand Maces","Two Hand Maces","Staves","Warstaves"]`). 착용 무기 없을 때 fallback |
| `python/weapon_class_extractor.py` | build_data → 무기 클래스 set 유도. 착용 무기 1순위 + 젬 이름 2순위 |
| `python/extract_weapon_bases.py` | GGPK 추출본(`data/extracted_game_data/BaseItemTypes.*`)에서 `weapon_base_to_class.json` 생성 (수동/반복실행) |
| `python/tests/test_weapon_class_extractor.py` | 4개 대표 fixture 스냅샷 테스트 (기존 `_mk()` 헬퍼 재사용) |
| `_analysis/neversink_weaponphys_rules.md` | NeverSink `1-REGULAR.filter:814-828` 블록 추출 + 각 mod 의미 주석 |

### 수정

| 파일 | 변경 내용 |
|------|-----------|
| `python/build_extractor.py` | `extract_build_weapon_classes(build_data)` 신규, `merge_build_stages` 결과에 `weapon_classes` 필드 추가 |
| `python/sections_continue.py` | L7 BUILD_TARGET에 `_make_weapon_phys_proxy_block()` 추가. 빌드 무기 클래스 + weapon_mod_tiers.json → HasExplicitMod 룰 emit. strictness 조건부 mod count |
| `python/tests/test_sections_continue.py` | L7 weapon phys 블록 출력 케이스 3개 (빌드 없음 / 1H Axe 빌드 / 2H 빌드) |
| `src/components/FilterPanel.tsx` | (선택) build summary에 "무기 클래스: One Hand Axe" 표시 추가 |

### 삭제

없음.

## 데이터 설계

### `data/weapon_mod_tiers.json`

```json
{
  "source": "NeverSink 1-REGULAR.filter:814-828 (v8.19.0b) — 룰 구조 참고",
  "license_note": "NeverSink 저장소 라이선스 미확인 (LICENSE 파일 없음). POE mod 이름 자체는 GGG 게임 데이터로 저작물 아님. 본 파일은 mod 이름 리스트만 수록, 룰 구조는 재작성.",
  "good_prefix_mods": {
    "flat_phys_T1": ["Tyrannical"],
    "flat_phys_T2": ["Merciless"],
    "flat_phys_T3": ["Cruel"],
    "pct_phys_T1": ["Emperor's"],
    "pct_phys_T2": ["Dictator's"],
    "accuracy_flat_phys_T1": ["of Incision"],
    "elemental_hybrid_T1_T2": ["of Celebration", "of Dissolution", "of Destruction"]
  },
  "good_suffix_mods": {
    "attack_speed_T1_T2": ["of the Underground", "Subterranean", "of Many"],
    "crit_T1": ["of Tacati", "Tacati's"],
    "flaring": ["Flaring", "Veil"]
  },
  "bad_mods_exclude": [
    "Heavy", "Serrated", "Wicked", "Vicious",
    "Glinting", "Burnished", "Polished", "Honed",
    "of Needling", "of Skill"
  ]
}
```

**결정**: mod 이름 리스트만 참조. 룰 구조(Class filter + HasExplicitMod include/exclude)는
PathcraftAI가 재작성. GGG mod 이름 변경 시 업스트림 추적 부담은 있으나 라이선스 리스크 제거.

### weapon_class_extractor.py API

```python
def extract_build_weapon_classes(
    build_data: dict,
    base_to_class: dict[str, str],
    gem_to_weapon_req: dict[str, list[str]],
) -> set[str]:
    """
    Returns a set of POE filter Class names (e.g., {"One Hand Axes", "Two Hand Axes"}).

    Resolution order (pob_parser 실측 스키마 기반):
    1. 착용 무기 1순위: build_data["progression_stages"][*]["gear_recommendation"]
       에서 슬롯 이름이 /Weapon\s*\d+/ 또는 'Weapon 1'/'Weapon 2'에 해당하는 항목의
       base_type → base_to_class[base_type] 매핑
    2. 착용 무기 미유도 시 fallback: gem_setups에서 extract_build_gems()로 젬 이름
       추출 → gem_to_weapon_req[gem_name] 의 Class set union
    3. 둘 다 비면 empty set (caller가 L7 블록 emit 생략)

    멀티 stage build_data인 경우 모든 stage의 union.
    경계 로깅: build_data에 progression_stages/gear_recommendation 누락,
    base_type이 매핑 사전에 없음, gem 이름이 사전에 없음 — 각 경우 logger.warning.
    """
```

**입력 케이스** (기존 `_mk()` fixture 확장으로 테스트 박제):
- Sunder POB (slot="Weapon 1", base_type="Reaver Axe" 착용) → `{"Two Hand Axes"}`
- Sunder + Bonesplitter 듀얼 stage (stage1=Reaver Axe, stage2=Stone Axe) → `{"Two Hand Axes", "One Hand Axes"}`
- CoC Ice Spear (Cospri's Malice → base_type="Jewelled Foil") → `{"Thrusting One Hand Swords"}`
- Spell caster (Weapon 1=base_type="Opal Wand", 젬에 Arc 있음) → `{"Wands"}`
- 젬 fallback 케이스: 빌드 무기 없고 gem_setups에 "Sunder" 있음 → Sunder 요구 클래스 set
- 완전 미유도: 빈 build_data → `set()` + warning 로그

## 필터 출력 설계

### L7 내 블록 순서 (first-match semantics)

POE 필터는 첫 매칭 Show/Hide에서 멈춘다. 빌드 무기 레어가 unique base와 겹치면 순서가
결과를 바꾼다. L7 내 emit 순서를 **고정**:

```
L7 BUILD_TARGET:
  1. unique_bases        (Rarity Unique + BaseType)      # 최상위, 거의 unique에만 매칭
  2. chanceable_bases    (Rarity Normal + BaseType)      # unique 체이스 베이스
  3. weapon_phys_proxy   (Rarity Rare + Class + mod)     # 신규 — unique가 아니면서 레어만
  4. gem_setups          (Class "Gems" + BaseType)
  5. act_identify_candidate (Rarity Rare Magic + base)   # AL<68 미감정 후보
  6. rare_base_upgrade   (Rarity Rare + BaseType, ilvl>=75)  # 기존 L7 레어 룰
```

`weapon_phys_proxy`가 6번 기존 rare_base_upgrade보다 **앞**에 있어야 Class 기반 + mod-tier
조합이 일반 base-whitelist보다 우선. 순서 주석을 `_make_weapon_phys_proxy_block()` 위에 명시.

### L7 weapon_phys_proxy 블록 (신규)

```
# PathcraftAI — Build weapon upgrade candidates (T1/T2 physical mods)
# Source: NeverSink 1-REGULAR.filter:814-828 mod-tier methodology
Show
    Identified True
    DropLevel >= 5
    Rarity Rare
    Class == <union of build weapon classes>
    HasExplicitMod "Tyrannical" "Merciless" "Cruel" "of the Underground" "Subterranean" "of Many" "of Tacati" "Tacati's"
    HasExplicitMod >= <strictness_mod_count> "Tyrannical" "Merciless" "Flaring" "Dictator's" "Emperor's" "of Celebration" "of Incision" "of Dissolution" "of Destruction" "of the Underground" "Subterranean" "of Many" "of Tacati" "Tacati's" "Veil"
    HasExplicitMod = 0 "Heavy" "Serrated" "Wicked" "Vicious" "Glinting" "Burnished" "Polished" "Honed" "of Needling" "of Skill"
    SetFontSize 43
    SetBorderColor 100 220 255 255
    SetBackgroundColor 0 0 0 220
    PlayAlertSound 2 300
    MinimapIcon 1 Cyan Star
```

**파라미터**:
- `<union of build weapon classes>` — `extract_build_weapon_classes()` 결과
- `<strictness_mod_count>` — `_STRICTNESS_WEAPON_MOD_COUNT`:
  - strictness 0~1: 2
  - strictness 2+: 3
- `DropLevel >= 5` — 너무 이른 레벨(Lv1~4)에서는 레어 무기 자체 희귀 → ratelimit

**미감정 레어는 별도 블록 (기존 L7 act_identify_candidate 이미 존재):**
- Identified False + 빌드 무기 클래스 → 마젠타 강조. 감정 후 상기 룰로 필터링.

## 엄격도 연동

`sections_continue.py:_STRICTNESS_SUPPLY_INDEX` 옆에 추가:

```python
_STRICTNESS_WEAPON_MOD_COUNT = {
    0: 2,  # 레벨링, 관대
    1: 2,
    2: 3,  # 표준
    3: 3,
    4: 3,  # 엄격은 L9 Hide가 이미 광범위하므로 count 증가보다 유지가 안전
}
```

## 실행 순서 + PASS 조건

### Step 1. 데이터 수집 — mod 사전 + base→Class 사전 (1.5h)

```bash
# 1a. NeverSink 룰 수동 추출 (mod 이름 리스트만)
# _analysis/neversink_weaponphys_rules.md 직접 작성 — 814-828 블록 복붙 + 각 mod 의미 주석

# 1b. 무기 base → Class 매핑 생성
python python/extract_weapon_bases.py  # GGPK 추출본 또는 정적 리스트 → data/weapon_base_to_class.json

# 1c. 젬 → weapon requirement 사전 수동 작성
# data/gem_weapon_requirements.json — POE 위키 기반 공격 스킬 젬만 (spell/brand 등은 키 생략)
```

**PASS**:
- `data/weapon_mod_tiers.json` 작성, NeverSink 814-828와 1:1 매핑 (`_analysis/neversink_weaponphys_rules.md`에서 매핑표 diff)
- `data/weapon_base_to_class.json` 존재, 9개 무기 Class 전부 커버 (One Hand Axes/Swords/Maces/Daggers/Claws, Two Hand Axes/Swords/Maces, Bows, Wands, Sceptres, Staves, Warstaves, Thrusting One Hand Swords 등)
- `data/gem_weapon_requirements.json` 존재, 주요 공격 젬 30개+ 커버 (Sunder, Cleave, Lacerate, Cyclone, Heavy Strike, Ice Shot, Lightning Arrow, Spectral Throw 등)

### Step 2. weapon_class_extractor.py (2h)

```bash
python -m pytest python/tests/test_weapon_class_extractor.py -v
```

**PASS**: 6개 fixture 스냅샷 테스트 전부 통과 (4개 주요 케이스 + fallback + 미유도).

### Step 3. build_extractor 통합 (1h)

```bash
python -m pytest python/tests/test_build_extractor_n_stage.py -v
```

**PASS**: `merge_build_stages` 결과 StageData에 `weapon_classes: frozenset[str]` 필드 존재. 기존 테스트 regression 없음.

### Step 4. sections_continue L7 확장 (3h)

```bash
# 단위 테스트
python -m pytest python/tests/test_sections_continue.py -v

# E2E 검증: POB URL → build_json → filter
python python/pob_parser.py "<sunder_pob_url>" > /tmp/sunder_build.json
python python/filter_generator.py /tmp/sunder_build.json --strictness 2 --json > /tmp/sunder_filter.json
python -c "
import json, sys
d = json.load(open('/tmp/sunder_filter.json', encoding='utf-8'))
f = d['overlay']
assert 'weapon_phys_proxy' in f or 'HasExplicitMod \"Tyrannical\"' in f, 'proxy block missing'
assert 'Two Hand Axes' in f, 'weapon class missing'
print('PASS: weapon_phys_proxy emitted with Two Hand Axes')
"
```

**PASS**:
- 단위 테스트 (빌드 없음 / 1H Axe / 2H Axe / 듀얼 stage 4 케이스) 통과
- E2E: 실제 Sunder POB 기반 필터 문자열에 weapon_phys_proxy 블록 + 정확한 Class 라인 포함
- regression: 빌드 무기 없는 케이스(예: DoT 빌드)에서 proxy 블록이 emit 안 됨 (assert 포함)

### Step 5. 빌드/타입 체크 (5min)

```bash
npm run build
npx tsc --noEmit
npm test
```

**PASS**: 0 errors, 모든 테스트 통과.

### Step 6a. 자동 스모크 — 필터 텍스트 검사 (10min)

```bash
# test_sections_continue.py에 신규 케이스 추가, 필터 전체 출력에 대한 assert
python -m pytest python/tests/test_sections_continue.py::test_weapon_phys_proxy_integration -v
```

**PASS**:
- 빌드 무기 주입된 케이스: `Class ==` 라인에 기대 Class만 포함, 다른 Class 유출 없음
- `HasExplicitMod "Tyrannical"` 등 T1 mod 라인 포함
- `HasExplicitMod = 0 "Heavy"` 등 저티어 배제 라인 포함
- strictness 1 vs strictness 3 비교: mod count 값이 2 → 3 변경 확인
- 빌드 무기 미유도 케이스: proxy 블록 부재 (regression)

### Step 6b. 인게임 스모크 (사용자 세션)

1. Sunder POB(2H Axe 메인)으로 필터 생성 → POE 필터 디렉토리 복사
2. 저레벨 존(AL 5~15) 입장
3. 확인:
   - Tyrannical 붙은 레어 2H Axe → 시안 스타 + 크게 표시
   - Heavy/Serrated 붙은 레어 2H Axe → L8 일반 레어색으로만 표시
   - 1H Axe 레어 → 일반 레어색 (빌드가 2H 전용이므로)
4. Bonesplitter용 듀얼 POB로 재생성 → 1H Axe도 강조되는지 확인

**PASS**: 4개 체크포인트 모두 육안 확인.

## 위험 / 미해결

### 리스크 1: POE mod 이름 변경
- mod 이름(Tyrannical, Merciless 등)은 GGG가 패치로 바꾸는 경우 드물게 있음
- 완화: `data/weapon_mod_tiers.json`에 `source` + `version` 기록, NeverSink 업데이트 추적
- 근본 대응: 프로젝트 밖 (NeverSink 업스트림 의존)

### 리스크 2: 트랜지션 빌드 처리
- "레벨링 2H → 엔드게임 1H" 같은 스왑 빌드는 multi-POB로 명시해야 둘 다 잡힘
- 단일 POB이면 최종 장비의 클래스만 추출됨 — 레벨링 구간 miss
- 완화: L7 블록에 AL 조건 없이 emit (DropLevel만 체크). 레벨링 중이어도 빌드 무기 클래스 레어는 항상 감지

### 리스크 3: 무기 Class 명 GGG 영문 정확성
- POE 필터의 `Class ==`는 영문 정확명만 매칭 ("One Hand Axes" 복수형 등)
- 완화: `data/weapon_base_to_class.json`의 Class 값을 NeverSink 필터 Class 라인과 대조하여 ground truth 고정
- 검증: Step 1c 완료 시 NeverSink 1-REGULAR.filter 그레핑으로 일치 확인

### 리스크 4: base_type 미매핑 드롭
- 신규 POE 패치에서 베이스 추가 시 `weapon_base_to_class.json`에 없는 base_type 발생
- 완화: `extract_build_weapon_classes` 내부에서 매핑 누락 시 logger.warning + 해당 base 스킵
- 사용자는 경고 로그로 누락 인지 가능, 추가 후 재생성

### 미해결: 방어 베이스 + 악세서리 강조
- Phase D/E로 분리 (DoD 섹션 "범위 + 후속 Phase 타임라인" 참조)
- 본 Phase 완료 후 바로 착수 (각 4~6h, 같은 패턴 재활용)

## 추정 합계

- Step 1 데이터 (mod + base→Class + gem→req): 1.5h
- Step 2 weapon_class_extractor: 2h
- Step 3 build_extractor 통합: 1h
- Step 4 sections_continue L7 확장: 3h
- Step 5 빌드/타입: 0.1h
- Step 6a 자동 스모크: 0.2h
- Step 6b 인게임: 사용자
- **합계: ~7.8h 구현 + 인게임 1회**

## 커밋 단위

1. `feat: weapon 관련 데이터 사전 3종 (mod-tier / base-to-class / gem-weapon-req)` (Step 1)
2. `feat: POB → weapon class extractor + 테스트` (Step 2+3)
3. `feat: L7 weapon_phys mod-tier 프록시 블록 + 자동 스모크` (Step 4+6a)
4. `chore: 인게임 스모크 검증 기록` (Step 6b 후)

## 마일스톤

각 Step 완료 시 사용자 확인 ("1~2개씩 구현→확인" 규칙). 특히 Step 2
(weapon class 유도)는 POB 파싱 정확성이 전체 정확성을 좌우하므로 스냅샷
테스트 박제 후 반드시 사용자 리뷰.
