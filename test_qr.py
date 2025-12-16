"""
Test script to verify QR Code in generated bubble sheets
"""

from pdf2image import convert_from_path
from pyzbar import pyzbar
import json

# Poppler path
poppler_path = r'C:\Users\HP\smart-attendance-system\poppler-24.08.0\Library\bin'

# PDF file to test
pdf_file = r'bubble-sheet-generator\generated_sheets\LEC-4D997EA9498D.pdf'

print("Converting PDF to image...")
images = convert_from_path(pdf_file, dpi=300, poppler_path=poppler_path)

print(f"Converted {len(images)} pages")

# Read QR code from first page
print("\nReading QR code from first page...")
qr_codes = pyzbar.decode(images[0])

if qr_codes:
    print(f"Found {len(qr_codes)} QR code(s)")

    for i, qr in enumerate(qr_codes, 1):
        print(f"\nQR Code {i}:")
        print(f"  Type: {qr.type}")
        print(f"  Data: {qr.data.decode('utf-8')}")

        # Try to parse as JSON
        try:
            data = json.loads(qr.data.decode('utf-8'))
            print(f"  Parsed JSON:")
            for key, value in data.items():
                print(f"    {key}: {value}")
        except:
            print("  (Not JSON format)")
else:
    print("❌ No QR code found!")
