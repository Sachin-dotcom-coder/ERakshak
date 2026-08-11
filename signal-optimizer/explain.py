"""
explain.py — Quantitative Decision Reasoning Generator
========================================================
Every signal decision carries a plain-English ``reason`` string built from the
same variables that fed the decision — not computed separately, so it always
matches the actual logic.

Enhanced with quantitative explanations including exact pressure scores,
growth rates, predicted values, starvation times, and downstream penalties.

Improvement #41 from new_instruct.md.
"""

from __future__ import annotations

from typing import Optional

from confidence import CONFIDENCE_THRESHOLD
from prediction import TrendLabel
from priority import PriorityResult


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def build_reason(
    # --- Max-pressure inputs ---
    dominant_approach: str,
    dominant_queue: int,
    secondary_approach: str,
    secondary_queue: int,
    recommended_cycle_sec: int,
    # --- Confidence ---
    confidence: float,
    weather_flag: str = "clear",
    cycle_delta_sec: Optional[float] = None,
    # --- Prediction ---
    trend: TrendLabel = "stable",
    predicted_extra_vehicles: Optional[float] = None,
    # --- Priority ---
    priority: Optional[PriorityResult] = None,
    # --- Enhanced: quantitative details (Improvement #41) ---
    pressure_scores: Optional[dict[str, float]] = None,
    growth_rates: Optional[dict[str, float]] = None,
    starvation_sec: Optional[dict[str, float]] = None,
    decision_confidence: Optional[float] = None,
    anomaly_level: Optional[str] = None,
    downstream_penalty: Optional[float] = None,
    prediction_uncertainty: Optional[float] = None,
) -> tuple[str, list[str]]:
    """Generate the headline reason string and a list of all contributing factors.

    Returns
    -------
    (headline_reason, all_factors)
        ``headline_reason`` is the single string for the ``reason`` field of
        the output contract.
        ``all_factors`` is the ordered list of all reasons that applied,
        highest priority first.
    """
    factors: list[str] = []
    pr = priority or PriorityResult()

    # 1. Emergency vehicle
    if pr.emergency_triggered and pr.emergency_approach:
        msg = (
            f"Emergency vehicle detected on {pr.emergency_approach} approach; "
            f"forced green corridor for {pr.emergency_hold_sec:.0f}s."
        )
        if pr.emergency_eta_sec is not None:
            msg += f" ETA to downstream junction: {pr.emergency_eta_sec:.0f}s."
        factors.append(msg)

    # 2. BRTS priority
    if pr.brts_triggered and pr.brts_approach and not pr.emergency_triggered:
        msg = (
            f"BRTS bus priority given on {pr.brts_approach} approach "
            f"(pressure boosted by {pr.brts_pressure_boost:.2f})."
        )
        factors.append(msg)

    # 3. Anomaly detection
    if anomaly_level and anomaly_level != "normal":
        msg = f"Traffic anomaly detected: {anomaly_level.replace('_', ' ')} level."
        factors.append(msg)

    # 4. Confidence / weather caution
    if confidence < CONFIDENCE_THRESHOLD:
        delta_str = ""
        if cycle_delta_sec is not None:
            sign = "+" if cycle_delta_sec >= 0 else ""
            delta_str = f" — change capped at {sign}{cycle_delta_sec:.0f}s"
        msg = (
            f"Confidence lowered to {confidence:.2f} due to {weather_flag}{delta_str}; "
            f"acting cautiously."
        )
        factors.append(msg)

    # 5. Rising congestion prediction (quantitative)
    if trend == "rising":
        growth_str = ""
        if growth_rates and dominant_approach in growth_rates:
            gr = growth_rates[dominant_approach]
            growth_str = f", rising at {gr:+.1f} veh/sample"
        pred_str = ""
        if predicted_extra_vehicles is not None:
            pred_str = f", predicted +{predicted_extra_vehicles:.0f} vehicles in ~5 min"
        uncert_str = ""
        if prediction_uncertainty is not None and prediction_uncertainty > 0:
            uncert_str = f" (±{prediction_uncertainty:.1f})"
        msg = (
            f"Queue trend rising on {dominant_approach}"
            f"{growth_str}{pred_str}{uncert_str}; green extended pre-emptively."
        )
        factors.append(msg)

    # 6. Starvation warning
    if starvation_sec:
        for phase_name, starv_time in starvation_sec.items():
            if starv_time > 60:
                factors.append(
                    f"Phase {phase_name} starved for {starv_time:.0f}s; "
                    f"fairness bonus applied."
                )

    # 7. Downstream congestion
    if downstream_penalty is not None and downstream_penalty > 0.5:
        factors.append(
            f"Downstream congestion detected (penalty {downstream_penalty:.1f}); "
            f"spillback protection active."
        )

    # 8. Baseline max-pressure (always included, now quantitative)
    pressure_detail = ""
    if pressure_scores:
        scores_str = ", ".join(
            f"{k}={v:.1f}" for k, v in sorted(pressure_scores.items(), key=lambda x: -x[1])
        )
        pressure_detail = f" Pressure scores: [{scores_str}]."
    factors.append(
        f"{dominant_approach} approach queue ({dominant_queue} vehicles) exceeds "
        f"{secondary_approach} ({secondary_queue} vehicles); "
        f"cycle set to {recommended_cycle_sec}s.{pressure_detail}"
    )

    # 9. Decision confidence footer
    if decision_confidence is not None:
        factors.append(f"Decision confidence: {decision_confidence:.2f}.")

    headline = factors[0] if factors else "Normal operation."
    return headline, factors


def reason_string(
    *,
    dominant_approach: str,
    dominant_queue: int,
    secondary_approach: str,
    secondary_queue: int,
    recommended_cycle_sec: int,
    confidence: float,
    weather_flag: str = "clear",
    cycle_delta_sec: Optional[float] = None,
    trend: TrendLabel = "stable",
    predicted_extra_vehicles: Optional[float] = None,
    priority: Optional[PriorityResult] = None,
    **kwargs,
) -> str:
    """Convenience wrapper that returns only the headline reason string."""
    headline, _ = build_reason(
        dominant_approach=dominant_approach,
        dominant_queue=dominant_queue,
        secondary_approach=secondary_approach,
        secondary_queue=secondary_queue,
        recommended_cycle_sec=recommended_cycle_sec,
        confidence=confidence,
        weather_flag=weather_flag,
        cycle_delta_sec=cycle_delta_sec,
        trend=trend,
        predicted_extra_vehicles=predicted_extra_vehicles,
        priority=priority,
        **kwargs,
    )
    return headline


# ---------------------------------------------------------------------------
# Quick self-test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    from priority import PriorityResult

    # Quantitative max-pressure scenario
    h, factors = build_reason(
        dominant_approach="NS",
        dominant_queue=22,
        secondary_approach="EW",
        secondary_queue=8,
        recommended_cycle_sec=42,
        confidence=0.62,
        weather_flag="rain",
        cycle_delta_sec=8.0,
        trend="rising",
        predicted_extra_vehicles=6.0,
        pressure_scores={"NS_green": 31.4, "EW_green": 14.2},
        growth_rates={"NS": 4.2, "EW": 0.4},
        starvation_sec={"NS_green": 5, "EW_green": 65},
        decision_confidence=0.78,
        anomaly_level="elevated",
        prediction_uncertainty=2.3,
    )
    print("Headline:", h)
    print("\nAll factors:")
    for f in factors:
        print(" -", f)

    # Emergency scenario with ETA
    pr = PriorityResult(
        emergency_triggered=True,
        emergency_approach="north",
        emergency_hold_sec=15.0,
        emergency_eta_sec=12.5,
    )
    h2, _ = build_reason(
        dominant_approach="NS",
        dominant_queue=10,
        secondary_approach="EW",
        secondary_queue=4,
        recommended_cycle_sec=45,
        confidence=0.90,
        priority=pr,
    )
    print("\nEmergency headline:", h2)
