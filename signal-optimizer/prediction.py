"""
prediction.py — Ensemble Congestion Forecasting
=================================================
Maintains a short rolling window of recent queue-length readings per lane
and forecasts using an **ensemble** of lightweight predictors:

  1. Linear regression (original)
  2. Moving average
  3. Exponential moving average
  4. Historical baseline (from historical.py)

Also provides prediction uncertainty estimation from residuals.

Improvements #7, #34 from new_instruct.md.
"""

from __future__ import annotations

import math
from collections import deque
from dataclasses import dataclass, field
from typing import Deque, Dict, Literal, Optional, Tuple

import numpy as np

from controller_config import ControllerConfig, get_config

# ---------------------------------------------------------------------------
# Tuning constants (defaults; overridden by ControllerConfig)
# ---------------------------------------------------------------------------
WINDOW_SIZE: int = 10
RISING_THRESHOLD: float = 0.5
FALLING_THRESHOLD: float = 0.5
FORECAST_HORIZON_SAMPLES: int = 10

TrendLabel = Literal["rising", "falling", "stable"]


# ---------------------------------------------------------------------------
# Per-lane ensemble predictor
# ---------------------------------------------------------------------------

@dataclass
class LanePredictor:
    """Rolling-window ensemble predictor for a single lane."""

    lane_id: str
    window_size: int = WINDOW_SIZE
    _queue_history: Deque[float] = field(default_factory=deque, init=False)
    _ema_value: float = field(default=0.0, init=False)
    _ema_alpha: float = field(default=0.3, init=False)
    _past_predictions: Deque[Tuple[float, float]] = field(default_factory=deque, init=False)
    _residuals: Deque[float] = field(default_factory=deque, init=False)
    _historical_value: Optional[float] = field(default=None, init=False)

    def set_historical(self, value: float) -> None:
        """Set the historical baseline prediction for ensemble blending."""
        self._historical_value = value

    def update(self, queue_length: float) -> None:
        """Append a new queue-length reading.  Oldest reading is evicted once
        the window is full."""
        # Track prediction error: compare current actual with past prediction
        if self._past_predictions:
            pred_time, pred_value = self._past_predictions[0]
            # If this is roughly the right time to evaluate
            error = abs(queue_length - pred_value)
            self._residuals.append(error)
            if len(self._residuals) > self.window_size * 2:
                self._residuals.popleft()
            self._past_predictions.popleft()

        self._queue_history.append(queue_length)
        if len(self._queue_history) > self.window_size:
            self._queue_history.popleft()

        # Update EMA
        if len(self._queue_history) == 1:
            self._ema_value = queue_length
        else:
            self._ema_value = (self._ema_alpha * queue_length
                               + (1 - self._ema_alpha) * self._ema_value)

    def predict(
        self,
        config: Optional[ControllerConfig] = None,
    ) -> Tuple[TrendLabel, float, float, float]:
        """Return ``(trend, slope, predicted_queue, uncertainty)``.

        Returns ``("stable", 0.0, current_queue, 0.0)`` when fewer than 2
        readings are available.
        """
        cfg = config or get_config()
        history = list(self._queue_history)
        n = len(history)

        if n < 2:
            current = history[-1] if history else 0.0
            return "stable", 0.0, current, 0.0

        x = np.arange(n, dtype=float)
        y = np.array(history, dtype=float)
        slope, intercept = np.polyfit(x, y, 1)

        # --- Individual predictions ---
        horizon = cfg.prediction_horizon

        # 1. Linear trend prediction
        linear_pred = max(0.0, intercept + slope * (n - 1 + horizon))

        # 2. Moving average prediction
        ma_pred = max(0.0, sum(history) / n)

        # 3. Exponential moving average prediction
        ema_pred = max(0.0, self._ema_value)

        # 4. Historical prediction
        hist_pred = self._historical_value if self._historical_value is not None else ma_pred

        # --- Ensemble combination ---
        ensemble_pred = (
            cfg.ensemble_weight_linear * linear_pred
            + cfg.ensemble_weight_ma * ma_pred
            + cfg.ensemble_weight_ema * ema_pred
            + cfg.ensemble_weight_historical * hist_pred
        )
        ensemble_pred = max(0.0, ensemble_pred)

        # Store prediction for future error tracking
        self._past_predictions.append((n, ensemble_pred))
        if len(self._past_predictions) > self.window_size:
            self._past_predictions.popleft()

        # --- Classify trend (still based on linear slope) ---
        rising_thresh = cfg.rising_threshold
        falling_thresh = cfg.falling_threshold

        if slope > rising_thresh:
            trend: TrendLabel = "rising"
        elif slope < -falling_thresh:
            trend = "falling"
        else:
            trend = "stable"

        # --- Prediction uncertainty (Improvement #34) ---
        uncertainty = self._compute_uncertainty()

        return trend, float(slope), float(ensemble_pred), uncertainty

    def _compute_uncertainty(self) -> float:
        """Estimate prediction uncertainty from historical residuals."""
        if len(self._residuals) < 2:
            return 0.0
        mean_err = sum(self._residuals) / len(self._residuals)
        variance = sum((e - mean_err) ** 2 for e in self._residuals) / len(self._residuals)
        return float(math.sqrt(max(0.0, variance)))

    @property
    def prediction_mae(self) -> float:
        """Mean Absolute Error of past predictions."""
        if not self._residuals:
            return 0.0
        return sum(self._residuals) / len(self._residuals)

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

    def set_historical_values(self, historical: dict[str, float]) -> None:
        """Set historical baseline values for all lanes."""
        for lane_id, value in historical.items():
            if lane_id in self._lanes:
                self._lanes[lane_id].set_historical(value)

    def get_trend(self, lane_id: str) -> TrendLabel:
        """Return the current trend label for ``lane_id``."""
        if lane_id not in self._lanes:
            return "stable"
        trend, _, _, _ = self._lanes[lane_id].predict()
        return trend

    def get_predicted_queue(self, lane_id: str) -> float:
        """Return the ensemble-predicted queue length at the forecast horizon."""
        if lane_id not in self._lanes:
            return 0.0
        _, _, predicted, _ = self._lanes[lane_id].predict()
        return predicted

    def get_prediction_uncertainty(self, lane_id: str) -> float:
        """Return the prediction uncertainty for a lane."""
        if lane_id not in self._lanes:
            return 0.0
        _, _, _, uncertainty = self._lanes[lane_id].predict()
        return uncertainty

    def get_full_prediction(self, lane_id: str) -> dict:
        """Return full prediction details for a lane."""
        if lane_id not in self._lanes:
            return {"trend": "stable", "slope": 0.0, "predicted": 0.0, "uncertainty": 0.0}
        trend, slope, predicted, uncertainty = self._lanes[lane_id].predict()
        return {
            "trend": trend,
            "slope": round(slope, 3),
            "predicted": round(predicted, 1),
            "uncertainty": round(uncertainty, 2),
            "mae": round(self._lanes[lane_id].prediction_mae, 2),
        }

    def dominant_trend(self) -> TrendLabel:
        """Return the most common trend across all lanes (majority vote)."""
        counts: dict[TrendLabel, int] = {"rising": 0, "falling": 0, "stable": 0}
        for lp in self._lanes.values():
            trend, _, _, _ = lp.predict()
            counts[trend] += 1
        return max(counts, key=lambda k: counts[k])  # type: ignore[return-value]

    def summary(self) -> dict:
        """Return a summary dict suitable for inclusion in the output contract."""
        result = {}
        for lane_id, lp in self._lanes.items():
            result[lane_id] = lp.prediction_mae  # backward-compat; use get_full_prediction for detail
            trend, slope, predicted, uncertainty = lp.predict()
            result[lane_id] = {
                "trend": trend,
                "slope_veh_per_sample": round(slope, 3),
                "predicted_queue_at_horizon": round(predicted, 1),
                "uncertainty": round(uncertainty, 2),
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
    print("NS uncert:", jp.get_prediction_uncertainty("lane_NS"))
    print("\nFull NS  :", jp.get_full_prediction("lane_NS"))
    print("Full EW  :", jp.get_full_prediction("lane_EW"))
    print("\nSummary  :", jp.summary())
