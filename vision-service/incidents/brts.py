"""
incidents/brts.py — Trajectory-Based BRTS Violation Detection (Sections 58-60)
================================================================================
Upgrades BRTS intrusion detection from simple polygon + dwell time to
trajectory-based evidence with a state machine.

State Machine:
  OUTSIDE → ENTERED → POTENTIAL_VIOLATION → CONFIRMED → EXITED

Evidence:
  entry point, entry direction, distance traveled inside, dwell time,
  heading alignment with corridor axis, class confidence

False-Positive Reduction (Section 60):
  Require dwell + distance + direction confirmation before flagging.
"""

import logging
import math
import time
from enum import Enum
from typing import Optional

import cv2
import numpy as np

logger = logging.getLogger(__name__)


class BRTSViolationState(str, Enum):
    OUTSIDE = "outside"
    ENTERED = "entered"
    POTENTIAL_VIOLATION = "potential_violation"
    CONFIRMED = "confirmed"
    EXITED = "exited"


class BRTSViolationDetector:
    """Trajectory-based BRTS corridor violation detection.

    Args:
        config: Dict from thresholds.yaml under 'brts'.
        brts_polygon: List of [x, y] pixel coordinates defining the BRTS corridor.
        corridor_direction: Expected direction vector [dx, dy] of BRTS traffic.
        corridor_axis_deg: Corridor axis heading in degrees (0=North, CW).
    """

    def __init__(
        self,
        config: dict,
        brts_polygon: Optional[list] = None,
        corridor_direction: Optional[list] = None,
        corridor_axis_deg: float = 180.0,
    ) -> None:
        self._min_dwell: float = config.get("minimum_dwell_sec", 3.0)
        self._min_distance: float = config.get("minimum_distance_m", 5.0)
        self._conf_threshold: float = config.get("confirmation_probability", 0.80)
        self._max_angle: float = config.get("max_angle_to_corridor_deg", 30.0)
        self._authorized: set[str] = set(
            config.get("authorized_classes", ["bus", "brts_bus"])
        )

        # BRTS corridor geometry
        # Handle dict or list input for brts_polygon
        poly_points = brts_polygon
        if isinstance(poly_points, dict):
            poly_points = poly_points.get("polygon", [])

        self._polygon = (
            np.array(poly_points, dtype=np.int32) if poly_points else None
        )
        self._corridor_dir = (
            np.array(corridor_direction, dtype=np.float64)
            if corridor_direction else np.array([0.0, -1.0])
        )
        self._corridor_heading = corridor_axis_deg

        # Per-track violation state
        self._states: dict[int, BRTSViolationState] = {}
        self._entry_times: dict[int, float] = {}
        self._entry_positions: dict[int, tuple[float, float]] = {}
        self._distance_inside: dict[int, float] = {}
        self._last_positions: dict[int, tuple[float, float]] = {}
        self._violation_records: list[dict] = []

    def get_state(self, track_id: int) -> Optional[BRTSViolationState]:
        """Get current violation state for a track."""
        return self._states.get(track_id)

    def is_inside_corridor(
        self,
        pixel_point: tuple[float, float],
    ) -> bool:
        """Check if a point is inside the BRTS corridor polygon."""
        if self._polygon is None:
            return False
        result = cv2.pointPolygonTest(
            self._polygon, (float(pixel_point[0]), float(pixel_point[1])), False
        )
        return result >= 0

    def update(
        self,
        track_id: int,
        class_name: str,
        detection_confidence: float,
        pixel_point: tuple[float, float],
        world_pos: Optional[tuple[float, float]] = None,
        heading_deg: float = 0.0,
        speed_kmph: float = 0.0,
    ) -> Optional[dict]:
        """Update BRTS violation state for a tracked vehicle.

        Args:
            track_id: Track identifier.
            class_name: Detected vehicle class.
            detection_confidence: Detection confidence.
            pixel_point: Ground contact point in pixel coords.
            world_pos: World position (x_m, y_m).
            heading_deg: Vehicle heading in degrees.
            speed_kmph: Vehicle speed.

        Returns:
            Violation dict if confirmed, None otherwise.
        """
        now = time.time()
        is_inside = self.is_inside_corridor(pixel_point)
        is_authorized = class_name in self._authorized
        current_state = self._states.get(track_id, BRTSViolationState.OUTSIDE)

        # Authorized vehicles are never violations
        if is_authorized:
            self._states[track_id] = (
                BRTSViolationState.OUTSIDE if not is_inside else BRTSViolationState.OUTSIDE
            )
            return None

        # State machine transitions
        if current_state == BRTSViolationState.OUTSIDE:
            if is_inside:
                self._states[track_id] = BRTSViolationState.ENTERED
                self._entry_times[track_id] = now
                self._entry_positions[track_id] = world_pos or pixel_point
                self._distance_inside[track_id] = 0.0
                self._last_positions[track_id] = world_pos or pixel_point

        elif current_state == BRTSViolationState.ENTERED:
            if not is_inside:
                # Exited quickly — not a violation
                self._states[track_id] = BRTSViolationState.EXITED
                self._cleanup_track_state(track_id)
                return None

            # Update distance traveled inside
            self._update_distance(track_id, world_pos or pixel_point)
            dwell = now - self._entry_times.get(track_id, now)

            if dwell >= 1.0:  # Initial dwell threshold
                self._states[track_id] = BRTSViolationState.POTENTIAL_VIOLATION

        elif current_state == BRTSViolationState.POTENTIAL_VIOLATION:
            if not is_inside:
                self._states[track_id] = BRTSViolationState.EXITED
                self._cleanup_track_state(track_id)
                return None

            # Update distance
            self._update_distance(track_id, world_pos or pixel_point)

            dwell = now - self._entry_times.get(track_id, now)
            distance = self._distance_inside.get(track_id, 0.0)
            direction_aligned = self._check_direction(heading_deg)

            # Check confirmation criteria (Section 60)
            if (
                dwell >= self._min_dwell
                and distance >= self._min_distance
                and direction_aligned
            ):
                # Compute violation confidence
                confidence = self._compute_violation_confidence(
                    dwell, distance, detection_confidence, heading_deg
                )

                if confidence >= self._conf_threshold:
                    self._states[track_id] = BRTSViolationState.CONFIRMED

                    violation = {
                        "track_id": track_id,
                        "violation_type": "BRTS_INTRUSION",
                        "vehicle_class": class_name,
                        "duration_sec": round(dwell, 1),
                        "distance_inside_m": round(distance, 1),
                        "confidence": round(confidence, 3),
                        "entry_position": self._entry_positions.get(track_id),
                        "heading_deg": round(heading_deg, 1),
                        "timestamp": now,
                    }
                    self._violation_records.append(violation)

                    logger.warning(
                        f"🚫 BRTS VIOLATION CONFIRMED: track={track_id}, "
                        f"class={class_name}, dwell={dwell:.1f}s, "
                        f"dist={distance:.1f}m, conf={confidence:.2f}"
                    )
                    return violation

        elif current_state == BRTSViolationState.CONFIRMED:
            if not is_inside:
                self._states[track_id] = BRTSViolationState.EXITED
                self._cleanup_track_state(track_id)
            else:
                # Continue tracking for duration/distance update
                self._update_distance(track_id, world_pos or pixel_point)

        return None

    def _update_distance(
        self,
        track_id: int,
        current_pos: tuple[float, float],
    ) -> None:
        """Update distance traveled inside the corridor."""
        last = self._last_positions.get(track_id)
        if last is not None:
            dx = current_pos[0] - last[0]
            dy = current_pos[1] - last[1]
            dist = math.sqrt(dx * dx + dy * dy)
            self._distance_inside[track_id] = (
                self._distance_inside.get(track_id, 0.0) + dist
            )
        self._last_positions[track_id] = current_pos

    def _check_direction(self, heading_deg: float) -> bool:
        """Check if vehicle heading is aligned with corridor direction."""
        angle_diff = abs(heading_deg - self._corridor_heading)
        if angle_diff > 180:
            angle_diff = 360 - angle_diff
        # Vehicle traveling along corridor axis (not just crossing)
        return angle_diff < self._max_angle or angle_diff > (180 - self._max_angle)

    def _compute_violation_confidence(
        self,
        dwell: float,
        distance: float,
        detection_conf: float,
        heading_deg: float,
    ) -> float:
        """Compute violation confidence score (Section 59)."""
        # Dwell factor: longer dwell → higher confidence
        dwell_factor = min(1.0, dwell / (self._min_dwell * 2))

        # Distance factor
        dist_factor = min(1.0, distance / (self._min_distance * 2))

        # Direction factor
        angle_diff = abs(heading_deg - self._corridor_heading)
        if angle_diff > 180:
            angle_diff = 360 - angle_diff
        # Close to corridor axis = high confidence it's traveling IN the corridor
        if angle_diff < self._max_angle or angle_diff > (180 - self._max_angle):
            dir_factor = 1.0 - min(angle_diff, 180 - angle_diff) / self._max_angle
        else:
            dir_factor = 0.3

        confidence = (
            0.30 * dwell_factor
            + 0.25 * dist_factor
            + 0.25 * dir_factor
            + 0.20 * detection_conf
        )

        return float(np.clip(confidence, 0.0, 1.0))

    def _cleanup_track_state(self, track_id: int) -> None:
        """Remove internal state for a track that left the corridor."""
        self._entry_times.pop(track_id, None)
        self._entry_positions.pop(track_id, None)
        self._distance_inside.pop(track_id, None)
        self._last_positions.pop(track_id, None)

    def cleanup_track(self, track_id: int) -> None:
        """Remove all state for a lost track."""
        self._states.pop(track_id, None)
        self._cleanup_track_state(track_id)

    def get_violation_records(self) -> list[dict]:
        """Get all confirmed violation records."""
        return list(self._violation_records)

    def get_active_violations(self) -> list[int]:
        """Get track IDs with active confirmed violations."""
        return [
            tid for tid, state in self._states.items()
            if state == BRTSViolationState.CONFIRMED
        ]
