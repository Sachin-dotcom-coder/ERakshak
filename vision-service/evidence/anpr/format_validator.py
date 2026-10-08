"""
format_validator.py — Indian Vehicle Registration Plate Format Validator
========================================================================
Validates and standardizes vehicle registration numbers against Indian MoRTH standards:
- Standard format: State code (2 letters) + RTO code (1-2 digits) + Series (0-3 letters) + Number (4 digits)
  Examples: GJ05XX1234, DL01AB1234, MH12C1234, KA031234
- Bharat Series (BH): Year (2 digits) + 'BH' + Number (4 digits) + Series (1-2 letters)
  Example: 22BH1234AA
- Also applies contextual character substitution for common OCR confusions:
  - Letters position: '0' -> 'O', '1' -> 'I', '8' -> 'B', '5' -> 'S'
  - Digits position: 'O' -> '0', 'I' -> '1', 'B' -> '8', 'S' -> '5', 'Z' -> '2'
"""

import re
from typing import Optional, NamedTuple


INDIAN_STATE_CODES = frozenset({
    "AN", "AP", "AR", "AS", "BR", "CH", "CG", "DD", "DL", "DN",
    "GA", "GJ", "HR", "HP", "JH", "JK", "KA", "KL", "LA", "LD",
    "MH", "ML", "MN", "MP", "MZ", "NL", "OD", "PB", "PY", "RJ",
    "SK", "TN", "TR", "TS", "UK", "UP", "WB"
})

STANDARD_PLATE_REGEX = re.compile(r"^([A-Z]{2})([0-9]{1,2})([A-Z]{0,3})([0-9]{4})$")
BHARAT_SERIES_REGEX = re.compile(r"^([0-9]{2})(BH)([0-9]{4})([A-Z]{1,2})$")


class PlateValidationResult(NamedTuple):
    is_valid: bool
    cleaned_plate: Optional[str]
    state_code: Optional[str]
    is_bharat_series: bool
    confidence_score: float
    error_reason: str


def sanitize_raw_text(raw_text: str) -> str:
    """Removes spaces, hyphens, and non-alphanumeric characters and converts to uppercase."""
    return re.sub(r"[^A-Za-z0-9]", "", raw_text).upper()


def correct_ocr_characters(plate: str) -> str:
    """
    Attempts to fix common OCR character confusions based on expected Indian plate layout:
    Chars 0-1: State letters (e.g. GJ)
    Chars 2-3: RTO digits (e.g. 05)
    Last 4 chars: Registration number digits (e.g. 1234)
    """
    if len(plate) < 8 or len(plate) > 10:
        return plate

    to_letter = {'0': 'O', '1': 'I', '8': 'B', '5': 'S', '2': 'Z'}
    to_digit = {'O': '0', 'I': '1', 'B': '8', 'S': '5', 'Z': '2', 'Q': '0', 'D': '0'}

    chars = list(plate)

    # State code: first 2 characters should be letters
    for i in (0, 1):
        if chars[i] in to_letter:
            chars[i] = to_letter[chars[i]]

    # RTO code: chars 2 and 3 usually digits
    if len(chars) >= 4:
        if chars[2] in to_digit:
            chars[2] = to_digit[chars[2]]
        if chars[3] in to_digit:
            chars[3] = to_digit[chars[3]]

    # Last 4 characters should be digits
    for i in range(len(chars) - 4, len(chars)):
        if chars[i] in to_digit:
            chars[i] = to_digit[chars[i]]

    return "".join(chars)


def validate_plate(raw_text: str) -> PlateValidationResult:
    """
    Validates and cleans an Indian vehicle license plate string.
    Returns PlateValidationResult.
    """
    if not raw_text or not raw_text.strip():
        return PlateValidationResult(
            is_valid=False,
            cleaned_plate=None,
            state_code=None,
            is_bharat_series=False,
            confidence_score=0.0,
            error_reason="Empty plate string",
        )

    sanitized = sanitize_raw_text(raw_text)

    # Check direct match with standard format
    m_std = STANDARD_PLATE_REGEX.match(sanitized)
    if m_std:
        state, rto, series, number = m_std.groups()
        if state in INDIAN_STATE_CODES:
            return PlateValidationResult(
                is_valid=True,
                cleaned_plate=sanitized,
                state_code=state,
                is_bharat_series=False,
                confidence_score=0.95,
                error_reason="",
            )

    # Check direct match with Bharat series
    m_bh = BHARAT_SERIES_REGEX.match(sanitized)
    if m_bh:
        return PlateValidationResult(
            is_valid=True,
            cleaned_plate=sanitized,
            state_code="BH",
            is_bharat_series=True,
            confidence_score=0.95,
            error_reason="",
        )

    # Try applying OCR corrections
    corrected = correct_ocr_characters(sanitized)
    m_std_corr = STANDARD_PLATE_REGEX.match(corrected)
    if m_std_corr:
        state, rto, series, number = m_std_corr.groups()
        if state in INDIAN_STATE_CODES:
            return PlateValidationResult(
                is_valid=True,
                cleaned_plate=corrected,
                state_code=state,
                is_bharat_series=False,
                confidence_score=0.80,  # Lower confidence due to correction
                error_reason="Corrected OCR confusions",
            )

    m_bh_corr = BHARAT_SERIES_REGEX.match(corrected)
    if m_bh_corr:
        return PlateValidationResult(
            is_valid=True,
            cleaned_plate=corrected,
            state_code="BH",
            is_bharat_series=True,
            confidence_score=0.80,
            error_reason="Corrected OCR confusions",
        )

    return PlateValidationResult(
        is_valid=False,
        cleaned_plate=sanitized,
        state_code=None,
        is_bharat_series=False,
        confidence_score=0.30,
        error_reason="Plate does not match Indian registration format",
    )
