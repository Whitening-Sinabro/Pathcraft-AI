# POE1 Recommendation Filter System

작성 시각: 2026-07-09 +07:00

## 목적

최종 목표는 `PoB/PoBB -> 빌드 프로필화 -> 현재 유저 상태 기준 추천`이다.
여기서 중요한 것은 단순 추천이 아니라 `맞춤 필터`와 `적대적검증`이다.

이 문서는 PathcraftAI가 아래 조건을 함께 처리할 수 있도록 운영 규칙을 정의한다.

- 특정 스킬젬 선호
- `0_button` / `1_click` 같은 입력 복잡도 제한
- 현재 커런시
- 현재 캐릭터 클래스/전직/레벨
- 리그 스타트 / SSF / 트윙크 여부
- 맵핑 / 보싱 / Sanctum 같은 목표 콘텐츠

## 핵심 객체

### 1. build_profile

빌드 자체의 정규화 레코드다.

반드시 포함해야 하는 축:

- `identity`: 패치, 클래스, 전직, 메인 스킬, 레벨링 스킬
- `playstyle`: 입력 복잡도, 이동 의존도, 수동 조작량
- `budget_curve`: 입문 비용, 쾌적 비용, 고예산 비용
- `availability`: 리그 스타트, SSF, HC, 트윙크 적합성
- `progression`: 캠페인, 전환 시점, 조기 맵핑 진입 난이도
- `suitability`: 맵핑/보싱/특정 콘텐츠 점수
- `confidence`: 대표 빌드 확정성, 레벨링 확정성, 소스 강도

### 2. user_state

추천 대상 유저의 현재 상태다.

반드시 포함해야 하는 축:

- `character_state`: 현재 클래스, 전직, 레벨, 기존 캐릭터 고정 여부
- `currency_state`: liquid currency, 보유 유니크, 링크/크래프팅 여력
- `preferences`: 선호 스킬, 입력 한도, 목표 콘텐츠, 죽음 허용도
- `constraints`: 반드시 지켜야 하는 조건과 절대 금지 조건

### 3. validation_result

추천 전에 남겨야 하는 감사 결과다.

- 어떤 조건이 `hard constraint` 인지
- 어떤 조건이 `soft constraint` 인지
- 무엇이 충돌했는지
- 무엇을 어느 순서로 완화했는지
- 최종 추천이 `Plan A/B/C/D` 중 어디인지

## 하드 제약과 소프트 제약

### 하드 제약

절대 자동 완화하면 안 된다.

- 유저가 `must_use_skill` 로 고정한 스킬
- 유저가 `max_input_style = 0_button` 로 고정한 경우
- `trade_mode = ssf` 인데 빌드가 사실상 거래 필수
- 현재 캐릭터 고정인데 클래스/전직 변경이 불가능한 경우
- 유저 예산이 빌드 진입 비용보다 현저히 낮은 경우
- 패치가 다르거나, 빌드가 현재 패치에서 폐기된 경우

### 소프트 제약

결과가 없을 때 순차 완화할 수 있다.

- 맵핑 점수 최소치
- 보싱 점수 최소치
- 이동 속도 선호
- death tolerance
- respec 허용 포인트
- “꼭 meta일 필요는 없음” 같은 취향성 조건

## 필터 파이프라인

반드시 아래 순서로 적용한다.

### 1. Patch Guard

- 현재 패치와 build_profile patch 정합성 확인
- 구버전 빌드라도 현재 패치 생존성이 검증되지 않으면 컷

### 2. Character Guard

- 유저가 기존 캐릭터를 유지해야 하는지 확인
- 현재 클래스/전직과 build_profile 간 전환 가능성 계산

### 3. Availability Guard

- `trade / ssf / twink / league_start` 모드 매칭
- 필수 유니크/트랜스피겨드 젬 존재 여부 확인

### 4. Input Guard

- `0_button`, `1_click`, `1_click_plus_movement`, `2_button`, `multi_button`
- 유저 상한보다 높은 입력 스타일은 컷

### 5. Skill Guard

- 유저가 원하는 메인 스킬과 build_profile 메인 스킬 비교
- exact match 우선
- 없으면 같은 archetype proxy 후보만 별도 풀에 보관

### 6. Budget Guard

- 현재 liquid currency와 entry cost 비교
- 예산이 부족하면 즉시 컷하지 말고 `budget_fit_ratio` 계산

기본 권장값:

- `Plan A`: `budget_fit_ratio <= 1.00`
- `Plan B`: `budget_fit_ratio <= 1.35`
- `Plan C`: `budget_fit_ratio <= 1.80`
- `Plan D`: `budget_fit_ratio > 1.80`

### 7. Confidence Guard

- 대표 빌드 상태가 `confirmed` 또는 `near_confirmed` 인지 우선 확인
- `hold` 는 더 나은 후보가 없을 때만 후보 풀에 남긴다
- 캠페인 생성까지 해야 하면 `leveling_confidence` 도 별도 확인

### 8. Ranking

후보가 남았을 때만 점수화한다.

권장 가중치:

- `skill_match_score`: 25
- `input_fit_score`: 20
- `budget_fit_score`: 20
- `character_fit_score`: 15
- `content_fit_score`: 10
- `availability_fit_score`: 5
- `confidence_score`: 5

## 자동 완화 규칙

조건이 과도하면 무작정 다 풀면 안 된다.
반드시 `soft -> softer -> proxy -> abstain` 순서로 간다.

### 완화 순서

1. 콘텐츠 점수 최소치 완화
2. 이동감/쾌적성 선호 완화
3. respec 허용 포인트 완화
4. exact skill match 실패 시 same-archetype proxy 허용
5. 그래도 없으면 추천 보류

### 절대 완화 금지

- max input style
- must-use skill
- ssf/trade 강제 모드
- 캐릭터 고정 조건
- 패치 생존성

## 적대적검증 항목

추천 엔진은 아래 실패 패턴을 정면으로 막아야 한다.

### 1. 불가능한 요구 묶음

예시:

- `0_button`
- `league_start`
- `ssf`
- `uber bossing`
- `0.5 div`
- `current character locked`

조치:

- 즉시 `impossible_bundle` 플래그
- 추천 대신 어느 제약이 충돌하는지 반환
- 우선 완화 대상은 소프트 제약뿐

### 2. 과도한 필터

증상:

- 후보 수 0
- hard constraint는 문제 없는데 soft constraint만 너무 많음

조치:

- soft constraint 완화 로그 생성
- 완화 후에도 0이면 `Plan C` 또는 `Plan D`

### 3. 조건 부족

증상:

- 원하는 스킬만 있고 예산/캐릭터/모드 정보가 거의 없음

조치:

- broad candidate pool 생성
- confidence 높은 대표 빌드만 우선 노출
- 부족한 입력은 별도 `missing_inputs` 로 기록

### 4. 빌드 프로필 과장

증상:

- `league_start_viable = true` 인데 entry cost가 과하게 높음
- `confirmed` 라고 적혀 있는데 소스가 1개뿐
- `confirmed leveling` 인데 transition timeline 없음

조치:

- profile audit에서 강등
- `confirmed -> near_confirmed` 또는 `near_confirmed -> hold`

### 5. 패치 드리프트

증상:

- 구패치에서는 대표 빌드였지만 현재 패치에서는 너프/삭제

조치:

- patch survival 검증 통과 전까지 `historical_only`
- 현재 추천 풀에서는 제외

### 6. 현재 캐릭터 함정

증상:

- 유저는 이미 `Templar 92` 인데 빌드는 `Deadeye` 기반
- 새 캐릭 생성이 아니라 전환만 원함

조치:

- 새 캐릭 전제 추천을 금지
- 같은 클래스/전직 또는 합리적 respec 범위 후보만 유지

## 해결방안 / 우회방안

### 해결방안

- build_profile을 더 엄격하게 만든다
- user_state의 하드 제약을 먼저 분리한다
- 추천 이전에 profile audit를 통과시킨다
- 결과가 0일 때는 soft constraint만 단계적으로 완화한다

### 우회방안

- exact skill이 없으면 same-archetype proxy를 제시한다
- 예산이 부족하면 해당 빌드의 starter phase만 분리 추천한다
- 현재 캐릭터가 안 맞으면 reroll 추천과 in-place respec 추천을 분리한다

## Plan A / B / C / D

### Plan A

정확 일치 추천.

조건:

- hard constraint 모두 충족
- budget fit 양호
- input fit 일치
- confidence 충분

### Plan B

근접 추천.

조건:

- hard constraint 모두 충족
- 일부 soft constraint만 완화
- exact skill 또는 동일 archetype 유지

### Plan C

우회 추천.

조건:

- exact skill 또는 exact character fit은 실패
- 대신 현재 유저 상태에서 실제 플레이 가능한 proxy 빌드 제시

예시:

- 원하는 최종 스킬은 고예산이라 불가
- 동일 클래스 기반 starter를 먼저 추천

### Plan D

추천 보류.

조건:

- hard constraint 충돌
- 패치 생존성 불명
- 입력 누락이 너무 큼
- 검증되지 않은 `hold` 빌드밖에 없음

반환값에는 반드시 아래가 있어야 한다.

- 왜 추천하지 않았는지
- 어떤 조건을 완화하면 되는지
- 어떤 추가 데이터가 있으면 A/B/C로 승격되는지

## 운영 로그

매 추천마다 아래 trace를 남긴다.

- `hard_rejections`
- `soft_rejections`
- `relaxation_steps`
- `selected_plan`
- `selected_build_id`
- `fallback_candidates`
- `missing_inputs`

## 최소 출시 기준

아래가 안 되면 실사용 추천 엔진으로 보면 안 된다.

- build_profile audit 존재
- user_state audit 존재
- impossible bundle 탐지 존재
- soft constraint auto-relaxation 존재
- `Plan D` abstain 반환 존재
- hold 빌드 억제 규칙 존재
- 현재 캐릭터 기준 reroll/in-place 구분 존재
