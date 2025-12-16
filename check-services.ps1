# Check Services Health Script
# Smart Attendance System

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Checking Services Status..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$services = @(
    @{Name="Service Registry"; URL="http://localhost:5008/health"},
    @{Name="Auth Service"; URL="http://localhost:5007/health"},
    @{Name="Student Service"; URL="http://localhost:5001/health"},
    @{Name="Course Service"; URL="http://localhost:5002/health"},
    @{Name="Attendance Service"; URL="http://localhost:5006/health"},
    @{Name="Bubble Sheet Generator"; URL="http://localhost:5003/health"},
    @{Name="PDF Processing Service"; URL="http://localhost:5004/health"},
    @{Name="Reporting Service"; URL="http://localhost:5007/health"},
    @{Name="API Gateway"; URL="http://localhost:5000/health"}
)

$healthyCount = 0
$unhealthyCount = 0

foreach ($service in $services) {
    try {
        $response = Invoke-WebRequest -Uri $service.URL -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop

        if ($response.StatusCode -eq 200) {
            Write-Host "✓ $($service.Name)" -ForegroundColor Green -NoNewline
            Write-Host " - HEALTHY" -ForegroundColor Green
            $healthyCount++
        } else {
            Write-Host "✗ $($service.Name)" -ForegroundColor Red -NoNewline
            Write-Host " - UNHEALTHY (Status: $($response.StatusCode))" -ForegroundColor Red
            $unhealthyCount++
        }
    } catch {
        Write-Host "✗ $($service.Name)" -ForegroundColor Red -NoNewline
        Write-Host " - NOT RUNNING" -ForegroundColor Red
        $unhealthyCount++
    }
}

Write-Host ""

# Check Frontend
try {
    $frontendResponse = Invoke-WebRequest -Uri "http://localhost:3000" -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop
    Write-Host "✓ Admin Dashboard" -ForegroundColor Green -NoNewline
    Write-Host " - RUNNING" -ForegroundColor Green
    $healthyCount++
} catch {
    Write-Host "✗ Admin Dashboard" -ForegroundColor Red -NoNewline
    Write-Host " - NOT RUNNING" -ForegroundColor Red
    $unhealthyCount++
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Summary:" -ForegroundColor Cyan
Write-Host "  Healthy:   $healthyCount" -ForegroundColor Green
Write-Host "  Unhealthy: $unhealthyCount" -ForegroundColor Red
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if ($unhealthyCount -eq 0) {
    Write-Host "All services are running! 🚀" -ForegroundColor Green
    Write-Host "Open http://localhost:3000 to use the system" -ForegroundColor Cyan
} else {
    Write-Host "Some services are not running." -ForegroundColor Yellow
    Write-Host "Run: .\start-all-services.ps1 to start all services" -ForegroundColor Yellow
}

Write-Host ""
