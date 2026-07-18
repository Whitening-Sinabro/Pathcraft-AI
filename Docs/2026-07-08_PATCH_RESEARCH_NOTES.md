# 3.22-3.28 Patch Research Notes

작성 시각: 2026-07-08 11:57 +07:00

## 공식 패치/리그 확인

웹 확인 기준:

- `3.22` Trial of the Ancestors, 2023-08-18
- `3.23` Affliction, 2023-12-08
- `3.24` Necropolis, 2024-03-29
- `3.25` Settlers of Kalguur, 2024-07-26
- `3.26` Secrets of the Atlas, 2025-06-13
- `3.27` Keepers of the Flame
- `3.28` Mirage

현재 `3.29`는 live corpus 대상이 아니라 watchlist로 유지.

## 근거 레이어

1. 웹: 패치/리그명과 출시 타임라인 확인
2. 로컬 curated transition patterns: archetype 후보의 상시 강도 확인
3. 로컬 raw transition patterns: patch-specific community 흔적 확인
4. 로컬 transcript evidence: 3.28 Strength Stacker Jugg 사례 확인
5. 로컬 patch note corpus: 3.27, 3.28 skill signal 확인

## patch별 1차 후보 해석

### 3.22 Trial of the Ancestors

현재 로컬 patch-specific 신호는 약함.
보수적 후보:

- Lightning Arrow 계열
- Toxic Rain 계열
- Lightning Strike 계열
- Spark 계열
- Scourge Arrow 계열

상태:

- `2 / 5 seeded`
- 나머지는 `needs_patch_verification`

### 3.23 Affliction

로컬 patch-specific raw 데이터가 사실상 비어 있다.
다만 queue는 대표 후보 5개로 맞췄다.

- Penance Brand of Dissipation Inquisitor
- Lightning Arrow Deadeye
- Toxic Rain Ranger
- Righteous Fire Chieftain
- Detonate Dead caster

상태:

- `1 / 5 seeded`
- `4 / 5 blocked_on_patch_specific_ingest`

### 3.24 Necropolis

현재 로컬 evidence 가장 양호.
우선 라벨링 후보:

- Penance Brand Inquisitor
- Righteous Fire Chieftain
- Detonate Dead caster
- Raise Spectre Necromancer
- Summon Skeletons Necromancer

상태:

- `5 / 5 seeded`

### 3.25 Settlers of Kalguur

raw trace와 curated transition을 합치면 대표 5개는 모두 seeded 가능 상태로 올라왔다.

- Lightning Arrow Deadeye
- Righteous Fire Chieftain
- Spark caster
- Ball Lightning caster
- Lacerate Duelist

상태:

- `5 / 5 seeded`
- 다만 `Ball Lightning`, `Lacerate`는 아직 `low-confidence real case`

### 3.26 Secrets of the Atlas

우선 라벨링 가능 후보:

- Ice Nova caster
- Earthquake Marauder
- Penance Brand Inquisitor
- Lightning Arrow Deadeye
- Ball Lightning caster

상태:

- `5 / 5 seeded`

### 3.27 Keepers of the Flame

로컬 raw trace가 `Ice Nova`, `Lacerate`, `Dominating Blow`, `Detonate Dead` 쪽 후보를 직접 지지한다.

- Ice Nova caster
- Vortex caster
- Lacerate Duelist
- Dominating Blow Guardian
- Detonate Dead caster

상태:

- `4 / 5 seeded`
- `Vortex`만 아직 `needs_patch_verification`

### 3.28 Mirage

현재 workspace에서 가장 강한 직접 evidence는 Strength Stacker Juggernaut transcript다.
다만 이건 `리그 대표 인기/친화 빌드`라기보다 `개인 목표/연습용 고난도 빌드`로 보는 게 맞다.
추가로 `3.28` patch notes에서는 `Penance Brand`, `Dominating Blow` 강화 신호가 있고 `Detonate Dead of Scavenging`는 약화 신호가 보인다.

대표 flagship 후보군:

- Penance Brand Inquisitor
- Dominating Blow Guardian
- Lightning Arrow Deadeye
- Ice Nova caster
- 미확정 1개 추가 ingest 필요

개인 target 후보:

- Strength Stacker Juggernaut (`personal_target`, non-flagship)

상태:

- `0 / 5 flagship seeded`
- `1 personal_target seeded`
- `Penance Brand`, `Dominating Blow`는 `needs_patch_verification`
- `Lightning Arrow`, `Ice Nova`는 `blocked_on_patch_specific_ingest`

strict 메모:

- `3.28_zenith_strength_stacker_juggernaut_v1`는 별도 flagship가 아니라 같은 archetype 내부 variant case다.
- `3.28_strength_stacker_juggernaut` 자체도 Connor Converse 기반 개인 연습/목표 빌드로 보고, 대표성 높은 리그 친화 flagship에서는 제외한다.
- 따라서 `3.28` coverage는 `flagship 0 / 5`, `personal target 1`로 세는 것이 맞다.

## 현재 결론

- patch명과 지원 범위는 충분히 고정됨
- representative flagship queue는 이제 `3.22~3.28` 전 patch에서 외부 교차검증 기준으로 한 차례 이상 재작성됐다
- 현재 seeded coverage는 `3.22~3.28` 전 patch에서 full 상태가 됐다
- 현재 효율이 가장 높은 후속 작업은 low-confidence/single-source 후보의 confidence upgrade 또는 제거다

## Queue Rewrite Wave 1

실제 operational queue에 먼저 반영한 수정:

- `3.22` flagship 후보를 `Shockwave Totems Hierophant / Boneshatter Juggernaut / Corrupting Fever Champion / Lightning Arrow Deadeye / Toxic Rain Pathfinder`로 교체
- `3.23` flagship 후보를 `Lightning Arrow Deadeye / Hexblast Miner Saboteur / Boneshatter Juggernaut / Ice Shot Deadeye / Shockwave Totems Hierophant`로 교체
- `3.28` flagship 후보에 `Shock Nova of Procession Hierophant`와 `Kinetic Fusillade of Detonation`을 추가하고, `Connor/Strength Stacker`는 `personal_target` 유지

남은 작업:

- 기존 seeded real-case와 새 flagship 후보 사이의 불일치 정리
- `3.24 Exsanguinate Mine`, `3.26 Siege Ballista`, `3.27 Pyroclast Mine` 추가 외부 근거 확보
- `3.26`과 `3.27`의 local-trace 의존 후보를 추가 교차검증으로 승격 또는 제거

## Queue Rewrite Wave 2

실제 operational queue에 추가 반영한 수정:

- `3.24` flagship 후보를 `Lightning Arrow Deadeye / Explosive Arrow Ballista Champion / Detonate Dead Ignite / Boneshatter Juggernaut / Exsanguinate Mine Trickster`로 교체
- `3.25` flagship 후보를 `Lacerate / Lightning Arrow / Boneshatter / Hexblast Miner / Lightning Strike` 축으로 교체
- `3.26` flagship 후보를 `Lightning Arrow / Boneshatter / Siege Ballista / Ice Nova / Ball Lightning` 혼합 큐로 교체
- `3.27` flagship 후보를 `Lacerate / Dominating Blow / Ice Nova / Toxic Rain / Pyroclast Mine` 축으로 교체

판단 메모:

- `3.24`, `3.25`는 외부 교차소스 우선도가 높아져 대표성은 개선됐지만 seeded coverage는 급감했다
- `3.26`, `3.27`은 여전히 source split이 남아 있으므로 mixed-confidence patch로 유지한다
- 다음 단계는 queue 교정이 아니라 real-case 적재와 confidence 승격이다


## Real-Case Seed Wave 3

실제 real-case 적재에 반영한 수정:

- `3.23 Boneshatter` 1건 추가로 `Affliction` coverage를 `1 / 5`까지 복구
- `3.24 Lightning Arrow / Explosive Arrow Ballista / Boneshatter`를 추가 적재해 `Necropolis`를 `4 / 5`까지 회복
- `3.25 Boneshatter / Hexblast`를 추가 적재해 `Settlers`를 `4 / 5`까지 회복
- `3.26 Siege Ballista`를 추가 적재해 `Secrets`를 `4 / 5`까지 회복
- `3.27 Toxic Rain`을 추가 적재해 `Keepers`를 `4 / 5`까지 회복

판단 메모:

- 이번 wave는 queue 설계보다 seeded corpus 정합성 복구가 목적이었다
- 새로 추가한 case는 전부 strict classifier 회귀와 validator를 통과했다
- 다음 단계부터는 coverage 숫자보다 각 미적재 후보의 증거 밀도를 올리는 쪽이 중요하다


## Final Seed Wave For 3.24~3.27

실제 real-case 적재에 추가 반영한 수정:

- `3.24 Exsanguinate Mine Trickster` 적재
- `3.25 Lightning Strike` 적재
- `3.26 Boneshatter Juggernaut` 적재
- `3.27 Pyroclast Mine Saboteur` 적재

판단 메모:

- `3.24~3.27`은 이제 queue 기준으로 `5 / 5` full seeded 상태다
- 하지만 `3.24 Exsanguinate`, `3.26 Boneshatter`, `3.27 Pyroclast`는 아직 single-source 기반이므로 confidence upgrade 대상이지 확정 종결 대상은 아니다
- 다음 집중 구간은 `3.22`, `3.23`, `3.28`이다


## Seed Wave For 3.22, 3.23, 3.28

실제 real-case 적재에 추가 반영한 수정:

- `3.22 Shockwave Totem / Boneshatter / Corrupting Fever` 적재
- `3.23 Lightning Arrow / Hexblast / Ice Shot / Shockwave Totem` 적재
- `3.28 Shock Nova / Kinetic Fusillade / Dominating Blow / Penance Brand / Cold Snap` 적재

판단 메모:

- `3.22~3.28`은 이제 queue 기준 full seeded 상태다
- 하지만 `3.28` flagship 다수는 single-source 또는 patch-note 중심 근거이므로 provisional seeded로 봐야 한다
- 다음 단계는 coverage 확대가 아니라 confidence 분포 정상화다


## Confidence Split Layer

운영상 추가한 원칙:

- `seeded_into_real_cases_v1`는 coverage 충족 여부만 의미한다
- `source_status = provisional_seeded` 또는 `confidence = low`인 case는 confirmed로 세지 않는다
- 따라서 `coverage_ratio`와 `confirmed_coverage_ratio`를 분리해 본다

현재 우선순위:

- `3.28` flagship 전반 confidence upgrade
- `3.27` PoE Vault 단일소스 후보 재검증
- `3.26` single-source 후보 재검증
- `3.22/3.23 Shockwave Totem` 추가 교차검증


## Provisional Tightening

추가 운영 원칙:

- provisional 판정은 `low confidence` 자체가 아니라 `source_status = provisional_seeded`로만 센다
- `Shock Nova of Procession`, `Dominating Blow`처럼 2축 근거가 이미 있는 후보는 confirmed 쪽으로 복구한다
- 반대로 `3.26`, `3.27`, `3.28`의 single-source 후보는 명시적으로 provisional 유지한다

현재 confirmed 우선순위:

- `3.26` 보강이 최우선
- 그 다음 `3.27 Pyroclast / Ice Nova / Toxic Rain`
- 그 다음 `3.28 Kinetic Fusillade / Penance Brand / Cold Snap`


## Confidence Audit Queue

추가 도구:

- `python/build_variant_confidence_audit.py`

현재 audit priority 상단:

- `3.26 Boneshatter Juggernaut`
- `3.26 Siege Ballista Hierophant`
- `3.27 Pyroclast Mine Saboteur`
- `3.28 Cold Snap of Power Hierophant`
- `3.28 Kinetic Fusillade of Detonation`
- `3.28 Penance Brand Inquisitor`

운영 의미:

- 다음 검증 순서가 문서가 아니라 실행 결과로 고정된다
- provisional 정리는 `3.26 -> 3.27 -> 3.28` 순으로 밀어붙이는 게 가장 효율적이다


## Evidence Consistency Audit

추가 도구:

- `python/build_variant_evidence_consistency_audit.py`

현재 해석:

- 일부 후보는 confidence 문제가 아니라 queue external evidence가 real-case evidence에 아직 옮겨지지 않은 ingest 문제다
- 특히 `3.22 Lightning Arrow`, `3.24 Detonate Dead`, `3.27 Dominating Blow`는 외부 근거 재수집보다 evidence 정규화가 먼저다
- 반대로 `3.26`, `3.28` 일부 후보는 실제로 source gap이 남아 있다
