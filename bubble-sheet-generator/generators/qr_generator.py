"""
QR Code Generator
Generates QR codes containing lecture and page information
"""

import qrcode
import json
from io import BytesIO
from PIL import Image
from typing import Dict, Any


class QRCodeGenerator:
    """
    Generates QR codes for bubble sheets
    Each QR code contains: lecture_id, course_id, date, page_number
    """

    def __init__(self):
        self.version = 1  # QR code version (1-40)
        self.box_size = 10  # Size of each box in pixels
        self.border = 2  # Border size in boxes

    def generate_qr_data(
        self,
        lecture_id: str,
        course_id: str,
        date: str,
        page_number: int,
        total_pages: int
    ) -> str:
        """
        Create JSON data for QR code

        Args:
            lecture_id: Unique lecture identifier
            course_id: Course identifier
            date: Lecture date (YYYY-MM-DD)
            page_number: Current page number
            total_pages: Total number of pages

        Returns:
            JSON string to encode in QR code
        """
        data = {
            'lecture_id': lecture_id,
            'course_id': course_id,
            'date': date,
            'page': page_number,
            'total_pages': total_pages,
            'version': '1.0'
        }
        return json.dumps(data)

    def generate_qr_image(
        self,
        lecture_id: str,
        course_id: str,
        date: str,
        page_number: int,
        total_pages: int,
        size: int = 150
    ) -> Image:
        """
        Generate QR code image

        Args:
            lecture_id: Lecture ID
            course_id: Course ID
            date: Lecture date
            page_number: Page number
            total_pages: Total pages
            size: QR code size in pixels

        Returns:
            PIL Image object
        """
        # Create QR data
        qr_data = self.generate_qr_data(
            lecture_id, course_id, date, page_number, total_pages
        )

        # Create QR code
        qr = qrcode.QRCode(
            version=self.version,
            error_correction=qrcode.constants.ERROR_CORRECT_H,  # High error correction
            box_size=self.box_size,
            border=self.border,
        )

        qr.add_data(qr_data)
        qr.make(fit=True)

        # Create image
        img = qr.make_image(fill_color="black", back_color="white")

        # Resize to desired size
        img = img.resize((size, size), Image.Resampling.LANCZOS)

        return img

    def generate_qr_bytes(
        self,
        lecture_id: str,
        course_id: str,
        date: str,
        page_number: int,
        total_pages: int,
        size: int = 150
    ) -> bytes:
        """
        Generate QR code as bytes (for embedding in PDF)

        Returns:
            PNG image bytes
        """
        img = self.generate_qr_image(
            lecture_id, course_id, date, page_number, total_pages, size
        )

        # Convert to bytes
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        return buffer.getvalue()

    @staticmethod
    def decode_qr_data(qr_data: str) -> Dict[str, Any]:
        """
        Decode QR code data back to dictionary

        Args:
            qr_data: JSON string from QR code

        Returns:
            Dictionary with lecture information
        """
        return json.loads(qr_data)


# Example usage
if __name__ == '__main__':
    generator = QRCodeGenerator()

    # Generate QR code
    img = generator.generate_qr_image(
        lecture_id='LEC-2024-001',
        course_id='CS101',
        date='2024-12-15',
        page_number=1,
        total_pages=3,
        size=200
    )

    # Save to file
    img.save('sample_qr.png')
    print("QR code saved to sample_qr.png")

    # Test data encoding/decoding
    qr_data = generator.generate_qr_data(
        lecture_id='LEC-2024-001',
        course_id='CS101',
        date='2024-12-15',
        page_number=1,
        total_pages=3
    )
    print(f"QR Data: {qr_data}")

    decoded = generator.decode_qr_data(qr_data)
    print(f"Decoded: {decoded}")
