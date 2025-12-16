"""
Image Processing Module
Handles image preprocessing, calibration, and bubble detection
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
    Processes scanned bubble sheet images
    Detects calibration points, aligns image, and detects filled bubbles
    """

    def __init__(self):
        # Detection thresholds
        self.calibration_circle_min_radius = 5  # More lenient: 10 -> 5
        self.calibration_circle_max_radius = 50  # More lenient: 30 -> 50
        self.bubble_fill_threshold = 0.75  # 75% dark pixels = filled (increased from 0.6)
        self.confidence_threshold = 0.7

    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess scanned image

        Args:
            image: Input image (BGR)

        Returns:
            Preprocessed grayscale image
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            blurred,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV,
            11,
            2
        )

        return thresh

    def detect_calibration_points(
        self,
        image: np.ndarray
    ) -> Optional[CalibrationPoints]:
        """
        Detect 4 calibration circles in corners

        Args:
            image: Preprocessed image

        Returns:
            CalibrationPoints or None if not found
        """
        # Detect circles using Hough Circle Transform
        print(f"🔍 Looking for calibration circles (radius {self.calibration_circle_min_radius}-{self.calibration_circle_max_radius})...")
        circles = cv2.HoughCircles(
            image,
            cv2.HOUGH_GRADIENT,
            dp=1,
            minDist=100,
            param1=50,
            param2=20,  # More lenient: 30 -> 20
            minRadius=self.calibration_circle_min_radius,
            maxRadius=self.calibration_circle_max_radius
        )

        if circles is None:
            print("❌ No circles detected at all")
            return None

        print(f"✅ Found {len(circles[0])} circles")
        if len(circles[0]) < 4:
            print(f"❌ Need at least 4 circles, only found {len(circles[0])}")
            return None

        # Convert to list of (x, y, radius)
        circles = circles[0]
        circles_list = [(int(c[0]), int(c[1]), int(c[2])) for c in circles]

        # Sort circles to identify corners
        # Top-left: smallest x+y
        # Top-right: largest x, small y
        # Bottom-left: small x, largest y
        # Bottom-right: largest x+y

        circles_sorted = sorted(circles_list, key=lambda c: c[0] + c[1])
        top_left = circles_sorted[0][:2]

        circles_sorted = sorted(circles_list, key=lambda c: c[0] + c[1], reverse=True)
        bottom_right = circles_sorted[0][:2]

        circles_sorted = sorted(circles_list, key=lambda c: c[0] - c[1])
        bottom_left = circles_sorted[0][:2]

        circles_sorted = sorted(circles_list, key=lambda c: c[0] - c[1], reverse=True)
        top_right = circles_sorted[0][:2]

        return CalibrationPoints(
            top_left=top_left,
            top_right=top_right,
            bottom_left=bottom_left,
            bottom_right=bottom_right
        )

    def align_image(
        self,
        image: np.ndarray,
        calibration: CalibrationPoints,
        target_width: int = 595,  # A4 width in points
        target_height: int = 842  # A4 height in points
    ) -> np.ndarray:
        """
        Align and perspective-correct image using calibration points

        Args:
            image: Input image
            calibration: Detected calibration points
            target_width: Target width after alignment
            target_height: Target height after alignment

        Returns:
            Aligned image
        """
        # Source points (detected calibration circles)
        src_points = np.array([
            calibration.top_left,
            calibration.top_right,
            calibration.bottom_right,
            calibration.bottom_left
        ], dtype=np.float32)

        # Destination points (where we want them to be)
        dst_points = np.array([
            [0, 0],
            [target_width, 0],
            [target_width, target_height],
            [0, target_height]
        ], dtype=np.float32)

        # Calculate perspective transform matrix
        matrix = cv2.getPerspectiveTransform(src_points, dst_points)

        # Apply perspective transformation
        aligned = cv2.warpPerspective(
            image,
            matrix,
            (target_width, target_height)
        )

        return aligned

    def detect_bubble_fill(
        self,
        image: np.ndarray,
        bubble_x: int,
        bubble_y: int,
        bubble_radius: int
    ) -> Tuple[bool, float]:
        """
        Detect if a bubble is filled

        Args:
            image: Aligned grayscale image
            bubble_x: X coordinate of bubble center
            bubble_y: Y coordinate of bubble center
            bubble_radius: Bubble radius in pixels

        Returns:
            (is_filled, fill_percentage)
        """
        # Create circular mask
        mask = np.zeros(image.shape, dtype=np.uint8)
        cv2.circle(mask, (bubble_x, bubble_y), bubble_radius, 255, -1)

        # Extract pixel values only within the mask
        masked_pixels = image[mask > 0]

        # Count dark pixels (pixel value < 127 means dark/filled)
        dark_pixels = np.sum(masked_pixels < 127)
        total_pixels = len(masked_pixels)

        fill_percentage = dark_pixels / total_pixels if total_pixels > 0 else 0

        # Determine if filled
        is_filled = fill_percentage >= self.bubble_fill_threshold

        return is_filled, fill_percentage

    def process_bubble_sheet_page(
        self,
        image_path: str,
        bubble_templates: List[Dict]
    ) -> List[BubbleDetectionResult]:
        """
        Process a complete bubble sheet page

        Args:
            image_path: Path to scanned image
            bubble_templates: List of bubble coordinates from database

        Returns:
            List of detection results
        """
        # Read image
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not read image: {image_path}")

        # Preprocess
        preprocessed = self.preprocess_image(image)

        # Detect calibration points
        calibration = self.detect_calibration_points(preprocessed)
        if calibration is None:
            raise ValueError("Could not detect calibration points")

        # Align image
        aligned = self.align_image(image, calibration)
        aligned_gray = cv2.cvtColor(aligned, cv2.COLOR_BGR2GRAY)

        print(f"📐 Aligned image size: {aligned.shape[1]}x{aligned.shape[0]} (width x height)")
        print(f"📍 Calibration points detected:")
        print(f"   Top-Left: {calibration.top_left}")
        print(f"   Top-Right: {calibration.top_right}")
        print(f"   Bottom-Left: {calibration.bottom_left}")
        print(f"   Bottom-Right: {calibration.bottom_right}")

        # Detect bubbles
        results = []
        print(f"🔍 Processing {len(bubble_templates)} bubbles...")

        # Get aligned image dimensions
        img_height, img_width = aligned_gray.shape

        for template in bubble_templates:
            student_id = template['student_id']
            student_name = template['student_name']

            # Use ratios if available (more accurate after perspective transform)
            if 'bubble_x_ratio' in template and 'bubble_y_ratio' in template and template['bubble_x_ratio'] is not None:
                # Calculate from ratios
                bubble_x = int(template['bubble_x_ratio'] * img_width)
                bubble_y = int(template['bubble_y_ratio'] * img_height)
                print(f"  Student: {student_name} ({student_id})")
                print(f"    Using ratios: ({template['bubble_x_ratio']:.3f}, {template['bubble_y_ratio']:.3f}) -> ({bubble_x}, {bubble_y})")
            else:
                # Fallback to absolute coordinates with Y flip
                pdf_x = template['bubble_x']
                pdf_y = template['bubble_y']
                bubble_x = int(pdf_x)
                bubble_y = int(img_height - pdf_y)  # Flip Y axis
                print(f"  Student: {student_name} ({student_id})")
                print(f"    PDF coords: ({pdf_x:.1f}, {pdf_y:.1f}) -> Image coords: ({bubble_x}, {bubble_y})")

            bubble_radius = int(template['bubble_radius'])

            # Detect if bubble is filled
            is_filled, fill_percentage = self.detect_bubble_fill(
                aligned_gray,
                bubble_x,
                bubble_y,
                bubble_radius
            )

            print(f"    → Fill: {fill_percentage:.2%}, Is Filled: {is_filled}, Threshold: {self.bubble_fill_threshold}")

            # Calculate confidence
            if is_filled:
                confidence = min(fill_percentage / self.bubble_fill_threshold, 1.0)
            else:
                confidence = 1.0 - (fill_percentage / self.bubble_fill_threshold)

            result = BubbleDetectionResult(
                student_id=student_id,
                student_name=student_name,
                is_filled=is_filled,
                confidence=confidence,
                bubble_center=(bubble_x, bubble_y),
                fill_percentage=fill_percentage
            )

            results.append(result)

        print(f"✅ Detected {len(results)} bubbles")
        return results

    def visualize_detection(
        self,
        image_path: str,
        results: List[BubbleDetectionResult],
        output_path: str
    ):
        """
        Create visualization of bubble detection

        Args:
            image_path: Original image path
            results: Detection results
            output_path: Where to save visualization
        """
        image = cv2.imread(image_path)

        for result in results:
            x, y = result.bubble_center
            color = (0, 255, 0) if result.is_filled else (0, 0, 255)  # Green if filled, red if empty

            # Draw circle
            cv2.circle(image, (x, y), 20, color, 2)

            # Draw confidence
            cv2.putText(
                image,
                f"{result.confidence:.2f}",
                (x + 25, y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                color,
                1
            )

        cv2.imwrite(output_path, image)


# Example usage
if __name__ == '__main__':
    processor = ImageProcessor()

    # Sample bubble templates
    bubble_templates = [
        {
            'student_id': '20240001',
            'student_name': 'Ahmed Ali',
            'bubble_x': 550,
            'bubble_y': 650,
            'bubble_radius': 15
        },
        {
            'student_id': '20240002',
            'student_name': 'Fatima Hassan',
            'bubble_x': 550,
            'bubble_y': 680,
            'bubble_radius': 15
        }
    ]

    # Process image (example - would need actual scanned image)
    # results = processor.process_bubble_sheet_page('scanned_sheet.jpg', bubble_templates)
    #
    # for result in results:
    #     status = "PRESENT" if result.is_filled else "ABSENT"
    #     print(f"{result.student_name}: {status} (confidence: {result.confidence:.2%})")

    print("Image processor initialized successfully")
