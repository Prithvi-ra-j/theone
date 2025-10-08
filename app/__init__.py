# Namespace package shim to allow 'import app' from repo root by pointing to backend/app
import os, sys
from pathlib import Path
_root = Path(__file__).resolve().parent
_backend_app = _root.parent / 'backend' / 'app'
if _backend_app.exists():
    if str(_backend_app) not in sys.path:
        sys.path.insert(0, str(_backend_app.parent))  # add 'backend' to path
    # After ensuring backend is on path, import submodules normally
else:
    # Fallback: do nothing; imports may fail if structure changes
    pass
