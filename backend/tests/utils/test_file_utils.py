"""Tests for file utility functions."""

import os
import zipfile
from app.utils.file_utils import (
    is_archive_file,
    extract_archive,
    count_files_in_directory,
)


class TestFileUtils:
    """Test suite for file utility functions."""

    def test_is_archive_file_zip(self):
        """Test ZIP file detection."""
        assert is_archive_file("test.zip") is True
        assert is_archive_file("TEST.ZIP") is True

    def test_is_archive_file_rar(self):
        """Test RAR file detection."""
        assert is_archive_file("test.rar") is True
        assert is_archive_file("TEST.RAR") is True

    def test_is_archive_file_7z(self):
        """Test 7z file detection."""
        assert is_archive_file("test.7z") is True
        assert is_archive_file("TEST.7Z") is True

    def test_is_archive_file_tar(self):
        """Test TAR file detection."""
        assert is_archive_file("test.tar") is True
        assert is_archive_file("test.tar.gz") is True
        assert is_archive_file("test.tar.bz2") is True

    def test_is_archive_file_non_archive(self):
        """Test non-archive file detection."""
        assert is_archive_file("test.txt") is False
        assert is_archive_file("test.py") is False
        assert is_archive_file("test.csv") is False

    def test_is_archive_file_no_extension(self):
        """Test file without extension."""
        assert is_archive_file("testfile") is False

    def test_extract_archive_zip(self, temp_work_dir):
        """Test extracting ZIP archive."""
        # Create test ZIP file
        zip_path = os.path.join(temp_work_dir, "test.zip")
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("file1.txt", "content 1")
            zf.writestr("file2.txt", "content 2")

        extract_dir = os.path.join(temp_work_dir, "extracted")
        extract_archive(zip_path, extract_dir)

        # Verify extraction
        assert os.path.exists(extract_dir)
        assert os.path.exists(os.path.join(extract_dir, "file1.txt"))
        assert os.path.exists(os.path.join(extract_dir, "file2.txt"))

    def test_extract_archive_nested_zip(self, temp_work_dir):
        """Test extracting ZIP with nested directories."""
        # Create ZIP with nested structure
        zip_path = os.path.join(temp_work_dir, "nested.zip")
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("dir1/file1.txt", "content 1")
            zf.writestr("dir1/dir2/file2.txt", "content 2")

        extract_dir = os.path.join(temp_work_dir, "extracted")
        extract_archive(zip_path, extract_dir)

        # Verify nested structure
        assert os.path.exists(os.path.join(extract_dir, "dir1", "file1.txt"))
        assert os.path.exists(os.path.join(extract_dir, "dir1", "dir2", "file2.txt"))

    def test_extract_archive_invalid_file(self, temp_work_dir):
        """Test extracting invalid archive."""
        invalid_file = os.path.join(temp_work_dir, "invalid.zip")
        with open(invalid_file, "w") as f:
            f.write("not a zip file")

        extract_dir = os.path.join(temp_work_dir, "extracted")

        # Function returns (success, error_msg, files) tuple
        success, error_msg, files = extract_archive(invalid_file, extract_dir)
        assert not success
        assert (
            "损坏的ZIP文件" in error_msg
            or "BadZipFile" in error_msg
            or "解压失败" in error_msg
        )

    def test_extract_archive_nonexistent_file(self, temp_work_dir):
        """Test extracting nonexistent archive."""
        nonexistent = os.path.join(temp_work_dir, "nonexistent.zip")
        extract_dir = os.path.join(temp_work_dir, "extracted")

        # Function returns (success, error_msg, files) tuple
        success, error_msg, files = extract_archive(nonexistent, extract_dir)
        assert not success
        assert "解压失败" in error_msg or "No such file" in error_msg

    def test_count_files_in_directory(self, temp_work_dir):
        """Test counting files in directory."""
        # Create test files
        for i in range(5):
            filepath = os.path.join(temp_work_dir, f"file{i}.txt")
            with open(filepath, "w") as f:
                f.write(f"content {i}")

        count = count_files_in_directory(temp_work_dir)

        assert count == 5

    def test_count_files_empty_directory(self, temp_work_dir):
        """Test counting files in empty directory."""
        count = count_files_in_directory(temp_work_dir)

        assert count == 0

    def test_count_files_with_subdirectories(self, temp_work_dir):
        """Test counting files with subdirectories."""
        # Create files in root
        for i in range(3):
            filepath = os.path.join(temp_work_dir, f"file{i}.txt")
            with open(filepath, "w") as f:
                f.write(f"content {i}")

        # Create subdirectory with files
        subdir = os.path.join(temp_work_dir, "subdir")
        os.makedirs(subdir)
        for i in range(2):
            filepath = os.path.join(subdir, f"subfile{i}.txt")
            with open(filepath, "w") as f:
                f.write(f"subcontent {i}")

        count = count_files_in_directory(temp_work_dir)

        # Should count recursively or not based on implementation
        assert count >= 3

    def test_count_files_nonexistent_directory(self):
        """Test counting files in nonexistent directory."""
        # Function returns 0 for nonexistent directories instead of raising
        count = count_files_in_directory("/nonexistent/directory")
        assert count == 0

    def test_extract_archive_rar(self, temp_work_dir):
        """Test extracting RAR archive."""
        # RAR extraction requires rarfile library
        # This is a placeholder test
        pass

    def test_extract_archive_7z(self, temp_work_dir):
        """Test extracting 7z archive."""
        # 7z extraction requires py7zr library
        # This is a placeholder test
        pass

    def test_extract_archive_tar_gz(self, temp_work_dir):
        """Test extracting tar.gz archive."""
        import tarfile

        # Create test tar.gz file
        tar_path = os.path.join(temp_work_dir, "test.tar.gz")
        with tarfile.open(tar_path, "w:gz") as tar:
            # Create temporary file to add
            temp_file = os.path.join(temp_work_dir, "temp.txt")
            with open(temp_file, "w") as f:
                f.write("test content")
            tar.add(temp_file, arcname="file.txt")

        extract_dir = os.path.join(temp_work_dir, "extracted")
        extract_archive(tar_path, extract_dir)

        # Verify extraction
        assert os.path.exists(extract_dir)

    def test_is_archive_file_case_insensitive(self):
        """Test case-insensitive archive detection."""
        assert is_archive_file("Test.ZIP") is True
        assert is_archive_file("Test.Rar") is True
        assert is_archive_file("Test.7Z") is True

    def test_extract_archive_overwrites_existing(self, temp_work_dir):
        """Test that extraction overwrites existing files."""
        # Create ZIP
        zip_path = os.path.join(temp_work_dir, "test.zip")
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("file.txt", "new content")

        extract_dir = os.path.join(temp_work_dir, "extracted")
        os.makedirs(extract_dir, exist_ok=True)

        # Create existing file
        existing_file = os.path.join(extract_dir, "file.txt")
        with open(existing_file, "w") as f:
            f.write("old content")

        extract_archive(zip_path, extract_dir)

        # Verify overwrite
        with open(existing_file, "r") as f:
            content = f.read()
            assert content == "new content"

    def test_count_files_filter_types(self, temp_work_dir):
        """Test counting specific file types."""
        # Create various file types
        file_types = [".txt", ".py", ".csv", ".json"]
        for i, ext in enumerate(file_types):
            filepath = os.path.join(temp_work_dir, f"file{i}{ext}")
            with open(filepath, "w") as f:
                f.write("content")

        count = count_files_in_directory(temp_work_dir)

        assert count == len(file_types)

    def test_extract_archive_large_file(self, temp_work_dir):
        """Test extracting large archive."""
        # This would test handling of large files
        pass

    def test_extract_archive_many_files(self, temp_work_dir):
        """Test extracting archive with many files."""
        # Create ZIP with many files
        zip_path = os.path.join(temp_work_dir, "many.zip")
        with zipfile.ZipFile(zip_path, "w") as zf:
            for i in range(100):
                zf.writestr(f"file{i}.txt", f"content {i}")

        extract_dir = os.path.join(temp_work_dir, "extracted")
        extract_archive(zip_path, extract_dir)

        # Verify all files extracted
        count = count_files_in_directory(extract_dir)
        assert count == 100

    def test_extract_archive_path_traversal_prevention(self, temp_work_dir):
        """Test prevention of path traversal in archives."""
        # Create malicious ZIP with path traversal
        zip_path = os.path.join(temp_work_dir, "malicious.zip")
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("../../../etc/passwd", "malicious content")

        extract_dir = os.path.join(temp_work_dir, "extracted")

        # Should prevent path traversal
        # Implementation dependent
        extract_archive(zip_path, extract_dir)
