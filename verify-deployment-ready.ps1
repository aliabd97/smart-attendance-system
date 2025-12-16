# PowerShell Script to Verify Deployment Readiness
# Smart Attendance Management System

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Deployment Readiness Verification" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$allPassed = $true

# Check 1: render.yaml exists and has no disk configurations
Write-Host "Check 1: render.yaml configuration..." -ForegroundColor Yellow
try {
    $renderYaml = Get-Content "render.yaml" -Raw

    if ($renderYaml -match "disk:") {
        Write-Host "✗ FAILED: render.yaml contains 'disk:' configuration" -ForegroundColor Red
        Write-Host "  Solution: Remove all disk configurations" -ForegroundColor Yellow
        $allPassed = $false
    } else {
        Write-Host "✓ PASSED: No disk configurations found" -ForegroundColor Green
    }

    if ($renderYaml -match "gunicorn") {
        Write-Host "✓ PASSED: Using gunicorn for production" -ForegroundColor Green
    } else {
        Write-Host "✗ FAILED: gunicorn not found in startCommand" -ForegroundColor Red
        $allPassed = $false
    }

    Write-Host ""
} catch {
    Write-Host "✗ FAILED: render.yaml not found" -ForegroundColor Red
    $allPassed = $false
    Write-Host ""
}

# Check 2: All services have gunicorn in requirements.txt
Write-Host "Check 2: Gunicorn in requirements.txt..." -ForegroundColor Yellow

$services = @(
    "api-gateway",
    "auth-service",
    "student-service",
    "course-service",
    "attendance-service",
    "service-registry"
)

foreach ($service in $services) {
    $reqFile = "$service\requirements.txt"

    if (Test-Path $reqFile) {
        $content = Get-Content $reqFile -Raw

        if ($content -match "gunicorn") {
            Write-Host "  ✓ $service" -ForegroundColor Green
        } else {
            Write-Host "  ✗ $service - Missing gunicorn" -ForegroundColor Red
            $allPassed = $false
        }
    } else {
        Write-Host "  ✗ $service - requirements.txt not found" -ForegroundColor Red
        $allPassed = $false
    }
}
Write-Host ""

# Check 3: All services have app.py
Write-Host "Check 3: Service files exist..." -ForegroundColor Yellow

foreach ($service in $services) {
    $appFile = "$service\app.py"

    if (Test-Path $appFile) {
        Write-Host "  ✓ $service\app.py" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $service\app.py not found" -ForegroundColor Red
        $allPassed = $false
    }
}
Write-Host ""

# Check 4: Common utilities exist
Write-Host "Check 4: Common utilities..." -ForegroundColor Yellow

$commonFiles = @(
    "common\database.py",
    "common\rabbitmq_client.py",
    "common\circuit_breaker.py",
    "common\utils.py"
)

foreach ($file in $commonFiles) {
    if (Test-Path $file) {
        Write-Host "  ✓ $file" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $file not found" -ForegroundColor Red
        $allPassed = $false
    }
}
Write-Host ""

# Check 5: Documentation files exist
Write-Host "Check 5: Documentation files..." -ForegroundColor Yellow

$docFiles = @(
    "README.md",
    "QUICKSTART.md",
    "DEPLOYMENT_CHECKLIST.md",
    "RENDER_QUICK_FIX.md",
    "test-api.ps1"
)

foreach ($file in $docFiles) {
    if (Test-Path $file) {
        Write-Host "  ✓ $file" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $file not found" -ForegroundColor Red
        $allPassed = $false
    }
}
Write-Host ""

# Check 6: Git repository
Write-Host "Check 6: Git repository..." -ForegroundColor Yellow

if (Test-Path ".git") {
    Write-Host "  ✓ Git repository initialized" -ForegroundColor Green

    # Check if there are uncommitted changes
    $gitStatus = git status --porcelain
    if ($gitStatus) {
        Write-Host "  ⚠ Warning: You have uncommitted changes" -ForegroundColor Yellow
        Write-Host "    Run: git add . && git commit -m 'Ready for deployment'" -ForegroundColor Cyan
    } else {
        Write-Host "  ✓ All changes committed" -ForegroundColor Green
    }
} else {
    Write-Host "  ⚠ Warning: Git not initialized" -ForegroundColor Yellow
    Write-Host "    Run: git init" -ForegroundColor Cyan
}
Write-Host ""

# Check 7: Python version
Write-Host "Check 7: Python version..." -ForegroundColor Yellow

try {
    $pythonVersion = python --version 2>&1
    if ($pythonVersion -match "Python 3\.(1[01])") {
        Write-Host "  ✓ $pythonVersion (Compatible)" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ $pythonVersion" -ForegroundColor Yellow
        Write-Host "    Recommended: Python 3.10 or 3.11" -ForegroundColor Cyan
    }
} catch {
    Write-Host "  ✗ Python not found in PATH" -ForegroundColor Red
}
Write-Host ""

# Check 8: File structure
Write-Host "Check 8: Project structure..." -ForegroundColor Yellow

$requiredDirs = @(
    "api-gateway",
    "auth-service",
    "student-service",
    "course-service",
    "attendance-service",
    "service-registry",
    "common"
)

foreach ($dir in $requiredDirs) {
    if (Test-Path $dir -PathType Container) {
        Write-Host "  ✓ $dir\" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $dir\ not found" -ForegroundColor Red
        $allPassed = $false
    }
}
Write-Host ""

# Final Result
Write-Host "========================================" -ForegroundColor Cyan

if ($allPassed) {
    Write-Host "  ✅ ALL CHECKS PASSED!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Your project is ready for deployment! 🚀" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next Steps:" -ForegroundColor Yellow
    Write-Host "1. Make sure all changes are committed:" -ForegroundColor White
    Write-Host "   git add ." -ForegroundColor Cyan
    Write-Host "   git commit -m 'Ready for Render deployment'" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "2. Push to GitHub:" -ForegroundColor White
    Write-Host "   git remote add origin YOUR_REPO_URL" -ForegroundColor Cyan
    Write-Host "   git push -u origin main" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "3. Deploy on Render.com:" -ForegroundColor White
    Write-Host "   - Go to https://render.com/dashboard" -ForegroundColor Cyan
    Write-Host "   - Click 'New +' → 'Blueprint'" -ForegroundColor Cyan
    Write-Host "   - Select your repository" -ForegroundColor Cyan
    Write-Host "   - Click 'Apply'" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "4. After deployment, test with:" -ForegroundColor White
    Write-Host "   .\test-api.ps1" -ForegroundColor Cyan
    Write-Host ""
} else {
    Write-Host "  ⚠ SOME CHECKS FAILED" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Please fix the issues above before deploying." -ForegroundColor Yellow
    Write-Host "Review DEPLOYMENT_CHECKLIST.md for detailed instructions." -ForegroundColor Yellow
    Write-Host ""
}

Write-Host "For detailed deployment guide, see:" -ForegroundColor Cyan
Write-Host "  - DEPLOYMENT_CHECKLIST.md" -ForegroundColor White
Write-Host "  - RENDER_QUICK_FIX.md" -ForegroundColor White
Write-Host ""
