"""
evaluation/detection_metrics.py — Detection Evaluation (Section 74)
=====================================================================
Precision, Recall, F1, mAP@50, mAP@50:95, small-object recall,
per-class recall.
"""

import logging
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)


class DetectionEvaluator:
    """Detection quality evaluation against ground truth.

    Args:
        iou_thresholds: IoU thresholds for mAP computation.
        small_object_area: Max area (px²) to classify as "small object".
    """

    def __init__(
        self,
        iou_thresholds: Optional[list[float]] = None,
        small_object_area: float = 1024.0,
    ) -> None:
        self._iou_thresholds = iou_thresholds or [
            0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95
        ]
        self._small_area = small_object_area

    def evaluate(
        self,
        predictions: list[dict],
        ground_truths: list[dict],
    ) -> dict:
        """Evaluate detection performance.

        Args:
            predictions: List of {'bbox': [x1,y1,x2,y2], 'class': str, 'confidence': float}.
            ground_truths: List of {'bbox': [x1,y1,x2,y2], 'class': str}.

        Returns:
            Dict with all detection metrics.
        """
        if not ground_truths:
            return {"precision": 0, "recall": 0, "f1": 0, "mAP50": 0}

        # Match predictions to ground truths at IoU=0.50
        tp, fp, fn = self._match(predictions, ground_truths, iou_threshold=0.50)

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0

        # mAP@50
        map50 = self._compute_ap(predictions, ground_truths, 0.50)

        # mAP@50:95
        aps = [self._compute_ap(predictions, ground_truths, t) for t in self._iou_thresholds]
        map_50_95 = float(np.mean(aps)) if aps else 0.0

        # Small object metrics
        small_gt = [g for g in ground_truths if self._bbox_area(g["bbox"]) < self._small_area]
        small_preds = [p for p in predictions if self._bbox_area(p["bbox"]) < self._small_area]
        if small_gt:
            s_tp, s_fp, s_fn = self._match(small_preds, small_gt, 0.50)
            small_recall = s_tp / (s_tp + s_fn) if (s_tp + s_fn) > 0 else 0.0
            small_precision = s_tp / (s_tp + s_fp) if (s_tp + s_fp) > 0 else 0.0
        else:
            small_recall = 0.0
            small_precision = 0.0

        # Per-class recall
        classes = set(g["class"] for g in ground_truths)
        per_class = {}
        for cls in classes:
            cls_gt = [g for g in ground_truths if g["class"] == cls]
            cls_pred = [p for p in predictions if p["class"] == cls]
            c_tp, _, c_fn = self._match(cls_pred, cls_gt, 0.50)
            per_class[cls] = round(c_tp / (c_tp + c_fn) if (c_tp + c_fn) > 0 else 0.0, 3)

        return {
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4),
            "mAP50": round(map50, 4),
            "mAP50_95": round(map_50_95, 4),
            "small_object_recall": round(small_recall, 4),
            "small_object_precision": round(small_precision, 4),
            "per_class_recall": per_class,
            "total_predictions": len(predictions),
            "total_ground_truths": len(ground_truths),
        }

    def _match(self, preds, gts, iou_threshold):
        """Match predictions to ground truths."""
        matched_gt = set()
        tp = 0
        for p in sorted(preds, key=lambda x: x.get("confidence", 0), reverse=True):
            best_iou = 0
            best_idx = -1
            for i, g in enumerate(gts):
                if i in matched_gt:
                    continue
                if p.get("class") != g.get("class"):
                    continue
                iou = self._compute_iou(p["bbox"], g["bbox"])
                if iou > best_iou:
                    best_iou = iou
                    best_idx = i
            if best_iou >= iou_threshold and best_idx >= 0:
                tp += 1
                matched_gt.add(best_idx)
        fp = len(preds) - tp
        fn = len(gts) - len(matched_gt)
        return tp, fp, fn

    def _compute_ap(self, preds, gts, iou_threshold):
        """Compute Average Precision at a given IoU threshold."""
        tp, fp, fn = self._match(preds, gts, iou_threshold)
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        return float(precision * recall)

    @staticmethod
    def _compute_iou(box1, box2):
        x1 = max(box1[0], box2[0])
        y1 = max(box1[1], box2[1])
        x2 = min(box1[2], box2[2])
        y2 = min(box1[3], box2[3])
        inter = max(0, x2 - x1) * max(0, y2 - y1)
        area1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
        area2 = (box2[2] - box2[0]) * (box2[3] - box2[1])
        union = area1 + area2 - inter
        return inter / union if union > 0 else 0

    @staticmethod
    def _bbox_area(bbox):
        return (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])
