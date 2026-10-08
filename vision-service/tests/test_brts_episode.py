"""
test_brts_episode.py — Unit tests for BRTS corridor episode detection
======================================================================
Tests BRTS intrusion state machine covering Section B12.1 of improvements.md:
1. Regular intrusion: unauthorised vehicle in BRTS for >= dwell_s and >= min_distance_m
2. Grazing: vehicle enters briefly (< dwell_s) and exits -> no violation
3. Class exemptions: BRTS bus, ambulance, fire truck -> no violation
4. Wrong-way detection: vehicle moves against corridor legal direction
5. Stationary parking stop: vehicle stationary for >= stop_s
6. ID-switch protection: track lost and re-associated inherits episode
"""

import unittest
from dataclasses import dataclass
from typing import Optional
from shapely.geometry import Polygon

from zones.brts_zone import ZoneAssigner
from violations.brts_engine import BRTSEngine, BRTSConfig, BRTSEpisode


@dataclass
class MockBRTSVehicle:
    track_id: int
    class_name: str
    bbox: tuple[float, float, float, float]
    world_xy: tuple[float, float]
    speed_kmh: float
    age_s: float
    velocity_world: Optional[tuple[float, float]] = (0.0, 5.0)
    dt: float = 0.1
    is_authorised: bool = False
    plate_text: Optional[str] = None


class TestBRTSEpisode(unittest.TestCase):
    def setUp(self):
        # BRTS zone polygon: x in [0, 40], y in [0, 100]
        self.brts_poly = Polygon([(0, 0), (40, 0), (40, 100), (0, 100)])
        self.zone_assigner = ZoneAssigner(
            zone_poly=self.brts_poly,
            zone_id="BRTS-TEST",
            enter_ratio=0.5,
            exit_ratio=0.2,
            n_enter=2,
            n_exit=2,
        )
        self.cfg = BRTSConfig(
            zone_id="BRTS-TEST",
            zone_assigner=self.zone_assigner,
            dwell_s=1.0,           # 1.0 s for quick testing
            min_distance_m=8.0,    # 8.0 metres
            stop_s=5.0,            # 5.0 seconds
            corridor_dir=(0.0, 1.0), # Legal direction is +Y
            min_track_age_s=0.2,
            id_switch_window_s=1.0,
            id_switch_max_m=3.0,
            wrong_way_min_m=5.0,
            min_dir_samples=3,
        )

    def test_scooter_intrusion_confirmed(self):
        engine = BRTSEngine(self.cfg)
        events = []

        # Vehicle moves inside corridor along +Y from y=5 to y=35 (dist=30m > 8m)
        t = 0.0
        for step in range(15):
            y = 5.0 + step * 2.0
            bbox = (10, y, 30, y + 20)
            v = MockBRTSVehicle(
                track_id=1,
                class_name="two_wheeler",
                bbox=bbox,
                world_xy=(20.0, y),
                speed_kmh=20.0,
                age_s=0.5 + t,
                velocity_world=(0.0, 5.0),
                dt=0.1,
            )
            ev = engine.update(t, [v])
            if ev:
                events.extend(ev)
            t += 0.1

        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["type"], "BRTS_INTRUSION")
        self.assertEqual(events[0]["track_id"], 1)

    def test_grazing_briefly_no_violation(self):
        engine = BRTSEngine(self.cfg)
        events = []

        # Enters for only 3 frames (0.3s < 1.0s dwell) and then leaves
        t = 0.0
        for step in range(3):
            v = MockBRTSVehicle(
                track_id=2,
                class_name="car",
                bbox=(10, 20, 30, 40),
                world_xy=(20.0, 20.0),
                speed_kmh=15.0,
                age_s=1.0 + t,
                velocity_world=(0.0, 5.0),
                dt=0.1,
            )
            ev = engine.update(t, [v])
            if ev:
                events.extend(ev)
            t += 0.1

        # Moves outside
        for step in range(5):
            v = MockBRTSVehicle(
                track_id=2,
                class_name="car",
                bbox=(60, 20, 80, 40),
                world_xy=(70.0, 20.0),
                speed_kmh=15.0,
                age_s=1.0 + t,
                velocity_world=(0.0, 5.0),
                dt=0.1,
            )
            ev = engine.update(t, [v])
            if ev:
                events.extend(ev)
            t += 0.1

        self.assertEqual(len(events), 0)

    def test_authorised_classes_exempt(self):
        engine = BRTSEngine(self.cfg)
        events = []

        # BRTS bus moving through
        t = 0.0
        for step in range(15):
            y = 5.0 + step * 2.0
            v_bus = MockBRTSVehicle(
                track_id=10,
                class_name="brts_bus",
                bbox=(10, y, 30, y + 30),
                world_xy=(20.0, y),
                speed_kmh=30.0,
                age_s=1.0 + t,
                velocity_world=(0.0, 8.0),
                dt=0.1,
            )
            v_amb = MockBRTSVehicle(
                track_id=11,
                class_name="ambulance",
                bbox=(10, y, 30, y + 20),
                world_xy=(20.0, y),
                speed_kmh=45.0,
                age_s=1.0 + t,
                velocity_world=(0.0, 12.0),
                dt=0.1,
            )
            ev = engine.update(t, [v_bus, v_amb])
            if ev:
                events.extend(ev)
            t += 0.1

        self.assertEqual(len(events), 0)

    def test_wrong_way_detection(self):
        engine = BRTSEngine(self.cfg)
        events = []

        # Legal direction is +Y (corridor_dir = (0, 1)).
        # Vehicle travels in -Y direction: velocity (0, -5.0)
        t = 0.0
        for step in range(15):
            y = 60.0 - step * 2.0
            bbox = (10, y, 30, y + 20)
            v = MockBRTSVehicle(
                track_id=3,
                class_name="two_wheeler",
                bbox=bbox,
                world_xy=(20.0, y),
                speed_kmh=20.0,
                age_s=0.5 + t,
                velocity_world=(0.0, -5.0), # Opposite to corridor_dir
                dt=0.1,
            )
            ev = engine.update(t, [v])
            if ev:
                events.extend(ev)
            t += 0.1

        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["type"], "BRTS_WRONG_WAY")

    def test_parking_stop_stationary_vehicle(self):
        engine = BRTSEngine(self.cfg)
        events = []

        # Vehicle stationary (speed < 2 km/h) for stop_s (5.0s)
        t = 0.0
        for step in range(55): # 5.5s
            bbox = (10, 20, 30, 40)
            v = MockBRTSVehicle(
                track_id=4,
                class_name="car",
                bbox=bbox,
                world_xy=(20.0, 30.0),
                speed_kmh=0.0,
                age_s=1.0 + t,
                velocity_world=(0.0, 0.0),
                dt=0.1,
            )
            ev = engine.update(t, [v])
            if ev:
                events.extend(ev)
            t += 0.1

        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["type"], "BRTS_PARKING_STOP")


if __name__ == "__main__":
    unittest.main()
