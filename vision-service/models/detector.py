"""
models/detector.py — Enhanced YOLO26 Vehicle Detection Wrapper
================================================================
Upgraded from original detector.py with:
- Scene-condition-aware dynamic confidence thresholds (Section 66)
- Integration with centralized config system
- Detection dataclass with full metadata

Wraps Ultralytics YOLO26 for vehicle detection on junction camera frames.
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import numpy as np

import torch

# Ensure PyTorch 2.6+ doesn't fail on weights_only loading of model checkpoints
try:
    _orig_torch_load = torch.load
    def _safe_torch_load(*args, **kwargs):
        if "weights_only" not in kwargs:
            kwargs["weights_only"] = False
        return _orig_torch_load(*args, **kwargs)
    torch.load = _safe_torch_load
except Exception:
    pass

logger = logging.getLogger(__name__)


@dataclass
class Detection:
    """A single detected vehicle in a frame.

    Attributes:
        bbox: Bounding box as [x1, y1, x2, y2] in pixel coordinates.
        confidence: Detection confidence score (0.0-1.0).
        class_id: Numeric class index from the model.
        class_name: Human-readable class name.
        area_px: Bounding box area in pixels².
    """

    bbox: np.ndarray          # [x1, y1, x2, y2] pixel coords
    confidence: float
    class_id: int
    class_name: str

    @property
    def bottom_center(self) -> tuple[float, float]:
        """Ground-contact point: bottom-center of the bounding box.

        Used for homography projection. Bottom-center avoids perspective
        parallax on tall vehicles (bus roofs project behind road surface).
        """
        x_center = (self.bbox[0] + self.bbox[2]) / 2.0
        y_bottom = self.bbox[3]
        return (float(x_center), float(y_bottom))

    @property
    def center(self) -> tuple[float, float]:
        """Bounding box centroid (for display only — NOT for calibration)."""
        return (
            float((self.bbox[0] + self.bbox[2]) / 2.0),
            float((self.bbox[1] + self.bbox[3]) / 2.0),
        )

    @property
    def width(self) -> float:
        return float(self.bbox[2] - self.bbox[0])

    @property
    def height(self) -> float:
        return float(self.bbox[3] - self.bbox[1])

    @property
    def area(self) -> float:
        return self.width * self.height

    @property
    def is_small(self) -> bool:
        """Whether this detection is small enough to benefit from tiled inference."""
        return self.area < 2500  # ~50x50 pixels


class VehicleDetector:
    """YOLO26-based vehicle detector with scene-aware thresholds.

    Loads a YOLO26 model and runs inference with dynamic confidence
    thresholds based on scene conditions (day/night/rain/fog).

    Args:
        config: Dict with model and detection config.
    """

    # COCO class ID → custom class name (fallback for stock model)
    COCO_TO_CUSTOM: dict[int, str] = {
        1: "cycle",
        2: "car",
        3: "two_wheeler",
        5: "bus",
        7: "truck",
    }
    COCO_VEHICLE_IDS: set[int] = {1, 2, 3, 5, 7}

    def __init__(self, model_config: dict, detection_config: dict) -> None:
        self._model_config = model_config
        self._detection_config = detection_config
        self._model = None
        self._is_custom_model: bool = False

        # Build class map from config
        self._class_map: dict[int, str] = {
            int(k): v for k, v in model_config.get("classes", {}).items()
        }

        # Scene-condition thresholds (Section 66)
        self._scene_thresholds: dict[str, float] = detection_config.get(
            "scene_thresholds",
            {"day": 0.45, "night": 0.35, "rain": 0.40, "fog": 0.30},
        )
        self._base_threshold: float = detection_config.get(
            "confidence_threshold", 0.45
        )

        self._load_model()

    def _load_model(self) -> None:
        """Load the YOLO26 model from configured weights path."""
        from ultralytics import YOLO

        weights_path = self._model_config.get("weights", "yolo26s.pt")
        logger.info(f"Loading YOLO model from: {weights_path}")

        try:
            self._model = YOLO(weights_path)
        except Exception as e:
            fallback = Path(__file__).resolve().parent.parent / "yolov8n.pt"
            if fallback.exists():
                logger.warning(
                    f"Configured weights '{weights_path}' failed to load: {e}. "
                    f"Falling back to local '{fallback.name}'."
                )
                self._model = YOLO(str(fallback))
            else:
                logger.error(
                    f"Failed to load model '{weights_path}': {e}\n"
                    f"Update ultralytics or edit config → model.weights"
                )
                raise

        model_names = getattr(self._model, "names", {})
        if model_names and "auto_rickshaw" in model_names.values():
            self._is_custom_model = True
            logger.info(
                f"Loaded CUSTOM fine-tuned model — {len(model_names)} classes: "
                f"{list(model_names.values())}"
            )
        else:
            self._is_custom_model = False
            logger.info("Loaded STOCK pretrained model (COCO). Will remap vehicle classes.")

    def detect(
        self,
        frame: np.ndarray,
        scene_condition: str = "day",
    ) -> list[Detection]:
        """Run vehicle detection with scene-aware confidence threshold.

        Args:
            frame: BGR image as numpy array.
            scene_condition: Current scene condition for dynamic thresholding.

        Returns:
            List of Detection objects for vehicles found.
        """
        if self._model is None:
            logger.error("Model not loaded — returning empty detections")
            return []

        # Dynamic threshold based on scene condition (Section 66)
        conf_thresh = self._scene_thresholds.get(
            scene_condition, self._base_threshold
        )
        img_size = self._detection_config.get("image_size", 640)
        half = self._detection_config.get("half_precision", True)

        try:
            results = self._model(
                frame,
                conf=conf_thresh,
                imgsz=img_size,
                half=half,
                verbose=False,
            )
        except Exception as e:
            logger.warning(f"Detection inference failed: {e}")
            return []

        return self._parse_results(results)

    def _parse_results(self, results) -> list[Detection]:
        """Parse ultralytics results into Detection objects."""
        detections: list[Detection] = []

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

                detections.append(Detection(
                    bbox=bbox,
                    confidence=float(conf),
                    class_id=int(cls_id),
                    class_name=class_name,
                ))

        return detections

    def _resolve_class(self, cls_id: int) -> Optional[str]:
        """Resolve class ID to class name, handling custom vs COCO models."""
        if self._is_custom_model:
            return self._class_map.get(cls_id)
        else:
            if cls_id in self.COCO_VEHICLE_IDS:
                return self.COCO_TO_CUSTOM.get(cls_id)
            return None

    @property
    def model(self):
        """Access underlying YOLO model (for tracker integration)."""
        return self._model
