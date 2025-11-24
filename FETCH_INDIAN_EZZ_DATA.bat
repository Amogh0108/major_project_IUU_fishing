@echo off
echo ======================================================================
echo FETCHING INDIAN EEZ DATA
echo ======================================================================
echo.
echo This script will:
echo 1. Try to fetch real AIS data from Indian EEZ
echo 2. If no real data available, generate sample data
echo 3. Verify the data is correctly positioned
echo.
echo Indian EEZ Coverage: 6-22 degrees N, 68-88 degrees E
echo ======================================================================
echo.

echo Step 1: Attempting to fetch real AIS data...
python src/data/ais_api_integration.py
echo.

echo Step 2: Checking if data was fetched...
if exist "data\raw\ais_live_data.csv" (
    echo ✅ Data file found
) else (
    echo ⚠️ No real data available, generating sample data...
    python src/data/generate_indian_ezz_sample.py
)
echo.

echo Step 3: Verifying data location...
python verify_indian_ezz_data.py
echo.

echo ======================================================================
echo COMPLETE!
echo ======================================================================
echo.
echo Data saved to:
echo   - data\raw\ais_live_data.csv
echo   - outputs\anomaly_predictions.csv
echo.
echo You can now:
echo   - View data in dashboard: python launch_dashboard_enhanced.py
echo   - Start live monitoring: python src\realtime\live_monitoring_system.py
echo.
pause
