# POE1 Build Corpus Progress Report

작성 시각: 2026-07-08 11:55 +07:00  
목표 시각: 2026-07-08 12:30 +07:00 형식 보고서 기준 중간본

## 2026-07-17 Handoff: Continue Corpus Collection

다음 세션의 중심은 특정 빌드 추천이 아니라 `3.22`부터 `3.29`까지 실제 빌드 사례를 계속 수집하고, Pathcraft AI가 사용할 수 있는 build corpus / candidate queue / source evidence DB로 정규화하는 것이다.

이어받을 원칙:

- 래딧, 공식 포럼, 커뮤니티 글, 빌드 사이트, 유튜브, PoB/pobb 링크, 패치노트, poe.ninja류 자료를 함께 수집한다.
- 단순히 시즌별 인기 빌드 5개를 고르는 작업이 아니다.
- 각 빌드를 `archetype / sub_archetype / variant / phase_state`로 나누고, `source_evidence / patch_delta / item_mod_pressure / passive_tree_shape / leveling-transition-endgame path / farming_fit`까지 파생 데이터로 연결한다.
- `3.22~3.28`은 confirmed collection target이고, `3.29`는 라이브/패치노트 반영 watchlist에서 점진적으로 confirmed 후보를 만든다.
- 방금 이야기한 Spectre 약화와 Dominating Blow 가능성은 `3.29 minion lane`의 부분 발견이다. `Dominating Blow Guardian`은 후보로 올리되, 다음 세션의 전체 목적을 이 빌드 하나로 좁히지 않는다.

우선 이어볼 데이터:

- `data/build_corpus_collection_targets_v1.json`
- `data/build_corpus_expanded_collection_queue_v1.json`
- `data/build_variant_collection_queue_v1.json`
- `data/build_variant_real_cases_v1.json`
- `data/build_corpus_manual_pob_sources_v1.json`
- `data/guide_sources/`
- `data/patch_notes/`
- `data/ggpk_derived/`

## 2026-07-17 Manual PoB Source Expansion

이번 이어가기 세션은 `manual_pob_sources -> pob_link_probe -> promote_ready_pobs -> promoted_case_snapshots` 경로를 강화했다.

추가된 parser-validated 후보:

- `3.22_detonate_dead_elementalist`
- `3.22_hexblast_mines_saboteur`
- `3.22_poison_srs_necromancer`
- `3.24_archmage_ice_nova_hierophant`
- `3.24_detonate_dead_necromancer`
- `3.25_lightning_strike_slayer`
- `3.22_lightning_arrow_deadeye`
- `3.22_spark_inquisitor`
- `3.22_minion_army_necromancer`
- `3.23_storm_brand_inquisitor`
- `3.23_guardian_srs`
- `3.23_poison_srs_necromancer`
- `3.23_caustic_arrow_poison_ballista`
- `3.27_ice_nova_hierophant`
- `3.27_lightning_arrow_deadeye`
- `3.27_raise_spectre_necromancer`
- `3.27_poison_srs_necromancer`
- `3.28_kinetic_fusillade_totem_hierophant`
- `3.28_holy_flame_totem_hierophant`
- `3.28_raise_spectre_necromancer`
- `3.28_summon_holy_relic_necromancer`

산출 변화:

- manual source records: `6 -> 28`
- direct PoB candidates: `6 -> 60`
- ready-for-parse candidates: `5 -> 27`
- promoted artifacts: `6 -> 50`
- promoted state snapshots: `83 -> 403`

남은 관찰:

- 재실행 시 기존 `3.23_boneshatter_slayer` 수동 링크 `https://pobb.in/8EaecQiFSzV0`도 정상 파싱되어 promoted parse error는 `0`건이다.
- `build_corpus_promote_ready_pobs.py`는 이미 생성된 parsed artifact가 있으면 네트워크 재요청 없이 재사용하도록 보강했다. pobb.in DNS/500 변동으로 promotion 최신 산출물이 흔들리는 문제를 줄이기 위한 조치다.
- 사용자 확인 후 기존 접근 실패 후보 대부분을 재파싱해 반영했다. 남은 예외는 `https://pobb.in/fW_6P92WqLcS` 하나로, 접근은 가능하지만 Holy Relic 최종 상태가 아니라 SRS 레벨링 상태라 promotion 대상에서 제외했다.

## 1. 목적

POE1 빌드 코퍼스를 `단순 빌드 목록`이 아니라 아래 구조로 재설계하고, 내부 테스트가 가능한 수준까지 끌어올리는 것이 목표였다.

- `archetype`
- `sub_archetype`
- `variant`
- `phase_state`

추가 목표는 다음 두 가지였다.

- strict한 분기 규칙을 기본값으로 둔다.
- 조건이 과도하거나 부족할 경우 threshold와 toggle을 조정 가능하게 만든다.

## 2. 이번 작업 결과

### 2.1 스키마 및 모델 정리

추가/수정 파일:

- `Docs/POE1_BUILD_CORPUS_SCHEMA.md`
- `Docs/POE1_BUILD_VARIANT_MODEL_V2.md`
- `data/schema/poe1_build_corpus.schema.json`
- `data/schema/poe1_build_variant_model_v2.schema.json`
- `data/build_corpus_taxonomy.json`
- `data/build_corpus_support_matrix.json`
- `data/build_corpus_seed.example.json`
- `data/build_variant_seed_v2.example.json`

핵심 변경:

- 최소 지원 범위를 `3.22 ~ 3.28`로 고정
- `3.29`는 `watchlist`만 허용
- `variant` 과분기를 막기 위해 `sub_archetype / variant / phase_state` 분리 도입

### 2.2 분기 판정기 추가

추가 파일:

- `python/build_variant_model_v2.py`

핵심 기능:

- 입력 빌드 상태 2개를 비교해 아래 중 하나로 판정
  - `sub_archetype_split`
  - `variant_split`
  - `phase_state_only`
- strict 기본 규칙 제공
- 규칙 threshold/toggle 외부화 가능

### 2.3 규칙 프로파일 및 calibration 기록 구조 추가

추가 파일:

- `data/build_variant_rules_v2.json`
- `data/build_variant_rule_calibration_log.example.json`

의미:

- strict 기본값을 JSON 프로파일로 관리
- 오분류 사례가 나오면 어떤 규칙을 왜 완화했는지 기록 가능

### 2.4 실제 사례 적재 큐 강화

추가/수정 파일:

- `data/build_variant_collection_queue_v1.json`
- `data/build_variant_real_cases_v1.json`

핵심 변경:

- `3.23`, `3.28`도 대표 후보 수를 `5개` 기준으로 맞춤
- `3.25`에 `Ball Lightning`, `Lacerate` real case 추가
- `3.27`에 `Ice Nova`, `Dominating Blow` real case 추가
- `3.28`은 `flagship`과 `personal_target`을 분리
- `Connor Converse / Strength Stacker`는 `personal_target`으로 재분류

## 3. 테스트 결과

추가 테스트 파일:

- `python/tests/test_build_variant_model_v2.py`
- `python/tests/test_build_variant_classifier_v2.py`
- `python/tests/test_build_variant_real_cases_v1.py`
- `python/tests/test_build_variant_coverage_report.py`

최신 실행 결과:

```text
python -m pytest python/tests/test_build_variant_model_v2.py python/tests/test_build_variant_classifier_v2.py python/tests/test_build_variant_real_cases_v1.py python/tests/test_build_variant_coverage_report.py -q
23 passed, 1 warning in 0.12s
```

추가 검증:

```text
python D:\Pathcraft-AI\python\build_variant_case_validator.py
{"ok": true, "mismatch_count": 0}
```

주의:

- warning은 `.pytest_cache` 쓰기 권한 문제
- 모델 로직 실패는 아님

## 4. 현재 판단

### 4.1 된 것

- 설계가 아니라 실행 가능한 판정기로 내려옴
- strict baseline + 완화 가능 구조 확보
- calibration log 구조 확보
- representative flagship queue와 intra-archetype variant case를 분리하는 stricter coverage 규칙 반영
- real-case regression set이 `24건`까지 증가
- `personal_target` 빌드가 flagship coverage를 오염시키지 않도록 분리 완료

### 4.2 아직 안 된 것

- patch별 대표 빌드 5개를 `실증 데이터`로 모두 확정하지 못함
- `3.23`, `3.28`은 patch-specific ingest 부족
- `3.22`도 seeded는 늘었지만 여전히 검증 밀도가 낮음
- low-confidence case를 medium-confidence 이상으로 올릴 추가 evidence가 필요

## 5. 리스크

1. local transition data는 patch-specific 메타 판정에 여전히 노이즈가 있다.
2. curated transition data는 cross-patch archetype 강도는 보여주지만 flagship 확정 근거로는 부족할 수 있다.
3. real-case 수는 늘었지만 confidence 분포가 아직 low에 치우쳐 있다.
4. strict coverage를 유지할수록 `같은 archetype 내 세부 variant`를 대표 빌드 수로 착각하는 오류를 계속 경계해야 한다.
5. personal target 빌드는 빌드 난이도나 예산, 친화도와 무관하게 사용자 관심 때문에 데이터에 들어올 수 있으므로 대표성과 분리 관리가 필요하다.

## 6. 다음 작업 우선순위

1. `3.22`, `3.23`, `3.28`의 patch-specific ingest 강화
2. `3.27` 마지막 1개 flagship 후보 확정
3. low-confidence seeded case를 medium-confidence로 승격할 evidence 매핑
4. `build_coach`와 연결할 adapter 설계

## 7. 결론

현재 상태는 `strict 분기 엔진 안정화 + real-case 회귀셋 확장 + flagship coverage 정규화` 단계다.

병목은 설계가 아니라 `patch-specific evidence 밀도`다.  
특히 `3.23`, `3.28`은 대표 후보 5개 틀은 만들었지만, 아직 대부분이 ingest 대기 상태다.

## 8. Coverage Snapshot (13:35 +07:00)

현재 flagship coverage:

- `3.22`: 5 / 5
- `3.23`: 5 / 5
- `3.24`: 5 / 5
- `3.25`: 5 / 5
- `3.26`: 5 / 5
- `3.27`: 5 / 5
- `3.28`: 5 / 5

현재 personal target seeded:

- `3.28`: 1

현재 flagship seed density가 가장 높은 patch:

- `3.24`
- `3.25`
- `3.26`
- `3.27`

현재 가장 confidence upgrade가 필요한 patch:

- `3.28`
- `3.23`
- `3.22`

strict correction 메모:

- 기존 `3.28 2 / 5`는 과대평가였다.
- 이후 `3.28 1 / 5`로 한번 교정했지만, 그조차도 대표성 기준으로는 높게 잡힌 값이었다.
- `3.28_zenith_strength_stacker_juggernaut_v1`는 별도 flagship가 아니라 같은 archetype 내부 variant case다.
- 동시에 `Connor/Strength Stacker` 자체도 리그 대표 flagship이 아니라 `personal_target`로 분리해야 한다.
- 따라서 현재 `3.28` 평가는 `flagship 0 / 5 + personal_target 1`이 맞다.

추가 calibration 포인트:

- `3.26_ball_lightning_caster_v1`에서 strict rule이 과분기하던 문제를 발견
- `Arc -> Ball Lightning`를 동일 `lightning spell hit` 엔진으로 정규화
- calibration log에 기록 완료

## 9. Internal Simulation Check (11:35 +07:00)

실행 항목:

- labeled pair 전수 재분류
- left/right 대칭성 확인
- state-level 단일 필드 교란 시뮬레이션
- threshold 민감도 시뮬레이션

결과:

- labeled pair 수: `35`
- expected 분포: `sub_archetype_split 13`, `variant_split 11`, `phase_state_only 11`
- actual 분포: expected와 완전 일치
- symmetry failure: `0`
- state-level mutation 총 `413`회 모두 의도한 방향으로 반응
  - `damage_engine`, `defense_engine`, `core_unique_gate`, `tree_shape_class`, `play_pattern` 교란 시 전부 `sub_archetype_split`
  - `content_specialization`을 `generic <-> bossing`으로 교란 시 전부 `variant_split`
  - `budget + package`를 함께 교란 시 전부 `variant_split`

민감도 해석:

- `variant_budget_distance_threshold = 1`로 낮추면 mismatch `11건`
- `variant_package_delta_threshold = 1`로 낮추면 mismatch `11건`
- 두 경우 모두 원래 `phase_state_only`여야 하는 `campaign -> maps` 전환을 과분기한다
- 따라서 현재 strict 기본값인 `budget_threshold = 2`, `package_threshold = 2`는 실케이스 회귀셋 기준에서 방어력이 있다
- `split_on_content_specialization_change = False`로 완화해도 현재 회귀셋에서는 mismatch `0건`이지만, 이는 데이터가 아직 보수적으로 구성돼 있다는 뜻이지 해당 규칙이 불필요하다는 뜻은 아니다

## 10. Queue Rewrite Wave 1 (12:35 +07:00)

외부 교차검증 매트릭스를 operational queue에 1차 반영했다.

적용 범위:

- `3.22`
- `3.23`
- `3.28`

핵심 교정:

- `3.22`에서 `Shockwave Totems Hierophant`를 flagship 후보로 복구
- `3.22`의 `Lightning Strike / Spark / Scourge Arrow` 중심 old queue를 `Shockwave Totem / Boneshatter / Corrupting Fever / Lightning Arrow / Toxic Rain` 축으로 재정렬
- `3.23`의 `Penance Brand` 중심 old queue를 제거하고 `Lightning Arrow / Hexblast Miner / Boneshatter / Ice Shot / Shockwave Totem` 축으로 교체
- `3.28` flagship 후보에 `Shock Nova of Procession Hierophant`, `Kinetic Fusillade of Detonation`을 반영
- `3.28`의 `Connor/Strength Stacker`는 계속 `personal_target`로 유지

반영 후 coverage 변화:

- `3.22`: `2 / 5` 유지
- `3.23`: `1 / 5`에서 `0 / 5`로 하락
  - 이유: 기존 seeded였던 `Penance Brand`를 대표 flagship에서 제외했기 때문
- `3.28`: `flagship 0 / 5 + personal_target 1` 유지

검증:

```text
python -m pytest python/tests/test_build_variant_coverage_report.py python/tests/test_build_variant_real_cases_v1.py python/tests/test_build_variant_classifier_v2.py python/tests/test_build_variant_model_v2.py -q
23 passed, 1 warning in 0.22s
```

의미:

- 이제 `3.22` queue는 최소한 `Shockwave Totem` 누락 오류에서는 벗어남
- `3.23` queue는 대표성 면에서 더 엄격해졌고, coverage 수치도 더 보수적으로 내려감
- `3.28`은 `Shock Nova`와 `Kinetic Fusillade`를 공식/외부 근거 기반 후보로 추적하기 시작함


## 11. Queue Rewrite Wave 2 (12:55 +07:00)

외부 교차검증 매트릭스를 `3.24~3.27` operational queue에도 반영했다.

적용 범위:

- `3.24`
- `3.25`
- `3.26`
- `3.27`

핵심 교정:

- `3.24` old queue의 `Penance Brand / RF / Spectre / Skeletons` 중심 구성을 `Lightning Arrow / Explosive Arrow Ballista / Detonate Dead Ignite / Boneshatter / Exsanguinate Mine` 축으로 교체
- `3.25` old queue의 `Spark / Ball Lightning / RF` 편향을 제거하고 `Lacerate / Lightning Arrow / Boneshatter / Hexblast / Lightning Strike` 축으로 재정렬
- `3.26`은 외부 단일 소스와 로컬 Reddit trace가 갈려 있어 `Lightning Arrow / Boneshatter / Siege Ballista`에 `Ice Nova / Ball Lightning` 로컬 신호를 혼합한 보수적 queue로 재작성
- `3.27`은 `Vortex / Detonate Dead`를 내리고 `Lacerate / Dominating Blow / Ice Nova / Toxic Rain / Pyroclast Mine` 조합으로 재정렬

반영 후 coverage 변화:

- `3.24`: `5 / 5`에서 `1 / 5`로 하락
- `3.25`: `5 / 5`에서 `2 / 5`로 하락
- `3.26`: `5 / 5`에서 `3 / 5`로 하락
- `3.27`: `4 / 5`에서 `3 / 5`로 하락

의미:

- 기존 seeded real-case가 representative flagship를 과대대표하던 patch가 정리됐다
- 이제 coverage는 더 낮지만, patch별 인기/유행 빌드라는 요구에 더 가깝다
- 다음 병목은 신규 flagship 후보 real-case 적재와 `3.26~3.27` 추가 외부 교차검증이다


## 12. Real-Case Seed Wave 3 (13:10 +07:00)

새 flagship queue에 맞춰 patch-specific real-case를 추가 적재했다.

추가된 case:

- `3.23_boneshatter_juggernaut_v1`
- `3.24_lightning_arrow_deadeye_v1`
- `3.24_explosive_arrow_ballista_champion_v1`
- `3.24_boneshatter_juggernaut_v1`
- `3.25_boneshatter_juggernaut_v1`
- `3.25_hexblast_miner_saboteur_v1`
- `3.26_siege_ballista_hierophant_v1`
- `3.27_toxic_rain_pathfinder_v1`

반영 후 coverage 변화:

- `3.23`: `0 / 5`에서 `1 / 5`
- `3.24`: `1 / 5`에서 `4 / 5`
- `3.25`: `2 / 5`에서 `4 / 5`
- `3.26`: `3 / 5`에서 `4 / 5`
- `3.27`: `3 / 5`에서 `4 / 5`

의미:

- representative flagship queue와 real-case seed 사이의 간극이 크게 줄었다
- 이제 다수 patch는 `마지막 1개 후보` 정리 단계로 넘어갔다
- 남은 미적재 flagship는 `3.24 Exsanguinate Mine`, `3.25 Lightning Strike`, `3.26 Boneshatter`, `3.27 Pyroclast Mine`, `3.28 flagship 전반`이다


## 13. Final Seed Wave For 3.24~3.27 (13:20 +07:00)

남아 있던 마지막 flagship 후보 4건을 추가 적재했다.

추가된 case:

- `3.24_exsanguinate_mine_trickster_v1`
- `3.25_lightning_strike_deadeye_or_warden_v1`
- `3.26_boneshatter_juggernaut_v1`
- `3.27_pyroclast_mine_saboteur_v1`

반영 후 coverage 변화:

- `3.24`: `4 / 5`에서 `5 / 5`
- `3.25`: `4 / 5`에서 `5 / 5`
- `3.26`: `4 / 5`에서 `5 / 5`
- `3.27`: `4 / 5`에서 `5 / 5`

의미:

- `3.24~3.27`은 이제 operational queue와 real-case seed가 모두 정렬된 상태다
- 다만 일부 마지막 후보는 여전히 `single-source` 기반이라 confidence는 낮게 유지해야 한다
- 남은 주된 공백은 `3.22`, `3.23`, `3.28 flagship`이다


## 14. Seed Wave For 3.22, 3.23, 3.28 (13:35 +07:00)

남아 있던 `3.22`, `3.23`, `3.28` flagship 후보를 추가 적재했다.

추가된 case:

- `3.22_shockwave_totems_hierophant_v1`
- `3.22_boneshatter_juggernaut_v1`
- `3.22_corrupting_fever_champion_v1`
- `3.23_lightning_arrow_deadeye_v1`
- `3.23_hexblast_miner_saboteur_v1`
- `3.23_ice_shot_deadeye_v1`
- `3.23_shockwave_totems_hierophant_v1`
- `3.28_shock_nova_of_procession_hierophant_v1`
- `3.28_kinetic_fusillade_of_detonation_v1`
- `3.28_dominating_blow_guardian_v1`
- `3.28_penance_brand_inquisitor_v1`
- `3.28_cold_snap_of_power_hierophant_v1`

반영 후 coverage 변화:

- `3.22`: `2 / 5`에서 `5 / 5`
- `3.23`: `1 / 5`에서 `5 / 5`
- `3.28`: `flagship 0 / 5 + personal_target 1`에서 `flagship 5 / 5 + personal_target 1`

의미:

- `3.22~3.28` 전 patch가 이제 queue 기준 full seeded 상태다
- 다만 `3.28` flagship 다수와 `3.22 Shockwave Totem`, `3.23 Shockwave Totem`은 low-confidence 또는 single-source 성격이 강하다
- 따라서 coverage 100%는 달성했지만, confidence 100%는 아직 아니다


## 15. Confidence Split Layer (13:45 +07:00)

coverage와 confidence를 분리하는 리포트 레이어를 추가했다.

새 지표:

- `coverage_ratio`: seeded 여부만 보는 완성도
- `confirmed_coverage_ratio`: `low confidence / provisional_seeded`를 제외한 확인도

현재 핵심 해석:

- `3.22`: seeded `5 / 5`, confirmed `3 / 5`
- `3.23`: seeded `5 / 5`, confirmed `4 / 5`
- `3.24`: seeded `5 / 5`, confirmed `4 / 5`
- `3.25`: seeded `5 / 5`, confirmed `4 / 5`
- `3.26`: seeded `5 / 5`, confirmed `2 / 5`
- `3.27`: seeded `5 / 5`, confirmed `0 / 5`
- `3.28`: seeded `5 / 5`, confirmed `0 / 5`, personal target `1`

의미:

- 이제 `100% coverage`와 `100% confidence`를 구분해서 볼 수 있다
- `3.27`, `3.28`은 숫자는 찼지만 여전히 provisional patch다
- 다음부터는 seeded 확대가 아니라 provisional을 confirmed로 승격하는 작업이 핵심이다


## 16. Provisional Tightening (13:55 +07:00)

`provisional_seeded` 기준을 다시 조였다.

변경 원칙:

- 단순 `low confidence` 전체를 provisional로 치지 않는다
- 실제로 `single-source`, `patch-note only`, `local trace` 비중이 큰 후보만 `source_status = provisional_seeded`로 남긴다
- `3.28 Shock Nova`, `3.28 Dominating Blow`처럼 2축 근거가 있는 후보는 provisional에서 해제한다

조정 후 confirmed 해석:

- `3.22`: confirmed `4 / 5`
- `3.23`: confirmed `4 / 5`
- `3.24`: confirmed `4 / 5`
- `3.25`: confirmed `5 / 5`
- `3.26`: confirmed `1 / 5`
- `3.27`: confirmed `2 / 5`
- `3.28`: confirmed `2 / 5`, provisional `3 / 5`, personal target `1`

의미:

- 이제 `3.27`, `3.28`이 완전히 0-confirmed로 묶이지 않고, 실제 교차근거가 있는 일부 후보는 분리된다
- 가장 취약한 patch는 `3.26`, 그 다음이 `3.27`, `3.28`이다


## 17. Confidence Audit Queue (14:05 +07:00)

provisional 후보를 자동 우선순위화하는 audit 스크립트를 추가했다.

추가 파일:

- `python/build_variant_confidence_audit.py`
- `python/tests/test_build_variant_confidence_audit.py`

현재 audit 상 최우선 후보:

- `3.26_boneshatter_juggernaut`
- `3.26_siege_ballista_hierophant`
- `3.27_pyroclast_mine_saboteur`
- `3.28_cold_snap_of_power_hierophant`
- `3.28_kinetic_fusillade_of_detonation`
- `3.28_penance_brand_inquisitor`

패치별 provisional 현황:

- `3.26`: confirmed `1`, provisional `4`
- `3.27`: confirmed `2`, provisional `3`
- `3.28`: confirmed `2`, provisional `3`

의미:

- 이제 다음 리서치 타깃이 코드와 테스트로 고정됐다
- 외부 근거가 더 들어오면 provisional -> confirmed 승격 여부를 바로 판정할 수 있다


## 18. Evidence Consistency Audit (14:15 +07:00)

`queue evidence_sources`와 `real-case evidence`의 불일치를 자동으로 잡는 audit를 추가했다.

추가 파일:

- `python/build_variant_evidence_consistency_audit.py`
- `python/tests/test_build_variant_evidence_consistency_audit.py`

현재 대표 findings:

- `3.22_lightning_arrow_ranger`: queue는 `maxroll + poe_vault`인데 case evidence는 아직 local trace 위주
- `3.24_detonate_dead_ignite_elementalist`: queue의 외부 근거가 case evidence에 아직 반영 안 됨
- `3.27_dominating_blow_guardian`: queue는 `poe_vault`를 갖고 있지만 case evidence엔 빠져 있음
- `3.28_kinetic_fusillade_of_detonation`: queue는 patch note만 들고 있고 case엔 local discussion까지 섞여 있음

의미:

- 이제 provisional 승격뿐 아니라 evidence ingest 누락도 따로 추적된다
- 다음 정제 작업은 external evidence가 이미 queue에 있는데 case에 안 실린 항목부터 맞추는 것이 가장 싸다


## 19. poe.ninja Variant Sampling Contract (2026-07-17 +07:00)

같은 archetype 안에서도 플레이어별 커스터마이징이 크게 갈리므로, poe.ninja 표본을 단일 정답이 아니라 `variant_evidence_candidate`로 수집하는 계약을 추가했다.

추가 파일:

- `data/poe_ninja_build_variant_sampling_plan_v1.json`
- `python/tests/test_poe_ninja_build_variant_sampling_plan.py`

핵심 원칙:

- poe.ninja build/profile 표본은 endgame/live meta 확인용이다
- 레벨링은 poe.ninja 최종 캐릭터 스냅샷만으로 확정하지 않는다
- `Mirage`는 current trade baseline, `SSF/HC Mirage`는 제약/생존성 확인, `Ruthless*`는 별도 scarcity ruleset, `Keepers/Ancestors/Phrecia`는 historical patch delta, `Ziz Rapture HCSSF Class Gauntlet`은 stress evidence로 분리한다
- gear package, defense shell, aura package, cluster package, tree shape, budget, content specialization이 다르면 같은 빌드명 아래에서도 variant 후보로 보존한다
- poe.ninja 공식 문서상 build/profile API는 internal/unsupported이므로 대량 내부 API 수집이 아니라 UI/개별 profile/PoB 중심의 bounded sampling만 허용한다

검증:

- `python -m pytest python/tests/test_poe_ninja_build_variant_sampling_plan.py -q`


## 20. poe.ninja Evidence Queue + Leveling Route Plan (2026-07-17 +07:00)

poe.ninja 쪽은 `build tab visible evidence -> variant_evidence_candidate` 흐름으로 고정하고, 레벨링 쪽은 기존 stage PoB를 route family별로 재사용하는 계획을 추가했다.

추가 파일:

- `data/poe_ninja_build_variant_evidence_queue_v1.json`
- `data/poe1_leveling_archetype_route_plan_v1.json`
- `python/tests/test_poe_ninja_build_variant_evidence_queue.py`
- `python/tests/test_poe1_leveling_archetype_route_plan.py`
- `python/tests/test_poe_ninja_build_api_policy.py`

정책 변경:

- `python/poe_ninja_fetcher.py`의 build overview 수집을 disabled 처리했다
- `python/poe_ninja_build_scraper.py`의 내부 build API 호출을 disabled 처리했다
- 이유: poe.ninja 공식 문서상 build/profile API는 internal / unsupported / unavailable for third-party use다
- 앞으로 poe.ninja build 탭은 대량 API 수집이 아니라 작은 profile/PoB evidence row로만 수집한다

레벨링 route plan 현황:

- `caster`: 3.27 Ice Nova Hierophant stage PoB로 confirmed route 가능
- `ranger`: Toxic Rain/chaos bow는 confirmed fallback, Lightning Arrow/hit bow는 near-confirmed
- `melee`: 3.25 Lightning Strike, 3.23 Boneshatter stage PoB로 confirmed fallback
- `minion`: 3.27 SRS, 3.28 Holy Relic stage PoB로 confirmed route 가능. 토리센세 YouTube 자료는 Spectre/소환수 쪽 source hunt에 우선 연결한다
- `totem`: 3.28 Kinetic Fusillade Totem stage PoB로 confirmed route 가능
- `mine`: Exsanguinate/Reap Miner Trickster가 기준이다. Cptn Garbage / Maxroll Exsanguinate Miner Trickster PoB/가이드를 우선 수집하고, 토리센세는 한국어 보조 확인 및 소환수/Spectre source hunt로 유지한다. Hexblast/Pyroclast는 fallback/reference로만 취급한다

2026-07-17 follow-up correction:

- 사용자 지적으로 mine route를 `mine_shadow_hexblast_or_pyroclast`에서 `mine_exsanguinate_trickster`로 교체했다
- 우선 creator source는 `maxroll_cptn_garbage_exsanguinate_miner`
- `youtube_tori_sensei`는 mine 보조 확인으로 남기고, Spectre/소환수 쪽 creator source로 별도 우선순위를 둔다
- 외부 보조 레퍼런스는 3.27 Cold Exsanguinate Miner Trickster guide와 기존 3.24/3.26/3.27 Exsanguinate Mine queue

2026-07-17 creator registry follow-up:

- `data/poe1_creator_source_registry_v1.json` 추가. CWS는 `emiracle`, mine은 `Cptn Garbage / Jorgen / Conner Converse / FearlessDumb0`, 기발한 빌드는 `CaptainLance9`, 소환수는 `GhazzyTV / 토리센세 / Dconnic`, HC/SSF는 `Zizaran`, 단일 빌드 장기 추적은 `POEGuy / ZeeBoub / Sanavixx`로 분리했다
- `Goblin`은 검색 결과상 `Goblin-Inc`가 유력하지만 POE1 권위 source로 쓰기 전 사용자 확인이 필요하다고 표시했다
- `3.28` mine transition slot은 `Pyroclast Mines Reliquarian`에서 `Exsanguinate Reap Mines Trickster`로 교체했다
- manual PoB source는 `28 -> 33`, direct PoB candidate는 `60 -> 68`, promoted artifact는 `50 -> 57`, promoted state snapshot은 `403 -> 501`로 갱신했다
- parser-validated Exsanguinate/Reap Miner PoB: `BWiaBJnF0XdF`, `VUc0XkHnNAmo`, `kypvIm80e6Ql`, `Rie57RA6iWK-`, `8cJ6kaa0XPZG`, `3J6Dm6pkA6-5`, `ZFC1itVixJSB`
- parser-validated 토리센세 Spectre PoB: `oimmJKVwZB2e`

2026-07-17 recommendation smoke follow-up:

- `poe1_representative_build_profiles.latest.json`에 promoted PoB 기반 supplemental profile을 1건 추가했다: `3.28_exsanguinate_reap_mines_trickster`
- 이 profile은 FearlessDumb0 3.28 staged PoB `3J6Dm6pkA6-5`를 기준으로 `Rolling Magma -> Pyroclast Mine -> Exsanguinate Mine` timeline을 `leveling_confidence=confirmed`로 보존한다
- 추천 smoke 결과: 3.28 Shadow Trickster + `Exsanguinate Mine` + confirmed leveling required 입력에서 `selected_plan=A`, `selected_candidate=3.28_exsanguinate_reap_mines_trickster`, `template_id=plan_a_exact`
- `poe_ninja_build_variant_evidence_queue_v1.json`에는 creator source track 9개를 추가했다: CWS/emiracle, mine/Jorgen+Conner+Cptn+Fearless, experimental/CaptainLance9, minion/Ghazzy+토리센세+Dconnic, HC/Zizaran, variety/Goblin, POEGuy, ZeeBoub, Sanavixx
- 지금부터 테스트 가능한 범위는 `corpus parse/promote/snapshot`, `representative profile generation`, `recommend_from_corpus` exact recommendation smoke다. UI 통합은 별도 dev-server/browser verification이 필요하다

2026-07-17 expanded creator/source correction:

- 수집 queue는 더 이상 패치당 20개를 상한으로 보지 않는다. `target_candidate_count=20`은 최소 baseline이고, 새 creator/build 후보는 기존 후보를 빼지 않고 추가한다
- `3.28_poison_carrion_golem_witch`를 추가했고, 기존 `3.28_volatile_dead_spellslinger_necromancer`는 유지했다. 따라서 expanded queue는 `160 -> 161`, 3.28 후보는 `20 -> 21`
- 사용자 제보 기준으로 토리센세 current-season minion lane은 `Poison Carrion Golem`로 별도 승격했다. 공개 검색에서 확인된 과거 reference는 `3.26 Poison Carrion Golem` 영상/PoB `Gji0uiu1Aoog`이며, current-season direct PoB는 아직 `needs_direct_pob_link`다
- creator registry는 사용자 seed 14명에 discovery creator 20명을 더해 `34`명으로 확장했다: Kankar, anime princess, LLYD, Palsteron, Fubgun, Ruetoo, Crouching_Tuna, Big Ducks, subtractem, Pohx, Jungroan, Goratha, Tatiantel2, Ventrua, Ben_, Steelmage, Carn, ds lily, Mathil, Travic
- poe.ninja evidence queue는 `13` archetype targets / `10` creator source tracks, leveling route plan은 `13` routes로 갱신했다

검증:

- `python -m json.tool data/poe_ninja_build_variant_evidence_queue_v1.json`
- `python -m json.tool data/poe1_leveling_archetype_route_plan_v1.json`
- `python -m pytest python/tests/test_poe_ninja_build_variant_sampling_plan.py python/tests/test_poe_ninja_build_variant_evidence_queue.py python/tests/test_poe1_leveling_archetype_route_plan.py python/tests/test_poe_ninja_build_api_policy.py -q`
