"""Utility functions for OOMOL Fusion SDK."""

import platform
import sys
import warnings
from typing import Literal


def detect_environment() -> Literal["cpython", "pypy", "unknown"]:
    """Detect the current Python runtime environment.

    Returns:
        The detected environment: 'cpython', 'pypy', or 'unknown'
    """
    implementation = platform.python_implementation()

    if implementation == "CPython":
        return "cpython"
    elif implementation == "PyPy":
        return "pypy"
    else:
        return "unknown"


def is_requests_available() -> bool:
    """Check if the requests library is available.

    Returns:
        True if requests can be imported, False otherwise
    """
    try:
        import requests

        return True
    except ImportError:
        return False


def validate_environment() -> None:
    """Validate the runtime environment and display warnings if necessary.

    This function checks:
    - Python version (should be >= 3.8)
    - Availability of the requests library

    Warnings will be displayed if any issues are detected.
    """
    # Check Python version
    version = sys.version_info
    if version < (3, 8):
        warnings.warn(
            f"Python {version.major}.{version.minor} is not officially supported. "
            f"Please upgrade to Python 3.8 or higher.",
            RuntimeWarning,
            stacklevel=2,
        )

    # Check requests availability
    if not is_requests_available():
        warnings.warn(
            "The 'requests' library is not installed. "
            "Please install it with: pip install requests",
            RuntimeWarning,
            stacklevel=2,
        )

    # Display environment info
    env = detect_environment()
    if env == "unknown":
        warnings.warn(
            f"Unknown Python implementation: {platform.python_implementation()}. "
            f"This SDK is tested on CPython and PyPy.",
            RuntimeWarning,
            stacklevel=2,
        )


# Export all utility functions
__all__ = [
    "detect_environment",
    "is_requests_available",
    "validate_environment",
]
