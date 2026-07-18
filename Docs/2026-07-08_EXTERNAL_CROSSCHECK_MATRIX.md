# POE1 External Crosscheck Matrix (3.22~3.28)

작성 시각: 2026-07-08 12:20 +07:00

## 목적

기존 로컬 queue와 real-case seed는 일부 patch에서 메타 대표성을 과소/과대평가하고 있었다.
이 문서는 `Reddit build index`, `Maxroll`, `PoE Vault`, `공식 패치 노트`를 교차 사용해 patch별 대표 후보를 다시 검증하는 중간 매트릭스다.

판정 라벨:

- `cross_checked`: 외부 소스 2개 이상에서 확인
- `single_source`: 외부 소스 1개에서만 확인
- `source_gap`: 현재 확보한 외부 소스에서 아직 확인 못함
- `stale_local_queue`: 현재 로컬 queue가 외부 근거 대비 뒤처짐

strict verification 메모:

- `standard_confirmable`: 외부 빌드 가이드 1개 + 보조 근거 1개 이상
- `strict_confirmable`: 서로 다른 외부 빌드 가이드 계열 2개 이상
- `strict_gap`: 현재 seed는 가능하지만 strict 확정은 금지

## 3.22 Trial of the Ancestors

확인 소스:

- Reddit 검색 결과: `3.22 Trial of the Ancestors League Start Build Index - Reddit`
- Maxroll: `Top 10 Ancestor League Starter Builds`
- PoE Vault: `[3.22] Trial of the Ancestors League Starters`

Maxroll Top 10:

- Righteous Fire Inquisitor
- Boneshatter Juggernaut
- Corrupting Fever Champion
- Cold DoT Elementalist
- Toxic Rain Pathfinder
- Explosive Arrow Elementalist
- Impending Doom Pathfinder
- Lightning Arrow Deadeye
- Detonate Dead Elementalist
- Hexblast Mine Saboteur

PoE Vault starters:

- Lightning Arrow Deadeye
- Minion Army Necromancer
- Storm Brand Inquisitor
- Herald of Agony Champion
- Spectral Shield Throw Raider
- Righteous Fire Inquisitor
- Righteous Fire Juggernaut
- Explosive Arrow Ballista Champion
- Shockwave Totems Hierophant
- Firestorm Inquisitor
- Mage Skeleton Guardian
- Zoomancer Necromancer
- Poison Summon Raging Spirits Necromancer
- Ice Shot Deadeye
- Corrupting Fever Champion
- Boneshatter Juggernaut

중간 판정:

- `Shockwave Totems Hierophant`: `single_source` but high-priority correction
- `Lightning Arrow Deadeye`: `cross_checked`
- `Toxic Rain / Pathfinder`: `cross_checked`
- `Boneshatter Juggernaut`: `cross_checked`
- `Corrupting Fever Champion`: `cross_checked`
- 현재 로컬 `3.22` queue는 `Shockwave Totem` 누락으로 `stale_local_queue`

## 3.23 Affliction

확인 소스:

- Maxroll: `New Affliction League Starters & More`
- PoE Vault: `Affliction League Starters`

Maxroll starters:

- Boneshatter Juggernaut
- Boneshatter Slayer
- Corrupting Fever Champion
- Explosive Arrow Ballista
- Hexblast Mines Saboteur
- Ice Shot Deadeye
- Lightning Arrow Deadeye
- Maw of Mischief
- Toxic Rain Pathfinder
- Detonate Dead Ignite
- SRS Guardian

PoE Vault starters:

- Lightning Arrow Deadeye
- Tornado Shot Deadeye
- Minion Army Necromancer
- Caustic Arrow Occultist
- Ice Trap Saboteur
- Herald of Agony Champion
- Spectral Shield Throw Raider
- Righteous Fire Inquisitor
- Righteous Fire Juggernaut
- Hexblast Miner Saboteur
- Shockwave Totems Hierophant
- Wintertide Brand Occultist
- Summon Raging Spirit Guardian
- Poison Summon Raging Spirits Necromancer
- Ice Shot Deadeye
- Boneshatter Juggernaut

중간 판정:

- `Lightning Arrow Deadeye`: `cross_checked`
- `Hexblast Miner Saboteur`: `cross_checked`
- `Ice Shot Deadeye`: `cross_checked`
- `Boneshatter Juggernaut`: `cross_checked`
- `Shockwave Totems Hierophant`: `single_source`
- 기존 로컬 `3.23` queue는 `Penance Brand` 과대, `Shockwave Totem / Hexblast / Boneshatter` 미반영 가능성 높음

## 3.24 Necropolis

확인 소스:

- Maxroll: `New Necropolis League Starters & More`
- PoE Vault: `Necropolis League Starters`
- 로컬 Reddit index trace 존재

Maxroll new starters / updated starters 핵심:

- Explosive Arrow Ballista Champion
- Ice Trap of Hollowness Trickster
- Wave of Conviction Ignite Elementalist
- Exsanguinate Mine Trickster
- Archmage Ball Lightning Hierophant
- Frostblink Ignite Elementalist
- Boneshatter Juggernaut
- Corrupting Fever Champion
- Hexblast Mines Saboteur
- Ice Shot Deadeye
- Lightning Arrow Deadeye
- Toxic Rain Pathfinder
- Detonate Dead Ignite

PoE Vault starters:

- Lightning Arrow Deadeye
- Minion Army Necromancer
- Caustic Arrow Occultist
- Poison Summon Raging Spirits Necromancer
- Ice Trap Saboteur
- Herald of Agony Champion
- Spectral Shield Throw Raider
- Righteous Fire Inquisitor
- Righteous Fire Juggernaut
- Splitting Steel Champion
- Detonate Dead Ignite Elementalist
- Explosive Arrow Ballista Champion
- Zoomancer Necromancer
- Dominating Blow Necromancer
- Ice Shot Deadeye
- Boneshatter Juggernaut
- Lacerate Gladiator

중간 판정:

- `Lightning Arrow Deadeye`: `cross_checked`
- `Explosive Arrow Ballista Champion`: `cross_checked`
- `Detonate Dead Ignite`: `cross_checked`
- `Boneshatter Juggernaut`: `cross_checked`
- `Exsanguinate Mine Trickster`: `single_source` but direct Maxroll confirmation
- `Archmage Ball Lightning Hierophant`: `single_source` but direct Maxroll confirmation
- 기존 로컬 `3.24` queue는 `Exsanguinate Mine Trickster`, `Archmage Ball Lightning Hierophant` 미반영으로 보수적

## 3.25 Settlers of Kalguur

확인 소스:

- Maxroll: `New Settlers of Kalguur League Starter Builds`
- PoE Vault: `Settlers of Kalguur League Starters`
- 로컬 Reddit index trace 존재

Maxroll에서 직접 보인 항목:

- Chaos Minion Army Necromancer
- Ice Shot of Penetration Deadeye
- Lacerate Gladiator
- Lightning Strike Deadeye
- Hexblast Mines Saboteur -> Trickster
- Boneshatter Juggernaut
- Explosive Arrow Ballista Elementalist
- Ice Shot Deadeye
- Lightning Arrow Deadeye

PoE Vault starters:

- Minion Army Necromancer
- Poison Summon Raging Spirits Necromancer
- Tornado Inquisitor
- Ground Slam Slayer
- Explosive Concoction Ascendant
- Lightning Strike Warden
- Cyclone Slayer
- Hexblast Miner Saboteur
- Righteous Fire Inquisitor
- Righteous Fire Juggernaut
- Zoomancer Necromancer
- Dominating Blow Necromancer
- Holy Relic Guardian
- Ice Shot Deadeye
- Boneshatter Juggernaut
- Lacerate Gladiator
- Lightning Arrow Deadeye

로컬 Reddit trace:

- Spark
- Ball Lightning
- Lacerate

중간 판정:

- `Lacerate`: `cross_checked`
- `Lightning Arrow Deadeye`: `cross_checked`
- `Boneshatter Juggernaut`: `cross_checked`
- `Hexblast Miner`: `cross_checked`
- `Lightning Strike`: `cross_checked` at archetype level
- `Spark / Ball Lightning`: `single_source` via local Reddit trace only

## 3.26 Secrets of the Atlas

확인 소스:

- PoE Vault: `Secrets of the Atlas League Starters`
- 로컬 Reddit index trace 존재

PoE Vault starters:

- Lightning Arrow Deadeye
- Blight of Contagion Trickster
- Arc Elementalist
- Siege Ballista Hierophant
- Poison Summon Raging Spirits Necromancer
- Holy Relic Necromancer
- Righteous Fire Inquisitor
- Righteous Fire Juggernaut
- Spectre Summoner Necromancer
- Dominating Blow Champion
- Poison Animate Weapon Necromancer
- Ice Shot Deadeye
- Boneshatter Juggernaut
- Cyclone Slayer

로컬 Reddit trace:

- Ice Nova
- Ball Lightning
- Spark
- Earthquake

중간 판정:

- `Lightning Arrow Deadeye`: `single_source` external + local support elsewhere
- `Ball Lightning / Spark / Ice Nova / Earthquake`: `single_source` via Reddit trace only
- `Siege Ballista Hierophant`: `single_source` via PoE Vault
- `3.26`은 source split이 커서 추가 교차검증 필요

## 3.27 Keepers of the Flame

확인 소스:

- PoE Vault: `Keepers of the Flame League Starters`
- 로컬 Reddit build index trace 존재

PoE Vault starters:

- Blight of Contagion Trickster
- Volatile Dead Spellslinger Elementalist
- Toxic Rain Pathfinder
- Pyroclast Mine Saboteur
- Siege Ballista Hierophant
- Poison Summon Raging Spirits Necromancer
- Holy Relic Necromancer
- Spectre Summoner Necromancer
- Dominating Blow Champion
- Lacerate Gladiator
- Cyclone Slayer

로컬 Reddit trace:

- Ice Nova
- Vortex
- Lacerate
- Dominating Blow
- Detonate Dead
- Penance Brand 흔적 일부

중간 판정:

- `Lacerate`: `cross_checked`
- `Dominating Blow`: `cross_checked`
- `Ice Nova / Vortex / Detonate Dead`: `single_source` via Reddit trace
- `Pyroclast Mine Saboteur / Siege Ballista Hierophant`: `single_source` via PoE Vault

## 3.28 Mirage

확인 소스:

- PoE Vault: `Mirage League Starters`
- 공식 패치 노트 3.28.0
- 로컬 transcript / user recall

PoE Vault starters:

- Blight of Contagion Trickster
- Volatile Dead Spellslinger Elementalist
- Sunder Ignite Elementalist
- Toxic Rain Pathfinder
- Pyroclast Mine Saboteur
- Siege Ballista Hierophant
- Poison Summon Raging Spirits Necromancer
- Holy Relic Necromancer
- Spectre Summoner Necromancer
- Dominating Blow Guardian
- Lacerate Gladiator
- Cyclone Slayer
- Boneshatter Juggernaut
- Cold Snap of Power Hierophant
- Shock Nova of Procession Hierophant

공식 패치 노트 확인:

- `Kinetic Fusillade of Detonation` 신규 추가
- `Shock Nova of Procession` 신규 추가
- `Penance Brand` 상향
- `Dominating Blow` 상향
- `Storm Brand` 상향
- `Orb of Storms` 상향

중간 판정:

- `Shock Nova of Procession Hierophant`: `cross_checked` (PoE Vault + official patch note)
- `Dominating Blow Guardian`: `cross_checked` (PoE Vault + official patch note buff)
- `Kinetic Fusillade of Detonation`: `single_source` official patch note only so far
- `Penance Brand`: `single_source` official patch note buff + local discussion 흔적
- `Cold Snap of Power Hierophant`: `single_source` via PoE Vault
- `Connor Converse Strength Stacker`: `personal_target`, non-flagship 유지

## 즉시 교정 포인트

1. `3.22` queue에 `Shockwave Totems Hierophant`가 반드시 재검토 후보로 들어가야 한다.
2. `3.23` queue는 `Penance Brand` 중심이 아니라 `Lightning Arrow / Hexblast / Boneshatter / Ice Shot / Shockwave Totem` 축으로 재설계해야 할 가능성이 높다.
3. `3.24`는 `Exsanguinate Mine Trickster`와 `Archmage Ball Lightning Hierophant`를 외부 확인 후보로 올려야 한다.
4. `3.28`은 `Shock Nova of Procession Hierophant`와 `Kinetic Fusillade of Detonation`을 후보 풀에 반영해야 한다.
5. `3.25~3.28`은 `PoE Vault + Reddit/local trace + official patch notes`를 조합하면 기존 queue보다 훨씬 넓은 메타 풀이 나온다.

