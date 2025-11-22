"""Tests for history router endpoints."""

import pytest
from httpx import AsyncClient
from unittest.mock import patch
from datetime import datetime
from app.models.task_history import TaskHistoryItem


@pytest.mark.asyncio
class TestHistoryRouter:
    """Test suite for history router."""

    async def test_get_task_history_list(self, async_client: AsyncClient):
        """Test getting task history list."""
        with patch(
            "app.models.task_history.task_history_manager.get_all_tasks"
        ) as mock_get:
            mock_get.return_value = [
                {
                    "task_id": "task1",
                    "problem": "Problem 1",
                    "status": "completed",
                    "created_at": datetime.now().isoformat(),
                },
                {
                    "task_id": "task2",
                    "problem": "Problem 2",
                    "status": "running",
                    "created_at": datetime.now().isoformat(),
                },
            ]

            response = await async_client.get("/history/tasks")

            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            assert len(data) == 2

    async def test_get_task_history_empty(self, async_client: AsyncClient):
        """Test getting empty task history."""
        with patch(
            "app.models.task_history.task_history_manager.get_all_tasks"
        ) as mock_get:
            mock_get.return_value = []

            response = await async_client.get("/history/tasks")

            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, dict)
            assert data["total"] == 0
            assert data["tasks"] == []

    async def test_get_specific_task(self, async_client: AsyncClient, sample_task_id):
        """Test getting specific task details."""
        mock_task = {
            "task_id": sample_task_id,
            "problem": "Test problem",
            "status": "completed",
            "created_at": datetime.now().isoformat(),
            "template": "国赛",
            "language": "zh",
        }

        with patch("app.models.task_history.task_history_manager.get_task") as mock_get:
            mock_get.return_value = mock_task

            response = await async_client.get(f"/history/tasks/{sample_task_id}")

            assert response.status_code == 200
            data = response.json()
            assert data["task_id"] == sample_task_id

    async def test_get_nonexistent_task(self, async_client: AsyncClient):
        """Test getting nonexistent task."""
        with patch("app.models.task_history.task_history_manager.get_task") as mock_get:
            mock_get.return_value = None

            response = await async_client.get("/history/tasks/nonexistent_task")

            assert response.status_code == 404

    async def test_update_task(self, async_client: AsyncClient, sample_task_id):
        """Test updating task information."""
        update_data = {
            "title": "Updated problem description",
            "status": "completed",
        }

        mock_task = TaskHistoryItem(
            task_id=sample_task_id,
            title="Updated problem description",
            status="completed",
        )

        with patch(
            "app.models.task_history.task_history_manager.update_task"
        ) as mock_update:
            mock_update.return_value = mock_task

            response = await async_client.patch(
                f"/history/tasks/{sample_task_id}", json=update_data
            )

            assert response.status_code == 200
            data = response.json()
            assert data["task_id"] == sample_task_id

    async def test_update_nonexistent_task(self, async_client: AsyncClient):
        """Test updating nonexistent task."""
        update_data = {"title": "Updated problem"}

        with patch(
            "app.models.task_history.task_history_manager.update_task"
        ) as mock_update:
            mock_update.return_value = None

            response = await async_client.patch(
                "/history/tasks/nonexistent_task", json=update_data
            )

            assert response.status_code == 404

    async def test_delete_task(self, async_client: AsyncClient, sample_task_id):
        """Test deleting a task."""
        with patch(
            "app.models.task_history.task_history_manager.delete_task"
        ) as mock_delete:
            mock_delete.return_value = True

            response = await async_client.delete(f"/history/tasks/{sample_task_id}")

            assert response.status_code == 200
            data = response.json()
            assert data["message"] == "任务已删除"

    async def test_delete_nonexistent_task(self, async_client: AsyncClient):
        """Test deleting nonexistent task."""
        with patch(
            "app.models.task_history.task_history_manager.delete_task"
        ) as mock_delete:
            mock_delete.return_value = False

            response = await async_client.delete("/history/tasks/nonexistent_task")

            assert response.status_code == 404

    async def test_pin_task(self, async_client: AsyncClient, sample_task_id):
        """Test pinning a task."""
        mock_task = TaskHistoryItem(
            task_id=sample_task_id,
            title="Test task",
            is_pinned=True,
        )

        with patch(
            "app.models.task_history.task_history_manager.toggle_pin"
        ) as mock_pin:
            mock_pin.return_value = mock_task

            response = await async_client.post(
                f"/history/tasks/{sample_task_id}/toggle-pin"
            )

            assert response.status_code == 200
            data = response.json()
            assert data["is_pinned"] is True

    async def test_unpin_task(self, async_client: AsyncClient, sample_task_id):
        """Test unpinning a task."""
        mock_task = TaskHistoryItem(
            task_id=sample_task_id,
            title="Test task",
            is_pinned=False,
        )

        with patch(
            "app.models.task_history.task_history_manager.toggle_pin"
        ) as mock_pin:
            mock_pin.return_value = mock_task

            response = await async_client.post(
                f"/history/tasks/{sample_task_id}/toggle-pin"
            )

            assert response.status_code == 200
            data = response.json()
            assert data["is_pinned"] is False

    async def test_pin_nonexistent_task(self, async_client: AsyncClient):
        """Test pinning nonexistent task."""
        with patch(
            "app.models.task_history.task_history_manager.toggle_pin"
        ) as mock_pin:
            mock_pin.return_value = None

            response = await async_client.post(
                "/history/tasks/nonexistent_task/toggle-pin"
            )

            assert response.status_code == 404

    async def test_get_task_history_pagination(self, async_client: AsyncClient):
        """Test task history pagination."""
        # This would test pagination parameters
        # Implementation depends on actual pagination support
        pass

    async def test_get_task_history_filtering(self, async_client: AsyncClient):
        """Test task history filtering by status."""
        with patch(
            "app.models.task_history.task_history_manager.get_all_tasks"
        ) as mock_get:
            mock_get.return_value = [
                {
                    "task_id": "task1",
                    "status": "completed",
                    "created_at": datetime.now().isoformat(),
                }
            ]

            response = await async_client.get(
                "/history/tasks", params={"status": "completed"}
            )

            # Should filter by status if supported
            assert response.status_code == 200

    async def test_get_task_history_sorting(self, async_client: AsyncClient):
        """Test task history sorting."""
        # This would test sorting by different fields
        # Implementation depends on actual sorting support
        pass

    async def test_bulk_delete_tasks(self, async_client: AsyncClient):
        """Test bulk deletion of tasks."""
        # This would test bulk operations if supported
        pass

    async def test_export_task_history(self, async_client: AsyncClient):
        """Test exporting task history."""
        # This would test export functionality if supported
        pass
