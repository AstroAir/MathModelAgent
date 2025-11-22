import pytest


@pytest.mark.asyncio
async def test_root_endpoint(async_client):
    response = await async_client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "Hello World"


@pytest.mark.asyncio
async def test_config_endpoint(async_client):
    response = await async_client.get("/config")
    assert response.status_code == 200
    data = response.json()
    assert data["environment"] == "test"
    assert "max_chat_turns" in data
    assert "max_retries" in data


@pytest.mark.asyncio
async def test_status_endpoint_uses_mock_redis(async_client):
    """Service status endpoint should return redis status without real Redis."""
    response = await async_client.get("/status")
    assert response.status_code == 200
    data = response.json()
    assert "backend" in data
    assert "redis" in data


@pytest.mark.asyncio
async def test_task_status_not_found(async_client):
    response = await async_client.get("/task-status/non-existent-task")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] in {"not_found", "error"}
