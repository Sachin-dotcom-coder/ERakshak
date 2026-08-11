"""
calibration/homography.py — Camera Calibration & Ground-Plane Projection
=========================================================================
ERH26_PS_08: Data-Driven Traffic Optimization

Converts pixel measurements to real-world meters using a homography transform.
This is the single biggest differentiator in our vision layer — almost every
competing team will report raw pixel counts as "queue length," which is meaningless
without knowing the camera's perspective geometry.

Key operations:
- Compute homography from known reference point pairs (pixel ↔ world)
- Project bounding box ground-contact points to real-world coordinates
- Compute calibrated queue length (meters from stop line)
- Compute calibrated vehicle speed (km/h from frame-to-frame displacement)

Usage:
    from calibration.homography import CameraCalibrator
    calibrator = CameraCalibrator(camera_config["junction_01"])
    world_x, world_y = calibrator.pixel_to_world(px, py)
    speed_kmph = calibrator.compute_speed(trajectory, fps)
"""

import logging
from typing import Optional

import cv2
import numpy as np

logger = logging.getLogger(__name__)


class CameraCalibrator:
    """Handles pixel-to-world coordinate conversion for a single camera.

    Uses a homography matrix computed from known reference point pairs
    (e.g., lane markings, stop lines, zebra crossings with known real-world
    dimensions) to map any pixel coordinate to real-world meters.

    Args:
        camera_config: Dict from camera_config.yaml for one camera/junction.
                       Must contain 'pixel_points' and 'world_points' (4+ pairs each).
    """

    def __init__(self, camera_config: dict) -> None:
        self._config = camera_config
        self._homography: Optional[np.ndarray] = None  # 3×3 matrix, pixel → world
        self._inverse_homography: Optional[np.ndarray] = None  # 3×3, world → pixel
        self._is_calibrated: bool = False

        self._stop_line_world: Optional[np.ndarray] = None
        self._fps: Optional[float] = camera_config.get("fps")

        self._compute_homography()

    def _compute_homography(self) -> None:
        """Compute homography from the configured reference point pairs.

        Requires at least 4 non-collinear point pairs. If reference points
        are not yet provided (FILL IN), the calibrator operates in uncalibrated
        mode — all world-coordinate functions return None and log warnings.
        """
        pixel_points = self._config.get("pixel_points", [])
        world_points = self._config.get("world_points", [])

        if not pixel_points or not world_points:
            logger.warning(
                "Camera calibration points not provided — operating in UNCALIBRATED mode. "
                "Queue lengths and speeds will be unavailable until you fill in "
                "calibration/camera_config.yaml with reference points."
            )
            return

        if len(pixel_points) != len(world_points):
            logger.error(
                f"Mismatch: {len(pixel_points)} pixel points vs {len(world_points)} world points. "
                f"They must be 1-to-1. Calibration FAILED."
            )
            return

        if len(pixel_points) < 4:
            logger.error(
                f"Need at least 4 reference point pairs, got {len(pixel_points)}. "
                f"Calibration FAILED."
            )
            return

        src = np.array(pixel_points, dtype=np.float64)
        dst = np.array(world_points, dtype=np.float64)

        # cv2.findHomography uses RANSAC to handle slight measurement errors
        self._homography, mask = cv2.findHomography(src, dst, cv2.RANSAC, 5.0)

        if self._homography is None:
            logger.error("cv2.findHomography returned None — check that points are not collinear")
            return

        # Compute inverse for world → pixel (useful for drawing zone overlays)
        self._inverse_homography = np.linalg.inv(self._homography)
        self._is_calibrated = True

        # Parse stop line position
        stop_line = self._config.get("stop_line_world")
        if stop_line is not None:
            self._stop_line_world = np.array(stop_line, dtype=np.float64)

        inlier_count = int(mask.sum()) if mask is not None else len(pixel_points)
        logger.info(
            f"Camera calibrated successfully — {inlier_count}/{len(pixel_points)} "
            f"reference points used as inliers"
        )

    def pixel_to_world(self, px: float, py: float) -> Optional[tuple[float, float]]:
        """Convert a pixel coordinate to real-world meters.

        Args:
            px: X coordinate in pixels.
            py: Y coordinate in pixels.

        Returns:
            (world_x, world_y) in meters, or None if not calibrated.
        """
        if not self._is_calibrated:
            return None

        # Homogeneous coordinates: [px, py, 1]
        point = np.array([px, py, 1.0], dtype=np.float64)
        world_h = self._homography @ point
        # Normalize by homogeneous coordinate
        world_x = world_h[0] / world_h[2]
        world_y = world_h[1] / world_h[2]
        return (float(world_x), float(world_y))

    def world_to_pixel(self, wx: float, wy: float) -> Optional[tuple[float, float]]:
        """Convert a real-world coordinate (meters) back to pixel coordinates.

        Useful for drawing calibrated zone overlays on the video frame.

        Args:
            wx: X coordinate in meters.
            wy: Y coordinate in meters.

        Returns:
            (px, py) in pixels, or None if not calibrated.
        """
        if not self._is_calibrated or self._inverse_homography is None:
            return None

        point = np.array([wx, wy, 1.0], dtype=np.float64)
        pixel_h = self._inverse_homography @ point
        px = pixel_h[0] / pixel_h[2]
        py = pixel_h[1] / pixel_h[2]
        return (float(px), float(py))

    def project_ground_contact(
        self, bbox: np.ndarray
    ) -> Optional[tuple[float, float]]:
        """Project a bounding box's ground-contact point to real-world coordinates.

        Uses the BOTTOM-CENTER of the bounding box — not the centroid.
        This is critical: the centroid of a tall vehicle (bus, truck) is far above
        the road surface, and projecting it through the homography gives a point
        that's behind the vehicle's actual ground position. Bottom-center
        approximates where the wheels touch the road.

        Args:
            bbox: Bounding box as [x1, y1, x2, y2] in pixel coordinates.

        Returns:
            (world_x, world_y) in meters, or None if not calibrated.
        """
        x_center = (bbox[0] + bbox[2]) / 2.0
        y_bottom = bbox[3]  # Bottom edge
        return self.pixel_to_world(float(x_center), float(y_bottom))

    def compute_queue_length(
        self,
        vehicle_world_positions: list[tuple[float, float]],
    ) -> Optional[float]:
        """Compute queue length in meters: distance from the furthest queued vehicle
        to the stop line.

        Args:
            vehicle_world_positions: List of (world_x, world_y) positions for
                                     vehicles detected in a lane.

        Returns:
            Queue length in meters, or None if not calibrated or no stop line defined.
        """
        if not self._is_calibrated or self._stop_line_world is None:
            return None

        if not vehicle_world_positions:
            return 0.0

        # Distance of each vehicle from the stop line
        stop = self._stop_line_world
        max_dist = 0.0
        for wx, wy in vehicle_world_positions:
            dist = np.sqrt((wx - stop[0]) ** 2 + (wy - stop[1]) ** 2)
            max_dist = max(max_dist, dist)

        return float(max_dist)

    def compute_speed(
        self,
        trajectory_world: list[tuple[float, float]],
        fps: Optional[float] = None,
        smoothing_window: int = 5,
    ) -> Optional[float]:
        """Compute vehicle speed in km/h from ground-plane trajectory.

        Uses frame-to-frame displacement of the projected ground-contact point,
        averaged over a sliding window for noise reduction.

        Args:
            trajectory_world: List of (world_x, world_y) positions over consecutive frames.
                              Most recent position is last.
            fps: Frames per second (overrides camera config fps if provided).
            smoothing_window: Number of recent frames to average over.

        Returns:
            Speed in km/h, or None if insufficient data or not calibrated.
        """
        effective_fps = fps or self._fps
        if effective_fps is None or effective_fps <= 0:
            logger.debug("FPS not set — cannot compute speed. Fill in config.yaml fps values.")
            return None

        if not self._is_calibrated:
            return None

        if len(trajectory_world) < 3:
            return None

        # Use the most recent `smoothing_window` positions
        recent = trajectory_world[-smoothing_window:]
        if len(recent) < 3:
            return None

        # Measure straight-line distance from start to end of window to cancel out
        # high-frequency tracking jitter. Summing point-to-point distances would
        # accumulate noise and falsely report high speeds for stationary objects.
        dx = recent[-1][0] - recent[0][0]
        dy = recent[-1][1] - recent[0][1]
        total_dist_m = float(np.sqrt(dx * dx + dy * dy))

        # Time elapsed = (number of frame gaps) / fps
        dt_seconds = (len(recent) - 1) / effective_fps
        if dt_seconds <= 0:
            return None

        speed_mps = total_dist_m / dt_seconds  # meters per second
        speed_kmph = speed_mps * 3.6           # convert to km/h

        # Clamp speed to realistic urban junction range (max 120 km/h) to prevent
        # horizon-line perspective distortion spikes
        speed_kmph = min(speed_kmph, 120.0)

        return float(speed_kmph)

    def compute_density(
        self,
        vehicle_count: int,
        lane_length_m: float,
    ) -> Optional[float]:
        """Compute vehicle density in vehicles per kilometer.

        Args:
            vehicle_count: Number of vehicles in the lane segment.
            lane_length_m: Length of the lane segment in meters.

        Returns:
            Density in vehicles/km, or None if lane_length is zero.
        """
        if lane_length_m <= 0:
            return None
        return float(vehicle_count / lane_length_m * 1000.0)

    @property
    def is_calibrated(self) -> bool:
        """Whether the homography has been successfully computed."""
        return self._is_calibrated

    @property
    def homography_matrix(self) -> Optional[np.ndarray]:
        """The 3×3 homography matrix (pixel → world). None if not calibrated."""
        return self._homography

    @property
    def fps(self) -> Optional[float]:
        """Configured FPS for this camera."""
        return self._fps

    @fps.setter
    def fps(self, value: float) -> None:
        """Update FPS (e.g., after reading it from ffprobe or cv2.VideoCapture)."""
        self._fps = value
