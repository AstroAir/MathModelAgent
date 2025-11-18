# 快速安装指南

> **文档版本**: v2.0  
> **最后更新**: 2025-01-17  
> **预计时间**: 5-15 分钟

本指南将帮助您快速部署 MathModelAgent 系统。我们提供三种部署方式，请根据您的需求选择。

## 📋 前置要求

### 方案一：Docker 部署（推荐）
- ✅ 已安装 Docker Desktop
- ✅ 至少 4GB 可用内存
- ✅ 至少 10GB 可用磁盘空间

### 方案二：本地部署
- ✅ Python 3.12 或更高版本
- ✅ Node.js 18 或更高版本
- ✅ Redis 服务器
- ✅ 至少 4GB 可用内存

### 方案三：自动脚本部署
- ✅ 支持的操作系统（Windows/Linux/macOS）
- ✅ 网络连接

## 🐳 方案一：Docker 部署（推荐）

Docker 部署是最简单、最可靠的方式，适合大多数用户。

### 1. 安装 Docker

#### Windows
1. 下载 [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/)
2. 运行安装程序
3. 重启计算机
4. 启动 Docker Desktop

#### macOS
```bash
# 使用 Homebrew 安装
brew install --cask docker

# 或下载安装包
# https://www.docker.com/products/docker-desktop/
```

#### Linux
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install docker.io docker-compose

# CentOS/RHEL
sudo yum install docker docker-compose

# 启动 Docker 服务
sudo systemctl start docker
sudo systemctl enable docker
```

### 2. 下载项目

```bash
# 克隆项目
git clone https://github.com/jihe520/MathModelAgent.git
cd MathModelAgent
```

> **网络问题？** 如果无法访问 GitHub，可以：
> - 使用 [Gitee 镜像](https://gitee.com/jihe520/MathModelAgent)（如果有）
> - 下载 [ZIP 压缩包](https://github.com/jihe520/MathModelAgent/archive/refs/heads/main.zip)
> - 参考 [网络问题解决方案](../faq/network-issues.md)

### 3. 启动服务

```bash
# 启动所有服务
docker-compose up

# 或在后台运行
docker-compose up -d
```

首次启动需要下载镜像，可能需要 5-10 分钟。

### 4. 验证安装

打开浏览器访问：

- **前端界面**: http://localhost:5173
- **后端 API**: http://localhost:8000
- **API 文档**: http://localhost:8000/docs

如果看到界面，说明安装成功！

### 5. 停止服务

```bash
# 停止服务
docker-compose down

# 停止并删除数据
docker-compose down -v
```

## 💻 方案二：本地部署

本地部署适合开发者或需要自定义配置的用户。

### 1. 安装依赖

#### 安装 Python 3.12+

**Windows**:
```powershell
# 使用 Chocolatey
choco install python312

# 或下载安装包
# https://www.python.org/downloads/
```

**macOS**:
```bash
brew install python@3.12
```

**Linux**:
```bash
sudo apt-get install python3.12 python3.12-venv
```

#### 安装 Node.js 18+

**Windows**:
```powershell
choco install nodejs
```

**macOS**:
```bash
brew install node@18
```

**Linux**:
```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

#### 安装 Redis

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
sudo systemctl enable redis
```

### 2. 下载项目

```bash
git clone https://github.com/jihe520/MathModelAgent.git
cd MathModelAgent
```

### 3. 配置后端

```bash
cd backend

# 安装 uv（Python 包管理器）
pip install uv

# 安装依赖
uv sync

# 激活虚拟环境
# Windows
.venv\Scripts\activate.bat

# macOS/Linux
source .venv/bin/activate
```

### 4. 配置环境变量

复制并编辑配置文件：

```bash
# 在 backend 目录下
cp .env.dev.example .env.dev

# 编辑 .env.dev 文件
# 至少需要配置一个 Agent 的 API Key
```

最小配置示例：
```bash
# .env.dev
ENV=dev

# 配置至少一个 Agent
COORDINATOR_API_KEY=your-api-key-here
COORDINATOR_MODEL=gpt-4
COORDINATOR_BASE_URL=https://api.openai.com/v1

# Redis 配置
REDIS_URL=redis://localhost:6379/0
```

### 5. 启动后端

```bash
# 确保在 backend 目录下，且虚拟环境已激活

# Windows
set ENV=DEV && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# macOS/Linux
ENV=DEV uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 6. 配置前端

打开新的终端窗口：

```bash
cd frontend

# 安装 pnpm
npm install -g pnpm

# 安装依赖
pnpm install

# 启动开发服务器
pnpm run dev
```

### 7. 验证安装

访问 http://localhost:5173，如果看到界面，说明安装成功！

## 🚀 方案三：自动脚本部署

社区提供的自动部署脚本，适合快速体验。

### 使用方法

```bash
# 克隆脚本仓库
git clone https://github.com/Fitia-UCAS/mmaAutoSetupRun.git
cd mmaAutoSetupRun

# 运行安装脚本
# Windows
.\install.bat

# Linux/macOS
chmod +x install.sh
./install.sh
```

详细说明请参考 [mmaAutoSetupRun 仓库](https://github.com/Fitia-UCAS/mmaAutoSetupRun)。

## ✅ 验证安装

### 检查服务状态

1. **后端服务**
   - 访问 http://localhost:8000
   - 应该看到 `{"message": "Hello World"}`

2. **前端服务**
   - 访问 http://localhost:5173
   - 应该看到 MathModelAgent 主页

3. **Redis 服务**
   ```bash
   redis-cli ping
   # 应该返回: PONG
   ```

### 运行测试任务

1. 打开前端界面
2. 点击"示例"
3. 选择一个内置示例
4. 点击"开始建模"
5. 观察实时进度

如果任务成功完成，说明系统运行正常！

## 🔧 常见问题

### Docker 相关

**问题**: Docker 启动失败
```bash
# 检查 Docker 状态
docker ps

# 查看日志
docker-compose logs
```

**问题**: 端口被占用
```bash
# 修改 docker-compose.yml 中的端口映射
ports:
  - "5174:5173"  # 前端改为 5174
  - "8001:8000"  # 后端改为 8001
```

### Redis 相关

**问题**: Redis 连接失败
```bash
# 检查 Redis 是否运行
redis-cli ping

# 检查配置
# 确保 .env.dev 中的 REDIS_URL 正确
```

### Python 相关

**问题**: uv 安装失败
```bash
# 使用 pip 直接安装依赖
pip install -r requirements.txt
```

**问题**: 虚拟环境激活失败
```bash
# Windows PowerShell 可能需要修改执行策略
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## 📚 下一步

安装完成后，建议您：

1. [配置 API Keys](basic-configuration.md) - 配置 LLM 模型
2. [运行第一个任务](first-task.md) - 体验完整流程
3. [了解文件上传](../guides/file-upload.md) - 学习如何上传数据

## 💡 获取帮助

遇到问题？

- 查看 [常见问题](../faq/installation.md)
- 查看 [网络问题解决方案](../faq/network-issues.md)
- 在 [GitHub Issues](https://github.com/jihe520/MathModelAgent/issues) 提问
- 加入 QQ 群：699970403

---

**上一页**: [文档首页](../README.md)  
**下一页**: [基础配置](basic-configuration.md)
