# API 参考概览

> **文档版本**: v2.0  
> **最后更新**: 2025-01-17

欢迎使用 MathModelAgent API！本部分文档提供了所有可用接口的详细信息，帮助您与系统进行编程交互。

## 📋 基础信息

-   **API Base URL**: `http://localhost:8000` (开发环境)
-   **WebSocket URL**: `ws://localhost:8000` (开发环境)
-   **交互式文档 (Swagger UI)**: [http://localhost:8000/docs](http://localhost:8000/docs)
-   **备用文档 (ReDoc)**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## 🧭 API 导航

API 按功能模块进行划分：

-   [**通用接口**](overview.md#通用接口): 健康检查、配置、服务状态等。
-   [**建模任务接口**](modeling.md): 提交任务、运行示例、验证配置等。
-   [**文件管理接口**](files.md): 上传、下载、列出和删除文件。
-   [**任务历史接口**](history.md): 管理和查询历史任务。
-   [**WebSocket 接口**](websocket.md): 接收任务的实时进度更新。
-   [**搜索接口**](search.md): 执行 Web 搜索和文献检索。
-   [**设置接口**](settings.md): 管理用户配置和偏好（待补充）。
-   [**Prompt 优化接口**](prompt.md): AI 辅助优化输入（待补充）。

## 🛡️ 认证与授权

当前版本的 MathModelAgent 主要为本地和单用户环境设计，**未内置用户认证系统**。

在生产环境中部署时，强烈建议在 API 前端添加一层认证和授权，例如：

-   **反向代理**: 使用 Nginx 或 Caddy 添加 Basic Auth 或 JWT 验证。
-   **API 网关**: 使用 Kong, Traefik 等 API 网关进行统一的认证和速率限制。
-   **代码修改**: 在 FastAPI 中间件中自行实现用户认证逻辑。

## 📈 速率限制

系统目前没有强制的速率限制，但为了保证系统稳定运行，建议遵循以下准则：

-   **建模任务提交**: 单用户并发任务数建议不超过 **3** 个。
-   **API 请求**: 每秒请求数建议不超过 **100** 次。
-   **WebSocket 连接**: 单用户并发连接数建议不超过 **10** 个。

## ❌ 错误处理

API 遵循标准的 HTTP 状态码，并在发生错误时返回统一格式的 JSON 响应体。

**标准错误响应格式**:
```json
{
  "detail": "具体的错误描述信息"
}
```

**示例：资源未找到 (404)**
```json
{
  "detail": "Task not found"
}
```

**示例：请求体验证失败 (422)**
```json
{
  "detail": [
    {
      "loc": ["body", "ques_all"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**常见状态码**:

-   `200 OK`: 请求成功。
-   `201 Created`: 资源创建成功。
-   `204 No Content`: 请求成功，但无内容返回（例如，删除成功）。
-   `400 Bad Request`: 请求无效（例如，参数错误）。
-   `401 Unauthorized`: 未经授权（在添加认证后）。
-   `403 Forbidden`: 禁止访问。
-   `404 Not Found`: 请求的资源不存在。
-   `422 Unprocessable Entity`: 请求体验证失败。
-   `500 Internal Server Error`: 服务器内部错误。

## 🌐 通用接口

这些接口提供系统的基本信息和健康状况。

### `GET /`

-   **描述**: 健康检查端点。
-   **响应 (`200 OK`)**:
    ```json
    {
      "message": "Hello World"
    }
    ```

### `GET /config`

-   **描述**: 获取部分公共配置信息。
-   **响应 (`200 OK`)**:
    ```json
    {
        "environment": "dev",
        "max_chat_turns": 70,
        "max_retries": 5
    }
    ```

### `GET /writer_seque`

-   **描述**: 获取默认的论文章节顺序。
-   **响应 (`200 OK`)**:
    ```json
    {
        "writer_seque": [
            "摘要",
            "问题重述",
            "问题分析",
            "模型假设",
            "符号说明",
            "模型建立与求解",
            "模型评价与推广",
            "参考文献",
            "附录"
        ]
    }
    ```

### `GET /status`

-   **描述**: 获取后端服务及其依赖（如 Redis）的运行状态。
-   **响应 (`200 OK`)**:
    ```json
    {
        "backend": {
            "status": "running",
            "message": "Backend service is running"
        },
        "redis": {
            "status": "running",
            "message": "Redis connection is healthy"
        }
    }
    ```

### `GET /track`

-   **描述**: 获取指定任务的 Token 使用量和成本统计。
-   **查询参数**: `task_id` (string, required)
-   **响应 (`200 OK`)**:
    ```json
    {
        "task_id": "some-task-id",
        "token_usage": {
            "CoordinatorAgent": {
                "prompt_tokens": 1000,
                "completion_tokens": 500,
                "total_tokens": 1500,
                "cost": 0.015
            },
            "ModelerAgent": { ... }
        },
        "total_cost": 0.123
    }
    ```

## 📚 相关文档

-   [快速开始 - 基础配置](../getting-started/basic-configuration.md)
-   [开发文档 - 架构设计](../development/architecture.md)

---

**下一页**: [建模任务接口](modeling.md)
