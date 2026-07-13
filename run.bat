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
    for /f "usebackq tokens=1,2 delims==" %%a in (".env") do (
        set "line=%%a"
        if not "!line:~0,1!"=="#" set %%a=%%b
    )
) else (
    echo [WARN] No .env file found. Copy .env.example to .env and set your keys.
    echo        cp .env.example .env
    echo.
)

echo [INFO] Installing Python dependencies...
pip install -r requirements.txt --quiet

echo.
echo [INFO] Applying database migrations (alembic upgrade head)...
alembic -c backend/alembic.ini upgrade head
if %errorlevel% neq 0 (
    echo [ERROR] Database migration failed.
    echo         Ensure PostgreSQL is running: docker-compose up -d
    echo         Then retry: run.bat
    pause
    exit /b 1
)

echo [INFO] Database schema is up to date.
echo.
echo [INFO] Starting Frontend on http://localhost:3000
start "Simulyn Frontend" cmd /c "python server.py 3000 && pause"

echo [INFO] Starting Backend API on http://127.0.0.1:8000
echo [INFO] Open http://localhost:3000 in your browser.
echo [INFO] Press Ctrl+C to stop.
echo.
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
