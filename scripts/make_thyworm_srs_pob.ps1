$ErrorActionPreference = 'Stop'

$sourceUrl = 'https://pobb.in/aqWq4xty5YI6/raw'
$sourcePage = 'https://pobb.in/aqWq4xty5YI6'
$buildDir = 'C:\Users\User\Desktop\Game\PoeCharm3_20260307\POE1 POB\Builds\3.29-CotA'
$xmlPath = Join-Path $buildDir 'Thyworm_SRS_Guardian_SSF_한글.xml'
$notePath = Join-Path $buildDir 'Thyworm_SRS_Guardian_SSF_한글_노트.md'

$titleMap = [ordered]@{
    'Level 4 - after mud flats and hailrake' = '레벨 4 - 1장 갯벌·우박갈퀴 완료'
    'Level 10 - after killing Brutus' = '레벨 10 - 1장 브루투스 처치 후'
    'Level 14 - after killing Merveil' = '레벨 14 - 1장 메르베일 처치 후'
    'Level 18 - after killing Piety' = '레벨 18 - 3장 피에티 처치 후'
    'Level 22 - after killing Vaal Oversoul' = '레벨 22 - 2장 바알 신령 처치 후'
    'Level 26 - after the crematorium' = '레벨 26 - 3장 화장터 완료 후'
    'Level 30 - Library side quest completed' = '레벨 30 - 3장 도서관 보조 퀘스트 완료'
    'Level 33 - First Ascendancy' = '레벨 33 - 1차 전직'
    'Level 40 - After killing Malachai' = '레벨 40 - 4장 말라카이 처치 후'
    'Level 46 - After killing Kitava' = '레벨 46 - 5장 키타바 처치 후'
    'Level 50 - An extra golem' = '레벨 50 - 추가 골렘'
    'Level 55 - Second Ascendancy' = '레벨 55 - 2차 전직'
    'Level 60 - Chaos Res & Minion Damage' = '레벨 60 - 카오스 저항·소환수 피해'
    'Level 65 - Trigger Wand (get craft from Refinery)' = '레벨 65 - 발동 완드 (9장 정제소 제작법)'
    'Level 70 - Third Ascendancy & Kitava Dead' = '레벨 70 - 3차 전직·10장 키타바 처치'
    'Level 75 - Passive Tree Swap & More Life' = '레벨 75 - 패시브 트리 전환·생명력 보강'
    'Level 80 - Third Spectre' = '레벨 80 - 세 번째 망령'
    'Level 86 - Max Res & Corrupted Blood Immunity' = '레벨 86 - 최대 저항·타락한 피 면역'
    'Level 88 - Fourth Ascendancy' = '레벨 88 - 4차 전직'
    'Level 90 - 5-link & 2 voidstones' = '레벨 90 - 5링크·공허석 2개'
    'Level 95 - More sockets, life & anoint' = '레벨 95 - 소켓·생명력·성유 보강'
    'Katarina Swap to Umbral Army' = '카타리나 이후 - Umbral Army 전환'
    'Gear/spectres needed for 4 voidstones' = '공허석 4개용 장비·망령'
    'Level 100 - MoM / Uber Pinnacle Setup' = '레벨 100 - 정신력 문제(MoM)·우버 보스 세팅'
}

$notes = @'
# Thyworm SRS 가디언 SSF - 한글 진행 노트

원본: https://pobb.in/aqWq4xty5YI6
빌드 성격: 일반 적중형 격노의 유령 소환(SRS) 가디언. SSF 스타터부터 공허석 4개와 우버 세팅까지 한 파일에 들어 있다.

## 먼저 확인
- 패시브 트리·장비·스킬·설정의 드롭다운을 반드시 같은 단계로 맞춘다.
- 이 빌드는 팝콘 SRS도, 중독 SRS도 아니다. 소환수 불안정(Minion Instability)을 찍지 말고 지옥불 군단(Infernal Legion)을 주력 링크에 넣지 않는다.
- SRS 최대치는 20마리다. 보스에서는 20마리에 가깝게 유지하고, 맵에서는 진행 방향 앞쪽에 몇 번 소환한 뒤 계속 이동한다.
- 새로 나온 '소환수 38% 증폭' 계열 보조 젬은 이 세팅에서는 함정이므로 원본 링크를 따른다.

## 액트 진행 핵심
- 레벨 4: SRS + Summon Phantasm + Ruthless. 보조 화력은 Holy Flame Totem, 이동은 Shield Charge와 Frostblink.
- 레벨 10: 주력은 SRS + Melee Splash + Added Lightning Damage. Clarity를 켜고 Minion Damage·Ruthless는 보조 장비에서 미리 레벨업한다.
- 레벨 18: Tempest Shield, Desecrate를 추가하고 Flesh Offering도 미리 레벨업한다.
- 레벨 30 / 3장 도서관: SRS 4링크를 갖추고 Animate Guardian + Raise Spectre + Minion Life + Meat Shield를 준비한다. Purity of Elements, Summon Skitterbots, Automation + Convocation도 이 단계에서 정리한다.
- 레벨 33 / 1차 전직: Radiant Crusade. Summon Sentinel of Radiance를 사용한다. 첫 번째 큰 파워 스파이크다.
- 레벨 55 / 2차 전직: Unwavering Crusade. Summon Elemental Relic이 추가되며 SRS 링크는 Melee Splash + Unleash + Elemental Damage with Attacks 중심으로 전환한다.
- 레벨 65: 접미어가 빈 소환수 완드에 '장착된 주문 발동' 제작을 붙인다. 제작법은 9장 정제소의 녹색 불빛이 보이는 철창 구역에 있으며 파이프를 따라가면 된다.
- 발동 완드 소켓 순서는 위에서부터 Desecrate -> Flesh Offering -> Elemental Weakness. 순서가 중요하다.
- 레벨 70 / 3차 전직: Bastion of Hope. Shield Charge를 최소 4초마다 써서 방어 효과를 유지한다.
- 레벨 88 / 4차 전직: Time of Need.
- 카타리나 전환 단계: Time of Need 쪽을 환불하고 Umbral Army 경로로 바꾼다. 전환 전후 패시브 트리는 해당 드롭다운에서 직접 비교한다.

## 장비 우선순위
1. 캠페인에서는 주력 링크 수
2. 이동 속도 신발
3. 생명력과 원소 저항
4. 소환수 피해·소환수 공격/시전 속도
- 공허석 2개까지 필수 고유 아이템은 없다. 5링크만으로도 목표를 잡은 구성이다.
- 레벨 65 전후에는 발동 제작을 붙일 수 있도록 접미어가 하나 비어 있는 소환수 완드를 챙긴다.
- 공허석 4개 단계에서는 6링크, 주력 보조 젬 품질 20%, 생존 가능한 망령 구성을 목표로 한다.

## 주력 링크
- 중반 4링크: SRS + Melee Splash + Unleash + Elemental Damage with Attacks
- 레벨 90 5링크: SRS + Multistrike + Unleash + Elemental Damage with Attacks + Minion Damage
- 공허석 4개 / 6링크: 위 5링크 + Ruthless
- 맵핑은 Melee Splash가 편하고, PoB 후반 단계에 표시된 링크 교체를 우선한다.

## 망령과 수호자 기동
- 초반 망령: 2장 Carnage Chieftain, 6장 Host Chieftain.
- 이후 의식에서 Forest Warrior를 구하면 맹공·마무리 타격 용도로 교체한다. 일반 등급도 사용할 수 있다.
- 최종 후보: Perfect Guardian Turtle, Perfect Warlord, Perfect Primal Thunderbird, Perfect Hulking Miscreation. SSF에서는 나온 것부터 사용한다.
- 수호자 기동은 액트 중 주운 희귀 장비로 시작해도 된다. 소환수 생존이 안정되기 전에는 잃기 아까운 장비를 넣지 않는다.

## 심연 주얼
- 생명력
- 소환수 물리 또는 화염 피해 추가 (냉기·번개 추가도 임시 사용 가능)
- 소환수 도발 1개, 실명 1개
- 소환수 공격/시전 속도
- 최근 소환수 스킬 사용 시 소환수 피해
- 같은 유틸 옵션을 여러 개 과하게 겹치기보다 필요한 효과를 하나씩 확보한다.

## 아틀라스와 방어
- 초반: 지도 수급 + 의식(Ritual) + 배신(Betrayal). 발동 제작과 망령·기초 장비를 안정시킨다.
- 이후: 심연(Abyss)에서 Ghastly Eye Jewel과 Darkness Enthroned를 노린다.
- 공허석 2개 뒤에는 금고·성소를 활용하고, 공허석 4개는 메이븐 보스 러시 세팅으로 진행한다.
- 방어 축은 방어도, 막기, 최대 저항, 받는 물리 피해 전환, Purity of Elements의 원소 상태 이상 면역이다.
- 판테온은 초반 Lunaris + Gruthkul, 작열의 총주교 지도 비중이 높아지면 보조 신을 Abberath로 바꾼다.

## 전환 체크포인트
- 1차 전직: Sentinel of Radiance 획득
- 2차 전직: Elemental Relic 획득
- 3차 전직: Bastion of Hope로 막기 보강
- 공허석 2개: 레벨 90 단계, 5링크 기준
- 공허석 4개: 전용 장비·망령 단계, 6링크와 젬 품질 보강
- 최종: 레벨 100 MoM / 우버 보스 단계. 이 단계는 초반부터 억지로 따라 하지 않는다.
'@

if (-not (Test-Path -LiteralPath $buildDir -PathType Container)) {
    throw "PoBCharm 빌드 폴더를 찾지 못했습니다: $buildDir"
}

$code = (Invoke-RestMethod -Uri $sourceUrl).Trim()
$base64 = $code.Replace('-', '+').Replace('_', '/')
switch ($base64.Length % 4) {
    2 { $base64 += '==' }
    3 { $base64 += '=' }
}

$compressed = [Convert]::FromBase64String($base64)
$inputStream = [IO.MemoryStream]::new($compressed)
$zlibStream = [IO.Compression.ZLibStream]::new($inputStream, [IO.Compression.CompressionMode]::Decompress)
$reader = [IO.StreamReader]::new($zlibStream, [Text.Encoding]::UTF8)
$xmlText = $reader.ReadToEnd()
$reader.Dispose()
$zlibStream.Dispose()
$inputStream.Dispose()

$document = [Xml.XmlDocument]::new()
$document.PreserveWhitespace = $true
$document.LoadXml($xmlText)

$groups = @(
    @{ Name = 'Tree'; XPath = '/PathOfBuilding/Tree/Spec' },
    @{ Name = 'Items'; XPath = '/PathOfBuilding/Items/ItemSet' },
    @{ Name = 'Skills'; XPath = '/PathOfBuilding/Skills/SkillSet' },
    @{ Name = 'Config'; XPath = '/PathOfBuilding/Config/ConfigSet' }
)

foreach ($group in $groups) {
    $nodes = @($document.SelectNodes($group.XPath))
    if ($nodes.Count -ne 24) {
        throw "$($group.Name) 단계 수가 24개가 아닙니다: $($nodes.Count)"
    }
    foreach ($node in $nodes) {
        $oldTitle = $node.GetAttribute('title')
        if (-not $titleMap.Contains($oldTitle)) {
            throw "번역표에 없는 단계명입니다: $oldTitle"
        }
        $node.SetAttribute('title', $titleMap[$oldTitle])
    }
}

$notesNode = $document.SelectSingleNode('/PathOfBuilding/Notes')
if ($null -eq $notesNode) {
    throw 'PoB XML에서 Notes 노드를 찾지 못했습니다.'
}
$notesNode.InnerText = $notes.Trim()

$settings = [Xml.XmlWriterSettings]::new()
$settings.Encoding = [Text.UTF8Encoding]::new($false)
$settings.Indent = $false
$settings.NewLineHandling = [Xml.NewLineHandling]::None
$writer = [Xml.XmlWriter]::Create($xmlPath, $settings)
$document.Save($writer)
$writer.Dispose()

$markdown = @"
$($notes.Trim())

---
PoB 원본: $sourcePage
PoBCharm XML: $([IO.Path]::GetFileName($xmlPath))
작성일: 2026-08-12
"@
[IO.File]::WriteAllText($notePath, $markdown, [Text.UTF8Encoding]::new($false))

[xml]$check = [IO.File]::ReadAllText($xmlPath, [Text.Encoding]::UTF8)
$result = [ordered]@{
    XmlPath = $xmlPath
    NotePath = $notePath
    XmlBytes = (Get-Item -LiteralPath $xmlPath).Length
    NoteBytes = (Get-Item -LiteralPath $notePath).Length
    TreeStages = @($check.PathOfBuilding.Tree.Spec).Count
    ItemStages = @($check.PathOfBuilding.Items.ItemSet).Count
    SkillStages = @($check.PathOfBuilding.Skills.SkillSet).Count
    ConfigStages = @($check.PathOfBuilding.Config.ConfigSet).Count
    NotesChars = $check.SelectSingleNode('/PathOfBuilding/Notes').InnerText.Length
}
$result | ConvertTo-Json
