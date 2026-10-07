"""
traffic_state/shockwave.py — Queue Shockwave Propagation Analysis (Section 44)
================================================================================
Tracks queue growth dynamics over time and detects shockwave events.

A shockwave occurs when a queue starts growing rapidly (positive growth rate
with increasing acceleration), indicating a phase of rapid congestion buildup.
"""

import logging
import time
from collections import deque
from enum import Enum
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)


class ShockwaveState(str, Enum):
    STABLE = "stable"
    GROWING = "growing"
    ACCELERATING = "accelerating"  # Shockwave detected
    DISSIPATING = "dissipating"
    SPILLBACK_RISK = "spillback_risk"


class ShockwaveAnalyzer:
    """Queue shockwave propagation analysis and risk scoring.

    Monitors queue growth rate and acceleration over time to detect
    shockwave events and predict spillback risk.

    Args:
        config: Dict with shockwave detection settings.
    """

    def __init__(self, config: Optional[dict] = None) -> None:
        cfg = config or {}
        self._growth_threshold: float = cfg.get("growth_threshold_m_per_s", 0.5)
        self._accel_threshold: float = cfg.get("accel_threshold", 0.1)
        self._dissipation_threshold: float = cfg.get("dissipation_threshold", -0.3)
        self._history_seconds: int = cfg.get("history_seconds", 120)

        # Per-lane state
        self._states: dict[str, ShockwaveState] = {}
        self._growth_history: dict[str, deque] = {}
        self._accel_history: dict[str, deque] = {}

    def update(
        self,
        lane_id: str,
        queue_length: float,
        growth_rate: float,
        acceleration: float,
        spillback_time: Optional[float] = None,
    ) -> dict:
        """Update shockwave analysis for a lane.

        Args:
            lane_id: Lane identifier.
            queue_length: Current queue length in meters.
            growth_rate: Queue growth rate (m/s).
            acceleration: Queue acceleration (m/s²).
            spillback_time: Predicted time to spillback (seconds).

        Returns:
            Dict with shockwave state, risk score, and dynamics.
        """
        now = time.time()

        # Track history
        if lane_id not in self._growth_history:
            self._growth_history[lane_id] = deque(maxlen=self._history_seconds)
            self._accel_history[lane_id] = deque(maxlen=self._history_seconds)

        self._growth_history[lane_id].append((now, growth_rate))
        self._accel_history[lane_id].append((now, acceleration))

        # Classify shockwave state
        state = self._classify_state(
            growth_rate, acceleration, spillback_time
        )
        prev_state = self._states.get(lane_id, ShockwaveState.STABLE)
        self._states[lane_id] = state

        if state != prev_state:
            logger.info(
                f"Lane {lane_id} shockwave: {prev_state.value} → {state.value} "
                f"(growth={growth_rate:.3f} m/s, accel={acceleration:.4f} m/s²)"
            )

        # Risk score
        risk = self._compute_risk_score(
            growth_rate, acceleration, queue_length, spillback_time
        )

        return {
            "state": state.value,
            "growth_rate_m_per_s": round(growth_rate, 4),
            "acceleration_m_per_s2": round(acceleration, 5),
            "risk_score": round(risk, 3),
            "spillback_time_s": (
                round(spillback_time, 1) if spillback_time is not None else None
            ),
        }

    def _classify_state(
        self,
        growth: float,
        accel: float,
        spillback_time: Optional[float],
    ) -> ShockwaveState:
        """Classify the shockwave state."""
        if spillback_time is not None and spillback_time < 30:
            return ShockwaveState.SPILLBACK_RISK

        if growth > self._growth_threshold and accel > self._accel_threshold:
            return ShockwaveState.ACCELERATING

        if growth > self._growth_threshold:
            return ShockwaveState.GROWING

        if growth < self._dissipation_threshold:
            return ShockwaveState.DISSIPATING

        return ShockwaveState.STABLE

    def _compute_risk_score(
        self,
        growth: float,
        accel: float,
        queue_length: float,
        spillback_time: Optional[float],
    ) -> float:
        """Compute a 0-1 risk score for the queue."""
        # Growth contribution
        growth_risk = min(1.0, max(0.0, growth / 2.0))

        # Acceleration contribution
        accel_risk = min(1.0, max(0.0, accel / 0.5))

        # Length contribution (longer queues are inherently riskier)
        length_risk = min(1.0, queue_length / 100.0)

        # Spillback urgency
        spillback_risk = 0.0
        if spillback_time is not None:
            if spillback_time < 10:
                spillback_risk = 1.0
            elif spillback_time < 60:
                spillback_risk = 1.0 - spillback_time / 60.0

        risk = (
            0.25 * growth_risk
            + 0.25 * accel_risk
            + 0.20 * length_risk
            + 0.30 * spillback_risk
        )

        return float(np.clip(risk, 0.0, 1.0))

    def get_state(self, lane_id: str) -> ShockwaveState:
        """Get current shockwave state for a lane."""
        return self._states.get(lane_id, ShockwaveState.STABLE)
