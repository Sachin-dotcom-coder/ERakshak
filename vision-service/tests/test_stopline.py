"""
test_stopline.py — Unit tests for stop-line geometry and crossing tests
========================================================================
Tests signed_dist, within_segment, crossing_time, and StopLine hysteresis.
Covers Section A4.2 and A12.1 in improvements.md.
"""

import unittest
import numpy as np
from violations.stopline import signed_dist, within_segment, crossing_time, StopLine


class TestStopLineGeometry(unittest.TestCase):
    def setUp(self):
        # Directed line along X axis from (0, 10) to (10, 10)
        self.a = (0.0, 10.0)
        self.b = (10.0, 10.0)
        self.sl = StopLine(self.a, self.b, travel_sign=1, hysteresis_m=0.3, margin_m=0.5)

    def test_signed_dist_signs(self):
        # A directed line from (0,10) to (10,10): d = (10, 0)
        # Point (5, 15) is to the left of the line (positive y)
        d_pos = signed_dist((5.0, 15.0), self.a, self.b)
        self.assertGreater(d_pos, 0.0)
        self.assertAlmostEqual(d_pos, 5.0, places=3)

        # Point (5, 5) is to the right of the line (negative y)
        d_neg = signed_dist((5.0, 5.0), self.a, self.b)
        self.assertLess(d_neg, 0.0)
        self.assertAlmostEqual(d_neg, -5.0, places=3)

        # Point on the line
        d_zero = signed_dist((5.0, 10.0), self.a, self.b)
        self.assertAlmostEqual(d_zero, 0.0, places=5)

    def test_within_segment_gating(self):
        # (5, 12) projects to middle of (0,10)->(10,10)
        self.assertTrue(within_segment((5.0, 12.0), self.a, self.b))

        # (10.3, 12) is within margin_m = 0.5
        self.assertTrue(within_segment((10.3, 12.0), self.a, self.b, margin_m=0.5))

        # (15.0, 12) is far beyond the segment endpoint (cross street traffic)
        self.assertFalse(within_segment((15.0, 12.0), self.a, self.b, margin_m=0.5))

        # (-2.0, 12) is beyond the other end
        self.assertFalse(within_segment((-2.0, 12.0), self.a, self.b, margin_m=0.5))

    def test_crossing_time_interpolation(self):
        # Frame 0: t=1.00s, d=+1.0m
        # Frame 1: t=1.04s, d=-1.0m
        # Line is at d=0, so crossing should be exactly halfway (1.02s)
        t_cross = crossing_time(1.00, 1.0, 1.04, -1.0)
        self.assertAlmostEqual(t_cross, 1.02, places=4)

        # Unequal distances: d0=+0.3, d1=-0.9 -> cross at t0 + (1/4)*(t1 - t0)
        t_cross2 = crossing_time(2.00, 0.3, 2.04, -0.9)
        self.assertAlmostEqual(t_cross2, 2.01, places=4)

    def test_hysteresis_state_classification(self):
        # d >= +0.3 is before
        self.assertEqual(self.sl.side((5.0, 10.5)), "before")
        # d <= -0.3 is past
        self.assertEqual(self.sl.side((5.0, 9.5)), "past")
        # -0.3 < d < 0.3 is ambiguous
        self.assertEqual(self.sl.side((5.0, 10.1)), "ambiguous")
        self.assertEqual(self.sl.side((5.0, 9.9)), "ambiguous")


if __name__ == "__main__":
    unittest.main()
