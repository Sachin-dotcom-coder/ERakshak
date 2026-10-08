"""
pipeline.py — End-to-End ANPR Pipeline
======================================
Executes plate localization, scoring, OCR, and Indian registration format validation.
If dedicated OCR engine (e.g. pytesseract / EasyOCR) is not installed, uses
heuristic fallback or mock hook for continuous integration and deterministic unit tests.
(improvements.md § A7.2, B8)
"""

import logging
from dataclasses import dataclass
from typing import Optional, Callable
import cv2
import numpy as np

from .format_validator import validate_plate, PlateValidationResult
from .plate_scorer import PlateCropSelector, ScoredCrop

logger = logging.getLogger(__name__)


@dataclass
class PlateReading:
    text: Optional[str]
    confidence: float
    is_valid_format: bool
    state_code: Optional[str]
    crop_bgr: Optional[np.ndarray]
    ts: Optional[float]


class ANPRPipeline:
    """
    ANPR Pipeline for vehicle tracks:
    1. Collects candidate crops from the track's bounding box or dedicated plate detector
    2. Selects the sharpest, highest-resolution crop
    3. Runs OCR
    4. Validates and normalizes against Indian vehicle registration format
    """

    def __init__(self, ocr_fn: Optional[Callable[[np.ndarray], tuple[str, float]]] = None):
        self._ocr_fn = ocr_fn

    def extract_plate(self, selector: PlateCropSelector) -> PlateReading:
        best_crop = selector.get_best()
        if best_crop is None:
            return PlateReading(
                text=None,
                confidence=0.0,
                is_valid_format=False,
                state_code=None,
                crop_bgr=None,
                ts=None,
            )

        # Run OCR
        raw_text, ocr_conf = self._run_ocr(best_crop.crop_bgr)
        if not raw_text:
            return PlateReading(
                text=None,
                confidence=0.0,
                is_valid_format=False,
                state_code=None,
                crop_bgr=best_crop.crop_bgr,
                ts=best_crop.ts,
            )

        val_result: PlateValidationResult = validate_plate(raw_text)
        final_conf = round(float(ocr_conf * val_result.confidence_score * (0.5 + 0.5 * best_crop.score)), 2)

        return PlateReading(
            text=val_result.cleaned_plate if val_result.is_valid else raw_text,
            confidence=min(1.0, max(0.0, final_conf)),
            is_valid_format=val_result.is_valid,
            state_code=val_result.state_code,
            crop_bgr=best_crop.crop_bgr,
            ts=best_crop.ts,
        )

    def _run_ocr(self, crop: np.ndarray) -> tuple[str, float]:
        if self._ocr_fn is not None:
            return self._ocr_fn(crop)

        # Check if pytesseract is available
        try:
            import pytesseract
            gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
            # Resize and threshold for better OCR
            resized = cv2.resize(gray, (0, 0), fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)
            thresh = cv2.adaptiveThreshold(
                resized, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
            config = "--psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
            text = pytesseract.image_to_string(thresh, config=config).strip()
            return text, 0.85
        except Exception:
            # Fallback when pytesseract/tesseract binary not installed on host
            return "", 0.0
