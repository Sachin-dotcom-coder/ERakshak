"""
incidents/emergency.py — Multi-Signal Emergency Vehicle Detection (Sections 54-57)
====================================================================================
Upgrades emergency vehicle detection from single-frame classification to
temporal multi-signal fusion with a state machine.

Fusion Score:
  E = 0.35V + 0.20B + 0.20T + 0.15H + 0.10A

Where:
  V = visual class confidence
  B = beacon (flashing light) confidence
  T = temporal persistence confidence
  H = heading/approach confidence
  A = audio siren confidence (scaffolded)

State Machine:
  CANDIDATE → CONFIRMED → APPROACHING → PREEMPTION_REQUESTED → PASSED → CLEAR
"""

import logging
import time
from enum import Enum
from typing import Optional

import cv2
import numpy as np

logger = logging.getLogger(__name__)


class EmergencyState(str, Enum):
    NONE = "none"
    CANDIDATE = "candidate"
    CONFIRMED = "confirmed"
    APPROACHING = "approaching"
    PREEMPTION_REQUESTED = "preemption_requested"
    PASSED = "passed"
    CLEAR = "clear"


class EmergencyVehicleDetector:
    """Multi-signal emergency vehicle detection with temporal state machine.

    Args:
        config: Dict from thresholds.yaml under 'emergency'.
    """

    EMERGENCY_CLASSES: set[str] = {"ambulance", "fire_truck"}

    def __init__(self, config: dict) -> None:
        self._confirmation_frames: int = config.get("confirmation_frames", 5)
        self._preemption_threshold: float = config.get("preemption_threshold", 0.75)

        # Fusion weights (Section 57)
        weights = config.get("weights", {})
        self._w_visual: float = weights.get("visual", 0.35)
        self._w_beacon: float = weights.get("beacon", 0.20)
        self._w_temporal: float = weights.get("temporal", 0.20)
        self._w_heading: float = weights.get("heading", 0.15)
        self._w_audio: float = weights.get("audio", 0.10)

        # Per-track emergency state
        self._states: dict[int, EmergencyState] = {}
        self._candidate_frames: dict[int, int] = {}
        self._first_seen: dict[int, float] = {}
        self._confidence_history: dict[int, list[float]] = {}

        # Audio interface (scaffolded)
        self._audio_available: bool = False

    def update_vehicle(
        self,
        track_id: int,
        class_name: str,
        detection_confidence: float,
        bbox: np.ndarray,
        frame: np.ndarray,
        world_pos: Optional[tuple[float, float]] = None,
        heading_deg: float = 0.0,
        speed_kmph: float = 0.0,
        approach: str = "",
    ) -> dict:
        """Alias for update."""
        return self.update(
            track_id, class_name, detection_confidence, bbox, frame,
            world_pos, heading_deg, speed_kmph, approach
        )

    def update(
        self,
        track_id: int,
        class_name: str,
        detection_confidence: float,
        bbox: np.ndarray,
        frame: np.ndarray,
        world_pos: Optional[tuple[float, float]] = None,
        heading_deg: float = 0.0,
        speed_kmph: float = 0.0,
        approach: str = "",
    ) -> dict:
        """Update emergency detection state for a tracked vehicle.

        Args:
            track_id: Track identifier.
            class_name: Detected class name.
            detection_confidence: Detection confidence.
            bbox: [x1, y1, x2, y2] bounding box.
            frame: Full BGR frame (for beacon detection).
            world_pos: World coordinates (x_m, y_m).
            heading_deg: Vehicle heading.
            speed_kmph: Vehicle speed.
            approach: Approach direction (NS, EW, etc.).

        Returns:
            Dict with emergency state, confidence, and recommendation.
        """
        now = time.time()

        # Check if this is an emergency vehicle class
        is_emergency_class = class_name in self.EMERGENCY_CLASSES

        # Visual confidence
        visual_conf = detection_confidence if is_emergency_class else 0.0

        # Beacon detection (flashing lights)
        beacon_conf = self._detect_beacon(frame, bbox) if is_emergency_class else 0.0

        # Temporal persistence
        temporal_conf = self._compute_temporal(track_id, is_emergency_class, now)

        # Heading/approach confidence
        heading_conf = self._compute_heading_conf(heading_deg, speed_kmph, approach)

        # Audio confidence (scaffolded)
        audio_conf = self._get_audio_confidence() if self._audio_available else 0.0

        # Redistribute audio weight if unavailable
        if not self._audio_available:
            total_non_audio = (
                self._w_visual + self._w_beacon + self._w_temporal + self._w_heading
            )
            if total_non_audio > 0:
                scale = 1.0 / total_non_audio
                w_v = self._w_visual * scale
                w_b = self._w_beacon * scale
                w_t = self._w_temporal * scale
                w_h = self._w_heading * scale
            else:
                w_v = w_b = w_t = w_h = 0.25
            emergency_score = (
                w_v * visual_conf
                + w_b * beacon_conf
                + w_t * temporal_conf
                + w_h * heading_conf
            )
        else:
            emergency_score = (
                self._w_visual * visual_conf
                + self._w_beacon * beacon_conf
                + self._w_temporal * temporal_conf
                + self._w_heading * heading_conf
                + self._w_audio * audio_conf
            )

        # Track confidence history
        if track_id not in self._confidence_history:
            self._confidence_history[track_id] = []
        self._confidence_history[track_id].append(emergency_score)
        if len(self._confidence_history[track_id]) > 30:
            self._confidence_history[track_id] = (
                self._confidence_history[track_id][-30:]
            )

        # Update state machine
        state = self._update_state(track_id, emergency_score, is_emergency_class)

        result = {
            "track_id": track_id,
            "state": state.value,
            "emergency_score": round(emergency_score, 3),
            "visual_confidence": round(visual_conf, 3),
            "beacon_confidence": round(beacon_conf, 3),
            "temporal_confidence": round(temporal_conf, 3),
            "heading_confidence": round(heading_conf, 3),
            "audio_confidence": round(audio_conf, 3),
            "should_preempt": (
                state in (EmergencyState.CONFIRMED, EmergencyState.APPROACHING)
                and emergency_score >= self._preemption_threshold
            ),
            "approach": approach,
        }

        if state == EmergencyState.CONFIRMED:
            logger.info(
                f"🚨 Emergency vehicle CONFIRMED: track={track_id}, "
                f"class={class_name}, score={emergency_score:.2f}, "
                f"approach={approach}"
            )

        return result

    def _detect_beacon(
        self,
        frame: np.ndarray,
        bbox: np.ndarray,
    ) -> float:
        """Detect flashing beacon lights in the vehicle's bounding box region.

        Looks for high-saturation red/blue/white pixels in the upper
        portion of the bbox (where roof-mounted beacons are located).
        """
        x1, y1, x2, y2 = int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])
        h, w = frame.shape[:2]
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(w, x2), min(h, y2)

        if (x2 - x1) < 10 or (y2 - y1) < 10:
            return 0.0

        # Focus on upper 30% of bbox (roof area)
        upper_y = y1 + int((y2 - y1) * 0.3)
        upper_region = frame[y1:upper_y, x1:x2]

        if upper_region.size == 0:
            return 0.0

        hsv = cv2.cvtColor(upper_region, cv2.COLOR_BGR2HSV)

        # Red beacon: low or high hue, high saturation, high value
        red_low = cv2.inRange(hsv, (0, 120, 100), (10, 255, 255))
        red_high = cv2.inRange(hsv, (170, 120, 100), (180, 255, 255))
        red_mask = red_low | red_high

        # Blue beacon
        blue_mask = cv2.inRange(hsv, (100, 120, 100), (130, 255, 255))

        # White beacon (high brightness, low saturation)
        white_mask = cv2.inRange(hsv, (0, 0, 200), (180, 30, 255))

        # Combined beacon pixels
        beacon_mask = red_mask | blue_mask | white_mask
        total_pixels = upper_region.shape[0] * upper_region.shape[1]
        beacon_pixels = np.sum(beacon_mask > 0)

        beacon_ratio = beacon_pixels / total_pixels if total_pixels > 0 else 0
        # Normalize: 5% beacon pixels → confidence 0.5, 15%+ → 1.0
        confidence = min(1.0, beacon_ratio / 0.15)

        return float(confidence)

    def _compute_temporal(
        self,
        track_id: int,
        is_emergency: bool,
        now: float,
    ) -> float:
        """Compute temporal persistence confidence."""
        if not is_emergency:
            self._candidate_frames.pop(track_id, None)
            return 0.0

        if track_id not in self._first_seen:
            self._first_seen[track_id] = now

        frames = self._candidate_frames.get(track_id, 0) + 1
        self._candidate_frames[track_id] = frames

        # Normalize: requires confirmation_frames for full confidence
        return min(1.0, frames / self._confirmation_frames)

    def _compute_heading_conf(
        self,
        heading_deg: float,
        speed_kmph: float,
        approach: str,
    ) -> float:
        """Compute heading/approach confidence.

        Higher confidence when heading toward the intersection and moving.
        """
        if speed_kmph < 2.0:
            return 0.3  # Stationary — moderate confidence

        # Moving toward intersection (any direction) is positive evidence
        if speed_kmph > 10.0:
            return 0.8

        return 0.5

    def _get_audio_confidence(self) -> float:
        """Get audio siren confidence. Scaffolded for future microphone input."""
        return 0.0

    def _update_state(
        self,
        track_id: int,
        score: float,
        is_emergency: bool,
    ) -> EmergencyState:
        """Update the emergency state machine (Section 55)."""
        current = self._states.get(track_id, EmergencyState.NONE)

        if not is_emergency and score < 0.3:
            if current in (EmergencyState.PASSED, EmergencyState.CLEAR):
                self._states[track_id] = EmergencyState.CLEAR
            elif current != EmergencyState.NONE:
                self._states[track_id] = EmergencyState.PASSED
            return self._states.get(track_id, EmergencyState.NONE)

        if current == EmergencyState.NONE:
            if is_emergency:
                self._states[track_id] = EmergencyState.CANDIDATE
            return self._states[track_id]

        if current == EmergencyState.CANDIDATE:
            frames = self._candidate_frames.get(track_id, 0)
            if frames >= self._confirmation_frames:
                self._states[track_id] = EmergencyState.CONFIRMED

        elif current == EmergencyState.CONFIRMED:
            if score >= self._preemption_threshold:
                self._states[track_id] = EmergencyState.APPROACHING

        elif current == EmergencyState.APPROACHING:
            if score >= self._preemption_threshold:
                self._states[track_id] = EmergencyState.PREEMPTION_REQUESTED

        return self._states[track_id]

    def get_active_emergencies(self) -> list[dict]:
        """Get all currently active emergency vehicles."""
        active = []
        for tid, state in self._states.items():
            if state in (
                EmergencyState.CONFIRMED,
                EmergencyState.APPROACHING,
                EmergencyState.PREEMPTION_REQUESTED,
            ):
                hist = self._confidence_history.get(tid, [])
                avg_score = float(np.mean(hist)) if hist else 0.0
                active.append({
                    "track_id": tid,
                    "state": state.value,
                    "avg_confidence": round(avg_score, 3),
                })
        return active

    def cleanup_track(self, track_id: int) -> None:
        """Remove state for a lost track."""
        self._states.pop(track_id, None)
        self._candidate_frames.pop(track_id, None)
        self._first_seen.pop(track_id, None)
        self._confidence_history.pop(track_id, None)
