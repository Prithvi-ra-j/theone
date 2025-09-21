"""Compatibility shim: export SQLAlchemy Base as `Base`.

Some model files import `app.db.base_class.Base`. Historically projects
use `base_class.py` to provide the declarative base. The project currently
defines Base in `app.db.session`. This shim re-exports it to avoid import
errors.
"""
from app.db.session import Base  # noqa: F401

__all__ = ["Base"]
