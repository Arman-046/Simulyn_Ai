@echo off
echo =========================================
echo Simulyn Hackathon Ready Runner
echo =========================================
echo.

echo Starting Frontend on http://localhost:3000
start cmd /c "python -m http.server 3000"

echo Starting Backend API on http://127.0.0.1:8000
echo (Ensure Fireworks API Key is set in your environment if needed)
echo.
echo Installing/Verifying Python Requirements...
pip install -r requirements.txt
echo.
uvicorn main:app --reload
