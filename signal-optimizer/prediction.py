"""
prediction.py — Short-Horizon Congestion Forecasting (Linear Regression)
=========================================================================
Maintains a short rolling window of recent queue-length readings per lane
and fits a degree-1 polynomial (linear regression) over that window using
``numpy.polyfit``.

The fitted slope classifies the trend:
  - ``"rising"``  : slope > +RISING_THRESHOLD  (veh / sample)
  - ``"falling"`` : slope < -FALLING_THRESHOLD
  - ``"stable"``  : otherwise

The extrapolated queue length ~5 minutes ahead is also returned so the
max-pressure algorithm can act *before* a junction becomes visibly gridlocked.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Deque, Dict, Literal, Tuple

import numpy as np

# ---------------------------------------------------------------------------
# Tuning constants
# ---------------------------------------------------------------------------
WINDOW_SIZE: int = 10          # number of recent samples to keep
RISING_THRESHOLD: float = 0.5  # veh per sample interval
FALLING_THRESHOLD: float = 0.5

# How many samples ahead to extrapolate for the "5-minute" forecast.
# Adjust based on Person A's actual publish rate.
FORECAST_HORIZON_SAMPLES: int = 10  # e.g. 10 samples × 30 s = 5 min

TrendLabel = Literal["rising", "falling", "stable"]


# ---------------------------------------------------------------------------
# Per-lane predictor
# ---------------------------------------------------------------------------

@dataclass
class LanePredictor:
    """Rolling-window linear-regression predictor for a single lane."""

    lane_id: str
    window_size: int = WINDOW_SIZE
    _queue_history: Deque[float] = field(default_factory=deque, init=False)

    def update(self, queue_length: float) -> None:
        """Append a new queue-length reading.  Oldest reading is evicted once
        the window is full."""
        self._queue_history.append(queue_length)
        if len(self._queue_history) > self.window_size:
            self._queue_history.popleft()

    def predict(self) -> Tuple[TrendLabel, float, float]:
        """Return ``(trend, slope, predicted_queue_at_horizon)``.

        Returns ``("stable", 0.0, current_queue)`` when fewer than 2 readings
        are available (cannot fit a line).
        """
        history = list(self._queue_history)
        n = len(history)

        if n < 2:
            current = history[-1] if history else 0.0
            return "stable", 0.0, current

        x = np.arange(n, dtype=float)
        y = np.array(history, dtype=float)
        slope, intercept = np.polyfit(x, y, 1)

        # Classify trend
        if slope > RISING_THRESHOLD:
            trend: TrendLabel = "rising"
        elif slope < -FALLING_THRESHOLD:
            trend = "falling"
        else:
            trend = "stable"

        # Extrapolate to forecast horizon
        predicted = intercept + slope * (n - 1 + FORECAST_HORIZON_SAMPLES)
        predicted = max(0.0, predicted)  # queues can't be negative

        return trend, float(slope), float(predicted)

    @property
    def sample_count(self) -> int:
        return len(self._queue_history)


# ---------------------------------------------------------------------------
# Junction-level predictor (aggregates across all lanes)
# ---------------------------------------------------------------------------

class JunctionPredictor:
    """Manages one :class:`LanePredictor` per lane at a junction."""

    def __init__(self, junction_id: str, window_size: int = WINDOW_SIZE) -> None:
        self.junction_id = junction_id
        self.window_size = window_size
        self._lanes: Dict[str, LanePredictor] = {}

    def update(self, lane_readings: dict[str, float]) -> None:
        """Accept a dict of ``{lane_id: queue_length}`` and update each lane.

        New lane IDs are registered automatically.
        """
        for lane_id, queue_length in lane_readings.items():
            if lane_id not in self._lanes:
                self._lanes[lane_id] = LanePredictor(
                    lane_id=lane_id, window_size=self.window_size
                )
            self._lanes[lane_id].update(queue_length)

    def get_trend(self, lane_id: str) -> TrendLabel:
        """Return the current trend label for ``lane_id``."""
        if lane_id not in self._lanes:
            return "stable"
        trend, _, _ = self._lanes[lane_id].predict()
        return trend

    def get_predicted_queue(self, lane_id: str) -> float:
        """Return the extrapolated queue length at the forecast horizon."""
        if lane_id not in self._lanes:
            return 0.0
        _, _, predicted = self._lanes[lane_id].predict()
        return predicted

    def dominant_trend(self) -> TrendLabel:
        """Return the most common trend across all lanes (majority vote)."""
        counts: dict[TrendLabel, int] = {"rising": 0, "falling": 0, "stable": 0}
        for lp in self._lanes.values():
            trend, _, _ = lp.predict()
            counts[trend] += 1
        return max(counts, key=lambda k: counts[k])  # type: ignore[return-value]

    def summary(self) -> dict:
        """Return a summary dict suitable for inclusion in the output contract."""
        result = {}
        for lane_id, lp in self._lanes.items():
            trend, slope, predicted = lp.predict()
            result[lane_id] = {
                "trend": trend,
                "slope_veh_per_sample": round(slope, 3),
                "predicted_queue_at_horizon": round(predicted, 1),
            }
        return result


# ---------------------------------------------------------------------------
# Convenience label for output contract
# ---------------------------------------------------------------------------

def congestion_label(predictor: JunctionPredictor) -> TrendLabel:
    """Return the junction-level congestion trend for the output contract
    field ``predicted_congestion_5min``."""
    return predictor.dominant_trend()


# ---------------------------------------------------------------------------
# Quick self-test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    jp = JunctionPredictor("junction_01")
    # Simulate rising NS queue
    for i, q in enumerate([2, 3, 4, 6, 8, 10, 12, 14, 16, 18]):
        jp.update({"lane_NS": float(q), "lane_EW": float(max(0, 10 - i))})

    print("NS trend :", jp.get_trend("lane_NS"))
    print("EW trend :", jp.get_trend("lane_EW"))
    print("Dominant :", jp.dominant_trend())
    print("NS pred  :", jp.get_predicted_queue("lane_NS"))
    print(jp.summary())
