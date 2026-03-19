import os
import sys
import unittest
from unittest.mock import patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from oomol_fusion_sdk import (  # noqa: E402
    FusionClient,
    FusionTaskNotFoundError,
    FusionTaskTimeoutError,
    OomolFusionSdkError,
)
from oomol_fusion_sdk.aliases import (  # noqa: E402
    DoubaoTTSSubmit,
    ImageTranslateResultData,
    WanxImageSubmit,
)
from oomol_fusion_sdk.openapi_types import (  # noqa: E402
    FalRemoveBackgroundResult,
    ImageTranslateResultSessionID200Response,
    WanxImageSubmitPostRequest,
)


class FakeResponse:
    def __init__(
        self,
        ok=True,
        status_code=200,
        json_data=None,
        text="",
        headers=None,
        reason="OK",
    ):
        self.ok = ok
        self.status_code = status_code
        self._json_data = json_data
        self.text = text
        self.headers = headers or {"content-type": "application/json"}
        self.reason = reason

    def json(self):
        return self._json_data


class FakeSession:
    def __init__(self, responses=None, error=None):
        self.responses = list(responses or [])
        self.error = error
        self.calls = []

    def request(self, method, url, **kwargs):
        self.calls.append({"method": method, "url": url, **kwargs})
        if self.error is not None:
            raise self.error
        return self.responses.pop(0)


class FusionClientTests(unittest.TestCase):
    def test_friendly_aliases_are_importable(self):
        self.assertIn("text", DoubaoTTSSubmit.__annotations__)
        self.assertIn("translatedImageURL", ImageTranslateResultData.__annotations__)
        self.assertIn("prompt", WanxImageSubmit.__annotations__)

    def test_generated_openapi_types_are_importable(self):
        self.assertIn("image", FalRemoveBackgroundResult.__annotations__)
        self.assertIn("translatedImageURL", ImageTranslateResultSessionID200Response.__annotations__)
        self.assertIn("prompt", WanxImageSubmitPostRequest.__annotations__)

    def test_shortcuts_and_auth_header_are_initialized(self):
        session = FakeSession(
            responses=[
                FakeResponse(json_data={"success": True, "data": {"items": []}}),
            ]
        )
        client = FusionClient(apiKey="test-key", session=session)

        response = client.customFinancialFundamentalReport.reportList({"symbol": "AAPL"})

        self.assertEqual(response["data"]["items"], [])
        self.assertTrue(hasattr(client, "doubao_tts"))
        self.assertTrue(hasattr(client, "doubaoTts"))
        self.assertEqual(session.calls[0]["headers"]["Authorization"], "Bearer test-key")

    def test_get_action_uses_query_params(self):
        session = FakeSession(
            responses=[
                FakeResponse(json_data={"success": True, "data": {"ok": True}}),
            ]
        )
        client = FusionClient(api_key="test-key", session=session)

        response = client.actions.call_by_name(
            "custom-financial-fundamental-report",
            "report",
            {"ticker": "TSLA"},
        )

        self.assertEqual(response["data"]["ok"], True)
        self.assertEqual(session.calls[0]["method"], "GET")
        self.assertEqual(session.calls[0]["params"], {"ticker": "TSLA"})

    @patch("oomol_fusion_sdk.client.time.sleep", return_value=None)
    def test_task_run_data_polls_until_completed(self, _sleep):
        session = FakeSession(
            responses=[
                FakeResponse(json_data={"success": True, "sessionID": "session-1"}),
                FakeResponse(status_code=202, json_data={"success": True, "state": "processing", "progress": 42}),
                FakeResponse(
                    json_data={"success": True, "state": "completed", "data": {"url": "https://files.example/result"}}
                ),
            ]
        )
        client = FusionClient(api_key="test-key", session=session)
        progress_events = []

        result = client.pdf_transform_markdown.run_data(
            {"pdfURL": "https://example.com/book.pdf"},
            {"on_progress": lambda progress, body: progress_events.append((progress, body["state"]))},
        )

        self.assertEqual(result["url"], "https://files.example/result")
        self.assertEqual(progress_events, [(42.0, "processing")])
        self.assertEqual(session.calls[0]["url"], "https://fusion-api.oomol.com/v1/pdf-transform-markdown/submit")

    @patch("oomol_fusion_sdk.client.time.sleep", return_value=None)
    def test_task_wait_raises_not_found(self, _sleep):
        session = FakeSession(
            responses=[
                FakeResponse(status_code=404, json_data={"error": "missing session"}),
            ]
        )
        client = FusionClient(api_key="test-key", session=session)

        with self.assertRaises(FusionTaskNotFoundError) as ctx:
            client.image_translate.wait("missing-session", {"pollIntervalMs": 1})

        self.assertEqual(str(ctx.exception), "missing session")
        self.assertEqual(ctx.exception.sessionID, "missing-session")

    def test_request_http_error_is_normalized(self):
        session = FakeSession(
            responses=[
                FakeResponse(ok=False, status_code=429, json_data={"error": "rate limited"}, reason="Too Many Requests"),
            ]
        )
        client = FusionClient(api_key="test-key", session=session)

        with self.assertRaises(OomolFusionSdkError) as ctx:
            client.request("/v1/example")

        self.assertEqual(ctx.exception.code, "HTTP_ERROR")
        self.assertEqual(ctx.exception.status, 429)
        self.assertEqual(ctx.exception.retryable, True)

    def test_timeout_error_is_normalized(self):
        error = OomolFusionSdkError.from_unknown(FusionTaskTimeoutError("demo", "session-1", 500))
        self.assertEqual(error.code, "TASK_TIMEOUT")
        self.assertEqual(error.retryable, True)
        self.assertEqual(error.details["sessionID"], "session-1")


if __name__ == "__main__":
    unittest.main()
