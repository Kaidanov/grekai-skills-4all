<#
.SYNOPSIS
  Append a TLDR report to the GLOBAL daily trail log, shared by every Claude window.

.DESCRIPTION
  Writes the report to  $HOME\.claude\tldr-trail\<YYYY-MM-DD>.md  so all windows on this
  machine accumulate one scannable TLDR log per day. Cross-process safe: a single atomic
  mkdir lock with a short bounded retry (default 2s) — if two windows finish at the same
  moment, the second waits a few ms and then appends, instead of clobbering the file.
  Fast by design (one append under lock); a stale lock (>30s, e.g. a crashed window) is
  auto-stolen so a dead process can never block the log.

.EXAMPLE
  & "$HOME\.claude\skills\tldr\scripts\Append-TldrTrail.ps1" -Path .\tldr.md -Project "m4n.map@feature-x" -Session 7be71b0
#>
[CmdletBinding()]
param(
  [Parameter(Mandatory = $true)] [string] $Path,   # file containing the TLDR markdown to log
  [string] $Project = '',                          # repo/branch or cwd, shown in the entry header
  [string] $Session = '',                          # short session/window id
  [int]    $TimeoutMs = 2000,                       # max time to wait for the lock
  [switch] $KeepSource                              # keep the source temp file (default: delete it)
)

$ErrorActionPreference = 'Stop'
if (-not (Test-Path -LiteralPath $Path)) { Write-Error "TLDR source not found: $Path"; exit 1 }

$trailDir = Join-Path $HOME '.claude\tldr-trail'
if (-not (Test-Path -LiteralPath $trailDir)) { New-Item -ItemType Directory -Path $trailDir -Force | Out-Null }

$now   = Get-Date
$day   = $now.ToString('yyyy-MM-dd')
$stamp = $now.ToString('HH:mm:ss')
$file  = Join-Path $trailDir "$day.md"
$lock  = Join-Path $trailDir '.lock'
$utf8  = New-Object System.Text.UTF8Encoding($false)   # UTF-8, no BOM (safe to append repeatedly)

# --- acquire lock (atomic directory create + bounded retry) ---
$acquired = $false
$deadline = $now.AddMilliseconds($TimeoutMs)
while ((Get-Date) -lt $deadline) {
  try { New-Item -ItemType Directory -Path $lock -ErrorAction Stop | Out-Null; $acquired = $true; break }
  catch { Start-Sleep -Milliseconds 50 }
}
if (-not $acquired) {
  # steal a stale lock left by a crashed window
  $li = Get-Item -LiteralPath $lock -ErrorAction SilentlyContinue
  if ($li -and ((Get-Date) - $li.CreationTime).TotalSeconds -gt 30) {
    Remove-Item -LiteralPath $lock -Recurse -Force -ErrorAction SilentlyContinue
    try { New-Item -ItemType Directory -Path $lock -ErrorAction Stop | Out-Null; $acquired = $true } catch {}
  }
}

try {
  # new-day file gets a title; otherwise compute real wall-clock since the last entry
  $delta = ''
  if (Test-Path -LiteralPath $file) {
    $mins = [math]::Round(((Get-Date) - (Get-Item -LiteralPath $file).LastWriteTime).TotalMinutes, 1)
    $delta = " * +$mins min since last"
  } else {
    [System.IO.File]::AppendAllText($file, "# TLDR trail - $day`r`n", $utf8)
  }

  $content = [System.IO.File]::ReadAllText($Path)   # UTF-8 w/ BOM auto-detect (robust in PS 5.1)
  $meta = @()
  if ($Project) { $meta += "proj: $Project" }
  if ($Session) { $meta += "session: $Session" }
  $metaLine = if ($meta.Count) { ' * ' + ($meta -join ' * ') } else { '' }
  if (-not $acquired) { $metaLine += ' * [!] wrote without lock (timeout)' }

  $entry = "`r`n---`r`n`r`n## $stamp$metaLine$delta`r`n`r`n$content`r`n"
  [System.IO.File]::AppendAllText($file, $entry, $utf8)
  Write-Output "Appended TLDR to $file"
}
finally {
  if ($acquired) { Remove-Item -LiteralPath $lock -Recurse -Force -ErrorAction SilentlyContinue }
}

if (-not $KeepSource) { Remove-Item -LiteralPath $Path -Force -ErrorAction SilentlyContinue }
