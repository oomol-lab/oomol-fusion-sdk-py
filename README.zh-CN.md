# oomol-fusion-sdk

Fusion API 的 Python SDK。

这个包围绕 Fusion API 里两种稳定接口形态设计：

- 异步任务型接口：`submit -> state/result`
- 动作型接口：`/action/{name}`

同时它还提供：

- 按服务分组的快捷调用，例如 `client.doubao_tts.run_data(...)`
- TypeScript 风格别名，例如 `client.doubaoTts.runData(...)`
- 自动生成的原始 OpenAPI 类型
- 统一错误模型

## 安装

```bash
pip install oomol-fusion-sdk
```

运行要求：

- Python 3.8+
- `requests`

## 初始化

```python
from oomol_fusion_sdk import FusionClient

client = FusionClient(
    api_key="your-api-key",
)
```

支持的初始化参数：

- `api_key: Optional[str]`
- `token: Optional[str]`
- `base_url: str`
- `default_headers: Optional[Dict[str, str]]`
- `poll_interval_ms: int`
- `timeout_ms: int`
- `session: Optional[requests.Session]`

同时也兼容 TypeScript 风格参数名：

- `apiKey`
- `baseUrl`
- `defaultHeaders`
- `pollIntervalMs`
- `timeoutMs`

带 `base_url` 的示例：

```python
client = FusionClient(
    api_key="your-api-key",
    base_url="https://fusion-api.oomol.com",
    poll_interval_ms=2000,
    timeout_ms=300000,
)
```

默认值：

- `base_url`: `https://fusion-api.oomol.com`
- `poll_interval_ms`: `2000`
- `timeout_ms`: `300000`

## 推荐调用方式

如果没有特殊原因，建议按下面的规则使用：

- 任务型接口优先用 `run_data()`
- 需要拆成提交和等待时，用 `submit()` + `wait_data()`
- action 接口优先用 `client.<service>.<action>()`
- SDK 还没建模的新接口，用 `client.request(...)`

## 快速开始

任务型示例：

```python
audio = client.doubao_tts.run_data(
    {
        "text": "Hello from Fusion SDK",
        "voice": "zh_female_vv_uranus_bigtts",
    }
)

print(audio)
```

action 示例：

```python
page = client.jina_reader.read(
    {
        "URL": "https://example.com/article",
        "format": "markdown",
    }
)

print(page["data"])
```

## 任务接口

所有异步任务型服务都支持同一套方法：

- `submit(payload, options=None)`
- `state(session_id, options=None)`
- `result(session_id, options=None)`
- `wait(session_id, options=None)`
- `run(payload, options=None)`
- `wait_data(session_id, options=None)`
- `run_data(payload, options=None)`

同时也提供 TypeScript 风格别名：

- `waitData(sessionID, options=None)`
- `runData(payload, options=None)`

示例：

```python
submit_response = client.pdf_transform_markdown.submit(
    {
        "pdfURL": "https://example.com/book.pdf",
    }
)

markdown = client.pdf_transform_markdown.wait_data(submit_response["sessionID"])
print(markdown)
```

### `run()` 和 `run_data()` 的区别

- `run()` 返回任务完成时的完整响应结构
- `run_data()` 直接返回结果载荷

Fusion API 完成态结果并不完全一致。有些接口返回：

```python
{"success": True, "state": "completed", "data": {...}}
```

有些接口直接返回结果对象。

SDK 的 `wait_data()` 和 `run_data()` 已经把这两种情况统一处理好了，所以大多数场景优先用它们。

## 内置服务快捷入口

内置任务服务：

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

内置 action 分组：

- `client.custom_financial_fundamental_report`
- `client.doubao_text_to_image_seedream`
- `client.text_to_epub_illustrate`
- `client.jina_reader`
- `client.tinify_png_shrink`
- `client.file_upload`
- `client.qwen_image_edit_plus`
- `client.qwen_doc_turbo`

同一批快捷入口也提供 TypeScript 风格 camelCase 别名。

## Action 接口

action 接口既可以通过分组方法调用，也可以通过原始 key 调用。

分组方式：

```python
response = client.qwen_doc_turbo.analyze(
    {
        "text": "Product A costs 100 USD.",
        "instruction": "Extract the product name and price.",
    }
)
```

原始 key 方式：

```python
response = client.action(
    "jina-reader/search",
    {
        "content": "Fusion API SDK",
        "jsonResponse": True,
    },
)
```

## 原始请求兜底

当后端新增了接口，但 SDK 还没更新时，可以直接用 `request()`：

```python
response = client.request(
    path="/v1/new-service/submit",
    method="POST",
    body={
        "prompt": "hello",
    },
)
```

## 运行时扩展

如果新接口仍然符合标准任务模式：

```python
client.register_task("new-service")

result = client.task("new-service").run_data(
    {
        "prompt": "hello",
    }
)
```

如果要注册一个自定义 action 接口：

```python
client.register_action(
    {
        "key": "custom-service/custom-action",
        "method": "POST",
        "path": "/v1/custom-service/action/custom-action",
    }
)
```

同时也兼容 `registerTask(...)` 和 `registerAction(...)` 这两个 TypeScript 风格别名。

## 错误处理

SDK 提供了统一错误类型：

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

统一后的字段：

- `code`
- `message`
- `status`
- `retryable`
- `details`

## 包导出

主 SDK：

```python
from oomol_fusion_sdk import FusionClient, OomolFusionSdkError
```

自动生成的原始 OpenAPI 类型：

```python
from oomol_fusion_sdk.openapi_types import WanxImageSubmitPostRequest
```

与 TypeScript `registry.ts` 尽量对齐的友好别名：

```python
from oomol_fusion_sdk.aliases import WanxImageSubmit, ImageTranslateResultData
```

## 类型扩展

Python 没有 TypeScript declaration merging 的直接等价机制。对于 SDK 还没内置的新接口，建议在本地定义自己的 `TypedDict`，再给 payload 和结果加类型注解：

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

## 代码生成

Python SDK 可以从共享的 OpenAPI 快照生成原始类型：

- `src/oomol_fusion_sdk/generated/openapi_types.py`

常用命令：

```bash
python3 scripts/generate_openapi_types.py
python3 scripts/generate_openapi_types.py --spec ../oomol-fusion-sdk-ts/openapi.full.snapshot.json
python3 -m unittest discover -s tests
```

## 开发说明

- 当前版本号是 `2.0.0`
- 内置服务快捷入口与 TypeScript SDK 的 registry 对齐
- 自动生成的原始 OpenAPI 类型通过单独子路径暴露
