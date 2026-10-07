"""
geometry/lane_assignment.py — Dynamic Lane Assignment (Sections 34-37)
=======================================================================
Multi-factor lane assignment using centerline distance, heading similarity,
and trajectory compatibility — with hysteresis to prevent oscillation.

Lane Score:
  S_lane = w1 * (1 - d_norm) + w2 * H_match + w3 * T_match

Falls back to polygon membership if centerlines are not configured.
"""

import logging
from typing import Optional

import numpy as np

from geometry.centerlines import CenterlineManager

logger = logging.getLogger(__name__)


class LaneAssigner:
    """Dynamic lane assignment with multi-factor scoring and hysteresis.

    Assigns each vehicle to the most probable lane using:
    1. Normalized distance from lane centerline
    2. Heading similarity (cosine between vehicle heading and lane direction)
    3. Trajectory compatibility (alignment of recent trajectory with lane)

    Hysteresis prevents rapid lane switching at boundaries (Section 37).

    Args:
        centerline_manager: Loaded CenterlineManager.
        config: Dict from thresholds.yaml under 'lane_assignment'.
    """

    def __init__(
        self,
        centerline_manager: CenterlineManager,
        config: dict,
    ) -> None:
        self._cm = centerline_manager
        weights = config.get("weights", {})
        self._w_distance: float = weights.get("distance", 0.40)
        self._w_heading: float = weights.get("heading", 0.35)
        self._w_trajectory: float = weights.get("trajectory", 0.25)
        self._switch_margin: float = config.get("switch_margin", 0.15)

        # Per-vehicle current lane assignment (for hysteresis)
        self._current_lanes: dict[int, str] = {}     # track_id → lane_id
        self._current_scores: dict[int, float] = {}   # track_id → score

    def assign_lane(
        self,
        track_id: int,
        world_pos: np.ndarray,
        heading_deg: float,
        trajectory: Optional[list[tuple[float, float]]] = None,
    ) -> tuple[str, float]:
        """Assign a vehicle to the best lane.

        Args:
            track_id: Track identifier.
            world_pos: [x, y] world position in meters.
            heading_deg: Vehicle heading in degrees (0=North, CW).
            trajectory: Recent world positions for trajectory matching.

        Returns:
            (lane_id, score) — best lane and its score.
        """
        if not self._cm.lanes:
            return ("unknown", 0.0)

        best_lane: str = "unknown"
        best_score: float = -1.0

        for lane_id, lane in self._cm.lanes.items():
            score = self._compute_lane_score(
                world_pos, heading_deg, trajectory, lane_id
            )
            if score > best_score:
                best_score = score
                best_lane = lane_id

        # Apply hysteresis (Section 37)
        current = self._current_lanes.get(track_id)
        if current is not None and current != best_lane:
            current_score = self._current_scores.get(track_id, 0.0)
            if best_score < current_score + self._switch_margin:
                # Keep current lane — new lane doesn't exceed by enough margin
                return (current, current_score)

        # Update assignment
        self._current_lanes[track_id] = best_lane
        self._current_scores[track_id] = best_score

        return (best_lane, best_score)

    def _compute_lane_score(
        self,
        world_pos: np.ndarray,
        heading_deg: float,
        trajectory: Optional[list[tuple[float, float]]],
        lane_id: str,
    ) -> float:
        """Compute composite lane assignment score (Section 36).

        S_lane = w1 * (1 - d_norm) + w2 * H_match + w3 * T_match
        """
        lane = self._cm.lanes[lane_id]

        # 1. Distance component — normalized by half lane width
        distance = self._cm.distance_to_centerline(world_pos, lane_id)
        half_width = lane.width_m / 2.0
        d_norm = min(distance / half_width, 1.0) if half_width > 0 else 1.0
        distance_score = 1.0 - d_norm

        # Vehicle too far from lane → zero score
        if distance > lane.width_m * 1.5:
            return 0.0

        # 2. Heading component — cosine similarity
        heading_score = self._heading_match(heading_deg, lane)

        # 3. Trajectory component
        trajectory_score = self._trajectory_match(trajectory, lane_id)

        score = (
            self._w_distance * distance_score
            + self._w_heading * heading_score
            + self._w_trajectory * trajectory_score
        )

        return float(score)

    def _heading_match(self, heading_deg: float, lane) -> float:
        """Cosine similarity between vehicle heading and lane direction.

        Returns value in [0, 1] where 1.0 = perfectly aligned.
        """
        # Convert headings to unit vectors
        vh = np.radians(heading_deg)
        lh = np.radians(lane.expected_heading_deg)

        v_vec = np.array([np.sin(vh), -np.cos(vh)])
        l_vec = np.array([np.sin(lh), -np.cos(lh)])

        cos_sim = float(np.dot(v_vec, l_vec))

        # Map from [-1, 1] to [0, 1]
        return max(0.0, (cos_sim + 1.0) / 2.0)

    def _trajectory_match(
        self,
        trajectory: Optional[list[tuple[float, float]]],
        lane_id: str,
    ) -> float:
        """How well does the recent trajectory align with the lane?

        Computes average distance of trajectory points to the centerline.
        """
        if not trajectory or len(trajectory) < 2:
            return 0.5  # Neutral when no trajectory available

        lane = self._cm.lanes.get(lane_id)
        if lane is None:
            return 0.5

        distances = []
        for point in trajectory[-10:]:  # Use last 10 positions
            p = np.array(point)
            d = self._cm.distance_to_centerline(p, lane_id)
            distances.append(d)

        if not distances:
            return 0.5

        avg_dist = np.mean(distances)
        half_width = lane.width_m / 2.0

        # Score: closer to centerline = better
        d_norm = min(avg_dist / half_width, 1.0) if half_width > 0 else 1.0
        return float(1.0 - d_norm)

    def get_lane_confidence(self, track_id: int) -> float:
        """Get the confidence score of the current lane assignment.

        Args:
            track_id: Track identifier.

        Returns:
            Score in [0.0, 1.0].
        """
        return self._current_scores.get(track_id, 0.0)

    def cleanup_track(self, track_id: int) -> None:
        """Remove tracking state for a lost track."""
        self._current_lanes.pop(track_id, None)
        self._current_scores.pop(track_id, None)
