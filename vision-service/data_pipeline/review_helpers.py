"""
data_pipeline/review_helpers.py — Frame Sampling & Label Review Utilities
==========================================================================
ERH26_PS_08: Data-Driven Traffic Optimization

Utilities for preparing auto-labeled frames for human review and correction.
Targets Roboflow as the review platform (free tier, web-based, YOLO export).

Key operations:
1. Stratified sampling: ~300-500 frames across all clips, balanced across
   lighting conditions and junctions
2. Visual spot-check grid: shows auto-labels overlaid on sample frames
3. Export to Roboflow-importable format (images + YOLO labels in directory structure)

Usage:
    python -m data_pipeline.review_helpers --draft_dir data_pipeline/labels_draft --output_dir data_pipeline/review_export
"""

import argparse
import logging
import os
import random
import sys
from pathlib import Path
from typing import Optional

import cv2
import numpy as np

logger = logging.getLogger(__name__)

# Class names (must match auto_label.py order)
CLASS_NAMES: list[str] = [
    "car", "bus", "brts_bus", "truck", "two_wheeler", "auto_rickshaw", "cycle"
]

# Colors for visualization (BGR format)
CLASS_COLORS: dict[str, tuple[int, int, int]] = {
    "car":           (255, 100, 0),     # Blue-ish
    "bus":           (0, 200, 0),       # Green
    "brts_bus":      (0, 0, 255),       # Red
    "truck":         (200, 200, 0),     # Cyan-ish
    "two_wheeler":   (255, 0, 255),     # Magenta
    "auto_rickshaw": (0, 255, 255),     # Yellow
    "cycle":         (128, 128, 255),   # Light red
}


def stratified_sample(
    frames_dir: str,
    n_samples: int = 400,
    seed: int = 42,
) -> list[str]:
    """Sample frames with stratification across video sources.

    Ensures we get a balanced spread of frames across all 5 videos
    (different junctions, different lighting conditions).

    Args:
        frames_dir: Directory containing extracted frame images.
        n_samples: Target number of frames to sample.
        seed: Random seed for reproducibility.

    Returns:
        List of selected frame paths.
    """
    random.seed(seed)

    all_frames = sorted([
        os.path.join(frames_dir, f)
        for f in os.listdir(frames_dir)
        if f.lower().endswith((".jpg", ".png", ".jpeg"))
    ])

    if not all_frames:
        logger.error(f"No frames found in {frames_dir}")
        return []

    # Group frames by video source (based on filename prefix)
    groups: dict[str, list[str]] = {}
    for frame_path in all_frames:
        # Extract video source prefix (before "_frame")
        basename = Path(frame_path).stem
        prefix = basename.rsplit("_frame", 1)[0] if "_frame" in basename else "unknown"
        if prefix not in groups:
            groups[prefix] = []
        groups[prefix].append(frame_path)

    logger.info(
        f"Found {len(all_frames)} total frames across {len(groups)} video sources"
    )

    # Sample proportionally from each group
    samples_per_group = max(1, n_samples // len(groups))
    selected: list[str] = []

    for prefix, frames in groups.items():
        n = min(samples_per_group, len(frames))
        # Use evenly-spaced sampling (not purely random) to cover time spread
        indices = np.linspace(0, len(frames) - 1, n, dtype=int)
        selected.extend(frames[i] for i in indices)

    # If we're short of the target, add random extras
    remaining = [f for f in all_frames if f not in set(selected)]
    if len(selected) < n_samples and remaining:
        extra = min(n_samples - len(selected), len(remaining))
        selected.extend(random.sample(remaining, extra))

    logger.info(
        f"Sampled {len(selected)} frames "
        f"({', '.join(f'{k}: {min(samples_per_group, len(v))}' for k, v in groups.items())})"
    )

    return selected


def visualize_labels(
    frame_path: str,
    label_path: str,
    output_path: Optional[str] = None,
) -> np.ndarray:
    """Draw auto-label bounding boxes on a frame for visual inspection.

    Args:
        frame_path: Path to the frame image.
        label_path: Path to the YOLO-format label file.
        output_path: If provided, save annotated frame here.

    Returns:
        Annotated frame as numpy array (BGR).
    """
    frame = cv2.imread(frame_path)
    if frame is None:
        logger.warning(f"Cannot read frame: {frame_path}")
        return np.zeros((100, 100, 3), dtype=np.uint8)

    h, w = frame.shape[:2]

    if not os.path.exists(label_path):
        # No labels for this frame
        cv2.putText(frame, "NO LABELS", (10, 30),
                     cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        return frame

    with open(label_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line in lines:
        parts = line.strip().split()
        if len(parts) < 5:
            continue

        class_id = int(parts[0])
        cx, cy, bw, bh = float(parts[1]), float(parts[2]), float(parts[3]), float(parts[4])

        # Convert YOLO format to pixel coordinates
        x1 = int((cx - bw / 2) * w)
        y1 = int((cy - bh / 2) * h)
        x2 = int((cx + bw / 2) * w)
        y2 = int((cy + bh / 2) * h)

        class_name = CLASS_NAMES[class_id] if class_id < len(CLASS_NAMES) else f"cls_{class_id}"
        color = CLASS_COLORS.get(class_name, (200, 200, 200))

        # Draw box
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

        # Draw label background + text
        label_text = class_name
        (tw, th), _ = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        cv2.rectangle(frame, (x1, y1 - th - 6), (x1 + tw, y1), color, -1)
        cv2.putText(frame, label_text, (x1, y1 - 4),
                     cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    if output_path:
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        cv2.imwrite(output_path, frame)

    return frame


def create_spot_check_grid(
    frames_dir: str,
    labels_dir: str,
    output_path: str = "data_pipeline/spot_check_grid.jpg",
    grid_size: tuple[int, int] = (4, 4),
    cell_size: tuple[int, int] = (400, 300),
    seed: int = 42,
) -> None:
    """Create a grid of annotated frames for quick visual quality check.

    Generates a single large image showing a grid of randomly sampled
    frames with auto-labels overlaid. This lets you quickly assess
    labeling quality before uploading to Roboflow.

    Args:
        frames_dir: Directory with extracted frames.
        labels_dir: Directory with YOLO-format label files.
        output_path: Where to save the grid image.
        grid_size: (rows, cols) of the grid.
        cell_size: (width, height) of each cell in pixels.
        seed: Random seed.
    """
    random.seed(seed)

    frame_files = sorted([
        f for f in os.listdir(frames_dir)
        if f.lower().endswith((".jpg", ".png", ".jpeg"))
    ])

    n_cells = grid_size[0] * grid_size[1]
    selected = random.sample(frame_files, min(n_cells, len(frame_files)))

    grid_w = grid_size[1] * cell_size[0]
    grid_h = grid_size[0] * cell_size[1]
    grid = np.zeros((grid_h, grid_w, 3), dtype=np.uint8)

    for idx, frame_file in enumerate(selected):
        row = idx // grid_size[1]
        col = idx % grid_size[1]

        frame_path = os.path.join(frames_dir, frame_file)
        label_file = Path(frame_file).stem + ".txt"
        label_path = os.path.join(labels_dir, label_file)

        annotated = visualize_labels(frame_path, label_path)
        resized = cv2.resize(annotated, cell_size)

        y_start = row * cell_size[1]
        x_start = col * cell_size[0]
        grid[y_start:y_start + cell_size[1], x_start:x_start + cell_size[0]] = resized

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    cv2.imwrite(output_path, grid, [cv2.IMWRITE_JPEG_QUALITY, 90])
    logger.info(f"Spot-check grid saved to {output_path} ({grid_size[0]}×{grid_size[1]} cells)")


def export_for_roboflow(
    sampled_frames: list[str],
    labels_dir: str,
    output_dir: str,
) -> None:
    """Export sampled frames + labels in Roboflow-importable format.

    Roboflow accepts a directory upload with:
    - Images: *.jpg files
    - Labels: matching *.txt files in YOLO format
    - classes.txt or data.yaml with class names

    After upload, you can correct annotations in Roboflow's web editor
    and re-export in YOLO format for fine-tuning.

    Args:
        sampled_frames: List of frame image paths to include.
        labels_dir: Directory containing draft YOLO labels.
        output_dir: Directory for the Roboflow-importable export.
    """
    images_dir = os.path.join(output_dir, "images")
    exported_labels_dir = os.path.join(output_dir, "labels")
    os.makedirs(images_dir, exist_ok=True)
    os.makedirs(exported_labels_dir, exist_ok=True)

    exported_count = 0
    missing_labels = 0

    for frame_path in sampled_frames:
        frame_name = Path(frame_path).name
        label_name = Path(frame_path).stem + ".txt"
        label_path = os.path.join(labels_dir, label_name)

        # Copy image
        import shutil
        dst_image = os.path.join(images_dir, frame_name)
        shutil.copy2(frame_path, dst_image)

        # Copy label (or create empty)
        dst_label = os.path.join(exported_labels_dir, label_name)
        if os.path.exists(label_path):
            shutil.copy2(label_path, dst_label)
        else:
            with open(dst_label, "w") as f:
                pass
            missing_labels += 1

        exported_count += 1

    # Write data.yaml (Roboflow/YOLO standard)
    data_yaml_content = {
        "names": CLASS_NAMES,
        "nc": len(CLASS_NAMES),
        "train": os.path.join(output_dir, "images"),
        "val": os.path.join(output_dir, "images"),
    }

    import yaml
    data_yaml_path = os.path.join(output_dir, "data.yaml")
    with open(data_yaml_path, "w", encoding="utf-8") as f:
        yaml.dump(data_yaml_content, f, default_flow_style=False)

    # Write classes.txt
    classes_path = os.path.join(output_dir, "classes.txt")
    with open(classes_path, "w", encoding="utf-8") as f:
        for name in CLASS_NAMES:
            f.write(name + "\n")

    logger.info(
        f"Exported {exported_count} frames to {output_dir} for Roboflow review "
        f"({missing_labels} frames had no labels)"
    )
    logger.info(
        f"\nNext steps:\n"
        f"  1. Upload the '{output_dir}' folder to Roboflow\n"
        f"  2. Review and correct annotations in Roboflow's web editor\n"
        f"  3. Export corrected dataset in 'YOLO v5 PyTorch' format\n"
        f"  4. Download and place in data_pipeline/labels_corrected/\n"
        f"  5. Run: python -m data_pipeline.finetune"
    )


# ─── CLI ─────────────────────────────────────────────────────────────

def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")

    parser = argparse.ArgumentParser(description="Label Review & Export Helpers")
    parser.add_argument(
        "--draft_dir", default="data_pipeline/labels_draft",
        help="Directory with draft auto-labels",
    )
    parser.add_argument(
        "--output_dir", default="data_pipeline/review_export",
        help="Directory for Roboflow export",
    )
    parser.add_argument(
        "--n_samples", type=int, default=400,
        help="Number of frames to sample for review (default: 400)",
    )
    parser.add_argument(
        "--spot_check", action="store_true",
        help="Generate spot-check visualization grid",
    )

    args = parser.parse_args()

    frames_dir = os.path.join(args.draft_dir, "frames")
    labels_dir = os.path.join(args.draft_dir, "labels")

    if not os.path.exists(frames_dir):
        logger.error(
            f"Frames directory not found: {frames_dir}\n"
            f"Run auto_label.py first: python -m data_pipeline.auto_label"
        )
        sys.exit(1)

    # Sample frames
    sampled = stratified_sample(frames_dir, n_samples=args.n_samples)

    # Generate spot-check grid
    if args.spot_check:
        create_spot_check_grid(frames_dir, labels_dir)

    # Export for Roboflow
    export_for_roboflow(sampled, labels_dir, args.output_dir)


if __name__ == "__main__":
    main()
