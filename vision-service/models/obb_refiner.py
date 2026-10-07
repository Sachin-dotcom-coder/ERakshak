"""
models/obb_refiner.py — Optional Oriented Bounding Box Refinement (Section 27)
================================================================================
Provides heading estimation from oriented bounding boxes for select vehicles.

OBB representation: (center_x, center_y, width, height, angle)

Used selectively for:
- Heading estimation (complementing trajectory-based heading)
- Wrong-way detection support
- Lane alignment verification
- Turn classification improvement

Not applied to every vehicle — only when heading accuracy matters
and standard bbox heading is unreliable (e.g., short trajectories,
recently appeared vehicles, or ambiguous motion).
"""

import logging
from dataclasses import dataclass
from typing import Optional

import cv2
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class OrientedBox:
    """An oriented bounding box with heading information.

    Attributes:
        center: (x, y) center in pixel coordinates.
        size: (width, height) in pixels.
        angle_deg: Orientation angle in degrees (0-360, clockwise from North).
        heading_deg: Estimated vehicle heading (0=North, clockwise).
        heading_confidence: Confidence in the heading estimate (0-1).
    """
    center: tuple[float, float]
    size: tuple[float, float]
    angle_deg: float
    heading_deg: float
    heading_confidence: float


class OBBRefiner:
    """Optional Oriented Bounding Box refinement for heading estimation.

    Estimates vehicle orientation from the bounding box region using
    contour analysis and minimum-area rotated rectangles. This provides
    a heading estimate independent of trajectory, useful for:
    - New tracks with short trajectories
    - Wrong-way detection verification
    - Stationary vehicle orientation

    Args:
        config: Dict with OBB refinement settings.
    """

    def __init__(self, config: dict) -> None:
        self._enabled: bool = config.get("enabled", True)
        self._min_area_px: float = config.get("min_area_px", 3000)
        self._obb_model = None
        self._obb_model_available: bool = False

        # Try to load YOLO-OBB model if configured
        obb_weights = config.get("obb_weights_path")
        if obb_weights:
            self._try_load_obb_model(obb_weights)

    def _try_load_obb_model(self, weights_path: str) -> None:
        """Attempt to load a YOLO-OBB model."""
        try:
            logger.info(f"OBB weights path configured: {weights_path}")
            logger.info("OBB model loading scaffolded — using contour fallback")
            self._obb_model_available = False
        except Exception as e:
            logger.warning(f"OBB model not available: {e}. Using contour fallback.")
            self._obb_model_available = False

    def should_refine(
        self,
        bbox: np.ndarray,
        trajectory_length: int,
        heading_variance: float = 0.0,
    ) -> bool:
        """Determine if OBB refinement should be applied.

        Triggered when:
        - Trajectory is too short for reliable heading from motion
        - Heading from trajectory is highly variable (indicating noise)
        - Vehicle bbox is large enough for reliable orientation estimation

        Args:
            bbox: [x1, y1, x2, y2] bounding box.
            trajectory_length: Number of trajectory points available.
            heading_variance: Variance of recent heading estimates.

        Returns:
            True if OBB refinement should run.
        """
        if not self._enabled:
            return False

        area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])
        if area < self._min_area_px:
            return False  # Too small for reliable orientation

        # Short trajectory — heading from motion is unreliable
        if trajectory_length < 5:
            return True

        # High heading variance — motion-based heading is noisy
        if heading_variance > 30.0:
            return True

        return False

    def estimate_heading(
        self,
        frame: np.ndarray,
        bbox: np.ndarray,
        expected_heading_deg: Optional[float] = None,
    ) -> OrientedBox:
        """Estimate vehicle heading from the bounding box region.

        Uses minimum-area rotated rectangle on the vehicle contour
        to estimate orientation.

        Args:
            frame: Full BGR frame.
            bbox: [x1, y1, x2, y2] bounding box.
            expected_heading_deg: Expected lane heading for disambiguation.

        Returns:
            OrientedBox with heading estimate.
        """
        if self._obb_model_available:
            return self._estimate_with_model(frame, bbox, expected_heading_deg)
        return self._estimate_with_contours(frame, bbox, expected_heading_deg)

    def _estimate_with_model(
        self,
        frame: np.ndarray,
        bbox: np.ndarray,
        expected_heading: Optional[float],
    ) -> OrientedBox:
        """Estimate heading using dedicated OBB model. Scaffolded."""
        logger.debug("OBB model estimation — using contour fallback")
        return self._estimate_with_contours(frame, bbox, expected_heading)

    def _estimate_with_contours(
        self,
        frame: np.ndarray,
        bbox: np.ndarray,
        expected_heading: Optional[float],
    ) -> OrientedBox:
        """Estimate heading from contour-based minimum-area rotated rectangle.

        Strategy:
        1. Crop the bbox region
        2. Background subtraction via adaptive thresholding
        3. Find the largest contour
        4. Fit a minimum-area rotated rectangle
        5. Extract orientation angle
        6. Disambiguate 180° ambiguity using expected heading
        """
        x1, y1, x2, y2 = int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])
        h, w = frame.shape[:2]
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(w, x2), min(h, y2)

        center = ((x1 + x2) / 2.0, (y1 + y2) / 2.0)
        size = (float(x2 - x1), float(y2 - y1))

        if (x2 - x1) < 10 or (y2 - y1) < 10:
            return OrientedBox(
                center=center, size=size,
                angle_deg=0.0, heading_deg=0.0,
                heading_confidence=0.1,
            )

        # Crop and process
        crop = frame[y1:y2, x1:x2]
        gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)

        # Adaptive threshold to separate vehicle from background
        binary = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV, 11, 2,
        )

        # Morphological cleanup
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)

        # Find contours
        contours, _ = cv2.findContours(
            binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        if not contours:
            return OrientedBox(
                center=center, size=size,
                angle_deg=0.0, heading_deg=0.0,
                heading_confidence=0.1,
            )

        # Largest contour
        largest = max(contours, key=cv2.contourArea)

        if cv2.contourArea(largest) < 100:
            return OrientedBox(
                center=center, size=size,
                angle_deg=0.0, heading_deg=0.0,
                heading_confidence=0.2,
            )

        # Fit minimum-area rotated rectangle
        rect = cv2.minAreaRect(largest)
        rect_center, rect_size, rect_angle = rect

        # Convert OpenCV angle to heading:
        # OpenCV minAreaRect angle is in [-90, 0) range
        # We need to determine vehicle's long axis
        obb_w, obb_h = rect_size
        if obb_w < obb_h:
            # Width < Height means the long axis is more vertical
            orientation = rect_angle + 90
        else:
            orientation = rect_angle

        # Normalize to [0, 360)
        orientation = orientation % 360

        # Disambiguate 180° ambiguity using expected heading
        heading = orientation
        if expected_heading is not None:
            alt_heading = (orientation + 180) % 360
            diff_orig = abs(self._angle_diff(heading, expected_heading))
            diff_alt = abs(self._angle_diff(alt_heading, expected_heading))
            if diff_alt < diff_orig:
                heading = alt_heading

        # Confidence based on contour quality
        contour_area = cv2.contourArea(largest)
        bbox_area = (x2 - x1) * (y2 - y1)
        fill_ratio = contour_area / bbox_area if bbox_area > 0 else 0
        confidence = min(1.0, fill_ratio * 2.0)
        confidence = max(0.2, confidence)

        return OrientedBox(
            center=center,
            size=size,
            angle_deg=float(orientation),
            heading_deg=float(heading),
            heading_confidence=float(confidence),
        )

    @staticmethod
    def _angle_diff(a: float, b: float) -> float:
        """Compute signed angle difference, normalized to [-180, 180]."""
        diff = a - b
        while diff > 180:
            diff -= 360
        while diff < -180:
            diff += 360
        return diff
