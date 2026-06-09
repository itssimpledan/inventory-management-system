@echo off
title Inventory Management System
cd /d "%~dp0"
echo =====================================================
echo   INVENTORY MANAGEMENT SYSTEM
echo   Starting local server...
echo =====================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not on PATH.
    echo Please install Python from https://python.org and try again.
    pause
    exit /b 1
)

REM Install dependencies silently
echo Installing / checking dependencies...
pip install flask werkzeug reportlab openpyxl --quiet --break-system-packages 2>nul
pip install flask werkzeug reportlab openpyxl --quiet 2>nul

REM Initialise the database (only runs once; skips if DB exists)
python init_db.py

echo.
echo Server is starting at http://localhost:5000
echo Opening browser...
echo Press Ctrl+C to stop the server.
echo.

REM Open browser after 2 seconds
start "" /b cmd /c "timeout /t 2 /nobreak >nul && start http://localhost:5000"

REM Start Flask
python app.py
pause
