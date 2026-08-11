"""
webster_formula.py — Webster's Optimal Cycle Time Formula
==========================================================
Provides an alternate / backup timing model to the max-pressure algorithm.
Webster (1958) derived the optimal cycle time that minimises average vehicle
delay at an isolated, signalised intersection:

    C_opt = (1.5 * L + 5) / (1 - Y)

where:
  L = total lost time per cycle (sum of inter-green times, seconds)
  Y = sum of critical-lane flow ratios (v_i / s_i) for each phase i

Individual phase green times are then split proportionally to Y_i / Y.

Reference:
  Webster, F. V. (1958). *Traffic Signal Settings*.
  Road Research Technical Paper No. 39. HMSO, London.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

# Absolute limits on cycle time (seconds)
MIN_CYCLE: int = 20
MAX_CYCLE: int = 180

# Minimum green per phase (seconds) — prevents a phase vanishing entirely
MIN_PHASE_GREEN: int = 7

# Lost time per phase (amber + all-red clearance, seconds)
DEFAULT_LOST_TIME_PER_PHASE: float = 4.0


@dataclass
class Phase:
    """One signal phase (e.g. NS-green, EW-green)."""
    name: str
    volume: float      # vehicles per hour (critical lane in this phase)
    saturation: float  # saturation flow rate (vehicles per hour of green)

    @property
    def flow_ratio(self) -> float:
        """y = v / s.  Clamped to avoid division issues."""
        if self.saturation <= 0:
            return 0.0
        return min(self.volume / self.saturation, 0.99)


def optimal_cycle(phases: Sequence[Phase], lost_time_per_phase: float = DEFAULT_LOST_TIME_PER_PHASE) -> int:
    """Compute Webster's optimal cycle time (seconds), clamped to [MIN_CYCLE, MAX_CYCLE].

    Parameters
    ----------
    phases:
        Sequence of :class:`Phase` objects (one per signal phase).
    lost_time_per_phase:
        Lost time in seconds for each phase (inter-green / clearance).

    Returns
    -------
    int
        Recommended cycle time in whole seconds.
    """
    n = len(phases)
    if n == 0:
        return MIN_CYCLE

    L = n * lost_time_per_phase                 # total lost time
    Y = sum(p.flow_ratio for p in phases)       # sum of critical y-values

    if Y >= 1.0:
        # Intersection is over-saturated — cap at maximum
        return MAX_CYCLE

    c_opt = (1.5 * L + 5) / (1.0 - Y)
    return int(max(MIN_CYCLE, min(MAX_CYCLE, round(c_opt))))


def split_green_times(
    phases: Sequence[Phase],
    cycle_sec: int,
    lost_time_per_phase: float = DEFAULT_LOST_TIME_PER_PHASE,
) -> dict[str, int]:
    """Distribute effective green time across phases proportionally to y_i.

    Parameters
    ----------
    phases:
        Sequence of phases (same order as ``optimal_cycle`` input).
    cycle_sec:
        Total cycle time in seconds (typically from :func:`optimal_cycle`).
    lost_time_per_phase:
        Lost time per phase used to derive effective green.

    Returns
    -------
    dict[str, int]
        Mapping of phase name → effective green time in seconds.
    """
    n = len(phases)
    total_lost = n * lost_time_per_phase
    effective_green = max(0, cycle_sec - total_lost)

    Y = sum(p.flow_ratio for p in phases)
    result: dict[str, int] = {}

    for phase in phases:
        if Y <= 0:
            share = effective_green / max(n, 1)
        else:
            share = (phase.flow_ratio / Y) * effective_green
        result[phase.name] = max(MIN_PHASE_GREEN, int(round(share)))

    return result


def webster_decision(phases: Sequence[Phase], lost_time_per_phase: float = DEFAULT_LOST_TIME_PER_PHASE) -> dict:
    """Convenience: return a dict with cycle time and per-phase green splits."""
    cycle = optimal_cycle(phases, lost_time_per_phase)
    greens = split_green_times(phases, cycle, lost_time_per_phase)
    return {
        "method": "webster",
        "cycle_time_sec": cycle,
        "phase_greens": greens,
        "flow_ratios": {p.name: round(p.flow_ratio, 3) for p in phases},
        "Y_total": round(sum(p.flow_ratio for p in phases), 3),
    }


# ---------------------------------------------------------------------------
# Quick self-test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import json

    phases = [
        Phase("NS_green", volume=800, saturation=1800),
        Phase("EW_green", volume=400, saturation=1800),
    ]
    decision = webster_decision(phases)
    print(json.dumps(decision, indent=2))

    # Over-saturated scenario
    phases_heavy = [
        Phase("NS_green", volume=1700, saturation=1800),
        Phase("EW_green", volume=1600, saturation=1800),
    ]
    print("\nOver-saturated:", webster_decision(phases_heavy))
