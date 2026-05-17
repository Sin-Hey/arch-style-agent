from __future__ import annotations

from app.schemas import ArchitectureCandidate, RequirementFeatures, ScoreDetail


DIMENSION_LABELS = {
    "concurrency": "高并发",
    "realtime": "实时性",
    "reliability": "可靠性",
    "scalability": "可扩展性",
    "deployment_complexity": "部署复杂度",
    "data_consistency": "数据一致性",
    "team_collaboration": "团队协作",
    "maintainability": "可维护性",
}


def recommend_candidates(
    features: RequirementFeatures,
    styles: list[dict],
    top_k: int = 3,
) -> list[ArchitectureCandidate]:
    scored = [score_style(features, style) for style in styles]
    scored.sort(key=lambda item: item.total_score, reverse=True)
    return scored[: max(3, top_k)]


def score_style(features: RequirementFeatures, style: dict) -> ArchitectureCandidate:
    quality_scores = style.get("quality_scores", {})
    details: list[ScoreDetail] = []
    weighted_total = 0.0
    weight_sum = 0.0

    for key, label in DIMENSION_LABELS.items():
        demand = float(getattr(features, key))
        style_score = float(quality_scores.get(key, 2))
        weight = demand if demand > 0 else 0.6
        contribution = style_score * weight
        weighted_total += contribution
        weight_sum += 5 * weight
        details.append(
            ScoreDetail(
                dimension=label,
                score=round(style_score, 2),
                reason=_dimension_reason(label, demand, style_score),
            )
        )

    keyword_bonus = _keyword_bonus(features, style)
    semantic_adjustment = _semantic_adjustment(features, style["id"])
    total = (weighted_total / weight_sum * 100 if weight_sum else 0) + keyword_bonus + semantic_adjustment
    total = max(0, min(100, total))

    return ArchitectureCandidate(
        id=style["id"],
        name=style["name"],
        total_score=round(total, 2),
        suitability=_suitability(total),
        advantages=style["advantages"],
        disadvantages=style["disadvantages"],
        applicable_scenarios=style["applicable_scenarios"],
        score_details=details,
        mermaid=to_mermaid(style),
    )


def build_comparison_matrix(candidates: list[ArchitectureCandidate]) -> list[dict]:
    rows: list[dict] = []
    for candidate in candidates:
        row = {
            "架构风格": candidate.name,
            "总分": candidate.total_score,
            "适配度": candidate.suitability,
        }
        for detail in candidate.score_details:
            row[detail.dimension] = detail.score
        rows.append(row)
    return rows


def to_mermaid(style: dict) -> str:
    topology = style.get("topology", {})
    nodes = topology.get("nodes", [])
    edges = topology.get("edges", [])
    lines = ["flowchart LR"]
    for node in nodes:
        lines.append(f'  {node["id"]}["{node["label"]}"]')
    for edge in edges:
        lines.append(f'  {edge["from"]} -->|{edge.get("label", "")}| {edge["to"]}')
    return "\n".join(lines)


def _keyword_bonus(features: RequirementFeatures, style: dict) -> float:
    text = " ".join(
        [
            features.domain,
            features.data_flow,
            " ".join(features.core_functions),
            " ".join(features.quality_attributes),
            " ".join(features.deployment_constraints),
        ]
    )
    bonus = 0.0
    for keyword in style.get("matching_keywords", []):
        if keyword and keyword in text:
            bonus += 2.0
    return min(12.0, bonus)


def _semantic_adjustment(features: RequirementFeatures, style_id: str) -> float:
    text = _feature_text(features)
    adjustment = 0.0

    plugin_terms = [
        "插件",
        "可插拔",
        "第三方",
        "独立安装",
        "卸载",
        "升级",
        "语法高亮",
        "格式化",
        "调试器",
        "主题",
        "扩展点",
        "扩展平台",
    ]
    pipeline_terms = ["日志", "清洗", "过滤", "转换", "聚合", "批处理", "流水线", "高吞吐"]

    if _contains_any(text, plugin_terms):
        if style_id == "microkernel":
            adjustment += 18.0
        elif style_id == "microservices":
            adjustment -= 14.0

    if _contains_any(text, pipeline_terms):
        if style_id == "pipe_filter":
            adjustment += 14.0
        elif style_id == "microservices":
            adjustment -= 6.0

    if features.data_consistency >= 4 and features.deployment_complexity <= 2:
        if style_id in {"layered", "mvc", "repository"}:
            adjustment += 8.0
        elif style_id == "microservices":
            adjustment -= 10.0

    if features.concurrency <= 2 and features.team_collaboration <= 2 and features.deployment_complexity <= 2:
        if style_id == "microservices":
            adjustment -= 8.0
        elif style_id in {"layered", "mvc"}:
            adjustment += 5.0

    return adjustment


def _feature_text(features: RequirementFeatures) -> str:
    return " ".join(
        [
            features.domain,
            features.data_flow,
            " ".join(features.core_functions),
            " ".join(features.quality_attributes),
            " ".join(features.deployment_constraints),
            " ".join(features.ambiguity_notes),
        ]
    )


def _contains_any(text: str, terms: list[str]) -> bool:
    return any(term in text for term in terms)


def _dimension_reason(label: str, demand: float, style_score: float) -> str:
    if demand >= 4 and style_score >= 4:
        return f"需求强调{label}，该架构在此维度表现突出。"
    if demand >= 4 and style_score <= 2:
        return f"需求强调{label}，但该架构在此维度存在短板。"
    if demand == 0:
        return f"需求未明确强调{label}，按架构通用能力计入基础分。"
    return f"需求对{label}有一定要求，该架构提供中等匹配能力。"


def _suitability(score: float) -> str:
    if score >= 82:
        return "高度适配"
    if score >= 68:
        return "较适配"
    if score >= 50:
        return "可作为备选"
    return "适配度较低"
