# POE1 Strict Verification Report

작성 시각: 2026-07-08 20:10 +07:00

## 1. 요약

- flagship seeded: `35`
- 현재 non-provisional: `22`
- standard confirmable: `23`
- strict confirmable: `16`
- strict gap: `19`
- blocked without external build guide: `5`

해석:
현재 corpus는 `coverage 35 seeded` 상태지만, strict 기준에서는 `16`개만 바로 확정 가능하다.
즉 `seed completeness`와 `strict confirmation`을 같은 숫자로 취급하면 과대평가가 발생한다.

## 2. Patch Snapshot

| Patch | Seeded | Current Confirmed | Standard | Strict | Strict Gap | Blocked No External |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 3.22 | 5 | 4 | 4 | 3 | 2 | 0 |
| 3.23 | 5 | 4 | 4 | 4 | 1 | 0 |
| 3.24 | 5 | 4 | 4 | 4 | 1 | 0 |
| 3.25 | 5 | 5 | 5 | 5 | 0 | 0 |
| 3.26 | 5 | 1 | 1 | 0 | 5 | 2 |
| 3.27 | 5 | 2 | 3 | 0 | 5 | 1 |
| 3.28 | 5 | 2 | 2 | 0 | 5 | 2 |

핵심 해석:
- `3.25`는 현재 데이터만으로도 strict 통과가 가능하다.
- `3.26`, `3.27`, `3.28`은 seeded는 5/5지만 strict confirmable은 각각 `0/5`, `0/5`, `0/5`다.
- `3.28`은 공식 패치 언급만 있는 후보가 섞여 있어 가장 보수적으로 다뤄야 한다.

## 3. Strict Gap 유형

- `find_second_external_build_guide_source`
  - 3.22_shockwave_totems_hierophant
  - 3.22_toxic_rain_ranger
  - 3.23_shockwave_totems_hierophant
  - 3.24_exsanguinate_mine_trickster
  - 3.26_boneshatter_juggernaut
  - 3.26_lightning_arrow_ranger
  - 3.26_siege_ballista_hierophant
  - 3.27_dominating_blow_guardian
  - 3.27_lacerate_duelist
  - 3.27_pyroclast_mine_saboteur
  - 3.27_toxic_rain_pathfinder
  - 3.28_cold_snap_of_power_hierophant
  - 3.28_dominating_blow_guardian
  - 3.28_shock_nova_of_procession_hierophant
- `find_first_external_build_guide_source`
  - 3.26_ball_lightning_caster
  - 3.26_ice_nova_caster
  - 3.27_ice_nova_caster
  - 3.28_kinetic_fusillade_of_detonation
  - 3.28_penance_brand_inquisitor
- `standard_only` but not strict
  - 3.22_toxic_rain_ranger
  - 3.26_lightning_arrow_ranger
  - 3.27_dominating_blow_guardian
  - 3.27_lacerate_duelist
  - 3.27_toxic_rain_pathfinder
  - 3.28_dominating_blow_guardian
  - 3.28_shock_nova_of_procession_hierophant

## 4. 결론

strict 기준으로는 `3.26~3.28` flagship 후보를 더 이상 자동 승격하면 안 된다.
특히 `3.28_kinetic_fusillade_of_detonation`과 `3.28_penance_brand_inquisitor`는 현재 `official_patch_notes + local_discussion_trace`뿐이라 외부 빌드 가이드가 잡히기 전까지 blocked 상태가 맞다.
반대로 `3.25`는 대표성 검증이 가장 안정적이고, `3.22~3.24`는 일부 single-source 후보만 추가 교차검증하면 된다.
