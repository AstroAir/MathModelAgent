# 参考 - 模型配置文件

> **文档版本**: v2.0  
> **最后更新**: 2025-01-17

本指南详细说明 `backend/app/config/model_config.toml` 文件的作用和配置方法。该文件允许您预设多套模型组合，并方便地在它们之间切换。

## 📋 核心功能

-   **多方案预设**: 您可以定义多套不同的模型配置方案（例如，`[config1]`, `[config2]`）。
-   **快速切换**: 只需修改 `[current]` 部分的 `current` 值，即可在不同方案间切换，无需修改环境变量。
-   **配置覆盖**: 此文件中的配置优先级低于环境变量。如果设置了环境变量（例如 `COORDINATOR_MODEL`），则会覆盖此文件中的同名配置。

## 📁 文件结构

文件位于 `backend/app/config/model_config.toml`，采用 TOML 格式。

```toml
# 方案一：高性价比组合
[config1]
# 如果某个 Agent 的配置留空，则会使用环境变量中的值
COORDINATOR_API_KEY=''
COORDINATOR_MODEL='gpt-3.5-turbo'
COORDINATOR_BASE_URL=''

MODELER_API_KEY=''
MODELER_MODEL='claude-3-sonnet-20240229'
MODELER_BASE_URL=''

CODER_API_KEY=''
CODER_MODEL='deepseek/deepseek-coder'
CODER_BASE_URL=''

WRITER_API_KEY=''
WRITER_MODEL='claude-3-sonnet-20240229'
WRITER_BASE_URL=''


# 方案二：极致性能组合
[config2]
COORDINATOR_API_KEY=''
COORDINATOR_MODEL='claude-3-haiku-20240307'
COORDINATOR_BASE_URL=''

MODELER_API_KEY=''
MODELER_MODEL='claude-3-opus-20240229'
MODELER_BASE_URL=''

CODER_API_KEY=''
CODER_MODEL='gpt-4-turbo'
CODER_BASE_URL=''

WRITER_API_KEY=''
WRITER_MODEL='gpt-4-turbo'
WRITER_BASE_URL=''


# 当前使用的配置方案
[current]
current = 'config1' # 将这里的值改为 'config2' 即可切换到方案二
```

## ⚙️ 配置说明

### 配置区块

-   每个 `[configN]` 区块代表一套独立的模型配置方案。
-   您可以根据需要添加任意数量的配置方案，例如 `[config3]`, `[my_test_config]` 等。

### Agent 配置项

在每个配置区块内，您可以为四个 Agent（Coordinator, Modeler, Coder, Writer）分别设置模型。

-   `*_API_KEY`: 该 Agent 使用的 API Key。
-   `*_MODEL`: 该 Agent 使用的模型 ID。
-   `*_BASE_URL`: 该 Agent 使用的 API Base URL。

**重要**: 如果这些值留空（例如 `COORDINATOR_API_KEY=''`），系统将自动回退到使用 `backend/.env.dev` 文件中相应的环境变量。这允许您在环境变量中设置一个全局的 API Key，而在 `model_config.toml` 中只定义模型 ID。

### 当前方案切换

-   `[current]` 区块下的 `current` 变量决定了当前系统使用的是哪一套配置方案。
-   要切换方案，只需将 `current` 的值修改为您想要使用的配置区块的名称（例如，`current = 'config2'`）。
-   修改后需要重启后端服务才能生效。

## 🚀 使用场景

### 1. 竞赛模式切换

您可以为不同类型的数学建模竞赛预设不同的模型组合。

```toml
[guo_sai_config] # 国赛配置：使用对中文支持更好的模型
MODELER_MODEL = 'deepseek/deepseek-chat'
...

[mei_sai_config] # 美赛配置：使用英文能力强的模型
MODELER_MODEL = 'claude-3-opus-20240229'
...

[current]
current = 'guo_sai_config'
```

### 2. 成本与性能切换

根据任务的重要性和预算，快速在“经济模式”和“性能模式”之间切换。

```toml
[economic_mode]
MODELER_MODEL = 'gpt-3.5-turbo'
...

[performance_mode]
MODELER_MODEL = 'gpt-4-turbo'
...

[current]
current = 'economic_mode'
```

### 3. 模型测试

方便地测试不同模型组合的效果，而无需频繁修改环境变量。

```toml
[test_claude_opus]
MODELER_MODEL = 'claude-3-opus-20240229'
...

[test_gemini_pro]
MODELER_MODEL = 'gemini/gemini-1.5-pro'
...

[current]
current = 'test_claude_opus'
```

## 💡 最佳实践

-   **全局 Key, 局部 Model**: 在 `.env.dev` 中设置通用的 `API_KEY` 和 `BASE_URL`，而在 `model_config.toml` 中只覆写 `*_MODEL` 字段。这样可以避免在多个地方重复填写敏感信息。
-   **清晰命名**: 为您的配置方案取一个有描述性的名称，如 `cost_saving`, `high_performance`, `debug_test`。
-   **备份**: 在修改此文件前，最好先创建一个备份。

## 📚 相关文档

-   [参考 - 环境变量](environment-variables.md)
-   [指南 - 模型配置](../guides/model-configuration.md)

---

**上一页**: [环境变量](environment-variables.md)  
**下一页**: [提示词模板](prompt-templates.md)
