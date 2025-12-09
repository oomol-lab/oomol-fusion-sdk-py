# OOMOL Fusion SDK - Python

官方 Python SDK，用于 OOMOL Fusion API。提供简单直观的接口来与 OOMOL Fusion API 交互。

[![Python Version](https://img.shields.io/pypi/pyversions/oomol-fusion-sdk)](https://pypi.org/project/oomol-fusion-sdk/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

简体中文 | [English](README.md)

## 特性

- ✅ **零外部依赖** - 仅依赖 `requests` 库
- ✅ **类型安全** - 完整的类型提示支持
- ✅ **自动轮询** - 内部自动处理任务状态查询
- ✅ **进度跟踪** - 实时获取任务执行进度
- ✅ **错误处理** - 完善的错误类层次结构
- ✅ **灵活使用** - 支持多种使用模式
- ✅ **上下文管理** - 支持 `with` 语句自动资源管理

## 安装

### 使用 pip

```bash
pip install oomol-fusion-sdk
```

### 使用 poetry

```bash
poetry add oomol-fusion-sdk
```

### 从源码安装

```bash
git clone https://github.com/oomol/oomol-fusion-sdk-py.git
cd oomol-fusion-sdk-py
pip install -e .
```

## 快速开始

### 基础使用

```python
from oomol_fusion_sdk import OomolFusionSDK

# 初始化 SDK
sdk = OomolFusionSDK(token="your-api-token")

# 提交任务并等待结果
result = sdk.run({
    "service": "fal-nano-banana-pro",
    "inputs": {
        "prompt": "A beautiful sunset over the mountains",
        "image_size": "landscape_4_3"
    }
})

# 使用结果
print(result.data)
print(f"Session ID: {result.session_id}")
```

### 使用上下文管理器

```python
from oomol_fusion_sdk import OomolFusionSDK

with OomolFusionSDK(token="your-api-token") as sdk:
    result = sdk.run({
        "service": "fal-nano-banana-pro",
        "inputs": {"prompt": "Hello world"}
    })
    print(result.data)
# 自动关闭连接
```

### 进度跟踪

```python
from oomol_fusion_sdk import OomolFusionSDK, RunOptions

sdk = OomolFusionSDK(token="your-api-token")

def on_progress(progress: float):
    print(f"Progress: {progress}%")

result = sdk.run(
    {
        "service": "fal-nano-banana-pro",
        "inputs": {"prompt": "A cat wearing sunglasses"}
    },
    options=RunOptions(on_progress=on_progress)
)
```

### 异步批量处理

```python
from concurrent.futures import ThreadPoolExecutor
from oomol_fusion_sdk import OomolFusionSDK

sdk = OomolFusionSDK(token="your-api-token")

prompts = [
    "A sunset over the ocean",
    "A mountain landscape",
    "A city skyline at night",
]

# 并行提交多个任务
with ThreadPoolExecutor(max_workers=5) as executor:
    futures = [
        executor.submit(
            sdk.run,
            {
                "service": "fal-nano-banana-pro",
                "inputs": {"prompt": prompt}
            }
        )
        for prompt in prompts
    ]

    results = [future.result() for future in futures]

for i, result in enumerate(results):
    print(f"Result {i+1}: {result.data}")
```

### 细粒度控制

```python
from oomol_fusion_sdk import OomolFusionSDK

sdk = OomolFusionSDK(token="your-api-token")

# 1. 仅提交任务
response = sdk.submit({
    "service": "fal-nano-banana-pro",
    "inputs": {"prompt": "Hello"}
})

session_id = response["sessionID"]
print(f"Task submitted: {session_id}")

# 2. 做其他事情...
# ...

# 3. 等待结果
result = sdk.wait_for("fal-nano-banana-pro", session_id)
print(result.data)
```

### 检查任务状态

```python
from oomol_fusion_sdk import OomolFusionSDK, TaskState

sdk = OomolFusionSDK(token="your-api-token")

# 提交任务
response = sdk.submit({
    "service": "fal-nano-banana-pro",
    "inputs": {"prompt": "Test"}
})

session_id = response["sessionID"]

# 检查状态（不等待）
status = sdk.get_task_status("fal-nano-banana-pro", session_id)

print(f"State: {status['state']}")
print(f"Progress: {status.get('progress', 0)}%")

if status["state"] == TaskState.COMPLETED:
    print(f"Result: {status['data']}")
```

## API 参考

### OomolFusionSDK

#### 构造函数

```python
OomolFusionSDK(
    token: str,
    base_url: str = "https://fusion-api.oomol.com/v1",
    polling_interval: float = 2.0,
    timeout: float = 300.0
)
```

**参数:**

- `token` (str): OOMOL API 认证令牌 **(必需)**
- `base_url` (str): API 基础 URL，默认: `https://fusion-api.oomol.com/v1`
- `polling_interval` (float): 状态轮询间隔（秒），默认: `2.0`
- `timeout` (float): 任务超时时间（秒），默认: `300.0`

#### 方法

##### `run(request, options=None)`

提交任务并等待完成（推荐使用）。

**参数:**

- `request` (SubmitTaskRequest): 包含 `service` 和 `inputs` 的字典
- `options` (RunOptions, optional): 运行选项，包含 `on_progress` 回调

**返回:** `TaskResult` - 包含 `data`, `session_id`, `service`

**异常:**

- `TaskSubmitError`: 任务提交失败
- `TaskTimeoutError`: 任务超时
- `TaskFailedError`: 任务执行失败
- `NetworkError`: 网络通信失败

##### `submit(request)`

仅提交任务，不等待完成。

**参数:**

- `request` (SubmitTaskRequest): 包含 `service` 和 `inputs` 的字典

**返回:** `SubmitTaskResponse` - 包含 `sessionID` 和 `success`

##### `wait_for(service, session_id, options=None)`

等待指定任务完成。

**参数:**

- `service` (str): 服务名称
- `session_id` (str): 任务会话 ID
- `options` (RunOptions, optional): 运行选项

**返回:** `TaskResult`

##### `get_task_status(service, session_id)`

获取任务当前状态（不等待）。

**参数:**

- `service` (str): 服务名称
- `session_id` (str): 任务会话 ID

**返回:** `TaskResultResponse` - 包含 `state`, `data`, `error`, `progress`

##### `close()`

关闭 HTTP 会话并清理资源。

## 错误处理

SDK 提供了完善的错误类层次结构：

```python
from oomol_fusion_sdk import (
    OomolFusionSDK,
    OomolFusionError,
    TaskSubmitError,
    TaskTimeoutError,
    TaskFailedError,
    NetworkError,
)

sdk = OomolFusionSDK(token="your-api-token")

try:
    result = sdk.run({
        "service": "fal-nano-banana-pro",
        "inputs": {"prompt": "Test"}
    })
except TaskSubmitError as e:
    print(f"提交失败: {e.message}")
    print(f"状态码: {e.status_code}")
except TaskTimeoutError as e:
    print(f"任务超时: {e.timeout} 秒")
    print(f"Session ID: {e.session_id}")
except TaskFailedError as e:
    print(f"任务失败: {e.state}")
    print(f"错误详情: {e.error_details}")
except NetworkError as e:
    print(f"网络错误: {e.message}")
except OomolFusionError as e:
    print(f"SDK 错误: {e.message}")
```

### 错误类

| 错误类 | 描述 | 属性 |
|--------|------|------|
| `OomolFusionError` | 所有 SDK 错误的基类 | `message` |
| `TaskSubmitError` | 任务提交失败 | `message`, `status_code`, `response` |
| `TaskTimeoutError` | 任务超时 | `message`, `session_id`, `service`, `timeout` |
| `TaskFailedError` | 任务执行失败 | `message`, `session_id`, `service`, `state`, `error_details` |
| `NetworkError` | 网络通信错误 | `message`, `original_error` |

## 类型定义

SDK 提供完整的类型提示支持：

```python
from oomol_fusion_sdk import (
    TaskState,
    SubmitTaskRequest,
    SubmitTaskResponse,
    TaskResultResponse,
    TaskResult,
    RunOptions,
    ProgressCallback,
    OomolFusionSDKOptions,
)

# 任务状态枚举
class TaskState(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    ERROR = "error"
```

## 开发

### 安装开发依赖

```bash
pip install -e ".[dev]"
```

### 运行测试

```bash
pytest
```

### 代码格式化

```bash
black oomol_fusion_sdk/
```

### 类型检查

```bash
mypy oomol_fusion_sdk/
```

### Linting

```bash
ruff check oomol_fusion_sdk/
```

## 环境要求

- Python 3.8 或更高版本
- `requests` 库 (>= 2.25.0)

## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 链接

- [GitHub 仓库](https://github.com/oomol/oomol-fusion-sdk-py)
- [问题反馈](https://github.com/oomol/oomol-fusion-sdk-py/issues)
- [OOMOL 官网](https://oomol.com)
- [API 文档](https://docs.oomol.com)

## 支持

如有问题或需要帮助，请：

1. 查看 [文档](https://docs.oomol.com)
2. 提交 [Issue](https://github.com/oomol/oomol-fusion-sdk-py/issues)
3. 联系支持: support@oomol.com

## 更新日志

### 1.0.0 (2024-12-09)

- 🎉 初始版本发布
- ✅ 完整的 API 支持
- ✅ 类型提示支持
- ✅ 进度跟踪
- ✅ 任务取消
- ✅ 完善的错误处理
