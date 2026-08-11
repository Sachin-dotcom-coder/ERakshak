"""
priority.py — BRTS Bus Priority + Emergency Vehicle Priority
=============================================================
Two related priority mechanisms that share the same "interrupt the normal
cycle" pathway.  Emergency **always** outranks BRTS.

Enhanced with:
  - Smooth BRTS priority function (continuous ramp instead of hard threshold)
  - Emergency ETA estimation for downstream junction preparation

Improvements #27, #28 from new_instruct.md.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional

from controller_config import ControllerConfig, get_config

# ---------------------------------------------------------------------------
# Legacy constants (kept for backward compat; actual values come from config)
# ---------------------------------------------------------------------------
BRTS_WAIT_THRESHOLD_SEC: float = 20.0
BRTS_PRESSURE_BOOST: float = 3.0
EMERGENCY_HOLD_SEC: float = 15.0


# ---------------------------------------------------------------------------
# Data classes (mirrors Person A's event contract extension)
# ---------------------------------------------------------------------------

@dataclass
class BRTSEvent:
    """BRTS bus waiting at a junction approach."""
    approach: str
    lane_id: str
    wait_time_sec: float
    brts_waiting: bool = True


@dataclass
class EmergencyEvent:
    """Emergency vehicle detected by Person A's CV pipeline."""
    detected: bool
    approach: str
    lane_id: str
    vehicle_speed_mps: Optional[float] = None


# ---------------------------------------------------------------------------
# Priority evaluator
# ---------------------------------------------------------------------------

@dataclass
class PriorityResult:
    """Outcome of a priority evaluation pass."""
    emergency_triggered: bool = False
    emergency_approach: Optional[str] = None
    emergency_hold_sec: float = EMERGENCY_HOLD_SEC
    emergency_eta_sec: Optional[float] = None  # ETA to downstream junction

    brts_triggered: bool = False
    brts_approach: Optional[str] = None
    brts_pressure_boost: float = 0.0

    cascade_approaches: list[str] = field(default_factory=list)

    @property
    def any_triggered(self) -> bool:
        return self.emergency_triggered or self.brts_triggered


def _smooth_brts_bonus(
    wait_time_sec: float,
    config: Optional[ControllerConfig] = None,
) -> float:
    """Compute a smooth, continuous BRTS pressure bonus.

    Instead of a hard threshold at 20s, the bonus ramps smoothly:
      - wait < start_sec  → 0
      - wait = full_sec   → max_bonus
      - Intermediate      → smooth interpolation (sigmoid-like ramp)

    Improvement #28 from new_instruct.md.
    """
    cfg = config or get_config()
    start = cfg.brts_smooth_start_sec
    full = cfg.brts_smooth_full_sec
    max_bonus = cfg.brts_max_bonus

    if wait_time_sec <= start:
        return 0.0
    if wait_time_sec >= full:
        return max_bonus

    # Smooth ramp using a scaled sigmoid-like function
    progress = (wait_time_sec - start) / (full - start)  # 0 → 1
    # Use a smooth step: 3x² - 2x³ (Hermite interpolation)
    smooth = progress * progress * (3.0 - 2.0 * progress)
    return max_bonus * smooth


def evaluate_priority(
    emergency_event: Optional[EmergencyEvent] = None,
    brts_event: Optional[BRTSEvent] = None,
    junction_path: Optional[list[str]] = None,
    config: Optional[ControllerConfig] = None,
) -> PriorityResult:
    """Evaluate BRTS and emergency priority for a single decision cycle.

    Emergency always wins.  If both are triggered at the same junction:
      - Emergency gets the immediate green.
      - BRTS boost is deferred to the *next* cycle.
    """
    cfg = config or get_config()
    result = PriorityResult()

    # --- Emergency override (highest priority) ---
    if emergency_event and emergency_event.detected:
        result.emergency_triggered = True
        result.emergency_approach = emergency_event.approach

        # Estimate hold time from speed if available
        if emergency_event.vehicle_speed_mps and emergency_event.vehicle_speed_mps > 0:
            # Junction crossing distance ~ 30 m
            result.emergency_hold_sec = max(
                cfg.emergency_hold_sec,
                30.0 / emergency_event.vehicle_speed_mps,
            )
            # ETA estimation for downstream junctions (Improvement #27)
            result.emergency_eta_sec = (
                cfg.emergency_approach_distance_m / emergency_event.vehicle_speed_mps
            )
        else:
            result.emergency_hold_sec = cfg.emergency_hold_sec
            result.emergency_eta_sec = None

        # Cascade along declared path
        if junction_path:
            result.cascade_approaches = list(junction_path)

    # --- BRTS smooth priority (Improvement #28) ---
    if (
        brts_event
        and brts_event.brts_waiting
        and not result.emergency_triggered
    ):
        bonus = _smooth_brts_bonus(brts_event.wait_time_sec, cfg)
        if bonus > 0:
            result.brts_triggered = True
            result.brts_approach = brts_event.approach
            result.brts_pressure_boost = bonus

    return result


def apply_brts_boost(
    pressure_scores: dict[str, float],
    priority: PriorityResult,
) -> dict[str, float]:
    """Add the BRTS pressure boost to the relevant approach's score.

    Returns a *new* dict so the original is not mutated.
    """
    if not priority.brts_triggered or priority.brts_approach is None:
        return pressure_scores
    updated = dict(pressure_scores)
    approach = priority.brts_approach
    updated[approach] = updated.get(approach, 0.0) + priority.brts_pressure_boost
    return updated


# ---------------------------------------------------------------------------
# Quick self-test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Smooth BRTS bonus curve
    print("=== Smooth BRTS Bonus Curve ===")
    for wait in [0, 5, 10, 15, 20, 25, 30, 35, 40, 50, 60, 70]:
        bonus = _smooth_brts_bonus(float(wait))
        bar = "#" * int(bonus * 10)
        print(f"  wait={wait:3d}s  bonus={bonus:.3f}  {bar}")

    # Emergency with ETA
    ev = EmergencyEvent(detected=True, approach="north", lane_id="lane_1",
                        vehicle_speed_mps=12.0)
    brts = BRTSEvent(approach="north", lane_id="lane_brts_N", wait_time_sec=40.0)
    res = evaluate_priority(emergency_event=ev, brts_event=brts)

    print(f"\nEmergency triggered : {res.emergency_triggered}")
    print(f"Emergency approach  : {res.emergency_approach}")
    print(f"Emergency hold (s)  : {res.emergency_hold_sec:.1f}")
    print(f"Emergency ETA (s)   : {res.emergency_eta_sec:.1f}")
    print(f"BRTS triggered      : {res.brts_triggered}")  # False — emergency wins

    # BRTS only — smooth curve
    res2 = evaluate_priority(
        brts_event=BRTSEvent(approach="east", lane_id="lane_brts_E", wait_time_sec=35.0)
    )
    print(f"\nBRTS only: triggered={res2.brts_triggered} "
          f"bonus={res2.brts_pressure_boost:.3f}")

    scores = {"north": 5.0, "east": 3.0, "south": 2.0, "west": 1.0}
    boosted = apply_brts_boost(scores, res2)
    print(f"Boosted scores: {boosted}")
