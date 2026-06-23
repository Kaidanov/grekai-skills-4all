<#
.SYNOPSIS
  Create (or repair) a git worktree that materializes ONLY selected folders of a
  large solution via cone-mode sparse-checkout. Optimized for pulling one
  sub-area (e.g. WebAPI + docs + tests) of a monorepo into its own folder
  without checking out the whole tree.

.DESCRIPTION
  - Auto-detects the changed top-level folders of a branch vs a base branch when
    -Folders is omitted (diff over the merge-base, directories only).
  - Idempotent: re-running against an existing worktree just re-applies the
    sparse set. Use -Force to drop and recreate.
  - Prints a fit report: file counts, size, branch tip, and the AssemblyVersion
    stamp(s) found under the materialized folders (so you can confirm the
    intended release, e.g. 1.2.3).

.EXAMPLE
  .\New-SubsetWorktree.ps1 -RepoPath C:\Projects\MyApp `
     -Branch feature/1234-api-docs `
     -DestPath C:\Projects\MyApp_1.2.3_webapi `
     -Folders WebApi,WebApiDocs,UnitTests,IntegrationTests `
     -ExpectVersion 1.2.3

.EXAMPLE
  # Auto-detect the changed folders vs origin/dev:
  .\New-SubsetWorktree.ps1 -RepoPath C:\Projects\MyApp `
     -Branch feature/1234-api-docs `
     -DestPath C:\Projects\MyApp_subset
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)] [string]   $RepoPath,
    [Parameter(Mandatory)] [string]   $Branch,
    [Parameter(Mandatory)] [string]   $DestPath,
    [string[]] $Folders,
    [string]   $BaseBranch    = 'origin/dev',
    [string]   $ExpectVersion,
    [switch]   $Force
)

$ErrorActionPreference = 'Stop'

function Resolve-PathSafe { param($p) try { (Resolve-Path $p -ErrorAction Stop).Path } catch { $p } }

function GitC { param([Parameter(ValueFromRemainingArguments)][string[]]$a)
    $out = & git.exe -C $RepoPath @a 2>&1
    if ($LASTEXITCODE -ne 0) { throw "git $($a -join ' ') failed:`n$out" }
    return $out
}

# --- validate repo + branch ---------------------------------------------------
if (-not (Test-Path $RepoPath)) { throw "RepoPath not found: $RepoPath" }
$null = GitC rev-parse --is-inside-work-tree
& git.exe -C $RepoPath rev-parse --verify --quiet "$Branch^{commit}" | Out-Null
if ($LASTEXITCODE -ne 0) { throw "Branch '$Branch' not found in $RepoPath" }

# --- auto-detect folders if not supplied --------------------------------------
if (-not $Folders -or $Folders.Count -eq 0) {
    Write-Host "No -Folders given; auto-detecting changed top-level dirs vs $BaseBranch ..." -ForegroundColor Cyan
    $base = (GitC merge-base $Branch $BaseBranch).Trim()
    $changed  = GitC diff --name-only $base $Branch
    $treeDirs = GitC ls-tree -d --name-only $Branch          # top-level dirs only
    $Folders  = $changed |
        ForEach-Object { ($_ -split '/')[0] } |
        Sort-Object -Unique |
        Where-Object { $treeDirs -contains $_ }
    if (-not $Folders) { throw "Auto-detect found no changed folders." }
    Write-Host ("  -> " + ($Folders -join ', ')) -ForegroundColor Cyan
}

# --- handle existing worktree / dest ------------------------------------------
$norm = { param($p) (Resolve-PathSafe $p).Replace('\','/').TrimEnd('/').ToLower() }
$destNorm = & $norm $DestPath
$registered = $false
foreach ($line in (& git.exe -C $RepoPath worktree list --porcelain)) {
    if ($line -like 'worktree *' -and (& $norm ($line -replace '^worktree ','')) -eq $destNorm) {
        $registered = $true; break
    }
}
if (Test-Path $DestPath) {
    if ($Force) {
        Write-Host "Removing existing worktree at $DestPath ..." -ForegroundColor Yellow
        & git -C $RepoPath worktree remove --force $DestPath 2>$null
        if (Test-Path $DestPath) { Remove-Item -Recurse -Force $DestPath }
    } elseif (-not $registered) {
        throw "DestPath exists and is not a registered worktree. Use -Force to overwrite: $DestPath"
    }
}

# --- create worktree (skeleton) -----------------------------------------------
if (-not (Test-Path $DestPath)) {
    Write-Host "Creating worktree -> $DestPath (branch $Branch)" -ForegroundColor Green
    & git -C $RepoPath worktree add --no-checkout $DestPath $Branch
    if ($LASTEXITCODE -ne 0) { throw "worktree add failed" }
}

# --- configure sparse-checkout + populate -------------------------------------
& git -C $DestPath sparse-checkout init --cone | Out-Null
& git -C $DestPath sparse-checkout set @Folders
& git -C $DestPath checkout 2>&1 | Out-Null

# --- fit report ----------------------------------------------------------------
$tip = (& git -C $DestPath rev-parse --short HEAD).Trim()
Write-Host "`n=== Subset worktree ready ===" -ForegroundColor Green
Write-Host ("  Path   : {0}" -f $DestPath)
Write-Host ("  Branch : {0} @ {1}" -f $Branch, $tip)
foreach ($f in $Folders) {
    $n = (Get-ChildItem -Recurse -File -ErrorAction SilentlyContinue (Join-Path $DestPath $f) | Measure-Object).Count
    Write-Host ("  {0,-26} {1,5} files" -f $f, $n)
}

# version stamp(s) under the materialized folders
$versions = Get-ChildItem -Recurse -File -ErrorAction SilentlyContinue `
                -Include 'AssemblyInfo.cs','AssemblyInfo.vb','*.csproj' `
                ($Folders | ForEach-Object { Join-Path $DestPath $_ }) |
            Select-String -Pattern 'AssemblyVersion\("([\d\.]+)"\)|<Version>([\d\.]+)</Version>' |
            ForEach-Object { $_.Matches[0].Groups[1].Value + $_.Matches[0].Groups[2].Value } |
            Sort-Object -Unique
if ($versions) {
    Write-Host ("  Version stamp(s): {0}" -f ($versions -join ', ')) -ForegroundColor Cyan
    if ($ExpectVersion -and ($versions -notcontains $ExpectVersion)) {
        Write-Host ("  [WARN] None of the stamps == expected '$ExpectVersion'." ) -ForegroundColor Yellow
    }
}
Write-Host ""
