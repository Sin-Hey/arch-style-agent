from __future__ import annotations

import json

from app.schemas import ArchitectureCandidate, EvaluationReport, RequirementFeatures
from app.services.llm import DeepSeekClient


class EvaluationGenerationAgent:
    def __init__(self, llm: DeepSeekClient | None = None) -> None:
        self.llm = llm or DeepSeekClient()

    async def evaluate(
        self,
        requirement: str,
        features: RequirementFeatures,
        candidates: list[ArchitectureCandidate],
    ) -> EvaluationReport:
        features_json = json.dumps(features.model_dump(), ensure_ascii=False)
        candidate_summary = [
            {
                "name": item.name,
                "score": item.total_score,
                "suitability": item.suitability,
                "advantages": item.advantages,
                "disadvantages": item.disadvantages,
                "score_details": [
                    {"dimension": detail.dimension, "score": detail.score, "reason": detail.reason}
                    for detail in item.score_details
                ],
            }
            for item in candidates
        ]
        messages = [
            {
                "role": "system",
                "content": (
                    "你是软件架构评估生成 Agent，负责给出可解释的架构决策报告。"
                    "请结合质量属性、架构风格特点与规则引擎评分结果进行分析。"
                    "必须只返回 JSON，不要 Markdown。"
                ),
            },
            {
                "role": "user",
                "content": f"""
基于需求特征和规则引擎候选结果，生成最终推荐报告。
必须返回 JSON：
{{
  "final_recommendation": "候选架构名称",
  "recommendation_reason": ["理由1", "理由2"],
  "advantages": ["优点1", "优点2"],
  "disadvantages": ["缺点1", "缺点2"],
  "risk_mitigation": ["风险应对1", "风险应对2"],
  "decision_trace": ["需求特征 -> 规则评分 -> LLM评估 的决策链路"],
  "hybrid_recommendation": "如果适合，给出组合架构方案，例如 微服务 + 事件驱动 + CQRS；如果不需要组合，说明单一风格足够。",
  "quality_tradeoffs": ["性能与一致性权衡", "可扩展性与部署复杂度权衡"],
  "refactoring_plan": ["从现有系统迁移到推荐架构的步骤1", "步骤2", "步骤3"]
}}

原始需求：
{requirement}

需求特征：
{features_json}

候选架构：
{json.dumps(candidate_summary, ensure_ascii=False)}
""".strip(),
            },
        ]
        payload = await self.llm.chat_json(messages, temperature=0.2)
        report = EvaluationReport.model_validate(payload)
        return ensure_report_extensions(report, candidates)


def ensure_report_extensions(
    report: EvaluationReport,
    candidates: list[ArchitectureCandidate],
) -> EvaluationReport:
    candidate_names = [item.name for item in candidates[:3]]
    if not report.hybrid_recommendation:
        report.hybrid_recommendation = " + ".join(candidate_names)
    if not report.quality_tradeoffs:
        report.quality_tradeoffs = [
            "高性能和高可扩展性通常会提高部署复杂度，需要补充自动化运维和可观测性。",
            "强一致性会降低异步处理吞吐，需要按业务边界选择最终一致或事务一致。",
        ]
    if not report.refactoring_plan:
        report.refactoring_plan = [
            "先识别核心业务边界、数据流和质量属性优先级。",
            f"以 {candidate_names[0] if candidate_names else report.final_recommendation} 作为目标架构建立核心链路原型。",
            "逐步拆分高变化或高负载模块，并为关键接口增加监控、回滚和验证机制。",
        ]
    return report
