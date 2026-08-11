"""
data_pipeline/finetune.py — YOLO26 Fine-Tuning on Surat Traffic Data
=====================================================================
ERH26_PS_08: Data-Driven Traffic Optimization

Fine-tunes YOLO26 (yolo26s.pt or yolo26n.pt) on our corrected Surat
traffic labels, optionally combined with a filtered subset of the IDD
(Indian Driving Dataset) for extra volume and class diversity.

This is the step that produces our CUSTOM model — the one with
auto_rickshaw, brts_bus, and all the Indian-traffic-specific classes
that stock COCO doesn't have. This is what we ship, not stock weights.

Hardware target: RTX 5060 Laptop, 8GB VRAM
- Conservative defaults: batch=8, imgsz=640
- Increase batch to 16 if VRAM allows (monitor with nvidia-smi)

Usage:
    python -m data_pipeline.finetune --data data_pipeline/labels_corrected
    python -m data_pipeline.finetune --data data_pipeline/labels_corrected --idd_supplement path/to/idd_filtered
"""

import argparse
import logging
import os
import sys
from pathlib import Path
from typing import Optional

import yaml

logger = logging.getLogger(__name__)

# Our 7 custom classes (order defines class ID)
CLASS_NAMES: list[str] = [
    "car",          # 0
    "bus",          # 1
    "brts_bus",     # 2
    "truck",        # 3
    "two_wheeler",  # 4
    "auto_rickshaw",# 5
    "cycle",        # 6
]


def prepare_dataset(
    corrected_dir: str,
    output_dir: str,
    idd_supplement_dir: Optional[str] = None,
    val_ratio: float = 0.1,
    test_ratio: float = 0.1,
    seed: int = 42,
) -> str:
    """Prepare the training dataset in Ultralytics YOLO format.

    Creates the directory structure and data.yaml that Ultralytics expects:
        dataset/
        ├── data.yaml
        ├── train/
        │   ├── images/
        │   └── labels/
        ├── val/
        │   ├── images/
        │   └── labels/
        └── test/
            ├── images/
            └── labels/

    Args:
        corrected_dir: Directory with corrected labels (from Roboflow export).
                       Expected to have images/ and labels/ subdirectories.
        output_dir: Where to create the training dataset.
        idd_supplement_dir: Optional directory with filtered IDD data
                           (same images/ + labels/ structure).
        val_ratio: Fraction of data for validation.
        test_ratio: Fraction of data for held-out testing.
        seed: Random seed for reproducible splits.

    Returns:
        Path to the generated data.yaml file.
    """
    import random
    import shutil

    random.seed(seed)

    # Locate images and labels
    images_dir = os.path.join(corrected_dir, "images")
    labels_dir = os.path.join(corrected_dir, "labels")

    if not os.path.exists(images_dir):
        logger.error(f"Images directory not found: {images_dir}")
        logger.error(
            "Expected Roboflow export structure:\n"
            f"  {corrected_dir}/\n"
            f"    images/\n"
            f"    labels/"
        )
        sys.exit(1)

    # Collect image-label pairs
    image_extensions = {".jpg", ".jpeg", ".png"}
    all_images = sorted([
        f for f in os.listdir(images_dir)
        if Path(f).suffix.lower() in image_extensions
    ])

    logger.info(f"Found {len(all_images)} images in {images_dir}")

    # Split into train/val/test
    random.shuffle(all_images)
    n_total = len(all_images)
    n_test = max(1, int(n_total * test_ratio))
    n_val = max(1, int(n_total * val_ratio))
    n_train = n_total - n_val - n_test

    splits = {
        "train": all_images[:n_train],
        "val": all_images[n_train:n_train + n_val],
        "test": all_images[n_train + n_val:],
    }

    logger.info(
        f"Split: train={n_train}, val={n_val}, test={n_test}"
    )

    # Create directory structure and copy files
    for split_name, split_images in splits.items():
        split_images_dir = os.path.join(output_dir, split_name, "images")
        split_labels_dir = os.path.join(output_dir, split_name, "labels")
        os.makedirs(split_images_dir, exist_ok=True)
        os.makedirs(split_labels_dir, exist_ok=True)

        for img_name in split_images:
            # Copy image
            src_img = os.path.join(images_dir, img_name)
            dst_img = os.path.join(split_images_dir, img_name)
            shutil.copy2(src_img, dst_img)

            # Copy corresponding label
            label_name = Path(img_name).stem + ".txt"
            src_label = os.path.join(labels_dir, label_name)
            dst_label = os.path.join(split_labels_dir, label_name)
            if os.path.exists(src_label):
                shutil.copy2(src_label, dst_label)
            else:
                # Create empty label (no detections in this frame)
                with open(dst_label, "w") as f:
                    pass

    # Optionally add IDD supplement to training set
    if idd_supplement_dir and os.path.exists(idd_supplement_dir):
        _add_idd_supplement(idd_supplement_dir, output_dir)

    # Generate data.yaml
    data_yaml = {
        "path": os.path.abspath(output_dir),
        "train": "train/images",
        "val": "val/images",
        "test": "test/images",
        "nc": len(CLASS_NAMES),
        "names": CLASS_NAMES,
    }

    data_yaml_path = os.path.join(output_dir, "data.yaml")
    with open(data_yaml_path, "w", encoding="utf-8") as f:
        yaml.dump(data_yaml, f, default_flow_style=False)

    logger.info(f"Dataset prepared — data.yaml at {data_yaml_path}")
    return data_yaml_path


def _add_idd_supplement(idd_dir: str, output_dir: str) -> None:
    """Add filtered IDD (Indian Driving Dataset) samples to training set.

    Only includes images containing our target classes (auto-rickshaw,
    two-wheeler, bus) for volume and diversity. The IDD labels may need
    class-ID remapping to match our class list.

    Args:
        idd_dir: Path to filtered IDD data (images/ + labels/).
        output_dir: Training dataset root.
    """
    import shutil

    idd_images = os.path.join(idd_dir, "images")
    idd_labels = os.path.join(idd_dir, "labels")

    if not os.path.exists(idd_images):
        logger.warning(f"IDD images directory not found: {idd_images}")
        return

    train_images = os.path.join(output_dir, "train", "images")
    train_labels = os.path.join(output_dir, "train", "labels")

    count = 0
    for img_file in os.listdir(idd_images):
        if not img_file.lower().endswith((".jpg", ".png", ".jpeg")):
            continue

        src_img = os.path.join(idd_images, img_file)
        dst_img = os.path.join(train_images, f"idd_{img_file}")
        shutil.copy2(src_img, dst_img)

        label_file = Path(img_file).stem + ".txt"
        src_label = os.path.join(idd_labels, label_file)
        dst_label = os.path.join(train_labels, f"idd_{label_file}")
        if os.path.exists(src_label):
            shutil.copy2(src_label, dst_label)
        else:
            with open(dst_label, "w") as f:
                pass

        count += 1

    logger.info(f"Added {count} IDD supplement images to training set")


def run_finetuning(
    data_yaml_path: str,
    base_model: str = "yolo26s.pt",
    epochs: int = 50,
    batch_size: int = 8,
    image_size: int = 640,
    patience: int = 10,
    output_dir: str = "models",
    project_name: str = "surat_finetune",
) -> str:
    """Fine-tune YOLO26 on the prepared dataset.

    Args:
        data_yaml_path: Path to data.yaml for the training dataset.
        base_model: Pretrained model to fine-tune from (e.g., "yolo26s.pt").
        epochs: Maximum training epochs.
        batch_size: Batch size (start at 8 for 8GB VRAM, try 16 if it fits).
        image_size: Training image size.
        patience: Early stopping patience (epochs without improvement).
        output_dir: Where to save the fine-tuned weights.
        project_name: Ultralytics project name for logging.

    Returns:
        Path to the best fine-tuned weights file.
    """
    from ultralytics import YOLO

    logger.info(
        f"Starting fine-tuning:\n"
        f"  Base model: {base_model}\n"
        f"  Dataset: {data_yaml_path}\n"
        f"  Epochs: {epochs}\n"
        f"  Batch size: {batch_size}\n"
        f"  Image size: {image_size}\n"
        f"  Patience: {patience}"
    )

    model = YOLO(base_model)

    try:
        results = model.train(
            data=data_yaml_path,
            epochs=epochs,
            batch=batch_size,
            imgsz=image_size,
            patience=patience,
            project=output_dir,
            name=project_name,
            exist_ok=True,
            # Performance settings for RTX 5060 (8GB VRAM)
            workers=4,
            amp=True,           # Automatic Mixed Precision
            cache=False,        # Don't cache images in RAM (16GB may be tight)
            # Augmentation (moderate — we have limited data)
            hsv_h=0.015,
            hsv_s=0.5,
            hsv_v=0.3,
            degrees=5.0,
            translate=0.1,
            scale=0.3,
            fliplr=0.5,
            mosaic=1.0,
            mixup=0.1,
            # Logging
            plots=True,
            save=True,
            verbose=True,
        )
    except RuntimeError as e:
        if "CUDA out of memory" in str(e) or "out of memory" in str(e):
            logger.error(
                f"CUDA OOM with batch_size={batch_size}. "
                f"Reduce to batch_size={batch_size // 2} and retry:\n"
                f"  python -m data_pipeline.finetune --batch {batch_size // 2}"
            )
        raise

    # Locate best weights
    best_weights = os.path.join(output_dir, project_name, "weights", "best.pt")

    if os.path.exists(best_weights):
        # Copy to models/ directory for easy access
        import shutil
        final_path = os.path.join("models", "surat_yolo26s_finetuned.pt")
        os.makedirs("models", exist_ok=True)
        shutil.copy2(best_weights, final_path)
        logger.info(f"Best weights saved to: {final_path}")
        logger.info(
            f"\nTo use the fine-tuned model, update config.yaml:\n"
            f"  model:\n"
            f"    weights: '{final_path}'"
        )
        return final_path
    else:
        logger.warning(f"Best weights not found at expected path: {best_weights}")
        return best_weights


# ─── CLI ─────────────────────────────────────────────────────────────

def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")

    parser = argparse.ArgumentParser(description="Fine-tune YOLO26 on Surat Traffic Data")
    parser.add_argument(
        "--data", default="data_pipeline/labels_corrected",
        help="Directory with corrected labels (images/ + labels/)",
    )
    parser.add_argument(
        "--idd_supplement", default=None,
        help="Optional: filtered IDD dataset directory to supplement training",
    )
    parser.add_argument(
        "--base_model", default="yolo26s.pt",
        help="Base model to fine-tune (default: yolo26s.pt)",
    )
    parser.add_argument(
        "--epochs", type=int, default=50,
        help="Training epochs (default: 50)",
    )
    parser.add_argument(
        "--batch", type=int, default=8,
        help="Batch size (default: 8, try 16 if VRAM allows)",
    )
    parser.add_argument(
        "--imgsz", type=int, default=640,
        help="Training image size (default: 640)",
    )
    parser.add_argument(
        "--patience", type=int, default=10,
        help="Early stopping patience (default: 10 epochs)",
    )
    parser.add_argument(
        "--output_dir", default="models",
        help="Directory for training output and weights",
    )
    parser.add_argument(
        "--skip_prepare", action="store_true",
        help="Skip dataset preparation (if data.yaml already exists)",
    )

    args = parser.parse_args()

    # Step 1: Prepare dataset
    dataset_dir = os.path.join(args.output_dir, "dataset")
    data_yaml_path = os.path.join(dataset_dir, "data.yaml")

    if not args.skip_prepare or not os.path.exists(data_yaml_path):
        data_yaml_path = prepare_dataset(
            corrected_dir=args.data,
            output_dir=dataset_dir,
            idd_supplement_dir=args.idd_supplement,
        )

    # Step 2: Fine-tune
    best_weights = run_finetuning(
        data_yaml_path=data_yaml_path,
        base_model=args.base_model,
        epochs=args.epochs,
        batch_size=args.batch,
        image_size=args.imgsz,
        patience=args.patience,
        output_dir=args.output_dir,
    )

    logger.info(
        f"\nFine-tuning complete!\n"
        f"  Best weights: {best_weights}\n"
        f"\nNext steps:\n"
        f"  1. Evaluate: python -m evaluation.evaluate --weights {best_weights}\n"
        f"  2. Update config.yaml → model.weights to point to the fine-tuned weights\n"
        f"  3. Run pipeline: python main.py"
    )


if __name__ == "__main__":
    main()
