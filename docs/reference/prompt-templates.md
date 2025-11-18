# 参考 - 提示词模板

> **文档版本**: v2.0  
> **最后更新**: 2025-01-17

本指南详细说明 `md_template.toml` 和 `md_template_en.toml` 文件的结构和自定义方法。这些文件是控制 Agent 行为的核心。

## 📁 文件位置

-   **中文模板**: `backend/app/config/md_template.toml`
-   **英文模板**: `backend/app/config/md_template_en.toml`

系统会根据任务选择的语言（中文/英文）或自动检测结果，加载相应的模板文件。

## ⚙️ TOML 文件结构

文件采用 TOML 格式，由多个区块组成，每个区块对应一个 Agent 或 Agent 的一个子任务。

### Agent 级别配置

每个 Agent（`coordinator`, `modeler`, `coder`, `writer`）都有一个主区块。

```toml
[coordinator]
system = """你是一个数学建模问题分析专家..."""
user = """请分析以下问题：
{ques_all}
"""
```

-   `[agent_name]`: 定义了这是哪个 Agent 的配置。
-   `system`: 定义了该 Agent 的系统提示词 (System Prompt)。它设定了 Agent 的角色、能力和高级指令，在整个任务中保持不变。
-   `user`: 定义了用户提示词 (User Prompt)。它包含了具体的任务指令和通过占位符注入的动态内容。

### Writer Agent 子任务配置

`WriterAgent` 比较特殊，它的任务被分解为多个子任务，每个子任务对应论文的一个章节。因此，它的配置也按章节划分。

```toml
# Writer Agent 的通用系统提示词
[writer]
system = """你是一个学术论文写作专家..."""

# “摘要”章节的提示词
[writer.摘要]
user = """请根据以下信息撰写摘要：
{modeling_results}
"""

# “问题重述”章节的提示词
[writer.问题重述]
user = """请根据原始问题，进行问题重述。
原始问题：
{ques_all}
"""

# ... 其他章节
```

-   `[writer]`: 定义了 `WriterAgent` 通用的 `system` 提示词。
-   `[writer.章节名]`: 为特定章节定义 `user` 提示词。章节名必须与 `common_router.py` 中 `get_writer_seque` 函数返回的顺序一致。

## 🧩 提示词变量 (占位符)

您可以在 `user` 提示词中使用 `{variable_name}` 格式的占位符来插入动态内容。

| 变量名 | 描述 | 适用 Agent |
|---|---|---|
| `{ques_all}` | 用户输入的完整问题描述。 | `Coordinator`, `Writer` |
| `{file_list}` | 用户上传的文件列表字符串。 | `Coordinator`, `Modeler` |
| `{problem_analysis}` | `CoordinatorAgent` 生成的问题分析结果。 | `Modeler` |
| `{model_description}` | `ModelerAgent` 生成的数学模型描述。 | `Coder` |
| `{code_output}` | `CoderAgent` 执行代码后的完整输出。 | `Writer` |
| `{python_code}` | `CoderAgent` 生成的 Python 代码。 | `Writer` |
| `{modeling_results}` | 整个建模过程的综合结果摘要。 | `Writer` |
| `{references}` | 通过 OpenAlex 搜索到的文献列表。 | `Writer` |

## 💡 自定义技巧

### 1. 强调指令

使用 Markdown（如 `**`、`#`）和明确的词语（如“必须”、“要求”、“严格遵循”）来强调重要指令。

```toml
[coder]
system = """...
**重要**: 你编写的所有代码都必须包含类型提示。"""
```

### 2. 提供输出格式示例 (Few-shot)

在提示词中提供一个期望的输出格式示例，可以极大地提升 LLM 理解您意图的准确性。

```toml
[coordinator]
user = """...
请严格按照以下 JSON 格式返回结果，不要包含任何额外的解释：

```json
{
  "ques_count": [问题的数量],
  "questions": {
    "ques1": "第一个子问题的描述",
    "ques2": "第二个子问题的描述"
  }
}
```
"""
```

### 3. 链式思考 (Chain of Thought)

引导模型分步思考，可以提高复杂任务的推理质量。

```toml
[modeler]
user = """...
请遵循以下步骤进行思考和建模：
1.  **第一步**: 确定这是一个什么类型的优化问题（例如，线性规划、整数规划、动态规划）。
2.  **第二步**: 定义所有必要的变量和符号。
3.  **第三步**: 写出目标函数。
4.  **第四步**: 列出所有的约束条件。
5.  **第五步**: 总结完整的数学模型。
"""
```

### 4. 修改 Agent 角色

通过修改 `system` 提示词，您可以赋予 Agent 不同的“性格”或专业领域。

**示例：让 WriterAgent 的风格更具批判性**
```toml
[writer]
system = """你是一位经验丰富、眼光挑剔的数学建模竞赛评委。你的任务是基于提供的材料，撰写一份高质量的论文，同时在 '模型评价与推广' 章节中，以评委的视角指出模型的潜在弱点和改进方向。"""
```

## 📚 相关文档

-   [指南 - 自定义提示词](../guides/custom-prompts.md)
-   [参考 - 环境变量](environment-variables.md)

---

**上一页**: [模型配置文件](model-config.md)  
**下一页**: [Docker 配置](docker-config.md)
