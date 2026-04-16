# NeverSink 필터 `weapon_phys` 블록 분석

> 출처: `_analysis/neversink_8.19.0b/NeverSink's filter - 1-REGULAR.filter`
> NeverSink v8.19.0b, 섹션 `[[0600]] IDENTIFIED MOD FILTERING > [0601] Physical`
> 라이선스: LICENSE 파일 부재. 공식 repo `github.com/NeverSinkDev/NeverSink-Filter`
> 본 문서는 mod 이름 리스트만 참조 (POE 게임 데이터). 룰 구조는 PathcraftAI에서 재작성.

## 블록 1 — `weapon_phys` (엄격, :812-826)

```
Show # %D5 $type->rareid $tier->weapon_phys
    Identified True
    DropLevel >= 50
    Rarity Rare
    Class == "Bows" "Claws" "Daggers" "One Hand Axes" "One Hand Maces" "One Hand Swords" "Thrusting One Hand Swords" "Two Hand Axes" "Two Hand Maces" "Two Hand Swords" "Wands" "Warstaves"
    HasExplicitMod "Merciless" "Tyrannical" "Cruel" "of the Underground" "Subterranean" "of Many" "of Tacati" "Tacati's"
    HasExplicitMod >=3 "Merciless" "Tyrannical" "Flaring" "Dictator's" "Emperor's" "of Celebration" "of Incision" "of Dissolution" "of Destruction" "of the Underground" "Subterranean" "of Many" "of Tacati" "Tacati's" "Veil"
    HasExplicitMod =0 "Heavy" "Serrated" "Wicked" "Vicious" "Glinting" "Burnished" "Polished" "Honed" "of Needling" "of Skill"
    SetFontSize 45
    SetTextColor 0 240 190 255
    SetBorderColor 0 240 190 255
    SetBackgroundColor 47 0 74 255
    PlayAlertSound 3 300
    PlayEffect Purple
    MinimapIcon 1 Purple Diamond
```

**조건 해석:**

| 줄 | 조건 | 의미 |
|----|------|------|
| `Identified True` | | 감정된 레어만 (미감정은 mod 텍스트 읽기 불가) |
| `DropLevel >= 50` | | 레벨링 초반(베이스 티어 낮음) 배제 |
| `Rarity Rare` | | 레어만 |
| `Class == ...` | 12 무기 클래스 | 물리 무기 가능 클래스 (Sceptres/Staves/Rune Daggers 제외 — 스펠 베이스) |
| `HasExplicitMod "..."` (첫 줄) | **최소 1개** "필수 prefix/suffix 있어야" | T1~T2 flat phys 또는 T1 공격속도 suffix 중 하나라도 있으면 통과 |
| `HasExplicitMod >=3 "..."` | **3개 이상** 좋은 mod | 조합된 좋은 mod 풀 (prefix + suffix 통합) |
| `HasExplicitMod =0 "..."` | **0개** bad mod | 저티어 phys mod 있으면 제외 |

**색/표시**: 시안 텍스트 + 보라 배경 + 보라 다이아 미니맵 + 소리 3.

## 블록 2 — `weapon_physpure` (완화, :828-844)

```
Show # %D5 $type->rareid $tier->weapon_physpure
    Mirrored False
    Corrupted False
    Identified True
    DropLevel >= 50
    Rarity Rare
    Class == "Bows" "Claws" "Daggers" "One Hand Axes" "One Hand Maces" "One Hand Swords" "Thrusting One Hand Swords" "Two Hand Axes" "Two Hand Maces" "Two Hand Swords" "Wands" "Warstaves"
    HasExplicitMod "Merciless" "Tyrannical" "Cruel" "of the Underground" "Subterranean" "of Many" "of Tacati" "Tacati's"
    HasExplicitMod >=2 "Merciless" "Tyrannical" "Flaring" "Dictator's" "Emperor's" "of Celebration" "of Incision" "of Dissolution" "of Destruction" "of the Underground" "Subterranean" "of Many" "of Tacati" "Tacati's" "Veil"
    HasExplicitMod =0 "Heavy" "Serrated" "Wicked" "Vicious" "Glinting" "Burnished" "Polished" "Honed" "of Needling" "of Skill"
    ... (색 동일)
```

**블록 1 대비 차이:**
- `>=3` → `>=2` (좋은 mod 개수 완화)
- `Mirrored False` + `Corrupted False` 추가 (수정 가능한 아이템만)

**논리**: mod 개수 낮추되(관대) 수정 불가한(미러/타락) 아이템은 배제(엄격). 트레이드오프.

## Mod 의미 주석

### Good mods — flat physical prefix

| Mod | POE 티어 | 효과 (요약) |
|-----|---------|--------------|
| `Tyrannical` | T1 | +flat phys damage, 최고 티어 |
| `Merciless` | T2 | +flat phys damage |
| `Cruel` | T3 | +flat phys damage (약간 낮은 티어, 블록 1 첫 줄에만 등장) |

### Good mods — % physical prefix

| Mod | POE 티어 | 효과 |
|-----|---------|------|
| `Emperor's` | T1 | %증가 phys |
| `Dictator's` | T2 | %증가 phys |
| `Flaring` | T1~T2 | %phys + added phys |

### Good mods — hybrid / 특수 prefix

| Mod | 의미 |
|-----|------|
| `Veil` | Veiled mod (감정 시 원하는 mod로 해제 가능) |

### Good mods — suffix (공격속도/크리)

| Mod | 의미 |
|-----|------|
| `of the Underground` | attack speed T1 (maven influence) |
| `Subterranean` | attack speed T1~T2 |
| `of Many` | +attack speed, multi-roll |
| `of Tacati` / `Tacati's` | crit strike T1 (Ultimatum mod) |
| `of Celebration` | hybrid crit suffix |
| `of Incision` | +accuracy, phys |
| `of Dissolution` | 원소 phys 혼합 |
| `of Destruction` | 원소 phys 혼합 T1 |

### Bad mods — 배제 대상

| Mod | 이유 |
|-----|------|
| `Heavy`, `Serrated`, `Wicked`, `Vicious` | flat phys T4~T7 (저티어) |
| `Glinting`, `Burnished`, `Polished`, `Honed` | %phys T4~T7 (저티어) |
| `of Needling`, `of Skill` | accuracy 저티어 |

이들 mod 중 하나라도 있으면 prefix/suffix 슬롯이 낭비된 아이템 → 전체 제외.

## PathcraftAI 매핑

PathcraftAI `_STRICTNESS_WEAPON_MOD_COUNT`:

| strictness | 블록 | 대응 NeverSink 블록 |
|------------|------|---------------------|
| 0~1 | mod count >=2 + Mirrored False + Corrupted False | `weapon_physpure` (:828-844) |
| 2+ | mod count >=3 | `weapon_phys` (:812-826) |

**차용할 mod 이름 리스트 (가공 없이 그대로)**:
- 블록 1 첫 줄 (필수 mod): `Merciless, Tyrannical, Cruel, of the Underground, Subterranean, of Many, of Tacati, Tacati's`
- 블록 1 `>=N` 줄 (카운트 대상): `Merciless, Tyrannical, Flaring, Dictator's, Emperor's, of Celebration, of Incision, of Dissolution, of Destruction, of the Underground, Subterranean, of Many, of Tacati, Tacati's, Veil`
- 블록 1 배제 mod: `Heavy, Serrated, Wicked, Vicious, Glinting, Burnished, Polished, Honed, of Needling, of Skill`

## Class 리스트 (ground truth)

12개 Class가 NeverSink의 "물리 무기 가능" 집합:

```
"Bows" "Claws" "Daggers" "One Hand Axes" "One Hand Maces" "One Hand Swords"
"Thrusting One Hand Swords" "Two Hand Axes" "Two Hand Maces" "Two Hand Swords"
"Wands" "Warstaves"
```

**주의**: Sceptres, Staves, Rune Daggers, Fishing Rods는 제외 (물리 스킬에 부적합).
PathcraftAI의 `weapon_base_to_class.json`도 이 12 Class를 ground truth로.

## 업스트림 추적

- NeverSink 신규 버전 릴리스 시 이 문서 기준으로 diff 확인
- GGG 패치로 mod 이름 변경 시 NeverSink가 먼저 반영 → 우리가 따라감
- 점검 주기: 리그 시작 직후 1회 + 월 1회
