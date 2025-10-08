"""Namespace shim so `import app.*` from repo root resolves to `backend/app`.

This adjusts the package search path for this package so that subpackages like
`app.models`, `app.routers`, etc., are discovered under `backend/app`.
"""
from pathlib import Path
import sys

_root = Path(__file__).resolve().parent
_backend_app = _root.parent / "backend" / "app"
if _backend_app.is_dir():
    # Ensure Python will look into backend/app when importing submodules
    __path__ = [str(_backend_app)] + [p for p in globals().get("__path__", [])]
    # Also add 'backend' to sys.path to allow absolute imports like 'from app.core import ...'
    backend_dir = _backend_app.parent
    if str(backend_dir) not in sys.path:
        sys.path.insert(0, str(backend_dir))
