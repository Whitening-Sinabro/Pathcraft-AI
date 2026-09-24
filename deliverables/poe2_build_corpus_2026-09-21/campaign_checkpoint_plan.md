> 후속 상태: 이 문서는 당시 진단/검토 근거를 보존합니다. 이후 A2 패시브 표시 사용자 확인과 Pathcraft 캠페인 구현·설치를 완료했습니다. 현재 결과는 [campaign_delivery_receipt.json](campaign_delivery_receipt.json) 및 [구현 보고서](campaign_composition_implementation_report.md)를 따릅니다. 신규 캠페인의 실게임 화면 검증은 본부가 별도로 진행합니다.

# Pathcraft campaign checkpoint composition — review candidate

Task task_1cf1e68c4497 / Dispatch ctx_856e8b405bae

**Delivered:** five exact general-node candidates with reproducible graph, budget and transition verification. These are Pathcraft compositions from saved sources, not restored Tangjung-authored act snapshots. No final native file, generator, HTML, canonical output, installed file or ZIP changed.

## Evidence and chosen assumptions

- Saved `linked_update_pob.xml` Specs 1, 2, Swap, 3, 4 and Interlude provide the node pool; their titles are provenance labels, never an act mapping. The saved tree supplies names, exact effects and connection edges. Each selected ID records every source Spec containing it. No new remote source was used.
- Warrior start is numeric 47175 / stringId marauder594; the tree explicitly lists Warrior in classesStart despite the MARAUDER display name. It anchors connectivity and costs zero; it is excluded from candidate spendable/export ID lists.
- Act placement, target priority and budgets are Pathcraft choices. Budgets 18/26/37/47/56 mean actual ordinary points available for that tree, not character levels, act rewards or guaranteed points on entering an act. No quest reward count is invented.
- Every selected node is common to both weapon sets. Each active tree costs the listed budget, extra weapon-set allocation is zero, and ascendancy allocation is zero. Thus the plan does not borrow restricted weapon-set points to fund common nodes. Manual skill set1/set2 preferences can coexist with this deliberately unspecialized tree.
- Saved video anchors: act1 melee/stun sequence at 01:07, two-hand discussion at 09:58, Shield Wall transition at 22:41–22:45, act3 set1 wall/set2 cry at 28:27–28:34. These anchor skill/weapon intent only, not exact passive IDs. The author’s Warbringer effects are not included.

## Checkpoints and transition costs

| Candidate | Ordinary common points | Extra set1 / set2 | Adds from previous | Refunds from previous | Role |
|---|---:|---|---:|---:|---|
| Act 1 late two-handed mace checkpoint | 18 | 0 / 0 | 18 | 0 | Brutal, Smash, Singular Purpose |
| Act 2 shield transition checkpoint | 26 | 0 / 0 | 13 | 5 | Brutal, Smash, Beef, Relentless, Crushing Verdict |
| Act 3 shield sustain checkpoint | 37 | 0 / 0 | 11 | 0 | Brutal, Smash, Beef, Relentless, Crushing Verdict, Unyielding |
| Act 4 mobility and cry recovery checkpoint | 47 | 0 / 0 | 10 | 0 | Brutal, Smash, Beef, Relentless, Crushing Verdict, Unyielding, Momentum, Admonisher |
| Interlude mobility checkpoint | 56 | 0 / 0 | 9 | 0 | Brutal, Smash, Beef, Relentless, Crushing Verdict, Unyielding, Momentum, Admonisher, Light on your Feet, Adrenaline Rush |

Points insufficient: keep the previous checkpoint **and its compatible weapon setup**; do not force the next tree because an act began. The validated 13-point common bridge supports an earlier shield swap after the five two-handed refunds, with connected prefixes of the Act 2 addition witness as points become available. This fallback is not a sixth act stage or a promise of sufficient damage/attributes. Check actual refund currency before committing; costs are not guessed.

Act 1 requires an actual two-handed mace and usable melee/stun skills. Act 2 onward requires an armour shield and one-handed mace plus usable Shield Wall; use available Shockwave Totem/Shield Charge and ordinary Infernal Cry cooldowns, not assumed Warbringer corpse explosion/cooldown-ignore. Actual gem level, attributes and spirit remain gear-dependent gates. Sturdy Metal specifically needs armour on body armour; it does not increase the shield armour stat.

## Effect review

| Notable | Applicability and limit |
|---|---|
| Brutal | Melee damage and stun buildup support the early mace hit/stun plan; no claim that every Shield Wall damage component is melee. Strength is a fixed stat. |
| Smash | Melee damage supports mace melee hits; the larger bonus requires the enemy to be Heavy Stunned. Shield Wall component scaling remains unverified. |
| Singular Purpose | Only the two-handed mace checkpoint; reduced attack speed is a real downside. Refund before one-handed mace plus shield. |
| Beef | Fixed Strength supports requirements only after actual equipment/gem comparison; does not certify sufficient attributes. |
| Relentless | Armour and life regeneration are generic defensive effects, independent of Warbringer. No survivability guarantee. |
| Sturdy Metal | Increases armour from body armour, not armour from the shield. Requires actual body armour with armour; never label as direct shield damage scaling. |
| Crushing Verdict | Generic attack damage and stun buildup target attack hits; reduced attack speed is a downside. Does not establish wall detonation/minion damage scaling or cry damage. |
| Unyielding | Attack speed is conditional on having been hit recently; slow mitigation is separate. No permanent attack-speed or warcry-speed assumption. |
| Momentum | Armour movement penalties and slowing debuffs only; not damage, not all movement penalties. |
| Admonisher | Warcry speed and cooldown recovery support Infernal Cry subject to real cooldown. Does not grant Warbringer cooldown-ignore or corpse explosion. |
| Light on your Feet | Movement speed plus Hinder/Maim immunity; not general immunity to every slow. |
| Adrenaline Rush | Attack/movement bonuses require a recent kill; not reliable on an isolated boss. |

The retained early melee path is source-supported access and helps melee attacks such as Mace Strike; this work does not prove every melee/stun modifier scales Shield Wall wall damage. These candidates are conservative connected structures, not damage-optimized builds. Small-node effects are copied verbatim in JSON so a manager can audit traversal costs and ineffective modifiers.

Excluded deliberately: every foreign ascendancy node; all two-hand-specific effects after act1; armour-break/fully-broken-armour investment without an established independent armour-break source; Blood Rush life-cost conversion; Gem Enthusiast support-colour thresholds; burning-enemy branch including Burning Strikes because burning uptime was not established. The latter removal reduces preliminary 40/50/59 estimates to 37/47/56. No latest-endgame intersection was used.

Empty jewel sockets are paid travel points where the source graph requires them; no jewel item, radius effect or extra socket power is assumed. This is a known efficiency cost of restricting candidates to saved-source paths, not a hidden equipment requirement. Each +5 to any Attribute node remains a choice: the stringId name does not force Strength. Actual gem/weapon requirements, attribute allocation and their transition effects are not validated by graph connectivity.

## Exact changes and graph witnesses

`campaign_checkpoint_candidates.json` contains exact numeric/string IDs, original stats, Spec provenance, source hashes, source edges, root-to-target paths, connected addition witnesses, safe refund witnesses, budget accounting and the fallback bridge. Witness order is an algorithmically valid Pathcraft order, never claimed as streamer click order.

### act1

Refund in validated order: `[]`.
Add in validated order: `[3936, 46325, 33556, 55473, 43164, 5710, 58528, 45363, 19011, 64284, 27373, 16725, 54811, 34210, 64939, 30123, 26092, 52392]`.

### act2

Refund in validated order: `[52392, 26092, 30123, 64939, 34210]`.
Add in validated order: `[57703, 54485, 25482, 6529, 32416, 27726, 7721, 26725, 63114, 18073, 36027, 45090, 18505]`.

### act3

Refund in validated order: `[]`.
Add in validated order: `[22975, 27439, 8600, 61490, 38876, 31903, 37258, 26568, 51732, 35863, 10774]`.

### act4

Refund in validated order: `[]`.
Add in validated order: `[37612, 13279, 2864, 32564, 39207, 33518, 63579, 38130, 53194, 35876]`.

### interlude

Refund in validated order: `[]`.
Add in validated order: `[37519, 17045, 55131, 54818, 15182, 54127, 21755, 62051, 17340]`.

## Verification and implementation boundary

`python verify_campaign_checkpoints.py` regenerates only campaign_checkpoint_candidates.json. It passed assertions for all five budget totals, source membership, foreign-ascendancy exclusion, shield/two-hand exclusion, root connectivity, every addition and refund intermediate state, both effective weapon-set trees, and the 13-point bridge. All paths use saved-tree edges; source files are read only.

Manager review should decide whether these conservative target priorities and their travel costs suit the product, verify current gem/gear attribute gates, and approve a final common-node serialization in a later implementation dispatch. User scope already authorizes this composition; no additional user permission is required for ordinary review/implementation. Kitava ascendancy choices, live point/reward availability, damage optimization, final endgame respec and actual game display remain separate unresolved checks.

A/B display probes are manager-owned: coordinator msg_4b12af7e0018 reports user-observed skills visible in B, while original A did not restore passives; a manager-owned revised A passive-range comparison remains pending. This worker has not independently observed that UI. Filling campaign nodes cannot be declared a fix for the current all-Tangjung display complaint.
