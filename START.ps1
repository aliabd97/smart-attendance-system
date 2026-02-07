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
    @{Name="Auth Service"; Path="auth-service"; Port=5007; Wait=2; Type="Python"},
    @{Name="Student Service"; Path="student-service"; Port=5001; Wait=2; Type="Python"},
    @{Name="Course Service"; Path="course-service"; Port=5002; Wait=2; Type="Python"},
    @{Name="Attendance Service"; Path="attendance-service"; Port=5005; Wait=2; Type="Python"},
    @{Name="Bubble Sheet Generator"; Path="bubble-sheet-generator"; Port=5003; Wait=2; Type="Python"},
    @{Name="PDF Processing Service"; Path="pdf-processing-service"; Port=5004; Wait=2; Type="Python"},
    @{Name="Reporting Service"; Path="reporting-service"; Port=5009; Wait=2; Type="Python"},
    @{Name="API Gateway"; Path="api-gateway"; Port=5000; Wait=3; Type="Python"},
    @{Name="Frontend Dashboard"; Path="frontend"; Port=3000; Wait=5; Type="NextJS"}
)

# =========================================
# Check RabbitMQ (Required for Choreography Pattern)
# =========================================
Write-Host "Checking RabbitMQ status..." -ForegroundColor Yellow

$rabbitmqRunning = $false
try {
    $rabbitmqProcess = Get-Process -Name "erl" -ErrorAction SilentlyContinue
    if ($rabbitmqProcess) {
        $rabbitmqRunning = $true
    }

    # Also check if port 5672 is in use (RabbitMQ default port)
    $rabbitmqPort = Get-NetTCPConnection -LocalPort 5672 -ErrorAction SilentlyContinue
    if ($rabbitmqPort) {
        $rabbitmqRunning = $true
    }
} catch {
    # Silent fail
}

if ($rabbitmqRunning) {
    Write-Host "  ✓ RabbitMQ is running (Port 5672)" -ForegroundColor Green
    Write-Host "  ✓ Management UI: http://localhost:15672" -ForegroundColor Green
} else {
    Write-Host "  ⚠ RabbitMQ is NOT running!" -ForegroundColor Red
    Write-Host "  → Choreography Pattern requires RabbitMQ" -ForegroundColor Yellow
    Write-Host "  → Start RabbitMQ: rabbitmq-server (or from Windows Services)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  Continue without RabbitMQ? (Choreography will not work)" -ForegroundColor Yellow
    $response = Read-Host "  Press Enter to continue, or Ctrl+C to cancel"
}

Write-Host ""

# =========================================
# Clean up ports before starting
# =========================================
Write-Host "Checking for running services on ports..." -ForegroundColor Yellow

$portsToClean = $services | ForEach-Object { $_.Port }
$cleanedCount = 0

foreach ($port in $portsToClean) {
    try {
        # Find processes using this port
        $processInfo = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue |
                       Select-Object -First 1 -ExpandProperty OwningProcess

        if ($processInfo) {
            $process = Get-Process -Id $processInfo -ErrorAction SilentlyContinue
            if ($process) {
                Write-Host "  → Stopping process on port $port (PID: $processInfo)..." -ForegroundColor DarkYellow
                Stop-Process -Id $processInfo -Force -ErrorAction SilentlyContinue
                $cleanedCount++
                Start-Sleep -Milliseconds 500
            }
        }
    } catch {
        # Port is free, continue
    }
}

if ($cleanedCount -gt 0) {
    Write-Host "  ✓ Cleaned $cleanedCount port(s)" -ForegroundColor Green
    Start-Sleep -Seconds 1
} else {
    Write-Host "  ✓ All ports are free" -ForegroundColor Green
}

Write-Host ""
Write-Host "Starting:" -ForegroundColor Yellow
Write-Host "  - 8 Backend Microservices" -ForegroundColor White
Write-Host "  - Next.js Frontend Dashboard" -ForegroundColor White
Write-Host ""

$totalServices = $services.Count
$currentService = 0

foreach ($service in $services) {
    $currentService++
    $servicePath = Join-Path $currentDir $service.Path

    Write-Host "[$currentService/$totalServices] Starting $($service.Name)..." -ForegroundColor Green

    if ($service.Type -eq "Python" -and (Test-Path "$servicePath\app.py")) {
        $title = "Smart Attendance - $($service.Name)"
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "& {`$Host.UI.RawUI.WindowTitle='$title'; cd '$servicePath'; python app.py}"

        Write-Host "   OK - Port $($service.Port)" -ForegroundColor Cyan
        Start-Sleep -Seconds $service.Wait
    } elseif ($service.Type -eq "NextJS" -and (Test-Path "$servicePath\package.json")) {
        $title = "Smart Attendance - Frontend"
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "& {`$Host.UI.RawUI.WindowTitle='$title'; cd '$servicePath'; npm run dev}"

        Write-Host "   OK - Port $($service.Port)" -ForegroundColor Cyan
        Start-Sleep -Seconds $service.Wait
    } else {
        Write-Host "   ERROR - Service files not found in $servicePath" -ForegroundColor Red
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
Write-Host "  Auth Service:           http://localhost:5007" -ForegroundColor White
Write-Host "  Student Service:        http://localhost:5001" -ForegroundColor White
Write-Host "  Course Service:         http://localhost:5002" -ForegroundColor White
Write-Host "  Attendance Service:     http://localhost:5005" -ForegroundColor White
Write-Host "  Bubble Sheet Generator: http://localhost:5003" -ForegroundColor White
Write-Host "  PDF Processing:         http://localhost:5004" -ForegroundColor White
Write-Host "  Reporting Service:      http://localhost:5009" -ForegroundColor White
Write-Host "  API Gateway:            http://localhost:5000" -ForegroundColor White
Write-Host ""
Write-Host "  Message Broker:" -ForegroundColor Yellow
Write-Host "  -----------------" -ForegroundColor DarkGray
Write-Host "  RabbitMQ:               http://localhost:15672 (guest/guest)" -ForegroundColor White
Write-Host ""
Write-Host "  ================================================" -ForegroundColor Magenta
Write-Host "  ADMIN DASHBOARD:  http://localhost:3000        " -ForegroundColor Magenta
Write-Host "  ================================================" -ForegroundColor Magenta
Write-Host ""

Write-Host "Login credentials:" -ForegroundColor Yellow
Write-Host "  Username: admin" -ForegroundColor Green
Write-Host "  Password: admin123" -ForegroundColor Green
Write-Host ""

Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Open browser" -ForegroundColor White
Write-Host "  2. Go to: http://localhost:3000" -ForegroundColor White
Write-Host "  3. Login with credentials above" -ForegroundColor White
Write-Host "  4. Start using the system!" -ForegroundColor White
Write-Host ""

Write-Host "To stop all services: .\STOP.ps1" -ForegroundColor Red
Write-Host ""

# Open browser automatically
Write-Host "Opening browser in 3 seconds..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

Start-Process "http://localhost:3000"

Write-Host ""
Write-Host "System is ready!" -ForegroundColor Green
Write-Host ""
