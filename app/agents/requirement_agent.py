from __future__ import annotations

from app.schemas import RequirementFeatures
from app.services.llm import DeepSeekClient


class RequirementAnalysisAgent:
    def __init__(self, llm: DeepSeekClient | None = None) -> None:
        self.llm = llm or DeepSeekClient()

    async def analyze(self, requirement: str) -> RequirementFeatures:
        messages = [
            {
                "role": "system",
                "content": (
                    "你是软件体系结构课程中的需求解析 Agent。"
                    "请只返回 JSON，不要 Markdown。所有 0-5 分字段必须是整数。"
                ),
            },
            {
                "role": "user",
                "content": f"""
从下面的软件需求中抽取架构决策特征。

字段要求：
- domain: 业务领域，字符串
- core_functions: 核心功能列表
- concurrency: 高并发要求 0-5
- realtime: 实时性要求 0-5
- reliability: 可靠性要求 0-5
- scalability: 可扩展性要求 0-5
- deployment_complexity: 部署复杂度/分布式部署要求 0-5
- data_consistency: 数据一致性要求 0-5
- team_collaboration: 多团队协作/独立交付要求 0-5
- maintainability: 可维护性要求 0-5
- data_flow: 数据流特征，字符串
- deployment_constraints: 部署约束列表
- quality_attributes: 质量属性列表
- ambiguity_notes: 不确定或缺失信息列表

需求：
{requirement}
""".strip(),
            },
        ]
        payload = await self.llm.chat_json(messages)
        return RequirementFeatures.model_validate(payload)
