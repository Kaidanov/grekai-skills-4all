<#
.SYNOPSIS
  Claude Code Stop hook: append a compact per-turn heartbeat to the global daily TLDR trail.

.DESCRIPTION
  Fires when the assistant finishes a turn (even without /tldr). Reads the hook JSON from
  stdin (cwd, transcript_path, session_id), derives project@branch, extracts a one-line gist
  of the assistant's last message, and appends a single line to ~/.claude/tldr-trail/<date>.md
  via Append-TldrTrail.ps1 (shared lock). NEVER throws — always exits 0 so it can't break a turn.
  The gap between consecutive heartbeats approximates each round's wall-clock duration.
#>
try {
  # Read the hook JSON from stdin with a hard 3s cap so a missing-EOF stdin can NEVER hang
  # turn-end. Real hooks pipe the JSON and close stdin (returns instantly); the cap only
  # matters for odd/interactive invocations.
  $raw = ''
  if ([Console]::IsInputRedirected) {
    try { $task = [Console]::In.ReadToEndAsync(); if ($task.Wait(3000)) { $raw = $task.Result } } catch {}
  }
  $j = $null
  if ($raw) { try { $j = $raw | ConvertFrom-Json } catch {} }

  $cwd = if ($j -and $j.cwd) { $j.cwd } else { (Get-Location).Path }
  $tp  = if ($j) { [string]$j.transcript_path } else { '' }
  $sid = ''
  if ($j -and $j.session_id) { $s = [string]$j.session_id; $sid = $s.Substring(0, [Math]::Min(8, $s.Length)) }

  $proj = Split-Path $cwd -Leaf
  $branch = ''
  try { $b = (git -C $cwd rev-parse --abbrev-ref HEAD 2>$null); if ($LASTEXITCODE -eq 0 -and $b) { $branch = $b.Trim() } } catch {}
  $projLabel = if ($branch) { "$proj@$branch" } else { $proj }

  # best-effort gist: first line of the assistant's last text message
  $gist = '(turn)'
  try {
    if ($tp -and (Test-Path -LiteralPath $tp)) {
      $tail = Get-Content -LiteralPath $tp -Tail 80 -ErrorAction Stop
      for ($i = $tail.Count - 1; $i -ge 0; $i--) {
        $o = $null; try { $o = $tail[$i] | ConvertFrom-Json } catch { continue }
        if ($o.type -eq 'assistant' -and $o.message -and $o.message.content) {
          $txt = ($o.message.content | Where-Object { $_.type -eq 'text' } | Select-Object -First 1).text
          if ($txt) {
            $gist = ($txt -split "`n" | Where-Object { $_.Trim() } | Select-Object -First 1).Trim()
            if ($gist.Length -gt 120) { $gist = $gist.Substring(0, 120) + [char]0x2026 }
            break
          }
        }
      }
    }
  } catch {}

  $script = Join-Path $PSScriptRoot 'Append-TldrTrail.ps1'
  & $script -Text $gist -Compact -Scope global -Project $projLabel -Session $sid -BaseDir $cwd | Out-Null
} catch {}
exit 0
