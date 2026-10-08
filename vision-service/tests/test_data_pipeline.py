"""
test_data_pipeline.py — Tests for Data Pipeline & Active Learning (Sprint 9, Sections 4-10)
"""

import json
import tempfile
import unittest
from pathlib import Path
from data_pipeline.active_learning import ActiveLearningSelector
from data_pipeline.dataset_split import DatasetSplitter


class TestDataPipeline(unittest.TestCase):

    def test_active_learning_scoring(self):
        selector = ActiveLearningSelector()
        vehicles = [
            {"detection_confidence": 0.35, "class_stability": 0.4, "track_quality": 0.5, "occlusion_ratio": 0.3},
            {"detection_confidence": 0.85, "class_stability": 0.9, "track_quality": 0.9, "occlusion_ratio": 0.0},
        ]
        score = selector.score_frame(frame_index=1, vehicles=vehicles)
        self.assertGreater(score, 0.0)
        self.assertLessEqual(score, 1.0)

    def test_dataset_split(self):
        splitter = DatasetSplitter(seed=42)
        with tempfile.TemporaryDirectory() as tmpdir:
            meta_path = Path(tmpdir) / "meta.jsonl"
            with open(meta_path, "w") as f:
                for i in range(10):
                    f.write(json.dumps({"frame": f"frame_{i}.jpg", "camera_id": f"cam_{i}"}) + "\n")

            out_dir = Path(tmpdir) / "splits"
            stats = splitter.split_by_video(str(meta_path), str(out_dir), train_ratio=0.7, val_ratio=0.2, test_ratio=0.1)
            self.assertIn("train", stats)
            self.assertIn("val", stats)
            self.assertIn("test", stats)
            self.assertEqual(stats["train"] + stats["val"] + stats["test"], 10)


if __name__ == "__main__":
    unittest.main()
