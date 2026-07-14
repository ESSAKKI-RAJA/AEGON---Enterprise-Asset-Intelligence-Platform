@echo off
echo ===================================================
echo   AEGON Local Development Startup
echo ===================================================
echo.

:: Kill any stale processes on the required ports
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5173 " ^| findstr "LISTENING"') do (
    echo Killing stale process on port 5173 (PID %%a)
    taskkill /PID %%a /F >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000 " ^| findstr "LISTENING"') do (
    echo Killing stale process on port 8000 (PID %%a)
    taskkill /PID %%a /F >nul 2>&1
)

echo Starting Backend on 127.0.0.1:8000...
start "AEGON-Backend" cmd /k "cd /d "%~dp0backend" && .\venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"

echo Starting Frontend on 127.0.0.1:5173...
start "AEGON-Frontend" cmd /k "cd /d "%~dp0frontend" && npm run dev -- --host 127.0.0.1 --port 5173"

echo ===================================================
echo   Servers started. Now open http://127.0.0.1:5173
echo ===================================================
pause
