> 후속 상태: 이 문서는 당시 진단/검토 근거를 보존합니다. 이후 A2 패시브 표시 사용자 확인과 Pathcraft 캠페인 구현·설치를 완료했습니다. 현재 결과는 [campaign_delivery_receipt.json](campaign_delivery_receipt.json) 및 [구현 보고서](campaign_composition_implementation_report.md)를 따릅니다. 신규 캠페인의 실게임 화면 검증은 본부가 별도로 진행합니다.

# Campaign path evidence and conditional fill plan

Task task_5703453be1d9 / Dispatch ctx_53a6582bf8e1 — 2026-09-21

## Decision

Saved evidence supports an attributed Warrior reference progression and existing stage-specific skill guidance, but does not establish five exact Kitava campaign passive snapshots or click order. Do not fill Act 1–Interlude merely by renaming XML trees 1/2/3/4. The current campaign files are incomplete as tree guides; absence of an authored path is a deliverable limitation, not proof of a native parsing defect. No build/generator mutation was made.

## Saved primary artifacts inspected

- `linked_update_pob.xml` SHA-256 `6a5f3885c4c4ea7b479912a0f8329fd49d897b280beb654e48e28f4bad4d4e9e`
- `linked_leveling.build` SHA-256 `65f600a2f398ccf121702c9f7b60a3163bc8e44c1e8adf538becc54d7c939021`
- `priority_29d39.xml` SHA-256 `29f57e9ebd6d7060ef3f6aa155c6121e4cb489da8a2c94c709c672c4e1c0a6ac`
- `cafe_act_video_transcript.json` SHA-256 `b147e3d3bf17b240803b54e5c3fbdc0a409823ead8501ed2b411925f3f7f013a`
- `cafe_update_video_transcript.json` SHA-256 `1b0a3eb440bc1cb88b86d0d5e42850ae42b4d28b104764b415af564d6fa2294d`

Context cross-check: `priority_taengjeong_kitava_shield_wall.md`, including saved cafe-author references to the separate Warrior guide. Saved transcript source URLs: https://www.youtube.com/watch?v=dcSWTFyF9TQ and https://www.youtube.com/watch?v=zaft1U-7klQ . These are distinct-author reference materials recommended by Tangjung, not recordings of Tangjung playing each act. ASR is not visual identification of passive IDs.

## Exact TreeSpec inventory

Linked XML Build is Warrior/Titan level 96 with automatic character level enabled. Specs contain no explicit character-level attribute or act mapping. Notes are blank. Counts include tree start nodes and are not spendable-point budgets. Ascendancy nodes below are identified by node ascendancyName or Ascendancy stringId; their removal alone does not validate a Kitava conversion.

| Spec title | All node IDs | General IDs | Ascendancy IDs | Internal ascendancy | Weapon set 1 / 2 |
|---|---:|---:|---:|---|---|
| 1 | 18 | 18 | 0 | none | 0 / 0 |
| 2 | 27 | 27 | 0 | none | 0 / 0 |
| Swap | 30 | 27 | 3 | Warrior2 | 0 / 0 |
| 3 | 62 | 57 | 5 | Warrior2 | 10 / 10 |
| 4 | 81 | 76 | 5 | Warrior2 | 16 / 16 |
| Interlude | 97 | 92 | 5 | Warrior2 | 16 / 16 |
| Early Mapping | 120 | 113 | 7 | Warrior2 | 19 / 19 |
| Titan Swap | 125 | 118 | 7 | Warrior1 | 16 / 16 |
| Nebuloch | 151 | 142 | 9 | Warrior1 | 22 / 22 |

Trees 1→2 add 9 IDs with no removal; 2→Swap adds 8 and removes 5 (including a transition into Warbringer). Thus even the early progression is not a monotonic acquisition list. Tree 1 contains Brutal (`marauder_brute_notable1`, 5710) and Smash (`melee55`, 45363); tree 2 also contains Blood Rush (`attack_speed55`, 39083) and Singular Purpose (`two_handed8`, 52392). These are real reference-tree IDs, not proven act-end allocations. Latest Tangjung XML contains only one untitled 151-ID Warrior3 Spec at observed character level 97; it supplies no campaign stages.

## SkillSet and level interpretation

| SkillSet title / id | XML Skill groups including empty | Evidence limitation |
|---|---:|---|
| 1 / 1 | 21 | Several alternative/repeated Mace Strike, Rolling Slam and Boneshatter groups, not 21 simultaneous skills or an acquisition order |
| Swap / 3 | 18 | Shield Wall level 7, Infernal Cry level 7, Freezing Mark level 7; also later spirit skills and granted groups |
| Titan / 4 | 10 | Separate ascendancy/endgame reference, not Kitava act stage |
| Nebuloch / 5 | 9 | Separate final weapon/build path; one Scavenged Plating group explicitly disabled |

SkillSet 1 includes level-5 early attacks but level-20 Pounce and Herald of Ash; this prevents treating gem levels as the character level of a consistent snapshot. Swap includes level-7 Shield Wall, level-10 Magma Barrier and level-20 Scavenged Plating. Gem `level` is not a character transition boundary. The saved linked_leveling.build has 17 skill groups and no passives or ascendancy; its broad level intervals do not prove acquisition levels.

## What the saved video evidence actually anchors

| Segment | Defensible evidence | Missing evidence for native tree fill |
|---|---|---|
| Act 1 | 01:07 early Rolling Slam/Boneshatter combo; 09:58 narrator begins two-handed nodes at character 11; later character 14 Perfect Strike; update adds Brink I | No passive IDs or proof that Spec 1 equals Act 1; the two-handed remark is consistent with Spec 2 but cannot identify its full set |
| Act 2 | 22:41 narrator swaps Shield Wall before ascendancy; saved 22:45 screen verifies gem 7; 26:34 explicitly Warbringer cooldown branch | Swap XML already contains Warbringer; it is not the exact pre-ascendancy screen snapshot or a Kitava tree |
| Act 3 | 28:19 Act 2 ends; 28:27–28:34 Shield Wall set1 and cry set2; 33:55 armour-break ascendancy; update 01:17–01:42 changes route | No ID-level correspondence of Spec 3 with the recorded stage; Warbringer mechanics cannot be assumed for Kitava |
| Act 4 | Updated 01:43–02:14 route/reward guidance; saved Tangjung elemental-golem order correction | Reward route does not identify a complete passive set or acquisition order |
| Interlude | Explicit XML title Interlude; video 55:11 onward describes reward priorities/free route order | 97 IDs include 5 Warbringer IDs; 92 general IDs remain a reference design requiring mechanical/point-budget review for Kitava |

The transcripts do not explicitly name the numeric Spec titles or enumerate passive IDs. Video 41:41 says the needed nodes are mostly taken but does not enumerate them. Screenshots used in the existing corpus verify limited skills/routes, not every tree.

## Concrete defensible fill plan (proposal only)

1. Preserve the source XML stages under exact original names in an attributed reference view, with separate author/ascendancy and no invented act label. Specs 1 and 2 can be shown as unascended Warrior reference allocations; Swap through Interlude remain Warbringer reference allocations. This provides inspectable real nodes without claiming they are Kitava campaign instructions.
2. For the requested five Kitava campaign files, develop the already-authorized, clearly labelled “Pathcraft source-based composition” if an original Kitava act source cannot be supplied. Use verified act skill/reward anchors above; use the 18/27/general-node sets only as candidate inputs, never automatic copies. Specify an explicit checkpoint for each act (reward completion and available points), chosen weapon/skill conditions, and actual Kitava ascendancy timing before assigning a set.
3. For that composition, review each candidate general-node effect for dependence on removed Warbringer cooldown/armour-break mechanics; check path connectivity from Warrior start, per-weapon-set point budgets, attribute choices, and transition refunds. Preserve source ID provenance and mark Pathcraft-added or removed nodes. Merely deleting AscendancyWarrior2 nodes is not sufficient. Do not derive progression by intersecting with endgame151; those overlaps are not level routes.
4. Acquire one of: an author-labelled act-to-Spec map, saved tree-screen identification at each checkpoint, or manager approval of an independently validated Pathcraft checkpoint plan. Until then, keep exact act passive assignment unresolved. Existing evidenced skill groups can remain, but false confidence about their displayed crafting recommendations must not be added.
5. After the manager selects and validates the plan, native owner produces a minimal patch; manager owns coordinated canonical/install/ZIP/HTML payload rollout and actual game acceptance. User scope already authorizes Pathcraft composition; manager evidence review and a follow-up task govern implementation and consistent rollout, without another user-approval gate.

## Display failure remains a separate issue

Root-confirmed campaign Act 3 explains that selected file’s missing tree. It does not explain user-confirmed absent skills and trees across several files. See native_game_diagnosis.md follow-up for stale saved config and unresolved current gem type/tier/filter/level state. Filling tree content must not be described as fixing the all-files display problem.

Authority clarification from manager msg_16f7dd11daae: source-based Pathcraft composition is already within the user-authorized build creation/campaign gap objective. Missing evidence is an engineering validation task, not a requirement to ask the user for permission again. A follow-up task will validate concrete checkpoints; this dispatch prioritizes the two display probes.
