"""
calibration/calibration_validator.py — Calibration Health Monitor (Section 33)
================================================================================
Monitors the overall health of the camera calibration by combining:
- Camera health score
- Homography quality
- Landmark stability (camera shift detection)
- Reprojection error analysis

Publishes:
  camera_health, homography_health, camera_shift_detected, calibration_valid
"""

import logging
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)


class CalibrationValidator:
    """Calibration health monitoring and validation.

    Combines multiple health signals to determine if the camera
    calibration (homography) is still trustworthy.

    Args:
        config: Dict with calibration validation settings.
    """

    def __init__(self, config: Optional[dict] = None) -> None:
        cfg = config or {}
        self._shift_threshold: float = cfg.get("shift_threshold", 15.0)
        self._health_threshold: float = cfg.get("health_threshold", 0.50)
        self._reprojection_tolerance: float = cfg.get("reprojection_tolerance", 5.0)

        # State
        self._calibration_valid: bool = True
        self._homography_health: float = 1.0
        self._camera_shift_detected: bool = False
        self._shift_magnitude: float = 0.0

    def validate(
        self,
        camera_health: float,
        landmark_displacements: Optional[list[float]] = None,
        reprojection_errors: Optional[list[float]] = None,
    ) -> dict:
        """Run calibration validation.

        Args:
            camera_health: Overall camera health score (0-1).
            landmark_displacements: Pixel displacements of reference landmarks.
            reprojection_errors: Reprojection errors for calibration points.

        Returns:
            Dict with calibration health status.
        """
        # Camera shift from landmark tracking
        self._camera_shift_detected = False
        self._shift_magnitude = 0.0
        if landmark_displacements:
            mean_disp = float(np.mean(landmark_displacements))
            self._shift_magnitude = mean_disp
            if mean_disp > self._shift_threshold:
                self._camera_shift_detected = True
                logger.warning(
                    f"📷 CAMERA SHIFT DETECTED: "
                    f"mean displacement = {mean_disp:.1f}px "
                    f"(threshold = {self._shift_threshold}px)"
                )

        # Homography health from reprojection errors
        if reprojection_errors:
            mean_err = float(np.mean(reprojection_errors))
            self._homography_health = max(
                0.0, 1.0 - mean_err / (self._reprojection_tolerance * 5)
            )
        else:
            # No reprojection data — estimate from other signals
            self._homography_health = min(1.0, camera_health * 1.1)

        # Overall calibration validity
        self._calibration_valid = (
            not self._camera_shift_detected
            and self._homography_health > self._health_threshold
            and camera_health > self._health_threshold
        )

        if not self._calibration_valid:
            logger.warning(
                f"⚠️ CALIBRATION INVALID: "
                f"shift={self._camera_shift_detected}, "
                f"homography_health={self._homography_health:.2f}, "
                f"camera_health={camera_health:.2f}"
            )

        return {
            "camera_health": round(camera_health, 3),
            "homography_health": round(self._homography_health, 3),
            "camera_shift_detected": self._camera_shift_detected,
            "shift_magnitude_px": round(self._shift_magnitude, 1),
            "calibration_valid": self._calibration_valid,
        }

    @property
    def is_valid(self) -> bool:
        return self._calibration_valid

    @property
    def homography_health(self) -> float:
        return self._homography_health
