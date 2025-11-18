# 基础配置指南

> **文档版本**: v2.0  
> **最后更新**: 2025-01-17  
> **预计时间**: 10 分钟

本指南将帮助您完成 MathModelAgent 的基础配置，让系统能够正常运行。

## 📋 配置清单

- [ ] 配置至少一个 Agent 的 API Key
- [ ] 验证 API Key 有效性
- [ ] 配置 OpenAlex Email（可选）
- [ ] 配置搜索引擎 API（可选）
- [ ] 测试系统连接

## 🔑 配置 LLM API Keys

MathModelAgent 使用 4 个 Agent，每个 Agent 可以配置不同的模型。

### 方式一：通过 Web 界面配置（推荐）

1. 打开前端界面：http://localhost:5173
2. 点击左侧边栏的 **头像图标**
3. 选择 **"API 配置"**
4. 填写各个 Agent 的配置

#### Coordinator Agent（协调器）

```
API Key: sk-your-api-key
Model ID: gpt-3.5-turbo
Base URL: https://api.openai.com/v1
```

**推荐模型**: 快速、便宜的模型
- `gpt-3.5-turbo`
- `claude-3-haiku-20240307`
- `gemini/gemini-1.5-flash`

#### Modeler Agent（建模器）

```
API Key: sk-your-api-key
Model ID: gpt-4
Base URL: https://api.openai.com/v1
```

**推荐模型**: 强推理能力的模型
- `gpt-4`
- `claude-3-opus-20240229`
- `deepseek/deepseek-chat`
- `deepseek/deepseek-r1`（推理模型）

#### Coder Agent（编码器）

```
API Key: sk-your-api-key
Model ID: gpt-4
Base URL: https://api.openai.com/v1
```

**推荐模型**: 代码能力强的模型
- `gpt-4`
- `deepseek/deepseek-coder`
- `claude-3-sonnet-20240229`

#### Writer Agent（写作器）

```
API Key: sk-your-api-key
Model ID: gpt-4
Base URL: https://api.openai.com/v1
```

**推荐模型**: 写作能力强的模型
- `gpt-4`
- `claude-3-opus-20240229`
- `claude-3-sonnet-20240229`

### 方式二：通过配置文件配置

编辑 `backend/.env.dev` 文件：

```bash
# Coordinator Agent
COORDINATOR_API_KEY=sk-your-api-key
COORDINATOR_MODEL=gpt-3.5-turbo
COORDINATOR_BASE_URL=https://api.openai.com/v1

# Modeler Agent
MODELER_API_KEY=sk-your-api-key
MODELER_MODEL=gpt-4
MODELER_BASE_URL=https://api.openai.com/v1

# Coder Agent
CODER_API_KEY=sk-your-api-key
CODER_MODEL=gpt-4
CODER_BASE_URL=https://api.openai.com/v1

# Writer Agent
WRITER_API_KEY=sk-your-api-key
WRITER_MODEL=gpt-4
WRITER_BASE_URL=https://api.openai.com/v1
```

## 🌐 模型 ID 格式说明

MathModelAgent 使用 [LiteLLM](https://docs.litellm.ai/docs/providers) 支持多种模型提供商。

### OpenAI
```bash
MODEL=gpt-4
MODEL=gpt-4-turbo
MODEL=gpt-3.5-turbo
```

### Anthropic Claude
```bash
MODEL=claude-3-opus-20240229
MODEL=claude-3-sonnet-20240229
MODEL=claude-3-haiku-20240307
```

### DeepSeek
```bash
MODEL=deepseek/deepseek-chat
MODEL=deepseek/deepseek-coder
MODEL=deepseek/deepseek-r1
```

### Google Gemini
```bash
MODEL=gemini/gemini-1.5-pro
MODEL=gemini/gemini-1.5-flash
```

### 自定义 Base URL

如果使用 API 中转服务或自部署模型：

```bash
COORDINATOR_API_KEY=your-api-key
COORDINATOR_MODEL=openai/custom-model-name
COORDINATOR_BASE_URL=https://your-api-endpoint.com/v1
```

**注意**: 使用中转时，模型 ID 仍需要 `provider/model` 格式。

## ✅ 验证 API Key

### 通过 Web 界面验证

1. 在 API 配置页面填写信息
2. 点击 **"验证"** 按钮
3. 等待验证结果
   - ✓ 绿色勾号：验证成功
   - ✗ 红色叉号：验证失败

### 通过命令行验证

```bash
# 进入 backend 目录
cd backend

# 激活虚拟环境
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate.bat  # Windows

# 运行验证脚本
python -c "
from app.config.setting import settings
print(f'Coordinator Model: {settings.COORDINATOR_MODEL}')
print(f'API Key: {settings.COORDINATOR_API_KEY[:10]}...')
"
```

## 📚 配置 OpenAlex Email（可选）

OpenAlex 用于文献搜索和引用。配置 Email 可以提高 API 速率限制。

### 获取 OpenAlex 访问权限

1. 访问 [OpenAlex.org](https://openalex.org/)
2. 使用任何有效的 Email 地址
3. 无需注册，直接使用

### 配置方式

**Web 界面**:
1. API 配置页面
2. 填写 "OpenAlex Email"
3. 点击验证

**配置文件**:
```bash
# backend/.env.dev
OPENALEX_EMAIL=your-email@example.com
```

## 🔍 配置搜索引擎（可选）

MathModelAgent 支持两种 Web 搜索引擎。

### Tavily（推荐）

1. 注册：https://tavily.com/
2. 获取 API Key
3. 配置：

```bash
# backend/.env.dev
TAVILY_API_KEY=tvly-your-api-key
SEARCH_DEFAULT_PROVIDER=tavily
```

**免费额度**: 1000 次/月

### Exa

1. 注册：https://exa.ai/
2. 获取 API Key
3. 配置：

```bash
# backend/.env.dev
EXA_API_KEY=exa-your-api-key
SEARCH_DEFAULT_PROVIDER=exa
```

## ☁️ 配置云端代码执行（可选）

默认使用本地 Jupyter，如需使用云端执行：

### E2B

1. 注册：https://e2b.dev/
2. 获取 API Key
3. 配置：

```bash
# backend/.env.dev
E2B_API_KEY=your-e2b-api-key
```

## 🔧 高级配置

### 工作流参数

```bash
# backend/.env.dev

# 最大对话轮次
MAX_CHAT_TURNS=70

# 代码执行最大重试次数
MAX_RETRIES=5
```

### Redis 配置

```bash
# backend/.env.dev

# Redis 连接 URL
REDIS_URL=redis://localhost:6379/0

# 如果 Redis 有密码
REDIS_URL=redis://:your_password@localhost:6379/0

# Redis 最大连接数
REDIS_MAX_CONNECTIONS=20
```

### 日志配置

```bash
# backend/.env.dev

# 日志级别: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL=DEBUG

# 调试模式
DEBUG=true
```

## 📊 配置验证清单

完成配置后，请验证以下项目：

### 必需配置
- [ ] 至少一个 Agent 的 API Key 已配置
- [ ] API Key 验证通过
- [ ] Redis 连接正常
- [ ] 后端服务启动成功
- [ ] 前端界面可访问

### 可选配置
- [ ] OpenAlex Email 已配置
- [ ] 搜索引擎 API 已配置
- [ ] E2B API Key 已配置（如需云端执行）

## 🧪 测试配置

### 1. 测试后端连接

```bash
curl http://localhost:8000/
# 应返回: {"message":"Hello World"}
```

### 2. 测试 Redis 连接

```bash
curl http://localhost:8000/status
# 检查 redis.status 是否为 "running"
```

### 3. 运行示例任务

1. 打开前端界面
2. 点击"示例"
3. 选择任意示例
4. 点击"开始建模"
5. 观察是否正常运行

## ❌ 常见配置错误

### API Key 无效

**错误信息**: `✗ API Key 无效或已过期`

**解决方案**:
1. 检查 API Key 是否正确复制
2. 确认 API Key 未过期
3. 检查账户余额是否充足

### 模型 ID 错误

**错误信息**: `✗ 模型 ID 不存在或 Base URL 错误`

**解决方案**:
1. 确认模型 ID 格式正确（`provider/model`）
2. 检查 Base URL 是否正确
3. 参考 [LiteLLM 文档](https://docs.litellm.ai/docs/providers)

### Redis 连接失败

**错误信息**: `Redis connection failed`

**解决方案**:
1. 确认 Redis 服务已启动
2. 检查 `REDIS_URL` 配置
3. 测试连接：`redis-cli ping`

## 💰 成本优化建议

### 混合配置策略

```bash
# 使用便宜的模型做协调
COORDINATOR_MODEL=gpt-3.5-turbo

# 使用强大的模型做建模
MODELER_MODEL=gpt-4

# 使用代码专用模型
CODER_MODEL=deepseek/deepseek-coder

# 使用写作模型
WRITER_MODEL=gpt-4
```

### 预估成本

| Agent | 推荐模型 | 每任务成本 |
|-------|---------|-----------|
| Coordinator | GPT-3.5 | $0.01 |
| Modeler | GPT-4 | $0.10 |
| Coder | DeepSeek-Coder | $0.02 |
| Writer | GPT-4 | $0.10 |
| **总计** | - | **$0.23** |

*成本仅供参考，实际费用取决于问题复杂度*

## 📚 下一步

配置完成后，您可以：

1. [运行第一个任务](first-task.md) - 体验完整流程
2. [了解文件上传](../guides/file-upload.md) - 学习数据上传
3. [查看 API 文档](../api/overview.md) - 深入了解 API

## 💡 获取帮助

- [配置问题 FAQ](../faq/configuration.md)
- [环境变量完整参考](../reference/environment-variables.md)
- [GitHub Issues](https://github.com/jihe520/MathModelAgent/issues)

---

**上一页**: [快速安装](installation.md)  
**下一页**: [第一个建模任务](first-task.md)
