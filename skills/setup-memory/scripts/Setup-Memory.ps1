<#
.SYNOPSIS
  Set up version-controlled, per-project Claude memory (memory-in-repo) with a junction.

.DESCRIPTION
  Moves Claude's per-project memory from ~/.claude/projects/<slug>/memory into the repo at
  <ProjectPath>/memories/repo and links it back with a directory junction, so the memory is
  committed, team-shared, and token-efficient. Idempotent. No admin needed (junction, not symlink).

  Generic + publishable: no hardcoded user/org/project values.

.PARAMETER ProjectPath
  Repo root to attach memory to. Defaults to the current directory.

.PARAMETER ClaudeHome
  Claude home. Defaults to $env:USERPROFILE\.claude.

.PARAMETER Force
  Re-write the seeded MEMORY.md / template / README even if they already exist.

.EXAMPLE
  .\Setup-Memory.ps1 -ProjectPath C:\Projects\MyApp
  .\Setup-Memory.ps1 -WhatIf
#>
[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [string]$ProjectPath = (Get-Location).Path,
    [string]$ClaudeHome  = (Join-Path $env:USERPROFILE '.claude'),
    [switch]$Force
)

$ErrorActionPreference = 'Stop'

function Get-ProjectSlug {
    param([string]$FullPath)
    # Match the harness convention: lowercase the drive letter, then map : \ / . _ and space -> -
    $p = $FullPath.TrimEnd('\', '/')
    if ($p.Length -ge 1) { $p = $p.Substring(0, 1).ToLower() + $p.Substring(1) }
    return ($p -replace '[:\\/._ ]', '-')
}

# ---- resolve paths --------------------------------------------------------
$ProjectPath = (Resolve-Path -LiteralPath $ProjectPath).Path
$slug        = Get-ProjectSlug $ProjectPath
$memRepo     = Join-Path $ProjectPath 'memories\repo'
$projDir     = Join-Path $ClaudeHome  ("projects\" + $slug)
$link        = Join-Path $projDir 'memory'

Write-Host "Project   : $ProjectPath"      -ForegroundColor Cyan
Write-Host "Slug      : $slug"
Write-Host "Mem repo  : $memRepo"
Write-Host "Junction  : $link"

# If a project dir with the capital-drive variant already exists, prefer it (harness has used both).
if (-not (Test-Path $projDir)) {
    $altSlug = $slug.Substring(0, 1).ToUpper() + $slug.Substring(1)
    $altDir  = Join-Path $ClaudeHome ("projects\" + $altSlug)
    if (Test-Path $altDir) { $projDir = $altDir; $link = Join-Path $projDir 'memory'; Write-Host "  (using existing slug variant: $altSlug)" -ForegroundColor DarkGray }
}

# ---- 1. ensure repo memory dir -------------------------------------------
if (-not (Test-Path $memRepo)) {
    if ($PSCmdlet.ShouldProcess($memRepo, 'create memories/repo')) {
        New-Item -ItemType Directory -Force -Path $memRepo | Out-Null
        Write-Host "  [+] created $memRepo" -ForegroundColor Green
    }
}

# ---- 2. migrate an existing REAL memory folder into the repo --------------
$migrated = 0
if (Test-Path $link) {
    $item = Get-Item -LiteralPath $link -Force
    $isReparse = ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0
    if ($isReparse) {
        $target = (Get-Item -LiteralPath $link -Force).Target
        Write-Host "  [=] junction already exists -> $target" -ForegroundColor DarkGray
        if ($target -and ((Resolve-Path -LiteralPath $target -ErrorAction SilentlyContinue).Path -ne $memRepo)) {
            Write-Host "  [!] junction points elsewhere; re-run with -Force to re-point" -ForegroundColor Yellow
            if ($Force -and $PSCmdlet.ShouldProcess($link, 're-point junction')) {
                (Get-Item -LiteralPath $link -Force).Delete()
                New-Item -ItemType Junction -Path $link -Target $memRepo | Out-Null
                Write-Host "  [~] re-pointed junction -> $memRepo" -ForegroundColor Green
            }
        }
    }
    else {
        # real folder -> migrate files then remove
        Get-ChildItem -LiteralPath $link -Force -File -ErrorAction SilentlyContinue | ForEach-Object {
            $dest = Join-Path $memRepo $_.Name
            if ((Test-Path $dest) -and ((Get-Item $dest).LastWriteTime -ge $_.LastWriteTime)) {
                Write-Host "      skip (dest newer): $($_.Name)" -ForegroundColor DarkGray
            }
            elseif ($PSCmdlet.ShouldProcess($_.FullName, "move -> $memRepo")) {
                Move-Item -LiteralPath $_.FullName -Destination $dest -Force
                $migrated++
            }
        }
        # also migrate any subfolders verbatim
        Get-ChildItem -LiteralPath $link -Force -Directory -ErrorAction SilentlyContinue | ForEach-Object {
            $dest = Join-Path $memRepo $_.Name
            if (-not (Test-Path $dest) -and $PSCmdlet.ShouldProcess($_.FullName, "move dir -> $memRepo")) {
                Move-Item -LiteralPath $_.FullName -Destination $dest -Force
            }
        }
        if ($PSCmdlet.ShouldProcess($link, 'remove real folder + create junction')) {
            Remove-Item -LiteralPath $link -Recurse -Force
            New-Item -ItemType Directory -Force -Path $projDir | Out-Null
            New-Item -ItemType Junction -Path $link -Target $memRepo | Out-Null
            Write-Host "  [~] migrated $migrated file(s), replaced folder with junction" -ForegroundColor Green
        }
    }
}
else {
    if ($PSCmdlet.ShouldProcess($link, 'create junction')) {
        New-Item -ItemType Directory -Force -Path $projDir | Out-Null
        New-Item -ItemType Junction -Path $link -Target $memRepo | Out-Null
        Write-Host "  [+] created junction -> $memRepo" -ForegroundColor Green
    }
}

# ---- 3. seed MEMORY.md / template / README -------------------------------
$assets = Join-Path (Split-Path -Parent $PSScriptRoot) 'assets'
function Seed($name, $destName) {
    $src  = Join-Path $assets $name
    $dest = Join-Path $memRepo $destName
    if ((Test-Path $src) -and ($Force -or -not (Test-Path $dest))) {
        if ($PSCmdlet.ShouldProcess($dest, "seed $destName")) {
            Copy-Item -LiteralPath $src -Destination $dest -Force
            Write-Host "  [+] seeded $destName" -ForegroundColor Green
        }
    }
}
Seed 'MEMORY.template.md'  'MEMORY.md'
Seed '_TEMPLATE.memory.md' '_TEMPLATE.memory.md'
Seed 'README.md'           'README.md'

Write-Host ""
Write-Host "Done. Memory for '$slug' now lives in the repo at memories\repo and is junctioned into ~/.claude." -ForegroundColor Cyan
Write-Host "Commit the 'memories/' folder to share it with the team (keep it secret-free)." -ForegroundColor DarkGray
