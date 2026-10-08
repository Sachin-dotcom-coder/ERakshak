"""
test_confidence.py — Tests for Confidence & Uncertainty Estimation (Sprint 8, Sections 49-53, 71-73)
"""

import unittest
from confidence.object_confidence import ObjectConfidenceEstimator
from confidence.scene_confidence import SceneConfidenceEstimator
from confidence.uncertainty import UncertaintyPropagator
from confidence.calibration import ConfidenceCalibrator


class TestConfidence(unittest.TestCase):

    def setUp(self):
        self.obj_conf = ObjectConfidenceEstimator()
        self.scene_conf = SceneConfidenceEstimator()
        self.uncertainty = UncertaintyPropagator()
        self.calibrator = ConfidenceCalibrator()

    def test_object_confidence(self):
        res = self.obj_conf.compute(
            detection_confidence=0.9,
            track_quality=0.85,
            class_stability=0.95,
            occlusion_ratio=0.1,
            age_frames=40,
        )
        self.assertIn("composite_confidence", res)
        self.assertGreater(res["composite_confidence"], 0.7)

    def test_scene_confidence(self):
        res = self.scene_conf.compute_scene_confidence(
            detection_quality=0.88,
            tracking_quality=0.82,
            camera_health=0.95,
            calibration_health=0.90,
            visibility=0.85,
        )
        self.assertIn("scene_confidence", res)
        self.assertFalse(res["cautious_mode"])

    def test_uncertainty_propagation(self):
        # Effective queue length = raw * confidence
        res = self.uncertainty.apply_confidence(
            lane_id="lane_1",
            queue_length=50.0,
            queue_confidence=0.8,
            pcu=10.0,
            pcu_confidence=0.9,
            avg_speed=30.0,
            speed_confidence=0.85,
        )
        self.assertAlmostEqual(res["queue_effective_m"], 40.0, places=1)


if __name__ == "__main__":
    unittest.main()
