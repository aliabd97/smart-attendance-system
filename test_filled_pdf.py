"""
Test processing of filled PDF
"""

import sys
sys.path.insert(0, 'pdf-processing-service')
from processors.omr_processor import OMRProcessor

omr = OMRProcessor()
result = omr.process_scanned_pdf(r'C:\Users\HP\Downloads\bubblesheet\test_new_design.pdf', 'temp_images')

print('=' * 60)
print('OMR Processing Results')
print('=' * 60)
print(f'Lecture ID: {result.get("lecture_id", "N/A")}')
print(f'Total Students: {len(result.get("attendance_records", []))}')
print(f'Present: {result.get("summary", {}).get("present", 0)}')
print(f'Absent: {result.get("summary", {}).get("absent", 0)}')
print(f'Attendance: {result.get("summary", {}).get("attendance_percentage", 0):.1f}%')
print()
print('Details:')
for rec in result.get('attendance_records', [])[:10]:
    print(f'  {rec["student_id"]}: {rec["status"].upper()} (fill={rec["fill_percentage"]:.1%}, conf={rec["confidence"]:.1%})')
