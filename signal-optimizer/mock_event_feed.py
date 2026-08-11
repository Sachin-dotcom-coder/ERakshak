"""
mock_event_feed.py — Mock Generator for Person A's Event Contract
=================================================================
Generates synthetic event JSON objects matching the shared contract so that
``max_pressure.py`` and ``traci_runner.py`` can be developed and tested
without waiting for the real vision-service output.

Usage
-----
    # One-shot: get a single mock event
    from mock_event_feed import generate_event
    event = generate_event()

    # Streaming: iterate events (blocking, ~30 s intervals)
    from mock_event_feed import event_stream
    for event in event_stream(count=20):
        process(event)

Person A's event contract (extended for signal-optimizer features):
{
    "junction_id":           "junction_01",
    "timestamp":             "2026-07-08T10:15:32Z",
    "lanes": {
        "<lane_id>": {
            "density":       12,          // vehicles currently in lane
            "queue_length":  8,           // vehicles waiting at stop-line
            "speed_mps":     3.2          // avg speed (lower = more congested)
        }, ...
    },
    "detection_confidence":  0.85,
    "weather_flag":          "clear",
    "brts_waiting":          false,
    "brts_wait_time_sec":    0,
    "brts_approach":         null,
    "emergency_vehicle": {
        "detected":          false,
        "approach":          null,
        "lane_id":           null,
        "vehicle_speed_mps": null
    },
    "brts_violation":        false
}
"""

from __future__ import annotations

import datetime
import random
import time
from typing import Generator, Optional

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
JUNCTION_ID = "junction_01"
LANE_IDS = ["lane_NS_1", "lane_NS_2", "lane_EW_1", "lane_EW_2"]

WEATHER_OPTIONS = ["clear", "clear", "clear", "rain", "fog", "cloudy"]
BRTS_APPROACH_OPTIONS = ["north", "south", None, None, None]  # weighted toward None

APPROACHES = ["north", "south", "east", "west"]


# ---------------------------------------------------------------------------
# Generators
# ---------------------------------------------------------------------------

def generate_event(
    junction_id: str = JUNCTION_ID,
    scenario: str = "normal",
    emergency_approach: Optional[str] = None,
    brts_approach: Optional[str] = None,
    weather_flag: Optional[str] = None,
) -> dict:
    """Generate a single synthetic event dict.

    Parameters
    ----------
    scenario:
        ``"normal"`` | ``"congested"`` | ``"festival"`` | ``"rain"``
    emergency_approach:
        If set, injects an emergency-vehicle detection on that approach.
    brts_approach:
        If set, injects a BRTS bus waiting on that approach.
    weather_flag:
        Override the weather.  If ``None``, chosen based on scenario.
    """
    now = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    # --- Scenario presets ---
    if scenario == "congested":
        base_density = random.randint(15, 30)
        det_conf = round(random.uniform(0.70, 0.90), 2)
        weather = weather_flag or "clear"
    elif scenario == "festival":
        base_density = random.randint(20, 40)
        det_conf = round(random.uniform(0.65, 0.85), 2)
        weather = weather_flag or "clear"
    elif scenario == "rain":
        base_density = random.randint(8, 20)
        det_conf = round(random.uniform(0.40, 0.65), 2)
        weather = weather_flag or "rain"
    else:  # normal
        base_density = random.randint(3, 15)
        det_conf = round(random.uniform(0.75, 0.95), 2)
        weather = weather_flag or random.choice(WEATHER_OPTIONS)

    # --- Per-lane readings ---
    lanes = {}
    for lane_id in LANE_IDS:
        density = max(0, int(base_density + random.gauss(0, 3)))
        queue = max(0, int(density * random.uniform(0.5, 0.9)))
        speed = round(max(0.5, random.gauss(4.0 - density * 0.1, 0.5)), 1)
        lanes[lane_id] = {
            "density": density,
            "queue_length": queue,
            "speed_mps": speed,
        }

    # --- BRTS ---
    brts_active = brts_approach is not None
    brts_wait = round(random.uniform(25, 60), 1) if brts_active else 0

    # --- Emergency ---
    em_detected = emergency_approach is not None
    em_speed = round(random.uniform(8.0, 14.0), 1) if em_detected else None

    event = {
        "junction_id": junction_id,
        "timestamp": now,
        "lanes": lanes,
        "detection_confidence": det_conf,
        "weather_flag": weather,
        "brts_waiting": brts_active,
        "brts_wait_time_sec": brts_wait,
        "brts_approach": brts_approach,
        "emergency_vehicle": {
            "detected": em_detected,
            "approach": emergency_approach,
            "lane_id": f"lane_{emergency_approach[0].upper()}" if em_detected else None,
            "vehicle_speed_mps": em_speed,
        },
        "brts_violation": random.random() < 0.05,  # 5 % random BRTS-lane violation
    }
    return event


def event_stream(
    count: int = 100,
    interval_sec: float = 0.0,
    scenario: str = "normal",
    inject_emergency_at: Optional[int] = None,
    inject_brts_at: Optional[int] = None,
) -> Generator[dict, None, None]:
    """Yield ``count`` synthetic events at ``interval_sec`` intervals.

    Parameters
    ----------
    inject_emergency_at:
        Step index at which to inject an emergency-vehicle event.
    inject_brts_at:
        Step index at which to inject a BRTS-waiting event.
    """
    for i in range(count):
        em_approach = "north" if i == inject_emergency_at else None
        brts_approach = "east" if i == inject_brts_at else None
        yield generate_event(
            scenario=scenario,
            emergency_approach=em_approach,
            brts_approach=brts_approach,
        )
        if interval_sec > 0:
            time.sleep(interval_sec)


# ---------------------------------------------------------------------------
# Quick self-test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import json

    print("=== Normal event ===")
    print(json.dumps(generate_event(), indent=2))

    print("\n=== Rain event ===")
    print(json.dumps(generate_event(scenario="rain"), indent=2))

    print("\n=== Emergency event ===")
    print(json.dumps(generate_event(emergency_approach="north"), indent=2))
