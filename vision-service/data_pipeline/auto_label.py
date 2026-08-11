"""
data_pipeline/auto_label.py — SAM 3.1 Auto-Labeling Pipeline
==============================================================
ERH26_PS_08: Data-Driven Traffic Optimization

Uses Meta SAM 3.1 (Segment Anything Model 3.1) with text-prompted
concept segmentation to auto-label the raw Surat CCTV footage.

This is the CORE of our data advantage: turning the given footage into
an actual training dataset with Indian-traffic-specific classes that
COCO doesn't have (auto_rickshaw, BRTS bus, etc.). Most competing teams
will skip this step and run stock pretrained weights — this is how we
differentiate.

The auto-labels are a DRAFT — they will be imperfect. The workflow is:
1. auto_label.py (this file) → generates draft YOLO-format labels
2. review_helpers.py → samples frames for human correction
3. Correct in Roboflow/CVAT → produces clean labels
4. finetune.py → trains YOLO26 on corrected labels

PORTABILITY NOTE: This script may need to run on a cloud GPU (Colab/Kaggle)
if SAM 3.1 exceeds local 8GB VRAM. All paths are relative and configurable
— no hardcoded local-only paths.

Usage:
    python -m data_pipeline.auto_label --video_dir sample_videos/raw --output_dir data_pipeline/labels_draft
    
    # On Colab:
    # Upload videos to /content/videos/, run with --video_dir /content/videos/
"""

import argparse
import json
import logging
import os
import sys
from pathlib import Path
from typing import Optional

import cv2
import numpy as np

logger = logging.getLogger(__name__)

# ─── Configuration ───────────────────────────────────────────────────

# Text prompts for SAM 3.1 concept segmentation.
# Each prompt targets one of our custom vehicle classes.
# SAM 3.1 uses short noun phrases as prompts.
TEXT_PROMPTS: dict[str, list[str]] = {
    "car": ["car", "sedan", "hatchback", "SUV"],
    "bus": ["bus", "city bus", "public bus"],
    "brts_bus": ["BRTS bus", "red bus"],  # Adjust color if BRTS buses have distinct paint
    "truck": ["truck", "lorry", "heavy vehicle"],
    "two_wheeler": ["motorcycle", "scooter", "two-wheeler", "motorbike"],
    "auto_rickshaw": ["auto rickshaw", "three-wheeler", "tuk-tuk", "auto"],
    "cycle": ["bicycle", "cycle"],
}

# Our target class list (order defines class ID in YOLO format)
CLASS_NAMES: list[str] = [
    "car",          # 0
    "bus",          # 1
    "brts_bus",     # 2
    "truck",        # 3
    "two_wheeler",  # 4
    "auto_rickshaw",# 5
    "cycle",        # 6
]

CLASS_TO_ID: dict[str, int] = {name: idx for idx, name in enumerate(CLASS_NAMES)}


# ─── Frame Extraction ───────────────────────────────────────────────

def extract_frames(
    video_path: str,
    output_dir: str,
    every_n_frames: int = 30,
    max_frames: Optional[int] = None,
) -> list[str]:
    """Extract frames from a video at regular intervals.

    Args:
        video_path: Path to the video file.
        output_dir: Directory to save extracted frames.
        every_n_frames: Extract every Nth frame (e.g., 30 = ~1 per second at 30fps).
        max_frames: Maximum number of frames to extract (None = no limit).

    Returns:
        List of paths to extracted frame images.
    """
    os.makedirs(output_dir, exist_ok=True)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        logger.error(f"Cannot open video: {video_path}")
        return []

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    video_name = Path(video_path).stem

    # Sanitize video name for filesystem (remove special chars)
    safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in video_name)[:50]

    logger.info(
        f"Extracting frames from {video_name} — "
        f"{total_frames} total frames, {fps:.1f} FPS, "
        f"sampling every {every_n_frames} frames"
    )

    frame_paths: list[str] = []
    frame_idx = 0
    extracted = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_idx % every_n_frames == 0:
            frame_filename = f"{safe_name}_frame{frame_idx:06d}.jpg"
            frame_path = os.path.join(output_dir, frame_filename)
            cv2.imwrite(frame_path, frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
            frame_paths.append(frame_path)
            extracted += 1

            if max_frames and extracted >= max_frames:
                break

        frame_idx += 1

    cap.release()
    logger.info(f"Extracted {extracted} frames from {video_name}")
    return frame_paths


# ─── SAM 3.1 Auto-Labeling ──────────────────────────────────────────

def auto_label_with_sam3(
    frame_paths: list[str],
    output_dir: str,
    model_checkpoint: str = "facebook/sam3.1",
    device: str = "cuda",
    batch_size: int = 1,
) -> None:
    """Run SAM 3.1 text-prompted concept segmentation on extracted frames.

    For each frame, runs SAM 3.1 with each text prompt to detect and
    segment instances of each vehicle class. Exports bounding boxes
    in YOLO format (one .txt per image).

    SAM 3.1's Object Multiplexing allows processing multiple concepts
    in a single forward pass (up to 16 objects), which we leverage
    by batching our 7 classes together.

    Args:
        frame_paths: Paths to frame images to label.
        output_dir: Directory to save YOLO-format label files.
        model_checkpoint: SAM 3.1 model identifier (HuggingFace or local path).
        device: "cuda" or "cpu".
        batch_size: Frames per batch (keep at 1 for VRAM-constrained setups).

    Output format (YOLO):
        Each .txt file contains one line per detected object:
        class_id center_x center_y width height
        (all values normalized to [0, 1] relative to image dimensions)
    """
    os.makedirs(output_dir, exist_ok=True)

    try:
        # Import SAM 3.1 — this will fail if not installed
        # On Colab: !pip install sam3
        from sam3.build_sam import build_sam3_pcs
        from sam3.predictor import Sam3Predictor
    except ImportError:
        logger.error(
            "SAM 3.1 (sam3) not installed.\n"
            "Install with: pip install sam3\n"
            "Or clone: git clone https://github.com/facebookresearch/sam3\n"
            "If running locally and VRAM is tight, run this script on Colab/Kaggle:\n"
            "  1. Upload extracted frames to cloud\n"
            "  2. Run auto_label.py there\n"
            "  3. Download the generated label .txt files back to data_pipeline/labels_draft/\n"
            "\n"
            "--- FALLBACK: Generating placeholder labels for pipeline testing ---"
        )
        _generate_placeholder_labels(frame_paths, output_dir)
        return

    logger.info(f"Loading SAM 3.1 model: {model_checkpoint}")

    try:
        model = build_sam3_pcs(checkpoint=model_checkpoint)
        predictor = Sam3Predictor(model)
        predictor.to(device)
    except Exception as e:
        logger.error(f"Failed to load SAM 3.1: {e}")
        logger.info("Falling back to placeholder labels")
        _generate_placeholder_labels(frame_paths, output_dir)
        return

    logger.info(f"Processing {len(frame_paths)} frames with SAM 3.1...")

    for i, frame_path in enumerate(frame_paths):
        try:
            image = cv2.imread(frame_path)
            if image is None:
                logger.warning(f"Cannot read image: {frame_path}")
                continue

            h, w = image.shape[:2]
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            # Set the image in SAM 3.1
            predictor.set_image(image_rgb)

            all_detections: list[str] = []

            # Process each vehicle class with its text prompts
            for class_name, prompts in TEXT_PROMPTS.items():
                class_id = CLASS_TO_ID[class_name]

                for prompt in prompts:
                    try:
                        # SAM 3.1 text-prompted concept segmentation
                        masks, boxes, scores = predictor.predict_text(
                            text_prompt=prompt,
                            multimask_output=False,
                        )

                        if boxes is None or len(boxes) == 0:
                            continue

                        # Convert boxes to YOLO format and add to detections
                        for box_idx in range(len(boxes)):
                            score = float(scores[box_idx]) if scores is not None else 0.5
                            if score < 0.3:  # Min confidence for auto-labels
                                continue

                            box = boxes[box_idx]  # [x1, y1, x2, y2]
                            # Convert to YOLO format: center_x, center_y, width, height (normalized)
                            cx = ((box[0] + box[2]) / 2.0) / w
                            cy = ((box[1] + box[3]) / 2.0) / h
                            bw = (box[2] - box[0]) / w
                            bh = (box[3] - box[1]) / h

                            line = f"{class_id} {cx:.6f} {cy:.6f} {bw:.6f} {bh:.6f}"
                            all_detections.append(line)

                    except Exception as e:
                        logger.debug(f"Prompt '{prompt}' failed on {frame_path}: {e}")
                        continue

            # Deduplicate overlapping detections (simple IoU-based NMS)
            all_detections = _deduplicate_labels(all_detections, iou_thresh=0.5)

            # Write YOLO label file
            label_filename = Path(frame_path).stem + ".txt"
            label_path = os.path.join(output_dir, label_filename)

            with open(label_path, "w", encoding="utf-8") as f:
                f.write("\n".join(all_detections))

            if (i + 1) % 50 == 0:
                logger.info(f"Processed {i + 1}/{len(frame_paths)} frames")

        except Exception as e:
            logger.warning(f"Error processing {frame_path}: {e}")
            continue

    logger.info(f"Auto-labeling complete — labels saved to {output_dir}")


def _deduplicate_labels(
    labels: list[str],
    iou_thresh: float = 0.5,
) -> list[str]:
    """Remove duplicate/overlapping detections using IoU-based NMS.

    When multiple text prompts detect the same physical object
    (e.g., "car" and "sedan" both find the same vehicle), keep only
    the first detection and suppress overlapping ones.

    Args:
        labels: List of YOLO-format label strings.
        iou_thresh: IoU threshold above which detections are considered duplicates.

    Returns:
        Deduplicated list of label strings.
    """
    if len(labels) <= 1:
        return labels

    # Parse labels into boxes
    parsed = []
    for label in labels:
        parts = label.split()
        class_id = int(parts[0])
        cx, cy, w, h = float(parts[1]), float(parts[2]), float(parts[3]), float(parts[4])
        # Convert to x1, y1, x2, y2
        x1 = cx - w / 2
        y1 = cy - h / 2
        x2 = cx + w / 2
        y2 = cy + h / 2
        parsed.append((class_id, x1, y1, x2, y2, label))

    # Simple greedy NMS
    keep: list[str] = []
    used = [False] * len(parsed)

    for i in range(len(parsed)):
        if used[i]:
            continue
        keep.append(parsed[i][-1])
        used[i] = True

        for j in range(i + 1, len(parsed)):
            if used[j]:
                continue
            iou = _compute_iou(parsed[i][1:5], parsed[j][1:5])
            if iou > iou_thresh:
                used[j] = True

    return keep


def _compute_iou(
    box_a: tuple[float, float, float, float],
    box_b: tuple[float, float, float, float],
) -> float:
    """Compute IoU between two boxes (x1, y1, x2, y2 format, normalized)."""
    x1 = max(box_a[0], box_b[0])
    y1 = max(box_a[1], box_b[1])
    x2 = min(box_a[2], box_b[2])
    y2 = min(box_a[3], box_b[3])

    intersection = max(0, x2 - x1) * max(0, y2 - y1)
    area_a = (box_a[2] - box_a[0]) * (box_a[3] - box_a[1])
    area_b = (box_b[2] - box_b[0]) * (box_b[3] - box_b[1])
    union = area_a + area_b - intersection

    return intersection / union if union > 0 else 0.0


def _generate_placeholder_labels(
    frame_paths: list[str],
    output_dir: str,
) -> None:
    """Generate empty placeholder label files for pipeline testing.

    Used when SAM 3.1 is not available locally. The actual auto-labeling
    should be run on a cloud GPU and the results downloaded.
    """
    os.makedirs(output_dir, exist_ok=True)

    for frame_path in frame_paths:
        label_filename = Path(frame_path).stem + ".txt"
        label_path = os.path.join(output_dir, label_filename)
        # Create empty label file (no detections)
        with open(label_path, "w", encoding="utf-8") as f:
            pass  # Empty file

    logger.info(
        f"Created {len(frame_paths)} PLACEHOLDER label files in {output_dir}. "
        f"These are EMPTY — run auto_label.py with SAM 3.1 on a cloud GPU "
        f"to generate real labels."
    )


# ─── CLI ─────────────────────────────────────────────────────────────

def main() -> None:
    """CLI entry point for auto-labeling."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")

    parser = argparse.ArgumentParser(description="SAM 3.1 Auto-Labeling Pipeline")
    parser.add_argument(
        "--video_dir", default="sample_videos/raw",
        help="Directory containing video files to label",
    )
    parser.add_argument(
        "--output_dir", default="data_pipeline/labels_draft",
        help="Directory to save extracted frames and draft labels",
    )
    parser.add_argument(
        "--frames_dir", default=None,
        help="Directory for extracted frames (default: output_dir/frames)",
    )
    parser.add_argument(
        "--every_n", type=int, default=30,
        help="Extract every Nth frame from each video (default: 30)",
    )
    parser.add_argument(
        "--max_frames_per_video", type=int, default=200,
        help="Max frames to extract per video (default: 200)",
    )
    parser.add_argument(
        "--device", default="cuda",
        help="Device for SAM 3.1 inference ('cuda' or 'cpu')",
    )
    parser.add_argument(
        "--model", default="facebook/sam3.1",
        help="SAM 3.1 model checkpoint (HuggingFace ID or local path)",
    )

    args = parser.parse_args()

    frames_dir = args.frames_dir or os.path.join(args.output_dir, "frames")
    labels_dir = os.path.join(args.output_dir, "labels")

    # Step 1: Extract frames from all videos
    video_dir = Path(args.video_dir)
    if not video_dir.exists():
        logger.error(f"Video directory not found: {video_dir}")
        sys.exit(1)

    video_extensions = {".avi", ".mp4", ".mkv", ".mov"}
    video_files = [
        f for f in video_dir.iterdir()
        if f.suffix.lower() in video_extensions
    ]

    if not video_files:
        logger.error(f"No video files found in {video_dir}")
        sys.exit(1)

    logger.info(f"Found {len(video_files)} videos in {video_dir}")

    all_frame_paths: list[str] = []
    for video_file in sorted(video_files):
        frame_paths = extract_frames(
            str(video_file),
            frames_dir,
            every_n_frames=args.every_n,
            max_frames=args.max_frames_per_video,
        )
        all_frame_paths.extend(frame_paths)

    logger.info(f"Total extracted frames: {len(all_frame_paths)}")

    # Step 2: Run SAM 3.1 auto-labeling
    auto_label_with_sam3(
        all_frame_paths,
        labels_dir,
        model_checkpoint=args.model,
        device=args.device,
    )

    # Step 3: Generate classes.txt for reference
    classes_path = os.path.join(args.output_dir, "classes.txt")
    with open(classes_path, "w", encoding="utf-8") as f:
        for name in CLASS_NAMES:
            f.write(name + "\n")

    logger.info(f"Class list saved to {classes_path}")
    logger.info(
        f"\nNext steps:\n"
        f"  1. Review labels with: python -m data_pipeline.review_helpers\n"
        f"  2. Correct in Roboflow/CVAT\n"
        f"  3. Fine-tune with: python -m data_pipeline.finetune"
    )


if __name__ == "__main__":
    main()
