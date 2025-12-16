# Install All Dependencies Script
# Smart Attendance System - Local Setup

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Installing All Dependencies..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$currentDir = Get-Location

# Install Student Service
Write-Host "Installing student-service..." -ForegroundColor Yellow
Set-Location "$currentDir\student-service"
pip install -r requirements.txt
if ($LASTEXITCODE -eq 0) { Write-Host "OK" -ForegroundColor Green } else { Write-Host "FAIL" -ForegroundColor Red }

# Install Course Service
Write-Host "Installing course-service..." -ForegroundColor Yellow
Set-Location "$currentDir\course-service"
pip install -r requirements.txt
if ($LASTEXITCODE -eq 0) { Write-Host "OK" -ForegroundColor Green } else { Write-Host "FAIL" -ForegroundColor Red }

# Install Attendance Service
Write-Host "Installing attendance-service..." -ForegroundColor Yellow
Set-Location "$currentDir\attendance-service"
pip install -r requirements.txt
if ($LASTEXITCODE -eq 0) { Write-Host "OK" -ForegroundColor Green } else { Write-Host "FAIL" -ForegroundColor Red }

# Install Auth Service
Write-Host "Installing auth-service..." -ForegroundColor Yellow
Set-Location "$currentDir\auth-service"
pip install -r requirements.txt
if ($LASTEXITCODE -eq 0) { Write-Host "OK" -ForegroundColor Green } else { Write-Host "FAIL" -ForegroundColor Red }

# Install Service Registry
Write-Host "Installing service-registry..." -ForegroundColor Yellow
Set-Location "$currentDir\service-registry"
pip install -r requirements.txt
if ($LASTEXITCODE -eq 0) { Write-Host "OK" -ForegroundColor Green } else { Write-Host "FAIL" -ForegroundColor Red }

# Install Bubble Sheet Generator
Write-Host "Installing bubble-sheet-generator..." -ForegroundColor Yellow
Set-Location "$currentDir\bubble-sheet-generator"
pip install -r requirements.txt
if ($LASTEXITCODE -eq 0) { Write-Host "OK" -ForegroundColor Green } else { Write-Host "FAIL" -ForegroundColor Red }

# Install PDF Processing Service
Write-Host "Installing pdf-processing-service..." -ForegroundColor Yellow
Set-Location "$currentDir\pdf-processing-service"
pip install -r requirements.txt
if ($LASTEXITCODE -eq 0) { Write-Host "OK" -ForegroundColor Green } else { Write-Host "FAIL" -ForegroundColor Red }

# Install Reporting Service
Write-Host "Installing reporting-service..." -ForegroundColor Yellow
Set-Location "$currentDir\reporting-service"
pip install -r requirements.txt
if ($LASTEXITCODE -eq 0) { Write-Host "OK" -ForegroundColor Green } else { Write-Host "FAIL" -ForegroundColor Red }

# Install API Gateway
Write-Host "Installing api-gateway..." -ForegroundColor Yellow
Set-Location "$currentDir\api-gateway"
pip install -r requirements.txt
if ($LASTEXITCODE -eq 0) { Write-Host "OK" -ForegroundColor Green } else { Write-Host "FAIL" -ForegroundColor Red }

Set-Location $currentDir

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Installation Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next step: Run .\START.ps1" -ForegroundColor Yellow
Write-Host ""
