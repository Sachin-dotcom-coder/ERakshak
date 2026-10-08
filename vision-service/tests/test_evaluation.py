"""
test_evaluation.py — Tests for Perception & Tracking Evaluation Metrics (Sprint 9, Sections 74-80)
"""

import unittest
import numpy as np
from evaluation.detection_metrics import DetectionEvaluator
from evaluation.tracking_metrics import TrackingEvaluator
from evaluation.traffic_metrics import TrafficStateEvaluator
from evaluation.event_metrics import EventEvaluator, LatencyBenchmark, AblationStudy


class TestEvaluation(unittest.TestCase):

    def test_detection_metrics(self):
        evaluator = DetectionEvaluator(iou_thresholds=[0.5])
        preds = [{"bbox": [10, 10, 50, 50], "class": "car", "confidence": 0.9}]
        targets = [{"bbox": [12, 12, 48, 48], "class": "car"}]
        res = evaluator.evaluate(preds, targets)
        self.assertIn("precision", res)
        self.assertIn("recall", res)
        self.assertGreater(res["recall"], 0.9)

    def test_traffic_metrics(self):
        evaluator = TrafficStateEvaluator()
        res = evaluator.evaluate_counts(predicted=[10, 15], actual=[12, 15])
        self.assertIn("count_mae", res)
        self.assertEqual(res["count_mae"], 1.0)

    def test_latency_benchmark(self):
        benchmark = LatencyBenchmark()
        t0 = benchmark.start()
        benchmark.record("detector", t0)
        summary = benchmark.report()
        self.assertIn("detector", summary)
        self.assertIn("mean_ms", summary["detector"])


if __name__ == "__main__":
    unittest.main()
