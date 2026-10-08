"""
test_anpr.py — Unit tests for ANPR plate scoring, format validation, and pipeline
================================================================================
Validates Indian registration plate format checks and OCR corrections (improvements.md § A7.2, B8).
"""

import unittest
import numpy as np

from evidence.anpr.format_validator import (
    validate_plate,
    correct_ocr_characters,
    sanitize_raw_text,
)
from evidence.anpr.plate_scorer import (
    score_plate_crop,
    compute_sharpness,
    PlateCropSelector,
)
from evidence.anpr.pipeline import ANPRPipeline


class TestANPR(unittest.TestCase):
    def test_sanitize_and_standard_plates(self):
        # Valid Gujarat plate
        res1 = validate_plate("GJ 05 XX 1234")
        self.assertTrue(res1.is_valid)
        self.assertEqual(res1.cleaned_plate, "GJ05XX1234")
        self.assertEqual(res1.state_code, "GJ")
        self.assertFalse(res1.is_bharat_series)

        # Valid Maharashtra plate
        res2 = validate_plate("mh-12-ab-5678")
        self.assertTrue(res2.is_valid)
        self.assertEqual(res2.cleaned_plate, "MH12AB5678")
        self.assertEqual(res2.state_code, "MH")

    def test_bharat_series_plate(self):
        # Valid BH plate: 22BH1234AA
        res = validate_plate("22 BH 1234 AA")
        self.assertTrue(res.is_valid)
        self.assertEqual(res.cleaned_plate, "22BH1234AA")
        self.assertTrue(res.is_bharat_series)

    def test_ocr_character_correction(self):
        # State letters OCR'd as numbers: "0J05XX1234" -> "GJ05XX1234" (0 -> O, or G)
        # RTO digits OCR'd as letters: "GJO5XX1234" -> 'O' at index 2 should become '0'
        corrected = correct_ocr_characters("GJO5XX1234")
        self.assertEqual(corrected, "GJ05XX1234")

        # Number digits OCR'd as letters: "GJ05XXI234" -> 'I' at number pos should become '1'
        res = validate_plate("GJ05XXI234")
        self.assertTrue(res.is_valid)
        self.assertEqual(res.cleaned_plate, "GJ05XX1234")

    def test_invalid_plate(self):
        res = validate_plate("INVALID123")
        self.assertFalse(res.is_valid)

    def test_plate_scorer_prefers_sharp_wide_crops(self):
        # Sharp synthetic crop
        sharp_img = np.zeros((30, 90, 3), dtype=np.uint8)
        sharp_img[::2, ::2] = 255  # high frequency checkerboard
        sharp_score = score_plate_crop(sharp_img)

        # Blurry synthetic crop (flat)
        flat_img = np.ones((30, 90, 3), dtype=np.uint8) * 128
        flat_score = score_plate_crop(flat_img)

        self.assertGreater(sharp_score, flat_score)

        # Selector ranks higher
        selector = PlateCropSelector()
        selector.add_candidate(flat_img, frame_idx=1, ts=1.0)
        selector.add_candidate(sharp_img, frame_idx=2, ts=1.1)

        best = selector.get_best()
        self.assertIsNotNone(best)
        self.assertEqual(best.frame_idx, 2)

    def test_anpr_pipeline_with_mock_ocr(self):
        selector = PlateCropSelector()
        img = np.ones((40, 120, 3), dtype=np.uint8) * 200
        selector.add_candidate(img, frame_idx=10, ts=5.0)

        mock_ocr = lambda crop: ("GJ05XX1234", 0.90)
        pipeline = ANPRPipeline(ocr_fn=mock_ocr)
        reading = pipeline.extract_plate(selector)

        self.assertEqual(reading.text, "GJ05XX1234")
        self.assertTrue(reading.is_valid_format)
        self.assertEqual(reading.state_code, "GJ")
        self.assertGreater(reading.confidence, 0.5)


if __name__ == "__main__":
    unittest.main()
