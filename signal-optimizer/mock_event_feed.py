"""
mock_event_feed.py — Mock Generator for Person A's Event Contract
=================================================================
Generates synthetic event JSON objects matching the shared contract so that
``max_pressure.py`` and ``traci_runner.py`` can be developed and tested
without waiting for the real vision-service output.

Enhanced with expanded scenario matrix (Improvement #36):
  - normal, congested, festival, rain
  - peak_ns, peak_ew, sudden_inflow, dissipating
  - downstream_blockage, oscillation
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
APPROACHES = ["north", "south", "east", "west"]


# ---------------------------------------------------------------------------
# Scenario presets
# ---------------------------------------------------------------------------

def _scenario_params(scenario: str, step: int = 0) -> dict:
    """Return per-lane generation parameters for a scenario."""
    if scenario == "congested":
        return {
            "ns_base": random.randint(15, 30),
            "ew_base": random.randint(12, 25),
            "det_conf": round(random.uniform(0.70, 0.90), 2),
            "weather": "clear",
        }
    elif scenario == "festival":
        return {
            "ns_base": random.randint(20, 40),
            "ew_base": random.randint(20, 40),
            "det_conf": round(random.uniform(0.65, 0.85), 2),
            "weather": "clear",
        }
    elif scenario == "rain":
        return {
            "ns_base": random.randint(8, 20),
            "ew_base": random.randint(6, 15),
            "det_conf": round(random.uniform(0.40, 0.65), 2),
            "weather": "rain",
        }
    elif scenario == "peak_ns":
        return {
            "ns_base": random.randint(25, 40),
            "ew_base": random.randint(3, 8),
            "det_conf": round(random.uniform(0.80, 0.95), 2),
            "weather": "clear",
        }
    elif scenario == "peak_ew":
        return {
            "ns_base": random.randint(3, 8),
            "ew_base": random.randint(25, 40),
            "det_conf": round(random.uniform(0.80, 0.95), 2),
            "weather": "clear",
        }
    elif scenario == "sudden_inflow":
        # Traffic ramps up sharply over steps
        ramp = min(step * 2, 30)
        return {
            "ns_base": 5 + ramp + random.randint(0, 3),
            "ew_base": random.randint(3, 8),
            "det_conf": round(random.uniform(0.80, 0.95), 2),
            "weather": "clear",
        }
    elif scenario == "dissipating":
        # Traffic decreases over steps
        decay = max(0, 30 - step * 2)
        return {
            "ns_base": decay + random.randint(0, 3),
            "ew_base": max(2, decay // 2) + random.randint(0, 2),
            "det_conf": round(random.uniform(0.80, 0.95), 2),
            "weather": "clear",
        }
    elif scenario == "downstream_blockage":
        return {
            "ns_base": random.randint(15, 25),
            "ew_base": random.randint(30, 40),  # downstream EW is blocked
            "det_conf": round(random.uniform(0.75, 0.90), 2),
            "weather": "clear",
        }
    elif scenario == "oscillation":
        # NS and EW alternate being dominant
        if step % 4 < 2:
            return {
                "ns_base": random.randint(18, 25),
                "ew_base": random.randint(15, 20),
                "det_conf": round(random.uniform(0.80, 0.95), 2),
                "weather": "clear",
            }
        else:
            return {
                "ns_base": random.randint(15, 20),
                "ew_base": random.randint(18, 25),
                "det_conf": round(random.uniform(0.80, 0.95), 2),
                "weather": "clear",
            }
    else:  # normal
        return {
            "ns_base": random.randint(3, 15),
            "ew_base": random.randint(3, 12),
            "det_conf": round(random.uniform(0.75, 0.95), 2),
            "weather": random.choice(WEATHER_OPTIONS),
        }


# ---------------------------------------------------------------------------
# Generators
# ---------------------------------------------------------------------------

def generate_event(
    junction_id: str = JUNCTION_ID,
    scenario: str = "normal",
    emergency_approach: Optional[str] = None,
    brts_approach: Optional[str] = None,
    weather_flag: Optional[str] = None,
    step: int = 0,
) -> dict:
    """Generate a single synthetic event dict."""
    now = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    params = _scenario_params(scenario, step)

    weather = weather_flag or params["weather"]
    det_conf = params["det_conf"]

    # Per-lane readings
    lanes = {}
    for lane_id in LANE_IDS:
        if "NS" in lane_id:
            base = params["ns_base"]
        else:
            base = params["ew_base"]
        density = max(0, int(base + random.gauss(0, 3)))
        queue = max(0, int(density * random.uniform(0.5, 0.9)))
        speed = round(max(0.5, random.gauss(4.0 - density * 0.1, 0.5)), 1)
        lanes[lane_id] = {
            "density": density,
            "queue_length": queue,
            "speed_mps": speed,
        }

    # BRTS
    brts_active = brts_approach is not None
    brts_wait = round(random.uniform(25, 60), 1) if brts_active else 0

    # Emergency
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
        "brts_violation": random.random() < 0.05,
    }
    return event


def event_stream(
    count: int = 100,
    interval_sec: float = 0.0,
    scenario: str = "normal",
    inject_emergency_at: Optional[int] = None,
    inject_brts_at: Optional[int] = None,
) -> Generator[dict, None, None]:
    """Yield ``count`` synthetic events at ``interval_sec`` intervals."""
    for i in range(count):
        em_approach = "north" if i == inject_emergency_at else None
        brts_approach = "east" if i == inject_brts_at else None
        yield generate_event(
            scenario=scenario,
            emergency_approach=em_approach,
            brts_approach=brts_approach,
            step=i,
        )
        if interval_sec > 0:
            time.sleep(interval_sec)


# ---------------------------------------------------------------------------
# Quick self-test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import json

    scenarios = ["normal", "congested", "rain", "peak_ns", "peak_ew",
                 "sudden_inflow", "dissipating", "oscillation",
                 "downstream_blockage", "festival"]

    for sc in scenarios:
        ev = generate_event(scenario=sc, step=5)
        ns_q = ev["lanes"]["lane_NS_1"]["queue_length"]
        ew_q = ev["lanes"]["lane_EW_1"]["queue_length"]
        print(f"{sc:22s}  NS_q={ns_q:3d}  EW_q={ew_q:3d}  "
              f"conf={ev['detection_confidence']:.2f}  weather={ev['weather_flag']}")
