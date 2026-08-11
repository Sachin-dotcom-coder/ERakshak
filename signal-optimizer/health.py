"""
health.py — Controller Health Metrics & Self-Evaluation
========================================================
Tracks operational health of the signal optimizer itself, not just traffic.

Monitors:
  - Decision frequency and latency
  - Phase switches per minute
  - Prediction error (MAE / RMSE)
  - Fallback, emergency, and BRTS event counts
  - Decision effectiveness (did the queue improve after a green?)

Improvements #43–#45 from new_instruct.md.
"""

from __future__ import annotations

import math
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Deque, Dict, Optional, Tuple


# ---------------------------------------------------------------------------
# Prediction tracking entry
# ---------------------------------------------------------------------------

@dataclass
class PredictionRecord:
    """One recorded prediction for later error measurement."""
    lane_id: str
    predicted_queue: float
    timestamp: float           # when the prediction was made
    horizon_samples: int       # how many samples ahead it predicted
    actual_queue: Optional[float] = None  # filled in when the future arrives


# ---------------------------------------------------------------------------
# Decision effectiveness entry
# ---------------------------------------------------------------------------

@dataclass
class DecisionRecord:
    """Track whether a decision actually improved traffic."""
    timestamp: float
    phase: str
    cycle_sec: int
    queue_before: float        # total queue on the chosen approach before green
    queue_after: Optional[float] = None  # queue after green duration elapsed
    effective: Optional[bool] = None     # True if queue decreased


# ---------------------------------------------------------------------------
# Health tracker
# ---------------------------------------------------------------------------

class HealthTracker:
    """Collects and reports controller health metrics."""

    def __init__(self, window_size: int = 100) -> None:
        self._window = window_size

        # Decision timing
        self._decision_timestamps: Deque[float] = deque(maxlen=window_size)
        self._decision_latencies_ms: Deque[float] = deque(maxlen=window_size)

        # Phase switching
        self._phase_history: Deque[str] = deque(maxlen=window_size)
        self._switch_timestamps: Deque[float] = deque(maxlen=window_size)

        # Event counts
        self.total_decisions: int = 0
        self.emergency_count: int = 0
        self.brts_count: int = 0
        self.fallback_count: int = 0
        self.safety_violation_count: int = 0

        # Prediction tracking
        self._predictions: Deque[PredictionRecord] = deque(maxlen=window_size * 4)
        self._prediction_errors: Deque[float] = deque(maxlen=window_size)

        # Decision effectiveness
        self._pending_decisions: Deque[DecisionRecord] = deque(maxlen=window_size)
        self._effectiveness_history: Deque[bool] = deque(maxlen=window_size)

    # --- Recording -----------------------------------------------------------

    def record_decision(
        self,
        phase: str,
        cycle_sec: int,
        latency_ms: float = 0.0,
        emergency: bool = False,
        brts: bool = False,
        fallback: bool = False,
        safety_violation: bool = False,
        queue_on_approach: float = 0.0,
    ) -> None:
        """Record one decision event."""
        now = time.time()
        self.total_decisions += 1
        self._decision_timestamps.append(now)
        self._decision_latencies_ms.append(latency_ms)

        # Phase switching
        if self._phase_history and self._phase_history[-1] != phase:
            self._switch_timestamps.append(now)
        self._phase_history.append(phase)

        # Counters
        if emergency:
            self.emergency_count += 1
        if brts:
            self.brts_count += 1
        if fallback:
            self.fallback_count += 1
        if safety_violation:
            self.safety_violation_count += 1

        # Decision effectiveness tracking
        self._pending_decisions.append(DecisionRecord(
            timestamp=now,
            phase=phase,
            cycle_sec=cycle_sec,
            queue_before=queue_on_approach,
        ))

    def record_prediction(
        self,
        lane_id: str,
        predicted_queue: float,
        horizon_samples: int = 10,
    ) -> None:
        """Record a prediction for later error measurement."""
        self._predictions.append(PredictionRecord(
            lane_id=lane_id,
            predicted_queue=predicted_queue,
            timestamp=time.time(),
            horizon_samples=horizon_samples,
        ))

    def update_prediction_actuals(
        self,
        lane_actuals: dict[str, float],
    ) -> None:
        """Match past predictions with actual values and compute errors."""
        now = time.time()
        for pred in self._predictions:
            if pred.actual_queue is not None:
                continue
            if pred.lane_id in lane_actuals:
                # Simple: if enough time has passed (> 2 decision cycles), record
                # In practice this should check horizon_samples elapsed
                if now - pred.timestamp > 30:  # ~1 decision cycle
                    pred.actual_queue = lane_actuals[pred.lane_id]
                    error = abs(pred.predicted_queue - pred.actual_queue)
                    self._prediction_errors.append(error)

    def update_decision_effectiveness(
        self,
        current_queue_by_phase: dict[str, float],
    ) -> None:
        """Check pending decisions — did the queue decrease?"""
        now = time.time()
        still_pending = deque()
        for dec in self._pending_decisions:
            # After the green duration has elapsed, check the result
            if now - dec.timestamp > dec.cycle_sec and dec.queue_after is None:
                after_queue = current_queue_by_phase.get(dec.phase, dec.queue_before)
                dec.queue_after = after_queue
                dec.effective = after_queue < dec.queue_before
                self._effectiveness_history.append(dec.effective)
            elif dec.queue_after is None:
                still_pending.append(dec)
        self._pending_decisions = still_pending

    # --- Reporting -----------------------------------------------------------

    @property
    def decisions_per_minute(self) -> float:
        """Approximate decision frequency."""
        if len(self._decision_timestamps) < 2:
            return 0.0
        span = self._decision_timestamps[-1] - self._decision_timestamps[0]
        if span <= 0:
            return 0.0
        return (len(self._decision_timestamps) - 1) / (span / 60.0)

    @property
    def avg_latency_ms(self) -> float:
        if not self._decision_latencies_ms:
            return 0.0
        return sum(self._decision_latencies_ms) / len(self._decision_latencies_ms)

    @property
    def switches_per_minute(self) -> float:
        if len(self._switch_timestamps) < 2:
            return 0.0
        span = self._switch_timestamps[-1] - self._switch_timestamps[0]
        if span <= 0:
            return 0.0
        return (len(self._switch_timestamps) - 1) / (span / 60.0)

    @property
    def prediction_mae(self) -> float:
        """Mean Absolute Error of predictions."""
        if not self._prediction_errors:
            return 0.0
        return sum(self._prediction_errors) / len(self._prediction_errors)

    @property
    def prediction_rmse(self) -> float:
        """Root Mean Square Error of predictions."""
        if not self._prediction_errors:
            return 0.0
        mse = sum(e * e for e in self._prediction_errors) / len(self._prediction_errors)
        return math.sqrt(mse)

    @property
    def effectiveness_rate(self) -> float:
        """Fraction of decisions that reduced the queue (0–1)."""
        if not self._effectiveness_history:
            return 0.0
        return sum(1 for e in self._effectiveness_history if e) / len(self._effectiveness_history)

    def report(self) -> dict:
        """Return a full health report dict."""
        return {
            "total_decisions": self.total_decisions,
            "decisions_per_minute": round(self.decisions_per_minute, 2),
            "avg_latency_ms": round(self.avg_latency_ms, 2),
            "phase_switches_per_minute": round(self.switches_per_minute, 2),
            "emergency_count": self.emergency_count,
            "brts_count": self.brts_count,
            "fallback_count": self.fallback_count,
            "safety_violation_count": self.safety_violation_count,
            "prediction_mae": round(self.prediction_mae, 2),
            "prediction_rmse": round(self.prediction_rmse, 2),
            "effectiveness_rate": round(self.effectiveness_rate, 3),
            "effectiveness_sample_size": len(self._effectiveness_history),
        }


# ---------------------------------------------------------------------------
# Quick self-test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    ht = HealthTracker()

    # Simulate 10 decisions
    for i in range(10):
        phase = "NS_green" if i % 3 != 0 else "EW_green"
        ht.record_decision(
            phase=phase,
            cycle_sec=40,
            latency_ms=1.5 + i * 0.1,
            emergency=(i == 7),
            brts=(i == 5),
            queue_on_approach=20 - i,
        )
        ht.record_prediction("lane_NS_1", predicted_queue=15.0 + i)

    print("=== Controller Health Report ===")
    for k, v in ht.report().items():
        print(f"  {k:35s} = {v}")
