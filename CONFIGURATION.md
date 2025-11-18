# Configuration Guide

本文档详细说明 MathModelAgent 的所有配置文件和环境变量。

## 目录

- [环境变量配置](#环境变量配置)
- [模型配置](#模型配置)
- [提示词模板配置](#提示词模板配置)
- [Docker 配置](#docker-配置)
- [前端配置](#前端配置)
- [Redis 配置](#redis-配置)
- [搜索引擎配置](#搜索引擎配置)

---

## 环境变量配置

### 后端环境变量 (`backend/.env.dev`)

```bash
# 环境标识
ENV=dev

# ============ Coordinator Agent 配置 ============
# 协调 Agent 负责分析问题结构和拆解子问题
COORDINATOR_API_KEY=sk-xxx
COORDINATOR_MODEL=gpt-4
COORDINATOR_BASE_URL=https://api.openai.com/v1

# ============ Modeler Agent 配置 ============
# 建模 Agent 负责创建数学模型（推荐使用 thinking model）
MODELER_API_KEY=sk-xxx
MODELER_MODEL=gpt-4
MODELER_BASE_URL=https://api.openai.com/v1

# ============ Coder Agent 配置 ============
# 编码 Agent 负责实现代码和调试
CODER_API_KEY=sk-xxx
CODER_MODEL=gpt-4
CODER_BASE_URL=https://api.openai.com/v1

# ============ Writer Agent 配置 ============
# 写作 Agent 负责生成论文
WRITER_API_KEY=sk-xxx
WRITER_MODEL=gpt-4
WRITER_BASE_URL=https://api.openai.com/v1

# ============ 工作流配置 ============
# 模型最大问答次数
MAX_CHAT_TURNS=70

# 代码执行失败后的最大重试次数
MAX_RETRIES=5

# ============ 代码解释器配置 ============
# E2B API Key（可选，留空则使用本地 Jupyter）
E2B_API_KEY=

# ============ 学术搜索配置 ============
# OpenAlex Email（用于文献搜索，提高 API 速率限制）
OPENALEX_EMAIL=your-email@example.com

# ============ Web 搜索配置 ============
# Tavily API Key（可选）
TAVILY_API_KEY=tvly-xxx

# Exa API Key（可选）
EXA_API_KEY=exa-xxx

# 默认搜索提供商 (tavily | exa)
SEARCH_DEFAULT_PROVIDER=tavily

# 搜索结果数量
SEARCH_MAX_RESULTS=10

# 搜索超时时间（秒）
SEARCH_TIMEOUT=30

# 是否启用搜索提供商降级
SEARCH_ENABLE_FALLBACK=true

# 降级搜索提供商列表（逗号分隔）
SEARCH_FALLBACK_PROVIDERS=exa

# ============ 系统配置 ============
# 日志级别 (DEBUG | INFO | WARNING | ERROR | CRITICAL)
LOG_LEVEL=DEBUG

# 调试模式
DEBUG=true

# 服务器地址
SERVER_HOST=http://localhost:8000

# ============ Redis 配置 ============
# Redis 连接 URL
# Docker 部署: redis://redis:6379/0
# 本地部署: redis://localhost:6379/0
# 带密码: redis://:password@localhost:6379/0
REDIS_URL=redis://localhost:6379/0

# Redis 最大连接数
REDIS_MAX_CONNECTIONS=20

# ============ CORS 配置 ============
# 允许的跨域来源（逗号分隔）
CORS_ALLOW_ORIGINS=http://localhost:5173,http://localhost:3000
```

### 环境变量说明

#### Agent 配置

每个 Agent 都有三个配置项：

1. **API_KEY**: LLM 提供商的 API 密钥
2. **MODEL**: 模型 ID（遵循 LiteLLM 格式）
3. **BASE_URL**: API 基础 URL（OpenAI 兼容端点）

**模型 ID 格式示例**:

- OpenAI: `gpt-4`, `gpt-4-turbo`, `gpt-3.5-turbo`
- Anthropic: `claude-3-opus-20240229`, `claude-3-sonnet-20240229`
- DeepSeek: `deepseek/deepseek-chat`, `deepseek/deepseek-coder`
- 自定义: `openai/custom-model-name`

**推荐配置**:

- **Coordinator**: 使用快速、便宜的模型（如 GPT-3.5）
- **Modeler**: 使用强大的推理模型（如 GPT-4, Claude-3-Opus, DeepSeek-R1）
- **Coder**: 使用代码能力强的模型（如 GPT-4, DeepSeek-Coder）
- **Writer**: 使用写作能力强的模型（如 GPT-4, Claude-3）

#### Redis 配置

Redis 是必需的依赖，用于：

- 任务状态管理
- WebSocket 消息发布/订阅
- 任务队列

**本地开发**:

```bash
# 无密码
REDIS_URL=redis://localhost:6379/0

# 有密码
REDIS_URL=redis://:your_password@localhost:6379/0
```

**Docker 部署**:

```bash
REDIS_URL=redis://redis:6379/0
```

#### 搜索引擎配置

系统支持两种 Web 搜索提供商：

1. **Tavily** (推荐)
   - 注册: <https://tavily.com/>
   - 免费额度: 1000 次/月
   - 特点: 快速、准确、支持深度搜索

2. **Exa**
   - 注册: <https://exa.ai/>
   - 特点: 语义搜索、内容提取、相似页面查找

---

## 模型配置

### 模型配置文件 (`backend/app/config/model_config.toml`)

```toml
[config1]
COORDINATOR_API_KEY=''
COORDINATOR_MODEL=''
COORDINATOR_BASE_URL=''

MODELER_API_KEY=''
MODELER_MODEL=''
MODELER_BASE_URL=''

CODER_API_KEY=''
CODER_MODEL=''
CODER_BASE_URL=''

WRITER_API_KEY=''
WRITER_MODEL=''
WRITER_BASE_URL=''

[config2]
# 可以配置多套模型配置，方便切换

[current]
current = 'config1'  # 指定当前使用的配置
```

**使用场景**:

- 为不同的竞赛模板配置不同的模型
- 在开发和生产环境使用不同的模型
- 快速切换模型进行测试

---

## 提示词模板配置

### 中文模板 (`backend/app/config/md_template.toml`)

```toml
[coordinator]
system = """你是一个数学建模问题分析专家..."""
user = """请分析以下数学建模问题：
{ques_all}

请识别：
1. 主要问题和子问题
2. 每个问题的类型
3. 需要的数据和约束条件
"""

[modeler]
system = """你是一个数学建模专家..."""
user = """基于以下问题分析，请建立数学模型：
{problem_analysis}

请提供：
1. 问题假设
2. 符号定义
3. 数学模型
4. 求解方法
"""

[coder]
system = """你是一个Python编程专家..."""
user = """请实现以下数学模型：
{model_description}

要求：
1. 使用Python实现
2. 包含完整的数据处理
3. 生成可视化结果
4. 添加详细注释
"""

[writer]
system = """你是一个学术论文写作专家..."""

[writer.摘要]
user = """基于以下建模结果，撰写论文摘要：
{modeling_results}

要求：
1. 200-300字
2. 包含问题、方法、结果
3. 突出创新点
"""

[writer.问题重述]
user = """..."""

[writer.问题分析]
user = """..."""

# ... 更多章节
```

### 英文模板 (`backend/app/config/md_template_en.toml`)

结构与中文模板相同，但使用英文提示词。

### 自定义提示词

**修改步骤**:

1. 复制现有模板文件
2. 修改 `system` 和 `user` 字段
3. 使用 `{变量名}` 占位符插入动态内容
4. 保存文件并重启后端

**可用占位符**:

- `{ques_all}`: 完整问题描述
- `{problem_analysis}`: 问题分析结果
- `{model_description}`: 模型描述
- `{code_results}`: 代码执行结果
- `{modeling_results}`: 建模结果
- `{references}`: 文献引用

---

## Docker 配置

### Docker Compose (`docker-compose.yml`)

```yaml
services:
  redis:
    image: redis:alpine
    container_name: mathmodelagent_redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: mathmodelagent_backend
    ports:
      - "8000:8000"
    env_file:
      - ./backend/.env.dev
    environment:
      - ENV=DEV
    volumes:
      - ./backend:/app
      - ./backend/project/work_dir:/app/project/work_dir
      - backend_venv:/app/.venv
    depends_on:
      - redis

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: mathmodelagent_frontend
    ports:
      - "5173:5173"
    env_file:
      - ./frontend/.env.development
    volumes:
      - ./frontend:/app
      - /app/node_modules
    depends_on:
      - backend

volumes:
  redis_data:
  backend_venv:
```

**配置说明**:

- **端口映射**: 可修改主机端口（冒号左侧）
- **卷挂载**: 实现代码热重载和数据持久化
- **依赖关系**: 确保服务按正确顺序启动

---

## 前端配置

### 开发环境 (`frontend/.env.development`)

```bash
# API 基础 URL
VITE_API_BASE_URL=http://localhost:8000

# WebSocket URL
VITE_WS_BASE_URL=ws://localhost:8000

# 应用标题
VITE_APP_TITLE=MathModelAgent

# 是否启用调试模式
VITE_DEBUG=true
```

### 生产环境 (`frontend/.env.production`)

```bash
VITE_API_BASE_URL=https://your-domain.com/api
VITE_WS_BASE_URL=wss://your-domain.com/ws
VITE_APP_TITLE=MathModelAgent
VITE_DEBUG=false
```

---

## Redis 配置

### 本地 Redis 安装

**Windows**:

```powershell
# 使用 Chocolatey
choco install redis-64

# 或下载 MSI 安装包
# https://github.com/microsoftarchive/redis/releases
```

**macOS**:

```bash
brew install redis
brew services start redis
```

**Linux**:

```bash
sudo apt-get install redis-server
sudo systemctl start redis
```

### Redis 配置文件 (可选)

如需自定义 Redis 配置，创建 `redis.conf`:

```conf
# 绑定地址
bind 127.0.0.1

# 端口
port 6379

# 密码（可选）
requirepass your_password

# 最大内存
maxmemory 256mb

# 内存淘汰策略
maxmemory-policy allkeys-lru

# 持久化
save 900 1
save 300 10
save 60 10000
```

---

## 搜索引擎配置

### Tavily 配置

1. 注册账号: <https://tavily.com/>
2. 获取 API Key
3. 配置环境变量:

```bash
TAVILY_API_KEY=tvly-xxx
SEARCH_DEFAULT_PROVIDER=tavily
```

### Exa 配置

1. 注册账号: <https://exa.ai/>
2. 获取 API Key
3. 配置环境变量:

```bash
EXA_API_KEY=exa-xxx
SEARCH_DEFAULT_PROVIDER=exa
```

### 搜索降级配置

当主搜索提供商失败时，自动切换到备用提供商：

```bash
SEARCH_ENABLE_FALLBACK=true
SEARCH_FALLBACK_PROVIDERS=exa,tavily
```

---

## 配置验证

### 验证后端配置

```bash
cd backend
python -c "from app.config.setting import settings; print(settings)"
```

### 验证 Redis 连接

```bash
redis-cli ping
# 应返回: PONG
```

### 验证 API Key

使用前端界面的 "设置" -> "API 配置" 页面验证各个 Agent 的 API Key。

---

## 常见配置问题

### 1. Redis 连接失败

**错误**: `ConnectionRefusedError: [Errno 111] Connection refused`

**解决方案**:

- 确保 Redis 服务已启动
- 检查 `REDIS_URL` 配置是否正确
- 检查防火墙设置

### 2. LLM API 调用失败

**错误**: `401 Unauthorized` 或 `403 Forbidden`

**解决方案**:

- 验证 API Key 是否正确
- 检查 API 账户余额
- 确认 Base URL 配置正确

### 3. 文件上传失败

**错误**: `413 Request Entity Too Large`

**解决方案**:

- 检查文件大小限制（默认 100MB）
- 修改 `backend/app/routers/files_router.py` 中的 `MAX_FILE_SIZE`

### 4. WebSocket 连接失败

**错误**: `WebSocket connection failed`

**解决方案**:

- 检查防火墙是否阻止 WebSocket 连接
- 确认后端 WebSocket 路由正常工作
- 检查 CORS 配置

---

## 更多信息

- [API Reference](API_REFERENCE.md)
- [Architecture](ARCHITECTURE.md)
- [Development Guide](CLAUDE.md)
