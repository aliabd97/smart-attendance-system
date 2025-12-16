# Test Dashboard Functionality

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Testing Dashboard Functionality    " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Test 1: Check if API Gateway is running
Write-Host "[1/5] Testing API Gateway..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5000/health" -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "   OK - API Gateway is running" -ForegroundColor Green
    }
} catch {
    Write-Host "   FAILED - API Gateway is not responding" -ForegroundColor Red
    Write-Host "   Please run .\START.ps1 first" -ForegroundColor Yellow
    exit 1
}

# Test 2: Check if Auth Service is running
Write-Host "[2/5] Testing Auth Service..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5007/health" -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "   OK - Auth Service is running" -ForegroundColor Green
    }
} catch {
    Write-Host "   FAILED - Auth Service is not responding" -ForegroundColor Red
    Write-Host "   Please run .\START.ps1 first" -ForegroundColor Yellow
    exit 1
}

# Test 3: Check if dashboard HTML loads
Write-Host "[3/5] Testing Dashboard HTML..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5000/" -UseBasicParsing
    if ($response.Content -match "Smart Attendance") {
        Write-Host "   OK - Dashboard HTML loads" -ForegroundColor Green
    } else {
        Write-Host "   FAILED - Dashboard HTML does not contain expected content" -ForegroundColor Red
    }
} catch {
    Write-Host "   FAILED - Cannot load dashboard" -ForegroundColor Red
}

# Test 4: Check if app.js loads
Write-Host "[4/5] Testing JavaScript file..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5000/static/app.js" -UseBasicParsing
    if ($response.Content -match "Login") {
        Write-Host "   OK - JavaScript file loads" -ForegroundColor Green
    } else {
        Write-Host "   WARNING - JavaScript file loads but content unexpected" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   FAILED - Cannot load app.js" -ForegroundColor Red
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 5: Test login API
Write-Host "[5/5] Testing Login API..." -ForegroundColor Yellow
try {
    $body = @{
        username = "admin"
        password = "admin123"
    } | ConvertTo-Json

    $response = Invoke-RestMethod -Uri "http://localhost:5000/api/auth/login" `
        -Method POST `
        -ContentType "application/json" `
        -Body $body

    if ($response.token) {
        Write-Host "   OK - Login API works, token received" -ForegroundColor Green

        # Bonus Test 6: Test API Gateway routing with token
        Write-Host ""
        Write-Host "[BONUS] Testing API Gateway Routing..." -ForegroundColor Yellow

        $headers = @{
            "Authorization" = "Bearer $($response.token)"
        }

        # Test students endpoint
        try {
            $studentsResponse = Invoke-RestMethod -Uri "http://localhost:5000/api/students" -Headers $headers
            Write-Host "   OK - Students endpoint works (count: $($studentsResponse.count))" -ForegroundColor Green
        } catch {
            Write-Host "   FAILED - Students endpoint error: $($_.Exception.Message)" -ForegroundColor Red
        }

        # Test courses endpoint
        try {
            $coursesResponse = Invoke-RestMethod -Uri "http://localhost:5000/api/courses" -Headers $headers
            Write-Host "   OK - Courses endpoint works (count: $($coursesResponse.count))" -ForegroundColor Green
        } catch {
            Write-Host "   FAILED - Courses endpoint error: $($_.Exception.Message)" -ForegroundColor Red
        }

        # Test attendance endpoint
        try {
            $attendanceResponse = Invoke-RestMethod -Uri "http://localhost:5000/api/attendance" -Headers $headers
            Write-Host "   OK - Attendance endpoint works (count: $($attendanceResponse.count))" -ForegroundColor Green
        } catch {
            Write-Host "   FAILED - Attendance endpoint error: $($_.Exception.Message)" -ForegroundColor Red
        }

    } else {
        Write-Host "   FAILED - No token received" -ForegroundColor Red
    }
} catch {
    Write-Host "   FAILED - Login API error" -ForegroundColor Red
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "             Test Summary              " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "If all tests passed:" -ForegroundColor Green
Write-Host "  1. Open browser to: http://localhost:5000" -ForegroundColor White
Write-Host "  2. Press F12 to open Developer Tools" -ForegroundColor White
Write-Host "  3. Go to Console tab" -ForegroundColor White
Write-Host "  4. You should see: 'App.js loaded successfully'" -ForegroundColor White
Write-Host "  5. Login with: admin / admin123" -ForegroundColor White
Write-Host ""
Write-Host "If you see errors in browser console:" -ForegroundColor Yellow
Write-Host "  - Check TROUBLESHOOTING_LOGIN.md for solutions" -ForegroundColor White
Write-Host ""
