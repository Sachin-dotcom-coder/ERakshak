"""
data_pipeline/extract_frames.py — Frame Extraction with Metadata (Section 5)
==============================================================================
Extracts frames from video files with metadata tagging for dataset creation.

Tags each frame with:
- weather, lighting, traffic_density, occlusion, camera_quality
- junction_id, camera_id, time_of_day, vehicle_classes_present
"""

import logging
import json
import os
from pathlib import Path
from typing import Optional

import cv2
import numpy as np

logger = logging.getLogger(__name__)


class FrameExtractor:
    """Extract frames from video with metadata for dataset construction.

    Args:
        output_dir: Directory to save extracted frames.
        extract_rate: Extract every Nth frame (default: 30 = ~1 FPS at 30fps).
    """

    def __init__(
        self,
        output_dir: str = "datasets/extracted",
        extract_rate: int = 30,
    ) -> None:
        self._output_dir = Path(output_dir)
        self._extract_rate = extract_rate
        self._output_dir.mkdir(parents=True, exist_ok=True)

    def extract_from_video(
        self,
        video_path: str,
        junction_id: str = "unknown",
        camera_id: str = "unknown",
        metadata_overrides: Optional[dict] = None,
    ) -> list[dict]:
        """Extract frames from a video file.

        Args:
            video_path: Path to video file.
            junction_id: Junction identifier.
            camera_id: Camera identifier.
            metadata_overrides: Additional metadata to tag each frame.

        Returns:
            List of metadata dicts for extracted frames.
        """
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            logger.error(f"Failed to open video: {video_path}")
            return []

        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_idx = 0
        extracted = []

        video_name = Path(video_path).stem
        frames_dir = self._output_dir / video_name
        frames_dir.mkdir(parents=True, exist_ok=True)

        logger.info(
            f"Extracting frames from {video_path} "
            f"(every {self._extract_rate} frames, ~{total // self._extract_rate} total)"
        )

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if frame_idx % self._extract_rate == 0:
                # Auto-classify frame conditions
                metadata = self._classify_frame(frame)
                metadata.update({
                    "junction_id": junction_id,
                    "camera_id": camera_id,
                    "video_source": video_path,
                    "frame_index": frame_idx,
                    "timestamp_sec": round(frame_idx / fps, 2),
                })
                if metadata_overrides:
                    metadata.update(metadata_overrides)

                # Save frame
                frame_name = f"frame_{frame_idx:06d}.jpg"
                frame_path = str(frames_dir / frame_name)
                cv2.imwrite(frame_path, frame)
                metadata["frame_path"] = frame_path

                extracted.append(metadata)

            frame_idx += 1

        cap.release()

        # Save metadata index
        meta_path = str(frames_dir / "metadata.jsonl")
        with open(meta_path, "w") as f:
            for entry in extracted:
                f.write(json.dumps(entry) + "\n")

        logger.info(f"Extracted {len(extracted)} frames to {frames_dir}")
        return extracted

    def _classify_frame(self, frame: np.ndarray) -> dict:
        """Auto-classify frame conditions from image statistics."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        brightness = float(np.mean(gray))
        contrast = float(np.std(gray))

        # Lighting
        if brightness > 120:
            lighting = "day"
        elif brightness > 60:
            lighting = "dusk"
        else:
            lighting = "night"

        # Camera quality estimate
        blur = float(cv2.Laplacian(gray, cv2.CV_64F).var())
        if blur > 200:
            quality = "clear"
        elif blur > 100:
            quality = "slightly_blurred"
        else:
            quality = "blurred"

        return {
            "lighting": lighting,
            "brightness": round(brightness, 1),
            "contrast": round(contrast, 1),
            "blur_score": round(blur, 1),
            "camera_quality": quality,
        }
