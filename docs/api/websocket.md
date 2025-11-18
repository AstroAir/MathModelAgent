# API - WebSocket 接口

> **文档版本**: v2.0  
> **最后更新**: 2025-01-17

MathModelAgent 使用 WebSocket 来实现服务器与客户端之间的实时、双向通信。这对于实时推送任务进度、代码执行输出和日志至关重要。

## 建立连接

-   **Endpoint**: `WS /task/{task_id}`
-   **URL 示例**: `ws://localhost:8000/task/20250117-153000-a1b2c3d4`

### 连接流程

1.  客户端在提交建模任务并获得 `task_id` 后，立即使用该 `task_id` 发起 WebSocket 连接。
2.  服务器验证 `task_id` 是否有效。
    -   如果有效，连接成功建立。
    -   如果无效，服务器将关闭连接，状态码为 `1008` (Policy Violation)。
3.  连接成功后，服务器会通过该连接实时推送该任务的所有更新。

### JavaScript 连接示例

```javascript
const taskId = 'your-task-id';
const ws = new WebSocket(`ws://localhost:8000/task/${taskId}`);

ws.onopen = () => {
  console.log('WebSocket connection established.');
};

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log('Received message:', message);
  // 在这里根据 message.type 处理不同类型的消息
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};

ws.onclose = (event) => {
  console.log(`WebSocket closed: ${event.code} - ${event.reason}`);
};
```

## 消息格式

所有从服务器发送到客户端的消息都是 JSON 格式，并包含一个 `type` 字段来区分消息类型。

### 1. `SystemMessage` (系统消息)

**描述**: 用于通知任务的宏观状态，如开始、结束、错误等。

**示例**:
```json
{
  "type": "system",
  "content": "任务开始处理",
  "timestamp": "2025-01-17T15:30:01Z"
}
```

### 2. `AgentMessage` (Agent 消息)

**描述**: 用于传达某个 Agent 的状态和它正在执行的操作。

**示例**:
```json
{
  "type": "agent",
  "agent_type": "ModelerAgent",
  "status": "working",
  "content": "正在分析问题并建立数学模型...",
  "timestamp": "2025-01-17T15:31:00Z"
}
```
-   `agent_type`: `CoordinatorAgent`, `ModelerAgent`, `CoderAgent`, `WriterAgent`.
-   `status`: `start`, `working`, `done`, `error`.

### 3. `StepMessage` (步骤消息)

**描述**: 用于更细粒度地展示一个 Agent 内部的工作步骤。

**示例**:
```json
{
  "type": "step",
  "step_name": "文献检索",
  "step_index": 2,
  "total_steps": 5,
  "status": "in_progress",
  "content": "正在使用 OpenAlex 搜索相关文献...",
  "timestamp": "2025-01-17T15:32:00Z"
}
```

### 4. `CodeExecutionMessage` (代码执行消息)

**描述**: 用于实时反馈 `CoderAgent` 执行代码的情况，包括代码本身、输出和错误。

**示例**:
```json
{
  "type": "code_execution",
  "code": "import numpy as np\nprint(f'Numpy version: {np.__version__}')",
  "output": "Numpy version: 1.26.2\n",
  "error": null,
  "execution_time": 0.8,
  "timestamp": "2025-01-17T15:33:00Z"
}
```

### 5. `ProgressMessage` (进度消息)

**描述**: 提供任务的总体完成百分比。

**示例**:
```json
{
  "type": "progress",
  "progress": 0.65,
  "stage": "代码执行",
  "message": "正在运行第 3 个代码块...",
  "timestamp": "2025-01-17T15:34:00Z"
}
```

### 6. `ErrorMessage` (错误消息)

**描述**: 当任务执行过程中发生严重错误时发送。

**示例**:
```json
{
  "type": "error",
  "error_type": "CodeExecutionError",
  "message": "代码执行失败，已达到最大重试次数。",
  "details": "NameError: name 'pandas' is not defined",
  "timestamp": "2025-01-17T15:35:00Z"
}
```

### 7. `CompletionMessage` (完成消息)

**描述**: 当任务成功完成时发送的最终消息。

**示例**:
```json
{
  "type": "success",
  "content": "任务处理完成",
  "result_files": [
    "notebook.ipynb",
    "res.md",
    "res.docx"
  ],
  "timestamp": "2025-01-17T15:45:00Z"
}
```

## 📚 相关文档

-   [API 概览](overview.md)
-   [指南 - 第一个建模任务](../guides/first-task.md)

---

**上一页**: [任务历史接口](history.md)  
**下一页**: [搜索接口](search.md)
