# Quick Enrollment Script - Demo Data
# This script enrolls demo students in courses

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Student Enrollment Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Instructions
Write-Host "STEP 1: Get your auth token" -ForegroundColor Yellow
Write-Host "  1. Open http://localhost:3000 in browser" -ForegroundColor Gray
Write-Host "  2. Login with admin/admin123" -ForegroundColor Gray
Write-Host "  3. Press F12 to open Developer Tools" -ForegroundColor Gray
Write-Host "  4. Go to Console tab" -ForegroundColor Gray
Write-Host "  5. Type: localStorage.getItem('token')" -ForegroundColor Gray
Write-Host "  6. Copy the token (without quotes)" -ForegroundColor Gray
Write-Host ""

$token = Read-Host "Paste your token here"

if ([string]::IsNullOrWhiteSpace($token)) {
    Write-Host "Error: Token is required!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "STEP 2: Enter Course ID to enroll students" -ForegroundColor Yellow
$courseId = Read-Host "Course ID (e.g., CS101)"

if ([string]::IsNullOrWhiteSpace($courseId)) {
    Write-Host "Error: Course ID is required!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Checking if course exists..." -ForegroundColor Yellow

try {
    $course = Invoke-RestMethod -Method GET `
        -Uri "http://localhost:5000/api/courses/$courseId" `
        -Headers @{"Authorization"="Bearer $token"} `
        -ErrorAction Stop

    Write-Host "✓ Course found: $($course.name)" -ForegroundColor Green
} catch {
    Write-Host "✗ Course not found! Please create the course first." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "STEP 3: Demo students to enroll" -ForegroundColor Yellow

# Demo students
$demoStudents = @(
    @{Id="S001"; Name="Ahmed Ali"},
    @{Id="S002"; Name="Fatima Hassan"},
    @{Id="S003"; Name="Mohammed Khalid"},
    @{Id="S004"; Name="Sara Abdullah"},
    @{Id="S005"; Name="Omar Youssef"}
)

Write-Host "Will enroll these students:" -ForegroundColor Gray
foreach ($student in $demoStudents) {
    Write-Host "  - $($student.Id): $($student.Name)" -ForegroundColor Gray
}

Write-Host ""
$confirm = Read-Host "Continue? (y/n)"

if ($confirm -ne 'y') {
    Write-Host "Cancelled." -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "Creating students and enrolling..." -ForegroundColor Yellow

$successCount = 0
$failCount = 0

foreach ($student in $demoStudents) {
    try {
        # Create student if not exists
        Write-Host "Creating student $($student.Id)..." -ForegroundColor Gray
        try {
            $createResult = Invoke-RestMethod -Method POST `
                -Uri "http://localhost:5000/api/students" `
                -Headers @{
                    "Authorization"="Bearer $token"
                    "Content-Type"="application/json"
                } `
                -Body (@{
                    student_id=$student.Id
                    name=$student.Name
                    email="$($student.Id.ToLower())@university.edu"
                    department="Computer Science"
                } | ConvertTo-Json) `
                -ErrorAction SilentlyContinue

            Write-Host "  ✓ Student created" -ForegroundColor Green
        } catch {
            Write-Host "  ⚠ Student may already exist, continuing..." -ForegroundColor Yellow
        }

        # Enroll in course
        Write-Host "Enrolling $($student.Id) in $courseId..." -ForegroundColor Gray
        $enrollResult = Invoke-RestMethod -Method POST `
            -Uri "http://localhost:5000/api/courses/$courseId/students/$($student.Id)" `
            -Headers @{"Authorization"="Bearer $token"} `
            -ErrorAction Stop

        Write-Host "  ✓ Enrolled successfully" -ForegroundColor Green
        $successCount++

    } catch {
        Write-Host "  ✗ Failed: $($_.Exception.Message)" -ForegroundColor Red
        $failCount++
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Enrollment Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Success: $successCount students" -ForegroundColor Green
Write-Host "Failed: $failCount students" -ForegroundColor Red
Write-Host ""
Write-Host "You can now generate bubble sheets for course: $courseId" -ForegroundColor Yellow
Write-Host "Go to: http://localhost:3000/dashboard/bubble-sheets" -ForegroundColor Cyan
Write-Host ""
