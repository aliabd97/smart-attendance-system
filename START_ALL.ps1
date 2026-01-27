# START_ALL.ps1 - Start All Services for Smart Attendance System

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Smart Attendance System - Starting All Services" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Kill any existing processes on the ports
Write-Host "[1/10] Cleaning up old processes..." -ForegroundColor Yellow
$ports = @(5000, 5001, 5002, 5003, 5004, 5005, 5007, 5008, 5009, 3000, 3001)
foreach ($port in $ports) {
    $process = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -ErrorAction SilentlyContinue
    if ($process) {
        Stop-Process -Id $process -Force -ErrorAction SilentlyContinue
        Write-Host "  Stopped process on port $port" -ForegroundColor Green
    }
}
Start-Sleep -Seconds 2

# Start API Gateway (Port 5000)
Write-Host "[2/10] Starting API Gateway (Port 5000)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\api-gateway'; python app.py" -WindowStyle Minimized
Start-Sleep -Seconds 2

# Start Student Service (Port 5001)
Write-Host "[3/10] Starting Student Service (Port 5001)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\student-service'; python app.py" -WindowStyle Minimized
Start-Sleep -Seconds 2

# Start Course Service (Port 5002)
Write-Host "[4/10] Starting Course Service (Port 5002)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\course-service'; python app.py" -WindowStyle Minimized
Start-Sleep -Seconds 2

# Start Bubble Sheet Generator (Port 5003)
Write-Host "[5/10] Starting Bubble Sheet Generator (Port 5003)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\bubble-sheet-generator'; python app.py" -WindowStyle Minimized
Start-Sleep -Seconds 2

# Start PDF Processing Service (Port 5004)
Write-Host "[6/10] Starting PDF Processing Service (Port 5004)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\pdf-processing-service'; python app.py" -WindowStyle Minimized
Start-Sleep -Seconds 2

# Start Attendance Service (Port 5005)
Write-Host "[7/10] Starting Attendance Service (Port 5005)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\attendance-service'; python app.py" -WindowStyle Minimized
Start-Sleep -Seconds 2

# Start Auth Service (Port 5007)
Write-Host "[8/10] Starting Auth Service (Port 5007)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\auth-service'; python app.py" -WindowStyle Minimized
Start-Sleep -Seconds 2

# Start Service Registry (Port 5008)
Write-Host "[9/10] Starting Service Registry (Port 5008)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\service-registry'; python app.py" -WindowStyle Minimized
Start-Sleep -Seconds 2

# Start Reporting Service (Port 5009)
Write-Host "[10/10] Starting Reporting Service (Port 5009)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\reporting-service'; python app.py" -WindowStyle Minimized
Start-Sleep -Seconds 3

Write-Host ""
Write-Host "All backend services started!" -ForegroundColor Green
Write-Host ""

# Start Frontend (Port 3000/3001)
Write-Host "Starting Frontend (Next.js)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\frontend'; npm run dev"
Start-Sleep -Seconds 5

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  All Services Started Successfully!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Dashboard: http://localhost:3001" -ForegroundColor White
Write-Host "Login: admin / admin123" -ForegroundColor White
Write-Host ""
Write-Host "Press any key to open the dashboard..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

Start-Process "http://localhost:3001"

Write-Host ""
Write-Host "Browser opened!" -ForegroundColor Green
Write-Host ""
