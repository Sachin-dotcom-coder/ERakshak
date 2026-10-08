"""
confidence/scene_confidence.py — Scene-Level Confidence (Sections 50-52)
=========================================================================
Scene-level confidence aggregation:

C_scene = 0.30*C_det + 0.20*C_track + 0.15*C_camera + 0.15*C_calib + 0.20*C_visibility

Also computes:
- Per-lane occlusion ratio (Section 51)
- Missed vehicle uncertainty interval (Section 52)
"""

import logging
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)


class SceneConfidenceEstimator:
    """Scene-level confidence aggregation from multiple perception signals.

    Args:
        config: Dict from thresholds.yaml under 'confidence'.
    """

    def __init__(self, config: Optional[dict] = None) -> None:
        cfg = config or {}
        weights = cfg.get("scene_weights", {})
        self._w_det: float = weights.get("detection", 0.30)
        self._w_track: float = weights.get("tracking", 0.20)
        self._w_camera: float = weights.get("camera", 0.15)
        self._w_calib: float = weights.get("calibration", 0.15)
        self._w_vis: float = weights.get("visibility", 0.20)
        self._cautious_threshold: float = cfg.get(
            "cautious_mode_threshold", 0.60
        )

    def compute_scene_confidence(
        self,
        detection_quality: float,
        tracking_quality: float,
        camera_health: float,
        calibration_health: float,
        visibility: float,
    ) -> dict:
        """Compute scene-level confidence (Section 50).

        Args:
            detection_quality: Average detection confidence across the scene.
            tracking_quality: Average tracking quality.
            camera_health: Camera health score.
            calibration_health: Homography/calibration health.
            visibility: Scene visibility score.

        Returns:
            Dict with scene confidence and mode recommendation.
        """
        scene_conf = (
            self._w_det * detection_quality
            + self._w_track * tracking_quality
            + self._w_camera * camera_health
            + self._w_calib * calibration_health
            + self._w_vis * visibility
        )
        scene_conf = float(np.clip(scene_conf, 0.0, 1.0))

        # Determine operating mode
        is_cautious = scene_conf < self._cautious_threshold

        return {
            "scene_confidence": round(scene_conf, 3),
            "detection_quality": round(detection_quality, 3),
            "tracking_quality": round(tracking_quality, 3),
            "camera_health": round(camera_health, 3),
            "calibration_health": round(calibration_health, 3),
            "visibility": round(visibility, 3),
            "cautious_mode": is_cautious,
        }

    def compute_lane_occlusion(
        self,
        vehicles: list[dict],
    ) -> float:
        """Compute aggregate occlusion ratio for a lane (Section 51).

        O_lane = mean(occlusion_ratio per vehicle)

        Args:
            vehicles: List of vehicle dicts with 'occlusion_ratio'.

        Returns:
            Lane-level occlusion ratio (0-1).
        """
        if not vehicles:
            return 0.0

        ratios = [v.get("occlusion_ratio", 0.0) for v in vehicles]
        return float(np.mean(ratios))

    def estimate_missed_vehicles(
        self,
        detected_count: int,
        scene_confidence: float,
        occlusion_ratio: float,
    ) -> dict:
        """Estimate missed vehicle uncertainty interval (Section 52).

        Provides an uncertainty range rather than a precise missed count.
        The range widens with lower confidence and higher occlusion.

        Args:
            detected_count: Number of detected vehicles.
            scene_confidence: Overall scene confidence.
            occlusion_ratio: Lane/scene occlusion level.

        Returns:
            Dict with estimated count range.
        """
        # Under perfect conditions, detected ≈ actual
        # Under poor conditions, we might miss up to ~30% of vehicles
        miss_rate = (1.0 - scene_confidence) * 0.3 + occlusion_ratio * 0.2

        lower = max(0, int(detected_count * (1.0 - miss_rate * 0.5)))
        upper = int(detected_count * (1.0 + miss_rate))

        return {
            "detected_count": detected_count,
            "estimated_range": [lower, upper],
            "miss_rate_estimate": round(miss_rate, 3),
            "confidence": round(scene_confidence, 3),
        }
