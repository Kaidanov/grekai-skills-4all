# intake-issue-image.ps1
# Saves screenshots to client/docs/issue-images/ with auto-naming (I1.png, I2.png, ...).
#
# Two modes:
#   HOOK MODE   - called by Claude Code UserPromptSubmit hook (JSON piped to stdin).
#                 Reads the latest transcript entry, extracts any image attachments,
#                 saves them and prints markdown refs so Claude echoes them back.
#   MANUAL MODE - run directly: saves the current clipboard image.
#                 Usage: powershell -File .claude\scripts\intake-issue-image.ps1
#                 Optional: powershell -File ... -IssueId 4   <- forces I4.png

param(
    [int]$IssueId = 0          # 0 = auto-number from next available slot
)

Set-StrictMode -Off

# ── helpers ──────────────────────────────────────────────────────────────────

function Get-IssueImagesDir {
    $root = Split-Path $PSScriptRoot -Parent | Split-Path -Parent
    Join-Path $root "client\docs\issue-images"
}

function Get-NextIssueNumber {
    param([string]$dir)
    if (-not (Test-Path $dir)) { return 1 }
    $taken = Get-ChildItem $dir -File |
        Where-Object { $_.Name -match '^I(\d+)' } |
        ForEach-Object { [int]$Matches[1] } |
        Sort-Object -Descending
    if ($taken) { return $taken[0] + 1 } else { return 1 }
}

function Save-Bytes {
    param([string]$dest, [byte[]]$bytes)
    $dir = Split-Path $dest -Parent
    if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Force $dir | Out-Null }
    [System.IO.File]::WriteAllBytes($dest, $bytes)
}

function Print-Saved {
    param([string[]]$names, [string]$dir)
    if ($names.Count -eq 0) { return }
    Write-Host "`n[intake-issue-image] Saved $($names.Count) image(s) to client/docs/issue-images/:"
    foreach ($n in $names) {
        Write-Host "  $n"
        Write-Host "  Markdown: ![$n](./issue-images/$n)"
    }
    Write-Host ""
}

# ── detect mode ───────────────────────────────────────────────────────────────

$hook_data  = $null
$hook_mode  = $false

# Claude Code pipes a JSON object to stdin for every hook event.
# We peek at stdin: if it has data and parses as JSON with transcript_path, we're in hook mode.
try {
    # Give stdin a short window - if nothing arrives, skip
    if ([Console]::In.Peek() -ne -1) {
        $raw = [Console]::In.ReadToEnd().Trim()
        if ($raw) {
            $hook_data = $raw | ConvertFrom-Json -ErrorAction Stop
            if ($hook_data.PSObject.Properties['transcript_path']) {
                $hook_mode = $true
            }
        }
    }
} catch {}

# ── HOOK MODE: extract images from transcript ─────────────────────────────────

if ($hook_mode) {
    $tp = $hook_data.transcript_path
    if (-not $tp -or -not (Test-Path $tp)) { exit 0 }

    # Read JSONL, find the LAST user message
    $lines = [System.IO.File]::ReadAllLines($tp, [System.Text.Encoding]::UTF8)
    $last_user = $null
    for ($i = $lines.Count - 1; $i -ge 0; $i--) {
        $line = $lines[$i].Trim()
        if (-not $line) { continue }
        try {
            $obj = $line | ConvertFrom-Json -ErrorAction Stop
            # Claude Code transcript format: { type:"user", message:{ role:"user", content:[...] } }
            # Fallback: { role:"user", content:[...] }
            $is_user = ($obj.type -eq 'user') -or ($obj.role -eq 'user') -or `
                       ($obj.PSObject.Properties['message'] -and $obj.message.role -eq 'user')
            if ($is_user) { $last_user = $obj; break }
        } catch {}
    }

    if (-not $last_user) { exit 0 }

    # Content may be at .content or .message.content
    $content = if ($last_user.PSObject.Properties['message'] -and $last_user.message.content) {
        $last_user.message.content
    } elseif ($last_user.PSObject.Properties['content']) {
        $last_user.content
    } else { @() }
    $image_blocks = @($content | Where-Object { $_.type -eq 'image' })
    if ($image_blocks.Count -eq 0) { exit 0 }

    $dir = Get-IssueImagesDir
    $n = if ($IssueId -gt 0) { $IssueId } else { Get-NextIssueNumber $dir }
    $saved = @()

    foreach ($blk in $image_blocks) {
        $dest = Join-Path $dir "I${n}.png"
        $src = $blk.source

        try {
            if ($src.type -eq 'base64' -and $src.data) {
                $bytes = [Convert]::FromBase64String($src.data)
                Save-Bytes $dest $bytes
                $saved += "I${n}.png"
                $n++
            } elseif ($src.type -eq 'file' -and $src.PSObject.Properties['path'] -and (Test-Path $src.path)) {
                Copy-Item $src.path $dest -Force
                $saved += "I${n}.png"
                $n++
            } elseif ($src.PSObject.Properties['url'] -and $src.url -match '^data:image') {
                # data-URI fallback
                $b64 = $src.url -replace '^data:image/[^;]+;base64,', ''
                $bytes = [Convert]::FromBase64String($b64)
                Save-Bytes $dest $bytes
                $saved += "I${n}.png"
                $n++
            }
        } catch { continue }
    }

    Print-Saved $saved $dir
    exit 0
}

# ── MANUAL MODE: save clipboard image ─────────────────────────────────────────

Add-Type -AssemblyName System.Windows.Forms, System.Drawing

$img = [System.Windows.Forms.Clipboard]::GetImage()
if (-not $img) {
    Write-Host "[intake-issue-image] No image found in clipboard. Copy a screenshot first."
    exit 1
}

$dir = Get-IssueImagesDir
$n = if ($IssueId -gt 0) { $IssueId } else { Get-NextIssueNumber $dir }
$dest = Join-Path $dir "I${n}.png"

if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Force $dir | Out-Null }
$img.Save($dest, [System.Drawing.Imaging.ImageFormat]::Png)
$img.Dispose()

$name = "I${n}.png"
Write-Host ""
Write-Host "[intake-issue-image] Saved: $dest"
Write-Host "Markdown:  ![$name](./issue-images/$name)"
Write-Host "Reference: - Screenshot: ./issue-images/$name"
Write-Host ""
