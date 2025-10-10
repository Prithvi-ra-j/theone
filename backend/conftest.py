import sys
from pathlib import Path

# Ensure the backend package root is on sys.path so tests can import `app.*` reliably.
_root = Path(__file__).resolve().parents[0]
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

def pytest_configure(config):
    # setuptools-based projects sometimes rely on this; keep default behavior.
    pass
