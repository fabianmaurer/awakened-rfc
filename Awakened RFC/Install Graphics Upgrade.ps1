# Installs or updates Deliverator's optional GraphicsUpgrade beside BtS.
# Run from an installed Mods\Awakened RFC folder, with the game closed.
$ErrorActionPreference = 'Stop'
$game = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
if (-not (Test-Path -LiteralPath (Join-Path $game 'Civ4BeyondSword.exe') -PathType Leaf)) {
    throw 'Place Awakened RFC in the Beyond the Sword Mods folder before running this installer.'
}
if (Get-Process -Name 'Civ4BeyondSword' -ErrorAction SilentlyContinue) {
    throw 'Close Beyond the Sword before installing or updating GraphicsUpgrade.'
}

$headers = @{ 'User-Agent' = 'Awakened-RFC-GraphicsUpgrade-Installer'; 'Accept' = 'application/vnd.github+json' }
$release = Invoke-RestMethod -Headers $headers -Uri 'https://api.github.com/repos/deliverator23/Civ4BTS-GraphicsUpgrade/releases/latest'
$asset = @($release.assets | Where-Object { $_.name -eq 'GraphicsUpgrade.zip' })
if ($asset.Count -ne 1 -or $asset[0].browser_download_url -notmatch '^https://github\.com/deliverator23/Civ4BTS-GraphicsUpgrade/releases/download/') {
    throw 'The latest release does not contain the expected GraphicsUpgrade.zip asset.'
}
$temp = Join-Path ([IO.Path]::GetTempPath()) ('arfc-graphics-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $temp | Out-Null
try {
    $zip = Join-Path $temp 'release.zip'
    Invoke-WebRequest -Headers $headers -Uri $asset[0].browser_download_url -OutFile $zip
    Expand-Archive -LiteralPath $zip -DestinationPath (Join-Path $temp 'release')
    $source = Join-Path $temp 'release'
    if (-not (Test-Path -LiteralPath (Join-Path $source 'd3d9.dll'))) {
        $folders = @(Get-ChildItem -LiteralPath $source -Directory)
        if ($folders.Count -ne 1) { throw 'Unexpected release layout: expected one release folder.' }
        $source = $folders[0].FullName
    }
    foreach ($required in @('d3d9.dll', 'GraphicsUpgrade.ini', 'GraphicsUpgrade')) {
        if (-not (Test-Path -LiteralPath (Join-Path $source $required))) { throw "Unexpected release layout: missing $required" }
    }
    $manifestPath = Join-Path $game 'GraphicsUpgrade\awakened-rfc-install.json'
    $old = @{}
    if (Test-Path -LiteralPath $manifestPath) {
        $manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
        foreach ($entry in $manifest.files.PSObject.Properties) { $old[$entry.Name] = $entry.Value }
    }
    $files = @((Get-Item -LiteralPath (Join-Path $source 'd3d9.dll')))
    foreach ($dir in @('GraphicsUpgrade', 'presets')) {
        $path = Join-Path $source $dir
        if (Test-Path -LiteralPath $path -PathType Container) { $files += @(Get-ChildItem -LiteralPath $path -File -Recurse) }
    }
    $new = @{}
    foreach ($file in $files) {
        $relative = $file.FullName.Substring($source.Length + 1)
        $target = Join-Path $game $relative
        if (Test-Path -LiteralPath $target) {
            if (-not $old.ContainsKey($relative) -or (Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash -ne $old[$relative]) {
                throw "Refusing to overwrite an existing or modified file: $target. See the GraphicsUpgrade instructions for proxy chaining."
            }
        }
        $new[$relative] = (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash
    }
    foreach ($file in $files) {
        $relative = $file.FullName.Substring($source.Length + 1)
        $target = Join-Path $game $relative
        New-Item -ItemType Directory -Force -Path (Split-Path -Parent $target) | Out-Null
        Copy-Item -LiteralPath $file.FullName -Destination $target -Force
    }
    $settings = Join-Path $game 'GraphicsUpgrade.ini'
    if (-not (Test-Path -LiteralPath $settings)) {
        Copy-Item -LiteralPath (Join-Path $source 'GraphicsUpgrade.ini') -Destination $settings
    } else {
        Write-Host 'Kept your existing GraphicsUpgrade.ini. Check upstream release notes for changed settings.'
    }
    @{ version = $release.tag_name; files = $new } | ConvertTo-Json | Set-Content -LiteralPath $manifestPath -Encoding UTF8
    Write-Host "Installed GraphicsUpgrade $($release.tag_name) in $game"
    Write-Host 'GraphicsUpgrade affects all BtS games. Start Awakened RFC normally.'
} finally {
    Remove-Item -LiteralPath $temp -Recurse -Force
}
