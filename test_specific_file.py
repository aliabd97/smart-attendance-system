"""
Test the specific PDF file with improved bubble detection
"""
import sys
import cv2
import numpy as np
from pdf2image import convert_from_path
import os

# Poppler path
poppler_path = r'C:\Users\HP\smart-attendance-system\poppler-24.08.0\Library\bin'

# The specific file the user is using
pdf_file = r'C:\Users\HP\smart-attendance-system\attendance_sheet_LEC-2F0727C78B21سسؤسؤ.pdf'

print("="*80)
print("TESTING SPECIFIC PDF FILE")
print("="*80)
print(f"PDF: {os.path.basename(pdf_file)}")

# Convert PDF to image
print("\n📄 Converting PDF to image...")
images = convert_from_path(pdf_file, dpi=300, poppler_path=poppler_path)
image = images[0]

# Save as PNG
image.save('test_page.png', 'PNG')
print("✅ Saved as test_page.png")

# Load with OpenCV
img = cv2.imread('test_page.png')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
print(f"✅ Image size: {img.shape[1]} x {img.shape[0]} pixels")

# Method 1: Original method (Adaptive Threshold + HoughCircles)
print("\n" + "="*80)
print("METHOD 1: Original (Adaptive + HoughCircles)")
print("="*80)

blurred1 = cv2.GaussianBlur(gray, (5, 5), 0)
thresh1 = cv2.adaptiveThreshold(blurred1, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                cv2.THRESH_BINARY_INV, 11, 2)

edges1 = cv2.Canny(thresh1, 50, 150)
circles1 = cv2.HoughCircles(edges1, cv2.HOUGH_GRADIENT, dp=1, minDist=10,
                           param1=50, param2=15, minRadius=4, maxRadius=12)

if circles1 is not None:
    print(f"Found {len(circles1[0])} circles with HoughCircles")
else:
    print("❌ No circles found with HoughCircles")

# Method 2: New method (OTSU + findContours)
print("\n" + "="*80)
print("METHOD 2: New (OTSU + findContours)")
print("="*80)

blurred2 = cv2.GaussianBlur(gray, (5, 5), 0)
thresh2 = cv2.threshold(blurred2, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

cv2.imwrite('test_otsu_thresh.png', thresh2)
print("✅ Saved threshold image: test_otsu_thresh.png")

cnts = cv2.findContours(thresh2.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cnts = cnts[0] if len(cnts) == 2 else cnts[1]

print(f"Found {len(cnts)} total contours")

# Filter for circular shapes in attendance area
height, width = gray.shape
min_x = width * 0.70
max_x = width * 0.95
min_y = 150
max_y = height - 100

circular_bubbles = []
for c in cnts:
    (x, y, w, h) = cv2.boundingRect(c)
    ar = w / float(h)

    if w >= 8 and h >= 8 and w <= 50 and h <= 50 and ar >= 0.85 and ar <= 1.15:
        center_x = x + w // 2
        center_y = y + h // 2

        if min_x < center_x < max_x and min_y < center_y < max_y:
            radius = max(w, h) // 2
            circular_bubbles.append((center_x, center_y, radius, w, h))

print(f"✅ Found {len(circular_bubbles)} circular bubbles in attendance area")

# Sort by Y position
circular_bubbles.sort(key=lambda c: c[1])

# Show first 10
print("\nFirst 10 bubbles (sorted top to bottom):")
for i, (cx, cy, r, w, h) in enumerate(circular_bubbles[:10]):
    print(f"{i+1}. Center: ({cx}, {cy}), Radius: {r}, Size: {w}x{h}")

# Test fill detection on first few bubbles
print("\n" + "="*80)
print("FILL DETECTION TEST")
print("="*80)

for i, (cx, cy, r, w, h) in enumerate(circular_bubbles[:5]):
    # Create mask
    mask = np.zeros(thresh2.shape, dtype=np.uint8)
    cv2.circle(mask, (cx, cy), r, 255, -1)

    # Apply mask and count pixels
    masked = cv2.bitwise_and(thresh2, thresh2, mask=mask)
    total = cv2.countNonZero(masked)
    total_pixels = cv2.countNonZero(mask)

    fill_percentage = total / float(total_pixels) if total_pixels > 0 else 0
    is_filled = fill_percentage >= 0.65

    status = "✅ FILLED" if is_filled else "❌ EMPTY"
    print(f"{i+1}. Position: ({cx}, {cy}) Fill: {fill_percentage:.1%} {status}")

# Draw detected bubbles on image
debug_img = img.copy()
for i, (cx, cy, r, w, h) in enumerate(circular_bubbles[:5]):
    # Create mask for this bubble
    mask = np.zeros(thresh2.shape, dtype=np.uint8)
    cv2.circle(mask, (cx, cy), r, 255, -1)

    masked = cv2.bitwise_and(thresh2, thresh2, mask=mask)
    total = cv2.countNonZero(masked)
    total_pixels = cv2.countNonZero(mask)
    fill_percentage = total / float(total_pixels) if total_pixels > 0 else 0
    is_filled = fill_percentage >= 0.65

    color = (0, 255, 0) if is_filled else (0, 0, 255)
    cv2.circle(debug_img, (cx, cy), r+5, color, 3)
    cv2.putText(debug_img, f"{i+1}: {fill_percentage:.0%}", (cx+20, cy),
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

cv2.imwrite('test_detected_bubbles.png', debug_img)
print("\n✅ Saved visualization: test_detected_bubbles.png")

print("\n" + "="*80)
print("✅ COMPLETE! Check these files:")
print("  - test_page.png (converted PDF)")
print("  - test_otsu_thresh.png (threshold visualization)")
print("  - test_detected_bubbles.png (detected bubbles with fill %)")
print("="*80)
