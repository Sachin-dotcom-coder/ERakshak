import unittest
from zones.zone_utils import ZoneManager

class TestZones(unittest.TestCase):
    def setUp(self):
        self.config = {
            "brts_corridor": {
                "polygon": [[0, 0], [10, 0], [10, 50], [0, 50]],
                "direction_axis": [0.0, 1.0]  # Corridor runs along the Y axis
            }
        }
        self.zone_mgr = ZoneManager(self.config, pcu_factors={"car": 1.0})

    def test_brts_angle_parallel(self):
        # Moving purely along Y axis
        motion = (0.0, 10.0)
        angle = self.zone_mgr.compute_angle_to_brts_axis(motion)
        self.assertIsNotNone(angle)
        self.assertAlmostEqual(angle, 0.0, places=1)
        
        # Moving opposite direction along Y axis (should also be 0 degrees due to abs dot product)
        motion_opp = (0.0, -10.0)
        angle_opp = self.zone_mgr.compute_angle_to_brts_axis(motion_opp)
        self.assertAlmostEqual(angle_opp, 0.0, places=1)

    def test_brts_angle_perpendicular(self):
        # Crossing the corridor horizontally (making a turn)
        motion = (10.0, 0.0)
        angle = self.zone_mgr.compute_angle_to_brts_axis(motion)
        self.assertIsNotNone(angle)
        self.assertAlmostEqual(angle, 90.0, places=1)

    def test_brts_angle_45_degrees(self):
        # Moving diagonally
        motion = (10.0, 10.0)
        angle = self.zone_mgr.compute_angle_to_brts_axis(motion)
        self.assertIsNotNone(angle)
        self.assertAlmostEqual(angle, 45.0, places=1)


if __name__ == "__main__":
    unittest.main()
