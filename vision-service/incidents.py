"""
incidents.py — Stall / Breakdown / Obstruction Detection
=========================================================
ERH26_PS_08: Data-Driven Traffic Optimization

Detects when a tracked vehicle's calibrated speed stays near-zero for an
extended window, indicating a probable breakdown, stall, or obstruction.

The detector distinguishes between vehicles stopped at a red light (normal)
and vehicles stopped mid-lane (abnormal) by excluding vehicles near known
stop-line areas. When signal-phase data from Person B's signal-optimizer
is available, confidence is higher; without it, we still flag with
"medium" confidence — designed to degrade gracefully.

Usage:
    from incidents import IncidentDetector
    detector = IncidentDetector(config["incidents"])
    stall_alerts = detector.check(tracked_vehicles, fps=10.0)
"""

import logging
import time
from dataclasses import dataclass
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class StallAlert:
    """A detected stall / breakdown / obstruction.

    Attributes:
        track_id: ID of the stalled vehicle.
        vehicle_class: Class name (e.g., "truck", "auto_rickshaw").
        lane_id: Lane where the stall occurred (if known).
        location_m: (world_x, world_y) position of the stall in meters.
        stall_duration_s: How long the vehicle has been stationary.
        confidence: "high" if we know it's not a red-light stop,
                    "medium" if we lack signal-phase context.
        timestamp: ISO-format timestamp when stall was first detected.
    """
    track_id: int
    vehicle_class: str
    lane_id: Optional[str]
    location_m: tuple[float, float]
    stall_duration_s: float
    confidence: str  # "high" or "medium"
    timestamp: str


class IncidentDetector:
    """Detects stalled/broken-down vehicles from near-zero calibrated speed.

    Monitors each tracked vehicle's speed over time. If a vehicle stays
    below the speed threshold for longer than the duration threshold,
    and is NOT near a known stop-line area, it's flagged as a stall.

    Args:
        config: Dict from config.yaml under 'incidents.stall' key.
    """

    def __init__(self, config: dict) -> None:
        stall_config = config.get("stall", {})

        self._speed_threshold: float = stall_config.get("speed_threshold_kmph", 2.0)
        self._min_duration: float = stall_config.get("min_duration_s", 15.0)
        self._stop_line_radius: float = stall_config.get("stop_line_exclusion_radius_m", 5.0)

        # Per-vehicle stall tracking state
        # track_id → {"stall_start": float, "stall_start_timestamp": str,
        #              "flagged": bool}
        self._stall_state: dict[int, dict] = {}

        # Known stop-line positions (populated from camera_config.yaml)
        # List of (world_x, world_y) positions where vehicles normally stop at red
        self._stop_line_positions: list[tuple[float, float]] = []

        # Signal phase data (from Person B's optimizer, if available)
        self._signal_phase_available: bool = False

        logger.info(
            f"IncidentDetector initialized — "
            f"speed threshold: {self._speed_threshold} km/h, "
            f"duration threshold: {self._min_duration}s, "
            f"stop-line exclusion radius: {self._stop_line_radius}m"
        )

    def set_stop_line_positions(
        self, positions: list[tuple[float, float]]
    ) -> None:
        """Register known stop-line positions for red-light exclusion.

        These are positions where vehicles normally stop at red signals.
        Vehicles stopped near these points are NOT flagged as stalls.

        Args:
            positions: List of (world_x, world_y) stop-line center positions.
        """
        self._stop_line_positions = positions
        logger.info(f"Registered {len(positions)} stop-line exclusion zones")

    def set_signal_phase(self, phase: Optional[str]) -> None:
        """Update current signal phase (from Person B's signal-optimizer).

        If we know the signal is green and a vehicle is still stopped,
        we can flag with higher confidence. If signal data is unavailable,
        we flag with "medium" confidence.

        Args:
            phase: Current signal phase string (e.g., "green", "red", "yellow"),
                   or None if signal data is not available.
        """
        self._signal_phase_available = phase is not None

    def check(
        self,
        tracked_vehicles: list,
        fps: float,
        current_timestamp: str = "",
    ) -> list[StallAlert]:
        """Check all tracked vehicles for stall/breakdown conditions.

        Args:
            tracked_vehicles: List of TrackedVehicle objects from tracker.py.
            fps: Video FPS (for context, though we use wall-clock time for duration).
            current_timestamp: ISO-format timestamp for the current frame.

        Returns:
            List of StallAlert objects. Each alert is emitted only ONCE
            when the threshold is first crossed (not repeatedly every frame).
        """
        stall_alerts: list[StallAlert] = []
        active_ids: set[int] = set()
        current_time = time.monotonic()

        for vehicle in tracked_vehicles:
            tid = vehicle.track_id
            active_ids.add(tid)

            # Need world-plane position and speed
            latest_pos = vehicle.latest_world_position
            if latest_pos is None:
                continue

            # Check if vehicle is near a stop line (normal stop)
            if self._is_near_stop_line(latest_pos):
                # Near a stop line — could be a normal red-light stop
                if tid in self._stall_state:
                    del self._stall_state[tid]
                continue

            # Compute current speed from trajectory
            speed = self._estimate_speed_from_trajectory(
                vehicle.trajectory_world, fps
            )

            if speed is not None and speed < self._speed_threshold:
                # Vehicle is near-stationary
                if tid not in self._stall_state:
                    self._stall_state[tid] = {
                        "stall_start": current_time,
                        "stall_start_timestamp": current_timestamp,
                        "flagged": False,
                    }

                state = self._stall_state[tid]
                duration = current_time - state["stall_start"]

                if duration >= self._min_duration and not state["flagged"]:
                    state["flagged"] = True

                    # Determine confidence based on signal phase availability
                    confidence = "high" if self._signal_phase_available else "medium"

                    # Try to get lane ID from vehicle's lane history
                    lane_id = None
                    if hasattr(vehicle, "lane_history") and vehicle.lane_history:
                        lane_id = vehicle.lane_history[-1]

                    logger.warning(
                        f"STALL ALERT: track {tid} ({vehicle.class_name}) "
                        f"stationary for {duration:.1f}s at {latest_pos} "
                        f"(confidence: {confidence})"
                    )

                    stall_alerts.append(StallAlert(
                        track_id=tid,
                        vehicle_class=vehicle.class_name,
                        lane_id=lane_id,
                        location_m=latest_pos,
                        stall_duration_s=round(duration, 1),
                        confidence=confidence,
                        timestamp=state["stall_start_timestamp"],
                    ))
            else:
                # Vehicle is moving — clear stall state
                if tid in self._stall_state:
                    del self._stall_state[tid]

        # Cleanup state for lost tracks
        lost = [tid for tid in self._stall_state if tid not in active_ids]
        for tid in lost:
            del self._stall_state[tid]

        return stall_alerts

    def _is_near_stop_line(self, position: tuple[float, float]) -> bool:
        """Check if a position is within the exclusion radius of any stop line.

        Args:
            position: (world_x, world_y) in meters.

        Returns:
            True if within exclusion radius of any stop line.
        """
        for sx, sy in self._stop_line_positions:
            dist = np.sqrt((position[0] - sx) ** 2 + (position[1] - sy) ** 2)
            if dist < self._stop_line_radius:
                return True
        return False

    def _estimate_speed_from_trajectory(
        self,
        trajectory_world: list[tuple[float, float]],
        fps: float,
        window: int = 5,
    ) -> Optional[float]:
        """Quick speed estimate from recent trajectory points.

        This is a simplified version of CameraCalibrator.compute_speed() —
        used here to avoid a circular dependency. The authoritative speed
        computation is in the calibrator; this is just for stall detection.

        Args:
            trajectory_world: World-coordinate trajectory, most recent last.
            fps: Frames per second.
            window: Number of recent points to consider.

        Returns:
            Speed in km/h, or None if insufficient data.
        """
        if fps <= 0 or len(trajectory_world) < 2:
            return None

        recent = trajectory_world[-window:]
        if len(recent) < 2:
            return None

        # Measure straight-line distance from start to end of window to cancel out
        # high-frequency tracking jitter. Summing point-to-point distances would
        # accumulate noise and falsely report high speeds for stationary objects.
        dx = recent[-1][0] - recent[0][0]
        dy = recent[-1][1] - recent[0][1]
        total_dist = float(np.sqrt(dx * dx + dy * dy))

        dt = (len(recent) - 1) / fps
        if dt <= 0:
            return None

        return float(total_dist / dt * 3.6)  # m/s → km/h
