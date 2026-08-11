"""
tracker.py — BoT-SORT Vehicle Tracking Wrapper
================================================
ERH26_PS_08: Data-Driven Traffic Optimization

Wraps Ultralytics BoT-SORT tracker for persistent vehicle ID assignment
across frames. Maintains per-track history (trajectory, class, lane assignments)
needed by downstream violation/incident detection and speed computation.

WHY BoT-SORT (not ByteTrack):
- Adds appearance-based re-identification on top of motion prediction
- Handles occlusion recovery (two-wheelers vanishing behind buses, etc.)
- Critical for dense Indian traffic where constant occlusion causes ByteTrack
  to lose and reassign track IDs, inflating vehicle counts

If BoT-SORT drops us below real-time, benchmark ByteTrack as a fallback
and report the FPS tradeoff — don't switch silently.

Usage:
    from tracker import VehicleTracker
    tracker = VehicleTracker(model, tracker_config_path)
    tracked_vehicles = tracker.update(frame, fps=10.0)
"""

import logging
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)


# Maximum trajectory history length per track (to avoid unbounded memory growth)
MAX_TRAJECTORY_LENGTH: int = 300


@dataclass
class TrackedVehicle:
    """A vehicle being tracked across frames.

    Carries the current detection plus accumulated history needed for
    speed computation, violation detection, and lane-change tracking.

    Attributes:
        track_id: Persistent integer ID assigned by BoT-SORT.
        bbox: Current bounding box [x1, y1, x2, y2] in pixels.
        confidence: Current detection confidence.
        class_id: Numeric class index.
        class_name: Human-readable class name.
        trajectory_px: History of bottom-center positions in pixel coords.
        trajectory_world: History of ground-plane positions (meters), populated
                          after homography projection.
        lane_history: History of lane assignments (for lane-change detection).
        frames_tracked: Number of consecutive frames this track has been alive.
        is_active: Whether this track was matched in the current frame.
    """
    track_id: int
    bbox: np.ndarray
    confidence: float
    class_id: int
    class_name: str
    trajectory_px: list[tuple[float, float]] = field(default_factory=list)
    trajectory_world: list[tuple[float, float]] = field(default_factory=list)
    lane_history: list[Optional[str]] = field(default_factory=list)
    frames_tracked: int = 0
    is_active: bool = True

    @property
    def bottom_center(self) -> tuple[float, float]:
        """Current ground-contact point (bottom-center of bbox) in pixels."""
        x_center = (self.bbox[0] + self.bbox[2]) / 2.0
        y_bottom = self.bbox[3]
        return (float(x_center), float(y_bottom))

    @property
    def latest_world_position(self) -> Optional[tuple[float, float]]:
        """Most recent ground-plane position, or None if not yet projected."""
        return self.trajectory_world[-1] if self.trajectory_world else None


class VehicleTracker:
    """BoT-SORT-based multi-object tracker for vehicles.

    Uses Ultralytics' built-in tracking API (model.track()) with a custom
    BoT-SORT configuration. Maintains persistent TrackedVehicle objects
    with trajectory history across frames.

    The tracker wraps model.track() rather than calling detect() separately —
    Ultralytics' tracking API handles the detect-then-track pipeline internally,
    which is more efficient and ensures the tracker sees raw detection scores.

    Args:
        model: Loaded Ultralytics YOLO model instance (from detector.py).
        tracker_config: Path to custom botsort_custom.yaml config file.
        model_config: Dict from config.yaml under the 'model' key.
    """

    # COCO class remapping (same as detector.py — duplicated intentionally
    # so tracker.py doesn't depend on detector.py for this)
    COCO_TO_CUSTOM: dict[int, str] = {
        1: "cycle",
        2: "car",
        3: "two_wheeler",
        5: "bus",
        7: "truck",
    }
    COCO_VEHICLE_IDS: set[int] = {1, 2, 3, 5, 7}

    def __init__(
        self,
        model,
        tracker_config: str,
        model_config: dict,
    ) -> None:
        self._model = model
        self._tracker_config = tracker_config
        self._model_config = model_config

        # Persistent track storage: track_id → TrackedVehicle
        self._tracks: dict[int, TrackedVehicle] = {}

        # Track which IDs were seen in the current frame (for marking lost tracks)
        self._active_ids: set[int] = set()

        # Detect whether we're using a custom-trained model
        model_names = getattr(model, "names", {})
        self._is_custom_model = "auto_rickshaw" in model_names.values()

        # Build class map from config (for custom models)
        self._class_map: dict[int, str] = {
            int(k): v for k, v in model_config.get("classes", {}).items()
        }

        logger.info(
            f"Tracker initialized with config: {tracker_config} | "
            f"Custom model: {self._is_custom_model}"
        )

    def update(
        self,
        frame: np.ndarray,
    ) -> list[TrackedVehicle]:
        """Run tracking on a new frame and return all active tracked vehicles.

        Calls model.track() which internally runs detection + BoT-SORT matching.
        Updates internal TrackedVehicle objects with new positions and history.

        Args:
            frame: BGR image as numpy array.

        Returns:
            List of TrackedVehicle objects that are active in this frame.
            Vehicles that were tracked previously but not seen in this frame
            are still stored internally (BoT-SORT's track_buffer keeps them
            alive for re-ID), but are not in the returned list.
        """
        conf_thresh = self._model_config.get("confidence_threshold", 0.35)
        img_size = self._model_config.get("image_size", 640)
        half = self._model_config.get("half_precision", True)

        try:
            results = self._model.track(
                frame,
                conf=conf_thresh,
                imgsz=img_size,
                half=half,
                tracker=self._tracker_config,
                persist=True,   # Maintain tracking state across calls
                verbose=False,
            )
        except Exception as e:
            logger.warning(f"Tracking inference failed: {e}")
            return list(self._get_active_tracks())

        self._active_ids.clear()
        active_vehicles: list[TrackedVehicle] = []

        if not results or len(results) == 0:
            return active_vehicles

        result = results[0]

        if result.boxes is None or len(result.boxes) == 0:
            return active_vehicles

        boxes = result.boxes

        # Check if tracking IDs are available
        if boxes.id is None:
            logger.debug("No track IDs assigned this frame (BoT-SORT initializing)")
            return active_vehicles

        for i in range(len(boxes)):
            track_id = int(boxes.id[i].item())
            class_id = int(boxes.cls[i].item())
            confidence = float(boxes.conf[i].item())
            bbox = boxes.xyxy[i].cpu().numpy().astype(float)

            # Filter to vehicle classes only
            class_name = self._resolve_class_name(class_id)
            if class_name is None:
                continue

            self._active_ids.add(track_id)

            # Update or create TrackedVehicle
            if track_id in self._tracks:
                vehicle = self._tracks[track_id]
                vehicle.bbox = bbox
                vehicle.confidence = confidence
                vehicle.class_id = class_id
                vehicle.class_name = class_name
                vehicle.is_active = True
                vehicle.frames_tracked += 1
            else:
                vehicle = TrackedVehicle(
                    track_id=track_id,
                    bbox=bbox,
                    confidence=confidence,
                    class_id=class_id,
                    class_name=class_name,
                    frames_tracked=1,
                    is_active=True,
                )
                self._tracks[track_id] = vehicle

            # Append bottom-center to pixel trajectory
            bc = vehicle.bottom_center
            vehicle.trajectory_px.append(bc)

            # Trim trajectory to prevent unbounded growth
            if len(vehicle.trajectory_px) > MAX_TRAJECTORY_LENGTH:
                vehicle.trajectory_px = vehicle.trajectory_px[-MAX_TRAJECTORY_LENGTH:]
            if len(vehicle.trajectory_world) > MAX_TRAJECTORY_LENGTH:
                vehicle.trajectory_world = vehicle.trajectory_world[-MAX_TRAJECTORY_LENGTH:]
            if len(vehicle.lane_history) > MAX_TRAJECTORY_LENGTH:
                vehicle.lane_history = vehicle.lane_history[-MAX_TRAJECTORY_LENGTH:]

            active_vehicles.append(vehicle)

        # Mark inactive tracks
        for tid, vehicle in self._tracks.items():
            if tid not in self._active_ids:
                vehicle.is_active = False

        return active_vehicles

    def _resolve_class_name(self, class_id: int) -> Optional[str]:
        """Map class ID to our target class name (same logic as detector.py)."""
        if self._is_custom_model:
            return self._class_map.get(class_id)
        else:
            if class_id in self.COCO_VEHICLE_IDS:
                return self.COCO_TO_CUSTOM.get(class_id)
            return None

    def _get_active_tracks(self) -> list[TrackedVehicle]:
        """Return currently active tracked vehicles."""
        return [v for v in self._tracks.values() if v.is_active]

    def get_track(self, track_id: int) -> Optional[TrackedVehicle]:
        """Retrieve a specific tracked vehicle by ID."""
        return self._tracks.get(track_id)

    def get_all_tracks(self) -> dict[int, TrackedVehicle]:
        """Get the full track registry (active + recently lost)."""
        return self._tracks

    def cleanup_lost_tracks(self, max_lost_frames: int = 120) -> int:
        """Remove tracks that have been inactive for too long.

        Called periodically to prevent memory buildup from old tracks.

        Args:
            max_lost_frames: Remove tracks inactive for more than this many frames.

        Returns:
            Number of tracks removed.
        """
        to_remove = []
        for tid, vehicle in self._tracks.items():
            if not vehicle.is_active:
                # We don't track exact lost-frame count here (BoT-SORT handles
                # re-ID internally), so we use a simple heuristic: remove tracks
                # that haven't been active for a while
                to_remove.append(tid)

        # Only remove if we have a lot of inactive tracks (conservative cleanup)
        if len(to_remove) > max_lost_frames:
            oldest = to_remove[:len(to_remove) - max_lost_frames]
            for tid in oldest:
                del self._tracks[tid]
            return len(oldest)

        return 0

    @property
    def active_count(self) -> int:
        """Number of currently active tracks."""
        return len(self._active_ids)

    @property
    def total_tracks(self) -> int:
        """Total number of tracks in registry (active + lost)."""
        return len(self._tracks)
