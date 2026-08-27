param(
    [string]$Spec = (Join-Path (Split-Path -Parent $PSScriptRoot) 'config\build_setups\magefist_chaos_hot_pathfinder_3_29.spec.json'),
    [string]$Output
)

$ErrorActionPreference = 'Stop'

function ConvertFrom-PobCode([string]$Code) {
    $base64 = $Code.Trim().Replace('-', '+').Replace('_', '/')
    $base64 = $base64.PadRight([Math]::Ceiling($base64.Length / 4) * 4, '=')
    $input = [IO.MemoryStream]::new([Convert]::FromBase64String($base64))
    $zlib = [IO.Compression.ZLibStream]::new($input, [IO.Compression.CompressionMode]::Decompress)
    $reader = [IO.StreamReader]::new($zlib, [Text.Encoding]::UTF8)
    try { return [xml]$reader.ReadToEnd() }
    finally { $reader.Dispose(); $zlib.Dispose(); $input.Dispose() }
}

function Get-PobXml([string]$RawUrl) {
    $response = Invoke-WebRequest -UseBasicParsing -Uri $RawUrl -TimeoutSec 30
    $code = if ($response.Content -is [byte[]]) {
        [Text.Encoding]::UTF8.GetString($response.Content)
    } else {
        [string]$response.Content
    }
    if (-not $code.Trim().StartsWith('eJ')) { throw "Invalid PoB response: $RawUrl" }
    return @{
        Code = $code.Trim()
        Xml = ConvertFrom-PobCode $code
    }
}

function Get-ActiveChild([Xml.XmlElement]$Container, [string]$ChildName, [string]$ActiveAttribute) {
    $nodes = @($Container.SelectNodes("./$ChildName"))
    if (-not $nodes.Count) { return $null }
    $active = $Container.GetAttribute($ActiveAttribute)
    if ($active) {
        $byId = $Container.SelectSingleNode("./$ChildName[@id='$active']")
        if ($byId) { return $byId }
        $position = 0
        if ([int]::TryParse($active, [ref]$position) -and $position -ge 1 -and $position -le $nodes.Count) {
            return $nodes[$position - 1]
        }
    }
    return $nodes[0]
}

function Set-MainSkillGroup([Xml.XmlElement]$SkillSet, [string]$GemName, [int]$TargetPosition) {
    $main = $null
    foreach ($skill in @($SkillSet.SelectNodes('./Skill'))) {
        if ($skill.SelectSingleNode("./Gem[@nameSpec='$GemName']")) {
            $main = $skill
            break
        }
    }
    if (-not $main) { throw "Main skill group not found: $GemName" }
    $SkillSet.RemoveChild($main) | Out-Null
    $remaining = @($SkillSet.SelectNodes('./Skill'))
    if ($TargetPosition -le $remaining.Count) {
        $SkillSet.InsertBefore($main, $remaining[$TargetPosition - 1]) | Out-Null
    } else {
        $SkillSet.AppendChild($main) | Out-Null
    }
}

function Save-Xml([xml]$Document, [string]$Path) {
    [IO.Directory]::CreateDirectory([IO.Path]::GetDirectoryName($Path)) | Out-Null
    $settings = [Xml.XmlWriterSettings]::new()
    $settings.Encoding = [Text.UTF8Encoding]::new($false)
    $settings.Indent = $true
    $settings.NewLineChars = "`r`n"
    $writer = [Xml.XmlWriter]::Create($Path, $settings)
    try { $Document.Save($writer) } finally { $writer.Dispose() }
}

if (-not (Test-Path -LiteralPath $Spec)) { throw "Missing canonical spec: $Spec" }
$definition = Get-Content -LiteralPath $Spec -Raw -Encoding UTF8 | ConvertFrom-Json -Depth 100
if (-not $Output) { $Output = $definition.outputs.pob }

$sources = @{}
$sourceHashes = @{}
foreach ($stage in @($definition.sources.pob_stages)) {
    $result = Get-PobXml $stage.raw_url
    $sources[$stage.id] = $result.Xml
    $bytes = [Text.Encoding]::UTF8.GetBytes($result.Code)
    $sourceHashes[$stage.id] = [Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($bytes))
}

$finalStage = @($definition.sources.pob_stages)[-1]
[xml]$xml = $sources[$finalStage.id].OuterXml
$tree = $xml.SelectSingleNode('/PathOfBuilding/Tree')
$skills = $xml.SelectSingleNode('/PathOfBuilding/Skills')
$items = $xml.SelectSingleNode('/PathOfBuilding/Items')
$config = $xml.SelectSingleNode('/PathOfBuilding/Config')
foreach ($pair in @(
    @{ Container = $tree; XPath = 'Spec' },
    @{ Container = $skills; XPath = 'SkillSet' },
    @{ Container = $items; XPath = 'Item | ItemSet' },
    @{ Container = $config; XPath = 'ConfigSet' }
)) {
    foreach ($node in @($pair.Container.SelectNodes($pair.XPath))) {
        $pair.Container.RemoveChild($node) | Out-Null
    }
}

$nextItemId = 1
$stageIndex = 1
foreach ($stage in @($definition.sources.pob_stages)) {
    [xml]$source = $sources[$stage.id]
    $sourceTree = $source.SelectSingleNode('/PathOfBuilding/Tree')
    $sourceSkills = $source.SelectSingleNode('/PathOfBuilding/Skills')
    $sourceItems = $source.SelectSingleNode('/PathOfBuilding/Items')
    $sourceConfig = $source.SelectSingleNode('/PathOfBuilding/Config')
    $sourceSpec = Get-ActiveChild $sourceTree 'Spec' 'activeSpec'
    $sourceSkillSet = Get-ActiveChild $sourceSkills 'SkillSet' 'activeSkillSet'
    $sourceItemSet = Get-ActiveChild $sourceItems 'ItemSet' 'activeItemSet'
    $sourceConfigSet = Get-ActiveChild $sourceConfig 'ConfigSet' 'activeConfigSet'
    if (-not $sourceSpec -or -not $sourceSkillSet -or -not $sourceItemSet -or -not $sourceConfigSet) {
        throw "Incomplete source PoB: $($stage.id)"
    }

    $referencedIds = [Collections.Generic.HashSet[string]]::new()
    foreach ($node in @($sourceItemSet.SelectNodes('.//*[@itemId]')) + @($sourceSpec.SelectNodes('.//*[@itemId]'))) {
        $itemId = $node.GetAttribute('itemId')
        if ($itemId -and $itemId -ne '0') { $referencedIds.Add($itemId) | Out-Null }
    }

    $idMap = @{}
    foreach ($oldId in $referencedIds) {
        $sourceItem = $sourceItems.SelectSingleNode("./Item[@id='$oldId']")
        if (-not $sourceItem) { throw "Missing referenced item $oldId in $($stage.id)" }
        $newId = [string]$nextItemId++
        $idMap[$oldId] = $newId
        $clone = $xml.ImportNode($sourceItem, $true)
        $clone.SetAttribute('id', $newId)
        $items.AppendChild($clone) | Out-Null
    }

    $itemSetClone = $xml.ImportNode($sourceItemSet, $true)
    $itemSetClone.SetAttribute('id', [string]$stageIndex)
    $itemSetClone.SetAttribute('title', "$($stage.title) - Items")
    foreach ($node in @($itemSetClone.SelectNodes('.//*[@itemId]'))) {
        $oldId = $node.GetAttribute('itemId')
        if ($idMap.ContainsKey($oldId)) { $node.SetAttribute('itemId', $idMap[$oldId]) }
    }
    $items.AppendChild($itemSetClone) | Out-Null

    $skillSetClone = $xml.ImportNode($sourceSkillSet, $true)
    $skillSetClone.SetAttribute('id', [string]$stageIndex)
    $skillSetClone.SetAttribute('title', "$($stage.title) - Gems")
    Set-MainSkillGroup $skillSetClone $definition.identity.main_skill 7
    $skills.AppendChild($skillSetClone) | Out-Null

    $specClone = $xml.ImportNode($sourceSpec, $true)
    $specClone.SetAttribute('title', "$($stage.title) - Passive Tree")
    foreach ($node in @($specClone.SelectNodes('.//*[@itemId]'))) {
        $oldId = $node.GetAttribute('itemId')
        if ($idMap.ContainsKey($oldId)) { $node.SetAttribute('itemId', $idMap[$oldId]) }
    }
    $tree.AppendChild($specClone) | Out-Null

    $configClone = $xml.ImportNode($sourceConfigSet, $true)
    $configClone.SetAttribute('id', [string]$stageIndex)
    $configClone.SetAttribute('title', "$($stage.title) - Configuration")
    $config.AppendChild($configClone) | Out-Null
    $stageIndex++
}

$tree.SetAttribute('activeSpec', '1')
$skills.SetAttribute('activeSkillSet', '1')
$items.SetAttribute('activeItemSet', '1')
$config.SetAttribute('activeConfigSet', '1')
$xml.PathOfBuilding.Build.SetAttribute('level', [string]$finalStage.level)
$xml.PathOfBuilding.Build.SetAttribute('mainSocketGroup', '7')

$notes = $xml.SelectSingleNode('/PathOfBuilding/Notes')
if (-not $notes) {
    $notes = $xml.CreateElement('Notes')
    $xml.DocumentElement.AppendChild($notes) | Out-Null
}
$notes.InnerText = @($definition.pob_notes) -join "`r`n"

Save-Xml $xml $Output

[xml]$check = [IO.File]::ReadAllText($Output, [Text.Encoding]::UTF8)
$expectedStages = @($definition.sources.pob_stages).Count
$counts = @(
    $check.SelectNodes('/PathOfBuilding/Tree/Spec').Count,
    $check.SelectNodes('/PathOfBuilding/Skills/SkillSet').Count,
    $check.SelectNodes('/PathOfBuilding/Items/ItemSet').Count,
    $check.SelectNodes('/PathOfBuilding/Config/ConfigSet').Count
)
if (@($counts | Where-Object { $_ -ne $expectedStages }).Count) {
    throw "Unexpected stage counts: $($counts -join '/')"
}

$itemIds = @{}
$check.SelectNodes('/PathOfBuilding/Items/Item') | ForEach-Object { $itemIds[$_.GetAttribute('id')] = $true }
$orphans = @($check.SelectNodes('//*[@itemId]') | Where-Object {
    $_.GetAttribute('itemId') -ne '0' -and -not $itemIds.ContainsKey($_.GetAttribute('itemId'))
})
if ($orphans.Count) { throw "Found $($orphans.Count) orphaned item references." }

foreach ($skillSet in @($check.SelectNodes('/PathOfBuilding/Skills/SkillSet'))) {
    $groups = @($skillSet.SelectNodes('./Skill'))
    if ($groups.Count -lt 7 -or -not $groups[6].SelectSingleNode("./Gem[@nameSpec='Herald of Thunder']")) {
        throw "Herald of Thunder is not main socket group 7 in SkillSet $($skillSet.id)."
    }
}

$requiredText = @(
    'Storm Secret',
    'Dendrobate',
    'Foulborn The Blue Nightmare',
    'Vessel of Vinktar',
    'Progenesis',
    'Calamitous Visions'
)
foreach ($value in $requiredText) {
    if (-not $check.OuterXml.Contains($value)) { throw "Merged PoB is missing required source data: $value" }
}
$excludedItemText = @('Leer Cast', 'Dying Breath', 'Belly of the Beast', "Vixen's Entrapment")
$mergedItemText = (@($check.SelectNodes('/PathOfBuilding/Items/Item')) | ForEach-Object { $_.InnerText }) -join "`n"
foreach ($value in $excludedItemText) {
    if ($mergedItemText.Contains($value)) { throw "Unused Animated Guardian item leaked into merged PoB: $value" }
}
if ($check.SelectSingleNode("/PathOfBuilding/Items/ItemSet[@title='Animated Guardian']")) {
    throw 'Unused Animated Guardian item set leaked into merged PoB.'
}

[pscustomobject]@{
    Output = $Output
    Bytes = (Get-Item -LiteralPath $Output).Length
    PassiveStages = $counts[0]
    SkillStages = $counts[1]
    ItemStages = $counts[2]
    ConfigStages = $counts[3]
    OrphanedItemReferences = $orphans.Count
    SourcePart1SHA256 = $sourceHashes['GXoW7hsWd6']
    SourcePart2SHA256 = $sourceHashes['gcNfqrGAAe']
    SHA256 = (Get-FileHash -LiteralPath $Output -Algorithm SHA256).Hash
}
