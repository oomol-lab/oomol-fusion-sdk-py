"""Type definitions for OOMOL Fusion SDK."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, Literal, Optional, TypedDict


class TaskState(str, Enum):
    """Task execution states."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    ERROR = "error"


# Type alias for progress callback
ProgressCallback = Callable[[float], None]


class SubmitTaskRequest(TypedDict):
    """Request structure for submitting a task.

    Attributes:
        service: The service name to invoke (e.g., 'fal-nano-banana-pro')
        inputs: Dynamic input parameters for the service
    """

    service: str
    inputs: Dict[str, Any]


class SubmitTaskResponse(TypedDict):
    """Response structure after submitting a task.

    Attributes:
        sessionID: Unique identifier for the task session
        success: Whether the submission was successful
    """

    sessionID: str
    success: bool


class TaskResultResponse(TypedDict, total=False):
    """Response structure for task status and result.

    Attributes:
        state: Current state of the task
        data: Task result data (optional, present when completed)
        error: Error message (optional, present when failed)
        progress: Task progress percentage 0-100 (optional)
    """

    state: TaskState
    data: Any
    error: str
    progress: float


@dataclass
class TaskResult:
    """Final result of a completed task.

    Attributes:
        data: The task result data
        session_id: The session ID of the task
        service: The service name that processed the task
    """

    data: Any
    session_id: str
    service: str


@dataclass
class RunOptions:
    """Options for running a task.

    Attributes:
        on_progress: Optional callback function to receive progress updates
    """

    on_progress: Optional[ProgressCallback] = None


@dataclass
class OomolFusionSDKOptions:
    """Configuration options for OomolFusionSDK.

    Attributes:
        token: OOMOL API authentication token (required)
        base_url: Base URL for the OOMOL Fusion API
        polling_interval: Interval in seconds between status checks
        timeout: Maximum time in seconds to wait for task completion
    """

    token: str
    base_url: str = "https://fusion-api.oomol.com/v1"
    polling_interval: float = 2.0
    timeout: float = 300.0


# Export all public types
__all__ = [
    "TaskState",
    "ProgressCallback",
    "SubmitTaskRequest",
    "SubmitTaskResponse",
    "TaskResultResponse",
    "TaskResult",
    "RunOptions",
    "OomolFusionSDKOptions",
]
