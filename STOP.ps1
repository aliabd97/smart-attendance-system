# ═══════════════════════════════════════════════════════════════
#  Smart Attendance System - STOP ALL SERVICES
#  إيقاف جميع الخدمات
# ═══════════════════════════════════════════════════════════════

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════╗" -ForegroundColor Red
Write-Host "║         Stopping Smart Attendance System...           ║" -ForegroundColor Red
Write-Host "╚════════════════════════════════════════════════════════╝" -ForegroundColor Red
Write-Host ""

# إيقاف جميع عمليات Python (Flask services)
$pythonProcesses = Get-Process python -ErrorAction SilentlyContinue

if ($pythonProcesses) {
    Write-Host "🛑 Found $($pythonProcesses.Count) Python process(es)" -ForegroundColor Yellow
    Write-Host "   Stopping all Flask services..." -ForegroundColor Yellow

    foreach ($process in $pythonProcesses) {
        try {
            Stop-Process -Id $process.Id -Force
            Write-Host "   ✓ Stopped PID $($process.Id)" -ForegroundColor Green
        } catch {
            Write-Host "   ✗ Failed to stop PID $($process.Id)" -ForegroundColor Red
        }
    }
} else {
    Write-Host "✓ No Python processes running" -ForegroundColor Green
}

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║           All Services Stopped Successfully!          ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "To start again, run: .\START.ps1" -ForegroundColor Cyan
Write-Host ""
