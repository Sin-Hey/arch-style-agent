# 软件架构风格智能助手

这是一个用于《软件体系结构》课程大作业演示的 Web 系统。系统通过 DeepSeek LLM、Agent 协作、架构风格知识库和规则引擎，把自然语言需求转换为可解释的架构推荐结果。

## 目录结构

```text
arch-style-agent/
├── backend/                 # 后端代码
│   ├── main.py              # 统一启动入口：backend.main:app
│   ├── app/                 # FastAPI 后端源码包
│   │   └── app/
│   │       ├── main.py
│   │       ├── agents/
│   │       ├── services/
│   │       ├── data/
│   │       └── schemas.py
│   └── tests/               # 后端测试
├── frontend/
│   └── static/
│       └── index.html       # 前端页面
├── requirements.txt
├── DESIGN.md
└── README.md
```

说明：`backend/main.py` 是为了让启动命令保持简单，内部会加载 `backend/app` 里的 FastAPI 应用。

## 从 GitHub 下载并启动

以下步骤以 Windows PowerShell 为例。

### 1. 克隆项目

```powershell
cd C:\Users\你的用户名
git clone https://github.com/Sin-Hey/arch-style-agent.git
cd arch-style-agent
```

确认当前目录里能看到：

```text
backend
frontend
README.md
requirements.txt
```

如果看不到 `requirements.txt`，说明你还没有进入项目根目录。

### 2. 创建虚拟环境

```powershell
python -m venv .venv
```

### 3. 安装依赖

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 4. 配置 DeepSeek API

```powershell
$env:DEEPSEEK_API_KEY="你的 DeepSeek API Key"
$env:DEEPSEEK_BASE_URL="https://api.deepseek.com"
$env:DEEPSEEK_MODEL="deepseek-chat"
```

不要把真实 API Key 发到群里、截图里或提交到 GitHub。

### 5. 启动服务

在项目根目录运行：

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8001
```

看到下面输出说明启动成功：

```text
Uvicorn running on http://127.0.0.1:8001
```

### 6. 打开页面

在浏览器地址栏访问：

```text
http://127.0.0.1:8001/
```

不要在 PowerShell、cmd 或 bash 里直接输入这个网址；那会被当成命令执行。

## 常用接口

- `GET /api/health`：健康检查
- `GET /api/styles`：查看架构风格知识库
- `GET /api/examples`：查看 20 条测试需求
- `GET /api/course-knowledge`：查看课程知识库摘要
- `GET /api/knowledge-graph`：查看轻量知识图谱节点和边
- `GET /api/cache/stats`：查看 LLM 缓存状态
- `POST /api/analyze`：需求解析
- `POST /api/recommend`：架构推荐

示例：

```powershell
curl http://127.0.0.1:8001/api/health
```

## 常见问题

### 点击“打开”打不开

通常是后端服务没有启动，或启动命令还是旧的 `app.main:app`。

现在请使用：

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8001
```

### 端口 8001 被占用

换一个端口：

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8002
```

然后浏览器访问：

```text
http://127.0.0.1:8002/
```

### 没有配置 API Key

如果 `/api/analyze` 或 `/api/recommend` 返回 503，并提示 `DEEPSEEK_API_KEY`，说明当前终端没有配置环境变量。重新执行：

```powershell
$env:DEEPSEEK_API_KEY="你的 DeepSeek API Key"
```

然后重启服务。

## 测试

```powershell
.\.venv\Scripts\python.exe -m pytest backend\tests
```

测试会替换 Agent 的 LLM 调用，不需要真实 API Key。
