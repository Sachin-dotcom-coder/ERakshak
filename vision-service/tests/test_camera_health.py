"""
test_camera_health.py — Tests for Camera Health & Calibration Validation (Sprint 7, Sections 28-33)
"""

import unittest
import numpy as np
from camera.health import CameraHealthMonitor
from camera.quality import FrameQualityAssessor
from camera.visibility import VisibilityEstimator
from calibration.calibration_validator import CalibrationValidator
from calibration.camera_shift import CameraShiftDetector


class TestCameraHealth(unittest.TestCase):

    def setUp(self):
        self.health_monitor = CameraHealthMonitor({})
        self.quality_assessor = FrameQualityAssessor()
        self.visibility_estimator = VisibilityEstimator()
        self.calibration_validator = CalibrationValidator()

    def test_camera_health_normal_frame(self):
        # Create a frame with texture (not blurry, not frozen)
        frame = np.random.randint(50, 200, (480, 640, 3), dtype=np.uint8)
        res = self.health_monitor.analyze(frame)
        self.assertIn("health_score", res)
        self.assertIn("blur_score", res)
        self.assertFalse(res["is_frozen"])

    def test_camera_freeze_detection(self):
        # Send identical frames repeatedly
        frame = np.zeros((100, 100, 3), dtype=np.uint8)
        for _ in range(35):
            res = self.health_monitor.analyze(frame)
        self.assertTrue(res["is_frozen"])

    def test_visibility_estimation(self):
        frame = np.full((100, 100, 3), 128, dtype=np.uint8)
        res = self.visibility_estimator.estimate(frame)
        self.assertIn("visibility_score", res)
        self.assertIn("condition", res)

    def test_calibration_validator(self):
        res = self.calibration_validator.validate(camera_health=0.95, landmark_displacements=[2.0])
        self.assertTrue(res["calibration_valid"])
        self.assertGreater(res["homography_health"], 0.8)


if __name__ == "__main__":
    unittest.main()
