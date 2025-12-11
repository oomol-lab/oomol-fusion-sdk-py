"""File upload functionality for OOMOL Fusion SDK."""

import asyncio
import concurrent.futures
import time
from io import BytesIO
from pathlib import Path
from typing import Any, BinaryIO, Dict, List, Optional, Tuple, Union
from urllib.parse import urljoin

import requests

from .errors import FileUploadError, FileTooLargeError, NetworkError
from .types import UploadOptions, UploadProgress

# Maximum file size (500MB)
MAX_FILE_SIZE = 500 * 1024 * 1024

# Supported file types and their content types
SUPPORTED_FILE_TYPES: Dict[str, str] = {
    # Images
    "png": "image/png",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "gif": "image/gif",
    "webp": "image/webp",
    # Audio/Video
    "mp3": "audio/mpeg",
    "mp4": "video/mp4",
    # Documents
    "txt": "text/plain",
    "md": "text/markdown",
    "pdf": "application/pdf",
    "epub": "application/epub+zip",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    # Data
    "csv": "text/csv",
    "json": "application/json",
    "zip": "application/zip",
}


def get_file_extension(file_name: str) -> str:
    """Extract file extension from file name.

    Args:
        file_name: The file name

    Returns:
        The file extension (lowercase, without dot)

    Raises:
        FileUploadError: If file has no extension
    """
    parts = file_name.rsplit(".", 1)
    if len(parts) != 2:
        raise FileUploadError(f"File name must have an extension: {file_name}")

    return parts[1].lower()


def get_content_type(file_name: str) -> str:
    """Get the content type based on file extension.

    Args:
        file_name: The file name

    Returns:
        The content type (MIME type)

    Raises:
        FileUploadError: If file type is not supported
    """
    ext = get_file_extension(file_name)

    if ext not in SUPPORTED_FILE_TYPES:
        raise FileUploadError(
            f"Unsupported file type: .{ext}. Supported types: {', '.join(SUPPORTED_FILE_TYPES.keys())}",
            file_name=file_name,
        )

    return SUPPORTED_FILE_TYPES[ext]


def get_file_size(file: Union[bytes, BinaryIO, Path]) -> int:
    """Get the size of a file in bytes.

    Args:
        file: The file (bytes, file-like object, or Path)

    Returns:
        The file size in bytes
    """
    if isinstance(file, bytes):
        return len(file)
    elif isinstance(file, Path):
        return file.stat().st_size
    else:
        # File-like object
        current_pos = file.tell()
        file.seek(0, 2)  # Seek to end
        size = file.tell()
        file.seek(current_pos)  # Restore position
        return size


def read_file_bytes(file: Union[bytes, BinaryIO, Path]) -> bytes:
    """Read file content as bytes.

    Args:
        file: The file (bytes, file-like object, or Path)

    Returns:
        The file content as bytes
    """
    if isinstance(file, bytes):
        return file
    elif isinstance(file, Path):
        return file.read_bytes()
    else:
        # File-like object
        current_pos = file.tell()
        file.seek(0)
        content = file.read()
        file.seek(current_pos)  # Restore position
        return content


class FileUploader:
    """Handles file upload operations to OOMOL cloud storage."""

    def __init__(self, base_url: str, token: str, session: requests.Session) -> None:
        """Initialize the file uploader.

        Args:
            base_url: The base URL for the API
            token: The authentication token
            session: The requests session to use
        """
        self._base_url = base_url
        self._token = token
        self._session = session

    def upload_file(
        self,
        file: Union[bytes, BinaryIO, Path],
        file_name: str,
        options: Optional[UploadOptions] = None,
    ) -> str:
        """Upload a file to OOMOL cloud storage.

        This method automatically chooses between single-file upload and multipart upload
        based on file size.

        Args:
            file: The file to upload (bytes, file-like object, or Path)
            file_name: The name of the file (must include extension)
            options: Optional upload options

        Returns:
            The download URL of the uploaded file

        Raises:
            FileUploadError: If upload fails
            FileTooLargeError: If file exceeds maximum size
            NetworkError: If network communication fails
        """
        # Use default options if not provided
        if options is None:
            options = UploadOptions()

        # Validate file size
        file_size = get_file_size(file)
        if file_size > MAX_FILE_SIZE:
            raise FileTooLargeError(
                f"File size {file_size} bytes exceeds maximum allowed size {MAX_FILE_SIZE} bytes",
                file_size=file_size,
                max_size=MAX_FILE_SIZE,
            )

        # Validate file type
        get_content_type(file_name)

        # Choose upload strategy based on file size
        if file_size < options.multipart_threshold:
            return self._upload_single_file(file, file_name, options)
        else:
            return self._upload_multipart_file(file, file_name, options)

    def _upload_single_file(
        self,
        file: Union[bytes, BinaryIO, Path],
        file_name: str,
        options: UploadOptions,
    ) -> str:
        """Upload a file using single-file upload.

        Args:
            file: The file to upload
            file_name: The name of the file
            options: Upload options

        Returns:
            The download URL of the uploaded file

        Raises:
            FileUploadError: If upload fails
        """
        file_bytes = read_file_bytes(file)
        file_size = len(file_bytes)
        content_type = get_content_type(file_name)

        # Retry logic
        for attempt in range(options.retries + 1):
            try:
                # Step 1: Get presigned URL
                url = urljoin(self._base_url + "/", "file-upload/action/generate-presigned-url")
                response = self._session.post(
                    url,
                    json={"fileSuffix": get_file_extension(file_name)},
                    timeout=30,
                )

                if response.status_code != 200:
                    raise FileUploadError(
                        f"Failed to get presigned URL: {response.status_code} {response.reason}",
                        file_name=file_name,
                    )

                result = response.json()
                data = result.get("data", {})
                presigned_url = data.get("uploadURL")
                fields = data.get("fields", {})
                download_url = data.get("downloadURL")

                if not presigned_url or not download_url:
                    raise FileUploadError("Invalid presigned URL response", file_name=file_name)

                # Step 2: Upload to OSS using multipart/form-data
                files = {"file": (file_name, BytesIO(file_bytes), content_type)}

                # Track upload progress
                if options.on_progress:
                    # For single file upload, we can report percentage based on upload progress
                    # However, requests library doesn't provide built-in progress tracking
                    # We'll report 50% at start and 100% at completion
                    options.on_progress(50.0)

                upload_response = requests.post(
                    presigned_url,
                    data=fields,
                    files=files,
                    timeout=300,
                )

                if upload_response.status_code not in [200, 204]:
                    raise FileUploadError(
                        f"Failed to upload file: {upload_response.status_code}",
                        file_name=file_name,
                    )

                # Report completion
                if options.on_progress:
                    options.on_progress(100.0)

                return download_url

            except (requests.exceptions.RequestException, FileUploadError) as e:
                if attempt < options.retries:
                    # Exponential backoff
                    time.sleep(attempt + 1)
                    continue
                else:
                    if isinstance(e, FileUploadError):
                        raise
                    raise FileUploadError(
                        f"Failed to upload file after {options.retries + 1} attempts: {str(e)}",
                        file_name=file_name,
                        original_error=e,
                    )

        raise FileUploadError("Upload failed", file_name=file_name)

    def _upload_multipart_file(
        self,
        file: Union[bytes, BinaryIO, Path],
        file_name: str,
        options: UploadOptions,
    ) -> str:
        """Upload a file using multipart upload.

        Args:
            file: The file to upload
            file_name: The name of the file
            options: Upload options

        Returns:
            The download URL of the uploaded file

        Raises:
            FileUploadError: If upload fails
        """
        file_bytes = read_file_bytes(file)
        file_size = len(file_bytes)
        content_type = get_content_type(file_name)

        try:
            # Step 1: Create multipart upload
            url = urljoin(self._base_url + "/", "file-upload/action/create-multipart-upload")
            response = self._session.post(
                url,
                json={
                    "fileSuffix": get_file_extension(file_name),
                    "fileSize": file_size,
                },
                timeout=30,
            )

            if response.status_code != 200:
                raise FileUploadError(
                    f"Failed to create multipart upload: {response.status_code}",
                    file_name=file_name,
                )

            result = response.json()
            data = result.get("data", {})
            upload_id = data.get("uploadID")  # Note: uppercase ID
            key = data.get("key")
            part_size = data.get("partSize", 5 * 1024 * 1024)  # Default 5MB

            if not upload_id or not key:
                raise FileUploadError("Invalid multipart upload response", file_name=file_name)

            # Step 2: Split file into chunks
            chunks: List[bytes] = []
            offset = 0
            while offset < file_size:
                chunk_size = min(part_size, file_size - offset)
                chunks.append(file_bytes[offset : offset + chunk_size])
                offset += chunk_size

            total_chunks = len(chunks)

            # Step 3: Generate presigned URLs for all parts
            url = urljoin(self._base_url + "/", "file-upload/action/generate-presigned-urls")
            response = self._session.post(
                url,
                json={
                    "uploadID": upload_id,  # Uppercase ID
                    "key": key,
                    "partNumbers": list(range(1, total_chunks + 1)),  # Part numbers array [1, 2, 3, ...]
                },
                timeout=30,
            )

            if response.status_code != 200:
                raise FileUploadError(
                    f"Failed to generate presigned URLs: {response.status_code}",
                    file_name=file_name,
                )

            result = response.json()
            data = result.get("data", [])
            # Data itself is the URLs array
            presigned_urls = data if isinstance(data, list) else []

            if len(presigned_urls) != total_chunks:
                raise FileUploadError(
                    f"Expected {total_chunks} presigned URLs, got {len(presigned_urls)}",
                    file_name=file_name,
                )

            # Step 4: Upload chunks concurrently
            uploaded_bytes = 0
            parts_info: List[Dict[str, Any]] = []

            def upload_chunk(index: int, chunk: bytes, presigned_url: str) -> Tuple[int, str]:
                """Upload a single chunk."""
                for attempt in range(options.retries + 1):
                    try:
                        resp = requests.put(
                            presigned_url,
                            data=chunk,
                            headers={"Content-Type": content_type},
                            timeout=300,
                        )

                        if resp.status_code not in [200, 204]:
                            raise FileUploadError(f"Failed to upload chunk {index + 1}")

                        # Get ETag from response headers
                        etag = resp.headers.get("ETag", "").strip('"')
                        if not etag:
                            raise FileUploadError(f"No ETag in response for chunk {index + 1}")

                        return index, etag

                    except Exception as e:
                        if attempt < options.retries:
                            time.sleep(attempt + 1)
                            continue
                        else:
                            raise

                raise FileUploadError(f"Failed to upload chunk {index + 1}")

                # Use ThreadPoolExecutor for concurrent uploads
            with concurrent.futures.ThreadPoolExecutor(
                max_workers=options.max_concurrent_uploads
            ) as executor:
                futures = []
                # presigned_urls is an array of dictionaries: [{"partNumber": 1, "uploadURL": "..."}, ...]
                for i, (chunk, url_info) in enumerate(zip(chunks, presigned_urls)):
                    upload_url = url_info.get("uploadURL") if isinstance(url_info, dict) else url_info
                    future = executor.submit(upload_chunk, i, chunk, upload_url)
                    futures.append(future)

                # Wait for all uploads to complete and track progress
                for future in concurrent.futures.as_completed(futures):
                    try:
                        part_number, etag = future.result()
                        # Note: API expects lowercase field names partNumber and etag
                        parts_info.append({"partNumber": part_number + 1, "etag": etag})
                        uploaded_bytes += len(chunks[part_number])

                        # Report progress
                        if options.on_progress:
                            progress = UploadProgress(
                                uploaded_bytes=uploaded_bytes,
                                total_bytes=file_size,
                                percentage=round(uploaded_bytes / file_size * 100, 2),
                                uploaded_chunks=len(parts_info),
                                total_chunks=total_chunks,
                            )
                            options.on_progress(progress)

                    except Exception as e:
                        # Cancel remaining uploads
                        for f in futures:
                            f.cancel()
                        raise FileUploadError(
                            f"Failed to upload chunks: {str(e)}",
                            file_name=file_name,
                            original_error=e,
                        )

            # Sort parts by part number
            parts_info.sort(key=lambda x: x["partNumber"])

            # Step 5: Complete multipart upload
            url = urljoin(self._base_url + "/", "file-upload/action/complete-multipart-upload")
            response = self._session.post(
                url,
                json={
                    "uploadID": upload_id,  # Uppercase ID
                    "key": key,
                    "parts": parts_info,
                },
                timeout=30,
            )

            if response.status_code != 200:
                raise FileUploadError(
                    f"Failed to complete multipart upload: {response.status_code}",
                    file_name=file_name,
                )

            # Get download URL from complete response
            result = response.json()
            data = result.get("data", {})
            download_url = data.get("downloadURL")

            if not download_url:
                raise FileUploadError("No download URL in complete response", file_name=file_name)

            return download_url

        except FileUploadError:
            raise
        except Exception as e:
            raise FileUploadError(
                f"Multipart upload failed: {str(e)}",
                file_name=file_name,
                original_error=e,
            )


# Export the uploader class
__all__ = [
    "FileUploader",
    "SUPPORTED_FILE_TYPES",
    "MAX_FILE_SIZE",
    "get_content_type",
    "get_file_extension",
]
