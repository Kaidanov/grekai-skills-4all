# Stop-hook footer: model used, session cost (API-equivalent), context-window usage.
# Reads the hook JSON from stdin ({transcript_path, session_id, ...}), aggregates token
# usage from the session transcript (+ any subagent transcripts), and emits a one-line
# footer as {"systemMessage": "..."} for Claude Code to surface to the user.
#
# Pricing (per MTok): Opus 4.8 in $5 / out $25 / cache-read $0.50 / cache-write 5m $6.25 /
# cache-write 1h $10. 1M context = no long-context premium. Sonnet/Haiku tiers below.
# ASCII-only output: PowerShell 5.1 stdout corrupts non-ASCII, which Claude Code would
# then surface as mojibake. Totals are de-duplicated by message id (the transcript logs
# each assistant message on more than one line), and the label is the dominant model by
# output tokens (Claude Code logs background haiku calls into the same transcript).
$ErrorActionPreference = 'SilentlyContinue'

$PRICES = @{
    'opus'   = @{ in = 5.0; out = 25.0; cr = 0.5; cw5 = 6.25; cw1 = 10.0 }
    'sonnet' = @{ in = 3.0; out = 15.0; cr = 0.3; cw5 = 3.75; cw1 = 6.0  }
    'haiku'  = @{ in = 1.0; out = 5.0;  cr = 0.1; cw5 = 1.25; cw1 = 2.0  }
}
function Get-Price($label) {
    foreach ($k in $PRICES.Keys) { if ($label -like "*$k*") { return $PRICES[$k] } }
    return $PRICES['opus']   # default to Opus pricing
}
function Get-Num($obj, $name) {
    if ($obj -and ($obj.PSObject.Properties.Name -contains $name)) { return [double]$obj.$name }
    return 0
}
function Format-Tokens([double]$n) {
    if ($n -ge 1e6) { return ('{0:0.##}M' -f ($n / 1e6)) }
    if ($n -ge 1e3) { return ('{0:0.#}K'  -f ($n / 1e3)) }
    return ('{0:0}' -f $n)
}
function To-Label($model) {
    if (-not $model) { return 'unknown' }
    $s = $model -replace '^claude-', ''
    $s = $s -replace '-\d{8}$', ''      # strip trailing -YYYYMMDD snapshot date
    $s = $s -replace '-(\d+)$', '.$1'   # opus-4-8 -> opus-4.8 ; haiku-4-5 -> haiku-4.5
    return $s
}

# --- locate the transcript --------------------------------------------------
$raw = [Console]::In.ReadToEnd()
$transcript = $null; $sessionId = $null
if ($raw) {
    try { $h = $raw | ConvertFrom-Json; $transcript = $h.transcript_path; $sessionId = $h.session_id } catch {}
}
$projDir = if ($transcript) { Split-Path -Parent $transcript } else { $PSScriptRoot }
if ((-not $transcript) -or (-not (Test-Path $transcript))) {
    $latest = Get-ChildItem $projDir -Filter *.jsonl -File | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if ($latest) { $transcript = $latest.FullName }
}
if ((-not $transcript) -or (-not (Test-Path $transcript))) { exit 0 }

# Include subagent transcripts for this session if present (they cost tokens too).
$files = @($transcript)
if ($sessionId) {
    $subDir = Join-Path $projDir "$sessionId\subagents"
    if (Test-Path $subDir) { $files += (Get-ChildItem $subDir -Recurse -Filter *.jsonl -File).FullName }
}

# --- aggregate (de-duplicated by message id) --------------------------------
$seen = New-Object 'System.Collections.Generic.HashSet[string]'
$modelOut = @{}            # label -> output tokens, to pick the dominant model
$cost = 0.0; $total = 0.0; $lastCtx = 0
foreach ($f in $files) {
    foreach ($line in [System.IO.File]::ReadLines($f)) {
        if ($line -notlike '*"usage"*') { continue }
        try { $o = $line | ConvertFrom-Json } catch { continue }
        $u = $o.message.usage
        if (-not $u) { continue }

        # de-dupe: the same assistant message is written on multiple transcript lines
        if ($o.message -and ($o.message.PSObject.Properties.Name -contains 'id') -and $o.message.id) {
            if (-not $seen.Add([string]$o.message.id)) { continue }
        }

        $label = To-Label $o.message.model
        $p = Get-Price $label

        $inTok  = Get-Num $u 'input_tokens'
        $outTok = Get-Num $u 'output_tokens'
        $crTok  = Get-Num $u 'cache_read_input_tokens'
        $ccTok  = Get-Num $u 'cache_creation_input_tokens'
        $c5 = 0; $c1 = 0
        if (($u.PSObject.Properties.Name -contains 'cache_creation') -and $u.cache_creation) {
            $c5 = Get-Num $u.cache_creation 'ephemeral_5m_input_tokens'
            $c1 = Get-Num $u.cache_creation 'ephemeral_1h_input_tokens'
        }
        if (($c5 + $c1) -le 0 -and $ccTok -gt 0) { $c1 = $ccTok }   # fallback: assume 1h tier (Claude Code default)

        $cost  += ($inTok * $p.in + $outTok * $p.out + $crTok * $p.cr + $c5 * $p.cw5 + $c1 * $p.cw1) / 1e6
        $total += $inTok + $outTok + $crTok + $c5 + $c1
        if ($label -ne 'unknown') { $modelOut[$label] = (Get-Num ([pscustomobject]$modelOut) $label) + $outTok }

        # Context window = most recent main-transcript request's input footprint.
        if ($f -eq $transcript) {
            $ctx = $inTok + $crTok + $ccTok
            if ($ctx -gt 0) { $lastCtx = $ctx }
        }
    }
}

# --- render (ASCII only) ----------------------------------------------------
$primary = 'unknown'
if ($modelOut.Count -gt 0) {
    $primary = ($modelOut.GetEnumerator() | Sort-Object Value -Descending | Select-Object -First 1).Key
}
$ctxWin  = 1000000
$ctxPct  = if ($lastCtx -gt 0) { [math]::Round($lastCtx / $ctxWin * 100, 0) } else { 0 }
$ctxFree = [math]::Round((100 - $ctxPct), 0)

$line = ('model {0} | session {1} tok ~ ${2:0.00} (API-equiv) | context {3}/1M ({4}% free) | /usage for plan limits' -f `
    $primary, (Format-Tokens $total), $cost, (Format-Tokens $lastCtx), $ctxFree)

(@{ systemMessage = $line } | ConvertTo-Json -Compress)
exit 0
