"""
evaluation/traffic_metrics.py — Traffic State Evaluation (Section 76)
=======================================================================
Vehicle count MAE, queue length MAE, speed MAE, lane assignment accuracy.
"""

import logging
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)


class TrafficStateEvaluator:
    """Evaluate traffic state estimation accuracy.

    Compares estimated traffic state against ground-truth annotations.
    """

    def evaluate_counts(
        self,
        predicted: list[int],
        actual: list[int],
    ) -> dict:
        """Evaluate vehicle count accuracy.

        Args:
            predicted: List of predicted counts per interval.
            actual: List of actual counts per interval.

        Returns:
            Dict with count metrics.
        """
        if not predicted or not actual:
            return {"mae": 0, "rmse": 0, "mape": 0}

        pred = np.array(predicted, dtype=float)
        act = np.array(actual, dtype=float)
        n = min(len(pred), len(act))
        pred, act = pred[:n], act[:n]

        errors = np.abs(pred - act)
        mae = float(np.mean(errors))
        rmse = float(np.sqrt(np.mean(errors ** 2)))
        mape = float(np.mean(errors / np.maximum(act, 1)) * 100)

        return {
            "count_mae": round(mae, 2),
            "count_rmse": round(rmse, 2),
            "count_mape_pct": round(mape, 2),
            "n_samples": n,
        }

    def evaluate_queue(
        self,
        predicted: list[float],
        actual: list[float],
    ) -> dict:
        """Evaluate queue length estimation accuracy."""
        if not predicted or not actual:
            return {"queue_mae": 0}

        pred = np.array(predicted)
        act = np.array(actual)
        n = min(len(pred), len(act))
        pred, act = pred[:n], act[:n]

        errors = np.abs(pred - act)
        return {
            "queue_mae_m": round(float(np.mean(errors)), 2),
            "queue_rmse_m": round(float(np.sqrt(np.mean(errors ** 2))), 2),
            "queue_max_error_m": round(float(np.max(errors)), 2),
            "n_samples": n,
        }

    def evaluate_speed(
        self,
        predicted: list[float],
        actual: list[float],
    ) -> dict:
        """Evaluate speed estimation accuracy."""
        if not predicted or not actual:
            return {"speed_mae": 0}

        pred = np.array(predicted)
        act = np.array(actual)
        n = min(len(pred), len(act))
        pred, act = pred[:n], act[:n]

        errors = np.abs(pred - act)
        return {
            "speed_mae_kmph": round(float(np.mean(errors)), 2),
            "speed_rmse_kmph": round(float(np.sqrt(np.mean(errors ** 2))), 2),
            "n_samples": n,
        }

    def evaluate_lane_assignment(
        self,
        predicted_lanes: list[str],
        actual_lanes: list[str],
    ) -> dict:
        """Evaluate lane assignment accuracy."""
        if not predicted_lanes or not actual_lanes:
            return {"lane_accuracy": 0}

        n = min(len(predicted_lanes), len(actual_lanes))
        correct = sum(
            1 for p, a in zip(predicted_lanes[:n], actual_lanes[:n]) if p == a
        )

        return {
            "lane_accuracy": round(correct / n if n > 0 else 0, 4),
            "correct_assignments": correct,
            "total_assignments": n,
        }

    def full_evaluation(
        self,
        counts_pred: list[int], counts_actual: list[int],
        queue_pred: list[float], queue_actual: list[float],
        speed_pred: list[float], speed_actual: list[float],
        lanes_pred: list[str], lanes_actual: list[str],
    ) -> dict:
        """Run full traffic state evaluation."""
        result = {}
        result.update(self.evaluate_counts(counts_pred, counts_actual))
        result.update(self.evaluate_queue(queue_pred, queue_actual))
        result.update(self.evaluate_speed(speed_pred, speed_actual))
        result.update(self.evaluate_lane_assignment(lanes_pred, lanes_actual))
        return result
