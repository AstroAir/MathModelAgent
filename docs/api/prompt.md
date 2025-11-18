# API - Prompt 优化接口

> **文档版本**: v2.0  
> **最后更新**: 2025-01-17

此接口提供了一个实验性功能，利用 LLM 来优化用户输入的原始问题描述，使其更清晰、更结构化，从而提升后续 Agent 的处理效果。

**Base Path**: `/api/prompt`

## 接口列表

-   `POST /api/prompt/optimize`: 优化用户输入的 Prompt。

---

### `POST /api/prompt/optimize`

**描述**: 接收一个原始的、可能比较模糊的 Prompt，以及一些上下文信息，然后调用一个 LLM（通常是 Coordinator Agent 配置的模型）来重写和优化这个 Prompt。

**请求体 (JSON)**:

```json
{
  "original_prompt": "帮我解决一个物流配送的优化问题，有几个仓库和几个门店，怎么送货成本最低？",
  "context": {
    "task_type": "modeling",
    "language": "zh",
    "files": ["warehouse.csv", "stores.csv"]
  }
}
```
-   `original_prompt` (string, required): 用户输入的原始问题描述。
-   `context` (object, optional): 提供一些附加上下文，帮助 LLM 更好地理解和优化 Prompt。
    -   `task_type` (string): 当前的任务类型。
    -   `language` (string): 使用的语言。
    -   `files` (array of strings): 用户已上传的文件列表。

**成功响应 (`200 OK`)**:

```json
{
  "original_prompt": "帮我解决一个物流配送的优化问题，有几个仓库和几个门店，怎么送货成本最低？",
  "optimized_prompt": "请为以下物流配送场景建立一个数学模型，以最小化总运输成本：\n\n**1. 问题背景与目标**\n目标：规划从多个仓库到多个门店的货物配送方案，使得总运输成本最低。\n\n**2. 已知数据**\n- 仓库信息（详见 `warehouse.csv` 文件），应包含：\n  - 各仓库的存货量。\n- 门店信息（详见 `stores.csv` 文件），应包含：\n  - 各门店的需求量。\n- 运输成本：\n  - 需要明确从每个仓库到每个门店的单位运输成本。如果数据文件中未提供，请在模型中将其设为参数。\n\n**3. 待解决的关键问题**\n- 确定从每个仓库向每个门店运输的货物数量。\n\n**4. 约束条件**\n- 每个仓库的总发货量不能超过其存货量。\n- 每个门店接收的总货物量必须满足其需求量。\n- 运输量不能为负数。",
  "improvements": [
    "将模糊问题结构化为清晰的建模任务",
    "明确了核心优化目标（最小化总成本）",
    "指出了所需数据和关键参数",
    "定义了待求解的决策变量",
    "列出了模型的基本约束条件"
  ]
}
```

**错误响应**:
-   `500 Internal Server Error`: 如果用于优化的 LLM 调用失败。

## 📚 相关文档

-   [API 概览](overview.md)
-   [指南 - 最佳实践](../guides/best-practices.md)

---

**上一页**: [设置接口](settings.md)  
**文档首页**: [../README.md](../README.md)
