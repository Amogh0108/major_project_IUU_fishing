@echo off
cls
echo ======================================================================
echo IUU FISHING DETECTION SYSTEM - DASHBOARD LAUNCHER
echo ======================================================================
echo.
echo Starting interactive dashboard...
echo.
echo Dashboard Features:
echo   - Real-time vessel tracking
echo   - Anomaly detection visualization
echo   - Risk level classification
echo   - Interactive maps and charts
echo   - Export functionality
echo.
echo ======================================================================
echo.

python src\dashboard\app.py

if errorlevel 1 (
    echo.
    echo ======================================================================
    echo ERROR: Failed to start dashboard
    echo ======================================================================
    echo.
    echo Possible solutions:
    echo   1. Ensure Python is installed and in PATH
    echo   2. Install required packages: pip install -r requirements.txt
    echo   3. Check if port 8050 is available
    echo.
    pause
) else (
    echo.
    echo ======================================================================
    echo Dashboard stopped successfully
    echo ======================================================================
    echo.
)

pause
