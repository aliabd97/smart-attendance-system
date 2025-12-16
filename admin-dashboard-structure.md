# Admin Dashboard Structure

## Features to Implement

### 1. Authentication
- Login page
- JWT token management
- Protected routes

### 2. Students Management
- View all students
- Add/Edit/Delete students
- Upload Excel file (bulk import)
- Search and filter

### 3. Courses Management
- View all courses
- Add/Edit/Delete courses
- Assign students to courses
- View course details

### 4. Attendance Management
- View attendance records
- Manual attendance marking
- Filter by date/course/student

### 5. Bubble Sheet Operations
- Generate bubble sheets for lectures
- Upload scanned sheets (PDF)
- Process OMR
- View processing results

### 6. Reports
- Generate student reports (Excel/PDF)
- Generate course reports (Excel/PDF)
- Department summaries
- Absence alerts
- Download reports

### 7. Dashboard (Home)
- Statistics overview
- Recent activities
- At-risk students
- Quick actions

## Technology Stack

### Frontend
- React 18
- React Router v6 (routing)
- Axios (HTTP requests)
- Material-UI (MUI) or Ant Design (components)
- Recharts or Chart.js (charts)
- React Query (data fetching)

### State Management
- React Context API or Redux Toolkit

### File Upload
- react-dropzone

### PDF Viewer
- react-pdf

## API Integration

All API calls will go through the API Gateway:
- Base URL: `https://attendance-api-gateway.onrender.com` (production)
- Base URL: `http://localhost:5000` (development)

## Pages Structure

```
/login                  - Login page
/                       - Dashboard home
/students               - Students list
/students/add           - Add student
/students/edit/:id      - Edit student
/students/upload        - Upload Excel
/courses                - Courses list
/courses/add            - Add course
/courses/edit/:id       - Edit course
/courses/:id/students   - Course students
/attendance             - Attendance records
/attendance/mark        - Manual marking
/bubble-sheets/generate - Generate sheets
/bubble-sheets/upload   - Upload scanned sheets
/bubble-sheets/results  - Processing results
/reports                - Reports page
```
