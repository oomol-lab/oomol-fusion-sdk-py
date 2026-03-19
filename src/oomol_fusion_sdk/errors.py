from __future__ import annotations

from enum import Enum
from typing import Any, Dict, Optional


class FusionError(Exception):
    pass


class FusionApiError(FusionError):
    def __init__(self, message: str, status: int, path: str, body: Any):
        super().__init__(message)
        self.status = status
        self.path = path
        self.body = body


class FusionTaskTimeoutError(FusionError):
    def __init__(self, service: str, session_id: str, timeout_ms: int):
        super().__init__('Task "{service}" timed out after {timeout_ms}ms: {session_id}'.format(
            service=service,
            timeout_ms=timeout_ms,
            session_id=session_id,
        ))
        self.service = service
        self.session_id = session_id
        self.sessionID = session_id


class FusionTaskNotFoundError(FusionError):
    def __init__(self, service: str, session_id: str, message: Optional[str] = None):
        super().__init__(message or 'Task "{service}" was not found: {session_id}'.format(
            service=service,
            session_id=session_id,
        ))
        self.service = service
        self.session_id = session_id
        self.sessionID = session_id


class FusionErrorCode(str, Enum):
    HTTP_ERROR = "HTTP_ERROR"
    TASK_NOT_FOUND = "TASK_NOT_FOUND"
    TASK_TIMEOUT = "TASK_TIMEOUT"
    NETWORK_ERROR = "NETWORK_ERROR"
    UNKNOWN_ERROR = "UNKNOWN_ERROR"


class OomolFusionSdkError(FusionError):
    def __init__(
        self,
        code: FusionErrorCode,
        message: str,
        retryable: bool,
        status: Optional[int] = None,
        details: Any = None,
    ):
        super().__init__(message)
        self.code = code.value if isinstance(code, FusionErrorCode) else str(code)
        self.status = status
        self.retryable = retryable
        self.details = details

    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code,
            "message": str(self),
            "status": self.status,
            "retryable": self.retryable,
            "details": self.details,
        }

    def toJSON(self) -> Dict[str, Any]:
        return self.to_dict()

    @staticmethod
    def from_unknown(error: Any) -> "OomolFusionSdkError":
        if isinstance(error, OomolFusionSdkError):
            return error

        if isinstance(error, FusionApiError):
            retryable = error.status >= 500 or error.status in (408, 429)
            return OomolFusionSdkError(
                code=FusionErrorCode.HTTP_ERROR,
                message=str(error),
                status=error.status,
                retryable=retryable,
                details={"path": error.path, "body": error.body},
            )

        if isinstance(error, FusionTaskNotFoundError):
            return OomolFusionSdkError(
                code=FusionErrorCode.TASK_NOT_FOUND,
                message=str(error),
                retryable=False,
                details={"service": error.service, "sessionID": error.session_id},
            )

        if isinstance(error, FusionTaskTimeoutError):
            return OomolFusionSdkError(
                code=FusionErrorCode.TASK_TIMEOUT,
                message=str(error),
                retryable=True,
                details={"service": error.service, "sessionID": error.session_id},
            )

        if isinstance(error, Exception):
            lower_message = str(error).lower()
            looks_network_related = any(
                token in lower_message
                for token in ("network", "connection", "aborted", "timed out", "timeout", "fetch")
            )
            return OomolFusionSdkError(
                code=FusionErrorCode.NETWORK_ERROR if looks_network_related else FusionErrorCode.UNKNOWN_ERROR,
                message=str(error),
                retryable=looks_network_related,
                details=error,
            )

        return OomolFusionSdkError(
            code=FusionErrorCode.UNKNOWN_ERROR,
            message="Unknown SDK error",
            retryable=False,
            details=error,
        )

