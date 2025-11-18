# API - 建模任务接口

> **文档版本**: v2.0  
> **最后更新**: 2025-01-17

这些接口负责创建和管理数学建模任务，是系统的核心入口。

## 接口列表

-   `POST /modeling`: 提交自定义建模任务。
-   `POST /example`: 运行内置示例任务。
-   `POST /validate-api-key`: 验证 LLM API Key。
-   `POST /validate-openalex-email`: 验证 OpenAlex Email。
-   `POST /save-api-config`: 保存 API 配置。

---

### `POST /modeling`

**描述**: 提交一个包含问题描述和数据文件的自定义建模任务。任务将在后台异步执行。

**Content-Type**: `multipart/form-data`

**表单参数 (Form Data)**:

-   `ques_all` (string, required): 完整的问题描述文本。
-   `comp_template` (string, required): 竞赛模板。允许的值: `"CHINA"`, `"AMERICAN"`。
-   `format_output` (string, required): 最终论文的输出格式。允许的值: `"Markdown"`, `"LaTeX"`。
-   `files` (file, optional): 一个或多个数据文件。支持单个文件、多个文件、文件夹和压缩包上传。

**成功响应 (`200 OK`)**:

```json
{
  "task_id": "20250117-153000-a1b2c3d4",
  "status": "processing"
}
```
-   `task_id`: 任务的唯一标识符。您需要使用此 ID 来通过 WebSocket 接收实时更新或查询任务结果。
-   `status`: 任务的初始状态。

**错误响应**:

-   `422 Unprocessable Entity`: 如果 `ques_all`, `comp_template` 或 `format_output` 字段缺失。
-   `500 Internal Server Error`: 如果文件保存失败或任务创建过程中发生其他错误。

---

### `POST /example`

**描述**: 运行一个内置的示例任务。这对于快速测试系统功能非常有用。

**请求体 (JSON)**:

```json
{
  "source": "example_name"
}
```
-   `source` (string, required): 示例的名称。示例名称可以在 `backend/app/example/example/` 目录下找到对应的文件夹名。

**成功响应 (`200 OK`)**:

```json
{
  "task_id": "20250117-153500-e5f6g7h8",
  "status": "processing"
}
```

---

### `POST /validate-api-key`

**描述**: 验证一个 LLM API Key 的有效性，通过向模型发送一个简短的测试请求来实现。

**请求体 (JSON)**:

```json
{
  "api_key": "sk-your-llm-api-key",
  "base_url": "https://api.openai.com/v1",
  "model_id": "gpt-4-turbo"
}
```
-   `api_key` (string, required): 要验证的 API Key。
-   `base_url` (string, optional): API 的基础 URL。默认为 OpenAI 的 URL。
-   `model_id` (string, required): 用于测试的模型 ID。

**成功响应 (`200 OK`)**:

```json
{
  "valid": true,
  "message": "✓ 模型 API 验证成功"
}
```

**失败响应 (`200 OK`)**:

```json
{
  "valid": false,
  "message": "✗ API Key 无效或已过期"
}
```
> **注意**: 即使验证失败，HTTP 状态码也是 200。您需要检查 `valid` 字段来判断结果。

---

### `POST /validate-openalex-email`

**描述**: 验证一个 Email 是否可以用于访问 OpenAlex API。

**请求体 (JSON)**:

```json
{
  "email": "your-email@example.com"
}
```

**成功响应 (`200 OK`)**:

```json
{
  "valid": true,
  "message": "✓ OpenAlex Email 验证成功"
}
```

---

### `POST /save-api-config`

**描述**: 将用户在 Web 界面上验证并保存的 API 配置应用到后端服务的当前会话中。

**请求体 (JSON)**:

```json
{
  "coordinator": {
    "apiKey": "sk-xxx",
    "modelId": "gpt-3.5-turbo",
    "baseUrl": "https://api.openai.com/v1"
  },
  "modeler": { ... },
  "coder": { ... },
  "writer": { ... },
  "openalex_email": "your-email@example.com"
}
```

**成功响应 (`200 OK`)**:

```json
{
  "success": true,
  "message": "配置保存成功"
}
```

## 📚 相关文档

-   [API 概览](overview.md)
-   [指南 - 第一个建模任务](../guides/first-task.md)
-   [指南 - 模型配置](../guides/model-configuration.md)

---

**上一页**: [API 概览](overview.md)  
**下一页**: [文件管理接口](files.md)
