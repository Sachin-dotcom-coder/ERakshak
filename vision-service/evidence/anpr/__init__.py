"""
anpr package — Automatic Number Plate Recognition for E-Rakshak evidence
========================================================================
"""

from .format_validator import (
    validate_plate,
    PlateValidationResult,
    correct_ocr_characters,
    sanitize_raw_text,
    INDIAN_STATE_CODES,
)
from .plate_scorer import (
    PlateCropSelector,
    ScoredCrop,
    score_plate_crop,
    compute_sharpness,
)
from .pipeline import ANPRPipeline, PlateReading

__all__ = [
    "validate_plate",
    "PlateValidationResult",
    "correct_ocr_characters",
    "sanitize_raw_text",
    "INDIAN_STATE_CODES",
    "PlateCropSelector",
    "ScoredCrop",
    "score_plate_crop",
    "compute_sharpness",
    "ANPRPipeline",
    "PlateReading",
]
