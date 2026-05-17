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
                    "如果需求描述模糊，要在 ambiguity_notes 中明确指出缺失信息。"
                ),
            },
            {
                "role": "user",
                "content": (
                    "Few-shot 示例：需求：开发企业内部审批和报表系统，用户量中等，要求权限、流程、"
                    "数据一致性和后期维护方便。请抽取架构特征。"
                ),
            },
            {
                "role": "assistant",
                "content": (
                    '{"domain":"企业管理系统","core_functions":["审批流程","权限管理","报表查询"],'
                    '"concurrency":2,"realtime":1,"reliability":3,"scalability":2,'
                    '"deployment_complexity":1,"data_consistency":5,"team_collaboration":3,'
                    '"maintainability":5,"data_flow":"页面请求 -> 业务处理 -> 事务数据存储 -> 报表查询",'
                    '"deployment_constraints":["企业内网部署"],'
                    '"quality_attributes":["可维护性","数据一致性","易用性"],'
                    '"ambiguity_notes":["未说明安全等级和峰值并发"]}'
                ),
            },
            {
                "role": "user",
                "content": (
                    "Few-shot 示例：需求：建设订单事件处理平台，需要高吞吐异步处理，多个下游系统订阅，"
                    "允许最终一致但要能追踪失败消息。请抽取架构特征。"
                ),
            },
            {
                "role": "assistant",
                "content": (
                    '{"domain":"异步数据处理平台","core_functions":["订单事件接入","消息分发","失败追踪"],'
                    '"concurrency":5,"realtime":3,"reliability":5,"scalability":5,'
                    '"deployment_complexity":4,"data_consistency":2,"team_collaboration":4,'
                    '"maintainability":4,"data_flow":"事件生产者 -> 消息队列 -> 消费者 -> 失败补偿",'
                    '"deployment_constraints":["分布式部署","可观测性要求"],'
                    '"quality_attributes":["高吞吐","可靠性","可扩展性"],'
                    '"ambiguity_notes":["未说明消息顺序和幂等策略"]}'
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
