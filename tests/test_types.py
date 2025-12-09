"""Tests for OOMOL Fusion SDK types."""

from oomol_fusion_sdk.types import (
    TaskState,
    TaskResult,
    RunOptions,
    OomolFusionSDKOptions,
)


def test_task_state_enum() -> None:
    """Test TaskState enum values."""
    assert TaskState.PENDING == "pending"
    assert TaskState.PROCESSING == "processing"
    assert TaskState.COMPLETED == "completed"
    assert TaskState.FAILED == "failed"
    assert TaskState.ERROR == "error"


def test_task_result_dataclass() -> None:
    """Test TaskResult dataclass."""
    result = TaskResult(
        data={"output": "test"},
        session_id="session-123",
        service="test-service",
    )

    assert result.data == {"output": "test"}
    assert result.session_id == "session-123"
    assert result.service == "test-service"


def test_run_options_dataclass() -> None:
    """Test RunOptions dataclass."""
    callback_called = False

    def progress_callback(progress: float) -> None:
        nonlocal callback_called
        callback_called = True

    options = RunOptions(on_progress=progress_callback)
    assert options.on_progress is not None

    # Test callback
    options.on_progress(50.0)
    assert callback_called


def test_run_options_defaults() -> None:
    """Test RunOptions default values."""
    options = RunOptions()
    assert options.on_progress is None


def test_sdk_options_dataclass() -> None:
    """Test OomolFusionSDKOptions dataclass."""
    options = OomolFusionSDKOptions(
        token="test-token",
        base_url="https://test.com",
        polling_interval=1.0,
        timeout=60.0,
    )

    assert options.token == "test-token"
    assert options.base_url == "https://test.com"
    assert options.polling_interval == 1.0
    assert options.timeout == 60.0


def test_sdk_options_defaults() -> None:
    """Test OomolFusionSDKOptions default values."""
    options = OomolFusionSDKOptions(token="test-token")

    assert options.token == "test-token"
    assert options.base_url == "https://fusion-api.oomol.com/v1"
    assert options.polling_interval == 2.0
    assert options.timeout == 300.0
