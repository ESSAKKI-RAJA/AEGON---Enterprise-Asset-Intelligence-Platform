$ErrorActionPreference = "Continue"

Write-Host "====================================="
Write-Host "      AEGON Verification Script"
Write-Host "====================================="

$success = $true

Write-Host "`n[1/4] Running Backend Tests (pytest)..."
Set-Location -Path "$PSScriptRoot\..\backend"
& .\venv\Scripts\python.exe -m pytest
if ($LASTEXITCODE -ne 0) { $success = $false; Write-Host "Backend tests failed!" -ForegroundColor Red }

Write-Host "`n[2/4] Running Frontend Linting..."
Set-Location -Path "$PSScriptRoot\..\frontend"
npm run lint
if ($LASTEXITCODE -ne 0) { $success = $false; Write-Host "Frontend linting failed!" -ForegroundColor Red }

Write-Host "`n[3/4] Running Frontend Type Check..."
npx tsc --noEmit
if ($LASTEXITCODE -ne 0) { $success = $false; Write-Host "Frontend type check failed!" -ForegroundColor Red }

Write-Host "`n[4/4] Running Frontend Build..."
npm run build
if ($LASTEXITCODE -ne 0) { $success = $false; Write-Host "Frontend build failed!" -ForegroundColor Red }

Write-Host "`n====================================="
if ($success) {
    Write-Host "ALL CHECKS PASSED!" -ForegroundColor Green
} else {
    Write-Host "SOME CHECKS FAILED! Please review the logs above." -ForegroundColor Red
}
Write-Host "====================================="
