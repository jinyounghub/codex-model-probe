param([switch]$PrepareOnly)
$ErrorActionPreference = 'Stop'
$compilerRoot = Join-Path $PSScriptRoot 'build\tools\inno-7.1.0'
$compiler = Join-Path $compilerRoot 'ISCC.exe'
if (-not (Test-Path -LiteralPath $compiler)) {
    $downloadDir = Join-Path $PSScriptRoot 'build\tools'
    New-Item -ItemType Directory -Force -Path $downloadDir | Out-Null
    $installer = Join-Path $downloadDir 'innosetup-7.1.0-x64.exe'
    Invoke-WebRequest -Uri 'https://github.com/jrsoftware/issrc/releases/download/is-7_1_0/innosetup-7.1.0-x64.exe' -OutFile $installer
    $signature = Get-AuthenticodeSignature -LiteralPath $installer
    if ($signature.Status -ne 'Valid' -or $signature.SignerCertificate.Subject -notmatch 'CN=Pyrsys B\.V\.') {
        throw 'The Inno Setup download does not have the expected valid publisher signature.'
    }
    $installArgs = @('/VERYSILENT', '/SUPPRESSMSGBOXES', '/NORESTART', '/SP-', '/CURRENTUSER', '/NOICONS', '/TASKS=', ('/DIR="' + $compilerRoot + '"'))
    $proc = Start-Process -FilePath $installer -ArgumentList $installArgs -WindowStyle Hidden -PassThru -Wait
    if ($proc.ExitCode -ne 0) { throw 'Inno Setup compiler installation failed.' }
}
if ($PrepareOnly) { return }
$python = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
Push-Location $PSScriptRoot
try {
    & $python -c 'from package_release import BUNDLE_ROOT, validate_bundle, validate_module_inventory; [(validate_bundle(BUNDLE_ROOT / ("CodexModelMonitor-" + lang)), validate_module_inventory(BUNDLE_ROOT / ("CodexModelMonitor-" + lang))) for lang in ("ko", "en")]'
    if ($LASTEXITCODE -ne 0) { throw 'Bundle verification failed before installer build.' }
} finally { Pop-Location }
foreach ($language in @('ko', 'en')) {
    & $compiler ("/DEdition=" + $language) (Join-Path $PSScriptRoot 'installer.iss')
    if ($LASTEXITCODE -ne 0) { throw "Installer compilation failed: $language" }
}
