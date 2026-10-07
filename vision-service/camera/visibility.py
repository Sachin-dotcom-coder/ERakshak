"""
camera/visibility.py — Visibility Estimation (Section 64-65)
==============================================================
Estimates scene visibility from image statistics for downstream
confidence scoring and preprocessing dispatch.

Detects: rain, fog, haze, glare conditions.
"""

import logging
from typing import Optional

import cv2
import numpy as np

logger = logging.getLogger(__name__)


class VisibilityEstimator:
    """Estimate scene visibility and weather conditions from frame analysis.

    Args:
        config: Dict with visibility estimation settings.
    """

    def __init__(self, config: Optional[dict] = None) -> None:
        cfg = config or {}
        self._fog_threshold: float = cfg.get("fog_contrast_threshold", 30.0)
        self._rain_edge_threshold: float = cfg.get("rain_edge_threshold", 0.03)
        self._glare_threshold: float = cfg.get("glare_pixel_threshold", 240)

    def estimate_visibility(self, frame: np.ndarray) -> dict:
        """Alias for estimate."""
        return self.estimate(frame)

    def estimate(self, frame: np.ndarray) -> dict:
        """Estimate visibility and weather conditions.

        Args:
            frame: BGR image.

        Returns:
            Dict with visibility score and condition flags.
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Brightness
        brightness = float(np.mean(gray))

        # Contrast
        contrast = float(np.std(gray))

        # Fog detection: low contrast + high brightness + low saturation
        fog_score = self._detect_fog(gray, hsv)

        # Rain detection: vertical streak patterns + reduced saturation
        rain_score = self._detect_rain(gray, frame)

        # Glare detection: bright hotspots
        glare_score = self._detect_glare(gray)

        # Haze detection: low contrast with moderate brightness
        haze_score = max(0.0, 1.0 - contrast / 50.0) * 0.5

        # Overall visibility score (1.0 = perfect, 0.0 = zero visibility)
        visibility = self._compute_visibility(
            contrast, fog_score, rain_score, glare_score, haze_score
        )

        # Dominant condition
        conditions = {
            "fog": fog_score,
            "rain": rain_score,
            "glare": glare_score,
            "haze": haze_score,
        }
        dominant = max(conditions, key=conditions.get)
        if conditions[dominant] < 0.3:
            dominant = "clear"

        return {
            "visibility_score": round(visibility, 3),
            "condition": dominant,
            "fog_score": round(fog_score, 3),
            "rain_score": round(rain_score, 3),
            "glare_score": round(glare_score, 3),
            "haze_score": round(haze_score, 3),
            "brightness": round(brightness, 1),
            "contrast": round(contrast, 1),
        }

    def _detect_fog(self, gray: np.ndarray, hsv: np.ndarray) -> float:
        """Detect fog from low contrast and low saturation."""
        contrast = float(np.std(gray))
        mean_sat = float(np.mean(hsv[:, :, 1]))

        if contrast < self._fog_threshold and mean_sat < 40:
            return min(1.0, (self._fog_threshold - contrast) / self._fog_threshold)
        return 0.0

    def _detect_rain(self, gray: np.ndarray, frame: np.ndarray) -> float:
        """Detect rain from vertical streak patterns and saturation drop."""
        # Vertical edge detection
        sobel_v = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        v_energy = float(np.mean(np.abs(sobel_v)))

        # Horizontal edges for comparison
        sobel_h = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        h_energy = float(np.mean(np.abs(sobel_h)))

        # Rain creates more vertical streaks
        if h_energy > 0:
            v_h_ratio = v_energy / h_energy
        else:
            v_h_ratio = 0

        # Rain typically shows v/h ratio > 1.5 with high vertical energy
        if v_h_ratio > 1.3 and v_energy > 10:
            return min(1.0, (v_h_ratio - 1.0) * 0.5)
        return 0.0

    def _detect_glare(self, gray: np.ndarray) -> float:
        """Detect glare from bright hotspots (e.g., headlight glare at night)."""
        bright_pixels = np.sum(gray > self._glare_threshold)
        total = gray.size
        bright_ratio = bright_pixels / total

        if bright_ratio > 0.05:
            return min(1.0, bright_ratio / 0.20)
        return 0.0

    def _compute_visibility(
        self,
        contrast: float,
        fog: float,
        rain: float,
        glare: float,
        haze: float,
    ) -> float:
        """Compute overall visibility score."""
        # Base from contrast
        base = min(1.0, contrast / 60.0)

        # Penalties for adverse conditions
        penalty = 0.3 * fog + 0.2 * rain + 0.2 * glare + 0.15 * haze

        visibility = base - penalty
        return float(np.clip(visibility, 0.0, 1.0))
