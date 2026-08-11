"""
confidence.py — Sensor Confidence Scoring (Weather / Visibility Awareness)
===========================================================================
Combines Person A's per-event detection confidence with a weather multiplier
to produce a single ``confidence`` score in [0, 1].

When confidence drops below CONFIDENCE_THRESHOLD the max-pressure algorithm
should:
  - Cap how much the recommended cycle time can change in one step.
  - Blend live density with a historical average (weight historical more as
    confidence falls): ``final = conf * live + (1 - conf) * historical``.

The confidence value is always forwarded to the output contract so the
dashboard can show an "acting cautiously" badge.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Weather multipliers — multiply raw detection confidence by this factor
# before clamping to [0, 1].
# ---------------------------------------------------------------------------
WEATHER_MULTIPLIERS: dict[str, float] = {
    "clear":   1.0,
    "cloudy":  0.95,
    "rain":    0.75,
    "fog":     0.65,
    "snow":    0.60,
    "night":   0.80,
    "glare":   0.70,
}

# If confidence falls below this value, enter cautious mode.
CONFIDENCE_THRESHOLD: float = 0.60

# Maximum cycle-time change (seconds) when in cautious mode.
MAX_DELTA_CAUTIOUS: float = 8.0  # seconds


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def compute_confidence(
    detection_confidence: float,
    weather_flag: str = "clear",
) -> float:
    """Return a blended confidence score in ``[0, 1]``.

    Parameters
    ----------
    detection_confidence:
        Raw detection confidence reported by Person A's CV pipeline (0–1).
    weather_flag:
        Current weather condition string.  Unknown values are treated as
        ``"clear"`` (no additional penalty).

    Returns
    -------
    float
        Confidence score clamped to ``[0, 1]``.
    """
    multiplier = WEATHER_MULTIPLIERS.get(weather_flag.lower(), 1.0)
    score = detection_confidence * multiplier
    return float(max(0.0, min(1.0, score)))


def blend_density(
    live_density: float,
    historical_density: float,
    confidence: float,
) -> float:
    """Blend live and historical density readings.

    ``final = confidence * live + (1 - confidence) * historical``

    As confidence approaches 0 the system relies entirely on historical
    averages; at confidence 1 it trusts the live reading fully.

    Parameters
    ----------
    live_density:
        Current per-lane vehicle density reported by Person A.
    historical_density:
        Historical average density for the same junction / time-of-day.
    confidence:
        Score from :func:`compute_confidence`.

    Returns
    -------
    float
        Blended density value.
    """
    return confidence * live_density + (1.0 - confidence) * historical_density


def cap_cycle_delta(
    proposed_delta: float,
    confidence: float,
    max_delta_cautious: float = MAX_DELTA_CAUTIOUS,
) -> float:
    """Clamp the proposed cycle-time change when in cautious mode.

    Parameters
    ----------
    proposed_delta:
        The cycle-time change (in seconds) computed by the max-pressure
        algorithm before any confidence adjustment.
    confidence:
        Score from :func:`compute_confidence`.
    max_delta_cautious:
        Absolute cap on the delta when confidence is below threshold.

    Returns
    -------
    float
        Possibly capped delta (same sign preserved).
    """
    if confidence < CONFIDENCE_THRESHOLD:
        sign = 1.0 if proposed_delta >= 0 else -1.0
        return sign * min(abs(proposed_delta), max_delta_cautious)
    return proposed_delta


def is_cautious(confidence: float) -> bool:
    """Return ``True`` if the system should operate in cautious mode."""
    return confidence < CONFIDENCE_THRESHOLD


# ---------------------------------------------------------------------------
# Quick self-test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    conf = compute_confidence(0.80, "rain")
    print(f"Confidence (rain, 0.80): {conf:.3f}")          # ~0.60
    blended = blend_density(20.0, 12.0, conf)
    print(f"Blended density:         {blended:.2f}")
    delta = cap_cycle_delta(15.0, conf)
    print(f"Capped delta:            {delta:.1f}s")         # 8.0
