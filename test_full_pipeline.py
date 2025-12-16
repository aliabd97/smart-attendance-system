"""
Complete test of OMR pipeline to identify the exact issue
"""
import sys
import cv2
import numpy as np
from pdf2image import convert_from_path

# Poppler path
poppler_path = r'C:\Users\HP\smart-attendance-system\poppler-24.08.0\Library\bin'

# Latest processed job
latest_pdf = r'pdf-processing-service\uploads\JOB-907B1E9D9CB2.pdf'
latest_image = r'pdf-processing-service\processed\JOB-907B1E9D9CB2\page_1.png'

print("=" * 80)
print("STEP 1: Check PDF and Image")
print("=" * 80)

# Load the processed image
image = cv2.imread(latest_image)
if image is None:
    print("❌ Cannot load image")
    sys.exit(1)

print(f"✅ Image loaded: {image.shape} (height x width x channels)")
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

print("\n" + "=" * 80)
print("STEP 2: Test Calibration Circle Detection")
print("=" * 80)

# Preprocess
blurred = cv2.GaussianBlur(gray, (5, 5), 0)
thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)

# Detect circles
circles = cv2.HoughCircles(
    thresh,
    cv2.HOUGH_GRADIENT,
    dp=1,
    minDist=100,
    param1=50,
    param2=20,
    minRadius=5,
    maxRadius=50
)

if circles is None:
    print("❌ No calibration circles detected!")
else:
    print(f"✅ Found {len(circles[0])} circles")
    for i, circle in enumerate(circles[0][:10]):  # Show first 10
        x, y, r = int(circle[0]), int(circle[1]), int(circle[2])
        print(f"   Circle {i+1}: center=({x}, {y}), radius={r}")

print("\n" + "=" * 80)
print("STEP 3: Check Bubble Coordinates from Database")
print("=" * 80)

sys.path.insert(0, 'pdf-processing-service')
from common.database import Database

db = Database('bubble-sheet-generator/bubble_templates.db')
templates = db.fetch_all(
    "SELECT * FROM bubble_templates WHERE lecture_id = 'LEC-2F0727C78B21'"
)

print(f"✅ Found {len(templates)} templates in database:")
for t in templates:
    print(f"   Student: {t['student_name']}, Bubble: ({t['bubble_x']}, {t['bubble_y']}), Radius: {t['bubble_radius']}")

print("\n" + "=" * 80)
print("STEP 4: Test Bubble Detection at Database Coordinates")
print("=" * 80)

for t in templates:
    x, y, r = int(t['bubble_x']), int(t['bubble_y']), int(t['bubble_radius'])

    # Check if coordinates are within image bounds
    if x < 0 or x >= gray.shape[1] or y < 0 or y >= gray.shape[0]:
        print(f"\n❌ {t['student_name']}: Coordinates OUT OF BOUNDS!")
        print(f"   Bubble at ({x}, {y}) but image is {gray.shape[1]}x{gray.shape[0]}")
        continue

    print(f"\n{t['student_name']}:")
    print(f"  Coordinates: ({x}, {y}), Radius: {r}")

    # Create mask
    mask = np.zeros(gray.shape, dtype=np.uint8)
    cv2.circle(mask, (x, y), r, 255, -1)

    # Extract pixels
    masked_pixels = gray[mask > 0]

    if len(masked_pixels) == 0:
        print(f"  ❌ No pixels in mask!")
        continue

    # Count dark pixels
    dark_pixels = np.sum(masked_pixels < 127)
    total_pixels = len(masked_pixels)
    fill_percentage = dark_pixels / total_pixels

    print(f"  Dark pixels: {dark_pixels} / {total_pixels}")
    print(f"  Fill percentage: {fill_percentage:.2%}")
    print(f"  Is filled (>75%): {fill_percentage >= 0.75}")

    # Sample pixel values
    print(f"  Sample pixel values:")
    for dy in [-r, 0, r]:
        for dx in [-r, 0, r]:
            px, py = x + dx, y + dy
            if 0 <= px < gray.shape[1] and 0 <= py < gray.shape[0]:
                val = gray[py, px]
                print(f"    ({px},{py}): {val}", end="  ")
    print()

print("\n" + "=" * 80)
print("COMPLETE!")
print("=" * 80)
