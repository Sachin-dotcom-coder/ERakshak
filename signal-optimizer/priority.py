"""
priority.py — BRTS Bus Priority + Emergency Vehicle Priority
=============================================================
Two related priority mechanisms that share the same "interrupt the normal
cycle" pathway.  Emergency **always** outranks BRTS.

BRTS Priority
-------------
When a BRTS bus has been waiting beyond BRTS_WAIT_THRESHOLD_SEC, boost
that approach's pressure score so its green comes sooner — this is a *bias*,
not a hard override (avoids stranding cross-traffic).

Emergency Priority
------------------
When Person A detects an emergency vehicle, this module signals a **full
green override** for that approach.  The override holds for
EMERGENCY_HOLD_SEC then hands back to the normal adaptive cycle.

For multi-junction (green_wave.py) use, this module also provides the list
of junctions that should receive the cascaded green corridor.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

# ---------------------------------------------------------------------------
# Tuning constants
# ---------------------------------------------------------------------------
BRTS_WAIT_THRESHOLD_SEC: float = 20.0   # seconds waiting before BRTS boost
BRTS_PRESSURE_BOOST: float = 3.0        # additive pressure boost per cycle
EMERGENCY_HOLD_SEC: float = 15.0        # seconds to hold emergency green


# ---------------------------------------------------------------------------
# Data classes (mirrors Person A's event contract extension)
# ---------------------------------------------------------------------------

@dataclass
class BRTSEvent:
    """BRTS bus waiting at a junction approach."""
    approach: str            # e.g. "north", "south", "east", "west"
    lane_id: str             # e.g. "lane_brts_N"
    wait_time_sec: float     # how long the bus has been waiting
    brts_waiting: bool = True


@dataclass
class EmergencyEvent:
    """Emergency vehicle detected by Person A's CV pipeline."""
    detected: bool
    approach: str            # e.g. "north"
    lane_id: str             # e.g. "lane_1"
    vehicle_speed_mps: Optional[float] = None  # optional, for hold-time estimate


# ---------------------------------------------------------------------------
# Priority evaluator
# ---------------------------------------------------------------------------

@dataclass
class PriorityResult:
    """Outcome of a priority evaluation pass."""
    emergency_triggered: bool = False
    emergency_approach: Optional[str] = None
    emergency_hold_sec: float = EMERGENCY_HOLD_SEC

    brts_triggered: bool = False
    brts_approach: Optional[str] = None
    brts_pressure_boost: float = 0.0   # added to that approach's pressure score

    # Which approaches should receive a cascaded green in green_wave.py
    cascade_approaches: list[str] = field(default_factory=list)

    @property
    def any_triggered(self) -> bool:
        return self.emergency_triggered or self.brts_triggered


def evaluate_priority(
    emergency_event: Optional[EmergencyEvent] = None,
    brts_event: Optional[BRTSEvent] = None,
    junction_path: Optional[list[str]] = None,
) -> PriorityResult:
    """Evaluate BRTS and emergency priority for a single decision cycle.

    Emergency always wins.  If both are triggered at the same junction:
      - Emergency gets the immediate green.
      - BRTS boost is deferred to the *next* cycle (handled in max_pressure.py
        by checking ``PriorityResult.brts_triggered`` only when
        ``emergency_triggered`` is False).

    Parameters
    ----------
    emergency_event:
        Detection from Person A (``None`` if no emergency vehicle present).
    brts_event:
        BRTS status from Person A (``None`` if no bus waiting or below
        threshold).
    junction_path:
        Ordered list of junction IDs along the emergency vehicle's expected
        route (for cascade in ``green_wave.py``).  May be ``None``.

    Returns
    -------
    PriorityResult
    """
    result = PriorityResult()

    # --- Emergency override (highest priority) ---
    if emergency_event and emergency_event.detected:
        result.emergency_triggered = True
        result.emergency_approach = emergency_event.approach

        # Estimate hold time from speed if available
        if emergency_event.vehicle_speed_mps and emergency_event.vehicle_speed_mps > 0:
            # Rough junction crossing distance = 30 m
            result.emergency_hold_sec = max(
                EMERGENCY_HOLD_SEC,
                30.0 / emergency_event.vehicle_speed_mps,
            )
        else:
            result.emergency_hold_sec = EMERGENCY_HOLD_SEC

        # Cascade along declared path
        if junction_path:
            result.cascade_approaches = list(junction_path)

    # --- BRTS bias (lower priority; only applied when no emergency) ---
    if (
        brts_event
        and brts_event.brts_waiting
        and brts_event.wait_time_sec >= BRTS_WAIT_THRESHOLD_SEC
        and not result.emergency_triggered          # emergency wins; defer BRTS
    ):
        result.brts_triggered = True
        result.brts_approach = brts_event.approach
        # Boost grows with wait time but is capped so it doesn't dominate
        result.brts_pressure_boost = min(
            BRTS_PRESSURE_BOOST,
            0.1 * brts_event.wait_time_sec,
        )

    return result


def apply_brts_boost(
    pressure_scores: dict[str, float],
    priority: PriorityResult,
) -> dict[str, float]:
    """Add the BRTS pressure boost to the relevant approach's score.

    The scores dict maps approach name → raw max-pressure score.
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
    # Scenario: BRTS bus waiting 40 s and ambulance on north approach
    ev = EmergencyEvent(detected=True, approach="north", lane_id="lane_1")
    brts = BRTSEvent(approach="north", lane_id="lane_brts_N", wait_time_sec=40.0)
    res = evaluate_priority(emergency_event=ev, brts_event=brts)

    print(f"Emergency triggered : {res.emergency_triggered}")
    print(f"Emergency approach  : {res.emergency_approach}")
    print(f"Emergency hold (s)  : {res.emergency_hold_sec}")
    print(f"BRTS triggered      : {res.brts_triggered}")   # False — emergency wins
    print(f"BRTS boost          : {res.brts_pressure_boost}")

    # Scenario: BRTS only
    res2 = evaluate_priority(
        brts_event=BRTSEvent(approach="east", lane_id="lane_brts_E", wait_time_sec=35.0)
    )
    scores = {"north": 5.0, "east": 3.0, "south": 2.0, "west": 1.0}
    boosted = apply_brts_boost(scores, res2)
    print(f"\nBoosted scores: {boosted}")
