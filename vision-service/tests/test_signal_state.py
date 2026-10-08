"""
test_signal_state.py — Unit tests for traffic signal state reading and debouncing
==================================================================================
Tests classify_head, multi-head fusion, debouncing, and retroactive state lookup (improvements.md § A3.2).
"""

import unittest
import numpy as np

from signals.signal_state import Lamp, HeadROI, classify_head, SignalStateReader


class TestSignalState(unittest.TestCase):
    def _create_synthetic_head(self, lit_lamp: Lamp, h: int = 90, w: int = 30) -> np.ndarray:
        """Create a synthetic 3-aspect vertical signal head image."""
        img = np.zeros((h, w, 3), dtype=np.uint8)
        # Background dark grey housing
        img[:] = (30, 30, 30)

        third_h = h // 3
        # In BGR:
        # Red: (0, 0, 255)
        # Yellow: (0, 255, 255)
        # Green: (0, 255, 0)
        if lit_lamp == Lamp.RED:
            # Top third
            img[5:third_h - 5, 5:w - 5] = (0, 0, 255)
        elif lit_lamp == Lamp.YELLOW:
            # Middle third
            img[third_h + 5:2 * third_h - 5, 5:w - 5] = (0, 255, 255)
        elif lit_lamp == Lamp.GREEN:
            # Bottom third
            img[2 * third_h + 5:h - 5, 5:w - 5] = (0, 255, 0)
        # Lamp.OFF is left all dark
        return img

    def test_classify_head_synthetic_lamps(self):
        roi = HeadROI(head_id="h1", x1=0, y1=0, x2=30, y2=90, orientation="vertical")

        # Test RED
        frame_red = self._create_synthetic_head(Lamp.RED)
        self.assertEqual(classify_head(frame_red, roi), Lamp.RED)

        # Test YELLOW
        frame_yel = self._create_synthetic_head(Lamp.YELLOW)
        self.assertEqual(classify_head(frame_yel, roi), Lamp.YELLOW)

        # Test GREEN
        frame_grn = self._create_synthetic_head(Lamp.GREEN)
        self.assertEqual(classify_head(frame_grn, roi), Lamp.GREEN)

        # Test OFF
        frame_off = self._create_synthetic_head(Lamp.OFF)
        self.assertEqual(classify_head(frame_off, roi), Lamp.OFF)

    def test_debouncing_and_backdating(self):
        roi = HeadROI(head_id="h1", x1=0, y1=0, x2=30, y2=90, orientation="vertical")
        # 10 fps, debounce_s=0.30s -> need 3 consecutive frames
        reader = SignalStateReader(rois=[roi], fps=10.0, debounce_s=0.30)

        frame_red = self._create_synthetic_head(Lamp.RED)
        frame_grn = self._create_synthetic_head(Lamp.GREEN)

        # Frame 1: RED (initial pending)
        s1 = reader.update(frame_red, ts=1.0)
        self.assertEqual(s1, Lamp.UNKNOWN)

        # Frame 2: RED
        s2 = reader.update(frame_red, ts=1.1)
        self.assertEqual(s2, Lamp.UNKNOWN)

        # Frame 3: RED -> threshold reached, state becomes RED!
        s3 = reader.update(frame_red, ts=1.2)
        self.assertEqual(s3, Lamp.RED)
        # Back-dated to first occurrence (ts=1.0)
        self.assertAlmostEqual(reader.state_since_ts, 1.0, places=2)

        # A 1-frame glitch to GREEN should NOT switch state
        s4 = reader.update(frame_grn, ts=1.3)
        self.assertEqual(s4, Lamp.RED)

        # Back to RED
        s5 = reader.update(frame_red, ts=1.4)
        self.assertEqual(s5, Lamp.RED)

    def test_retroactive_state_lookup(self):
        roi = HeadROI(head_id="h1", x1=0, y1=0, x2=30, y2=90, orientation="vertical")
        reader = SignalStateReader(rois=[roi], fps=10.0, debounce_s=0.20)

        frame_red = self._create_synthetic_head(Lamp.RED)
        # Establish RED
        reader.update(frame_red, ts=1.0)
        reader.update(frame_red, ts=1.1)
        reader.update(frame_red, ts=1.2)

        lamp, red_elapsed = reader.state_at(1.15)
        self.assertEqual(lamp, Lamp.RED)
        self.assertIsNotNone(red_elapsed)


if __name__ == "__main__":
    unittest.main()
