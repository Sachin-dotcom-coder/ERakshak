"""Prepare browser-compatible MP4 feeds from every raw sample video."""

import subprocess
from pathlib import Path

import cv2
import imageio_ffmpeg


SCRIPT_DIR = Path(__file__).resolve().parent
RAW_VIDEO_DIR = SCRIPT_DIR / "sample_videos" / "raw"
OUTPUT_DIR = SCRIPT_DIR.parent / "frontend" / "public" / "videos"
SUPPORTED_EXTENSIONS = {".avi", ".mkv", ".mov", ".mp4"}


def prepare_video(source: Path, destination: Path, ffmpeg: str) -> None:
    temporary_output = destination.with_name(f".{destination.stem}.tmp.mp4")
    command = [
        ffmpeg,
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-i",
        str(source),
        "-map",
        "0:v:0",
        "-map",
        "0:a?",
        "-c:v",
        "libx264",
        "-preset",
        "fast",
        "-crf",
        "23",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        "-movflags",
        "+faststart",
        str(temporary_output),
    ]

    try:
        subprocess.run(command, check=True)

        capture = cv2.VideoCapture(str(temporary_output))
        try:
            if not capture.isOpened():
                raise RuntimeError(f"Unable to open transcoded video: {temporary_output}")
            success, frame = capture.read()
            if not success or frame is None:
                raise RuntimeError(f"Unable to decode transcoded video: {temporary_output}")
        finally:
            capture.release()

        temporary_output.replace(destination)
    finally:
        temporary_output.unlink(missing_ok=True)


def main() -> None:
    if not RAW_VIDEO_DIR.is_dir():
        raise FileNotFoundError(f"Raw video directory not found: {RAW_VIDEO_DIR}")

    sources = sorted(
        (
            path
            for path in RAW_VIDEO_DIR.iterdir()
            if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
        ),
        key=lambda path: path.name.casefold(),
    )
    if not sources:
        raise FileNotFoundError(f"No supported video files found in {RAW_VIDEO_DIR}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

    for index, source in enumerate(sources, start=1):
        destination = OUTPUT_DIR / f"traffic{index}.mp4"
        print(f"{source.name} -> {destination.name}")
        prepare_video(source, destination, ffmpeg)

    print(f"Prepared {len(sources)} browser-compatible video feeds in {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
