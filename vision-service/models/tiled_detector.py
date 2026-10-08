"""
models/tiled_detector.py — Far-Field Tiled Detection (Sections 11-16)
======================================================================
Implements multi-scale detection via tiling for small/distant vehicles.

The far end of a traffic approach contains tiny vehicles (10-15 pixels).
This module crops a configurable far-field ROI, tiles it into overlapping
crops, runs YOLO on each tile, and remaps detections back to global
frame coordinates.

Tiled inference is adaptive — only triggered when far-field confidence
is low or object count drops unexpectedly (Section 16).
"""

import logging
from dataclasses import dataclass
from typing import Optional

import cv2
import numpy as np

from models.detector import Detection

logger = logging.getLogger(__name__)


@dataclass
class Tile:
    """A crop from the far-field ROI for tiled inference."""
    image: np.ndarray
    x_offset: int
    y_offset: int
    index: int


class TiledDetector:
    """Far-field tiled detection for small/distant vehicles.

    Crops the configured far-field ROI polygon, divides it into
    overlapping tiles, runs detection on each, and remaps coordinates
    back to the original frame.

    Args:
        model: Loaded YOLO model instance.
        config: Dict from thresholds.yaml under 'tiled_detection'.
        far_field_polygon: List of [x, y] pixel coordinates defining the ROI.
        model_config: Model configuration dict.
    """

    def __init__(
        self,
        model,
        config: dict,
        far_field_polygon: list[list[int]],
        model_config: dict,
    ) -> None:
        self._model = model
        self._tile_size: int = config.get("tile_size", 640)
        self._overlap: float = config.get("overlap", 0.20)
        self._trigger_confidence: float = config.get("trigger_confidence", 0.50)
        self._min_count_drop: int = config.get("min_count_drop", 3)
        self._far_field_polygon = np.array(far_field_polygon, dtype=np.int32)
        self._model_config = model_config

        # Track previous far-field count for adaptive triggering
        self._prev_far_field_count: int = 0

        # Precompute bounding rect of polygon for faster cropping
        x, y, w, h = cv2.boundingRect(self._far_field_polygon)
        self._roi_x, self._roi_y = x, y
        self._roi_w, self._roi_h = w, h

        logger.info(
            f"TiledDetector initialized: tile_size={self._tile_size}, "
            f"overlap={self._overlap}, ROI=({x},{y},{w},{h})"
        )

    def should_trigger(
        self,
        full_frame_detections: list[Detection],
    ) -> bool:
        """Determine if tiled inference should run (Section 16).

        Triggered when:
        - Far-field object count drops unexpectedly
        - Small-object confidence is low
        - Queue estimate inconsistency detected

        Args:
            full_frame_detections: Detections from full-frame inference.

        Returns:
            True if tiled inference should be triggered.
        """
        # Count detections inside far-field ROI
        far_field_count = 0
        low_conf_count = 0

        for det in full_frame_detections:
            bc = det.bottom_center
            point = np.array([bc[0], bc[1]])

            # Check if detection is inside far-field polygon
            inside = cv2.pointPolygonTest(
                self._far_field_polygon, (float(bc[0]), float(bc[1])), False
            )
            if inside >= 0:
                far_field_count += 1
                if det.confidence < self._trigger_confidence:
                    low_conf_count += 1

        # Trigger if count dropped significantly
        count_dropped = (
            self._prev_far_field_count > 0
            and (self._prev_far_field_count - far_field_count) >= self._min_count_drop
        )

        # Trigger if many low-confidence detections in far field
        low_conf_ratio = (
            low_conf_count / max(far_field_count, 1) if far_field_count > 0 else 0
        )

        self._prev_far_field_count = far_field_count

        should = count_dropped or low_conf_ratio > 0.5
        if should:
            logger.debug(
                f"Tiled inference triggered: count_drop={count_dropped}, "
                f"low_conf_ratio={low_conf_ratio:.2f}"
            )
        return should

    def detect_tiled(
        self,
        frame: np.ndarray,
        scene_condition: str = "day",
    ) -> list[Detection]:
        """Run tiled detection on the far-field ROI.

        1. Crop the ROI bounding rectangle from the frame
        2. Generate overlapping tiles
        3. Run detection on each tile
        4. Remap tile coordinates to global frame coordinates
        5. Return all detections

        Args:
            frame: Full BGR frame.
            scene_condition: Current scene condition for thresholding.

        Returns:
            List of Detection objects in global frame coordinates.
        """
        # Crop ROI region
        roi = frame[
            self._roi_y : self._roi_y + self._roi_h,
            self._roi_x : self._roi_x + self._roi_w,
        ]

        if roi.size == 0:
            return []

        # Generate tiles
        tiles = self._generate_tiles(roi)

        if not tiles:
            return []

        # Run detection on each tile and remap
        all_detections: list[Detection] = []
        conf_thresh = 0.30  # Lower threshold for tiled (catching small objects)
        img_size = self._model_config.get("image_size", 640)
        half = self._model_config.get("half_precision", True)

        for tile in tiles:
            try:
                results = self._model(
                    tile.image,
                    conf=conf_thresh,
                    imgsz=img_size,
                    half=half,
                    verbose=False,
                )
            except Exception as e:
                logger.warning(f"Tiled inference failed on tile {tile.index}: {e}")
                continue

            for result in results:
                if result.boxes is None or len(result.boxes) == 0:
                    continue

                boxes = result.boxes.xyxy.cpu().numpy()
                confidences = result.boxes.conf.cpu().numpy()
                class_ids = result.boxes.cls.cpu().numpy().astype(int)

                for bbox, conf, cls_id in zip(boxes, confidences, class_ids):
                    class_name = self._resolve_class(cls_id)
                    if class_name is None:
                        continue

                    # Remap tile coordinates → global frame coordinates
                    global_bbox = np.array([
                        bbox[0] + tile.x_offset + self._roi_x,
                        bbox[1] + tile.y_offset + self._roi_y,
                        bbox[2] + tile.x_offset + self._roi_x,
                        bbox[3] + tile.y_offset + self._roi_y,
                    ])

                    all_detections.append(Detection(
                        bbox=global_bbox,
                        confidence=float(conf),
                        class_id=int(cls_id),
                        class_name=class_name,
                    ))

        logger.debug(f"Tiled detection: {len(tiles)} tiles → {len(all_detections)} detections")
        return all_detections

    def _generate_tiles(self, roi: np.ndarray) -> list[Tile]:
        """Generate overlapping tiles from the ROI (Section 14).

        Args:
            roi: Cropped ROI image.

        Returns:
            List of Tile objects with coordinate mappings.
        """
        h, w = roi.shape[:2]
        stride = int(self._tile_size * (1.0 - self._overlap))
        tiles: list[Tile] = []
        idx = 0

        for y in range(0, h, stride):
            for x in range(0, w, stride):
                x_end = min(x + self._tile_size, w)
                y_end = min(y + self._tile_size, h)

                # Skip very small edge tiles
                tile_w = x_end - x
                tile_h = y_end - y
                if tile_w < self._tile_size * 0.3 or tile_h < self._tile_size * 0.3:
                    continue

                tile_img = roi[y:y_end, x:x_end]

                tiles.append(Tile(
                    image=tile_img,
                    x_offset=x,
                    y_offset=y,
                    index=idx,
                ))
                idx += 1

        return tiles

    def detect(self, frame: np.ndarray, *args, **kwargs) -> list[Detection]:
        """Alias for detect_tiled to provide a uniform detector interface."""
        scene_cond = kwargs.get("scene_condition", "day")
        if args and isinstance(args[0], str):
            scene_cond = args[0]
        return self.detect_tiled(frame, scene_condition=scene_cond)

    def _resolve_class(self, cls_id: int) -> Optional[str]:
        """Resolve class ID to class name."""
        model_names = getattr(self._model, "names", {})
        is_custom = bool(model_names and "auto_rickshaw" in model_names.values())
        if is_custom:
            classes = self._model_config.get("classes", {})
            class_map = {int(k): v for k, v in classes.items()}
            if class_map:
                return class_map.get(cls_id)
        # COCO fallback
        coco_map = {1: "cycle", 2: "car", 3: "two_wheeler", 5: "bus", 7: "truck"}
        return coco_map.get(cls_id)
