> 후속 상태: 이 문서는 당시 진단/검토 근거를 보존합니다. 이후 A2 패시브 표시 사용자 확인과 Pathcraft 캠페인 구현·설치를 완료했습니다. 현재 결과는 [campaign_delivery_receipt.json](campaign_delivery_receipt.json) 및 [구현 보고서](campaign_composition_implementation_report.md)를 따릅니다. 신규 캠페인의 실게임 화면 검증은 본부가 별도로 진행합니다.

# Native game display diagnosis — 2026-09-21

Task task_ba3a9c6fbf18 / Dispatch ctx_e3c941540417

## Verdict

Actual game file-load success is confirmed for all 10 Tangjung files; root has now confirmed campaign Act 3 selection in a screenshot, while latest-06 activation and visible skill/passive overlays remain unverified. No native format defect has been established, so no generator, build, canonical, installation, HTML, ZIP, or product change is justified by this investigation. Campaign passives are genuinely empty by design, which explains absent campaign tree guidance for the root-observed Act 3 selection; this does not explain the user-reported failure across several files.

## Official contract checked directly

Source: https://www.pathofexile.com/developer/docs/game#buildplanner (directly opened 2026-09-21). Skills provide recommendations through uncut skill/spirit gem crafting; they do not equip skill slots. Passives appear in the passive tree. Meta gems are unsupported. level_interval is optional; the official example omits it. The documentation does not specify its omitted runtime default, so a guessed default level must not be inserted. weapon_set accepts 0–2.

## Reproduced checks

- All 23 installed builds decode as UTF-8 without BOM and parse as JSON.
- All 10 source/canonical/installed triples have matching SHA-256 using installed_filename_mapping from the canonical receipt.
- All 10 pass existing allowed-key/type/required-field checks, all passive string IDs exist in the supplied tree, and all skill/support Metadata IDs exist in the supplied BaseItemTypes and SkillGems tables. This is static validation against supplied data, not proof of current client overlay rendering.
- Latest XML active Spec exactly matches 151 (stringId, weapon_set) pairs: common=104, set1=24, set2=23; ascendancyInternalId and exported ascendancy are Warrior3.
- Mixed Metadata/Items/Gem and Metadata/Items/Gems paths are actual supplied table IDs; pluralizing paths speculatively would corrupt IDs.
- All 13 existing comparator files omit passive level_interval. The existing Gemling Legionnaire poe.ninja file also omits it on all 12 skills.
- Existing comparator common passives omit weapon_set; new files explicitly use 0. Both fit the documented contract; no rendering equivalence test was performed.
- Existing comparator ascendancies are Warrior2/Mercenary3, not Warrior3, so they do not prove Kitava-specific display behavior.

| Canonical | Installed | Skills | Passives | SHA-256 |
|---|---|---:|---:|---|
| campaign-act1.build | 탱정_01_액트1_철퇴육성.build | 5 | 0 | e619e2be271ff530ad8b3445e1193e4cb1872a8538fed9ddce0ba88e0352f400 |
| campaign-act2.build | 탱정_02_액트2_방패벽전환.build | 5 | 0 | 90879f37e5f291d797b9819669a0fba90899e0efaf59311ce2d9bd3d849ab0e5 |
| campaign-act3.build | 탱정_03_액트3_방패벽유지.build | 7 | 0 | d0c08fb1b6ec8926051e443a7bc5277eed25578fc926921dc4bf3364fb7ff8bd |
| campaign-act4.build | 탱정_04_액트4_보상과장비.build | 7 | 0 | 2d7e6c095ce3e55b8bad9c876a7c0fb836d6b5739a3b09b09e9943571aca4cea |
| campaign-interlude.build | 탱정_05_막간_방패개선.build | 7 | 0 | cf2a265d894d7dead8902a44dedd816935af20bef5b441aaeed94e9af4079bd8 |
| current-kitava-29d39.build | 탱정_06_최신_키타바방패벽_저자본.build | 7 | 151 | 2f94a19b6e7b854be5d7151fd6ef81e76e326d41da8ef0933cfa9bf2bd171ff5 |
| archive-28509.build | 탱정_참고_과거_일반갑옷과철퇴.build | 9 | 124 | 62abaf7a9a9d794a568299c70343d7cfdb5556317783bb4a179771ee658316fc |
| archive-285e2.build | 탱정_참고_과거_방패와보조보강.build | 9 | 125 | bfa528b1013e42c10d67a37a5e54a69512de6c79ccf329826582ca764720a7d7 |
| archive-28604.build | 탱정_참고_과거_황동철갑전환.build | 7 | 126 | 42714a0254a0dc2d964f1f1921e9c7c38cdec5cca2d97b56cf805edf664df5b0 |
| archive-28695.build | 탱정_참고_과거_투구교체_ConstrictingCommand.build | 7 | 127 | 696509f805ff2594dcaf26e0cd14d99342de3d34cb59bb4c114aadef44733382 |

## Current game log evidence

Log read only: `C:\Program Files (x86)\Grinding Gear Games\Path of Exile 2 - poe2_production\logs\Client.txt`. Bounded scan: last 5,000 lines, filtered to BuildPlanner and current PID 28244 supplied by coordinator. LatestClient.txt was empty at observation. All 23 files have explicit load-success messages at 2026/09/21 21:36:08; the 10 relevant messages follow. This confirms loader acceptance, not active selection or node visibility.

```text
2026/09/21 21:36:08 33723031 19801446 [DEBUG Client 28244] [BuildPlanner] Successfully loaded build 'file:C:/Users/User/Documents/My Games/Path of Exile 2/BuildPlanner/탱정_01_액트1_철퇴육성.build'
2026/09/21 21:36:08 33723031 19801446 [DEBUG Client 28244] [BuildPlanner] Successfully loaded build 'file:C:/Users/User/Documents/My Games/Path of Exile 2/BuildPlanner/탱정_02_액트2_방패벽전환.build'
2026/09/21 21:36:08 33723031 19801446 [DEBUG Client 28244] [BuildPlanner] Successfully loaded build 'file:C:/Users/User/Documents/My Games/Path of Exile 2/BuildPlanner/탱정_03_액트3_방패벽유지.build'
2026/09/21 21:36:08 33723031 19801446 [DEBUG Client 28244] [BuildPlanner] Successfully loaded build 'file:C:/Users/User/Documents/My Games/Path of Exile 2/BuildPlanner/탱정_04_액트4_보상과장비.build'
2026/09/21 21:36:08 33723031 19801446 [DEBUG Client 28244] [BuildPlanner] Successfully loaded build 'file:C:/Users/User/Documents/My Games/Path of Exile 2/BuildPlanner/탱정_05_막간_방패개선.build'
2026/09/21 21:36:08 33723031 19801446 [DEBUG Client 28244] [BuildPlanner] Successfully loaded build 'file:C:/Users/User/Documents/My Games/Path of Exile 2/BuildPlanner/탱정_06_최신_키타바방패벽_저자본.build'
2026/09/21 21:36:08 33723031 19801446 [DEBUG Client 28244] [BuildPlanner] Successfully loaded build 'file:C:/Users/User/Documents/My Games/Path of Exile 2/BuildPlanner/탱정_참고_과거_방패와보조보강.build'
2026/09/21 21:36:08 33723031 19801446 [DEBUG Client 28244] [BuildPlanner] Successfully loaded build 'file:C:/Users/User/Documents/My Games/Path of Exile 2/BuildPlanner/탱정_참고_과거_일반갑옷과철퇴.build'
2026/09/21 21:36:08 33723031 19801446 [DEBUG Client 28244] [BuildPlanner] Successfully loaded build 'file:C:/Users/User/Documents/My Games/Path of Exile 2/BuildPlanner/탱정_참고_과거_투구교체_ConstrictingCommand.build'
2026/09/21 21:36:08 33723031 19801446 [DEBUG Client 28244] [BuildPlanner] Successfully loaded build 'file:C:/Users/User/Documents/My Games/Path of Exile 2/BuildPlanner/탱정_참고_과거_황동철갑전환.build'
```

WATCH Invalidate messages at 21:31:32 show file watcher invalidation, not a JSON validation error. The scanned BuildPlanner messages contain no failure; absence of a logged error cannot establish display success. Kerning errors occur around both old and new file interactions and already predate this loading event; no causal link to missing recommendations is established.

## What remains for root integration

1. Root has confirmed campaign Act 3 selection; its absent tree is an acknowledged content limitation. The user reports several files all show no skills/passives, so this observation does not settle the wider issue. Latest-06 activation remains unverified.
2. For latest 06, inspect passive-tree guidance separately for common nodes and weapon sets 1/2; do not allocate/refund nodes.
3. Inspect recommendations in the appropriate uncut gem crafting interface, not equipped skill slots; record character level, gem tier/type, and filters without consuming gems. The latest supplied gem-table minimum requirements vary (Eternal Rage 59, War Banner/Scavenged Plating 11, Elemental Weakness/Shield Wall/Freezing Mark 23, Infernal Cry 7), which is context to inspect, not an inferred transition rule.
4. Only after a reproducible field-specific failure should a minimal backed-up source patch and controlled root-owned deployment be proposed. Do not mass-add level_interval, fabricate Kitava campaign nodes, or copy another ascendancy.

## Changes and boundaries

Only this report was intentionally created. No repair claimed, no install performed, no game input, no process action, no new agent, and no HTML-worker assets touched. Root owns real-game acceptance and any coordinated canonical/ZIP/embedded-native deployment.

## Follow-up — task_5703453be1d9 / ctx_53a6582bf8e1

Current observations supersede the earlier unknown-selection statement: root reports campaign Act 3 selected in `C:/Users/User/AppData/Local/Temp/orca-computer-use/a5a1db94-1aa1-473b-bd20-c574d1b8b817-screenshot.png`. This worker did not operate the GUI. User confirms several files all show no skills/passives. Do not classify the entire complaint as campaign-empty or user-interface misunderstanding: these remain only partial explanations. Latest-06 actual activation and display have not been demonstrated; root has stopped further game input.

Narrow read-only config inspection of `C:/Users/User/Documents/My Games/Path of Exile 2/poe2_production_Config.ini`:

- Last write 2026-09-21 21:14:36 local, older than root's selection observation. Saved `active_builds` has 23 per-character records and zero Tangjung filenames. This stale persisted value cannot contradict the observed in-memory selection. Character names and unrelated account information are omitted from this report.
- `gemcutting_restrictions=true`; `cache_gem_crafter_search=` is empty. These are observed stored values, not proven current crafting filter state or a cause. Actual character level, opened gem type/tier, current tab, and in-memory filters remain unavailable.
- `additional_support_gem_popup=true`, `open_gem_panel_on_gem_pickup=true`.
- `passive_keyword_search_active=true`, `passive_keyword_search_glow=1`, `passive_keyword_search_exclude_brightness=0.5` (same player-2 values). The inspected file contains no identified BuildPlanner-specific disable/display key. No causal effect of keyword search on planner overlays was established.
- No settings were changed. The optional `level_interval` contract does not establish an omitted runtime default and no speculative level patch was made.

The bounded follow-up log inspection did not expose a current selection event or filter state; loader success is the previously established evidence and will not be treated as display success. Campaign source inventory and a conditional fill plan are in `campaign_path_evidence.md`. The all-files display complaint remains unresolved without root-owned UI evidence or a reproducible parser/rendering defect.

## Compatibility probe authorized by manager (same follow-up dispatch)

New user-confirmed discriminator: existing files display correctly; Tangjung files do not. This increases priority of a controlled content/format comparison and does not prove a global UI setting fault. Manager messages msg_1c49c87da94e and msg_3bd403f144ab authorize a separate source-only compatibility probe.

Created `native_planner/compatibility_probe/current-kitava-29d39-omit-common-weapon-set.build`: exactly one field-policy change, omitting explicit weapon_set=0 on 104 common passives. All 151 passive IDs, their effective common/set1/set2 assignments, all 7 skills/supports, names, descriptions, ascendancy, inventory and remaining fields are unchanged. Original source bytes are unchanged. `compatibility_probe/validation.json` records hashes, exact 104 JSON paths and comparator field inventories. All 13 existing files omit explicit common weapon_set=0; the documented range still permits 0, so this is a client-compatibility hypothesis only. It cannot yet explain skill invisibility and is not a repair.

Do not mix a level_interval change into this comparison: existing normal poe.ninja file omits it on all skills, and all existing files omit it on passives. Keep the campaign-empty content issue separate by using latest151/7 for this experiment.

Manager alone may deploy one controlled test file. The internal build name is intentionally unchanged to isolate the variable: ensure the selected filename/path is identifiable, since adding a second same-name menu entry could confuse results. Prefer a manager-controlled reversible A/B replacement of the known latest filename with a byte-for-byte backup, only if that is the manager's chosen deployment method; this worker has not installed or overwritten anything. Record baseline and probe separately, confirm latest filename activation, and inspect tree guidance and appropriate gem-crafting recommendations independently. A failure leaves the hypothesis unproven; a success needs a repeat baseline/probe comparison before calling the field causal. Rollback is the preserved source file, not regeneration.

## Final two-probe revision — manager msg_53cd139178db

This revision supersedes the unchanged-name/single-probe proposal immediately above. Manager explicitly approved distinct menu names as identification metadata and two independent probes, with no deployment by this worker:

- A file `native_planner/compatibility_probe/current-kitava-29d39-omit-common-weapon-set.build`; exact menu name **탱정 표시확인 A 공통패시브**. Changes: name plus omission of 104 common weapon_set=0 fields. Skills and supports unchanged.
- B file `native_planner/compatibility_probe/current-kitava-29d39-explicit-skill-range.build`; exact menu name **탱정 표시확인 B 스킬**. Derived independently from original latest, not from A. Changes: name plus level_interval=[1,100] on the 7 skills and all their supports. Every passive and weapon_set is byte-value equivalent to original JSON. [1,100] is an experimental display range, not an acquisition or transition-level assertion.

Both retain all 151 passive IDs and 7 skills, all supports and all other metadata except explicitly authorized names. validation.json now records both exact diffs and hashes. There are exactly two probe .build files; no further probe created. The existing no-interval poe.ninja file is a structural comparator only: the user confirmed existing files work generally, but that individual comparator's actual display was not separately established. Thus its field omission is not a conclusive runtime counterexample. Manager owns copying/installing and asking for separate A/B tree and skill results; no fix or actual-display pass is claimed.
