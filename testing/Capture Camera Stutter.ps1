# User-operated capture of manual panning/zooming; never starts Civ4 or autoplay.
param([ValidateRange(10, 60)][int]$Seconds = 30)
$ErrorActionPreference = 'Stop'
$identity = [Security.Principal.WindowsIdentity]::GetCurrent()
$principal = New-Object Security.Principal.WindowsPrincipal($identity)
if (!$principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    # This console is interactive: the user must see the instructions and countdown.
    $arguments = '-NoProfile -ExecutionPolicy Bypass -File "{0}" -Seconds {1}' -f $PSCommandPath, $Seconds
    $elevated = Start-Process powershell.exe -Verb RunAs -ArgumentList $arguments -Wait -PassThru
    exit $elevated.ExitCode
}

$wpr = (Get-Command wpr.exe -ErrorAction Stop).Source
$games = @(Get-Process Civ4BeyondSword -ErrorAction SilentlyContinue)
if ($games.Count -ne 1) { throw 'Open exactly one Civ4 Beyond the Sword game and load the affected map first.' }
$game = $games[0]
$repo = Split-Path $PSScriptRoot -Parent
$run = Join-Path $PSScriptRoot ('runs\camera-stutter-' + (Get-Date -Format 'yyyyMMdd-HHmmss') + '-' + $game.Id)
New-Item -ItemType Directory -Path $run -ErrorAction Stop | Out-Null
$instance = 'AwakenedCamera' + $PID
$trace = Join-Path $run 'camera-stutter.etl'
$scenario = Read-Host 'Map/mode being captured (for example XL 3000 BC, WorldBuilder)'
$metadata = [ordered]@{
    game_pid = $game.Id
    game_executable = $game.Path
    scenario = $scenario
    duration_seconds = $Seconds
    profiles = @('GeneralProfile', 'GPU')
    wpr_instance = $instance
    symbol_search_path = Join-Path $repo 'Awakened RFC\CvGameCoreDLL\temp_files'
}
# Read-only module inventory: do not assume the game uses this checkout's DLL.
try {
    $module = @($game.Modules | Where-Object { $_.ModuleName -ieq 'CvGameCoreDLL.dll' })
    if ($module.Count -eq 1) {
        $metadata.game_dll = $module[0].FileName
        $metadata.game_dll_sha256 = (Get-FileHash -LiteralPath $module[0].FileName).Hash
    } else { $metadata.module_note = 'Game DLL path unavailable; use the trace image-load data.' }
} catch { $metadata.module_note = $_.Exception.Message }
$metadata | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $run 'capture.json') -Encoding UTF8
Write-Host "After pressing Enter, switch to Civ4 within 8 seconds."
Write-Host "Pan and zoom continuously for $Seconds seconds; do not end the turn."
Write-Host 'Recording stops automatically. Leave this console open until the trace is saved.'
[void](Read-Host 'Press Enter when ready')
Start-Sleep -Seconds 8

$recording = $false
try {
    # Memory mode avoids continuous trace-file writes during the measured interval.
    $startOutput = & $wpr -start GeneralProfile -start GPU -instancename $instance 2>&1
    $startCode = $LASTEXITCODE
    $startOutput | Out-File -LiteralPath (Join-Path $run 'wpr.log') -Encoding UTF8
    if ($startCode -ne 0) { throw "WPR could not start ($startCode). See $run\wpr.log. Existing recordings were not cancelled." }
    $recording = $true
    $metadata.capture_started_utc = [DateTime]::UtcNow.ToString('o')
    for ($remaining = $Seconds; $remaining -gt 0; $remaining--) {
        Write-Progress -Activity 'Capturing camera stutter' -Status "$remaining seconds remaining" -PercentComplete (100 * ($Seconds - $remaining) / $Seconds)
        Start-Sleep -Seconds 1
    }
    Write-Progress -Activity 'Capturing camera stutter' -Completed
    $metadata.capture_ended_utc = [DateTime]::UtcNow.ToString('o')
    Write-Host 'Saving the trace; this can take a minute...'
    & $wpr -stop $trace 'Civ4 manual camera panning and zooming stutter' -skipPdbGen -instancename $instance 2>&1 |
        Out-File -LiteralPath (Join-Path $run 'wpr.log') -Append -Encoding UTF8
    if ($LASTEXITCODE -ne 0) { throw "WPR could not save the trace. See $run\wpr.log." }
    $recording = $false
    $metadata.trace_bytes = (Get-Item -LiteralPath $trace).Length
} finally {
    # Only clean up this script's recording, never another WPR session.
    if ($recording) { & $wpr -cancel -instancename $instance | Out-Null }
    $metadata | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $run 'capture.json') -Encoding UTF8
}
Write-Host "Saved: $trace"
Write-Host 'Return to the chat and ask to analyze the camera-stutter capture.'
if ($principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    [void](Read-Host 'Press Enter to close')
}
