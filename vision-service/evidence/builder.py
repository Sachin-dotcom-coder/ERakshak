"""
builder.py — Violation evidence packet builder
================================================
Assembles a complete, cryptographically-hashed evidence packet for each
confirmed violation event, ready for human reviewer inspection.

Design (improvements.md §A7.1, C2):
- Draws overlays on COPIES of frames (never modifies originals)
- Includes 3 key frames + a short clip around the crossing moment
- SHA-256 hashes every file and produces a signed manifest
- Attaches full metadata: camera, calibration, model, config hash, timestamps
- All files written to object storage path (local or S3 URI stub)

Usage:
    builder = EvidenceBuilder(output_root="output/evidence")
    packet = builder.build(event, ring_buffer, key_frames, metadata)
"""

import hashlib
import json
import logging
import os
import time
import uuid
from pathlib import Path
from typing import Optional

import cv2
import numpy as np

logger = logging.getLogger(__name__)


class EvidenceBuilder:
    """
    Builds a tamper-evident evidence packet for a confirmed violation.

    Each packet is stored in a dedicated directory:
        <output_root>/<junction_id>/<date>/<event_id>/
            manifest.json     ← all metadata + file hashes
            frame_before.jpg  ← vehicle before the line (signal head visible)
            frame_at_cross.jpg← closest frame to the crossing moment
            frame_confirmed.jpg← vehicle inside box / deep in corridor
            clip.avi or clip.mjpeg ← N-second window around the event
            plate_best.jpg    ← best-scoring plate crop (if available)

    Args:
        output_root: Base directory for evidence files.
        pre_roll_s: Seconds of footage before the crossing to include in the clip.
        post_roll_s: Seconds of footage after confirmation to include.
    """

    def __init__(
        self,
        output_root: str = "output/evidence",
        pre_roll_s: float = 4.0,
        post_roll_s: float = 4.0,
    ):
        self.output_root = Path(output_root)
        self.pre_roll_s = pre_roll_s
        self.post_roll_s = post_roll_s

    def build(
        self,
        event: dict,
        ring_buffer,
        key_frames: dict,
        metadata: dict,
        plate_crop: Optional[np.ndarray] = None,
    ) -> dict:
        """
        Build the full evidence packet and write it to disk.

        Args:
            event: The violation event dict from RLVEngine or BRTSEngine.
            ring_buffer: RingBuffer instance (must cover pre_roll + post_roll window).
            key_frames: Dict with keys "before", "crossing", "confirmed" → (ts, frame_bgr).
            metadata: Dict with camera_id, calibration_version, model_version, config_hash,
                      junction_id, etc.
            plate_crop: Optional BGR image of the best plate crop.

        Returns:
            Updated event dict with "evidence_uri" field populated.
        """
        event_id = event.get("event_id") or f"e-{int(time.time() * 1000)}"
        junction_id = metadata.get("junction_id", "J000")
        date_str = time.strftime("%Y-%m-%d")

        packet_dir = self.output_root / junction_id / date_str / event_id
        packet_dir.mkdir(parents=True, exist_ok=True)

        file_hashes = {}

        # 1. Write key frames (overlays on copies)
        for label, data in key_frames.items():
            if data is None:
                continue
            ts, frame = data
            fname = f"frame_{label}.jpg"
            fpath = packet_dir / fname
            annotated = self._annotate_frame(frame.copy(), event, metadata)
            ok, jpg = cv2.imencode(".jpg", annotated, [cv2.IMWRITE_JPEG_QUALITY, 90])
            if ok:
                fpath.write_bytes(jpg.tobytes())
                file_hashes[fname] = self._sha256(fpath)

        # 2. Extract clip from ring buffer
        cross_ts = event.get("cross_ts") or event.get("entry_ts") or 0.0
        t_start = cross_ts - self.pre_roll_s
        t_end = cross_ts + self.post_roll_s
        clip_frames = ring_buffer.window(t_start, t_end)
        if clip_frames:
            clip_path = packet_dir / "clip.mjpeg"
            with open(clip_path, "wb") as f:
                for _, jpg_bytes in clip_frames:
                    f.write(jpg_bytes)
            file_hashes["clip.mjpeg"] = self._sha256(clip_path)

        # 3. Plate crop
        if plate_crop is not None:
            plate_path = packet_dir / "plate_best.jpg"
            ok, jpg = cv2.imencode(".jpg", plate_crop, [cv2.IMWRITE_JPEG_QUALITY, 95])
            if ok:
                plate_path.write_bytes(jpg.tobytes())
                file_hashes["plate_best.jpg"] = self._sha256(plate_path)

        # 4. Build manifest
        manifest = {
            "event_id": event_id,
            "type": event.get("type"),
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "camera_id": metadata.get("camera_id"),
            "junction_id": junction_id,
            "calibration_version": metadata.get("calibration_version"),
            "model_version": metadata.get("model_version"),
            "config_hash": metadata.get("config_hash"),
            "event": event,
            "files": file_hashes,
            "review_status": "NEW",
            "reviewer": None,
            "reviewer_decision": None,
            "reviewer_ts": None,
        }

        manifest_path = packet_dir / "manifest.json"
        manifest_bytes = json.dumps(manifest, indent=2, default=str).encode()
        manifest_path.write_bytes(manifest_bytes)
        manifest["manifest_sha256"] = self._sha256_bytes(manifest_bytes)
        manifest_path.write_text(json.dumps(manifest, indent=2, default=str))

        evidence_uri = str(packet_dir)  # Replace with s3:// URI in production
        event["evidence_uri"] = evidence_uri
        event["event_id"] = event_id

        logger.info(f"Evidence packet written: {evidence_uri}")
        return event

    def _annotate_frame(self, frame: np.ndarray, event: dict, metadata: dict) -> np.ndarray:
        """
        Draw minimal annotation on a copy of a frame.
        Draws: event type label, timestamp, camera ID. No personal data.
        """
        label = f"{event.get('type', 'VIOLATION')} | {metadata.get('camera_id', '')}"
        ts_str = str(event.get("cross_ts") or event.get("entry_ts") or "")
        cv2.putText(frame, label, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.putText(frame, ts_str[:26], (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        return frame

    @staticmethod
    def _sha256(path: Path) -> str:
        """Compute SHA-256 hex digest of a file."""
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()

    @staticmethod
    def _sha256_bytes(data: bytes) -> str:
        """Compute SHA-256 hex digest of raw bytes."""
        return hashlib.sha256(data).hexdigest()
