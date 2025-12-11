# OOMOL Fusion SDK - Python

Official Python SDK for OOMOL Fusion API. Simple and intuitive interface for interacting with OOMOL Fusion API.

[![Python Version](https://img.shields.io/pypi/pyversions/oomol-fusion-sdk)](https://pypi.org/project/oomol-fusion-sdk/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

[简体中文](README_zh-CN.md) | English

## Features

- ✅ **Zero External Dependencies** - Only depends on `requests` library
- ✅ **Type Safe** - Full type hints support
- ✅ **Auto Polling** - Automatic task status polling
- ✅ **Progress Tracking** - Real-time task execution progress
- ✅ **File Upload** - Upload files to OOMOL cloud storage with multipart support
- ✅ **Error Handling** - Comprehensive error class hierarchy
- ✅ **Flexible Usage** - Multiple usage patterns supported
- ✅ **Context Manager** - Support `with` statement for automatic resource management

## Installation

### Using pip

```bash
pip install oomol-fusion-sdk
```

### Using poetry

```bash
poetry add oomol-fusion-sdk
```

### Install from source

```bash
git clone https://github.com/oomol/oomol-fusion-sdk-py.git
cd oomol-fusion-sdk-py
pip install -e .
```

## Quick Start

### Basic Usage

```python
from oomol_fusion_sdk import OomolFusionSDK

# Initialize SDK
sdk = OomolFusionSDK(token="your-api-token")

# Submit task and wait for result
result = sdk.run({
    "service": "fal-nano-banana-pro",
    "inputs": {
        "prompt": "A beautiful sunset over the mountains",
        "image_size": "landscape_4_3"
    }
})

# Use the result
print(result.data)
print(f"Session ID: {result.session_id}")
```

### Using Context Manager

```python
from oomol_fusion_sdk import OomolFusionSDK

with OomolFusionSDK(token="your-api-token") as sdk:
    result = sdk.run({
        "service": "fal-nano-banana-pro",
        "inputs": {"prompt": "Hello world"}
    })
    print(result.data)
# Connection closed automatically
```

### Progress Tracking

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

### Asynchronous Batch Processing

```python
from concurrent.futures import ThreadPoolExecutor
from oomol_fusion_sdk import OomolFusionSDK

sdk = OomolFusionSDK(token="your-api-token")

prompts = [
    "A sunset over the ocean",
    "A mountain landscape",
    "A city skyline at night",
]

# Submit multiple tasks in parallel
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

### Fine-grained Control

```python
from oomol_fusion_sdk import OomolFusionSDK

sdk = OomolFusionSDK(token="your-api-token")

# 1. Submit task only
response = sdk.submit({
    "service": "fal-nano-banana-pro",
    "inputs": {"prompt": "Hello"}
})

session_id = response["sessionID"]
print(f"Task submitted: {session_id}")

# 2. Do other things...
# ...

# 3. Wait for result
result = sdk.wait_for("fal-nano-banana-pro", session_id)
print(result.data)
```

### Check Task Status

```python
from oomol_fusion_sdk import OomolFusionSDK, TaskState

sdk = OomolFusionSDK(token="your-api-token")

# Submit task
response = sdk.submit({
    "service": "fal-nano-banana-pro",
    "inputs": {"prompt": "Test"}
})

session_id = response["sessionID"]

# Check status (without waiting)
status = sdk.get_task_status("fal-nano-banana-pro", session_id)

print(f"State: {status['state']}")
print(f"Progress: {status.get('progress', 0)}%")

if status["state"] == TaskState.COMPLETED:
    print(f"Result: {status['data']}")
```

### File Upload

Upload files to OOMOL cloud storage with automatic multipart upload for large files:

```python
from pathlib import Path
from oomol_fusion_sdk import OomolFusionSDK, UploadOptions, UploadProgress

sdk = OomolFusionSDK(token="your-api-token")

# Basic upload
download_url = sdk.upload_file(file_bytes, "document.pdf")
print(f"File uploaded: {download_url}")

# Upload with progress tracking
def on_progress(progress):
    if isinstance(progress, UploadProgress):
        # Multipart upload - detailed progress
        print(f"Progress: {progress.percentage:.1f}% "
              f"({progress.uploaded_chunks}/{progress.total_chunks} chunks)")
    else:
        # Single file upload - simple percentage
        print(f"Progress: {progress}%")

options = UploadOptions(on_progress=on_progress)
download_url = sdk.upload_file(file_bytes, "video.mp4", options)

# Upload from file path
download_url = sdk.upload_file(Path("./image.png"), "image.png")

# Upload from file handle
with open("data.csv", "rb") as f:
    download_url = sdk.upload_file(f, "data.csv")

# Custom options
options = UploadOptions(
    max_concurrent_uploads=5,           # Concurrent chunk uploads
    multipart_threshold=10*1024*1024,   # 10MB threshold
    retries=3                            # Retry attempts
)
download_url = sdk.upload_file(large_file, "large.zip", options)
```

**Supported file types:**

- Images: `png`, `jpg`, `jpeg`, `gif`, `webp`
- Audio/Video: `mp3`, `mp4`
- Documents: `txt`, `md`, `pdf`, `epub`, `docx`, `xlsx`, `pptx`
- Data: `csv`, `json`, `zip`

**Features:**

- 🎯 Smart upload strategy (< 5MB: single file, ≥ 5MB: multipart)
- 📊 Real-time progress tracking
- 🚀 Concurrent chunk uploads (default: 3)
- 🔄 Automatic retry on failure (default: 3 times)
- 📦 Maximum file size: 500MB

## API Reference

### OomolFusionSDK

#### Constructor

```python
OomolFusionSDK(
    token: str,
    base_url: str = "https://fusion-api.oomol.com/v1",
    polling_interval: float = 2.0,
    timeout: float = 300.0
)
```

**Parameters:**

- `token` (str): OOMOL API authentication token **(required)**
- `base_url` (str): API base URL, default: `https://fusion-api.oomol.com/v1`
- `polling_interval` (float): Status polling interval (seconds), default: `2.0`
- `timeout` (float): Task timeout (seconds), default: `300.0`

#### Methods

##### `run(request, options=None)`

Submit task and wait for completion (recommended).

**Parameters:**

- `request` (SubmitTaskRequest): Dictionary containing `service` and `inputs`
- `options` (RunOptions, optional): Run options, including `on_progress` callback

**Returns:** `TaskResult` - Contains `data`, `session_id`, `service`

**Raises:**

- `TaskSubmitError`: Task submission failed
- `TaskTimeoutError`: Task timeout
- `TaskFailedError`: Task execution failed
- `NetworkError`: Network communication failed

##### `submit(request)`

Submit task only, without waiting for completion.

**Parameters:**

- `request` (SubmitTaskRequest): Dictionary containing `service` and `inputs`

**Returns:** `SubmitTaskResponse` - Contains `sessionID` and `success`

##### `wait_for(service, session_id, options=None)`

Wait for specific task to complete.

**Parameters:**

- `service` (str): Service name
- `session_id` (str): Task session ID
- `options` (RunOptions, optional): Run options

**Returns:** `TaskResult`

##### `get_task_status(service, session_id)`

Get current task status (without waiting).

**Parameters:**

- `service` (str): Service name
- `session_id` (str): Task session ID

**Returns:** `TaskResultResponse` - Contains `state`, `data`, `error`, `progress`

##### `upload_file(file, file_name, options=None)`

Upload a file to OOMOL cloud storage.

**Parameters:**

- `file` (Union[bytes, BinaryIO, Path]): The file to upload
  - `bytes`: Raw file content
  - `BinaryIO`: File-like object (e.g., from `open()`)
  - `Path`: pathlib.Path object
- `file_name` (str): The name of the file (must include extension)
- `options` (UploadOptions, optional): Upload options

**Returns:** `str` - The download URL of the uploaded file

**Raises:**

- `FileUploadError`: Upload failed or unsupported file type
- `FileTooLargeError`: File exceeds maximum size (500MB)
- `NetworkError`: Network communication failed

##### `close()`

Close HTTP session and clean up resources.

## Error Handling

The SDK provides a comprehensive error class hierarchy:

```python
from oomol_fusion_sdk import (
    OomolFusionSDK,
    OomolFusionError,
    TaskSubmitError,
    TaskTimeoutError,
    TaskFailedError,
    NetworkError,
    FileUploadError,
    FileTooLargeError,
)

sdk = OomolFusionSDK(token="your-api-token")

try:
    result = sdk.run({
        "service": "fal-nano-banana-pro",
        "inputs": {"prompt": "Test"}
    })
except TaskSubmitError as e:
    print(f"Submission failed: {e.message}")
    print(f"Status code: {e.status_code}")
except TaskTimeoutError as e:
    print(f"Task timeout: {e.timeout} seconds")
    print(f"Session ID: {e.session_id}")
except TaskFailedError as e:
    print(f"Task failed: {e.state}")
    print(f"Error details: {e.error_details}")
except FileUploadError as e:
    print(f"Upload failed: {e.message}")
    print(f"File name: {e.file_name}")
except FileTooLargeError as e:
    print(f"File too large: {e.file_size} bytes (max: {e.max_size})")
except NetworkError as e:
    print(f"Network error: {e.message}")
except OomolFusionError as e:
    print(f"SDK error: {e.message}")
```

### Error Classes

| Error Class | Description | Attributes |
|-------------|-------------|------------|
| `OomolFusionError` | Base class for all SDK errors | `message` |
| `TaskSubmitError` | Task submission failed | `message`, `status_code`, `response` |
| `TaskTimeoutError` | Task timeout | `message`, `session_id`, `service`, `timeout` |
| `TaskFailedError` | Task execution failed | `message`, `session_id`, `service`, `state`, `error_details` |
| `NetworkError` | Network communication error | `message`, `original_error` |
| `FileUploadError` | File upload failed | `message`, `file_name`, `original_error` |
| `FileTooLargeError` | File exceeds maximum size | `message`, `file_size`, `max_size` |

## Type Definitions

The SDK provides full type hints support:

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
    UploadOptions,
    UploadProgress,
    UploadProgressCallback,
)

# Task state enum
class TaskState(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    ERROR = "error"

# Upload progress tracking
@dataclass
class UploadProgress:
    uploaded_bytes: int
    total_bytes: int
    percentage: float
    uploaded_chunks: int
    total_chunks: int
```

## Development

### Install Development Dependencies

```bash
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest
```

### Code Formatting

```bash
black oomol_fusion_sdk/
```

### Type Checking

```bash
mypy oomol_fusion_sdk/
```

### Linting

```bash
ruff check oomol_fusion_sdk/
```

## Requirements

- Python 3.8 or higher
- `requests` library (>= 2.25.0)

## License

MIT License - See [LICENSE](LICENSE) file for details

## Links

- [GitHub Repository](https://github.com/oomol/oomol-fusion-sdk-py)
- [Issue Tracker](https://github.com/oomol/oomol-fusion-sdk-py/issues)
- [OOMOL Official Website](https://oomol.com)
- [API Documentation](https://docs.oomol.com)

## Support

For questions or assistance, please:

1. Check the [documentation](https://docs.oomol.com)
2. Submit an [issue](https://github.com/oomol/oomol-fusion-sdk-py/issues)
3. Contact support: support@oomol.com

## Changelog

### 1.1.0 (2025-12-11)

#### New Features ✨

Added `upload_file()` method for uploading files to OOMOL cloud storage:

- 🎯 **Smart Strategy**: Automatically chooses single-file or multipart upload
  - Files < 5MB: Single-file upload
  - Files ≥ 5MB: Multipart upload with concurrent chunks
- 📊 **Real-time Progress**: Progress callbacks showing percentage and chunk progress
- 🚀 **Concurrent Upload**: Multipart upload supports concurrency (default: 3)
- 🔄 **Auto Retry**: Automatic retry on failure (default: 3 times)
- 📦 **File Types**: Supports 17 file types with automatic Content-Type mapping
- 🛡️ **Error Handling**: Comprehensive error handling

**Supported File Types**: png, jpg, jpeg, gif, webp, mp3, mp4, txt, md, pdf, epub, docx, xlsx, pptx, csv, json, zip

#### New Types 📝

- `UploadOptions`: Upload configuration options
- `UploadProgress`: Detailed upload progress information
- `UploadProgressCallback`: Progress callback type

#### New Error Classes 🚨

- `FileUploadError`: File upload failed
- `FileTooLargeError`: File size exceeds limit (max 500MB)

### 1.0.0 (2024-12-09)

- 🎉 Initial release
- ✅ Full API support
- ✅ Type hints support
- ✅ Progress tracking
- ✅ Task cancellation
- ✅ Comprehensive error handling
