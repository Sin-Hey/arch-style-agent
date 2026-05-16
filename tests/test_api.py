from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient

from app.agents.evaluation_agent import EvaluationGenerationAgent
from app.agents.requirement_agent import RequirementAnalysisAgent
from app.main import app
from app.schemas import EvaluationReport, RequirementFeatures


def test_static_data_endpoints() -> None:
    client = TestClient(app)

    styles = client.get("/api/styles")
    examples = client.get("/api/examples")

    assert styles.status_code == 200
    assert examples.status_code == 200
    assert len(styles.json()) >= 10
    assert len(examples.json()) >= 20


def test_recommend_returns_three_candidates(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_analyze(self: RequirementAnalysisAgent, requirement: str) -> RequirementFeatures:
        return RequirementFeatures(
            domain="即时通讯",
            core_functions=["消息", "视频通话"],
            concurrency=5,
            realtime=5,
            reliability=4,
            scalability=5,
            deployment_complexity=4,
            data_consistency=2,
            team_collaboration=4,
            maintainability=3,
            data_flow="消息事件实时广播",
            quality_attributes=["高并发", "实时", "可靠", "扩展"],
        )

    async def fake_evaluate(
        self: EvaluationGenerationAgent,
        requirement: str,
        features: RequirementFeatures,
        candidates: list,
    ) -> EvaluationReport:
        return EvaluationReport(
            final_recommendation=candidates[0].name,
            recommendation_reason=["规则评分最高", "满足高并发和实时消息要求"],
            advantages=candidates[0].advantages[:2],
            disadvantages=candidates[0].disadvantages[:2],
            risk_mitigation=["补充消息追踪和重试机制"],
            decision_trace=["需求解析", "规则评分", "LLM评估"],
        )

    monkeypatch.setattr(RequirementAnalysisAgent, "analyze", fake_analyze)
    monkeypatch.setattr(EvaluationGenerationAgent, "evaluate", fake_evaluate)

    client = TestClient(app)
    response = client.post(
        "/api/recommend",
        json={"requirement": "开发一个跨平台即时通讯系统，支持万人同时在线和视频通话扩展。"},
    )

    assert response.status_code == 200
    body = response.json()
    assert len(body["candidates"]) >= 3
    assert len(body["comparison_matrix"]) >= 3
    assert body["final_report"]["final_recommendation"] in {
        item["name"] for item in body["candidates"]
    }


def test_analyze_requires_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    os.environ.pop("DEEPSEEK_API_KEY", None)

    client = TestClient(app)
    response = client.post(
        "/api/analyze",
        json={"requirement": "开发一个企业管理系统，需要审批、权限和报表功能。"},
    )

    assert response.status_code == 503
    assert "DEEPSEEK_API_KEY" in response.json()["detail"]
