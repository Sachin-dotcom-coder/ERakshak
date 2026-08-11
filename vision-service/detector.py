"""
detector.py — YOLO26 Vehicle Detection Wrapper
================================================
ERH26_PS_08: Data-Driven Traffic Optimization

Wraps Ultralytics YOLO26 model for vehicle detection on junction camera frames.
Handles model loading, inference, and parsing results into clean Detection objects.

WHY YOLO26 (not YOLOv8/v11):
- NMS-free, DFL-free architecture → lower, more deterministic latency
- Small-Target-Aware Label Assignment (STAL) → better detection of distant/small
  vehicles at the tail of a long queue, where naive counting undercounts
- Released Jan 2026, latest-gen at time of hackathon

Usage:
    from detector import VehicleDetector
    detector = VehicleDetector(config["model"])
    detections = detector.detect(frame)
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class Detection:
    """A single detected vehicle in a frame.

    Attributes:
        bbox: Bounding box as [x1, y1, x2, y2] in pixel coordinates.
        confidence: Detection confidence score (0.0–1.0).
        class_id: Numeric class index from the model.
        class_name: Human-readable class name (e.g., "auto_rickshaw").
    """

    bbox: np.ndarray          # [x1, y1, x2, y2] pixel coords
    confidence: float
    class_id: int
    class_name: str

    @property
    def bottom_center(self) -> tuple[float, float]:
        """Ground-contact point: bottom-center of the bounding box.

        This is the point we project through the homography to get real-world
        coordinates. We use bottom-center (not centroid) to avoid perspective
        bias — especially important for tall vehicles like buses and trucks,
        where the centroid is far above the road surface.
        """
        x_center = (self.bbox[0] + self.bbox[2]) / 2.0
        y_bottom = self.bbox[3]  # Bottom edge of bounding box
        return (float(x_center), float(y_bottom))

    @property
    def center(self) -> tuple[float, float]:
        """Bounding box centroid (for display/annotation only — NOT for calibration)."""
        return (
            float((self.bbox[0] + self.bbox[2]) / 2.0),
            float((self.bbox[1] + self.bbox[3]) / 2.0),
        )

    @property
    def width(self) -> float:
        """Bounding box width in pixels."""
        return float(self.bbox[2] - self.bbox[0])

    @property
    def height(self) -> float:
        """Bounding box height in pixels."""
        return float(self.bbox[3] - self.bbox[1])

    @property
    def area(self) -> float:
        """Bounding box area in pixels²."""
        return self.width * self.height


class VehicleDetector:
    """YOLO26-based vehicle detector.

    Loads a YOLO26 model (stock pretrained or fine-tuned on Surat footage)
    and runs inference on individual frames. Returns a list of Detection
    objects filtered to only vehicle classes we care about.

    The detector handles two modes:
    1. **Stock COCO model** (before fine-tuning): Maps COCO vehicle class IDs
       to our target class names. Limited — no auto-rickshaw, no BRTS distinction.
    2. **Fine-tuned model** (after Phase 2): Uses our 7 custom Indian traffic
       classes directly. This is the goal; stock is just the starting fallback.

    Args:
        config: Dict from config.yaml under the 'model' key.
    """

    # COCO class ID → our target class name (best-effort mapping for stock model)
    # This is a lossy mapping — fine-tuned model eliminates these compromises.
    COCO_TO_CUSTOM: dict[int, str] = {
        1: "cycle",         # COCO "bicycle"
        2: "car",           # COCO "car"
        3: "two_wheeler",   # COCO "motorcycle" → our "two_wheeler"
        5: "bus",           # COCO "bus"
        7: "truck",         # COCO "truck"
    }

    # Set of COCO class IDs that are vehicles we track
    COCO_VEHICLE_IDS: set[int] = {1, 2, 3, 5, 7}

    def __init__(self, config: dict) -> None:
        self._config = config
        self._model = None  # Lazy type; ultralytics.YOLO
        self._is_custom_model: bool = False

        # Build class map from config (used for fine-tuned models)
        self._class_map: dict[int, str] = {
            int(k): v for k, v in config.get("classes", {}).items()
        }

        self._load_model()

    def _load_model(self) -> None:
        """Load the YOLO26 model from the configured weights path.

        Tries YOLO26 first. If it fails (e.g., ultralytics version too old),
        logs a clear error pointing to the fallback — does NOT silently
        substitute a different model.
        """
        # Import here so the module can be imported without ultralytics installed
        # (useful for testing zone_utils etc. independently)
        from ultralytics import YOLO

        weights_path = self._config.get("weights", "yolo26s.pt")
        logger.info(f"Loading YOLO model from: {weights_path}")

        try:
            self._model = YOLO(weights_path)
        except Exception as e:
            logger.error(
                f"Failed to load model '{weights_path}': {e}\n"
                f"If YOLO26 weights are not available in your ultralytics version:\n"
                f"  1. Update ultralytics: pip install -U ultralytics\n"
                f"  2. If still unavailable, edit config.yaml → model.weights to 'yolo11s.pt'\n"
                f"     and tell the team lead (this is a known fallback, not a silent swap)."
            )
            raise

        # Detect whether this is our fine-tuned model or stock COCO
        model_names = getattr(self._model, "names", {})
        if model_names and "auto_rickshaw" in model_names.values():
            self._is_custom_model = True
            logger.info(
                f"Loaded CUSTOM fine-tuned model — {len(model_names)} classes: "
                f"{list(model_names.values())}"
            )
        else:
            self._is_custom_model = False
            logger.info(
                f"Loaded STOCK pretrained model (COCO classes). "
                f"Will filter to vehicle classes and remap. "
                f"Fine-tune for best results — see data_pipeline/finetune.py"
            )

    def detect(self, frame: np.ndarray) -> list[Detection]:
        """Run vehicle detection on a single frame.

        Args:
            frame: BGR image as numpy array (from cv2.VideoCapture).

        Returns:
            List of Detection objects for vehicles found in this frame.
            Non-vehicle classes (people, animals, etc.) are filtered out.
            Returns empty list on inference failure (never raises).
        """
        if self._model is None:
            logger.error("Model not loaded — returning empty detections")
            return []

        conf_thresh = self._config.get("confidence_threshold", 0.35)
        img_size = self._config.get("image_size", 640)
        half = self._config.get("half_precision", True)

        try:
            results = self._model(
                frame,
                conf=conf_thresh,
                imgsz=img_size,
                half=half,
                verbose=False,  # Suppress per-frame ultralytics logging
            )
        except Exception as e:
            # Graceful degradation: log and return empty, don't crash the pipeline
            logger.warning(f"Detection inference failed: {e}")
            return []

        return self._parse_results(results)

    def _parse_results(self, results) -> list[Detection]:
        """Parse Ultralytics result objects into our Detection dataclass.

        Filters to vehicle classes only. Maps class IDs to our target names.
        """
        detections: list[Detection] = []

        if not results or len(results) == 0:
            return detections

        result = results[0]  # Single image → single result

        if result.boxes is None or len(result.boxes) == 0:
            return detections

        boxes = result.boxes

        for i in range(len(boxes)):
            class_id = int(boxes.cls[i].item())
            confidence = float(boxes.conf[i].item())
            bbox = boxes.xyxy[i].cpu().numpy().astype(float)  # [x1, y1, x2, y2]

            # Map to our class name; skip if not a vehicle we track
            class_name = self._resolve_class_name(class_id)
            if class_name is None:
                continue

            detections.append(Detection(
                bbox=bbox,
                confidence=confidence,
                class_id=class_id,
                class_name=class_name,
            ))

        return detections

    def _resolve_class_name(self, class_id: int) -> Optional[str]:
        """Map a model class ID to our target class name.

        For fine-tuned models: uses the config class map directly.
        For stock COCO models: maps known vehicle IDs to our closest class.

        Returns:
            Class name string, or None if this class isn't a vehicle we track.
        """
        if self._is_custom_model:
            return self._class_map.get(class_id)
        else:
            if class_id in self.COCO_VEHICLE_IDS:
                return self.COCO_TO_CUSTOM.get(class_id)
            return None

    @property
    def model(self):
        """Access the underlying Ultralytics YOLO model.

        Used by tracker.py to call model.track() with the same model instance.
        """
        return self._model

    @property
    def is_custom_model(self) -> bool:
        """Whether the loaded model is our fine-tuned version (vs. stock COCO)."""
        return self._is_custom_model
