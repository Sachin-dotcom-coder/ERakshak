"""
calibration/pick_reference_points.py — Point-and-Click Reference Helper
=========================================================================
ERH26_PS_08: Data-Driven Traffic Optimization

A standalone OpenCV helper script to make camera calibration less tedious.
Opens a single frame from a given video and lets you click exactly where
the reference points are. It then prints the pixel coordinates in the exact
YAML format needed for `camera_config.yaml`.

Usage:
    python pick_reference_points.py ../sample_videos/raw/some_video.avi
"""

import argparse
import sys
from pathlib import Path

import cv2

# Global state for mouse callback
clicked_points = []
frame_copy = None

def mouse_callback(event, x, y, flags, param):
    """OpenCV mouse callback to record clicks and draw them on screen."""
    global clicked_points, frame_copy
    if event == cv2.EVENT_LBUTTONDOWN:
        clicked_points.append((x, y))
        # Draw a clear marker
        cv2.circle(frame_copy, (x, y), 5, (0, 255, 0), -1)
        # Put text slightly offset
        cv2.putText(frame_copy, f"P{len(clicked_points)}", (x + 10, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.imshow("Reference Point Picker", frame_copy)

def main():
    global frame_copy
    parser = argparse.ArgumentParser(description="Pick homography reference points from a video frame.")
    parser.add_argument("video_path", help="Path to the video file")
    parser.add_argument("--frame_index", type=int, default=0, help="Frame index to extract (default: 0)")
    args = parser.parse_args()

    video_path = Path(args.video_path)
    if not video_path.exists():
        print(f"Error: Video file not found at {video_path}")
        sys.exit(1)

    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        print(f"Error: Failed to open video {video_path}")
        sys.exit(1)

    # Seek to requested frame
    cap.set(cv2.CAP_PROP_POS_FRAMES, args.frame_index)
    ret, frame = cap.read()
    if not ret:
        print(f"Error: Could not read frame {args.frame_index}")
        sys.exit(1)

    cap.release()

    frame_copy = frame.copy()
    window_name = "Reference Point Picker"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.imshow(window_name, frame_copy)
    cv2.setMouseCallback(window_name, mouse_callback)

    print("\n" + "="*50)
    print(f"Opened: {video_path.name}")
    print("INSTRUCTIONS:")
    print("1. Click on the image to place reference points.")
    print("2. You need at least 4 non-collinear points for homography.")
    print("3. Press 'c' to clear points if you make a mistake.")
    print("4. Press 'q' or 'ENTER' or 'ESC' when finished.")
    print("="*50 + "\n")

    while True:
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27 or key == 13:  # q, esc, enter
            break
        elif key == ord('c'):
            clicked_points.clear()
            frame_copy = frame.copy()
            cv2.imshow(window_name, frame_copy)
            print("Points cleared.")

    cv2.destroyAllWindows()

    print("\n--- RESULTS ---")
    if not clicked_points:
        print("No points selected.")
        return

    print(f"You selected {len(clicked_points)} points.\n")
    print("Paste the following into camera_config.yaml under 'pixel_points':\n")
    
    print("    pixel_points:")
    for idx, (x, y) in enumerate(clicked_points):
        print(f"      - [{x}, {y}]   # Point {idx+1}")
        
    print("\nRemember to supply the corresponding 'world_points' in meters!\n")


if __name__ == "__main__":
    main()
