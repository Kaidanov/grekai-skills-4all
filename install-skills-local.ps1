# install-skills-local.ps1
# Copies all GrekAI skills from this repo into ~/.claude/skills/
# Run once on any PC where you have cloned grekai-skills-4all.
# Usage:  cd C:\Projects\grekai-skills-4all  &&  .\install-skills-local.ps1

$source = Join-Path $PSScriptRoot 'skills'
$target = Join-Path $HOME '.claude\skills'

$skills = @(
    'tutorial',
    'gemelnet-advisor',
    'share-presentation',
    'handoff',
    'setup-memory',
    'dev-rules-and-agents',
    'daily-cv',
    'my-claude-toolkit',
    'tldr',
    'token-audit'
)

Write-Host ''
Write-Host 'GrekAI Skills -- Local Install' -ForegroundColor Cyan
Write-Host "Source : $source"
Write-Host "Target : $target"
Write-Host ''

$installed = 0
$skipped   = 0

foreach ($skill in $skills) {
    $src = Join-Path $source $skill
    $dst = Join-Path $target $skill

    if (-not (Test-Path $src)) {
        Write-Host "  SKIP  $skill  (folder not found in repo)" -ForegroundColor Yellow
        $skipped++
        continue
    }

    if (-not (Test-Path $target)) {
        New-Item -ItemType Directory -Path $target -Force | Out-Null
    }

    Copy-Item -Path $src -Destination $dst -Recurse -Force
    Write-Host "  OK    $skill" -ForegroundColor Green
    $installed++
}

Write-Host ''
Write-Host "Done. $installed installed, $skipped skipped." -ForegroundColor Cyan
Write-Host ''
Write-Host "Skills are now in: $target"
Write-Host 'Restart Claude Code to pick them up.'
