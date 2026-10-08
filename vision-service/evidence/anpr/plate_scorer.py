"""
plate_scorer.py — Plate crop scoring & selection
=================================================
Selects the best frame for plate reading from a tracked vehicle's trajectory,
scoring by width in pixels, sharpness (Laplacian variance), and aspect ratio.
(improvements.md § A7.2)
"""

from dataclasses import dataclass
from typing import Optional
import cv2
import numpy as np


@dataclass
class ScoredCrop:
    crop_bgr: np.ndarray
    frame_idx: int
    ts: float
    score: float
    sharpness: float
    width_px: int
    aspect_ratio: float


def compute_sharpness(img_bgr: np.ndarray) -> float:
    """Computes image sharpness using the variance of the Laplacian."""
    if img_bgr is None or img_bgr.size == 0:
        return 0.0
    if len(img_bgr.shape) == 3:
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    else:
        gray = img_bgr
    return float(cv2.Laplacian(gray, cv2.CV_64F).var())


def score_plate_crop(crop_bgr: np.ndarray, target_aspect: float = 3.0) -> float:
    """
    Computes a composite score [0, 1] for a candidate plate crop.
    - Width factor: >= 100px is ideal, penalized below 60px.
    - Sharpness factor: variance of Laplacian (> 100 is sharp).
    - Aspect ratio: penalty for extreme non-rectangular crops.
    """
    if crop_bgr is None or crop_bgr.size == 0:
        return 0.0

    h, w = crop_bgr.shape[:2]
    if h < 8 or w < 20:
        return 0.0

    # 1. Width score (0.0 to 1.0)
    w_score = min(1.0, max(0.0, (w - 20) / 100.0))

    # 2. Sharpness score (0.0 to 1.0)
    sharpness = compute_sharpness(crop_bgr)
    sharp_score = min(1.0, max(0.0, sharpness / 200.0))

    # 3. Aspect ratio score (0.0 to 1.0)
    aspect = w / float(h)
    aspect_diff = abs(aspect - target_aspect)
    aspect_score = max(0.2, 1.0 - (aspect_diff / 3.0))

    # Composite weighted score
    return 0.45 * sharp_score + 0.35 * w_score + 0.20 * aspect_score


class PlateCropSelector:
    """
    Maintains candidate plate crops for a tracked vehicle and returns
    the highest quality crop for OCR.
    """

    def __init__(self, max_candidates: int = 10):
        self.max_candidates = max_candidates
        self.candidates: list[ScoredCrop] = []

    def add_candidate(self, crop_bgr: np.ndarray, frame_idx: int, ts: float):
        if crop_bgr is None or crop_bgr.size == 0:
            return

        h, w = crop_bgr.shape[:2]
        sharpness = compute_sharpness(crop_bgr)
        aspect = w / float(max(1, h))
        score = score_plate_crop(crop_bgr)

        scored = ScoredCrop(
            crop_bgr=crop_bgr,
            frame_idx=frame_idx,
            ts=ts,
            score=score,
            sharpness=sharpness,
            width_px=w,
            aspect_ratio=aspect,
        )

        self.candidates.append(scored)
        # Keep top candidates sorted by score
        self.candidates.sort(key=lambda c: c.score, reverse=True)
        if len(self.candidates) > self.max_candidates:
            self.candidates.pop()

    def get_best(self) -> Optional[ScoredCrop]:
        if not self.candidates:
            return None
        return self.candidates[0]
