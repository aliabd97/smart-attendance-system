"""
PDF Bubble Sheet Generator
Generates attendance sheets with student lists and bubble marks
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Table, TableStyle
from io import BytesIO
from typing import List, Dict, Tuple
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from common.database import Database


class BubbleSheetPDFGenerator:
    """
    Generates PDF bubble sheets for attendance tracking

    Layout:
    - Header: University name, course info, date, lecture number
    - QR Code: Top right corner
    - 4 Calibration circles: One in each corner
    - Student list: 30 students per page
    - Each student: Number, Name, One bubble for attendance
    """

    def __init__(self, db_path: str = 'bubble_templates.db'):
        self.page_width, self.page_height = A4
        self.db = Database(db_path)
        self._init_database()

        # Layout constants (in mm)
        self.margin_left = 15 * mm
        self.margin_right = 15 * mm
        self.margin_top = 15 * mm
        self.margin_bottom = 15 * mm

        # Calibration circle positions and size
        self.calibration_radius = 4 * mm
        self.calibration_positions = [
            (self.margin_left, self.page_height - self.margin_top),  # Top-left
            (self.page_width - self.margin_right, self.page_height - self.margin_top),  # Top-right
            (self.margin_left, self.margin_bottom),  # Bottom-left
            (self.page_width - self.margin_right, self.margin_bottom),  # Bottom-right
        ]

        # Bubble settings
        self.bubble_radius = 3 * mm
        self.bubble_x_offset = self.page_width - 40 * mm  # Right side

        # Row settings
        self.students_per_page = 30
        self.row_height = 8 * mm
        self.header_height = 50 * mm

    def _init_database(self):
        """Initialize database tables for storing bubble coordinates"""
        schema = """
        CREATE TABLE IF NOT EXISTS bubble_templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lecture_id TEXT NOT NULL,
            page_number INTEGER NOT NULL,
            student_id TEXT NOT NULL,
            student_name TEXT NOT NULL,
            row_number INTEGER NOT NULL,
            bubble_x REAL NOT NULL,
            bubble_y REAL NOT NULL,
            bubble_radius REAL NOT NULL,
            bubble_x_ratio REAL,
            bubble_y_ratio REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        self.db.create_table(schema)

    def generate_bubble_sheet(
        self,
        lecture_id: str,
        course_info: Dict,
        students: List[Dict],
        output_path: str
    ) -> Dict:
        """
        Generate complete bubble sheet PDF

        Args:
            lecture_id: Unique lecture identifier
            course_info: Dictionary with course, date, lecture_number, etc.
            students: List of student dictionaries
            output_path: Path to save PDF file

        Returns:
            Dictionary with generation results
        """
        # Calculate number of pages needed
        total_students = len(students)
        total_pages = (total_students + self.students_per_page - 1) // self.students_per_page

        # Create PDF
        c = canvas.Canvas(output_path, pagesize=A4)

        # Generate each page
        for page_num in range(1, total_pages + 1):
            # Get students for this page
            start_idx = (page_num - 1) * self.students_per_page
            end_idx = min(start_idx + self.students_per_page, total_students)
            page_students = students[start_idx:end_idx]

            # Draw page
            self._draw_page(
                c, lecture_id, course_info, page_students,
                page_num, total_pages
            )

            # Save bubble coordinates to database
            self._save_bubble_coordinates(
                lecture_id, page_num, page_students
            )

            # Add new page if not last
            if page_num < total_pages:
                c.showPage()

        # Save PDF
        c.save()

        return {
            'lecture_id': lecture_id,
            'total_pages': total_pages,
            'total_students': total_students,
            'output_path': output_path,
            'status': 'success'
        }

    def _draw_page(
        self,
        c: canvas.Canvas,
        lecture_id: str,
        course_info: Dict,
        students: List[Dict],
        page_num: int,
        total_pages: int
    ):
        """Draw a single page of the bubble sheet"""
        # Draw header first
        self._draw_header(c, course_info, page_num, total_pages)

        # Draw barcode (instead of QR code - doesn't interfere with bubble detection)
        self._draw_barcode(c, lecture_id, page_num, total_pages)

        # Draw student list
        self._draw_student_list(c, students, page_num)

        # Draw calibration markers AROUND the bubble area (after drawing bubbles)
        self._draw_bubble_area_markers(c, len(students))

        # Draw footer
        self._draw_footer(c)

    def _draw_bubble_area_markers(self, c: canvas.Canvas, students_count: int):
        """
        Draw ZipGrade-style calibration markers:
        1. 4 corner markers for page alignment
        2. Timing marks on left edge (one per row)
        This provides precise row-by-row alignment
        """
        c.setFillColor(colors.black)
        c.setStrokeColor(colors.black)

        # Corner marker size (larger for easy detection)
        corner_marker_size = 6 * mm

        # Timing mark size (small squares on edge)
        timing_mark_size = 3 * mm

        # Calculate bubble area boundaries
        # First bubble Y position
        first_bubble_y = self.page_height - self.header_height - 20 * mm - 2 * mm - self.row_height + 3 * mm
        # Last bubble Y position
        last_bubble_y = first_bubble_y - (students_count - 1) * self.row_height

        # Bubble X position
        bubble_x = self.bubble_x_offset

        # Add margins around the bubble area
        margin = 10 * mm

        # Marker positions around the BUBBLE AREA only
        top_y = first_bubble_y + margin
        bottom_y = last_bubble_y - margin
        left_x = bubble_x - margin - 5 * mm  # Extra space for timing marks
        right_x = bubble_x + margin

        # Draw 4 corner markers (large squares)
        corner_positions = [
            (left_x, top_y),      # Top-left of bubble area
            (right_x, top_y),     # Top-right of bubble area
            (left_x, bottom_y),   # Bottom-left of bubble area
            (right_x, bottom_y),  # Bottom-right of bubble area
        ]

        for x, y in corner_positions:
            c.rect(
                x - corner_marker_size/2,
                y - corner_marker_size/2,
                corner_marker_size,
                corner_marker_size,
                fill=1
            )

        # Draw timing marks on LEFT edge (one per student row)
        # These help with precise row alignment
        timing_x = left_x - timing_mark_size - 2 * mm

        for i in range(students_count):
            row_y = first_bubble_y - i * self.row_height
            c.rect(
                timing_x - timing_mark_size/2,
                row_y - timing_mark_size/2,
                timing_mark_size,
                timing_mark_size,
                fill=1
            )

        # Store marker positions for later use
        self._bubble_area_markers = corner_positions
        self._bubble_area_bounds = {
            'top_y': top_y,
            'bottom_y': bottom_y,
            'left_x': left_x,
            'right_x': right_x,
            'timing_x': timing_x,
            'first_bubble_y': first_bubble_y,
            'row_height': self.row_height
        }

    def _draw_header(
        self,
        c: canvas.Canvas,
        course_info: Dict,
        page_num: int,
        total_pages: int
    ):
        """Draw header with university and course information"""
        y_position = self.page_height - self.margin_top - 10 * mm

        # University name
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(
            self.page_width / 2,
            y_position,
            "University of Babylon - College of Engineering"
        )

        y_position -= 8 * mm

        # Course information in one line with small font
        c.setFont("Helvetica", 8)
        course_name = course_info.get('course_name', 'N/A')
        department = course_info.get('department', 'N/A')
        date = course_info.get('date', 'N/A')
        lecture_num = course_info.get('lecture_number', 'N/A')

        # All info in one line
        info_text = f"Course: {course_name}  |  Department: {department}  |  Date: {date}  |  Lecture: {lecture_num}  |  Page: {page_num}/{total_pages}"
        c.drawCentredString(
            self.page_width / 2,
            y_position,
            info_text
        )

        # Draw line
        y_position -= 4 * mm
        c.setStrokeColor(colors.black)
        c.setLineWidth(1)
        c.line(
            self.margin_left,
            y_position,
            self.page_width - self.margin_right,
            y_position
        )

    def _draw_barcode(
        self,
        c: canvas.Canvas,
        lecture_id: str,
        page_num: int,
        total_pages: int
    ):
        """Draw vertical ITF barcode with VERY THICK bars on LEFT side of page"""
        from .barcode_generator import BarcodeGenerator

        barcode_gen = BarcodeGenerator()

        # Generate numeric code and save mapping
        numeric_code = barcode_gen.generate_barcode_data(lecture_id, page_num, total_pages)
        barcode_gen.save_lecture_mapping(lecture_id, numeric_code)

        barcode_bytes = barcode_gen.generate_barcode_bytes(
            lecture_id=lecture_id,
            page_number=page_num,
            total_pages=total_pages,
            height=800
        )

        # Save barcode to temp file
        barcode_path = f'temp_barcode_{page_num}.png'
        with open(barcode_path, 'wb') as f:
            f.write(barcode_bytes)

        # Draw ITF barcode with THICK bars - smaller size to avoid table
        barcode_width = 18 * mm   # Width of vertical barcode
        barcode_height = 180 * mm  # Height - reduced to stay away from table

        # Position on left edge, centered vertically
        x_pos = 4 * mm
        y_pos = (self.page_height - barcode_height) / 2

        c.drawImage(
            barcode_path,
            x_pos,
            y_pos,
            width=barcode_width,
            height=barcode_height,
            preserveAspectRatio=True
        )

        # Clean up temp file
        try:
            os.remove(barcode_path)
        except:
            pass

    def _draw_student_list(
        self,
        c: canvas.Canvas,
        students: List[Dict],
        page_num: int
    ):
        """Draw student list with bubbles"""
        # Starting position
        y_position = self.page_height - self.header_height - 20 * mm

        # Table header
        c.setFont("Helvetica-Bold", 10)
        c.drawString(self.margin_left + 5 * mm, y_position, "#")
        c.drawString(self.margin_left + 15 * mm, y_position, "Student Name")
        c.drawString(self.bubble_x_offset - 10 * mm, y_position, "Attendance")

        # Draw header line
        y_position -= 2 * mm
        c.line(
            self.margin_left,
            y_position,
            self.page_width - self.margin_right,
            y_position
        )

        # Draw students
        y_position -= self.row_height
        c.setFont("Helvetica", 9)

        for idx, student in enumerate(students, 1):
            row_num = (page_num - 1) * self.students_per_page + idx

            # Student number
            c.drawString(
                self.margin_left + 5 * mm,
                y_position,
                str(row_num)
            )

            # Student name
            student_name = student.get('name', 'Unknown')
            c.drawString(
                self.margin_left + 15 * mm,
                y_position,
                student_name
            )

            # Draw bubble (empty circle) - center it vertically in the row
            # Text is at y_position (baseline), bubble should be at middle of text height
            bubble_y = y_position + 3 * mm  # Adjusted for better vertical centering
            c.setStrokeColor(colors.black)
            c.setLineWidth(0.5)
            c.circle(
                self.bubble_x_offset,
                bubble_y,
                self.bubble_radius,
                fill=0
            )

            # Draw row line
            y_position -= self.row_height
            if idx < len(students):
                c.setStrokeColor(colors.lightgrey)
                c.setLineWidth(0.3)
                c.line(
                    self.margin_left,
                    y_position + self.row_height - 1 * mm,
                    self.page_width - self.margin_right,
                    y_position + self.row_height - 1 * mm
                )

    def _draw_footer(self, c: canvas.Canvas):
        """Draw footer - empty for cleaner look"""
        # Footer removed for cleaner appearance
        return

    def _save_bubble_coordinates(
        self,
        lecture_id: str,
        page_num: int,
        students: List[Dict]
    ):
        """Save bubble coordinates to database for later OMR processing"""
        # Match exact y_position calculation from _draw_student_list
        y_position = self.page_height - self.header_height - 20 * mm
        y_position -= 2 * mm  # Table header line
        y_position -= self.row_height  # First row

        # Get bubble area bounds (set by _draw_bubble_area_markers)
        bounds = getattr(self, '_bubble_area_bounds', None)

        for idx, student in enumerate(students, 1):
            row_num = (page_num - 1) * self.students_per_page + idx
            bubble_y = y_position + 3 * mm  # Match the drawing code

            # Calculate ratio WITHIN the bubble area (not the whole page)
            if bounds:
                area_width = bounds['right_x'] - bounds['left_x']
                area_height = bounds['top_y'] - bounds['bottom_y']

                # Bubble position relative to bubble area (0-1)
                x_ratio_in_area = (self.bubble_x_offset - bounds['left_x']) / area_width
                y_ratio_in_area = (bubble_y - bounds['bottom_y']) / area_height
            else:
                # Fallback to page ratios
                x_ratio_in_area = self.bubble_x_offset / self.page_width
                y_ratio_in_area = bubble_y / self.page_height

            # Save coordinates
            data = {
                'lecture_id': lecture_id,
                'page_number': page_num,
                'student_id': student.get('id', ''),
                'student_name': student.get('name', ''),
                'row_number': row_num,
                'bubble_x': float(self.bubble_x_offset),
                'bubble_y': float(bubble_y),
                'bubble_radius': float(self.bubble_radius),
                # Store ratios WITHIN the bubble area for accurate detection
                'bubble_x_ratio': float(x_ratio_in_area),
                'bubble_y_ratio': float(y_ratio_in_area)
            }

            self.db.insert('bubble_templates', data)

            y_position -= self.row_height


# Example usage
if __name__ == '__main__':
    generator = BubbleSheetPDFGenerator()

    # Sample course info
    course_info = {
        'course_id': 'CS101',
        'course_name': 'Database Systems',
        'department': 'Second Year',
        'date': '2024-12-15',
        'lecture_number': '5'
    }

    # Sample students (90 students)
    students = [
        {'id': f'2024{i:04d}', 'name': f'Student Number {i}'}
        for i in range(1, 91)
    ]

    # Generate PDF
    result = generator.generate_bubble_sheet(
        lecture_id='LEC-2024-001',
        course_info=course_info,
        students=students,
        output_path='sample_bubble_sheet.pdf'
    )

    print(f"Generated: {result}")
