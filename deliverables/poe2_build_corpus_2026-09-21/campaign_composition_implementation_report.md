# Campaign composition and observed display compatibility

Task `task_5e351886d302`, dispatch `ctx_3310e7b8d930`, 2026-09-21.

Delivered the accepted five Pathcraft campaign compositions and the user-confirmed B/A2 display representation in the shared pack and ten native builds. These are source-attributed Pathcraft choices, not restored Tangjung act snapshots. No new-campaign real-game, DPS, or HC PASS is claimed.

## Evidence and output

- Approval: HQ `msg_61c2d37901fa`; exact accepted candidate SHA-256 `98cdec142151594fa358e448149a449202041e2d0be854045e3939ef9803d241` is pinned by the pack builder.
- Campaign ordinary common points: **18/26/37/47/56**, excluding free Warrior start 47175. All nodes are common (`weapon_set: 0`), no foreign ascendancy, no borrowed weapon-set points. Numbers are point gates, never levels or assumed quest rewards.
- Act 1 equipment is explicitly two-handed mace; later equipment is one-handed mace plus armour shield. Act 1→2 refunds five nodes and adds thirteen. The exact validated thirteen-point common bridge and connected addition/refund witnesses remain in `stage.campaign_checkpoint`; insufficient points retain the previous checkpoint and compatible weapon setup.
- Actual gem/support/attribute/spirit requirements and refund affordability remain conditional. Effect caveats and attribute choices are retained. Source Spec provenance, numeric/string IDs, original stats, real coordinates, and real edges are preserved; the pack graph has 522 nodes and 578 edges including neighbors.
- Latest remains **151 = 104 common / 24 set 1 / 23 set 2**. Four historical snapshots retain counts 124/125/126/127 and their original data IDs, inventory, source annotations, and sets. Display intervals and their explanatory description are the only snapshot changes.
- All ten native builds explicitly set `[1,100]` on skills, supports, and passives. B skill display was relayed in `msg_db4b49567e07`; unchanged original act3 also displayed five recommendations (HQ `msg_ccc4f724cad0`, relay `msg_ba97abe53f22`), so omission is not asserted as the general root cause. Passive ranges were enabled only after user-confirmed A2 display (HQ `msg_0f2e79de7708`, manager `msg_ae87d801be97`), keeping explicit original `weapon_set: 0/1/2`. These ranges are display conventions, not acquisition, allocation, or readiness levels.
- Final shared JSON SHA-256: `c213cbb79994c6a418d5cfa851a5c32e3bc1aae3170d0dd389c3fcb2b4804a53`. Final data-ready notification: `msg_4ddc139832e8`; HTML owner can consume the stable pack.

## Shared contract

`stage.campaign_checkpoint` contains the accepted candidate fields, including `classification`, `point_budget`, `weapon_condition`, `skill_condition`, `transition_from_previous` (exact safe refund/add IDs and counts), and `allocation_witness_not_author_click_order`, plus `shield_bridge`, `insufficient_points_policy`, and approval. `stage.conditions` supplies Korean point/gear/refund/fallback guidance. `stage.passives` contains real source node records with composition provenance and display intervals; `weapon_set_nodes` remains empty for both sets because all campaign nodes are common.

`pack.campaign_composition` preserves source hashes, free start, policy, bridge, effect review, assumptions, limits, and candidate approval/hash. `pack.display_compatibility` separates observed B/A2 display evidence from acquisition and gameplay claims.

## Verification

`python build_planner_data.py` and `python native_planner/generate.py` passed once for the initial composition and B ranges. New manager evidence then authorized A2 passive ranges, requiring one affected pack/native regeneration and validation; both passed again. No unrelated repeat test run or new probe was performed.

The final generator checks all five source graph compositions, source membership and hashes, exact native candidate ID order, no foreign ascendancy or later two-hand conflict, connectivity for both effective weapon sets, every refund/add intermediate state, five refunds/thirteen additions, and the thirteen-point bridge. It checks all ten native JSON shapes, allowed keys and types, BaseItemTypes/SkillGems IDs, JSON round trips, original source hashes, all five shared-pack snapshot mappings, and latest 151/104/24/23. Detailed durable results are in `native_planner/validation.json`.

The historical `native_planner/ux_structure_baseline.json` remains byte-for-byte unchanged: SHA-256 `4dc3340a00ac54f01848fac01b447096eba4c3f5a4dd67cae57f20e19f7fb48e`. Its old equality assertion was replaced by explicit allowed differences: exact `[1,100]` skill/support/passive intervals and exactly accepted campaign common nodes. After removing only those allowed additions, all ten structures must equal the historical baseline. Latest/historical builds are additionally compared with full prechange files, allowing only intervals and the exact display-note suffix; their other data and annotations must be identical. The baseline is required, never overwritten, and validation remains active.

## Files delivered

Changed current files relative to this corpus root:

- `build_planner_data.py`
- `planner_data/build_data.json`, `planner_data/build_data.js`, `planner_data/validation.json`
- `native_planner/generate.py`, `native_planner/validation.json`, `native_planner/README_ko.md`, `native_planner/report.md`
- `native_planner/campaign-act1.build`, `native_planner/campaign-act2.build`, `native_planner/campaign-act3.build`, `native_planner/campaign-act4.build`, `native_planner/campaign-interlude.build`
- `native_planner/current-kitava-29d39.build`, `native_planner/archive-28509.build`, `native_planner/archive-285e2.build`, `native_planner/archive-28604.build`, `native_planner/archive-28695.build`
- This implementation report.

Before generation, local `native_planner/versions/pre_campaign_composition_20260921/` preserved all ten prechange native builds, `generate.py`, `ux_structure_baseline.json`, `README_ko.md`, `report.md`, the pack builder, shared JSON/JS, and shared-pack `validation.json` (the flat snapshot's validation file is the pack validation, not the old native validation). This snapshot is recovery evidence, not a new delivery set or game-install folder.

No edits to manager-owned `compatibility_probe/`, HTML-owned `planner/`, source candidates/verifier, canonical D:, game-installed files, or ZIP. Existing corpus-wide installation/review receipts were not rewritten as evidence of this worker's actions.

## Remaining verification

HTML adaptation, review/deployment, and any packaging belong to the coordinator and other owner. Real-game rendering of these newly composed campaigns, skill/gear/attribute/spirit eligibility, actual available points and refund costs, damage effectiveness, HC survivability, and the campaign-to-endgame respec remain unverified. A2 display confirmation does not substitute for those checks; no further user decision is needed for this completed implementation scope.
