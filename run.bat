@echo off
setlocal
cd /d "%~dp0"

echo ========================================
echo   ProjectPartner AI - Startup
echo ========================================

where py >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python launcher "py" not found. Install Python 3.8+ from python.org
    pause
    exit /b 1
)

echo Checking dependencies...
py -3.8 -c "import flask, streamlit, mysql.connector" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing dependencies...
    py -3.8 -m pip install -r requirements.txt
)

echo Starting backend on http://localhost:5001 ...
start "ProjectPartner Backend" cmd /k "cd /d "%~dp0" && py -3.8 backend\app.py"

timeout /t 4 /nobreak > nul

echo Starting frontend on http://localhost:8501 ...
start "ProjectPartner Frontend" cmd /k "cd /d "%~dp0" && py -3.8 -m streamlit run frontend\app.py --server.port 8501"

timeout /t 5 /nobreak > nul

echo Opening browser...
start http://localhost:8501

echo.
echo Backend:  http://localhost:5001
echo Frontend: http://localhost:8501
echo Admin:    admin@projectpartner.ai / admin123
echo Demo:     tanmay@example.com / demo123
echo.
pause
