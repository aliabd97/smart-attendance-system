# API Gateway Routing Fix - Complete Resolution

## Problem Summary

The dashboard was loading successfully and login was working, but all API calls were returning **404 NOT FOUND** errors:

```
GET /api/students → 404
GET /api/courses → 404
GET /api/attendance → 404
POST /api/students → 404
```

## Root Causes Identified

### Issue 1: Incorrect URL Building in API Gateway

**Problem:**
The API Gateway was building incorrect URLs when forwarding requests to microservices.

**Example:**
- Dashboard calls: `GET /api/students`
- Gateway interprets: service="students", path="" (empty)
- Gateway was building: `http://localhost:5001/api` ❌
- Should build: `http://localhost:5001/api/students` ✓

**Code Before:**
```python
# Build target URL
url = f"{SERVICES[service]}/api/{path}"
# With service="students", path=""
# Result: http://localhost:5001/api/ (wrong!)
```

**Code After:**
```python
# Build target URL
if path:
    url = f"{SERVICES[service]}/api/{service}/{path}"
else:
    url = f"{SERVICES[service]}/api/{service}"
# With service="students", path=""
# Result: http://localhost:5001/api/students (correct!)
```

### Issue 2: Missing Route for Service Root Endpoints

**Problem:**
The API Gateway only had a route for `/api/<service>/<path:path>` which requires a path after the service name. Calls to `/api/students` (without additional path) weren't matching any route.

**Fix:**
Added a dedicated route for service root endpoints:

```python
@app.route('/api/<service>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def gateway_route_no_path(service):
    """Gateway route for service root endpoints"""
    return gateway_route(service, '')
```

### Issue 3: Port Mismatches

**Problem:**
Service ports were inconsistent across configuration files.

**Fixes:**
1. **Attendance Service:** Changed from 5006 to 5005 (correct port)
2. **Reporting Service:** Changed from 5006 to 5009 (correct port)

## Files Modified

### 1. api-gateway/app.py

**Changes:**
- Added route for `/api/<service>` endpoints (lines 138-142)
- Fixed URL building logic to include service name (lines 166-172)
- Fixed Attendance Service port: 5005 (line 29)
- Fixed Reporting Service port: 5009 (line 30)

### 2. START.ps1

**Changes:**
- Fixed Attendance Service port from 5006 to 5005 (line 18)
- Fixed display message for Attendance Service (line 68)

### 3. api-gateway/static/dashboard.html

**Changes:**
- Fixed JavaScript path from `app.js` to `/static/app.js` (line 440)

### 4. api-gateway/static/app.js

**Changes:**
- Added comprehensive console logging for debugging (lines 5-6, 10, 14, 18, 25, 32, 39, 46-48, 51, 58, 63)

## How Routing Works Now

### Example: Get All Students

1. **Dashboard → API Gateway:**
   ```
   GET http://localhost:5000/api/students
   Authorization: Bearer <token>
   ```

2. **API Gateway Processing:**
   - Route matches: `/api/<service>` → service="students"
   - Validates JWT token
   - Checks service exists in SERVICES map
   - Builds target URL: `http://localhost:5001/api/students`
   - Adds user headers: X-User-ID, X-Username, X-Role
   - Forwards GET request

3. **Student Service Processing:**
   - Receives: `GET http://localhost:5001/api/students`
   - Route matches: Blueprint('/api') + route('/students')
   - Returns JSON: `{count: N, students: [...]}`

4. **API Gateway → Dashboard:**
   - Forwards response with same status code
   - Dashboard displays students in table

### Example: Add New Student

1. **Dashboard → API Gateway:**
   ```
   POST http://localhost:5000/api/students
   Authorization: Bearer <token>
   Content-Type: application/json

   {
     "id": "S001",
     "name": "Ahmad Hassan",
     "department": "Computer Science",
     "email": "ahmad@university.edu"
   }
   ```

2. **API Gateway Processing:**
   - Route matches: `/api/<service>` → service="students"
   - Validates token
   - Builds target: `http://localhost:5001/api/students`
   - Forwards POST with JSON body

3. **Student Service Processing:**
   - Validates required fields
   - Checks if student exists
   - Saves to database
   - Returns: `{message: "Student created successfully", student_id: "S001"}`

4. **Dashboard:**
   - Closes modal
   - Reloads student list
   - Updates statistics

## Testing the Fix

### Method 1: Use Browser

1. Open: http://localhost:5000
2. Login: admin / admin123
3. Press F12 → Console
4. You should see successful API responses
5. Try adding a student - should work!

### Method 2: Use Test Script

```powershell
.\test-dashboard.ps1
```

All tests should pass:
- [1/5] API Gateway ✓
- [2/5] Auth Service ✓
- [3/5] Dashboard HTML ✓
- [4/5] JavaScript file ✓
- [5/5] Login API ✓

### Method 3: Direct API Test

```powershell
# Login to get token
$response = Invoke-RestMethod -Uri "http://localhost:5000/api/auth/login" `
    -Method POST `
    -ContentType "application/json" `
    -Body '{"username":"admin","password":"admin123"}'

$token = $response.token

# Test students endpoint
Invoke-RestMethod -Uri "http://localhost:5000/api/students" `
    -Headers @{"Authorization"="Bearer $token"}
```

Should return: `{count: 0, students: []}`

## Microservice Endpoints Reference

### Student Service (Port 5001)
- `GET /api/students` - Get all students
- `GET /api/students/<id>` - Get student by ID
- `POST /api/students` - Create student
- `PUT /api/students/<id>` - Update student
- `DELETE /api/students/<id>` - Delete student

### Course Service (Port 5002)
- `GET /api/courses` - Get all courses
- `GET /api/courses/<id>` - Get course by ID
- `POST /api/courses` - Create course
- `PUT /api/courses/<id>` - Update course
- `DELETE /api/courses/<id>` - Delete course

### Attendance Service (Port 5005)
- `GET /api/attendance` - Get all attendance records
- `GET /api/attendance/student/<id>` - Get by student
- `GET /api/attendance/course/<id>` - Get by course
- `POST /api/attendance/record` - Record attendance

### Other Services
- **Auth Service:** Port 5007
- **Bubble Sheet Generator:** Port 5003
- **PDF Processing:** Port 5004
- **Reporting Service:** Port 5009
- **Service Registry:** Port 5008

## Port Summary Table

| Service | Port | Status |
|---------|------|--------|
| API Gateway | 5000 | Dashboard + Routing |
| Student Service | 5001 | CRUD Operations |
| Course Service | 5002 | CRUD Operations |
| Bubble Sheet Generator | 5003 | PDF Generation |
| PDF Processing | 5004 | OMR Processing |
| Attendance Service | 5005 | Attendance Tracking |
| Auth Service | 5007 | JWT Authentication |
| Service Registry | 5008 | Service Discovery |
| Reporting Service | 5009 | Excel/PDF Reports |

## What Should Work Now

✅ Login with admin/admin123
✅ Dashboard loads with navigation
✅ View students (empty initially)
✅ Add new student
✅ Delete student
✅ View courses (empty initially)
✅ Add new course
✅ Delete course
✅ View attendance (empty initially)
✅ All API calls return proper responses
✅ Error messages display correctly

## If Issues Persist

1. **Restart all services:**
   ```powershell
   .\STOP.ps1
   Start-Sleep -Seconds 10
   .\START.ps1
   ```

2. **Check browser console (F12 → Console):**
   - Should see: "Login successful, saving token..."
   - Should NOT see: "404" errors

3. **Check Network tab (F12 → Network):**
   - All /api/* requests should return 200 OK
   - Check Response preview for actual data

4. **Verify all services running:**
   - Should have 9 PowerShell windows open
   - Each showing service startup messages
   - No error messages in any window

## Next Steps After Fix

1. **Add Sample Data:**
   - Add 5-10 students
   - Add 2-3 courses

2. **Test Full Workflow:**
   - Generate bubble sheets
   - Process scanned sheets
   - View attendance records
   - Generate reports

3. **Verify Integration:**
   - All services communicate correctly
   - Circuit breakers work
   - Timeouts are reasonable
   - Error handling is graceful

## Summary

The API Gateway routing is now fixed with:
1. Proper URL building that includes service name
2. Route for service root endpoints
3. Correct port mappings for all services
4. Improved error logging and debugging

The system is now fully functional from frontend to backend!
