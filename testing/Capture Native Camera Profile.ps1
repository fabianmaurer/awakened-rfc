# User-operated manual camera profile. No autoplay, turn advancement or ETW session.
param(
    [ValidateRange(10, 60)][int]$Seconds = 10,
    [string]$GameExecutable
)
$ErrorActionPreference = 'Stop'
if (Get-Process Civ4BeyondSword -ErrorAction SilentlyContinue) {
    throw 'Close Civ4 first. This launcher enables diagnostics only in the game process it starts.'
}
$repo = Split-Path $PSScriptRoot -Parent
if (!$GameExecutable) {
    $settings = Join-Path $repo 'Awakened RFC\CvGameCoreDLL\Makefile.settings'
    $installLine = Get-Content -LiteralPath $settings | Where-Object { $_ -match '^CIV4_MOD_INSTALL_PATH=' } | Select-Object -First 1
    if (!$installLine) { throw 'Pass -GameExecutable with the path to Civ4BeyondSword.exe, or configure Makefile.settings.' }
    $installedMod = ($installLine -split '=', 2)[1].Trim().Trim('"')
    $gameFolder = Split-Path (Split-Path $installedMod -Parent) -Parent
    $GameExecutable = Join-Path $gameFolder 'Civ4BeyondSword.exe'
}
$GameExecutable = (Resolve-Path -LiteralPath $GameExecutable).Path
$installedDll = Join-Path (Split-Path $GameExecutable -Parent) 'Mods\Awakened RFC\Assets\CvGameCoreDLL.dll'
$sourceDll = Join-Path $repo 'Awakened RFC\Assets\CvGameCoreDLL.dll'
$dllHash = (Get-FileHash -LiteralPath $installedDll).Hash
if ($dllHash -ne (Get-FileHash -LiteralPath $sourceDll).Hash) { throw 'Installed DLL differs from the checkout. Synchronize the diagnostic build first.' }
if (![Text.Encoding]::ASCII.GetString([IO.File]::ReadAllBytes($installedDll)).Contains('camera_profile_v1')) {
    throw 'The installed DLL does not contain the native camera profiler. Build with ARFC_ENABLE_REPORTING=1.'
}
$run = Join-Path $PSScriptRoot ('runs\camera-native-' + (Get-Date -Format 'yyyyMMdd-HHmmss') + '-' + [Guid]::NewGuid().ToString('N').Substring(0, 8))
New-Item -ItemType Directory -Path $run | Out-Null
$symbolFolder = Join-Path $repo 'Awakened RFC\CvGameCoreDLL\temp_files\reporting\Release'
foreach ($name in @('CvGameCoreDLL.pdb', 'CvGameCoreDLL.map')) {
    $symbol = Join-Path $symbolFolder $name
    if (Test-Path -LiteralPath $symbol) { Copy-Item -LiteralPath $symbol -Destination $run }
}
$controlName = 'Local\AwakenedRFC.Camera.' + [Guid]::NewGuid().ToString('N')
$mapping = [IO.MemoryMappedFiles.MemoryMappedFile]::CreateNew($controlName, 4096)
$view = $mapping.CreateViewAccessor()
$game = $null
$metadata = [ordered]@{
    duration_seconds = $Seconds
    game_executable = $GameExecutable
    game_dll_sha256 = $dllHash
    output = Join-Path $run 'native-camera.csv'
    sampling = 'Lookups and dirty flags: 1/64; plot display callbacks: 1/16; map callbacks and script-data getters: all calls.'
}
try {
    $view.Write(0, [int]0)
    $view.Write(4, [int]0x43414d31)
    $startInfo = New-Object Diagnostics.ProcessStartInfo
    $startInfo.FileName = $GameExecutable
    $startInfo.WorkingDirectory = Split-Path $GameExecutable -Parent
    $startInfo.Arguments = 'mod="Mods\Awakened RFC"'
    $startInfo.UseShellExecute = $false
    $startInfo.EnvironmentVariables['ARFC_CAMERA_PROFILE_CONTROL'] = $controlName
    $startInfo.EnvironmentVariables['ARFC_CAMERA_PROFILE_LOG'] = $metadata.output
    $game = [Diagnostics.Process]::Start($startInfo)
    $metadata.game_pid = $game.Id
    Write-Host 'Load the affected XL scenario or save, then enter WorldBuilder if that is where you reproduce the hitch.'
    Write-Host 'Return to this console once the map is ready. Do not close the game.'
    $metadata.scenario = Read-Host 'Map and mode being captured'
    Write-Host "After pressing Enter, switch back to Civ4 within 8 seconds. Pan and zoom for $Seconds seconds."
    Write-Host 'Do not end the turn. Collection and saving stop automatically.'
    [void](Read-Host 'Press Enter when ready')
    if ($game.HasExited) { throw 'The launched game process exited before capture. No profile was started.' }
    Start-Sleep -Seconds 8
    $metadata.capture_started_utc = [DateTime]::UtcNow.ToString('o')
    $view.Write(0, [int]1)
    for ($remaining = $Seconds; $remaining -gt 0; $remaining--) {
        Write-Progress -Activity 'Recording native camera timings' -Status "$remaining seconds remaining" -PercentComplete (100 * ($Seconds - $remaining) / $Seconds)
        Start-Sleep -Seconds 1
        if ($game.HasExited) { throw 'Civ4 exited during capture; native counters could not be saved.' }
    }
    Write-Progress -Activity 'Recording native camera timings' -Completed
    $metadata.capture_ended_utc = [DateTime]::UtcNow.ToString('o')
    $view.Write(0, [int]2)
    $deadline = [DateTime]::UtcNow.AddSeconds(15)
    while ($view.ReadInt32(0) -eq 2 -and [DateTime]::UtcNow -lt $deadline -and !$game.HasExited) { Start-Sleep -Milliseconds 100 }
    if ($view.ReadInt32(0) -ne 3) { throw 'The DLL did not acknowledge saving. Keep Civ4 visible during capture and check that the diagnostic DLL is installed.' }
    $metadata.status = 'saved'
    Write-Host "Saved: $($metadata.output)"
    Write-Host 'Collection is now disabled. Ask to analyze the native camera profile in the chat.'
} finally {
    $view.Write(0, [int]0)
    $metadata | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $run 'capture.json') -Encoding UTF8
    $view.Dispose()
    $mapping.Dispose()
}
