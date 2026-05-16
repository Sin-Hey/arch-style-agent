# 软件架构风格智能助手

这是一个用于《软件体系结构》课程大作业演示的 Web API 系统，核心能力包括需求解析、架构风格推荐、规则评分、LLM 评估报告、对比矩阵和 Mermaid 拓扑图。

## 运行环境

```powershell
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
$env:DEEPSEEK_API_KEY="你的 DeepSeek API Key"
$env:DEEPSEEK_BASE_URL="https://api.deepseek.com"
$env:DEEPSEEK_MODEL="deepseek-chat"
.\.venv\Scripts\uvicorn app.main:app --reload
```

浏览器访问：

```text
http://127.0.0.1:8000
```

未配置 `DEEPSEEK_API_KEY` 时，`/api/analyze` 和 `/api/recommend` 会返回 503，并提示配置环境变量。

## API

### `POST /api/analyze`

请求：

```json
{
  "requirement": "开发一个跨平台的即时通讯系统，要求支持万人同时在线..."
}
```

返回需求结构化特征，包括并发、实时性、可靠性、扩展性、部署约束、数据流等。

### `POST /api/recommend`

请求同 `/api/analyze`。

返回：

- `features`：需求特征
- `candidates`：至少 3 个候选架构
- `comparison_matrix`：多维评分对比矩阵
- `final_report`：LLM 生成的最终推荐、优缺点、风险应对和决策溯源

### `GET /api/styles`

返回内置架构风格知识库，包含 11 种架构风格。

### `GET /api/examples`

返回 20 条典型需求测试案例。

### `GET /api/course-knowledge`

返回从课程 PPT 提炼的课程知识库摘要，包括经典架构风格分类、质量属性、架构描述方法和 SAAM/ATAM 评估方法。评估 Agent 会引用这些摘要生成更贴合课程术语的推荐理由。

## 测试

```powershell
pytest
```

测试中会替换 Agent 的 LLM 调用，不需要真实 API Key。
