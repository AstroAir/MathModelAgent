# API - 设置接口

> **文档版本**: v2.0  
> **最后更新**: 2025-01-17

这些接口用于管理用户相关的设置，如个人资料和偏好。当前版本主要为前端提供模拟数据，尚未连接到持久化数据库。

**Base Path**: `/api/settings`

## 接口列表

-   `GET /api/settings/profile`: 获取用户个人资料。
-   `PUT /api/settings/profile`: 更新用户个人资料。
-   `GET /api/settings/preferences`: 获取用户偏好设置。
-   `PUT /api/settings/preferences`: 更新用户偏好设置。
-   `GET /api/settings/security/sessions`: 获取活动会话列表。

---

### `GET /api/settings/profile`

**描述**: 获取当前用户的个人资料信息。

**成功响应 (`200 OK`)**:

```json
{
  "name": "默认用户",
  "email": "user@example.com",
  "avatar": "/path/to/default/avatar.png",
  "bio": "数学建模爱好者",
  "phone": "+86 1234567890",
  "timezone": "Asia/Shanghai",
  "language": "zh"
}
```

---

### `PUT /api/settings/profile`

**描述**: 更新用户的个人资料信息。

**请求体 (JSON)**:

```json
{
  "name": "新用户名",
  "email": "new.email@example.com",
  "bio": "更新后的个人简介。"
}
```

**成功响应 (`200 OK`)**:

```json
{
  "success": true,
  "message": "Profile updated successfully"
}
```

---

### `GET /api/settings/preferences`

**描述**: 获取用户的界面和行为偏好设置。

**成功响应 (`200 OK`)**:

```json
{
  "theme": "dark",
  "notifications_enabled": true,
  "email_notifications": false,
  "auto_save": true,
  "default_language": "zh"
}
```

---

### `PUT /api/settings/preferences`

**描述**: 更新用户的偏好设置。

**请求体 (JSON)**:

```json
{
  "theme": "light",
  "notifications_enabled": false
}
```

**成功响应 (`200 OK`)**:

```json
{
  "success": true,
  "message": "Preferences updated successfully"
}
```

---

### `GET /api/settings/security/sessions`

**描述**: 获取用户当前活动的会话列表（模拟数据）。

**成功响应 (`200 OK`)**:

```json
[
  {
    "session_id": "sess_001",
    "device": "Chrome on Windows",
    "location": "Beijing, China",
    "last_active": "2025-01-17T16:00:00Z",
    "current": true
  },
  {
    "session_id": "sess_002",
    "device": "Safari on iPhone",
    "location": "Shanghai, China",
    "last_active": "2025-01-16T10:30:00Z",
    "current": false
  }
]
```

## 📚 相关文档

-   [API 概览](overview.md)

---

**上一页**: [搜索接口](search.md)  
**下一页**: [Prompt 优化接口](prompt.md)
