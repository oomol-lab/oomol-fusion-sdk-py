from __future__ import annotations

from typing import Any, Callable, Dict, List, Mapping, Optional, Sequence, Tuple, TypedDict, Union

try:
    from typing import Literal
except ImportError:  # pragma: no cover
    from typing_extensions import Literal

HttpMethod = Literal["GET", "POST", "PUT", "PATCH", "DELETE"]
QueryPrimitive = Optional[Union[str, int, float, bool]]
QueryValue = Union[QueryPrimitive, Sequence[QueryPrimitive]]
QueryParams = Mapping[str, QueryValue]
HeaderMap = Dict[str, str]
JsonObject = Dict[str, Any]
ProgressCallback = Callable[[float, Mapping[str, Any]], None]


class SubmitResponse(TypedDict):
    success: bool
    sessionID: str


class ErrorResponse(TypedDict):
    error: str


class ActionResponse(TypedDict, total=False):
    success: bool
    data: Any


class ProcessingTaskResponse(TypedDict):
    success: bool
    state: Literal["processing"]
    progress: float


class NotFoundTaskResponse(TypedDict):
    success: bool
    state: Literal["not_found"]
    error: str


class CompletedTaskStateResponse(TypedDict):
    success: bool
    state: Literal["completed"]


class CompletedTaskResultResponse(TypedDict, total=False):
    success: bool
    state: Literal["completed"]
    data: Any


class RequestOptions(TypedDict, total=False):
    headers: HeaderMap
    timeout: float


class TaskWaitOptions(RequestOptions, total=False):
    poll_interval_ms: int
    pollIntervalMs: int
    timeout_ms: int
    timeoutMs: int
    on_progress: ProgressCallback
    onProgress: ProgressCallback


class ActionCallOptions(RequestOptions, total=False):
    method: HttpMethod


class TaskEndpointConfig(TypedDict, total=False):
    service: str
    submit_path: str
    submitPath: str
    state_path: str
    statePath: str
    result_path: str
    resultPath: str


class ActionEndpointConfig(TypedDict, total=False):
    key: str
    method: HttpMethod
    path: str


ExpectedStatusesResponse = Tuple[int, Any]
