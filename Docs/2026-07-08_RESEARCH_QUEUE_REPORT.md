# POE1 Research Queue Report

작성 시각: 2026-07-08 20:20 +07:00

## 1. 요약

- research targets: `19`
- first external guide needed: `5`
- second external guide needed: `14`

우선 원칙:
- `blocked_no_external_build_guide`를 최우선으로 처리한다.
- 그다음 `single-source` flagship를 처리한다.
- 같은 조건이면 strict confirmable이 0인 patch를 먼저 처리한다.

## 2. Top Priority

- `3.28_kinetic_fusillade_of_detonation` score `167` / `blocked_no_external_build_guide` / next `find_first_external_build_guide_source`
- `3.28_penance_brand_inquisitor` score `167` / `blocked_no_external_build_guide` / next `find_first_external_build_guide_source`
- `3.27_ice_nova_caster` score `166` / `blocked_no_external_build_guide` / next `find_first_external_build_guide_source`
- `3.26_ball_lightning_caster` score `165` / `blocked_no_external_build_guide` / next `find_first_external_build_guide_source`
- `3.26_ice_nova_caster` score `160` / `blocked_no_external_build_guide` / next `find_first_external_build_guide_source`
- `3.28_cold_snap_of_power_hierophant` score `137` / `provisional_external_gap` / next `find_second_external_build_guide_source`
- `3.27_pyroclast_mine_saboteur` score `136` / `provisional_external_gap` / next `find_second_external_build_guide_source`
- `3.26_boneshatter_juggernaut` score `135` / `provisional_external_gap` / next `find_second_external_build_guide_source`
- `3.26_siege_ballista_hierophant` score `135` / `provisional_external_gap` / next `find_second_external_build_guide_source`
- `3.22_shockwave_totems_hierophant` score `119` / `provisional_external_gap` / next `find_second_external_build_guide_source`

## 3. Patch Priority

- `3.22` backlog `2` / max score `119` / top `3.22_shockwave_totems_hierophant, 3.22_toxic_rain_ranger`
- `3.23` backlog `1` / max score `116` / top `3.23_shockwave_totems_hierophant`
- `3.24` backlog `1` / max score `117` / top `3.24_exsanguinate_mine_trickster`
- `3.26` backlog `5` / max score `165` / top `3.26_ball_lightning_caster, 3.26_ice_nova_caster, 3.26_boneshatter_juggernaut`
- `3.27` backlog `5` / max score `166` / top `3.27_ice_nova_caster, 3.27_pyroclast_mine_saboteur, 3.27_dominating_blow_guardian`
- `3.28` backlog `5` / max score `167` / top `3.28_kinetic_fusillade_of_detonation, 3.28_penance_brand_inquisitor, 3.28_cold_snap_of_power_hierophant`

## 4. Immediate Focus

- `3.28_kinetic_fusillade_of_detonation`
- `3.28_penance_brand_inquisitor`
- `3.27_ice_nova_caster`
- `3.26_ball_lightning_caster`
- `3.26_ice_nova_caster`

이 5개는 현재 외부 빌드 가이드가 0개라, 여기를 못 뚫으면 strict 기준 정확도가 더 올라가지 않는다.
