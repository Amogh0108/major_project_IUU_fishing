@echo off
REM ========================================
REM Push IUU Fishing Detection to GitHub
REM ========================================

echo.
echo ========================================
echo IUU Fishing Detection - GitHub Push
echo ========================================
echo.

REM Check if Git is installed
where git >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Git is not installed!
    echo.
    echo Please install Git from: https://git-scm.com/download/win
    echo.
    pause
    exit /b 1
)

echo [1/7] Git is installed - OK
echo.

REM Initialize git repository if not already initialized
if not exist .git (
    echo [2/7] Initializing Git repository...
    git init
    echo Repository initialized!
) else (
    echo [2/7] Git repository already initialized - OK
)
echo.

REM Configure Git (update with your details)
echo [3/7] Configuring Git...
git config user.name "Amogh0108"
git config user.email "amogh@example.com"
echo Git configured!
echo.

REM Add remote repository
echo [4/7] Adding remote repository...
git remote remove origin 2>nul
git remote add origin https://github.com/Amogh0108/illegal_fishing_detection.git
echo Remote repository added!
echo.

REM Add all files (respecting .gitignore)
echo [5/7] Adding files to Git...
git add .
echo Files added!
echo.

REM Show status
echo [6/7] Git Status:
git status --short
echo.

REM Commit changes
echo [7/7] Committing changes...
git commit -m "Complete IUU Fishing Detection System - ML models, dashboard, and comprehensive documentation"
echo.

REM Push to GitHub
echo ========================================
echo Ready to push to GitHub!
echo ========================================
echo.
echo Repository: https://github.com/Amogh0108/illegal_fishing_detection.git
echo Branch: main
echo.
echo NOTE: You may be prompted for GitHub credentials.
echo If using Personal Access Token, use it as the password.
echo.
pause

echo Pushing to GitHub...
git push -u origin main

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo SUCCESS! Code pushed to GitHub!
    echo ========================================
    echo.
    echo View your repository at:
    echo https://github.com/Amogh0108/illegal_fishing_detection
    echo.
) else (
    echo.
    echo ========================================
    echo Push failed! Trying alternative branch...
    echo ========================================
    echo.
    
    REM Try master branch if main fails
    git push -u origin master
    
    if %ERRORLEVEL% EQU 0 (
        echo.
        echo SUCCESS! Code pushed to GitHub (master branch)!
        echo.
    ) else (
        echo.
        echo ERROR: Push failed!
        echo.
        echo Possible solutions:
        echo 1. Check your internet connection
        echo 2. Verify repository URL is correct
        echo 3. Ensure you have push access to the repository
        echo 4. Try: git push -u origin main --force
        echo.
    )
)

pause
