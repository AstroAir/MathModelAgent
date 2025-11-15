# 历史记录管理功能说明

## 功能概述

为 MathModelAgent 的 chat 页面侧边栏添加了完整的历史记录管理系统，支持任务分类、收藏（pin）功能，以及完整的后端数据持久化。

## 主要功能

### 1. 历史记录展示
- **自动记录**：每次创建新任务（自定义任务或示例任务）时自动保存到历史记录
- **实时状态**：显示任务状态（处理中、已完成、失败）
- **详细信息**：包含任务标题、描述、创建时间、文件数量、任务类型等信息

### 2. 任务分类
支持四种筛选模式：
- **全部**：显示所有历史任务
- **收藏**：仅显示已收藏的任务
- **自定义**：显示用户创建的自定义任务
- **示例**：显示从示例库选择的任务

### 3. 收藏功能
- 可以快速收藏/取消收藏任务
- 收藏的任务在列表中优先显示
- 支持收藏筛选，快速找到重要任务

### 4. 任务管理
- **删除任务**：可以删除不需要的历史记录
- **刷新列表**：手动刷新获取最新状态
- **状态图标**：直观显示任务完成状态

## 技术实现

### 后端实现

#### 1. 数据模型 (`backend/app/models/task_history.py`)
```python
class TaskHistoryItem:
    - task_id: 任务ID
    - title: 任务标题
    - description: 任务描述
    - task_type: 任务类型（custom/example）
    - comp_template: 比赛模板类型
    - is_pinned: 是否收藏
    - created_at: 创建时间
    - updated_at: 更新时间
    - status: 任务状态（processing/completed/failed）
    - file_count: 文件数量
```

#### 2. API 路由 (`backend/app/routers/history_router.py`)
提供完整的 RESTful API：
- `POST /history/tasks` - 创建历史记录
- `GET /history/tasks` - 获取历史记录列表（支持筛选）
- `GET /history/tasks/{task_id}` - 获取单个历史记录
- `PATCH /history/tasks/{task_id}` - 更新历史记录
- `POST /history/tasks/{task_id}/toggle-pin` - 切换收藏状态
- `DELETE /history/tasks/{task_id}` - 删除历史记录
- `GET /history/tasks/count` - 获取任务数量统计

#### 3. 数据存储
- 使用 JSON 文件持久化存储：`logs/task_history.json`
- 自动备份和恢复机制
- 支持并发访问

#### 4. 集成到任务流程
- 在 `modeling_router.py` 中集成
- 任务创建时自动保存历史记录
- 任务完成/失败时自动更新状态

### 前端实现

#### 1. 类型定义 (`frontend/src/types/history.ts`)
完整的 TypeScript 类型定义，确保类型安全

#### 2. API 封装 (`frontend/src/apis/historyApi.ts`)
- 封装所有历史记录相关的 API 调用
- 统一错误处理
- 支持 TypeScript 类型推断

#### 3. UI 组件重构 (`frontend/src/components/AppSidebar.vue`)
- 完全重构侧边栏组件
- 添加筛选器UI
- 实现任务列表展示
- 支持收藏和删除操作
- 响应式设计，移动端友好

#### 4. 交互特性
- **悬停效果**：鼠标悬停显示操作按钮
- **加载状态**：显示加载动画
- **空状态提示**：无数据时显示友好提示
- **时间格式化**：智能显示相对时间（刚刚、几分钟前、昨天等）
- **状态图标**：不同状态使用不同颜色和图标

## 使用说明

### 用户操作流程

1. **查看历史记录**
   - 打开侧边栏，自动加载历史记录
   - 使用筛选器查看不同类型的任务

2. **收藏任务**
   - 鼠标悬停在任务上
   - 点击 Pin 图标收藏任务
   - 收藏的任务会显示黄色图钉图标

3. **删除任务**
   - 鼠标悬停在任务上
   - 点击更多按钮（⋮）
   - 选择"删除"选项

4. **查看任务详情**
   - 任务卡片显示标题、描述、时间、文件数量
   - 状态图标显示任务进度

### 开发者说明

#### 添加新的筛选条件
在 `AppSidebar.vue` 的 `filteredTasks` computed 中添加新的过滤逻辑：

```typescript
const filteredTasks = computed(() => {
  switch (activeFilter.value) {
    case 'your_new_filter':
      return historyTasks.value.filter(task => /* your logic */)
    // ...
  }
})
```

#### 扩展历史记录字段
1. 在 `backend/app/models/task_history.py` 中的 `TaskHistoryItem` 添加字段
2. 在 `frontend/src/types/history.ts` 中同步更新类型定义
3. 更新 UI 组件显示新字段

#### 自定义存储方式
默认使用 JSON 文件存储，如需使用数据库：
1. 修改 `TaskHistoryManager` 类的存储方法
2. 实现数据库连接和 CRUD 操作
3. 保持 API 接口不变

## 数据结构示例

### 历史记录存储格式
```json
[
  {
    "task_id": "20241116_023456_abc123",
    "title": "数学建模竞赛题目分析...",
    "description": "问题1：建立数学模型分析...",
    "task_type": "custom",
    "comp_template": "CHINA",
    "is_pinned": true,
    "created_at": "2024-11-16T02:34:56.123456",
    "updated_at": "2024-11-16T02:35:00.123456",
    "status": "completed",
    "file_count": 3
  }
]
```

## 注意事项

1. **性能优化**
   - 历史记录列表使用虚拟滚动（ScrollArea）
   - 大量数据时建议添加分页功能

2. **数据安全**
   - 删除操作需要用户确认
   - 建议定期备份 `logs/task_history.json`

3. **并发处理**
   - 当前使用文件锁防止并发写入
   - 生产环境建议使用数据库

4. **浏览器兼容性**
   - 使用现代 ES6+ 特性
   - 需要支持 CSS Grid 和 Flexbox

## 未来改进方向

1. **搜索功能**：添加任务搜索和全文搜索
2. **标签系统**：支持给任务打标签
3. **导出功能**：导出历史记录为 CSV/Excel
4. **分页加载**：支持大量历史记录的分页
5. **任务详情页**：点击任务跳转到详情页面
6. **批量操作**：支持批量删除、批量收藏
7. **统计图表**：任务完成率、时间分布等统计

## 相关文件

### 后端
- `backend/app/models/task_history.py` - 数据模型
- `backend/app/routers/history_router.py` - API 路由
- `backend/app/routers/modeling_router.py` - 任务创建集成
- `backend/app/main.py` - 路由注册

### 前端
- `frontend/src/types/history.ts` - 类型定义
- `frontend/src/apis/historyApi.ts` - API 封装
- `frontend/src/components/AppSidebar.vue` - UI 组件

### 数据
- `logs/task_history.json` - 历史记录存储文件
