"""Tests for modeling router endpoints."""

import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, MagicMock, patch
from io import BytesIO


@pytest.mark.asyncio
class TestModelingRouter:
    """Test suite for modeling router."""

    async def test_validate_api_key_valid(self, async_client: AsyncClient):
        """Test API key validation with valid credentials."""
        with patch("litellm.acompletion") as mock_completion:
            mock_completion.return_value = MagicMock()

            response = await async_client.post(
                "/modeling/validate-api-key",
                json={
                    "api_key": "test-key",
                    "base_url": "http://test.local/v1",
                    "model_id": "gpt-4o-mini",
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert data["valid"] is True

    async def test_validate_api_key_invalid(self, async_client: AsyncClient):
        """Test API key validation with invalid credentials."""
        with patch("litellm.acompletion") as mock_completion:
            mock_completion.side_effect = Exception("Invalid API key")

            response = await async_client.post(
                "/modeling/validate-api-key",
                json={
                    "api_key": "invalid-key",
                    "base_url": "http://test.local/v1",
                    "model_id": "gpt-4o-mini",
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert data["valid"] is False

    async def test_validate_openalex_email_valid(self, async_client: AsyncClient):
        """Test OpenAlex email validation with valid email."""
        with patch("requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"results": [{"id": "test"}]}
            mock_get.return_value = mock_response

            response = await async_client.post(
                "/modeling/validate-openalex-email",
                json={"email": "test@example.com"},
            )

            assert response.status_code == 200
            data = response.json()
            assert data["valid"] is True

    async def test_validate_openalex_email_invalid(self, async_client: AsyncClient):
        """Test OpenAlex email validation with invalid email."""
        with patch("requests.get") as mock_get:
            mock_get.side_effect = Exception("Network error")

            response = await async_client.post(
                "/modeling/validate-openalex-email",
                json={"email": "invalid@example.com"},
            )

            assert response.status_code == 200
            data = response.json()
            assert data["valid"] is False

    async def test_save_api_config(self, async_client: AsyncClient, temp_work_dir):
        """Test saving API configuration."""
        config_data = {
            "COORDINATOR_API_KEY": "test-key-1",
            "COORDINATOR_MODEL": "gpt-4o-mini",
            "COORDINATOR_BASE_URL": "http://test.local/v1",
            "MODELER_API_KEY": "test-key-2",
            "MODELER_MODEL": "gpt-4o-mini",
            "MODELER_BASE_URL": "http://test.local/v1",
            "CODER_API_KEY": "test-key-3",
            "CODER_MODEL": "gpt-4o-mini",
            "CODER_BASE_URL": "http://test.local/v1",
            "WRITER_API_KEY": "test-key-4",
            "WRITER_MODEL": "gpt-4o-mini",
            "WRITER_BASE_URL": "http://test.local/v1",
        }

        with patch("app.utils.config_loader.save_model_config") as mock_save:
            mock_save.return_value = None

            response = await async_client.post(
                "/modeling/save-api-config", json=config_data
            )

            assert response.status_code == 200
            data = response.json()
            assert data["message"] == "API configuration saved successfully"

    async def test_modeling_endpoint_missing_problem(self, async_client: AsyncClient):
        """Test modeling endpoint with missing problem description."""
        response = await async_client.post(
            "/modeling",
            data={
                "template": "国赛",
                "language": "zh",
                "format_output": "markdown",
            },
        )

        # Should return validation error
        assert response.status_code == 422

    async def test_modeling_endpoint_with_files(
        self, async_client: AsyncClient, temp_work_dir
    ):
        """Test modeling endpoint with file uploads."""
        with patch("app.core.workflow.MathModelWorkFlow") as mock_workflow:
            mock_instance = AsyncMock()
            mock_workflow.return_value = mock_instance
            mock_instance.run = AsyncMock()

            # Create test file
            file_content = b"Test data content"
            files = {
                "files": ("test.txt", BytesIO(file_content), "text/plain"),
            }

            data = {
                "problem": "测试问题",
                "template": "国赛",
                "language": "zh",
                "format_output": "markdown",
            }

            with patch("app.utils.common_utils.create_work_dir") as mock_create_dir:
                mock_create_dir.return_value = temp_work_dir

                response = await async_client.post("/modeling", data=data, files=files)

                assert response.status_code == 200
                result = response.json()
                assert "task_id" in result

    async def test_example_endpoint(self, async_client: AsyncClient):
        """Test example endpoint with built-in example."""
        with patch("app.core.workflow.MathModelWorkFlow") as mock_workflow:
            mock_instance = AsyncMock()
            mock_workflow.return_value = mock_instance
            mock_instance.run = AsyncMock()

            response = await async_client.post(
                "/modeling/example",
                json={
                    "example_name": "2024A",
                    "template": "国赛",
                    "language": "zh",
                    "format_output": "markdown",
                },
            )

            assert response.status_code == 200
            result = response.json()
            assert "task_id" in result

    async def test_example_endpoint_invalid_example(self, async_client: AsyncClient):
        """Test example endpoint with invalid example name."""
        response = await async_client.post(
            "/modeling/example",
            json={
                "example_name": "invalid_example",
                "template": "国赛",
                "language": "zh",
                "format_output": "markdown",
            },
        )

        # Should handle gracefully
        assert response.status_code in [200, 404, 422]

    async def test_modeling_with_archive_file(
        self, async_client: AsyncClient, temp_work_dir
    ):
        """Test modeling with archive file upload (zip)."""
        with patch("app.core.workflow.MathModelWorkFlow") as mock_workflow:
            mock_instance = AsyncMock()
            mock_workflow.return_value = mock_instance
            mock_instance.run = AsyncMock()

            # Create mock zip file
            import zipfile
            from io import BytesIO

            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zip_file:
                zip_file.writestr("data.txt", "test data")

            zip_buffer.seek(0)

            files = {
                "files": ("test.zip", zip_buffer, "application/zip"),
            }

            data = {
                "problem": "测试问题",
                "template": "国赛",
                "language": "zh",
                "format_output": "markdown",
            }

            with patch("app.utils.common_utils.create_work_dir") as mock_create_dir:
                mock_create_dir.return_value = temp_work_dir
                with patch("app.utils.file_utils.extract_archive") as mock_extract:
                    mock_extract.return_value = None

                    response = await async_client.post(
                        "/modeling", data=data, files=files
                    )

                    assert response.status_code == 200
                    result = response.json()
                    assert "task_id" in result

    async def test_modeling_max_file_limit(self, async_client: AsyncClient):
        """Test modeling endpoint respects max file limit."""
        # This would test the MAX_FILES_LIMIT constant
        # Implementation depends on actual limit checking in the router
        pass

    async def test_modeling_concurrent_requests(self, async_client: AsyncClient):
        """Test handling of concurrent modeling requests."""
        # This would test concurrent request handling
        # Implementation depends on rate limiting and queue management
        pass
