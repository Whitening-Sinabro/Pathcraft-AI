param(
    [string]$LayeredTemplate = "C:\Users\User\Documents\My Games\Path of Exile\Vortican_Luminary_SSF_3.29.filter",
    [string]$CurrentLuminary = "D:\Pathcraft-AI\filters\Luminary_Bot_SSF_3.29_Progressive.filter",
    [string]$OutputFilter = "D:\Pathcraft-AI\filters\Luminary_Bot_SSF_3.29_Progressive.filter"
)

$template = Get-Content -LiteralPath $LayeredTemplate
$current = Get-Content -LiteralPath $CurrentLuminary

$templateStartMatch = $template | Select-String -Pattern '^# PATHCRAFT: VORTICAN 3\.29 LUMINARY' | Select-Object -First 1
$templateEndMatch = $template | Select-String -Pattern '^# END VORTICAN BUILD-SPECIFIC TARGETS' | Select-Object -First 1
$currentStartMatch = $current | Select-String -Pattern '^# PATHCRAFT: PATH OF CHORES 3\.29 LUMINARY BOT' | Select-Object -First 1
$currentEndMatch = $current | Select-String -Pattern '^# END PATH OF CHORES LUMINARY BUILD-SPECIFIC TARGETS' | Select-Object -First 1

if (-not $templateStartMatch -or -not $templateEndMatch -or -not $currentStartMatch -or -not $currentEndMatch) {
    throw 'Could not locate one or more build-layer markers.'
}

# Drop the old composed-file header and the Vortican-specific build block.
$templatePrefixEnd = $templateStartMatch.LineNumber - 3
$templateSuffixStart = $templateEndMatch.LineNumber + 1
$layeredPrefix = $template[8..$templatePrefixEnd]
$layeredSuffix = $template[$templateSuffixStart..($template.Count - 1)]

# Full-audit compatibility baseline. The NeverSink visual extraction has a
# generic known-equipment fallback, but its more specific leveling rules do not
# cover every Normal/Magic/Rare weapon and armour item that Wrecker SSF keeps.
# Insert rarity baselines immediately after that known-equipment fallback; later
# NeverSink Continue rules can still override these styles when they match.
$equipmentClasses = '"Amulets" "Belts" "Body Armours" "Boots" "Bows" "Claws" "Daggers" "Gloves" "Helmets" "One Hand Axes" "One Hand Maces" "One Hand Swords" "Quivers" "Rings" "Rune Daggers" "Sceptres" "Shields" "Staves" "Thrusting One Hand Swords" "Two Hand Axes" "Two Hand Maces" "Two Hand Swords" "Wands" "Warstaves"'
$auditBaseline = @(
    '',
    '#===============================================================================================================',
    '# PATHCRAFT FULL AUDIT BASELINE - ORDINARY EQUIPMENT RARITY COVERAGE',
    '# SSF may keep equipment that NeverSink leveling decorators do not match. These Continue rules prevent',
    '# ordinary weapons/armour from falling back to one indistinct grey style. Later specific rules still win.',
    '# Normal=white, Magic=desaturated blue, Rare=pale gold; all remain silent and icon-free.',
    '#===============================================================================================================',
    'Show # PATHCRAFT AUDIT - NORMAL EQUIPMENT FALLBACK',
    "`tClass == $equipmentClasses",
    "`tRarity Normal",
    "`tSetFontSize 34",
    "`tSetTextColor 235 235 235 255",
    "`tSetBorderColor 115 65 65 255",
    "`tSetBackgroundColor 18 10 11 225",
    "`tContinue",
    '',
    'Show # PATHCRAFT AUDIT - MAGIC EQUIPMENT FALLBACK',
    "`tClass == $equipmentClasses",
    "`tRarity Magic",
    "`tSetFontSize 35",
    "`tSetTextColor 175 195 225 255",
    "`tSetBorderColor 95 105 145 255",
    "`tSetBackgroundColor 18 16 27 225",
    "`tContinue",
    '',
    'Show # PATHCRAFT AUDIT - RARE EQUIPMENT FALLBACK',
    "`tClass == $equipmentClasses",
    "`tRarity Rare",
    "`tSetFontSize 36",
    "`tSetTextColor 255 220 155 255",
    "`tSetBorderColor 205 120 55 255",
    "`tSetBackgroundColor 48 20 5 230",
    "`tContinue",
    ''
)
$baselineAnchor = [Array]::IndexOf($layeredPrefix, 'Show # Pathcraft Death Oath visual rule 742')
if ($baselineAnchor -lt 0) {
    throw 'Could not locate the NeverSink known-equipment fallback anchor.'
}
$baselineInsertAfter = $baselineAnchor
while ($baselineInsertAfter -lt ($layeredPrefix.Count - 1) -and $layeredPrefix[$baselineInsertAfter] -notmatch '^\s*Continue\s*$') {
    $baselineInsertAfter++
}
$layeredPrefix = @(
    $layeredPrefix[0..$baselineInsertAfter] +
    $auditBaseline +
    $layeredPrefix[($baselineInsertAfter + 1)..($layeredPrefix.Count - 1)]
)

# Theme normalization is placed after the broad NeverSink layer and before the
# Allie high-value layer. It gives ordinary categories a coherent crimson family
# while allowing later high-value, build-required and link rules to remain more
# prominent. Category identity also uses minimap shape, not hue alone.
$categoryTheme = @(
    '',
    '#===============================================================================================================',
    '# PATHCRAFT FULL AUDIT - CRIMSON CATEGORY NORMALIZATION',
    '# Broad NeverSink rules classify value first. These generic Continue rules normalize ordinary category',
    '# presentation; the following Allie high-value layer and Luminary terminal rules can still override them.',
    '#===============================================================================================================',
    'Show # PATHCRAFT AUDIT - GENERIC UNIQUE',
    "`tRarity Unique",
    "`tSetFontSize 40",
    "`tSetTextColor 255 205 150 255",
    "`tSetBorderColor 190 70 35 255",
    "`tSetBackgroundColor 38 4 5 240",
    "`tMinimapIcon 2 Red Star",
    "`tContinue",
    '',
    'Show # PATHCRAFT AUDIT - GENERIC CURRENCY',
    '    Class "Currency"',
    "`tSetFontSize 38",
    "`tSetTextColor 255 210 195 255",
    "`tSetBorderColor 170 35 35 255",
    "`tSetBackgroundColor 35 2 4 240",
    "`tMinimapIcon 2 Red Cross",
    "`tContinue",
    '',
    'Show # PATHCRAFT AUDIT - GENERIC GEMS',
    '    Class "Gem"',
    "`tSetFontSize 36",
    "`tSetTextColor 245 190 185 255",
    "`tSetBorderColor 150 55 70 255",
    "`tSetBackgroundColor 30 3 8 235",
    "`tMinimapIcon 2 Red Triangle",
    "`tContinue",
    '',
    'Show # PATHCRAFT AUDIT - GENERIC DIVINATION CARDS',
    '    Class "Divination Cards"',
    "`tSetFontSize 38",
    "`tSetTextColor 235 180 190 255",
    "`tSetBorderColor 175 65 90 255",
    "`tSetBackgroundColor 38 4 12 240",
    "`tMinimapIcon 2 Red Square",
    "`tContinue",
    '',
    'Show # PATHCRAFT AUDIT - GENERIC MAPS',
    '    Class "Maps"',
    "`tSetFontSize 38",
    "`tSetTextColor 255 235 225 255",
    "`tSetBorderColor 195 70 55 255",
    "`tSetBackgroundColor 42 3 5 240",
    "`tMinimapIcon 2 Red Square",
    "`tContinue",
    '',
    'Show # PATHCRAFT AUDIT - GENERIC FRAGMENTS AND SCARABS',
    '    Class "Map Fragments" "Misc Map Items"',
    "`tSetFontSize 38",
    "`tSetTextColor 230 180 190 255",
    "`tSetBorderColor 140 55 75 255",
    "`tSetBackgroundColor 30 3 10 235",
    "`tMinimapIcon 2 Red Hexagon",
    "`tContinue",
    '',
    'Show # PATHCRAFT AUDIT - GENERIC FLASKS AND TINCTURES',
    '    Class "Life Flasks" "Mana Flasks" "Hybrid Flasks" "Utility Flasks" "Tinctures"',
    "`tSetFontSize 35",
    "`tSetTextColor 220 185 175 255",
    "`tSetBorderColor 125 65 55 255",
    "`tSetBackgroundColor 28 10 8 225",
    "`tMinimapIcon 2 Red Raindrop",
    "`tContinue",
    '',
    'Show # PATHCRAFT AUDIT - GENERIC GOLD',
    '    BaseType == "Gold"',
    "`tSetFontSize 38",
    "`tSetTextColor 245 200 125 255",
    "`tSetBorderColor 185 95 40 255",
    "`tSetBackgroundColor 45 14 3 235",
    "`tMinimapIcon 2 Red Cross",
    "`tContinue",
    ''
)
$allieAnchor = [Array]::IndexOf($layeredPrefix, '# ALLIE HIGH-PRIORITY VELVET ACCENT LAYER - DISPLAY/ALERT PRIORITY 6-9 ONLY')
if ($allieAnchor -lt 1) {
    throw 'Could not locate the Allie high-priority layer anchor.'
}
$categoryInsertAt = $allieAnchor - 1
$layeredPrefix = @(
    $layeredPrefix[0..($categoryInsertAt - 1)] +
    $categoryTheme +
    $layeredPrefix[$categoryInsertAt..($layeredPrefix.Count - 1)]
)

# Keep the current Luminary terminal overrides, including their surrounding separators.
$currentStart = $currentStartMatch.LineNumber - 2
$currentEnd = [Math]::Min($current.Count - 1, $currentEndMatch.LineNumber)
$luminaryOverrides = $current[$currentStart..$currentEnd]

$header = @(
    '#===============================================================================================================',
    '# PATHCRAFT LUMINARY BOT SSF 3.29 - LAYERED PROGRESSIVE FILTER',
    '# Visibility/progression base: C:\Users\User\Desktop\SSF.txt',
    '# Broad NeverSink visual layer: C:\Users\User\Desktop\death oath.txt',
    '# High-value NeverSink accent layer: C:\Users\User\Desktop\allie.txt',
    '# Build overrides: Path of Chores Luminary Bot SSF 3.29',
    '# Architecture: NeverSink visual Continue layers -> Luminary terminal overrides -> SSF visibility rules',
    '#===============================================================================================================',
    ''
)

$result = @($header + $layeredPrefix + $luminaryOverrides + $layeredSuffix)

# Alternate-quality gems were removed from modern POE1. The desktop SSF source still
# contains one legacy block, so omit that block from the generated filter without
# modifying the user's source file.
$legacyIndex = [Array]::IndexOf($result, 'AlternateQuality True')
if ($legacyIndex -ge 0) {
    $legacyStart = $legacyIndex
    while ($legacyStart -gt 0 -and $result[$legacyStart] -notmatch '^Show(?:\s+#.*)?$') {
        $legacyStart--
    }
    $legacyEnd = $legacyIndex
    while ($legacyEnd -lt ($result.Count - 1) -and $result[$legacyEnd] -notmatch '^\s*Continue\s*$') {
        $legacyEnd++
    }
    $result = @($result[0..($legacyStart - 1)] + $result[($legacyEnd + 1)..($result.Count - 1)])
}

$utf8NoBom = [System.Text.UTF8Encoding]::new($false)
[System.IO.File]::WriteAllLines($OutputFilter, $result, $utf8NoBom)
