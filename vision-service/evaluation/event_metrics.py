"""
evaluation/event_metrics.py — Event Evaluation & Benchmarking (Sections 77-80)
================================================================================
BRTS, emergency, breakdown precision/recall/F1, false-alert rate,
detection latency, and latency benchmarking.
"""

import logging
import time
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)


class EventEvaluator:
    """Evaluate event detection quality (BRTS, emergency, breakdown)."""

    def evaluate_events(
        self,
        predicted_events: list[dict],
        ground_truth_events: list[dict],
        event_type: str,
        time_tolerance_sec: float = 5.0,
    ) -> dict:
        """Evaluate event detection against ground truth.

        Args:
            predicted_events: Predicted events with 'timestamp' and 'track_id'.
            ground_truth_events: Ground truth events.
            event_type: Event type label (for reporting).
            time_tolerance_sec: Time window for matching events.

        Returns:
            Dict with precision, recall, F1, false alert rate.
        """
        matched_gt = set()
        tp = 0

        for pred in predicted_events:
            for i, gt in enumerate(ground_truth_events):
                if i in matched_gt:
                    continue
                # Match by time proximity
                pred_time = pred.get("timestamp", 0)
                gt_time = gt.get("timestamp", 0)
                if abs(pred_time - gt_time) <= time_tolerance_sec:
                    tp += 1
                    matched_gt.add(i)
                    break

        fp = len(predicted_events) - tp
        fn = len(ground_truth_events) - len(matched_gt)

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

        return {
            f"{event_type}_precision": round(precision, 4),
            f"{event_type}_recall": round(recall, 4),
            f"{event_type}_f1": round(f1, 4),
            f"{event_type}_true_positives": tp,
            f"{event_type}_false_positives": fp,
            f"{event_type}_false_negatives": fn,
        }


class LatencyBenchmark:
    """Pipeline stage latency benchmarking (Section 78).

    Measures execution time of each pipeline stage.
    """

    def __init__(self) -> None:
        self._timings: dict[str, list[float]] = {}

    def start(self) -> float:
        """Start a timing measurement."""
        return time.perf_counter()

    def record(self, stage: str, start_time: float) -> float:
        """Record timing for a pipeline stage.

        Args:
            stage: Stage name.
            start_time: Start time from self.start().

        Returns:
            Elapsed time in milliseconds.
        """
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        if stage not in self._timings:
            self._timings[stage] = []
        self._timings[stage].append(elapsed_ms)
        return elapsed_ms

    def report(self) -> dict:
        """Generate latency report across all stages."""
        report = {}
        total_mean = 0.0

        for stage, times in self._timings.items():
            arr = np.array(times)
            mean_ms = float(np.mean(arr))
            total_mean += mean_ms
            report[stage] = {
                "mean_ms": round(mean_ms, 2),
                "p50_ms": round(float(np.percentile(arr, 50)), 2),
                "p95_ms": round(float(np.percentile(arr, 95)), 2),
                "p99_ms": round(float(np.percentile(arr, 99)), 2),
                "max_ms": round(float(np.max(arr)), 2),
                "samples": len(times),
            }

        report["total_pipeline"] = {
            "mean_ms": round(total_mean, 2),
            "estimated_fps": round(1000 / total_mean if total_mean > 0 else 0, 1),
        }

        return report

    def reset(self) -> None:
        """Clear all timing data."""
        self._timings.clear()


class AblationStudy:
    """Ablation study framework (Section 79).

    Runs and compares different system configurations.
    """

    def __init__(self) -> None:
        self._results: dict[str, dict] = {}

    def record_configuration(self, name: str, metrics: dict) -> None:
        """Record metrics for a configuration.

        Args:
            name: Configuration name (e.g., "Baseline", "Baseline + Tiling").
            metrics: Dict of metric values.
        """
        self._results[name] = metrics
        logger.info(f"Ablation recorded: {name}")

    def generate_comparison(self) -> list[dict]:
        """Generate comparison table across configurations."""
        rows = []
        for name, metrics in self._results.items():
            row = {"configuration": name}
            row.update(metrics)
            rows.append(row)
        return rows
