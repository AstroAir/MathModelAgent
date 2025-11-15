# 文件上传功能升级说明

## 更新内容

本次更新优化了 MathModelAgent 的文件上传功能，新增对文件夹和压缩包的支持。

## 主要变更

### 前端变更

**文件**: `frontend/src/components/UserStepper.vue`

- ✅ 添加"上传文件夹"按钮，支持选择整个文件夹
- ✅ 更新文件类型支持：`.zip`, `.rar`, `.7z`, `.tar`, `.tar.gz` 等
- ✅ 优化文件列表显示，显示文件大小信息
- ✅ 添加拖拽文件提示
- ✅ 引入新图标：`FolderUp`, `FileArchive`

### 后端变更

**新增文件**: `backend/app/utils/file_utils.py`
- 压缩包检测功能
- 多格式解压支持（ZIP, RAR, 7Z, TAR）
- 文件夹结构处理
- 文件树生成工具

**更新文件**: `backend/app/routers/modeling_router.py`
- 支持文件夹路径保存（保留目录结构）
- 自动检测并解压压缩包
- 准确统计解压后的文件数量
- 解压成功后自动清理原始压缩包

**依赖更新**: `backend/pyproject.toml`
- 添加 `py7zr>=0.22.0` - 7Z 格式支持
- 添加 `rarfile>=4.2` - RAR 格式支持

## 安装步骤

### 1. 更新前端依赖（如有需要）

```bash
cd frontend
npm install
```

### 2. 更新后端依赖

```bash
cd backend
# 使用 uv（推荐）
uv sync

# 或使用 pip
pip install py7zr rarfile
```

### 3. RAR 支持（可选）

如果需要支持 RAR 格式，还需要安装 unrar 工具：

**Windows**:
- 下载并安装 [WinRAR](https://www.rarlab.com/download.htm)
- 或下载 unrar.exe 并添加到 PATH

**Linux**:
```bash
sudo apt-get install unrar
```

**macOS**:
```bash
brew install unrar
```

## 功能测试

### 测试场景 1: 上传单个文件

1. 启动应用
2. 进入 chat 页面
3. 点击"上传文件"按钮
4. 选择一个或多个文件（如 data.csv）
5. 验证文件显示在列表中

### 测试场景 2: 上传文件夹

1. 点击"上传文件夹"按钮
2. 选择一个包含多个文件的文件夹
3. 验证所有文件都显示在列表中
4. 提交任务后，检查后端日志，确认目录结构被保留

### 测试场景 3: 上传压缩包

1. 准备一个 ZIP 或 RAR 文件（包含多个数据文件）
2. 点击"上传文件"按钮
3. 选择压缩包文件
4. 提交任务
5. 检查后端日志：
   - 应显示"检测到压缩包"
   - 应显示"成功解压 X 个文件"
   - 应显示"已删除原始压缩包"

### 测试场景 4: 混合上传

1. 同时上传：
   - 一个普通文件（如 problem.txt）
   - 一个压缩包（如 data.zip）
2. 验证所有文件都被正确处理

## 预期行为

### 成功上传后
- 前端显示：✅ 已选择 X 个文件
- 文件列表显示所有文件名和大小
- 进度提示显示"文件上传成功"

### 压缩包处理
- 后端自动检测压缩包格式
- 自动解压到工作目录
- 保留解压后的目录结构
- 删除原始压缩包文件
- 统计并记录实际文件数量

### 文件夹上传
- 前端使用 `webkitdirectory` 属性
- 保留完整的文件路径信息
- 后端重建目录结构

## 日志检查

启动后端时，关注以下日志：

```
INFO: 开始处理上传的文件，工作目录: /path/to/work_dir
INFO: 保存文件: data.csv -> /path/to/work_dir/data.csv
INFO: 检测到压缩包: dataset.zip
INFO: 开始解压 1 个压缩包
INFO: 开始解压 ZIP 文件: /path/to/work_dir/dataset.zip
INFO: ZIP 文件包含 5 个文件
INFO: 成功解压 5 个文件
INFO: 已删除原始压缩包: /path/to/work_dir/dataset.zip
INFO: 文件处理完成，共 5 个文件
```

## 故障排查

### 问题 1: RAR 文件解压失败

**错误信息**:
```
ERROR: RAR解压失败: Cannot find working tool
```

**解决方法**:
- 安装 unrar 工具（见上文安装步骤）
- 重启应用

### 问题 2: 7Z 文件无法解压

**错误信息**:
```
ERROR: 不支持 7Z 格式（需要安装 py7zr 库）
```

**解决方法**:
```bash
pip install py7zr
```

### 问题 3: 文件夹上传按钮无响应

**可能原因**:
- 浏览器不支持 `webkitdirectory` 属性

**解决方法**:
- 使用 Chrome、Edge 或 Firefox 浏览器
- 或将文件夹压缩为 ZIP 后上传

### 问题 4: 文件数量统计不准确

**检查点**:
1. 查看后端日志中的文件处理信息
2. 确认压缩包是否成功解压
3. 检查是否有文件被过滤

## 兼容性说明

### 浏览器兼容性

| 浏览器 | 文件上传 | 文件夹上传 | 压缩包上传 |
|--------|---------|-----------|-----------|
| Chrome | ✅ | ✅ | ✅ |
| Firefox | ✅ | ✅ | ✅ |
| Edge | ✅ | ✅ | ✅ |
| Safari | ✅ | ⚠️ (部分支持) | ✅ |

### 压缩格式支持

| 格式 | 支持状态 | 依赖 |
|------|---------|------|
| ZIP | ✅ 原生支持 | Python 内置 |
| TAR | ✅ 原生支持 | Python 内置 |
| TAR.GZ | ✅ 原生支持 | Python 内置 |
| RAR | ✅ 需要额外工具 | rarfile + unrar |
| 7Z | ✅ 需要额外库 | py7zr |

## 回滚方案

如果出现问题，可以回滚到之前的版本：

```bash
# 前端
git checkout HEAD~1 frontend/src/components/UserStepper.vue

# 后端
git checkout HEAD~1 backend/app/routers/modeling_router.py
rm backend/app/utils/file_utils.py

# 恢复依赖文件
git checkout HEAD~1 backend/pyproject.toml
```

## 相关文档

- 详细使用指南：`docs/md/file-upload-guide.md`
- 前端组件：`frontend/src/components/UserStepper.vue`
- 后端工具：`backend/app/utils/file_utils.py`
- 后端路由：`backend/app/routers/modeling_router.py`

## 反馈与支持

如遇到问题或有改进建议，请：
1. 查看日志文件
2. 检查依赖是否正确安装
3. 提交 Issue 或联系技术支持
