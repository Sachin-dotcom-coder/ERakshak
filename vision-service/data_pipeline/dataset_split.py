"""
data_pipeline/dataset_split.py — Video-Aware Dataset Splitting (Section 7)
============================================================================
Splits datasets by camera/junction (not adjacent frames) to prevent
data leakage between train/val/test sets.
"""

import logging
import json
import random
import shutil
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class DatasetSplitter:
    """Video-aware dataset splitting to prevent data leakage.

    Splits by camera or junction rather than randomly splitting adjacent
    video frames, which would create highly similar train/val images.

    Args:
        seed: Random seed for reproducibility.
    """

    def __init__(self, seed: int = 42) -> None:
        self._seed = seed

    def split_by_video(
        self,
        metadata_path: str,
        output_dir: str,
        train_ratio: float = 0.70,
        val_ratio: float = 0.15,
        test_ratio: float = 0.15,
    ) -> dict:
        """Split dataset by video source to prevent leakage.

        Args:
            metadata_path: Path to metadata JSONL file.
            output_dir: Output directory for split files.
            train_ratio: Fraction for training.
            val_ratio: Fraction for validation.
            test_ratio: Fraction for testing.

        Returns:
            Dict with split statistics.
        """
        # Load metadata
        entries = []
        with open(metadata_path, "r") as f:
            for line in f:
                if line.strip():
                    entries.append(json.loads(line))

        if not entries:
            logger.warning("No entries found in metadata file")
            return {"train": 0, "val": 0, "test": 0}

        # Group by video source / camera
        groups: dict[str, list[dict]] = {}
        for entry in entries:
            key = entry.get("camera_id", entry.get("video_source", "unknown"))
            if key not in groups:
                groups[key] = []
            groups[key].append(entry)

        # Split groups into train/val/test
        group_keys = list(groups.keys())
        random.seed(self._seed)
        random.shuffle(group_keys)

        n = len(group_keys)
        n_train = max(1, int(n * train_ratio))
        n_val = max(1, int(n * val_ratio))

        train_keys = group_keys[:n_train]
        val_keys = group_keys[n_train:n_train + n_val]
        test_keys = group_keys[n_train + n_val:]

        # If only 1-2 groups, fall back to temporal split within groups
        if n <= 2:
            logger.warning(
                f"Only {n} video sources — using temporal split within videos"
            )
            return self._temporal_split(
                entries, output_dir, train_ratio, val_ratio
            )

        # Write split files
        out = Path(output_dir)
        stats = {}
        for split_name, keys in [
            ("train", train_keys),
            ("val", val_keys),
            ("test", test_keys),
        ]:
            split_dir = out / split_name
            split_dir.mkdir(parents=True, exist_ok=True)
            split_entries = []
            for key in keys:
                split_entries.extend(groups[key])

            # Write metadata
            with open(str(split_dir / "metadata.jsonl"), "w") as f:
                for entry in split_entries:
                    f.write(json.dumps(entry) + "\n")

            stats[split_name] = len(split_entries)
            logger.info(
                f"Split '{split_name}': {len(split_entries)} frames "
                f"from {len(keys)} videos"
            )

        return stats

    def _temporal_split(
        self,
        entries: list[dict],
        output_dir: str,
        train_ratio: float,
        val_ratio: float,
    ) -> dict:
        """Fallback: temporal split with buffer between splits."""
        n = len(entries)
        # Sort by frame index
        entries.sort(key=lambda e: e.get("frame_index", 0))

        n_train = int(n * train_ratio)
        n_val = int(n * val_ratio)
        buffer = max(10, int(n * 0.02))  # 2% buffer between splits

        train = entries[:n_train]
        val = entries[n_train + buffer:n_train + buffer + n_val]
        test = entries[n_train + buffer + n_val + buffer:]

        out = Path(output_dir)
        stats = {}
        for name, data in [("train", train), ("val", val), ("test", test)]:
            split_dir = out / name
            split_dir.mkdir(parents=True, exist_ok=True)
            with open(str(split_dir / "metadata.jsonl"), "w") as f:
                for entry in data:
                    f.write(json.dumps(entry) + "\n")
            stats[name] = len(data)

        return stats
