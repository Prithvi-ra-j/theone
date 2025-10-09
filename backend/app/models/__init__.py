"""Models package.

Keep this package initialization lightweight to avoid import-time side effects
in production environments (e.g., Render). Import models directly from their
modules, for example:

    from app.models.user import User

Avoid ``from app.models import ...`` so we don't need to import every model
on package initialization.
"""

__all__ = []