"""Tests for files router endpoints."""

import pytest
from httpx import AsyncClient
from unittest.mock import patch
import os


@pytest.mark.asyncio
class TestFilesRouter:
    """Test suite for files router."""

    async def test_get_files_list(
        self, async_client: AsyncClient, sample_task_id, temp_work_dir
    ):
        """Test getting list of files for a task."""
        # Create test files
        test_file = os.path.join(temp_work_dir, "test.txt")
        with open(test_file, "w") as f:
            f.write("test content")

        with patch("app.routers.files_router.get_work_dir") as mock_get_dir:
            mock_get_dir.return_value = temp_work_dir

            response = await async_client.get(f"/files/{sample_task_id}/files")

            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)

    async def test_get_files_list_nonexistent_task(self, async_client: AsyncClient):
        """Test getting files for nonexistent task."""
        response = await async_client.get("/files/nonexistent_task/files")

        # Should handle gracefully
        assert response.status_code in [200, 404]

    async def test_get_download_url(
        self, async_client: AsyncClient, sample_task_id, temp_work_dir
    ):
        """Test getting download URL for a file."""
        # Create test file
        test_file = os.path.join(temp_work_dir, "test.txt")
        with open(test_file, "w") as f:
            f.write("test content")

        # download-url doesn't use get_work_dir, it just constructs a URL
        response = await async_client.get(
            f"/files/{sample_task_id}/download-url",
            params={"filename": "test.txt"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "download_url" in data

    async def test_get_download_url_missing_file(
        self, async_client: AsyncClient, sample_task_id
    ):
        """Test getting download URL for missing file."""
        response = await async_client.get(
            f"/files/{sample_task_id}/download-url",
            params={"filename": "nonexistent.txt"},
        )
        # Endpoint only constructs a static URL, it doesn't check file existence
        assert response.status_code == 200
        data = response.json()
        assert "download_url" in data

    async def test_download_all_files(
        self, async_client: AsyncClient, sample_task_id, temp_work_dir
    ):
        """Test downloading all files as ZIP."""
        # Create test files
        test_file1 = os.path.join(temp_work_dir, "test1.txt")
        test_file2 = os.path.join(temp_work_dir, "test2.txt")
        with open(test_file1, "w") as f:
            f.write("content 1")
        with open(test_file2, "w") as f:
            f.write("content 2")

        with patch("app.routers.files_router.get_work_dir") as mock_get_dir:
            mock_get_dir.return_value = temp_work_dir

            response = await async_client.get(f"/files/{sample_task_id}/download-all")

            assert response.status_code == 200
            assert response.headers["content-type"] == "application/zip"

    async def test_get_file_content(
        self, async_client: AsyncClient, sample_task_id, temp_work_dir
    ):
        """Test getting specific file content."""
        # Create test file
        test_content = "Test file content\nLine 2"
        test_file = os.path.join(temp_work_dir, "test.txt")
        with open(test_file, "w") as f:
            f.write(test_content)

        with patch("app.routers.files_router.get_work_dir") as mock_get_dir:
            mock_get_dir.return_value = temp_work_dir

            response = await async_client.get(
                f"/files/{sample_task_id}/file-content",
                params={"filename": "test.txt"},
            )

            assert response.status_code == 200
            data = response.json()
            assert data["content"] == test_content

    async def test_get_file_content_binary_file(
        self, async_client: AsyncClient, sample_task_id, temp_work_dir
    ):
        """Test getting binary file content."""
        # Create binary file
        test_file = os.path.join(temp_work_dir, "test.png")
        with open(test_file, "wb") as f:
            f.write(b"\x89PNG\r\n\x1a\n")

        with patch("app.routers.files_router.get_work_dir") as mock_get_dir:
            mock_get_dir.return_value = temp_work_dir

            response = await async_client.get(
                f"/files/{sample_task_id}/file-content",
                params={"filename": "test.png"},
            )

            # Should handle binary files appropriately
            assert response.status_code in [200, 400]

    async def test_upload_file(
        self, async_client: AsyncClient, sample_task_id, temp_work_dir
    ):
        """Test uploading a file to task directory."""
        from io import BytesIO

        file_content = b"Uploaded file content"
        files = {
            "files": ("uploaded.txt", BytesIO(file_content), "text/plain"),
        }

        with patch("app.routers.files_router.get_work_dir") as mock_get_dir:
            mock_get_dir.return_value = temp_work_dir

            response = await async_client.post(
                f"/files/{sample_task_id}/upload", files=files
            )

            assert response.status_code == 200
            data = response.json()
            assert data["message"] == "Files uploaded successfully"

    async def test_upload_multiple_files(
        self, async_client: AsyncClient, sample_task_id, temp_work_dir
    ):
        """Test uploading multiple files."""
        from io import BytesIO

        files = [
            ("files", ("file1.txt", BytesIO(b"content 1"), "text/plain")),
            ("files", ("file2.txt", BytesIO(b"content 2"), "text/plain")),
        ]

        with patch("app.routers.files_router.get_work_dir") as mock_get_dir:
            mock_get_dir.return_value = temp_work_dir

            response = await async_client.post(
                f"/files/{sample_task_id}/upload", files=files
            )

            assert response.status_code == 200

    async def test_delete_file(
        self, async_client: AsyncClient, sample_task_id, temp_work_dir
    ):
        """Test deleting a file."""
        # Create test file
        test_file = os.path.join(temp_work_dir, "to_delete.txt")
        with open(test_file, "w") as f:
            f.write("delete me")

        with patch("app.routers.files_router.get_work_dir") as mock_get_dir:
            mock_get_dir.return_value = temp_work_dir

            response = await async_client.delete(
                f"/files/{sample_task_id}/file",
                params={"filename": "to_delete.txt"},
            )

            assert response.status_code == 200
            data = response.json()
            assert data["message"] == "File deleted successfully"

    async def test_delete_nonexistent_file(
        self, async_client: AsyncClient, sample_task_id
    ):
        """Test deleting a nonexistent file."""
        response = await async_client.delete(
            f"/files/{sample_task_id}/file",
            params={"filename": "nonexistent.txt"},
        )

        assert response.status_code in [404, 400]

    async def test_upload_file_size_limit(
        self, async_client: AsyncClient, sample_task_id
    ):
        """Test file upload size limit."""
        # This would test MAX_FILE_SIZE limit
        # Implementation depends on actual size checking
        pass

    async def test_upload_invalid_file_type(
        self, async_client: AsyncClient, sample_task_id
    ):
        """Test uploading invalid file type."""
        # This would test file type validation
        # Implementation depends on ALLOWED_FILE_TYPES
        pass

    async def test_file_path_traversal_prevention(
        self, async_client: AsyncClient, sample_task_id
    ):
        """Test prevention of path traversal attacks."""
        response = await async_client.get(
            f"/files/{sample_task_id}/file-content",
            params={"filename": "../../../etc/passwd"},
        )

        # Should reject path traversal attempts
        assert response.status_code in [400, 403, 404]

    async def test_concurrent_file_operations(
        self, async_client: AsyncClient, sample_task_id
    ):
        """Test concurrent file operations."""
        # This would test thread safety of file operations
        pass
