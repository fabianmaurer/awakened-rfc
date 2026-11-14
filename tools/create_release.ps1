# Builds a production DLL and creates a dated ZIP and Windows installer.
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$dllDir = Join-Path $root 'Awakened RFC\CvGameCoreDLL'
$settings = Join-Path $dllDir 'Makefile.settings'
if (-not (Test-Path $settings)) { throw 'Create CvGameCoreDLL\Makefile.settings from Makefile.settings.example first.' }
if (Select-String -Path $settings -Pattern '^\s*ARFC_ENABLE_REPORTING\s*=\s*1\s*$') { throw 'Set ARFC_ENABLE_REPORTING=0 in Makefile.settings before building a release.' }
$vswhere = Join-Path ${env:ProgramFiles(x86)} 'Microsoft Visual Studio\Installer\vswhere.exe'
if (-not (Test-Path $vswhere)) { throw 'Visual Studio Installer (vswhere.exe) was not found.' }
$vs = & $vswhere -latest -products '*' -requires Microsoft.Component.MSBuild Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath
if (-not $vs) { throw 'Visual Studio with MSBuild and C++ tools is required.' }
$msbuild = Join-Path $vs 'MSBuild\Current\Bin\MSBuild.exe'
$vc = Get-ChildItem (Join-Path $vs 'VC\Tools\MSVC') -Directory | Sort-Object Name -Descending | Select-Object -First 1
$nmakeDir = Join-Path $vc.FullName 'bin\Hostx64\x64'
$iscc = Get-Command ISCC.exe -ErrorAction SilentlyContinue
if ($iscc) { $compiler = $iscc.Source } else {
    $compiler = Join-Path ${env:ProgramFiles(x86)} 'Inno Setup 6\ISCC.exe'
    if (-not (Test-Path $compiler)) { $compiler = Join-Path $env:LOCALAPPDATA 'Programs\Inno Setup 6\ISCC.exe' }
    if (-not (Test-Path $compiler)) { throw 'Install Inno Setup 6 or add ISCC.exe to PATH.' }
}
$releaseRoot = Join-Path $root 'dist'
$dateName = Get-Date -Format 'yyyy-MM-dd-HHmmss'
$destination = Join-Path $releaseRoot $dateName
$number = 2
while (Test-Path -LiteralPath $destination) {
    $destination = Join-Path $releaseRoot "$dateName-$number"
    $number++
}
$stage = Join-Path ([IO.Path]::GetTempPath()) ('arfc-release-' + [guid]::NewGuid().ToString('N'))
$oldPath = $env:Path
try {
    New-Item -ItemType Directory -Path $stage | Out-Null
    $env:Path = "$nmakeDir;$env:Path"
    Push-Location $dllDir
    try {
        & $msbuild 'CvGameCoreDLL.vcxproj' /p:Configuration=Release /p:Platform=Win32 /verbosity:minimal /m:1
        if ($LASTEXITCODE -ne 0) { throw 'Production DLL build failed.' }
    } finally { Pop-Location }
    & python (Join-Path $PSScriptRoot 'package_release.py') --output-dir $stage
    if ($LASTEXITCODE -ne 0) { throw 'Release packaging failed.' }
    Expand-Archive -LiteralPath (Join-Path $stage 'Awakened-RFC.zip') -DestinationPath (Join-Path $stage 'payload')
    & $compiler "/DPayloadDir=$stage\payload\Awakened RFC" "/DOutputDir=$stage" (Join-Path $PSScriptRoot 'release_installer.iss')
    if ($LASTEXITCODE -ne 0) { throw 'Installer compilation failed.' }
    New-Item -ItemType Directory -Path $destination | Out-Null
    Move-Item -LiteralPath (Join-Path $stage 'Awakened-RFC.zip'), (Join-Path $stage 'Awakened-RFC-Setup.exe') -Destination $destination
    Write-Host "Release created: $destination"
} finally {
    $env:Path = $oldPath
    if (Test-Path $stage) { Remove-Item -LiteralPath $stage -Recurse -Force }
}
