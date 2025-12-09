"""Core client implementation for OOMOL Fusion SDK."""

import time
from typing import Any, Dict, Optional
from urllib.parse import urljoin

import requests

from .errors import (
    NetworkError,
    TaskCancelledError,
    TaskFailedError,
    TaskSubmitError,
    TaskTimeoutError,
)
from .types import (
    OomolFusionSDKOptions,
    RunOptions,
    SubmitTaskRequest,
    SubmitTaskResponse,
    TaskResult,
    TaskResultResponse,
    TaskState,
)
from .utils import validate_environment


class OomolFusionSDK:
    """Client for interacting with OOMOL Fusion API.

    This class provides methods to submit tasks, wait for results, and manage
    task execution through the OOMOL Fusion API.

    Example:
        >>> sdk = OomolFusionSDK(token="your-api-token")
        >>> result = sdk.run({
        ...     "service": "fal-nano-banana-pro",
        ...     "inputs": {"prompt": "A beautiful sunset"}
        ... })
        >>> print(result.data)
    """

    def __init__(self, token: str, **kwargs: Any) -> None:
        """Initialize the OOMOL Fusion SDK client.

        Args:
            token: OOMOL API authentication token (required)
            **kwargs: Additional options from OomolFusionSDKOptions
                - base_url: Base URL for the API (default: https://fusion-api.oomol.com/v1)
                - polling_interval: Polling interval in seconds (default: 2.0)
                - timeout: Timeout in seconds (default: 300.0)
        """
        validate_environment()

        # Create options with defaults
        self._options = OomolFusionSDKOptions(
            token=token,
            base_url=kwargs.get("base_url", "https://fusion-api.oomol.com/v1"),
            polling_interval=kwargs.get("polling_interval", 2.0),
            timeout=kwargs.get("timeout", 300.0),
        )

        # Store cancel flags for each session
        self._cancelled_sessions: Dict[str, bool] = {}

        # Create session for connection pooling
        self._session = requests.Session()
        self._session.headers.update({"Authorization": f"Bearer {self._options.token}"})

    def __enter__(self) -> "OomolFusionSDK":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit - closes the session."""
        self.close()

    def close(self) -> None:
        """Close the HTTP session and clean up resources."""
        self._session.close()

    def run(
        self,
        request: SubmitTaskRequest,
        options: Optional[RunOptions] = None,
    ) -> TaskResult:
        """Submit a task and wait for its completion.

        This is the recommended method for most use cases. It combines submit()
        and wait_for() into a single convenient call.

        Args:
            request: The task submission request containing service name and inputs
            options: Optional run options including progress callback

        Returns:
            The completed task result

        Raises:
            TaskSubmitError: If task submission fails
            TaskTimeoutError: If task exceeds timeout limit
            TaskCancelledError: If task is cancelled
            TaskFailedError: If task execution fails
            NetworkError: If network communication fails

        Example:
            >>> result = sdk.run({
            ...     "service": "fal-nano-banana-pro",
            ...     "inputs": {"prompt": "Hello world"}
            ... })
        """
        # Submit the task
        submit_response = self.submit(request)

        # Wait for the result
        return self.wait_for(
            service=request["service"],
            session_id=submit_response["sessionID"],
            options=options,
        )

    def submit(self, request: SubmitTaskRequest) -> SubmitTaskResponse:
        """Submit a task to the OOMOL Fusion API without waiting for completion.

        Use this method when you want to submit a task and retrieve results later
        using wait_for() or get_task_status().

        Args:
            request: The task submission request containing service name and inputs

        Returns:
            The submission response containing session ID

        Raises:
            TaskSubmitError: If task submission fails
            NetworkError: If network communication fails

        Example:
            >>> response = sdk.submit({
            ...     "service": "fal-nano-banana-pro",
            ...     "inputs": {"prompt": "Hello"}
            ... })
            >>> session_id = response["sessionID"]
        """
        service = request["service"]
        inputs = request["inputs"]

        try:
            url = urljoin(self._options.base_url + "/", f"{service}/submit")
            response = self._session.post(url, json=inputs, timeout=30)

            if response.status_code != 200:
                raise TaskSubmitError(
                    f"Failed to submit task: {response.status_code} {response.reason}",
                    status_code=response.status_code,
                    response=response.text,
                )

            result = response.json()

            return SubmitTaskResponse(
                sessionID=result.get("sessionID", ""),
                success=result.get("success", False),
            )

        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Network error during task submission: {str(e)}", e)

    def wait_for(
        self,
        service: str,
        session_id: str,
        options: Optional[RunOptions] = None,
    ) -> TaskResult:
        """Wait for a task to complete by polling its status.

        This method automatically polls the task status at regular intervals until
        the task completes, fails, or times out.

        Args:
            service: The service name
            session_id: The session ID of the task to wait for
            options: Optional run options including progress callback

        Returns:
            The completed task result

        Raises:
            TaskTimeoutError: If task exceeds timeout limit
            TaskCancelledError: If task is cancelled
            TaskFailedError: If task execution fails
            NetworkError: If network communication fails

        Example:
            >>> result = sdk.wait_for("fal-nano-banana-pro", session_id)
        """
        start_time = time.time()
        last_progress: float = 0.0

        while True:
            # Check if task was cancelled
            if self._cancelled_sessions.get(session_id, False):
                del self._cancelled_sessions[session_id]
                raise TaskCancelledError(
                    f"Task {session_id} was cancelled",
                    session_id=session_id,
                    service=service,
                )

            # Check timeout
            elapsed = time.time() - start_time
            if elapsed >= self._options.timeout:
                raise TaskTimeoutError(
                    f"Task {session_id} timed out after {self._options.timeout} seconds",
                    session_id=session_id,
                    service=service,
                    timeout=self._options.timeout,
                )

            # Get task status
            status_response = self.get_task_status(service, session_id)
            state = status_response["state"]

            # Update progress if callback provided
            if options and options.on_progress:
                progress = status_response.get("progress", last_progress)
                if progress != last_progress:
                    options.on_progress(progress)
                    last_progress = progress

            # Check task state
            if state == TaskState.COMPLETED:
                # Ensure progress is 100% on completion
                if options and options.on_progress:
                    options.on_progress(100.0)

                return TaskResult(
                    data=status_response.get("data"),
                    session_id=session_id,
                    service=service,
                )

            elif state in (TaskState.FAILED, TaskState.ERROR):
                raise TaskFailedError(
                    f"Task {session_id} failed with state: {state}",
                    session_id=session_id,
                    service=service,
                    state=state,
                    error_details=status_response.get("error"),
                )

            # Wait before next poll
            time.sleep(self._options.polling_interval)

    def get_task_status(
        self,
        service: str,
        session_id: str,
    ) -> TaskResultResponse:
        """Get the current status of a task without waiting.

        This method performs a single status check without any polling or waiting.

        Args:
            service: The service name
            session_id: The session ID of the task

        Returns:
            The current task status response

        Raises:
            NetworkError: If network communication fails

        Example:
            >>> status = sdk.get_task_status("fal-nano-banana-pro", session_id)
            >>> print(status["state"])
        """
        try:
            url = urljoin(self._options.base_url + "/", f"{service}/result/{session_id}")
            response = self._session.get(url, timeout=30)

            if response.status_code not in [200, 202]:
                raise NetworkError(
                    f"Failed to get task status: {response.status_code} {response.reason}"
                )

            result = response.json()

            return TaskResultResponse(
                state=TaskState(result.get("state", TaskState.PENDING)),
                data=result.get("data"),
                error=result.get("error"),
                progress=result.get("progress", 0.0),
            )

        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Network error during status check: {str(e)}", e)

    def cancel(self, session_id: str) -> None:
        """Cancel a running task.

        This marks the task as cancelled, which will cause wait_for() to stop
        polling and raise a TaskCancelledError.

        Args:
            session_id: The session ID of the task to cancel

        Example:
            >>> sdk.cancel(session_id)
        """
        self._cancelled_sessions[session_id] = True


# Export the main class
__all__ = ["OomolFusionSDK"]
