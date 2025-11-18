# 自定义提示词指南

> **文档版本**: v2.0  
> **最后更新**: 2025-01-17  
> **预计阅读时间**: 15 分钟

本指南将教您如何通过修改提示词 (Prompt) 模板来定制和优化 MathModelAgent 中各个 Agent 的行为，以满足您的特定需求。

## 📋 核心概念

### 1. 提示词模板的作用

提示词是指导大型语言模型 (LLM) 如何思考和行动的关键。通过定制提示词，您可以：

-   **改变 Agent 的角色和性格**: 例如，让 WriterAgent 的写作风格更严谨或更通俗。
-   **调整输出格式**: 要求 CoderAgent 生成带特定注释格式的代码。
-   **增加特定约束**: 要求 ModelerAgent 优先考虑某种类型的模型。
-   **注入领域知识**: 为特定问题类型提供额外的背景知识或公式。

### 2. 模板文件结构

提示词模板位于 `backend/app/config/` 目录下，分为中英文两个版本：

-   `md_template.toml`: 中文模板 (国赛模式默认使用)
-   `md_template_en.toml`: 英文模板 (美赛模式默认使用)

文件采用 [TOML](https://toml.io/cn/) 格式，结构如下：

```toml
# backend/app/config/md_template.toml

# Coordinator Agent 的提示词
[coordinator]
system = """你是一个数学建模问题分析专家..."""
user = """请分析以下问题：
{ques_all}
"""

# Modeler Agent 的提示词
[modeler]
system = """你是一个顶级的数学建模专家..."""
user = """..."""

# Coder Agent 的提示词
[coder]
system = """你是一个 Python 编程专家..."""
user = """..."""

# Writer Agent 的提示词
[writer]
system = """你是一个学术论文写作专家..."""

# Writer Agent 的子任务提示词（按章节划分）
[writer.摘要]
user = """请根据以下信息撰写摘要：
{modeling_results}
"""

[writer.问题重述]
user = """..."""

# ... 其他章节
```

### 3. 提示词变量（占位符）

在提示词中，您可以使用 `{}` 占位符来注入动态内容。这些变量由系统在运行时自动替换。

**常用变量**:

| 变量名 | 描述 | 适用 Agent |
|---|---|---|
| `{ques_all}` | 用户输入的完整问题描述 | `Coordinator`, `Modeler` |
| `{problem_analysis}` | CoordinatorAgent 生成的问题分析 | `Modeler` |
| `{model_description}` | ModelerAgent 生成的模型描述 | `Coder` |
| `{code_output}` | CoderAgent 生成的代码执行结果 | `Writer` |
| `{modeling_results}` | 整个建模过程的综合结果 | `Writer` |
| `{references}` | OpenAlex 搜索到的文献列表 | `Writer` |
| `{file_list}` | 上传的文件列表 | `Coordinator`, `Modeler` |

## 🚀 如何自定义提示词

### 步骤 1: 找到并备份模板文件

1.  导航到 `backend/app/config/` 目录。
2.  复制 `md_template.toml` 并重命名为 `md_template.toml.bak` 以作备份。

### 步骤 2: 编辑模板文件

使用文本编辑器打开 `md_template.toml` (或 `md_template_en.toml`)。

**示例：修改 CoderAgent 的行为**

假设我们希望 CoderAgent 生成的代码遵循 PEP8 规范，并添加更详细的类型提示。

**修改前**:
```toml
[coder]
system = """你是一个 Python 编程专家，精通数据分析和科学计算。"""
user = """请根据以下模型描述，编写 Python 代码来解决问题。
模型描述：
{model_description}
"""
```

**修改后**:
```toml
[coder]
system = """你是一个顶级的 Python 编程专家，精通数据分析和科学计算，并且是代码规范的倡导者。你编写的所有代码都必须遵循 PEP8 规范，并包含详细的类型提示 (Type Hinting)。"""
user ="""请根据以下模型描述，编写高质量的 Python 代码来解决问题。

**要求**:
1.  **代码规范**: 严格遵循 PEP8 规范。
2.  **类型提示**: 为所有函数参数和返回值添加明确的类型提示。
3.  **模块化**: 将代码组织成逻辑清晰的函数。
4.  **注释**: 在关键步骤添加必要的注释。
5.  **可视化**: 如果适用，请使用 Matplotlib 或 Seaborn 生成图表。

**模型描述**:
{model_description}
"""
```

### 步骤 3: 重启后端服务

为了让修改生效，您需要重启后端服务。

-   **Docker 部署**: `docker-compose restart backend`
-   **本地部署**: 停止 (`Ctrl+C`) 并重新运行 `uvicorn` 命令。

## 💡 最佳实践与技巧

### 1. 使用 `system` 和 `user` 提示词

-   **`system`**: 用于定义 Agent 的角色、性格和高级指令。这部分内容在整个对话中保持不变。
-   **`user`**: 用于提供具体的任务指令和动态内容（如问题描述）。

### 2. 结构化指令

使用 Markdown 的列表、标题和粗体来组织您的指令，使其更清晰、更易于 LLM 理解。

**反例**:
`user = "写代码，要图，要注释。"`

**正例**:
```
user = """
**任务**: 编写 Python 代码

**要求**:
1.  **可视化**: 使用 Matplotlib 生成折线图。
2.  **注释**: 对每个函数进行详细注释。
"""
```

### 3. 提供示例 (Few-shot Learning)

如果希望输出特定格式，可以在提示词中提供一个示例。

**示例：要求 WriterAgent 生成特定格式的摘要**
```toml
[writer.摘要]
user = """
请根据以下建模结果，撰写一段 200-300 字的摘要。

**摘要格式示例**:
本文针对 [问题简述]，建立了一个 [模型名称] 模型。我们首先对数据进行了 [数据处理方法]，然后利用 [核心算法] 求解模型，得到了 [主要结论]。结果表明，[结论的意义]。

**建模结果**:
{modeling_results}
"""
```

### 4. 迭代和测试

修改提示词是一个不断迭代的过程。建议您：

1.  只修改一个 Agent 的提示词，然后运行任务进行测试。
2.  比较修改前后的输出结果。
3.  根据结果微调提示词。
4.  使用 `backend/project/work_dir/{task_id}/chat_completion.json` 文件查看完整的对话历史，分析 Agent 的实际输入和输出。

## ❓ 常见问题

### Q: 修改了提示词但没有生效？

**A**: 请确保您已经重启了后端服务。如果您是 Docker 部署，需要执行 `docker-compose restart backend`。

### Q: 如何知道哪些变量可用？

**A**: 本指南的[核心概念](#-3-提示词变量占位符)部分列出了常用变量。您也可以在 `backend/core/workflow.py` 文件中查找传递给每个 Agent 的参数。

### Q: 我可以为 WriterAgent 添加新的章节吗？

**A**: 可以。只需在 `md_template.toml` 中添加新的 `[writer.新章节名]` 部分即可。例如：

```toml
[writer.模型评价与推广]
user = """请根据以下结果，撰写模型的评价与推广部分。
{modeling_results}
"""
```
**注意**: 您还需要在 `backend/app/routers/common_router.py` 的 `get_writer_seque` 函数中调整章节顺序。

### Q: 提示词写得太长会影响性能吗？

**A**: 会。更长的提示词会消耗更多的 Token，增加成本和响应时间。请尽量保持提示词简洁、明确。但通常情况下，清晰的指令比极度简短的指令效果更好。

## 📚 相关文档

-   [模型配置指南](model-configuration.md)
-   [环境变量参考](../reference/environment-variables.md)
-   [开发文档 - Agent 系统](../development/agent-system.md)

---

**上一页**: [模型配置指南](model-configuration.md)  
**下一页**: [任务管理指南](task-management.md)
