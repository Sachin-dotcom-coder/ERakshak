"""
traffic_state/queue.py — Queue Probability & Estimation (Sections 40-45)
=========================================================================
Upgrades queue detection from simple speed threshold to a multi-factor
probability model.

Queue Probability:
  Q_i = w1*S_i + w2*D_i + w3*R_i + w4*F_i + w5*T_i + w6*G_i

Where:
  S_i = low-speed evidence
  D_i = distance to stop line (closer = more likely queued)
  R_i = red-signal evidence
  F_i = following-vehicle density
  T_i = stop duration
  G_i = group/queue continuity

Also provides:
- Queue length from farthest reliable queue member (Section 42)
- EMA smoothing (Section 43)
- Queue growth rate and acceleration (Section 44)
- Spillback prediction (Section 45)
"""

import logging
import time
from collections import deque
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)


class QueueEstimator:
    """Multi-factor queue probability model and queue state tracker.

    Args:
        config: Dict from thresholds.yaml under 'queue'.
        lanes_config: Dict from lanes.yaml for max queue capacity.
    """

    def __init__(self, config: dict, lanes_config: Optional[dict] = None) -> None:
        self._speed_thresh: float = config.get("speed_threshold_kmph", 5.0)
        self._prob_thresh: float = config.get("probability_threshold", 0.70)
        self._ema_alpha: float = config.get("smoothing_alpha", 0.30)

        # Queue probability weights (Section 40)
        weights = config.get("weights", {})
        self._w_speed: float = weights.get("low_speed", 0.25)
        self._w_distance: float = weights.get("stop_line_distance", 0.15)
        self._w_signal: float = weights.get("red_signal", 0.15)
        self._w_following: float = weights.get("following_density", 0.15)
        self._w_duration: float = weights.get("stop_duration", 0.15)
        self._w_group: float = weights.get("group_continuity", 0.15)

        # Lane capacities for spillback detection
        self._lane_capacities: dict[str, float] = {}
        if lanes_config:
            for lane_id, cfg in lanes_config.get("lanes", {}).items():
                self._lane_capacities[lane_id] = cfg.get(
                    "max_queue_capacity_m", 100.0
                )

        # Per-lane queue state for smoothing and dynamics
        self._smoothed_lengths: dict[str, float] = {}
        self._queue_history: dict[str, deque] = {}  # lane → deque of (timestamp, length)
        self._history_max: int = 60  # ~60 seconds of history

        # Per-vehicle stop tracking
        self._stop_start_times: dict[int, float] = {}  # track_id → stop start time

    def compute_queue_probability(
        self,
        track_id: int,
        speed_kmph: float,
        distance_to_stop_m: float,
        signal_is_red: bool = False,
        nearby_vehicle_count: int = 0,
        max_nearby: int = 10,
    ) -> float:
        """Compute queue membership probability for a vehicle (Section 40).

        Args:
            track_id: Vehicle track ID.
            speed_kmph: Current vehicle speed in km/h.
            distance_to_stop_m: Distance to stop line in meters.
            signal_is_red: Whether the signal for this approach is red.
            nearby_vehicle_count: Number of vehicles nearby in the same lane.
            max_nearby: Maximum expected nearby count for normalization.

        Returns:
            Queue probability in [0.0, 1.0].
        """
        now = time.time()

        # S_i: Low-speed evidence (1.0 when stopped, 0.0 when moving fast)
        speed_score = max(0.0, 1.0 - speed_kmph / self._speed_thresh)

        # D_i: Distance to stop line (closer = higher probability)
        # Normalize: 0m → 1.0, >100m → 0.0
        dist_score = max(0.0, 1.0 - distance_to_stop_m / 100.0)

        # R_i: Red signal evidence
        signal_score = 1.0 if signal_is_red else 0.0

        # F_i: Following-vehicle density
        following_score = min(1.0, nearby_vehicle_count / max(max_nearby, 1))

        # T_i: Stop duration
        duration_score = 0.0
        if speed_kmph < self._speed_thresh:
            if track_id not in self._stop_start_times:
                self._stop_start_times[track_id] = now
            stop_duration = now - self._stop_start_times[track_id]
            # Normalize: 0s → 0, >10s → 1.0
            duration_score = min(1.0, stop_duration / 10.0)
        else:
            self._stop_start_times.pop(track_id, None)

        # G_i: Group/queue continuity (approximated by following density + speed)
        group_score = (speed_score + following_score) / 2.0

        # Weighted sum
        probability = (
            self._w_speed * speed_score
            + self._w_distance * dist_score
            + self._w_signal * signal_score
            + self._w_following * following_score
            + self._w_duration * duration_score
            + self._w_group * group_score
        )

        return float(np.clip(probability, 0.0, 1.0))

    def estimate_queue_length(
        self,
        lane_id: str,
        vehicles: list[dict],
        stop_line_pos: Optional[np.ndarray] = None,
    ) -> tuple[float, float]:
        """Estimate queue length from vehicles with high queue probability.

        Section 42: Find the farthest reliable queue member from the stop line.

        Args:
            lane_id: Lane identifier.
            vehicles: List of dicts with keys: 'world_x', 'world_y',
                     'queue_probability', 'speed_kmph'.
            stop_line_pos: [x, y] stop line position in world coords.

        Returns:
            (raw_length_m, smoothed_length_m) — raw and EMA-smoothed queue length.
        """
        if not vehicles or stop_line_pos is None:
            return (0.0, self._smoothed_lengths.get(lane_id, 0.0))

        # Filter to queue members
        queue_vehicles = [
            v for v in vehicles
            if v.get("queue_probability", 0) >= self._prob_thresh
        ]

        if not queue_vehicles:
            raw_length = 0.0
        else:
            # Find farthest queue member from stop line
            max_dist = 0.0
            for v in queue_vehicles:
                pos = np.array([v["world_x"], v["world_y"]])
                dist = float(np.linalg.norm(pos - stop_line_pos))
                max_dist = max(max_dist, dist)
            raw_length = max_dist

        # EMA smoothing (Section 43)
        prev = self._smoothed_lengths.get(lane_id, raw_length)
        smoothed = self._ema_alpha * raw_length + (1 - self._ema_alpha) * prev
        self._smoothed_lengths[lane_id] = smoothed

        # Record in history for dynamics
        now = time.time()
        if lane_id not in self._queue_history:
            self._queue_history[lane_id] = deque(maxlen=self._history_max)
        self._queue_history[lane_id].append((now, smoothed))

        return (raw_length, smoothed)

    def compute_queue_dynamics(
        self,
        lane_id: str,
    ) -> tuple[float, float]:
        """Compute queue growth rate and acceleration (Section 44).

        v_q = (Q_t - Q_{t-Δt}) / Δt
        a_q = (v_q(t) - v_q(t-Δt)) / Δt

        Args:
            lane_id: Lane identifier.

        Returns:
            (growth_rate_m_per_sec, acceleration_m_per_sec2)
        """
        history = self._queue_history.get(lane_id)
        if not history or len(history) < 2:
            return (0.0, 0.0)

        # Growth rate from last two entries
        t1, q1 = history[-2]
        t2, q2 = history[-1]
        dt = t2 - t1
        if dt <= 0:
            return (0.0, 0.0)

        growth_rate = (q2 - q1) / dt

        # Acceleration from last three entries
        acceleration = 0.0
        if len(history) >= 3:
            t0, q0 = history[-3]
            dt_prev = t1 - t0
            if dt_prev > 0:
                prev_growth = (q1 - q0) / dt_prev
                acceleration = (growth_rate - prev_growth) / dt

        return (growth_rate, acceleration)

    def predict_spillback(
        self,
        lane_id: str,
    ) -> Optional[float]:
        """Predict time-to-spillback for a lane (Section 45).

        T_spill = (L_available - Q) / v_q   when v_q > 0

        Args:
            lane_id: Lane identifier.

        Returns:
            Estimated seconds until spillback, or None if not applicable.
        """
        capacity = self._lane_capacities.get(lane_id)
        if capacity is None:
            return None

        current_length = self._smoothed_lengths.get(lane_id, 0.0)
        growth_rate, _ = self.compute_queue_dynamics(lane_id)

        if growth_rate <= 0:
            return None  # Queue not growing

        available = capacity - current_length
        if available <= 0:
            return 0.0  # Already at capacity

        time_to_spillback = available / growth_rate
        return float(time_to_spillback)

    def get_queue_confidence(
        self,
        lane_id: str,
        vehicles: list[dict],
    ) -> float:
        """Estimate confidence in the queue length estimate.

        Based on:
        - Number of queue members (more = more confident)
        - Consistency of queue probabilities
        - Speed of queue members (consistently low = more confident)

        Args:
            lane_id: Lane identifier.
            vehicles: List of vehicle dicts in the lane.

        Returns:
            Queue confidence in [0.0, 1.0].
        """
        if not vehicles:
            return 0.5  # Neutral

        queue_probs = [
            v.get("queue_probability", 0) for v in vehicles
        ]
        queue_members = [p for p in queue_probs if p >= self._prob_thresh]

        if not queue_members:
            return 0.5

        # More queue members → higher confidence
        count_factor = min(1.0, len(queue_members) / 5.0)

        # Higher mean probability → higher confidence
        mean_prob = float(np.mean(queue_members))

        # Lower variance → higher confidence
        if len(queue_members) >= 2:
            variance = float(np.var(queue_members))
            consistency = 1.0 - min(1.0, variance * 4)
        else:
            consistency = 0.5

        confidence = 0.4 * count_factor + 0.4 * mean_prob + 0.2 * consistency
        return float(np.clip(confidence, 0.0, 1.0))

    def cleanup_track(self, track_id: int) -> None:
        """Remove state for a lost track."""
        self._stop_start_times.pop(track_id, None)
