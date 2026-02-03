# Smart Attendance System - STOP ALL SERVICES

Write-Host ""
Write-Host "========================================================" -ForegroundColor Red
Write-Host "    Stopping Smart Attendance System...                " -ForegroundColor Red
Write-Host "========================================================" -ForegroundColor Red
Write-Host ""

# Stop all Python processes (Flask services)
$pythonProcesses = Get-Process python -ErrorAction SilentlyContinue

if ($pythonProcesses) {
    Write-Host "Found $($pythonProcesses.Count) Python process(es)" -ForegroundColor Yellow
    Write-Host "Stopping all Flask services..." -ForegroundColor Yellow

    foreach ($process in $pythonProcesses) {
        try {
            Stop-Process -Id $process.Id -Force
            Write-Host "  Stopped PID $($process.Id)" -ForegroundColor Green
        } catch {
            Write-Host "  Failed to stop PID $($process.Id)" -ForegroundColor Red
        }
    }
} else {
    Write-Host "No Python processes running" -ForegroundColor Green
}

Write-Host ""

# Stop all Node.js processes (Next.js frontend)
$nodeProcesses = Get-Process node -ErrorAction SilentlyContinue

if ($nodeProcesses) {
    Write-Host "Found $($nodeProcesses.Count) Node.js process(es)" -ForegroundColor Yellow
    Write-Host "Stopping Next.js frontend..." -ForegroundColor Yellow

    foreach ($process in $nodeProcesses) {
        try {
            Stop-Process -Id $process.Id -Force
            Write-Host "  Stopped PID $($process.Id)" -ForegroundColor Green
        } catch {
            Write-Host "  Failed to stop PID $($process.Id)" -ForegroundColor Red
        }
    }
} else {
    Write-Host "No Node.js processes running" -ForegroundColor Green
}

# Clean up ports (fallback)
Write-Host ""
Write-Host "Cleaning up ports..." -ForegroundColor Yellow

$ports = @(5000, 5001, 5002, 5003, 5004, 5005, 5007, 5009, 3000)
$cleanedCount = 0

foreach ($port in $ports) {
    try {
        $processInfo = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue |
                       Select-Object -First 1 -ExpandProperty OwningProcess

        if ($processInfo) {
            Stop-Process -Id $processInfo -Force -ErrorAction SilentlyContinue
            $cleanedCount++
        }
    } catch {
        # Port already free
    }
}

if ($cleanedCount -gt 0) {
    Write-Host "  Cleaned $cleanedCount additional port(s)" -ForegroundColor Green
} else {
    Write-Host "  All ports are free" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================================" -ForegroundColor Green
Write-Host "      All Services Stopped Successfully!               " -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Green
Write-Host ""
Write-Host "To start again, run: .\START.ps1" -ForegroundColor Cyan
Write-Host ""
