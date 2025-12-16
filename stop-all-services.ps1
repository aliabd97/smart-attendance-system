# Stop All Services Script
# Smart Attendance System

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Stopping All Services..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Get all Python processes (Flask services)
$pythonProcesses = Get-Process python -ErrorAction SilentlyContinue

if ($pythonProcesses) {
    Write-Host "Found $($pythonProcesses.Count) Python process(es)" -ForegroundColor Yellow
    Write-Host "Stopping Flask services..." -ForegroundColor Yellow

    foreach ($process in $pythonProcesses) {
        try {
            Stop-Process -Id $process.Id -Force
            Write-Host "✓ Stopped process $($process.Id)" -ForegroundColor Green
        } catch {
            Write-Host "✗ Failed to stop process $($process.Id)" -ForegroundColor Red
        }
    }
} else {
    Write-Host "No Python processes found" -ForegroundColor Yellow
}

Write-Host ""

# Get all Node processes (Frontend)
$nodeProcesses = Get-Process node -ErrorAction SilentlyContinue

if ($nodeProcesses) {
    Write-Host "Found $($nodeProcesses.Count) Node process(es)" -ForegroundColor Yellow
    Write-Host "Stopping Frontend dashboard..." -ForegroundColor Yellow

    foreach ($process in $nodeProcesses) {
        try {
            Stop-Process -Id $process.Id -Force
            Write-Host "✓ Stopped process $($process.Id)" -ForegroundColor Green
        } catch {
            Write-Host "✗ Failed to stop process $($process.Id)" -ForegroundColor Red
        }
    }
} else {
    Write-Host "No Node processes found" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "All Services Stopped!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
