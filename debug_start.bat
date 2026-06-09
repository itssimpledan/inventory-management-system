@echo off
title IMS Debug Mode
cd /d "%~dp0"
echo =====================================================
echo   IMS DEBUG MODE — errors will stay on screen
echo =====================================================
echo.

python --version
echo.

echo Checking dependencies...
python -c "import flask; print('flask OK')" 2>&1
python -c "import werkzeug; print('werkzeug OK')" 2>&1
python -c "import openpyxl; print('openpyxl OK')" 2>&1
python -c "import reportlab; print('reportlab OK')" 2>&1
echo.

echo Installing / checking dependencies...
pip install flask werkzeug reportlab openpyxl --break-system-packages 2>&1
pip install flask werkzeug reportlab openpyxl 2>&1
echo.

echo Running init_db...
python init_db.py
echo.

echo Starting Flask server (Ctrl+C to stop)...
python app.py

echo.
echo =====================================================
echo   SERVER STOPPED — see error above if any
echo =====================================================
pause
