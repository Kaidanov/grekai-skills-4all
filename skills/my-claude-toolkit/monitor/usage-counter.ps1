# usage-counter.ps1 — PostToolUse hook: append each Skill / SlashCommand / Agent
# invocation to a CSV so usage can be ranked over time. KISS, read-only except for
# its own append-only CSV. ASCII output, never blocks the tool (always exit 0).
#
# Claude Code pipes a JSON object to stdin for the PostToolUse event, including
# tool_name and tool_input. We log only the three categories we care about and
# ignore everything else (Read/Edit/Bash/etc.) to keep the CSV signal-dense.
$ErrorActionPreference = 'SilentlyContinue'

$csv = Join-Path $env:USERPROFILE '.claude\usage-log.csv'

try { $h = [Console]::In.ReadToEnd() | ConvertFrom-Json } catch { exit 0 }
if (-not $h) { exit 0 }

$tool = [string]$h.tool_name
$in   = $h.tool_input
$cat  = $null; $name = $null

switch ($tool) {
    'Skill'        { $cat = 'skill';   $name = [string]$in.skill;        if (-not $name) { $name = [string]$in.command } }
    'Agent'        { $cat = 'agent';   $name = [string]$in.subagent_type }
    'Task'         { $cat = 'agent';   $name = [string]$in.subagent_type }   # legacy name
    'SlashCommand' { $cat = 'command'; $name = [string]$in.command }
}
if (-not $cat -or -not $name) { exit 0 }

# CSV-safe: strip commas/quotes/newlines from the name field.
$name = ($name -replace '[",\r\n]', ' ').Trim()
if ($name.Length -gt 80) { $name = $name.Substring(0, 80) }

$dir = Split-Path $csv -Parent
if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Force $dir | Out-Null }
if (-not (Test-Path $csv)) { Set-Content -Path $csv -Value 'timestamp,session,category,name' -Encoding ASCII }

$row = '{0},{1},{2},{3}' -f (Get-Date -Format 'o'), ([string]$h.session_id), $cat, $name
Add-Content -Path $csv -Value $row -Encoding ASCII
exit 0
