# Smart Attendance System - ONE-CLICK STARTER
# Starts all services + Dashboard in one command

Write-Host ""
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "   Smart Attendance System - Starting All Services     " -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

$currentDir = Get-Location

# Services list (order matters!)
$services = @(
    @{Name="Service Registry"; Path="service-registry"; Port=5008; Wait=2},
    @{Name="Auth Service"; Path="auth-service"; Port=5007; Wait=2},
    @{Name="Student Service"; Path="student-service"; Port=5001; Wait=2},
    @{Name="Course Service"; Path="course-service"; Port=5002; Wait=2},
    @{Name="Attendance Service"; Path="attendance-service"; Port=5005; Wait=2},
    @{Name="Bubble Sheet Generator"; Path="bubble-sheet-generator"; Port=5003; Wait=2},
    @{Name="PDF Processing Service"; Path="pdf-processing-service"; Port=5004; Wait=2},
    @{Name="Reporting Service"; Path="reporting-service"; Port=5009; Wait=2},
    @{Name="API Gateway"; Path="api-gateway"; Port=5000; Wait=3}
)

Write-Host "Starting:" -ForegroundColor Yellow
Write-Host "  - 9 Backend Microservices" -ForegroundColor White
Write-Host "  - Dashboard integrated with API Gateway" -ForegroundColor White
Write-Host ""

$totalServices = $services.Count
$currentService = 0

foreach ($service in $services) {
    $currentService++
    $servicePath = Join-Path $currentDir $service.Path

    Write-Host "[$currentService/$totalServices] Starting $($service.Name)..." -ForegroundColor Green

    if (Test-Path "$servicePath\app.py") {
        $title = "Smart Attendance - $($service.Name)"
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "& {`$Host.UI.RawUI.WindowTitle='$title'; cd '$servicePath'; python app.py}"

        Write-Host "   OK - Port $($service.Port)" -ForegroundColor Cyan
        Start-Sleep -Seconds $service.Wait
    } else {
        Write-Host "   ERROR - app.py not found in $servicePath" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Waiting for all services to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

Write-Host ""
Write-Host "========================================================" -ForegroundColor Green
Write-Host "            System Started Successfully!                " -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Green
Write-Host ""

Write-Host "Services running:" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Backend Services:" -ForegroundColor Yellow
Write-Host "  -----------------" -ForegroundColor DarkGray
Write-Host "  Service Registry:       http://localhost:5008" -ForegroundColor White
Write-Host "  Auth Service:           http://localhost:5007" -ForegroundColor White
Write-Host "  Student Service:        http://localhost:5001" -ForegroundColor White
Write-Host "  Course Service:         http://localhost:5002" -ForegroundColor White
Write-Host "  Attendance Service:     http://localhost:5005" -ForegroundColor White
Write-Host "  Bubble Sheet Generator: http://localhost:5003" -ForegroundColor White
Write-Host "  PDF Processing:         http://localhost:5004" -ForegroundColor White
Write-Host "  Reporting Service:      http://localhost:5009" -ForegroundColor White
Write-Host "  API Gateway:            http://localhost:5000" -ForegroundColor White
Write-Host ""
Write-Host "  ================================================" -ForegroundColor Magenta
Write-Host "  ADMIN DASHBOARD:  http://localhost:5000        " -ForegroundColor Magenta
Write-Host "  ================================================" -ForegroundColor Magenta
Write-Host ""

Write-Host "Login credentials:" -ForegroundColor Yellow
Write-Host "  Username: admin" -ForegroundColor Green
Write-Host "  Password: admin123" -ForegroundColor Green
Write-Host ""

Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Open browser" -ForegroundColor White
Write-Host "  2. Go to: http://localhost:5000" -ForegroundColor White
Write-Host "  3. Login with credentials above" -ForegroundColor White
Write-Host "  4. Start using the system!" -ForegroundColor White
Write-Host ""

Write-Host "To stop all services: .\STOP.ps1" -ForegroundColor Red
Write-Host ""

# Open browser automatically
Write-Host "Opening browser in 3 seconds..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

Start-Process "http://localhost:5000"

Write-Host ""
Write-Host "System is ready!" -ForegroundColor Green
Write-Host ""
