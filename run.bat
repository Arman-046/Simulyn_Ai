@echo off
echo =========================================
echo  Simulyn — AI Decision Intelligence
echo  AMD Developer Hackathon
echo =========================================
echo.

REM Check Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Please install Python 3.10+.
    pause
    exit /b 1
)

REM Load .env if present
if exist .env (
    echo [INFO] Loading environment from .env...
    for /f "tokens=1,2 delims==" %%a in (.env) do set %%a=%%b
)

echo [INFO] Installing Python dependencies...
pip install -r requirements.txt --quiet

echo.
echo [INFO] Starting Frontend on http://localhost:3000
start "Simulyn Frontend" cmd /c "python -m http.server 3000 && pause"

echo [INFO] Starting Backend API on http://127.0.0.1:8000
echo [INFO] Press Ctrl+C to stop.
echo.
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
