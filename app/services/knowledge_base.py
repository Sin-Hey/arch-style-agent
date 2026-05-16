from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any


DATA_DIR = Path(__file__).resolve().parents[1] / "data"


@lru_cache(maxsize=1)
def load_architecture_styles() -> list[dict[str, Any]]:
    path = DATA_DIR / "architecture_styles.json"
    return json.loads(path.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def load_test_cases() -> list[dict[str, Any]]:
    path = DATA_DIR / "test_cases.json"
    return json.loads(path.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def load_course_knowledge() -> dict[str, Any]:
    path = DATA_DIR / "course_knowledge.json"
    return json.loads(path.read_text(encoding="utf-8"))
