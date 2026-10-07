"""
data_pipeline/active_learning.py — Uncertainty-Based Active Learning (Section 10)
==================================================================================
Selects the most informative frames for annotation by computing an
uncertainty score that combines multiple signals.

uncertainty = 0.30*low_confidence + 0.20*class_instability +
              0.20*tracking_instability + 0.15*occlusion + 0.15*disagreement
"""

import logging
import json
from pathlib import Path
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)


class ActiveLearningSelector:
    """Select frames for annotation based on model uncertainty.

    Instead of random sampling, selects frames where the model is most
    uncertain — making annotation more efficient.

    Args:
        config: Dict with active learning settings.
    """

    def __init__(self, config: Optional[dict] = None) -> None:
        cfg = config or {}
        self._w_conf: float = cfg.get("w_low_confidence", 0.30)
        self._w_class: float = cfg.get("w_class_instability", 0.20)
        self._w_track: float = cfg.get("w_tracking_instability", 0.20)
        self._w_occ: float = cfg.get("w_occlusion", 0.15)
        self._w_disagree: float = cfg.get("w_disagreement", 0.15)

        # Candidate pool
        self._candidates: list[dict] = []

    def score_frame(
        self,
        frame_index: int,
        vehicles: list[dict],
        frame_path: Optional[str] = None,
    ) -> float:
        """Compute uncertainty score for a frame.

        Args:
            frame_index: Frame number.
            vehicles: List of vehicle state dicts in the frame.
            frame_path: Path to saved frame (optional).

        Returns:
            Uncertainty score (0-1). Higher = more informative.
        """
        if not vehicles:
            return 0.0

        # Average low-confidence evidence
        confidences = [v.get("detection_confidence", 1.0) for v in vehicles]
        low_conf = 1.0 - float(np.mean(confidences))

        # Class instability evidence
        stabilities = [v.get("class_stability", 1.0) for v in vehicles]
        class_instab = 1.0 - float(np.mean(stabilities))

        # Tracking instability
        track_confs = [v.get("tracking_confidence", 1.0) for v in vehicles]
        track_instab = 1.0 - float(np.mean(track_confs))

        # Occlusion
        occlusions = [v.get("occlusion_ratio", 0.0) for v in vehicles]
        occ_score = float(np.mean(occlusions))

        # Detector disagreement (if available)
        disagreements = [v.get("detector_disagreement", 0.0) for v in vehicles]
        disagree = float(np.mean(disagreements))

        uncertainty = (
            self._w_conf * low_conf
            + self._w_class * class_instab
            + self._w_track * track_instab
            + self._w_occ * occ_score
            + self._w_disagree * disagree
        )
        uncertainty = float(np.clip(uncertainty, 0.0, 1.0))

        self._candidates.append({
            "frame_index": frame_index,
            "frame_path": frame_path,
            "uncertainty": round(uncertainty, 4),
            "num_vehicles": len(vehicles),
            "mean_confidence": round(float(np.mean(confidences)), 3),
        })

        return uncertainty

    def select_top_n(self, n: int = 100) -> list[dict]:
        """Select the top-N most uncertain frames for annotation.

        Args:
            n: Number of frames to select.

        Returns:
            List of frame metadata dicts, sorted by uncertainty (descending).
        """
        sorted_candidates = sorted(
            self._candidates, key=lambda x: x["uncertainty"], reverse=True
        )
        return sorted_candidates[:n]

    def export_selection(
        self,
        output_path: str,
        n: int = 100,
    ) -> None:
        """Export selected frames to a JSONL file for annotation workflow."""
        selected = self.select_top_n(n)
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w") as f:
            for entry in selected:
                f.write(json.dumps(entry) + "\n")

        logger.info(
            f"Exported {len(selected)} frames for annotation to {output_path}"
        )

    def reset(self) -> None:
        """Clear candidate pool."""
        self._candidates.clear()
