"""
event_modes.py — Event Mode Profiles (Festival / School / Office / Weekend / Rain)
===================================================================================
Different traffic patterns need different algorithm parameters, not different
algorithms.  This module provides a config-driven parameter lookup so that
``max_pressure.py`` uses one line to get its tuning constants.

Enhanced with:
  - Weather-specific control policy parameters (aggressiveness, safety margin)
  - Additional per-mode tuning knobs beyond min/max green

Improvement #21 from new_instruct.md.
"""

from __future__ import annotations

import datetime
from dataclasses import dataclass
from typing import Optional


# ---------------------------------------------------------------------------
# Mode profile definition
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ModeProfile:
    """Immutable set of algorithm parameters for one event mode."""
    name: str
    max_green: int         # seconds — longest a single phase may stay green
    min_green: int         # seconds — minimum green before a switch is allowed
    pressure_weight: float # multiplier on max-pressure score (>1 = more aggressive)
    description: str = ""

    # --- Enhanced: Weather-aware control policy (Improvement #21) ---
    aggressiveness: float = 1.0    # multiplier on growth/prediction bonuses (lower = more cautious)
    safety_margin_sec: float = 0.0 # additional seconds added to min_green for safety
    max_cycle_delta: float = 20.0  # max cycle-time change per step (seconds)
    switching_penalty_mult: float = 1.0  # multiplier on the base switching penalty


# ---------------------------------------------------------------------------
# Mode registry
# ---------------------------------------------------------------------------

MODES: dict[str, ModeProfile] = {
    "office_hours": ModeProfile(
        name="office_hours",
        max_green=60,
        min_green=15,
        pressure_weight=1.0,
        description="Standard weekday commuter flow.",
        aggressiveness=1.0,
        safety_margin_sec=0.0,
        max_cycle_delta=20.0,
        switching_penalty_mult=1.0,
    ),
    "school_hours": ModeProfile(
        name="school_hours",
        max_green=45,
        min_green=20,
        pressure_weight=0.8,
        description="Predictable, shorter cycles; prioritise pedestrian clearance.",
        aggressiveness=0.8,
        safety_margin_sec=3.0,
        max_cycle_delta=15.0,
        switching_penalty_mult=1.2,
    ),
    "weekend": ModeProfile(
        name="weekend",
        max_green=50,
        min_green=15,
        pressure_weight=0.9,
        description="Relaxed flow, slightly reduced pressure weight.",
        aggressiveness=0.9,
        safety_margin_sec=0.0,
        max_cycle_delta=18.0,
        switching_penalty_mult=0.8,
    ),
    "festival": ModeProfile(
        name="festival",
        max_green=90,
        min_green=20,
        pressure_weight=1.3,
        description="Heavy, less predictable flows; allow long greens.",
        aggressiveness=1.3,
        safety_margin_sec=2.0,
        max_cycle_delta=25.0,
        switching_penalty_mult=1.5,
    ),
    "rain": ModeProfile(
        name="rain",
        max_green=55,
        min_green=20,
        pressure_weight=0.7,
        description="Cautious mode — reduced aggressiveness, larger safety margins.",
        aggressiveness=0.6,
        safety_margin_sec=5.0,
        max_cycle_delta=10.0,
        switching_penalty_mult=1.5,
    ),
    "fog": ModeProfile(
        name="fog",
        max_green=50,
        min_green=22,
        pressure_weight=0.65,
        description="Very cautious — poor visibility, strong safety margins.",
        aggressiveness=0.5,
        safety_margin_sec=6.0,
        max_cycle_delta=8.0,
        switching_penalty_mult=2.0,
    ),
    "night": ModeProfile(
        name="night",
        max_green=45,
        min_green=12,
        pressure_weight=0.85,
        description="Low traffic, shorter cycles, slightly reduced weight.",
        aggressiveness=0.8,
        safety_margin_sec=2.0,
        max_cycle_delta=15.0,
        switching_penalty_mult=0.7,
    ),
}

DEFAULT_MODE = "office_hours"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_mode_params(mode_name: str) -> ModeProfile:
    """Return the :class:`ModeProfile` for *mode_name*.

    Falls back to ``office_hours`` for unknown mode names so the system
    never crashes on a bad override value.
    """
    return MODES.get(mode_name, MODES[DEFAULT_MODE])


def select_mode(
    manual_override: Optional[str] = None,
    weather_flag: Optional[str] = None,
    festival_active: bool = False,
    now: Optional[datetime.datetime] = None,
) -> str:
    """Determine the active mode name using the priority chain.

    Parameters
    ----------
    manual_override:
        Mode name sent from Person D's dashboard toggle.
    weather_flag:
        Current weather string from Person A or a weather API.
    festival_active:
        ``True`` when a festival calendar says today is a festival.
    now:
        Current datetime; defaults to ``datetime.datetime.now()``.

    Returns
    -------
    str
        The active mode name (always a key in :data:`MODES`).
    """
    if now is None:
        now = datetime.datetime.now()

    # 1. External event overrides
    if festival_active:
        return "festival"
    if weather_flag and weather_flag.lower() in ("rain", "fog", "snow"):
        weather_mode = weather_flag.lower()
        if weather_mode == "snow":
            weather_mode = "rain"  # treat snow like rain
        return weather_mode if weather_mode in MODES else "rain"
    if weather_flag and weather_flag.lower() == "night":
        return "night"

    # 2. Manual override from dashboard
    if manual_override and manual_override in MODES:
        return manual_override

    # 3. Scheduled by time-of-day / day-of-week
    return _scheduled_mode(now)


def _scheduled_mode(now: datetime.datetime) -> str:
    """Return a mode based on day-of-week and hour-of-day rules."""
    weekday = now.weekday()   # 0=Monday … 6=Sunday
    hour = now.hour

    if weekday >= 5:          # Saturday or Sunday
        return "weekend"

    # Weekday time-of-day rules (India IST assumed)
    if 7 <= hour < 9 or 15 <= hour < 18:
        return "school_hours"
    if 9 <= hour < 19:
        return "office_hours"

    # Night / off-peak
    if hour >= 21 or hour < 6:
        return "night"

    return "weekend"


# ---------------------------------------------------------------------------
# Quick self-test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    for mode, profile in MODES.items():
        print(f"{mode:15s}  max_green={profile.max_green}  "
              f"min_green={profile.min_green}  weight={profile.pressure_weight}  "
              f"aggress={profile.aggressiveness}  safety={profile.safety_margin_sec}s  "
              f"max_delta={profile.max_cycle_delta}s")

    print("\nScheduled mode right now:", select_mode())
    print("With rain flag         :", select_mode(weather_flag="rain"))
    print("With fog flag          :", select_mode(weather_flag="fog"))
    print("Festival override      :", select_mode(festival_active=True))
    print("Manual dashboard       :", select_mode(manual_override="school_hours"))
