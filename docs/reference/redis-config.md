# 参考 - Redis 配置

> **文档版本**: v2.0  
> **最后更新**: 2025-01-17

本指南详细说明了 Redis 在 MathModelAgent 项目中的作用、安装方法和配置选项。

## 📋 Redis 的作用

**Redis 是 MathModelAgent 的一个必需依赖**。它在系统中扮演着至关重要的角色：

1.  **任务状态管理**: 存储每个任务的基本信息和当前状态（处理中、已完成、失败）。
2.  **WebSocket 消息队列**: 作为发布/订阅 (Pub/Sub) 系统，将后端 Agent 生成的实时消息广播给前端客户端。
3.  **任务ID验证**: 快速验证 WebSocket 连接请求的 `task_id` 是否有效。
4.  **分布式锁 (未来)**: 为多实例部署提供并发控制。

## ⚙️ 配置环境变量

Redis 的连接信息通过 `backend/.env.dev` 文件中的环境变量进行配置。

-   `REDIS_URL`
    -   **描述**: Redis 服务的连接 URL。
    -   **格式**: `redis://[username:password@]host:port/db`
    -   **示例**:
        -   **本地无密码 (默认)**: `redis://localhost:6379/0`
        -   **本地有密码**: `redis://:your_password@localhost:6379/0`
        -   **Docker 环境**: `redis://redis:6379/0` (使用服务名 `redis` 作为主机名)

-   `REDIS_MAX_CONNECTIONS`
    -   **描述**: Redis 连接池的最大连接数。
    -   **默认值**: `20`

## 🚀 本地安装 Redis

如果您选择本地部署（非 Docker），您需要手动安装并运行 Redis 服务。

### Windows

**方法一：使用 WSL (推荐)**
1.  安装 [WSL (Windows Subsystem for Linux)](https://learn.microsoft.com/en-us/windows/wsl/install)。
2.  在 WSL 的 Linux 发行版（如 Ubuntu）中安装 Redis:
    ```bash
    sudo apt-get update
    sudo apt-get install redis-server
    ```
3.  启动 Redis 服务:
    ```bash
    sudo service redis-server start
    ```

**方法二：使用 Memurai (Redis for Windows)**
1.  下载并安装 [Memurai](https://www.memurai.com/)
2.  安装后，它会作为一个 Windows 服务自动运行。

**方法三：使用旧版 Redis (不推荐)**
1.  从 [MSOpenTech/redis releases](https://github.com/microsoftarchive/redis/releases) 下载 `Redis-x64-*.msi`。
2.  运行安装程序。

### macOS

使用 [Homebrew](https://brew.sh/) 是最简单的方式。

```bash
# 安装 Redis
brew install redis

# 启动 Redis 服务并设置为开机自启
brew services start redis
```

### Linux (Ubuntu/Debian)

```bash
sudo apt-get update
sudo apt-get install redis-server

# 启动 Redis 服务并设置为开机自启
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

## ✅ 验证 Redis 连接

无论您如何安装，都可以通过 `redis-cli` 工具来验证服务是否正常运行。

```bash
# 打开终端并执行
redis-cli ping
```

如果 Redis 服务正常，它将返回：
```
PONG
```

您还可以通过访问后端的 `/status` 端点来检查连接状态：
```bash
curl http://localhost:8000/status
```
响应中 `redis.status` 应为 `running`。

## ❓ 常见问题

### Q: 启动后端时报错 `ConnectionRefusedError`？

**A**: 这意味着后端无法连接到 Redis。请检查：
1.  **Redis 服务是否已启动？** 运行 `redis-cli ping` 进行检查。
2.  **`REDIS_URL` 是否正确？** 确认主机名、端口和密码（如果有）是否正确。
3.  **防火墙是否拦截？** 确保防火墙没有阻止 `6379` 端口的连接。
4.  **Docker 环境？** 如果您在 Docker 中运行后端，但在主机上运行 Redis，`REDIS_URL` 的主机名不能是 `localhost`，而应该是您的主机的局域网 IP 地址或 Docker 的特殊 DNS 名称 `host.docker.internal`。
    ```bash
    # 示例：在 Docker 容器中连接主机上的 Redis
    REDIS_URL=redis://host.docker.internal:6379/0
    ```

### Q: 我需要修改 Redis 的默认配置吗？

**A**: 对于本地开发和测试，默认配置通常足够了。在生产环境中，您可能需要根据负载情况调整 `redis.conf` 文件，例如设置 `maxmemory` 和持久化策略。

## 📚 相关文档

-   [指南 - 快速安装](../getting-started/installation.md)
-   [参考 - 环境变量](environment-variables.md)
-   [参考 - Docker 配置](docker-config.md)

---

**上一页**: [Docker 配置](docker-config.md)  
**文档首页**: [../README.md](../README.md)
