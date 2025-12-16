"""
Debug script to test bubble detection on actual scanned image
"""
import cv2
import numpy as np
import sys
import os

def test_bubble_detection(image_path):
    """Test different bubble detection methods"""

    print(f"📂 Reading image: {image_path}")
    image = cv2.imread(image_path)

    if image is None:
        print(f"❌ Could not read image: {image_path}")
        return

    print(f"✅ Image loaded: {image.shape}")

    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Method 1: Adaptive Threshold
    print("\n" + "="*60)
    print("METHOD 1: Adaptive Threshold (Old)")
    print("="*60)
    blurred1 = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh1 = cv2.adaptiveThreshold(
        blurred1, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV, 11, 2
    )
    cv2.imwrite('debug_adaptive_thresh.png', thresh1)
    print("Saved: debug_adaptive_thresh.png")

    # Method 2: OTSU Threshold
    print("\n" + "="*60)
    print("METHOD 2: OTSU Threshold (New)")
    print("="*60)
    blurred2 = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh2 = cv2.threshold(blurred2, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    cv2.imwrite('debug_otsu_thresh.png', thresh2)
    print("Saved: debug_otsu_thresh.png")

    # Method 3: Simple threshold with different values
    print("\n" + "="*60)
    print("METHOD 3: Testing different threshold values")
    print("="*60)
    for threshold_val in [100, 127, 150, 180, 200]:
        _, thresh_test = cv2.threshold(blurred2, threshold_val, 255, cv2.THRESH_BINARY_INV)
        cv2.imwrite(f'debug_thresh_{threshold_val}.png', thresh_test)
        print(f"Saved: debug_thresh_{threshold_val}.png")

    # Find contours with OTSU
    print("\n" + "="*60)
    print("CONTOUR DETECTION")
    print("="*60)
    cnts = cv2.findContours(thresh2.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]

    print(f"Total contours found: {len(cnts)}")

    # Analyze all contours
    height, width = gray.shape
    circular_contours = []

    for idx, c in enumerate(cnts):
        (x, y, w, h) = cv2.boundingRect(c)
        ar = w / float(h)
        area = cv2.contourArea(c)

        # Check if in right area
        center_x = x + w // 2
        center_y = y + h // 2
        min_x = width * 0.70
        max_x = width * 0.95
        min_y = 150
        max_y = height - 100

        in_area = min_x < center_x < max_x and min_y < center_y < max_y

        if w >= 8 and h >= 8 and w <= 50 and h <= 50 and ar >= 0.85 and ar <= 1.15:
            circular_contours.append({
                'x': center_x,
                'y': center_y,
                'w': w,
                'h': h,
                'ar': ar,
                'area': area,
                'in_area': in_area
            })

    print(f"\nCircular contours (AR 0.85-1.15, size 8-50): {len(circular_contours)}")

    # Sort by Y position
    circular_contours.sort(key=lambda c: c['y'])

    # Show first 20
    print("\nFirst 20 circular contours:")
    for i, cnt in enumerate(circular_contours[:20]):
        in_area_str = "✅ IN AREA" if cnt['in_area'] else "❌ OUTSIDE"
        print(f"{i+1}. Center: ({cnt['x']}, {cnt['y']}) Size: {cnt['w']}x{cnt['h']} AR: {cnt['ar']:.2f} {in_area_str}")

    # Draw all circular contours
    debug_image = image.copy()
    for cnt in circular_contours:
        if cnt['in_area']:
            color = (0, 255, 0)  # Green for in area
        else:
            color = (0, 0, 255)  # Red for outside

        cv2.circle(debug_image, (cnt['x'], cnt['y']), cnt['w']//2, color, 2)
        cv2.putText(debug_image, f"{cnt['y']}", (cnt['x']+15, cnt['y']),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)

    cv2.imwrite('debug_contours_detected.png', debug_image)
    print("\n✅ Saved: debug_contours_detected.png")

    # Test fill detection on first few bubbles
    print("\n" + "="*60)
    print("FILL DETECTION TEST")
    print("="*60)

    in_area_bubbles = [c for c in circular_contours if c['in_area']]
    print(f"Testing fill detection on {len(in_area_bubbles[:5])} bubbles in attendance area...")

    for i, bubble in enumerate(in_area_bubbles[:5]):
        bubble_x = bubble['x']
        bubble_y = bubble['y']
        bubble_radius = max(bubble['w'], bubble['h']) // 2

        # Apply OTSU threshold
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

        # Create mask
        mask = np.zeros(thresh.shape, dtype=np.uint8)
        cv2.circle(mask, (bubble_x, bubble_y), bubble_radius, 255, -1)

        # Count pixels
        masked = cv2.bitwise_and(thresh, thresh, mask=mask)
        total = cv2.countNonZero(masked)
        total_pixels = cv2.countNonZero(mask)

        fill_percentage = total / float(total_pixels) if total_pixels > 0 else 0
        is_filled = fill_percentage >= 0.65

        status = "✅ FILLED" if is_filled else "❌ EMPTY"
        print(f"{i+1}. Position: ({bubble_x}, {bubble_y}) Fill: {fill_percentage:.1%} {status}")

    print("\n" + "="*60)
    print("✅ Debug complete! Check the generated images:")
    print("  - debug_adaptive_thresh.png")
    print("  - debug_otsu_thresh.png")
    print("  - debug_thresh_*.png")
    print("  - debug_contours_detected.png")
    print("="*60)


if __name__ == '__main__':
    # Find the most recent processed image
    temp_folders = []
    temp_dir = 'C:\\Users\\HP\\AppData\\Local\\Temp'

    for folder in os.listdir(temp_dir):
        if folder.startswith('tmp'):
            folder_path = os.path.join(temp_dir, folder)
            if os.path.isdir(folder_path):
                # Check if it has page_1.png
                page_path = os.path.join(folder_path, 'page_1.png')
                if os.path.exists(page_path):
                    temp_folders.append((folder_path, os.path.getmtime(folder_path)))

    if temp_folders:
        # Get most recent
        temp_folders.sort(key=lambda x: x[1], reverse=True)
        most_recent = temp_folders[0][0]
        image_path = os.path.join(most_recent, 'page_1.png')
        print(f"Found most recent scanned image: {image_path}")
        test_bubble_detection(image_path)
    else:
        print("❌ No processed images found in temp folder")
        print("Please upload a PDF first, then run this script")
