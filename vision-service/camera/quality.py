"""
camera/quality.py — Frame Quality Assessment
==============================================
Combines multiple quality metrics into a frame quality score
and provides preprocessing dispatch recommendations.
"""

import logging
from typing import Optional

import cv2
import numpy as np

logger = logging.getLogger(__name__)


class FrameQualityAssessor:
    """Assess frame quality and recommend preprocessing pipeline.

    Args:
        config: Dict with quality assessment settings.
    """

    def __init__(self, config: Optional[dict] = None) -> None:
        cfg = config or {}
        self._noise_threshold: float = cfg.get("noise_threshold", 15.0)
        self._edge_density_threshold: float = cfg.get("edge_density_threshold", 0.05)

    def assess(self, frame: np.ndarray) -> dict:
        """Assess frame quality.

        Args:
            frame: BGR image.

        Returns:
            Dict with quality metrics and preprocessing recommendations.
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Noise estimation (using Laplacian MAD)
        noise = self._estimate_noise(gray)

        # Edge density (indicator of scene complexity)
        edge_density = self._compute_edge_density(gray)

        # Color saturation
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        saturation = float(np.mean(hsv[:, :, 1]))

        # Dynamic range
        dynamic_range = float(np.max(gray)) - float(np.min(gray))

        # Overall quality score
        quality = self._compute_quality(noise, edge_density, saturation, dynamic_range)

        # Preprocessing recommendation
        recommendation = self._recommend_preprocessing(
            noise, edge_density, float(np.mean(gray)), saturation
        )

        return {
            "quality_score": round(quality, 3),
            "noise_level": round(noise, 2),
            "edge_density": round(edge_density, 4),
            "saturation": round(saturation, 1),
            "dynamic_range": round(dynamic_range, 1),
            "preprocessing": recommendation,
        }

    def _estimate_noise(self, gray: np.ndarray) -> float:
        """Estimate image noise using Laplacian MAD method."""
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        sigma = float(np.median(np.abs(laplacian))) * 1.4826
        return sigma

    def _compute_edge_density(self, gray: np.ndarray) -> float:
        """Compute edge pixel density using Canny."""
        edges = cv2.Canny(gray, 50, 150)
        return float(np.sum(edges > 0)) / edges.size

    def _compute_quality(
        self, noise: float, edge_density: float,
        saturation: float, dynamic_range: float,
    ) -> float:
        """Compute composite quality score."""
        noise_factor = max(0, 1.0 - noise / 30.0)
        edge_factor = min(1.0, edge_density / 0.10)
        sat_factor = min(1.0, saturation / 80.0)
        range_factor = min(1.0, dynamic_range / 200.0)

        return float(np.clip(
            0.30 * noise_factor + 0.25 * edge_factor
            + 0.20 * sat_factor + 0.25 * range_factor,
            0.0, 1.0,
        ))

    def _recommend_preprocessing(
        self, noise: float, edge_density: float,
        brightness: float, saturation: float,
    ) -> list[str]:
        """Recommend preprocessing steps based on quality metrics."""
        steps = []
        if brightness < 60:
            steps.append("clahe")
        if noise > self._noise_threshold:
            steps.append("denoise")
        if brightness > 200:
            steps.append("reduce_brightness")
        if saturation < 20:
            steps.append("enhance_contrast")
        if not steps:
            steps.append("none")
        return steps
