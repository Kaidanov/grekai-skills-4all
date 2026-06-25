<#
.SYNOPSIS
  Append a TLDR report (or a one-line heartbeat) to a daily trail log, cross-process safe.

.DESCRIPTION
  Writes to  <trail-dir>\<YYYY-MM-DD>.md  so windows accumulate one scannable log per day.
  Trail location:
    -Scope global  (default) -> $HOME\.claude\tldr-trail
    -Scope project           -> <git repo root of -BaseDir, else -BaseDir>\.claude\tldr-trail
    -TrailDir <path>         -> explicit override (wins over -Scope)
  Content comes from -Path <file> (full report) or -Text <string> (inline; used by the hook).
  -Compact writes a single bullet line instead of a full block (for per-turn heartbeats).

  Cross-process safe: one atomic mkdir lock with a bounded retry (default 2s); if two windows
  finish together the second waits a few ms then appends. A stale lock (>30s, crashed window)
  is auto-stolen. UTF-8 no-BOM. Each entry stamps real wall-clock since the previous entry.
  Emits the trail file path on success (so callers can render a clickable link).

.EXAMPLE
  & Append-TldrTrail.ps1 -Path .\tldr.md -Project "m4n.map@feature-x" -Session 7be71b0
.EXAMPLE
  & Append-TldrTrail.ps1 -Text "fixed the lock bug" -Compact -Project repo@main -Session abcd1234
.EXAMPLE
  & Append-TldrTrail.ps1 -Path .\tldr.md -Scope project   # keep the trail inside the repo
#>
[CmdletBinding(DefaultParameterSetName = 'Path')]
param(
  [Parameter(ParameterSetName = 'Path', Mandatory = $true)] [string] $Path,   # file with the TLDR markdown
  [Parameter(ParameterSetName = 'Text', Mandatory = $true)] [string] $Text,   # inline content
  [ValidateSet('global', 'project')] [string] $Scope = 'global',
  [string] $TrailDir = '',                          # explicit dir override (wins over -Scope)
  [string] $BaseDir  = '',                          # project-root base for -Scope project (default: cwd)
  [switch] $Compact,                                # one-line entry instead of a full block
  [string] $Project = '',                           # repo@branch label in the entry header
  [string] $Session = '',                           # short session/window id
  [int]    $TimeoutMs = 2000,
  [switch] $KeepSource                              # keep the source temp file (default: delete it)
)

$ErrorActionPreference = 'Stop'

# --- resolve trail directory ---
if ($TrailDir) {
  $trailDir = $TrailDir
} elseif ($Scope -eq 'project') {
  $base = if ($BaseDir) { $BaseDir } else { (Get-Location).Path }
  try { $root = (git -C $base rev-parse --show-toplevel 2>$null); if ($LASTEXITCODE -eq 0 -and $root) { $base = $root.Trim() } } catch {}
  $trailDir = Join-Path $base '.claude\tldr-trail'
} else {
  $trailDir = Join-Path $HOME '.claude\tldr-trail'
}
if (-not (Test-Path -LiteralPath $trailDir)) { New-Item -ItemType Directory -Path $trailDir -Force | Out-Null }

# --- content ---
if ($PSCmdlet.ParameterSetName -eq 'Text') {
  $content = $Text
} else {
  if (-not (Test-Path -LiteralPath $Path)) { Write-Error "TLDR source not found: $Path"; exit 1 }
  $content = [System.IO.File]::ReadAllText($Path)   # UTF-8 w/ BOM auto-detect (robust in PS 5.1)
}

$now   = Get-Date
$day   = $now.ToString('yyyy-MM-dd')
$stamp = $now.ToString('HH:mm:ss')
$file  = Join-Path $trailDir "$day.md"
$lock  = Join-Path $trailDir '.lock'
$utf8  = New-Object System.Text.UTF8Encoding($false)

# --- acquire lock (atomic directory create + bounded retry) ---
$acquired = $false
$deadline = $now.AddMilliseconds($TimeoutMs)
while ((Get-Date) -lt $deadline) {
  try { New-Item -ItemType Directory -Path $lock -ErrorAction Stop | Out-Null; $acquired = $true; break }
  catch { Start-Sleep -Milliseconds 50 }
}
if (-not $acquired) {
  $li = Get-Item -LiteralPath $lock -ErrorAction SilentlyContinue
  if ($li -and ((Get-Date) - $li.CreationTime).TotalSeconds -gt 30) {
    Remove-Item -LiteralPath $lock -Recurse -Force -ErrorAction SilentlyContinue
    try { New-Item -ItemType Directory -Path $lock -ErrorAction Stop | Out-Null; $acquired = $true } catch {}
  }
}

try {
  $delta = ''
  if (Test-Path -LiteralPath $file) {
    $mins = [math]::Round(((Get-Date) - (Get-Item -LiteralPath $file).LastWriteTime).TotalMinutes, 1)
    $delta = " * +$mins min since last"
  } else {
    [System.IO.File]::AppendAllText($file, "# TLDR trail - $day`r`n", $utf8)
  }

  $meta = @()
  if ($Project) { $meta += "proj: $Project" }
  if ($Session) { $meta += "session: $Session" }
  $metaLine = if ($meta.Count) { ' * ' + ($meta -join ' * ') } else { '' }
  if (-not $acquired) { $metaLine += ' * [!] wrote without lock (timeout)' }

  if ($Compact) {
    $oneLine = ($content -replace '\s*\r?\n\s*', ' ').Trim()
    $entry = "- $stamp$metaLine$delta - $oneLine`r`n"
  } else {
    $entry = "`r`n---`r`n`r`n## $stamp$metaLine$delta`r`n`r`n$content`r`n"
  }
  [System.IO.File]::AppendAllText($file, $entry, $utf8)
  Write-Output $file
}
finally {
  if ($acquired) { Remove-Item -LiteralPath $lock -Recurse -Force -ErrorAction SilentlyContinue }
}

if ($PSCmdlet.ParameterSetName -eq 'Path' -and -not $KeepSource) {
  Remove-Item -LiteralPath $Path -Force -ErrorAction SilentlyContinue
}
