"""
incidents/wrong_way.py — Persistent Wrong-Way Detection (Section 61)
=====================================================================
Detects vehicles traveling in the wrong direction by comparing vehicle
heading to expected lane direction using cosine similarity.

Requires 1-second persistence + trajectory consistency before confirmation
to avoid false alerts from turning vehicles.
"""

import logging
import time
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)


class WrongWayDetector:
    """Persistent wrong-way driving detection.

    Uses cosine similarity between vehicle heading vector and expected
    lane direction vector. Requires sustained wrong-way motion before
    triggering an alert.

    Args:
        config: Dict from thresholds.yaml under 'wrong_way'.
    """

    def __init__(self, config: dict) -> None:
        self._cosine_threshold: float = config.get("cosine_threshold", -0.3)
        self._persistence_sec: float = config.get("persistence_sec", 1.0)
        self._min_trajectory: int = config.get("min_trajectory_points", 5)

        # Per-track state
        self._candidate_start: dict[int, float] = {}  # track_id → time
        self._wrong_way_confirmed: dict[int, bool] = {}

    def check(
        self,
        track_id: int,
        heading_deg: float,
        expected_heading_deg: float,
        trajectory: Optional[list[tuple[float, float]]] = None,
        speed_kmph: float = 0.0,
    ) -> Optional[dict]:
        """Check if a vehicle is traveling the wrong way.

        Args:
            track_id: Track identifier.
            heading_deg: Vehicle heading (0=North, CW).
            expected_heading_deg: Expected lane heading (0=North, CW).
            trajectory: Recent world positions for trajectory consistency.
            speed_kmph: Vehicle speed (stationary vehicles can't be wrong-way).

        Returns:
            Alert dict if wrong-way confirmed, None otherwise.
        """
        now = time.time()

        # Stationary vehicles are not wrong-way candidates
        if speed_kmph < 2.0:
            self._candidate_start.pop(track_id, None)
            return None

        # Need minimum trajectory for reliable heading
        if trajectory and len(trajectory) < self._min_trajectory:
            return None

        # Compute cosine similarity between headings
        cos_sim = self._heading_cosine_similarity(heading_deg, expected_heading_deg)

        # Check trajectory consistency if available
        trajectory_consistent = True
        if trajectory and len(trajectory) >= 3:
            trajectory_heading = self._compute_trajectory_heading(trajectory)
            traj_cos = self._heading_cosine_similarity(
                trajectory_heading, expected_heading_deg
            )
            trajectory_consistent = traj_cos < self._cosine_threshold

        is_wrong_way = cos_sim < self._cosine_threshold and trajectory_consistent

        if is_wrong_way:
            if track_id not in self._candidate_start:
                self._candidate_start[track_id] = now
                logger.debug(
                    f"Track {track_id}: wrong-way candidate "
                    f"(cos={cos_sim:.2f}, heading={heading_deg:.0f}°, "
                    f"expected={expected_heading_deg:.0f}°)"
                )

            elapsed = now - self._candidate_start[track_id]
            if elapsed >= self._persistence_sec:
                if not self._wrong_way_confirmed.get(track_id, False):
                    self._wrong_way_confirmed[track_id] = True
                    logger.warning(
                        f"⚠️ WRONG-WAY CONFIRMED: track={track_id}, "
                        f"cos={cos_sim:.2f}, heading={heading_deg:.0f}°, "
                        f"expected={expected_heading_deg:.0f}°, "
                        f"duration={elapsed:.1f}s"
                    )

                return {
                    "track_id": track_id,
                    "violation_type": "WRONG_WAY",
                    "heading_deg": round(heading_deg, 1),
                    "expected_heading_deg": round(expected_heading_deg, 1),
                    "cosine_similarity": round(cos_sim, 3),
                    "duration_sec": round(elapsed, 1),
                    "speed_kmph": round(speed_kmph, 1),
                    "timestamp": now,
                }
        else:
            # Reset candidate if no longer wrong-way
            self._candidate_start.pop(track_id, None)
            self._wrong_way_confirmed.pop(track_id, None)

        return None

    def _heading_cosine_similarity(
        self,
        heading_a: float,
        heading_b: float,
    ) -> float:
        """Compute cosine similarity between two headings.

        Args:
            heading_a: Heading in degrees (0=North, CW).
            heading_b: Heading in degrees (0=North, CW).

        Returns:
            Cosine similarity in [-1.0, 1.0].
            1.0 = same direction, -1.0 = opposite.
        """
        rad_a = np.radians(heading_a)
        rad_b = np.radians(heading_b)

        vec_a = np.array([np.sin(rad_a), -np.cos(rad_a)])
        vec_b = np.array([np.sin(rad_b), -np.cos(rad_b)])

        return float(np.dot(vec_a, vec_b))

    def _compute_trajectory_heading(
        self,
        trajectory: list[tuple[float, float]],
    ) -> float:
        """Compute heading from trajectory displacement."""
        if len(trajectory) < 2:
            return 0.0

        p_old = np.array(trajectory[-min(5, len(trajectory))])
        p_new = np.array(trajectory[-1])

        dx = p_new[0] - p_old[0]
        dy = p_new[1] - p_old[1]

        if abs(dx) < 1e-6 and abs(dy) < 1e-6:
            return 0.0

        heading_rad = np.arctan2(dx, -dy)
        return float(np.degrees(heading_rad) % 360)

    def cleanup_track(self, track_id: int) -> None:
        """Remove state for a lost track."""
        self._candidate_start.pop(track_id, None)
        self._wrong_way_confirmed.pop(track_id, None)
