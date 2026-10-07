"""
incidents/breakdown.py — Breakdown Detection State Machine (Sections 62-63)
=============================================================================
Classifies stationary vehicles into contextual categories instead of
using a single hard-coded 45-second rule.

State Machine:
  MOVING → SLOWING → STOPPED_CANDIDATE → CONTEXT_CHECK →
    { NORMAL_QUEUE | PARKED | PICKUP | BREAKDOWN }

Context features: speed, duration, signal state, lane location,
surrounding vehicle motion, behavior before stopping.
"""

import logging
import time
from enum import Enum
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)


class BreakdownState(str, Enum):
    MOVING = "moving"
    SLOWING = "slowing"
    STOPPED_CANDIDATE = "stopped_candidate"
    CONTEXT_CHECK = "context_check"
    NORMAL_QUEUE = "normal_queue"
    PARKED = "parked"
    PICKUP = "pickup"
    BREAKDOWN = "breakdown"


class BreakdownDetector:
    """Context-aware breakdown detection with state machine.

    Instead of flagging every vehicle stopped for >45 seconds, classifies
    the stationary state using multiple contextual features.

    Args:
        config: Dict from thresholds.yaml under 'breakdown'.
    """

    def __init__(self, config: dict) -> None:
        self._speed_thresh: float = config.get("speed_threshold_kmph", 2.0)
        self._candidate_dur: float = config.get("candidate_duration_sec", 15.0)
        self._confirmed_dur: float = config.get("confirmed_duration_sec", 45.0)
        self._stop_line_excl: float = config.get("stop_line_exclusion_m", 5.0)
        self._roadside_dist: float = config.get("roadside_distance_m", 3.0)

        # Per-track state
        self._states: dict[int, BreakdownState] = {}
        self._stop_start: dict[int, float] = {}
        self._pre_stop_speed: dict[int, float] = {}

    def update(
        self,
        track_id: int,
        speed_kmph: float,
        world_pos: Optional[tuple[float, float]] = None,
        distance_to_stop_line_m: float = 50.0,
        distance_to_centerline_m: float = 0.0,
        lane_width_m: float = 3.5,
        signal_is_green: bool = False,
        nearby_moving_count: int = 0,
    ) -> Optional[dict]:
        """Update breakdown detection for a tracked vehicle.

        Args:
            track_id: Track identifier.
            speed_kmph: Current speed.
            world_pos: World position (x_m, y_m).
            distance_to_stop_line_m: Distance to nearest stop line.
            distance_to_centerline_m: Distance from lane centerline.
            lane_width_m: Lane width for roadside detection.
            signal_is_green: Whether the signal is green (stopped during green = suspicious).
            nearby_moving_count: Number of nearby vehicles that are moving.

        Returns:
            Alert dict if breakdown confirmed, None otherwise.
        """
        now = time.time()
        current = self._states.get(track_id, BreakdownState.MOVING)

        # Track pre-stop speed
        if speed_kmph > self._speed_thresh:
            self._pre_stop_speed[track_id] = speed_kmph

        is_stopped = speed_kmph < self._speed_thresh

        # State transitions
        if current == BreakdownState.MOVING:
            if is_stopped:
                self._states[track_id] = BreakdownState.SLOWING
            else:
                self._stop_start.pop(track_id, None)

        elif current == BreakdownState.SLOWING:
            if not is_stopped:
                self._states[track_id] = BreakdownState.MOVING
                self._stop_start.pop(track_id, None)
            else:
                if track_id not in self._stop_start:
                    self._stop_start[track_id] = now
                elapsed = now - self._stop_start[track_id]
                if elapsed >= self._candidate_dur:
                    self._states[track_id] = BreakdownState.STOPPED_CANDIDATE

        elif current == BreakdownState.STOPPED_CANDIDATE:
            if not is_stopped:
                self._states[track_id] = BreakdownState.MOVING
                self._stop_start.pop(track_id, None)
                return None

            self._states[track_id] = BreakdownState.CONTEXT_CHECK

        elif current == BreakdownState.CONTEXT_CHECK:
            if not is_stopped:
                self._states[track_id] = BreakdownState.MOVING
                self._stop_start.pop(track_id, None)
                return None

            # Context classification
            classification = self._classify_context(
                track_id=track_id,
                distance_to_stop_line=distance_to_stop_line_m,
                distance_to_centerline=distance_to_centerline_m,
                lane_width=lane_width_m,
                signal_green=signal_is_green,
                nearby_moving=nearby_moving_count,
                stop_duration=now - self._stop_start.get(track_id, now),
            )
            self._states[track_id] = classification

            if classification == BreakdownState.BREAKDOWN:
                duration = now - self._stop_start.get(track_id, now)
                alert = {
                    "track_id": track_id,
                    "incident_type": "BREAKDOWN",
                    "duration_sec": round(duration, 1),
                    "world_position": world_pos,
                    "pre_stop_speed_kmph": round(
                        self._pre_stop_speed.get(track_id, 0.0), 1
                    ),
                    "signal_was_green": signal_is_green,
                    "nearby_moving_vehicles": nearby_moving_count,
                    "timestamp": now,
                }
                logger.warning(
                    f"🔧 BREAKDOWN DETECTED: track={track_id}, "
                    f"duration={duration:.0f}s, "
                    f"signal_green={signal_is_green}"
                )
                return alert

        elif current == BreakdownState.BREAKDOWN:
            # Continue monitoring — upgrade severity if still stopped
            if not is_stopped:
                self._states[track_id] = BreakdownState.MOVING
                self._stop_start.pop(track_id, None)
                logger.info(f"Track {track_id}: breakdown cleared (vehicle moved)")

        # Other terminal states (NORMAL_QUEUE, PARKED, PICKUP) reset on motion
        elif current in (
            BreakdownState.NORMAL_QUEUE,
            BreakdownState.PARKED,
            BreakdownState.PICKUP,
        ):
            if not is_stopped:
                self._states[track_id] = BreakdownState.MOVING
                self._stop_start.pop(track_id, None)

        return None

    def _classify_context(
        self,
        track_id: int,
        distance_to_stop_line: float,
        distance_to_centerline: float,
        lane_width: float,
        signal_green: bool,
        nearby_moving: int,
        stop_duration: float,
    ) -> BreakdownState:
        """Classify the reason a vehicle is stationary (Section 63).

        Logic:
        - Near stop line + signal not green → NORMAL_QUEUE
        - Far from centerline (roadside) → PARKED
        - Short stop duration → PICKUP
        - Long duration + signal green + others moving → BREAKDOWN
        """
        # Near stop line and signal is likely red
        if distance_to_stop_line < self._stop_line_excl and not signal_green:
            return BreakdownState.NORMAL_QUEUE

        # Roadside: far from lane center
        if distance_to_centerline > lane_width * 0.6:
            if stop_duration < 30:
                return BreakdownState.PICKUP
            return BreakdownState.PARKED

        # Short stop (< confirmed duration) — might be pickup/dropoff
        if stop_duration < self._confirmed_dur:
            # If during green with others moving, suspicious
            if signal_green and nearby_moving >= 2:
                return BreakdownState.BREAKDOWN
            return BreakdownState.NORMAL_QUEUE

        # Long stop in active lane during green = breakdown
        if signal_green and nearby_moving >= 2:
            return BreakdownState.BREAKDOWN

        # Long stop but signal might be red — queue
        if not signal_green:
            return BreakdownState.NORMAL_QUEUE

        # Default: if stopped very long regardless, flag as breakdown
        if stop_duration > self._confirmed_dur * 2:
            return BreakdownState.BREAKDOWN

        return BreakdownState.NORMAL_QUEUE

    def get_state(self, track_id: int) -> BreakdownState:
        """Get current state for a track."""
        return self._states.get(track_id, BreakdownState.MOVING)

    def get_active_breakdowns(self) -> list[int]:
        """Get track IDs with active breakdown alerts."""
        return [
            tid for tid, state in self._states.items()
            if state == BreakdownState.BREAKDOWN
        ]

    def cleanup_track(self, track_id: int) -> None:
        """Remove state for a lost track."""
        self._states.pop(track_id, None)
        self._stop_start.pop(track_id, None)
        self._pre_stop_speed.pop(track_id, None)
