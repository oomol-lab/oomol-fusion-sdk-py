# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-12-11

### Added

#### File Upload API

New `upload_file()` method with intelligent file upload to OOMOL cloud storage:

```python
def upload_file(
    file: Union[bytes, BinaryIO, Path],
    file_name: str,
    options: Optional[UploadOptions] = None
) -> str
```

**Key Features**:
- **Smart Strategy**: Automatically chooses between single-file and multipart upload
  - Files < 5MB: Single-file upload
  - Files ≥ 5MB: Multipart upload with concurrent chunks
- **Real-time Progress**: Progress callback support with percentage and chunk details
- **Concurrent Upload**: Multipart upload supports concurrency (default: 3)
- **Auto Retry**: Automatic retry on failure (default: 3 attempts)
- **File Types**: 17 supported file types with automatic Content-Type mapping
- **Error Handling**: Comprehensive error handling mechanism

**Supported File Types**:
- Images: `png`, `jpg`, `jpeg`, `gif`, `webp`
- Audio/Video: `mp3`, `mp4`
- Documents: `txt`, `md`, `pdf`, `epub`, `docx`, `xlsx`, `pptx`
- Data: `csv`, `json`, `zip`

### New Types

#### Upload Types

```python
# Upload options
@dataclass
class UploadOptions:
    on_progress: Optional[UploadProgressCallback] = None
    max_concurrent_uploads: int = 3      # Default: 3
    multipart_threshold: int = 5MB       # Default: 5MB
    retries: int = 3                     # Default: 3

# Upload progress
@dataclass
class UploadProgress:
    uploaded_bytes: int
    total_bytes: int
    percentage: float
    uploaded_chunks: int
    total_chunks: int

# Progress callback
UploadProgressCallback = Callable[[Union[UploadProgress, float]], None]
```

### New Errors

- `FileUploadError` - File upload failure error
- `FileTooLargeError` - File exceeds size limit (max 500MB)

### API Endpoints

#### Single File Upload
```
POST /v1/file-upload/action/generate-presigned-url
```

#### Multipart Upload
```
POST /v1/file-upload/action/create-multipart-upload
POST /v1/file-upload/action/generate-presigned-urls
POST /v1/file-upload/action/complete-multipart-upload
```

### Usage Examples

```python
from pathlib import Path
from oomol_fusion_sdk import OomolFusionSDK, UploadOptions, UploadProgress

sdk = OomolFusionSDK(token="your-api-token")

# Basic usage
download_url = sdk.upload_file(file_bytes, "document.pdf")

# With progress callback
def on_progress(progress):
    if isinstance(progress, UploadProgress):
        print(f"Uploaded {progress.uploaded_chunks}/{progress.total_chunks} chunks")
    else:
        print(f"Progress: {progress}%")

download_url = sdk.upload_file(file_bytes, "video.mp4", UploadOptions(on_progress=on_progress))

# Upload from file path
download_url = sdk.upload_file(Path("./image.png"), "image.png")

# Custom configuration
options = UploadOptions(
    multipart_threshold=10 * 1024 * 1024,  # 10MB threshold
    max_concurrent_uploads=5,                # 5 concurrent uploads
    retries=3                                # Retry 3 times
)
download_url = sdk.upload_file(large_file, "large.zip", options)
```

### Implementation Details

#### Single File Upload Flow
1. Call API to get presigned URL and form fields
2. Set correct Content-Type based on file extension
3. Upload file to OSS using multipart/form-data
4. Automatic retry on failure (exponential backoff)
5. Return download URL

#### Multipart Upload Flow
1. Create multipart upload session (get uploadID, key, partSize)
2. Split file based on partSize
3. Generate presigned URLs for all parts
4. Upload parts concurrently (using PUT method)
5. Collect ETags from all parts
6. Complete multipart upload
7. Return download URL

### Technical Improvements

- ✅ Automatic Content-Type mapping (17 file types)
- ✅ File extension validation and normalization
- ✅ Concurrency control (default 3, configurable)
- ✅ Progress tracking (single: percentage, multipart: detailed)
- ✅ Complete type definitions
- ✅ Comprehensive error handling and retry mechanism

### Testing

- ✅ Unit tests (18 test cases, all passing)
- ✅ File type validation tests
- ✅ Content-Type mapping tests
- ✅ Upload options configuration tests
- ✅ Progress tracking tests

### Documentation

- ✅ README.md - Added file upload functionality
- ✅ API reference documentation updated
- ✅ Usage examples updated
- ✅ Error handling examples updated
- ✅ Type definitions documented

---

## [1.0.1] - 2024-12-09

### Changed
- Updated documentation and package information
- Fixed build configuration

---

## [1.0.0] - 2024-12-09

### Added
- Initial release
- Support for calling any OOMOL Fusion service
- Simple and easy-to-use API
- Automatic polling mechanism
- Complete type support
- Comprehensive error handling
- Task cancellation feature
- Highly configurable

### API Design
- `run()` - Execute task and wait for result (recommended)
- `submit()` - Submit task only, don't wait for result
- `wait_for()` - Wait for specified task to complete
- `cancel()` - Cancel running task
- `get_task_status()` - Get task status

### Improvements
- Optimized Authorization header format
- Added runtime environment detection
- Comprehensive error handling
- Added test framework
- Clear documentation

### Technical Details
- Python >= 3.8
- Native requests library support
- 100% type hint coverage
