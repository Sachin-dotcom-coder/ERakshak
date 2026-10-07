"""
geometry/centerlines.py — Lane Centerline Representation (Sections 34-35)
==========================================================================
Represents lanes as centerline polylines + width instead of just polygons.
Provides fast point-to-centerline distance calculations for lane assignment.
"""

import logging
from dataclasses import dataclass
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class LaneCenterline:
    """A lane represented by its centerline polyline and width.

    Attributes:
        lane_id: Unique lane identifier.
        approach: Approach direction (e.g., "NS", "EW").
        points: List of [x, y] world-coordinate points (meters).
        width_m: Lane width in meters.
        expected_heading_deg: Expected traffic heading (0=North, CW).
        max_queue_capacity_m: Maximum queue length before spillback.
        stop_line: Stop line position [x, y] in world coords.
    """
    lane_id: str
    approach: str
    points: np.ndarray          # (N, 2) array of world points
    width_m: float
    expected_heading_deg: float
    max_queue_capacity_m: float
    stop_line: Optional[np.ndarray] = None  # [x, y]

    @property
    def direction_vector(self) -> np.ndarray:
        """Unit direction vector from approach to stop line."""
        if len(self.points) < 2:
            # Fall back to heading
            rad = np.radians(self.expected_heading_deg)
            return np.array([np.sin(rad), -np.cos(rad)])

        direction = self.points[-1] - self.points[0]
        norm = np.linalg.norm(direction)
        if norm < 1e-6:
            rad = np.radians(self.expected_heading_deg)
            return np.array([np.sin(rad), -np.cos(rad)])
        return direction / norm


class CenterlineManager:
    """Manages lane centerlines and provides distance calculations.

    Loads lane centerline definitions from config and provides fast
    point-to-centerline distance computation for lane assignment.

    Args:
        lanes_config: Dict from lanes.yaml.
    """

    def __init__(self, lanes_config: dict) -> None:
        self.lanes: dict[str, LaneCenterline] = {}
        self._load_lanes(lanes_config)

    def _load_lanes(self, config: dict) -> None:
        """Load lane definitions from config."""
        lanes_dict = config.get("lanes", {})

        for lane_id, lane_cfg in lanes_dict.items():
            points = np.array(lane_cfg.get("centerline", []), dtype=np.float64)
            stop_line = lane_cfg.get("stop_line_position")
            if stop_line:
                stop_line = np.array(stop_line, dtype=np.float64)

            self.lanes[lane_id] = LaneCenterline(
                lane_id=lane_id,
                approach=lane_cfg.get("approach", ""),
                points=points,
                width_m=lane_cfg.get("width_m", 3.5),
                expected_heading_deg=lane_cfg.get("expected_heading_deg", 0),
                max_queue_capacity_m=lane_cfg.get("max_queue_capacity_m", 100.0),
                stop_line=stop_line,
            )

        logger.info(f"Loaded {len(self.lanes)} lane centerlines")

    def distance_to_centerline(
        self,
        point: np.ndarray,
        lane_id: str,
    ) -> float:
        """Calculate shortest distance from a point to a lane centerline.

        d(P, L) = min_{x ∈ L} ||P - x||   (Section 35)

        Uses point-to-line-segment distance for each segment of the polyline.

        Args:
            point: [x, y] world position.
            lane_id: Lane identifier.

        Returns:
            Shortest distance in meters. Returns float('inf') if lane not found.
        """
        lane = self.lanes.get(lane_id)
        if lane is None or len(lane.points) < 2:
            return float("inf")

        min_dist = float("inf")
        for i in range(len(lane.points) - 1):
            seg_start = lane.points[i]
            seg_end = lane.points[i + 1]
            dist = self._point_to_segment_distance(point, seg_start, seg_end)
            min_dist = min(min_dist, dist)

        return min_dist

    def distance_to_stop_line(
        self,
        point: np.ndarray,
        lane_id: str,
    ) -> float:
        """Distance from a point to the lane's stop line.

        Args:
            point: [x, y] world position.
            lane_id: Lane identifier.

        Returns:
            Distance in meters.
        """
        lane = self.lanes.get(lane_id)
        if lane is None or lane.stop_line is None:
            return float("inf")
        return float(np.linalg.norm(point - lane.stop_line))

    def projection_along_lane(
        self,
        point: np.ndarray,
        lane_id: str,
    ) -> float:
        """Project a point onto the lane centerline and return progress.

        Returns a value from 0.0 (start of approach) to 1.0 (stop line).

        Args:
            point: [x, y] world position.
            lane_id: Lane identifier.

        Returns:
            Progress along the lane centerline (0.0-1.0).
        """
        lane = self.lanes.get(lane_id)
        if lane is None or len(lane.points) < 2:
            return 0.0

        # Calculate total centerline length
        total_length = 0.0
        segment_lengths: list[float] = []
        for i in range(len(lane.points) - 1):
            seg_len = float(np.linalg.norm(lane.points[i + 1] - lane.points[i]))
            segment_lengths.append(seg_len)
            total_length += seg_len

        if total_length < 1e-6:
            return 0.0

        # Find closest segment and projection
        min_dist = float("inf")
        best_progress = 0.0
        accumulated = 0.0

        for i in range(len(lane.points) - 1):
            seg_start = lane.points[i]
            seg_end = lane.points[i + 1]
            t = self._project_onto_segment(point, seg_start, seg_end)
            proj_point = seg_start + t * (seg_end - seg_start)
            dist = float(np.linalg.norm(point - proj_point))

            if dist < min_dist:
                min_dist = dist
                best_progress = (accumulated + t * segment_lengths[i]) / total_length

            accumulated += segment_lengths[i]

        return float(np.clip(best_progress, 0.0, 1.0))

    @staticmethod
    def _point_to_segment_distance(
        point: np.ndarray,
        seg_start: np.ndarray,
        seg_end: np.ndarray,
    ) -> float:
        """Distance from point to line segment."""
        t = CenterlineManager._project_onto_segment(point, seg_start, seg_end)
        projection = seg_start + t * (seg_end - seg_start)
        return float(np.linalg.norm(point - projection))

    @staticmethod
    def _project_onto_segment(
        point: np.ndarray,
        seg_start: np.ndarray,
        seg_end: np.ndarray,
    ) -> float:
        """Project point onto line segment, returning parameter t ∈ [0, 1]."""
        seg_vec = seg_end - seg_start
        seg_len_sq = np.dot(seg_vec, seg_vec)

        if seg_len_sq < 1e-12:
            return 0.0

        t = np.dot(point - seg_start, seg_vec) / seg_len_sq
        return float(np.clip(t, 0.0, 1.0))

    def get_stop_line_position(self, lane_id: str) -> Optional[np.ndarray]:
        """Get the stop line position for a lane."""
        lane = self.lanes.get(lane_id)
        if lane is not None:
            return lane.stop_line
        return None

    def get_expected_heading(self, lane_id: str) -> float:
        """Get the expected traffic heading in degrees for a lane."""
        lane = self.lanes.get(lane_id)
        if lane is not None:
            return lane.expected_heading_deg
        return 180.0
