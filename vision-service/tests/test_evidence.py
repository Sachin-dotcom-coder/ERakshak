"""
test_evidence.py — Unit tests for Evidence RingBuffer and Packet Builder
========================================================================
Tests RingBuffer frame window extraction and EvidenceBuilder SHA-256 manifest integrity.
(improvements.md § A7.1, C2)
"""

import json
import os
import shutil
import tempfile
import unittest
import numpy as np

from evidence.ring_buffer import RingBuffer
from evidence.builder import EvidenceBuilder


class TestEvidence(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_ring_buffer_push_and_window(self):
        rb = RingBuffer(seconds=2.0, fps=10.0)
        # Push 20 frames across 2.0 seconds
        dummy_frame = np.zeros((100, 100, 3), dtype=np.uint8)
        for i in range(20):
            ts = 100.0 + i * 0.1
            rb.push(ts, dummy_frame)

        # Window between 100.5 and 101.5
        win = rb.window(100.5, 101.5)
        self.assertEqual(len(win), 11)  # 100.5 to 101.5 inclusive at 0.1 step
        self.assertAlmostEqual(win[0][0], 100.5, places=2)
        self.assertAlmostEqual(win[-1][0], 101.5, places=2)

    def test_evidence_builder_packet_and_manifest(self):
        builder = EvidenceBuilder(output_root=self.temp_dir, pre_roll_s=1.0, post_roll_s=1.0)
        rb = RingBuffer(seconds=5.0, fps=10.0)
        frame = np.ones((80, 80, 3), dtype=np.uint8) * 100

        for i in range(30):
            rb.push(10.0 + i * 0.1, frame)

        event = {
            "event_id": "e-test-123",
            "type": "RED_LIGHT_VIOLATION",
            "cross_ts": 11.5,
            "track_id": 42,
        }
        metadata = {
            "camera_id": "J001-S-01",
            "junction_id": "J001",
            "calibration_version": "v1",
            "model_version": "v1",
            "config_hash": "abc123hash",
        }
        key_frames = {
            "before": (11.0, frame),
            "crossing": (11.5, frame),
            "confirmed": (12.0, frame),
        }

        built_event = builder.build(event, rb, key_frames, metadata, plate_crop=frame)

        self.assertIn("evidence_uri", built_event)
        evidence_path = built_event["evidence_uri"]
        self.assertTrue(os.path.exists(evidence_path))

        # Check manifest file
        manifest_path = os.path.join(evidence_path, "manifest.json")
        self.assertTrue(os.path.exists(manifest_path))

        with open(manifest_path, "r") as f:
            manifest = json.load(f)

        self.assertEqual(manifest["event_id"], "e-test-123")
        self.assertEqual(manifest["camera_id"], "J001-S-01")
        self.assertIn("manifest_sha256", manifest)
        self.assertIn("files", manifest)
        self.assertIn("frame_before.jpg", manifest["files"])
        self.assertIn("frame_crossing.jpg", manifest["files"])
        self.assertIn("frame_confirmed.jpg", manifest["files"])
        self.assertIn("clip.mjpeg", manifest["files"])
        self.assertIn("plate_best.jpg", manifest["files"])


if __name__ == "__main__":
    unittest.main()
