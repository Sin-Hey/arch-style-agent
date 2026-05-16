from __future__ import annotations

import json

from app.schemas import ArchitectureCandidate, EvaluationReport, RequirementFeatures
from app.services.knowledge_base import load_course_knowledge
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
        course_knowledge = load_course_knowledge()
        course_summary = json.dumps(course_knowledge["prompt_summary"], ensure_ascii=False)
        candidate_summary = [
            {
                "name": item.name,
                "score": item.total_score,
                "suitability": item.suitability,
                "advantages": item.advantages,
                "disadvantages": item.disadvantages,
            }
            for item in candidates
        ]
        messages = [
            {
                "role": "system",
                "content": (
                    "你是软件架构评估生成 Agent，负责给出可解释的架构决策报告。"
                    "请只返回 JSON，不要 Markdown。"
                ),
            },
            {
                "role": "user",
                "content": f"""
基于需求特征、规则引擎候选结果，生成最终推荐报告。

必须返回 JSON：
{{
  "final_recommendation": "候选架构名称",
  "recommendation_reason": ["理由1", "理由2"],
  "advantages": ["优点1", "优点2"],
  "disadvantages": ["缺点1", "缺点2"],
  "risk_mitigation": ["风险应对1", "风险应对2"],
  "decision_trace": ["需求特征 -> 规则评分 -> LLM评估 的决策链条"]
}}

原始需求：
{requirement}

需求特征：
{features_json}

候选架构：
{candidate_summary}

课程知识库摘要：
{course_summary}
""".strip(),
            },
        ]
        payload = await self.llm.chat_json(messages, temperature=0.2)
        return EvaluationReport.model_validate(payload)
