import os
import tempfile
import shutil
from typing import AsyncIterator, Generator
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import AsyncClient

# Import app components for mocking
from app.main import app
from app.services.redis_manager import redis_manager
from app.services.ws_manager import ws_manager
from app.core.llm.llm import LLM
from app.utils.task_logger import TaskLogger
from app.config.setting import settings


@pytest.fixture(scope="session", autouse=True)
def _set_test_env() -> None:
    """Set ENV for tests so Settings.from_env can use .env.test if needed."""
    os.environ.setdefault("ENV", "test")


@pytest.fixture(scope="session", autouse=True)
def _setup_fake_redis():
    """Provide a shared fakeredis client for all tests and patch redis_manager."""
    from fakeredis.aioredis import FakeRedis
    from app.services import redis_manager as rm_module

    fake = FakeRedis(decode_responses=True)
    rm_module.redis_manager._client = fake
    setattr(rm_module.redis_manager, "redis", fake)
    yield


@pytest.fixture(scope="session")
def app_fixture():
    """Import FastAPI app once for all tests."""

    return app


@pytest.fixture()
async def async_client(app_fixture) -> AsyncIterator[AsyncClient]:
    """Async HTTP client for testing FastAPI endpoints."""
    from httpx import ASGITransport

    transport = ASGITransport(app=app_fixture)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


@pytest.fixture(autouse=True)
def patch_settings_defaults(monkeypatch):
    """Ensure critical settings attributes exist during tests.

    This avoids AttributeError when code accesses optional settings
    like DEEPSEEK_MODEL in common_router.
    """

    defaults = {
        "ENV": "test",
        "DEEPSEEK_MODEL": "test-deepseek-model",
        "DEEPSEEK_BASE_URL": "http://deepseek.local/v1",
    }

    for key, value in defaults.items():
        # 在测试环境中强制覆盖为测试配置值
        setattr(settings, key, value)


@pytest.fixture(scope="session")
def event_loop():  # type: ignore[override]
    """Custom event loop fixture compatible with pytest-asyncio."""
    import asyncio

    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# ============ Temporary Directory Fixtures ============


@pytest.fixture
def temp_work_dir() -> Generator[str, None, None]:
    """Create a temporary work directory for testing."""
    temp_dir = tempfile.mkdtemp(prefix="test_work_dir_")
    yield temp_dir
    # Cleanup
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


@pytest.fixture
def temp_upload_dir() -> Generator[str, None, None]:
    """Create a temporary upload directory for testing."""
    temp_dir = tempfile.mkdtemp(prefix="test_upload_")
    yield temp_dir
    # Cleanup
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


# ============ Mock LLM Fixtures ============


@pytest.fixture
def mock_llm_response():
    """Mock LLM response object."""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Test LLM response"
    mock_response.choices[0].message.tool_calls = None
    mock_response.usage.total_tokens = 100
    mock_response.usage.prompt_tokens = 50
    mock_response.usage.completion_tokens = 50
    return mock_response


@pytest.fixture
def mock_llm(mock_llm_response):
    """Mock LLM instance with async chat method."""
    llm = AsyncMock(spec=LLM)
    llm.chat.return_value = mock_llm_response
    llm.model_name = "test-model"
    llm.api_key = "test-key"
    llm.base_url = "http://test.local"
    return llm


# ============ Mock Task Logger Fixtures ============


@pytest.fixture
def mock_task_logger():
    """Mock TaskLogger instance."""
    logger = AsyncMock(spec=TaskLogger)
    logger.info = AsyncMock()
    logger.error = AsyncMock()
    logger.warning = AsyncMock()
    logger.debug = AsyncMock()
    return logger


# ============ Mock Redis Fixtures ============


@pytest.fixture
async def mock_redis_manager():
    """Mock redis_manager for testing."""
    from fakeredis.aioredis import FakeRedis

    fake_redis = FakeRedis(decode_responses=True)
    original_client = redis_manager._client

    # Replace with fake redis
    redis_manager._client = fake_redis
    setattr(redis_manager, "redis", fake_redis)

    yield redis_manager

    # Restore original
    redis_manager._client = original_client


# ============ Mock WebSocket Manager Fixtures ============


@pytest.fixture
def mock_ws_manager():
    """Mock WebSocket manager."""
    manager = AsyncMock(spec=ws_manager.__class__)
    manager.connect = AsyncMock()
    manager.disconnect = AsyncMock()
    manager.send_message = AsyncMock()
    manager.broadcast = AsyncMock()
    return manager


# ============ Mock Code Interpreter Fixtures ============


@pytest.fixture
def mock_code_interpreter():
    """Mock code interpreter (local or E2B)."""
    interpreter = AsyncMock()
    interpreter.execute_code.return_value = {
        "success": True,
        "output": "Test output",
        "error": None,
        "logs": ["Log line 1", "Log line 2"],
    }
    interpreter.close = AsyncMock()
    return interpreter


# ============ Test Data Fixtures ============


@pytest.fixture
def sample_task_id() -> str:
    """Sample task ID for testing."""
    return "test_task_123456"


@pytest.fixture
def sample_problem_data() -> dict:
    """Sample problem data for testing."""
    return {
        "problem": "测试问题描述",
        "template": "国赛",
        "language": "zh",
        "format_output": "markdown",
    }


@pytest.fixture
def sample_upload_file():
    """Create a sample upload file for testing."""
    from fastapi import UploadFile
    from io import BytesIO

    content = b"Test file content\nLine 2\nLine 3"
    file = UploadFile(filename="test.txt", file=BytesIO(content))
    return file


# ============ Mock External API Fixtures ============


@pytest.fixture
def mock_litellm_completion(monkeypatch):
    """Mock litellm.acompletion for testing."""

    async def mock_completion(*args, **kwargs):
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Mocked LLM response"
        mock_response.choices[0].message.tool_calls = None
        mock_response.usage.total_tokens = 100
        mock_response.usage.prompt_tokens = 50
        mock_response.usage.completion_tokens = 50
        return mock_response

    import litellm

    monkeypatch.setattr(litellm, "acompletion", mock_completion)
    return mock_completion
