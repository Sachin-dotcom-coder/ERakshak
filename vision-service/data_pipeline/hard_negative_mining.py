"""
data_pipeline/hard_negative_mining.py — Hard-Negative Mining (Section 9)
=========================================================================
Automatically collects difficult examples for retraining:
- Low confidence detections
- Class instability (oscillating classifications)
- Track loss/reappearance (ID switches)
- Detector disagreement
- Queue count inconsistencies
"""

import logging
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

import cv2
import numpy as np

logger = logging.getLogger(__name__)


class HardNegativeMiner:
    """Automatic hard-case frame collection for dataset improvement.

    Monitors detection quality and saves difficult frames for human review
    and retraining.

    Args:
        output_dir: Directory to save hard cases.
        config: Dict with mining thresholds.
    """

    def __init__(
        self,
        output_dir: str = "failure_cases",
        config: Optional[dict] = None,
    ) -> None:
        cfg = config or {}
        self._output_dir = Path(output_dir)
        self._low_conf_threshold: float = cfg.get("low_confidence", 0.40)
        self._save_class_instability: bool = cfg.get("class_instability", True)
        self._save_id_switch: bool = cfg.get("id_switch", True)
        self._save_queue_inconsistency: bool = cfg.get("queue_inconsistency", True)

        # Create subdirectories
        self._categories = [
            "low_confidence", "class_instability", "tracking",
            "queue_inconsistency", "detector_disagreement",
        ]
        for cat in self._categories:
            (self._output_dir / cat).mkdir(parents=True, exist_ok=True)

        self._save_count: int = 0
        self._max_per_session: int = cfg.get("max_saves_per_session", 500)

    def check_and_save(
        self,
        frame: np.ndarray,
        vehicles: list[dict],
        frame_index: int,
        junction_id: str = "unknown",
    ) -> list[dict]:
        """Check for hard cases and save them.

        Args:
            frame: BGR frame.
            vehicles: List of vehicle state dicts.
            frame_index: Current frame number.
            junction_id: Junction identifier.

        Returns:
            List of saved hard-case records.
        """
        if self._save_count >= self._max_per_session:
            return []

        saved = []

        for v in vehicles:
            # Low confidence detection
            conf = v.get("detection_confidence", 1.0)
            if conf < self._low_conf_threshold:
                record = self._save_frame(
                    frame, "low_confidence", frame_index, junction_id,
                    reason=f"confidence={conf:.2f}",
                    track_id=v.get("track_id"),
                    metadata={"confidence": conf, "class": v.get("class_name")},
                )
                if record:
                    saved.append(record)

            # Class instability
            if self._save_class_instability:
                stability = v.get("class_stability", 1.0)
                if stability < 0.5:
                    record = self._save_frame(
                        frame, "class_instability", frame_index, junction_id,
                        reason=f"stability={stability:.2f}",
                        track_id=v.get("track_id"),
                        metadata={
                            "stability": stability,
                            "class": v.get("class_name"),
                        },
                    )
                    if record:
                        saved.append(record)

        return saved

    def check_id_switch(
        self,
        frame: np.ndarray,
        track_id: int,
        frame_index: int,
        junction_id: str = "unknown",
    ) -> Optional[dict]:
        """Save frame when an ID switch is suspected."""
        if not self._save_id_switch:
            return None
        return self._save_frame(
            frame, "tracking", frame_index, junction_id,
            reason="id_switch_suspected",
            track_id=track_id,
        )

    def check_queue_inconsistency(
        self,
        frame: np.ndarray,
        lane_id: str,
        detected_count: int,
        expected_count: int,
        frame_index: int,
        junction_id: str = "unknown",
    ) -> Optional[dict]:
        """Save frame when queue count is inconsistent."""
        if not self._save_queue_inconsistency:
            return None
        if abs(detected_count - expected_count) > 5:
            return self._save_frame(
                frame, "queue_inconsistency", frame_index, junction_id,
                reason=f"detected={detected_count}, expected≈{expected_count}",
                metadata={"lane_id": lane_id, "detected": detected_count},
            )
        return None

    def _save_frame(
        self,
        frame: np.ndarray,
        category: str,
        frame_index: int,
        junction_id: str,
        reason: str = "",
        track_id: Optional[int] = None,
        metadata: Optional[dict] = None,
    ) -> Optional[dict]:
        """Save a hard-case frame."""
        if self._save_count >= self._max_per_session:
            return None

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{junction_id}_{timestamp}_f{frame_index:06d}.jpg"
        filepath = self._output_dir / category / filename

        cv2.imwrite(str(filepath), frame)
        self._save_count += 1

        record = {
            "category": category,
            "frame_path": str(filepath),
            "frame_index": frame_index,
            "junction_id": junction_id,
            "reason": reason,
            "track_id": track_id,
            "timestamp": timestamp,
        }
        if metadata:
            record.update(metadata)

        # Append to JSONL log
        log_path = self._output_dir / category / "log.jsonl"
        with open(str(log_path), "a") as f:
            f.write(json.dumps(record) + "\n")

        return record

    @property
    def save_count(self) -> int:
        return self._save_count
