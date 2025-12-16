# Quick Start Guide - Smart Attendance System

## Step 1: Install Dependencies (First Time Only)

```powershell
.\install-all.ps1
```

Wait for all packages to install (5-10 minutes).

## Step 2: Start All Services

```powershell
.\START.ps1
```

This will:
- Open 9 PowerShell windows (one for each service)
- Start all services automatically
- Wait for initialization
- Open browser to http://localhost:5000

**Important:** Wait 30 seconds for all services to fully start.

## Step 3: Login to Dashboard

When browser opens:

1. You'll see a purple login page with "🎓 Smart Attendance"
2. Enter:
   - **Username:** admin
   - **Password:** admin123
3. Click "Login"
4. Dashboard will appear with sidebar navigation

## Step 4: Verify Everything Works

Press **F12** to open browser Developer Tools, then:

1. Click on **Console** tab
2. You should see:
   ```
   App.js loaded successfully
   Token from localStorage: not found
   DOM Content Loaded
   No saved session, showing login page
   ```

3. Login with admin/admin123

4. Console should show:
   ```
   Login form submitted
   Attempting login for user: admin
   Login response status: 200
   Login successful, saving token and redirecting to dashboard
   ```

5. Dashboard appears with:
   - Sidebar: Overview, Students, Courses, Attendance, Logout
   - Main area: Statistics cards showing 0 students, 0 courses, 0 records

## Step 5: Add Test Data

### Add a Student

1. Click "👥 Students" in sidebar
2. Click "+ Add Student" button
3. Fill in:
   - Student ID: S001
   - Name: Ahmad Hassan
   - Department: Computer Science
   - Email: ahmad@university.edu
4. Click "Save"
5. Student appears in table

### Add a Course

1. Click "📚 Courses" in sidebar
2. Click "+ Add Course" button
3. Fill in:
   - Course Code: CS101
   - Course Name: Introduction to Programming
   - Instructor: Dr. Sarah Ahmed
   - Department: Computer Science
4. Click "Save"
5. Course appears in table

## Step 6: Test Automated System

Run the test script:

```powershell
.\test-dashboard.ps1
```

All 5 tests should pass with green checkmarks.

## Step 7: Stop All Services (When Done)

```powershell
.\STOP.ps1
```

This closes all PowerShell windows and stops all services.

## Common Issues

### Issue: Login button does nothing

**Solution:**
1. Press F12, check Console for errors
2. If you see "404 /static/app.js" - the fix in DASHBOARD_FIXED.md wasn't applied
3. Restart services: `.\STOP.ps1` then `.\START.ps1`

### Issue: "Failed to fetch" error

**Solution:**
- Auth Service is not running
- Check if port 5007 window shows errors
- Restart all services

### Issue: Blank page after login

**Solution:**
- Clear browser cache: Ctrl+Shift+Delete
- Or use Incognito mode: Ctrl+Shift+N
- Clear localStorage: F12 → Application → Local Storage → Clear

### Issue: Services won't start

**Solution:**
1. Close all PowerShell windows
2. Run `.\STOP.ps1` to ensure cleanup
3. Wait 10 seconds
4. Run `.\START.ps1` again

## File Structure

```
smart-attendance-system/
├── api-gateway/              # Port 5000 - Dashboard + API routing
│   ├── static/
│   │   ├── dashboard.html    # Admin dashboard UI
│   │   └── app.js           # Dashboard JavaScript
│   └── app.py               # Gateway service
├── auth-service/            # Port 5007 - Authentication
├── student-service/         # Port 5001 - Student CRUD
├── course-service/          # Port 5002 - Course CRUD
├── attendance-service/      # Port 5006 - Attendance tracking
├── bubble-sheet-generator/  # Port 5003 - Generate PDF sheets
├── pdf-processing-service/  # Port 5004 - OMR processing
├── reporting-service/       # Port 5009 - Excel/PDF reports
├── service-registry/        # Port 5008 - Service discovery
├── START.ps1               # Start all services
├── STOP.ps1                # Stop all services
├── test-dashboard.ps1      # Test system health
└── install-all.ps1         # Install dependencies
```

## Dashboard Features

### Overview Page
- Shows total counts for students, courses, and attendance records
- Quick access to all features

### Students Page
- **View:** Table of all students with ID, Name, Department, Email
- **Add:** Modal form to add new student
- **Delete:** Delete button for each student (with confirmation)

### Courses Page
- **View:** Table of all courses with Code, Name, Instructor, Department
- **Add:** Modal form to add new course
- **Delete:** Delete button for each course (with confirmation)

### Attendance Page
- **View:** Table of all attendance records
- Shows: Student ID, Course ID, Lecture ID, Date, Status (colored)
- **Present** = Green text
- **Absent** = Red text

## API Testing (Advanced)

You can test the backend APIs directly:

```powershell
# Test login
curl -X POST http://localhost:5000/api/auth/login `
  -H "Content-Type: application/json" `
  -d '{\"username\":\"admin\",\"password\":\"admin123\"}'

# Test student service (replace TOKEN with actual token)
curl http://localhost:5000/api/students `
  -H "Authorization: Bearer TOKEN"

# Test course service
curl http://localhost:5000/api/courses `
  -H "Authorization: Bearer TOKEN"

# Test attendance service
curl http://localhost:5000/api/attendance `
  -H "Authorization: Bearer TOKEN"
```

## Full Workflow Example

### Complete Attendance Tracking Workflow:

1. **Setup:**
   - Add 30 students (S001-S030)
   - Add course: CS101

2. **Generate Bubble Sheet:**
   ```powershell
   curl -X POST http://localhost:5000/api/bubble-sheet/generate `
     -H "Content-Type: application/json" `
     -H "Authorization: Bearer TOKEN" `
     -d '{
       \"course_id\": \"CS101\",
       \"lecture_id\": \"L001\",
       \"date\": \"2024-01-15\",
       \"student_ids\": [\"S001\", \"S002\", ...]
     }'
   ```

3. **Print the PDF:**
   - PDF saved in `bubble-sheet-generator/generated_sheets/`
   - Print and distribute to class

4. **Students fill bubbles:**
   - Students mark their ID number
   - Mark PRESENT bubble

5. **Scan filled sheets:**
   - Scan to PDF or images

6. **Process scanned sheets:**
   ```powershell
   curl -X POST http://localhost:5000/api/pdf-processing/process `
     -H "Authorization: Bearer TOKEN" `
     -F "file=@scanned_sheet.pdf" `
     -F "course_id=CS101" `
     -F "lecture_id=L001"
   ```

7. **View attendance:**
   - Go to Dashboard → Attendance
   - See all records with PRESENT/ABSENT status

8. **Generate report:**
   ```powershell
   # Excel report
   curl http://localhost:5000/api/reporting/generate/excel/CS101 `
     -H "Authorization: Bearer TOKEN" `
     -o CS101_report.xlsx

   # PDF report
   curl http://localhost:5000/api/reporting/generate/pdf/CS101 `
     -H "Authorization: Bearer TOKEN" `
     -o CS101_report.pdf
   ```

## Next Steps

1. **Customize:** Edit `auth-service/app.py` to add more users
2. **Import Data:** Bulk import students from Excel
3. **Configure:** Set environment variables for production
4. **Deploy:** Use render.yaml for cloud deployment
5. **Monitor:** Check service health endpoints

## Support Files

- **DASHBOARD_FIXED.md** - Detailed explanation of the login fix
- **TROUBLESHOOTING_LOGIN.md** - Complete troubleshooting guide
- **PROJECT_COMPLETE.md** - Full system documentation
- **LOCAL_SETUP_GUIDE.md** - Detailed local setup instructions

## Success Checklist

- [ ] All services installed (install-all.ps1)
- [ ] All services started (START.ps1)
- [ ] Can access http://localhost:5000
- [ ] Can login with admin/admin123
- [ ] Dashboard shows with sidebar
- [ ] Can add student
- [ ] Can add course
- [ ] Can view attendance (empty initially)
- [ ] test-dashboard.ps1 shows all tests passing

**If all checkboxes are checked, your system is ready to use!**
