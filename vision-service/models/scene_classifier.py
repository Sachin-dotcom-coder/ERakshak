"""
models/scene_classifier.py — Scene & Weather Classifier (Sections 64-65)
=========================================================================
Classifies scene conditions from frame image statistics and selects
appropriate preprocessing strategy.

Conditions: day, night, rain, fog, glare, low_visibility
Preprocessing: normal (day), CLAHE (night), denoise+contrast (rain)
"""

import logging
from enum import Enum
from typing import Optional

import cv2
import numpy as np

logger = logging.getLogger(__name__)


class SceneCondition(str, Enum):
    DAY = "day"
    NIGHT = "night"
    RAIN = "rain"
    FOG = "fog"
    GLARE = "glare"
    LOW_VISIBILITY = "low_visibility"


class SceneClassifier:
    """Rule-based scene condition classifier from frame image statistics.

    Uses brightness, contrast, saturation, and edge analysis to determine
    the current scene condition. Drives condition-aware preprocessing
    and dynamic detection thresholds.

    Args:
        config: Dict from thresholds.yaml under 'preprocessing'.
    """

    def __init__(self, config: dict) -> None:
        self._lum_threshold: int = config.get("luminance_threshold", 80)
        self._clahe_clip: float = config.get("clahe_clip_limit", 3.0)
        self._clahe_grid = tuple(config.get("clahe_grid_size", [8, 8]))

        # Create CLAHE instance
        self._clahe = cv2.createCLAHE(
            clipLimit=self._clahe_clip,
            tileGridSize=self._clahe_grid,
        )

        self._prev_condition: SceneCondition = SceneCondition.DAY

    def classify(self, frame: np.ndarray) -> SceneCondition:
        """Classify the scene condition from frame statistics.

        Args:
            frame: BGR image.

        Returns:
            SceneCondition enum value.
        """
        # Convert to grayscale and HSV
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Image statistics
        mean_brightness = float(np.mean(gray))
        brightness_std = float(np.std(gray))
        mean_saturation = float(np.mean(hsv[:, :, 1]))
        contrast = brightness_std  # Proxy for contrast

        # Edge density (blur indicator)
        laplacian_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())

        # Classify
        condition = self._classify_from_stats(
            mean_brightness, contrast, mean_saturation, laplacian_var
        )

        if condition != self._prev_condition:
            logger.info(
                f"Scene condition changed: {self._prev_condition.value} → {condition.value} "
                f"(brightness={mean_brightness:.0f}, contrast={contrast:.1f}, "
                f"saturation={mean_saturation:.0f}, edge_var={laplacian_var:.0f})"
            )
            self._prev_condition = condition

        return condition

    def _classify_from_stats(
        self,
        brightness: float,
        contrast: float,
        saturation: float,
        edge_var: float,
    ) -> SceneCondition:
        """Rule-based classification from image statistics."""
        # Night: very low brightness
        if brightness < 50:
            return SceneCondition.NIGHT

        # Low visibility: low contrast + low edge density
        if contrast < 25 and edge_var < 50:
            # Fog: low contrast + low saturation
            if saturation < 40:
                return SceneCondition.FOG
            return SceneCondition.LOW_VISIBILITY

        # Glare: very high brightness with high variance
        if brightness > 200 and contrast > 60:
            return SceneCondition.GLARE

        # Rain: moderate brightness, low saturation, reduced edges
        if saturation < 50 and edge_var < 200 and brightness > 60:
            return SceneCondition.RAIN

        # Dusk/dawn treated as night if below threshold
        if brightness < self._lum_threshold:
            return SceneCondition.NIGHT

        return SceneCondition.DAY

    def preprocess(
        self,
        frame: np.ndarray,
        condition: SceneCondition,
    ) -> np.ndarray:
        """Apply condition-aware preprocessing (Section 65).

        - DAY: no modification
        - NIGHT: CLAHE on luminance channel
        - RAIN: bilateral filter + contrast enhancement
        - FOG: CLAHE + slight dehazing
        - GLARE: brightness reduction
        - LOW_VISIBILITY: CLAHE aggressive

        Args:
            frame: BGR image.
            condition: Current scene condition.

        Returns:
            Preprocessed BGR frame.
        """
        if condition == SceneCondition.DAY:
            return frame

        if condition == SceneCondition.NIGHT:
            return self._apply_clahe(frame)

        if condition == SceneCondition.RAIN:
            # Bilateral filter to reduce rain noise while preserving edges
            denoised = cv2.bilateralFilter(frame, 5, 50, 50)
            return self._apply_clahe(denoised)

        if condition == SceneCondition.FOG:
            return self._apply_clahe(frame)

        if condition == SceneCondition.GLARE:
            # Reduce brightness
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            hsv[:, :, 2] = np.clip(hsv[:, :, 2].astype(np.float32) * 0.7, 0, 255).astype(np.uint8)
            return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

        if condition == SceneCondition.LOW_VISIBILITY:
            return self._apply_clahe(frame)

        return frame

    def _apply_clahe(self, frame: np.ndarray) -> np.ndarray:
        """Apply CLAHE on the luminance channel (preserves color)."""
        lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
        l_channel = lab[:, :, 0]
        l_enhanced = self._clahe.apply(l_channel)
        lab[:, :, 0] = l_enhanced
        return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
