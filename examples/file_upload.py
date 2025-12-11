"""Example: File upload with OOMOL Fusion SDK.

This example demonstrates how to upload files to OOMOL cloud storage
using the SDK's upload functionality.
"""

import os
from pathlib import Path

from oomol_fusion_sdk import OomolFusionSDK, UploadOptions, UploadProgress

# Get API token from environment
API_TOKEN = os.environ.get("OOMOL_API_TOKEN")
if not API_TOKEN:
    print("Error: OOMOL_API_TOKEN environment variable is not set")
    print("Please set it with: export OOMOL_API_TOKEN='your-token'")
    exit(1)


def main():
    """Main function demonstrating file upload features."""
    # Initialize SDK
    sdk = OomolFusionSDK(token=API_TOKEN)

    print("=== OOMOL Fusion SDK - File Upload Examples ===\n")

    # Example 1: Basic file upload from bytes
    print("1. Basic file upload from bytes")
    try:
        # Create a sample text file
        file_content = b"Hello, OOMOL! This is a test file."
        download_url = sdk.upload_file(file_content, "test.txt")
        print(f"   ✓ File uploaded successfully!")
        print(f"   Download URL: {download_url}\n")
    except Exception as e:
        print(f"   ✗ Upload failed: {e}\n")

    # Example 2: Upload with progress tracking (single file)
    print("2. Upload with progress tracking (small file)")
    try:

        def progress_callback_simple(progress):
            """Simple progress callback for single file upload."""
            if isinstance(progress, (int, float)):
                print(f"   Progress: {progress}%")

        # Create a 1MB test file
        file_content = b"0" * (1024 * 1024)  # 1MB
        options = UploadOptions(on_progress=progress_callback_simple)
        download_url = sdk.upload_file(file_content, "large_file.txt", options)
        print(f"   ✓ File uploaded successfully!")
        print(f"   Download URL: {download_url}\n")
    except Exception as e:
        print(f"   ✗ Upload failed: {e}\n")

    # Example 3: Upload with detailed progress tracking (multipart)
    print("3. Upload with detailed progress tracking (large file - multipart)")
    try:

        def progress_callback_detailed(progress):
            """Detailed progress callback for multipart upload."""
            if isinstance(progress, UploadProgress):
                print(
                    f"   Progress: {progress.percentage:.1f}% "
                    f"({progress.uploaded_chunks}/{progress.total_chunks} chunks, "
                    f"{progress.uploaded_bytes}/{progress.total_bytes} bytes)"
                )
            elif isinstance(progress, (int, float)):
                print(f"   Progress: {progress}%")

        # Create a 6MB test file (will trigger multipart upload)
        file_content = b"0" * (6 * 1024 * 1024)  # 6MB
        options = UploadOptions(on_progress=progress_callback_detailed)
        download_url = sdk.upload_file(file_content, "very_large_file.txt", options)
        print(f"   ✓ File uploaded successfully!")
        print(f"   Download URL: {download_url}\n")
    except Exception as e:
        print(f"   ✗ Upload failed: {e}\n")

    # Example 4: Upload from file path
    print("4. Upload from file path")
    try:
        # Create a temporary file
        temp_file = Path("temp_test.txt")
        temp_file.write_text("This is a test file from Path object.")

        download_url = sdk.upload_file(temp_file, "test_from_path.txt")
        print(f"   ✓ File uploaded successfully!")
        print(f"   Download URL: {download_url}")

        # Clean up
        temp_file.unlink()
        print("   ✓ Temporary file cleaned up\n")
    except Exception as e:
        print(f"   ✗ Upload failed: {e}\n")

    # Example 5: Upload from file handle
    print("5. Upload from file handle")
    try:
        # Create a temporary file
        temp_file = Path("temp_test2.txt")
        temp_file.write_text("This is a test file from file handle.")

        # Upload using file handle
        with open(temp_file, "rb") as f:
            download_url = sdk.upload_file(f, "test_from_handle.txt")
            print(f"   ✓ File uploaded successfully!")
            print(f"   Download URL: {download_url}")

        # Clean up
        temp_file.unlink()
        print("   ✓ Temporary file cleaned up\n")
    except Exception as e:
        print(f"   ✗ Upload failed: {e}\n")

    # Example 6: Custom upload options
    print("6. Custom upload options")
    try:
        # Create a test file
        file_content = b"Test file with custom options"

        # Custom options
        options = UploadOptions(
            max_concurrent_uploads=5,  # 5 concurrent uploads
            multipart_threshold=10 * 1024 * 1024,  # 10MB threshold
            retries=5,  # 5 retries
        )

        download_url = sdk.upload_file(file_content, "custom_options.txt", options)
        print(f"   ✓ File uploaded with custom options!")
        print(f"   Download URL: {download_url}\n")
    except Exception as e:
        print(f"   ✗ Upload failed: {e}\n")

    # Example 7: Different file types
    print("7. Upload different file types")
    file_types = [
        ("test.pdf", b"%PDF-1.4 test"),
        ("test.json", b'{"test": "data"}'),
        ("test.csv", b"col1,col2\nval1,val2"),
    ]

    for file_name, content in file_types:
        try:
            download_url = sdk.upload_file(content, file_name)
            print(f"   ✓ {file_name} uploaded: {download_url}")
        except Exception as e:
            print(f"   ✗ {file_name} failed: {e}")

    print("\n=== All examples completed ===")

    # Close SDK
    sdk.close()


if __name__ == "__main__":
    main()
