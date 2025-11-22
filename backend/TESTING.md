# MathModelAgent 测试指南

本文档提供 MathModelAgent 后端项目的完整测试指南。

## 目录

- [快速开始](#快速开始)
- [测试架构](#测试架构)
- [运行测试](#运行测试)
- [编写测试](#编写测试)
- [测试覆盖率](#测试覆盖率)
- [持续集成](#持续集成)
- [最佳实践](#最佳实践)
- [故障排除](#故障排除)

## 快速开始

### 安装依赖

```bash
cd backend
uv sync --dev
```

### 运行所有测试

```bash
pytest
```

### 生成覆盖率报告

```bash
pytest --cov=app --cov-report=html
```

查看报告：打开 `htmlcov/index.html`

## 测试架构

### 目录结构

```
tests/
├── conftest.py              # 全局 fixtures 和配置
├── test_main.py             # 主应用测试
├── routers/                 # API 路由测试
├── core/                    # 核心业务逻辑测试
├── services/                # 服务层测试
├── utils/                   # 工具函数测试
├── tools/                   # 工具类测试
├── models/                  # 数据模型测试
├── schemas/                 # 数据模式测试
└── config/                  # 配置测试
```

### 测试类型

1. **单元测试 (Unit Tests)**
   - 测试单个函数或方法
   - 完全隔离，使用 mock
   - 快速执行

2. **集成测试 (Integration Tests)**
   - 测试多个组件协作
   - 使用真实依赖（如 Redis）
   - 标记为 `@pytest.mark.integration`

3. **端到端测试 (E2E Tests)**
   - 测试完整工作流
   - 从 API 到数据库
   - 标记为 `@pytest.mark.e2e`

### 测试工具

- **pytest**: 测试框架
- **pytest-asyncio**: 异步测试支持
- **pytest-cov**: 覆盖率报告
- **pytest-mock**: Mock 支持
- **fakeredis**: Redis mock
- **httpx**: HTTP 客户端测试

## 运行测试

### 基本命令

```bash
# 运行所有测试
pytest

# 详细输出
pytest -v

# 显示 print 输出
pytest -s

# 组合使用
pytest -v -s
```

### 选择性运行

```bash
# 运行特定目录
pytest tests/routers/

# 运行特定文件
pytest tests/routers/test_modeling_router.py

# 运行特定测试类
pytest tests/routers/test_modeling_router.py::TestModelingRouter

# 运行特定测试方法
pytest tests/routers/test_modeling_router.py::TestModelingRouter::test_validate_api_key_valid

# 按名称匹配
pytest -k "test_api"
```

### 使用标记

```bash
# 只运行单元测试
pytest -m unit

# 只运行集成测试
pytest -m integration

# 跳过慢速测试
pytest -m "not slow"

# 组合标记
pytest -m "unit and not slow"
```

### 覆盖率报告

```bash
# 生成 HTML 报告
pytest --cov=app --cov-report=html

# 生成终端报告
pytest --cov=app --cov-report=term

# 生成 XML 报告（用于 CI）
pytest --cov=app --cov-report=xml

# 显示缺失的行
pytest --cov=app --cov-report=term-missing
```

### 失败处理

```bash
# 第一次失败时停止
pytest -x

# 最多失败 3 次后停止
pytest --maxfail=3

# 只运行上次失败的测试
pytest --lf

# 先运行失败的测试
pytest --ff
```

### 并行执行

```bash
# 安装 pytest-xdist
uv pip install pytest-xdist

# 使用所有 CPU 核心
pytest -n auto

# 使用指定数量的核心
pytest -n 4
```

### 使用测试脚本

```bash
# 基本运行
python run_tests.py

# 带覆盖率
python run_tests.py --coverage

# 详细输出
python run_tests.py --verbose

# 跳过慢速测试
python run_tests.py --fast

# 运行特定目录
python run_tests.py --directory routers

# 并行执行
python run_tests.py --parallel
```

## 编写测试

### 测试文件结构

```python
"""Tests for module_name."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.mark.asyncio
class TestClassName:
    """Test suite for ClassName."""

    @pytest.fixture
    def setup_data(self):
        """Setup test data."""
        return {"key": "value"}

    async def test_function_name(self, async_client, setup_data):
        """Test description."""
        # Arrange
        expected = "result"

        # Act
        result = await some_function(setup_data)

        # Assert
        assert result == expected
```

### 使用 Fixtures

```python
# 使用全局 fixtures
async def test_with_client(async_client):
    response = await async_client.get("/")
    assert response.status_code == 200

# 使用自定义 fixtures
@pytest.fixture
def custom_data():
    return {"test": "data"}

async def test_with_custom(custom_data):
    assert custom_data["test"] == "data"
```

### Mock 外部服务

```python
# Mock LLM 调用
@pytest.mark.asyncio
async def test_with_mock_llm(mock_llm):
    mock_llm.chat.return_value = mock_response
    result = await agent.run("prompt")
    assert result is not None

# Mock Redis
@pytest.mark.asyncio
async def test_with_redis(mock_redis_manager):
    await mock_redis_manager.redis.set("key", "value")
    value = await mock_redis_manager.redis.get("key")
    assert value == "value"

# Mock 文件操作
def test_file_operation(temp_work_dir):
    file_path = os.path.join(temp_work_dir, "test.txt")
    with open(file_path, "w") as f:
        f.write("content")
    assert os.path.exists(file_path)
```

### 测试异步函数

```python
@pytest.mark.asyncio
async def test_async_function():
    result = await async_function()
    assert result is not None

@pytest.mark.asyncio
async def test_concurrent_operations():
    import asyncio
    tasks = [async_function() for _ in range(5)]
    results = await asyncio.gather(*tasks)
    assert len(results) == 5
```

### 测试异常

```python
def test_exception_handling():
    with pytest.raises(ValueError):
        function_that_raises()

def test_exception_message():
    with pytest.raises(ValueError, match="expected message"):
        function_that_raises()
```

### 参数化测试

```python
@pytest.mark.parametrize("input,expected", [
    ("test1", "result1"),
    ("test2", "result2"),
    ("test3", "result3"),
])
def test_with_params(input, expected):
    result = function(input)
    assert result == expected
```

## 测试覆盖率

### 覆盖率目标

- **总体覆盖率**: ≥ 80%
- **核心业务逻辑**: ≥ 90%
- **工具函数**: ≥ 85%
- **路由层**: ≥ 75%

### 查看覆盖率

```bash
# 生成报告
pytest --cov=app --cov-report=html

# 在浏览器中打开
# Windows
start htmlcov/index.html

# macOS
open htmlcov/index.html

# Linux
xdg-open htmlcov/index.html
```

### 提高覆盖率

1. 识别未覆盖的代码
2. 编写针对性测试
3. 测试边界条件
4. 测试异常路径
5. 测试所有分支

## 持续集成

### GitHub Actions

测试在以下情况自动运行：
- Push 到 main/develop 分支
- 创建 Pull Request
- 修改 backend/ 目录

### 本地 CI 模拟

```bash
# 运行完整 CI 流程
./scripts/ci-local.sh

# 或手动执行
ruff check .
ruff format --check .
pytest --cov=app --cov-report=xml
```

## 最佳实践

### 1. 测试命名

- 使用描述性名称
- 遵循 `test_<功能>_<场景>` 格式
- 例如：`test_validate_api_key_invalid`

### 2. 测试独立性

- 每个测试应独立运行
- 不依赖执行顺序
- 使用 fixtures 管理状态

### 3. Mock 使用

- Mock 外部 API 调用
- Mock 慢速操作
- 保持 mock 简单

### 4. 断言清晰

```python
# 好的断言
assert response.status_code == 200
assert "error" not in result

# 避免
assert response  # 不清楚测试什么
```

### 5. 测试文档

- 每个测试添加 docstring
- 说明测试目的
- 记录特殊场景

### 6. 边界测试

- 测试空值
- 测试极限值
- 测试无效输入

## 故障排除

### 常见问题

#### 1. Redis 连接错误

**问题**: `ConnectionError: Error connecting to Redis`

**解决**: 测试使用 FakeRedis，检查 `conftest.py` 配置

#### 2. 异步测试失败

**问题**: `RuntimeError: Event loop is closed`

**解决**: 确保使用 `@pytest.mark.asyncio` 装饰器

#### 3. 导入错误

**问题**: `ModuleNotFoundError: No module named 'app'`

**解决**: 检查 `pytest.ini` 中的 `pythonpath` 配置

#### 4. Fixture 未找到

**问题**: `fixture 'fixture_name' not found`

**解决**: 确保 fixture 在 `conftest.py` 中定义或正确导入

### 调试技巧

```bash
# 显示详细错误信息
pytest -vv

# 进入调试器
pytest --pdb

# 在第一个失败时进入调试器
pytest -x --pdb

# 显示局部变量
pytest -l

# 显示完整的 traceback
pytest --tb=long
```

### 性能分析

```bash
# 显示最慢的 10 个测试
pytest --durations=10

# 显示所有测试时间
pytest --durations=0
```

## 参考资源

- [pytest 官方文档](https://docs.pytest.org/)
- [pytest-asyncio 文档](https://pytest-asyncio.readthedocs.io/)
- [FastAPI 测试指南](https://fastapi.tiangolo.com/tutorial/testing/)
- [Python unittest.mock](https://docs.python.org/3/library/unittest.mock.html)
