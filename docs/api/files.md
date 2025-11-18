# API - 文件管理接口

> **文档版本**: v2.0  
> **最后更新**: 2025-01-17

这些接口提供了对每个任务工作区内文件的完整 CRUD (创建、读取、更新、删除) 操作能力。

**Base Path**: `/{task_id}/`

## 接口列表

-   `GET /{task_id}/files`: 获取任务的文件列表。
-   `POST /{task_id}/upload`: 上传文件到任务工作区。
-   `GET /{task_id}/file-content`: 获取指定文件的内容。
-   `GET /{task_id}/download-url`: 获取文件的静态下载 URL。
-   `GET /{task_id}/download-all`: 将所有文件打包为 ZIP 下载。
-   `DELETE /{task_id}/file`: 删除指定文件。

---

### `GET /{task_id}/files`

**描述**: 获取指定任务工作区内的所有文件和文件夹的列表。

**路径参数**:
-   `task_id` (string, required): 任务的唯一标识符。

**成功响应 (`200 OK`)**:

```json
{
  "files": [
    {
      "name": "notebook.ipynb",
      "type": "ipynb",
      "size": 15234,
      "path": "/static/20250117-153000-a1b2c3d4/notebook.ipynb",
      "created_at": "2025-01-17T15:35:00Z"
    },
    {
      "name": "res.md",
      "type": "md",
      "size": 8192,
      "path": "/static/20250117-153000-a1b2c3d4/res.md",
      "created_at": "2025-01-17T15:40:00Z"
    },
    {
      "name": "data/sales.csv",
      "type": "csv",
      "size": 2048,
      "path": "/static/20250117-153000-a1b2c3d4/data/sales.csv",
      "created_at": "2025-01-17T15:30:05Z"
    }
  ]
}
```

**错误响应**:
-   `404 Not Found`: 如果 `task_id` 对应的工作区不存在。

---

### `POST /{task_id}/upload`

**描述**: 上传一个或多个文件到指定任务的工作区。此接口支持在任务进行中或完成后追加文件。

**Content-Type**: `multipart/form-data`

**路径参数**:
-   `task_id` (string, required): 任务的唯一标识符。

**表单参数 (Form Data)**:
-   `files` (file, required): 一个或多个要上传的文件。

**成功响应 (`200 OK`)**:

```json
{
  "success": true,
  "uploaded_files": [
    "new_data.csv",
    "notes.txt"
  ]
}
```

**错误响应**:
-   `400 Bad Request`: 如果没有提供文件。
-   `413 Request Entity Too Large`: 如果文件大小超过服务器限制（默认为 100MB）。
-   `500 Internal Server Error`: 如果文件保存失败。

---

### `GET /{task_id}/file-content`

**描述**: 获取指定文件的文本内容，用于在前端进行预览。

**路径参数**:
-   `task_id` (string, required): 任务的唯一标识符。

**查询参数**:
-   `filename` (string, required): 要获取内容的文件名（如果文件在子目录中，需要包含相对路径，例如 `data/sales.csv`）。

**成功响应 (`200 OK`)**:

```json
{
  "content": "文件内容的字符串表示...",
  "filename": "res.md",
  "type": "md"
}
```
> **注意**: 此接口主要用于文本文件。对于二进制文件（如图片、xlsx），`content` 字段可能返回 Base64 编码的字符串或为空。

**错误响应**:
-   `404 Not Found`: 如果文件不存在。

---

### `GET /{task_id}/download-url`

**描述**: 获取一个文件的静态资源 URL，可用于直接下载或在 `<img>`、`<a href>` 等标签中使用。

**路径参数**:
-   `task_id` (string, required): 任务的唯一标识符。

**查询参数**:
-   `filename` (string, required): 文件名。

**成功响应 (`200 OK`)**:

```json
{
  "download_url": "http://localhost:8000/static/20250117-153000-a1b2c3d4/res.md"
}
```

---

### `GET /{task_id}/download-all`

**描述**: 将指定任务工作区内的所有文件和文件夹打包成一个 ZIP 压缩包供用户下载。

**路径参数**:
-   `task_id` (string, required): 任务的唯一标识符。

**成功响应 (`200 OK`)**:
-   **Content-Type**: `application/zip`
-   **Content-Disposition**: `attachment; filename={task_id}_all_files.zip`
-   **响应体**: ZIP 文件的二进制流。

**错误响应**:
-   `404 Not Found`: 如果工作区不存在。

---

### `DELETE /{task_id}/file`

**描述**: 从指定任务的工作区中删除一个文件。

**路径参数**:
-   `task_id` (string, required): 任务的唯一标识符。

**查询参数**:
-   `filename` (string, required): 要删除的文件名（支持相对路径）。

**成功响应 (`200 OK`)**:

```json
{
  "success": true,
  "message": "文件删除成功"
}
```

**错误响应**:
-   `404 Not Found`: 如果文件不存在。
-   `500 Internal[object Object]概览](overview.md)
-   [指南 - 文件上传](../guides/file-upload.md)

---

**上一页**: [建模任务接口](modeling.md)  
**下一页**: [任务历史接口](history.md)
