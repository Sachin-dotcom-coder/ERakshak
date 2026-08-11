"""
explain.py — Decision Reasoning Generator
==========================================
Every signal decision carries a plain-English ``reason`` string built from the
same variables that fed the decision — not computed separately, so it always
matches the actual logic.

Priority order for the headline reason (most urgent first):
  1. Emergency vehicle
  2. BRTS priority
  3. Confidence / weather caution
  4. Prediction (rising trend)
  5. Baseline max-pressure

All contributing factors are also collected so Person D can show detail.
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
        factors.append(msg)

    # 2. BRTS priority
    if pr.brts_triggered and pr.brts_approach and not pr.emergency_triggered:
        msg = (
            f"BRTS bus priority given on {pr.brts_approach} approach "
            f"(pressure boosted by {pr.brts_pressure_boost:.1f})."
        )
        factors.append(msg)

    # 3. Confidence / weather caution
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

    # 4. Rising congestion prediction
    if trend == "rising" and predicted_extra_vehicles is not None:
        msg = (
            f"Queue trend rising (predicted +{predicted_extra_vehicles:.0f} vehicles "
            f"in ~5 min on {dominant_approach}); green extended pre-emptively."
        )
        factors.append(msg)
    elif trend == "rising":
        factors.append(
            f"Queue trend rising on {dominant_approach}; green extended pre-emptively."
        )

    # 5. Baseline max-pressure (always included)
    factors.append(
        f"{dominant_approach} approach queue ({dominant_queue} vehicles) exceeds "
        f"{secondary_approach} ({secondary_queue} vehicles); "
        f"cycle set to {recommended_cycle_sec}s."
    )

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
    )
    return headline


# ---------------------------------------------------------------------------
# Quick self-test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    from priority import PriorityResult

    # Normal max-pressure scenario
    h, factors = build_reason(
        dominant_approach="NS",
        dominant_queue=14,
        secondary_approach="EW",
        secondary_queue=5,
        recommended_cycle_sec=38,
        confidence=0.62,
        weather_flag="rain",
        cycle_delta_sec=8.0,
        trend="rising",
        predicted_extra_vehicles=6.0,
    )
    print("Headline:", h)
    print("All factors:")
    for f in factors:
        print(" -", f)

    # Emergency scenario
    pr = PriorityResult(
        emergency_triggered=True,
        emergency_approach="north",
        emergency_hold_sec=15.0,
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
