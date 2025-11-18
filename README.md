<h1 align="center">🤖 MathModelAgent 📐</h1>
<p align="center">
    <img src="./docs/images/icon.png" height="250px">
</p>
<h4 align="center">
    专为数学建模设计的 Agent<br>
    自动完成数学建模，生成一份完整的可以直接提交的论文。
</h4>

<h5 align="center">简体中文 | <a href="README_EN.md">English</a></h5>

## 🌟 愿景

3 天的比赛时间变为 1 小时  
自动完成一份可以获奖级别的建模论文

<p align="center">
    <img src="./docs/images/index.png">
    <img src="./docs/images/chat.png">
    <img src="./docs/images/coder.png">
    <img src="./docs/images/writer.png">
</p>

## ✨ 功能特性

### 🎯 核心功能

- 🔍 **全自动建模流程**：自动分析问题、数学建模、编写代码、纠正错误、撰写论文
- 🌐 **智能语言检测**：自动识别中英文输入，支持国赛（中文）和美赛（英文）模板
- 📊 **多格式输出**：支持 Markdown 和 Word (DOCX) 格式的论文输出
- 📁 **多文件处理**：支持多种文件格式上传（.txt, .csv, .xlsx, .json, .pdf, .png, .jpg 等）
- 🗜️ **压缩包自动解压**：支持 .zip, .rar, .7z, .tar, .gz 等压缩格式自动解压

### 💻 代码执行环境

- 🖥️ **本地解释器**：基于 Jupyter Notebook，代码保存为 .ipynb 方便再编辑
- ☁️ **云端解释器**：支持 [E2B](https://e2b.dev/) 远程代码执行环境
- 🔄 **智能错误重试**：代码执行失败时自动分析错误并重试（最多 5 次）
- 📡 **实时执行反馈**：通过 WebSocket 实时显示代码执行过程和结果

### 🤝 多 Agent 系统

- 🎯 **协调 Agent (CoordinatorAgent)**：分析问题结构，拆解子问题
- 🧮 **建模 Agent (ModelerAgent)**：创建数学模型和求解方案
- 💻 **编码 Agent (CoderAgent)**：实现模型代码并执行调试
- ✍️ **写作 Agent (WriterAgent)**：生成格式化的学术论文

### 🔄 模型与配置

- 🎨 **多模型支持**：每个 Agent 可配置不同的 LLM 模型
- 🤖 **全模型兼容**：通过 [LiteLLM](https://docs.litellm.ai/docs/providers) 支持所有主流 LLM 提供商
  - OpenAI (GPT-4, GPT-3.5)
  - Anthropic (Claude-3)
  - DeepSeek (DeepSeek-Chat, DeepSeek-Coder, DeepSeek-R1)
  - 其他兼容 OpenAI API 的模型
- 🧩 **自定义提示词**：可为每个 Agent 和子任务单独配置 Prompt 模板
- 💰 **成本优化**：Agentless 工作流设计，无需复杂 Agent 框架

### 📚 学术功能

- 📖 **文献引用**：集成 OpenAlex API 自动搜索和引用相关文献
- [object Object] 搜索**：支持 Tavily 和 Exa 搜索引擎集成
- 📄 **论文模板**：内置国赛和美赛论文模板

### 🎨 用户体验

- 💎 **现代化界面**：基于 Vue 3 + TailwindCSS 的响应式界面
- 🔌 **实时通信**：WebSocket 实时推送任务进度和结果
- 📜 **任务历史**：完整的任务历史记录和收藏功能
- 🎯 **示例案例**：内置多个示例问题，快速体验系统功能
- 💡 **Prompt 优化**：AI 辅助优化用户输入的问题描述

## 🚀 后期计划

- [x] 添加并完成 webui、cli
- [x] 英文支持（美赛 MCM/ICM）**含智能语言检测**
- [x] 添加正确文献引用
- [x] 更多测试案例
- [x] docker 部署
- [x] codeinterpreter 接入云端 如 e2b 等供应商
- [x] web search tool (Tavily, Exa)
- [ ] 完善的教程、文档
- [ ] 提供 web 服务
- [ ] 集成 latex 模板
- [ ] 接入视觉模型
- [ ] human in loop (HIL): 引入用户的交互（选择模型，@agent重写，等等）
- [ ] feedback: evaluate the result and modify
- [ ] 多语言: R 语言, matlab
- [ ] 绘图 napkin, draw.io, plantuml, svg, mermaid.js
- [ ] 添加 benchmark
- [ ] RAG 知识库
- [ ] A2A hand off: 代码手多次反思错误，hand off 更聪明模型 agent
- [ ] chat / agent mode

## 视频 Demo

<video src="https://github.com/user-attachments/assets/954cb607-8e7e-45c6-8b15-f85e204a0c5d"></video>

> [!CAUTION]
> 项目处于实验探索迭代 demo 阶段，有许多需要改进优化改进地方，我(项目作者)很忙，有时间会优化更新  
> 欢迎贡献

## 📖 使用教程

提供三种部署方式，请选择最适合你的方案：

1. [Docker 部署（推荐）](#-方案一docker-部署推荐最简单)
2. [本地部署](#-方案二-本地部署)
3. [脚本自动部署（社区）](#-方案三自动脚本部署来自社区)

### 下载项目

```bash
git clone https://github.com/jihe520/MathModelAgent.git
cd MathModelAgent
```

> 如果你想运行命令行版本 CLI，切换到 [master](https://github.com/jihe520/MathModelAgent/tree/master) 分支，部署更简单，但未来不会更新

### 🐳 方案一：Docker 部署（推荐：安全简单）

> 确保电脑安装了 Docker 环境

#### 1. 启动服务

在项目文件夹下运行:

```bash
docker-compose up
```

后台运行:

```bash
docker-compose up -d
```

#### 2. 访问

现在你可以访问：

- **前端界面**: <http://localhost:5173>
- **后端 API**: <http://localhost:8000>
- **API 文档**: <http://localhost:8000/docs>

#### 3. 配置

侧边栏 -> 头像 -> API Key

**必需配置**:

- 至少配置一个 Agent 的 API Key（推荐全部配置）
- OpenAlex Email（用于文献搜索，可选）

**可选配置**:

- Tavily API Key（Web 搜索）
- Exa API Key（Web 搜索）
- E2B API Key（云端代码执行）

### [object Object] 本地部署

> 确保电脑中安装好 Python 3.12+, Node.js 18+, **Redis** 环境

#### 1. 安装 Redis

**Windows**:

```powershell
# 使用 Chocolatey
choco install redis-64

# 或下载 MSI 安装包
# https://github.com/microsoftarchive/redis/releases
```

**macOS**:

```bash
brew install redis
brew services start redis
```

**Linux**:

```bash
sudo apt-get install redis-server
sudo systemctl start redis
```

#### 2. 配置环境变量

修改 `backend/.env.dev` 文件：

```bash
# 修改 Redis URL（如果有密码）
REDIS_URL=redis://localhost:6379/0

# 配置至少一个 Agent 的 API Key
COORDINATOR_API_KEY=your-api-key
COORDINATOR_MODEL=gpt-4
COORDINATOR_BASE_URL=https://api.openai.com/v1

# 其他 Agent 配置...
```

#### 3. 启动后端

```bash
cd backend
pip install uv  # 推荐使用 uv 管理 Python 项目
uv sync  # 安装依赖

# 激活 Python 虚拟环境
source .venv/bin/activate  # macOS or Linux
.venv\Scripts\activate.bat  # Windows

# 启动后端
# macOS or Linux
ENV=DEV uvicorn app.main:app --host 0.0.0.0 --port 8000 --ws-ping-interval 60 --ws-ping-timeout 120 --reload

# Windows
set ENV=DEV && uvicorn app.main:app --host 0.0.0.0 --port 8000 --ws-ping-interval 60 --ws-ping-timeout 120 --reload
```

#### 4. 启动前端

```bash
cd frontend
npm install -g pnpm
pnpm i  # 安装依赖
pnpm run dev  # 启动开发服务器
```

#### 5. 访问

- **前端界面**: <http://localhost:5173>
- **后端 API**: <http://localhost:8000>
- **API 文档**: <http://localhost:8000/docs>

### 🚀 方案三：自动脚本部署（来自社区）

社区提供的自动部署脚本：[mmaAutoSetupRun](https://github.com/Fitia-UCAS/mmaAutoSetupRun)

## 📚 文档

我们提供了全新的、结构化的文档中心来帮助您。

- **[📄 文档中心](./docs/README.md)** - 所有文档的入口
- **[🚀 快速安装](./docs/getting-started/installation.md)** - 5分钟快速部署指南
- **[⚙️ 基础配置](./docs/getting-started/basic-configuration.md)** - 配置 API Keys 和其他设置
- **[🥇 第一个任务](./docs/getting-started/first-task.md)** - 运行您的第一个建模任务
- **[❓ 常见问题](./docs/faq/network-issues.md)** - 包含网络问题解决方案

## 📁 输出文件

运行的结果和产生在 `backend/project/work_dir/{task_id}/` 目录下：

- `notebook.ipynb`: 保存运行过程中产生的代码
- `res.md`: 保存最后运行产生的结果为 Markdown 格式
- `res.docx`: Word 格式的论文（如果选择）
- `data/`: 上传的数据文件
- `figures/`: 生成的图表
- `token_usage.json`: Token 使用统计
- `chat_completion.json`: 聊天记录

## 🎨 自定义

### 自定义提示词模板

编辑 `backend/app/config/md_template.toml` (中文) 或 `md_template_en.toml` (英文)

```toml
[modeler]
system = """你是一个数学建模专家..."""
user = """请分析以下问题：{ques_all}"""

[coder]
system = """你是一个Python编程专家..."""
# ...
```

### 自定义模型配置

编辑 `backend/app/config/model_config.toml`

```toml
[config1]
COORDINATOR_MODEL='gpt-3.5-turbo'
MODELER_MODEL='gpt-4'
CODER_MODEL='deepseek/deepseek-coder'
WRITER_MODEL='claude-3-sonnet-20240229'
```

## 🤝 贡献和开发

[DeepWiki](https://deepwiki.com/jihe520/MathModelAgent) | [Zread](https://zread.ai/jihe520/MathModelAgent)

> [!TIP]
> 如果你有跑出来好的案例可以提交 PR 在该仓库下:  
> [MathModelAgent-Example](https://github.com/jihe520/MathModelAgent-Example)

- 项目处于**开发实验阶段**（我有时间就会更新），变更较多，还存在许多 Bug，我正着手修复。
- 希望大家一起参与，让这个项目变得更好
- 非常欢迎使用和提交 **PRs** 和 issues
- 需求参考后期计划

Clone 项目后，下载 **Todo Tree** 插件，可以查看代码中所有具体位置的 todo

`.cursor/*` 有项目整体架构、rules、mcp 可以方便开发使用

## 📄 版权 License

个人免费使用，请勿商业用途，商业用途联系我（作者）

[License](./docs/md/License.md)

## 🙏 Reference

Thanks to the following projects:

- [OpenCodeInterpreter](https://github.com/OpenCodeInterpreter/OpenCodeInterpreter/tree/main)
- [TaskWeaver](https://github.com/microsoft/TaskWeaver)
- [Code-Interpreter](https://github.com/MrGreyfun/Local-Code-Interpreter/tree/main)
- [Latex](https://github.com/Veni222987/MathModelingLatexTemplate/tree/main)
- [Agent Laboratory](https://github.com/SamuelSchmidgall/AgentLaboratory)
- [ai-manus](https://github.com/Simpleyyt/ai-manus)

## 其他

### 💖 Sponsor

[☕️ 给作者买一杯咖啡](./docs/md/sponser.md)

感谢赞助

#### 企业

<div align="center">
    <a href="https://share.302.ai/UoTruU" target="_blank">
    <img src="./docs/images/302ai.jpg">
    </a>
</div>

[302.AI](https://share.302.ai/UoTruU) 是一个按用量付费的企业级AI资源平台，提供市场上最新、最全面的AI模型和API，以及多种开箱即用的在线AI应用

#### 用户

[danmo-tyc](https://github.com/danmo-tyc)

### [object Object]

有问题可以进群问

点击链接加入腾讯频道【MathModelAgent】：<https://pd.qq.com/s/7rfbai3au>

点击链接加入群聊 779159301【MathModelAgent3】：<https://qm.qq.com/q/Fw2cCJPoki>

[Discord](https://discord.gg/3Jmpqg5J)

[QQ 群：699970403](http://qm.qq.com/cgi-bin/qm/qr?_wv=1027&k=rFKquDTSxKcWpEhRgpJD-dPhTtqLwJ9r&authKey=xYKvCFG5My4uYZTbIIoV5MIPQedW7hYzf0%2Fbs4EUZ100UegQWcQ8xEEgTczHsyU6&noverify=0&group_code=699970403)

<div align="center">
    <img src="./docs/images/qq.jpg" height="400px">
</div>

> [!CAUTION]
> 免责声明: 注意，AI 生成仅供参考，目前水平直接参加国赛获奖是不可能的，但我相信 AI 和该项目未来的成长。
