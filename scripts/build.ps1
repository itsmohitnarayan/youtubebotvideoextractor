# YouTube Bot Video Extractor - Build Script
# This script builds the application into a standalone executable

Write-Host "=== YouTube Bot Video Extractor - Build Script ===" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment is activated
if ($env:VIRTUAL_ENV) {
    Write-Host "✓ Virtual environment is active" -ForegroundColor Green
} else {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & .\venv\Scripts\Activate.ps1
}

# Clean previous builds
Write-Host ""
Write-Host "Cleaning previous builds..." -ForegroundColor Yellow
if (Test-Path "build") { Remove-Item -Recurse -Force build }
if (Test-Path "dist") { Remove-Item -Recurse -Force dist }
Write-Host "✓ Cleaned build directories" -ForegroundColor Green

# Run PyInstaller
Write-Host ""
Write-Host "Building executable with PyInstaller..." -ForegroundColor Yellow
Write-Host "This may take several minutes..." -ForegroundColor Gray

# Note: build.spec will be created in Phase 6
# For now, this is a placeholder
Write-Host ""
Write-Host "Build script ready - PyInstaller configuration will be added in Phase 6" -ForegroundColor Yellow
Write-Host ""
