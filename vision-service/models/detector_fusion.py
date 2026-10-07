"""
models/detector_fusion.py — Detection Fusion Layer (Section 15)
================================================================
Fuses detections from full-frame and tiled inference using IoU matching.

Overlapping tiles can detect the same vehicle twice. This module deduplicates
detections by matching bounding boxes via IoU and keeping the highest-confidence
detection or fusing coordinates.

The fusion layer runs BEFORE tracking.
"""

import logging
from typing import Optional

import numpy as np

from models.detector import Detection

logger = logging.getLogger(__name__)


def compute_iou(box_a: np.ndarray, box_b: np.ndarray) -> float:
    """Compute Intersection over Union between two bounding boxes.

    Args:
        box_a: [x1, y1, x2, y2]
        box_b: [x1, y1, x2, y2]

    Returns:
        IoU value in [0.0, 1.0].
    """
    x1 = max(box_a[0], box_b[0])
    y1 = max(box_a[1], box_b[1])
    x2 = min(box_a[2], box_b[2])
    y2 = min(box_a[3], box_b[3])

    intersection = max(0, x2 - x1) * max(0, y2 - y1)

    area_a = (box_a[2] - box_a[0]) * (box_a[3] - box_a[1])
    area_b = (box_b[2] - box_b[0]) * (box_b[3] - box_b[1])
    union = area_a + area_b - intersection

    if union <= 0:
        return 0.0
    return intersection / union


class DetectionFusion:
    """Fuses full-frame and tiled detections, removing duplicates.

    Uses IoU-based matching to identify duplicate detections from
    overlapping tiles. Keeps the highest-confidence detection for
    each matched pair, or fuses their coordinates.

    Args:
        config: Dict from thresholds.yaml under 'detection'.
    """

    def __init__(self, config: dict) -> None:
        self._iou_threshold: float = config.get("fusion_iou_threshold", 0.50)

    def fuse(
        self,
        full_frame_dets: list[Detection],
        tiled_dets: list[Detection],
    ) -> list[Detection]:
        """Fuse detections from full-frame and tiled inference.

        Algorithm:
        1. Start with all full-frame detections
        2. For each tiled detection, check IoU against all current detections
        3. If IoU > threshold with any existing detection:
           - Keep whichever has higher confidence
        4. If no match: add the tiled detection (new small object found)

        Args:
            full_frame_dets: Detections from full-frame YOLO inference.
            tiled_dets: Detections from tiled far-field inference.

        Returns:
            Fused, deduplicated list of Detection objects.
        """
        if not tiled_dets:
            return full_frame_dets

        if not full_frame_dets:
            return tiled_dets

        # Start with copies of full-frame detections
        fused: list[Detection] = list(full_frame_dets)
        added_from_tiles = 0
        replaced_from_tiles = 0

        for tiled_det in tiled_dets:
            best_iou = 0.0
            best_idx = -1

            for i, existing in enumerate(fused):
                iou = compute_iou(tiled_det.bbox, existing.bbox)
                if iou > best_iou:
                    best_iou = iou
                    best_idx = i

            if best_iou >= self._iou_threshold:
                # Duplicate found — keep higher confidence
                if tiled_det.confidence > fused[best_idx].confidence:
                    fused[best_idx] = tiled_det
                    replaced_from_tiles += 1
            else:
                # New detection from tiles (not found by full-frame)
                fused.append(tiled_det)
                added_from_tiles += 1

        if added_from_tiles > 0 or replaced_from_tiles > 0:
            logger.debug(
                f"Fusion: {len(full_frame_dets)} full-frame + {len(tiled_dets)} tiled "
                f"→ {len(fused)} fused (added={added_from_tiles}, "
                f"replaced={replaced_from_tiles})"
            )

        return fused

    def fuse_tiles_only(self, tiled_dets: list[Detection]) -> list[Detection]:
        """Deduplicate detections from overlapping tiles (intra-tile fusion).

        When tiles overlap, the same vehicle can appear in multiple tiles.
        This merges those duplicates before merging with full-frame detections.

        Args:
            tiled_dets: All detections from all tiles.

        Returns:
            Deduplicated tiled detections.
        """
        if len(tiled_dets) <= 1:
            return tiled_dets

        # Sort by confidence (highest first)
        sorted_dets = sorted(tiled_dets, key=lambda d: d.confidence, reverse=True)
        keep: list[Detection] = []
        suppressed: set[int] = set()

        for i, det_i in enumerate(sorted_dets):
            if i in suppressed:
                continue
            keep.append(det_i)

            for j in range(i + 1, len(sorted_dets)):
                if j in suppressed:
                    continue
                iou = compute_iou(det_i.bbox, sorted_dets[j].bbox)
                if iou >= self._iou_threshold:
                    suppressed.add(j)

        return keep
