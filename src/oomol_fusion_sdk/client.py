from __future__ import annotations

import json
import time
from typing import Any, Mapping, Optional, Sequence, Tuple, Union
from urllib.parse import quote, urljoin

import requests

from .errors import (
    FusionApiError,
    FusionTaskNotFoundError,
    FusionTaskTimeoutError,
    OomolFusionSdkError,
)
from .registry import BUILTIN_ACTION_ENDPOINTS
from .services import create_action_shortcuts, create_task_shortcuts
from .types import (
    ActionCallOptions,
    ActionEndpointConfig,
    ExpectedStatusesResponse,
    HeaderMap,
    HttpMethod,
    QueryParams,
    RequestOptions,
    TaskEndpointConfig,
    TaskWaitOptions,
)

DEFAULT_BASE_URL = "https://fusion-api.oomol.com"
DEFAULT_POLL_INTERVAL_MS = 2000
DEFAULT_TIMEOUT_MS = 300000


def _ensure_trailing_slash(value: str) -> str:
    return value if value.endswith("/") else value + "/"


def _build_url(base_url: str, path: str) -> str:
    normalized_path = path if path.startswith("/") else "/" + path
    return urljoin(_ensure_trailing_slash(base_url), normalized_path.lstrip("/"))


def _interpolate_path(template: str, params: Mapping[str, str]) -> str:
    path = template
    for key, value in params.items():
        path = path.replace("{" + key + "}", quote(value, safe=""))
    return path


def _is_plain_object(value: Any) -> bool:
    return isinstance(value, dict)


def _read_json_or_text(response: requests.Response) -> Any:
    content_type = response.headers.get("content-type", "")
    if "application/json" in content_type:
        return response.json()

    text = response.text
    if not text:
        return None

    try:
        return json.loads(text)
    except ValueError:
        return text


class FusionTaskResource:
    def __init__(self, client: "FusionClient", service: str):
        self._client = client
        self.service = service

    def submit(self, input: Any, options: Optional[RequestOptions] = None) -> Any:
        options = options or {}
        return self._client.request(
            path=self._client.resolve_task_path(self.service, "submit"),
            method="POST",
            body=input,
            headers=options.get("headers"),
            timeout=options.get("timeout"),
        )

    def state(self, session_id: str, options: Optional[RequestOptions] = None) -> Any:
        options = options or {}
        _, body = self._client.request_expected_statuses(
            path=self._client.resolve_task_path(self.service, "state", session_id),
            method="GET",
            headers=options.get("headers"),
            timeout=options.get("timeout"),
            expected_statuses=(200, 404),
        )
        return body

    def result(self, session_id: str, options: Optional[RequestOptions] = None) -> Any:
        options = options or {}
        _, body = self._client.request_expected_statuses(
            path=self._client.resolve_task_path(self.service, "result", session_id),
            method="GET",
            headers=options.get("headers"),
            timeout=options.get("timeout"),
            expected_statuses=(200, 202, 404),
        )
        return body

    def wait(self, session_id: str, options: Optional[TaskWaitOptions] = None) -> Any:
        options = options or {}
        timeout_ms = options.get("timeout_ms", options.get("timeoutMs", self._client.timeout_ms))
        poll_interval_ms = options.get(
            "poll_interval_ms",
            options.get("pollIntervalMs", self._client.poll_interval_ms),
        )
        on_progress = options.get("on_progress") or options.get("onProgress")
        started_at = time.monotonic()

        while (time.monotonic() - started_at) * 1000 < timeout_ms:
            status, body = self._client.request_expected_statuses(
                path=self._client.resolve_task_path(self.service, "result", session_id),
                method="GET",
                headers=options.get("headers"),
                timeout=options.get("timeout"),
                expected_statuses=(200, 202, 404),
            )

            if status == 200:
                return body

            if status == 404:
                message = body.get("error") if isinstance(body, dict) else None
                raise FusionTaskNotFoundError(self.service, session_id, message)

            if callable(on_progress) and isinstance(body, dict):
                on_progress(float(body.get("progress", 0)), body)

            time.sleep(poll_interval_ms / 1000.0)

        raise FusionTaskTimeoutError(self.service, session_id, int(timeout_ms))

    def run(self, input: Any, options: Optional[TaskWaitOptions] = None) -> Any:
        response = self.submit(input, options)
        session_id = response["sessionID"]
        return self.wait(session_id, options)

    def wait_data(self, session_id: str, options: Optional[TaskWaitOptions] = None) -> Any:
        response = self.wait(session_id, options)
        if isinstance(response, dict) and "data" in response:
            return response["data"]
        return response

    def run_data(self, input: Any, options: Optional[TaskWaitOptions] = None) -> Any:
        response = self.submit(input, options)
        session_id = response["sessionID"]
        return self.wait_data(session_id, options)

    def waitData(self, sessionID: str, options: Optional[TaskWaitOptions] = None) -> Any:
        return self.wait_data(sessionID, options)

    def runData(self, input: Any, options: Optional[TaskWaitOptions] = None) -> Any:
        return self.run_data(input, options)


class FusionActionsClient:
    def __init__(self, client: "FusionClient"):
        self._client = client

    def register(self, definition: ActionEndpointConfig) -> "FusionActionsClient":
        self._client.register_action(definition)
        return self

    def call(self, key: str, request: Any = None, options: Optional[ActionCallOptions] = None) -> Any:
        options = options or {}
        definition = self._client.resolve_action_definition(key, options.get("method"))
        path = definition.get("path") or self._client.build_action_path_from_key(key)

        if definition["method"] == "GET":
            query = request if _is_plain_object(request) else None
            return self._client.request(
                path=path,
                method="GET",
                query=query,
                headers=options.get("headers"),
                timeout=options.get("timeout"),
            )

        return self._client.request(
            path=path,
            method=definition["method"],
            body=request,
            headers=options.get("headers"),
            timeout=options.get("timeout"),
        )

    def call_by_name(
        self,
        service: str,
        action: str,
        request: Any = None,
        options: Optional[ActionCallOptions] = None,
    ) -> Any:
        return self.call(service + "/" + action, request, options)

    def callByName(
        self,
        service: str,
        action: str,
        request: Any = None,
        options: Optional[ActionCallOptions] = None,
    ) -> Any:
        return self.call_by_name(service, action, request, options)


class FusionClient:
    def __init__(
        self,
        api_key: Optional[str] = None,
        token: Optional[str] = None,
        base_url: str = DEFAULT_BASE_URL,
        default_headers: Optional[HeaderMap] = None,
        poll_interval_ms: int = DEFAULT_POLL_INTERVAL_MS,
        timeout_ms: int = DEFAULT_TIMEOUT_MS,
        session: Optional[requests.Session] = None,
        **kwargs: Any
    ):
        api_key = kwargs.get("apiKey", api_key)
        base_url = kwargs.get("baseUrl", base_url)
        default_headers = kwargs.get("defaultHeaders", default_headers)
        poll_interval_ms = kwargs.get("pollIntervalMs", poll_interval_ms)
        timeout_ms = kwargs.get("timeoutMs", timeout_ms)

        self.base_url = base_url
        self.poll_interval_ms = poll_interval_ms
        self.timeout_ms = timeout_ms
        self.session = session or requests.Session()
        self.default_headers = dict(default_headers or {})
        self._task_registry = {}
        self._action_registry = {}

        auth_token = api_key or token
        if auth_token:
            self.default_headers["Authorization"] = (
                auth_token if auth_token.startswith("Bearer ") else "Bearer " + auth_token
            )

        for definition in BUILTIN_ACTION_ENDPOINTS:
            self._action_registry[definition["key"]] = dict(definition)

        self.actions = FusionActionsClient(self)

        for name, value in create_task_shortcuts(self).items():
            setattr(self, name, value)
        for name, value in create_action_shortcuts(self).items():
            setattr(self, name, value)

    def task(self, service: str) -> FusionTaskResource:
        return FusionTaskResource(self, service)

    def register_task(
        self,
        service_or_definition: Union[str, TaskEndpointConfig],
        overrides: Optional[TaskEndpointConfig] = None,
    ) -> "FusionClient":
        overrides = overrides or {}
        if isinstance(service_or_definition, str):
            definition = {"service": service_or_definition}
            definition.update(overrides)
        else:
            definition = dict(service_or_definition)
        self._task_registry[definition["service"]] = definition
        return self

    def registerTask(
        self,
        serviceOrDefinition: Union[str, TaskEndpointConfig],
        overrides: Optional[TaskEndpointConfig] = None,
    ) -> "FusionClient":
        return self.register_task(serviceOrDefinition, overrides)

    def register_action(self, definition: ActionEndpointConfig) -> "FusionClient":
        self._action_registry[definition["key"]] = dict(definition)
        return self

    def registerAction(self, definition: ActionEndpointConfig) -> "FusionClient":
        return self.register_action(definition)

    def resolve_task_path(
        self,
        service: str,
        kind: str,
        session_id: Optional[str] = None,
    ) -> str:
        definition = self._task_registry.get(service, {})
        if kind == "submit":
            template = definition.get("submit_path") or definition.get("submitPath") or "/v1/{service}/submit"
        elif kind == "state":
            template = definition.get("state_path") or definition.get("statePath") or "/v1/{service}/state/{sessionID}"
        else:
            template = definition.get("result_path") or definition.get("resultPath") or "/v1/{service}/result/{sessionID}"

        return _interpolate_path(
            template,
            {"service": service, "sessionID": session_id or ""},
        )

    def resolveTaskPath(self, service: str, kind: str, sessionID: Optional[str] = None) -> str:
        return self.resolve_task_path(service, kind, sessionID)

    def build_action_path_from_key(self, key: str) -> str:
        parts = key.split("/")
        if len(parts) < 2:
            raise ValueError('Invalid action key "{key}". Expected "service/action".'.format(key=key))
        return "/v1/{service}/action/{action}".format(service=parts[0], action="/".join(parts[1:]))

    def buildActionPathFromKey(self, key: str) -> str:
        return self.build_action_path_from_key(key)

    def resolve_action_definition(
        self,
        key: str,
        fallback_method: Optional[HttpMethod] = None,
    ) -> ActionEndpointConfig:
        return dict(self._action_registry.get(key, {"key": key, "method": fallback_method or "POST"}))

    def resolveActionDefinition(
        self,
        key: str,
        fallbackMethod: Optional[HttpMethod] = None,
    ) -> ActionEndpointConfig:
        return self.resolve_action_definition(key, fallbackMethod)

    def action(self, key: str, request: Any = None, options: Optional[ActionCallOptions] = None) -> Any:
        return self.actions.call(key, request, options)

    def request(
        self,
        path: str,
        method: HttpMethod = "GET",
        query: Optional[QueryParams] = None,
        body: Any = None,
        headers: Optional[HeaderMap] = None,
        timeout: Optional[float] = None,
    ) -> Any:
        try:
            response = self._request_raw(path, method, query, body, headers, timeout)
            if not response.ok:
                raise self._build_api_error(response, path)
            return _read_json_or_text(response)
        except Exception as error:
            raise OomolFusionSdkError.from_unknown(error)

    def request_expected_statuses(
        self,
        path: str,
        expected_statuses: Sequence[int],
        method: HttpMethod = "GET",
        query: Optional[QueryParams] = None,
        body: Any = None,
        headers: Optional[HeaderMap] = None,
        timeout: Optional[float] = None,
    ) -> ExpectedStatusesResponse:
        try:
            response = self._request_raw(path, method, query, body, headers, timeout)
            if response.status_code not in expected_statuses:
                raise self._build_api_error(response, path)
            return response.status_code, _read_json_or_text(response)
        except Exception as error:
            raise OomolFusionSdkError.from_unknown(error)

    def requestExpectedStatuses(
        self,
        path: str,
        expectedStatuses: Sequence[int],
        method: HttpMethod = "GET",
        query: Optional[QueryParams] = None,
        body: Any = None,
        headers: Optional[HeaderMap] = None,
        timeout: Optional[float] = None,
    ) -> ExpectedStatusesResponse:
        return self.request_expected_statuses(path, expectedStatuses, method, query, body, headers, timeout)

    def _request_raw(
        self,
        path: str,
        method: HttpMethod,
        query: Optional[QueryParams],
        body: Any,
        headers: Optional[HeaderMap],
        timeout: Optional[float],
    ) -> requests.Response:
        merged_headers = dict(self.default_headers)
        if headers:
            merged_headers.update(headers)

        request_kwargs = {
            "headers": merged_headers,
            "params": query,
        }
        if timeout is not None:
            request_kwargs["timeout"] = timeout

        if body is not None and method != "GET":
            merged_headers.setdefault("Content-Type", "application/json")
            request_kwargs["json"] = body

        return self.session.request(method, _build_url(self.base_url, path), **request_kwargs)

    def _build_api_error(self, response: requests.Response, path: str) -> FusionApiError:
        body = _read_json_or_text(response)
        message = None
        if isinstance(body, dict):
            message = body.get("error") or body.get("message")
        if not isinstance(message, str):
            message = "HTTP {status} {reason}".format(
                status=response.status_code,
                reason=getattr(response, "reason", ""),
            ).strip()
        return FusionApiError(message, response.status_code, path, body)
