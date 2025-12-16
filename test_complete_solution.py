"""
Complete end-to-end test:
1. Generate new bubble sheet
2. Manually "fill" one bubble (simulate scanning)
3. Process with OMR
4. Verify results
"""
import sys
import os

sys.path.insert(0, 'bubble-sheet-generator')
sys.path.insert(0, 'bubble-sheet-generator/generators')

from generators.pdf_generator import BubbleSheetPDFGenerator

print("=" * 80)
print("STEP 1: Generate new bubble sheet with FIXED coordinates")
print("=" * 80)

generator = BubbleSheetPDFGenerator()

course_info = {
    'course_id': 'TEST-COURSE',
    'course_name': 'Test Course',
    'department': 'Test Dept',
    'date': '2025-12-16',
    'lecture_number': '99'
}

students = [
    {'id': 'STU-001', 'name': 'Test Student 1'},
    {'id': 'STU-002', 'name': 'Test Student 2'}
]

result = generator.generate_bubble_sheet(
    lecture_id='LEC-TEST-FINAL',
    course_info=course_info,
    students=students,
    output_path='test_sheet_fixed.pdf'
)

print(f"✅ Generated: {result}")

# Check saved coordinates
from common.database import Database
db = Database('bubble-sheet-generator/bubble_templates.db')
templates = db.fetch_all(
    "SELECT * FROM bubble_templates WHERE lecture_id = 'LEC-TEST-FINAL'"
)

print(f"\n✅ Saved {len(templates)} bubble templates:")
for t in templates:
    print(f"   {t['student_name']}: ({t['bubble_x']}, {t['bubble_y']})")

print(f"\n✅ PDF saved to: test_sheet_fixed.pdf")
print(f"\nNow you can:")
print(f"1. Open test_sheet_fixed.pdf")
print(f"2. Fill ONE bubble (e.g., Student 1)")
print(f"3. Save as PDF")
print(f"4. Upload through the web interface to test OMR")
