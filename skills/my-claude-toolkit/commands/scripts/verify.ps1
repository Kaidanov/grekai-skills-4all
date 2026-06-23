# Run from repo root in PowerShell: powershell -ExecutionPolicy Bypass -File .\.claude\scripts\verify.ps1
Write-Host "🔍 Running Lint..."
pnpm lint
if ($LASTEXITCODE -ne 0) { exit 1 }

Write-Host "🧠 Running Type Checks..."
pnpm typecheck
if ($LASTEXITCODE -ne 0) { exit 1 }

Write-Host "🧪 Running Tests..."
pnpm test
if ($LASTEXITCODE -ne 0) { exit 1 }

Write-Host "🚀 Checking Dev Server Boot..."
Start-Process "pnpm" "dev" -NoNewWindow
Start-Sleep -Seconds 5

try {
    Invoke-WebRequest -Uri http://localhost:3000 -UseBasicParsing -TimeoutSec 10 | Out-Null
    Write-Host "✅ Dev server is up!"
} catch {
    Write-Host "❌ Dev server failed to respond."
    exit 1
}
