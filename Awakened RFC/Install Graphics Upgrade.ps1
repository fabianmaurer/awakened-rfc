# Installs or updates Deliverator's optional GraphicsUpgrade beside BtS.
# Run from an installed Mods\Awakened RFC folder, with the game closed.
$ErrorActionPreference = 'Stop'
function Set-IniValue([string]$text, [string]$section, [string]$key, [string]$value) {
    $header = '(?im)^[ \t]*\[' + [regex]::Escape($section) + '\][ \t]*\r?$'
    $match = [regex]::Match($text, $header)
    if (-not $match.Success) { return $text.TrimEnd() + "`r`n`r`n[$section]`r`n$key=$value`r`n" }
    $start = $match.Index + $match.Length
    $next = [regex]::Match($text.Substring($start), '(?m)^[ \t]*\[[^\]\r\n]+\]')
    $end = if ($next.Success) { $start + $next.Index } else { $text.Length }
    $body = $text.Substring($start, $end - $start)
    $keyPattern = '(?im)^[ \t]*' + [regex]::Escape($key) + '[ \t]*=[^\r\n]*'
    if ([regex]::IsMatch($body, $keyPattern)) {
        $body = [regex]::Replace($body, $keyPattern, "$key=$value")
    } else { $body = "`r`n$key=$value" + $body }
    return $text.Substring(0, $start) + $body + $text.Substring($end)
}
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
        $config = Get-Content -LiteralPath (Join-Path $source 'GraphicsUpgrade.ini') -Raw
        foreach ($section in @('water', 'reflection', 'shadows', 'lighting')) {
            $config = Set-IniValue $config $section 'Enabled' '0'
        }
        $config = Set-IniValue $config 'textures' 'Anisotropy' '1'
        $config = Set-IniValue $config 'textures' 'DetailNormals' '0'
        Set-Content -LiteralPath $settings -Value $config -Encoding Default
    } else {
        Write-Host 'Kept your existing GraphicsUpgrade.ini. Check upstream release notes for changed settings.'
    }
    @{ version = $release.tag_name; files = $new } | ConvertTo-Json | Set-Content -LiteralPath $manifestPath -Encoding UTF8
    Write-Host "Installed GraphicsUpgrade $($release.tag_name) in $game"
    Write-Host 'Start Awakened RFC normally. Existing global settings are preserved.'
} finally {
    Remove-Item -LiteralPath $temp -Recurse -Force
}
