"""
Final complete test of fixed OMR system
"""
import sys
sys.path.insert(0, 'pdf-processing-service/processors')

from pdf2image import convert_from_path
import cv2
import numpy as np
from image_processor import ImageProcessor

# Convert PDF to image
poppler_path = r'C:\Users\HP\smart-attendance-system\poppler-24.08.0\Library\bin'
print("Converting PDF to image...")
images = convert_from_path('test_sheet_fixed.pdf', dpi=300, poppler_path=poppler_path)
image = cv2.cvtColor(np.array(images[0]), cv2.COLOR_RGB2BGR)

print(f"Image size: {image.shape}")

# Process
processor = ImageProcessor()
preprocessed = processor.preprocess_image(image)
calibration = processor.detect_calibration_points(preprocessed)

if not calibration:
    print("❌ No calibration found")
    sys.exit(1)

print(f"✅ Calibration found")

# Align
aligned = processor.align_image(image, calibration, 595, 842)
aligned_gray = cv2.cvtColor(aligned, cv2.COLOR_BGR2GRAY)

print(f"✅ Aligned to {aligned.shape}")

# Test bubbles with NEW coordinates AND Y-axis flip
from common.database import Database
db = Database('bubble_templates.db')
templates = db.fetch_all(
    "SELECT * FROM bubble_templates WHERE lecture_id = 'LEC-TEST-FINAL'"
)

img_height = aligned_gray.shape[0]

print(f"\n" + "="*80)
print("Testing bubble detection:")
print("="*80)

for t in templates:
    print(f"\n{t['student_name']}:")

    # Use ratios if available
    if t['bubble_x_ratio'] is not None:
        bubble_x = int(t['bubble_x_ratio'] * aligned_gray.shape[1])
        bubble_y = int(t['bubble_y_ratio'] * aligned_gray.shape[0])
        print(f"  Ratios: ({t['bubble_x_ratio']:.4f}, {t['bubble_y_ratio']:.4f})")
        print(f"  Image coords: ({bubble_x}, {bubble_y})")
    else:
        # Fallback to PDF coords
        pdf_x, pdf_y = t['bubble_x'], t['bubble_y']
        bubble_x = int(pdf_x)
        bubble_y = int(img_height - pdf_y)
        print(f"  PDF coords: ({pdf_x:.1f}, {pdf_y:.1f})")
        print(f"  Image coords: ({bubble_x}, {bubble_y})")

    bubble_r = int(t['bubble_radius'])

    # Create mask
    mask = np.zeros(aligned_gray.shape, dtype=np.uint8)
    cv2.circle(mask, (bubble_x, bubble_y), bubble_r, 255, -1)

    # Extract pixels
    masked_pixels = aligned_gray[mask > 0]

    if len(masked_pixels) == 0:
        print("  ❌ No pixels in mask!")
        continue

    # Count dark pixels
    dark_pixels = np.sum(masked_pixels < 127)
    total_pixels = len(masked_pixels)
    fill_percentage = dark_pixels / total_pixels

    print(f"  Fill: {fill_percentage:.2%}")
    print(f"  Is filled (>75%): {'YES ✅' if fill_percentage >= 0.75 else 'NO ❌'}")

    # Draw on image
    color = (0, 255, 0) if fill_percentage >= 0.75 else (0, 0, 255)
    cv2.circle(aligned, (bubble_x, bubble_y), bubble_r, color, 2)
    cv2.putText(aligned, t['student_name'], (bubble_x+15, bubble_y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)

cv2.imwrite('final_test_result.png', aligned)
print(f"\n✅ Saved result to: final_test_result.png")
