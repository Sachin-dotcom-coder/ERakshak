"""
models/segmentation_refiner.py — Selective Segmentation Refinement (Section 26)
==================================================================================
Provides optional mask-based refinement for difficult detections:
- Large vehicles (bus, truck) where bottom-center from bbox is inaccurate
- Heavily occluded vehicles where bbox area is misleading
- Any detection where ground contact accuracy matters

Uses SAM (Segment Anything Model) when available, otherwise falls back to
contour-based estimation from the detection region.

This module is designed to be called SELECTIVELY — not on every vehicle.
Only trigger when the detection is difficult and the extra compute is justified.
"""

import logging
from dataclasses import dataclass
from typing import Optional

import cv2
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class RefinedContact:
    """Result of segmentation-based ground contact refinement.

    Attributes:
        ground_contact: Refined ground contact point (x, y) in pixel coords.
        mask_area_px: Area of the segmentation mask in pixels².
        confidence: Confidence in the refinement (0-1).
        used_segmentation: Whether full segmentation was used (vs fallback).
    """
    ground_contact: tuple[float, float]
    mask_area_px: float
    confidence: float
    used_segmentation: bool = False


class SegmentationRefiner:
    """Selective segmentation refinement for difficult vehicle detections.

    Improves ground contact point accuracy for tall/occluded vehicles by
    analyzing the lower portion of the bounding box to find the actual
    road contact region.

    When SAM is available, uses zero-shot prompted segmentation.
    Otherwise, falls back to contour/edge analysis within the bbox.

    Args:
        config: Dict with segmentation refinement settings.
    """

    # Classes that benefit most from refinement
    REFINEMENT_CLASSES: set[str] = {"bus", "truck", "brts_bus"}

    def __init__(self, config: dict) -> None:
        self._enabled: bool = config.get("enabled", True)
        self._occlusion_threshold: float = config.get("occlusion_trigger", 0.40)
        self._area_threshold_px: float = config.get("area_trigger_px", 15000)
        self._sam_model = None
        self._sam_available: bool = False

        # Try to load SAM if configured
        sam_weights = config.get("sam_weights_path")
        if sam_weights:
            self._try_load_sam(sam_weights)

    def _try_load_sam(self, weights_path: str) -> None:
        """Attempt to load SAM model for segmentation."""
        try:
            # SAM 3.1 integration point — scaffolded for when weights are available
            logger.info(f"SAM weights path configured: {weights_path}")
            logger.info("SAM model loading scaffolded — using contour fallback")
            self._sam_available = False
        except Exception as e:
            logger.warning(f"SAM not available: {e}. Using contour fallback.")
            self._sam_available = False

    def should_refine(
        self,
        class_name: str,
        bbox: np.ndarray,
        occlusion_ratio: float = 0.0,
    ) -> bool:
        """Determine if a detection should be refined (Section 26).

        Refinement is triggered when:
        - Vehicle is a large class (bus/truck/brts_bus), OR
        - Occlusion ratio is high, OR
        - Bounding box area is very large (close-up vehicle)

        Args:
            class_name: Detected vehicle class.
            bbox: [x1, y1, x2, y2] bounding box.
            occlusion_ratio: Estimated occlusion ratio (0-1).

        Returns:
            True if refinement should be applied.
        """
        if not self._enabled:
            return False

        # Large vehicle classes always benefit
        if class_name in self.REFINEMENT_CLASSES:
            return True

        # High occlusion
        if occlusion_ratio >= self._occlusion_threshold:
            return True

        # Very large bounding box (close to camera)
        area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])
        if area >= self._area_threshold_px:
            return True

        return False

    def refine_ground_contact(
        self,
        frame: np.ndarray,
        bbox: np.ndarray,
        class_name: str,
    ) -> RefinedContact:
        """Refine the ground contact point using segmentation or contour analysis.

        For tall vehicles, the standard bottom-center of the bbox may not
        accurately represent the road contact point. This method analyzes
        the lower portion of the bbox to find a more accurate contact.

        Args:
            frame: Full BGR frame.
            bbox: [x1, y1, x2, y2] bounding box in pixel coordinates.
            class_name: Vehicle class name.

        Returns:
            RefinedContact with improved ground contact point.
        """
        if self._sam_available:
            return self._refine_with_sam(frame, bbox, class_name)
        return self._refine_with_contours(frame, bbox, class_name)

    def _refine_with_sam(
        self,
        frame: np.ndarray,
        bbox: np.ndarray,
        class_name: str,
    ) -> RefinedContact:
        """Refine using SAM segmentation model.

        Scaffolded — when SAM weights are provided, this will use
        bbox-prompted segmentation to get the vehicle mask and extract
        the lowest reliable road-contact region.
        """
        # SAM integration point — for now, fall back to contour method
        logger.debug(f"SAM refinement for {class_name} — using contour fallback")
        return self._refine_with_contours(frame, bbox, class_name)

    def _refine_with_contours(
        self,
        frame: np.ndarray,
        bbox: np.ndarray,
        class_name: str,
    ) -> RefinedContact:
        """Refine ground contact using edge/contour analysis in the lower bbox region.

        Strategy:
        1. Crop the lower 40% of the bounding box (where wheels/road contact is)
        2. Apply edge detection
        3. Find the lowest strong horizontal edge (likely the vehicle-road boundary)
        4. Use the centroid of that edge as the refined contact point
        """
        x1, y1, x2, y2 = int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])
        h, w = frame.shape[:2]

        # Clamp to frame bounds
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(w, x2), min(h, y2)

        bbox_h = y2 - y1
        bbox_w = x2 - x1

        if bbox_h < 10 or bbox_w < 10:
            # Too small to refine — return standard bottom-center
            return RefinedContact(
                ground_contact=(float((x1 + x2) / 2), float(y2)),
                mask_area_px=float(bbox_h * bbox_w),
                confidence=0.5,
                used_segmentation=False,
            )

        # Focus on the lower 40% of the bbox
        lower_y = y1 + int(bbox_h * 0.6)
        lower_region = frame[lower_y:y2, x1:x2]

        if lower_region.size == 0:
            return RefinedContact(
                ground_contact=(float((x1 + x2) / 2), float(y2)),
                mask_area_px=float(bbox_h * bbox_w),
                confidence=0.5,
                used_segmentation=False,
            )

        # Edge detection on the lower region
        gray = cv2.cvtColor(lower_region, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)

        # Find the lowest row with significant edge activity
        row_sums = np.sum(edges, axis=1)
        threshold = np.max(row_sums) * 0.3 if np.max(row_sums) > 0 else 0

        # Search from bottom up for the lowest edge-active row
        contact_row_local = edges.shape[0] - 1  # Default: very bottom
        for row_idx in range(edges.shape[0] - 1, -1, -1):
            if row_sums[row_idx] > threshold:
                contact_row_local = row_idx
                break

        # Convert to global coordinates
        contact_y = lower_y + contact_row_local
        contact_x = float((x1 + x2) / 2)

        # Confidence: higher when we found a clear edge, lower otherwise
        max_edge = float(np.max(row_sums)) if np.max(row_sums) > 0 else 0
        confidence = min(1.0, max_edge / (bbox_w * 255 * 0.3))
        confidence = max(0.3, confidence)  # Floor at 0.3

        # Estimate mask area (rough — from non-zero edge pixels)
        mask_area = float(np.sum(edges > 0))

        return RefinedContact(
            ground_contact=(contact_x, float(contact_y)),
            mask_area_px=mask_area,
            confidence=confidence,
            used_segmentation=False,
        )
