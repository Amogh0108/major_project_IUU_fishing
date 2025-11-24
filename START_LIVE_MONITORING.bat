@echo off
echo ======================================================================
echo 🌊 IUU FISHING DETECTION - LIVE MONITORING SYSTEM
echo ======================================================================
echo.
echo This will start continuous monitoring of vessels in Indian EEZ
echo.
echo Features:
echo   - Fetches live AIS data every 15 minutes
echo   - Processes data through ML pipeline
echo   - Detects anomalies in real-time
echo   - Generates alerts for high-risk vessels
echo   - Updates dashboard automatically
echo.
echo ======================================================================
echo.

python src\realtime\live_monitoring_system.py

pause
