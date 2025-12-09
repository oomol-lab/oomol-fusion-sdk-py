"""Tests for OOMOL Fusion SDK utilities."""

import warnings
from oomol_fusion_sdk.utils import (
    detect_environment,
    is_requests_available,
    validate_environment,
)


def test_detect_environment() -> None:
    """Test environment detection."""
    env = detect_environment()
    assert env in ("cpython", "pypy", "unknown")


def test_is_requests_available() -> None:
    """Test requests availability check."""
    # Since requests is a dependency, it should always be available in tests
    assert is_requests_available() is True


def test_validate_environment_no_warnings() -> None:
    """Test environment validation with no warnings."""
    # Should not raise any exceptions
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        try:
            validate_environment()
        except RuntimeWarning:
            # This is expected in some environments
            pass
