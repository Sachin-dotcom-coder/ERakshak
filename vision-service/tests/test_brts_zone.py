"""
test_brts_zone.py — Unit tests for BRTS zone footprint & overlap tests
======================================================================
Tests footprint extraction, overlap_ratio, and ground_point_inside.
Validates Section B4 in improvements.md:
- Fully inside vehicle has overlap = 1.0
- Straddling vehicle has fractional overlap
- Tall vehicle leaning across barrier with wheels outside fails ground_point_inside / overlap criteria
"""

import unittest
from shapely.geometry import Polygon
from zones.brts_zone import footprint, overlap_ratio, ground_point_inside, ZoneAssigner


class TestBRTSZone(unittest.TestCase):
    def setUp(self):
        # BRTS corridor polygon: x from 0 to 100, y from 0 to 200
        self.brts_poly = Polygon([(0, 0), (100, 0), (100, 200), (0, 200)])
        self.assigner = ZoneAssigner(
            zone_poly=self.brts_poly,
            zone_id="BRTS_CORRIDOR",
            enter_ratio=0.50,
            exit_ratio=0.20,
            n_enter=3,
            n_exit=4,
        )

    def test_vehicle_fully_inside(self):
        # Box inside: x in [20, 60], y in [50, 100]
        bbox = (20, 50, 60, 100)
        self.assertTrue(ground_point_inside(bbox, self.brts_poly))
        self.assertAlmostEqual(overlap_ratio(bbox, self.brts_poly), 1.0, places=3)

    def test_vehicle_fully_outside(self):
        # Box in adjacent lane: x in [120, 160], y in [50, 100]
        bbox = (120, 50, 160, 100)
        self.assertFalse(ground_point_inside(bbox, self.brts_poly))
        self.assertAlmostEqual(overlap_ratio(bbox, self.brts_poly), 0.0, places=3)

    def test_straddling_vehicle_fractional_overlap(self):
        # Box centered on right edge (x=100): x in [80, 120]
        bbox = (80, 50, 120, 100)
        ratio = overlap_ratio(bbox, self.brts_poly)
        self.assertGreater(ratio, 0.2)
        self.assertLess(ratio, 0.8)

    def test_leaning_tall_vehicle_wheels_in_lane1(self):
        # Wheels are in Lane 1 (ground point at x=110, outside BRTS x <= 100)
        # Even if box top/side reaches x=95, wheels touch road in Lane 1
        bbox = (95, 20, 125, 100)
        # Ground point is (110, 100) -> outside BRTS
        self.assertFalse(ground_point_inside(bbox, self.brts_poly))
        # Overlap ratio should be small
        ratio = overlap_ratio(bbox, self.brts_poly)
        self.assertLess(ratio, 0.50)

    def test_zone_assigner_hysteresis(self):
        # Test enter/exit hysteresis with consecutive frames
        inside_bbox = (20, 50, 60, 100)
        outside_bbox = (120, 50, 160, 100)

        # Needs n_enter = 3 consecutive frames to confirm inside
        self.assertFalse(self.assigner.is_inside(1, inside_bbox))
        self.assertFalse(self.assigner.is_inside(1, inside_bbox))
        self.assertTrue(self.assigner.is_inside(1, inside_bbox))  # 3rd frame: inside

        # Stay inside
        self.assertTrue(self.assigner.is_inside(1, inside_bbox))

        # Leaving needs n_exit = 4 consecutive frames
        self.assertTrue(self.assigner.is_inside(1, outside_bbox))
        self.assertTrue(self.assigner.is_inside(1, outside_bbox))
        self.assertTrue(self.assigner.is_inside(1, outside_bbox))
        self.assertFalse(self.assigner.is_inside(1, outside_bbox))  # 4th frame: out


if __name__ == "__main__":
    unittest.main()
