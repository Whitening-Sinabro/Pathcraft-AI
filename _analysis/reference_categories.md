# 레퍼런스 필터 카테고리 분해 (Phase 1)

## 요약

- NeverSink HC Strict: 53 섹션
- Cobalt Strict: 53 섹션
- Cobalt UberStrict: 53 섹션
- Wreckers SSF: 25 ### 섹션 헤더

## NeverSink 섹션 코드 사전

| 코드 | 카테고리 | 우리 커버 |
|---|---|---|
| [0100] | Global Overrides | L0 HARD_HIDE, L1 CATCH_ALL, L2 DEFAULT_RARITY |
| [0200] | Gold | ❌ |
| [0300] | Influenced Items | ❌ |
| [0400] | Eldritch Items | ❌ |
| [0500] | Exotic Bases | ❌ |
| [0600] | ID Mod Filtering (Combinations) | ❌ |
| [0700] | ID Mod Filtering (Dual) | ❌ |
| [0800] | ID Mod Filtering (Single) | ❌ |
| [0900] | Early-game Crafting Bases | ❌ |
| [1000] | Crafting Bases | L6 T1_BORDER (부분) |
| [1100] | Unique Items | L7 BUILD_TARGET unique |
| [1200] | Leveling Items | ❌ |
| [1300] | Gems | L7 BUILD_TARGET gem |
| [1400] | Flasks | ❌ |
| [1500] | Jewels | ❌ |
| [1600] | Endgame Rare Gear | ❌ |
| [1700] | Endgame Rare Decorators | ❌ |
| [1800] | Endgame Rare Exotic Veiled | ❌ |
| [1900] | Endgame Rare Exotic Corrupted | ❌ |
| [2000] | Endgame Rare Conditional Hide | ❌ |
| [2100] | Endgame Rare Amulets/Rings/Boots | ❌ |
| [2200] | Endgame Rare Droplevel Hiding | ❌ |
| [2300] | Endgame Crafting Projects | ❌ |
| [2500] | Endgame Flasks & Tinctures | ❌ |
| [2600] | Scouring & Special Sockets | ❌ |
| [2700] | Gems (detailed) | ❌ |
| [3000] | Divination Cards | L7 divcard, L8 divcards 기본 |
| [3100] | Jewelry (Amulets/Rings/Belts) | ❌ |
| [3300] | Trinkets | ❌ |
| [3400] | Utility Flasks | ❌ |
| [3500] | Map Fragments | L8 'Map Fragments' class (부분) |
| [3600] | Scarabs | ❌ |
| [3700] | Essences | ❌ |
| [3800] | Fossils & Resonators | ❌ |
| [3900] | Breach | ❌ |
| [4000] | Incubators | ❌ |
| [4100] | Delve | ❌ |
| [4200] | Harvest (Lifeforce) | ❌ |
| [4300] | Currency (Stackable) | L8 currency (4티어만) |
| [4400] | Quest Items Override 1 | ❌ |
| [4500] | Quest Items Override 2 | ❌ |
| [5000] | Blight | ❌ |
| [5100] | Delirium | ❌ |
| [5200] | Heist | ❌ |
| [5300] | Expedition (Logbook/Coinage) | ❌ |
| [5400] | Sentinel | ❌ |
| [5500] | Sanctum | ❌ |
| [5600] | Ritual | ❌ |
| [5700] | Synthesis | ❌ |
| [5800] | Ultimatum | ❌ |
| [5900] | Legion (Splinters) | ❌ |
| [6000] | Atlas Special | ❌ |
| [6100] | Maps | L8 maps 4티어 |
| [7000] | Hide Layer | ❌ |
| [9000] | Final Overrides | ❌ |

## SSF 필수 카테고리 (Phase 3 우선순위)

- `[4200]` **Harvest (Lifeforce)** — 미구현
- `[5900]` **Legion (Splinters)** — 미구현
- `[4300]` **Currency (Stackable)** — 부분
- `[3500]` **Map Fragments** — 부분
- `[3600]` **Scarabs** — 미구현
- `[3700]` **Essences** — 미구현
- `[3800]` **Fossils & Resonators** — 미구현
- `[4400]` **Quest Items Override 1** — 미구현
- `[1400]` **Flasks** — 미구현
- `[3900]` **Breach** — 미구현
- `[5000]` **Blight** — 미구현
- `[5100]` **Delirium** — 미구현
- `[5200]` **Heist** — 미구현

## Wreckers SSF 특화 섹션 (참조 모델)

- My Colours and themes explained
- CATCH-ALL
- DEFAULT COLOURS & SIZING
- Default colours & T1 Borders
- Catch All, "WTF is that?!" items, new items, items with unique mods, & special B
- Corrupted, Tainted, Mirrored # Needs to be above ALL hidden items
- Default colours & T1 Borders
- Hiding basic Normal & Magic items
- Items that shouldn't be hidden yet / More T1 Borders
- HIDE PROGRESSION
- Levelling Help # Needs to be above the Guide Specific restrictions.
- List of Hidden Items Section (applied only for the "Builds Only" filter)
- ITEMS THAT ALWAYS SHOW   # Needs to be below all hidden items.
- Equippable Items I Always Want Showing
- Gems
- Flasks
- Stackable Currency # Using "Currency" instead of "Stackable" because of Delve's 
- Maps
- Map Fragments
- Pieces
- Misc Map Items
- Divination Cards
- Quest
- LEAGUE / NEW ITEMS   # Just: SetBorderColor 255 123 0 # Orange & SetFontSize 35+
- RECIPES (& Quality Progression)   # Needs to be below ALL hidden items. (May as 
