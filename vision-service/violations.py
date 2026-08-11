"""
violations.py — Lane-Discipline & BRTS-Intrusion Detection
============================================================
ERH26_PS_08: Data-Driven Traffic Optimization

Implements rule-based violation detection using ground-plane trajectories
and zone assignments. Two violation types:

1. **Lane-discipline violation**: Vehicle crosses into adjacent lane and
   STAYS there for N consecutive frames (not a single-frame boundary crossing,
   which is tracker noise or a legitimate lane change).

2. **BRTS-corridor intrusion**: Non-authorized vehicle enters the BRTS corridor,
   stays for >threshold seconds, AND is moving roughly parallel to the corridor
   axis (not just crossing perpendicular to turn).

All thresholds are configurable via config.yaml — no magic numbers in code.

Usage:
    from violations import ViolationDetector
    vd = ViolationDetector(config["violations"], zone_manager)
    violations = vd.check(tracked_vehicles, fps=10.0)
"""

import logging
import time
from dataclasses import dataclass, field
from typing import Optional

import numpy as np

from zones.zone_utils import ZoneManager

logger = logging.getLogger(__name__)


@dataclass
class LaneViolation:
    """A detected lane-discipline violation.

    Attributes:
        track_id: ID of the violating vehicle.
        vehicle_class: Class name (e.g., "car", "auto_rickshaw").
        from_lane: Original lane before the violation.
        to_lane: Lane the vehicle intruded into.
        dwell_frames: Number of consecutive frames in the wrong lane.
        dwell_time_s: Duration in seconds.
        timestamp: ISO-format timestamp when violation was first detected.
        confidence: Detection confidence of the vehicle.
    """
    track_id: int
    vehicle_class: str
    from_lane: str
    to_lane: str
    dwell_frames: int
    dwell_time_s: float
    timestamp: str
    confidence: float


@dataclass
class BRTSIntrusion:
    """A detected BRTS-corridor intrusion.

    Attributes:
        track_id: ID of the intruding vehicle.
        vehicle_class: Class name (should be non-authorized type).
        dwell_time_s: Duration inside the BRTS corridor.
        angle_to_corridor_deg: Angle between vehicle motion and corridor axis.
                               Low angle = parallel = genuine intrusion.
        entry_timestamp: ISO-format timestamp when vehicle entered corridor.
        confidence: Detection confidence.
    """
    track_id: int
    vehicle_class: str
    dwell_time_s: float
    angle_to_corridor_deg: float
    entry_timestamp: str
    confidence: float


class ViolationDetector:
    """Detects lane-discipline violations and BRTS-corridor intrusions.

    Maintains per-vehicle state tracking (which lane they've been in,
    how long in the BRTS corridor) and applies configurable thresholds
    to determine when to flag a violation.

    Args:
        config: Dict from config.yaml under 'violations' key.
        zone_manager: ZoneManager instance for the current junction.
    """

    def __init__(self, config: dict, zone_manager: ZoneManager) -> None:
        self._zone_manager = zone_manager

        # Lane-change violation thresholds
        lane_config = config.get("lane_change", {})
        self._min_dwell_frames: int = lane_config.get("min_dwell_frames", 10)

        # BRTS intrusion thresholds
        brts_config = config.get("brts_intrusion", {})
        self._brts_authorized: set[str] = set(
            brts_config.get("authorized_classes", ["bus", "brts_bus"])
        )
        self._brts_min_dwell_s: float = brts_config.get("min_dwell_time_s", 1.5)
        self._brts_max_angle: float = brts_config.get("max_angle_to_corridor_deg", 30.0)

        # Per-vehicle state tracking for lane violations
        # track_id → {"current_lane": str, "original_lane": str,
        #              "consecutive_frames_in_new_lane": int}
        self._lane_state: dict[int, dict] = {}

        # Per-vehicle state for BRTS intrusions
        # track_id → {"entry_time": float, "entry_timestamp": str}
        self._brts_state: dict[int, dict] = {}

        logger.info(
            f"ViolationDetector initialized — "
            f"lane dwell threshold: {self._min_dwell_frames} frames, "
            f"BRTS dwell threshold: {self._brts_min_dwell_s}s, "
            f"BRTS angle threshold: {self._brts_max_angle}°"
        )

    def check(
        self,
        tracked_vehicles: list,
        fps: float,
        current_timestamp: str = "",
    ) -> tuple[list[LaneViolation], list[BRTSIntrusion]]:
        """Check all tracked vehicles for violations.

        Should be called once per frame with the current set of active
        tracked vehicles.

        Args:
            tracked_vehicles: List of TrackedVehicle objects from tracker.py.
            fps: Current video FPS (for converting frames to seconds).
            current_timestamp: ISO-format timestamp for the current frame.

        Returns:
            Tuple of (lane_violations, brts_intrusions) detected this frame.
            A violation is only returned the FIRST time it crosses the threshold
            (not repeatedly every subsequent frame).
        """
        lane_violations: list[LaneViolation] = []
        brts_intrusions: list[BRTSIntrusion] = []

        active_ids: set[int] = set()

        for vehicle in tracked_vehicles:
            active_ids.add(vehicle.track_id)

            # --- Lane-discipline check ---
            if vehicle.lane_history:
                lv = self._check_lane_violation(vehicle, fps, current_timestamp)
                if lv is not None:
                    lane_violations.append(lv)

            # --- BRTS intrusion check ---
            if self._zone_manager.has_brts_corridor and vehicle.trajectory_world:
                bi = self._check_brts_intrusion(vehicle, fps, current_timestamp)
                if bi is not None:
                    brts_intrusions.append(bi)

        # Clean up state for vehicles that are no longer tracked
        self._cleanup_state(active_ids)

        return lane_violations, brts_intrusions

    def _check_lane_violation(
        self,
        vehicle,
        fps: float,
        timestamp: str,
    ) -> Optional[LaneViolation]:
        """Check if a vehicle has committed a lane-discipline violation.

        Logic: A violation is flagged only when a vehicle's lane assignment
        changes from its "established" lane AND it remains in the new lane
        for >= min_dwell_frames consecutive frames.

        A single-frame boundary crossing is NOT a violation — it's either
        tracker jitter or a legitimate lane change in progress.
        """
        tid = vehicle.track_id
        current_lane = vehicle.lane_history[-1] if vehicle.lane_history else None

        if current_lane is None:
            # Vehicle momentarily not in any lane (e.g., tracking jitter at boundary).
            # Do NOT reset the state. This prevents a track that flickers out of the polygon 
            # for 1 frame from completely resetting the consecutive frame counter.
            return None

        if tid not in self._lane_state:
            # First time seeing this vehicle — establish its lane
            self._lane_state[tid] = {
                "original_lane": current_lane,
                "current_lane": current_lane,
                "consecutive_frames_in_new_lane": 0,
                "violation_flagged": False,
            }
            return None

        state = self._lane_state[tid]

        if current_lane == state["original_lane"]:
            # Vehicle is back in its original lane — reset
            state["consecutive_frames_in_new_lane"] = 0
            state["current_lane"] = current_lane
            state["violation_flagged"] = False
            return None

        if current_lane != state["current_lane"]:
            # Lane changed again (to a third lane?) — update tracking
            state["current_lane"] = current_lane
            state["consecutive_frames_in_new_lane"] = 1
            state["violation_flagged"] = False
            return None

        # Vehicle is in a different lane from its original — count consecutive frames
        state["consecutive_frames_in_new_lane"] += 1

        if (
            state["consecutive_frames_in_new_lane"] >= self._min_dwell_frames
            and not state["violation_flagged"]
        ):
            # Threshold crossed — flag violation (only once)
            state["violation_flagged"] = True
            dwell_frames = state["consecutive_frames_in_new_lane"]
            dwell_time = dwell_frames / fps if fps > 0 else 0.0

            logger.info(
                f"LANE VIOLATION: track {tid} ({vehicle.class_name}) "
                f"moved from {state['original_lane']} to {current_lane} "
                f"for {dwell_frames} frames ({dwell_time:.1f}s)"
            )

            return LaneViolation(
                track_id=tid,
                vehicle_class=vehicle.class_name,
                from_lane=state["original_lane"],
                to_lane=current_lane,
                dwell_frames=dwell_frames,
                dwell_time_s=round(dwell_time, 2),
                timestamp=timestamp,
                confidence=vehicle.confidence,
            )

        return None

    def _check_brts_intrusion(
        self,
        vehicle,
        fps: float,
        timestamp: str,
    ) -> Optional[BRTSIntrusion]:
        """Check if a vehicle is intruding on the BRTS corridor.

        Three conditions must ALL hold for an intrusion to be flagged:
        1. Vehicle class is NOT in the authorized list (e.g., not a bus)
        2. Vehicle has been inside the BRTS polygon for > min dwell time
        3. Vehicle's motion vector is roughly parallel to the corridor axis
           (angle < max_angle_to_corridor_deg)

        The direction check (condition 3) prevents false positives from
        vehicles that cross the BRTS lane to make a turn — those move
        perpendicular to the corridor, not parallel.
        """
        tid = vehicle.track_id

        # Condition 1: Is this vehicle type authorized?
        if vehicle.class_name in self._brts_authorized:
            # Authorized vehicle — clear any intrusion state
            if tid in self._brts_state:
                del self._brts_state[tid]
            return None

        # Check current position
        in_brts = self._zone_manager.is_in_brts_corridor(vehicle.bottom_center)

        if not in_brts:
            # Vehicle left the BRTS corridor — clear state
            if tid in self._brts_state:
                del self._brts_state[tid]
            return None

        # Vehicle is inside BRTS corridor
        current_time = time.monotonic()

        if tid not in self._brts_state:
            # Just entered — start tracking dwell time
            self._brts_state[tid] = {
                "entry_time": current_time,
                "entry_timestamp": timestamp,
                "flagged": False,
            }
            return None

        state = self._brts_state[tid]
        dwell_s = current_time - state["entry_time"]

        # Condition 2: Has dwell time exceeded threshold?
        if dwell_s < self._brts_min_dwell_s:
            return None

        # Already flagged — don't re-flag
        if state["flagged"]:
            return None

        # Condition 3: Is the vehicle moving parallel to the corridor?
        motion_vec = self._zone_manager.get_motion_vector(vehicle.trajectory_world)
        if motion_vec is None:
            # Can't determine direction yet — wait for more data
            return None

        angle = self._zone_manager.compute_angle_to_brts_axis(motion_vec)
        if angle is None:
            return None

        if angle > self._brts_max_angle:
            # Vehicle is crossing perpendicular — likely making a turn, not intruding
            return None

        # All three conditions met — flag intrusion
        state["flagged"] = True

        logger.info(
            f"BRTS INTRUSION: track {tid} ({vehicle.class_name}) "
            f"in corridor for {dwell_s:.1f}s, angle {angle:.1f}°"
        )

        return BRTSIntrusion(
            track_id=tid,
            vehicle_class=vehicle.class_name,
            dwell_time_s=round(dwell_s, 2),
            angle_to_corridor_deg=round(angle, 1),
            entry_timestamp=state["entry_timestamp"],
            confidence=vehicle.confidence,
        )

    def _cleanup_state(self, active_ids: set[int]) -> None:
        """Remove state for vehicles that are no longer being tracked."""
        lost_lane = [tid for tid in self._lane_state if tid not in active_ids]
        for tid in lost_lane:
            del self._lane_state[tid]

        lost_brts = [tid for tid in self._brts_state if tid not in active_ids]
        for tid in lost_brts:
            del self._brts_state[tid]
