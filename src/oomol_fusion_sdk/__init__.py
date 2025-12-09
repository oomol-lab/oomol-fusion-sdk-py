"""OOMOL Fusion SDK - Official Python SDK for OOMOL Fusion API.

This SDK provides a simple and intuitive interface to interact with OOMOL Fusion API,
allowing you to submit tasks, monitor their progress, and retrieve results.

Example:
    >>> from oomol_fusion_sdk import OomolFusionSDK
    >>> sdk = OomolFusionSDK(token="your-api-token")
    >>> result = sdk.run({
    ...     "service": "fal-nano-banana-pro",
    ...     "inputs": {"prompt": "A beautiful sunset"}
    ... })
    >>> print(result.data)
"""

__version__ = "1.0.0"

# Import main client
from .client import OomolFusionSDK

# Import all error classes
from .errors import (
    NetworkError,
    OomolFusionError,
    TaskCancelledError,
    TaskFailedError,
    TaskSubmitError,
    TaskTimeoutError,
)

# Import all types
from .types import (
    OomolFusionSDKOptions,
    ProgressCallback,
    RunOptions,
    SubmitTaskRequest,
    SubmitTaskResponse,
    TaskResult,
    TaskResultResponse,
    TaskState,
)

# Import utility functions
from .utils import detect_environment, is_requests_available, validate_environment

# Define public API
__all__ = [
    # Main client
    "OomolFusionSDK",
    # Types
    "TaskState",
    "ProgressCallback",
    "SubmitTaskRequest",
    "SubmitTaskResponse",
    "TaskResultResponse",
    "TaskResult",
    "RunOptions",
    "OomolFusionSDKOptions",
    # Errors
    "OomolFusionError",
    "TaskSubmitError",
    "TaskTimeoutError",
    "TaskCancelledError",
    "TaskFailedError",
    "NetworkError",
    # Utils
    "detect_environment",
    "is_requests_available",
    "validate_environment",
]
