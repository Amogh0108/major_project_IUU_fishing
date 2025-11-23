@echo off
echo ======================================================================
echo IUU FISHING DETECTION SYSTEM - ENHANCED PIPELINE
echo ======================================================================
echo.
echo Starting enhanced pipeline execution...
echo This will take approximately 5-10 minutes.
echo.

python scripts\run_enhanced_pipeline.py

echo.
echo ======================================================================
echo PIPELINE EXECUTION COMPLETE
echo ======================================================================
echo.
echo Check the outputs folder for results:
echo   - outputs/explainability/alert_summary.csv (High-risk vessels)
echo   - outputs/evaluation/ (Performance metrics)
echo   - outputs/realtime/ (Real-time detection results)
echo.
pause
