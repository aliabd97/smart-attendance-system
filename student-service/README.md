# Student Management Service

**Port:** 5001

## Overview

The Student Management Service handles all student-related operations including CRUD operations and Excel import functionality using the **Adapter Pattern**.

## Features

✅ **Excel Adapter Pattern Implementation**
- Import students from legacy Excel files
- Automatic field mapping (e.g., `Student_No` → `id`)
- Value transformation (e.g., `"CS"` → `"Computer Science"`)
- Preview before import

✅ **CRUD Operations**
- Create, Read, Update, Delete students
- Search students by name or ID
- Filter students by department

✅ **SQLite Database**
- Independent `students.db` database
- Automatic table creation

## Installation

```bash
cd student-service
pip install -r requirements.txt
```

## Running the Service

```bash
python app.py
```

The service will start on `http://localhost:5001`

## Generate Sample Excel File

```bash
python create_sample_excel.py
```

This creates `sample_students.xlsx` with 50 sample student records.

## API Endpoints

### Health Check
```http
GET /
GET /api/health
```

### Student CRUD

**Get All Students**
```http
GET /api/students
```

**Get Student by ID**
```http
GET /api/students/{student_id}
```

**Create Student**
```http
POST /api/students
Content-Type: application/json

{
    "id": "20210001",
    "name": "Ahmed Ali Mohammed",
    "email": "ahmed@university.edu",
    "department": "Computer Science",
    "level": 3,
    "phone": "07712345678",
    "is_active": true
}
```

**Update Student**
```http
PUT /api/students/{student_id}
Content-Type: application/json

{
    "name": "Ahmed Ali Updated",
    "email": "ahmed.updated@university.edu"
}
```

**Delete Student**
```http
DELETE /api/students/{student_id}
```

### Search & Filter

**Search Students**
```http
GET /api/students/search?q=ahmed
```

**Get Students by Department**
```http
GET /api/students/department/Computer%20Science
```

### Excel Import (Adapter Pattern)

**Preview Excel File**
```http
POST /api/students/import-excel/preview
Content-Type: multipart/form-data

file: sample_students.xlsx
```

**Import from Excel**
```http
POST /api/students/import-excel
Content-Type: multipart/form-data

file: sample_students.xlsx
```

## Adapter Pattern Explanation

### Problem
Legacy Excel files use different field names and formats:
- `Student_No` instead of `id`
- `Dept` with codes like "CS" instead of "Computer Science"
- Dates in `DD/MM/YYYY` format instead of `YYYY-MM-DD`

### Solution
The Adapter Pattern translates legacy data to modern format:

1. **Field Mapper** - Maps column names
2. **Value Transformer** - Transforms data values
3. **Excel Adapter** - Combines both to create Student objects

### Files
- `adapters/field_mapper.py` - Field name mapping
- `adapters/value_transformer.py` - Value transformation
- `adapters/excel_adapter.py` - Main adapter implementation

## Testing

### 1. Test Health Check
```bash
curl http://localhost:5001/
```

### 2. Create a Student
```bash
curl -X POST http://localhost:5001/api/students \
  -H "Content-Type: application/json" \
  -d '{
    "id": "20210001",
    "name": "Ahmed Ali",
    "email": "ahmed@university.edu",
    "department": "Computer Science",
    "level": 3
  }'
```

### 3. Get All Students
```bash
curl http://localhost:5001/api/students
```

### 4. Import from Excel
First, generate sample file:
```bash
python create_sample_excel.py
```

Then import:
```bash
curl -X POST http://localhost:5001/api/students/import-excel \
  -F "file=@sample_students.xlsx"
```

### 5. Search Students
```bash
curl "http://localhost:5001/api/students/search?q=Ahmed"
```

## Database Schema

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

## Dependencies

- Flask 3.0.0 - Web framework
- Flask-CORS 4.0.0 - Cross-origin support
- openpyxl 3.1.2 - Excel file handling
- pika 1.3.2 - RabbitMQ client
- python-dotenv 1.0.0 - Environment variables

## Architecture

```
student-service/
├── models/
│   └── student.py          # Student model & repository
├── adapters/               # Adapter Pattern
│   ├── field_mapper.py
│   ├── value_transformer.py
│   └── excel_adapter.py
├── routes/
│   └── student_routes.py   # API endpoints
├── app.py                  # Main Flask application
├── create_sample_excel.py  # Sample data generator
└── students.db             # SQLite database
```

## Success Criteria

- ✅ Service starts on port 5001
- ✅ All CRUD endpoints working
- ✅ Excel import with Adapter Pattern functional
- ✅ Field mapping working correctly
- ✅ Value transformation working
- ✅ Database operations successful

## Next Steps

After completing Student Service:
1. Implement Course Service (Port 5002)
2. Implement Auth Service (Port 5007)
3. Implement API Gateway (Port 5000)
