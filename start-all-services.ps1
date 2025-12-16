# Start All Services Script
# Smart Attendance System - Local Execution

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting Smart Attendance System" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$currentDir = Get-Location

# Services configuration (order matters!)
$services = @(
    @{Name="Service Registry"; Path="service-registry"; Port=5008; Priority=1},
    @{Name="Auth Service"; Path="auth-service"; Port=5007; Priority=2},
    @{Name="Student Service"; Path="student-service"; Port=5001; Priority=3},
    @{Name="Course Service"; Path="course-service"; Port=5002; Priority=4},
    @{Name="Attendance Service"; Path="attendance-service"; Port=5006; Priority=5},
    @{Name="Bubble Sheet Generator"; Path="bubble-sheet-generator"; Port=5003; Priority=6},
    @{Name="PDF Processing Service"; Path="pdf-processing-service"; Port=5004; Priority=7},
    @{Name="Reporting Service"; Path="reporting-service"; Port=5007; Priority=8},
    @{Name="API Gateway"; Path="api-gateway"; Port=5000; Priority=9}
)

Write-Host "Starting Backend Services..." -ForegroundColor Yellow
Write-Host "This will open 9 PowerShell windows" -ForegroundColor Yellow
Write-Host ""

foreach ($service in $services | Sort-Object Priority) {
    $servicePath = Join-Path $currentDir $service.Path

    if (Test-Path "$servicePath\app.py") {
        Write-Host "Starting $($service.Name) on port $($service.Port)..." -ForegroundColor Green

        # Start service in new window
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$servicePath'; python app.py"

        # Wait a bit before starting next service
        Start-Sleep -Seconds 2
    } else {
        Write-Host "✗ app.py not found for $($service.Name)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Waiting for backend services to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

Write-Host ""
Write-Host "Starting Frontend Dashboard..." -ForegroundColor Yellow

$dashboardPath = Join-Path $currentDir "admin-dashboard"

if (Test-Path "$dashboardPath\package.json") {
    Write-Host "Starting Admin Dashboard on http://localhost:3000..." -ForegroundColor Green

    # Create .env file if not exists
    if (-not (Test-Path "$dashboardPath\.env")) {
        Copy-Item "$dashboardPath\.env.example" "$dashboardPath\.env"
        Write-Host "Created .env file from .env.example" -ForegroundColor Cyan
    }

    # Start frontend in new window
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$dashboardPath'; npm run dev"
} else {
    Write-Host "✗ Frontend not found" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "All Services Started!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Services running on:" -ForegroundColor Yellow
Write-Host "  - Service Registry:       http://localhost:5008" -ForegroundColor White
Write-Host "  - Auth Service:           http://localhost:5007" -ForegroundColor White
Write-Host "  - Student Service:        http://localhost:5001" -ForegroundColor White
Write-Host "  - Course Service:         http://localhost:5002" -ForegroundColor White
Write-Host "  - Attendance Service:     http://localhost:5006" -ForegroundColor White
Write-Host "  - Bubble Sheet Generator: http://localhost:5003" -ForegroundColor White
Write-Host "  - PDF Processing:         http://localhost:5004" -ForegroundColor White
Write-Host "  - Reporting Service:      http://localhost:5007" -ForegroundColor White
Write-Host "  - API Gateway:            http://localhost:5000" -ForegroundColor White
Write-Host ""
Write-Host "  - Admin Dashboard:        http://localhost:3000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Login credentials:" -ForegroundColor Yellow
Write-Host "  Username: admin" -ForegroundColor White
Write-Host "  Password: admin123" -ForegroundColor White
Write-Host ""
Write-Host "To stop all services, run: .\stop-all-services.ps1" -ForegroundColor Yellow
Write-Host ""
