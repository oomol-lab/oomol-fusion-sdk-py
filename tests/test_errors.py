"""Tests for OOMOL Fusion SDK errors."""

import pytest
from oomol_fusion_sdk.errors import (
    OomolFusionError,
    TaskSubmitError,
    TaskTimeoutError,
    TaskCancelledError,
    TaskFailedError,
    NetworkError,
)
from oomol_fusion_sdk.types import TaskState


def test_base_error() -> None:
    """Test OomolFusionError base class."""
    error = OomolFusionError("Test error")
    assert error.message == "Test error"
    assert str(error) == "Test error"
    assert isinstance(error, Exception)


def test_task_submit_error() -> None:
    """Test TaskSubmitError."""
    error = TaskSubmitError(
        "Submit failed",
        status_code=400,
        response={"error": "Bad request"},
    )

    assert error.message == "Submit failed"
    assert error.status_code == 400
    assert error.response == {"error": "Bad request"}
    assert isinstance(error, OomolFusionError)


def test_task_submit_error_minimal() -> None:
    """Test TaskSubmitError with minimal arguments."""
    error = TaskSubmitError("Submit failed")
    assert error.message == "Submit failed"
    assert error.status_code is None
    assert error.response is None


def test_task_timeout_error() -> None:
    """Test TaskTimeoutError."""
    error = TaskTimeoutError(
        "Task timed out",
        session_id="session-123",
        service="test-service",
        timeout=300.0,
    )

    assert error.message == "Task timed out"
    assert error.session_id == "session-123"
    assert error.service == "test-service"
    assert error.timeout == 300.0
    assert isinstance(error, OomolFusionError)


def test_task_cancelled_error() -> None:
    """Test TaskCancelledError."""
    error = TaskCancelledError(
        "Task cancelled",
        session_id="session-456",
        service="test-service",
    )

    assert error.message == "Task cancelled"
    assert error.session_id == "session-456"
    assert error.service == "test-service"
    assert isinstance(error, OomolFusionError)


def test_task_failed_error() -> None:
    """Test TaskFailedError."""
    error = TaskFailedError(
        "Task failed",
        session_id="session-789",
        service="test-service",
        state=TaskState.FAILED,
        error_details="Server error",
    )

    assert error.message == "Task failed"
    assert error.session_id == "session-789"
    assert error.service == "test-service"
    assert error.state == TaskState.FAILED
    assert error.error_details == "Server error"
    assert isinstance(error, OomolFusionError)


def test_task_failed_error_minimal() -> None:
    """Test TaskFailedError with minimal arguments."""
    error = TaskFailedError(
        "Task failed",
        session_id="session-789",
        service="test-service",
        state=TaskState.ERROR,
    )

    assert error.error_details is None


def test_network_error() -> None:
    """Test NetworkError."""
    original = ValueError("Connection failed")
    error = NetworkError("Network error occurred", original)

    assert error.message == "Network error occurred"
    assert error.original_error is original
    assert isinstance(error, OomolFusionError)


def test_network_error_minimal() -> None:
    """Test NetworkError with minimal arguments."""
    error = NetworkError("Network error occurred")
    assert error.message == "Network error occurred"
    assert error.original_error is None


def test_error_inheritance() -> None:
    """Test error inheritance chain."""
    errors = [
        TaskSubmitError("test"),
        TaskTimeoutError("test", "sid", "svc", 300.0),
        TaskCancelledError("test", "sid", "svc"),
        TaskFailedError("test", "sid", "svc", TaskState.FAILED),
        NetworkError("test"),
    ]

    for error in errors:
        assert isinstance(error, OomolFusionError)
        assert isinstance(error, Exception)
