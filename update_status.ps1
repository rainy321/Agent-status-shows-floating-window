# update_status.ps1 - called by Claude Code hooks to write the traffic-light status.
# Why PowerShell: ships with Windows, so it runs on any PC without installing Python.
# Usage:  powershell -File update_status.ps1 working    (or thinking / idle)
# NOTE: keep this file ASCII-only (no Chinese) so Windows PowerShell 5.1 parses it on any locale.

param([string]$status = 'idle')

# Fixed per-user path, so the widget and this script always share ONE file,
# regardless of where the exe / this script live (Nuitka onefile runs from a temp dir).
$dir = Join-Path $env:LOCALAPPDATA "ClaudeTrafficLight"
if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }
$signalFile = Join-Path $dir "status.json"

# Unix epoch seconds, matching Python's time.time()
$ts = [DateTimeOffset]::Now.ToUnixTimeSeconds()

# Build  {"status":"working","timestamp":1781628303}
$json = '{"status":"' + $status + '","timestamp":' + $ts + '}'

# WriteAllText writes UTF-8 without BOM; content is pure ASCII -> safe across readers.
[IO.File]::WriteAllText($signalFile, $json)
