"""
confidence/object_confidence.py — Per-Vehicle Multi-Dimensional Confidence (Section 49)
=========================================================================================
Computes per-vehicle confidence scores across multiple dimensions:
  detection_confidence, tracking_confidence, class_confidence,
  position_confidence, speed_confidence, lane_confidence

These feed into the scene-level confidence and ultimately the
confidence-aware signal optimizer.
"""

import logging
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)


class ObjectConfidenceEstimator:
    """Per-vehicle multi-dimensional confidence scoring.

    For every tracked vehicle, computes six confidence dimensions
    that together characterize how much the system should trust
    the reported state of that vehicle.

    Args:
        config: Dict with confidence estimation settings.
    """

    def __init__(self, config: Optional[dict] = None) -> None:
        self._config = config or {}

    def compute(
        self,
        detection_confidence: float,
        track_quality: float = 0.5,
        class_stability: float = 0.5,
        position_confidence: Optional[float] = None,
        speed_confidence: Optional[float] = None,
        lane_confidence: Optional[float] = None,
        occlusion_ratio: float = 0.0,
        age_frames: int = 0,
    ) -> dict[str, float]:
        """Compute all confidence dimensions for a vehicle.

        Args:
            detection_confidence: Raw detection score from YOLO.
            track_quality: Track quality score from Re-ID/motion (0-1).
            class_stability: Class stability from vote history (0-1).
            position_confidence: Position confidence (from calibration quality).
            speed_confidence: Speed estimation confidence.
            lane_confidence: Lane assignment confidence.
            occlusion_ratio: Estimated occlusion (0-1).
            age_frames: Track age in frames.

        Returns:
            Dict with all confidence dimensions.
        """
        # Detection confidence (raw from model)
        det_conf = float(np.clip(detection_confidence, 0.0, 1.0))

        # Tracking confidence (from track quality + age)
        age_factor = min(1.0, age_frames / 30.0)  # Full confidence after 30 frames
        track_conf = 0.6 * track_quality + 0.4 * age_factor

        # Class confidence (from stability — are we sure about the class?)
        cls_conf = class_stability

        # Position confidence (from homography quality + occlusion)
        pos_conf = position_confidence if position_confidence is not None else (
            max(0.2, 1.0 - occlusion_ratio * 0.5)
        )

        # Speed confidence (from speed estimator)
        spd_conf = speed_confidence if speed_confidence is not None else 0.5

        # Lane confidence (from lane assigner)
        ln_conf = lane_confidence if lane_confidence is not None else 0.5

        # Composite (weighted average of all dimensions)
        composite = (
            0.25 * det_conf
            + 0.20 * track_conf
            + 0.15 * cls_conf
            + 0.15 * pos_conf
            + 0.10 * spd_conf
            + 0.15 * ln_conf
        )

        return {
            "detection_confidence": round(det_conf, 3),
            "tracking_confidence": round(float(np.clip(track_conf, 0, 1)), 3),
            "class_confidence": round(float(np.clip(cls_conf, 0, 1)), 3),
            "position_confidence": round(float(np.clip(pos_conf, 0, 1)), 3),
            "speed_confidence": round(float(np.clip(spd_conf, 0, 1)), 3),
            "lane_confidence": round(float(np.clip(ln_conf, 0, 1)), 3),
            "composite_confidence": round(float(np.clip(composite, 0, 1)), 3),
        }
