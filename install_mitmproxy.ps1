$ErrorActionPreference = 'Stop'

$bundledPython = Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
$candidates = @(
    [pscustomobject]@{ File = $bundledPython; Prefix = @() },
    [pscustomobject]@{ File = 'py'; Prefix = @('-3') },
    [pscustomobject]@{ File = 'python'; Prefix = @() }
)
$selected = $null
foreach ($candidate in $candidates) {
    if ($candidate.File -eq $bundledPython) {
        if (-not (Test-Path -LiteralPath $candidate.File)) { continue }
    } elseif (-not (Get-Command $candidate.File -ErrorAction SilentlyContinue)) {
        continue
    }
    $exe = $candidate.File
    $prefix = $candidate.Prefix
    & $exe @prefix -c 'import sys; sys.exit(0 if sys.version_info >= (3, 12) else 1)' 2>$null
    if ($LASTEXITCODE -eq 0) {
        $selected = $candidate
        break
    }
}
if ($null -eq $selected) {
    throw 'Python 3.12 or newer is required. Install Python from python.org, then rerun this script. / Python 3.12 이상이 필요합니다.'
}

$venv = Join-Path $PSScriptRoot '.venv'
$exe = $selected.File
$prefix = $selected.Prefix
& $exe @prefix -m venv $venv
if ($LASTEXITCODE -ne 0) { throw 'Could not create Python environment. / Python 가상환경 생성 실패' }
$venvPython = Join-Path $venv 'Scripts\python.exe'
& $venvPython -m pip install --disable-pip-version-check 'mitmproxy==12.2.3'
if ($LASTEXITCODE -ne 0) { throw 'mitmproxy installation failed. / mitmproxy 설치 실패' }
Write-Output ('Installed / 설치 완료: ' + (Join-Path $venv 'Scripts\mitmdump.exe'))
