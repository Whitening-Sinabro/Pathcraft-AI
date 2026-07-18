# POE1 Build Variant Model V2

## 목적

이 문서는 POE1 빌드 코퍼스에서 `variant` 과분기 문제를 줄이기 위해
`archetype -> sub_archetype -> variant -> phase_state` 4계층 모델을 정의한다.

핵심은 아래 네 가지를 서로 다른 레벨에서 처리하는 것이다.

- 엔진 차이
- 예산 차이
- 진행 단계 차이
- 콘텐츠 특화 차이

기존 문제는 이 네 가지를 전부 `variant` 하나에 몰아넣었다는 점이다.

## 계층 정의

### 1. archetype

가장 큰 빌드 정체성.

예:

- `strength_stacker_juggernaut`
- `lightning_arrow_deadeye`
- `hexblast_miner_trickster`

판단 기준:

- 같은 클래스/어센던시 뼈대
- 같은 장기 성장 방향
- 같은 핵심 스탯/메커닉 축

### 2. sub_archetype

`주 딜 엔진` 또는 `주 방어 엔진`이 다른 경우의 강제 분기 레벨.

예:

- `strength_stacker_juggernaut.holy_static_progression`
- `strength_stacker_juggernaut.zenith_strength_stacker`
- `strength_stacker_juggernaut.heavy_strike_crit_stacker`

판단 기준:

- 메인 스킬 이름이 아니라 `주 딜 엔진`이 바뀌는지 본다
- 주 방어 엔진이 바뀌는지 본다
- 필수 유니크 게이트가 바뀌는지 본다

### 3. variant

같은 sub_archetype 안에서 예산/세부 세팅 차이를 표현한다.

예:

- `budget`
- `mid`
- `high_end`
- `mirror`

variant는 엔진이 같은 상태에서만 유지된다.

### 4. phase_state

같은 variant 안의 진행 단계다.

- `campaign`
- `maps_entry`
- `early_endgame`
- `mid_endgame`
- `late_endgame`

phase_state는 `운영 상태 변화`이며, 별도 빌드로 분기하지 않는다.

## 강제 분기 규칙

아래 중 하나라도 참이면 `sub_archetype` 분기다.

1. `damage_engine` 변경
- 예: hit -> dot
- 예: self attack -> projectile trigger
- 예: static chain clear 엔진 -> single-hit crit 엔진

2. `defense_engine` 변경
- 예: life armour -> ES CI
- 예: generic armour stack -> block 기반 흡수 세팅
- 예: hybrid str/es divine shield -> pure life berserk rush

3. `core_unique_gate` 변경
- 특정 유니크가 없으면 빌드가 성립하지 않거나
- 유니크 획득 전후로 엔진이 완전히 달라지는 경우

4. `tree_shape_class` 변경
- 키스톤 축 교체
- 대형 클러스터 도입/제거
- 무기 전용 휠 축 전환
- attribute stack -> crit stack 같은 구조 전환

5. `play_pattern` 변경
- stationary bosser -> zoom mapper
- auto-chain clear -> strike-range melee bossing

중요:

- `메인 스킬 이름 변경`만으로는 강제 분기하지 않는다
- 반드시 `damage_engine`, `defense_engine`, `core_unique_gate`, `tree_shape_class`, `play_pattern` 중 하나와 연결되어야 한다

## variant 분기 규칙

같은 sub_archetype 안에서 아래를 본다.

### 예산 tier

- `starter`
- `budget`
- `mid`
- `high_end`
- `mirror`

### variant 강제 분기

아래 중 하나면 별도 variant다.

1. `budget_tier`가 2단계 이상 차이남
2. `core gear package`가 3개 이상 바뀜
3. 동일 엔진이지만 `aura package`와 `cluster package`가 동시에 바뀜
4. 동일 엔진이지만 추천 콘텐츠가 완전히 뒤집힘
- 예: generic mapper -> delve-specialized
- 단, 콘텐츠 태그만 늘어난 건 분기 사유가 아니다

### variant 비분기

아래는 phase_state 변화로 본다.

- 저항/생명/에쉴 수치 개선
- 링크 1~2개 업그레이드
- 같은 오라 패키지 안의 예약 미세조정
- 희귀 아이템의 티어 향상
- 동일 엔진 내 단순 DPS 상승

## phase_state 분기 규칙

phase_state는 같은 variant 안에서만 존재한다.

### 허용 변화

- 링크 수 증가
- 희귀 장비 업그레이드
- life/resist checkpoint 변화
- flask 개선
- gem level 상승
- 동일 세팅 내 passive point 확장

### phase_state를 넘어서면 안 되는 변화

아래가 발생하면 phase_state가 아니라 variant 또는 sub_archetype 재판정이다.

- 딜 엔진 변경
- 방어 엔진 변경
- 필수 유니크 게이트 도달
- 플레이 패턴 급변

## evidence 규칙

분기 판단은 evidence 최소 요건을 만족해야 한다.

### sub_archetype 분기 최소 요건

- 아래 중 2개 이상
- `pob`
- `video_transcript`
- `video_description`
- `forum_guide`
- `manual_curated` 단독으로는 불가

### variant 분기 최소 요건

- 아래 중 1개 이상
- `pob`
- `poe_ninja`
- `video_transcript`
- `forum_guide`

### phase_state 기록 최소 요건

- transcript 또는 manual_curated 허용

## 세부 판정 필드

각 비교는 아래 필드로 수행한다.

- `damage_engine`
- `defense_engine`
- `core_unique_gate`
- `tree_shape_class`
- `play_pattern`
- `budget_tier`
- `aura_package_id`
- `cluster_package_id`
- `content_specialization`

## split 판정표

### sub_archetype split

아래 중 하나면 split:

- `damage_engine` 다름
- `defense_engine` 다름
- `core_unique_gate` 다름
- `tree_shape_class` 다름
- `play_pattern` 다름

### variant split

sub_archetype가 같고, 아래 중 하나면 split:

- `budget_tier_distance >= 2`
- `gear_package_delta >= 3`
- `aura_package_changed && cluster_package_changed`
- `content_specialization`이 `generic`에서 `specialized`로 바뀜

### phase_state only

sub_archetype와 variant가 같고 아래만 달라지면 phase_state:

- defensive thresholds
- link count
- item tier quality
- gem levels
- flask quality

## Strength Stacker Juggernaut 예시

### archetype

- `strength_stacker_juggernaut`

### sub_archetypes

1. `holy_static_progression`
- campaign and early mapping
- accuracy/lab spike 기반

2. `zenith_strength_stacker`
- Alberon's 이후 중자본 파밍형
- projectile/hit 기반

3. `heavy_strike_crit_stacker`
- 더블 인플 헬멧 기반
- crit and fortify endgame형

### variants

`zenith_strength_stacker`
- `budget`
- `mid`
- `high_end`

`heavy_strike_crit_stacker`
- `high_end`
- `mirror`

### phase_states

`zenith_strength_stacker.mid`
- `maps_entry`
- `early_endgame`
- `mid_endgame`

`heavy_strike_crit_stacker.high_end`
- `early_endgame`
- `late_endgame`

## 운영 지침

1. 먼저 archetype를 정한다.
2. 다음으로 딜/방어 엔진을 보고 sub_archetype를 정한다.
3. 같은 sub_archetype 안에서 예산/세팅 차이를 보고 variant를 정한다.
4. 마지막으로 진행 정도만 phase_state로 기록한다.

이 순서를 어기면 과분기 또는 과병합이 발생한다.
