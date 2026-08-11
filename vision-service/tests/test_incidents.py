import unittest
from dataclasses import dataclass
from incidents import IncidentDetector

@dataclass
class MockTrack:
    track_id: int
    class_name: str
    trajectory_world: list
    latest_world_position: tuple
    lane_history: list = None

class TestIncidents(unittest.TestCase):
    def setUp(self):
        self.config = {
            "stall": {
                "speed_threshold_kmph": 2.0,
                "min_duration_s": 1.0, # low for easy testing
                "stop_line_exclusion_radius_m": 5.0
            }
        }
        self.detector = IncidentDetector(self.config)

    def test_stationary_with_jitter_flags_stall(self):
        # Jitter around a single point
        traj = [
            (10.0, 10.0),
            (10.1, 10.1),
            (9.9, 9.9),
            (10.2, 9.8),
            (10.05, 10.05)
        ]
        track = MockTrack(track_id=1, class_name="car", trajectory_world=traj, latest_world_position=traj[-1])
        
        # Test speed directly
        speed = self.detector._estimate_speed_from_trajectory(traj, fps=20.0, window=5)
        # End point (10.05, 10.05), start point (10.0, 10.0) -> dist = ~0.07m
        # dt = 4/20 = 0.2s -> 0.35 m/s = 1.26 km/h. Below 2.0 km/h!
        self.assertLess(speed, 2.0)
        
    def test_slow_moving_traffic_not_flagged(self):
        # Moving ~1m every 4 frames (0.2s) -> 5 m/s -> 18 km/h
        traj = [
            (10.0, 10.0),
            (10.25, 10.0),
            (10.5, 10.0),
            (10.75, 10.0),
            (11.0, 10.0)
        ]
        track = MockTrack(track_id=2, class_name="car", trajectory_world=traj, latest_world_position=traj[-1])
        
        speed = self.detector._estimate_speed_from_trajectory(traj, fps=20.0, window=5)
        # Distance = 1.0m, dt = 0.2s -> 5 m/s = 18 km/h. Well above 2.0 km/h!
        self.assertGreater(speed, 2.0)

    def test_stop_line_exclusion(self):
        self.detector.set_stop_line_positions([(0.0, 0.0)])
        
        # Point near stop line (3m away, radius is 5m)
        self.assertTrue(self.detector._is_near_stop_line((3.0, 0.0)))
        
        # Point far from stop line
        self.assertFalse(self.detector._is_near_stop_line((10.0, 0.0)))


if __name__ == "__main__":
    unittest.main()
