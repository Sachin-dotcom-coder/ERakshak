"""
event_modes.py — Event Mode Profiles (Festival / School / Office / Weekend / Rain)
===================================================================================
Different traffic patterns need different algorithm parameters, not different
algorithms.  This module provides a config-driven parameter lookup so that
``max_pressure.py`` uses one line to get its tuning constants:

    params = get_mode_params(active_mode)

Mode selection priority (highest to lowest):
  1. External override (emergency flag, weather API, festival calendar)
  2. Manual override (dashboard toggle from Person D)
  3. Scheduled (time-of-day / day-of-week rules)
  4. Default → ``"office_hours"``
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
    ),
    "school_hours": ModeProfile(
        name="school_hours",
        max_green=45,
        min_green=20,
        pressure_weight=0.8,
        description="Predictable, shorter cycles; prioritise pedestrian clearance.",
    ),
    "weekend": ModeProfile(
        name="weekend",
        max_green=50,
        min_green=15,
        pressure_weight=0.9,
        description="Relaxed flow, slightly reduced pressure weight.",
    ),
    "festival": ModeProfile(
        name="festival",
        max_green=90,
        min_green=20,
        pressure_weight=1.3,
        description="Heavy, less predictable flows; allow long greens.",
    ),
    "rain": ModeProfile(
        name="rain",
        max_green=55,
        min_green=20,
        pressure_weight=0.7,
        description="Cautious mode — ties into confidence.py to reduce erratic swings.",
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
        Mode name sent from Person D's dashboard toggle (highest priority after
        external events).
    weather_flag:
        Current weather string from Person A or a weather API.  ``"rain"`` or
        ``"fog"`` will activate the ``rain`` mode when no manual override is set.
    festival_active:
        ``True`` when an external festival calendar says today is a festival.
    now:
        Current datetime; defaults to ``datetime.datetime.now()`` if not
        supplied.  Used for time-of-day scheduling.

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
        return "rain"

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
    if 7 <= hour < 9 or 15 <= hour < 18:   # School rush: morning + afternoon
        return "school_hours"
    if 9 <= hour < 19:                      # Office hours
        return "office_hours"

    # Night / off-peak — use weekend params (light flow)
    return "weekend"


# ---------------------------------------------------------------------------
# Quick self-test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    for mode, profile in MODES.items():
        print(f"{mode:15s}  max_green={profile.max_green}  "
              f"min_green={profile.min_green}  weight={profile.pressure_weight}")

    print("\nScheduled mode right now:", select_mode())
    print("With rain flag         :", select_mode(weather_flag="rain"))
    print("Festival override      :", select_mode(festival_active=True))
    print("Manual dashboard       :", select_mode(manual_override="school_hours"))
