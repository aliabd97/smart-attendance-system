"""
Image Processing Module - ZipGrade Style
Dynamic bubble detection without saved coordinates
"""

import cv2
import numpy as np
from typing import Tuple, List, Dict, Optional
from dataclasses import dataclass


@dataclass
class CalibrationPoints:
    """Calibration points detected in the image"""
    top_left: Tuple[int, int]
    top_right: Tuple[int, int]
    bottom_left: Tuple[int, int]
    bottom_right: Tuple[int, int]


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
    ZipGrade-style OMR processor
    Dynamically detects bubbles without relying on saved coordinates
    """

    def __init__(self):
        self.calibration_circle_min_radius = 5
        self.calibration_circle_max_radius = 50
        self.bubble_fill_threshold = 0.65  # 65% dark = filled
        self.confidence_threshold = 0.7

    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for better circle detection"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        thresh = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV, 11, 2
        )
        return thresh

    def detect_calibration_points(self, image: np.ndarray) -> Optional[CalibrationPoints]:
        """Detect 4 corner calibration circles"""
        circles = cv2.HoughCircles(
            image, cv2.HOUGH_GRADIENT, dp=1, minDist=100,
            param1=50, param2=20,
            minRadius=self.calibration_circle_min_radius,
            maxRadius=self.calibration_circle_max_radius
        )

        if circles is None or len(circles[0]) < 4:
            return None

        circles_list = [(int(c[0]), int(c[1]), int(c[2])) for c in circles[0]]

        # Find corners
        circles_list.sort(key=lambda c: c[0] + c[1])  # Top-left
        top_left = circles_list[0][:2]

        circles_list.sort(key=lambda c: c[1] - c[0])  # Bottom-left
        bottom_left = circles_list[0][:2]

        circles_list.sort(key=lambda c: -c[0] - c[1])  # Bottom-right
        bottom_right = circles_list[0][:2]

        circles_list.sort(key=lambda c: c[0] - c[1], reverse=True)  # Top-right
        top_right = circles_list[0][:2]

        return CalibrationPoints(
            top_left=top_left, top_right=top_right,
            bottom_left=bottom_left, bottom_right=bottom_right
        )

    def align_image(
        self, image: np.ndarray, calibration: CalibrationPoints,
        target_width: int = 595, target_height: int = 842
    ) -> np.ndarray:
        """Align image using perspective transformation"""
        src_points = np.array([
            calibration.top_left, calibration.top_right,
            calibration.bottom_right, calibration.bottom_left
        ], dtype=np.float32)

        dst_points = np.array([
            [0, 0], [target_width, 0],
            [target_width, target_height], [0, target_height]
        ], dtype=np.float32)

        matrix = cv2.getPerspectiveTransform(src_points, dst_points)
        aligned = cv2.warpPerspective(image, matrix, (target_width, target_height))
        return aligned

    def detect_attendance_bubbles(self, aligned_gray: np.ndarray, expected_count: int) -> List[Tuple[int, int, int]]:
        """
        ZipGrade-style: Dynamically detect attendance bubbles

        Returns list of (x, y, radius) sorted top-to-bottom
        """
        height, width = aligned_gray.shape

        # Apply edge detection for better circle detection
        edges = cv2.Canny(aligned_gray, 50, 150)

        # Detect ALL circles in the image
        circles = cv2.HoughCircles(
            edges,
            cv2.HOUGH_GRADIENT,
            dp=1,
            minDist=10,  # Reduced for better detection
            param1=50,
            param2=15,   # Reduced for more sensitivity
            minRadius=4,
            maxRadius=12
        )

        if circles is None:
            print("⚠️  No circles detected!")
            return []

        print(f"🔍 Detected {len(circles[0])} total circles")

        # Filter: Keep only circles in right side (attendance column)
        # Typically attendance bubbles are at 75-85% from left
        attendance_bubbles = []
        min_x = width * 0.70  # Right 30% of page
        max_x = width * 0.95
        min_y = 150  # Skip header
        max_y = height - 100  # Skip footer

        for circle in circles[0]:
            x, y, r = int(circle[0]), int(circle[1]), int(circle[2])
            if min_x < x < max_x and min_y < y < max_y:
                attendance_bubbles.append((x, y, r))

        print(f"✅ Found {len(attendance_bubbles)} bubbles in attendance area")

        # Sort by Y position (top to bottom)
        attendance_bubbles.sort(key=lambda c: c[1])

        # Return only expected number
        return attendance_bubbles[:expected_count]

    def detect_bubble_fill(
        self, image: np.ndarray, bubble_x: int, bubble_y: int, bubble_radius: int
    ) -> Tuple[bool, float]:
        """Check if bubble is filled"""
        mask = np.zeros(image.shape, dtype=np.uint8)
        cv2.circle(mask, (bubble_x, bubble_y), bubble_radius, 255, -1)

        masked_pixels = image[mask > 0]
        if len(masked_pixels) == 0:
            return False, 0.0

        dark_pixels = np.sum(masked_pixels < 127)
        fill_percentage = dark_pixels / len(masked_pixels)
        is_filled = fill_percentage >= self.bubble_fill_threshold

        return is_filled, fill_percentage

    def process_bubble_sheet_page(
        self, image_path: str, bubble_templates: List[Dict]
    ) -> List[BubbleDetectionResult]:
        """
        ZipGrade-style processing:
        1. Align image
        2. Detect bubbles dynamically
        3. Match with student list by order
        """
        # Read and preprocess
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not read image: {image_path}")

        preprocessed = self.preprocess_image(image)

        # Detect calibration and align
        calibration = self.detect_calibration_points(preprocessed)
        if calibration is None:
            raise ValueError("Could not detect calibration points")

        aligned = self.align_image(image, calibration)
        aligned_gray = cv2.cvtColor(aligned, cv2.COLOR_BGR2GRAY)

        print(f"📐 Aligned: {aligned.shape[1]}x{aligned.shape[0]}")

        # Dynamically detect attendance bubbles
        detected_bubbles = self.detect_attendance_bubbles(
            aligned_gray, len(bubble_templates)
        )

        # Match bubbles with students (by order)
        results = []
        for idx, template in enumerate(bubble_templates):
            student_id = template['student_id']
            student_name = template['student_name']

            if idx < len(detected_bubbles):
                bubble_x, bubble_y, bubble_radius = detected_bubbles[idx]
                is_filled, fill_percentage = self.detect_bubble_fill(
                    aligned_gray, bubble_x, bubble_y, bubble_radius
                )

                status = "✅ PRESENT" if is_filled else "❌ ABSENT"
                print(f"  {student_name}: ({bubble_x}, {bubble_y}) Fill={fill_percentage:.1%} {status}")

                confidence = min(fill_percentage / self.bubble_fill_threshold, 1.0) if is_filled else 1.0 - (fill_percentage / self.bubble_fill_threshold)

                result = BubbleDetectionResult(
                    student_id=student_id,
                    student_name=student_name,
                    is_filled=is_filled,
                    confidence=confidence,
                    bubble_center=(bubble_x, bubble_y),
                    fill_percentage=fill_percentage
                )
            else:
                # No bubble found for this student
                print(f"  {student_name}: ⚠️  NO BUBBLE DETECTED")
                result = BubbleDetectionResult(
                    student_id=student_id,
                    student_name=student_name,
                    is_filled=False,
                    confidence=0.0,
                    bubble_center=(0, 0),
                    fill_percentage=0.0
                )

            results.append(result)

        return results

    def visualize_detection(
        self, image_path: str, results: List[BubbleDetectionResult], output_path: str
    ):
        """Visualize detected bubbles"""
        image = cv2.imread(image_path)

        for result in results:
            if result.bubble_center != (0, 0):
                x, y = result.bubble_center
                color = (0, 255, 0) if result.is_filled else (0, 0, 255)
                cv2.circle(image, (x, y), 8, color, 2)
                cv2.putText(image, result.student_name[:10], (x+15, y),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)

        cv2.imwrite(output_path, image)
