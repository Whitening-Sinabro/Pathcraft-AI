# Luminary Bot SSF — Exiled Cat Crimson Progressive Filter

Date: 2026-08-18

## Decision

- Build logic: Path of Chores Luminary Bot SSF 3.29
- Output mode selected by user: one progressive filter
- Visual reference selected by user: Exiled Cat's 3.29 Death's Oath early video
- Video checked: [NEW AUTOBOMBER | From Zero to Hero | Part 1 | Path of Exile 3.29](https://www.youtube.com/watch?v=lVC3jV4SlWo)
- Video metadata: uploaded 2026-08-09, duration 16:31; description identifies Death's Oath Chieftain

The video did not publish a filter file. Its full storyboard and enlarged loot-heavy frames were inspected. The implemented palette is therefore an evidence-based visual derivative, not a claim that Exiled Cat's exact filter source was copied.

## Output and backups

- Canonical workspace output: `D:\Pathcraft-AI\filters\Luminary_Bot_SSF_3.29_Progressive.filter`
- Installed game copy: `C:\Users\User\Documents\My Games\Path of Exile\Luminary_Bot_SSF_3.29.filter`
- Download copy: `C:\Users\User\Downloads\Luminary_Bot_SSF_3.29.filter`
- Pre-change backup: `C:\Users\User\Downloads\Luminary_Bot_SSF_3.29.pre-exiledcat-crimson-progressive.filter`
- Pre-full-NeverSink-rebuild backup: `C:\Users\User\Downloads\Luminary_Bot_SSF_3.29.pre-full-neversink-rebuild.filter`
- Pre-layered-SSF-correction backup: `C:\Users\User\Downloads\Luminary_Bot_SSF_3.29.pre-layered-ssf-correction.filter`
- Pre-full-audit backup: `C:\Users\User\Downloads\Luminary_Bot_SSF_3.29.pre-full-audit.filter`
- Final SHA-256: `BBB52B29F1594EFBA70AF6690C9EF83AA642B82CB2C38A312FD6A4CB720AC6D4`

All three final copies matched this hash after installation.

## Continuation handoff

The authoritative defect history and follow-up validation procedure are recorded in `2026-08-18_LUMINARY_BOT_SSF_FULL_FILTER_AUDIT.md`. Future edits must be made in the regeneration path or the preserved Luminary override block, then propagated to all three output locations. Do not patch only the installed game copy.

Current quest and Chart policy is also embedded as comments beside the executable filter blocks: quest items use their dedicated sound, a temporary green beam and a green circle; Allflame Charts are silent and iconless with a blue beam.

## Palette and visual grammar

- Primary main colour: deep crimson around `#970707`
- Common backgrounds: black-red values such as `18 10 11`, `35 2 4`, `42 3 5`, `58 4 7`
- Important borders: muted crimson/coral such as `200 75 55`, `215 65 50`, `245 125 95`
- Restricted secondary accents: muted copper for selected equipment and dusty rose for cards/fragments
- Fixed semantic exceptions: white/red required uniques and six-links, dark-green quest items with a temporary green beam and green circle, acid-green Dead Man's Sulphur, subdued blue Portal Scrolls, silent/iconless deep-sea Charts with a blue beam

NeverSink-style value tiers are separated from the generic category colours:

- Build-required unique bases: white text and border on a deep-crimson background, preserving the user's requested grammar
- Global T0 unique bases and currency: deep-crimson text/border on a warm-white background, strongest custom alert, permanent red beam, size-0 red star/circle
- Global high-value tier: white text and pale warm border on a deep-crimson background, strong custom alert and red beam
- Lists were refreshed from the official NeverSink `8.20.1d` Regular filter on 2026-08-18 and placed before generic unique/currency decorators

Links are not distinguished by hue alone:

- 3-link: font 36, muted rust border, dark neutral-red background, temporary grey effect, icon size 2
- 4-link: font 40, stronger rust border, black-crimson background, grey effect, icon size 2
- 5-link: font 45, pale coral border, deeper crimson background, `5Link.mp3`, yellow effect, icon size 1
- 6-link: font 45, white text/border, red background, `6Link.mp3`, permanent red effect, icon size 0
- Normal/Magic/Rare link text remains white/desaturated blue/pale gold for immediate rarity recognition

## Progressive behaviour

The final architecture preserves `C:\Users\User\Desktop\SSF.txt` as the visibility and progression authority. NeverSink-derived rules from `death oath.txt` and `allie.txt` are converted to visual `Continue` layers, so they classify and decorate drops without replacing the SSF Show/Hide policy. Luminary build requirements and current top economy targets are terminal priority overrides between those visual layers and the SSF rules.

Additional single-filter SSF progression is applied above the NeverSink base:

- Wisdom and Portal Scrolls are large and voiced during campaign.
- In maps, stacks of 5+ retain a quieter voice; single scrolls become smaller and silent.
- Basic SSF crafting currency is large and receives a temporary beam during campaign, but remains silent to avoid constant voice spam.
- In maps, stacks of 5+ remain visually emphasized but silent; useful single crafting currency stays visible and silent; low-value single currency becomes smaller and silent.
- Campaign 3-link/4-link rules naturally expire by AreaLevel; 5-link/6-link safety remains global.

## Category decorators

Generic uniques, currency, gems, divination cards, maps, fragments, flasks and gold now receive a coherent crimson-family treatment. Category recognition also uses fixed minimap shapes:

- Unique: Star
- Currency: Circle/Cross
- Gem: Triangle
- Divination card/map: Square
- Fragment/scarab: Hexagon
- Flask/tincture: Raindrop
- Link/crafting base: Diamond

## Validation

- Full audit: [`2026-08-18_LUMINARY_BOT_SSF_FULL_FILTER_AUDIT.md`](2026-08-18_LUMINARY_BOT_SSF_FULL_FILTER_AUDIT.md)
- Final structure: 11,769 lines; Show 1,161; Hide 87; Continue 1,198
- The 87 Wrecker SSF Hide rules are preserved; NeverSink-derived decorators do not become terminal visibility rules
- Full-audit rules embedded in the `.filter`: 11 (3 ordinary-equipment rarity fallbacks + 8 category normalization rules)
- Custom sound calls: 21; 12 unique MP3 filenames; 131 minimap rules; 100 beam rules
- The obsolete `AlternateQuality` block present in the desktop SSF source is omitted only during generation; the source file remains untouched
- All 12 referenced MP3 files exist in the game filter directory
- No terminal block combines a built-in alert and a custom alert
- Quote, RGB/RGBA range and font-size lint: no errors
- No new unknown directive token was introduced relative to the previously loaded filter
- Workspace, installed and download copies have matching SHA-256
- `production_Config.ini` selects `Luminary_Bot_SSF_3.29.filter` and records that filename as previously loaded successfully
- Path of Exile was running during the final audited installation. The filename remains selected, but this exact revision still requires an in-game reload before live syntax success can be claimed.

## Reload instruction

On the next game launch, the same selected filename should be loaded automatically. If the game was already open elsewhere, use Options > Game > Item Filter and reload/select `Luminary_Bot_SSF_3.29.filter` once.
