$ErrorActionPreference = "Stop"

Write-Host "====================================="
Write-Host "      AEGON Run Pipeline Script"
Write-Host "====================================="

Write-Host "`n[1/4] Starting Redis Container..."
docker run -d --name aegon-redis -p 6379:6379 redis:7
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to start Redis or it's already running." -ForegroundColor Yellow
}

Write-Host "`n[2/4] Running Database Migrations..."
Set-Location -Path "$PSScriptRoot\..\backend"
& .\venv\Scripts\python.exe -m alembic upgrade head

Write-Host "`n[3/4] Starting Backend (FastAPI)..."
Start-Process cmd -ArgumentList "/c `"cd /d `"$PSScriptRoot\..\backend`" && .\venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000`"" -WindowStyle Normal

Write-Host "`n[4/4] Starting Frontend (React/Vite)..."
Set-Location -Path "$PSScriptRoot\..\frontend"
Start-Process cmd -ArgumentList "/c `"cd /d `"$PSScriptRoot\..\frontend`" && npm run dev -- --host 127.0.0.1 --port 5173`"" -WindowStyle Normal

Write-Host "`n====================================="
Write-Host "Pipeline Started Successfully!" -ForegroundColor Green
Write-Host "====================================="
Write-Host "Backend API / Swagger: http://127.0.0.1:8000/docs"
Write-Host "Frontend Application : http://127.0.0.1:5173"
Write-Host "====================================="
