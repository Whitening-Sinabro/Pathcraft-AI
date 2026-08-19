param(
    [string]$CurrentFilter = "D:\Pathcraft-AI\filters\Luminary_Bot_SSF_3.29_Progressive.filter",
    [string]$NeverSinkBase = "D:\Pathcraft-AI\_analysis\NeverSink_8.20.1d_1-Regular_Crimson.filter",
    [string]$OutputFilter = "D:\Pathcraft-AI\filters\Luminary_Bot_SSF_3.29_Progressive.filter"
)

$current = Get-Content -LiteralPath $CurrentFilter
$base = Get-Content -LiteralPath $NeverSinkBase

$startMatch = $current | Select-String -Pattern '^# PATHCRAFT: PATH OF CHORES 3\.29 LUMINARY BOT' | Select-Object -First 1
$endMatch = $current | Select-String -Pattern '^# END PATH OF CHORES LUMINARY BUILD-SPECIFIC TARGETS' | Select-Object -First 1

if (-not $startMatch -or -not $endMatch) {
    throw 'Could not locate the Luminary override markers.'
}

$start = [Math]::Max(0, $startMatch.LineNumber - 2)
$end = [Math]::Min($current.Count - 1, $endMatch.LineNumber)
$overrides = $current[$start..$end]

$header = @(
    '#===============================================================================================================',
    '# PATHCRAFT LUMINARY BOT SSF 3.29 - NEVERSINK CRIMSON PROGRESSIVE',
    '# Base logic and economy tiers: official NeverSink 8.20.1d, 1-Regular, Crimson style',
    '# SSF/build overrides: Path of Chores Luminary Bot guide',
    '# Output: one progressive filter; NeverSink leveling/map logic plus AreaLevel/StackSize SSF overrides',
    '# Important custom alerts are retained; common SSF crafting currency remains silent.',
    '#===============================================================================================================',
    ''
)

$result = @($header + $overrides + '' + $base)
$utf8NoBom = [System.Text.UTF8Encoding]::new($false)
[System.IO.File]::WriteAllLines($OutputFilter, $result, $utf8NoBom)
