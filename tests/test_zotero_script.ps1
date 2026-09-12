param(
    [string]$Python = 'C:\Users\XJF\AppData\Local\Programs\Python\Python311\python.exe',
    [string]$SkillRoot = (Split-Path -Parent $PSScriptRoot)
)

$ErrorActionPreference = 'Stop'
$script = Join-Path $SkillRoot 'scripts\push_to_zotero.py'

if (-not (Test-Path -LiteralPath $Python -PathType Leaf)) {
    throw "Python interpreter not found: $Python"
}

& $Python -m py_compile $script
if ($LASTEXITCODE -ne 0) { throw 'Python compilation failed.' }

$help = & $Python $script --help 2>&1
if ($LASTEXITCODE -ne 0) { throw 'CLI help command failed.' }
if (($help -join "`n") -notmatch '--ris-file') { throw 'CLI help does not expose RIS import.' }
if (($help -join "`n") -notmatch '--json-file') { throw 'CLI help does not expose JSON import.' }

Write-Output 'Zotero helper checks passed.'
