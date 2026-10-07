"""
test_incidents_v2.py — Tests for Upgraded Incident Intelligence (Sprint 6, Sections 54-63)
"""

import unittest
import numpy as np
from incidents.emergency import EmergencyVehicleDetector
from incidents.brts import BRTSViolationDetector
from incidents.wrong_way import WrongWayDetector
from incidents.breakdown import BreakdownDetector


class TestIncidentsV2(unittest.TestCase):

    def setUp(self):
        self.emergency_detector = EmergencyVehicleDetector({"confirmation_frames": 2})
        self.brts_detector = BRTSViolationDetector(
            config={"minimum_dwell_sec": 0.1, "minimum_distance_m": 1.0, "confirmation_probability": 0.5},
            brts_polygon=[[0, 0], [100, 0], [100, 100], [0, 100]],
        )
        self.wrong_way_detector = WrongWayDetector({"cosine_threshold": -0.3, "persistence_sec": 0.0})
        self.breakdown_detector = BreakdownDetector({"speed_threshold_kmph": 2.0, "candidate_duration_sec": 0.1})

    def test_emergency_detector(self):
        dummy_frame = np.zeros((100, 100, 3), dtype=np.uint8)
        # Update with ambulance
        res = self.emergency_detector.update_vehicle(
            track_id=1,
            class_name="ambulance",
            detection_confidence=0.95,
            bbox=np.array([10, 10, 50, 50]),
            frame=dummy_frame,
            speed_kmph=40.0,
        )
        self.assertIn("emergency_score", res)
        self.assertGreater(res["emergency_score"], 0.0)

    def test_brts_violation_unauthorized(self):
        # Car inside BRTS corridor
        inside_point = (50.0, 50.0)
        self.assertTrue(self.brts_detector.is_inside_corridor(inside_point))

        # First entry
        res1 = self.brts_detector.update(
            track_id=10,
            class_name="car",
            detection_confidence=0.9,
            pixel_point=inside_point,
            world_pos=(5.0, 5.0),
        )
        # Second update after dwell
        res2 = self.brts_detector.update(
            track_id=10,
            class_name="car",
            detection_confidence=0.9,
            pixel_point=inside_point,
            world_pos=(5.0, 15.0),
        )
        # Should detect transition or candidate
        self.assertIsNotNone(self.brts_detector.get_state(10))

    def test_wrong_way_detection(self):
        # Heading 0 (North) vs Expected 180 (South) -> Opposite direction (cosine = -1.0)
        alert = self.wrong_way_detector.check(
            track_id=20,
            heading_deg=0.0,
            expected_heading_deg=180.0,
            speed_kmph=30.0,
        )
        self.assertIsNotNone(alert)
        self.assertEqual(alert["track_id"], 20)

    def test_correct_way_no_alert(self):
        # Heading 180 (South) vs Expected 180 (South) -> Same direction (cosine = 1.0)
        alert = self.wrong_way_detector.check(
            track_id=21,
            heading_deg=180.0,
            expected_heading_deg=180.0,
            speed_kmph=30.0,
        )
        self.assertIsNone(alert)


if __name__ == "__main__":
    unittest.main()
