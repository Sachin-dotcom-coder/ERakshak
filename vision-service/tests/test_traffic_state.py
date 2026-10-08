"""
test_traffic_state.py — Tests for Traffic State Analytics (Sprint 5, Sections 40-48)
"""

import unittest
import numpy as np
from traffic_state.queue import QueueEstimator
from traffic_state.speed import SpeedEstimator
from traffic_state.pcu import PCUCalculator
from traffic_state.density import DensityEstimator
from traffic_state.shockwave import ShockwaveAnalyzer


class TestTrafficState(unittest.TestCase):

    def setUp(self):
        self.queue_estimator = QueueEstimator({
            "speed_threshold_kmph": 5.0,
            "probability_threshold": 0.70,
            "weights": {
                "low_speed": 0.30,
                "stop_line_distance": 0.20,
                "red_signal": 0.20,
                "following_density": 0.15,
                "stop_duration": 0.15,
            }
        })
        self.speed_estimator = SpeedEstimator({"fast_window_frames": 3, "slow_window_frames": 10})
        self.pcu_calculator = PCUCalculator()
        self.density_estimator = DensityEstimator({"critical_density": 80.0, "jam_density": 150.0})
        self.shockwave_analyzer = ShockwaveAnalyzer()

    def test_queue_probability(self):
        # Stopped vehicle close to stop line with red light should have high probability
        prob_high = self.queue_estimator.compute_queue_probability(
            track_id=1,
            speed_kmph=1.0,
            distance_to_stop_m=5.0,
            signal_is_red=True,
            nearby_vehicle_count=4,
        )
        self.assertGreater(prob_high, 0.6)

        # Fast vehicle far away should have low probability
        prob_low = self.queue_estimator.compute_queue_probability(
            track_id=2,
            speed_kmph=50.0,
            distance_to_stop_m=80.0,
            signal_is_red=False,
            nearby_vehicle_count=0,
        )
        self.assertLess(prob_low, 0.3)

    def test_pcu_calculation(self):
        vehicles = [
            {"class_name": "car", "detection_confidence": 0.9},
            {"class_name": "bus", "detection_confidence": 0.8},
            {"class_name": "two_wheeler", "detection_confidence": 0.95},
        ]
        pcu_weighted, pcu_raw = self.pcu_calculator.compute_lane_pcu(vehicles)
        # Raw: car(1.0) + bus(3.0) + two_wheeler(0.5) = 4.5
        self.assertAlmostEqual(pcu_raw, 4.5, places=2)
        # Weighted: 1.0*0.9 + 3.0*0.8 + 0.5*0.95 = 0.9 + 2.4 + 0.475 = 3.775
        self.assertAlmostEqual(pcu_weighted, 3.775, places=2)

    def test_density_estimation(self):
        res = self.density_estimator.compute_density(lane_id="lane_1", vehicle_count=10, pcu_total=12.0)
        self.assertIn("linear_density_per_100m", res)
        self.assertIn("congestion_level", res)
        self.assertGreater(res["linear_density_per_100m"], 0.0)

    def test_speed_estimator(self):
        traj = [(0.0, 0.0), (0.0, 5.0), (0.0, 10.0), (0.0, 15.0)]
        speed, accel, confidence = self.speed_estimator.estimate_speed(1, traj)
        self.assertGreater(speed, 0.0)
        self.assertGreater(confidence, 0.0)


if __name__ == "__main__":
    unittest.main()
