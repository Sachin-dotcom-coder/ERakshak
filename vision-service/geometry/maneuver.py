"""
geometry/maneuver.py — Movement / Maneuver Classification (Sections 38-39)
===========================================================================
Classifies vehicle maneuvers (straight, left, right, u-turn) from trajectory
heading changes. Provides per-movement PCU counts for the signal optimizer.
"""

import logging
from enum import Enum
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)


class ManeuverType(str, Enum):
    STRAIGHT = "straight"
    LEFT = "left"
    RIGHT = "right"
    U_TURN = "u_turn"
    UNKNOWN = "unknown"


class ManeuverClassifier:
    """Classifies vehicle maneuvers from trajectory heading changes.

    Uses the difference between entry heading and current/exit heading
    to determine if a vehicle is going straight, turning left, turning
    right, or making a U-turn.

    Heading change ranges:
    - Straight: |Δθ| < 30°
    - Left: -150° < Δθ < -30°  (counterclockwise)
    - Right: 30° < Δθ < 150°   (clockwise)
    - U-turn: |Δθ| > 150°

    Args:
        heading_window: Number of trajectory points to analyze.
    """

    def __init__(self, heading_window: int = 20) -> None:
        self._window = heading_window
        # Per-track entry heading (when first detected in the approach)
        self._entry_headings: dict[int, float] = {}
        # Per-track maneuver result
        self._maneuvers: dict[int, ManeuverType] = {}

    def classify(
        self,
        track_id: int,
        heading_history: list[float],
    ) -> ManeuverType:
        """Classify the vehicle's maneuver from heading history.

        Args:
            track_id: Track identifier.
            heading_history: List of heading values in degrees.

        Returns:
            ManeuverType classification.
        """
        if len(heading_history) < 3:
            return ManeuverType.UNKNOWN

        # Record entry heading
        if track_id not in self._entry_headings:
            self._entry_headings[track_id] = heading_history[0]

        entry = self._entry_headings[track_id]
        current = heading_history[-1]

        # Calculate heading change (normalized to [-180, 180])
        delta = self._normalize_angle(current - entry)

        maneuver = self._classify_from_delta(delta)
        self._maneuvers[track_id] = maneuver

        return maneuver

    def _classify_from_delta(self, delta_deg: float) -> ManeuverType:
        """Classify from heading change magnitude."""
        abs_delta = abs(delta_deg)

        if abs_delta < 30:
            return ManeuverType.STRAIGHT
        elif abs_delta > 150:
            return ManeuverType.U_TURN
        elif delta_deg < 0:
            return ManeuverType.LEFT
        else:
            return ManeuverType.RIGHT

    @staticmethod
    def _normalize_angle(angle: float) -> float:
        """Normalize angle to [-180, 180] range."""
        while angle > 180:
            angle -= 360
        while angle < -180:
            angle += 360
        return angle

    def get_maneuver(self, track_id: int) -> ManeuverType:
        """Get the current maneuver classification for a track."""
        return self._maneuvers.get(track_id, ManeuverType.UNKNOWN)

    def cleanup_track(self, track_id: int) -> None:
        """Remove state for a lost track."""
        self._entry_headings.pop(track_id, None)
        self._maneuvers.pop(track_id, None)


class MovementCounter:
    """Counts per-movement PCU for signal optimizer input (Section 39).

    Instead of just "NS = 22 PCU", provides:
      NS straight = 12 PCU
      NS left = 7 PCU
      NS right = 3 PCU
    """

    def __init__(self) -> None:
        pass

    def count_by_movement(
        self,
        vehicles: list[dict],
        pcu_weights: dict[str, float],
    ) -> dict[str, dict[str, float]]:
        """Count vehicles and PCU by lane and maneuver.

        Args:
            vehicles: List of vehicle dicts with 'lane_id', 'class_name', 'maneuver'.
            pcu_weights: Class → PCU weight mapping.

        Returns:
            Nested dict: lane_id → {movement → PCU count}.
        """
        from collections import defaultdict

        counts: dict[str, dict[str, float]] = defaultdict(
            lambda: defaultdict(float)
        )
        vehicle_counts: dict[str, dict[str, int]] = defaultdict(
            lambda: defaultdict(int)
        )

        for v in vehicles:
            lane = v.get("lane_id", "unknown")
            maneuver = v.get("maneuver", "unknown")
            cls = v.get("class_name", "car")
            conf = v.get("detection_confidence", 1.0)

            pcu = pcu_weights.get(cls, 1.0)
            counts[lane][maneuver] += pcu * conf
            vehicle_counts[lane][maneuver] += 1

        # Convert to regular dicts
        return {
            lane: dict(movements) for lane, movements in counts.items()
        }
