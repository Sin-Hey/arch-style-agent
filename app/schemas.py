from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


Priority = Literal[0, 1, 2, 3, 4, 5]


class RequirementRequest(BaseModel):
    requirement: str = Field(..., min_length=5, description="Natural language requirement text")


class RequirementFeatures(BaseModel):
    domain: str = Field(default="通用软件系统")
    core_functions: list[str] = Field(default_factory=list)
    concurrency: Priority = 0
    realtime: Priority = 0
    reliability: Priority = 0
    scalability: Priority = 0
    deployment_complexity: Priority = 0
    data_consistency: Priority = 0
    team_collaboration: Priority = 0
    maintainability: Priority = 0
    data_flow: str = "未明确"
    deployment_constraints: list[str] = Field(default_factory=list)
    quality_attributes: list[str] = Field(default_factory=list)
    ambiguity_notes: list[str] = Field(default_factory=list)


class ScoreDetail(BaseModel):
    dimension: str
    score: float
    reason: str


class ArchitectureCandidate(BaseModel):
    id: str
    name: str
    total_score: float
    suitability: str
    advantages: list[str]
    disadvantages: list[str]
    applicable_scenarios: list[str]
    score_details: list[ScoreDetail]
    mermaid: str


class EvaluationReport(BaseModel):
    final_recommendation: str
    recommendation_reason: list[str]
    advantages: list[str]
    disadvantages: list[str]
    risk_mitigation: list[str]
    decision_trace: list[str]


class AnalyzeResponse(BaseModel):
    requirement: str
    features: RequirementFeatures


class RecommendResponse(BaseModel):
    requirement: str
    features: RequirementFeatures
    candidates: list[ArchitectureCandidate]
    comparison_matrix: list[dict[str, Any]]
    final_report: EvaluationReport


class ErrorResponse(BaseModel):
    detail: str
