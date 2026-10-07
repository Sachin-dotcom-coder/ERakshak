"""
tracking/track_state.py — Rich Track State & Temporal Logic (Sections 17-19, 24)
==================================================================================
The fundamental unit of perception: VehicleState — carrying detection,
tracking, class, position, velocity, heading, lane, maneuver, queue,
occlusion, and confidence information for every tracked vehicle.

Implements:
- Temporal detection confirmation (Section 17)
- Detection history tracking (Section 18)
- Class stabilization via voting (Section 19)
- Full VehicleState dataclass (Section 24)
"""

import logging
import time
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)


class TrackLifecycle(str, Enum):
    """Track lifecycle states (Section 20)."""
    NEW = "NEW"
    TENTATIVE = "TENTATIVE"
    CONFIRMED = "CONFIRMED"
    VISIBLE = "VISIBLE"
    PARTIALLY_OCCLUDED = "PARTIALLY_OCCLUDED"
    HEAVILY_OCCLUDED = "HEAVILY_OCCLUDED"
    PREDICTED = "PREDICTED"
    REAPPEARED = "REAPPEARED"
    LOST = "LOST"


@dataclass
class VehicleState:
    """Comprehensive vehicle state — the fundamental perception unit (Section 24).

    This replaces the simple (bbox, class, confidence) with a rich object
    carrying everything downstream modules need.
    """
    track_id: int
    class_name: str
    detection_confidence: float
    track_confidence: float = 0.0
    bbox: Optional[np.ndarray] = None       # [x1,y1,x2,y2] pixels
    ground_contact: Optional[tuple[float, float]] = None  # pixel coords
    world_x: float = 0.0
    world_y: float = 0.0
    speed_kmph: float = 0.0
    acceleration_mps2: float = 0.0
    heading_deg: float = 0.0                # 0=North, clockwise
    lane_id: Optional[str] = None
    maneuver: str = "unknown"               # straight|left|right|u-turn
    queue_probability: float = 0.0
    occlusion_ratio: float = 0.0
    age_frames: int = 0
    state: TrackLifecycle = TrackLifecycle.NEW
    is_confirmed: bool = False


class TrackState:
    """Per-track temporal state manager (Section 18).

    Maintains history of detections, classes, confidences, positions,
    speeds, and headings for a single tracked vehicle. Computes
    stability metrics for downstream confidence estimation.

    Args:
        track_id: Persistent track ID from BoT-SORT.
        config: Dict from thresholds.yaml under 'temporal'.
    """

    def __init__(self, track_id: int, config: dict) -> None:
        self.track_id = track_id
        self._config = config

        # Confirmation thresholds
        self._confirmation_frames: int = config.get("confirmation_frames", 3)
        self._max_missing: int = config.get("max_missing_frames", 15)
        self._class_window: int = config.get("class_switch_window", 10)
        self._critical_confirmation: int = config.get("critical_confirmation", 5)

        # History buffers (Section 18)
        self.class_history: list[str] = []
        self.confidence_history: list[float] = []
        self.bbox_history: list[np.ndarray] = []
        self.world_position_history: list[tuple[float, float]] = []
        self.speed_history: list[float] = []
        self.heading_history: list[float] = []
        self.timestamp_history: list[float] = []

        # Class voting (Section 19)
        self._class_votes: dict[str, float] = defaultdict(float)

        # Lifecycle
        self.state: TrackLifecycle = TrackLifecycle.NEW
        self.frames_seen: int = 0
        self.frames_missing: int = 0
        self.is_confirmed: bool = False
        self.total_frames: int = 0

        # Current best class
        self.stable_class: Optional[str] = None
        self.class_confidence: float = 0.0

        self._max_history: int = 300  # ~30s at 10 FPS

    def update(
        self,
        class_name: str,
        confidence: float,
        bbox: np.ndarray,
        world_pos: Optional[tuple[float, float]] = None,
        speed: float = 0.0,
        heading: float = 0.0,
    ) -> None:
        """Update track state with new detection.

        Args:
            class_name: Detected class name.
            confidence: Detection confidence.
            bbox: Bounding box [x1,y1,x2,y2].
            world_pos: World coordinates (x_m, y_m) if available.
            speed: Current speed in km/h.
            heading: Current heading in degrees.
        """
        now = time.time()

        # Append to histories
        self.class_history.append(class_name)
        self.confidence_history.append(confidence)
        self.bbox_history.append(bbox.copy())
        self.timestamp_history.append(now)
        self.speed_history.append(speed)
        self.heading_history.append(heading)

        if world_pos is not None:
            self.world_position_history.append(world_pos)

        # Update class votes (Section 19)
        self._class_votes[class_name] += confidence

        # Trim histories to prevent unbounded growth
        self._trim_histories()

        # Update counters
        self.frames_seen += 1
        self.frames_missing = 0
        self.total_frames += 1

        # Compute stable class
        self._update_stable_class(class_name, confidence)

        # Update lifecycle state
        self._update_lifecycle()

    def mark_missing(self) -> None:
        """Mark this track as missing in the current frame."""
        self.frames_missing += 1
        self.total_frames += 1

        if self.state == TrackLifecycle.VISIBLE:
            self.state = TrackLifecycle.PREDICTED
        elif self.state == TrackLifecycle.PARTIALLY_OCCLUDED:
            self.state = TrackLifecycle.HEAVILY_OCCLUDED
        elif self.state == TrackLifecycle.HEAVILY_OCCLUDED:
            self.state = TrackLifecycle.PREDICTED

        if self.frames_missing >= self._max_missing:
            self.state = TrackLifecycle.LOST

    def mark_reappeared(self) -> None:
        """Mark this track as reappeared after being predicted/lost."""
        if self.state in (TrackLifecycle.PREDICTED, TrackLifecycle.HEAVILY_OCCLUDED):
            self.state = TrackLifecycle.REAPPEARED
            logger.debug(f"Track {self.track_id} reappeared after {self.frames_missing} frames")

    @property
    def is_lost(self) -> bool:
        return self.state == TrackLifecycle.LOST

    @property
    def mean_confidence(self) -> float:
        if not self.confidence_history:
            return 0.0
        # Use recent window
        recent = self.confidence_history[-30:]
        return float(np.mean(recent))

    @property
    def confidence_variance(self) -> float:
        if len(self.confidence_history) < 2:
            return 0.0
        recent = self.confidence_history[-30:]
        return float(np.var(recent))

    @property
    def class_stability(self) -> float:
        """How stable is the class assignment? 1.0 = perfectly stable."""
        if not self.class_history:
            return 0.0
        recent = self.class_history[-self._class_window:]
        if not recent:
            return 0.0
        most_common = max(set(recent), key=recent.count)
        return recent.count(most_common) / len(recent)

    @property
    def motion_stability(self) -> float:
        """How consistent is the motion? Based on heading variance."""
        if len(self.heading_history) < 3:
            return 1.0
        recent = self.heading_history[-20:]
        heading_std = float(np.std(recent))
        # Normalize: low std = high stability
        return max(0.0, 1.0 - heading_std / 180.0)

    def _update_stable_class(self, latest_class: str, latest_conf: float) -> None:
        """Update stable class via voting (Section 19).

        A vehicle shouldn't oscillate between classes. Use accumulated
        weighted votes to determine the dominant class.
        """
        # Critical classes need stronger confirmation
        critical = {"ambulance", "fire_truck", "brts_bus"}

        if not self._class_votes:
            self.stable_class = latest_class
            self.class_confidence = latest_conf
            return

        # Find dominant class
        best_class = max(self._class_votes, key=self._class_votes.get)
        total_votes = sum(self._class_votes.values())
        best_ratio = self._class_votes[best_class] / total_votes if total_votes > 0 else 0

        # Only switch class if new class is substantially stronger
        if self.stable_class and best_class != self.stable_class:
            current_votes = self._class_votes.get(self.stable_class, 0)
            new_votes = self._class_votes[best_class]
            # Require 30% margin to switch
            if new_votes < current_votes * 1.3:
                return  # Keep current class

        self.stable_class = best_class
        self.class_confidence = best_ratio

    def _update_lifecycle(self) -> None:
        """Update track lifecycle state based on confirmation (Section 17)."""
        if self.state == TrackLifecycle.NEW:
            self.state = TrackLifecycle.TENTATIVE

        if self.state == TrackLifecycle.TENTATIVE:
            required = self._confirmation_frames
            # Critical classes need extra confirmation
            if self.stable_class in {"ambulance", "fire_truck", "brts_bus"}:
                required = self._critical_confirmation
            if self.frames_seen >= required:
                self.state = TrackLifecycle.CONFIRMED
                self.is_confirmed = True
                logger.debug(
                    f"Track {self.track_id} confirmed as {self.stable_class} "
                    f"after {self.frames_seen} frames"
                )

        if self.state == TrackLifecycle.CONFIRMED:
            self.state = TrackLifecycle.VISIBLE

        if self.state == TrackLifecycle.REAPPEARED:
            self.state = TrackLifecycle.VISIBLE

    def _trim_histories(self) -> None:
        """Trim history buffers to prevent unbounded memory growth."""
        max_len = self._max_history
        if len(self.class_history) > max_len:
            self.class_history = self.class_history[-max_len:]
            self.confidence_history = self.confidence_history[-max_len:]
            self.bbox_history = self.bbox_history[-max_len:]
            self.timestamp_history = self.timestamp_history[-max_len:]
            self.speed_history = self.speed_history[-max_len:]
            self.heading_history = self.heading_history[-max_len:]
        if len(self.world_position_history) > max_len:
            self.world_position_history = self.world_position_history[-max_len:]

    def to_vehicle_state(self) -> VehicleState:
        """Export current state as a VehicleState object."""
        bbox = self.bbox_history[-1] if self.bbox_history else None
        ground_contact = None
        if bbox is not None:
            x_center = (bbox[0] + bbox[2]) / 2.0
            y_bottom = bbox[3]
            ground_contact = (float(x_center), float(y_bottom))

        world_pos = (
            self.world_position_history[-1]
            if self.world_position_history
            else (0.0, 0.0)
        )

        return VehicleState(
            track_id=self.track_id,
            class_name=self.stable_class or "unknown",
            detection_confidence=self.mean_confidence,
            track_confidence=0.0,  # Set by reid module
            bbox=bbox,
            ground_contact=ground_contact,
            world_x=world_pos[0],
            world_y=world_pos[1],
            speed_kmph=self.speed_history[-1] if self.speed_history else 0.0,
            heading_deg=self.heading_history[-1] if self.heading_history else 0.0,
            age_frames=self.total_frames,
            state=self.state,
            is_confirmed=self.is_confirmed,
        )
