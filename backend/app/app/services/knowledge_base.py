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


def build_knowledge_graph() -> dict[str, list[dict[str, Any]]]:
    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    seen_nodes: set[str] = set()

    def add_node(node_id: str, label: str, node_type: str, **extra: Any) -> None:
        if node_id in seen_nodes:
            return
        seen_nodes.add(node_id)
        nodes.append({"id": node_id, "label": label, "type": node_type, **extra})

    for style in load_architecture_styles():
        style_id = f"style:{style['id']}"
        add_node(style_id, style["name"], "architecture_style")
        for scenario in style.get("applicable_scenarios", []):
            scenario_id = f"scenario:{scenario}"
            add_node(scenario_id, scenario, "scenario")
            edges.append({"source": style_id, "target": scenario_id, "relation": "applies_to"})
        for keyword in style.get("matching_keywords", []):
            keyword_id = f"keyword:{keyword}"
            add_node(keyword_id, keyword, "keyword")
            edges.append({"source": keyword_id, "target": style_id, "relation": "matches"})
        for dimension, score in style.get("quality_scores", {}).items():
            quality_id = f"quality:{dimension}"
            add_node(quality_id, dimension, "quality_attribute")
            edges.append(
                {
                    "source": style_id,
                    "target": quality_id,
                    "relation": "has_quality_score",
                    "score": score,
                }
            )

    return {"nodes": nodes, "edges": edges}
