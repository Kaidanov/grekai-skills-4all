# analyze-history.ps1 — one-off historical usage analysis from Claude Code transcripts.
# Scans ~/.claude/projects/**/*.jsonl, counts Skill / SlashCommand / Task(subagent_type)
# tool_use blocks, and prints a ranked top-list per category + the timestamp date range.
# Read-only. ASCII output. KISS — no external deps.
param([string]$ProjectsDir = (Join-Path $env:USERPROFILE '.claude\projects'))
$ErrorActionPreference = 'SilentlyContinue'

$skill = @{}; $slash = @{}; $agent = @{}; $mcp = @{}
$minTs = $null; $maxTs = $null; $lines = 0; $fileCount = 0

function Bump($t, $k) { if (-not $k) { return }; $t[$k] = ([int]$t[$k]) + 1 }

$files = Get-ChildItem $ProjectsDir -Recurse -Filter *.jsonl -File
foreach ($f in $files) {
    $fileCount++
    foreach ($line in [System.IO.File]::ReadLines($f.FullName)) {
        if ($line -notlike '*tool_use*' -and $line -notlike '*command-name*') {
            # still track timestamp range cheaply
            if ($line -like '*"timestamp"*') {
                try { $o = $line | ConvertFrom-Json } catch { continue }
                $ts = [string]$o.timestamp
                if ($ts) { if (-not $minTs -or $ts -lt $minTs) { $minTs = $ts }; if (-not $maxTs -or $ts -gt $maxTs) { $maxTs = $ts } }
            }
            continue
        }
        $lines++
        try { $o = $line | ConvertFrom-Json } catch { continue }
        $ts = [string]$o.timestamp
        if ($ts) { if (-not $minTs -or $ts -lt $minTs) { $minTs = $ts }; if (-not $maxTs -or $ts -gt $maxTs) { $maxTs = $ts } }

        # Slash commands appear as user messages wrapped in <command-name>/foo</command-name>
        $content = $o.message.content
        if ($content -is [string] -and $content -match '<command-name>\s*/?([\w:-]+)') { Bump $slash $Matches[1] }

        if ($content -isnot [System.Array]) { continue }
        foreach ($b in $content) {
            if ($b.type -ne 'tool_use') { continue }
            switch ($b.name) {
                'Skill'         { $s = [string]$b.input.skill; if (-not $s) { $s = [string]$b.input.command }; Bump $skill $s }
                'Agent'         { Bump $agent ([string]$b.input.subagent_type) }   # subagent dispatch
                'Task'          { Bump $agent ([string]$b.input.subagent_type) }   # legacy name
                'SlashCommand'  { Bump $slash ([string]$b.input.command) }
            }
            if ($b.name -like 'mcp__*') { Bump $mcp ([string]$b.name) }
        }
    }
}

function Show($title, $table, $top) {
    "`n=== $title (top $top) ==="
    $table.GetEnumerator() | Where-Object { $_.Key } | Sort-Object Value -Descending |
        Select-Object -First $top | ForEach-Object { '{0,5}  {1}' -f $_.Value, $_.Key }
}

"Files scanned : $fileCount"
"Tool/cmd lines: $lines"
"Date range    : $minTs .. $maxTs"
Show 'SKILL invocations'        $skill 15
Show 'SLASH commands'           $slash 15
Show 'SUBAGENTS (subagent_type)' $agent 15
Show 'MCP tools'                $mcp 15
