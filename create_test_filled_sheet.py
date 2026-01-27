"""
Script to create a test filled bubble sheet for OMR testing
This simulates a scanned sheet with filled bubbles
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

try:
    import fitz  # PyMuPDF
except ImportError:
    print("Installing PyMuPDF...")
    os.system("pip install --user PyMuPDF")
    import fitz

def fill_bubbles_in_pdf(input_pdf_path, output_pdf_path, students_to_mark_present=[]):
    """
    Fill bubbles in a bubble sheet PDF to simulate filled attendance

    Args:
        input_pdf_path: Path to the generated bubble sheet
        output_pdf_path: Path to save the filled sheet
        students_to_mark_present: List of student indices to mark as present (0-based)
    """
    print(f"Opening PDF: {input_pdf_path}")

    # Open the PDF
    doc = fitz.open(input_pdf_path)

    # Process each page
    for page_num in range(len(doc)):
        page = doc[page_num]

        print(f"Processing page {page_num + 1}/{len(doc)}...")

        # Get page dimensions
        rect = page.rect
        width = rect.width
        height = rect.height

        # Bubble sheet layout (approximate positions)
        # These are typical positions - adjust based on actual template

        # Student ID bubbles area (left side, below header)
        # Typically starts around x=100, y=200
        student_id_x = 100
        student_id_y_start = 200

        # Attendance bubbles (Present/Absent) - right side
        # For each student row
        attendance_x = width - 150  # Right side
        attendance_y_start = 200
        row_height = 25  # Space between student rows

        # Number of students per page (typically 30)
        students_per_page = min(30, len(students_to_mark_present) - (page_num * 30))

        # Fill bubbles for students marked as present
        for i in range(students_per_page):
            student_idx = (page_num * 30) + i

            if student_idx in students_to_mark_present:
                # Calculate bubble position for "Present" bubble
                bubble_y = attendance_y_start + (i * row_height)

                # Draw filled circle (black)
                # Present bubble is typically first, Absent is second
                present_bubble_x = attendance_x
                bubble_radius = 8

                # Create a filled circle annotation
                circle_rect = fitz.Rect(
                    present_bubble_x - bubble_radius,
                    bubble_y - bubble_radius,
                    present_bubble_x + bubble_radius,
                    bubble_y + bubble_radius
                )

                # Draw filled black circle
                shape = page.new_shape()
                shape.draw_circle(
                    fitz.Point(present_bubble_x, bubble_y),
                    bubble_radius
                )
                shape.finish(color=(0, 0, 0), fill=(0, 0, 0))  # Black filled
                shape.commit()

                print(f"  ✓ Marked student {student_idx} as PRESENT")
            else:
                # Mark as absent (optional - fill absent bubble)
                bubble_y = attendance_y_start + (i * row_height)
                absent_bubble_x = attendance_x + 40  # Absent bubble is to the right
                bubble_radius = 8

                shape = page.new_shape()
                shape.draw_circle(
                    fitz.Point(absent_bubble_x, bubble_y),
                    bubble_radius
                )
                shape.finish(color=(0, 0, 0), fill=(0, 0, 0))  # Black filled
                shape.commit()

                print(f"  ○ Marked student {student_idx} as ABSENT")

    # Save the modified PDF
    print(f"\nSaving filled PDF to: {output_pdf_path}")
    doc.save(output_pdf_path)
    doc.close()

    print(f"✅ Success! Test filled sheet created: {output_pdf_path}")
    print(f"\nYou can now upload this file to OMR Processing to test the system.")


if __name__ == "__main__":
    import glob

    # Find the most recently generated bubble sheet
    generated_sheets_folder = "bubble-sheet-generator/generated_sheets"

    if not os.path.exists(generated_sheets_folder):
        print(f"Error: Folder not found: {generated_sheets_folder}")
        print("Please generate a bubble sheet first using the dashboard.")
        sys.exit(1)

    # Get all PDF files
    pdf_files = glob.glob(os.path.join(generated_sheets_folder, "*.pdf"))

    if not pdf_files:
        print("No bubble sheets found!")
        print("Please generate a bubble sheet first:")
        print("  Dashboard → Bubble Sheets → Generate PDF")
        sys.exit(1)

    # Sort by modification time (most recent first)
    pdf_files.sort(key=os.path.getmtime, reverse=True)
    latest_sheet = pdf_files[0]

    print("=" * 60)
    print("Creating Test Filled Bubble Sheet")
    print("=" * 60)
    print(f"\nUsing latest bubble sheet: {os.path.basename(latest_sheet)}")

    # Create output filename
    base_name = os.path.basename(latest_sheet).replace(".pdf", "")
    output_path = os.path.join(generated_sheets_folder, f"{base_name}_FILLED_TEST.pdf")

    # Mark first 2 students as present, rest as absent (for testing)
    print("\nMarking students:")
    print("  - Students 0, 1: PRESENT ✓")
    print("  - Other students: ABSENT ○")

    students_present = [0, 1]  # First two students present

    # Create the filled sheet
    fill_bubbles_in_pdf(latest_sheet, output_path, students_present)

    print("\n" + "=" * 60)
    print("Next Steps:")
    print("=" * 60)
    print("1. Go to: http://localhost:3001/dashboard/omr")
    print("2. Upload the file:", os.path.basename(output_path))
    print("3. Click 'Process'")
    print("4. Expected result: 2 present, 1 absent")
    print("=" * 60)
