import unittest
from dataclasses import dataclass
from violations import ViolationDetector

@dataclass
class MockTrack:
    track_id: int
    class_name: str
    lane_history: list
    confidence: float = 0.9

class MockZoneManager:
    has_brts_corridor = False

class TestViolations(unittest.TestCase):
    def setUp(self):
        self.config = {
            "lane_change": {
                "min_dwell_frames": 10
            }
        }
        self.vd = ViolationDetector(self.config, MockZoneManager())

    def test_consecutive_frames_with_flicker(self):
        # Vehicle starts in lane_1
        track = MockTrack(track_id=1, class_name="car", lane_history=["lane_1"])
        
        # Establish lane_1
        self.vd.check([track], fps=20.0, current_timestamp="2026")
        
        # Move to lane_2 for 5 frames
        for _ in range(5):
            track.lane_history.append("lane_2")
            violations, _ = self.vd.check([track], fps=20.0, current_timestamp="2026")
            self.assertEqual(len(violations), 0)
        
        # Flicker out of lane (None) for 2 frames
        for _ in range(2):
            track.lane_history.append(None)
            violations, _ = self.vd.check([track], fps=20.0, current_timestamp="2026")
            self.assertEqual(len(violations), 0)
            
        # Re-enter lane_2 for 5 more frames.
        # Since we modified the logic to NOT reset on None, the total frames in lane_2
        # will hit 5 + 5 = 10 and flag a violation.
        violation_flagged = False
        for _ in range(5):
            track.lane_history.append("lane_2")
            violations, _ = self.vd.check([track], fps=20.0, current_timestamp="2026")
            if len(violations) > 0:
                violation_flagged = True
                
        self.assertTrue(violation_flagged, "Flicker to None should not reset dwell counter")

    def test_real_reentry_resets_counter(self):
        # Vehicle establishes in lane_1
        track = MockTrack(track_id=2, class_name="car", lane_history=["lane_1"])
        self.vd.check([track], fps=20.0, current_timestamp="2026")
        
        # Move to lane_2 for 5 frames
        for _ in range(5):
            track.lane_history.append("lane_2")
            self.vd.check([track], fps=20.0, current_timestamp="2026")
            
        # Back to original lane_1
        track.lane_history.append("lane_1")
        self.vd.check([track], fps=20.0, current_timestamp="2026")
        
        # Now move to lane_2 again for 5 frames
        for _ in range(5):
            track.lane_history.append("lane_2")
            violations, _ = self.vd.check([track], fps=20.0, current_timestamp="2026")
            self.assertEqual(len(violations), 0, "Counter should have reset after re-entering lane_1")


if __name__ == "__main__":
    unittest.main()
