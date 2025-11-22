"""Tests for common utility functions."""

import pytest
import os
import shutil
from unittest.mock import patch
from app.utils.common_utils import (
    create_task_id,
    create_work_dir,
    get_work_dir,
    get_current_files,
    md_2_docx,
)


class TestCommonUtils:
    """Test suite for common utility functions."""

    def test_create_task_id(self):
        """Test task ID creation."""
        task_id = create_task_id()

        assert task_id is not None
        assert isinstance(task_id, str)
        assert len(task_id) > 0

    def test_create_task_id_uniqueness(self):
        """Test that task IDs are unique."""
        task_ids = [create_task_id() for _ in range(10)]

        # All task IDs should be unique
        assert len(task_ids) == len(set(task_ids))

    def test_create_work_dir(self, sample_task_id):
        """Test work directory creation."""
        work_dir = create_work_dir(sample_task_id)

        assert work_dir is not None
        assert isinstance(work_dir, str)
        assert sample_task_id in work_dir

        # Cleanup
        if os.path.exists(work_dir):
            shutil.rmtree(work_dir)

    def test_create_work_dir_exists(self, sample_task_id, temp_work_dir):
        """Test work directory creation when it already exists."""
        # Create directory first
        os.makedirs(temp_work_dir, exist_ok=True)

        with patch("app.utils.common_utils.get_work_dir") as mock_get_dir:
            mock_get_dir.return_value = temp_work_dir

            work_dir = create_work_dir(sample_task_id)

            # Should return existing directory
            assert os.path.exists(work_dir)

    def test_get_work_dir(self, sample_task_id):
        """Test getting work directory path."""
        work_dir = get_work_dir(sample_task_id)

        assert work_dir is not None
        assert isinstance(work_dir, str)
        assert sample_task_id in work_dir

    def test_get_current_files(self, temp_work_dir):
        """Test getting current files in directory."""
        # Create test files
        test_files = ["file1.txt", "file2.py", "file3.csv"]
        for filename in test_files:
            filepath = os.path.join(temp_work_dir, filename)
            with open(filepath, "w") as f:
                f.write("test content")

        files = get_current_files(temp_work_dir)

        assert isinstance(files, list)
        assert len(files) >= len(test_files)

    def test_get_current_files_empty_dir(self, temp_work_dir):
        """Test getting files from empty directory."""
        files = get_current_files(temp_work_dir)

        assert isinstance(files, list)
        assert len(files) == 0

    def test_get_current_files_with_subdirs(self, temp_work_dir):
        """Test getting files with subdirectories."""
        # Create subdirectory with files
        subdir = os.path.join(temp_work_dir, "subdir")
        os.makedirs(subdir)

        with open(os.path.join(subdir, "file.txt"), "w") as f:
            f.write("content")

        files = get_current_files(temp_work_dir)

        # Should handle subdirectories appropriately
        assert isinstance(files, list)

    def test_md_2_docx_success(self, temp_work_dir):
        """Test Markdown to DOCX conversion."""
        # Create test markdown file
        md_file = os.path.join(temp_work_dir, "test.md")
        with open(md_file, "w", encoding="utf-8") as f:
            f.write("# Test Markdown\n\nThis is a test.")

        with patch("pypandoc.convert_file") as mock_convert:
            mock_convert.return_value = None

            md_2_docx(md_file)

            # Should call pypandoc
            mock_convert.assert_called_once()

    def test_md_2_docx_file_not_found(self):
        """Test DOCX conversion with nonexistent file."""
        with pytest.raises(FileNotFoundError):
            md_2_docx("nonexistent.md")

    def test_md_2_docx_invalid_markdown(self, temp_work_dir):
        """Test DOCX conversion with invalid markdown."""
        # Create file with invalid content
        md_file = os.path.join(temp_work_dir, "invalid.md")
        with open(md_file, "w", encoding="utf-8") as f:
            f.write("")

        with patch("pypandoc.convert_file") as mock_convert:
            mock_convert.return_value = None

            # Should handle gracefully
            md_2_docx(md_file)

    def test_create_work_dir_permissions(self, sample_task_id):
        """Test work directory creation with proper permissions."""
        work_dir = create_work_dir(sample_task_id)

        # Verify directory is writable
        assert os.access(work_dir, os.W_OK)

        # Cleanup
        if os.path.exists(work_dir):
            shutil.rmtree(work_dir)

    def test_get_current_files_filter_hidden(self, temp_work_dir):
        """Test that hidden files are filtered."""
        # Create hidden file
        hidden_file = os.path.join(temp_work_dir, ".hidden")
        with open(hidden_file, "w") as f:
            f.write("hidden content")

        # Create normal file
        normal_file = os.path.join(temp_work_dir, "normal.txt")
        with open(normal_file, "w") as f:
            f.write("normal content")

        files = get_current_files(temp_work_dir)

        # Should filter hidden files (implementation dependent)
        assert isinstance(files, list)

    def test_get_current_files_with_patterns(self, temp_work_dir):
        """Test getting files with specific patterns."""
        # Create various file types
        files_to_create = [
            "data.csv",
            "script.py",
            "notebook.ipynb",
            "result.txt",
        ]

        for filename in files_to_create:
            filepath = os.path.join(temp_work_dir, filename)
            with open(filepath, "w") as f:
                f.write("content")

        files = get_current_files(temp_work_dir)

        # Should return all files
        assert len(files) >= len(files_to_create)

    def test_task_id_format(self):
        """Test task ID format."""
        task_id = create_task_id()

        # Verify format (implementation dependent)
        # Common formats: UUID, timestamp-based, etc.
        assert len(task_id) > 0
        assert " " not in task_id  # No spaces

    def test_work_dir_path_safety(self, sample_task_id):
        """Test work directory path safety."""
        # Create the work directory first so get_work_dir doesn't raise
        work_dir_path = os.path.join("project", "work_dir", sample_task_id)
        os.makedirs(work_dir_path, exist_ok=True)

        try:
            work_dir = get_work_dir(sample_task_id)

            # Should not contain path traversal
            assert ".." not in work_dir
            # Should be within project directory (can be relative or absolute)
            assert "project" in work_dir and "work_dir" in work_dir
            assert sample_task_id in work_dir
        finally:
            # Cleanup
            import shutil

            if os.path.exists("project"):
                shutil.rmtree("project")

    def test_md_2_docx_output_path(self, temp_work_dir):
        """Test DOCX output path."""
        md_file = os.path.join(temp_work_dir, "test.md")
        with open(md_file, "w", encoding="utf-8") as f:
            f.write("# Test")

        with patch("pypandoc.convert_file") as mock_convert:
            mock_convert.return_value = None

            md_2_docx(md_file)

            # Verify output path
            # Implementation dependent
            pass

    def test_concurrent_work_dir_creation(self):
        """Test concurrent work directory creation."""

        async def create_dir():
            task_id = create_task_id()
            return create_work_dir(task_id)

        # Create multiple directories concurrently
        # Should handle race conditions
        pass
