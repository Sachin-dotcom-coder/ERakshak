"""
camera/health.py — Camera Health Monitoring (Sections 28-31)
==============================================================
Comprehensive camera health monitoring:
- Brightness (Section 28)
- Blur detection via Laplacian variance (Section 30)
- Frozen camera detection via frame differencing (Section 29)
- Camera vibration via feature matching (Section 31)
- Composite health score
"""

import logging
from collections import deque
from typing import Optional

import cv2
import numpy as np

logger = logging.getLogger(__name__)


class CameraHealthMonitor:
    """Camera health monitoring with multiple quality metrics.

    Args:
        config: Dict from thresholds.yaml under 'camera'.
    """

    def __init__(self, config: dict) -> None:
        self._blur_threshold: float = config.get("blur_threshold", 100.0)
        self._freeze_threshold: float = config.get("freeze_threshold", 0.001)
        self._freeze_frames: int = config.get("freeze_frames", 30)
        self._brightness_low: float = config.get("brightness_low", 40)
        self._brightness_high: float = config.get("brightness_high", 220)
        self._vibration_threshold: float = config.get("vibration_threshold", 5.0)

        # State
        self._prev_frame_gray: Optional[np.ndarray] = None
        self._frozen_count: int = 0
        self._health_history: deque = deque(maxlen=30)

    def analyze(self, frame: np.ndarray) -> dict:
        """Analyze a frame and compute all camera health metrics.

        Args:
            frame: BGR image.

        Returns:
            Dict with all health metrics.
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Brightness
        brightness = float(np.mean(gray))
        brightness_status = self._classify_brightness(brightness)

        # Blur (Section 30)
        blur_score = float(cv2.Laplacian(gray, cv2.CV_64F).var())
        is_blurry = blur_score < self._blur_threshold

        # Contrast
        contrast = float(np.std(gray))

        # Frozen detection (Section 29)
        is_frozen = False
        frame_diff = 0.0
        if self._prev_frame_gray is not None:
            diff = cv2.absdiff(gray, self._prev_frame_gray)
            frame_diff = float(np.mean(diff)) / 255.0

            if frame_diff < self._freeze_threshold:
                self._frozen_count += 1
            else:
                self._frozen_count = 0

            is_frozen = self._frozen_count >= self._freeze_frames
        self._prev_frame_gray = gray.copy()

        # Camera vibration (Section 31)
        vibration_px = self._estimate_vibration(gray)
        is_vibrating = vibration_px > self._vibration_threshold

        # Composite health score
        health_score = self._compute_health_score(
            brightness, blur_score, is_frozen, vibration_px, contrast
        )
        self._health_history.append(health_score)

        result = {
            "health_score": round(health_score, 3),
            "brightness": round(brightness, 1),
            "brightness_status": brightness_status,
            "blur_score": round(blur_score, 1),
            "is_blurry": is_blurry,
            "contrast": round(contrast, 1),
            "frame_difference": round(frame_diff, 5),
            "is_frozen": is_frozen,
            "frozen_frames": self._frozen_count,
            "vibration_px": round(vibration_px, 2),
            "is_vibrating": is_vibrating,
        }

        # Log warnings
        if is_frozen:
            logger.warning(
                f"📷 Camera FROZEN for {self._frozen_count} frames!"
            )
        if is_blurry:
            logger.debug(
                f"📷 Camera blur detected (score={blur_score:.0f} "
                f"< threshold={self._blur_threshold})"
            )
        if is_vibrating:
            logger.debug(
                f"📷 Camera vibration detected ({vibration_px:.1f}px)"
            )

        return result

    def _classify_brightness(self, brightness: float) -> str:
        """Classify brightness into categories."""
        if brightness < self._brightness_low:
            return "dark"
        elif brightness > self._brightness_high:
            return "overexposed"
        elif brightness < self._brightness_low * 1.5:
            return "dim"
        else:
            return "normal"

    def _estimate_vibration(self, gray: np.ndarray) -> float:
        """Estimate camera vibration using feature matching (Section 31).

        Detects global image motion by comparing feature point positions
        between consecutive frames.

        Returns:
            Estimated vibration in pixels.
        """
        if self._prev_frame_gray is None:
            return 0.0

        # Use ORB features for speed
        try:
            orb = cv2.ORB_create(nfeatures=200)
            kp1, des1 = orb.detectAndCompute(self._prev_frame_gray, None)
            kp2, des2 = orb.detectAndCompute(gray, None)

            if des1 is None or des2 is None or len(kp1) < 10 or len(kp2) < 10:
                return 0.0

            # Match features
            bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
            matches = bf.match(des1, des2)

            if len(matches) < 5:
                return 0.0

            # Compute average displacement
            displacements = []
            for m in matches[:50]:  # Use top matches
                pt1 = np.array(kp1[m.queryIdx].pt)
                pt2 = np.array(kp2[m.trainIdx].pt)
                disp = np.linalg.norm(pt2 - pt1)
                displacements.append(disp)

            # Use median to be robust to outliers
            return float(np.median(displacements))

        except Exception as e:
            logger.debug(f"Vibration estimation failed: {e}")
            return 0.0

    def _compute_health_score(
        self,
        brightness: float,
        blur: float,
        frozen: bool,
        vibration: float,
        contrast: float,
    ) -> float:
        """Compute composite camera health score (0-1)."""
        # Brightness factor
        if brightness < self._brightness_low or brightness > self._brightness_high:
            brightness_factor = 0.5
        else:
            brightness_factor = 1.0

        # Blur factor
        blur_factor = min(1.0, blur / self._blur_threshold)

        # Frozen penalty
        frozen_factor = 0.0 if frozen else 1.0

        # Vibration factor
        vib_factor = max(0.0, 1.0 - vibration / (self._vibration_threshold * 3))

        # Contrast factor (low contrast = poor quality)
        contrast_factor = min(1.0, contrast / 40.0)

        health = (
            0.20 * brightness_factor
            + 0.25 * blur_factor
            + 0.25 * frozen_factor
            + 0.15 * vib_factor
            + 0.15 * contrast_factor
        )

        return float(np.clip(health, 0.0, 1.0))

    @property
    def avg_health(self) -> float:
        """Average health score over recent history."""
        if not self._health_history:
            return 1.0
        return float(np.mean(self._health_history))
