# Thyworm SRS Guardian SSF Filter — Luminary Palette Handoff

Date: 2026-08-12

## User inputs

- PoB: https://pobb.in/aqWq4xty5YI6
- Source filter: `C:\Users\User\Desktop\thyworm.txt`
- Requested direction: customize the filter for the Thyworm SRS Guardian SSF build and use the Luminary visual palette.

## Current outputs

- Workspace filter: `D:\Pathcraft-AI\thyworm_srs_guardian_ssf.filter`
- Installed copy: `C:\Users\User\Documents\My Games\Path of Exile\Thyworm_SRS_Guardian_SSF.filter`
- Source `thyworm.txt` was not modified.
- The workspace and installed copies matched at the last completed verification.
- SHA-256 before the Luminary recolour: `83993827A3D724CAD8CE05D616DEB08DC8C6A805830B114B35E65C975273DBD7`
- SHA-256 after the Luminary recolour: `1C86E862EA03F6AE4DA05B98FE78B99522B739CF273D18A88B97AF70B8ED2B70`

## Work already completed

The source NeverSink 8.20.0b semi-strict filter was copied and given 12 high-priority build rules covering:

- SRS socket progression: `BBR`, `BBRR` / `BBBR`, `BBBRR`, `BBBRRR`
- Forest Warrior and target Perfect Ritual spectre corpses
- target unique bases for Darkness Enthroned, Profane Proxy, and Rumi's Concoction
- Ghastly Eye Jewels
- Essences of Fear
- Calling, Convening, and Convoking Wands
- Bone, Ivory, and Fossilised Spirit Shields
- PoB hybrid armour/energy-shield bases
- SSF jewellery bases

The custom section is inserted immediately above NeverSink waypoint `c0.alpha`. Its structure, allowed directives, balanced quotes, rule count, and installed-copy hash were checked successfully.

## Luminary recolour completed

The Thyworm custom override section now uses the confirmed Allie Velvet / Vortican Luminary colour tuples. The SRS socket-colour requirements and Thyworm build targets were preserved.

The recolour also added mirrored/corrupted/ordinary six-link exceptions, split Essence of Fear by tier, split Ghastly Eye Jewels by item level and rarity, and separated high-level crafting bases from quieter transitional bases.

## Full-palette correction — 2026-08-13

The first recolour changed only the Thyworm override section, so ordinary drops still used the old NeverSink palette and could look unchanged in game. The filter was subsequently rebuilt on the complete Vortican Luminary composed base:

- Base visibility: SSF
- Broad/default colours: Death's Oath visual layer
- High-value accents: Allie 3.29 Velvet
- Build-specific targets: Thyworm SRS Guardian SSF only

All Vortican build-target rules were removed and the 24 Thyworm rules were retained. The workspace and installed copies now have SHA-256 `ECCDD98BA290B924FA0D38A3A036B129D9BA9B25B4CDAF8EE806846FEA58F478`.

PoE was already running when the full-palette file was installed. The game must reload the selected filter once to replace the in-memory copy.

## Luminary reference sources

- Installed reference filter: `C:\Users\User\Documents\My Games\Path of Exile\Vortican_Luminary_SSF_3.29.filter`
- Original Allie Velvet source: `C:\Users\User\Desktop\allie.txt`
- Relevant reference section in the installed filter begins near:
  `# PATHCRAFT: VORTICAN 3.29 LUMINARY - BUILD-SPECIFIC SSF TARGETS`
- That section identifies its visual source as `Allie 3.29 Velvet 8.20.1c`.

## Confirmed Luminary style tuples

Use these exact treatments as the starting mapping:

### Ordinary six-link / strongest generic build link

- Text: `255 255 255 255`
- Border: `255 255 255 255`
- Background: `128 90 179 172`
- Sound: `PlayAlertSound 1 300`
- Beam: `PlayEffect Pink`
- Icon: `MinimapIcon 0 Pink Star`

Corrupted or mirrored six-links use background `175 37 37 171` with the same white text/border, Pink beam, and Pink Star.

### Target unique T2

- Text: `255 255 255 255`
- Border: `255 255 255 255`
- Background: `234 87 223 172`
- Sound: `PlayAlertSound 1 300`
- Beam: `PlayEffect Red`
- Icon: `MinimapIcon 0 Yellow Star`

### Deafening target essence

- Text: `234 87 223 255`
- Border: `234 87 223 255`
- Background: `255 255 255 255`
- Strong alert and `MinimapIcon 0 Pink Star`

The Luminary reference uses `PlayAlertSound ShGeneral 300`, but the Thyworm source may not ship the matching custom sound. Prefer a safe built-in sound unless the sound asset is confirmed.

### Screaming/Shrieking target essence

- Text: `0 0 0 255`
- Border: `0 0 0 255`
- Background: `200 101 242 255`
- Sound: `PlayAlertSound 2 300`
- Beam: `PlayEffect White`
- Icon: `MinimapIcon 2 White Circle`

### High crafting base

- Text: `0 240 190 255`
- Border: `0 240 190 255`
- Background: `0 75 30 162`
- Sound: `PlayAlertSound 3 300`
- Beam: `PlayEffect Blue`
- Icon: `MinimapIcon 0 Blue Diamond`

This treatment is appropriate for high-level minion wands, spirit shields, jewellery, and selected armour bases. Quieter transitional variants use the same colours without sound/beam/icon.

### Rare and magic Ghastly Eye Jewels

Rare, item level 84+:

- Text/border: `220 220 0 255`
- Background: `120 120 0 175`

Magic, item level 84+:

- Text/border: `0 75 250 255`
- Background: `0 20 40 179`

Create lower-level/transitional jewel rules only if useful for SSF progression; avoid turning every low-level jewel into a top alert.

### Campaign links

Allie Velvet campaign four-link:

- Border: `255 255 255 255`
- Background: rare/magic `250 212 168 255`; normal/magic reference `227 154 67 255`
- Beam: `PlayEffect Yellow`
- Icon: `MinimapIcon 2 Yellow Diamond`

Campaign three-link:

- Border: `255 255 255 255`
- Background: `182 124 54 255`
- Early beam: `PlayEffect Blue Temp`; later reference uses `PlayEffect Green Temp`

Preserve the Thyworm-specific socket-colour conditions while adopting these visuals.

## Completed recolour checks

1. Only the custom Thyworm override section was recoloured; the NeverSink base filter was not rewritten.
2. Essence of Fear was split into Deafening, Screaming/Shrieking, and lower-tier treatments.
3. Crafting bases were split into high-value endgame and quiet transitional rules.
4. Target Ritual corpses now use the Luminary unique/T2 velvet accent.
5. Mirrored, corrupted, and ordinary six-link exception rules precede socket-colour SRS links.
6. The custom section has 24 `Show` rules, balanced quotes, recognized directives, and a valid condition/style structure.
7. The workspace and installed copies have matching SHA-256 hashes.
8. PoE selected `Thyworm_SRS_Guardian_SSF.filter` and recorded it in `item_filter_loaded_successfully`, confirming a successful live load.

## Current game state note

At the final inspection, `production_Config.ini` showed:

- `item_filter=Thyworm_SRS_Guardian_SSF.filter`
- `item_filter_loaded_successfully=Thyworm_SRS_Guardian_SSF.filter`

Therefore the recoloured Thyworm filter was selected and loaded successfully in game.
