from app.schemas import RequirementFeatures
from app.services.knowledge_base import load_architecture_styles, load_test_cases
from app.services.rule_engine import build_comparison_matrix, recommend_candidates


def test_knowledge_base_has_required_styles() -> None:
    styles = load_architecture_styles()
    names = {style["name"] for style in styles}

    assert len(styles) >= 10
    assert {"分层架构", "微服务架构", "事件驱动架构"}.issubset(names)
    for style in styles:
        assert style["advantages"]
        assert style["disadvantages"]
        assert style["applicable_scenarios"]
        assert style["topology"]["nodes"]
        assert style["topology"]["edges"]


def test_test_case_dataset_has_twenty_scenarios() -> None:
    cases = load_test_cases()

    assert len(cases) >= 20
    assert all(item["requirement"] for item in cases)


def test_im_requirement_prefers_event_or_microservices() -> None:
    features = RequirementFeatures(
        domain="即时通讯",
        core_functions=["消息", "视频通话", "通知"],
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

    candidates = recommend_candidates(features, load_architecture_styles(), top_k=3)
    names = [item.name for item in candidates]

    assert len(candidates) >= 3
    assert names[0] in {"事件驱动架构", "微服务架构"}
    assert "事件驱动架构" in names
    assert "微服务架构" in names


def test_management_system_prefers_layered_or_mvc() -> None:
    features = RequirementFeatures(
        domain="企业管理系统",
        core_functions=["表单", "审批", "后台管理"],
        concurrency=2,
        realtime=1,
        reliability=3,
        scalability=2,
        deployment_complexity=1,
        data_consistency=4,
        team_collaboration=3,
        maintainability=5,
        data_flow="请求响应和事务数据",
        quality_attributes=["维护", "一致性"],
    )

    candidates = recommend_candidates(features, load_architecture_styles(), top_k=3)
    names = [item.name for item in candidates]
    matrix = build_comparison_matrix(candidates)

    assert names[0] in {"分层架构", "MVC架构", "仓库架构"}
    assert "分层架构" in names or "MVC架构" in names
    assert len(matrix) == 3
    assert "总分" in matrix[0]
