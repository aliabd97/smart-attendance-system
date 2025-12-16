"""
Test alignment and precise bubble detection
"""
import sys
import cv2
import numpy as np
from pdf2image import convert_from_path

# Poppler path
poppler_path = r'C:\Users\HP\smart-attendance-system\poppler-24.08.0\Library\bin'

# The specific file
pdf_file = r'C:\Users\HP\smart-attendance-system\attendance_sheet_LEC-2F0727C78B21سسؤسؤ.pdf'

print("="*80)
print("ALIGNMENT-BASED BUBBLE DETECTION")
print("="*80)

# Convert and load
images = convert_from_path(pdf_file, dpi=300, poppler_path=poppler_path)
image = images[0]
image.save('aligned_test.png', 'PNG')

img = cv2.imread('aligned_test.png')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
height, width = gray.shape

print(f"Image size: {width} x {height}")

# Find attendance bubbles in the RIGHT column
print("\n" + "="*80)
print("DETECTING ATTENDANCE BUBBLES")
print("="*80)

blurred = cv2.GaussianBlur(gray, (5, 5), 0)
thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

# Find contours
cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cnts = cnts[0] if len(cnts) == 2 else cnts[1]

print(f"Total contours: {len(cnts)}")

# Attendance bubbles are in the RIGHT column
attendance_bubbles = []
min_x = width * 0.75
max_x = width * 0.90
min_y = height * 0.08
max_y = height * 0.15

for c in cnts:
    (x, y, w, h) = cv2.boundingRect(c)
    ar = w / float(h)

    if 15 <= w <= 40 and 15 <= h <= 40 and 0.80 <= ar <= 1.20:
        center_x = x + w // 2
        center_y = y + h // 2

        if min_x < center_x < max_x and min_y < center_y < max_y:
            radius = max(w, h) // 2
            attendance_bubbles.append((center_x, center_y, radius))

print(f"Found {len(attendance_bubbles)} bubbles")

# Sort by Y
attendance_bubbles.sort(key=lambda c: c[1])

debug_img = img.copy()

for i, (cx, cy, r) in enumerate(attendance_bubbles[:5]):
    mask = np.zeros(thresh.shape, dtype=np.uint8)
    cv2.circle(mask, (cx, cy), r, 255, -1)

    masked = cv2.bitwise_and(thresh, thresh, mask=mask)
    total = cv2.countNonZero(masked)
    total_pixels = cv2.countNonZero(mask)

    fill = total / float(total_pixels) if total_pixels > 0 else 0
    filled = fill >= 0.65

    status = "PRESENT" if filled else "ABSENT"
    print(f"{i+1}. ({cx}, {cy}) Fill: {fill:.1%} {status}")

    color = (0, 255, 0) if filled else (0, 0, 255)
    cv2.circle(debug_img, (cx, cy), r+5, color, 3)
    cv2.putText(debug_img, f"{i+1}:{fill:.0%}", (cx+25, cy+5),
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

cv2.imwrite('aligned_annotated.png', debug_img)
print("\nSaved: aligned_annotated.png")
