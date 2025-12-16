# PowerShell Script to Test APIs on Render.com
# Smart Attendance Management System

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Smart Attendance API Testing" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Base URL (change to your deployed URL)
$BASE_URL = "https://attendance-api-gateway.onrender.com"

# Test 1: Health Check
Write-Host "Test 1: Health Check..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$BASE_URL/" -Method Get
    Write-Host "Success!" -ForegroundColor Green
    Write-Host "Service: $($response.service)" -ForegroundColor White
    Write-Host "Status: $($response.status)" -ForegroundColor White
    Write-Host ""
} catch {
    Write-Host "Failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
}

# Test 2: Login
Write-Host "Test 2: Login..." -ForegroundColor Yellow
try {
    $loginBody = @{
        username = "admin"
        password = "admin123"
    } | ConvertTo-Json

    $loginResponse = Invoke-RestMethod -Uri "$BASE_URL/api/auth/login" -Method Post -Body $loginBody -ContentType "application/json"

    Write-Host "Login Successful!" -ForegroundColor Green
    Write-Host "Username: $($loginResponse.username)" -ForegroundColor White
    Write-Host "Role: $($loginResponse.role)" -ForegroundColor White
    Write-Host "Token: $($loginResponse.token.Substring(0, 50))..." -ForegroundColor White
    Write-Host ""

    # Save Token for later use
    $global:TOKEN = $loginResponse.token

} catch {
    Write-Host "Failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    exit
}

# Test 3: Get All Students
Write-Host "Test 3: Get All Students..." -ForegroundColor Yellow
try {
    $headers = @{
        "Authorization" = "Bearer $global:TOKEN"
    }

    $studentsResponse = Invoke-RestMethod -Uri "$BASE_URL/api/students/students" -Method Get -Headers $headers

    Write-Host "Success!" -ForegroundColor Green
    Write-Host "Total Students: $($studentsResponse.count)" -ForegroundColor White
    Write-Host ""
} catch {
    Write-Host "Failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
}

# Test 4: Create Student
Write-Host "Test 4: Create Student..." -ForegroundColor Yellow
try {
    $headers = @{
        "Authorization" = "Bearer $global:TOKEN"
        "Content-Type" = "application/json"
    }

    $studentBody = @{
        id = "20240001"
        name = "Ahmed Ali Mohammed"
        email = "ahmed@university.edu"
        department = "Computer Science"
        level = 3
        phone = "07712345678"
        is_active = $true
    } | ConvertTo-Json

    $createResponse = Invoke-RestMethod -Uri "$BASE_URL/api/students/students" -Method Post -Headers $headers -Body $studentBody

    Write-Host "Student Created!" -ForegroundColor Green
    Write-Host "Message: $($createResponse.message)" -ForegroundColor White
    Write-Host "Student ID: $($createResponse.student_id)" -ForegroundColor White
    Write-Host ""
} catch {
    Write-Host "Failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Note: Student may already exist" -ForegroundColor Yellow
    Write-Host ""
}

# Test 5: Create Course
Write-Host "Test 5: Create Course..." -ForegroundColor Yellow
try {
    $headers = @{
        "Authorization" = "Bearer $global:TOKEN"
        "Content-Type" = "application/json"
    }

    $courseBody = @{
        id = "CS101"
        name = "Introduction to Computer Science"
        code = "CS101"
        department = "Computer Science"
        credits = 3
        instructor = "Dr. Ahmed Ali"
        semester = "Fall"
        academic_year = "2024-2025"
    } | ConvertTo-Json

    $courseResponse = Invoke-RestMethod -Uri "$BASE_URL/api/courses/courses" -Method Post -Headers $headers -Body $courseBody

    Write-Host "Course Created!" -ForegroundColor Green
    Write-Host "Message: $($courseResponse.message)" -ForegroundColor White
    Write-Host "Course ID: $($courseResponse.course_id)" -ForegroundColor White
    Write-Host ""
} catch {
    Write-Host "Failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Note: Course may already exist" -ForegroundColor Yellow
    Write-Host ""
}

# Test 6: Enroll Student
Write-Host "Test 6: Enroll Student..." -ForegroundColor Yellow
try {
    $headers = @{
        "Authorization" = "Bearer $global:TOKEN"
        "Content-Type" = "application/json"
    }

    $enrollBody = @{
        student_id = "20240001"
    } | ConvertTo-Json

    $enrollResponse = Invoke-RestMethod -Uri "$BASE_URL/api/courses/courses/CS101/enroll" -Method Post -Headers $headers -Body $enrollBody

    Write-Host "Student Enrolled!" -ForegroundColor Green
    Write-Host "Message: $($enrollResponse.message)" -ForegroundColor White
    Write-Host ""
} catch {
    Write-Host "Failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Note: Student may already be enrolled" -ForegroundColor Yellow
    Write-Host ""
}

# Test 7: Record Attendance
Write-Host "Test 7: Record Attendance..." -ForegroundColor Yellow
try {
    $headers = @{
        "Authorization" = "Bearer $global:TOKEN"
        "Content-Type" = "application/json"
    }

    $attendanceBody = @{
        student_id = "20240001"
        course_id = "CS101"
        date = (Get-Date -Format "yyyy-MM-dd")
        status = "present"
        session_name = "Lecture 1"
    } | ConvertTo-Json

    $attendanceResponse = Invoke-RestMethod -Uri "$BASE_URL/api/attendance/attendance" -Method Post -Headers $headers -Body $attendanceBody

    Write-Host "Attendance Recorded!" -ForegroundColor Green
    Write-Host "Message: $($attendanceResponse.message)" -ForegroundColor White
    Write-Host "Record ID: $($attendanceResponse.record_id)" -ForegroundColor White
    Write-Host ""
} catch {
    Write-Host "Failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
}

# Test 8: Get Student Attendance
Write-Host "Test 8: Get Student Attendance..." -ForegroundColor Yellow
try {
    $headers = @{
        "Authorization" = "Bearer $global:TOKEN"
    }

    $attendanceHistory = Invoke-RestMethod -Uri "$BASE_URL/api/attendance/attendance/student/20240001" -Method Get -Headers $headers

    Write-Host "Success!" -ForegroundColor Green
    Write-Host "Total Records: $($attendanceHistory.summary.total)" -ForegroundColor White
    Write-Host "Present: $($attendanceHistory.summary.present)" -ForegroundColor White
    Write-Host "Attendance %: $($attendanceHistory.summary.attendance_percentage)%" -ForegroundColor White
    Write-Host ""
} catch {
    Write-Host "Failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
}

# Final Result
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Testing Complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Your Token:" -ForegroundColor Yellow
Write-Host $global:TOKEN -ForegroundColor White
Write-Host ""
Write-Host "Save this token to use in future requests!" -ForegroundColor Green
Write-Host ""
