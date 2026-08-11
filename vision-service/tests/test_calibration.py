import unittest
import numpy as np
from calibration.homography import CameraCalibrator


class TestCalibration(unittest.TestCase):
    def setUp(self):
        # A simple square 10x10 meters mapped to a 100x100 pixel square
        self.config = {
            "fps": 20.0,
            "pixel_points": [
                [0, 0],
                [100, 0],
                [100, 100],
                [0, 100]
            ],
            "world_points": [
                [0.0, 0.0],
                [10.0, 0.0],
                [10.0, 10.0],
                [0.0, 10.0]
            ],
            "stop_line_world": [5.0, 5.0]
        }
        self.calibrator = CameraCalibrator(self.config)

    def test_bottom_center_projection(self):
        # Bbox: [x1, y1, x2, y2]
        # x1=10, y1=10, x2=30, y2=50 -> bottom center is x=20, y=50
        bbox = np.array([10, 10, 30, 50])
        
        world_pt = self.calibrator.project_ground_contact(bbox)
        self.assertIsNotNone(world_pt)
        
        # Expected world pt: x=2.0, y=5.0
        expected_x = 2.0
        expected_y = 5.0
        
        self.assertAlmostEqual(world_pt[0], expected_x, places=2)
        self.assertAlmostEqual(world_pt[1], expected_y, places=2)
        
        # If it incorrectly used centroid, it would be x=20, y=30 -> world y=3.0
        # Assert it's NOT 3.0 to explicitly prove it's using bottom-center
        self.assertNotAlmostEqual(world_pt[1], 3.0, places=2)

    def test_round_trip_projection(self):
        # Project pixel to world and back
        px_original, py_original = 45.0, 60.0
        world_pt = self.calibrator.pixel_to_world(px_original, py_original)
        self.assertIsNotNone(world_pt)
        
        px_recovered, py_recovered = self.calibrator.world_to_pixel(*world_pt)
        
        self.assertAlmostEqual(px_original, px_recovered, places=3)
        self.assertAlmostEqual(py_original, py_recovered, places=3)

    def test_speed_computation_cancels_jitter(self):
        # A stationary vehicle with tracking jitter
        # Starts at (5.0, 5.0), jitters back and forth, ends at (5.1, 5.1)
        trajectory = [
            (5.0, 5.0),
            (5.2, 5.2),
            (4.8, 4.8),
            (5.3, 5.3),
            (5.1, 5.1)
        ]
        
        # Old bug: sum of step distances:
        # 5.0->5.2 = 0.28m
        # 5.2->4.8 = 0.56m
        # 4.8->5.3 = 0.70m
        # 5.3->5.1 = 0.28m
        # Total = 1.82m
        # Time = 4 frames / 20 fps = 0.2s
        # Speed = 1.82 / 0.2 * 3.6 = ~32 km/h (huge false positive)
        
        # New correct math: straight line from (5.0, 5.0) to (5.1, 5.1)
        # Dist = sqrt(0.1^2 + 0.1^2) = 0.141m
        # Speed = 0.141 / 0.2 * 3.6 = ~2.5 km/h (much more realistic for jitter)
        
        speed = self.calibrator.compute_speed(trajectory, fps=20.0, smoothing_window=5)
        self.assertIsNotNone(speed)
        
        expected_dist = np.sqrt(0.1**2 + 0.1**2)
        expected_speed_mps = expected_dist / (4 / 20.0)
        expected_speed_kmph = expected_speed_mps * 3.6
        
        self.assertAlmostEqual(speed, expected_speed_kmph, places=2)


if __name__ == "__main__":
    unittest.main()
