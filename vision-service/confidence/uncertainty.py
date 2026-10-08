"""
confidence/uncertainty.py — Uncertainty Propagation (Sections 71-73)
=====================================================================
Propagates perception uncertainty into traffic state for confidence-aware
signal optimization.

Q_effective = C_Q * Q
PCU_effective = C_P * PCU
P_safe(p) = E[P(p)] - λ√Var(P(p))

Also handles historical fallback blending when confidence is low.
"""

import logging
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)


class UncertaintyPropagator:
    """Propagates perception confidence into traffic state values.

    The signal optimizer should use confidence-weighted values rather
    than raw values, so that uncertain measurements don't cause
    extreme signal changes.

    Args:
        config: Dict with uncertainty propagation settings.
    """

    def __init__(self, config: Optional[dict] = None) -> None:
        cfg = config or {}
        self._lambda: float = cfg.get("risk_lambda", 1.0)
        self._cautious_threshold: float = cfg.get("cautious_threshold", 0.60)
        self._historical_blend_alpha: float = cfg.get("blend_alpha", 0.30)

        # Historical state for blending
        self._historical_state: dict[str, dict] = {}

    def apply_confidence(
        self,
        lane_id: str,
        queue_length: float,
        queue_confidence: float,
        pcu: float,
        pcu_confidence: float,
        avg_speed: float,
        speed_confidence: float,
    ) -> dict:
        """Apply confidence weighting to traffic state (Section 71).

        Args:
            lane_id: Lane identifier.
            queue_length: Estimated queue length in meters.
            queue_confidence: Queue confidence (0-1).
            pcu: PCU count.
            pcu_confidence: PCU confidence (0-1).
            avg_speed: Average speed in km/h.
            speed_confidence: Speed confidence (0-1).

        Returns:
            Dict with confidence-weighted traffic state.
        """
        q_eff = queue_length * queue_confidence
        pcu_eff = pcu * pcu_confidence
        speed_eff = avg_speed * speed_confidence

        return {
            "queue_length_m": round(queue_length, 2),
            "queue_effective_m": round(q_eff, 2),
            "queue_confidence": round(queue_confidence, 3),
            "pcu": round(pcu, 2),
            "pcu_effective": round(pcu_eff, 2),
            "pcu_confidence": round(pcu_confidence, 3),
            "avg_speed_kmph": round(avg_speed, 2),
            "speed_effective_kmph": round(speed_eff, 2),
            "speed_confidence": round(speed_confidence, 3),
        }

    def compute_risk_aware_pressure(
        self,
        expected_pressure: float,
        pressure_variance: float,
    ) -> float:
        """Compute risk-aware pressure (Section 72).

        P_safe(p) = E[P(p)] - λ√Var(P(p))

        This prevents a noisy camera from causing extreme signal changes.
        High uncertainty → more conservative pressure estimate.

        Args:
            expected_pressure: Expected pressure value.
            pressure_variance: Variance of the pressure estimate.

        Returns:
            Risk-aware (conservative) pressure value.
        """
        if pressure_variance < 0:
            pressure_variance = 0.0

        safe_pressure = (
            expected_pressure - self._lambda * np.sqrt(pressure_variance)
        )
        return float(max(0.0, safe_pressure))

    def blend_with_historical(
        self,
        lane_id: str,
        current_state: dict,
        scene_confidence: float,
    ) -> dict:
        """Blend current state with historical when confidence is low (Section 73).

        When scene_confidence < threshold, gradually blend toward
        historical average to prevent erratic behavior.

        Args:
            lane_id: Lane identifier.
            current_state: Current traffic state dict.
            scene_confidence: Overall scene confidence.

        Returns:
            Blended traffic state dict.
        """
        # Update historical state
        if lane_id not in self._historical_state:
            self._historical_state[lane_id] = dict(current_state)
            return current_state

        historical = self._historical_state[lane_id]

        if scene_confidence >= self._cautious_threshold:
            # High confidence — use current, update historical
            self._historical_state[lane_id] = dict(current_state)
            return current_state

        # Low confidence — blend
        blend = self._historical_blend_alpha
        # Scale blending by how far below threshold we are
        confidence_ratio = scene_confidence / self._cautious_threshold
        effective_blend = blend * confidence_ratio  # Less blending when very low

        blended = {}
        for key in current_state:
            curr_val = current_state[key]
            hist_val = historical.get(key, curr_val)

            if isinstance(curr_val, (int, float)) and isinstance(hist_val, (int, float)):
                blended[key] = (
                    effective_blend * curr_val
                    + (1 - effective_blend) * hist_val
                )
            else:
                blended[key] = curr_val

        # Update historical with blended (slow adaptation)
        self._historical_state[lane_id] = dict(blended)

        logger.debug(
            f"Lane {lane_id}: confidence={scene_confidence:.2f} < "
            f"{self._cautious_threshold}, blending with historical "
            f"(α={effective_blend:.2f})"
        )

        return blended

    def estimate_pressure_variance(
        self,
        queue_length: float,
        queue_confidence: float,
        pcu: float,
        pcu_confidence: float,
    ) -> float:
        """Estimate variance of the pressure signal.

        Higher uncertainty in inputs → higher pressure variance.

        Args:
            queue_length: Queue length.
            queue_confidence: Queue confidence.
            pcu: PCU count.
            pcu_confidence: PCU confidence.

        Returns:
            Estimated variance of the pressure signal.
        """
        # Variance inversely related to confidence
        q_var = queue_length * (1 - queue_confidence)
        p_var = pcu * (1 - pcu_confidence)

        return float(q_var ** 2 + p_var ** 2)
