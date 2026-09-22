$ErrorActionPreference = 'Stop'
Remove-Item Env:TCL_LIBRARY,Env:TK_LIBRARY,Env:_MEIPASS2 -ErrorAction SilentlyContinue
$envKeys = @(Get-ChildItem Env: | Where-Object { $_.Name -like '_PYI_*' } | Select-Object -ExpandProperty Name)
foreach ($envKey in $envKeys) { Remove-Item -Path ("Env:" + $envKey) -ErrorAction SilentlyContinue }
$python = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $python)) {
    throw 'Run install_mitmproxy.ps1 first. / install_mitmproxy.ps1을 먼저 실행하세요.'
}
& $python (Join-Path $PSScriptRoot 'vendor_mitmdump.py')
if ($LASTEXITCODE -ne 0) { throw 'Runtime distribution is blocked or verification failed. See DEFENDER.md.' }
& $python -m pip install --quiet --disable-pip-version-check 'pyinstaller==6.22.3'
if ($LASTEXITCODE -ne 0) { throw 'PyInstaller installation failed.' }

foreach ($language in @('ko', 'en')) {
    & $python -m PyInstaller --noconfirm --clean --onefile --windowed `
        --name "CodexModelMonitor-$language" `
        --distpath (Join-Path $PSScriptRoot 'dist') `
        --workpath (Join-Path $PSScriptRoot "build\$language") `
        --specpath (Join-Path $PSScriptRoot 'build') `
        (Join-Path $PSScriptRoot 'gui.py')
    if ($LASTEXITCODE -ne 0) { throw "Build failed: $language" }
}
Write-Output (Join-Path $PSScriptRoot 'dist')
