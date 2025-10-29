import os
import pytest

# These integration-style tests require a running service. By default
# we skip them to keep CI/unit runs fast and self-contained.
pytestmark = pytest.mark.skipif(
    os.getenv("ENABLE_INTEGRATION", "0") != "1",
    reason="Integration tests disabled; set ENABLE_INTEGRATION=1 to run.",
)

# Retain file so that enabling the env var runs the original flows via http
# but keep it skipped by default to avoid external dependencies.
