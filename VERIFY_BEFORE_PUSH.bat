@echo off
REM ========================================
REM Verify Repository Before Push
REM ========================================

echo.
echo ========================================
echo Repository Verification
echo ========================================
echo.

REM Check if Git is installed
where git >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [X] Git is NOT installed
    echo     Install from: https://git-scm.com/download/win
    echo.
) else (
    echo [OK] Git is installed
)

REM Check if .gitignore exists
if exist .gitignore (
    echo [OK] .gitignore exists
) else (
    echo [X] .gitignore NOT found
)

REM Check if README exists
if exist README.md (
    echo [OK] README.md exists
) else (
    echo [X] README.md NOT found
)

REM Check if PRESENTATION.md exists
if exist PRESENTATION.md (
    echo [OK] PRESENTATION.md exists
) else (
    echo [X] PRESENTATION.md NOT found
)

REM Check if requirements.txt exists
if exist requirements.txt (
    echo [OK] requirements.txt exists
) else (
    echo [X] requirements.txt NOT found
)

REM Check if source code exists
if exist src\ (
    echo [OK] src/ directory exists
) else (
    echo [X] src/ directory NOT found
)

REM Check if scripts exist
if exist scripts\ (
    echo [OK] scripts/ directory exists
) else (
    echo [X] scripts/ directory NOT found
)

REM Check if push script exists
if exist PUSH_TO_GITHUB.bat (
    echo [OK] PUSH_TO_GITHUB.bat exists
) else (
    echo [X] PUSH_TO_GITHUB.bat NOT found
)

echo.
echo ========================================
echo File Size Check
echo ========================================
echo.

REM Check for large files that should be excluded
echo Checking for large files (should be excluded)...
echo.

if exist data\raw\ais_data.csv (
    echo [!] data\raw\ais_data.csv found - Will be excluded by .gitignore
) else (
    echo [OK] data\raw\ais_data.csv not present (or will be excluded)
)

if exist data\processed\ais_all_features.csv (
    echo [!] data\processed\ais_all_features.csv found - Will be excluded by .gitignore
) else (
    echo [OK] data\processed\ais_all_features.csv not present (or will be excluded)
)

if exist outputs\models\random_forest.pkl (
    echo [!] Model files found - Will be excluded by .gitignore
) else (
    echo [OK] Model files not present (or will be excluded)
)

echo.
echo ========================================
echo Documentation Check
echo ========================================
echo.

if exist GITHUB_PUSH_INSTRUCTIONS.md (
    echo [OK] GITHUB_PUSH_INSTRUCTIONS.md exists
) else (
    echo [X] GITHUB_PUSH_INSTRUCTIONS.md NOT found
)

if exist REPOSITORY_CONTENTS.md (
    echo [OK] REPOSITORY_CONTENTS.md exists
) else (
    echo [X] REPOSITORY_CONTENTS.md NOT found
)

if exist PUSH_SUMMARY.md (
    echo [OK] PUSH_SUMMARY.md exists
) else (
    echo [X] PUSH_SUMMARY.md NOT found
)

if exist data\README.md (
    echo [OK] data\README.md exists
) else (
    echo [X] data\README.md NOT found
)

if exist outputs\models\README.md (
    echo [OK] outputs\models\README.md exists
) else (
    echo [X] outputs\models\README.md NOT found
)

echo.
echo ========================================
echo Git Status Preview
echo ========================================
echo.

where git >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    if exist .git (
        echo Current Git status:
        git status --short
    ) else (
        echo Git repository not initialized yet
        echo Run PUSH_TO_GITHUB.bat to initialize
    )
) else (
    echo Git not installed - cannot show status
)

echo.
echo ========================================
echo Summary
echo ========================================
echo.
echo Repository URL: https://github.com/Amogh0108/illegal_fishing_detection.git
echo.
echo Next Steps:
echo 1. Review the checks above
echo 2. Ensure all [OK] items are present
echo 3. Run PUSH_TO_GITHUB.bat to push to GitHub
echo.
echo Documentation:
echo - GITHUB_PUSH_INSTRUCTIONS.md - Detailed push guide
echo - REPOSITORY_CONTENTS.md - File listing
echo - PUSH_SUMMARY.md - Quick summary
echo.

pause
