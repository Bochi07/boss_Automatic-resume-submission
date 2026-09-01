@echo off
cd /d "%~dp0"

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python not found, please install Python first.
    pause
    exit /b 1
)

echo Installing dependencies...
pip install -r requirements.txt -q

echo Starting goodjob backend...
python main.py

echo.
echo Backend exited.
pause
