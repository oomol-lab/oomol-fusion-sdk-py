"""Custom exception classes for OOMOL Fusion SDK."""

from typing import Any, Optional

from .types import TaskState


class OomolFusionError(Exception):
    """Base exception class for all OOMOL Fusion SDK errors."""

    def __init__(self, message: str) -> None:
        """Initialize the base error.

        Args:
            message: The error message
        """
        self.message = message
        super().__init__(message)


class TaskSubmitError(OomolFusionError):
    """Exception raised when task submission fails.

    Attributes:
        message: The error message
        status_code: HTTP status code of the failed request (if available)
        response: The response body from the server (if available)
    """

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response: Optional[Any] = None,
    ) -> None:
        """Initialize the task submit error.

        Args:
            message: The error message
            status_code: HTTP status code of the failed request
            response: The response body from the server
        """
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class TaskTimeoutError(OomolFusionError):
    """Exception raised when a task exceeds the timeout limit.

    Attributes:
        message: The error message
        session_id: The session ID of the timed out task
        service: The service name
        timeout: The timeout duration in seconds
    """

    def __init__(
        self,
        message: str,
        session_id: str,
        service: str,
        timeout: float,
    ) -> None:
        """Initialize the task timeout error.

        Args:
            message: The error message
            session_id: The session ID of the timed out task
            service: The service name
            timeout: The timeout duration in seconds
        """
        super().__init__(message)
        self.session_id = session_id
        self.service = service
        self.timeout = timeout


class TaskCancelledError(OomolFusionError):
    """Exception raised when a task is cancelled by the user.

    Attributes:
        message: The error message
        session_id: The session ID of the cancelled task
        service: The service name
    """

    def __init__(self, message: str, session_id: str, service: str) -> None:
        """Initialize the task cancelled error.

        Args:
            message: The error message
            session_id: The session ID of the cancelled task
            service: The service name
        """
        super().__init__(message)
        self.session_id = session_id
        self.service = service


class TaskFailedError(OomolFusionError):
    """Exception raised when a task execution fails on the server.

    Attributes:
        message: The error message
        session_id: The session ID of the failed task
        service: The service name
        state: The final state of the task
        error_details: Additional error details from the server
    """

    def __init__(
        self,
        message: str,
        session_id: str,
        service: str,
        state: TaskState,
        error_details: Optional[str] = None,
    ) -> None:
        """Initialize the task failed error.

        Args:
            message: The error message
            session_id: The session ID of the failed task
            service: The service name
            state: The final state of the task
            error_details: Additional error details from the server
        """
        super().__init__(message)
        self.session_id = session_id
        self.service = service
        self.state = state
        self.error_details = error_details


class NetworkError(OomolFusionError):
    """Exception raised when a network communication error occurs.

    Attributes:
        message: The error message
        original_error: The underlying exception that caused the network error
    """

    def __init__(self, message: str, original_error: Optional[Exception] = None) -> None:
        """Initialize the network error.

        Args:
            message: The error message
            original_error: The underlying exception that caused the network error
        """
        super().__init__(message)
        self.original_error = original_error


class FileUploadError(OomolFusionError):
    """Exception raised when file upload fails.

    Attributes:
        message: The error message
        file_name: The name of the file that failed to upload
        original_error: The underlying exception that caused the upload error
    """

    def __init__(
        self,
        message: str,
        file_name: Optional[str] = None,
        original_error: Optional[Exception] = None,
    ) -> None:
        """Initialize the file upload error.

        Args:
            message: The error message
            file_name: The name of the file that failed to upload
            original_error: The underlying exception that caused the upload error
        """
        super().__init__(message)
        self.file_name = file_name
        self.original_error = original_error


class FileTooLargeError(OomolFusionError):
    """Exception raised when file size exceeds the maximum allowed size.

    Attributes:
        message: The error message
        file_size: The size of the file in bytes
        max_size: The maximum allowed file size in bytes
    """

    def __init__(self, message: str, file_size: int, max_size: int) -> None:
        """Initialize the file too large error.

        Args:
            message: The error message
            file_size: The size of the file in bytes
            max_size: The maximum allowed file size in bytes
        """
        super().__init__(message)
        self.file_size = file_size
        self.max_size = max_size


# Export all error classes
__all__ = [
    "OomolFusionError",
    "TaskSubmitError",
    "TaskTimeoutError",
    "TaskCancelledError",
    "TaskFailedError",
    "NetworkError",
    "FileUploadError",
    "FileTooLargeError",
]
