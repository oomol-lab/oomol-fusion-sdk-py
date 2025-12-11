"""Tests for file upload functionality."""

import io
from pathlib import Path

import pytest

from oomol_fusion_sdk import FileUploadError, FileTooLargeError, UploadOptions, UploadProgress
from oomol_fusion_sdk.uploader import (
    MAX_FILE_SIZE,
    SUPPORTED_FILE_TYPES,
    get_content_type,
    get_file_extension,
    get_file_size,
    read_file_bytes,
)


class TestFileExtension:
    """Tests for file extension extraction."""

    def test_get_file_extension_success(self):
        """Test successful file extension extraction."""
        assert get_file_extension("document.pdf") == "pdf"
        assert get_file_extension("image.PNG") == "png"
        assert get_file_extension("archive.tar.gz") == "gz"

    def test_get_file_extension_no_extension(self):
        """Test error when file has no extension."""
        with pytest.raises(FileUploadError) as exc_info:
            get_file_extension("noextension")
        assert "must have an extension" in str(exc_info.value)


class TestContentType:
    """Tests for content type mapping."""

    def test_get_content_type_images(self):
        """Test content type for image files."""
        assert get_content_type("photo.png") == "image/png"
        assert get_content_type("photo.jpg") == "image/jpeg"
        assert get_content_type("photo.JPEG") == "image/jpeg"
        assert get_content_type("photo.gif") == "image/gif"
        assert get_content_type("photo.webp") == "image/webp"

    def test_get_content_type_audio_video(self):
        """Test content type for audio/video files."""
        assert get_content_type("song.mp3") == "audio/mpeg"
        assert get_content_type("video.mp4") == "video/mp4"

    def test_get_content_type_documents(self):
        """Test content type for document files."""
        assert get_content_type("note.txt") == "text/plain"
        assert get_content_type("readme.md") == "text/markdown"
        assert get_content_type("document.pdf") == "application/pdf"
        assert get_content_type("book.epub") == "application/epub+zip"

    def test_get_content_type_office_documents(self):
        """Test content type for Office documents."""
        assert (
            get_content_type("document.docx")
            == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        assert (
            get_content_type("spreadsheet.xlsx")
            == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        assert (
            get_content_type("presentation.pptx")
            == "application/vnd.openxmlformats-officedocument.presentationml.presentation"
        )

    def test_get_content_type_data(self):
        """Test content type for data files."""
        assert get_content_type("data.csv") == "text/csv"
        assert get_content_type("config.json") == "application/json"
        assert get_content_type("archive.zip") == "application/zip"

    def test_get_content_type_unsupported(self):
        """Test error for unsupported file types."""
        with pytest.raises(FileUploadError) as exc_info:
            get_content_type("file.xyz")
        assert "Unsupported file type" in str(exc_info.value)


class TestFileOperations:
    """Tests for file operation utilities."""

    def test_get_file_size_bytes(self):
        """Test getting file size from bytes."""
        data = b"Hello World"
        assert get_file_size(data) == 11

    def test_get_file_size_file_object(self):
        """Test getting file size from file object."""
        data = b"Hello World"
        file_obj = io.BytesIO(data)
        assert get_file_size(file_obj) == 11
        # Verify position is restored
        assert file_obj.tell() == 0

    def test_read_file_bytes_from_bytes(self):
        """Test reading bytes from bytes."""
        data = b"Hello World"
        assert read_file_bytes(data) == data

    def test_read_file_bytes_from_file_object(self):
        """Test reading bytes from file object."""
        data = b"Hello World"
        file_obj = io.BytesIO(data)
        file_obj.seek(5)  # Move position
        result = read_file_bytes(file_obj)
        assert result == data
        # Verify position is restored
        assert file_obj.tell() == 5


class TestUploadOptions:
    """Tests for UploadOptions configuration."""

    def test_upload_options_defaults(self):
        """Test default upload options."""
        options = UploadOptions()
        assert options.on_progress is None
        assert options.max_concurrent_uploads == 3
        assert options.multipart_threshold == 5 * 1024 * 1024
        assert options.retries == 3

    def test_upload_options_custom(self):
        """Test custom upload options."""
        callback = lambda p: None
        options = UploadOptions(
            on_progress=callback,
            max_concurrent_uploads=5,
            multipart_threshold=10 * 1024 * 1024,
            retries=5,
        )
        assert options.on_progress == callback
        assert options.max_concurrent_uploads == 5
        assert options.multipart_threshold == 10 * 1024 * 1024
        assert options.retries == 5


class TestUploadProgress:
    """Tests for UploadProgress tracking."""

    def test_upload_progress_creation(self):
        """Test creating upload progress object."""
        progress = UploadProgress(
            uploaded_bytes=1024,
            total_bytes=2048,
            percentage=50.0,
            uploaded_chunks=2,
            total_chunks=4,
        )
        assert progress.uploaded_bytes == 1024
        assert progress.total_bytes == 2048
        assert progress.percentage == 50.0
        assert progress.uploaded_chunks == 2
        assert progress.total_chunks == 4

    def test_upload_progress_defaults(self):
        """Test upload progress with default chunk values."""
        progress = UploadProgress(
            uploaded_bytes=512,
            total_bytes=1024,
            percentage=50.0,
        )
        assert progress.uploaded_chunks == 0
        assert progress.total_chunks == 0


class TestConstants:
    """Tests for module constants."""

    def test_supported_file_types_count(self):
        """Test that we have the expected number of supported file types."""
        assert len(SUPPORTED_FILE_TYPES) == 17

    def test_max_file_size(self):
        """Test maximum file size constant."""
        assert MAX_FILE_SIZE == 500 * 1024 * 1024  # 500MB
