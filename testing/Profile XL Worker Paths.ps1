# User-operated: one scenario-capture run; optionally precede it with clean timings.
# 3000 BC XL, performance mode, seed 1, 250 turns, one process.
param([switch]$IncludeCleanRun)
$ErrorActionPreference = 'Stop'
$repo = Split-Path $PSScriptRoot -Parent
$native = Join-Path $repo 'Awakened RFC\CvGameCoreDLL'
$oldPath = $env:Path
$oldTarget = $env:TARGET
$originalLocation = Get-Location

if (Get-Process Civ4BeyondSword -ErrorAction SilentlyContinue) {
    throw 'Close Civ4 before running the worker path profile.'
}
$nmakeCommand = Get-Command nmake.exe -ErrorAction SilentlyContinue
if ($nmakeCommand) {
    $nmakePath = $nmakeCommand.Source
} else {
    $vswhere = Join-Path ${env:ProgramFiles(x86)} 'Microsoft Visual Studio\Installer\vswhere.exe'
    if (!(Test-Path -LiteralPath $vswhere)) { throw 'NMake is unavailable; use a Visual Studio developer PowerShell.' }
    $nmakePath = & $vswhere -latest -products '*' -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -find 'VC\Tools\MSVC\**\bin\Hostx64\x64\nmake.exe' | Select-Object -Last 1
    if (!$nmakePath) { throw 'NMake is unavailable; install the Visual Studio C++ build tools launcher.' }
}

function Build-GameDll([int]$reporting) {
    # Same preparation/build sequence as the existing MSBuild project. NMake
    # and jom launch VC7.1 from Makefile.settings; they do not compile with VS2022.
    Set-Location $native
    $log = Join-Path $native "legacy-toolchain\worker-profile-build-$reporting.log"
    Write-Host "Building legacy DLL with ARFC_ENABLE_REPORTING=$reporting (log: $log)"
    $savedPreference = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        & $nmakePath source_list "ARFC_ENABLE_REPORTING=$reporting" *> $log
        $result = $LASTEXITCODE
        if ($result -eq 0) { & $nmakePath fastdep "ARFC_ENABLE_REPORTING=$reporting" *>> $log; $result = $LASTEXITCODE }
        if ($result -eq 0) { & $nmakePath precompile "ARFC_ENABLE_REPORTING=$reporting" *>> $log; $result = $LASTEXITCODE }
        if ($result -eq 0) { & '.\bin\jom.exe' build "ARFC_ENABLE_REPORTING=$reporting" *>> $log; $result = $LASTEXITCODE }
    } finally {
        $ErrorActionPreference = $savedPreference
    }
    if ($result -ne 0) {
        Get-Content -LiteralPath $log -Tail 30
        throw "DLL build failed ($result). See $log"
    }
    $mode = if ($reporting -eq 1) { 'reporting' } else { 'gameplay' }
    $selectedDll = Join-Path $native "temp_files\$mode\Release\CvGameCoreDLL.dll"
    $selectedHash = (Get-FileHash -LiteralPath $selectedDll -Algorithm SHA256).Hash
    $publishedDlls = @((Join-Path $native 'Release\CvGameCoreDLL.dll'),
                      (Join-Path $repo 'Awakened RFC\Assets\CvGameCoreDLL.dll'))
    foreach ($dll in $publishedDlls) {
        if ((Get-FileHash -LiteralPath $dll -Algorithm SHA256).Hash -ne $selectedHash) {
            throw "Published DLL does not match the selected $mode build: $dll"
        }
    }
    $tag = "AWAKENED_RFC_REPORTING=$reporting"
    if (![Text.Encoding]::ASCII.GetString([IO.File]::ReadAllBytes($selectedDll)).Contains($tag)) {
        throw "DLL build has the wrong reporting mode; expected $tag. See $log"
    }
}

try {
    $env:Path = "$(Split-Path $nmakePath -Parent);$oldPath"
    $env:TARGET = 'Release'
    Build-GameDll 1
    Set-Location $repo
    if ($IncludeCleanRun) {
        Write-Host 'Clean timing measurement, 3000 BC XL, seed 1, 250 turns.'
        & (Join-Path $PSScriptRoot 'run-test.cmd') --mode performance --start 0 --xl --runs 1 --turns 250 --seed 1 --startup-timeout 600 --stall-timeout 1800
        if ($LASTEXITCODE -ne 0) { throw "Clean performance run failed ($LASTEXITCODE)." }
    }
    Write-Host 'Capture representative worker searches and paired legacy comparisons.'
    & (Join-Path $PSScriptRoot 'run-test.cmd') --mode performance --start 0 --xl --runs 1 --turns 250 --seed 1 --capture-worker-paths --startup-timeout 600 --stall-timeout 1800
    if ($LASTEXITCODE -ne 0) { throw "Worker capture run failed ($LASTEXITCODE)." }
    Write-Host 'Recordings and reports are under testing\runs. Capture turns include export/comparison overhead.'
} finally {
    try {
        # Keep the normal workspace and installed mod on the production DLL.
        Build-GameDll 0
    } finally {
        $env:Path = $oldPath
        $env:TARGET = $oldTarget
        Set-Location $originalLocation
    }
}
