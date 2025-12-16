# Smart Attendance Management System - Complete Project Documentation
## For Claude Code Implementation

---

## 📋 PROJECT OVERVIEW

**Project Name:** Smart Attendance Management System Using Bubble Sheet Technology

**Architecture:** Microservices Architecture (6 independent services)

**Purpose:** Automate student attendance tracking using OMR (Optical Mark Recognition) technology with bubble sheets, replacing manual attendance recording.

**Target Users:** Universities and educational institutions in Iraq

**Expected Impact:** 
- Reduce attendance tracking time from 30 minutes to 2 minutes
- 95%+ accuracy in mark recognition
- Support for 90+ students per class
- Real-time attendance reports

---

## 🏗️ SYSTEM ARCHITECTURE

### Microservices Breakdown (6 Services):

```
1. Student Management Service (Port: 5001)
2. Course Management Service (Port: 5002)
3. Bubble Sheet Generator Service (Port: 5003)
4. PDF Processing Service (Port: 5004) - CORE SERVICE
5. Attendance Recording Service (Port: 5005)
6. Reporting & Analytics Service (Port: 5006)
```

### Communication Architecture:

**Synchronous Communication (REST API):**
- Used for: CRUD operations, queries, service validation
- Technology: Flask REST API over HTTP
- Use cases: <3 seconds operations

**Asynchronous Communication (RabbitMQ):**
- Used for: PDF processing, report generation, notifications
- Technology: RabbitMQ message broker
- Use cases: >10 seconds operations

**Message Queues:**
```
1. pdf_processing queue
2. attendance_recording queue  
3. report_generation queue
4. notifications queue
```

---

## 🗄️ DATABASE SCHEMA

### Each service has independent SQLite database:

#### 1. students.db (Student Service)
```sql
CREATE TABLE students (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE,
    department TEXT,
    level INTEGER,
    phone TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    registration_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 2. courses.db (Course Service)
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

#### 3. templates.db (Bubble Sheet Generator)
```sql
CREATE TABLE bubble_sheet_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id TEXT NOT NULL,
    date DATE NOT NULL,
    session_name TEXT,
    num_students INTEGER,
    pdf_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 4. processing_logs.db (PDF Processing)
```sql
CREATE TABLE processing_jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id TEXT NOT NULL,
    date DATE NOT NULL,
    pdf_path TEXT,
    status TEXT DEFAULT 'pending',
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT,
    num_students_detected INTEGER,
    accuracy_score REAL
);
```

#### 5. attendance.db (Attendance Recording)
```sql
CREATE TABLE attendance_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT NOT NULL,
    course_id TEXT NOT NULL,
    date DATE NOT NULL,
    status TEXT NOT NULL,
    session_name TEXT,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(student_id, course_id, date, session_name)
);
```

#### 6. reports.db (Reporting Service)
```sql
CREATE TABLE report_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_type TEXT NOT NULL,
    course_id TEXT,
    student_id TEXT,
    date_from DATE,
    date_to DATE,
    data TEXT,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🔄 DESIGN PATTERNS IMPLEMENTATION

### 1. Adapter Pattern (Student Service)

**Location:** `student-service/adapters/`

**Purpose:** Translate legacy Excel files to modern JSON/SQLite format

**Components:**
```python
# Interface
class IStudentDataSource(ABC):
    @abstractmethod
    def get_student_by_id(self, student_id: str) -> Optional[Student]
    
    @abstractmethod
    def get_all_students(self) -> List[Student]
    
    @abstractmethod
    def save_student(self, student: Student) -> bool

# Adapter
class ExcelAdapter(IStudentDataSource):
    def __init__(self, file_path: str):
        self.excel_reader = ExcelReader()
        self.field_mapper = FieldMapper()
        self.value_transformer = ValueTransformer()
    
    # Implementation of interface methods...

# Helpers
class FieldMapper:
    # Student_No → id
    # Full_Name → name
    # Dept → department
    
class ValueTransformer:
    # "CS" → "Computer Science"
    # "3" → 3
    # "Active" → True
```

**Field Mapping:**
```
Excel (Old)          →  Modern (New)
Student_No           →  id
Full_Name            →  name
Email_Address        →  email
Dept                 →  department
Year                 →  level
Mobile               →  phone
Status               →  is_active
Reg_Date             →  registration_date
```

**Value Transformation:**
```
Excel Value          →  Modern Value
"CS"                 →  "Computer Science"
"IT"                 →  "Information Technology"
"SE"                 →  "Software Engineering"
"3" (text)           →  3 (integer)
"Active"             →  True (boolean)
"Inactive"           →  False (boolean)
"01/12/2024"         →  "2024-12-01" (ISO format)
```

### 2. Breaking Foreign Keys Pattern (Attendance Service)

**Challenge:** Cannot use Foreign Keys across separate databases in microservices.

**Solution:** Service-to-Service Validation

**Implementation:**
```python
# attendance-service/validators/service_validator.py

class ServiceValidator:
    def validate_student_exists(self, student_id: str) -> bool:
        """Call Student Service to check if student exists"""
        response = requests.get(f'http://student-service:5001/api/students/{student_id}')
        return response.status_code == 200
    
    def validate_course_exists(self, course_id: str) -> bool:
        """Call Course Service to check if course exists"""
        response = requests.get(f'http://course-service:5002/api/courses/{course_id}')
        return response.status_code == 200
    
    def validate_before_recording(self, student_id: str, course_id: str) -> tuple[bool, str]:
        """Validate both student and course before recording attendance"""
        if not self.validate_student_exists(student_id):
            return False, f"Student {student_id} does not exist"
        
        if not self.validate_course_exists(course_id):
            return False, f"Course {course_id} does not exist"
        
        return True, "Validation successful"
```

**Flow:**
```
1. Attendance Service receives attendance data
2. Validate student_id with Student Service (sync API call)
3. Validate course_id with Course Service (sync API call)
4. If both valid → Save attendance record
5. If either invalid → Reject with error message
```

---

## 📡 API ENDPOINTS SPECIFICATION

### Service 1: Student Management Service (Port 5001)

**Base URL:** `http://localhost:5001/api`

```
GET    /students                    - Get all students
GET    /students/{id}               - Get student by ID
POST   /students                    - Create new student
PUT    /students/{id}               - Update student
DELETE /students/{id}               - Delete student
POST   /students/import-excel       - Import from Excel using Adapter
GET    /students/search?q={query}   - Search students
GET    /students/department/{dept}  - Get students by department
```

**Request/Response Examples:**

```json
// POST /students
{
    "id": "20210001",
    "name": "Ahmed Ali Mohammed",
    "email": "ahmed@university.edu",
    "department": "Computer Science",
    "level": 3,
    "phone": "07712345678",
    "is_active": true
}

// Response 201 Created
{
    "message": "Student created successfully",
    "student_id": "20210001"
}
```

### Service 2: Course Management Service (Port 5002)

**Base URL:** `http://localhost:5002/api`

```
GET    /courses                     - Get all courses
GET    /courses/{id}                - Get course by ID
POST   /courses                     - Create new course
PUT    /courses/{id}                - Update course
DELETE /courses/{id}                - Delete course
POST   /courses/{id}/enroll         - Enroll student in course
GET    /courses/{id}/students       - Get enrolled students
```

### Service 3: Bubble Sheet Generator (Port 5003)

**Base URL:** `http://localhost:5003/api`

```
POST   /generate                    - Generate bubble sheet PDF
GET    /templates                   - List all templates
GET    /templates/{id}              - Get template by ID
GET    /download/{id}               - Download generated PDF
```

**Request Example:**
```json
// POST /generate
{
    "course_id": "CS101",
    "date": "2024-12-15",
    "session_name": "Lecture 10",
    "student_ids": ["20210001", "20210002", "..."]
}

// Response
{
    "template_id": 123,
    "pdf_url": "/download/123",
    "num_students": 90
}
```

### Service 4: PDF Processing Service (Port 5004) - CORE

**Base URL:** `http://localhost:5004/api`

```
POST   /process                     - Start PDF processing (async)
GET    /jobs                        - List processing jobs
GET    /jobs/{id}                   - Get job status
GET    /jobs/{id}/results           - Get processing results
```

**Processing Flow:**
```
1. Receive PDF upload
2. Publish to RabbitMQ pdf_processing queue
3. Return job_id immediately (async)
4. Worker processes PDF with OpenCV
5. Extract bubble marks (OMR)
6. Publish results to attendance_recording queue
7. Update job status
```

### Service 5: Attendance Recording (Port 5005)

**Base URL:** `http://localhost:5005/api`

```
POST   /attendance                  - Record attendance
GET    /attendance                  - Query attendance records
GET    /attendance/student/{id}     - Student attendance history
GET    /attendance/course/{id}      - Course attendance records
GET    /attendance/date/{date}      - Attendance by date
```

### Service 6: Reporting & Analytics (Port 5006)

**Base URL:** `http://localhost:5006/api`

```
GET    /reports/student/{id}        - Student attendance report
GET    /reports/course/{id}         - Course attendance summary
GET    /reports/department/{dept}   - Department statistics
POST   /reports/custom              - Generate custom report
GET    /export/excel                - Export to Excel
GET    /export/pdf                  - Export to PDF
```

---

## 🐰 RABBITMQ CONFIGURATION

### Queue Definitions:

```python
# rabbitmq_config.py

QUEUES = {
    'pdf_processing': {
        'durable': True,
        'auto_delete': False,
        'arguments': {
            'x-message-ttl': 3600000,  # 1 hour
            'x-max-length': 1000
        }
    },
    'attendance_recording': {
        'durable': True,
        'auto_delete': False
    },
    'report_generation': {
        'durable': True,
        'auto_delete': False
    },
    'notifications': {
        'durable': True,
        'auto_delete': False
    }
}
```

### Message Format:

```json
// PDF Processing Message
{
    "job_id": "job_123",
    "course_id": "CS101",
    "date": "2024-12-15",
    "pdf_path": "/uploads/cs101_2024-12-15.pdf",
    "callback_url": "http://attendance-service:5005/api/attendance/bulk"
}

// Attendance Recording Message
{
    "job_id": "job_123",
    "course_id": "CS101",
    "date": "2024-12-15",
    "records": [
        {"student_id": "20210001", "status": "present"},
        {"student_id": "20210002", "status": "present"},
        {"student_id": "20210003", "status": "absent"}
    ]
}
```

### RabbitMQ Setup:

```python
# common/rabbitmq_client.py

import pika

class RabbitMQClient:
    def __init__(self, host='localhost'):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=host)
        )
        self.channel = self.connection.channel()
        self._setup_queues()
    
    def _setup_queues(self):
        for queue_name, config in QUEUES.items():
            self.channel.queue_declare(
                queue=queue_name,
                **config
            )
    
    def publish(self, queue_name: str, message: dict):
        self.channel.basic_publish(
            exchange='',
            routing_key=queue_name,
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2,  # persistent
            )
        )
    
    def consume(self, queue_name: str, callback):
        self.channel.basic_consume(
            queue=queue_name,
            on_message_callback=callback,
            auto_ack=False
        )
        self.channel.start_consuming()
```

---

## 🖼️ PDF PROCESSING IMPLEMENTATION

### Bubble Sheet Layout:

```
┌─────────────────────────────────────────────┐
│  Course: CS101    Date: 2024-12-15          │
│  Session: Lecture 10                        │
├─────────────────────────────────────────────┤
│  Student ID: [○][○][○][○][○][○][○][○]      │
│              [0][1][2][3][4][5][6][7][8][9] │
│                                             │
│  Attendance Status:                         │
│     [●] Present                             │
│     [○] Absent                              │
│     [○] Late                                │
│     [○] Excused                             │
└─────────────────────────────────────────────┘
```

### OpenCV Processing Steps:

```python
# pdf-processing-service/processors/omr_processor.py

import cv2
import numpy as np

class OMRProcessor:
    def process_bubble_sheet(self, pdf_path: str) -> list:
        """
        Process scanned bubble sheet using OpenCV
        Returns list of attendance records
        """
        # Step 1: Convert PDF to images
        images = self.pdf_to_images(pdf_path)
        
        results = []
        for image in images:
            # Step 2: Preprocessing
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
            
            # Step 3: Find contours (bubbles)
            contours = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
            
            # Step 4: Filter bubble contours
            bubbles = self.filter_bubble_contours(contours)
            
            # Step 5: Extract student ID
            student_id = self.extract_student_id(bubbles)
            
            # Step 6: Extract attendance status
            status = self.extract_attendance_status(bubbles)
            
            results.append({
                'student_id': student_id,
                'status': status
            })
        
        return results
    
    def is_bubble_filled(self, bubble_roi) -> bool:
        """Check if bubble is filled (>60% dark pixels)"""
        total_pixels = bubble_roi.shape[0] * bubble_roi.shape[1]
        filled_pixels = cv2.countNonZero(bubble_roi)
        fill_percentage = (filled_pixels / total_pixels) * 100
        return fill_percentage > 60
```

### Processing Time Estimates:
```
- Single bubble sheet: 2-3 seconds
- Class of 30 students: 60-90 seconds
- Class of 90 students: 180-270 seconds (3-4.5 minutes)
```

---

## 📁 PROJECT STRUCTURE

```
smart-attendance-system/
│
├── common/                          # Shared utilities
│   ├── __init__.py
│   ├── rabbitmq_client.py
│   ├── database.py
│   └── utils.py
│
├── student-service/                 # Service 1
│   ├── app.py                       # Flask app
│   ├── models/
│   │   └── student.py
│   ├── adapters/                    # Adapter Pattern
│   │   ├── excel_adapter.py
│   │   ├── field_mapper.py
│   │   └── value_transformer.py
│   ├── routes/
│   │   └── student_routes.py
│   ├── students.db
│   ├── requirements.txt
│   └── README.md
│
├── course-service/                  # Service 2
│   ├── app.py
│   ├── models/
│   │   ├── course.py
│   │   └── enrollment.py
│   ├── routes/
│   │   └── course_routes.py
│   ├── courses.db
│   └── requirements.txt
│
├── bubble-sheet-generator/          # Service 3
│   ├── app.py
│   ├── generators/
│   │   └── pdf_generator.py
│   ├── templates/
│   │   └── bubble_sheet_template.html
│   ├── templates.db
│   └── requirements.txt
│
├── pdf-processing-service/          # Service 4 (CORE)
│   ├── app.py
│   ├── processors/
│   │   └── omr_processor.py
│   ├── workers/
│   │   └── pdf_worker.py           # RabbitMQ consumer
│   ├── processing_logs.db
│   └── requirements.txt
│
├── attendance-service/              # Service 5
│   ├── app.py
│   ├── models/
│   │   └── attendance.py
│   ├── validators/
│   │   └── service_validator.py    # Breaking FK Pattern
│   ├── routes/
│   │   └── attendance_routes.py
│   ├── attendance.db
│   └── requirements.txt
│
├── reporting-service/               # Service 6
│   ├── app.py
│   ├── generators/
│   │   ├── excel_generator.py
│   │   └── pdf_generator.py
│   ├── routes/
│   │   └── report_routes.py
│   ├── reports.db
│   └── requirements.txt
│
├── docker-compose.yml               # Deploy all services
├── .env                             # Environment variables
└── README.md                        # Main documentation
```

---

## 🐳 DOCKER DEPLOYMENT

### docker-compose.yml:

```yaml
version: '3.8'

services:
  rabbitmq:
    image: rabbitmq:3-management
    ports:
      - "5672:5672"
      - "15672:15672"
    environment:
      RABBITMQ_DEFAULT_USER: admin
      RABBITMQ_DEFAULT_PASS: admin123

  student-service:
    build: ./student-service
    ports:
      - "5001:5001"
    environment:
      - RABBITMQ_HOST=rabbitmq
    depends_on:
      - rabbitmq

  course-service:
    build: ./course-service
    ports:
      - "5002:5002"
    depends_on:
      - rabbitmq

  bubble-sheet-generator:
    build: ./bubble-sheet-generator
    ports:
      - "5003:5003"
    depends_on:
      - rabbitmq

  pdf-processing-service:
    build: ./pdf-processing-service
    ports:
      - "5004:5004"
    environment:
      - RABBITMQ_HOST=rabbitmq
    depends_on:
      - rabbitmq

  attendance-service:
    build: ./attendance-service
    ports:
      - "5005:5005"
    environment:
      - RABBITMQ_HOST=rabbitmq
      - STUDENT_SERVICE_URL=http://student-service:5001
      - COURSE_SERVICE_URL=http://course-service:5002
    depends_on:
      - rabbitmq
      - student-service
      - course-service

  reporting-service:
    build: ./reporting-service
    ports:
      - "5006:5006"
    depends_on:
      - rabbitmq
```

---

## 📦 DEPENDENCIES

### Common Requirements (all services):
```
# requirements.txt
flask==3.0.0
flask-cors==4.0.0
pika==1.3.2
python-dotenv==1.0.0
```

### Service-Specific:

**Student Service:**
```
openpyxl==3.1.2
```

**Bubble Sheet Generator:**
```
reportlab==4.0.7
Pillow==10.1.0
```

**PDF Processing Service:**
```
opencv-python==4.8.1.78
numpy==1.26.2
pdf2image==1.16.3
pytesseract==0.3.10
```

**Reporting Service:**
```
openpyxl==3.1.2
reportlab==4.0.7
matplotlib==3.8.2
```

---

## 🔄 WORKFLOW EXAMPLES

### Complete Flow: Recording Attendance

```
1. Admin generates bubble sheet:
   POST /api/generate → bubble-sheet-generator:5003
   Response: PDF file with 90 student bubbles

2. Teacher prints and distributes bubble sheets

3. Students mark attendance (fill bubbles)

4. Teacher scans completed sheets → uploads PDF

5. Admin uploads PDF for processing:
   POST /api/process → pdf-processing-service:5004
   
6. PDF Processing Service:
   - Returns job_id immediately
   - Publishes to RabbitMQ pdf_processing queue
   
7. PDF Worker (async):
   - Consumes message from queue
   - Processes PDF with OpenCV (30-60 seconds)
   - Extracts 90 student records
   
8. For each student record:
   - Publishes to attendance_recording queue
   
9. Attendance Service:
   - Consumes from attendance_recording queue
   - Validates student_id (calls student-service:5001)
   - Validates course_id (calls course-service:5002)
   - If valid → saves attendance record
   - If invalid → logs error
   
10. Publishes to notifications queue

11. Admin receives notification:
    "90 students marked present in CS101"
    
12. Admin views report:
    GET /api/reports/course/CS101 → reporting-service:5006
```

---

## 🎯 SUCCESS CRITERIA

### Functional Requirements:
- ✅ 6 microservices running independently
- ✅ Synchronous API calls working (<3s response)
- ✅ Asynchronous processing via RabbitMQ
- ✅ Excel Adapter functioning (import/export)
- ✅ Service-to-Service validation working
- ✅ OMR processing 90+ students with 95% accuracy
- ✅ Real-time attendance reports

### Non-Functional Requirements:
- ✅ Each service can restart independently
- ✅ Queues persist messages (durable)
- ✅ API response times <3s for sync, immediate for async
- ✅ System handles 1000+ students
- ✅ Processing accuracy >95%

---

## 🚀 DEPLOYMENT STEPS

### Quick Start:

```bash
# 1. Clone repository
git clone <repo-url>
cd smart-attendance-system

# 2. Install RabbitMQ
docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management

# 3. Start each service
cd student-service && python app.py &
cd course-service && python app.py &
cd bubble-sheet-generator && python app.py &
cd pdf-processing-service && python app.py &
cd attendance-service && python app.py &
cd reporting-service && python app.py &

# 4. Verify all services
curl http://localhost:5001/
curl http://localhost:5002/
curl http://localhost:5003/
curl http://localhost:5004/
curl http://localhost:5005/
curl http://localhost:5006/

# 5. Check RabbitMQ
open http://localhost:15672
# Login: admin/admin123
```

---

## 📝 TESTING SCENARIOS

### Test 1: Import Students from Excel
```bash
curl -X POST http://localhost:5001/api/students/import-excel
# Expected: "Imported 500 students successfully"
```

### Test 2: Generate Bubble Sheet
```bash
curl -X POST http://localhost:5003/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "course_id": "CS101",
    "date": "2024-12-15",
    "student_ids": ["20210001", "20210002"]
  }'
# Expected: PDF download link
```

### Test 3: Process PDF (Async)
```bash
curl -X POST http://localhost:5004/api/process \
  -F "file=@attendance.pdf" \
  -F "course_id=CS101"
# Expected: {"job_id": "job_123", "status": "processing"}
```

### Test 4: Check Processing Status
```bash
curl http://localhost:5004/api/jobs/job_123
# Expected: {"status": "completed", "records_count": 90}
```

### Test 5: View Attendance Report
```bash
curl http://localhost:5006/api/reports/course/CS101
# Expected: Attendance statistics and records
```

---

## 🎓 NOTES FOR CLAUDE CODE

### Priority Order for Implementation:

1. **Phase 1: Foundation** (Week 1)
   - Common utilities (RabbitMQ client, database helper)
   - Student Service with Excel Adapter ✅ (already done)
   - Course Service (basic CRUD)

2. **Phase 2: Core Functionality** (Week 2)
   - Bubble Sheet Generator
   - PDF Processing Service (OMR with OpenCV)
   - RabbitMQ integration

3. **Phase 3: Integration** (Week 3)
   - Attendance Service with validation
   - Service-to-Service communication
   - End-to-end workflow testing

4. **Phase 4: Reporting** (Week 4)
   - Reporting Service
   - Excel/PDF export
   - Analytics and statistics

### Key Implementation Notes:

1. **Start Simple:** Each service should work standalone first
2. **Test Incrementally:** Test each API endpoint as you build
3. **RabbitMQ:** Set up queues early, test message publishing/consuming
4. **OpenCV:** PDF processing is the most complex - allocate time
5. **Validation:** Service-to-Service validation is critical - don't skip
6. **Error Handling:** Add try-catch blocks everywhere
7. **Logging:** Log all operations for debugging

### Common Pitfalls to Avoid:

- ❌ Don't hardcode URLs - use environment variables
- ❌ Don't forget to close database connections
- ❌ Don't ignore RabbitMQ acknowledgments
- ❌ Don't skip input validation
- ❌ Don't forget error responses (400, 404, 500)

---

## 📞 FINAL CHECKLIST

Before calling the project complete, verify:

- [ ] All 6 services start without errors
- [ ] RabbitMQ dashboard shows 4 queues
- [ ] Student Service: Import Excel works
- [ ] Course Service: CRUD operations work
- [ ] Bubble Sheet Generator: Generates PDF
- [ ] PDF Processing: Extracts attendance marks
- [ ] Attendance Service: Validates before saving
- [ ] Reporting Service: Generates reports
- [ ] End-to-end: Upload PDF → See attendance report
- [ ] Docker Compose: All services start together

---

## 🎯 EXPECTED DELIVERABLES

1. **Code Repository**
   - All 6 microservices
   - Docker configuration
   - README with setup instructions

2. **Documentation**
   - API documentation (endpoints, requests, responses)
   - Architecture diagrams
   - Database schemas

3. **Demo**
   - Import 500 students from Excel
   - Generate bubble sheet for CS101
   - Process scanned PDF
   - View attendance report

---

## 🔐 AUTHENTICATION & AUTHORIZATION

### Selected Approach: **JWT (JSON Web Tokens) with API Gateway**

**Why JWT over SSO:**
- Simpler to implement in microservices
- Stateless authentication
- No need for centralized auth server (simpler than SSO)
- Sufficient for academic project scope

**Architecture:**

```
Client → API Gateway → Microservices
         (JWT Validation)
```

### JWT Implementation:

#### 1. Authentication Service (New Service 7 - Port 5007)

```python
# auth-service/app.py

from flask import Flask, request, jsonify
import jwt
import datetime
from functools import wraps

app = Flask(__name__)
SECRET_KEY = "your-secret-key-change-in-production"

# Simple user store (in production: use database)
USERS = {
    "admin": {
        "password": "admin123",  # In production: hash with bcrypt
        "role": "admin"
    },
    "teacher": {
        "password": "teacher123",
        "role": "teacher"
    }
}

@app.route('/api/auth/login', methods=['POST'])
def login():
    """
    Login endpoint - returns JWT token
    """
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    # Validate credentials
    user = USERS.get(username)
    if not user or user['password'] != password:
        return jsonify({'error': 'Invalid credentials'}), 401
    
    # Generate JWT token
    token = jwt.encode({
        'username': username,
        'role': user['role'],
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }, SECRET_KEY, algorithm='HS256')
    
    return jsonify({
        'token': token,
        'username': username,
        'role': user['role']
    }), 200

def require_auth(f):
    """
    Decorator to protect endpoints
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'error': 'Token required'}), 401
        
        try:
            # Remove 'Bearer ' prefix if present
            if token.startswith('Bearer '):
                token = token[7:]
            
            # Decode and validate token
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            request.user = payload
            
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(*args, **kwargs)
    
    return decorated

if __name__ == '__main__':
    app.run(port=5007)
```

#### 2. API Gateway (New Service 8 - Port 5000)

```python
# api-gateway/app.py

from flask import Flask, request, jsonify
import requests
import jwt

app = Flask(__name__)
SECRET_KEY = "your-secret-key-change-in-production"

# Service registry
SERVICES = {
    'students': 'http://localhost:5001',
    'courses': 'http://localhost:5002',
    'bubble-sheet': 'http://localhost:5003',
    'pdf-processing': 'http://localhost:5004',
    'attendance': 'http://localhost:5005',
    'reporting': 'http://localhost:5006',
    'auth': 'http://localhost:5007'
}

def validate_token():
    """Validate JWT token from request"""
    token = request.headers.get('Authorization')
    
    if not token:
        return None, {'error': 'Token required'}, 401
    
    try:
        if token.startswith('Bearer '):
            token = token[7:]
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload, None, None
        
    except jwt.ExpiredSignatureError:
        return None, {'error': 'Token expired'}, 401
    except jwt.InvalidTokenError:
        return None, {'error': 'Invalid token'}, 401

@app.route('/api/auth/<path:path>', methods=['GET', 'POST'])
def auth_route(path):
    """Forward auth requests (no token required)"""
    url = f"{SERVICES['auth']}/api/auth/{path}"
    
    if request.method == 'GET':
        response = requests.get(url)
    else:
        response = requests.post(url, json=request.get_json())
    
    return jsonify(response.json()), response.status_code

@app.route('/api/<service>/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def gateway_route(service, path):
    """
    Main gateway - validates token then forwards request
    """
    # Validate token
    user, error, status = validate_token()
    if error:
        return jsonify(error), status
    
    # Check if service exists
    if service not in SERVICES:
        return jsonify({'error': 'Service not found'}), 404
    
    # Forward request to service
    url = f"{SERVICES[service]}/api/{path}"
    headers = {'X-User': user['username'], 'X-Role': user['role']}
    
    try:
        if request.method == 'GET':
            response = requests.get(url, headers=headers, params=request.args)
        elif request.method == 'POST':
            response = requests.post(url, headers=headers, json=request.get_json())
        elif request.method == 'PUT':
            response = requests.put(url, headers=headers, json=request.get_json())
        elif request.method == 'DELETE':
            response = requests.delete(url, headers=headers)
        
        return jsonify(response.json()), response.status_code
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000)
```

#### 3. Update Microservices to Read User Info

```python
# Example: student-service/app.py

@app.route('/api/students', methods=['POST'])
def create_student():
    # Get user info from gateway
    username = request.headers.get('X-User')
    role = request.headers.get('X-Role')
    
    # Check permissions
    if role != 'admin':
        return jsonify({'error': 'Admin only'}), 403
    
    # Process request...
```

### Authentication Flow:

```
1. Client: POST /api/auth/login
   Body: {"username": "admin", "password": "admin123"}
   Response: {"token": "eyJhbGc..."}

2. Client stores token

3. Client: GET /api/students/students
   Headers: {"Authorization": "Bearer eyJhbGc..."}
   
4. API Gateway:
   - Validates token
   - Extracts user info
   - Forwards to Student Service with X-User header
   
5. Student Service:
   - Checks X-User header
   - Processes request
   - Returns response
   
6. API Gateway forwards response to client
```

---

## 🔄 CI/CD AUTOMATION WITH ANSIBLE

### Selected Tool: **Ansible**

**Why Ansible:**
- Agentless (no need to install anything on target servers)
- Simple YAML syntax
- Wide acceptance in industry
- Perfect for deployment automation

### Ansible Project Structure:

```
ansible/
├── ansible.cfg
├── inventory.ini
├── playbooks/
│   ├── deploy-all.yml
│   ├── deploy-service.yml
│   └── setup-environment.yml
├── roles/
│   ├── common/
│   ├── docker/
│   ├── rabbitmq/
│   └── microservice/
└── group_vars/
    └── all.yml
```

### 1. Inventory File (inventory.ini)

```ini
[local]
localhost ansible_connection=local

[production]
prod-server-1 ansible_host=192.168.1.100 ansible_user=deploy

[staging]
stage-server-1 ansible_host=192.168.1.101 ansible_user=deploy
```

### 2. Main Deployment Playbook (deploy-all.yml)

```yaml
---
- name: Deploy Smart Attendance Management System
  hosts: local
  become: yes
  
  vars:
    project_root: /opt/smart-attendance
    services:
      - name: student-service
        port: 5001
      - name: course-service
        port: 5002
      - name: bubble-sheet-generator
        port: 5003
      - name: pdf-processing-service
        port: 5004
      - name: attendance-service
        port: 5005
      - name: reporting-service
        port: 5006
      - name: auth-service
        port: 5007
      - name: api-gateway
        port: 5000
  
  tasks:
    # Step 1: System Setup
    - name: Update apt cache
      apt:
        update_cache: yes
      tags: setup
    
    - name: Install required packages
      apt:
        name:
          - python3
          - python3-pip
          - docker.io
          - docker-compose
        state: present
      tags: setup
    
    # Step 2: Install RabbitMQ
    - name: Start RabbitMQ container
      docker_container:
        name: rabbitmq
        image: rabbitmq:3-management
        state: started
        restart_policy: always
        ports:
          - "5672:5672"
          - "15672:15672"
        env:
          RABBITMQ_DEFAULT_USER: admin
          RABBITMQ_DEFAULT_PASS: admin123
      tags: rabbitmq
    
    # Step 3: Create project directory
    - name: Create project directory
      file:
        path: "{{ project_root }}"
        state: directory
        mode: '0755'
      tags: setup
    
    # Step 4: Deploy each service
    - name: Deploy microservices
      include_tasks: deploy-service.yml
      loop: "{{ services }}"
      loop_control:
        loop_var: service
      tags: deploy
    
    # Step 5: Health check
    - name: Wait for services to be healthy
      uri:
        url: "http://localhost:{{ item.port }}/"
        status_code: 200
      loop: "{{ services }}"
      register: result
      until: result.status == 200
      retries: 10
      delay: 3
      tags: healthcheck
    
    # Step 6: Display status
    - name: Display deployment status
      debug:
        msg: "All services deployed successfully!"
      tags: status
```

### 3. Service Deployment Task (deploy-service.yml)

```yaml
---
- name: "Deploy {{ service.name }}"
  block:
    - name: "Create {{ service.name }} directory"
      file:
        path: "{{ project_root }}/{{ service.name }}"
        state: directory
    
    - name: "Copy {{ service.name }} files"
      copy:
        src: "../{{ service.name }}/"
        dest: "{{ project_root }}/{{ service.name }}/"
    
    - name: "Install {{ service.name }} dependencies"
      pip:
        requirements: "{{ project_root }}/{{ service.name }}/requirements.txt"
        virtualenv: "{{ project_root }}/{{ service.name }}/venv"
    
    - name: "Create systemd service for {{ service.name }}"
      template:
        src: microservice.service.j2
        dest: "/etc/systemd/system/{{ service.name }}.service"
    
    - name: "Start {{ service.name }}"
      systemd:
        name: "{{ service.name }}"
        state: restarted
        enabled: yes
        daemon_reload: yes
```

### 4. Systemd Service Template (microservice.service.j2)

```ini
[Unit]
Description={{ service.name }}
After=network.target rabbitmq.service

[Service]
Type=simple
User=www-data
WorkingDirectory={{ project_root }}/{{ service.name }}
Environment="PATH={{ project_root }}/{{ service.name }}/venv/bin"
ExecStart={{ project_root }}/{{ service.name }}/venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

### 5. Docker Deployment Playbook (deploy-docker.yml)

```yaml
---
- name: Deploy with Docker Compose
  hosts: local
  become: yes
  
  tasks:
    - name: Copy docker-compose.yml
      copy:
        src: ../docker-compose.yml
        dest: /opt/smart-attendance/docker-compose.yml
    
    - name: Pull latest images
      command: docker-compose pull
      args:
        chdir: /opt/smart-attendance
    
    - name: Deploy stack
      command: docker-compose up -d
      args:
        chdir: /opt/smart-attendance
    
    - name: Wait for stack to be ready
      wait_for:
        port: "{{ item }}"
        delay: 5
        timeout: 60
      loop:
        - 5000  # API Gateway
        - 5001  # Student Service
        - 5002  # Course Service
        - 5003  # Bubble Sheet
        - 5004  # PDF Processing
        - 5005  # Attendance
        - 5006  # Reporting
        - 5007  # Auth
```

### Running Ansible Playbooks:

```bash
# Deploy everything
ansible-playbook -i inventory.ini playbooks/deploy-all.yml

# Deploy with Docker
ansible-playbook -i inventory.ini playbooks/deploy-docker.yml

# Deploy specific service only
ansible-playbook -i inventory.ini playbooks/deploy-service.yml --extra-vars "service_name=student-service"

# Dry run (check mode)
ansible-playbook -i inventory.ini playbooks/deploy-all.yml --check

# Deploy to production
ansible-playbook -i inventory.ini playbooks/deploy-all.yml --limit production
```

---

## 🛡️ FAULT TOLERANCE PATTERNS

### 1. Circuit Breaker Pattern

**Where to Apply:** Service-to-Service communication (especially in Attendance Service)

**Implementation:**

```python
# common/circuit_breaker.py

from datetime import datetime, timedelta
from enum import Enum

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing - reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered

class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60, success_threshold=2):
        self.failure_threshold = failure_threshold
        self.timeout = timeout  # seconds
        self.success_threshold = success_threshold
        
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
    
    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
            else:
                raise Exception("Circuit breaker is OPEN - service unavailable")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
            
        except Exception as e:
            self._on_failure()
            raise e
    
    def _on_success(self):
        """Handle successful call"""
        self.failure_count = 0
        
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.success_threshold:
                self.state = CircuitState.CLOSED
                self.success_count = 0
    
    def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
    
    def _should_attempt_reset(self):
        """Check if enough time has passed to try again"""
        return (datetime.now() - self.last_failure_time) > timedelta(seconds=self.timeout)

# Usage in Attendance Service:
from common.circuit_breaker import CircuitBreaker

student_service_breaker = CircuitBreaker(failure_threshold=5, timeout=60)
course_service_breaker = CircuitBreaker(failure_threshold=5, timeout=60)

def validate_student(student_id):
    def call_student_service():
        response = requests.get(f'http://student-service:5001/api/students/{student_id}', timeout=3)
        return response.status_code == 200
    
    return student_service_breaker.call(call_student_service)
```

### 2. Timeout Pattern

**Implementation:**

```python
# common/timeout.py

import requests
from functools import wraps
import signal

class TimeoutError(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutError("Operation timed out")

def with_timeout(seconds):
    """Decorator to add timeout to function"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Set alarm
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(seconds)
            
            try:
                result = func(*args, **kwargs)
            finally:
                # Cancel alarm
                signal.alarm(0)
            
            return result
        return wrapper
    return decorator

# Service-specific timeouts
SERVICE_TIMEOUTS = {
    'student-service': 3,      # 3 seconds
    'course-service': 3,       # 3 seconds
    'pdf-processing': 120,     # 2 minutes
    'reporting': 30            # 30 seconds
}

# Usage:
@with_timeout(3)
def call_student_service(student_id):
    response = requests.get(
        f'http://student-service:5001/api/students/{student_id}',
        timeout=SERVICE_TIMEOUTS['student-service']
    )
    return response.json()
```

### 3. Bulkhead Pattern

**Purpose:** Isolate resources to prevent cascading failures

**Implementation:**

```python
# common/bulkhead.py

from concurrent.futures import ThreadPoolExecutor
from queue import Queue

class Bulkhead:
    """
    Isolate different operations into separate thread pools
    """
    def __init__(self, max_workers=10):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.active_tasks = 0
        self.max_workers = max_workers
    
    def submit(self, func, *args, **kwargs):
        """Submit task to bulkhead"""
        if self.active_tasks >= self.max_workers:
            raise Exception("Bulkhead full - too many concurrent operations")
        
        self.active_tasks += 1
        future = self.executor.submit(func, *args, **kwargs)
        future.add_done_callback(lambda f: self._task_done())
        return future
    
    def _task_done(self):
        self.active_tasks -= 1

# Create separate bulkheads for different operations
pdf_processing_bulkhead = Bulkhead(max_workers=5)   # Max 5 concurrent PDF processing
api_requests_bulkhead = Bulkhead(max_workers=20)    # Max 20 concurrent API calls
database_bulkhead = Bulkhead(max_workers=10)        # Max 10 concurrent DB operations

# Usage in PDF Processing Service:
def process_pdf(pdf_path):
    future = pdf_processing_bulkhead.submit(_do_process_pdf, pdf_path)
    return future.result()
```

### 4. Idempotency

**Where to Apply:** Attendance Recording (prevent duplicate entries)

**Implementation:**

```python
# attendance-service/models/attendance.py

import hashlib

class AttendanceRecord:
    @staticmethod
    def generate_idempotency_key(student_id, course_id, date, session_name):
        """
        Generate unique key for attendance record
        Same student + course + date + session = same key
        """
        data = f"{student_id}:{course_id}:{date}:{session_name}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    @staticmethod
    def record_attendance(student_id, course_id, date, status, session_name):
        """
        Idempotent attendance recording
        """
        # Generate idempotency key
        key = AttendanceRecord.generate_idempotency_key(
            student_id, course_id, date, session_name
        )
        
        # Check if already exists
        existing = db.execute(
            "SELECT id FROM attendance_records WHERE idempotency_key = ?",
            (key,)
        ).fetchone()
        
        if existing:
            # Already recorded - return existing record
            return {'message': 'Already recorded', 'id': existing[0]}
        
        # Insert new record
        db.execute("""
            INSERT INTO attendance_records 
            (student_id, course_id, date, status, session_name, idempotency_key)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (student_id, course_id, date, status, session_name, key))
        
        return {'message': 'Recorded', 'id': db.lastrowid}

# Add idempotency_key column to database:
ALTER TABLE attendance_records ADD COLUMN idempotency_key TEXT UNIQUE;
```

### 5. Service Discovery

**Implementation with Simple Registry:**

```python
# service-registry/app.py

from flask import Flask, request, jsonify
from datetime import datetime, timedelta

app = Flask(__name__)

# In-memory service registry
SERVICES = {}
HEALTH_CHECK_INTERVAL = 30  # seconds

class ServiceRegistry:
    @staticmethod
    def register(service_name, host, port):
        """Register a service"""
        SERVICES[service_name] = {
            'host': host,
            'port': port,
            'url': f'http://{host}:{port}',
            'last_heartbeat': datetime.now(),
            'status': 'healthy'
        }
    
    @staticmethod
    def deregister(service_name):
        """Remove service from registry"""
        if service_name in SERVICES:
            del SERVICES[service_name]
    
    @staticmethod
    def get_service(service_name):
        """Get service URL"""
        service = SERVICES.get(service_name)
        if not service:
            return None
        
        # Check if service is healthy (recent heartbeat)
        if (datetime.now() - service['last_heartbeat']) > timedelta(seconds=HEALTH_CHECK_INTERVAL * 2):
            service['status'] = 'unhealthy'
            return None
        
        return service['url']
    
    @staticmethod
    def heartbeat(service_name):
        """Update service heartbeat"""
        if service_name in SERVICES:
            SERVICES[service_name]['last_heartbeat'] = datetime.now()
            SERVICES[service_name]['status'] = 'healthy'

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    ServiceRegistry.register(data['name'], data['host'], data['port'])
    return jsonify({'message': 'Registered'}), 200

@app.route('/discover/<service_name>', methods=['GET'])
def discover(service_name):
    url = ServiceRegistry.get_service(service_name)
    if not url:
        return jsonify({'error': 'Service not found'}), 404
    return jsonify({'url': url}), 200

@app.route('/heartbeat/<service_name>', methods=['POST'])
def heartbeat(service_name):
    ServiceRegistry.heartbeat(service_name)
    return jsonify({'message': 'OK'}), 200

@app.route('/services', methods=['GET'])
def list_services():
    return jsonify(SERVICES), 200

if __name__ == '__main__':
    app.run(port=5008)

# Usage in microservices:
# Each service registers on startup
import requests
import threading
import time

def register_service():
    requests.post('http://service-registry:5008/register', json={
        'name': 'student-service',
        'host': 'localhost',
        'port': 5001
    })

def send_heartbeat():
    while True:
        requests.post('http://service-registry:5008/heartbeat/student-service')
        time.sleep(30)

# On startup:
register_service()
threading.Thread(target=send_heartbeat, daemon=True).start()

# When calling another service:
def call_course_service():
    # Discover service URL
    response = requests.get('http://service-registry:5008/discover/course-service')
    if response.status_code == 200:
        service_url = response.json()['url']
        # Make request
        return requests.get(f'{service_url}/api/courses')
    else:
        raise Exception("Course service not available")
```

### Fault Tolerance Summary Table:

```
Pattern             | Where Applied              | Purpose
--------------------|---------------------------|------------------------------------------
Circuit Breaker     | Attendance Service        | Prevent cascading failures when calling Student/Course services
Timeout             | All service-to-service    | Prevent hanging requests
Bulkhead            | PDF Processing            | Limit concurrent operations
Idempotency         | Attendance Recording      | Prevent duplicate records
Service Discovery   | All services              | Dynamic service location
```

---

## 📊 UPDATED ARCHITECTURE DIAGRAM

```
                         ┌─────────────────┐
                         │  API Gateway    │ (Port 5000)
                         │  + JWT Auth     │
                         └────────┬────────┘
                                  │
                ┌─────────────────┼─────────────────┐
                │                 │                 │
         ┌──────▼──────┐   ┌──────▼──────┐  ┌──────▼──────┐
         │   Student   │   │   Course    │  │   Bubble    │
         │   Service   │   │   Service   │  │   Sheet     │
         │   (5001)    │   │   (5002)    │  │   (5003)    │
         └──────┬──────┘   └──────┬──────┘  └─────────────┘
                │                 │
         [Circuit Breaker]  [Timeout 3s]
                │                 │
         ┌──────▼─────────────────▼──────┐
         │   Attendance Service (5005)   │
         │   + Service Validation        │
         │   + Idempotency               │
         └───────────┬───────────────────┘
                     │
              ┌──────▼──────┐
              │  RabbitMQ   │
              │  (5672)     │
              └──────┬──────┘
                     │
         ┌───────────┼───────────┐
         │           │           │
    ┌────▼────┐ ┌────▼────┐ ┌───▼────┐
    │   PDF   │ │ Report  │ │  Auth  │
    │ Process │ │ Service │ │Service │
    │ (5004)  │ │ (5006)  │ │ (5007) │
    │+Bulkhead│ │         │ │        │
    └─────────┘ └─────────┘ └────────┘
         │
    [Service Registry (5008)]
```

---

## 🎯 UPDATED DELIVERABLES

### Now Including:

1. **Authentication System**
   - ✅ JWT-based authentication
   - ✅ API Gateway with token validation
   - ✅ Auth Service (login/logout)
   - ✅ Protected endpoints

2. **CI/CD Automation**
   - ✅ Ansible playbooks for deployment
   - ✅ Automated service deployment
   - ✅ Docker Compose automation
   - ✅ Health checks

3. **Fault Tolerance**
   - ✅ Circuit Breaker implementation
   - ✅ Timeout configuration
   - ✅ Bulkhead pattern
   - ✅ Idempotency keys
   - ✅ Service Discovery registry

---

**PROJECT READY FOR IMPLEMENTATION BY CLAUDE CODE** ✅

**Estimated Development Time:** 4-5 weeks (with new requirements)
**Complexity Level:** High
**Primary Technology:** Python Flask + OpenCV + RabbitMQ + Ansible + JWT

**Total Services:** 9 (6 microservices + API Gateway + Auth Service + Service Registry)

---

END OF DOCUMENTATION
