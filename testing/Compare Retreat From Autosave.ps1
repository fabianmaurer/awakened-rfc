# Switch production DLLs only. The user loads the same save and advances turns.
param([ValidateSet('before', 'after')][string]$Version = 'after')
$ErrorActionPreference = 'Stop'
if (Get-Process Civ4BeyondSword -ErrorAction SilentlyContinue) {
    throw 'Close Civ4 before switching DLLs.'
}
$repo = Split-Path $PSScriptRoot -Parent
$snapshot = Join-Path $PSScriptRoot 'bin\retreat-comparison'
$manifest = Get-Content -LiteralPath (Join-Path $snapshot 'versions.json') -Raw | ConvertFrom-Json
$source = Join-Path $snapshot "$Version.dll"
$expected = $manifest.$Version
if (!$expected -or (Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash -ne $expected) {
    throw "The $Version DLL does not match the preserved comparison snapshot."
}
$settings = Join-Path $repo 'Awakened RFC\CvGameCoreDLL\Makefile.settings'
$installLine = Get-Content -LiteralPath $settings | Where-Object { $_ -match '^\s*CIV4_MOD_INSTALL_PATH\s*=' } | Select-Object -Last 1
if (!$installLine) { throw 'Set CIV4_MOD_INSTALL_PATH in the ignored Makefile.settings first.' }
$install = ($installLine -split '=', 2)[1].Trim().Trim('"')
$destinations = @((Join-Path $repo 'Awakened RFC\Assets\CvGameCoreDLL.dll'),
                  (Join-Path $install 'Assets\CvGameCoreDLL.dll'))
foreach ($destination in $destinations) {
    if (!(Test-Path -LiteralPath (Split-Path $destination -Parent))) {
        throw "Mod Assets folder is missing: $destination"
    }
}
foreach ($destination in $destinations) {
    Copy-Item -LiteralPath $source -Destination $destination -Force
    if ((Get-FileHash -LiteralPath $destination -Algorithm SHA256).Hash -ne $expected) {
        throw "DLL copy verification failed: $destination"
    }
}
Write-Host "Installed '$Version' retreat DLL. No game has been launched."
Write-Host 'Load the same autosave, use the same settings/actions, and time the next 3-5 end turns.'
Write-Host 'Close Civ4 before selecting the other version. Finish with after selected for normal play.'
