"""
tracking/occlusion.py — Occlusion Detection & State Machine (Sections 20-22)
==============================================================================
Estimates occlusion ratio per vehicle using bounding box overlap analysis.
Manages the occlusion state lifecycle and handles track reappearance matching.
"""

import logging
from typing import Optional

import numpy as np

from tracking.track_state import TrackLifecycle

logger = logging.getLogger(__name__)


class OcclusionEstimator:
    """Estimates per-vehicle occlusion ratio and manages occlusion state.

    Uses bounding box overlap with neighboring vehicles to estimate
    what fraction of a vehicle is hidden.

    Thresholds (Section 21):
    - < 0.20 → VISIBLE
    - 0.20–0.50 → PARTIALLY_OCCLUDED
    - > 0.50 → HEAVILY_OCCLUDED

    Args:
        config: Dict from thresholds.yaml under 'occlusion'.
    """

    def __init__(self, config: dict) -> None:
        self._visible_thresh: float = config.get("visible_threshold", 0.20)
        self._partial_thresh: float = config.get("partial_threshold", 0.50)

    def estimate_occlusion(
        self,
        target_bbox: np.ndarray,
        all_bboxes: list[np.ndarray],
        target_idx: int,
    ) -> float:
        """Estimate occlusion ratio for a single vehicle.

        Calculates the fraction of the target bbox area that is overlapped
        by other vehicle bboxes.

        Args:
            target_bbox: [x1,y1,x2,y2] of the target vehicle.
            all_bboxes: List of all vehicle bboxes in the frame.
            target_idx: Index of target in all_bboxes (to skip self).

        Returns:
            Occlusion ratio in [0.0, 1.0].
        """
        target_area = (
            (target_bbox[2] - target_bbox[0]) *
            (target_bbox[3] - target_bbox[1])
        )

        if target_area <= 0:
            return 0.0

        total_overlap = 0.0

        for i, other_bbox in enumerate(all_bboxes):
            if i == target_idx:
                continue

            # Calculate intersection
            x1 = max(target_bbox[0], other_bbox[0])
            y1 = max(target_bbox[1], other_bbox[1])
            x2 = min(target_bbox[2], other_bbox[2])
            y2 = min(target_bbox[3], other_bbox[3])

            if x2 > x1 and y2 > y1:
                intersection = (x2 - x1) * (y2 - y1)
                total_overlap += intersection

        occlusion_ratio = min(total_overlap / target_area, 1.0)
        return float(occlusion_ratio)

    def classify_occlusion(self, ratio: float) -> TrackLifecycle:
        """Classify occlusion level into lifecycle state.

        Args:
            ratio: Occlusion ratio in [0.0, 1.0].

        Returns:
            Appropriate TrackLifecycle state.
        """
        if ratio < self._visible_thresh:
            return TrackLifecycle.VISIBLE
        elif ratio < self._partial_thresh:
            return TrackLifecycle.PARTIALLY_OCCLUDED
        else:
            return TrackLifecycle.HEAVILY_OCCLUDED

    def estimate_all(
        self,
        bboxes: list[np.ndarray],
    ) -> list[float]:
        """Estimate occlusion ratios for all vehicles in a frame.

        Args:
            bboxes: List of all vehicle bboxes.

        Returns:
            List of occlusion ratios, one per vehicle.
        """
        ratios = []
        for i, bbox in enumerate(bboxes):
            ratio = self.estimate_occlusion(bbox, bboxes, i)
            ratios.append(ratio)
        return ratios

    def aggregate_lane_occlusion(
        self,
        vehicle_occlusions: list[float],
    ) -> float:
        """Aggregate occlusion ratios for a lane (Section 51).

        Args:
            vehicle_occlusions: List of per-vehicle occlusion ratios in a lane.

        Returns:
            Mean occlusion ratio for the lane.
        """
        if not vehicle_occlusions:
            return 0.0
        return float(np.mean(vehicle_occlusions))
