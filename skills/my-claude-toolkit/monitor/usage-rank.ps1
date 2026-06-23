# usage-rank.ps1 — aggregate the usage-counter CSV into a ranked top-list per
# category (skill / command / agent). Read-only. ASCII output.
#   Run:  powershell -NoProfile -ExecutionPolicy Bypass -File usage-rank.ps1 [-Top 10]
param(
    [string]$Csv = (Join-Path $env:USERPROFILE '.claude\usage-log.csv'),
    [int]$Top = 10
)
$ErrorActionPreference = 'SilentlyContinue'

if (-not (Test-Path $Csv)) {
    "No usage log yet at $Csv. Install the usage-counter hook (see README.md) and run a few sessions."
    exit 0
}

$rows = Import-Csv $Csv
if (-not $rows -or $rows.Count -eq 0) { "Usage log is empty: $Csv"; exit 0 }

$first = ($rows | Select-Object -First 1).timestamp
$last  = ($rows | Select-Object -Last 1).timestamp
"Usage ranking from $Csv"
"Rows: $($rows.Count)  |  Range: $first .. $last"

foreach ($cat in @('skill', 'command', 'agent')) {
    "`n=== $cat (top $Top) ==="
    $rows | Where-Object { $_.category -eq $cat } |
        Group-Object name |
        Sort-Object Count -Descending |
        Select-Object -First $Top |
        ForEach-Object { '{0,5}  {1}' -f $_.Count, $_.Name }
}
