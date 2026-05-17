from __future__ import annotations

import sys
from pathlib import Path


BACKEND_APP_DIR = Path(__file__).resolve().parent / "app"
sys.path.insert(0, str(BACKEND_APP_DIR))

from app.main import app  # noqa: E402
