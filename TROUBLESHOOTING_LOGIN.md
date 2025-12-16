# Login Troubleshooting Guide

## Problem: Cannot login to dashboard

The backend API is confirmed working (tested successfully with curl). This means the issue is in the frontend.

## Diagnostic Steps

### Step 1: Check if all services are running

Open PowerShell and run:
```powershell
.\check-services.ps1
```

Make sure ALL services show "✓ Running" including:
- Service Registry (Port 5008)
- Auth Service (Port 5007)
- API Gateway (Port 5000)

### Step 2: Check Browser Console for JavaScript Errors

1. Open browser to: http://localhost:5000
2. Press **F12** to open Developer Tools
3. Click on the **Console** tab
4. You should see these messages:
   ```
   App.js loaded successfully
   Token from localStorage: not found
   DOM Content Loaded
   No saved session, showing login page
   ```

5. Try to login with **admin** / **admin123**
6. You should see:
   ```
   Login form submitted
   Attempting login for user: admin
   Sending login request to /api/auth/login
   Login response status: 200
   Login response data: {token: "...", username: "admin", role: "admin", ...}
   Login successful, saving token and redirecting to dashboard
   ```

### Step 3: Common Issues and Solutions

#### Issue 1: "app.js:1 Uncaught SyntaxError"
**Solution:** The JavaScript file has a syntax error. This shouldn't happen, but if it does, restart all services.

#### Issue 2: "Failed to fetch" or "Connection refused"
**Solution:**
- Auth Service is not running
- Run `.\START.ps1` again
- Wait for all services to fully start (about 30 seconds)

#### Issue 3: Console shows "404 Not Found" for app.js
**Solution:**
- The app.js file is not being served
- Check that `api-gateway/static/app.js` exists
- Restart API Gateway service

#### Issue 4: Login response shows error message
**Solution:**
- Check the error message in the console
- If it says "Invalid credentials", the username/password is wrong
- If it says "Service unavailable", Auth Service is down

#### Issue 5: Browser shows blank page
**Solution:**
- Clear browser cache: Ctrl+Shift+Delete
- Or use Incognito mode: Ctrl+Shift+N
- Try again

#### Issue 6: Login button doesn't respond when clicked
**Solution:**
- Check Console tab for JavaScript errors
- Make sure no browser extensions are blocking JavaScript
- Try a different browser (Chrome, Edge, Firefox)

### Step 4: Manual Test of API

Open PowerShell and test the API directly:

```powershell
curl -X POST http://localhost:5000/api/auth/login `
  -H "Content-Type: application/json" `
  -d '{\"username\":\"admin\",\"password\":\"admin123\"}'
```

You should see:
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "username": "admin",
  "role": "admin",
  "email": "admin@university.edu",
  "expires_in": 86400
}
```

If this works but the browser login doesn't, the issue is definitely in the frontend JavaScript.

### Step 5: Clear Browser Storage

1. Open Developer Tools (F12)
2. Go to **Application** tab (Chrome) or **Storage** tab (Firefox)
3. Click on **Local Storage** → **http://localhost:5000**
4. Right-click and select **Clear**
5. Refresh the page (F5)
6. Try logging in again

### Step 6: Check Network Tab

1. Open Developer Tools (F12)
2. Click on **Network** tab
3. Try to login
4. Look for the request to `/api/auth/login`
5. Click on it to see details:
   - **Status Code:** Should be 200
   - **Response:** Should contain the token
   - **Request Payload:** Should contain username and password

### Step 7: If nothing works - Full Reset

```powershell
# Stop all services
.\STOP.ps1

# Wait 10 seconds
Start-Sleep -Seconds 10

# Start all services again
.\START.ps1

# Wait for services to initialize (30 seconds)
Start-Sleep -Seconds 30

# Clear browser cache and try again
```

## Expected Behavior

When login works correctly:

1. You type username and password
2. Click "Login" button
3. Button shows "Logging in..." (disabled)
4. After 1-2 seconds:
   - Login page disappears
   - Dashboard appears with sidebar
   - Sidebar shows "Overview, Students, Courses, Attendance, Logout"
   - Main area shows statistics cards

## Default Credentials

- **Username:** admin
- **Password:** admin123

## Getting Help

If none of the above steps work, provide these details:

1. Screenshot of browser Console tab (F12 → Console)
2. Screenshot of browser Network tab (F12 → Network) showing the /api/auth/login request
3. Output of `.\check-services.ps1`
4. Browser name and version (Chrome, Firefox, Edge, etc.)

## Technical Details

**Frontend:**
- Dashboard: `api-gateway/static/dashboard.html`
- JavaScript: `api-gateway/static/app.js`
- Served by Flask from: `http://localhost:5000/`

**Backend:**
- Auth API: `http://localhost:5000/api/auth/login`
- Proxied to: `http://localhost:5007/login` (Auth Service)

**Authentication Flow:**
1. User submits login form
2. JavaScript sends POST to `/api/auth/login`
3. API Gateway proxies to Auth Service
4. Auth Service validates credentials
5. Returns JWT token
6. JavaScript saves token to localStorage
7. Redirects to dashboard
