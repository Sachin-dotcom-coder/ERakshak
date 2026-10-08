"""
tracking/tracker.py — Refactored BoT-SORT Tracking Wrapper (Section 20-23)
============================================================================
Bridges Ultralytics BoT-SORT tracking with the upgraded TrackState system.

Responsibilities:
- Runs model.track() to get raw tracking results
- Maintains per-track TrackState objects with full history
- Integrates occlusion estimation
- Computes track quality scores via ReID manager
- Exports VehicleState objects for downstream modules
- Handles track lifecycle: creation, update, loss, reappearance
"""

import logging
from typing import Optional

import numpy as np

from tracking.track_state import TrackLifecycle, TrackState, VehicleState
from tracking.occlusion import OcclusionEstimator
from tracking.reid import ReIDManager, TrackQualityScorer

logger = logging.getLogger(__name__)


class VehicleTrackerV2:
    """Upgraded BoT-SORT tracking wrapper with rich state management.

    Integrates the YOLO26 model's built-in tracking with the upgraded
    TrackState system, occlusion estimation, and track quality scoring.

    Args:
        model: Loaded YOLO model instance (with .track() support).
        tracker_config_path: Path to BoT-SORT YAML config.
        temporal_config: Dict from thresholds.yaml under 'temporal'.
        tracking_config: Dict from thresholds.yaml under 'tracking'.
        occlusion_config: Dict from thresholds.yaml under 'occlusion'.
        model_config: Model config dict for class resolution.
    """

    def __init__(
        self,
        model,
        tracker_config_path: str = "trackers/botsort_custom.yaml",
        temporal_config: Optional[dict] = None,
        tracking_config: Optional[dict] = None,
        occlusion_config: Optional[dict] = None,
        model_config: Optional[dict] = None,
    ) -> None:
        self._model = model
        self._tracker_config = tracker_config_path
        self._temporal_config = temporal_config or {}
        self._tracking_config = tracking_config or {}
        self._model_config = model_config or {}

        # Track states keyed by track_id
        self._tracks: dict[int, TrackState] = {}

        # Occlusion estimator
        self._occlusion = OcclusionEstimator(occlusion_config or {})

        # Re-ID and quality scoring
        self._reid = ReIDManager()
        self._quality = TrackQualityScorer(tracking_config or {})

        # Detect custom vs stock model
        model_names = getattr(self._model, "names", {})
        self._is_custom_model: bool = bool(model_names and "auto_rickshaw" in model_names.values())

        # Class resolution map
        self._class_map: dict[int, str] = {
            int(k): v
            for k, v in self._model_config.get("classes", {}).items()
        }

        # COCO fallback
        self._coco_map: dict[int, str] = {
            1: "cycle", 2: "car", 3: "two_wheeler", 5: "bus", 7: "truck",
        }
        self._coco_ids: set[int] = {1, 2, 3, 5, 7}

        # Track counters
        self._frame_count: int = 0

    def update(
        self,
        frame: np.ndarray,
        conf_threshold: float = 0.45,
    ) -> list[VehicleState]:
        """Run tracking on a frame and return updated vehicle states.

        Args:
            frame: BGR image.
            conf_threshold: Detection confidence threshold.

        Returns:
            List of VehicleState objects for all active, confirmed tracks.
        """
        self._frame_count += 1

        # Run YOLO model.track() for combined detection + tracking
        try:
            results = self._model.track(
                frame,
                conf=conf_threshold,
                persist=True,
                tracker=self._tracker_config,
                verbose=False,
            )
        except Exception as e:
            logger.warning(f"Tracking inference failed: {e}")
            self._mark_all_missing()
            return self._get_active_states()

        # Parse tracking results
        current_track_ids: set[int] = set()
        current_bboxes: list[np.ndarray] = []
        current_indices: list[int] = []  # Map bbox index → track_id

        for result in results:
            if result.boxes is None or len(result.boxes) == 0:
                continue

            boxes = result.boxes.xyxy.cpu().numpy()
            confidences = result.boxes.conf.cpu().numpy()
            class_ids = result.boxes.cls.cpu().numpy().astype(int)

            # Track IDs (may be None if tracking fails)
            track_ids = None
            if result.boxes.id is not None:
                track_ids = result.boxes.id.cpu().numpy().astype(int)

            for i, (bbox, conf, cls_id) in enumerate(
                zip(boxes, confidences, class_ids)
            ):
                class_name = self._resolve_class(cls_id)
                if class_name is None:
                    continue

                # Get track ID
                tid = int(track_ids[i]) if track_ids is not None else -(i + 1)
                current_track_ids.add(tid)
                current_bboxes.append(bbox)

                # Create or update TrackState
                if tid not in self._tracks:
                    self._tracks[tid] = TrackState(
                        track_id=tid,
                        config=self._temporal_config,
                    )

                self._tracks[tid].update(
                    class_name=class_name,
                    confidence=float(conf),
                    bbox=bbox,
                )

        # Estimate occlusion for all current vehicles
        if current_bboxes:
            occlusion_ratios = self._occlusion.estimate_all(current_bboxes)
        else:
            occlusion_ratios = []

        # Mark missing tracks
        for tid, track in list(self._tracks.items()):
            if tid not in current_track_ids:
                track.mark_missing()
                if track.is_lost:
                    self._cleanup_track(tid)

        # Periodically clean up Re-ID embeddings
        if self._frame_count % 100 == 0:
            active_ids = set(self._tracks.keys())
            self._reid.cleanup_old(active_ids)

        return self._get_active_states()

    def _get_active_states(self) -> list[VehicleState]:
        """Export VehicleState objects for all active, confirmed tracks."""
        states: list[VehicleState] = []

        for tid, track in self._tracks.items():
            if track.is_lost:
                continue

            vs = track.to_vehicle_state()

            # Compute track quality score
            vs.track_confidence = self._quality.compute_quality(
                detection_confidence=track.mean_confidence,
                reid_confidence=0.5,  # Default when Re-ID not available
                motion_consistency=track.motion_stability,
                class_stability=track.class_stability,
            )

            states.append(vs)

        return states

    def _mark_all_missing(self) -> None:
        """Mark all tracks as missing (used when tracking fails)."""
        for track in self._tracks.values():
            track.mark_missing()

    def _cleanup_track(self, track_id: int) -> None:
        """Remove a lost track and clean up associated state."""
        self._tracks.pop(track_id, None)
        self._reid.remove_track(track_id)

    def _resolve_class(self, cls_id: int) -> Optional[str]:
        """Resolve class ID to class name."""
        if self._is_custom_model and self._class_map:
            return self._class_map.get(cls_id)
        if cls_id in self._coco_ids:
            return self._coco_map.get(cls_id)
        return None

    def get_track_state(self, track_id: int) -> Optional[TrackState]:
        """Get the full TrackState for a specific track."""
        return self._tracks.get(track_id)

    @property
    def active_count(self) -> int:
        """Number of currently active (non-lost) tracks."""
        return sum(
            1 for t in self._tracks.values()
            if not t.is_lost
        )

    @property
    def confirmed_count(self) -> int:
        """Number of confirmed (past temporal threshold) tracks."""
        return sum(
            1 for t in self._tracks.values()
            if t.is_confirmed and not t.is_lost
        )

    @property
    def total_tracks_created(self) -> int:
        """Total tracks ever created (for debugging)."""
        return len(self._tracks)
