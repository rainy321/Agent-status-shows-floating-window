# install.ps1 - installs the Claude traffic light for the current Windows user.
# Run it by double-clicking install.bat. Idempotent; backs up settings.json first.
# ASCII-only on purpose: Windows PowerShell 5.1 must parse it on any locale.

$ErrorActionPreference = 'Stop'
$src      = $PSScriptRoot
$dest     = Join-Path $env:USERPROFILE ".claude\traffic-light"
$settings = Join-Path $env:USERPROFILE ".claude\settings.json"

Write-Host "=== Claude traffic light installer ==="

# 1) Copy program files to a fixed location
New-Item -ItemType Directory -Force -Path $dest | Out-Null
Copy-Item (Join-Path $src "traffic_light.exe") $dest -Force
Copy-Item (Join-Path $src "update_status.ps1") $dest -Force
$hookScript = Join-Path $dest "update_status.ps1"
Write-Host "Files copied to: $dest"

# 2) Load settings.json (back it up first if it exists)
if (Test-Path $settings) {
    Copy-Item $settings "$settings.bak" -Force
    $cfg = Get-Content $settings -Raw -Encoding UTF8 | ConvertFrom-Json
} else {
    $cfg = [PSCustomObject]@{}
}
if (-not $cfg.PSObject.Properties['hooks']) {
    $cfg | Add-Member -NotePropertyName hooks -NotePropertyValue ([PSCustomObject]@{})
}

# 3) Merge our hooks: keep any existing hooks, replace prior traffic-light ones.
function Set-TLHook($hooks, $eventName, $status, $hookScript) {
    $cmd = 'powershell -NoProfile -ExecutionPolicy Bypass -File "' + $hookScript + '" ' + $status
    $entry = [PSCustomObject]@{ matcher=''; hooks=@(@([PSCustomObject]@{ type='command'; command=$cmd })) }
    if (-not $hooks.PSObject.Properties[$eventName]) {
        $hooks | Add-Member -NotePropertyName $eventName -NotePropertyValue @()
    }
    $kept = @($hooks.$eventName | Where-Object {
        $c = $null; try { $c = $_.hooks[0].command } catch {}
        -not ($c -like '*\traffic-light\update_status.ps1*')
    })
    $hooks.$eventName = @($kept) + $entry
}
Set-TLHook $cfg.hooks 'PreToolUse'  'working'  $hookScript
Set-TLHook $cfg.hooks 'PostToolUse' 'thinking' $hookScript
Set-TLHook $cfg.hooks 'Stop'        'idle'     $hookScript

# 4) Save settings.json WITHOUT a BOM (a BOM would break Claude Code's JSON parser)
$jsonStr = $cfg | ConvertTo-Json -Depth 30
[IO.File]::WriteAllText($settings, $jsonStr)
Write-Host "Hooks merged into: $settings"
Write-Host "(Old settings backed up to: $settings.bak)"

# 5) Desktop shortcut + launch the widget
$lnk = Join-Path ([Environment]::GetFolderPath('Desktop')) "Claude Traffic Light.lnk"
$ws = New-Object -ComObject WScript.Shell
$s = $ws.CreateShortcut($lnk)
$s.TargetPath = Join-Path $dest "traffic_light.exe"
$s.Save()
Write-Host "Desktop shortcut created."
Start-Process (Join-Path $dest "traffic_light.exe")
Write-Host ""
Write-Host "Done. The traffic light is running."
Write-Host "Restart any already-open Claude Code windows so the new hooks take effect."
