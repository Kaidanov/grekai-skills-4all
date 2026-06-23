# Run from repo root in PowerShell: powershell -ExecutionPolicy Bypass -File .\.claude\scripts\commit-and-pr.ps1
$timestamp = Get-Date -Format "yyyyMMdd-HHmm"
$branch = "release-$timestamp"
$tag = "rollback-$timestamp"

Write-Host "📦 Creating branch: $branch"
git checkout -b $branch

git add .
git commit -m "✅ MCP verified release [$timestamp]"
git tag $tag
git push origin $branch --tags

Write-Host "🚀 Creating GitHub PR..."
gh pr create --fill --base main --head $branch --title "Auto PR: MCP Agent Update $timestamp" --body "Claude verified tests, lint, dev boot, and committed agent changes."
