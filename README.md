# oomol-fusion-sdk

Python SDK for Fusion API task and action endpoints.

This package is designed around the two stable shapes in Fusion API:

- async task endpoints: `submit -> state/result`
- action endpoints: `/action/{name}`

It also includes:

- grouped service shortcuts such as `client.doubao_tts.run_data(...)`
- TypeScript-style aliases such as `client.doubaoTts.runData(...)`
- generated raw OpenAPI types
- normalized error handling

## Install

```bash
pip install oomol-fusion-sdk
```

Requirements:

- Python 3.8+
- `requests`

## Initialize

```python
from oomol_fusion_sdk import FusionClient

client = FusionClient(
    api_key="your-api-key",
)
```

Available client options:

- `api_key: Optional[str]`
- `token: Optional[str]`
- `base_url: str`
- `default_headers: Optional[Dict[str, str]]`
- `poll_interval_ms: int`
- `timeout_ms: int`
- `session: Optional[requests.Session]`

TypeScript-style constructor keys are also accepted:

- `apiKey`
- `baseUrl`
- `defaultHeaders`
- `pollIntervalMs`
- `timeoutMs`

Example with custom `base_url`:

```python
client = FusionClient(
    api_key="your-api-key",
    base_url="https://fusion-api.oomol.com",
    poll_interval_ms=2000,
    timeout_ms=300000,
)
```

Default values:

- `base_url`: `https://fusion-api.oomol.com`
- `poll_interval_ms`: `2000`
- `timeout_ms`: `300000`

## Recommended Usage

Use these defaults unless you have a specific reason not to:

- task endpoints: prefer `run_data()`
- split task control: use `submit()` then `wait_data()`
- action endpoints: prefer grouped methods like `client.jina_reader.read(...)`
- unmodeled future endpoints: use `client.request(...)`

## Quick Start

Task example:

```python
audio = client.doubao_tts.run_data(
    {
        "text": "Hello from Fusion SDK",
        "voice": "zh_female_vv_uranus_bigtts",
    }
)

print(audio)
```

Action example:

```python
page = client.jina_reader.read(
    {
        "URL": "https://example.com/article",
        "format": "markdown",
    }
)

print(page["data"])
```

## Task APIs

Every async task service supports the same workflow methods:

- `submit(payload, options=None)`
- `state(session_id, options=None)`
- `result(session_id, options=None)`
- `wait(session_id, options=None)`
- `run(payload, options=None)`
- `wait_data(session_id, options=None)`
- `run_data(payload, options=None)`

TypeScript-style aliases are also available:

- `waitData(sessionID, options=None)`
- `runData(payload, options=None)`

Example:

```python
submit_response = client.pdf_transform_markdown.submit(
    {
        "pdfURL": "https://example.com/book.pdf",
    }
)

markdown = client.pdf_transform_markdown.wait_data(submit_response["sessionID"])
print(markdown)
```

### `run()` vs `run_data()`

- `run()` returns the completed response shape
- `run_data()` returns the result payload directly

Fusion API completion responses are not perfectly uniform across all services. Some endpoints return:

```python
{"success": True, "state": "completed", "data": {...}}
```

Some return the completed object directly.

`wait_data()` and `run_data()` normalize both cases and are the preferred choice for most callers.

## Built-in Service Shortcuts

Built-in task services:

- `client.doubao_tts`
- `client.doubao_stt`
- `client.oomol_tts`
- `client.fal_remove_background`
- `client.fal_flux_pro_kontext`
- `client.fal_aura_sr`
- `client.fal_sora2_image_to_video`
- `client.fal_sora2_text_to_video`
- `client.fal_nano_banana_2`
- `client.fal_nano_banana`
- `client.image_translate`
- `client.manga_zip_translate`
- `client.qwen_mt_image`
- `client.wanx_image`
- `client.pdf_transform_epub`
- `client.pdf_transform_markdown`
- `client.fal_nano_banana_pro`
- `client.wanx_kf2v_video`
- `client.cphone_nano_banana`

Built-in action groups:

- `client.custom_financial_fundamental_report`
- `client.doubao_text_to_image_seedream`
- `client.text_to_epub_illustrate`
- `client.jina_reader`
- `client.tinify_png_shrink`
- `client.file_upload`
- `client.qwen_image_edit_plus`
- `client.qwen_doc_turbo`

TypeScript-style camelCase aliases for the same shortcuts are also available.

## Action APIs

You can call action endpoints either by grouped shortcut or by raw action key.

Grouped shortcut:

```python
response = client.qwen_doc_turbo.analyze(
    {
        "text": "Product A costs 100 USD.",
        "instruction": "Extract the product name and price.",
    }
)
```

Raw action key:

```python
response = client.action(
    "jina-reader/search",
    {
        "content": "Fusion API SDK",
        "jsonResponse": True,
    },
)
```

## Raw Request Escape Hatch

Use `request()` when the backend adds a new endpoint before the SDK model is updated:

```python
response = client.request(
    path="/v1/new-service/submit",
    method="POST",
    body={
        "prompt": "hello",
    },
)
```

## Runtime Extension

If a new endpoint still matches the standard task shape:

```python
client.register_task("new-service")

result = client.task("new-service").run_data(
    {
        "prompt": "hello",
    }
)
```

If you need to register a custom action endpoint:

```python
client.register_action(
    {
        "key": "custom-service/custom-action",
        "method": "POST",
        "path": "/v1/custom-service/action/custom-action",
    }
)
```

TypeScript-style aliases `registerTask(...)` and `registerAction(...)` are also available.

## Error Handling

The SDK exports a normalized error type:

```python
from oomol_fusion_sdk import OomolFusionSdkError

try:
    result = client.doubao_tts.run_data(
        {
            "text": "hello",
            "voice": "zh_female_vv_uranus_bigtts",
        }
    )
except Exception as error:
    sdk_error = OomolFusionSdkError.from_unknown(error)

    print(sdk_error.code)
    print(str(sdk_error))
    print(sdk_error.status)
    print(sdk_error.retryable)
    print(sdk_error.details)
```

Normalized fields:

- `code`
- `message`
- `status`
- `retryable`
- `details`

## Package Exports

Main SDK:

```python
from oomol_fusion_sdk import FusionClient, OomolFusionSdkError
```

Generated raw OpenAPI types:

```python
from oomol_fusion_sdk.openapi_types import WanxImageSubmitPostRequest
```

Friendly aliases matching the TypeScript registry where practical:

```python
from oomol_fusion_sdk.aliases import WanxImageSubmit, ImageTranslateResultData
```

## Typed Extension

Python does not have a direct equivalent of TypeScript declaration merging. For new APIs that are not yet built into the SDK, define your own `TypedDict` shapes locally and annotate your payloads and results:

```python
from typing import TypedDict


class NewServiceSubmit(TypedDict, total=False):
    prompt: str
    mode: str


payload: NewServiceSubmit = {
    "prompt": "hello",
    "mode": "fast",
}

client.register_task("new-service")
result = client.task("new-service").run_data(payload)
```

## Code Generation

The Python SDK can generate raw OpenAPI types from the shared snapshot:

- `src/oomol_fusion_sdk/generated/openapi_types.py`

Useful commands:

```bash
python3 scripts/generate_openapi_types.py
python3 scripts/generate_openapi_types.py --spec ../oomol-fusion-sdk-ts/openapi.full.snapshot.json
python3 -m unittest discover -s tests
```

## Development Notes

- This package is currently versioned as `2.0.0`
- Built-in grouped services mirror the TypeScript SDK registry
- Generated raw OpenAPI types are exposed as a separate import path
