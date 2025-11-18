# 参考 - 环境变量

> **文档版本**: v2.0  
> **最后更新**: 2025-01-17

本指南详细列出了 MathModelAgent 使用的所有环境变量及其说明。这些变量在 `backend/.env.dev` 文件中配置。

## 📋 目录

-   [Agent 配置](#-agent-配置)
-   [工作流配置](#-工作流配置)
-   [代码解释器配置](#-代码解释器配置)
-   [学术与 Web 搜索配置](#-学术与-web-搜索配置)
-   [系统与服务配置](#-系统与服务配置)

---

## 🤖 Agent 配置

每个 Agent（Coordinator, Modeler, Coder, Writer）都有自己独立的一套配置，允许您为不同任务选择最优模型。

### Coordinator Agent

-   `COORDINATOR_API_KEY`: Coordinator Agent 使用的 LLM API Key。
-   `COORDINATOR_MODEL`: Coordinator Agent 使用的模型 ID (例如, `gpt-3.5-turbo`)。
-   `COORDINATOR_BASE_URL`: API 的基础 URL (例如, `https://api.openai.com/v1`)。

### Modeler Agent

-   `MODELER_API_KEY`: Modeler Agent 使用的 LLM API Key。
-   `MODELER_MODEL`: Modeler Agent 使用的模型 ID (例如, `gpt-4-turbo`)。
-   `MODELER_BASE_URL`: API 的基础 URL。

### Coder Agent

-   `CODER_API_KEY`: Coder Agent 使用的 LLM API Key。
-   `CODER_MODEL`: Coder Agent 使用的模型 ID (例如, `deepseek/deepseek-coder`)。
-   `CODER_BASE_URL`: API 的基础 URL。

### Writer Agent

-   `WRITER_API_KEY`: Writer Agent 使用的 LLM API Key。
-   `WRITER_MODEL`: Writer Agent 使用的模型 ID (例如, `claude-3-opus-20240229`)。
-   `WRITER_BASE_URL`: API 的基础 URL。

---

## ⚙️ 工作流配置

-   `MAX_CHAT_TURNS`
    -   **描述**: 单个 Agent 在一次执行中所允许的最大对话轮次。
    -   **默认值**: `70`
    -   **说明**: 用于防止 Agent 陷入无限循环，或产生过高的费用。

-   `MAX_RETRIES`
    -   **描述**: 当 CoderAgent 执行代码失败时，允许的最大自动重试次数。
    -   **默认值**: `5`
    -   **说明**: 每次重试，CoderAgent 都会分析错误并尝试修复代码。

---

## 💻 代码解释器配置

-   `E2B_API_KEY`
    -   **描述**: [E2B.dev](https://e2b.dev/) 的 API Key，用于启用云端沙箱代码执行环境。
    -   **默认值**: `(空)`
    -   **说明**: 如果此项留空，系统将默认使用本地的 Jupyter 内核执行代码。如果填写了有效的 Key，则会优先使用 E2B 云端解释器。

---

## 🔍 学术与 Web 搜索配置

### 学术搜索

-   `OPENALEX_EMAIL`
    -   **描述**: 用于访问 [OpenAlex](https://openalex.org/) 学术文献 API 的 Email 地址。
    -   **默认值**: `(空)`
    -   **说明**: 提供 Email 可以获得更高的 API 请求速率限制，从而获得更稳定、更快速的文献检索服务。

### Web 搜索

-   `TAVILY_API_KEY`
    -   **描述**: [Tavily AI](https://tavily.com/) 的 API Key。
    -   **默认值**: `(空)`

-   `EXA_API_KEY`
    -   **描述**: [Exa AI](https://exa.ai/) 的 API Key。
    -   **默认值**: `(空)`

-   `SEARCH_DEFAULT_PROVIDER`
    -   **描述**: 指定默认使用的搜索引擎。
    -   **默认值**: `tavily`
    -   **可选值**: `tavily`, `exa`

-   `SEARCH_MAX_RESULTS`
    -   **描述**: 单次搜索返回的最大结果数量。
    -   **默认值**: `10`

-   `SEARCH_TIMEOUT`
    -   **描述**: 搜索请求的超时时间（秒）。
    -   **默认值**: `30`

-   `SEARCH_ENABLE_FALLBACK`
    -   **描述**: 当默认搜索引擎失败时，是否自动尝试使用备用搜索引擎。
    -   **默认值**: `true`

-   `SEARCH_FALLBACK_PROVIDERS`
    -   **描述**: 备用搜索引擎的列表，按尝试顺序排列，用逗号分隔。
    -   **默认值**: `exa`
    -   **示例**: `exa,another_provider`

---

## 🛠️ 系统与服务配置

### 系统

-   `ENV`
    -   **描述**: 设置运行环境。
    -   **默认值**: `dev`
    -   **说明**: 主要用于加载不同环境的配置文件，例如 `.env.dev`。

-   `LOG_LEVEL`
    -   **描述**: 应用程序的日志记录级别。
    -   **默认值**: `DEBUG`
    -   **可选值**: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`

-   `DEBUG`
    -   **描述**: 是否启用调试模式。
    -   **默认值**: `true`
    -   **说明**: 在调试模式下，日志会更详细，FastAPI 会提供更丰富的错误信息。

-   `SERVER_HOST`
    -   **描述**: 后端服务器的主机地址。
    -   **默认值**: `http://localhost:8000`
    -   **说明**: 用于生成静态文件的绝对 URL。

### 服务

-   `REDIS_URL`
    -   **描述**: Redis 服务的连接 URL。
    -   **默认值**: `redis://localhost:6379/0`
    -   **说明**: **此项为必需配置**。用于任务队列、状态管理和 WebSocket 消息。
    -   **Docker 示例**: `redis://redis:6379/0`
    -   **带密码示例**: `redis://:your_password@localhost:6379/0`

-   `REDIS_MAX_CONNECTIONS`
    -   **描述**: Redis 连接池的最大连接数。
    -   **默认值**: `20`

-   `CORS_ALLOW_ORIGINS`
    -   **描述**: 允许跨域请求的前端来源地址，用逗号分隔。
    -   **默认值**: `http://localhost:5173,http://localhost:3000`
    -   **说明**: 设为 `*` 将允许所有来源，但这在生产环境中不安全。

## 📚 相关文档

-   [指南 - 基础配置](../getting-started/basic-configuration.md)
-   [指南 - 模型配置](../guides/model-configuration.md)

---

**上一页**: [文档首页](../README.md)  
**下一页**: [模型配置文件](model-config.md)
