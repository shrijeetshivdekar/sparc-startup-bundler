$ChromeCandidates = @(
  "$env:ProgramFiles\Google\Chrome\Application\chrome.exe",
  "$env:ProgramFiles(x86)\Google\Chrome\Application\chrome.exe",
  "$env:LocalAppData\Google\Chrome\Application\chrome.exe"
)

$Chrome = $ChromeCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $Chrome) {
  throw "Could not find chrome.exe. Install Google Chrome or update this script with your Chrome path."
}

$RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Profile = Join-Path $RepoRoot ".chrome-profile\manual-google-form"
New-Item -ItemType Directory -Force -Path $Profile | Out-Null

$Port = 9333

Start-Process -FilePath $Chrome -ArgumentList @(
  "--remote-debugging-port=$Port",
  "--user-data-dir=$Profile",
  "https://docs.google.com/forms/u/0/create"
)

Write-Host ""
Write-Host "Chrome opened in normal mode with remote debugging on port $Port."
Write-Host "1. Sign in to Google in that Chrome window."
Write-Host "2. Open or keep the blank Google Form editor visible."
Write-Host "3. Run: python tools/create_underwriter_google_form_selenium.py --attach --no-pause"
