"""
traffic_state.py — Temporal Intelligence Engine
=================================================
Derives rich traffic state from the same small telemetry contract by
tracking measurements over time.  Per-lane stateful tracker that computes:

- Queue growth rate          (Δqueue / Δt)
- Queue acceleration         (Δgrowth / Δt)
- Congestion score           (normalized queue + speed + growth composite)
- Arrival rate               (estimated from queue increases during red)
- Clearance rate             (estimated from queue decreases during green)
- Time-to-congestion         ((capacity − queue) / growth_rate)
- Temporal smoothing         (EMA with confidence-weighted α)
- Normalization              (queue/capacity, 1 − speed/free_flow)

Improvements #1–#4, #16–#18, #23–#24 from new_instruct.md.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Deque, Dict, Literal, Optional

from controller_config import ControllerConfig, get_config


# ---------------------------------------------------------------------------
# Anomaly levels (also used by historical.py)
# ---------------------------------------------------------------------------

AnomalyLevel = Literal["normal", "elevated", "high_anomaly", "extreme_anomaly"]


# ---------------------------------------------------------------------------
# Per-lane state tracker
# ---------------------------------------------------------------------------

@dataclass
class LaneState:
    """Stateful tracker for a single lane."""

    lane_id: str

    # --- Raw latest values ---
    queue: float = 0.0
    density: float = 0.0
    speed_mps: float = 0.0

    # --- Smoothed values ---
    smoothed_queue: float = 0.0
    smoothed_speed: float = 0.0

    # --- Derived metrics ---
    growth_rate: float = 0.0          # veh/sample  (positive = growing)
    acceleration: float = 0.0        # veh/sample²
    congestion_score: float = 0.0    # [0, 1] composite
    arrival_rate: float = 0.0        # veh/sample (estimated)
    clearance_rate: float = 0.0      # veh/sample (estimated, positive = clearing)
    time_to_congestion: float = float("inf")  # samples until capacity

    # --- Normalized values ---
    queue_occupancy: float = 0.0     # queue / capacity  [0, 1]
    speed_congestion: float = 0.0    # 1 - speed/free_flow [0, 1]
    growth_score: float = 0.0        # normalized growth [0, 1]

    # --- Internal history ---
    _prev_queue: float = field(default=0.0, repr=False)
    _prev_growth: float = field(default=0.0, repr=False)
    _sample_count: int = field(default=0, repr=False)


class TrafficStateEngine:
    """Manages per-lane state for all lanes at a junction."""

    def __init__(self, config: Optional[ControllerConfig] = None) -> None:
        self._cfg = config or get_config()
        self._lanes: Dict[str, LaneState] = {}
        self._current_phase: Optional[str] = None

    @property
    def lanes(self) -> Dict[str, LaneState]:
        return self._lanes

    def set_current_phase(self, phase: str) -> None:
        """Update the current green phase (used for arrival/clearance estimation)."""
        self._current_phase = phase

    def update(
        self,
        lane_readings: dict[str, dict],
        confidence: float = 1.0,
        current_phase: Optional[str] = None,
    ) -> None:
        """Process one event's lane data and update all derived metrics.

        Parameters
        ----------
        lane_readings:
            ``{lane_id: {"queue_length": int, "density": int, "speed_mps": float}}``
        confidence:
            Sensor confidence score for adaptive smoothing.
        current_phase:
            Currently active phase name (e.g. ``"NS_green"``).
        """
        if current_phase is not None:
            self._current_phase = current_phase

        cfg = self._cfg
        for lane_id, data in lane_readings.items():
            if lane_id not in self._lanes:
                self._lanes[lane_id] = LaneState(lane_id=lane_id)

            ls = self._lanes[lane_id]
            raw_queue = float(data.get("queue_length", data.get("density", 0)))
            raw_speed = float(data.get("speed_mps", 0.0))
            raw_density = float(data.get("density", raw_queue))

            # --- Confidence-weighted EMA alpha (Improvement #24) ---
            if confidence >= cfg.confidence_normal:
                alpha = cfg.smoothing_alpha_high_conf
            elif confidence < cfg.confidence_smoothed:
                alpha = cfg.smoothing_alpha_low_conf
            else:
                alpha = cfg.smoothing_alpha

            # --- Temporal smoothing (Improvement #23) ---
            if ls._sample_count == 0:
                ls.smoothed_queue = raw_queue
                ls.smoothed_speed = raw_speed
            else:
                ls.smoothed_queue = alpha * raw_queue + (1 - alpha) * ls.smoothed_queue
                ls.smoothed_speed = alpha * raw_speed + (1 - alpha) * ls.smoothed_speed

            # --- Queue growth rate (Improvement #1) ---
            prev_growth = ls.growth_rate
            if ls._sample_count > 0:
                ls.growth_rate = ls.smoothed_queue - ls._prev_queue
            else:
                ls.growth_rate = 0.0

            # --- Queue acceleration (Improvement #2) ---
            if ls._sample_count > 1:
                ls.acceleration = ls.growth_rate - ls._prev_growth
            else:
                ls.acceleration = 0.0

            # --- Arrival / clearance rate (Improvement #16, #17) ---
            if ls.growth_rate > 0:
                ls.arrival_rate = ls.growth_rate
            elif ls.growth_rate < 0:
                ls.clearance_rate = abs(ls.growth_rate)

            # --- Normalization (Improvement #4) ---
            capacity = float(cfg.default_lane_capacity)
            free_flow = cfg.free_flow_speed_mps

            ls.queue_occupancy = min(1.0, max(0.0, ls.smoothed_queue / capacity)) if capacity > 0 else 0.0
            ls.speed_congestion = min(1.0, max(0.0, 1.0 - (ls.smoothed_speed / free_flow))) if free_flow > 0 else 0.0

            # Normalize growth to [0, 1] range — cap at ±capacity/2 per sample
            max_growth = capacity / 2
            ls.growth_score = min(1.0, max(0.0, ls.growth_rate / max_growth)) if max_growth > 0 else 0.0

            # --- Congestion score (Improvement #3) ---
            ls.congestion_score = (
                cfg.congestion_queue_weight * ls.queue_occupancy
                + cfg.congestion_speed_weight * ls.speed_congestion
                + cfg.congestion_growth_weight * ls.growth_score
            )
            ls.congestion_score = min(1.0, max(0.0, ls.congestion_score))

            # --- Time-to-congestion (Improvement #18) ---
            if ls.growth_rate > 0.01:
                remaining = capacity - ls.smoothed_queue
                ls.time_to_congestion = max(0.0, remaining / ls.growth_rate)
            else:
                ls.time_to_congestion = float("inf")

            # --- Store raw values and advance counters ---
            ls.queue = raw_queue
            ls.density = raw_density
            ls.speed_mps = raw_speed
            ls._prev_queue = ls.smoothed_queue
            ls._prev_growth = ls.growth_rate
            ls._sample_count += 1

    def get_lane(self, lane_id: str) -> LaneState:
        """Return the state for a lane, or a default empty state."""
        if lane_id in self._lanes:
            return self._lanes[lane_id]
        return LaneState(lane_id=lane_id)

    def get_approach_state(self, lane_ids: list[str]) -> dict:
        """Aggregate traffic state across multiple lanes (one approach)."""
        total_queue = 0.0
        total_growth = 0.0
        total_accel = 0.0
        avg_speed = 0.0
        avg_congestion = 0.0
        max_occupancy = 0.0
        min_ttc = float("inf")
        count = 0

        for lid in lane_ids:
            ls = self.get_lane(lid)
            total_queue += ls.smoothed_queue
            total_growth += ls.growth_rate
            total_accel += ls.acceleration
            avg_speed += ls.smoothed_speed
            avg_congestion += ls.congestion_score
            max_occupancy = max(max_occupancy, ls.queue_occupancy)
            min_ttc = min(min_ttc, ls.time_to_congestion)
            count += 1

        if count > 0:
            avg_speed /= count
            avg_congestion /= count

        return {
            "total_queue": total_queue,
            "total_growth": total_growth,
            "total_acceleration": total_accel,
            "avg_speed": avg_speed,
            "avg_congestion": avg_congestion,
            "max_occupancy": max_occupancy,
            "time_to_congestion": min_ttc,
        }

    def summary(self) -> dict[str, dict]:
        """Return a summary dict of all lane states."""
        result = {}
        for lane_id, ls in self._lanes.items():
            result[lane_id] = {
                "queue": round(ls.smoothed_queue, 1),
                "growth_rate": round(ls.growth_rate, 3),
                "acceleration": round(ls.acceleration, 3),
                "congestion_score": round(ls.congestion_score, 3),
                "queue_occupancy": round(ls.queue_occupancy, 3),
                "speed_congestion": round(ls.speed_congestion, 3),
                "time_to_congestion": round(ls.time_to_congestion, 1)
                    if ls.time_to_congestion < float("inf") else None,
                "arrival_rate": round(ls.arrival_rate, 3),
                "clearance_rate": round(ls.clearance_rate, 3),
            }
        return result


# ---------------------------------------------------------------------------
# Quick self-test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import json

    engine = TrafficStateEngine()

    # Simulate rising NS queue, stable EW
    readings_sequence = [
        {"lane_NS_1": {"queue_length": 10, "density": 12, "speed_mps": 5.0},
         "lane_EW_1": {"queue_length": 5,  "density": 6,  "speed_mps": 7.0}},
        {"lane_NS_1": {"queue_length": 13, "density": 15, "speed_mps": 4.5},
         "lane_EW_1": {"queue_length": 5,  "density": 6,  "speed_mps": 6.8}},
        {"lane_NS_1": {"queue_length": 17, "density": 19, "speed_mps": 3.8},
         "lane_EW_1": {"queue_length": 6,  "density": 7,  "speed_mps": 6.5}},
        {"lane_NS_1": {"queue_length": 22, "density": 24, "speed_mps": 2.5},
         "lane_EW_1": {"queue_length": 5,  "density": 6,  "speed_mps": 7.0}},
        {"lane_NS_1": {"queue_length": 28, "density": 30, "speed_mps": 1.5},
         "lane_EW_1": {"queue_length": 4,  "density": 5,  "speed_mps": 7.2}},
    ]

    for i, readings in enumerate(readings_sequence):
        engine.update(readings, confidence=0.90)
        ns = engine.get_lane("lane_NS_1")
        print(f"Step {i}: NS queue={ns.smoothed_queue:.1f}  "
              f"growth={ns.growth_rate:+.2f}  accel={ns.acceleration:+.2f}  "
              f"congestion={ns.congestion_score:.3f}  "
              f"TTC={ns.time_to_congestion:.1f}")

    print("\n=== Full Summary ===")
    print(json.dumps(engine.summary(), indent=2))

    print("\n=== NS Approach State ===")
    print(engine.get_approach_state(["lane_NS_1"]))
