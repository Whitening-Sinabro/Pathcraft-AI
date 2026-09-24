# Worker 1 collection report

Delivered 16 new guide records across 15 provisional families, with 11 records containing concrete stage/transition conditions. All records have approval_status collected_not_game_validated.

## Counts and definitions

| Measure | Count |
|---|---:|
| Tracked distinct candidate guide URLs discovered | 22 |
| Distinct candidate guides opened (including one excluded worker2 starter) | 17 |
| Retained opened guides | 16 |
| Retained guide/configuration samples | 16 |
| Retained families | 15 |
| Detail-extracted records, including deep | 16 |
| Deep-stage-extracted records | 11 |
| Detail-only records | 5 |
| Tracked discovery-only candidate guides | 5 |
| Counted blocked guides | 0 |
| Context sources opened (listing, tier list, poe.ninja) | 3 |
| Source rows | 25 |

Discovery count covers the curated candidate ledger in sources.jsonl, not every incidental footer/search result. Query aliases are not new guides. The 16 configuration samples include default/overview configurations; this does not claim 16 separately clicked interactive variants. Partial fields and inaccessible image labels remain explicit gaps. No popularity rank was invented.

## Every counted deep record

| Record / original page | Extracted condition and transition | Locator |
|---|---|---|
| [w1_oil](https://mobalytics.gg/poe-2/builds/fubgun-flameblast-oil-grenade) | Level 52; about 30000 gold; saved GCP and skill/support gems → Grenades until gem level requirement; then respec. | Build Overview; Equipment; How it Works |
| [w1_plants](https://mobalytics.gg/poe-2/builds/scorps-plants-coc-endgame-guide-scorpius) | Tier 1-7 maps → Move to mid at comfortable T7 and T8/9 entry. / More mana sustain → Add Thunderstorm; later Vines for dense maps. | Build Overview; Early Endgame; Equipment |
| [w1_ice](https://mobalytics.gg/poe-2/builds/ice-shot-deadeye) | Good critical bow and quiver, or Cadiro's Gambit → Finish noncrit setup before crit. / Approximately 450 ES helmet → Add ES hybrid defenses. | Equipment; How it Plays > Gear Progression |
| [w1_rue](https://mobalytics.gg/poe-2/builds/ruetoo-tactician-mirage) | 15-20 Divine budget; Runeforged Double Vision → Replace earlier setup after Olroth's Resolve nerf. | Build Overview; crit redesign notes L153-163 |
| [w1_beast](https://mobalytics.gg/poe-2/builds/spirit-walker-beast-master) | Act 3 after second lab; level-7 gem access; about 20000 gold → Respec Twister tree after sufficient useful companion passives. | Build Overview > Early Leveling; Defence |
| [w1_grim](https://mobalytics.gg/poe-2/builds/grim-totem-oracle-imexile) | Level 60+; >1500 mana before Archmage; roughly 2500 mana before EB → Aim 395 Spirit for four totems plus Archmage. | Build Overview; Build Variants L136-141 |
| [w1_spark_totem](https://mobalytics.gg/poe-2/builds/waggle-spell-totem-shaman) | End Act 2; three charm slots; Sacred Flow yields 120 Spirit → Author intends early swap; alternative wait level 55-60 for four totems. | Build Overview; Equipment L226-233 |
| [w1_cold](https://mobalytics.gg/poe-2/builds/cold-cast-on-crit-archmage-paintmaster) | Eye of Winter becomes available → Replace Frost Darts; use Deliberation, Considered Casting, Inevitable Critical. | Build Overview; Leveling L149-168 |
| [w1_shrine](https://mobalytics.gg/poe-2/profile/paintmaster/builds/melee-chronomancer) | After first Act 2 boss, roughly level 18; save three supports and level-5 skill gem → Respec caster passives into mace nodes. | Build Overview; Leveling L191-228 |
| [w1_afk](https://mobalytics.gg/poe-2/builds/afk-simulacrum-immortal-ritualist-lazyexile) | 3000 life; 6000 ES; 600 mana; 90% elemental and 75% chaos resistance → Establish wall/bolt/refraction loop using assigned weapon sets. | Minimum Stats L141-151; Starting the Loop L597-601 |
| [w1_twister](https://mobalytics.gg/poe-2/profile/fgkorbyn21/builds/0-5-full-screen-twister-martial-artist-endgame-build-guide) | Rigwald's Ferocity acquired → Movement tech overtakes sprinting after this support. | Build Overview L121-154; Equipment L310-325,372 |

Stage gates and mechanism descriptions are creator claims, not independently tested game facts. The Shaman early swap is expressly experimental; AFK entry includes minimum-stat conditions and actual loop setup; Twister movement upgrade has a specific support gate.

## Checks and remaining limits

JSON/schema, unique identifiers, source references, allowed statuses, date bounds, output scope and count consistency are checked locally. notes.md preserves a bounded poe.ninja numerical receipt for independent inspection. All 16 guides were explicitly opened; search-only candidates remain excluded. Exact item rolls and most support panels are incomplete, and selected tabs were not exhaustively traversed.

Public Mobalytics currently labels 0.5.5 FR but its older titles, league references, update dates and favorites are not fully consistent. poe.ninja renders Forbidden Rites and Runes of Aldur cohorts without patch numbers. This worker therefore does not declare an official current patch/season; parent can reconcile with its independently collected authority sources.

No user decision is required for this collection. Manager inspection and retention remain with the parent. Files: records.json, sources.jsonl, notes.md, report.md.

