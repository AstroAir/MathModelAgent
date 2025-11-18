# 网络问题解决方案

> **文档版本**: v2.0  
> **最后更新**: 2025-01-17  
> **原始文档**: 基于社区贡献整理

本文档提供在网络环境较差时部署和使用 MathModelAgent 的解决方案。

## 📋 常见网络问题

- 无法访问 GitHub
- 无法访问 Docker Hub
- pip/npm 下载速度慢
- Docker 镜像拉取失败
- API 请求超时

## 🌐 场景一：无法访问 GitHub

### 问题描述

```bash
git clone https://github.com/jihe520/MathModelAgent.git
# fatal: unable to access 'https://github.com/...': Failed to connect
```

### 解决方案

#### 方案 1: 使用镜像站

```bash
# 使用 GitHub 镜像（如果可用）
git clone https://ghproxy.com/https://github.com/jihe520/MathModelAgent.git

# 或使用 Gitee 镜像（如果有）
git clone https://gitee.com/jihe520/MathModelAgent.git
```

#### 方案 2: 下载 ZIP 压缩包

1. 访问项目页面（通过代理或镜像）
2. 点击 "Code" -> "Download ZIP"
3. 解压到本地目录

#### 方案 3: 使用代理

```bash
# 设置 Git 代理
git config --global http.proxy http://127.0.0.1:7890
git config --global https.proxy http://127.0.0.1:7890

# 取消代理
git config --global --unset http.proxy
git config --global --unset https.proxy
```

#### 方案 4: 修改 hosts 文件

```bash
# Windows: C:\Windows\System32\drivers\etc\hosts
# Linux/Mac: /etc/hosts

# 添加以下内容（IP 地址可能需要更新）
140.82.114.4 github.com
199.232.69.194 github.global.ssl.fastly.net
```

## 🐳 场景二：Docker Hub 访问问题

### 问题描述

```bash
docker-compose build
# Error response from daemon: Get https://registry-1.docker.io/v2/: net/http: TLS handshake timeout
```

### 解决方案

#### 方案 1: 使用国内镜像源

编辑 Docker 配置文件：

**Windows**: Docker Desktop -> Settings -> Docker Engine

**Linux**: `/etc/docker/daemon.json`

**macOS**: `~/.docker/daemon.json`

```json
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com",
    "https://mirror.ccs.tencentyun.com"
  ]
}
```

重启 Docker 服务：

```bash
# Linux
sudo systemctl restart docker

# Windows/Mac: 重启 Docker Desktop
```

#### 方案 2: 手动拉取镜像

```bash
# 使用镜像源拉取
docker pull docker.mirrors.ustc.edu.cn/library/python:3.12-slim
docker tag docker.mirrors.ustc.edu.cn/library/python:3.12-slim python:3.12-slim

docker pull docker.mirrors.ustc.edu.cn/library/node:20
docker tag docker.mirrors.ustc.edu.cn/library/node:20 node:20

docker pull docker.mirrors.ustc.edu.cn/library/redis:alpine
docker tag docker.mirrors.ustc.edu.cn/library/redis:alpine redis:alpine
```

#### 方案 3: 离线导入镜像

如果有其他可以访问 Docker Hub 的机器：

```bash
# 在可访问的机器上导出镜像
docker save python:3.12-slim node:20 redis:alpine -o mma-images.tar

# 传输到目标机器后导入
docker load -i mma-images.tar
```

## 📦 场景三：Python 包下载慢

### 问题描述

```bash
pip install -r requirements.txt
# 下载速度极慢或超时
```

### 解决方案

#### 方案 1: 使用国内镜像源

```bash
# 临时使用
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 永久配置
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

**常用镜像源**:
- 清华: `https://pypi.tuna.tsinghua.edu.cn/simple`
- 阿里云: `https://mirrors.aliyun.com/pypi/simple/`
- 中科大: `https://pypi.mirrors.ustc.edu.cn/simple/`
- 豆瓣: `http://pypi.douban.com/simple/`

#### 方案 2: 使用 uv 加速

```bash
# uv 自动使用最快的镜像源
pip install uv
uv sync
```

#### 方案 3: 离线安装

```bash
# 在有网络的机器上下载所有包
pip download -r requirements.txt -d ./packages

# 在目标机器上安装
pip install --no-index --find-links=./packages -r requirements.txt
```

## 📦 场景四：npm 包下载慢

### 问题描述

```bash
pnpm install
# 下载速度极慢
```

### 解决方案

#### 方案 1: 使用国内镜像源

```bash
# 使用淘宝镜像
pnpm config set registry https://registry.npmmirror.com

# 或使用 cnpm
npm install -g cnpm --registry=https://registry.npmmirror.com
cnpm install
```

#### 方案 2: 使用 .npmrc 配置

创建 `frontend/.npmrc` 文件：

```ini
registry=https://registry.npmmirror.com
```

#### 方案 3: 离线安装

```bash
# 在有网络的机器上
pnpm install
tar -czf node_modules.tar.gz node_modules

# 在目标机器上
tar -xzf node_modules.tar.gz
```

## 🔄 场景五：WSL 安装卡住

### 问题描述

在 Windows 上安装 Docker Desktop 时，WSL 安装进度卡在 30% 左右。

### 解决方案

#### 方案 1: 手动安装 WSL

```powershell
# 以管理员身份运行 PowerShell

# 启用 WSL 功能
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart

# 启用虚拟机功能
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

# 重启计算机
Restart-Computer

# 下载并安装 WSL2 内核更新包
# https://wslstorestorage.blob.core.windows.net/wslblob/wsl_update_x64.msi

# 设置 WSL2 为默认版本
wsl --set-default-version 2
```

#### 方案 2: 使用离线安装包

1. 下载 WSL 离线安装包
2. 手动安装
3. 重启 Docker Desktop

#### 方案 3: 使用 Hyper-V 代替 WSL2

Docker Desktop Settings -> General -> 取消勾选 "Use WSL 2 based engine"

## [object Object] 请求超时

### 问题描述

```bash
# 调用 OpenAI API 超时
Error: Request timeout after 30000ms
```

### 解决方案

#### 方案 1: 使用 API 中转服务

```bash
# backend/.env.dev
COORDINATOR_BASE_URL=https://your-proxy-api.com/v1
```

**常见中转服务**:
- OpenAI 中转
- Claude 中转
- 自建中转服务

#### 方案 2: 增加超时时间

```bash
# backend/.env.dev
API_TIMEOUT=120  # 增加到 120 秒
```

#### 方案 3: 使用国内模型

```bash
# 使用 DeepSeek（国内访问快）
COORDINATOR_MODEL=deepseek/deepseek-chat
COORDINATOR_BASE_URL=https://api.deepseek.com/v1
```

## 🛠️ 综合解决方案：完整配置

### 1. 配置系统代理

**Windows**:
```powershell
# 设置系统代理
netsh winhttp set proxy proxy-server="127.0.0.1:7890" bypass-list="localhost;127.*;10.*;172.16.*;172.17.*;172.18.*;172.19.*;172.20.*;172.21.*;172.22.*;172.23.*;172.24.*;172.25.*;172.26.*;172.27.*;172.28.*;172.29.*;172.30.*;172.31.*;192.168.*"

# 取消代理
netsh winhttp reset proxy
```

**Linux/Mac**:
```bash
# 临时设置
export http_proxy=http://127.0.0.1:7890
export https_proxy=http://127.0.0.1:7890

# 永久设置（添加到 ~/.bashrc 或 ~/.zshrc）
echo 'export http_proxy=http://127.0.0.1:7890' >> ~/.bashrc
echo 'export https_proxy=http://127.0.0.1:7890' >> ~/.bashrc
```

### 2. 配置 Docker 镜像源

```json
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com"
  ],
  "dns": ["8.8.8.8", "114.114.114.114"]
}
```

### 3. 配置 Python 镜像源

```bash
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
pip config set global.trusted-host pypi.tuna.tsinghua.edu.cn
```

### 4. 配置 npm 镜像源

```bash
pnpm config set registry https://registry.npmmirror.com
```

## 📝 完整部署流程（网络受限环境）

### 步骤 1: 准备工作

1. 在网络良好的环境下载所有必要文件
2. 打包传输到目标环境

### 步骤 2: 安装 Docker

1. 下载 Docker Desktop 离线安装包
2. 手动安装 WSL2（如需要）
3. 配置 Docker 镜像源

### 步骤 3: 获取项目代码

1. 下载项目 ZIP 包
2. 解压到本地

### 步骤 4: 配置镜像源

1. 配置 Docker 镜像源
2. 配置 pip 镜像源
3. 配置 npm 镜像源

### 步骤 5: 构建和启动

```bash
# 使用镜像源构建
docker-compose build

# 启动服务
docker-compose up -d
```

## 🔍 故障排查

### 检查网络连接

```bash
# 测试 GitHub 连接
ping github.com

# 测试 Docker Hub 连接
curl -I https://registry-1.docker.io/v2/

# 测试 PyPI 连接
curl -I https://pypi.org/simple/

# 测试 npm 连接
curl -I https://registry.npmjs.org/
```

### 检查代理设置

```bash
# 查看当前代理
echo $http_proxy
echo $https_proxy

# 查看 Git 代理
git config --global --get http.proxy

# 查看 Docker 代理
docker info | grep[object Object] 最佳实践

1. **提前准备**: 在网络良好时下载所有依赖
2. **使用镜像源**: 配置国内镜像源加速下载
3. **离线部署**: 准备离线安装包
4. **文档记录**: 记录成功的配置方案
5. **寻求帮助**: 加入社区获取支持

## 📚 相关资源

- [Docker 镜像源列表](https://github.com/docker/docker.github.io/blob/master/registry/recipes/mirror.md)
- [PyPI 镜像源帮助](https://mirrors.tuna.tsinghua.edu.cn/help/pypi/)
- [npm 镜像源帮助](https://npmmirror.com/)

## 💬 社区支持

遇到问题？

- QQ 群：699970403 / 779159301
- GitHub Issues
- Discord 社区

---

**上一页**: [常见问题](../README.md)  
**相关文档**: [安装指南](../getting-started/installation.md)
