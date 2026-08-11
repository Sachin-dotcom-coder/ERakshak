"""
confidence.py — Sensor Confidence Scoring (Weather / Visibility Awareness)
===========================================================================
Combines Person A's per-event detection confidence with a weather multiplier
to produce a single ``confidence`` score in [0, 1].

Enhanced with:
  - Confidence bands (normal / cautious / smoothed / fallback)
  - Confidence-weighted EMA alpha
  - Adaptive hysteresis threshold
  - Decision confidence computation

Improvements #22, #24, #25, #33 from new_instruct.md.
"""

from __future__ import annotations

from typing import Optional

from controller_config import ControllerConfig, get_config

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

# Legacy constants kept for backward compatibility
CONFIDENCE_THRESHOLD: float = 0.60
MAX_DELTA_CAUTIOUS: float = 8.0


# ---------------------------------------------------------------------------
# Confidence band labels
# ---------------------------------------------------------------------------

def confidence_band(confidence: float, config: Optional[ControllerConfig] = None) -> str:
    """Classify confidence into a named band.

    Returns one of: ``"normal"``, ``"cautious"``, ``"smoothed"``, ``"fallback"``.
    """
    cfg = config or get_config()
    if confidence >= cfg.confidence_normal:
        return "normal"
    elif confidence >= cfg.confidence_cautious:
        return "cautious"
    elif confidence >= cfg.confidence_smoothed:
        return "smoothed"
    else:
        return "fallback"


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
# Enhanced: Confidence-weighted smoothing alpha (Improvement #24)
# ---------------------------------------------------------------------------

def confidence_weighted_alpha(
    confidence: float,
    config: Optional[ControllerConfig] = None,
) -> float:
    """Return the EMA smoothing alpha adjusted for sensor confidence.

    High confidence → high α (react quickly to new data).
    Low  confidence → low  α (smooth aggressively, trust history).
    """
    cfg = config or get_config()
    band = confidence_band(confidence, cfg)
    if band == "normal":
        return cfg.smoothing_alpha_high_conf
    elif band == "cautious":
        return cfg.smoothing_alpha
    elif band == "smoothed":
        # Linear interpolation between low and base
        return (cfg.smoothing_alpha_low_conf + cfg.smoothing_alpha) / 2
    else:  # fallback
        return cfg.smoothing_alpha_low_conf


# ---------------------------------------------------------------------------
# Enhanced: Adaptive hysteresis (Improvement #25)
# ---------------------------------------------------------------------------

def adaptive_hysteresis(
    confidence: float,
    config: Optional[ControllerConfig] = None,
) -> float:
    """Return the hysteresis threshold adjusted for sensor confidence.

    Low confidence → higher threshold (don't let noise trigger switches).
    High confidence → lower threshold (react to genuine changes).
    """
    cfg = config or get_config()
    band = confidence_band(confidence, cfg)
    if band == "normal":
        return cfg.hysteresis_high_conf
    elif band in ("cautious", "smoothed"):
        return cfg.hysteresis_threshold
    else:  # fallback
        return cfg.hysteresis_low_conf


# ---------------------------------------------------------------------------
# Enhanced: Decision confidence (Improvement #33)
# ---------------------------------------------------------------------------

def compute_decision_confidence(
    sensor_confidence: float,
    pressure_margin: float,
    max_possible_pressure: float = 50.0,
    prediction_agreement: float = 1.0,
    historical_agreement: float = 1.0,
    config: Optional[ControllerConfig] = None,
) -> float:
    """Compute an overall decision confidence score.

    Combines sensor confidence, pressure margin (how decisive is the choice),
    prediction agreement (do predictors agree), and historical agreement
    (does the decision align with historical patterns).

    Parameters
    ----------
    pressure_margin:
        Absolute difference between best and second-best phase pressure.
    max_possible_pressure:
        Normalizer for pressure margin (default 50).
    prediction_agreement:
        0–1 score: 1 = all predictors agree, 0 = complete disagreement.
    historical_agreement:
        0–1 score: 1 = decision aligns with historical patterns.

    Returns
    -------
    float
        Decision confidence in [0, 1].
    """
    cfg = config or get_config()

    # Normalize pressure margin to [0, 1]
    margin_score = min(1.0, pressure_margin / max_possible_pressure) if max_possible_pressure > 0 else 0.0

    decision_conf = (
        cfg.decision_conf_sensor_weight * sensor_confidence
        + cfg.decision_conf_margin_weight * margin_score
        + cfg.decision_conf_prediction_weight * prediction_agreement
        + cfg.decision_conf_historical_weight * historical_agreement
    )
    return float(max(0.0, min(1.0, decision_conf)))


# ---------------------------------------------------------------------------
# Quick self-test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Basic confidence
    conf = compute_confidence(0.80, "rain")
    print(f"Confidence (rain, 0.80): {conf:.3f}")          # ~0.60
    print(f"Band: {confidence_band(conf)}")

    # Blending
    blended = blend_density(20.0, 12.0, conf)
    print(f"Blended density:         {blended:.2f}")

    # Delta capping
    delta = cap_cycle_delta(15.0, conf)
    print(f"Capped delta:            {delta:.1f}s")         # 8.0

    # Enhanced features
    print(f"\nSmoothing alpha (conf={conf:.2f}): {confidence_weighted_alpha(conf):.3f}")
    print(f"Hysteresis threshold:              {adaptive_hysteresis(conf):.1f}")

    # Decision confidence
    dc = compute_decision_confidence(
        sensor_confidence=conf,
        pressure_margin=15.0,
        prediction_agreement=0.8,
        historical_agreement=0.9,
    )
    print(f"Decision confidence:               {dc:.3f}")

    # High confidence scenario
    print("\n--- High confidence scenario ---")
    hc = compute_confidence(0.95, "clear")
    print(f"Confidence: {hc:.3f}, Band: {confidence_band(hc)}")
    print(f"Smoothing alpha: {confidence_weighted_alpha(hc):.3f}")
    print(f"Hysteresis: {adaptive_hysteresis(hc):.1f}")
