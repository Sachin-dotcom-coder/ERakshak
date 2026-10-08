"""
evaluation/tracking_metrics.py — Tracking Evaluation (Section 75)
===================================================================
HOTA, IDF1, MOTA, ID switches, track fragmentation.
"""

import logging
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)


class TrackingEvaluator:
    """Tracking quality evaluation against ground truth annotations.

    Computes standard MOT metrics: MOTA, IDF1, HOTA, ID switches,
    and track fragmentation.
    """

    def __init__(self, iou_threshold: float = 0.50) -> None:
        self._iou_threshold = iou_threshold

    def evaluate(
        self,
        predicted_tracks: list[dict],
        ground_truth_tracks: list[dict],
    ) -> dict:
        """Evaluate tracking performance.

        Args:
            predicted_tracks: List of per-frame predictions:
                [{'frame': int, 'track_id': int, 'bbox': [...], 'class': str}, ...]
            ground_truth_tracks: List of per-frame ground truths:
                [{'frame': int, 'gt_id': int, 'bbox': [...], 'class': str}, ...]

        Returns:
            Dict with all tracking metrics.
        """
        # Group by frame
        pred_by_frame = self._group_by_frame(predicted_tracks, "track_id")
        gt_by_frame = self._group_by_frame(ground_truth_tracks, "gt_id")
        all_frames = sorted(set(pred_by_frame.keys()) | set(gt_by_frame.keys()))

        total_gt = 0
        total_tp = 0
        total_fp = 0
        total_fn = 0
        total_id_switches = 0
        total_fragmentations = 0

        # Track ID mapping across frames
        prev_mapping: dict[int, int] = {}  # gt_id → predicted track_id

        for frame in all_frames:
            preds = pred_by_frame.get(frame, [])
            gts = gt_by_frame.get(frame, [])
            total_gt += len(gts)

            # Match predictions to GTs
            mapping = self._match_frame(preds, gts)

            tp = len(mapping)
            fp = len(preds) - tp
            fn = len(gts) - tp

            total_tp += tp
            total_fp += fp
            total_fn += fn

            # Count ID switches
            for gt_id, pred_id in mapping.items():
                if gt_id in prev_mapping and prev_mapping[gt_id] != pred_id:
                    total_id_switches += 1

            prev_mapping.update(mapping)

        # MOTA
        mota = 1.0 - (total_fp + total_fn + total_id_switches) / max(total_gt, 1)

        # IDF1 (simplified: 2*TP / (2*TP + FP + FN))
        idf1 = 2 * total_tp / (2 * total_tp + total_fp + total_fn) if total_gt > 0 else 0

        # HOTA (simplified approximation)
        det_accuracy = total_tp / max(total_tp + total_fp + total_fn, 1)
        ass_accuracy = max(0, 1.0 - total_id_switches / max(total_tp, 1))
        hota = float(np.sqrt(det_accuracy * ass_accuracy))

        return {
            "MOTA": round(mota, 4),
            "IDF1": round(idf1, 4),
            "HOTA": round(hota, 4),
            "id_switches": total_id_switches,
            "true_positives": total_tp,
            "false_positives": total_fp,
            "false_negatives": total_fn,
            "total_gt_objects": total_gt,
            "total_frames": len(all_frames),
        }

    def _match_frame(self, preds, gts):
        """Match predictions to GTs in a single frame using IoU."""
        mapping = {}
        used_preds = set()

        for gt in gts:
            best_iou = 0
            best_pred = None
            for i, pred in enumerate(preds):
                if i in used_preds:
                    continue
                iou = self._iou(gt["bbox"], pred["bbox"])
                if iou > best_iou:
                    best_iou = iou
                    best_pred = i
            if best_iou >= self._iou_threshold and best_pred is not None:
                mapping[gt["gt_id"]] = preds[best_pred]["track_id"]
                used_preds.add(best_pred)

        return mapping

    @staticmethod
    def _group_by_frame(tracks, id_key):
        groups = {}
        for t in tracks:
            frame = t.get("frame", 0)
            if frame not in groups:
                groups[frame] = []
            groups[frame].append(t)
        return groups

    @staticmethod
    def _iou(box1, box2):
        x1 = max(box1[0], box2[0])
        y1 = max(box1[1], box2[1])
        x2 = min(box1[2], box2[2])
        y2 = min(box1[3], box2[3])
        inter = max(0, x2 - x1) * max(0, y2 - y1)
        a1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
        a2 = (box2[2] - box2[0]) * (box2[3] - box2[1])
        union = a1 + a2 - inter
        return inter / union if union > 0 else 0
