import os
import sys

# Ensure project root on path so `import app` works when running from repo root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# By default, treat HTTP integration tests as skipped unless explicitly enabled
INTEGRATION_ENABLED = os.getenv("ENABLE_INTEGRATION", "0") == "1"

