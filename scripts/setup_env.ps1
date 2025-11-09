# YouTube Bot Video Extractor - Setup Script
# This script sets up the development environment

Write-Host "=== YouTube Bot Video Extractor - Environment Setup ===" -ForegroundColor Cyan
Write-Host ""

# Check Python installation
Write-Host "Checking Python installation..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Python found: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Python not found. Please install Python 3.11 or higher." -ForegroundColor Red
    exit 1
}

# Check Python version
$version = python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
$major, $minor = $version -split '\.'
if ([int]$major -lt 3 -or ([int]$major -eq 3 -and [int]$minor -lt 11)) {
    Write-Host "[ERROR] Python version must be 3.11 or higher. Found: $version" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Python version is compatible: $version" -ForegroundColor Green

# Create virtual environment
Write-Host ""
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "Virtual environment already exists." -ForegroundColor Gray
} else {
    python -m venv venv
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Virtual environment created" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] Failed to create virtual environment" -ForegroundColor Red
        exit 1
    }
}

# Activate virtual environment
Write-Host ""
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Upgrade pip
Write-Host ""
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Install dependencies
Write-Host ""
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

Write-Host ""
Write-Host "Installing development dependencies..." -ForegroundColor Yellow
pip install -r requirements-dev.txt

# Create necessary directories
Write-Host ""
Write-Host "Creating necessary directories..." -ForegroundColor Yellow
$directories = @("data", "downloads", "logs", "resources/icons")
foreach ($dir in $directories) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "[OK] Created directory: $dir" -ForegroundColor Green
    }
}

# Copy example configuration files
Write-Host ""
Write-Host "Setting up configuration files..." -ForegroundColor Yellow
if (!(Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Created .env from .env.example" -ForegroundColor Green
    Write-Host "  Please edit .env with your settings" -ForegroundColor Gray
}

if (!(Test-Path "config.json")) {
    Copy-Item "config.example.json" "config.json"
    Write-Host "Created config.json from config.example.json" -ForegroundColor Green
    Write-Host "  Please edit config.json with your settings" -ForegroundColor Gray
}

# Summary
Write-Host ""
Write-Host "=== Setup Complete! ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Edit .env with your YouTube API credentials" -ForegroundColor White
Write-Host "2. Edit config.json with your channel settings" -ForegroundColor White
Write-Host "3. Run: python src/main.py" -ForegroundColor White
Write-Host ""
Write-Host "To activate the virtual environment later, run:" -ForegroundColor Yellow
Write-Host '  .\venv\Scripts\Activate.ps1' -ForegroundColor White
Write-Host ""
