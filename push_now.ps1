# Push to GitHub Script
$gitPath = "C:\Program Files\Git\bin\git.exe"
$repoPath = "C:\Users\asus\Downloads\illegal_fishing_detection-main\illegal_fishing_detection-main"

Set-Location $repoPath

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Pushing to GitHub" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Initialize git repository
Write-Host "[1/7] Initializing Git repository..." -ForegroundColor Yellow
& $gitPath init
Write-Host "Done!" -ForegroundColor Green
Write-Host ""

# Configure Git
Write-Host "[2/7] Configuring Git..." -ForegroundColor Yellow
& $gitPath config user.name "Amogh0108"
& $gitPath config user.email "amogh@example.com"
Write-Host "Done!" -ForegroundColor Green
Write-Host ""

# Add remote
Write-Host "[3/7] Adding remote repository..." -ForegroundColor Yellow
& $gitPath remote remove origin 2>$null
& $gitPath remote add origin https://github.com/Amogh0108/illegal_fishing_detection.git
Write-Host "Done!" -ForegroundColor Green
Write-Host ""

# Add all files
Write-Host "[4/7] Adding files..." -ForegroundColor Yellow
& $gitPath add .
Write-Host "Done!" -ForegroundColor Green
Write-Host ""

# Show status
Write-Host "[5/7] Git Status:" -ForegroundColor Yellow
& $gitPath status --short
Write-Host ""

# Commit
Write-Host "[6/7] Committing changes..." -ForegroundColor Yellow
& $gitPath commit -m "Complete IUU Fishing Detection System with organized documentation"
Write-Host "Done!" -ForegroundColor Green
Write-Host ""

# Push
Write-Host "[7/7] Pushing to GitHub..." -ForegroundColor Yellow
Write-Host "Repository: https://github.com/Amogh0108/illegal_fishing_detection.git" -ForegroundColor Cyan
Write-Host "Branch: main" -ForegroundColor Cyan
Write-Host ""
Write-Host "NOTE: You may be prompted for GitHub credentials." -ForegroundColor Yellow
Write-Host "Use your Personal Access Token as the password." -ForegroundColor Yellow
Write-Host ""

& $gitPath push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "SUCCESS! Code pushed to GitHub!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "View your repository at:" -ForegroundColor Cyan
    Write-Host "https://github.com/Amogh0108/illegal_fishing_detection" -ForegroundColor Cyan
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "Push failed! Trying alternative branch..." -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    
    & $gitPath push -u origin master
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "SUCCESS! Code pushed to GitHub (master branch)!" -ForegroundColor Green
        Write-Host ""
    } else {
        Write-Host ""
        Write-Host "ERROR: Push failed!" -ForegroundColor Red
        Write-Host ""
        Write-Host "Possible solutions:" -ForegroundColor Yellow
        Write-Host "1. Check your internet connection" -ForegroundColor White
        Write-Host "2. Verify repository URL is correct" -ForegroundColor White
        Write-Host "3. Ensure you have push access to the repository" -ForegroundColor White
        Write-Host "4. Get a Personal Access Token from: https://github.com/settings/tokens" -ForegroundColor White
        Write-Host ""
    }
}

Write-Host "Press any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
