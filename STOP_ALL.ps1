# STOP_ALL.ps1 - Stop All Services for Smart Attendance System

Write-Host "============================================================" -ForegroundColor Red
Write-Host "  Smart Attendance System - Stopping All Services" -ForegroundColor Red
Write-Host "============================================================" -ForegroundColor Red
Write-Host ""

Write-Host "Stopping all services..." -ForegroundColor Yellow
Write-Host ""

# Define all ports
$ports = @(5000, 5001, 5002, 5003, 5004, 5005, 5007, 5008, 5009, 3000, 3001)

$stoppedCount = 0

foreach ($port in $ports) {
    try {
        $connections = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
        if ($connections) {
            $processes = $connections | Select-Object -ExpandProperty OwningProcess -Unique
            foreach ($processId in $processes) {
                try {
                    Stop-Process -Id $processId -Force -ErrorAction Stop
                    Write-Host "  Stopped process on port $port" -ForegroundColor Green
                    $stoppedCount++
                } catch {
                    Write-Host "  Could not stop port $port" -ForegroundColor Yellow
                }
            }
        }
    } catch {
        # Port not in use
    }
}

Write-Host ""
Write-Host "Cleaned up $stoppedCount processes" -ForegroundColor Green
Write-Host ""
Write-Host "============================================================" -ForegroundColor Red
Write-Host "  All services stopped!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Red
Write-Host ""
Write-Host "To start the system again, run: .\START_ALL.ps1" -ForegroundColor Cyan
Write-Host ""
