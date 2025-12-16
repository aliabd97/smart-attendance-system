# Reporting Service

Generates attendance reports in Excel and PDF formats.

## Features

- **Student Reports**: Individual student attendance history
- **Course Reports**: Complete course attendance matrix
- **Department Reports**: Department-wide attendance summary
- **Absence Alerts**: PDF alerts for at-risk students
- **Statistics API**: JSON statistics without file generation

## Report Types

### 1. Student Report
- Student information
- Attendance statistics (present/absent/percentage)
- Detailed attendance records per lecture
- Available in Excel and PDF

### 2. Course Report
- Course information
- Attendance matrix (all students × all lectures)
- Student-level statistics
- Color-coded attendance status
- Available in Excel and PDF

### 3. Department Report
- Summary of all courses in department
- Average attendance per course
- At-risk students count
- Status indicators (Good/Warning/Critical)
- Available in Excel

### 4. Absence Alert
- List of students below attendance threshold
- Risk level indicators (Critical/High/Moderate)
- Course-specific alerts
- Available in PDF

## API Endpoints

### Health Check
```
GET /health
```

### Generate Student Report
```
GET /api/reports/student/<student_id>?course_id=<course_id>&format=<excel|pdf>
```

**Parameters:**
- `student_id` (path): Student ID
- `course_id` (query, required): Course ID
- `format` (query, optional): 'excel' or 'pdf' (default: excel)

**Response:** File download

### Generate Course Report
```
GET /api/reports/course/<course_id>?format=<excel|pdf>
```

**Parameters:**
- `course_id` (path): Course ID
- `format` (query, optional): 'excel' or 'pdf' (default: excel)

**Response:** File download

### Generate Department Report
```
GET /api/reports/department/<department>?format=excel
```

**Parameters:**
- `department` (path): Department name
- `format` (query, optional): 'excel' (PDF not implemented for department reports)

**Response:** File download

### Generate Absence Alerts
```
GET /api/reports/alerts?course_id=<course_id>&threshold=<percentage>
```

**Parameters:**
- `course_id` (query, required): Course ID
- `threshold` (query, optional): Attendance percentage threshold (default: 75)

**Response:** PDF file download

### Get Course Statistics
```
GET /api/reports/statistics/<course_id>
```

**Parameters:**
- `course_id` (path): Course ID

**Response:** JSON statistics (no file)

## Installation

```bash
cd reporting-service
pip install -r requirements.txt
```

## Configuration

Copy `.env.example` to `.env` and configure:

```env
PORT=5007
STUDENT_SERVICE_URL=http://localhost:5001
COURSE_SERVICE_URL=http://localhost:5002
ATTENDANCE_SERVICE_URL=http://localhost:5006
```

## Running the Service

```bash
python app.py
```

Service will run on port 5007.

## Dependencies

- **Student Service**: Fetches student information
- **Course Service**: Fetches course and enrollment data
- **Attendance Service**: Fetches attendance records and lectures

## Design Patterns

### Circuit Breaker
- Prevents cascading failures when calling external services
- 3 failure threshold before opening circuit
- 30-second timeout before retry

### Timeouts
- 10-second timeout for HTTP requests to external services

### Bulkheads
- HTTP requests limited to 20 concurrent operations
- Prevents resource exhaustion

## Report Formats

### Excel Reports
- Professional styling with color-coded cells
- Headers with background colors
- Present (green), Absent (red), Warning (yellow)
- Auto-adjusted column widths
- Borders and alignment

### PDF Reports
- ReportLab-generated professional layouts
- Color-coded tables
- Headers and titles
- Landscape orientation for wide tables
- Compact and readable format

## Output Directories

Reports are saved to:
- Excel: `reports/excel/`
- PDF: `reports/pdf/`

Directories are created automatically if they don't exist.

## Example Usage

### Get Student Report (Excel)
```bash
curl "http://localhost:5007/api/reports/student/S001?course_id=CS101&format=excel" \
  -o student_report.xlsx
```

### Get Course Report (PDF)
```bash
curl "http://localhost:5007/api/reports/course/CS101?format=pdf" \
  -o course_report.pdf
```

### Get Department Report
```bash
curl "http://localhost:5007/api/reports/department/Computer%20Science" \
  -o department_report.xlsx
```

### Get Absence Alerts
```bash
curl "http://localhost:5007/api/reports/alerts?course_id=CS101&threshold=70" \
  -o alerts.pdf
```

### Get Statistics (JSON)
```bash
curl "http://localhost:5007/api/reports/statistics/CS101"
```

## Error Handling

All endpoints return appropriate HTTP status codes:
- 200: Success
- 400: Bad request (missing parameters, invalid format)
- 404: Resource not found (student, course, or department)
- 500: Internal server error

Error responses include JSON error messages:
```json
{
  "error": "Error description"
}
```
