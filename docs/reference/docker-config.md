# 参考 - Docker 配置

> **文档版本**: v2.0  
> **最后更新**: 2025-01-17

本指南详细解析项目根目录下的 `docker-compose.yml` 文件，帮助您理解和自定义 Docker 部署。

## 📋 文件概览

`docker-compose.yml` 定义了运行 MathModelAgent 所需的三个核心服务：

1.  `redis`: Redis 缓存和消息队列服务。
2.  `backend`: FastAPI 后端应用程序。
3.  `frontend`: Vue.js 前端应用程序。

## ⚙️ 服务详解

### 1. `redis` 服务

```yaml
services:
  redis:
    image: redis:alpine
    container_name: mathmodelagent_redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
```

-   `image: redis:alpine`: 使用轻量级的 `alpine` 版 Redis 镜像。
-   `container_name`: 为容器指定一个易于识别的名称。
-   `ports`: 将容器的 `6379` 端口映射到主机的 `6379` 端口。这意味着您可以在主机上通过 `localhost:6379` 访问 Redis。
-   `volumes`: 使用名为 `redis_data` 的 Docker 卷来持久化 Redis 数据。即使容器被删除，数据（如任务历史）也不会丢失。

### 2. `backend` 服务

```yaml
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: mathmodelagent_backend
    ports:
      - "8000:8000"
    env_file:
      - ./backend/.env.dev
    environment:
      - ENV=DEV
      # 在 Docker 网络中，Redis 的地址是服务名 `redis`
      - REDIS_URL=redis://redis:6379/0
    volumes:
      - ./backend:/app
      - ./backend/project/work_dir:/app/project/work_dir
    depends_on:
      - redis
```

-   `build`: 指示 Docker Compose 从 `./backend` 目录下的 `Dockerfile` 构建镜像。
-   `ports`: 将容器的 `8000` 端口映射到主机的 `8000` 端口。
-   `env_file`: 从 `./backend/.env.dev` 文件加载环境变量。
-   `environment`: 可以在此直接设置或覆盖环境变量。**重要**: 在 Docker Compose 网络中，后端服务通过服务名 `redis` 来访问 Redis 容器，因此 `REDIS_URL` 必须设置为 `redis://redis:6379/0`。通常建议在 `.env.dev` 文件中直接使用这个值。
-   `volumes`:
    -   `./backend:/app`: 将主机的 `./backend` 目录挂载到容器的 `/app` 目录。这实现了**代码热重载**：您在主机上修改后端代码，容器内的服务会自动重启，无需重新构建镜像。
    -   `./backend/project/work_dir:/app/project/work_dir`: 将任务生成的文件（代码、论文、图表等）持久化到主机上，防止容器删除后丢失。
-   `depends_on`: 确保 `redis` 服务在 `backend` 服务启动之前完全启动。

### 3. `frontend` 服务

```yaml
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: mathmodelagent_frontend
    ports:
      - "5173:5173"
    env_file:
      - ./frontend/.env.development
    volumes:
      - ./frontend:/app
      - /app/node_modules
    depends_on:
      - backend
```

-   `build`: 从 `./frontend` 目录下的 `Dockerfile` 构建镜像。
-   `ports`: 将 Vite 开发服务器的默认端口 `5173` 映射到主机。
-   `env_file`: 从 `./frontend/.env.development` 加载前端环境变量。
-   `volumes`:
    -   `./frontend:/app`: 挂载前端代码以实现热重载。
    -   `/app/node_modules`: 这是一个**匿名卷**。它的作用是防止主机上的 `node_modules` 目录（如果存在）覆盖容器在构建时安装的 `node_modules` 目录。这是一个标准的 Docker 开发技巧。
-   `depends_on`: 确保 `backend` 服务先于 `frontend` 启动。

## 📦 卷 (Volumes) 详解

```yaml
volumes:
  redis_data:
  backend_venv:
```

-   `redis_data`: 这是一个**命名卷**，由 Docker 管理，用于持久化存储 Redis 的数据。
-   `backend_venv`: (可选) 用于持久化 Python 虚拟环境，可以在依赖不变的情况下加快后续构建速度。

## 🚀 常用 Docker 命令

在项目根目录下执行：

-   **构建并启动所有服务 (前台运行)**:
    ```bash
    docker-compose up --build
    ```

-   **在后台启动所有服务**:
    ```bash
    docker-compose up -d
    ```

-   **停止所有服务**:
    ```bash
    docker-compose down
    ```

-   **停止并删除卷 (清除所有数据)**:
    > **警告**: 此操作会删除所有 Redis 数据和任务文件！
    ```bash
    docker-compose down -v
    ```

-   **查看服务日志**:
    ```bash
    # 查看所有服务的日志
    docker-compose logs -f

    # 只查看后端服务的日志
    docker-compose logs -f backend
    ```

-   **进入容器执行命令**:
    ```bash
    # 进入后端容器的 shell
    docker-compose exec backend bash
    ```

## 💡 自定义技巧

### 修改端口

如果主机的 `8000` 或 `5173` 端口已被占用，您可以修改端口映射。

```yaml
# 将后端的 8000 端口映射到主机的 8001
ports:
  - "8001:8000"
```
修改后，您需要通过 `http://localhost:8001` 访问后端。

### 生产环境部署

当前的 `docker-compose.yml` 主要为开发环境设计（包含代码热重载）。在生产环境中，您可能需要：

-   创建一个生产专用的 `docker-compose.prod.yml`。
-   移除 `volumes` 中的代码挂载，将代码直接复制到镜像中。
-   使用 Gunicorn 或其他 WSGI 服务器运行 FastAPI。
-   使用 Nginx 作为反向代理来处理 HTTPS 和静态文件。

## 📚 相关文档

-   [指南 - 快速安装](../getting-started/installation.md)
-   [参考 - 环境变量](environment-variables.md)

---

**上一页**: [提示词模板](prompt-templates.md)  
**下一页**: [Redis 配置](redis-config.md)
