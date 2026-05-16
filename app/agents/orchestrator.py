from __future__ import annotations

from app.agents.evaluation_agent import EvaluationGenerationAgent
from app.agents.matching_agent import ArchitectureMatchingAgent
from app.agents.requirement_agent import RequirementAnalysisAgent
from app.schemas import AnalyzeResponse, RecommendResponse
from app.services.rule_engine import build_comparison_matrix


class ArchitectureAssistantOrchestrator:
    def __init__(
        self,
        requirement_agent: RequirementAnalysisAgent | None = None,
        matching_agent: ArchitectureMatchingAgent | None = None,
        evaluation_agent: EvaluationGenerationAgent | None = None,
    ) -> None:
        self.requirement_agent = requirement_agent or RequirementAnalysisAgent()
        self.matching_agent = matching_agent or ArchitectureMatchingAgent()
        self.evaluation_agent = evaluation_agent or EvaluationGenerationAgent()

    async def analyze(self, requirement: str) -> AnalyzeResponse:
        features = await self.requirement_agent.analyze(requirement)
        return AnalyzeResponse(requirement=requirement, features=features)

    async def recommend(self, requirement: str) -> RecommendResponse:
        features = await self.requirement_agent.analyze(requirement)
        candidates = self.matching_agent.match(features, top_k=3)
        report = await self.evaluation_agent.evaluate(requirement, features, candidates)
        return RecommendResponse(
            requirement=requirement,
            features=features,
            candidates=candidates,
            comparison_matrix=build_comparison_matrix(candidates),
            final_report=report,
        )
