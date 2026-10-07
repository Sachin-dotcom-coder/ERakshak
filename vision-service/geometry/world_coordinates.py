"""
geometry/world_coordinates.py — Unified World Coordinate Pipeline (Section 24-25)
===================================================================================
Transforms pixel-space detections into world-space VehicleState objects.

Pipeline:
  Detection bbox → Ground contact point → Homography projection →
  World (x, y) in meters → Speed / Heading / Acceleration computation

Integrates with:
- calibration/homography.py for pixel→world projection
- models/segmentation_refiner.py for selective ground contact improvement
- tracking/track_state.py for VehicleState enrichment
"""

import logging
import math
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)


class WorldCoordinateTransformer:
    """Transforms pixel-space detections into world-space coordinates.

    Provides the core geometric pipeline:
    1. Extract ground contact point from bbox
    2. Optionally refine with segmentation for difficult vehicles
    3. Project to world coordinates via homography
    4. Compute velocity, heading, and acceleration from trajectory

    Args:
        homography_matrix: 3x3 homography matrix (pixel→world).
        fps: Camera frame rate for speed computation.
        speed_config: Dict from thresholds.yaml under 'speed'.
    """

    def __init__(
        self,
        homography_matrix: Optional[np.ndarray],
        fps: float = 10.0,
        speed_config: Optional[dict] = None,
    ) -> None:
        self._H = homography_matrix
        self._fps = fps
        self._has_homography = homography_matrix is not None

        cfg = speed_config or {}
        self._fast_window: int = cfg.get("fast_window_frames", 3)
        self._slow_window: int = cfg.get("slow_window_frames", 10)
        self._speed_boundary: float = cfg.get("speed_boundary_kmph", 15.0)
        self._ema_alpha: float = cfg.get("ema_alpha", 0.30)
        self._max_accel: float = cfg.get("max_acceleration_mps2", 8.0)

        # Per-track smoothed speed state
        self._smoothed_speeds: dict[int, float] = {}

        if not self._has_homography:
            logger.warning(
                "No homography matrix provided — world coordinates will be "
                "pixel-based estimates. Calibrate the camera for accurate metrics."
            )

    def set_homography(self, H: np.ndarray) -> None:
        """Update the homography matrix (e.g., after recalibration)."""
        self._H = H.copy()
        self._has_homography = True

    def set_fps(self, fps: float) -> None:
        """Update FPS (e.g., when video source changes)."""
        self._fps = fps

    @staticmethod
    def extract_ground_contact(bbox: np.ndarray) -> tuple[float, float]:
        """Extract the ground contact point from a bounding box.

        Uses bottom-center as the default ground contact point.
        This avoids perspective parallax on tall vehicles.

        Args:
            bbox: [x1, y1, x2, y2] in pixel coordinates.

        Returns:
            (x, y) ground contact point in pixel coordinates.
        """
        x_center = (bbox[0] + bbox[2]) / 2.0
        y_bottom = bbox[3]
        return (float(x_center), float(y_bottom))

    def pixel_to_world(
        self,
        pixel_point: tuple[float, float],
    ) -> tuple[float, float]:
        """Project a pixel point to world coordinates using homography.

        H * [x_px, y_px, 1]^T = [s*X_m, s*Y_m, s]^T
        X_m = s*X_m / s, Y_m = s*Y_m / s

        Args:
            pixel_point: (x, y) in pixel coordinates.

        Returns:
            (x_m, y_m) in world coordinates (meters).
            Returns pixel point if homography is unavailable.
        """
        if not self._has_homography:
            return pixel_point

        px = np.array([pixel_point[0], pixel_point[1], 1.0], dtype=np.float64)
        world_homogeneous = self._H @ px
        s = world_homogeneous[2]

        if abs(s) < 1e-10:
            logger.warning("Homography projection: near-zero scale factor")
            return pixel_point

        x_m = world_homogeneous[0] / s
        y_m = world_homogeneous[1] / s
        return (float(x_m), float(y_m))

    def compute_speed(
        self,
        track_id: int,
        world_trajectory: list[tuple[float, float]],
    ) -> tuple[float, float, bool]:
        """Compute speed with adaptive windowing and outlier rejection.

        Uses shorter window for fast vehicles and longer for stationary ones.
        Applies EMA smoothing and acceleration-limit outlier rejection.

        Args:
            track_id: Track identifier for state persistence.
            world_trajectory: List of (x_m, y_m) world positions (oldest first).

        Returns:
            (speed_kmph, is_reliable) — smoothed speed and reliability flag.
            is_reliable is False when speed change exceeds max_acceleration.
        """
        if len(world_trajectory) < 2:
            return (0.0, 0.0, True)

        # Determine adaptive window size based on previous speed
        prev_speed = self._smoothed_speeds.get(track_id, 0.0)
        if prev_speed > self._speed_boundary:
            window = self._fast_window
        else:
            window = self._slow_window

        # Ensure enough trajectory points
        window = min(window, len(world_trajectory) - 1)
        if window < 1:
            return (0.0, 0.0, True)

        # Displacement over window
        p_new = np.array(world_trajectory[-1])
        p_old = np.array(world_trajectory[-1 - window])

        delta_d = float(np.linalg.norm(p_new - p_old))
        delta_t = window / self._fps

        if delta_t <= 0:
            return (0.0, 0.0, True)

        speed_mps = delta_d / delta_t
        speed_kmph = speed_mps * 3.6

        # Outlier rejection: check acceleration limit
        is_reliable = True
        if prev_speed > 0:
            speed_change_mps = abs(speed_mps - prev_speed / 3.6)
            acceleration = speed_change_mps / delta_t
            if acceleration > self._max_accel:
                is_reliable = False
                logger.debug(
                    f"Track {track_id}: speed outlier rejected "
                    f"({prev_speed:.1f} → {speed_kmph:.1f} km/h, "
                    f"accel={acceleration:.1f} m/s²)"
                )
                # Don't update smoothed speed with outlier
                return (prev_speed, acceleration, False)

        # EMA smoothing
        if track_id in self._smoothed_speeds:
            smoothed = (
                self._ema_alpha * speed_kmph
                + (1 - self._ema_alpha) * self._smoothed_speeds[track_id]
            )
        else:
            smoothed = speed_kmph

        self._smoothed_speeds[track_id] = smoothed

        # Compute acceleration
        accel_mps2 = 0.0
        if prev_speed > 0:
            accel_mps2 = (speed_mps - prev_speed / 3.6) / delta_t

        return (smoothed, accel_mps2, is_reliable)

    def compute_heading(
        self,
        world_trajectory: list[tuple[float, float]],
        window: int = 5,
    ) -> float:
        """Compute vehicle heading from recent world trajectory.

        Heading is measured in degrees: 0=North, clockwise.

        Args:
            world_trajectory: List of (x_m, y_m) world positions.
            window: Number of recent positions to use.

        Returns:
            Heading in degrees [0, 360).
        """
        if len(world_trajectory) < 2:
            return 0.0

        # Use recent window
        n = min(window, len(world_trajectory) - 1)
        p_old = np.array(world_trajectory[-1 - n])
        p_new = np.array(world_trajectory[-1])

        dx = p_new[0] - p_old[0]
        dy = p_new[1] - p_old[1]

        if abs(dx) < 1e-6 and abs(dy) < 1e-6:
            return 0.0

        # atan2(dx, -dy) gives angle from North, clockwise
        heading_rad = math.atan2(dx, -dy)
        heading_deg = math.degrees(heading_rad) % 360

        return heading_deg

    def cleanup_track(self, track_id: int) -> None:
        """Remove state for a lost track."""
        self._smoothed_speeds.pop(track_id, None)

    @property
    def has_homography(self) -> bool:
        """Whether a valid homography matrix is loaded."""
        return self._has_homography
