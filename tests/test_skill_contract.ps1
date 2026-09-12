param(
    [string]$SkillRoot = (Split-Path -Parent $PSScriptRoot)
)

$ErrorActionPreference = 'Stop'

$requiredFiles = @(
    'SKILL.md',
    'references/common-workflow.md',
    'references/batch-doi.md',
    'references/publishers.md',
    'references/zotero.md',
    'scripts/push_to_zotero.py',
    'scripts/prepare_doi_batch.py',
    'scripts/record_doi_result.py'
)

foreach ($relativePath in $requiredFiles) {
    $path = Join-Path $SkillRoot $relativePath
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        throw "Missing required file: $relativePath"
    }
}

$skill = Get-Content (Join-Path $SkillRoot 'SKILL.md') -Raw
if ($skill -notmatch '(?ms)^---\s*\r?\nname:\s*publisher-web-research\s*\r?\ndescription:\s*Use when') {
    throw 'SKILL.md frontmatter is missing the expected name or routing description.'
}

foreach ($publisher in @('ScienceDirect', 'ACS Publications', 'RSC Publishing', 'Wiley Online Library', 'Science/AAAS', 'Nature Portfolio')) {
    if ($skill -notmatch [regex]::Escape($publisher)) {
        throw "SKILL.md does not route $publisher."
    }
}

$allText = Get-ChildItem $SkillRoot -Recurse -File | Where-Object { $_.Extension -in '.md', '.py' } | Get-Content -Raw
foreach ($forbidden in @('webdriver', 'AutomationControlled', 'ignoreDefaultChromeArg', 'Cookie:')) {
    if ($allText -match [regex]::Escape($forbidden)) {
        throw "Forbidden browser-evasion or cookie-forwarding content found: $forbidden"
    }
}

Write-Output 'Skill contract checks passed.'
