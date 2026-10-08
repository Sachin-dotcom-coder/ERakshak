import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
VISION_DIR = ROOT_DIR / "vision-service"
SCRIPT = VISION_DIR / "annotate_videos.py"

print("Running vision service video annotator...")
res = subprocess.run([sys.executable, str(SCRIPT)], cwd=str(VISION_DIR))
sys.exit(res.returncode)
