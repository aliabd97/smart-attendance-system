"""
Test full system: Generate PDF -> Scan -> Detect
"""

import sys
import os

# Test 1: Generate PDF with new design
print("=" * 50)
print("TEST 1: Generate PDF with new barcode design")
print("=" * 50)

sys.path.insert(0, 'bubble-sheet-generator')
from generators.pdf_generator import BubbleSheetPDFGenerator

students = [
    {'id': 'STU001', 'name': 'Ahmed Ali'},
    {'id': 'STU002', 'name': 'Mohammed Hassan'},
    {'id': 'STU003', 'name': 'Sara Ahmed'},
]

course_info = {
    'course_id': 'CS101',
    'course_name': 'Introduction to Programming',
    'department': 'Computer Science',
    'date': '2024-12-16',
    'lecture_number': 1
}

generator = BubbleSheetPDFGenerator()
result = generator.generate_bubble_sheet(
    lecture_id='LEC-TEST-001',
    course_info=course_info,
    students=students,
    output_path='test_system.pdf'
)

print(f"✅ PDF generated: {result['output_path']}")
print(f"   Pages: {result['total_pages']}")
print(f"   Students: {result['total_students']}")

# Test 2: Convert PDF to image and read barcode
print("\n" + "=" * 50)
print("TEST 2: Read barcode from PDF")
print("=" * 50)

sys.path.insert(0, 'pdf-processing-service')
from processors.omr_processor import OMRProcessor

omr = OMRProcessor()

# Convert to image
print("Converting PDF to image...")
image_paths = omr.convert_pdf_to_images('test_system.pdf', 'temp_images')
print(f"✅ Converted to {len(image_paths)} images")

# Read barcode
print("\nReading barcode...")
try:
    barcode_data = omr.read_barcode(image_paths[0])
    print(f"✅ Barcode read successfully!")
    print(f"   Lecture ID: {barcode_data.get('lecture_id', 'N/A')}")
    print(f"   Page: {barcode_data.get('page', 'N/A')}/{barcode_data.get('total_pages', 'N/A')}")
except Exception as e:
    print(f"❌ Failed to read barcode: {e}")

# Test 3: Detect markers and timing marks
print("\n" + "=" * 50)
print("TEST 3: Detect corner markers and timing marks")
print("=" * 50)

from processors.image_processor import ImageProcessor
import cv2

processor = ImageProcessor()
image = cv2.imread(image_paths[0])
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Find corner markers
corner_markers = processor.find_corner_markers(gray)
if corner_markers:
    print(f"✅ Found 4 corner markers:")
    for i, (x, y) in enumerate(corner_markers):
        print(f"   Corner {i+1}: ({x}, {y})")

    # Find timing marks
    timing_marks = processor.find_timing_marks(gray, corner_markers)
    print(f"✅ Found {len(timing_marks)} timing marks")
else:
    print("❌ No corner markers found")

print("\n" + "=" * 50)
print("TEST COMPLETE")
print("=" * 50)
