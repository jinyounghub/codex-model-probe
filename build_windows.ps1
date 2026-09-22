$ErrorActionPreference = 'Stop'
Remove-Item Env:TCL_LIBRARY,Env:TK_LIBRARY,Env:_MEIPASS2 -ErrorAction SilentlyContinue
$envKeys = @(Get-ChildItem Env: | Where-Object { $_.Name -like '_PYI_*' } | Select-Object -ExpandProperty Name)
foreach ($envKey in $envKeys) { Remove-Item -Path ("Env:" + $envKey) -ErrorAction SilentlyContinue }
$python = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $python)) {
    throw 'Run install_mitmproxy.ps1 first. / install_mitmproxy.ps1을 먼저 실행하세요.'
}
& $python -m pip install --quiet --disable-pip-version-check 'pyinstaller==6.22.3'
if ($LASTEXITCODE -ne 0) { throw 'PyInstaller installation failed.' }

& $python (Join-Path $PSScriptRoot 'build_bundle.py')
if ($LASTEXITCODE -ne 0) { throw 'Application bundle build failed.' }
& (Join-Path $PSScriptRoot 'build_installer.ps1')
& $python (Join-Path $PSScriptRoot 'package_release.py')
if ($LASTEXITCODE -ne 0) { throw 'Release packaging failed.' }
Write-Output (Join-Path $PSScriptRoot 'dist\0.4.0')
