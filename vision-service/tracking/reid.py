"""
tracking/reid.py — Re-ID Embedding Management & Track Quality (Section 23)
============================================================================
Manages Re-ID feature embeddings and computes track quality scores
for downstream confidence estimation.

Track Quality Score:
  T = w1*C_d + w2*C_r + w3*C_m + w4*C_c

where:
  C_d = detection confidence
  C_r = Re-ID confidence (embedding match quality)
  C_m = motion consistency
  C_c = class consistency
"""

import logging
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)


class TrackQualityScorer:
    """Computes a composite track quality score from multiple signals.

    Combines detection confidence, Re-ID embedding match quality,
    motion consistency, and class assignment stability into a single
    0-1 quality score that feeds into downstream traffic-state confidence.

    Args:
        config: Dict from thresholds.yaml under 'tracking.quality_weights'.
    """

    def __init__(self, config: dict) -> None:
        weights = config.get("quality_weights", {})
        self._w_detection: float = weights.get("detection", 0.30)
        self._w_reid: float = weights.get("reid", 0.25)
        self._w_motion: float = weights.get("motion", 0.25)
        self._w_class: float = weights.get("class_consistency", 0.20)

    def compute_quality(
        self,
        detection_confidence: float,
        reid_confidence: float,
        motion_consistency: float,
        class_stability: float,
    ) -> float:
        """Compute composite track quality score.

        Args:
            detection_confidence: Mean detection confidence (0-1).
            reid_confidence: Re-ID embedding match quality (0-1).
                            Use 0.5 default if Re-ID not available.
            motion_consistency: Motion stability score (0-1).
            class_stability: Class assignment stability (0-1).

        Returns:
            Track quality score in [0.0, 1.0].
        """
        score = (
            self._w_detection * detection_confidence
            + self._w_reid * reid_confidence
            + self._w_motion * motion_consistency
            + self._w_class * class_stability
        )
        return float(np.clip(score, 0.0, 1.0))


class ReIDManager:
    """Manages Re-ID embeddings for track reappearance matching (Section 22).

    Stores the most recent Re-ID feature embedding for each track,
    enabling matching when a vehicle reappears after occlusion.
    """

    def __init__(self) -> None:
        # track_id → most recent embedding (128-dim or 256-dim float vector)
        self._embeddings: dict[int, np.ndarray] = {}

    def update_embedding(self, track_id: int, embedding: np.ndarray) -> None:
        """Store or update the Re-ID embedding for a track.

        Args:
            track_id: Track identifier.
            embedding: Feature embedding vector.
        """
        self._embeddings[track_id] = embedding.copy()

    def get_embedding(self, track_id: int) -> Optional[np.ndarray]:
        """Retrieve stored embedding for a track.

        Args:
            track_id: Track identifier.

        Returns:
            Embedding vector, or None if not stored.
        """
        return self._embeddings.get(track_id)

    def compute_similarity(
        self,
        embedding_a: np.ndarray,
        embedding_b: np.ndarray,
    ) -> float:
        """Compute cosine similarity between two embeddings.

        Args:
            embedding_a: First embedding vector.
            embedding_b: Second embedding vector.

        Returns:
            Cosine similarity in [-1.0, 1.0], where 1.0 = identical.
        """
        norm_a = np.linalg.norm(embedding_a)
        norm_b = np.linalg.norm(embedding_b)

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return float(np.dot(embedding_a, embedding_b) / (norm_a * norm_b))

    def find_best_match(
        self,
        query_embedding: np.ndarray,
        candidate_ids: list[int],
        min_similarity: float = 0.70,
    ) -> Optional[tuple[int, float]]:
        """Find the best matching track for a reappearing detection.

        Args:
            query_embedding: Embedding of the reappearing detection.
            candidate_ids: List of lost track IDs to match against.
            min_similarity: Minimum cosine similarity threshold.

        Returns:
            (track_id, similarity) of best match, or None if no match.
        """
        best_id: Optional[int] = None
        best_sim: float = min_similarity

        for tid in candidate_ids:
            stored = self._embeddings.get(tid)
            if stored is None:
                continue

            sim = self.compute_similarity(query_embedding, stored)
            if sim > best_sim:
                best_sim = sim
                best_id = tid

        if best_id is not None:
            return (best_id, best_sim)
        return None

    def remove_track(self, track_id: int) -> None:
        """Remove stored embedding for a lost track."""
        self._embeddings.pop(track_id, None)

    def cleanup_old(self, active_ids: set[int], max_lost_tracks: int = 100) -> None:
        """Remove embeddings for tracks that are no longer relevant."""
        stored_ids = set(self._embeddings.keys())
        lost_ids = stored_ids - active_ids
        if len(lost_ids) > max_lost_tracks:
            # Remove oldest lost tracks
            for tid in list(lost_ids)[: len(lost_ids) - max_lost_tracks]:
                self._embeddings.pop(tid, None)
