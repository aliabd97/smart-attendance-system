"""
Test bubble detection with the new design
"""

import sys
import cv2
import numpy as np

sys.path.insert(0, 'pdf-processing-service')
from processors.image_processor import ImageProcessor

# Load test image
image_path = 'temp_images/page_1.png'
image = cv2.imread(image_path)
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

print(f"Image size: {gray.shape}")

processor = ImageProcessor()

# Find markers
corner_markers = processor.find_corner_markers(gray)
print(f"\nCorner markers: {corner_markers}")

if corner_markers:
    timing_marks = processor.find_timing_marks(gray, corner_markers)
    print(f"Timing marks: {len(timing_marks)}")
    for i, tm in enumerate(timing_marks):
        print(f"  {i}: {tm}")

    # Calculate bubble X position
    bubble_x = (corner_markers[0][0] + corner_markers[1][0]) // 2
    print(f"\nBubble X position: {bubble_x}")

    # Check each bubble
    print("\n" + "=" * 50)
    print("Bubble Detection Results:")
    print("=" * 50)

    for i, tm in enumerate(timing_marks[:3]):  # First 3 = 3 students
        y = tm[1]
        is_filled, fill_pct = processor.check_bubble_by_timing_mark(gray, y, bubble_x, radius=15)
        status = "PRESENT" if is_filled else "ABSENT"
        print(f"Student {i+1}: Y={y}, Fill={fill_pct:.1%} -> {status}")

    # Save visualization
    vis = image.copy()

    # Draw corner markers
    for x, y in corner_markers:
        cv2.rectangle(vis, (x-20, y-20), (x+20, y+20), (0, 255, 0), 3)

    # Draw timing marks and bubble positions
    for i, tm in enumerate(timing_marks[:3]):
        tx, ty = tm
        cv2.rectangle(vis, (tx-10, ty-10), (tx+10, ty+10), (255, 0, 0), 2)

        # Bubble position
        bx = bubble_x
        by = ty
        is_filled, fill_pct = processor.check_bubble_by_timing_mark(gray, by, bx, radius=15)
        color = (0, 255, 0) if is_filled else (0, 0, 255)
        cv2.circle(vis, (bx, by), 20, color, 3)
        cv2.putText(vis, f"{fill_pct:.0%}", (bx+25, by), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

    cv2.imwrite('bubble_detection_test.png', vis)
    print(f"\nVisualization saved: bubble_detection_test.png")
