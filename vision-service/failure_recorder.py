"""
failure_recorder.py — Automatic Failure-Case Recording (Section 85)
=====================================================================
Saves frames when anomalous conditions are detected:
- Low confidence detections
- ID switch suspected
- Lane switch instability
- BRTS candidate
- Emergency candidate
- Camera shift
- Queue inconsistency

Directory structure:
  failure_cases/
  ├── detection/
  ├── tracking/
  ├── lane/
  ├── queue/
  ├── brts/
  ├── emergency/
  └── camera/
"""

import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

import cv2
import numpy as np

logger = logging.getLogger(__name__)


class FailureRecorder:
    """Automatic failure-case recording for continuous improvement.

    Saves frames and metadata when anomalous conditions are detected,
    creating the training data needed for the next model iteration.

    Args:
        config: Dict from thresholds.yaml under 'failure_recording'.
    """

    CATEGORIES = [
        "detection", "tracking", "lane", "queue",
        "brts", "emergency", "camera",
    ]

    def __init__(self, config: Optional[dict] = None) -> None:
        cfg = config or {}
        self._enabled: bool = cfg.get("enabled", True)
        self._output_dir = Path(cfg.get("output_dir", "failure_cases"))

        triggers = cfg.get("triggers", {})
        self._low_conf_threshold: float = triggers.get("low_confidence", 0.40)
        self._record_id_switch: bool = triggers.get("id_switch", True)
        self._record_lane_instability: bool = triggers.get("lane_instability", True)
        self._record_brts: bool = triggers.get("brts_candidate", True)
        self._record_emergency: bool = triggers.get("emergency_candidate", True)
        self._record_camera_shift: bool = triggers.get("camera_shift", True)
        self._record_queue_incons: bool = triggers.get("queue_inconsistency", True)

        # Create directories
        if self._enabled:
            for cat in self.CATEGORIES:
                (self._output_dir / cat).mkdir(parents=True, exist_ok=True)

        self._session_count: int = 0
        self._max_per_category: int = cfg.get("max_per_category", 200)
        self._category_counts: dict[str, int] = {c: 0 for c in self.CATEGORIES}

    def record_low_confidence(
        self,
        frame: np.ndarray,
        track_id: int,
        confidence: float,
        class_name: str,
        junction_id: str,
        frame_index: int,
    ) -> Optional[str]:
        """Record a low-confidence detection."""
        if not self._enabled or confidence >= self._low_conf_threshold:
            return None
        return self._save(
            frame, "detection", junction_id, frame_index,
            metadata={
                "track_id": track_id,
                "confidence": round(confidence, 3),
                "class": class_name,
                "reason": "low_confidence",
            },
        )

    def record_id_switch(
        self,
        frame: np.ndarray,
        old_id: int,
        new_id: int,
        junction_id: str,
        frame_index: int,
    ) -> Optional[str]:
        """Record a suspected ID switch."""
        if not self._enabled or not self._record_id_switch:
            return None
        return self._save(
            frame, "tracking", junction_id, frame_index,
            metadata={
                "old_track_id": old_id,
                "new_track_id": new_id,
                "reason": "id_switch",
            },
        )

    def record_lane_instability(
        self,
        frame: np.ndarray,
        track_id: int,
        lane_switches: int,
        junction_id: str,
        frame_index: int,
    ) -> Optional[str]:
        """Record lane assignment instability."""
        if not self._enabled or not self._record_lane_instability:
            return None
        return self._save(
            frame, "lane", junction_id, frame_index,
            metadata={
                "track_id": track_id,
                "lane_switches": lane_switches,
                "reason": "lane_instability",
            },
        )

    def record_brts_candidate(
        self,
        frame: np.ndarray,
        track_id: int,
        violation_state: str,
        junction_id: str,
        frame_index: int,
    ) -> Optional[str]:
        """Record a BRTS violation candidate."""
        if not self._enabled or not self._record_brts:
            return None
        return self._save(
            frame, "brts", junction_id, frame_index,
            metadata={
                "track_id": track_id,
                "violation_state": violation_state,
                "reason": "brts_candidate",
            },
        )

    def record_emergency_candidate(
        self,
        frame: np.ndarray,
        track_id: int,
        emergency_score: float,
        junction_id: str,
        frame_index: int,
    ) -> Optional[str]:
        """Record an emergency vehicle candidate."""
        if not self._enabled or not self._record_emergency:
            return None
        return self._save(
            frame, "emergency", junction_id, frame_index,
            metadata={
                "track_id": track_id,
                "emergency_score": round(emergency_score, 3),
                "reason": "emergency_candidate",
            },
        )

    def record_camera_shift(
        self,
        frame: np.ndarray,
        displacement_px: float,
        junction_id: str,
        frame_index: int,
    ) -> Optional[str]:
        """Record a camera shift event."""
        if not self._enabled or not self._record_camera_shift:
            return None
        return self._save(
            frame, "camera", junction_id, frame_index,
            metadata={
                "displacement_px": round(displacement_px, 2),
                "reason": "camera_shift",
            },
        )

    def record_queue_inconsistency(
        self,
        frame: np.ndarray,
        lane_id: str,
        detected: int,
        expected: int,
        junction_id: str,
        frame_index: int,
    ) -> Optional[str]:
        """Record a queue count inconsistency."""
        if not self._enabled or not self._record_queue_incons:
            return None
        return self._save(
            frame, "queue", junction_id, frame_index,
            metadata={
                "lane_id": lane_id,
                "detected_count": detected,
                "expected_count": expected,
                "reason": "queue_inconsistency",
            },
        )

    def _save(
        self,
        frame: np.ndarray,
        category: str,
        junction_id: str,
        frame_index: int,
        metadata: Optional[dict] = None,
    ) -> Optional[str]:
        """Save a failure case frame with metadata."""
        if self._category_counts.get(category, 0) >= self._max_per_category:
            return None

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = f"{junction_id}_{timestamp}_f{frame_index:06d}.jpg"
        filepath = self._output_dir / category / filename

        cv2.imwrite(str(filepath), frame)
        self._category_counts[category] = self._category_counts.get(category, 0) + 1
        self._session_count += 1

        # Write metadata
        record = {
            "frame_path": str(filepath),
            "junction_id": junction_id,
            "frame_index": frame_index,
            "category": category,
            "timestamp": timestamp,
        }
        if metadata:
            record.update(metadata)

        log_path = self._output_dir / category / "log.jsonl"
        with open(str(log_path), "a") as f:
            f.write(json.dumps(record) + "\n")

        return str(filepath)

    @property
    def session_count(self) -> int:
        return self._session_count

    @property
    def category_counts(self) -> dict[str, int]:
        return dict(self._category_counts)
