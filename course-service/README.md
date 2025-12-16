# Course Management Service

**Port:** 5002

## Overview

The Course Management Service handles all course-related operations including CRUD operations and student enrollment management.

## Features

✅ **Course Management**
- Create, Read, Update, Delete courses
- Filter courses by department
- Course code uniqueness validation

✅ **Enrollment Management**
- Enroll students in courses
- Unenroll students from courses
- Get enrolled students for a course
- Get courses for a student

✅ **SQLite Database**
- Independent `courses.db` database
- Two tables: `courses` and `enrollments`

## Installation

```bash
cd course-service
pip install -r requirements.txt
```

## Running the Service

```bash
python app.py
```

The service will start on `http://localhost:5002`

## API Endpoints

### Health Check
```http
GET /
GET /api/health
```

### Course CRUD

**Get All Courses**
```http
GET /api/courses
```

**Get Course by ID**
```http
GET /api/courses/{course_id}
```

**Create Course**
```http
POST /api/courses
Content-Type: application/json

{
    "id": "CS101",
    "name": "Introduction to Computer Science",
    "code": "CS101",
    "department": "Computer Science",
    "credits": 3,
    "instructor": "Dr. Ahmed Ali",
    "semester": "Fall",
    "academic_year": "2024-2025"
}
```

**Update Course**
```http
PUT /api/courses/{course_id}
Content-Type: application/json

{
    "name": "Advanced Computer Science",
    "instructor": "Dr. Mohammed Hassan"
}
```

**Delete Course**
```http
DELETE /api/courses/{course_id}
```

**Get Courses by Department**
```http
GET /api/courses/department/Computer%20Science
```

### Enrollment Management

**Enroll Student in Course**
```http
POST /api/courses/{course_id}/enroll
Content-Type: application/json

{
    "student_id": "20210001"
}
```

**Unenroll Student from Course**
```http
POST /api/courses/{course_id}/unenroll
Content-Type: application/json

{
    "student_id": "20210001"
}
```

**Get Enrolled Students**
```http
GET /api/courses/{course_id}/students
```

**Get Student's Courses**
```http
GET /api/students/{student_id}/courses
```

## Testing

### 1. Test Health Check
```bash
curl http://localhost:5002/
```

### 2. Create a Course
```bash
curl -X POST http://localhost:5002/api/courses \
  -H "Content-Type: application/json" \
  -d '{
    "id": "CS101",
    "name": "Introduction to Computer Science",
    "code": "CS101",
    "department": "Computer Science",
    "credits": 3,
    "instructor": "Dr. Ahmed Ali"
  }'
```

### 3. Get All Courses
```bash
curl http://localhost:5002/api/courses
```

### 4. Enroll a Student
```bash
curl -X POST http://localhost:5002/api/courses/CS101/enroll \
  -H "Content-Type: application/json" \
  -d '{"student_id": "20210001"}'
```

### 5. Get Enrolled Students
```bash
curl http://localhost:5002/api/courses/CS101/students
```

## Database Schema

```sql
CREATE TABLE courses (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    code TEXT UNIQUE NOT NULL,
    department TEXT,
    credits INTEGER,
    instructor TEXT,
    semester TEXT,
    academic_year TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE enrollments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT NOT NULL,
    course_id TEXT NOT NULL,
    enrollment_date DATE,
    status TEXT DEFAULT 'active',
    UNIQUE(student_id, course_id)
);
```

## Dependencies

- Flask 3.0.0 - Web framework
- Flask-CORS 4.0.0 - Cross-origin support
- pika 1.3.2 - RabbitMQ client
- python-dotenv 1.0.0 - Environment variables

## Architecture

```
course-service/
├── models/
│   └── course.py           # Course & Enrollment models
├── routes/
│   └── course_routes.py    # API endpoints
├── app.py                  # Main Flask application
└── courses.db              # SQLite database
```

## Integration

The Course Service integrates with:
- **Student Service** (5001) - Validates student IDs
- **Attendance Service** (5005) - Provides enrollment data
- **Bubble Sheet Generator** (5003) - Provides student lists

## Success Criteria

- ✅ Service starts on port 5002
- ✅ All CRUD endpoints working
- ✅ Enrollment management functional
- ✅ Database operations successful
- ✅ Validation working correctly
