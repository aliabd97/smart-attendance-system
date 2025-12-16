# 🚀 Quick Start Guide

## Prerequisites

1. **Python 3.9+** installed
2. **Docker Desktop** installed (for RabbitMQ)
3. **Git** (optional)

## Step 1: Install Dependencies

Open a terminal in the project root directory:

```bash
# Install dependencies for all services
pip install flask flask-cors pika requests pyjwt openpyxl python-dotenv
```

Or install for each service individually:

```bash
cd student-service
pip install -r requirements.txt
cd ..

cd course-service
pip install -r requirements.txt
cd ..

cd auth-service
pip install -r requirements.txt
cd ..

cd api-gateway
pip install -r requirements.txt
cd ..

cd attendance-service
pip install -r requirements.txt
cd ..

cd service-registry
pip install -r requirements.txt
cd ..
```

## Step 2: Start RabbitMQ

```bash
docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 \
  -e RABBITMQ_DEFAULT_USER=admin \
  -e RABBITMQ_DEFAULT_PASS=admin123 \
  rabbitmq:3-management
```

Wait 10-15 seconds for RabbitMQ to fully start.

## Step 3: Start All Services

### Option A: Using Startup Script (Windows)

```bash
start-all-services.bat
```

### Option B: Using Startup Script (Linux/Mac)

```bash
chmod +x start-all-services.sh
./start-all-services.sh
```

### Option C: Manual Start (6 terminals)

**Terminal 1 - Service Registry:**
```bash
cd service-registry
python app.py
```

**Terminal 2 - Auth Service:**
```bash
cd auth-service
python app.py
```

**Terminal 3 - Student Service:**
```bash
cd student-service
python app.py
```

**Terminal 4 - Course Service:**
```bash
cd course-service
python app.py
```

**Terminal 5 - Attendance Service:**
```bash
cd attendance-service
python app.py
```

**Terminal 6 - API Gateway:**
```bash
cd api-gateway
python app.py
```

## Step 4: Verify All Services Running

Open your browser and check:

- ✅ API Gateway: http://localhost:5000
- ✅ Student Service: http://localhost:5001
- ✅ Course Service: http://localhost:5002
- ✅ Attendance Service: http://localhost:5005
- ✅ Auth Service: http://localhost:5007
- ✅ Service Registry: http://localhost:5008
- ✅ RabbitMQ UI: http://localhost:15672 (admin/admin123)

## Step 5: Test the System

### 5.1 Login and Get Token

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"admin\",\"password\":\"admin123\"}"
```

**Response:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "username": "admin",
  "role": "admin",
  "expires_in": 86400
}
```

**Save the token!** You'll need it for all subsequent requests.

### 5.2 Import Sample Students

```bash
# Generate sample Excel file
cd student-service
python create_sample_excel.py

# Import via API
curl -X POST http://localhost:5000/api/students/import-excel \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -F "file=@sample_students.xlsx"
```

### 5.3 Create a Course

```bash
curl -X POST http://localhost:5000/api/courses/courses \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "CS101",
    "name": "Introduction to Computer Science",
    "code": "CS101",
    "department": "Computer Science",
    "credits": 3,
    "instructor": "Dr. Ahmed Ali",
    "semester": "Fall",
    "academic_year": "2024-2025"
  }'
```

### 5.4 Enroll a Student

```bash
curl -X POST http://localhost:5000/api/courses/courses/CS101/enroll \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"student_id": "20210001"}'
```

### 5.5 Record Attendance

```bash
curl -X POST http://localhost:5000/api/attendance/attendance \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "20210001",
    "course_id": "CS101",
    "date": "2024-12-15",
    "status": "present",
    "session_name": "Lecture 1"
  }'
```

### 5.6 View Attendance Report

```bash
curl "http://localhost:5000/api/attendance/attendance/student/20210001" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## 🎯 Success!

If all the above steps worked, you have successfully:

✅ Started all 6 microservices
✅ Authenticated with JWT
✅ Imported students using Excel Adapter Pattern
✅ Created a course
✅ Enrolled a student
✅ Recorded attendance with service validation
✅ Retrieved attendance report

## 🔧 Common Issues

### Port Already in Use

If you get "port already in use" errors:

```bash
# Windows - Find and kill process
netstat -ano | findstr "5000"
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:5000 | xargs kill -9
```

### RabbitMQ Not Starting

```bash
# Check Docker is running
docker ps

# Restart RabbitMQ
docker stop rabbitmq
docker rm rabbitmq
# Then run the docker run command again
```

### Cannot Connect to Service

1. Check the service is running (look at terminal output)
2. Check the port is correct
3. Try restarting the service

## 📚 Next Steps

- Read [README.md](README.md) for complete documentation
- Check individual service READMEs for detailed API docs
- Explore the codebase to understand design patterns
- Try implementing the remaining services (Bubble Sheet Generator, PDF Processing, Reporting)

## 💡 Tips

- Keep all terminal windows open to see service logs
- Use Postman or Thunder Client for easier API testing
- Check RabbitMQ Management UI to see message queues
- All databases are SQLite files in each service directory

---

**Happy Coding! 🎓**
