"""
Barcode Generator for OMR Sheets
Uses ITF (Interleaved 2 of 5) barcode - VERY THICK bars perfect for printing
ITF has the thickest bars of all barcode types, ideal for print visibility
"""

from io import BytesIO
from PIL import Image
from typing import Dict, Any
import json

# Use python-barcode library
try:
    import barcode
    from barcode.writer import ImageWriter
    BARCODE_AVAILABLE = True
except ImportError:
    BARCODE_AVAILABLE = False


class BarcodeGenerator:
    """
    Generates LARGE ITF (Interleaved 2 of 5) barcodes with VERY THICK bars
    Barcode is vertical along the left edge of the page for easy scanning
    ITF provides the thickest, most visible bars - perfect for printing
    """

    def __init__(self):
        if not BARCODE_AVAILABLE:
            raise ImportError("python-barcode library is required. Install with: pip install python-barcode")

    def generate_barcode_data(
        self,
        lecture_id: str,
        page_number: int,
        total_pages: int
    ) -> str:
        """
        Create numeric-only data string for ITF barcode
        ITF requires even number of digits (numeric only)
        We'll use a simple numeric encoding: hash the lecture_id
        """
        # Create a simple numeric code from lecture_id hash + page info
        # ITF needs even number of digits
        lecture_hash = abs(hash(lecture_id)) % 100000000  # 8 digits
        page_code = f"{page_number:02d}{total_pages:02d}"  # 4 digits (2+2)
        code = f"{lecture_hash:08d}{page_code}"  # Total: 12 digits (even)
        return code

    def generate_barcode_image(
        self,
        lecture_id: str,
        page_number: int,
        total_pages: int,
        height: int = 800,
        bar_width: float = 2.5
    ) -> Image.Image:
        """
        Generate LARGE ITF barcode image with VERY THICK bars (vertical orientation)

        Args:
            lecture_id: Lecture ID (will be encoded to numeric)
            page_number: Page number
            total_pages: Total pages
            height: Barcode height in pixels (will be rotated)
            bar_width: Width of each bar module (VERY THICK bars for printing)

        Returns:
            PIL Image object (rotated 90 degrees for vertical placement)
        """
        # Create numeric barcode data for ITF
        data = self.generate_barcode_data(lecture_id, page_number, total_pages)

        # Create ITF barcode (THICKEST bars - best for printing)
        ITF = barcode.get_barcode_class('itf')

        # Custom writer options - VERY LARGE barcode with VERY THICK bars
        writer = ImageWriter()

        # Generate barcode
        code = ITF(data, writer=writer)

        # Save to buffer with MAXIMUM thickness settings
        buffer = BytesIO()
        code.write(buffer, options={
            'module_width': bar_width,      # EXTREMELY THICK bars (2.5mm)
            'module_height': 40.0,          # VERY TALL bars
            'font_size': 20,                # Large text
            'text_distance': 12.0,          # Extra space for text
            'quiet_zone': 10.0,             # Large quiet zone
            'write_text': True
        })

        # Load as PIL image
        buffer.seek(0)
        img = Image.open(buffer)

        # Convert to RGB if needed
        if img.mode != 'RGB':
            img = img.convert('RGB')

        # Rotate 90 degrees for vertical placement on left side
        img = img.rotate(90, expand=True)

        return img

    def generate_barcode_bytes(
        self,
        lecture_id: str,
        page_number: int,
        total_pages: int,
        height: int = 800
    ) -> bytes:
        """
        Generate LARGE vertical barcode as bytes (for embedding in PDF)

        Returns:
            PNG image bytes
        """
        img = self.generate_barcode_image(
            lecture_id, page_number, total_pages, height
        )

        # Convert to bytes
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        return buffer.getvalue()

    # Store mapping of numeric codes to lecture IDs
    _lecture_mapping = {}

    def save_lecture_mapping(self, lecture_id: str, numeric_code: str):
        """Save mapping between lecture_id and numeric code"""
        self._lecture_mapping[numeric_code[:8]] = lecture_id  # Store hash part

    def decode_barcode_data(self, barcode_data: str) -> Dict[str, Any]:
        """
        Decode ITF barcode data back to dictionary

        Args:
            barcode_data: Numeric string from barcode (12 digits: 8 hash + 4 page info)

        Returns:
            Dictionary with lecture information
        """
        try:
            # Parse format: 8-digit hash + 2-digit page + 2-digit total
            if len(barcode_data) != 12:
                raise ValueError(f"Invalid barcode length: {len(barcode_data)}, expected 12")

            lecture_hash = barcode_data[:8]
            page_number = int(barcode_data[8:10])
            total_pages = int(barcode_data[10:12])

            # Try to get lecture_id from mapping
            lecture_id = self._lecture_mapping.get(lecture_hash, f"LEC-{lecture_hash}")

            return {
                'lecture_id': lecture_id,
                'page': page_number,
                'total_pages': total_pages,
                'hash': lecture_hash
            }
        except (IndexError, ValueError) as e:
            raise ValueError(f"Invalid barcode format: {barcode_data}") from e


# Example usage
if __name__ == '__main__':
    generator = BarcodeGenerator()

    # Generate barcode
    img = generator.generate_barcode_image(
        lecture_id='LEC-2024-001',
        page_number=1,
        total_pages=3,
        width=250,
        height=60
    )

    # Save to file
    img.save('sample_barcode.png')
    print("Barcode saved to sample_barcode.png")

    # Test data encoding/decoding
    barcode_data = generator.generate_barcode_data(
        lecture_id='LEC-2024-001',
        page_number=1,
        total_pages=3
    )
    print(f"Barcode Data: {barcode_data}")

    decoded = generator.decode_barcode_data(barcode_data)
    print(f"Decoded: {decoded}")
