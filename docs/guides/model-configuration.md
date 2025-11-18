# 模型配置指南

> **文档版本**: v2.0  
> **最后更新**: 2025-01-17  
> **预计阅读时间**: 15 分钟

本指南详细介绍如何为 MathModelAgent 配置和优化大型语言模型 (LLM)，以在不同任务中获得最佳性能和成本效益。

## 📋 核心概念

### 1. 多 Agent 独立配置

MathModelAgent 的核心优势之一是其多 Agent 系统，每个 Agent 都可以独立配置不同的 LLM。这允许您：

-   为不同任务选择最合适的模型。
-   在成本和性能之间取得平衡。
-   试验不同模型的组合。

### 2. Agent 职责与模型推荐

| Agent | 职责 | 推荐模型类型 | 示例模型 |
|---|---|---|---|
| **Coordinator** | 问题分析、任务拆解 | 快速、低成本 | `gpt-3.5-turbo`, `claude-3-haiku`, `gemini-1.5-flash` |
| **Modeler** | 数学建模、方案设计 | 强推理能力 | `gpt-4`, `claude-3-opus`, `deepseek-r1` |
| **Coder** | 代码实现、调试 | 强代码能力 | `gpt-4`, `deepseek-coder`, `claude-3-sonnet` |
| **Writer** | 论文撰写、润色 | 强语言能力 | `gpt-4`, `claude-3-opus`, `gemini-1.5-pro` |

### 3. LiteLLM 集成

系统通过 [LiteLLM](https://docs.litellm.ai/docs/providers) 实现了对几乎所有主流 LLM 提供商的兼容。您需要遵循 LiteLLM 的模型 ID 格式。

**模型 ID 格式**: `provider/model_name`

-   **OpenAI**: `gpt-4-turbo` (provider `openai` 是默认值，可以省略)
-   **Anthropic**: `claude-3-opus-20240229`
-   **DeepSeek**: `deepseek/deepseek-chat`
-   **Google**: `gemini/gemini-1.5-pro`

## ⚙️ 配置方法

### 方法一：通过 Web 界面配置（推荐）

这是最简单、最直观的方式。

1.  打开前端界面，点击左侧边栏的 **头像图标** -> **"API 配置"**。
2.  为每个 Agent 填写以下信息：
    -   `API Key`: 您的 LLM 提供商的 API 密钥。
    -   `Model ID`: 您要使用的模型 ID。
    -   `Base URL`: API 的基础 URL。
3.  点击 **"验证"** 按钮测试连接。
4.  验证成功后，点击 **"保存配置"**。

![API 配置界面](../images/api-config-ui.png)  
*（请在此处添加 API 配置界面的截图）*

### 方法二：通过环境变量配置

直接编辑 `backend/.env.dev` 文件。此方法适合自动化部署或没有 Web 界面的环境。

```bash
# backend/.env.dev

# 为 Coordinator Agent 配置便宜快速的模型
COORDINATOR_API_KEY=sk-xxx
COORDINATOR_MODEL=gpt-3.5-turbo
COORDINATOR_BASE_URL=https://api.openai.com/v1

# 为 Modeler Agent 配置强推理模型
MODELER_API_KEY=sk-yyy
MODELER_MODEL=claude-3-opus-20240229
MODELER_BASE_URL=https://api.anthropic.com/v1

# 为 Coder Agent 配置代码专用模型
CODER_API_KEY=sk-zzz
CODER_MODEL=deepseek/deepseek-coder
CODER_BASE_URL=https://api.deepseek.com/v1

# 为 Writer Agent 配置强写作模型
WRITER_API_KEY=sk-aaa
WRITER_MODEL=gpt-4-turbo
WRITER_BASE_URL=https://api.openai.com/v1
```

### 方法三：通过模型配置文件

编辑 `backend/app/config/model_config.toml` 文件，可以预设多套配置方案，方便快速切换。

```toml
# backend/app/config/model_config.toml

# 配置方案一：高性价比
[config1]
COORDINATOR_MODEL='gpt-3.5-turbo'
MODELER_MODEL='claude-3-sonnet-20240229'
CODER_MODEL='deepseek/deepseek-coder'
WRITER_MODEL='claude-3-sonnet-20240229'

# 配置方案二：极致性能
[config2]
COORDINATOR_MODEL='claude-3-haiku-20240307'
MODELER_MODEL='claude-3-opus-20240229'
CODER_MODEL='gpt-4-turbo'
WRITER_MODEL='gpt-4-turbo'

# 指定当前使用的配置方案
[current]
current = 'config1'
```

**优先级说明**: Web 界面配置 > 环境变量配置 > `model_config.toml` 文件配置。

## 💡 最佳实践与策略

### 1. 成本效益策略

-   **Coordinator**: 使用最便宜、最快的模型，如 `gpt-3.5-turbo` 或 `claude-3-haiku`。
-   **Modeler & Writer**: 使用中档模型，如 `claude-3-sonnet` 或 `gemini-1.5-pro`。
-   **Coder**: 使用代码能力强的免费或低成本模型，如 `deepseek/deepseek-coder`。

### 2. 性能优先策略

-   **Coordinator**: 仍然可以使用快速模型，或使用中档模型以获得更精确的任务拆解。
-   **Modeler, Coder, Writer**: 使用当前最强大的模型，如 `gpt-4-turbo` 或 `claude-3-opus`。

### 3. 使用 API 中转服务

如果您的网络环境无法直接访问 LLM 提供商，或者希望统一管理 API Keys，可以使用 API 中转服务。

**配置示例**:
```bash
# backend/.env.dev

# 所有 Agent 使用同一个中转 Key 和 URL
COORDINATOR_API_KEY=sk-proxy-key
COORDINATOR_MODEL=gpt-4-turbo
COORDINATOR_BASE_URL=https://your.proxy.com/v1

MODELER_API_KEY=sk-proxy-key
MODELER_MODEL=claude-3-opus-20240229
MODELER_BASE_URL=https://your.proxy.com/v1

# ... 其他 Agent
```

**注意**: 即使使用中转，`Model ID` 仍需遵循 LiteLLM 格式，以便系统正确构建请求。

## ❓ 常见问题

### Q: 我可以将所有 Agent 都配置成同一个模型吗？

**A**: 可以。您可以在 Web 界面或 `.env.dev` 文件中为所有 Agent 填写相同的 `API Key`, `Model ID` 和 `Base URL`。但这会失去多 Agent 独立配置的优势。

### Q: 如何知道一个模型是否被支持？

**A**: 请查阅 [LiteLLM 的官方文档](https://docs.litellm.ai/docs/providers)。只要 LiteLLM 支持，MathModelAgent 就支持。

### Q: 模型验证失败，提示 "401 Unauthorized"？

**A**: 这通常意味着您的 API Key 有问题。请检查：
    1.  API Key 是否正确复制。
    2.  您的账户是否还有足够余额。
    3.  API Key 是否已过期或被禁用。

### Q: 模型验证失败，提示 "404 Not Found"？

**A**: 这通常意味着 `Model ID` 或 `Base URL` 不正确。
    1.  检查 `Model ID` 是否拼写正确，并符合 LiteLLM 格式。
    2.  确认 `Base URL` 是正确的 API 端点。

### Q: 我可以添加不在 LiteLLM 列表中的自定义模型吗？

**A**: 可以，前提是该模型提供了与 OpenAI 兼容的 API 接口。您只需正确填写 `Model ID` 和 `Base URL` 即可。

## 📚 相关文档

-   [基础配置指南](../getting-started/basic-configuration.md)
-   [环境变量参考](../reference/environment-variables.md)
-   [自定义提示词](custom-prompts.md)
-   [常见问题 - 配置问题](../faq/configuration.md)

---

**上一页**: [文件上传指南](file-upload.md)  
**下一页**: [自定义提示词](custom-prompts.md)
