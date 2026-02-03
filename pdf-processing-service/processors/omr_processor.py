"""
OMR (Optical Mark Recognition) Processor
Reads filled bubbles from scanned attendance sheets
"""

import cv2
import numpy as np
from pyzbar import pyzbar
import json
from pdf2image import convert_from_path
from typing import List, Dict, Tuple
import os
import tempfile

from .image_processor import ImageProcessor, BubbleDetectionResult


class OMRProcessor:
    """
    Complete OMR processing pipeline:
    1. Convert PDF to images
    2. Read QR code from each page
    3. Fetch bubble templates from database
    4. Detect filled bubbles
    5. Generate attendance records
    6. Send results to Attendance Service (protected by Circuit Breaker)
    """

    def __init__(self, bubble_service_url: str = "http://localhost:5003"):
        self.image_processor = ImageProcessor()
        self.bubble_service_url = bubble_service_url

        # Circuit Breaker: protects calls from PDF Processing (Client) to Attendance Service (Server)
        from common.circuit_breaker import CircuitBreaker
        self.attendance_cb = CircuitBreaker(
            name="attendance-service",
            failure_threshold=3,
            timeout=15,
            success_threshold=2
        )

    def convert_pdf_to_images(
        self,
        pdf_path: str,
        output_folder: str = None
    ) -> List[str]:
        """
        Convert PDF pages to images

        Args:
            pdf_path: Path to scanned PDF
            output_folder: Where to save images (temp folder if None)

        Returns:
            List of image file paths
        """
        if output_folder is None:
            output_folder = tempfile.mkdtemp()

        # Try PyMuPDF first (faster and no external dependencies)
        try:
            import fitz  # PyMuPDF

            # Open PDF
            pdf_document = fitz.open(pdf_path)

            # Convert each page to image
            image_paths = []
            for page_num in range(len(pdf_document)):
                page = pdf_document[page_num]

                # Render page to image (300 DPI)
                mat = fitz.Matrix(300/72, 300/72)  # 300 DPI scaling
                pix = page.get_pixmap(matrix=mat)

                # Save as PNG
                image_path = os.path.join(output_folder, f'page_{page_num + 1}.png')
                pix.save(image_path)
                image_paths.append(image_path)

            pdf_document.close()
            return image_paths

        except ImportError:
            # PyMuPDF not available, try pdf2image with poppler
            pass
        except Exception as e:
            print(f"PyMuPDF failed: {e}, trying pdf2image...")

        # Fallback to pdf2image (requires poppler)
        try:
            images = convert_from_path(pdf_path, dpi=300)
        except Exception as e:
            # If that fails, try common Windows poppler locations
            # Get project root directory (2 levels up from this file)
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

            poppler_paths = [
                os.path.join(project_root, 'poppler-24.08.0', 'Library', 'bin'),  # Project poppler
                r'C:\Program Files\poppler\Library\bin',
                r'C:\Program Files (x86)\poppler\Library\bin',
                r'C:\poppler\Library\bin',
                os.path.join(os.path.expanduser('~'), 'poppler', 'Library', 'bin')
            ]

            images = None
            for poppler_path in poppler_paths:
                if os.path.exists(poppler_path):
                    try:
                        images = convert_from_path(pdf_path, dpi=300, poppler_path=poppler_path)
                        break
                    except:
                        continue

            if images is None:
                raise Exception(
                    "Unable to convert PDF to images. Please install PyMuPDF:\n"
                    "pip install --user PyMuPDF\n\n"
                    "Or install poppler:\n"
                    "1. Download from: https://github.com/oschwartz10612/poppler-windows/releases/\n"
                    "2. Extract to C:\\poppler\n"
                    "3. Add C:\\poppler\\Library\\bin to your system PATH"
                )

        image_paths = []
        for i, image in enumerate(images, 1):
            image_path = os.path.join(output_folder, f'page_{i}.png')
            image.save(image_path, 'PNG')
            image_paths.append(image_path)

        return image_paths

    def read_barcode(self, image_path: str) -> Dict:
        """
        Read barcode from image (LARGE vertical barcode on left side)

        Args:
            image_path: Path to image

        Returns:
            Barcode data as dictionary
        """
        # Read image
        image = cv2.imread(image_path)

        # Detect barcodes (pyzbar reads both QR and barcodes)
        barcodes = pyzbar.decode(image)

        if not barcodes:
            # Try with different settings - rotate image
            rotated = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
            barcodes = pyzbar.decode(rotated)

        if not barcodes:
            raise ValueError(f"No barcode found in {image_path}")

        # Get first barcode
        barcode_data = barcodes[0].data.decode('utf-8')

        # Try ITF format first (12 digits: 8 hash + 2 page + 2 total)
        if len(barcode_data) == 12 and barcode_data.isdigit():
            # ITF barcode format
            lecture_hash = barcode_data[:8]
            page_number = int(barcode_data[8:10])
            total_pages = int(barcode_data[10:12])

            # Look up lecture_id, course_id, date from barcode mapping database
            import sqlite3
            import os

            db_paths = [
                'bubble-sheet-generator/barcode_mapping.db',
                '../bubble-sheet-generator/barcode_mapping.db',
                'barcode_mapping.db'
            ]

            lecture_id = f"LEC-{lecture_hash}"
            course_id = None
            date = None

            for db_path in db_paths:
                if os.path.exists(db_path):
                    try:
                        conn = sqlite3.connect(db_path)
                        cursor = conn.cursor()
                        cursor.execute('SELECT lecture_id, course_id, date FROM barcode_mapping WHERE barcode_hash = ?', (lecture_hash,))
                        result = cursor.fetchone()
                        conn.close()

                        if result:
                            lecture_id = result[0]
                            course_id = result[1]
                            date = result[2]
                            break
                    except:
                        pass

            return {
                'lecture_id': lecture_id,
                'course_id': course_id,
                'date': date,
                'page': page_number,
                'total_pages': total_pages,
                'hash': lecture_hash
            }

        # Parse old barcode format: LECTUREID-PAGE/TOTAL
        try:
            parts = barcode_data.rsplit('-', 1)
            lecture_id = parts[0]
            page_info = parts[1].split('/')
            page_number = int(page_info[0])
            total_pages = int(page_info[1])

            return {
                'lecture_id': lecture_id,
                'page': page_number,
                'total_pages': total_pages
            }
        except (IndexError, ValueError):
            # Fallback - try JSON format (old QR code)
            return json.loads(barcode_data)

    def read_qr_code(self, image_path: str) -> Dict:
        """Alias for backwards compatibility - now reads barcode"""
        return self.read_barcode(image_path)

    def fetch_bubble_templates(
        self,
        lecture_id: str,
        page_number: int
    ) -> List[Dict]:
        """
        Fetch bubble coordinate templates from Bubble Sheet Generator service

        Args:
            lecture_id: Lecture ID
            page_number: Page number

        Returns:
            List of bubble templates
        """
        import requests

        try:
            # Call Bubble Sheet Generator service
            response = requests.get(
                f"{self.bubble_service_url}/api/templates/{lecture_id}",
                timeout=10
            )

            if response.status_code != 200:
                raise ValueError(f"Could not fetch templates: {response.text}")

            data = response.json()
            templates = data['templates']

            # Filter for this page
            page_templates = [
                t for t in templates
                if t['page_number'] == page_number
            ]

            return page_templates

        except requests.RequestException as e:
            raise ValueError(f"Error connecting to Bubble Sheet Generator: {e}")

    def process_scanned_pdf(
        self,
        pdf_path: str,
        output_folder: str = None
    ) -> Dict:
        """
        Complete OMR processing of scanned PDF

        Args:
            pdf_path: Path to scanned PDF
            output_folder: Where to save temporary files

        Returns:
            Processing results with attendance records
        """
        # Convert PDF to images
        image_paths = self.convert_pdf_to_images(pdf_path, output_folder)

        all_results = []
        lecture_id = None
        course_id = None

        # Process each page
        for page_num, image_path in enumerate(image_paths, 1):
            try:
                # Read barcode (or QR code for backwards compatibility)
                barcode_info = self.read_qr_code(image_path)

                lecture_id = barcode_info['lecture_id']
                course_id = barcode_info.get('course_id', 'UNKNOWN')
                page_number = barcode_info['page']
                date = barcode_info.get('date', 'UNKNOWN')

                # Fetch bubble templates
                print(f"📋 Fetching templates for lecture {lecture_id}, page {page_number}...")
                bubble_templates = self.fetch_bubble_templates(
                    lecture_id,
                    page_number
                )

                print(f"📊 Found {len(bubble_templates)} bubble templates")
                if not bubble_templates:
                    raise ValueError(f"No bubble templates found for page {page_number}")

                # Process bubbles
                print(f"🔍 Processing bubble sheet page...")
                detection_results = self.image_processor.process_bubble_sheet_page(
                    image_path,
                    bubble_templates
                )

                print(f"✅ Got {len(detection_results)} detection results")
                # Convert to attendance records
                for result in detection_results:
                    status = "present" if result.is_filled else "absent"

                    attendance_record = {
                        'student_id': result.student_id,
                        'lecture_id': lecture_id,
                        'course_id': barcode_info.get('course_id', ''),
                        'date': barcode_info.get('date', ''),
                        'status': status,
                        'confidence': result.confidence,
                        'fill_percentage': result.fill_percentage
                    }

                    all_results.append(attendance_record)

                # Optional: Create visualization
                if output_folder:
                    viz_path = os.path.join(output_folder, f'page_{page_num}_detected.png')
                    self.image_processor.visualize_detection(
                        image_path,
                        detection_results,
                        viz_path
                    )

            except Exception as e:
                print(f"Error processing page {page_num}: {e}")
                continue

        # Calculate statistics
        total_students = len(all_results)
        present_count = sum(1 for r in all_results if r['status'] == 'present')
        absent_count = total_students - present_count
        attendance_percentage = (present_count / total_students * 100) if total_students > 0 else 0

        return {
            'lecture_id': lecture_id,
            'total_pages': len(image_paths),
            'total_students': total_students,
            'present': present_count,
            'absent': absent_count,
            'attendance_percentage': round(attendance_percentage, 2),
            'attendance_records': all_results,
            'status': 'success'
        }

    def send_to_attendance_service(
        self,
        attendance_records: List[Dict],
        attendance_service_url: str = "http://localhost:5005"
    ) -> Dict:
        """
        Send attendance records to Attendance Service.
        Protected by Circuit Breaker (Client-Side pattern).

        If Attendance Service is down:
        - First 3 failures: CB stays CLOSED, counts failures
        - After 3 failures: CB opens, all subsequent requests rejected immediately
        - After 15s timeout: CB goes HALF_OPEN, tests with one request
        - If test succeeds: CB closes, normal operation resumes
        """
        import requests

        success_count = 0
        error_count = 0
        cb_rejected_count = 0
        errors = []

        for record in attendance_records:
            try:
                # Use Circuit Breaker to protect the HTTP call
                def send_single_record():
                    response = requests.post(
                        f"{attendance_service_url}/api/attendance",
                        json=record,
                        headers={'Content-Type': 'application/json'},
                        timeout=10
                    )
                    if response.status_code not in [200, 201]:
                        raise Exception(f"HTTP {response.status_code}: {response.text}")
                    return response

                response = self.attendance_cb.call(send_single_record)
                success_count += 1

            except Exception as e:
                error_msg = str(e)
                if "circuit is OPEN" in error_msg:
                    cb_rejected_count += 1
                else:
                    error_count += 1
                errors.append({
                    'student_id': record['student_id'],
                    'error': error_msg
                })

        return {
            'total_records': len(attendance_records),
            'success': success_count,
            'errors': error_count,
            'cb_rejected': cb_rejected_count,
            'circuit_breaker_state': self.attendance_cb.get_state(),
            'error_details': errors if errors else None,
            'status': 'success' if error_count == 0 and cb_rejected_count == 0 else 'partial_success'
        }


# Example usage
if __name__ == '__main__':
    processor = OMRProcessor()

    # Example: Process scanned PDF
    # result = processor.process_scanned_pdf('scanned_attendance.pdf')
    #
    # print(f"Processed {result['total_pages']} pages")
    # print(f"Total students: {result['total_students']}")
    # print(f"Present: {result['present']} ({result['attendance_percentage']}%)")
    # print(f"Absent: {result['absent']}")
    #
    # # Send to Attendance Service
    # send_result = processor.send_to_attendance_service(result['attendance_records'])
    # print(f"Sent {send_result['success']} records successfully")

    print("OMR Processor initialized successfully")
