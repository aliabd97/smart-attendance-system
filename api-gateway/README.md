# API Gateway

**Port:** 5000

## Overview

The API Gateway is the central entry point for all microservices. It handles JWT authentication and routes requests to appropriate services.

## Features

✅ **JWT Authentication**
- Validates tokens for all protected routes
- Forwards user info to services

✅ **Request Routing**
- Routes requests to correct microservice
- Handles timeouts and connection errors

✅ **Health Monitoring**
- Checks health of all services
- Reports service availability

## Installation

```bash
cd api-gateway
pip install -r requirements.txt
```

## Running the Service

```bash
python app.py
```

The gateway will start on `http://localhost:5000`

## Request Flow

```
1. Client → API Gateway (with JWT token)
2. Gateway validates token
3. Gateway forwards request to microservice
4. Microservice processes request
5. Gateway returns response to client
```

## Endpoint Format

```
http://localhost:5000/api/<service>/<path>
```

Examples:
- `/api/students/students` → Student Service
- `/api/courses/courses` → Course Service
- `/api/attendance/attendance` → Attendance Service

## API Endpoints

### Gateway Health
```http
GET /
GET /api/health        # Check all services
GET /api/services      # List all services
```

### Authentication (No Token Required)
```http
POST /api/auth/login
POST /api/auth/register
POST /api/auth/validate
```

### Protected Routes (Token Required)

**Students**
```http
GET    /api/students/students
POST   /api/students/students
GET    /api/students/students/{id}
POST   /api/students/import-excel
```

**Courses**
```http
GET    /api/courses/courses
POST   /api/courses/courses
POST   /api/courses/{id}/enroll
GET    /api/courses/{id}/students
```

**Attendance**
```http
POST   /api/attendance/attendance
GET    /api/attendance/attendance
GET    /api/attendance/student/{id}
```

## Testing

### 1. Check Gateway Health
```bash
curl http://localhost:5000/
curl http://localhost:5000/api/health
```

### 2. Login (Get Token)
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

Save the token from response.

### 3. Use Token to Access Protected Route
```bash
curl http://localhost:5000/api/students/students \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### 4. Create Student via Gateway
```bash
curl -X POST http://localhost:5000/api/students/students \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "20210001",
    "name": "Ahmed Ali",
    "email": "ahmed@university.edu",
    "department": "Computer Science",
    "level": 3
  }'
```

## Service Registry

The gateway maintains URLs for all services:

```python
SERVICES = {
    'students': 'http://localhost:5001',
    'courses': 'http://localhost:5002',
    'bubble-sheet': 'http://localhost:5003',
    'pdf-processing': 'http://localhost:5004',
    'attendance': 'http://localhost:5005',
    'reporting': 'http://localhost:5006',
    'auth': 'http://localhost:5007',
    'registry': 'http://localhost:5008',
}
```

## Error Handling

- **401 Unauthorized** - Invalid or missing token
- **404 Not Found** - Service or endpoint not found
- **503 Service Unavailable** - Target service unreachable
- **504 Gateway Timeout** - Service took too long to respond

## Dependencies

- Flask 3.0.0 - Web framework
- Flask-CORS 4.0.0 - Cross-origin support
- requests 2.31.0 - HTTP client
- PyJWT 2.8.0 - JWT validation
- python-dotenv 1.0.0 - Environment variables

## Environment Variables

```bash
JWT_SECRET_KEY=your-secret-key
STUDENT_SERVICE_URL=http://localhost:5001
COURSE_SERVICE_URL=http://localhost:5002
# ... etc
```

## Success Criteria

- ✅ Gateway starts on port 5000
- ✅ JWT validation working
- ✅ Request routing working
- ✅ All services reachable
- ✅ Error handling implemented
