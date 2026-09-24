# Worker 2 collection report

Delivered 17 opened creator-guide variants across 14 distinct skill/mechanic families, with 12 concrete stage/transition extracts. All records are collected_not_game_validated; none is 1.0 approved.

## Accounting

| Measure | Count |
| --- | ---: |
| Persisted discovered source URLs | 25 |
| Successfully opened source URLs | 21 |
| Opened creator-guide URLs | 17 |
| Guide variants represented | 17 |
| Distinct families | 14 |
| Detail extracted, inclusive of deep | 17 |
| Deep stage extracted | 12 |
| Detail-only records | 5 |
| Opened context/secondary pages, not guides | 4 |
| Blocked source URLs retained | 2 |
| Discovery-only source URLs retained | 2 |

Search returned further irrelevant or duplicate leads; 25 is the bounded persisted ledger count, not an exhaustive search-engine hit count. Additional failed Maxroll clicks are not added to the URL ledger because their target URLs were not resolved. Internal stage-tab labels do not inflate guide or variant counts.

## Deep evidence register

| Record | Concrete gate | Extracted transition | Source and locator |
| --- | --- | --- | --- |
| w2-ice | Level 31 | Replace Lightning Arrow/Rod after unlock | [w2-s01](https://mobalytics.gg/poe-2/profile/fubgun/builds/0-5-ice-shot-deadeye-leveling-guide) — Build Overview; Equipment lines 113-117, 240-255 |
| w2-arc | Act 2 | Replace Essence Drain and Contagion | [w2-s02](https://mobalytics.gg/poe-2/profile/spud-the-king-nksem3/builds/sorceress-leveling-0-5-league-starter) — How it Plays lines 514-522 |
| w2-grenade | Level 14 before Geonor | Add newly unlocked grenade | [w2-s03](https://mobalytics.gg/poe-2/profile/guythatdies/builds/0-4-mercenary-grenades-leaguestarter) — Build Variants; Equipment; Skill Gems lines 114-122,190-202,272-279 |
| w2-glacial | Hollow Palm Technique obtained | Unequip weapon | [w2-s04](https://mobalytics.gg/poe-2/builds/hollow-palm-levelling) — Equipment and Skill Gems lines 190-246 |
| w2-varashta | Act 2 ascension, level-19 variant | Replace early spell setup after ascending | [w2-s05](https://mobalytics.gg/poe-2/builds/varashta-levelling) — Build Overview; Variants; Equipment lines 109-133,201-220 |
| w2-edc | Level 6 then level 14 | Unlock ED at 6; separate chaos/physical weapon sets at 14 | [w2-s07](https://mobalytics.gg/poe-2/builds/bone-storm-leaguestarter) — Build Variants; Equipment lines 119-190 |
| w2-slam | Perfect Strike acquired | Change boss rotation from Mace Strike; retain it as alternative | [w2-s08](https://mobalytics.gg/poe-2/builds/warrior-leveling-woolie) — Very Important Info; Skill Rotation lines 128-175 |
| w2-twister-far | Level 6, first level-3 gem | Optional replacement for Frost Bomb/Ice Nova chilled-ground setup | [w2-s11](https://mobalytics.gg/poe-2/builds/xthefarmerx-s-gemling-twister-league-starter) — Build Variants; Equipment lines 152-192 |
| w2-plants | Level-4 Spirit gem then level-5 skill gem | Add Corrosion swarm then boss-damage spell | [w2-s12](https://mobalytics.gg/poe-2/builds/plant-oracle-druid?_lang=en_us) — Act 1 checklist lines 139-153 |
| w2-shield | Level 22 | Replace early Rolling Slam/Boneshatter setup | [w2-s14](https://mobalytics.gg/poe-2/builds/warrior-league-start-lundburgerr) — Build Overview; Variants lines 114-150 |
| w2-wyvern-gtd | Level 31 then 36 | Add barrage then replace stun-only charge generation with illusions | [w2-s16](https://mobalytics.gg/poe-2/builds/wyvern-druid-leveling) — Equipment 178-188; How it Plays 410-435 |
| w2-wyvern-peu | Level 31 then tier-4 supports | Use for bosses first; expand to clearing after support access | [w2-s17](https://mobalytics.gg/poe-2/builds/0-4-hellfire-wyvern-league-starter) — Build Overview; Variants lines 111-184 |

A gear-triggered transition (Hollow Palm acquisition) and a skill-acquisition transition (Perfect Strike) are counted because the page specifies what changes; they do not invent numeric levels. Each row has the condition, action and source locator in records.json. The five remaining guides have useful opened detail but are not counted deep merely for listing act or budget headings.

## Patch and coverage limits

The official opened [0.5.5 notes](https://www.pathofexile.com/forum/view-thread/4000864) identify Forbidden Rites and say Runes of Aldur remains available. Records retain exact stated title/overview patch tokens, including 0.5 versus 0.5.0, separately from the shared 0.5.5 FR page tag. Update dates never substitute for patch evidence.

Historical title/body material is not an immutable archived patch snapshot. Interactive gear names, complete support links and passive allocations are incomplete; missing values remain null or empty with gaps. Damage and defense descriptions summarize creator advice, not tested mechanics. There are no HC/SC observations or measured player-share figures.

Maxroll explicit web opens failed, and Korean original-guide extraction remains unfulfilled. The opened Korean secondary summary contains translation concerns and is context only. May-dated prerelease/prospective advice, including Peuget2's work-in-progress ascendancy discussion, is retained as historical creator material with no release-performance validation; source dates are before the collection cutoff. Future content and POE1 build material are excluded.

## Checks

JSON parsing, required fields, unique IDs, source references, date cutoff, equipment role enumeration, and deep-stage conditions/locators were checked locally. The parent manager must independently review sources and decide whether any record is suitable for later implementation. No user decision is needed to retain this collection.

Files: records.json, sources.jsonl, notes.md, report.md. Only the assigned worker_output directory was written.

