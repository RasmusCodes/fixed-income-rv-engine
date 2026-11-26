# Render a page (optionally with a URL hash) in headless Edge and save a PNG screenshot.
#   powershell -File scripts/shoot.ps1 -Page web/index.html -Hash "m=PL&tab=frpl" -Out shot.png [-Width 1300] [-Height 2400] [-Dark]
param(
  [string]$Page = "web/index.html",
  [string]$Hash = "",
  [Parameter(Mandatory = $true)][string]$Out,
  [int]$Width = 1300,
  [int]$Height = 2400,
  [switch]$Dark
)
$edge = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
$root = Split-Path -Parent $PSScriptRoot
$full = (Resolve-Path (Join-Path $root $Page)).Path -replace '\\', '/'
$url = "file:///$full"
if ($Hash) { $url = "$url#$Hash" }
$profile = Join-Path $env:TEMP "firv-edge-profile"
$args = @("--headless=new", "--disable-gpu", "--no-first-run", "--user-data-dir=$profile", "--allow-file-access-from-files",
  "--virtual-time-budget=25000", "--window-size=$Width,$Height", "--hide-scrollbars", "--screenshot=$Out")
if ($Dark) { $args += "--force-dark-mode" } else { $args += "--blink-settings=preferredColorScheme=1" }
$args += $url
$p = Start-Process -FilePath $edge -ArgumentList $args -PassThru -Wait -WindowStyle Hidden
if (Test-Path $Out) { "saved $Out ($((Get-Item $Out).Length) bytes)" } else { "screenshot failed (exit $($p.ExitCode))" }
