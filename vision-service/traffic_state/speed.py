"""
traffic_state/speed.py — Adaptive Speed Estimation (Sections 47-48)
====================================================================
Adaptive-window speed estimation with outlier rejection and confidence scoring.

- Fast vehicles → shorter measurement window (less smoothing lag)
- Stationary vehicles → longer window (reduces jitter)
- Acceleration-limited outlier rejection
- Speed confidence scoring based on trajectory quality
"""

import logging
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)


class SpeedEstimator:
    """Adaptive-window speed estimation with outlier rejection.

    Args:
        config: Dict from thresholds.yaml under 'speed'.
        fps: Camera frame rate.
    """

    def __init__(self, config: dict, fps: float = 10.0) -> None:
        self._fps = fps
        self._fast_window: int = config.get("fast_window_frames", 3)
        self._slow_window: int = config.get("slow_window_frames", 10)
        self._speed_boundary: float = config.get("speed_boundary_kmph", 15.0)
        self._ema_alpha: float = config.get("ema_alpha", 0.30)
        self._max_accel: float = config.get("max_acceleration_mps2", 8.0)

        # Per-track state
        self._smoothed_speeds: dict[int, float] = {}
        self._speed_confidences: dict[int, float] = {}
        self._outlier_counts: dict[int, int] = {}

    def estimate_speed(
        self,
        track_id: int,
        world_trajectory: list[tuple[float, float]],
    ) -> tuple[float, float, float]:
        """Estimate speed with adaptive windowing and outlier rejection.

        Args:
            track_id: Track identifier.
            world_trajectory: List of (x_m, y_m) world positions, oldest first.

        Returns:
            (speed_kmph, acceleration_mps2, confidence) tuple.
        """
        if len(world_trajectory) < 2:
            return (0.0, 0.0, 0.5)

        # Adaptive window based on previous speed
        prev_speed = self._smoothed_speeds.get(track_id, 0.0)
        if prev_speed > self._speed_boundary:
            window = self._fast_window
        else:
            window = self._slow_window

        window = min(window, len(world_trajectory) - 1)
        if window < 1:
            return (0.0, 0.0, 0.5)

        # Compute displacement
        p_new = np.array(world_trajectory[-1])
        p_old = np.array(world_trajectory[-1 - window])
        delta_d = float(np.linalg.norm(p_new - p_old))
        delta_t = window / self._fps

        if delta_t <= 0:
            return (0.0, 0.0, 0.5)

        speed_mps = delta_d / delta_t
        speed_kmph = speed_mps * 3.6

        # Outlier rejection (Section 48)
        acceleration_mps2 = 0.0
        is_outlier = False
        if prev_speed > 0:
            prev_mps = prev_speed / 3.6
            speed_change = abs(speed_mps - prev_mps)
            acceleration_mps2 = speed_change / delta_t

            if acceleration_mps2 > self._max_accel:
                is_outlier = True
                self._outlier_counts[track_id] = (
                    self._outlier_counts.get(track_id, 0) + 1
                )
                logger.debug(
                    f"Track {track_id}: speed outlier "
                    f"({prev_speed:.1f}→{speed_kmph:.1f} km/h, "
                    f"accel={acceleration_mps2:.1f} m/s²)"
                )
                # Keep previous speed, don't update
                speed_kmph = prev_speed
                acceleration_mps2 = 0.0
        else:
            # First speed estimate — compute signed acceleration
            acceleration_mps2 = 0.0

        # EMA smoothing
        if not is_outlier:
            if track_id in self._smoothed_speeds:
                smoothed = (
                    self._ema_alpha * speed_kmph
                    + (1 - self._ema_alpha) * self._smoothed_speeds[track_id]
                )
            else:
                smoothed = speed_kmph
            self._smoothed_speeds[track_id] = smoothed
            self._outlier_counts[track_id] = 0
        else:
            smoothed = self._smoothed_speeds.get(track_id, speed_kmph)

        # Speed confidence
        confidence = self._compute_confidence(track_id, world_trajectory, is_outlier)
        self._speed_confidences[track_id] = confidence

        return (smoothed, acceleration_mps2, confidence)

    def _compute_confidence(
        self,
        track_id: int,
        trajectory: list[tuple[float, float]],
        is_outlier: bool,
    ) -> float:
        """Compute speed confidence based on trajectory quality.

        Factors:
        - Trajectory length (longer = more confident)
        - Recent outlier count (more outliers = less confident)
        - Trajectory smoothness (jittery = less confident)
        """
        # Trajectory length factor
        length_factor = min(1.0, len(trajectory) / 20.0)

        # Outlier factor
        outlier_count = self._outlier_counts.get(track_id, 0)
        outlier_factor = max(0.0, 1.0 - outlier_count * 0.2)

        # Trajectory smoothness (variance of inter-point distances)
        smoothness = 1.0
        if len(trajectory) >= 4:
            recent = trajectory[-10:]
            dists = []
            for i in range(1, len(recent)):
                d = np.linalg.norm(
                    np.array(recent[i]) - np.array(recent[i - 1])
                )
                dists.append(d)
            if len(dists) >= 2:
                mean_d = np.mean(dists)
                std_d = np.std(dists)
                cv = std_d / mean_d if mean_d > 0 else 0
                smoothness = max(0.0, 1.0 - cv)

        confidence = 0.3 * length_factor + 0.3 * outlier_factor + 0.4 * smoothness

        if is_outlier:
            confidence *= 0.5

        return float(np.clip(confidence, 0.0, 1.0))

    def get_speed_confidence(self, track_id: int) -> float:
        """Get the speed confidence for a track."""
        return self._speed_confidences.get(track_id, 0.5)

    def cleanup_track(self, track_id: int) -> None:
        """Remove state for a lost track."""
        self._smoothed_speeds.pop(track_id, None)
        self._speed_confidences.pop(track_id, None)
        self._outlier_counts.pop(track_id, None)

    def set_fps(self, fps: float) -> None:
        """Update camera FPS."""
        self._fps = fps
