"""
Check latest OMR job results
"""
import sys
sys.path.insert(0, 'pdf-processing-service')

from common.database import Database

# Connect to database
db = Database('pdf-processing-service/processing_history.db')

# Get latest job
query = """
SELECT * FROM processing_jobs
ORDER BY created_at DESC
LIMIT 1
"""

job = db.fetch_one(query)

if job:
    print("Latest Job:")
    print(f"  Job ID: {job['job_id']}")
    print(f"  Lecture ID: {job['lecture_id']}")
    print(f"  Total Students: {job['total_students']}")
    print(f"  Present: {job['present_count']}")
    print(f"  Absent: {job['absent_count']}")
    print(f"  Attendance %: {job['attendance_percentage']}")
else:
    print("No jobs found")
