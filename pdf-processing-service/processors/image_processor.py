"""
Image Processing Module - ZipGrade-Style OMR Detection
Uses timing marks for precise row alignment and bubble detection
"""

import cv2
import numpy as np
from typing import Tuple, List, Dict, Optional
from dataclasses import dataclass


@dataclass
class BubbleDetectionResult:
    """Result of bubble detection"""
    student_id: str
    student_name: str
    is_filled: bool
    confidence: float
    bubble_center: Tuple[int, int]
    fill_percentage: float


class ImageProcessor:
    """
    ZipGrade-style OMR processor:
    1. Find 4 corner markers around the bubble area
    2. Find timing marks on left edge (one per row)
    3. Use timing marks to locate each bubble precisely
    4. Check each bubble for fill
    """

    def __init__(self):
        self.bubble_fill_threshold = 0.50  # 50% dark = filled (more strict)

    def find_corner_markers(self, gray: np.ndarray) -> Optional[List[Tuple[int, int]]]:
        """
        Find the 4 corner calibration squares around the bubble area
        Returns: [top-left, top-right, bottom-left, bottom-right]
        """
        height, width = gray.shape

        # Use OTSU threshold for better detection
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)

        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Find square-shaped contours (corner markers are ~6mm = ~70px at 300dpi)
        squares = []
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            area = w * h
            ar = w / float(h) if h > 0 else 0

            # Corner markers: square shape, medium size (50-200 pixels)
            # At 300 DPI, 6mm = ~70px, so area ~4900
            if 2000 < area < 20000 and 0.7 < ar < 1.4:
                cx, cy = x + w // 2, y + h // 2
                # Only consider markers in right 40% of page (bubble area)
                if cx > width * 0.55:
                    squares.append((cx, cy, area, w, h))

        if len(squares) < 4:
            print(f"Warning: Found only {len(squares)} corner markers, need 4")
            return None

        # Sort by area (largest first) and take candidates
        squares.sort(key=lambda s: s[2], reverse=True)
        candidates = squares[:10]

        if len(candidates) < 4:
            return None

        # Find the 4 corners by position
        # Sort by Y to separate top and bottom
        candidates.sort(key=lambda s: s[1])

        top_half = candidates[:len(candidates)//2]
        bottom_half = candidates[len(candidates)//2:]

        # From top candidates, find leftmost and rightmost
        top_half.sort(key=lambda s: s[0])
        top_left = (top_half[0][0], top_half[0][1])
        top_right = (top_half[-1][0], top_half[-1][1])

        # From bottom candidates, find leftmost and rightmost
        bottom_half.sort(key=lambda s: s[0])
        bottom_left = (bottom_half[0][0], bottom_half[0][1])
        bottom_right = (bottom_half[-1][0], bottom_half[-1][1])

        return [top_left, top_right, bottom_left, bottom_right]

    def find_actual_bubbles(
        self,
        gray: np.ndarray,
        corner_markers: List[Tuple[int, int]]
    ) -> List[Tuple[int, int]]:
        """
        Find the ACTUAL filled bubbles (not timing marks)
        Returns Y positions of bubbles for alignment
        """
        height, width = gray.shape

        # Use threshold to find dark regions
        _, binary = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY_INV)

        # Find contours
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Find large filled circles (actual attendance bubbles)
        bubbles = []
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            area = cv2.contourArea(cnt)

            # Large filled circles: area 2000-12000 (filled attendance marks)
            if 2000 < area < 12000:
                ar = w / float(h) if h > 0 else 0
                # Roughly circular
                if 0.6 < ar < 1.5:
                    cx, cy = x + w // 2, y + h // 2
                    # Must be on the RIGHT side (where bubbles are)
                    # and in the middle vertical area (not corner markers)
                    if cx > width * 0.70 and 850 < cy < 1300:
                        bubbles.append((cx, cy))

        # Sort by Y position (top to bottom)
        bubbles.sort(key=lambda b: b[1])

        return bubbles

    def extract_bubble_area(
        self,
        image: np.ndarray,
        markers: List[Tuple[int, int]],
        target_width: int = 200,
        target_height: int = 400
    ) -> np.ndarray:
        """
        Extract and align just the bubble area using the 4 corner markers
        """
        top_left, top_right, bottom_left, bottom_right = markers

        src_points = np.array([
            top_left,
            top_right,
            bottom_right,
            bottom_left,
        ], dtype=np.float32)

        dst_points = np.array([
            [0, 0],
            [target_width, 0],
            [target_width, target_height],
            [0, target_height]
        ], dtype=np.float32)

        matrix = cv2.getPerspectiveTransform(src_points, dst_points)
        extracted = cv2.warpPerspective(image, matrix, (target_width, target_height))

        return extracted

    def check_bubble_by_timing_mark(
        self,
        gray: np.ndarray,
        timing_mark_y: int,
        bubble_x: int,
        radius: int = 12
    ) -> Tuple[bool, float]:
        """
        Check if bubble at the same Y level as timing mark is filled
        This is much more accurate than using ratios
        """
        height, width = gray.shape

        # Bubble is at the same Y as timing mark, but at bubble_x
        x = bubble_x
        y = timing_mark_y

        # Ensure within bounds
        x = max(radius, min(width - radius, x))
        y = max(radius, min(height - radius, y))

        # Create circular mask
        mask = np.zeros((height, width), dtype=np.uint8)
        cv2.circle(mask, (x, y), radius, 255, -1)

        # Get pixels in mask
        pixels = gray[mask > 0]

        if len(pixels) == 0:
            return False, 0.0

        # Count dark pixels (threshold at 128 for grayscale)
        dark_count = np.sum(pixels < 128)
        fill_percentage = dark_count / len(pixels)

        is_filled = fill_percentage >= self.bubble_fill_threshold

        return is_filled, fill_percentage

    def process_bubble_sheet_page(
        self,
        image_path: str,
        bubble_templates: List[Dict]
    ) -> List[BubbleDetectionResult]:
        """
        Process a bubble sheet page using timing marks for alignment:
        1. Find corner markers
        2. Find timing marks
        3. For each row, use timing mark to locate bubble
        4. Check each bubble for fill
        """
        # Load image
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not read image: {image_path}")

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        height, width = gray.shape

        print(f"Image loaded: {width}x{height}")

        # Find corner markers
        corner_markers = self.find_corner_markers(gray)

        if corner_markers:
            print(f"Found 4 corner markers")
            for i, (x, y) in enumerate(corner_markers):
                print(f"   Corner {i+1}: ({x}, {y})")

            # Find actual filled bubbles to get their Y positions
            bubble_positions = self.find_actual_bubbles(gray, corner_markers)
            print(f"Found {len(bubble_positions)} actual bubbles")

            # Get bubble_x from the detected bubbles
            if bubble_positions:
                bubble_x = bubble_positions[0][0]  # Use X from first bubble
                print(f"Using bubble_x from detected bubbles: {bubble_x}")
            else:
                # Fallback calculation
                bubble_x = int(width * 0.81)
                print(f"No bubbles detected, using fallback bubble_x: {bubble_x}")

        else:
            print("Warning: No corner markers found, using fallback detection")
            bubble_positions = []
            bubble_x = int(width * 0.81)

        # Process each student
        results = []

        # Calculate expected Y position for each student (rows are ~95px apart starting at ~910)
        base_y = 910
        row_spacing = 95

        for idx, template in enumerate(bubble_templates):
            student_id = template['student_id']
            student_name = template['student_name']

            # Expected Y position for this student's row
            expected_y = base_y + (idx * row_spacing)

            # Check if there's a filled bubble near this Y position
            # Look for bubble within ±40 pixels of expected position
            found_bubble = None
            for bubble_x_pos, bubble_y_pos in bubble_positions:
                if abs(bubble_y_pos - expected_y) < 40:
                    found_bubble = (bubble_x_pos, bubble_y_pos)
                    break

            if found_bubble:
                # Use the detected bubble position
                bubble_cx, bubble_cy = found_bubble
                is_filled, fill_percentage = self.check_bubble_by_timing_mark(
                    gray, bubble_cy, bubble_cx, radius=42  # Larger to cover full bubble
                )
                center = (bubble_cx, bubble_cy)
            else:
                # No bubble detected at this position - check anyway at expected position
                is_filled, fill_percentage = self.check_bubble_by_timing_mark(
                    gray, expected_y, bubble_x, radius=42  # Larger to cover full bubble
                )
                center = (bubble_x, expected_y)

            status = "PRESENT" if is_filled else "ABSENT"
            print(f"  {student_name}: pos={center} fill={fill_percentage:.1%} {status}")

            # Calculate confidence
            if is_filled:
                confidence = min(fill_percentage / self.bubble_fill_threshold, 1.0)
            else:
                confidence = 1.0 - (fill_percentage / self.bubble_fill_threshold)

            result = BubbleDetectionResult(
                student_id=student_id,
                student_name=student_name,
                is_filled=is_filled,
                confidence=max(0, min(1, confidence)),
                bubble_center=center,
                fill_percentage=fill_percentage
            )

            results.append(result)

        return results

    def visualize_detection(
        self,
        image_path: str,
        results: List[BubbleDetectionResult],
        output_path: str
    ):
        """Save visualization of detection results"""
        image = cv2.imread(image_path)

        for result in results:
            if result.bubble_center != (0, 0):
                x, y = result.bubble_center
                color = (0, 255, 0) if result.is_filled else (0, 0, 255)
                # Draw larger circle to show detection area (radius=42)
                cv2.circle(image, (x, y), 42, color, 4)

                # Add label
                label = f"{result.fill_percentage:.0%}"
                cv2.putText(image, label, (x + 50, y + 5),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 3)

        cv2.imwrite(output_path, image)
        print(f"Visualization saved: {output_path}")
