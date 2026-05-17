# 软件架构风格智能助手

这是一个用于《软件体系结构》课程大作业演示的 Web API 系统。核心能力包括：需求解析、架构风格推荐、规则评分、LLM 评估报告、对比矩阵、Mermaid 拓扑图、轻量知识图谱、LLM 调用缓存、组合架构推荐和架构重构建议。

## 从 GitHub 下载并启动

以下步骤以 Windows PowerShell 为例。

### 1. 克隆项目

```powershell
cd C:\Users\你的用户名
git clone https://github.com/Sin-Hey/arch-style-agent.git
cd arch-style-agent
```

进入项目目录后，执行：

```powershell
dir
```

应该能看到：

```text
app
static
tests
README.md
requirements.txt
```

如果看不到 `requirements.txt`，说明当前不在项目根目录，需要先 `cd` 到 `arch-style-agent` 文件夹。

### 2. 创建虚拟环境

```powershell
python -m venv .venv
```

### 3. 安装依赖

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

不要在 `C:\Users\你的用户名>` 这种用户根目录直接执行安装命令，必须先进入项目目录，否则会报：

```text
ERROR: Could not open requirements file: [Errno 2] No such file or directory: 'requirements.txt'
```

### 4. 配置 DeepSeek API

```powershell
$env:DEEPSEEK_API_KEY="你的 DeepSeek API Key"
$env:DEEPSEEK_BASE_URL="https://api.deepseek.com"
$env:DEEPSEEK_MODEL="deepseek-chat"
```

注意：不要把真实 API Key 发到群里、截图里或提交到 GitHub。

### 5. 启动服务

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8001
```

看到类似输出说明启动成功：

```text
Uvicorn running on http://127.0.0.1:8001
```

### 6. 打开网页

在浏览器地址栏访问：

```text
http://127.0.0.1:8001/
```

不要在 PowerShell、cmd 或 bash 里直接输入 `http://127.0.0.1:8001/`，那会被当成命令执行。终端测试接口可以用：

```powershell
curl http://127.0.0.1:8001/api/health
```

## 常见问题

### 端口 8001 被占用

换一个端口启动，例如：

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8002
```

浏览器对应访问：

```text
http://127.0.0.1:8002/
```

### 提示没有配置 API Key

如果 `/api/analyze` 或 `/api/recommend` 返回 503，并提示 `DEEPSEEK_API_KEY is not set`，说明当前终端没有配置环境变量。重新执行：

```powershell
$env:DEEPSEEK_API_KEY="你的 DeepSeek API Key"
```

然后重启 uvicorn。

### WSL 或 Linux 终端访问

如果在 WSL/bash 里测试，不要直接输入网址。使用：

```bash
curl http://127.0.0.1:8001/api/health
```

网页仍然用浏览器打开：

```text
http://127.0.0.1:8001/
```

## API 接口

### `GET /api/health`

健康检查。

### `POST /api/analyze`

输入自然语言需求，返回结构化需求特征。

请求示例：

```json
{
  "requirement": "开发一个跨平台即时通讯系统，要求支持万人同时在线，需要保证消息实时性和可靠性，后期可能扩展视频通话功能。"
}
```

### `POST /api/recommend`

输入自然语言需求，返回架构推荐结果，包括：

- `features`：需求特征
- `candidates`：Top 3 候选架构
- `comparison_matrix`：多维评分对比矩阵
- `final_report`：最终推荐、优缺点、风险应对、决策溯源、组合架构方案、质量属性权衡、重构建议

### `GET /api/styles`

返回内置架构风格知识库，包含 11 种架构风格。

### `GET /api/examples`

返回 20 条典型测试需求案例。

### `GET /api/course-knowledge`

返回课程 PPT 摘要知识库。

### `GET /api/knowledge-graph`

返回轻量知识图谱节点和边。

### `GET /api/cache/stats`

返回 LLM 缓存状态。

## 测试

安装测试依赖后运行：

```powershell
.\.venv\Scripts\python.exe -m pytest
```

测试中会替换 Agent 的 LLM 调用，不需要真实 API Key。
