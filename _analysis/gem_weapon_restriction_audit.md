# GGPK 전체 스킬젬 WeaponRestriction 감사

출처: `data/game_data/ActiveSkills.json` + `data/game_data/BaseItemTypes.json` (GGPK 추출본)

필터 기준: player-facing 변형만 (변형/몬스터/토템/공격봇/트리거 id 제외)

- WeaponRestriction 있는 스킬: **187개**
- WeaponRestriction 없는 스킬 (스펠/오라/버프): 579개
- 스킵된 변형/내부 엔트리: 1151개

## 열 설명

- **Name**: DisplayedName (게임 내 이름)
- **Id**: ActiveSkills.Id (내부 ID)
- **All Classes**: WeaponRestriction → 모든 Class (Sceptre/Staff/Rune Dagger/Fishing Rod 포함)
- **Phys-only**: NeverSink 물리 12 Class 필터 적용 후 (PathcraftAI에서 실제 쓰는 값)
- **Raw keys**: 원본 ItemClassesKey 숫자

## ItemClassesKey 매핑 (참고)

```
    6: Claws
    7: Daggers
    8: Wands
    9: One Hand Swords
   10: Thrusting One Hand Swords
   11: One Hand Axes
   12: One Hand Maces
   13: Bows
   14: Staves
   15: Two Hand Swords
   16: Two Hand Axes
   17: Two Hand Maces
   32: Sceptres
   37: Fishing Rods
   56: Rune Daggers
   57: Warstaves
```

## 전체 표

| Name | Id | All Classes | Phys-only | Raw |
|------|-----|-------------|-----------|-----|
| ... | `combo_strike` | Claws, Daggers, One Hand Axes, One Hand Maces, One Hand Swords, Sceptres, Thrusting One Hand Swords | Claws, Daggers, One Hand Axes, One Hand Maces, One Hand Swords, Thrusting One Hand Swords | [6, 7, 9, 10, 11, 12, 32] |
| [DNT] Chain Grab | `chain_grab` | One Hand Axes, One Hand Swords, Thrusting One Hand Swords | One Hand Axes, One Hand Swords, Thrusting One Hand Swords | [9, 10, 11] |
| [UNUSED] Blitz (NOT CURRENTLY USED) | `blitz` | Claws, Daggers, One Hand Axes, One Hand Maces, One Hand Swords, Sceptres, Thrusting One Hand Swords | Claws, Daggers, One Hand Axes, One Hand Maces, One Hand Swords, Thrusting One Hand Swords | [6, 7, 9, 10, 11, 12, 32] |
| [UNUSED] Blood Whirl | `blood_whirl` | Claws, Daggers, One Hand Axes, One Hand Maces, One Hand Swords, Sceptres, Thrusting One Hand Swords | Claws, Daggers, One Hand Axes, One Hand Maces, One Hand Swords, Thrusting One Hand Swords | [6, 7, 9, 10, 11, 12, 32] |
| [UNUSED] DISCONTINUED | `serpent_strike` | Claws, Daggers, One Hand Swords | Claws, Daggers, One Hand Swords | [6, 7, 9] |
| [UNUSED] DISCONTINUED | `coiling_assault` | Daggers, One Hand Swords, Thrusting One Hand Swords | Daggers, One Hand Swords, Thrusting One Hand Swords | [7, 9, 10] |
| [UNUSED] Slice and Dice (NOT CURRENTLY USED) | `slice_and_dice` | Claws, Daggers, One Hand Axes, One Hand Maces, One Hand Swords, Sceptres, Thrusting One Hand Swords | Claws, Daggers, One Hand Axes, One Hand Maces, One Hand Swords, Thrusting One Hand Swords | [6, 7, 9, 10, 11, 12, 32] |
| Ancestral Blademaster | `ancestor_totem_slash` | Claws, Daggers, One Hand Axes, One Hand Maces, One Hand Swords, Sceptres, Thrusting One Hand Swords | Claws, Daggers, One Hand Axes, One Hand Maces, One Hand Swords, Thrusting One Hand Swords | [6, 7, 9, 10, 11, 12, 32] |
| Ancestral Protector | `ancestral_protector` | Claws, Daggers, One Hand Axes, One Hand Maces, One Hand Swords, Sceptres, Thrusting One Hand Swords | Claws, Daggers, One Hand Axes, One Hand Maces, One Hand Swords, Thrusting One Hand Swords | [6, 7, 9, 10, 11, 12, 32] |
| Ancestral Warchief | `ancestral_warchief` | Claws, Daggers, One Hand Axes, One Hand Maces, One Hand Swords, Sceptres, Thrusting One Hand Swords | Claws, Daggers, One Hand Axes, One Hand Maces, One Hand Swords, Thrusting One Hand Swords | [6, 7, 9, 10, 11, 12, 32] |
| Artillery Ballista | `artillery_ballista` | Bows | Bows | [13] |
| Backstab | `backstab` | Daggers | Daggers | [7] |
| Barrage | `barrage` | Bows | Bows | [13] |
| Blade Flurry | `charged_attack` | Claws, Daggers, One Hand Swords | Claws, Daggers, One Hand Swords | [6, 7, 9] |
| Blade Flurry | `blade_flurry` | Claws, Daggers, One Hand Swords | Claws, Daggers, One Hand Swords | [6, 7, 9] |
| Blade Trap | `blade_trap` | Daggers, One Hand Swords, Rune Daggers | Daggers, One Hand Swords | [9, 7, 56] |
| Bladestorm | `bladestorm` | One Hand Swords, Thrusting One Hand Swords, Two Hand Swords | One Hand Swords, Thrusting One Hand Swords, Two Hand Swords | [9, 10, 15] |
| Blast Rain | `blast_rain` | Bows | Bows | [13] |
| Blink Arrow | `blink_arrow` | Bows | Bows | [13] |
| Blink Arrow | `blink_arrow_triggered` | Bows | Bows | [13] |
| Boneshatter | `boneshatter` | One Hand Axes, One Hand Maces, Sceptres, Staves | One Hand Axes, One Hand Maces | [11, 12, 32, 14] |
| Burning Arrow | `burning_arrow` | Bows | Bows | [13] |
| Call the Pyre | `call_the_pyre` | Claws, Daggers, One Hand Axes, One Hand Maces, One Hand Swords, Sceptres, Thrusting One Hand Swords | Claws, Daggers, One Hand Axes, One Hand Maces, One Hand Swords, Thrusting One Hand Swords | [6, 7, 9, 10, 11, 12, 32] |
| Caustic Arrow | `caustic_arrow` | Bows | Bows | [13] |
| Chain Hook | `chain_hook` | One Hand Axes, One Hand Swords, Thrusting One Hand Swords | One Hand Axes, One Hand Swords, Thrusting One Hand Swords | [9, 10, 11] |
| Charged Dash | `charged_dash` | Claws, Daggers, One Hand Axes, One Hand Maces, One Hand Swords, Sceptres, Thrusting One Hand Swords | Claws, Daggers, One Hand Axes, One Hand Maces, One Hand Swords, Thrusting One Hand Swords | [6, 7, 9, 10, 11, 12, 32] |
| Cleave | `cleave` | One Hand Axes, One Hand Swords, Thrusting One Hand Swords | One Hand Axes, One Hand Swords, Thrusting One Hand Swords | [9, 10, 11] |
| Cobra Lash | `cobra_lash` | Claws, Daggers | Claws, Daggers | [7, 6] |
| Combust | `infernal_cry_on_hit_explosion` | One Hand Axes, One Hand Maces, One Hand Swords, Thrusting One Hand Swords, Two Hand Axes, Two Hand Swords | One Hand Axes, One Hand Maces, One Hand Swords, Thrusting One Hand Swords, Two Hand Axes, Two Hand Swords | [9, 10, 15, 11, 16, 12] |
| Commandment of Fury | `commandment_of_fury_on_hit` | Bows, Claws, Daggers, Fishing Rods, One Hand Axes, One Hand Maces, One Hand Swords, Sceptres | Bows, Claws, Daggers, One Hand Axes, One Hand Maces, One Hand Swords | [13, 6, 7, 37, 11, 12, 9, 32] |
| Commandment of Ire | `commandment_of_ire_when_hit` | Bows, Claws, Daggers, Fishing Rods, One Hand Axes, One Hand Maces, One Hand Swords, Sceptres | Bows, Claws, Daggers, One Hand Axes, One Hand Maces, One Hand Swords | [13, 6, 7, 37, 11, 12, 9, 32] |
| Commandment of Spite | `commandment_of_spite_when_hit` | Bows, Claws, Daggers, Fishing Rods, One Hand Axes, One Hand Maces, One Hand Swords, Sceptres | Bows, Claws, Daggers, One Hand Axes, One Hand Maces, One Hand Swords | [13, 6, 7, 37, 11, 12, 9, 32] |
| Commandment of War | `commandment_of_war_on_kill` | Bows, Claws, Daggers, Fishing Rods, One Hand Axes, One Hand Maces, One Hand Swords, Sceptres | Bows, Claws, Daggers, One Hand Axes, One Hand Maces, One Hand Swords | [13, 6, 7, 37, 11, 12, 9, 32] |
| Conflagration | `napalm_arrows` | Bows | Bows | [13] |
| Consecrated Path | `consecrated_path` | One Hand Axes, One Hand Maces, One Hand Swords, Thrusting One Hand Swords, Two Hand Axes, Two Hand Swords | One Hand Axes, One Hand Maces, One Hand Swords, Thrusting One Hand Swords, Two Hand Axes, Two Hand Swords | [9, 10, 15, 11, 16, 12] |
| Crushing Fist | `crushing_fist` | Claws, Daggers, One Hand Axes, One Hand Maces, One Hand Swords, Sceptres, Thrusting One Hand Swords | Claws, Daggers, One Hand Axes, One Hand Maces, One Hand Swords, Thrusting One Hand Swords | [6, 7, 9, 10, 11, 12, 32] |
| Cyclone | `cyclone` | Claws, Daggers, One Hand Axes, One Hand Maces, One Hand Swords, Sceptres, Thrusting One Hand Swords | Claws, Daggers, One Hand Axes, One Hand Maces, One Hand Swords, Thrusting One Hand Swords | [6, 7, 9, 10, 11, 12, 32] |
| Decree of Fury | `decree_of_fury_on_hit` | Bows, Claws, Daggers, Fishing Rods, One Hand Axes, One Hand Maces, One Hand Swords, Sceptres | Bows, Claws, Daggers, One Hand Axes, One Hand Maces, One Hand Swords | [13, 6, 7, 37, 11, 12, 9, 32] |
| Decree of Ire | `decree_of_ire_when_hit` | Bows, Claws, Daggers, Fishing Rods, One Hand Axes, One Hand Maces, One Hand Swords, Sceptres | Bows, Claws, Daggers, One Hand Axes, One Hand Maces, One Hand Swords | [13, 6, 7, 37, 11, 12, 9, 32] |
| Decree of Spite | `decree_of_spite_when_hit` | Bows, Claws, Daggers, Fishing Rods, One Hand Axes, One Hand Maces, One Hand Swords, Sceptres | Bows, Claws, Daggers, One Hand Axes, One Hand Maces, One Hand Swords | [13, 6, 7, 37, 11, 12, 9, 32] |
| Decree of War | `decree_of_war_on_kill` | Bows, Claws, Daggers, Fishing Rods, One Hand Axes, One Hand Maces, One Hand Swords, Sceptres | Bows, Claws, Daggers, One Hand Axes, One Hand Maces, One Hand Swords | [13, 6, 7, 37, 11, 12, 9, 32] |
| Divine Blast | `discus_slam` | ?26 | ∅ | [26] |
| Dominating Blow | `dominating_blow` | One Hand Axes, One Hand Maces, One Hand Swords, Sceptres, Thrusting One Hand Swords, Two Hand Axes, Two Hand Swords | One Hand Axes, One Hand Maces, One Hand Swords, Thrusting One Hand Swords, Two Hand Axes, Two Hand Swords | [9, 10, 15, 11, 16, 12, 32] |
| Doom Arrow | `doom_arrow` | Bows | Bows | [13] |
| Doryani's Touch | `doryanis_touch` | ?36 | ∅ | [36] |
| Double Strike | `double_strike` | Claws, Daggers, One Hand Axes, One Hand Maces, One Hand Swords, Sceptres, Thrusting One Hand Swords | Claws, Daggers, One Hand Axes, One Hand Maces, One Hand Swords, Thrusting One Hand Swords | [6, 7, 9, 10, 11, 12, 32] |
| Dual Strike | `dual_strike` | Claws, Daggers, One Hand Axes, One Hand Swords, Thrusting One Hand Swords | Claws, Daggers, One Hand Axes, One Hand Swords, Thrusting One Hand Swords | [6, 7, 9, 10, 11] |
| Earthquake | `earthquake` | One Hand Axes, One Hand Maces, Sceptres, Staves | One Hand Axes, One Hand Maces | [11, 12, 32, 14] |
| Earthshatter | `earthshatter` | One Hand Maces, Sceptres, Staves, Two Hand Maces | One Hand Maces, Two Hand Maces | [12, 32, 14, 17] |
| Edict of Fury | `edict_of_fury_on_hit` | Bows, Claws, Daggers, Fishing Rods, One Hand Axes, One Hand Maces, One Hand Swords, Sceptres | Bows, Claws, Daggers, One Hand Axes, One Hand Maces, One Hand Swords | [13, 6, 7, 37, 11, 12, 9, 32] |
| Edict of Ire | `edict_of_ire_when_hit` | Bows, Claws, Daggers, Fishing Rods, One Hand Axes, One Hand Maces, One Hand Swords, Sceptres | Bows, Claws, Daggers, One Hand Axes, One Hand Maces, One Hand Swords | [13, 6, 7, 37, 11, 12, 9, 32] |
| Edict of Spite | `edict_of_spite_when_hit` | Bows, Claws, Daggers, Fishing Rods, One Hand Axes, One Hand Maces, One Hand Swords, Sceptres | Bows, Claws, Daggers, One Hand Axes, One Hand Maces, One Hand Swords | [13, 6, 7, 37, 11, 12, 9, 32] |
| Edict of War | `edict_of_war_on_kill` | Bows, Claws, Daggers, Fishing Rods, One Hand Axes, One Hand Maces, One Hand Swords, Sceptres | Bows, Claws, Daggers, One Hand Axes, One Hand Maces, One Hand Swords | [13, 6, 7, 37, 11, 12, 9, 32] |
| Elemental Hit | `elemental_hit` | One Hand Axes, One Hand Maces, One Hand Swords, Sceptres, Thrusting One Hand Swords, Two Hand Axes, Two Hand Swords | One Hand Axes, One Hand Maces, One Hand Swords, Thrusting One Hand Swords, Two Hand Axes, Two Hand Swords | [9, 10, 15, 11, 16, 12, 32] |
| Energy Blade | `energy_blade` | Claws, Daggers, Fishing Rods, One Hand Axes, One Hand Maces, One Hand Swords, Sceptres, Staves | Claws, Daggers, One Hand Axes, One Hand Maces, One Hand Swords | [6, 7, 37, 11, 12, 9, 32, 14] |
| Ensnaring Arrow | `ensnaring_arrow` | Bows | Bows | [13] |
| Eviscerate | `eviscerate` | One Hand Swords, Thrusting One Hand Swords | One Hand Swords, Thrusting One Hand Swords | [9, 10] |
| Explosive Arrow | `explosive_arrow` | Bows | Bows | [13] |
| Explosive Concoction | `explosive_concoction` | ?36 | ∅ | [36] |
| Fiery Impact | `fiery_impact` | Claws, Daggers, One Hand Axes, One Hand Maces, One Hand Swords, Sceptres, Thrusting One Hand Swords | Claws, Daggers, One Hand Axes, One Hand Maces, One Hand Swords, Thrusting One Hand Swords | [6, 7, 9, 10, 11, 12, 32] |
| Fissure | `triggered_fissure` | One Hand Maces, Sceptres, Two Hand Maces, Warstaves | One Hand Maces, Two Hand Maces, Warstaves | [12, 17, 32, 57] |
| Flammable Shot | `oil_arrow` | Bows | Bows | [13] |
| Flicker Strike | `flicker_strike` | Claws, Daggers, One Hand Axes, One Hand Maces, One Hand Swords, Sceptres, Thrusting One Hand Swords | Claws, Daggers, One Hand Axes, One Hand Maces, One Hand Swords, Thrusting One Hand Swords | [6, 7, 9, 10, 11, 12, 32] |
| Frenzy | `frenzy` | Bows | Bows | [13] |
| Frost Blades | `frost_blades` | Claws, Daggers, One Hand Axes, One Hand Maces, One Hand Swords, Sceptres, Thrusting One Hand Swords | Claws, Daggers, One Hand Axes, One Hand Maces, One Hand Swords, Thrusting One Hand Swords | [6, 7, 9, 10, 11, 12, 32] |
| Frozen Legion | `frozen_legion` | One Hand Axes, One Hand Maces, Staves, Two Hand Maces | One Hand Axes, One Hand Maces, Two Hand Maces | [14, 12, 17, 11] |
| Frozen Sweep | `frozen_sweep` | One Hand Axes, One Hand Maces, Staves, Two Hand Maces | One Hand Axes, One Hand Maces, Two Hand Maces | [14, 12, 17, 11] |
| Galvanic Arrow | `galvanic_arrow` | Bows | Bows | [13] |
| Glacial Hammer | `glacial_hammer` | One Hand Maces, Sceptres, Two Hand Maces | One Hand Maces, Two Hand Maces | [12, 32, 17] |
| Glacial Shield Swipe | `glacial_shield_swipe` | ?26 | ∅ | [26] |
| Gore Shockwave | `gore_shockwave` | Two Hand Axes | Two Hand Axes | [16] |
| Ground Slam | `ground_slam` | One Hand Maces, Sceptres, Staves, Two Hand Maces | One Hand Maces, Two Hand Maces | [12, 32, 14, 17] |
| Heavy Strike | `heavy_strike` | One Hand Axes, One Hand Maces, Sceptres, Staves, Two Hand Swords | One Hand Axes, One Hand Maces, Two Hand Swords | [11, 12, 32, 14, 15] |
| Holy Hammers | `holy_hammers` | One Hand Maces, Staves, Warstaves | One Hand Maces, Warstaves | [14, 57, 12] |
| Holy Strike | `holy_strike` | One Hand Maces, Staves, Two Hand Maces | One Hand Maces, Two Hand Maces | [12, 17, 14] |
| Holy Sweep | `sweep` | Two Hand Maces, Warstaves | Two Hand Maces, Warstaves | [17, 57] |
| Ice Crash | `ice_crash` | One Hand Axes, One Hand Maces, One Hand Swords, Sceptres, Staves, Thrusting One Hand Swords | One Hand Axes, One Hand Maces, One Hand Swords, Thrusting One Hand Swords | [9, 10, 11, 12, 32, 14] |
| Ice Crash | `ice_crash_triggered` | One Hand Axes, One Hand Maces, One Hand Swords, Sceptres, Staves, Thrusting One Hand Swords | One Hand Axes, One Hand Maces, One Hand Swords, Thrusting One Hand Swords | [9, 10, 11, 12, 32, 14] |
| Ice Shot | `ice_shot` | Bows | Bows | [13] |
| Infernal Blow | `infernal_blow` | One Hand Axes, One Hand Maces, One Hand Swords, Thrusting One Hand Swords, Two Hand Axes, Two Hand Swords | One Hand Axes, One Hand Maces, One Hand Swords, Thrusting One Hand Swords, Two Hand Axes, Two Hand Swords | [9, 10, 15, 11, 16, 12] |
| Infernal Sweep | `infernal_sweep` | Staves, Two Hand Axes, Two Hand Maces | Two Hand Axes, Two Hand Maces | [14, 16, 17] |
| Kinetic Anomaly | `kinetic_rain_kinetic_instability` | Wands | Wands | [8] |
| Kinetic Blast | `kinetic_blast` | Wands | Wands | [8] |
| Kinetic Bolt | `kinetic_bolt` | Wands | Wands | [8] |
| Kinetic Fusillade | `kinetic_fusillade` | Wands | Wands | [8] |
| Kinetic Rain | `kinetic_rain` | Wands | Wands | [8] |
| Lacerate | `lacerate` | One Hand Axes, One Hand Swords, Two Hand Swords | One Hand Axes, One Hand Swords, Two Hand Swords | [9, 15, 11] |
| Lancing Steel | `lancing_steel` | One Hand Swords, Thrusting One Hand Swords, Two Hand Swords | One Hand Swords, Thrusting One Hand Swords, Two Hand Swords | [9, 10, 15] |
| Lancing Steel | `lancing_steel_new` | One Hand Swords, Thrusting One Hand Swords, Two Hand Swords | One Hand Swords, Thrusting One Hand Swords, Two Hand Swords | [9, 10, 15] |
| Leap Slam | `leap_slam` | One Hand Axes, One Hand Maces, One Hand Swords, Sceptres, Thrusting One Hand Swords | One Hand Axes, One Hand Maces, One Hand Swords, Thrusting One Hand Swords | [9, 10, 11, 12, 32] |
| Leap Slam | `leap_slam_cooldown` | One Hand Axes, One Hand Maces, One Hand Swords, Sceptres, Thrusting One Hand Swords | One Hand Axes, One Hand Maces, One Hand Swords, Thrusting One Hand Swords | [9, 10, 11, 12, 32] |
| Leap Slam | `leap_slam_behind` | One Hand Axes, One Hand Maces, One Hand Swords, Sceptres, Thrusting One Hand Swords | One Hand Axes, One Hand Maces, One Hand Swords, Thrusting One Hand Swords | [9, 10, 11, 12, 32] |
| Leap Slam | `vulture_leap_slam` | One Hand Axes, One Hand Maces, One Hand Swords, Sceptres, Thrusting One Hand Swords | One Hand Axes, One Hand Maces, One Hand Swords, Thrusting One Hand Swords | [9, 10, 11, 12, 32] |
| Lightning Arrow | `lightning_arrow` | Bows | Bows | [13] |
| Lightning Strike | `lightning_strike` | Claws, Daggers, One Hand Axes, One Hand Maces, One Hand Swords, Sceptres, Thrusting One Hand Swords | Claws, Daggers, One Hand Axes, One Hand Maces, One Hand Swords, Thrusting One Hand Swords | [6, 7, 9, 10, 11, 12, 32] |
| Mirror Arrow | `mirror_arrow` | Bows | Bows | [13] |
| Mirror Arrow | `mirror_arrow_triggered` | Bows | Bows | [13] |
| Molten Strike | `molten_strike` | Claws, Daggers, One Hand Axes, One Hand Maces, One Hand Swords, Sceptres, Thrusting One Hand Swords | Claws, Daggers, One Hand Axes, One Hand Maces, One Hand Swords, Thrusting One Hand Swords | [6, 7, 9, 10, 11, 12, 32] |
| Perforate | `perforate` | One Hand Swords, Thrusting One Hand Swords, Two Hand Swords | One Hand Swords, Thrusting One Hand Swords, Two Hand Swords | [9, 10, 15] |
| Pestilent Strike | `pestilent_strike` | Claws, Daggers | Claws, Daggers | [6, 7] |
| Playtest Slam | `playtest_slam` | One Hand Maces, Sceptres, Staves, Two Hand Maces | One Hand Maces, Two Hand Maces | [12, 32, 14, 17] |
| Poisonous Concoction | `poisonous_concoction` | ?36 | ∅ | [36] |
| Power Siphon | `power_siphon` | Wands | Wands | [8] |
| Puncture | `puncture` | Bows | Bows | [13] |
| Puncture | `monster_puncture` | Bows, Claws, Daggers, One Hand Swords | Bows, Claws, Daggers, One Hand Swords | [13, 6, 7, 9] |
| Rage Vortex | `rage_vortex` | One Hand Swords, Thrusting One Hand Swords, Two Hand Swords | One Hand Swords, Thrusting One Hand Swords, Two Hand Swords | [9, 10, 15] |
| Rain of Arrows | `rain_of_arrows` | Bows | Bows | [13] |
| Rain of Arrows | `rain_of_arrows_triggered` | Bows | Bows | [13] |
| Reave | `reave` | Claws, Daggers, One Hand Swords | Claws, Daggers, One Hand Swords | [6, 7, 9] |
| Reckoning | `reckoning` | Claws, Daggers, One Hand Axes, One Hand Swords, Thrusting One Hand Swords | Claws, Daggers, One Hand Axes, One Hand Swords, Thrusting One Hand Swords | [6, 7, 9, 10, 11] |
| Rending Steel (NOT CURRENTLY USED) | `rending_steel` | One Hand Swords, Thrusting One Hand Swords, Two Hand Swords | One Hand Swords, Thrusting One Hand Swords, Two Hand Swords | [9, 10, 15] |
| Riposte | `riposte` | Claws, Daggers, One Hand Axes, One Hand Maces, One Hand Swords, Sceptres, Thrusting One Hand Swords | Claws, Daggers, One Hand Axes, One Hand Maces, One Hand Swords, Thrusting One Hand Swords | [6, 7, 9, 10, 11, 12, 32] |
| Scourge Arrow | `scourge_arrow` | Bows | Bows | [13] |
| Seize the Flesh | `seize_the_flesh` | Claws, Daggers, One Hand Axes, One Hand Maces, One Hand Swords, Sceptres, Thrusting One Hand Swords | Claws, Daggers, One Hand Axes, One Hand Maces, One Hand Swords, Thrusting One Hand Swords | [6, 7, 9, 10, 11, 12, 32] |
| Shattering Steel | `shattering_steel` | One Hand Swords, Thrusting One Hand Swords, Two Hand Swords | One Hand Swords, Thrusting One Hand Swords, Two Hand Swords | [9, 10, 15] |
| Shield Charge | `new_shield_charge` | Claws, Daggers, One Hand Axes, One Hand Swords, Thrusting One Hand Swords | Claws, Daggers, One Hand Axes, One Hand Swords, Thrusting One Hand Swords | [6, 7, 9, 10, 11] |
| Shield Charge | `shield_charge` | ?26 | ∅ | [26] |
| Shield Charge | `shield_charge_cooldown` | ?26 | ∅ | [26] |
| Shield Crush | `shield_crush` | ?26 | ∅ | [26] |
| Shield of Light | `shield_of_light` | ?26 | ∅ | [26] |
| Shield Shatter | `shield_shatter` | ?26 | ∅ | [26] |
| Shockwave | `support_blunt_shockwave` | One Hand Maces, Sceptres, Two Hand Maces | One Hand Maces, Two Hand Maces | [12, 32, 17] |
| Shrapnel Ballista | `shrapnel_ballista` | Bows | Bows | [13] |
| Siege Ballista | `siege_ballista` | Bows | Bows | [13] |
| Smite | `smite` | One Hand Axes, One Hand Maces, One Hand Swords, Thrusting One Hand Swords, Two Hand Axes, Two Hand Swords | One Hand Axes, One Hand Maces, One Hand Swords, Thrusting One Hand Swords, Two Hand Axes, Two Hand Swords | [9, 10, 15, 11, 16, 12] |
| Snipe | `channelled_snipe` | Bows | Bows | [13] |
| Somatic Shell | `kinetic_shell` | Wands | Wands | [8] |
| Spectral Helix | `spectral_helix` | Claws, Daggers, One Hand Axes, One Hand Maces, One Hand Swords, Sceptres, Thrusting One Hand Swords | Claws, Daggers, One Hand Axes, One Hand Maces, One Hand Swords, Thrusting One Hand Swords | [6, 7, 9, 10, 11, 12, 32] |
| Spectral Shield Throw | `spectral_shield_throw` | ?26 | ∅ | [26] |
| Spectral Spinning Weapon | `spectral_spinning_weapon` | Claws, Daggers, One Hand Axes, One Hand Maces, One Hand Swords, Sceptres, Staves, Thrusting One Hand Swords | Claws, Daggers, One Hand Axes, One Hand Maces, One Hand Swords, Thrusting One Hand Swords | [6, 7, 9, 10, 11, 12, 32, 14] |
| Spectral Throw | `spectral_throw` | Claws, Daggers, One Hand Axes, One Hand Maces, One Hand Swords, Sceptres, Thrusting One Hand Swords | Claws, Daggers, One Hand Axes, One Hand Maces, One Hand Swords, Thrusting One Hand Swords | [6, 7, 9, 10, 11, 12, 32] |
| Split Arrow | `split_arrow` | Bows | Bows | [13] |
| Splitting Steel | `splitting_steel` | One Hand Swords, Thrusting One Hand Swords, Two Hand Swords | One Hand Swords, Thrusting One Hand Swords, Two Hand Swords | [9, 10, 15] |
| Static Strike | `static_strike` | Claws, Daggers, One Hand Axes, One Hand Maces, One Hand Swords, Sceptres, Thrusting One Hand Swords | Claws, Daggers, One Hand Axes, One Hand Maces, One Hand Swords, Thrusting One Hand Swords | [6, 7, 9, 10, 11, 12, 32] |
| Storm Rain | `storm_rain` | Bows | Bows | [13] |
| Sunder | `sunder` | One Hand Maces, Sceptres, Staves, Two Hand Maces | One Hand Maces, Two Hand Maces | [12, 32, 14, 17] |
| Swordstorm | `swordstorm` | Claws, Daggers, One Hand Swords, Thrusting One Hand Swords | Claws, Daggers, One Hand Swords, Thrusting One Hand Swords | [6, 7, 9, 10] |
| Table Charge | `table_charge` | Claws, Daggers, One Hand Axes, One Hand Swords, Thrusting One Hand Swords | Claws, Daggers, One Hand Axes, One Hand Swords, Thrusting One Hand Swords | [6, 7, 9, 10, 11] |
| Tectonic Slam | `tectonic_slam` | One Hand Axes, One Hand Maces, Sceptres, Staves, Two Hand Axes, Two Hand Maces | One Hand Axes, One Hand Maces, Two Hand Axes, Two Hand Maces | [12, 32, 14, 17, 11, 16] |
| Tectonic Slam | `tectonic_slam_mercenary` | One Hand Axes, One Hand Maces, Sceptres, Staves, Two Hand Axes, Two Hand Maces | One Hand Axes, One Hand Maces, Two Hand Axes, Two Hand Maces | [12, 32, 14, 17, 11, 16] |
| Thunderburst | `thunderstorm_thunderburst` | Bows | Bows | [13] |
| Thunderstorm | `thunderstorm` | Bows | Bows | [13] |
| Tornado Shot | `tornado_shot` | Bows | Bows | [13] |
| Toxic Rain | `toxic_rain` | Bows | Bows | [13] |
| Toxic Rain | `toxic_rain_triggered` | Bows | Bows | [13] |
| Unseen Strike | `unseen_strike` | Claws, Daggers, One Hand Swords, Rune Daggers | Claws, Daggers, One Hand Swords | [6, 7, 56, 9] |
| Vaal Ancestral Warchief | `vaal_ancestral_warchief` | Claws, Daggers, One Hand Axes, One Hand Maces, One Hand Swords, Sceptres, Thrusting One Hand Swords | Claws, Daggers, One Hand Axes, One Hand Maces, One Hand Swords, Thrusting One Hand Swords | [6, 7, 9, 10, 11, 12, 32] |
| Vaal Blade Flurry | `vaal_blade_flurry` | Claws, Daggers, One Hand Swords | Claws, Daggers, One Hand Swords | [6, 7, 9] |
| Vaal Burning Arrow | `vaal_burning_arrow` | Bows | Bows | [13] |
| Vaal Caustic Arrow | `vaal_caustic_arrow` | Bows | Bows | [13] |
| Vaal Cleave | `vaal_cleave` | One Hand Axes, One Hand Swords, Thrusting One Hand Swords | One Hand Axes, One Hand Swords, Thrusting One Hand Swords | [9, 10, 11] |
| Vaal Cyclone | `vaal_cyclone` | Claws, Daggers, One Hand Axes, One Hand Maces, One Hand Swords, Sceptres, Thrusting One Hand Swords | Claws, Daggers, One Hand Axes, One Hand Maces, One Hand Swords, Thrusting One Hand Swords | [6, 7, 9, 10, 11, 12, 32] |
| Vaal Double Strike | `vaal_double_strike` | Claws, Daggers, One Hand Axes, One Hand Maces, One Hand Swords, Sceptres, Thrusting One Hand Swords | Claws, Daggers, One Hand Axes, One Hand Maces, One Hand Swords, Thrusting One Hand Swords | [6, 7, 9, 10, 11, 12, 32] |
| Vaal Earthquake | `vaal_earthquake` | One Hand Axes, One Hand Maces, Sceptres, Staves | One Hand Axes, One Hand Maces | [11, 12, 32, 14] |
| Vaal Flicker Strike | `vaal_flicker_strike` | Claws, Daggers, One Hand Axes, One Hand Maces, One Hand Swords, Sceptres, Thrusting One Hand Swords | Claws, Daggers, One Hand Axes, One Hand Maces, One Hand Swords, Thrusting One Hand Swords | [6, 7, 9, 10, 11, 12, 32] |
| Vaal Glacial Hammer | `vaal_glacial_hammer` | One Hand Maces, Sceptres, Two Hand Maces | One Hand Maces, Two Hand Maces | [12, 32, 17] |
| Vaal Ground Slam | `vaal_ground_slam` | One Hand Maces, Sceptres, Staves, Two Hand Maces | One Hand Maces, Two Hand Maces | [12, 32, 14, 17] |
| Vaal Heavy Strike | `vaal_heavy_strike` | One Hand Axes, One Hand Maces, Sceptres, Staves, Two Hand Swords | One Hand Axes, One Hand Maces, Two Hand Swords | [11, 12, 32, 14, 15] |
| Vaal Ice Shot | `vaal_ice_shot` | Bows | Bows | [13] |
| Vaal Lightning Arrow | `vaal_lightning_arrow` | Bows | Bows | [13] |
| Vaal Lightning Strike | `vaal_lightning_strike` | Claws, Daggers, One Hand Axes, One Hand Maces, One Hand Swords, Sceptres, Thrusting One Hand Swords | Claws, Daggers, One Hand Axes, One Hand Maces, One Hand Swords, Thrusting One Hand Swords | [6, 7, 9, 10, 11, 12, 32] |
| Vaal Molten Strike | `vaal_molten_strike` | Claws, Daggers, One Hand Axes, One Hand Maces, One Hand Swords, Sceptres, Thrusting One Hand Swords | Claws, Daggers, One Hand Axes, One Hand Maces, One Hand Swords, Thrusting One Hand Swords | [6, 7, 9, 10, 11, 12, 32] |
| Vaal Power Siphon | `vaal_power_siphon` | Wands | Wands | [8] |
| Vaal Rain of Arrows | `vaal_rain_of_arrows` | Bows | Bows | [13] |
| Vaal Reave | `vaal_reave` | Claws, Daggers, One Hand Swords | Claws, Daggers, One Hand Swords | [6, 7, 9] |
| Vaal Smite | `vaal_smite` | One Hand Axes, One Hand Maces, One Hand Swords, Thrusting One Hand Swords, Two Hand Axes, Two Hand Swords | One Hand Axes, One Hand Maces, One Hand Swords, Thrusting One Hand Swords, Two Hand Axes, Two Hand Swords | [9, 10, 15, 11, 16, 12] |
| Vaal Spectral Throw | `vaal_spectral_throw` | Claws, Daggers, One Hand Axes, One Hand Maces, One Hand Swords, Sceptres, Thrusting One Hand Swords | Claws, Daggers, One Hand Axes, One Hand Maces, One Hand Swords, Thrusting One Hand Swords | [6, 7, 9, 10, 11, 12, 32] |
| Vaal Spectral Throw | `vaal_thrown_weapon` | Claws, Daggers, One Hand Axes, One Hand Maces, One Hand Swords, Sceptres, Thrusting One Hand Swords | Claws, Daggers, One Hand Axes, One Hand Maces, One Hand Swords, Thrusting One Hand Swords | [6, 7, 9, 10, 11, 12, 32] |
| Vaal Split Arrow | `vaal_split_arrow` | Bows | Bows | [13] |
| Vaal Sweep | `vaal_sweep` | Staves, Two Hand Axes, Two Hand Maces | Two Hand Axes, Two Hand Maces | [14, 16, 17] |
| Vaal Venom Gyre | `vaal_venom_gyre` | Claws, Daggers | Claws, Daggers | [6, 7] |
| Vaal Volcanic Fissure | `vaal_volcanic_fissure` | One Hand Maces, Sceptres, Two Hand Maces, Warstaves | One Hand Maces, Two Hand Maces, Warstaves | [12, 17, 32, 57] |
| Vengeance | `vengeance` | Claws, Daggers, One Hand Axes, One Hand Maces, One Hand Swords, Sceptres, Thrusting One Hand Swords | Claws, Daggers, One Hand Axes, One Hand Maces, One Hand Swords, Thrusting One Hand Swords | [6, 7, 9, 10, 11, 12, 32] |
| Venom Gyre | `venom_gyre` | Claws, Daggers | Claws, Daggers | [6, 7] |
| Vigilant Strike | `vigilant_strike` | Claws, Daggers, One Hand Axes, One Hand Maces, One Hand Swords, Sceptres, Thrusting One Hand Swords | Claws, Daggers, One Hand Axes, One Hand Maces, One Hand Swords, Thrusting One Hand Swords | [6, 7, 9, 10, 11, 12, 32] |
| Viper Strike | `viper_strike` | Claws, Daggers, One Hand Swords | Claws, Daggers, One Hand Swords | [6, 7, 9] |
| Void Shockwave | `support_void_shockwave` | One Hand Maces, Sceptres, Staves, Two Hand Maces | One Hand Maces, Two Hand Maces | [12, 32, 17, 14] |
| Void Shot | `void_shot` | Bows | Bows | [13] |
| Voidstorm | `triggered_voidstorm` | Bows | Bows | [13] |
| Volcanic Fissure | `volcanic_fissure` | One Hand Maces, Sceptres, Two Hand Maces, Warstaves | One Hand Maces, Two Hand Maces, Warstaves | [12, 17, 32, 57] |
| Whirling Blades | `whirling_blades` | Daggers, One Hand Swords, Thrusting One Hand Swords | Daggers, One Hand Swords, Thrusting One Hand Swords | [7, 9, 10] |
| Whirling Blades | `whirling_blades_cooldown` | Daggers, One Hand Swords, Thrusting One Hand Swords | Daggers, One Hand Swords, Thrusting One Hand Swords | [7, 9, 10] |
| Wild Strike | `wild_strike` | Claws, Daggers, One Hand Axes, One Hand Maces, One Hand Swords, Sceptres, Thrusting One Hand Swords | Claws, Daggers, One Hand Axes, One Hand Maces, One Hand Swords, Thrusting One Hand Swords | [6, 7, 9, 10, 11, 12, 32] |
| Word of Fury | `word_of_fury_on_hit` | Bows, Claws, Daggers, Fishing Rods, One Hand Axes, One Hand Maces, One Hand Swords, Sceptres | Bows, Claws, Daggers, One Hand Axes, One Hand Maces, One Hand Swords | [13, 6, 7, 37, 11, 12, 9, 32] |
| Word of Ire | `word_of_ire_when_hit` | Bows, Claws, Daggers, Fishing Rods, One Hand Axes, One Hand Maces, One Hand Swords, Sceptres | Bows, Claws, Daggers, One Hand Axes, One Hand Maces, One Hand Swords | [13, 6, 7, 37, 11, 12, 9, 32] |
| Word of Spite | `word_of_spite_when_hit` | Bows, Claws, Daggers, Fishing Rods, One Hand Axes, One Hand Maces, One Hand Swords, Sceptres | Bows, Claws, Daggers, One Hand Axes, One Hand Maces, One Hand Swords | [13, 6, 7, 37, 11, 12, 9, 32] |
| Word of War | `word_of_war_on_kill` | Bows, Claws, Daggers, Fishing Rods, One Hand Axes, One Hand Maces, One Hand Swords, Sceptres | Bows, Claws, Daggers, One Hand Axes, One Hand Maces, One Hand Swords | [13, 6, 7, 37, 11, 12, 9, 32] |