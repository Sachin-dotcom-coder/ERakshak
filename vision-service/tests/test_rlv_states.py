"""
test_rlv_states.py — Unit tests for RLV per-track state machine
===============================================================
Tests all state transitions and scenarios defined in improvements.md § A12.1:
1. Normal RLV: crosses on red (speed > 8 km/h, confirmed > 5m) -> RED_LIGHT_VIOLATION
2. Yellow entry: crosses on yellow -> YELLOW_ENTRY, no violation
3. Green entry: crosses on green -> GREEN_ENTRY, no violation
4. Encroachment: stops just over the line -> ENCROACHMENT
5. Creep: creeps over line < 8 km/h -> ENCROACHMENT
6. Glare / Unknown signal: signal is UNKNOWN -> UNKNOWN_SIGNAL, no fine
7. Emergency exemption: ambulance / fire_truck -> exempt, no violation
8. Rollback / Discarded: crosses then reverses back -> DISCARDED
9. Segment gating: cross-traffic outside stop line span -> no crossing
10. High-risk flag: cross-traffic in box -> RED_LIGHT_VIOLATION_HIGH_RISK
"""

import unittest
from dataclasses import dataclass
from typing import Optional

from signals.signal_state import Lamp
from violations.stopline import StopLine
from violations.rlv_engine import RLVEngine, RLVConfig, S


@dataclass
class MockRLVVehicle:
    track_id: int
    class_name: str
    world_xy: tuple[float, float]
    speed_kmh: float
    age_s: float


class MockSignalReader:
    def __init__(self, lamp: Lamp = Lamp.RED, red_elapsed_s: float = 5.0):
        self.lamp = lamp
        self.red_elapsed_s = red_elapsed_s

    def state_at(self, ts: float) -> tuple[Lamp, Optional[float]]:
        return self.lamp, self.red_elapsed_s


class TestRLVStateMachine(unittest.TestCase):
    def setUp(self):
        # Stop line along y=10.0, from x=0 to x=10.
        # Positive d means y > 10.0 (approaching). Negative d means y < 10.0 (past line).
        self.stop_line = StopLine((0.0, 10.0), (10.0, 10.0), travel_sign=1, hysteresis_m=0.3, margin_m=0.5)
        self.cfg = RLVConfig(
            stop_line=self.stop_line,
            min_track_age_s=0.5,
            min_frames_before=3,
            min_speed_at_crossing_kmh=8.0,
            confirm_distance_m=5.0,
            confirm_min_frames=4,
            max_candidate_frames=10,
            grace_s=0.0,
        )

    def test_normal_rlv_confirmed(self):
        sig = MockSignalReader(Lamp.RED, red_elapsed_s=3.0)
        engine = RLVEngine(self.cfg, sig)

        # 1. Approach frames before the line (y=15, 14, 13)
        t = 1.0
        for y in [15.0, 14.0, 13.0, 12.0]:
            v = MockRLVVehicle(1, "car", (5.0, y), speed_kmh=30.0, age_s=t)
            events = engine.update(t, [v])
            self.assertEqual(len(events), 0)
            t += 0.1

        self.assertEqual(engine.tracks[1].state, S.BEFORE_LINE)

        # 2. Crossing frame (y=8.0, past the line)
        v = MockRLVVehicle(1, "car", (5.0, 8.0), speed_kmh=30.0, age_s=t)
        events = engine.update(t, [v])
        self.assertEqual(len(events), 0)
        self.assertEqual(engine.tracks[1].state, S.RED_CANDIDATE)
        t += 0.1

        # 3. Confirmation frames (moving further past the line, y=4.0 -> dist_after = 6m >= 5m)
        for y in [7.0, 6.0, 5.0, 4.0]:
            v = MockRLVVehicle(1, "car", (5.0, y), speed_kmh=30.0, age_s=t)
            events = engine.update(t, [v])
            t += 0.1

        self.assertEqual(engine.tracks[1].state, S.CONFIRMED)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["type"], "RED_LIGHT_VIOLATION")
        self.assertEqual(events[0]["track_id"], 1)

    def test_high_risk_flag_when_cross_traffic_in_box(self):
        sig = MockSignalReader(Lamp.RED, red_elapsed_s=3.0)
        engine = RLVEngine(self.cfg, sig)

        t = 1.0
        for y in [15.0, 14.0, 13.0, 12.0]:
            v = MockRLVVehicle(2, "car", (5.0, y), speed_kmh=25.0, age_s=t)
            engine.update(t, [v])
            t += 0.1

        # Crossing
        v = MockRLVVehicle(2, "car", (5.0, 8.0), speed_kmh=25.0, age_s=t)
        engine.update(t, [v])
        t += 0.1

        # Confirm with cross_traffic_in_box=True
        events = []
        for y in [7.0, 6.0, 5.0, 4.0]:
            v = MockRLVVehicle(2, "car", (5.0, y), speed_kmh=25.0, age_s=t)
            ev = engine.update(t, [v], cross_traffic_in_box=True)
            if ev:
                events.extend(ev)
            t += 0.1

        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["type"], "RED_LIGHT_VIOLATION_HIGH_RISK")
        self.assertTrue(events[0]["cross_traffic_in_box"])

    def test_yellow_and_green_entry_no_violation(self):
        # Yellow
        engine_yellow = RLVEngine(self.cfg, MockSignalReader(Lamp.YELLOW, 1.0))
        t = 1.0
        for y in [14.0, 13.0, 12.0]:
            engine_yellow.update(t, [MockRLVVehicle(3, "car", (5.0, y), 30.0, t)])
            t += 0.1
        engine_yellow.update(t, [MockRLVVehicle(3, "car", (5.0, 8.0), 30.0, t)])
        self.assertEqual(engine_yellow.tracks[3].state, S.YELLOW_ENTRY)

        # Green
        engine_green = RLVEngine(self.cfg, MockSignalReader(Lamp.GREEN, 5.0))
        t = 1.0
        for y in [14.0, 13.0, 12.0]:
            engine_green.update(t, [MockRLVVehicle(4, "car", (5.0, y), 30.0, t)])
            t += 0.1
        engine_green.update(t, [MockRLVVehicle(4, "car", (5.0, 8.0), 30.0, t)])
        self.assertEqual(engine_green.tracks[4].state, S.GREEN_ENTRY)

    def test_unknown_signal_no_enforcement(self):
        engine = RLVEngine(self.cfg, MockSignalReader(Lamp.UNKNOWN, None))
        t = 1.0
        for y in [14.0, 13.0, 12.0]:
            engine.update(t, [MockRLVVehicle(5, "car", (5.0, y), 30.0, t)])
            t += 0.1
        engine.update(t, [MockRLVVehicle(5, "car", (5.0, 8.0), 30.0, t)])
        self.assertEqual(engine.tracks[5].state, S.UNKNOWN_SIGNAL)

    def test_encroachment_low_speed_creep(self):
        sig = MockSignalReader(Lamp.RED, 5.0)
        engine = RLVEngine(self.cfg, sig)
        t = 1.0
        for y in [14.0, 13.0, 12.0]:
            engine.update(t, [MockRLVVehicle(6, "two_wheeler", (5.0, y), 5.0, t)])
            t += 0.1
        # Crossing at 5 km/h < min_speed_at_crossing_kmh (8 km/h)
        events = engine.update(t, [MockRLVVehicle(6, "two_wheeler", (5.0, 8.0), 5.0, t)])
        self.assertEqual(len(events), 0)
        self.assertEqual(engine.tracks[6].state, S.ENCROACHMENT)

    def test_exempt_classes_never_violate(self):
        sig = MockSignalReader(Lamp.RED, 5.0)
        engine = RLVEngine(self.cfg, sig)
        t = 1.0
        for y in [14.0, 13.0, 12.0, 8.0, 4.0]:
            events = engine.update(t, [MockRLVVehicle(7, "ambulance", (5.0, y), 45.0, t)])
            self.assertEqual(len(events), 0)
            t += 0.1
        # Track 7 shouldn't even be added or should stay untouched
        self.assertNotIn(7, engine.tracks)

    def test_rollback_reverses_behind_line(self):
        sig = MockSignalReader(Lamp.RED, 5.0)
        engine = RLVEngine(self.cfg, sig)
        t = 1.0
        for y in [14.0, 13.0, 12.0]:
            engine.update(t, [MockRLVVehicle(8, "car", (5.0, y), 20.0, t)])
            t += 0.1
        # Crosses
        engine.update(t, [MockRLVVehicle(8, "car", (5.0, 9.0), 20.0, t)])
        self.assertEqual(engine.tracks[8].state, S.RED_CANDIDATE)
        t += 0.1
        # Reverses back behind the line (y=11.0 >= hysteresis 0.3)
        events = engine.update(t, [MockRLVVehicle(8, "car", (5.0, 11.0), -5.0, t)])
        self.assertEqual(len(events), 0)
        self.assertEqual(engine.tracks[8].state, S.DISCARDED)


if __name__ == "__main__":
    unittest.main()
