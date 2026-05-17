from __future__ import annotations

from app.schemas import ArchitectureCandidate, RequirementFeatures
from app.services.knowledge_base import load_architecture_styles
from app.services.rule_engine import recommend_candidates


class ArchitectureMatchingAgent:
    def match(self, features: RequirementFeatures, top_k: int = 3) -> list[ArchitectureCandidate]:
        styles = load_architecture_styles()
        return recommend_candidates(features, styles, top_k=top_k)
