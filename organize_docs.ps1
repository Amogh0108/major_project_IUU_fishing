# Organize documentation files
$rootPath = "C:\Users\asus\Downloads\illegal_fishing_detection-main\illegal_fishing_detection-main"
Set-Location $rootPath

# Create project_docs folder
New-Item -ItemType Directory -Name "project_docs" -Force | Out-Null

# List of files to move (all .md except README.md)
$filesToMove = @(
    "PRESENTATION.md",
    "GITHUB_PUSH_INSTRUCTIONS.md",
    "REPOSITORY_CONTENTS.md",
    "PUSH_SUMMARY.md",
    "READY_TO_PUSH.md",
    "DASHBOARD_QUICK_START.md",
    "EXECUTION_RESULTS.md",
    "GIT_PUSH_SUMMARY.md",
    "IMPLEMENTATION_GUIDE.md",
    "OBJECTIVES_ACHIEVEMENT.md",
    "PROJECT_COMPLETION_SUMMARY.md",
    "PROJECT_SUMMARY.md",
    "QUICK_REFERENCE.md",
    "SYSTEM_OVERVIEW.md",
    "UI_ENHANCEMENTS_SUMMARY.md",
    "UI_FEATURES.md"
)

# Move each file
foreach ($file in $filesToMove) {
    if (Test-Path $file) {
        Move-Item -Path $file -Destination "project_docs\" -Force
        Write-Host "Moved: $file"
    }
}

Write-Host "Done! All documentation files moved to project_docs folder."
