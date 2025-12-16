"""
Test new design with LARGE vertical barcode and timing marks
"""

import sys
sys.path.insert(0, 'bubble-sheet-generator')

from generators.pdf_generator import BubbleSheetPDFGenerator

# Create test data
students = [
    {'id': 'STU001', 'name': 'Ahmed Ali'},
    {'id': 'STU002', 'name': 'Mohammed Hassan'},
    {'id': 'STU003', 'name': 'Sara Ahmed'},
    {'id': 'STU004', 'name': 'Fatima Omar'},
    {'id': 'STU005', 'name': 'Ali Hussein'},
]

course_info = {
    'course_id': 'CS101',
    'course_name': 'Introduction to Programming',
    'department': 'Computer Science',
    'date': '2024-12-16',
    'lecture_number': 1
}

# Generate PDF
generator = BubbleSheetPDFGenerator()
result = generator.generate_bubble_sheet(
    lecture_id='LEC-TEST-001',
    course_info=course_info,
    students=students,
    output_path='test_new_design.pdf'
)

print(f"PDF generated: {result['output_path']}")
print(f"Pages: {result['total_pages']}")
print("Open the PDF to see the new design with:")
print("  - LARGE vertical barcode on LEFT side")
print("  - 4 corner markers around bubble area")
print("  - Timing marks for each row")
